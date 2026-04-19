# scrapers

Polite HTTPS scrapers for the AI Privacy Tracker. Managed with
[uv](https://github.com/astral-sh/uv), Python 3.12.

```bash
uv sync --extra dev
uv run python -m scrapers.main --help
uv run pytest
```

## Conventions

- All HTTP requests go through a single client with a descriptive
  `User-Agent` header that includes a project contact URL.
- `robots.txt` is consulted before fetching any policy URL.
- 2-second delay between requests to the same host.
- Retries with exponential backoff on 429 and 5xx responses.
- No network calls in tests — use fixtures under `tests/fixtures/`.
