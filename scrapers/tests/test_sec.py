"""Tests for the EDGAR scraper. No network calls."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
import pytest

from scrapers import sec
from scrapers.config import Company

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
        if url not in self._responses:
            raise httpx.HTTPError(f"unexpected url: {url}")
        return self._responses[url]


@pytest.fixture
def meta_company() -> Company:
    return Company(
        name="Meta",
        slug="meta",
        ticker="META",
        sec_cik="0001326801",
        policy_urls=[],
    )


def test_parse_recent_filings_filters_to_10k_10q() -> None:
    payload = json.loads((FIXTURES / "edgar_submissions.json").read_text())
    filings = sec._parse_recent_filings(payload)
    forms = [f.form for f in filings]
    assert forms == ["10-K", "10-Q"]
    assert filings[0].accession_number == "0001326801-25-000012"
    assert filings[0].primary_document == "meta-20241231.htm"


def test_extract_keyword_paragraphs_identifies_ai_mentions() -> None:
    html = (FIXTURES / "edgar_10k.html").read_text()
    matched, excerpts = sec.extract_keyword_paragraphs(html)
    assert any("generative ai" in m for m in matched)
    assert any("training data" in m for m in matched)
    assert any("foundation model" in m for m in matched) or any(
        "foundation model" in e["paragraph"].lower() for e in excerpts
    )
    # Non-matching paragraphs must be excluded.
    assert all(
        "Competition is intense" not in e["paragraph"] for e in excerpts
    ), "Generic competition paragraph should not match"


def test_extract_keyword_paragraphs_drops_short_fragments() -> None:
    html = "<p>AI.</p><p>Machine learning.</p>"
    matched, excerpts = sec.extract_keyword_paragraphs(html)
    # Both paragraphs are below the min-length filter.
    assert excerpts == []
    assert matched == []


def test_process_filing_writes_json_record(
    tmp_path: Path, meta_company: Company
) -> None:
    filing = sec.Filing(
        accession_number="0001326801-25-000012",
        form="10-K",
        filing_date="2025-02-01",
        report_date="2024-12-31",
        primary_document="meta-20241231.htm",
    )
    url = sec._archive_url(meta_company.sec_cik, filing)  # type: ignore[arg-type]
    html = (FIXTURES / "edgar_10k.html").read_text()
    client = _Client({url: _Resp(text=html)})

    record = sec.process_filing(
        client,  # type: ignore[arg-type]
        meta_company,
        filing,
        root=tmp_path,
    )

    assert record is not None
    out = tmp_path / "META" / "0001326801-25-000012.json"
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["company_slug"] == "meta"
    assert data["form"] == "10-K"
    assert data["matched_keywords"]
    assert data["excerpts"]


def test_process_filing_is_idempotent(tmp_path: Path, meta_company: Company) -> None:
    filing = sec.Filing(
        accession_number="0001326801-25-000012",
        form="10-K",
        filing_date="2025-02-01",
        report_date="2024-12-31",
        primary_document="meta-20241231.htm",
    )
    url = sec._archive_url(meta_company.sec_cik, filing)  # type: ignore[arg-type]
    html = (FIXTURES / "edgar_10k.html").read_text()
    client = _Client({url: _Resp(text=html)})

    first = sec.process_filing(
        client, meta_company, filing, root=tmp_path  # type: ignore[arg-type]
    )
    assert first is not None
    second = sec.process_filing(
        client, meta_company, filing, root=tmp_path  # type: ignore[arg-type]
    )
    assert second is None  # second run is a no-op
    # Only one HTTP call was made.
    assert client.calls.count(url) == 1
