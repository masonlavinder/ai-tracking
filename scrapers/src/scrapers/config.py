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
    Company(
        name="Apple",
        slug="apple",
        ticker="AAPL",
        sec_cik="0000320193",
        policy_urls=[
            PolicyURL(
                url="https://www.apple.com/legal/privacy/en-ww/",
                kind="privacy_policy",
                label="Apple Privacy Policy",
            ),
        ],
        news_query_terms=["Apple", "Apple Intelligence", "Siri"],
    ),
    Company(
        name="Amazon",
        slug="amazon",
        ticker="AMZN",
        sec_cik="0001018724",
        policy_urls=[
            PolicyURL(
                url="https://www.amazon.com/gp/help/customer/display.html?nodeId=GX7NJQ4ZB8MHFRNJ",
                kind="privacy_policy",
                label="Amazon Privacy Notice",
            ),
            PolicyURL(
                url="https://aws.amazon.com/privacy/",
                kind="privacy_policy",
                label="AWS Privacy Notice",
                region="AWS",
            ),
        ],
        news_query_terms=["Amazon", "AWS", "Alexa", "Bedrock"],
    ),
    Company(
        name="Reddit",
        slug="reddit",
        ticker="RDDT",
        sec_cik="0001713445",
        policy_urls=[
            PolicyURL(
                url="https://www.redditinc.com/policies/privacy-policy",
                kind="privacy_policy",
                label="Reddit Privacy Policy",
            ),
            PolicyURL(
                url="https://www.redditinc.com/policies/user-agreement",
                kind="terms_of_service",
                label="Reddit User Agreement",
            ),
        ],
        news_query_terms=["Reddit"],
    ),
    Company(
        name="Adobe",
        slug="adobe",
        ticker="ADBE",
        sec_cik="0000796343",
        policy_urls=[
            PolicyURL(
                url="https://www.adobe.com/privacy/policy.html",
                kind="privacy_policy",
                label="Adobe Privacy Policy",
            ),
            PolicyURL(
                url="https://www.adobe.com/legal/licenses-terms/adobe-gen-ai-user-guidelines.html",
                kind="ai_terms",
                label="Adobe Generative AI User Guidelines",
            ),
        ],
        news_query_terms=["Adobe", "Firefly"],
    ),
    Company(
        name="X",
        slug="x",
        ticker=None,
        sec_cik=None,
        policy_urls=[
            PolicyURL(
                url="https://x.com/en/privacy",
                kind="privacy_policy",
                label="X Privacy Policy",
            ),
            PolicyURL(
                url="https://x.ai/legal/privacy-policy",
                kind="privacy_policy",
                label="xAI (Grok) Privacy Policy",
                region="xAI",
            ),
        ],
        news_query_terms=["Twitter", "xAI", "Grok"],
    ),
    Company(
        name="LinkedIn",
        slug="linkedin",
        ticker=None,
        sec_cik=None,
        policy_urls=[
            PolicyURL(
                url="https://www.linkedin.com/legal/privacy-policy",
                kind="privacy_policy",
                label="LinkedIn Privacy Policy",
            ),
        ],
        news_query_terms=["LinkedIn"],
    ),
    Company(
        name="TikTok",
        slug="tiktok",
        ticker=None,
        sec_cik=None,
        policy_urls=[
            PolicyURL(
                url="https://www.tiktok.com/legal/page/us/privacy-policy/en",
                kind="privacy_policy",
                label="TikTok Privacy Policy (US)",
                region="US",
            ),
            PolicyURL(
                url="https://www.tiktok.com/legal/page/row/privacy-policy/en",
                kind="privacy_policy",
                label="TikTok Privacy Policy (ROW)",
                region="ROW",
            ),
        ],
        news_query_terms=["TikTok", "ByteDance"],
    ),
    Company(
        name="Snap",
        slug="snap",
        ticker="SNAP",
        sec_cik="0001564408",
        policy_urls=[
            PolicyURL(
                url="https://values.snap.com/privacy/privacy-policy",
                kind="privacy_policy",
                label="Snap Privacy Policy",
            ),
        ],
        news_query_terms=["Snapchat", "Snap Inc", "My AI"],
    ),
    Company(
        name="Spotify",
        slug="spotify",
        ticker="SPOT",
        sec_cik="0001639920",
        policy_urls=[
            PolicyURL(
                url="https://www.spotify.com/us/legal/privacy-policy/",
                kind="privacy_policy",
                label="Spotify Privacy Policy",
                region="US",
            ),
        ],
        news_query_terms=["Spotify"],
    ),
    Company(
        name="Netflix",
        slug="netflix",
        ticker="NFLX",
        sec_cik="0001065280",
        policy_urls=[
            PolicyURL(
                url="https://help.netflix.com/legal/privacy",
                kind="privacy_policy",
                label="Netflix Privacy Statement",
            ),
        ],
        news_query_terms=["Netflix"],
    ),
    Company(
        name="Pinterest",
        slug="pinterest",
        ticker="PINS",
        sec_cik="0001506293",
        policy_urls=[
            PolicyURL(
                url="https://policy.pinterest.com/en/privacy-policy",
                kind="privacy_policy",
                label="Pinterest Privacy Policy",
            ),
        ],
        news_query_terms=["Pinterest"],
    ),
    Company(
        name="Samsung",
        slug="samsung",
        ticker=None,
        sec_cik=None,
        policy_urls=[
            PolicyURL(
                url="https://www.samsung.com/us/account/privacy-policy/",
                kind="privacy_policy",
                label="Samsung Privacy Policy (US)",
                region="US",
            ),
        ],
        news_query_terms=["Samsung", "Galaxy AI", "Bixby"],
    ),
    Company(
        name="Discord",
        slug="discord",
        ticker=None,
        sec_cik=None,
        policy_urls=[
            PolicyURL(
                url="https://discord.com/privacy",
                kind="privacy_policy",
                label="Discord Privacy Policy",
            ),
        ],
        news_query_terms=["Discord"],
    ),
    Company(
        name="Uber",
        slug="uber",
        ticker="UBER",
        sec_cik="0001543151",
        policy_urls=[
            PolicyURL(
                url="https://privacy.uber.com/policy/",
                kind="privacy_policy",
                label="Uber Privacy Notice",
            ),
        ],
        news_query_terms=["Uber"],
    ),
    Company(
        name="PayPal",
        slug="paypal",
        ticker="PYPL",
        sec_cik="0001633917",
        policy_urls=[
            PolicyURL(
                url="https://www.paypal.com/us/legalhub/privacy-full",
                kind="privacy_policy",
                label="PayPal Privacy Statement (US)",
                region="US",
            ),
        ],
        news_query_terms=["PayPal", "Venmo"],
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
