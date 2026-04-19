# AI Privacy Tracker

Tracks how major tech companies' privacy policies, SEC disclosures, regulatory
filings, and news coverage evolve with respect to AI data use.

The site detects policy changes, classifies them with rule-based heuristics,
and publishes a public dashboard. Fully automated via GitHub Actions and
hosted on GitHub Pages.

## Companies tracked (v1)

- Meta
- OpenAI
- Anthropic
- Google
- Microsoft

## Repository layout

- `scrapers/` — Python scrapers that pull raw data into `data/raw/`
- `analysis/` — Python pipeline that diffs snapshots and emits classified changes into `data/processed/`
- `frontend/` — Vite + React + TypeScript static site that renders the dashboard
- `data/` — raw and processed data, committed to the repo
- `.github/workflows/` — scheduled scrape + build-and-deploy workflows

## Development

Each Python project is managed with [uv](https://github.com/astral-sh/uv) and targets Python 3.12.

```bash
# Scrapers
cd scrapers
uv sync
uv run python -m scrapers.main --help
uv run pytest

# Analysis
cd analysis
uv sync
uv run python -m analysis.main
uv run pytest

# Frontend
cd frontend
npm ci
npm run dev
```

## Documentation

- [METHODOLOGY.md](./METHODOLOGY.md) — how classification and scoring work
- [CONTRIBUTING.md](./CONTRIBUTING.md) — how to propose rules or companies
- [KNOWN_ISSUES.md](./KNOWN_ISSUES.md) — sources that are blocked or flaky

## Disclaimer

This project is **not legal advice**. Classifications are heuristic and may be
wrong. Always read the original source linked from each change detail page
before drawing conclusions.

## License

[MIT](./LICENSE)
