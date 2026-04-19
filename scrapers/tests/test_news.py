"""Tests for the GDELT news scraper. No network calls."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from scrapers import news
from scrapers.config import Company

FIXTURES = Path(__file__).parent / "fixtures"


def test_build_query_combines_terms_with_qualifier() -> None:
    company = Company(
        name="Meta",
        slug="meta",
        policy_urls=[],
        news_query_terms=["Meta", "Facebook"],
    )
    q = news.build_query(company)
    assert '"Meta"' in q
    assert '"Facebook"' in q
    assert "AND" in q
    assert "artificial intelligence" in q or '"AI"' in q


def test_parse_gdelt_response_drops_malformed_and_converts_timestamps() -> None:
    payload = json.loads((FIXTURES / "gdelt_response.json").read_text())
    records = news.parse_gdelt_response(payload)
    assert len(records) == 2
    first = records[0]
    assert first.url.startswith("https://")
    assert first.title
    assert first.seen_at.startswith("2026-03-15")
    assert first.tone == -1.5
    assert first.source_domain == "example.com"


def test_write_company_news_is_metadata_only(tmp_path: Path) -> None:
    company = Company(name="Meta", slug="meta", policy_urls=[])
    records = [
        news.NewsRecord(
            url="https://example.com/a",
            title="Headline",
            source_domain="example.com",
            language="English",
            country="United States",
            seen_at="2026-03-15T12:00:00+00:00",
            tone=-1.0,
        )
    ]
    path = news.write_company_news(
        company, records, root=tmp_path, today=date(2026, 4, 19)
    )
    assert path is not None
    data = json.loads(path.read_text())
    assert data[0]["url"] == "https://example.com/a"
    # The record must contain metadata only — no body text field.
    assert set(data[0].keys()) == {
        "url",
        "title",
        "source_domain",
        "language",
        "country",
        "seen_at",
        "tone",
    }


def test_write_company_news_skips_when_empty(tmp_path: Path) -> None:
    company = Company(name="Meta", slug="meta", policy_urls=[])
    assert news.write_company_news(company, [], root=tmp_path) is None
    assert not (tmp_path / "meta").exists()
