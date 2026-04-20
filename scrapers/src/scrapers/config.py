"""Central registry of companies and their data sources.

This module is the single source of truth for which companies are tracked,
which policy URLs belong to each, and which external identifiers
(SEC CIK, news query terms) downstream scrapers should use.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl

PolicyKind = Literal[
    "privacy_policy",
    "terms_of_service",
    "ai_terms",
    "data_usage",
    "cookie_policy",
]


class PolicyURL(BaseModel):
    """One policy page to snapshot for a company."""

    url: HttpUrl
    kind: PolicyKind
    label: str = Field(
        ...,
        description="Human-readable label used in the UI, e.g. 'Privacy Policy (US)'.",
    )
    region: str | None = Field(
        default=None,
        description="ISO-like region code, e.g. 'US', 'EU', 'ROW'. None = global.",
    )


class Company(BaseModel):
    """A company tracked by the project."""

    name: str
    slug: str = Field(..., pattern=r"^[a-z0-9-]+$")
    ticker: str | None = Field(
        default=None,
        description="Stock ticker, or None for private companies.",
    )
    sec_cik: str | None = Field(
        default=None,
        description="SEC CIK, zero-padded to 10 digits. None for private companies.",
    )
    policy_urls: list[PolicyURL]
    news_query_terms: list[str] = Field(
        default_factory=list,
        description="Search terms used when querying news sources for this company.",
    )


# Contact URL embedded in the User-Agent so scraped services can reach us.
PROJECT_USER_AGENT = (
    "AIPrivacyTracker/0.1 (+https://github.com/masonlavinder/ai-tracking)"
)

# Root of the repo, computed relative to this file: src/scrapers/config.py -> ../../..
REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = REPO_ROOT / "data"
RAW_ROOT = DATA_ROOT / "raw"
PROCESSED_ROOT = DATA_ROOT / "processed"


COMPANIES: list[Company] = [
    Company(
        name="Meta",
        slug="meta",
        ticker="META",
        sec_cik="0001326801",
        policy_urls=[
            # ?locale=en_US pins Facebook to the English version regardless
            # of IP geolocation; otherwise CI runners in various regions
            # have captured Finnish, Urdu, and Spanish copies.
            PolicyURL(
                url="https://www.facebook.com/privacy/policy/?locale=en_US",
                kind="privacy_policy",
                label="Meta Privacy Policy",
            ),
            PolicyURL(
                url="https://www.facebook.com/privacy/genai/?locale=en_US",
                kind="ai_terms",
                label="Meta Generative AI Terms",
            ),
        ],
        news_query_terms=["Meta", "Facebook", "Instagram"],
    ),
    Company(
        name="OpenAI",
        slug="openai",
        ticker=None,
        sec_cik=None,
        policy_urls=[
            PolicyURL(
                url="https://openai.com/policies/row-privacy-policy/",
                kind="privacy_policy",
                label="OpenAI Privacy Policy",
            ),
            PolicyURL(
                url="https://openai.com/policies/row-terms-of-use/",
                kind="terms_of_service",
                label="OpenAI Terms of Use",
            ),
        ],
        news_query_terms=["OpenAI", "ChatGPT"],
    ),
    Company(
        name="Anthropic",
        slug="anthropic",
        ticker=None,
        sec_cik=None,
        policy_urls=[
            PolicyURL(
                url="https://www.anthropic.com/legal/privacy",
                kind="privacy_policy",
                label="Anthropic Privacy Policy",
            ),
            PolicyURL(
                url="https://www.anthropic.com/legal/consumer-terms",
                kind="terms_of_service",
                label="Anthropic Consumer Terms",
            ),
        ],
        news_query_terms=["Anthropic", "Claude"],
    ),
    Company(
        name="Google",
        slug="google",
        ticker="GOOGL",
        sec_cik="0001652044",
        policy_urls=[
            PolicyURL(
                url="https://policies.google.com/privacy",
                kind="privacy_policy",
                label="Google Privacy Policy",
            ),
            PolicyURL(
                url="https://policies.google.com/terms/generative-ai",
                kind="ai_terms",
                label="Google Generative AI Additional Terms",
            ),
        ],
        news_query_terms=["Google", "Gemini", "Alphabet"],
    ),
    Company(
        name="Microsoft",
        slug="microsoft",
        ticker="MSFT",
        sec_cik="0000789019",
        policy_urls=[
            PolicyURL(
                url="https://privacy.microsoft.com/en-us/privacystatement",
                kind="privacy_policy",
                label="Microsoft Privacy Statement",
            ),
            PolicyURL(
                url="https://www.microsoft.com/en-us/servicesagreement",
                kind="terms_of_service",
                label="Microsoft Services Agreement",
            ),
        ],
        news_query_terms=["Microsoft", "Copilot"],
    ),
]


def get_company(slug: str) -> Company:
    """Return the company with the given slug or raise KeyError."""
    for company in COMPANIES:
        if company.slug == slug:
            return company
    raise KeyError(f"Unknown company slug: {slug!r}")


def all_slugs() -> list[str]:
    """Slugs of all registered companies, in registry order."""
    return [c.slug for c in COMPANIES]
