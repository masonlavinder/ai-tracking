"""Tests for paragraph-level snapshot diffing."""

from __future__ import annotations

from pathlib import Path

from analysis.diff import diff_all, iter_snapshot_pairs

from .conftest import write_snapshot


EARLIER_TEXT = """
We collect information that you provide to us, including your profile details, content you share, and activity on our services.

We retain your personal data for up to 24 months after account closure, subject to legal obligations.

We do not share your information with third parties except as described in this policy.
"""

LATER_TEXT = """
We collect information that you provide to us, including your profile details, content you share, and activity on our services.

We may use your public posts and content to train our generative AI models, subject to the opt-out controls in settings.

We retain your personal data for up to 36 months after account closure, subject to legal obligations.

We do not share your information with third parties except as described in this policy.
"""


def test_iter_snapshot_pairs_yields_consecutive_dates(tmp_path: Path) -> None:
    write_snapshot(tmp_path, "example", "privacy_policy", "2026-01-01", EARLIER_TEXT)
    write_snapshot(tmp_path, "example", "privacy_policy", "2026-02-01", EARLIER_TEXT)
    write_snapshot(tmp_path, "example", "privacy_policy", "2026-03-01", LATER_TEXT)

    pairs = list(iter_snapshot_pairs(tmp_path))
    assert [(p.from_date, p.to_date) for p in pairs] == [
        ("2026-01-01", "2026-02-01"),
        ("2026-02-01", "2026-03-01"),
    ]


def test_diff_all_detects_added_and_modified_paragraphs(tmp_path: Path) -> None:
    write_snapshot(tmp_path, "example", "privacy_policy", "2026-01-01", EARLIER_TEXT)
    write_snapshot(tmp_path, "example", "privacy_policy", "2026-03-01", LATER_TEXT)

    changes = diff_all(tmp_path)
    assert len(changes) == 1
    change = changes[0]
    assert change.id == "example-privacy_policy-2026-01-01-2026-03-01"
    assert change.from_date == "2026-01-01"
    assert change.to_date == "2026-03-01"
    assert change.source_type == "policy"

    # The AI-training paragraph is new and should be an addition.
    joined_added = " ".join(change.added_paragraphs).lower()
    assert "generative ai" in joined_added

    # The retention paragraph changed from 24 to 36 months -> modification.
    assert any(
        "24 months" in m.before and "36 months" in m.after
        for m in change.modified_paragraphs
    )


def test_diff_all_skips_identical_snapshots(tmp_path: Path) -> None:
    write_snapshot(tmp_path, "example", "privacy_policy", "2026-01-01", EARLIER_TEXT)
    write_snapshot(tmp_path, "example", "privacy_policy", "2026-02-01", EARLIER_TEXT)

    changes = diff_all(tmp_path)
    assert changes == []
