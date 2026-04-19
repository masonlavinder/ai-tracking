"""Paragraph splitting and normalization.

Policy snapshots are stored as plain text produced by trafilatura. To get
clean diffs we split that text into paragraph-level units, normalize
whitespace, and drop fragments that look like navigation or single words.
"""

from __future__ import annotations

import re

# A "paragraph" is a block of non-empty lines separated by one or more blank
# lines. Trafilatura output usually already aligns with this shape.
_BLANK_LINE_RE = re.compile(r"\n\s*\n+")
_WHITESPACE_RE = re.compile(r"\s+")

# Fragments shorter than this are treated as navigation/boilerplate noise
# and get dropped before diffing.
MIN_PARAGRAPH_CHARS = 40


def split_paragraphs(text: str, *, min_chars: int = MIN_PARAGRAPH_CHARS) -> list[str]:
    """Split plain text into normalized paragraphs.

    - collapses internal whitespace to single spaces
    - drops paragraphs shorter than `min_chars` (navigation, single links)
    - preserves order
    """
    if not text:
        return []
    paragraphs: list[str] = []
    for block in _BLANK_LINE_RE.split(text):
        cleaned = _WHITESPACE_RE.sub(" ", block).strip()
        if len(cleaned) < min_chars:
            continue
        paragraphs.append(cleaned)
    return paragraphs


def is_heading(paragraph: str) -> bool:
    """Heuristic: does this paragraph look like a section heading?

    Used by the scorer to give +1 when matched keywords appear in a nearby
    heading. Not exact — trafilatura doesn't always mark headings — so we
    accept short title-cased lines as a proxy.
    """
    if not paragraph:
        return False
    if len(paragraph) > 120:
        return False
    # Heading-ish: few words, mostly capitalized, no trailing period.
    words = paragraph.split()
    if len(words) < 1 or len(words) > 15:
        return False
    if paragraph.rstrip().endswith(("."  , ",", ":")):
        return False
    cap_words = sum(1 for w in words if w[:1].isupper())
    return cap_words / len(words) >= 0.5
