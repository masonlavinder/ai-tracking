"""Privacy policy scraper.

Fetches each company's registered policy URLs and writes three sibling files
per snapshot under `data/raw/policies/<slug>/<kind>/`:

- `<YYYY-MM-DD>.html`      — the raw response body
- `<YYYY-MM-DD>.txt`       — plain text extracted with trafilatura (BS4 fallback)
- `<YYYY-MM-DD>.meta.json` — fetch metadata (URL, HTTP status, sha256, etc.)

If a snapshot for today already exists and its sha256 matches, the fetch is
skipped (idempotent same-day re-runs). If the content hash differs from the
most recent prior snapshot, a new dated snapshot is written.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import httpx
import trafilatura
from bs4 import BeautifulSoup

from .config import COMPANIES, Company, PolicyURL, RAW_ROOT, get_company
from .http import PoliteClient, RobotsDisallowedError

log = logging.getLogger(__name__)

POLICIES_ROOT = RAW_ROOT / "policies"


@dataclass
class SnapshotResult:
    """Outcome of one policy fetch."""

    company_slug: str
    policy_kind: str
    url: str
    snapshot_path: Path | None  # None if skipped
    status: str  # "written" | "unchanged" | "skipped" | "error"
    detail: str = ""


def _policy_id(policy: PolicyURL) -> str:
    """Stable on-disk identifier for a policy URL within a company.

    Uses `kind`, optionally suffixed with region, so snapshots of the same
    kind across regions stay separated.
    """
    if policy.region:
        return f"{policy.kind}-{policy.region.lower()}"
    return policy.kind


def _today_str() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _extract_text(html: str) -> str:
    """Best-effort plaintext extraction.

    Prefer trafilatura, which is tuned for article-like pages. Fall back to
    BeautifulSoup stripping if trafilatura returns nothing.
    """
    extracted = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=True,
        favor_precision=True,
    )
    if extracted and extracted.strip():
        return extracted.strip() + "\n"

    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text("\n")
    lines = [line.strip() for line in text.splitlines()]
    cleaned = "\n".join(line for line in lines if line)
    return cleaned + "\n" if cleaned else ""


def _latest_prior_hash(policy_dir: Path) -> str | None:
    """Find the sha256 of the most recent prior snapshot in a policy directory."""
    if not policy_dir.is_dir():
        return None
    metas = sorted(policy_dir.glob("*.meta.json"))
    if not metas:
        return None
    try:
        with metas[-1].open("r", encoding="utf-8") as fh:
            meta = json.load(fh)
        value = meta.get("sha256")
        return value if isinstance(value, str) else None
    except (OSError, json.JSONDecodeError) as err:
        log.warning("Could not read %s: %s", metas[-1], err)
        return None


def _write_snapshot(
    policy_dir: Path,
    date_str: str,
    html_bytes: bytes,
    text: str,
    meta: dict[str, object],
) -> Path:
    policy_dir.mkdir(parents=True, exist_ok=True)
    html_path = policy_dir / f"{date_str}.html"
    text_path = policy_dir / f"{date_str}.txt"
    meta_path = policy_dir / f"{date_str}.meta.json"

    html_path.write_bytes(html_bytes)
    text_path.write_text(text, encoding="utf-8")
    with meta_path.open("w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return html_path


def save_snapshot_if_changed(
    *,
    company: Company,
    policy: PolicyURL,
    html_bytes: bytes,
    date_str: str,
    root: Path = POLICIES_ROOT,
    extra_meta: dict[str, object] | None = None,
) -> SnapshotResult:
    """Write a snapshot for (company, policy) at `date_str` if content is new.

    Shared by live fetches and Wayback backfill. Deduplicates by comparing
    the sha256 of `html_bytes` against the most recent prior snapshot (by
    filename, which sorts chronologically). Also skips if a snapshot file
    for `date_str` already exists.
    """
    url = str(policy.url)
    policy_dir = root / company.slug / _policy_id(policy)

    if (policy_dir / f"{date_str}.html").exists():
        return SnapshotResult(
            company_slug=company.slug,
            policy_kind=policy.kind,
            url=url,
            snapshot_path=None,
            status="unchanged",
            detail=f"snapshot for {date_str} already exists",
        )

    sha256 = _sha256_bytes(html_bytes)
    prior_hash = _latest_prior_hash(policy_dir)
    if prior_hash == sha256:
        return SnapshotResult(
            company_slug=company.slug,
            policy_kind=policy.kind,
            url=url,
            snapshot_path=None,
            status="unchanged",
            detail=f"sha256 matches prior snapshot {prior_hash[:12]}",
        )

    html = html_bytes.decode("utf-8", errors="replace")
    text = _extract_text(html)
    meta: dict[str, object] = {
        "company_slug": company.slug,
        "policy_kind": policy.kind,
        "policy_label": policy.label,
        "policy_region": policy.region,
        "url": url,
        "snapshot_date": date_str,
        "fetched_at": datetime.now(UTC).isoformat(),
        "sha256": sha256,
        "byte_length": len(html_bytes),
        "text_length": len(text),
    }
    if extra_meta:
        meta.update(extra_meta)
    path = _write_snapshot(policy_dir, date_str, html_bytes, text, meta)
    log.info("Wrote snapshot %s", path)
    return SnapshotResult(
        company_slug=company.slug,
        policy_kind=policy.kind,
        url=url,
        snapshot_path=path,
        status="written",
        detail=f"sha256 {sha256[:12]}",
    )


def fetch_policy(
    client: PoliteClient,
    company: Company,
    policy: PolicyURL,
    *,
    root: Path = POLICIES_ROOT,
    now: datetime | None = None,
) -> SnapshotResult:
    """Fetch one policy URL and persist a snapshot if content has changed.

    Returns a SnapshotResult describing what happened. Does not raise on
    transport errors — they are captured into the result so callers can
    continue with the next policy.
    """
    url = str(policy.url)
    date_str = (now or datetime.now(UTC)).strftime("%Y-%m-%d")

    try:
        resp = client.get(url)
    except RobotsDisallowedError as err:
        log.warning("robots.txt blocked %s: %s", url, err)
        return SnapshotResult(
            company_slug=company.slug,
            policy_kind=policy.kind,
            url=url,
            snapshot_path=None,
            status="skipped",
            detail=f"robots.txt: {err}",
        )
    except httpx.HTTPError as err:
        log.error("HTTP error fetching %s: %s", url, err)
        return SnapshotResult(
            company_slug=company.slug,
            policy_kind=policy.kind,
            url=url,
            snapshot_path=None,
            status="error",
            detail=str(err),
        )

    return save_snapshot_if_changed(
        company=company,
        policy=policy,
        html_bytes=resp.content,
        date_str=date_str,
        root=root,
        extra_meta={
            "http_status": resp.status_code,
            "content_type": resp.headers.get("content-type"),
            "source": "live",
        },
    )


def fetch_all_policies(
    slugs: list[str] | None = None,
    *,
    client: PoliteClient | None = None,
    root: Path = POLICIES_ROOT,
) -> list[SnapshotResult]:
    """Fetch policies for the given companies (default: all registered ones)."""
    targets: list[Company]
    if slugs is None:
        targets = list(COMPANIES)
    else:
        targets = [get_company(s) for s in slugs]

    results: list[SnapshotResult] = []
    owned_client = client is None
    client_cm = client if client is not None else PoliteClient()
    if owned_client:
        client_cm.__enter__()
    try:
        for company in targets:
            for policy in company.policy_urls:
                result = fetch_policy(client_cm, company, policy, root=root)
                results.append(result)
    finally:
        if owned_client:
            client_cm.__exit__(None, None, None)
    return results
