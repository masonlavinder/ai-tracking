"""End-to-end enrichment behavior: reuse, budget, gating."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from analysis import aggregate, llm
from analysis.models import ChangeRecord

from .conftest import write_snapshot


EARLIER = """
We collect information that you provide to us, including profile details and activity on our services across our family of apps.

We retain your personal data for up to 24 months after account closure, subject to legal obligations and regulatory requirements that apply.
"""

LATER = """
We collect information that you provide to us, including profile details and activity on our services across our family of apps.

We may use your public posts and content to train our generative AI models, subject to the opt-out controls available in your settings.

We retain your personal data for up to 36 months after account closure, subject to legal obligations and regulatory requirements that apply.
"""


def _setup_two_snapshots(tmp_path: Path) -> tuple[Path, Path]:
    policies_root = tmp_path / "policies"
    processed_root = tmp_path / "processed"
    write_snapshot(policies_root, "meta", "privacy_policy", "2026-01-01", EARLIER)
    write_snapshot(policies_root, "meta", "privacy_policy", "2026-03-01", LATER)
    return policies_root, processed_root


def test_run_pipeline_without_enrich_keeps_prior_summary(tmp_path: Path) -> None:
    policies_root, processed_root = _setup_two_snapshots(tmp_path)
    aggregate.run_pipeline(
        policies_root=policies_root, processed_root=processed_root
    )

    change_files = list((processed_root / "changes").glob("*.json"))
    assert len(change_files) == 1
    # Pretend a prior run already produced a summary.
    detail = json.loads(change_files[0].read_text())
    detail["llm_summary"] = "A prior summary we shouldn't lose."
    change_files[0].write_text(json.dumps(detail, indent=2))

    aggregate.run_pipeline(
        policies_root=policies_root,
        processed_root=processed_root,
        enrich_with_llm=False,
    )

    after = json.loads(change_files[0].read_text())
    assert after["llm_summary"] == "A prior summary we shouldn't lose."


def test_run_pipeline_with_enrich_calls_llm_only_for_new_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    policies_root, processed_root = _setup_two_snapshots(tmp_path)

    calls: list[str] = []

    def fake_generate(change: ChangeRecord, **_kwargs: Any) -> str:
        calls.append(change.id)
        return f"summary for {change.id}"

    monkeypatch.setattr(aggregate, "generate_summary", fake_generate)

    stats = aggregate.run_pipeline(
        policies_root=policies_root,
        processed_root=processed_root,
        enrich_with_llm=True,
    )
    assert stats["llm_calls"] == 1
    assert len(calls) == 1

    change_files = list((processed_root / "changes").glob("*.json"))
    detail = json.loads(change_files[0].read_text())
    assert detail["llm_summary"].startswith("summary for ")

    # Second run should reuse — no additional calls.
    calls.clear()
    stats = aggregate.run_pipeline(
        policies_root=policies_root,
        processed_root=processed_root,
        enrich_with_llm=True,
    )
    assert stats["llm_calls"] == 0
    assert calls == []


def test_run_pipeline_respects_llm_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    policies_root, processed_root = _setup_two_snapshots(tmp_path)

    def always_call(change: ChangeRecord, **_kwargs: Any) -> str:
        return "summary"

    monkeypatch.setattr(aggregate, "generate_summary", always_call)

    stats = aggregate.run_pipeline(
        policies_root=policies_root,
        processed_root=processed_root,
        enrich_with_llm=True,
        llm_call_budget=0,
    )
    # Budget of 0 means no calls, but the run still succeeds.
    assert stats["llm_calls"] == 0


def test_llm_module_integrates_with_real_generate_api(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Sanity: the llm.generate_summary symbol that aggregate imports is
    # actually the same module-level function, so monkeypatching it on
    # aggregate works in the real workflow.
    assert aggregate.generate_summary is llm.generate_summary


def test_force_reenrich_overrides_existing_summary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    policies_root, processed_root = _setup_two_snapshots(tmp_path)

    # Seed a prior summary by doing one normal enriched run.
    monkeypatch.setattr(
        aggregate, "generate_summary", lambda _c, **_k: "original summary"
    )
    aggregate.run_pipeline(
        policies_root=policies_root,
        processed_root=processed_root,
        enrich_with_llm=True,
    )

    change_files = list((processed_root / "changes").glob("*.json"))
    before = json.loads(change_files[0].read_text())
    assert before["llm_summary"] == "original summary"

    # Without --force-reenrich, even a tuned prompt would be skipped.
    monkeypatch.setattr(
        aggregate, "generate_summary", lambda _c, **_k: "tuned summary"
    )
    stats = aggregate.run_pipeline(
        policies_root=policies_root,
        processed_root=processed_root,
        enrich_with_llm=True,
    )
    assert stats["llm_calls"] == 0
    unchanged = json.loads(change_files[0].read_text())
    assert unchanged["llm_summary"] == "original summary"

    # With --force-reenrich, the tuned prompt replaces the cached summary.
    stats = aggregate.run_pipeline(
        policies_root=policies_root,
        processed_root=processed_root,
        enrich_with_llm=True,
        force_reenrich=True,
    )
    assert stats["llm_calls"] == 1
    after = json.loads(change_files[0].read_text())
    assert after["llm_summary"] == "tuned summary"
