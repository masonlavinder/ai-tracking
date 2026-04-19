"""Scrapers CLI entry point.

Usage:

    uv run python -m scrapers.main --source policies --companies meta,openai
    uv run python -m scrapers.main --source sec
    uv run python -m scrapers.main --source regulatory
    uv run python -m scrapers.main --source news
    uv run python -m scrapers.main --source wayback --companies meta

`--source all` runs every scheduled source (policies, sec, regulatory, news).
Wayback is excluded from `all` because it is intended as a one-shot backfill.
"""

from __future__ import annotations

import argparse
import logging
import sys

from .config import all_slugs
from .news import fetch_all_news
from .policies import fetch_all_policies
from .regulatory import fetch_all_regulatory
from .sec import fetch_all_filings
from .wayback import backfill_all

SCHEDULED_SOURCES = ("policies", "sec", "regulatory", "news")
ALL_SOURCES = (*SCHEDULED_SOURCES, "wayback")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="scrapers.main",
        description="Fetch data sources for the AI Privacy Tracker.",
    )
    parser.add_argument(
        "--source",
        choices=("all", *ALL_SOURCES),
        default="all",
        help="Source to fetch. 'all' runs policies+sec+regulatory+news (not wayback).",
    )
    parser.add_argument(
        "--companies",
        default=None,
        help=(
            "Comma-separated slugs (default: all). "
            f"Known: {','.join(all_slugs())}"
        ),
    )
    parser.add_argument(
        "--sec-limit",
        type=int,
        default=None,
        help="Cap on number of SEC filings processed per company per run.",
    )
    parser.add_argument(
        "--news-timespan",
        default="7d",
        help="GDELT timespan, e.g. 1d, 7d, 30d (default: 7d).",
    )
    parser.add_argument(
        "--wayback-months",
        type=int,
        default=24,
        help="How many months back to pull Wayback snapshots (default: 24).",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Python logging level (default: INFO).",
    )
    return parser.parse_args(argv)


def _resolve_slugs(raw: str | None) -> list[str] | None:
    if raw is None:
        return None
    slugs = [s.strip() for s in raw.split(",") if s.strip()]
    return slugs or None


def _run_policies(slugs: list[str] | None) -> int:
    results = fetch_all_policies(slugs)
    written = sum(1 for r in results if r.status == "written")
    unchanged = sum(1 for r in results if r.status == "unchanged")
    errors = sum(1 for r in results if r.status == "error")
    skipped = sum(1 for r in results if r.status == "skipped")
    print(
        f"policies: written={written} unchanged={unchanged} "
        f"skipped={skipped} errors={errors}"
    )
    for r in results:
        if r.status in ("error", "skipped"):
            print(f"  {r.status} {r.company_slug}/{r.policy_kind}: {r.detail}")
    return 1 if errors else 0


def _run_sec(slugs: list[str] | None, limit: int | None) -> int:
    records = fetch_all_filings(slugs, limit=limit)
    by_company: dict[str, int] = {}
    for rec in records:
        by_company[rec.company_slug] = by_company.get(rec.company_slug, 0) + 1
    total_excerpts = sum(len(r.excerpts) for r in records)
    print(
        f"sec: filings_processed={len(records)} total_excerpts={total_excerpts} "
        f"by_company={by_company}"
    )
    return 0


def _run_regulatory() -> int:
    results = fetch_all_regulatory()
    summary = {k: (str(v) if v else "no-matches") for k, v in results.items()}
    print(f"regulatory: {summary}")
    return 0


def _run_news(slugs: list[str] | None, timespan: str) -> int:
    results = fetch_all_news(slugs, timespan=timespan)
    summary = {k: (str(v) if v else "no-matches") for k, v in results.items()}
    print(f"news: timespan={timespan} {summary}")
    return 0


def _run_wayback(slugs: list[str] | None, months: int) -> int:
    results = backfill_all(slugs, months_back=months)
    written = sum(1 for r in results if r.status == "written")
    unchanged = sum(1 for r in results if r.status == "unchanged")
    print(f"wayback: written={written} unchanged={unchanged}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    slugs = _resolve_slugs(args.companies)
    sources = SCHEDULED_SOURCES if args.source == "all" else (args.source,)

    exit_code = 0
    for source in sources:
        if source == "policies":
            exit_code |= _run_policies(slugs)
        elif source == "sec":
            exit_code |= _run_sec(slugs, args.sec_limit)
        elif source == "regulatory":
            exit_code |= _run_regulatory()
        elif source == "news":
            exit_code |= _run_news(slugs, args.news_timespan)
        elif source == "wayback":
            exit_code |= _run_wayback(slugs, args.wayback_months)
        else:  # pragma: no cover
            raise ValueError(f"Unhandled source: {source}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
