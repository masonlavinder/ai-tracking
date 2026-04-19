# Contributing

Thanks for your interest. This project is designed to stay small and
reviewable — pull requests that follow the existing patterns merge
faster than ones that introduce new abstractions.

## Dev setup

```bash
# Python projects
cd scrapers && uv sync --extra dev && uv run pytest
cd ../analysis && uv sync --extra dev && uv run pytest

# Frontend
cd ../frontend && npm ci && npm run build
```

- Python 3.12, managed with [uv](https://github.com/astral-sh/uv).
- Node 22 for the frontend.
- Tests use saved fixtures — no network calls.

## Proposing a new classifier rule

Classifier rules live in
[`analysis/src/analysis/rules/keywords.yml`](./analysis/src/analysis/rules/keywords.yml).

Each rule has a `tag`, a one-line `description`, a list of regex
`patterns`, and (optionally) `require_nearby` terms that must co-occur
in the same paragraph for the rule to fire. See
[METHODOLOGY.md](./METHODOLOGY.md) for the matching semantics.

1. Add the rule. Prefer short, specific patterns over broad ones. Use
   `require_nearby` for ambiguous keywords (the word "training" is the
   canonical example).
2. Add a test in
   [`analysis/tests/test_classify.py`](./analysis/tests/test_classify.py)
   with one paragraph that should fire the rule and one that should not.
3. Run `uv run pytest`.

Guidelines:

- **Scope**: we tag language *changes* relevant to AI data use, privacy
  posture, or regulatory carveouts. Rules outside that scope are better
  left to downstream consumers.
- **Patterns are word-boundaried** automatically for bare words. If you
  need regex features (alternation inside a token, character classes,
  etc.) write the full fragment — the classifier will compile it as-is.
- **Added / modified text only.** Rules never fire on removed
  paragraphs; that is intentional and not a bug.

## Proposing a new company

1. Add an entry to
   [`scrapers/src/scrapers/config.py`](./scrapers/src/scrapers/config.py)
   — set `name`, `slug`, `ticker` (if public), `sec_cik` (zero-padded to
   10 digits), and the list of `policy_urls` with `kind` / `label`.
2. Mirror the minimal company metadata in
   [`analysis/src/analysis/companies.py`](./analysis/src/analysis/companies.py)
   so aggregate output includes the new company.
3. Add the slug to `test_config.test_all_required_companies_present` if
   it is core to v1 scope, or leave the existing test alone and just
   verify it still passes.
4. Run both test suites.
5. Once merged, trigger the `backfill` workflow for the new slug to
   seed Wayback snapshots:
   `gh workflow run backfill.yml -f companies=<slug>`.

## Code style

- Python: full type hints. Prefer `pydantic` for data models that cross
  module boundaries; dataclasses for internal-only shapes.
- TypeScript: strict mode is on. Avoid `any`. Prefer named components.
- Comments: only where the **why** is non-obvious. No running commentary
  of what the code does; the code and tests should say that.
- Tests: one or more per module, fixture-based, no network.

## Releasing

There is no release process. `main` deploys to
[masonlavinder.github.io/ai-tracking](https://masonlavinder.github.io/ai-tracking/)
via `.github/workflows/build.yml`.

## Reporting issues

- Broken source pages, bot walls, or incorrect tags:
  [open an issue](https://github.com/masonlavinder/ai-tracking/issues).
- For suspected false positives, include the change URL — links deep
  into the change-detail page are stable.
