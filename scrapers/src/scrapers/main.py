"""Scrapers CLI entry point.

Usage:

    uv run python -m scrapers.main --source policies --companies meta,openai

Only the policies source is wired up in Phase 1. Additional sources
(sec, regulatory, news, wayback) are added in later phases.
"""

from __future__ import annotations

import argparse
import logging
import sys

from .config import all_slugs
from .policies import fetch_all_policies

KNOWN_SOURCES = ("policies",)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="scrapers.main",
        description="Fetch data sources for the AI Privacy Tracker.",
    )
    parser.add_argument(
        "--source",
        choices=("all", *KNOWN_SOURCES),
        default="all",
        help="Which source to fetch. Default: all.",
    )
    parser.add_argument(
        "--companies",
        default=None,
        help=(
            "Comma-separated slugs to fetch (default: all registered companies). "
            f"Known slugs: {','.join(all_slugs())}"
        ),
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


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    slugs = _resolve_slugs(args.companies)

    sources = KNOWN_SOURCES if args.source == "all" else (args.source,)

    exit_code = 0
    for source in sources:
        if source == "policies":
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
            if errors:
                exit_code = 1
        else:  # pragma: no cover - defensive; argparse restricts choices
            raise ValueError(f"Unhandled source: {source}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
