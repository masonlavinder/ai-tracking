"""Regulatory sources: FTC press releases, EU Commission, California AG.

All three sources are normalized to a single schema before persistence:

    {source, title, url, published_at, body_excerpt}

Records are filtered by AI / privacy keywords so we don't store unrelated
enforcement news. Each run writes one file per source per day at
`data/raw/regulatory/<source>/<YYYY-MM-DD>.json` containing a JSON array of
matching records. EU and California sources are best-effort — if the listing
page layout changes they can fail silently and are noted in KNOWN_ISSUES.md.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET

import httpx
from bs4 import BeautifulSoup

from .config import RAW_ROOT
from .http import PoliteClient

log = logging.getLogger(__name__)

REGULATORY_ROOT = RAW_ROOT / "regulatory"

FTC_RSS_URL = "https://www.ftc.gov/news-events/news/press-releases/rss"
EU_COMMISSION_URL = "https://ec.europa.eu/commission/presscorner/home/en"
CALIFORNIA_AG_URL = "https://oag.ca.gov/news"

# Matching is case-insensitive. Keywords are deliberately broad; v1 prefers
# recall over precision so interesting enforcement actions don't get missed.
AI_PRIVACY_KEYWORDS: tuple[str, ...] = (
    "artificial intelligence",
    "AI",
    "generative",
    "machine learning",
    "algorithm",
    "automated decision",
    "chatbot",
    "facial recognition",
    "biometric",
    "privacy",
    "data broker",
    "consent",
    "consumer data",
    "personal data",
    "personal information",
    "deepfake",
    "large language model",
)

_KEYWORD_PATTERN = re.compile(
    r"(?i)\b(?:"
    + "|".join(re.escape(k).replace(r"\ ", r"\s+") for k in AI_PRIVACY_KEYWORDS)
    + r")\b"
)


@dataclass
class RegulatoryRecord:
    source: str
    title: str
    url: str
    published_at: str  # ISO-8601 or "YYYY-MM-DD"
    body_excerpt: str


def _matches_keywords(*texts: str) -> bool:
    for t in texts:
        if t and _KEYWORD_PATTERN.search(t):
            return True
    return False


# --- FTC ------------------------------------------------------------------


def parse_ftc_rss(xml_bytes: bytes) -> list[RegulatoryRecord]:
    """Parse an FTC press release RSS feed into normalized records."""
    root = ET.fromstring(xml_bytes)
    records: list[RegulatoryRecord] = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        description = (item.findtext("description") or "").strip()

        # Strip HTML from description for the excerpt.
        excerpt = BeautifulSoup(description, "lxml").get_text(" ", strip=True)
        # Keep excerpts compact.
        excerpt = excerpt[:1000]

        if not _matches_keywords(title, excerpt):
            continue

        published_iso = _rfc822_to_iso(pub_date) or pub_date
        records.append(
            RegulatoryRecord(
                source="ftc",
                title=title,
                url=link,
                published_at=published_iso,
                body_excerpt=excerpt,
            )
        )
    return records


def _rfc822_to_iso(value: str) -> str | None:
    from email.utils import parsedate_to_datetime

    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC).isoformat()


def fetch_ftc(client: PoliteClient) -> list[RegulatoryRecord]:
    try:
        resp = client.get(FTC_RSS_URL)
    except httpx.HTTPError as err:
        log.error("FTC RSS fetch failed: %s", err)
        return []
    return parse_ftc_rss(resp.content)


# --- EU Commission --------------------------------------------------------


def parse_eu_commission(html: str, base_url: str = EU_COMMISSION_URL) -> list[RegulatoryRecord]:
    """Best-effort parse of the Commission press corner HTML.

    The page lists recent items in repeating cards. We walk anchor tags that
    link to `/commission/presscorner/detail/` pages and grab nearby date
    text if present. This is fragile by design — changes to markup must
    be caught by the scheduled run and logged, not cause a hard failure.
    """
    soup = BeautifulSoup(html, "lxml")
    records: list[RegulatoryRecord] = []
    seen: set[str] = set()

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        if "/presscorner/detail" not in href:
            continue
        url = href if href.startswith("http") else _join_url(base_url, href)
        if url in seen:
            continue
        seen.add(url)

        title = anchor.get_text(" ", strip=True)
        if not title:
            continue

        # Look for a date in ancestor elements (commonly a <time> or text node).
        published = ""
        ancestor = anchor
        for _ in range(4):
            ancestor = ancestor.parent
            if ancestor is None:
                break
            time_el = ancestor.find("time") if hasattr(ancestor, "find") else None
            if time_el and time_el.get("datetime"):
                published = time_el["datetime"]
                break
            if time_el and time_el.get_text(strip=True):
                published = time_el.get_text(strip=True)
                break

        if not _matches_keywords(title):
            continue

        records.append(
            RegulatoryRecord(
                source="eu_commission",
                title=title,
                url=url,
                published_at=published,
                body_excerpt=title,
            )
        )
    return records


def _join_url(base: str, path: str) -> str:
    from urllib.parse import urljoin

    return urljoin(base, path)


def fetch_eu_commission(client: PoliteClient) -> list[RegulatoryRecord]:
    try:
        resp = client.get(EU_COMMISSION_URL)
    except httpx.HTTPError as err:
        log.error("EU Commission fetch failed: %s", err)
        return []
    return parse_eu_commission(resp.text)


# --- California AG --------------------------------------------------------


def parse_california_ag(html: str, base_url: str = CALIFORNIA_AG_URL) -> list[RegulatoryRecord]:
    """Parse the California AG news listing (best-effort)."""
    soup = BeautifulSoup(html, "lxml")
    records: list[RegulatoryRecord] = []
    seen: set[str] = set()

    # News listings on oag.ca.gov tend to use article-level wrappers with
    # a headline <a> and a <time> / date <div> sibling.
    for article in soup.find_all(["article", "div"]):
        headline = article.find("a", href=True) if hasattr(article, "find") else None
        if not headline:
            continue
        href = headline["href"]
        if not href or href.startswith("#"):
            continue
        url = href if href.startswith("http") else _join_url(base_url, href)
        if url in seen:
            continue
        title = headline.get_text(" ", strip=True)
        if not title or len(title) < 5:
            continue
        seen.add(url)

        time_el = article.find("time") if hasattr(article, "find") else None
        published = ""
        if time_el is not None:
            published = time_el.get("datetime") or time_el.get_text(strip=True) or ""

        excerpt_el = article.find("p") if hasattr(article, "find") else None
        excerpt = excerpt_el.get_text(" ", strip=True) if excerpt_el else title
        excerpt = excerpt[:1000]

        if not _matches_keywords(title, excerpt):
            continue

        records.append(
            RegulatoryRecord(
                source="california_ag",
                title=title,
                url=url,
                published_at=published,
                body_excerpt=excerpt,
            )
        )
    return records


def fetch_california_ag(client: PoliteClient) -> list[RegulatoryRecord]:
    try:
        resp = client.get(CALIFORNIA_AG_URL)
    except httpx.HTTPError as err:
        log.error("California AG fetch failed: %s", err)
        return []
    return parse_california_ag(resp.text)


# --- Orchestration --------------------------------------------------------


def _write_records(
    source: str,
    records: Iterable[RegulatoryRecord],
    *,
    root: Path = REGULATORY_ROOT,
    today: date | None = None,
) -> Path | None:
    records_list = list(records)
    if not records_list:
        return None
    day = today or datetime.now(UTC).date()
    out_dir = root / source
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{day.isoformat()}.json"
    payload = [asdict(r) for r in records_list]
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")
    log.info("Wrote %d %s records to %s", len(records_list), source, out_path)
    return out_path


def fetch_all_regulatory(
    *,
    client: PoliteClient | None = None,
    root: Path = REGULATORY_ROOT,
    today: date | None = None,
) -> dict[str, Path | None]:
    """Fetch all regulatory sources and write per-source dated JSON files."""
    owned = client is None
    cm = client if client is not None else PoliteClient()
    if owned:
        cm.__enter__()
    try:
        results: dict[str, Path | None] = {
            "ftc": _write_records("ftc", fetch_ftc(cm), root=root, today=today),
            "eu_commission": _write_records(
                "eu_commission", fetch_eu_commission(cm), root=root, today=today
            ),
            "california_ag": _write_records(
                "california_ag", fetch_california_ag(cm), root=root, today=today
            ),
        }
        return results
    finally:
        if owned:
            cm.__exit__(None, None, None)
