"""Minimal company metadata used by the analysis pipeline.

Duplicated from scrapers.config on purpose — the analysis project is
independent and only needs the small subset of fields used in summary
output. Keep in sync with `scrapers/src/scrapers/config.py`.
"""

from __future__ import annotations

from pydantic import BaseModel


class AnalysisCompany(BaseModel):
    slug: str
    name: str
    ticker: str | None = None
    sec_cik: str | None = None
    homepage_url: str | None = None


def _stock_url(ticker: str | None) -> str | None:
    """Yahoo Finance quote page URL for a ticker, or None."""
    if not ticker:
        return None
    return f"https://finance.yahoo.com/quote/{ticker}"


COMPANIES: list[AnalysisCompany] = [
    AnalysisCompany(
        slug="meta",
        name="Meta",
        ticker="META",
        sec_cik="0001326801",
        homepage_url="https://about.meta.com/",
    ),
    AnalysisCompany(
        slug="openai",
        name="OpenAI",
        homepage_url="https://openai.com/",
    ),
    AnalysisCompany(
        slug="anthropic",
        name="Anthropic",
        homepage_url="https://www.anthropic.com/",
    ),
    AnalysisCompany(
        slug="google",
        name="Google",
        ticker="GOOGL",
        sec_cik="0001652044",
        homepage_url="https://about.google/",
    ),
    AnalysisCompany(
        slug="microsoft",
        name="Microsoft",
        ticker="MSFT",
        sec_cik="0000789019",
        homepage_url="https://www.microsoft.com/about",
    ),
    AnalysisCompany(
        slug="apple",
        name="Apple",
        ticker="AAPL",
        sec_cik="0000320193",
        homepage_url="https://www.apple.com/",
    ),
    AnalysisCompany(
        slug="amazon",
        name="Amazon",
        ticker="AMZN",
        sec_cik="0001018724",
        homepage_url="https://www.aboutamazon.com/",
    ),
    AnalysisCompany(
        slug="reddit",
        name="Reddit",
        ticker="RDDT",
        sec_cik="0001713445",
        homepage_url="https://redditinc.com/",
    ),
    AnalysisCompany(
        slug="adobe",
        name="Adobe",
        ticker="ADBE",
        sec_cik="0000796343",
        homepage_url="https://www.adobe.com/",
    ),
    AnalysisCompany(
        slug="x",
        name="X",
        homepage_url="https://x.com/",
    ),
    AnalysisCompany(
        slug="linkedin",
        name="LinkedIn",
        homepage_url="https://about.linkedin.com/",
    ),
    AnalysisCompany(
        slug="tiktok",
        name="TikTok",
        homepage_url="https://www.tiktok.com/",
    ),
    AnalysisCompany(
        slug="snap",
        name="Snap",
        ticker="SNAP",
        sec_cik="0001564408",
        homepage_url="https://snap.com/",
    ),
    AnalysisCompany(
        slug="spotify",
        name="Spotify",
        ticker="SPOT",
        sec_cik="0001639920",
        homepage_url="https://www.spotify.com/",
    ),
    AnalysisCompany(
        slug="netflix",
        name="Netflix",
        ticker="NFLX",
        sec_cik="0001065280",
        homepage_url="https://www.netflix.com/",
    ),
    AnalysisCompany(
        slug="pinterest",
        name="Pinterest",
        ticker="PINS",
        sec_cik="0001506293",
        homepage_url="https://www.pinterest.com/",
    ),
    AnalysisCompany(
        slug="samsung",
        name="Samsung",
        homepage_url="https://www.samsung.com/",
    ),
    AnalysisCompany(
        slug="discord",
        name="Discord",
        homepage_url="https://discord.com/",
    ),
    AnalysisCompany(
        slug="uber",
        name="Uber",
        ticker="UBER",
        sec_cik="0001543151",
        homepage_url="https://www.uber.com/",
    ),
    AnalysisCompany(
        slug="paypal",
        name="PayPal",
        ticker="PYPL",
        sec_cik="0001633917",
        homepage_url="https://www.paypal.com/",
    ),
]


COMPANIES_BY_SLUG: dict[str, AnalysisCompany] = {c.slug: c for c in COMPANIES}


def get_company(slug: str) -> AnalysisCompany:
    if slug not in COMPANIES_BY_SLUG:
        raise KeyError(f"Unknown company slug: {slug!r}")
    return COMPANIES_BY_SLUG[slug]
