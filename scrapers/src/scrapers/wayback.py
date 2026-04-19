"""Wayback Machine backfill for policy URLs.

For each company's policy URL, list historical captures from the Internet
Archive's CDX API at roughly monthly cadence over the last 24 months,
fetch the raw capture body (using the `id_` flag to skip Wayback's chrome),
and feed each capture through `policies.save_snapshot_if_changed` with its
original capture date so the `data/raw/policies/` tree is seeded with
history on first run.

Intended to be run once per policy URL. Subsequent runs re-check and are
cheap because CDX results that match existing snapshots short-circuit.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx

from .config import COMPANIES, Company, PolicyURL, get_company
from .http import PoliteClient
from .policies import POLICIES_ROOT, SnapshotResult, save_snapshot_if_changed

log = logging.getLogger(__name__)

CDX_URL = "https://web.archive.org/cdx/search/cdx"
WAYBACK_RAW_URL_TEMPLATE = "https://web.archive.org/web/{timestamp}id_/{url}"


@dataclass
class Snapshot:
    """A single Wayback capture."""

    timestamp: str  # YYYYMMDDHHMMSS
    original_url: str
    mimetype: str
    statuscode: str
    digest: str

    @property
    def capture_date(self) -> str:
        """Date portion of the timestamp as YYYY-MM-DD."""
        return f"{self.timestamp[0:4]}-{self.timestamp[4:6]}-{self.timestamp[6:8]}"


def parse_cdx_rows(payload: list[list[str]]) -> list[Snapshot]:
    """Parse a CDX JSON response into Snapshot objects.

    The first row is the header row (`urlkey,timestamp,original,...`).
    """
    if not payload:
        return []
    header = payload[0]
    idx = {name: i for i, name in enumerate(header)}

    required = ("timestamp", "original", "mimetype", "statuscode", "digest")
    for name in required:
        if name not in idx:
            log.warning("CDX response missing expected column %r", name)
            return []

    snapshots: list[Snapshot] = []
    for row in payload[1:]:
        try:
            snapshots.append(
                Snapshot(
                    timestamp=row[idx["timestamp"]],
                    original_url=row[idx["original"]],
                    mimetype=row[idx["mimetype"]],
                    statuscode=row[idx["statuscode"]],
                    digest=row[idx["digest"]],
                )
            )
        except IndexError:
            continue
    return snapshots


def list_snapshots(
    client: PoliteClient,
    url: str,
    *,
    months_back: int = 24,
    now: datetime | None = None,
) -> list[Snapshot]:
    """Query CDX for one snapshot per month in the last `months_back` months."""
    now = now or datetime.now(UTC)
    start = now - timedelta(days=months_back * 31)
    params = {
        "url": url,
        "from": start.strftime("%Y%m%d"),
        "to": now.strftime("%Y%m%d"),
        "output": "json",
        "filter": "statuscode:200",
        "collapse": "timestamp:6",  # one capture per YYYYMM
    }
    try:
        resp = client.get(CDX_URL, params=params)
    except httpx.HTTPError as err:
        log.error("CDX query failed for %s: %s", url, err)
        return []
    try:
        payload = resp.json()
    except json.JSONDecodeError as err:
        log.error("CDX returned non-JSON for %s: %s", url, err)
        return []
    return parse_cdx_rows(payload)


def fetch_raw_capture(client: PoliteClient, snapshot: Snapshot) -> bytes | None:
    """Fetch the raw content of a Wayback capture."""
    url = WAYBACK_RAW_URL_TEMPLATE.format(
        timestamp=snapshot.timestamp, url=snapshot.original_url
    )
    try:
        resp = client.get(url)
    except httpx.HTTPError as err:
        log.error("Wayback fetch failed for %s: %s", url, err)
        return None
    return resp.content


def backfill_policy(
    client: PoliteClient,
    company: Company,
    policy: PolicyURL,
    *,
    root: Path = POLICIES_ROOT,
    months_back: int = 24,
) -> list[SnapshotResult]:
    """Backfill historical snapshots for one policy URL."""
    snapshots = list_snapshots(
        client, str(policy.url), months_back=months_back
    )
    results: list[SnapshotResult] = []
    for snap in snapshots:
        content = fetch_raw_capture(client, snap)
        if content is None:
            continue
        result = save_snapshot_if_changed(
            company=company,
            policy=policy,
            html_bytes=content,
            date_str=snap.capture_date,
            root=root,
            extra_meta={
                "source": "wayback",
                "wayback_timestamp": snap.timestamp,
                "wayback_digest": snap.digest,
                "http_status": int(snap.statuscode) if snap.statuscode.isdigit() else None,
                "content_type": snap.mimetype,
            },
        )
        results.append(result)
    return results


def backfill_all(
    slugs: list[str] | None = None,
    *,
    client: PoliteClient | None = None,
    root: Path = POLICIES_ROOT,
    months_back: int = 24,
) -> list[SnapshotResult]:
    """Run Wayback backfill for every policy URL of the selected companies."""
    targets = [get_company(s) for s in slugs] if slugs else list(COMPANIES)

    owned = client is None
    cm = client if client is not None else PoliteClient()
    if owned:
        cm.__enter__()
    try:
        results: list[SnapshotResult] = []
        for company in targets:
            for policy in company.policy_urls:
                results.extend(
                    backfill_policy(
                        cm, company, policy, root=root, months_back=months_back
                    )
                )
        return results
    finally:
        if owned:
            cm.__exit__(None, None, None)
