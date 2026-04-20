"""Aggregate diffs, tags, and scores into the four frontend JSON artifacts.

Outputs under `data/processed/`:

- `companies.json`    — registry + per-company summary
- `changes.json`      — lean list of all changes (no full paragraphs)
- `timeline.json`     — changes with score >= 4, sorted date desc
- `changes/<id>.json` — one file per change with full before/after text
                         and a score breakdown

Idempotent: `changes/` is wiped and rewritten each run.
"""

from __future__ import annotations

import json
import logging
import shutil
from datetime import UTC, datetime
from pathlib import Path

from .classify import classify_all, load_rules
from .companies import COMPANIES, _stock_url
from .diff import diff_all, iter_policy_dirs
from .llm import generate_summary
from .models import ChangeRecord, ChangeSummary, CompanySummary
from .score import ScoreBreakdown, score_all

log = logging.getLogger(__name__)

TIMELINE_THRESHOLD = 4
RECENT_CHANGES_PER_COMPANY = 10
DEFAULT_LLM_CALL_BUDGET = 50


def _generated_at() -> str:
    return datetime.now(UTC).isoformat()


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True, default=str)
        fh.write("\n")


def _latest_snapshot_date(policies_root: Path, slug: str) -> str | None:
    """Most recent YYYY-MM-DD across any policy stream for one company."""
    company_root = policies_root / slug
    if not company_root.is_dir():
        return None
    dates: list[str] = []
    for policy_dir in company_root.iterdir():
        if not policy_dir.is_dir():
            continue
        for txt in policy_dir.glob("*.txt"):
            dates.append(txt.stem)
    if not dates:
        return None
    return max(dates)


def _build_company_summaries(
    policies_root: Path, changes: list[ChangeRecord]
) -> list[CompanySummary]:
    changes_by_company: dict[str, list[ChangeRecord]] = {}
    for change in changes:
        changes_by_company.setdefault(change.company_slug, []).append(change)

    summaries: list[CompanySummary] = []
    for company in COMPANIES:
        company_changes = sorted(
            changes_by_company.get(company.slug, []),
            key=lambda c: (c.date, c.id),
            reverse=True,
        )
        policies: list[dict[str, str]] = []
        company_root = policies_root / company.slug
        if company_root.is_dir():
            for policy_dir in sorted(p for p in company_root.iterdir() if p.is_dir()):
                latest_txt = max(
                    policy_dir.glob("*.txt"),
                    default=None,
                    key=lambda p: p.stem,
                )
                label = policy_dir.name
                url = ""
                if latest_txt is not None:
                    meta_path = latest_txt.with_suffix(".meta.json")
                    if meta_path.exists():
                        try:
                            meta = json.loads(meta_path.read_text(encoding="utf-8"))
                            label = str(meta.get("policy_label") or label)
                            url = str(meta.get("url") or "")
                        except (OSError, json.JSONDecodeError):
                            pass
                policies.append(
                    {
                        "policy_id": policy_dir.name,
                        "label": label,
                        "url": url,
                        "latest_snapshot_date": latest_txt.stem if latest_txt else "",
                    }
                )
        summaries.append(
            CompanySummary(
                slug=company.slug,
                name=company.name,
                ticker=company.ticker,
                sec_cik=company.sec_cik,
                homepage_url=company.homepage_url,
                stock_url=_stock_url(company.ticker),
                latest_snapshot_date=_latest_snapshot_date(policies_root, company.slug),
                total_changes=len(company_changes),
                recent_change_ids=[
                    c.id for c in company_changes[:RECENT_CHANGES_PER_COMPANY]
                ],
                policies=policies,
            )
        )
    return summaries


def _change_detail(
    change: ChangeRecord, breakdown: ScoreBreakdown
) -> dict[str, object]:
    payload = change.model_dump()
    payload["score_breakdown"] = breakdown.to_dict()
    return payload


def _load_existing_summaries(processed_root: Path) -> dict[str, str]:
    """Map change id → prior llm_summary so we don't re-spend API calls."""
    changes_dir = processed_root / "changes"
    summaries: dict[str, str] = {}
    if not changes_dir.is_dir():
        return summaries
    for path in changes_dir.glob("*.json"):
        try:
            with path.open("r", encoding="utf-8") as fh:
                payload = json.load(fh)
        except (OSError, json.JSONDecodeError) as err:
            log.warning("Unable to read prior %s: %s", path, err)
            continue
        existing = payload.get("llm_summary")
        if isinstance(existing, str) and existing.strip():
            summaries[path.stem] = existing
    return summaries


def _enrich_with_llm(
    changes: list[ChangeRecord],
    existing: dict[str, str],
    *,
    threshold: int,
    budget: int,
    force: bool = False,
) -> int:
    """Attach llm_summary to eligible changes, spending at most `budget` calls.

    Reuses prior summaries from `existing` to stay well inside the free
    tier on repeated runs. Returns the number of LLM calls actually made.

    When `force` is set, any existing summary for a change at or above
    the timeline threshold is regenerated (used after tuning the prompt).
    Below-threshold changes still reuse prior summaries because we never
    spent calls on them in the first place.
    """
    spent = 0
    for change in changes:
        prior = existing.get(change.id)
        eligible = change.score >= threshold
        if prior and not (force and eligible):
            change.llm_summary = prior
            continue
        if not eligible:
            continue
        if spent >= budget:
            log.warning(
                "LLM budget exhausted at %d calls; remaining changes stay "
                "unsummarized this run and will be picked up next time",
                budget,
            )
            if prior:
                change.llm_summary = prior  # fall back to existing
            break
        summary = generate_summary(change)
        spent += 1
        if summary:
            change.llm_summary = summary
        elif prior:
            # Call failed — keep the old summary rather than blanking it.
            change.llm_summary = prior
    return spent


def run_pipeline(
    policies_root: Path,
    processed_root: Path,
    *,
    timeline_threshold: int = TIMELINE_THRESHOLD,
    enrich_with_llm: bool = False,
    llm_call_budget: int = DEFAULT_LLM_CALL_BUDGET,
    force_reenrich: bool = False,
) -> dict[str, int]:
    """Run diff → classify → score → (enrich) → aggregate."""
    changes = diff_all(policies_root)
    log.info("Computed %d raw changes", len(changes))

    rules = load_rules()
    classify_all(changes, rules)
    breakdowns = score_all(changes)

    changes.sort(key=lambda c: (c.date, c.id), reverse=True)

    # Load prior summaries BEFORE we wipe changes/ so we can reuse them.
    existing_summaries = _load_existing_summaries(processed_root)
    llm_calls = 0
    if enrich_with_llm:
        llm_calls = _enrich_with_llm(
            changes,
            existing_summaries,
            threshold=timeline_threshold,
            budget=llm_call_budget,
            force=force_reenrich,
        )
    else:
        # Preserve prior summaries even without enrichment so we never
        # lose a summary someone earned in an earlier run.
        for change in changes:
            prior = existing_summaries.get(change.id)
            if prior:
                change.llm_summary = prior

    # Rewrite changes/ directory from scratch for idempotency.
    changes_dir = processed_root / "changes"
    if changes_dir.exists():
        shutil.rmtree(changes_dir)

    for change in changes:
        _write_json(
            changes_dir / f"{change.id}.json",
            _change_detail(change, breakdowns[change.id]),
        )

    summaries = [ChangeSummary.from_change(c).model_dump() for c in changes]
    generated_at = _generated_at()

    _write_json(
        processed_root / "changes.json",
        {"generated_at": generated_at, "changes": summaries},
    )

    timeline = [s for s in summaries if s["score"] >= timeline_threshold]
    _write_json(
        processed_root / "timeline.json",
        {
            "generated_at": generated_at,
            "threshold": timeline_threshold,
            "changes": timeline,
        },
    )

    company_summaries = _build_company_summaries(policies_root, changes)
    _write_json(
        processed_root / "companies.json",
        {
            "generated_at": generated_at,
            "companies": [c.model_dump() for c in company_summaries],
        },
    )

    return {
        "total_changes": len(changes),
        "timeline_changes": len(timeline),
        "companies": len(company_summaries),
        "llm_calls": llm_calls,
    }
