"""Tests for significance scoring."""

from __future__ import annotations

from analysis.models import ChangeRecord, ParagraphChange
from analysis.score import score_change


def _make_change(**kwargs: object) -> ChangeRecord:
    defaults: dict[str, object] = {
        "id": "x",
        "company_slug": "example",
        "company_name": "Example",
        "source_type": "policy",
        "policy_kind": "privacy_policy",
        "policy_label": "Example Privacy Policy",
        "url": "https://example.com/privacy",
        "from_date": "2026-01-01",
        "to_date": "2026-02-01",
        "date": "2026-02-01",
    }
    defaults.update(kwargs)
    return ChangeRecord(**defaults)  # type: ignore[arg-type]


def test_score_add_only_with_tags_and_content() -> None:
    change = _make_change(
        added_paragraphs=[
            "We may use your content to train our generative AI models across "
            "our family of products, consistent with user-level opt-out controls."
        ],
        tags=["ai-training-expansion", "opt-out-mechanism"],
    )
    breakdown = score_change(change)
    # +3 content, +4 tags (2 × 2), +2 add-only = 9
    assert breakdown.content == 3
    assert breakdown.tags == 4
    assert breakdown.add_only == 2
    assert breakdown.total == 9
    assert change.score == 9


def test_score_capped_at_10() -> None:
    change = _make_change(
        added_paragraphs=["We will now train our AI models on all your data."] * 1,
        tags=["a", "b", "c", "d", "e"],  # 5 tags × 2 = 10 already
    )
    breakdown = score_change(change)
    assert breakdown.total == 10


def test_score_modification_only_no_add_bonus() -> None:
    change = _make_change(
        modified_paragraphs=[
            ParagraphChange(
                before="We retain your data for up to 24 months after account closure "
                "subject to legal obligations applicable to our services.",
                after="We retain your data for up to 36 months after account closure "
                "subject to legal obligations applicable to our services.",
            )
        ],
        tags=["data-retention-change"],
    )
    breakdown = score_change(change)
    assert breakdown.add_only == 0  # modifications don't trigger the +2
    assert breakdown.content == 3
    assert breakdown.tags == 2
    assert breakdown.total == 5


def test_score_zero_for_empty_change() -> None:
    change = _make_change()
    breakdown = score_change(change)
    assert breakdown.total == 0


def test_score_heading_bonus() -> None:
    change = _make_change(
        added_paragraphs=[
            "AI and Your Data",  # heading-like
            "We train our models using public information from the internet and "
            "licensed datasets, not your private messages.",
        ],
        tags=["ai-training-expansion"],
    )
    breakdown = score_change(change)
    assert breakdown.heading_keyword == 1
