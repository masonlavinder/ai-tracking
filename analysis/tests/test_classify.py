"""Tests for rule-based classification."""

from __future__ import annotations

from analysis.classify import classify_change, load_rules
from analysis.models import ChangeRecord, ParagraphChange


def _make_change(
    added: list[str] | None = None,
    modified: list[ParagraphChange] | None = None,
    removed: list[str] | None = None,
) -> ChangeRecord:
    return ChangeRecord(
        id="x",
        company_slug="example",
        company_name="Example",
        source_type="policy",
        policy_kind="privacy_policy",
        policy_label="Example Privacy Policy",
        url="https://example.com/privacy",
        from_date="2026-01-01",
        to_date="2026-02-01",
        date="2026-02-01",
        added_paragraphs=added or [],
        modified_paragraphs=modified or [],
        removed_paragraphs=removed or [],
    )


def test_classify_detects_ai_training_expansion() -> None:
    change = _make_change(
        added=[
            "We may use your public content to train our generative AI models "
            "across our family of apps."
        ]
    )
    tags = classify_change(change)
    assert "ai-training-expansion" in tags


def test_classify_skips_removed_paragraphs() -> None:
    change = _make_change(
        removed=[
            "We may use your public content to train our generative AI models."
        ],
        added=["We do not collect biometric information from anyone."],
    )
    tags = classify_change(change)
    assert "ai-training-expansion" not in tags
    assert "biometric-facial" in tags


def test_classify_requires_nearby_for_training_keyword() -> None:
    change = _make_change(
        added=["We provide annual employee training on workplace safety."]
    )
    tags = classify_change(change)
    assert "ai-training-expansion" not in tags


def test_classify_detects_biometric_and_minors_together() -> None:
    change = _make_change(
        added=[
            "We do not collect biometric identifiers from users under 16. "
            "Children cannot create accounts on our services."
        ]
    )
    tags = classify_change(change)
    assert "biometric-facial" in tags
    assert "minors" in tags


def test_classify_all_rules_compile() -> None:
    # Smoke check that the YAML rule file is parseable and each rule has at
    # least one compiled pattern.
    rules = load_rules()
    assert len(rules) >= 5
    for rule in rules:
        assert rule.patterns, f"Rule {rule.tag} has no compiled patterns"
