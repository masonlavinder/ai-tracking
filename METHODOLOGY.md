# Methodology

This document describes how the AI Privacy Tracker detects, classifies, and
scores changes across the sources it monitors. It will be filled in as the
analysis pipeline lands.

## Sources

- **Privacy policies / ToS**: direct HTTPS scrapes of each company's policy
  pages. Historical backfill via the Wayback Machine CDX API.
- **SEC filings**: EDGAR 10-K and 10-Q filings for publicly traded companies.
- **Regulatory filings**: FTC press releases, EU Commission announcements,
  California AG announcements, filtered for AI + privacy keywords.
- **News context**: GDELT 2.0 DOC API metadata only — never article body.

## Change detection

Paragraph-level diff between the two most recent snapshots of a given source,
computed with `difflib.SequenceMatcher`. Navigation and boilerplate blocks are
excluded.

## Classification

Pure rule-based keyword and regex matching. Rules live in
`analysis/rules/keywords.yml`. Each rule emits one or more tags such as
`ai-training-expansion`, `data-retention-change`, or `regional-carveout`.

## Scoring

Each change gets a significance score from 0–10:

- +3 if the change is in a policy section (not navigation/boilerplate)
- +2 per matched change-type tag
- +2 if the change adds new paragraphs rather than editing existing ones
- +1 if keywords appear in the headline or section title
- capped at 10

Changes with score ≥ 4 are surfaced on the home timeline; all changes are
available from per-company pages.

## Limitations

- Rule-based classification can and will produce false positives and
  negatives.
- This project makes no legal claims about policy changes. The displayed tags
  and scores are heuristics to help readers find interesting diffs, not
  conclusions about what the changes mean.
- News metadata does not imply endorsement or verification of article
  content.
