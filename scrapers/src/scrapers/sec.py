"""EDGAR (SEC) filings scraper.

For each publicly traded company in the registry:

1. Fetch the company submissions JSON from `data.sec.gov`.
2. Filter to 10-K and 10-Q filings.
3. For each filing not already snapshotted, download the primary HTML
   document from `www.sec.gov/Archives/...`.
4. Extract paragraphs that mention AI / training / model keywords.
5. Persist a JSON record at `data/raw/sec/<ticker>/<accession>.json`.

Only filings that match at least one keyword are persisted; filings with no
matches are recorded as `{...,"excerpts":[]}` so the pipeline can skip them
on subsequent runs without re-downloading.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
from bs4 import BeautifulSoup

from .config import COMPANIES, Company, RAW_ROOT, get_company
from .http import PoliteClient

log = logging.getLogger(__name__)

SEC_ROOT = RAW_ROOT / "sec"

SUBMISSIONS_URL_TEMPLATE = "https://data.sec.gov/submissions/CIK{cik}.json"
ARCHIVE_URL_TEMPLATE = (
    "https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_nodash}/{primary_doc}"
)

FORMS_OF_INTEREST = ("10-K", "10-Q")

# Keywords to flag paragraphs as AI-relevant. Matching is case-insensitive;
# multi-word phrases use word-boundary-ish regex (whitespace-tolerant).
AI_KEYWORDS: tuple[str, ...] = (
    "generative AI",
    "training data",
    "model training",
    "AI model",
    "large language model",
    "foundation model",
    "artificial intelligence",
    "machine learning",
)


def _compile_keyword_pattern(keywords: tuple[str, ...]) -> re.Pattern[str]:
    alternation = "|".join(re.escape(k).replace(r"\ ", r"\s+") for k in keywords)
    return re.compile(rf"(?i)\b(?:{alternation})\b")


KEYWORD_PATTERN = _compile_keyword_pattern(AI_KEYWORDS)


@dataclass
class Filing:
    """Minimal filing metadata pulled from EDGAR submissions."""

    accession_number: str  # e.g. "0001326801-25-000012"
    form: str  # "10-K" | "10-Q"
    filing_date: str  # "YYYY-MM-DD"
    report_date: str  # "YYYY-MM-DD"
    primary_document: str  # e.g. "meta-20241231.htm"


@dataclass
class FilingRecord:
    """What we persist per filing."""

    company_slug: str
    ticker: str
    cik: str
    form: str
    accession_number: str
    filing_date: str
    report_date: str
    primary_document_url: str
    fetched_at: str
    matched_keywords: list[str]
    excerpts: list[dict[str, str]] = field(default_factory=list)


def _parse_recent_filings(data: dict[str, Any]) -> list[Filing]:
    recent = data.get("filings", {}).get("recent", {})
    acc_nos = recent.get("accessionNumber") or []
    forms = recent.get("form") or []
    filing_dates = recent.get("filingDate") or []
    report_dates = recent.get("reportDate") or []
    primary_docs = recent.get("primaryDocument") or []

    filings: list[Filing] = []
    for i in range(len(acc_nos)):
        form = forms[i] if i < len(forms) else ""
        if form not in FORMS_OF_INTEREST:
            continue
        filings.append(
            Filing(
                accession_number=acc_nos[i],
                form=form,
                filing_date=filing_dates[i] if i < len(filing_dates) else "",
                report_date=report_dates[i] if i < len(report_dates) else "",
                primary_document=primary_docs[i] if i < len(primary_docs) else "",
            )
        )
    return filings


def _archive_url(cik: str, filing: Filing) -> str:
    cik_int = int(cik)
    acc_nodash = filing.accession_number.replace("-", "")
    return ARCHIVE_URL_TEMPLATE.format(
        cik_int=cik_int, acc_nodash=acc_nodash, primary_doc=filing.primary_document
    )


def extract_keyword_paragraphs(
    html: str,
    *,
    pattern: re.Pattern[str] = KEYWORD_PATTERN,
    max_paragraphs: int = 50,
    max_chars: int = 1500,
) -> tuple[list[str], list[dict[str, str]]]:
    """Return (matched_keywords, excerpts).

    `excerpts` is a list of `{keyword, paragraph}` dicts. Paragraphs are
    truncated to `max_chars` and capped at `max_paragraphs` total to keep
    per-filing JSON bounded in size.
    """
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()

    paragraphs: list[str] = []
    for block in soup.find_all(["p", "div", "li", "td"]):
        text = block.get_text(" ", strip=True)
        if len(text) < 80:  # skip fragments / nav-like cells
            continue
        paragraphs.append(text)

    # Dedupe while preserving order; outer divs often repeat inner <p> text.
    seen: set[str] = set()
    unique: list[str] = []
    for p in paragraphs:
        if p in seen:
            continue
        seen.add(p)
        unique.append(p)

    matched: set[str] = set()
    excerpts: list[dict[str, str]] = []
    for para in unique:
        hit = pattern.search(para)
        if not hit:
            continue
        matched.add(hit.group(0).lower())
        excerpts.append(
            {
                "keyword": hit.group(0),
                "paragraph": para[:max_chars],
            }
        )
        if len(excerpts) >= max_paragraphs:
            break

    return sorted(matched), excerpts


def _record_path(ticker: str, accession_number: str, root: Path = SEC_ROOT) -> Path:
    return root / ticker / f"{accession_number}.json"


def process_filing(
    client: PoliteClient,
    company: Company,
    filing: Filing,
    *,
    root: Path = SEC_ROOT,
) -> FilingRecord | None:
    """Fetch a single filing and persist its extracted keyword paragraphs.

    Returns the FilingRecord, or None if the filing was already persisted
    (idempotent re-run) or failed to fetch.
    """
    if company.ticker is None or company.sec_cik is None:
        log.debug("Skipping %s: not a public filer", company.slug)
        return None

    out_path = _record_path(company.ticker, filing.accession_number, root)
    if out_path.exists():
        return None

    url = _archive_url(company.sec_cik, filing)
    try:
        resp = client.get(url)
    except httpx.HTTPError as err:
        log.error("HTTP error fetching SEC filing %s: %s", url, err)
        return None

    html = resp.text
    matched, excerpts = extract_keyword_paragraphs(html)

    record = FilingRecord(
        company_slug=company.slug,
        ticker=company.ticker,
        cik=company.sec_cik,
        form=filing.form,
        accession_number=filing.accession_number,
        filing_date=filing.filing_date,
        report_date=filing.report_date,
        primary_document_url=url,
        fetched_at=datetime.now(UTC).isoformat(),
        matched_keywords=matched,
        excerpts=excerpts,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(record.__dict__, fh, indent=2, sort_keys=True)
        fh.write("\n")
    log.info(
        "Wrote SEC record %s (%d excerpts, keywords=%s)",
        out_path,
        len(excerpts),
        matched,
    )
    return record


def fetch_company_filings(
    client: PoliteClient,
    company: Company,
    *,
    root: Path = SEC_ROOT,
    limit: int | None = None,
) -> list[FilingRecord]:
    """Fetch and process all 10-K/10-Q filings for a single company.

    `limit` caps the number of filings processed per call (useful for the
    daily cron, where the initial backfill has already happened).
    """
    if company.sec_cik is None:
        return []

    url = SUBMISSIONS_URL_TEMPLATE.format(cik=company.sec_cik)
    try:
        resp = client.get(url)
    except httpx.HTTPError as err:
        log.error("Failed to fetch submissions for %s: %s", company.slug, err)
        return []

    filings = _parse_recent_filings(resp.json())
    if limit is not None:
        filings = filings[:limit]

    records: list[FilingRecord] = []
    for filing in filings:
        record = process_filing(client, company, filing, root=root)
        if record is not None:
            records.append(record)
    return records


def fetch_all_filings(
    slugs: list[str] | None = None,
    *,
    client: PoliteClient | None = None,
    root: Path = SEC_ROOT,
    limit: int | None = None,
) -> list[FilingRecord]:
    """Fetch filings for all public companies (or the subset in `slugs`)."""
    targets = [get_company(s) for s in slugs] if slugs else list(COMPANIES)

    owned = client is None
    cm = client if client is not None else PoliteClient()
    if owned:
        cm.__enter__()
    try:
        records: list[FilingRecord] = []
        for company in targets:
            if company.sec_cik is None:
                continue
            records.extend(fetch_company_filings(cm, company, root=root, limit=limit))
        return records
    finally:
        if owned:
            cm.__exit__(None, None, None)
