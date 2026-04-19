"""Sanity checks on the company registry."""

from __future__ import annotations

from scrapers.config import COMPANIES, all_slugs, get_company


def test_all_required_companies_present() -> None:
    slugs = set(all_slugs())
    assert {"meta", "openai", "anthropic", "google", "microsoft"} <= slugs


def test_slugs_are_unique() -> None:
    slugs = all_slugs()
    assert len(slugs) == len(set(slugs))


def test_each_company_has_at_least_one_policy_url() -> None:
    for company in COMPANIES:
        assert company.policy_urls, f"{company.slug} has no policy URLs"


def test_get_company_roundtrip() -> None:
    for slug in all_slugs():
        assert get_company(slug).slug == slug


def test_public_companies_have_cik() -> None:
    for slug in ("meta", "google", "microsoft"):
        company = get_company(slug)
        assert company.sec_cik is not None and len(company.sec_cik) == 10
        assert company.ticker is not None
