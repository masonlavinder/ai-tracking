"""Tests for the Wayback Machine backfill. No network calls."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
import pytest

from scrapers import wayback
from scrapers.config import Company, PolicyURL

FIXTURES = Path(__file__).parent / "fixtures"


@dataclass
class _Resp:
    text: str = ""
    content: bytes = b""
    status_code: int = 200

    def json(self) -> Any:
        return json.loads(self.text or self.content.decode("utf-8"))


class _Client:
    def __init__(self, response_map: dict[str, _Resp]) -> None:
        self._responses = response_map
        self.calls: list[str] = []

    def get(self, url: str, *, params: dict[str, str] | None = None) -> _Resp:
        self.calls.append(url)
        if url in self._responses:
            return self._responses[url]
        # Try matching ignoring params
        raise httpx.HTTPError(f"unexpected url: {url}")


@pytest.fixture
def example_company() -> Company:
    return Company(
        name="Example",
        slug="example",
        policy_urls=[
            PolicyURL(
                url="https://example.com/privacy",
                kind="privacy_policy",
                label="Example Privacy Policy",
            )
        ],
    )


def test_parse_cdx_rows_returns_snapshots() -> None:
    payload = json.loads((FIXTURES / "cdx_response.json").read_text())
    snapshots = wayback.parse_cdx_rows(payload)
    assert len(snapshots) == 3
    first = snapshots[0]
    assert first.timestamp == "20240115120000"
    assert first.capture_date == "2024-01-15"
    assert first.statuscode == "200"


def test_parse_cdx_rows_handles_empty() -> None:
    assert wayback.parse_cdx_rows([]) == []


def test_backfill_policy_writes_dated_snapshots(
    tmp_path: Path, example_company: Company
) -> None:
    cdx_payload = (FIXTURES / "cdx_response.json").read_bytes()
    body_a = b"<html><body><p>Original privacy policy content here.</p></body></html>"
    body_b = b"<html><body><p>Updated privacy policy content here for AI.</p></body></html>"

    # Jan = body_a (new). Feb = body_a again (unchanged vs Jan).
    # Mar = body_b (new content after Feb).
    responses = {
        wayback.CDX_URL: _Resp(content=cdx_payload),
        wayback.WAYBACK_RAW_URL_TEMPLATE.format(
            timestamp="20240115120000", url="https://example.com/privacy"
        ): _Resp(content=body_a),
        wayback.WAYBACK_RAW_URL_TEMPLATE.format(
            timestamp="20240215090000", url="https://example.com/privacy"
        ): _Resp(content=body_a),
        wayback.WAYBACK_RAW_URL_TEMPLATE.format(
            timestamp="20240315100000", url="https://example.com/privacy"
        ): _Resp(content=body_b),
    }
    client = _Client(responses)

    results = wayback.backfill_policy(
        client,  # type: ignore[arg-type]
        example_company,
        example_company.policy_urls[0],
        root=tmp_path,
    )
    statuses = [r.status for r in results]
    assert statuses.count("written") == 2
    assert statuses.count("unchanged") == 1

    policy_dir = tmp_path / "example" / "privacy_policy"
    dates = sorted(p.stem for p in policy_dir.glob("*.html"))
    assert dates == ["2024-01-15", "2024-03-15"]

    # Meta carries the wayback markers.
    meta = json.loads((policy_dir / "2024-01-15.meta.json").read_text())
    assert meta["source"] == "wayback"
    assert meta["wayback_timestamp"] == "20240115120000"
