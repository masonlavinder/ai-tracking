"""End-to-end test for the analysis pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from analysis.aggregate import run_pipeline

from .conftest import write_snapshot


EARLIER_TEXT = """
We collect information that you provide to us, including profile details and activity on our services across our family of apps.

We retain your personal data for up to 24 months after account closure, subject to legal obligations and regulatory requirements that apply.

We do not share your information with third parties except as described in this policy document and the linked supplementary notices.
"""

LATER_TEXT = """
We collect information that you provide to us, including profile details and activity on our services across our family of apps.

We may use your public posts and content to train our generative AI models, subject to the opt-out controls available in your settings.

We retain your personal data for up to 36 months after account closure, subject to legal obligations and regulatory requirements that apply.

We do not share your information with third parties except as described in this policy document and the linked supplementary notices.
"""


def test_run_pipeline_writes_all_artifacts(tmp_path: Path) -> None:
    policies_root = tmp_path / "policies"
    processed_root = tmp_path / "processed"

    write_snapshot(
        policies_root,
        "meta",
        "privacy_policy",
        "2026-01-01",
        EARLIER_TEXT,
        url="https://www.facebook.com/privacy/policy/",
        policy_label="Meta Privacy Policy",
    )
    write_snapshot(
        policies_root,
        "meta",
        "privacy_policy",
        "2026-03-01",
        LATER_TEXT,
        url="https://www.facebook.com/privacy/policy/",
        policy_label="Meta Privacy Policy",
    )

    stats = run_pipeline(
        policies_root=policies_root, processed_root=processed_root
    )
    assert stats["total_changes"] == 1
    # Every registered company gets listed, not just ones with changes.
    assert stats["companies"] >= 5

    # Top-level artifacts exist.
    for name in ("companies.json", "changes.json", "timeline.json"):
        assert (processed_root / name).exists()

    changes_json = json.loads((processed_root / "changes.json").read_text())
    assert "generated_at" in changes_json
    assert len(changes_json["changes"]) == 1
    change_summary = changes_json["changes"][0]
    assert change_summary["company_slug"] == "meta"
    assert "ai-training-expansion" in change_summary["tags"]
    assert change_summary["score"] >= 4  # should make the timeline

    # Per-change detail file has full paragraphs + breakdown.
    detail_path = processed_root / "changes" / f"{change_summary['id']}.json"
    assert detail_path.exists()
    detail = json.loads(detail_path.read_text())
    assert detail["added_paragraphs"]
    assert "score_breakdown" in detail
    assert detail["score_breakdown"]["total"] == change_summary["score"]

    # Timeline file respects threshold and is sorted.
    timeline = json.loads((processed_root / "timeline.json").read_text())
    assert timeline["threshold"] == 4
    assert all(c["score"] >= 4 for c in timeline["changes"])

    # Companies.json surfaces the change against Meta and empty lists elsewhere.
    companies = json.loads((processed_root / "companies.json").read_text())
    meta_entry = next(c for c in companies["companies"] if c["slug"] == "meta")
    assert meta_entry["total_changes"] == 1
    assert meta_entry["latest_snapshot_date"] == "2026-03-01"
    assert meta_entry["policies"], "policies list should include the detected stream"


def test_run_pipeline_is_idempotent(tmp_path: Path) -> None:
    policies_root = tmp_path / "policies"
    processed_root = tmp_path / "processed"
    write_snapshot(policies_root, "meta", "privacy_policy", "2026-01-01", EARLIER_TEXT)
    write_snapshot(policies_root, "meta", "privacy_policy", "2026-03-01", LATER_TEXT)

    first = run_pipeline(policies_root=policies_root, processed_root=processed_root)
    first_changes = (processed_root / "changes.json").read_text()

    second = run_pipeline(policies_root=policies_root, processed_root=processed_root)
    second_changes = (processed_root / "changes.json").read_text()

    assert first == second
    # generated_at changes each run, so strip that before comparing.
    first_payload = json.loads(first_changes)
    second_payload = json.loads(second_changes)
    first_payload.pop("generated_at")
    second_payload.pop("generated_at")
    assert first_payload == second_payload
