"""Paragraph-level diffing of consecutive policy snapshots.

Walks `data/raw/policies/<slug>/<policy_id>/*.txt`, pairs consecutive
snapshots by date, and emits one `ChangeRecord` per pair whose paragraph
lists differ. An empty diff (e.g., whitespace-only changes) yields no
record.

The diff uses `difflib.SequenceMatcher` on cleaned paragraph lists. A
`replace` opcode is converted into one or more `ParagraphChange` pairs
(one-to-one where possible); extras become added/removed paragraphs.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterator

from .companies import get_company
from .language import is_probably_english
from .models import ChangeRecord, ParagraphChange
from .paragraphs import split_paragraphs

log = logging.getLogger(__name__)


@dataclass
class SnapshotPair:
    """Two consecutive snapshots for the same (company, policy) stream."""

    company_slug: str
    policy_id: str
    from_text_path: Path
    to_text_path: Path
    from_date: str
    to_date: str

    @property
    def policy_dir(self) -> Path:
        return self.from_text_path.parent


def iter_policy_dirs(policies_root: Path) -> Iterator[Path]:
    """Yield each <policies_root>/<slug>/<policy_id> directory."""
    if not policies_root.is_dir():
        return
    for company_dir in sorted(p for p in policies_root.iterdir() if p.is_dir()):
        for policy_dir in sorted(p for p in company_dir.iterdir() if p.is_dir()):
            yield policy_dir


def _english_snapshots(policy_dir: Path) -> list[Path]:
    """Return this policy's `.txt` snapshots, filtering out non-English ones.

    Wayback sometimes served localized pages (Meta in Finnish or Urdu on
    certain capture dates). Including those produces huge bogus diffs
    when the language flips back. The English-ish heuristic here skips
    such captures so the remaining chronology diffs cleanly.
    """
    kept: list[Path] = []
    for txt in sorted(policy_dir.glob("*.txt")):
        try:
            text = txt.read_text(encoding="utf-8", errors="replace")
        except OSError as err:
            log.warning("Unable to read %s: %s", txt, err)
            continue
        if not is_probably_english(text):
            log.info("Skipping non-English snapshot %s", txt)
            continue
        kept.append(txt)
    return kept


def iter_snapshot_pairs(policies_root: Path) -> Iterator[SnapshotPair]:
    """Yield consecutive English snapshot pairs across all policy directories."""
    for policy_dir in iter_policy_dirs(policies_root):
        txt_files = _english_snapshots(policy_dir)
        if len(txt_files) < 2:
            continue
        slug = policy_dir.parent.name
        policy_id = policy_dir.name
        for prev, curr in zip(txt_files, txt_files[1:]):
            yield SnapshotPair(
                company_slug=slug,
                policy_id=policy_id,
                from_text_path=prev,
                to_text_path=curr,
                from_date=prev.stem,
                to_date=curr.stem,
            )


def _load_meta(policy_dir: Path, date_str: str) -> dict[str, object]:
    path = policy_dir / f"{date_str}.meta.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        log.warning("Unable to read %s: %s", path, err)
        return {}


MODIFICATION_SIMILARITY_THRESHOLD = 0.5

# SequenceMatcher.ratio() is O(N*M) on character strings. Guard the
# similarity pairing with two budgets:
#
# 1. Pair-count budget. Too many (old, new) combinations and even cheap
#    matching dominates wall time. When exceeded we skip pairing entirely
#    and emit add + remove — correct when a page has been substantially
#    rewritten.
# 2. Per-pair content-size guard. A single pair of multi-kilobyte
#    paragraphs is enough to hang for minutes on its own (seen with
#    Wayback captures that extract as one giant blob). Fall back to
#    `quick_ratio` for big strings — it's O(N+M) and close enough for
#    the 0.5 threshold.
MAX_PAIRING_BUDGET = 400
MAX_RATIO_CHARS = 4000


def _paragraph_similarity(a: str, b: str) -> float:
    """Similarity in [0, 1]. Uses the fast approximation on large inputs."""
    matcher = SequenceMatcher(a=a, b=b, autojunk=False)
    if len(a) > MAX_RATIO_CHARS or len(b) > MAX_RATIO_CHARS:
        return matcher.quick_ratio()
    return matcher.ratio()


def _pair_replacements(
    olds: list[str], news: list[str]
) -> tuple[list[str], list[str], list[ParagraphChange]]:
    """Greedy-match replaced paragraphs by similarity.

    For each old paragraph, find the most similar remaining new paragraph.
    If their similarity is above the threshold, record it as a
    modification; otherwise treat the old as removed. Any new paragraphs
    left unmatched at the end become additions.
    """
    if len(olds) * len(news) > MAX_PAIRING_BUDGET:
        return list(news), list(olds), []

    added: list[str] = []
    removed: list[str] = []
    modified: list[ParagraphChange] = []
    remaining_news: list[tuple[int, str]] = list(enumerate(news))

    for old in olds:
        if not remaining_news:
            removed.append(old)
            continue
        best_idx = -1
        best_ratio = 0.0
        for pos, (_, candidate) in enumerate(remaining_news):
            ratio = _paragraph_similarity(old, candidate)
            if ratio > best_ratio:
                best_ratio = ratio
                best_idx = pos
        if best_ratio >= MODIFICATION_SIMILARITY_THRESHOLD and best_idx >= 0:
            _, match = remaining_news.pop(best_idx)
            modified.append(ParagraphChange(before=old, after=match))
        else:
            removed.append(old)
    added.extend(text for _, text in remaining_news)
    return added, removed, modified


def _opcodes_to_change_lists(
    from_paras: list[str], to_paras: list[str]
) -> tuple[list[str], list[str], list[ParagraphChange]]:
    matcher = SequenceMatcher(a=from_paras, b=to_paras, autojunk=False)
    added: list[str] = []
    removed: list[str] = []
    modified: list[ParagraphChange] = []

    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            continue
        if op == "insert":
            added.extend(to_paras[j1:j2])
        elif op == "delete":
            removed.extend(from_paras[i1:i2])
        elif op == "replace":
            a_span = from_paras[i1:i2]
            b_span = to_paras[j1:j2]
            add_span, rem_span, mod_span = _pair_replacements(a_span, b_span)
            added.extend(add_span)
            removed.extend(rem_span)
            modified.extend(mod_span)
    return added, removed, modified


def diff_pair(pair: SnapshotPair) -> ChangeRecord | None:
    """Compute the ChangeRecord for one snapshot pair, or None if no diff."""
    from_text = pair.from_text_path.read_text(encoding="utf-8", errors="replace")
    to_text = pair.to_text_path.read_text(encoding="utf-8", errors="replace")
    from_paras = split_paragraphs(from_text)
    to_paras = split_paragraphs(to_text)

    added, removed, modified = _opcodes_to_change_lists(from_paras, to_paras)
    if not (added or removed or modified):
        return None

    meta = _load_meta(pair.policy_dir, pair.to_date)
    url = str(meta.get("url") or "")
    policy_label = str(meta.get("policy_label") or pair.policy_id)
    policy_kind = str(meta.get("policy_kind") or pair.policy_id)

    try:
        company = get_company(pair.company_slug)
        company_name = company.name
    except KeyError:
        company_name = pair.company_slug

    change_id = f"{pair.company_slug}-{pair.policy_id}-{pair.from_date}-{pair.to_date}"
    return ChangeRecord(
        id=change_id,
        company_slug=pair.company_slug,
        company_name=company_name,
        source_type="policy",
        policy_kind=policy_kind,
        policy_label=policy_label,
        url=url,
        from_date=pair.from_date,
        to_date=pair.to_date,
        date=pair.to_date,
        added_paragraphs=added,
        removed_paragraphs=removed,
        modified_paragraphs=modified,
    )


def diff_all(policies_root: Path) -> list[ChangeRecord]:
    """Return ChangeRecords for every consecutive snapshot pair under root."""
    records: list[ChangeRecord] = []
    for pair in iter_snapshot_pairs(policies_root):
        record = diff_pair(pair)
        if record is not None:
            records.append(record)
    return records
