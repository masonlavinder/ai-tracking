"""Smoke tests for the policy scraper.

These tests never touch the network. They substitute a fake client that
returns a fixture HTML body and assert that snapshot files get written
in the expected layout.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import pytest

from scrapers import policies
from scrapers.config import Company, PolicyURL

FIXTURES = Path(__file__).parent / "fixtures"


@dataclass
class _FakeResponse:
    content: bytes
    status_code: int = 200
    headers: dict[str, str] | None = None
    encoding: str | None = "utf-8"

    def __post_init__(self) -> None:
        if self.headers is None:
            self.headers = {"content-type": "text/html; charset=utf-8"}


class _FakeClient:
    """Stand-in for PoliteClient that returns preset responses."""

    def __init__(self, response_map: dict[str, _FakeResponse]) -> None:
        self._responses = response_map
        self.calls: list[str] = []

    def get(self, url: str) -> Any:
        self.calls.append(url)
        if url not in self._responses:
            raise httpx.HTTPError(f"unexpected url: {url}")
        return self._responses[url]


@pytest.fixture
def sample_html() -> bytes:
    return (FIXTURES / "sample_policy.html").read_bytes()


@pytest.fixture
def company() -> Company:
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


def test_fetch_policy_writes_snapshot_trio(
    tmp_path: Path, sample_html: bytes, company: Company
) -> None:
    client = _FakeClient({"https://example.com/privacy": _FakeResponse(sample_html)})
    result = policies.fetch_policy(
        client,  # type: ignore[arg-type]
        company,
        company.policy_urls[0],
        root=tmp_path,
        now=datetime(2026, 4, 19, tzinfo=UTC),
    )

    assert result.status == "written"
    policy_dir = tmp_path / "example" / "privacy_policy"
    html_path = policy_dir / "2026-04-19.html"
    text_path = policy_dir / "2026-04-19.txt"
    meta_path = policy_dir / "2026-04-19.meta.json"

    assert html_path.exists()
    assert text_path.exists()
    assert meta_path.exists()

    assert html_path.read_bytes() == sample_html
    text = text_path.read_text(encoding="utf-8")
    assert "AI model training" in text or "generative AI" in text

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["company_slug"] == "example"
    assert meta["policy_kind"] == "privacy_policy"
    assert meta["http_status"] == 200
    assert len(meta["sha256"]) == 64


def test_fetch_policy_skips_unchanged_content(
    tmp_path: Path, sample_html: bytes, company: Company
) -> None:
    client = _FakeClient({"https://example.com/privacy": _FakeResponse(sample_html)})

    first = policies.fetch_policy(
        client,  # type: ignore[arg-type]
        company,
        company.policy_urls[0],
        root=tmp_path,
        now=datetime(2026, 4, 18, tzinfo=UTC),
    )
    assert first.status == "written"

    second = policies.fetch_policy(
        client,  # type: ignore[arg-type]
        company,
        company.policy_urls[0],
        root=tmp_path,
        now=datetime(2026, 4, 19, tzinfo=UTC),
    )
    assert second.status == "unchanged"
    # Only one dated snapshot should exist.
    assert sorted(
        p.name for p in (tmp_path / "example" / "privacy_policy").glob("*.html")
    ) == ["2026-04-18.html"]


def test_fetch_policy_writes_new_snapshot_when_content_changes(
    tmp_path: Path, sample_html: bytes, company: Company
) -> None:
    modified = sample_html.replace(b"24 months", b"36 months")
    client_v1 = _FakeClient({"https://example.com/privacy": _FakeResponse(sample_html)})
    client_v2 = _FakeClient({"https://example.com/privacy": _FakeResponse(modified)})

    policies.fetch_policy(
        client_v1,  # type: ignore[arg-type]
        company,
        company.policy_urls[0],
        root=tmp_path,
        now=datetime(2026, 4, 18, tzinfo=UTC),
    )
    second = policies.fetch_policy(
        client_v2,  # type: ignore[arg-type]
        company,
        company.policy_urls[0],
        root=tmp_path,
        now=datetime(2026, 4, 19, tzinfo=UTC),
    )
    assert second.status == "written"

    htmls = sorted(
        p.name for p in (tmp_path / "example" / "privacy_policy").glob("*.html")
    )
    assert htmls == ["2026-04-18.html", "2026-04-19.html"]


def test_extract_text_strips_scripts_and_returns_body_text() -> None:
    html = (
        "<html><body><p>Hello world, this is body content.</p>"
        "<script>x=1</script></body></html>"
    )
    text = policies._extract_text(html)
    assert "Hello world" in text
    assert "x=1" not in text


def test_extract_text_bs4_fallback_when_trafilatura_empty() -> None:
    # Very short / odd input where trafilatura typically returns nothing;
    # we fall back to BeautifulSoup stripping.
    html = "<html><body><h1>Hi</h1></body></html>"
    text = policies._extract_text(html)
    assert "Hi" in text
