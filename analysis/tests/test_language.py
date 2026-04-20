"""Tests for the English-ish language detector."""

from __future__ import annotations

from analysis.language import is_probably_english


ENGLISH_POLICY = """
We at Example want you to understand what information we collect, and
how we use and share it. That is why we encourage you to read our
Privacy Policy. This helps you use Example in the way that is right for
you.

In the Privacy Policy, we explain how we collect, use, share, retain,
and transfer information. We also let you know your rights.
"""

FINNISH_COOKIE_WALL = """
Sallitaanko Facebookin evästeiden käyttö tällä selaimella? Käytämme
evästeitä ja vastaavia tekniikoita auttaaksemme tarjoamaan sinulle
parempia ja yksilöllisempiä palveluita.
"""

URDU_HEAD = "Meta میں ہم چاہتے ہیں کہ آپ یہ جانیں کہ ہم کون سی معلومات جمع کرتے ہیں۔"


def test_english_policy_is_detected() -> None:
    assert is_probably_english(ENGLISH_POLICY) is True


def test_finnish_cookie_wall_is_rejected() -> None:
    assert is_probably_english(FINNISH_COOKIE_WALL) is False


def test_urdu_excerpt_is_rejected() -> None:
    assert is_probably_english(URDU_HEAD) is False


def test_empty_is_rejected() -> None:
    assert is_probably_english("") is False


def test_ascii_garbage_is_rejected() -> None:
    # A bunch of Latin letters without English grammar still shouldn't pass.
    assert is_probably_english("xyz abc qrs tuv wxyz lmn opq" * 50) is False
