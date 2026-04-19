"""Tests for paragraph splitting and heading detection."""

from __future__ import annotations

from analysis.paragraphs import is_heading, split_paragraphs


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
