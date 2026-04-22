# AI Privacy Tracker

**Live site:** <https://masonlavinder.github.io/ai-tracking/>

[![scrape](https://github.com/masonlavinder/ai-tracking/actions/workflows/scrape.yml/badge.svg)](https://github.com/masonlavinder/ai-tracking/actions/workflows/scrape.yml)
[![build](https://github.com/masonlavinder/ai-tracking/actions/workflows/build.yml/badge.svg)](https://github.com/masonlavinder/ai-tracking/actions/workflows/build.yml)
[![last commit](https://img.shields.io/github/last-commit/masonlavinder/ai-tracking/main)](https://github.com/masonlavinder/ai-tracking/commits/main)
[![license](https://img.shields.io/badge/license-MIT-blue)](./LICENSE)

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

## Automation

Three GitHub Actions workflows live under `.github/workflows/`:

- `scrape.yml` — scheduled daily (06:00 UTC) and manual. Runs every
  scheduled scraper source (policies, SEC, regulatory, news) and commits
  new snapshots to `data/raw/`.
- `build.yml` — triggered by pushes to `data/raw/**`, `analysis/**`, or
  `frontend/**`. Runs the analysis pipeline, commits `data/processed/`,
  builds the Vite site, and deploys to GitHub Pages.
- `backfill.yml` — manual-only. Runs the Wayback Machine backfill for
  all or selected companies.

### One-time GitHub Pages setup

1. Push `main` to GitHub.
2. In the repository settings, open **Pages** and set **Source** to
   **GitHub Actions**.
3. Trigger `build.yml` from the Actions tab (`workflow_dispatch`) to
   produce the first deployment.

Subsequent daily scrapes will flow through `build.yml` automatically.

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
