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
]


COMPANIES_BY_SLUG: dict[str, AnalysisCompany] = {c.slug: c for c in COMPANIES}


def get_company(slug: str) -> AnalysisCompany:
    if slug not in COMPANIES_BY_SLUG:
        raise KeyError(f"Unknown company slug: {slug!r}")
    return COMPANIES_BY_SLUG[slug]
