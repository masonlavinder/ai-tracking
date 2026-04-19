"""Tests for the CLI runners' exit-code behaviour."""

from __future__ import annotations

from typing import Any

import pytest

from scrapers import main
from scrapers.policies import SnapshotResult


def _make_result(status: str, slug: str = "example") -> SnapshotResult:
    return SnapshotResult(
        company_slug=slug,
        policy_kind="privacy_policy",
        url="https://example.com/privacy",
        snapshot_path=None,
        status=status,
        detail="",
    )


def test_run_policies_exits_zero_on_partial_success(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def fake_fetch(_slugs: Any) -> list[SnapshotResult]:
        return [
            _make_result("written", "meta"),
            _make_result("error", "openai"),
            _make_result("unchanged", "google"),
        ]

    monkeypatch.setattr(main, "fetch_all_policies", fake_fetch)
    assert main._run_policies(None) == 0
    out = capsys.readouterr().out
    assert "errors=1" in out
    assert "openai" in out  # error detail surfaced


def test_run_policies_exits_nonzero_only_when_everything_failed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_all_failed(_slugs: Any) -> list[SnapshotResult]:
        return [
            _make_result("error", "meta"),
            _make_result("error", "openai"),
        ]

    monkeypatch.setattr(main, "fetch_all_policies", fake_all_failed)
    assert main._run_policies(None) == 1


def test_run_policies_exits_zero_when_no_urls_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A degenerate config shouldn't falsely fail the workflow.
    monkeypatch.setattr(main, "fetch_all_policies", lambda _slugs: [])
    assert main._run_policies(None) == 0
