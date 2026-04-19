# analysis

The analysis pipeline diffs consecutive policy snapshots under `data/raw/policies/`,
classifies each change with rule-based keyword matching, scores significance,
and writes four JSON artifacts to `data/processed/`:

- `companies.json` — registry + per-company summary
- `changes.json` — flat list of all detected changes, sorted by date desc
- `timeline.json` — changes with score ≥ 4 (for the home timeline)
- `changes/<id>.json` — one file per change with full before/after paragraphs

```bash
uv sync --extra dev
uv run python -m analysis.main
uv run pytest
```

Re-running on the same inputs produces the same outputs (idempotent).
