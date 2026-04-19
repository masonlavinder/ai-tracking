# Methodology

How the AI Privacy Tracker detects, classifies, and scores changes across
the sources it monitors, and the limits of each step.

> This document is not legal advice. The tags and scores on the site are
> heuristics designed to help readers find interesting diffs, not
> conclusions about what the changes mean.

## Sources

| Source | Module | Storage | What is stored |
|---|---|---|---|
| Privacy policies, ToS, AI terms | `scrapers/policies.py` | `data/raw/policies/<slug>/<policy_id>/<YYYY-MM-DD>.{html,txt,meta.json}` | Full HTML, extracted text (trafilatura with BS4 fallback), sha256, HTTP metadata |
| Wayback backfill (policies) | `scrapers/wayback.py` | same as above | Raw captures fetched via the CDX API's `id_` flag, dated to the original capture timestamp |
| SEC 10-K / 10-Q filings | `scrapers/sec.py` | `data/raw/sec/<ticker>/<accession>.json` | Filing metadata + AI-keyword paragraphs (up to 50, truncated to 1500 chars each) |
| Regulatory | `scrapers/regulatory.py` | `data/raw/regulatory/<source>/<YYYY-MM-DD>.json` | Normalized `{source, title, url, published_at, body_excerpt}` records from FTC RSS, EU Commission press corner, and California AG news, filtered to AI / privacy keywords |
| News | `scrapers/news.py` | `data/raw/news/<slug>/<YYYY-MM-DD>.json` | GDELT DOC 2.0 metadata only (URL, title, domain, language, country, seen timestamp, tone). **Article text is never stored.** |

All HTTP traffic goes through a polite client (`scrapers/http.py`) that
consults `robots.txt`, enforces a 2-second per-host delay, retries 429 /
5xx responses with exponential backoff, and identifies itself as
`AIPrivacyTracker/0.1 (+https://github.com/masonlavinder/ai-tracking)`.

## Change detection

`analysis/diff.py` walks every `data/raw/policies/<slug>/<policy_id>/` and
pairs consecutive snapshots by filename date. For each pair:

1. Load both `.txt` files (trafilatura output, generally one paragraph
   per block separated by blank lines).
2. Normalize: collapse internal whitespace, drop paragraphs shorter than
   40 characters — these are usually navigation, social links, or
   footers that trafilatura did not scrub.
3. Run `difflib.SequenceMatcher` on the two paragraph lists.
4. Convert opcodes:
   - `insert` → `added_paragraphs`
   - `delete` → `removed_paragraphs`
   - `replace` → greedy pairing by `SequenceMatcher.ratio`. Pairs with
     ratio ≥ 0.5 become `modified_paragraphs` with both `before` and
     `after` text; any leftovers go to added/removed.

A snapshot pair that yields zero added/removed/modified paragraphs
produces no change record.

## Classification

`analysis/classify.py` loads `analysis/src/analysis/rules/keywords.yml`.
Each rule has the shape:

```yaml
- tag: ai-training-expansion
  description: ...
  require_nearby: [AI, model, generative, ...]   # optional
  patterns:
    - "train(?:ing|ed)?"
    - "to train (?:our|the)"
```

The classifier:

1. Compiles each pattern case-insensitively. Bare words are wrapped in
   `\b...\b` word boundaries; entries that look like regex fragments
   (contain backslashes or `?`) are compiled as-is.
2. For each **added** or **modified.after** paragraph:
   - At least one `pattern` must match.
   - If `require_nearby` is present, at least one of those terms must
     also appear in the same paragraph.
3. Any matching rule contributes its `tag` to the change.

Removed paragraphs are intentionally not scanned — the tracker surfaces
newly introduced language, not deletions.

### Tag dictionary

| Tag | Meaning |
|---|---|
| `ai-training-expansion` | Language that permits data use for AI / model training. Requires an AI-adjacent term nearby so plain "employee training" does not trigger. |
| `ai-training-restriction` | New opt-out or explicit restriction on AI / model training. |
| `data-retention-change` | Mentions of retention periods or deletion windows measured in days / months / years. |
| `third-party-sharing` | Third-party, partner, advertiser, affiliate, or service-provider language. |
| `regional-carveout` | Jurisdiction-specific language: EU / EEA / GDPR, California / CCPA / CPRA, UK GDPR, LGPD. |
| `dm-private-content` | Direct messages, DMs, private messages, one-to-one chats. |
| `biometric-facial` | Biometric identifiers, facial recognition, voiceprints, fingerprints. |
| `minors` | Child / teen / "under 13/16/18" / COPPA / age-appropriate language. |
| `opt-out-mechanism` | Introduction of or changes to opt-out / unsubscribe / privacy controls. |
| `encryption-change` | End-to-end encryption, E2EE, encryption-in-transit / at-rest language. |

Contributions to the rule dictionary are welcome — see
[CONTRIBUTING.md](./CONTRIBUTING.md).

## Scoring

`analysis/score.py` assigns each change a total from 0 to 10 and a
per-component breakdown that the change-detail page renders as
"Why this score?":

| Component | Bonus | Rule |
|---|---|---|
| Real content | +3 | At least one added / modified / removed paragraph is ≥ 80 characters. Filters out boilerplate-only changes. |
| Tags | +2 per tag | `2 × len(change.tags)`. Rewards changes that fire multiple classifier rules. |
| Add-only | +2 | `added_paragraphs` is non-empty and there are no modifications or removals. Gives pure additions a boost over reshuffles. |
| Heading keyword | +1 | An added / modified paragraph that looks heading-like (short, mostly capitalized, no trailing period) contains one of `ai`, `artificial intelligence`, `generative`, `training`, `privacy`, `biometric`, `retention`, `third-party`, `third party`. |

Total is capped at 10. Timeline threshold is 4 — changes below that
score are available from per-company pages but do not appear on the
home timeline.

## Limitations

- **Heuristic, not understanding.** Rule-based keyword matching will
  produce both false positives (e.g. policy tables of contents that
  mention tracked words without changing substance) and false negatives
  (synonyms, paraphrases, structural reorganizations that happen to
  avoid tagged words).
- **Paragraph granularity.** Minor wording tweaks inside a long paragraph
  are captured as a modified pair but the site does not render
  intra-paragraph token diffs.
- **Extraction quality.** trafilatura is good for article-like pages but
  occasionally omits sections or captures navigation text; the BS4
  fallback is cruder. Some policy URLs sit behind bot walls and will
  snapshot junk HTML — see [KNOWN_ISSUES.md](./KNOWN_ISSUES.md).
- **No cross-source correlation.** SEC filings, regulatory filings, and
  news metadata exist in `data/raw/` and on per-company pages but do
  not currently factor into the change timeline or scoring.
- **No legal claims.** The displayed tags and scores are heuristics.
  Every change links to its original source; read the original before
  drawing any conclusion about what it means.

## Planned for v2 (out of scope here)

- Optional LLM-generated plain-English summaries as a second-opinion
  layer on top of rule-based tags.
- Sub-paragraph token diffs rendered inline.
- More companies; richer regional policy coverage.
- Change records for SEC and regulatory sources in the timeline.
- Crowdsourced rule contributions with review.
