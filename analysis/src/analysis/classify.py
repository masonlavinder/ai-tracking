"""Rule-based classification of paragraph changes.

Load `rules/keywords.yml`, compile each rule's regex patterns, and for each
paragraph check:

1. At least one `pattern` matches (case-insensitive).
2. If the rule has `require_nearby`, at least one of those terms also
   appears in the same paragraph.

A rule that fires anywhere in the change's added or modified paragraphs
emits its tag. Removed paragraphs are intentionally ignored — we surface
*new* language, not deletions.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Iterable

import yaml

from .models import ChangeRecord

log = logging.getLogger(__name__)

RULES_PATH = Path(__file__).parent / "rules" / "keywords.yml"


@dataclass
class Rule:
    tag: str
    description: str
    patterns: list[re.Pattern[str]]
    require_nearby: list[re.Pattern[str]]

    def matches(self, paragraph: str) -> bool:
        if not any(p.search(paragraph) for p in self.patterns):
            return False
        if not self.require_nearby:
            return True
        return any(r.search(paragraph) for r in self.require_nearby)


def _compile_term(term: str) -> re.Pattern[str]:
    """Compile a raw dictionary term with word boundaries, case-insensitive."""
    if term.startswith("\\b") or "\\" in term or "?" in term:
        # Already a regex fragment.
        return re.compile(term, re.IGNORECASE)
    escaped = re.escape(term).replace(r"\ ", r"\s+")
    return re.compile(rf"\b{escaped}\b", re.IGNORECASE)


def _load_rules(path: Path) -> list[Rule]:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    raw_rules = data.get("rules") or []
    rules: list[Rule] = []
    for raw in raw_rules:
        tag = raw.get("tag")
        if not tag:
            log.warning("Skipping rule without tag: %r", raw)
            continue
        patterns = [_compile_term(p) for p in (raw.get("patterns") or [])]
        nearby = [_compile_term(r) for r in (raw.get("require_nearby") or [])]
        rules.append(
            Rule(
                tag=str(tag),
                description=str(raw.get("description") or ""),
                patterns=patterns,
                require_nearby=nearby,
            )
        )
    return rules


@cache
def load_rules(path: str | None = None) -> list[Rule]:
    """Load and compile the rule set. Cached; pass a path to bust the cache."""
    return _load_rules(Path(path) if path else RULES_PATH)


def _paragraphs_to_scan(change: ChangeRecord) -> Iterable[str]:
    yield from change.added_paragraphs
    for pair in change.modified_paragraphs:
        yield pair.after


def classify_change(change: ChangeRecord, rules: list[Rule] | None = None) -> list[str]:
    """Return the list of rule tags that fire on a single change record."""
    rules = rules if rules is not None else load_rules()
    paragraphs = list(_paragraphs_to_scan(change))
    matched: list[str] = []
    for rule in rules:
        if any(rule.matches(p) for p in paragraphs):
            matched.append(rule.tag)
    return matched


def classify_all(
    changes: list[ChangeRecord], rules: list[Rule] | None = None
) -> list[ChangeRecord]:
    """Attach tags to every change in the list (mutates and returns)."""
    rules = rules if rules is not None else load_rules()
    for change in changes:
        change.tags = classify_change(change, rules)
    return changes
