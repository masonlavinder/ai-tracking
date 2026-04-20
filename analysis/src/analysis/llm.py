"""Optional LLM enrichment via the free GitHub Models inference endpoint.

For each significant change (score ≥ timeline threshold) we ask a small
hosted model to produce a 2–3 sentence plain-English summary so the
change-detail page can show humans what actually happened without them
having to read the full diff.

The call is deliberately optional:

- No GITHUB_TOKEN in the environment → returns None, pipeline continues.
- HTTP errors / rate limits → logged, returns None, prior summary (if
  any on disk) is preserved by the aggregator.

Only the summary string is kept; raw prompts and responses are not
persisted. Summaries are regenerated only for changes that do not
already have one so we stay well inside the free-tier allowance.
"""

from __future__ import annotations

import logging
import os
from typing import Final

import httpx

from .models import ChangeRecord

log = logging.getLogger(__name__)

GITHUB_MODELS_ENDPOINT: Final = "https://models.github.ai/inference/chat/completions"
DEFAULT_MODEL: Final = "openai/gpt-4o-mini"
DEFAULT_TIMEOUT: Final = 30.0
MAX_INPUT_CHARS: Final = 4000  # safety clamp per prompt section

SYSTEM_PROMPT: Final = (
    "You summarize privacy-policy diffs for a public tracking site. "
    "Be factual and specific. Never state what the change 'means' legally. "
    "Do not speculate about intent. Keep it to 2–3 sentences in plain English. "
    "Emphasize changes that might affect users from a practical perspective. "
    "If nothing substantive changed, say so."
)


def _clamp(text: str, limit: int = MAX_INPUT_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 20] + "\n…(truncated)"


def _build_user_prompt(change: ChangeRecord) -> str:
    added = "\n".join(f"+ {p}" for p in change.added_paragraphs)
    removed = "\n".join(f"- {p}" for p in change.removed_paragraphs)
    modified = "\n".join(
        f"- {p.before}\n+ {p.after}" for p in change.modified_paragraphs
    )
    tag_line = ", ".join(change.tags) if change.tags else "none detected"

    return (
        f"Company: {change.company_name}\n"
        f"Document: {change.policy_label}\n"
        f"Dates: {change.from_date} → {change.to_date}\n"
        f"Detected tags: {tag_line}\n\n"
        f"Added paragraphs:\n{_clamp(added) or '(none)'}\n\n"
        f"Modified paragraphs (before → after):\n{_clamp(modified) or '(none)'}\n\n"
        f"Removed paragraphs:\n{_clamp(removed) or '(none)'}\n\n"
        "Write a 2–3 sentence plain-English summary of what changed "
        "in this document."
    )


def generate_summary(
    change: ChangeRecord,
    *,
    model: str = DEFAULT_MODEL,
    token: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    client: httpx.Client | None = None,
) -> str | None:
    """Return a summary string for this change, or None if unavailable."""
    token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get(
        "GITHUB_MODELS_TOKEN"
    )
    if not token:
        log.info("No GitHub token available; skipping LLM summary for %s", change.id)
        return None

    payload = {
        "model": model,
        "temperature": 0.2,
        "max_tokens": 220,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(change)},
        ],
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
    }

    owned = client is None
    cm = client if client is not None else httpx.Client(timeout=timeout)
    try:
        resp = cm.post(GITHUB_MODELS_ENDPOINT, json=payload, headers=headers)
    except httpx.HTTPError as err:
        log.warning("LLM call failed for %s: %s", change.id, err)
        return None
    finally:
        if owned:
            cm.close()

    if resp.status_code >= 400:
        snippet = resp.text[:200].replace("\n", " ")
        log.warning(
            "LLM non-2xx for %s: %s %s", change.id, resp.status_code, snippet
        )
        return None

    try:
        data = resp.json()
        choices = data.get("choices") or []
        if not choices:
            log.warning("LLM empty choices for %s: %s", change.id, data)
            return None
        message = choices[0].get("message") or {}
        content = message.get("content")
        if not isinstance(content, str):
            log.warning("LLM unexpected content shape for %s: %s", change.id, data)
            return None
    except (KeyError, ValueError) as err:
        log.warning("LLM parse error for %s: %s", change.id, err)
        return None

    summary = content.strip()
    return summary or None
