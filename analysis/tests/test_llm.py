"""Tests for the GitHub Models LLM client. No network calls."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import httpx
import pytest

from analysis import llm
from analysis.models import ChangeRecord, ParagraphChange


def _change() -> ChangeRecord:
    return ChangeRecord(
        id="example-privacy_policy-2026-03-01-2026-04-01",
        company_slug="example",
        company_name="Example",
        source_type="policy",
        policy_kind="privacy_policy",
        policy_label="Example Privacy Policy",
        url="https://example.com/privacy",
        from_date="2026-03-01",
        to_date="2026-04-01",
        date="2026-04-01",
        tags=["ai-training-expansion"],
        added_paragraphs=[
            "We may use your public content to train our generative AI models."
        ],
        modified_paragraphs=[
            ParagraphChange(
                before="We retain your data for 24 months.",
                after="We retain your data for 36 months.",
            )
        ],
    )


@dataclass
class _FakeResponse:
    status_code: int
    payload: dict[str, Any] = field(default_factory=dict)
    text: str = ""

    def json(self) -> Any:
        return self.payload


class _FakeClient:
    """Stand-in for httpx.Client covering the narrow surface we use."""

    def __init__(self, response: _FakeResponse) -> None:
        self.response = response
        self.calls: list[dict[str, Any]] = []

    def post(
        self,
        url: str,
        *,
        json: dict[str, Any],
        headers: dict[str, str],
    ) -> _FakeResponse:
        self.calls.append({"url": url, "json": json, "headers": headers})
        return self.response

    def close(self) -> None:  # pragma: no cover - not exercised here
        pass


def test_generate_summary_returns_content_on_success() -> None:
    client = _FakeClient(
        _FakeResponse(
            200,
            {
                "choices": [
                    {"message": {"content": "We added wording about training AI."}}
                ]
            },
        )
    )
    summary = llm.generate_summary(_change(), token="fake", client=client)  # type: ignore[arg-type]
    assert summary == "We added wording about training AI."
    assert len(client.calls) == 1
    body = client.calls[0]["json"]
    assert body["model"] == llm.DEFAULT_MODEL
    assert any("Example" in m["content"] for m in body["messages"])
    assert client.calls[0]["headers"]["Authorization"] == "Bearer fake"


def test_generate_summary_returns_none_without_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_MODELS_TOKEN", raising=False)
    assert llm.generate_summary(_change()) is None


def test_generate_summary_returns_none_on_4xx() -> None:
    client = _FakeClient(_FakeResponse(429, text="rate limited"))
    assert llm.generate_summary(_change(), token="fake", client=client) is None  # type: ignore[arg-type]


def test_generate_summary_returns_none_on_empty_choices() -> None:
    client = _FakeClient(_FakeResponse(200, {"choices": []}))
    assert llm.generate_summary(_change(), token="fake", client=client) is None  # type: ignore[arg-type]


def test_generate_summary_returns_none_on_http_error() -> None:
    class _ExplodingClient:
        def post(self, *_args: Any, **_kwargs: Any) -> Any:
            raise httpx.ConnectError("no route")

        def close(self) -> None:
            pass

    assert llm.generate_summary(  # type: ignore[arg-type]
        _change(), token="fake", client=_ExplodingClient()
    ) is None
