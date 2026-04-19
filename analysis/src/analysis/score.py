"""Significance scoring for change records.

Score contributions per the methodology in METHODOLOGY.md:

    +3 if the change contains real content (not just navigation/boilerplate)
    +2 per matched change-type tag
    +2 if the change only adds new paragraphs (no modifications)
    +1 if keywords appear in nearby heading-like text

Score is capped at 10. Also produces a per-component breakdown that the
frontend renders in the change-detail page ("Why this score?").
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import ChangeRecord
from .paragraphs import is_heading

MAX_SCORE = 10
MIN_CONTENT_CHARS = 80

# Shared (with the classifier) shortlist of keywords that, when found in a
# heading-like paragraph, trigger the +1 "headline keyword" bonus. Kept
# intentionally small — not every AI keyword in a heading deserves a boost.
_HEADING_KEYWORDS: tuple[str, ...] = (
    "ai",
    "artificial intelligence",
    "generative",
    "training",
    "privacy",
    "biometric",
    "retention",
    "third-party",
    "third party",
)


@dataclass
class ScoreBreakdown:
    """Per-component explanation that accompanies a change's total score."""

    content: int = 0  # +3 if real content (not boilerplate)
    tags: int = 0  # +2 per tag
    add_only: int = 0  # +2 if only additions
    heading_keyword: int = 0  # +1 if keywords in a nearby heading
    total: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "content": self.content,
            "tags": self.tags,
            "add_only": self.add_only,
            "heading_keyword": self.heading_keyword,
            "total": self.total,
        }


def _has_real_content(change: ChangeRecord) -> bool:
    def is_substantial(text: str) -> bool:
        return len(text.strip()) >= MIN_CONTENT_CHARS

    if any(is_substantial(p) for p in change.added_paragraphs):
        return True
    if any(is_substantial(p.after) or is_substantial(p.before) for p in change.modified_paragraphs):
        return True
    if any(is_substantial(p) for p in change.removed_paragraphs):
        return True
    return False


def _is_add_only(change: ChangeRecord) -> bool:
    return bool(change.added_paragraphs) and not (
        change.modified_paragraphs or change.removed_paragraphs
    )


def _heading_keyword_hit(change: ChangeRecord) -> bool:
    """True if a heading-like paragraph mentions a tracked keyword."""
    candidates: list[str] = []
    candidates.extend(change.added_paragraphs)
    candidates.extend(p.after for p in change.modified_paragraphs)
    for cand in candidates:
        if not is_heading(cand):
            continue
        lower = cand.lower()
        if any(kw in lower for kw in _HEADING_KEYWORDS):
            return True
    return False


def score_change(change: ChangeRecord) -> ScoreBreakdown:
    """Compute the score + breakdown for a change and attach it to the record."""
    breakdown = ScoreBreakdown()
    if _has_real_content(change):
        breakdown.content = 3
    breakdown.tags = 2 * len(change.tags)
    if _is_add_only(change):
        breakdown.add_only = 2
    if _heading_keyword_hit(change):
        breakdown.heading_keyword = 1

    total = (
        breakdown.content
        + breakdown.tags
        + breakdown.add_only
        + breakdown.heading_keyword
    )
    breakdown.total = min(MAX_SCORE, total)
    change.score = breakdown.total
    return breakdown


def score_all(changes: list[ChangeRecord]) -> dict[str, ScoreBreakdown]:
    """Score every change in the list and return a map from id to breakdown."""
    breakdowns: dict[str, ScoreBreakdown] = {}
    for change in changes:
        breakdowns[change.id] = score_change(change)
    return breakdowns
