"""Tests for regulatory scrapers. No network calls."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from scrapers import regulatory

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_ftc_rss_filters_to_ai_privacy_items() -> None:
    xml = (FIXTURES / "ftc_rss.xml").read_bytes()
    records = regulatory.parse_ftc_rss(xml)
    titles = [r.title for r in records]

    assert any("AI Chatbot" in t for t in titles)
    assert any("Biometric" in t for t in titles)
    # The unrelated grocery merger must be filtered out.
    assert not any("Grocery" in t for t in titles)

    for r in records:
        assert r.source == "ftc"
        assert r.url.startswith("https://")
        assert r.published_at  # non-empty


def test_write_records_creates_dated_json(tmp_path: Path) -> None:
    records = [
        regulatory.RegulatoryRecord(
            source="ftc",
            title="Test",
            url="https://example.org/a",
            published_at="2026-03-04T17:00:00+00:00",
            body_excerpt="privacy stuff",
        )
    ]
    path = regulatory._write_records(
        "ftc", records, root=tmp_path, today=date(2026, 4, 19)
    )
    assert path is not None
    assert path == tmp_path / "ftc" / "2026-04-19.json"
    payload = json.loads(path.read_text())
    assert payload[0]["source"] == "ftc"
    assert payload[0]["title"] == "Test"


def test_write_records_skips_empty_list(tmp_path: Path) -> None:
    out = regulatory._write_records("ftc", [], root=tmp_path)
    assert out is None
    assert not (tmp_path / "ftc").exists()


def test_parse_eu_commission_extracts_press_links() -> None:
    html = """
    <html><body>
      <div class="card"><a href="/commission/presscorner/detail/en/IP_26_100">
        AI Act enforcement begins</a>
        <time datetime="2026-03-14">14 March 2026</time>
      </div>
      <div class="card"><a href="/commission/presscorner/detail/en/IP_26_101">
        Agricultural policy update</a>
        <time datetime="2026-03-15">15 March 2026</time>
      </div>
    </body></html>
    """
    records = regulatory.parse_eu_commission(html)
    titles = [r.title for r in records]
    assert any("AI Act" in t for t in titles)
    assert not any("Agricultural" in t for t in titles)


def test_parse_california_ag_extracts_news_items() -> None:
    html = """
    <html><body>
      <article>
        <a href="/news/ca-ag-privacy-enforcement">Attorney General Announces Privacy Enforcement</a>
        <time datetime="2026-03-10">March 10, 2026</time>
        <p>Enforcement action related to consumer personal data.</p>
      </article>
      <article>
        <a href="/news/wildfire-response">Attorney General Announces Wildfire Response Team</a>
        <time datetime="2026-03-11">March 11, 2026</time>
        <p>Emergency response.</p>
      </article>
    </body></html>
    """
    records = regulatory.parse_california_ag(html)
    titles = [r.title for r in records]
    assert any("Privacy Enforcement" in t for t in titles)
    assert not any("Wildfire" in t for t in titles)
