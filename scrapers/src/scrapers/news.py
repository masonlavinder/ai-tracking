"""News context scraper via the GDELT 2.0 DOC API.

We query GDELT per company using the company's news query terms combined
with an AI/privacy qualifier, then persist ONLY metadata — never article
body text — at `data/raw/news/<slug>/<YYYY-MM-DD>.json`.

Each record contains:

    {url, title, source_domain, language, country, seen_at, tone}

`tone` is GDELT's own tone score for the article (roughly -10 to +10).
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import httpx

from .config import COMPANIES, Company, RAW_ROOT, get_company
from .http import PoliteClient

log = logging.getLogger(__name__)

NEWS_ROOT = RAW_ROOT / "news"

GDELT_DOC_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

# Combined with each company's query terms to filter to AI/privacy coverage.
AI_PRIVACY_QUALIFIER = '("AI" OR "artificial intelligence" OR privacy OR "data protection")'


@dataclass
class NewsRecord:
    url: str
    title: str
    source_domain: str
    language: str
    country: str
    seen_at: str  # ISO-8601
    tone: float | None


def build_query(company: Company) -> str:
    """Build a GDELT query combining company terms with an AI/privacy qualifier."""
    terms = company.news_query_terms or [company.name]
    quoted = [f'"{t}"' for t in terms]
    company_clause = "(" + " OR ".join(quoted) + ")"
    return f"{company_clause} AND {AI_PRIVACY_QUALIFIER}"


def _parse_gdelt_timestamp(value: str) -> str:
    """Convert GDELT's YYYYMMDDHHMMSS format to an ISO-8601 UTC string."""
    if not value:
        return ""
    try:
        dt = datetime.strptime(value, "%Y%m%d%H%M%S").replace(tzinfo=UTC)
    except ValueError:
        return value
    return dt.isoformat()


def parse_gdelt_response(payload: dict[str, Any]) -> list[NewsRecord]:
    """Convert a GDELT DOC API JSON response into NewsRecords (metadata only)."""
    articles = payload.get("articles") or []
    records: list[NewsRecord] = []
    for a in articles:
        url = a.get("url") or ""
        title = a.get("title") or ""
        if not url or not title:
            continue
        records.append(
            NewsRecord(
                url=url,
                title=title,
                source_domain=a.get("domain") or "",
                language=a.get("language") or "",
                country=a.get("sourcecountry") or "",
                seen_at=_parse_gdelt_timestamp(a.get("seendate") or ""),
                tone=_coerce_float(a.get("tone")),
            )
        )
    return records


def _coerce_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def query_company(
    client: PoliteClient,
    company: Company,
    *,
    timespan: str = "7d",
    max_records: int = 250,
) -> list[NewsRecord]:
    """Run one GDELT query for a company. Returns [] on failure."""
    params = {
        "query": build_query(company),
        "mode": "ArtList",
        "format": "json",
        "timespan": timespan,
        "maxrecords": str(max_records),
        "sort": "DateDesc",
    }
    try:
        resp = client.get(GDELT_DOC_URL, params=params)
    except httpx.HTTPError as err:
        log.error("GDELT query failed for %s: %s", company.slug, err)
        return []

    try:
        payload = resp.json()
    except json.JSONDecodeError as err:
        log.error("GDELT returned non-JSON for %s: %s", company.slug, err)
        return []

    return parse_gdelt_response(payload)


def write_company_news(
    company: Company,
    records: list[NewsRecord],
    *,
    root: Path = NEWS_ROOT,
    today: date | None = None,
) -> Path | None:
    if not records:
        return None
    day = today or datetime.now(UTC).date()
    out_dir = root / company.slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{day.isoformat()}.json"
    payload = [asdict(r) for r in records]
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")
    log.info("Wrote %d news records to %s", len(records), out_path)
    return out_path


def fetch_all_news(
    slugs: list[str] | None = None,
    *,
    client: PoliteClient | None = None,
    timespan: str = "7d",
    max_records: int = 250,
    root: Path = NEWS_ROOT,
    today: date | None = None,
) -> dict[str, Path | None]:
    """Query GDELT for every company (or the subset in `slugs`)."""
    targets = [get_company(s) for s in slugs] if slugs else list(COMPANIES)

    owned = client is None
    cm = client if client is not None else PoliteClient()
    if owned:
        cm.__enter__()
    try:
        results: dict[str, Path | None] = {}
        for company in targets:
            records = query_company(
                cm, company, timespan=timespan, max_records=max_records
            )
            results[company.slug] = write_company_news(
                company, records, root=root, today=today
            )
        return results
    finally:
        if owned:
            cm.__exit__(None, None, None)
