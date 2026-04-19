# Known Issues

Sources and assumptions that are known to be fragile.

## Regulatory

- **EU Commission press corner (`ec.europa.eu/commission/presscorner/home/en`)**
  is parsed by walking HTML links that contain `/presscorner/detail/`. The
  Commission's markup is subject to redesigns; if parsing breaks, the
  `regulatory` scraper will log an error and emit zero records for that day
  rather than crash the pipeline. The DSA transparency database may be a more
  stable long-term option (v2).
- **California AG news (`oag.ca.gov/news`)** has no public RSS. We scrape
  the HTML listing with article-wrapper heuristics. Same fragility as the EU
  source.
- **FTC RSS** is stable.

## News

- **GDELT 2.0 DOC API** returns per-query metadata only, with no
  authentication. Occasional rate-limit or 502 responses are retried by the
  polite client with backoff. If queries return empty for a company for an
  extended period, investigate whether the query terms match anything in
  GDELT's index for that timespan.

## SEC

- **EDGAR submissions** only include the `.recent` block (up to ~1000 most
  recent filings per company). For the five v1 companies that is many years
  of 10-K/10-Q filings, so the older-filings pagination
  (`filings.files[*].name`) is not yet implemented.

## Privacy policies

- Some policy pages (Instagram / Meta regional variants, Google consent
  walls) may return bot-wall HTML or 403 on direct fetch. When that happens
  the snapshot record still contains the wall HTML, which is useless for
  diffs. If a particular URL is consistently blocked, remove it from the
  registry and rely on Wayback backfill until a workaround exists.
