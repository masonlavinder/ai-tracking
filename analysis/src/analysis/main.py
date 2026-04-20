"""Analysis pipeline CLI.

Runs the whole diff → classify → score → aggregate chain:

    uv run python -m analysis.main
    uv run python -m analysis.main --raw-root /path/to/data/raw --processed-root /path/to/data/processed

The paths default to the monorepo's `data/raw` and `data/processed`.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .aggregate import DEFAULT_LLM_CALL_BUDGET, TIMELINE_THRESHOLD, run_pipeline

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RAW = REPO_ROOT / "data" / "raw"
DEFAULT_PROCESSED = REPO_ROOT / "data" / "processed"


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="analysis.main",
        description="Run the analysis pipeline on raw scraper output.",
    )
    parser.add_argument(
        "--raw-root",
        type=Path,
        default=DEFAULT_RAW,
        help="Directory containing raw scraper output (default: data/raw).",
    )
    parser.add_argument(
        "--processed-root",
        type=Path,
        default=DEFAULT_PROCESSED,
        help="Directory for processed JSON artifacts (default: data/processed).",
    )
    parser.add_argument(
        "--timeline-threshold",
        type=int,
        default=TIMELINE_THRESHOLD,
        help="Minimum score required to appear on the home timeline.",
    )
    parser.add_argument(
        "--enrich",
        action="store_true",
        help=(
            "Call the GitHub Models hosted LLM to generate plain-English "
            "summaries for changes on the timeline. Requires GITHUB_TOKEN "
            "(or GITHUB_MODELS_TOKEN). Off by default so local runs stay "
            "network-free."
        ),
    )
    parser.add_argument(
        "--llm-budget",
        type=int,
        default=DEFAULT_LLM_CALL_BUDGET,
        help=(
            "Maximum LLM calls per run. New changes beyond the budget stay "
            "unsummarized this run and are picked up next time."
        ),
    )
    parser.add_argument(
        "--force-reenrich",
        action="store_true",
        help=(
            "Regenerate summaries for all timeline-eligible changes, even "
            "ones that already have a cached summary. Use after tuning the "
            "prompt. Respects --llm-budget."
        ),
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Python logging level (default: INFO).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    policies_root = args.raw_root / "policies"
    stats = run_pipeline(
        policies_root=policies_root,
        processed_root=args.processed_root,
        timeline_threshold=args.timeline_threshold,
        enrich_with_llm=args.enrich,
        llm_call_budget=args.llm_budget,
        force_reenrich=args.force_reenrich,
    )
    print(
        "analysis: "
        f"changes={stats['total_changes']} "
        f"timeline={stats['timeline_changes']} "
        f"companies={stats['companies']} "
        f"llm_calls={stats['llm_calls']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
