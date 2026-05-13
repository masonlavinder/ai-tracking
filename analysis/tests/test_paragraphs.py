"""Tests for paragraph splitting and heading detection."""

from __future__ import annotations

from analysis.paragraphs import is_heading, split_paragraphs, strip_noise


def test_split_paragraphs_separates_on_blank_lines() -> None:
    text = """
First paragraph with enough length to pass the filter and be retained.

Second paragraph. Also long enough to survive the minimum length filter cleanly.

Short
"""
    paragraphs = split_paragraphs(text)
    assert len(paragraphs) == 2
    assert paragraphs[0].startswith("First paragraph")
    assert paragraphs[1].startswith("Second paragraph")


def test_split_paragraphs_collapses_internal_whitespace() -> None:
    text = "Line one\nwraps to line two of the same paragraph because the file was wrapped."
    paragraphs = split_paragraphs(text)
    assert len(paragraphs) == 1
    assert "  " not in paragraphs[0]


def test_split_paragraphs_handles_empty() -> None:
    assert split_paragraphs("") == []
    assert split_paragraphs("\n   \n") == []


def test_is_heading_positive_cases() -> None:
    assert is_heading("How We Use Your Data for AI Training")
    assert is_heading("Data Retention")


def test_is_heading_negative_cases() -> None:
    assert not is_heading("we may use your content to train our models.")
    assert not is_heading("A" * 200)  # too long


def test_strip_noise_removes_microsoft_trace_id() -> None:
    text = (
        "Microsoft Services Agreement\n"
        "This is the Trace Id: 41db0ee6d8ebcac58dea80b553484fac\n"
        "Skip to main content\n"
    )
    cleaned = strip_noise(text)
    assert "Trace Id" not in cleaned
    assert "Microsoft Services Agreement" in cleaned


def test_split_paragraphs_ignores_microsoft_trace_id_changes() -> None:
    """Two snapshots that differ only in the per-fetch Trace Id must
    produce identical paragraph lists, so diff_pair yields no change."""
    body = (
        "Microsoft Services Agreement is a contract between you and Microsoft "
        "that governs your use of Microsoft consumer products and services.\n"
        "\n"
        "Your privacy is important to us; please read the Microsoft Privacy "
        "Statement for details about how we collect and process your data.\n"
    )
    a = f"This is the Trace Id: 41db0ee6d8ebcac58dea80b553484fac\n\n{body}"
    b = f"This is the Trace Id: 10a770ce80c59615e10caa2a5cd13c21\n\n{body}"
    assert split_paragraphs(a) == split_paragraphs(b)


def test_split_paragraphs_fallback_when_no_blank_lines() -> None:
    # Wayback captures of some policy pages extract text as one line per
    # paragraph with no blank lines in between. The blank-line splitter
    # would emit a single giant paragraph and blow up the diff pipeline;
    # the fallback must split on single newlines.
    text = (
        "Anthropic is an AI safety and research company working to build "
        "reliable, interpretable, and steerable AI systems.\n"
        "This Privacy Policy explains how we collect, use, disclose, and "
        "process your personal data when you use our website and services.\n"
        "We retain your personal data for as long as we have a legitimate "
        "business need to do so, after which we delete or anonymize it.\n"
    )
    paragraphs = split_paragraphs(text)
    assert len(paragraphs) == 3
    assert paragraphs[0].startswith("Anthropic is an AI safety")
    assert paragraphs[1].startswith("This Privacy Policy")
    assert paragraphs[2].startswith("We retain")
