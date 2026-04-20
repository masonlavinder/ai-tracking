"""Lightweight English-ish language detector.

Wayback Machine captures of localized sites (most visibly Meta's privacy
policy) routinely land in Finnish, Urdu, Spanish, and other languages
depending on which crawler saw the page. Those off-language captures
blow up downstream diffs because every paragraph appears "new" relative
to the nearest English snapshot.

A real language detector (fastText, langdetect) would be overkill and
adds a dependency. For our purpose — "is this recognizably English
prose?" — counting the occurrence of common English function words is
cheap, dependency-free, and accurate enough.
"""

from __future__ import annotations

import re

# Common English function words. Chosen because they appear in virtually
# every English privacy policy and have no cognates in the languages we
# see in captures (Finnish, Urdu, Spanish, German, French, Japanese).
_STOPWORDS = frozenset(
    {
        "the",
        "and",
        "of",
        "to",
        "a",
        "in",
        "that",
        "is",
        "for",
        "on",
        "with",
        "as",
        "by",
        "this",
        "are",
        "we",
        "you",
        "your",
        "our",
        "or",
        "be",
        "not",
        "have",
        "it",
        "may",
        "use",
        "from",
        "about",
    }
)

_TOKEN_RE = re.compile(r"[A-Za-z']+")
_MIN_STOPWORDS = 8
_SAMPLE_CHARS = 2000


def is_probably_english(text: str) -> bool:
    """True if the first few KB of `text` look like English prose.

    The threshold (at least 8 distinct stopwords) is deliberately
    conservative: a policy-sized chunk of real English always clears it;
    translated or non-Latin-script content rarely does.
    """
    if not text:
        return False
    sample = text[:_SAMPLE_CHARS]
    tokens = _TOKEN_RE.findall(sample.lower())
    if not tokens:
        return False
    seen = {t for t in tokens if t in _STOPWORDS}
    return len(seen) >= _MIN_STOPWORDS
