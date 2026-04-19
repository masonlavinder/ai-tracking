"""Shared fixtures for analysis tests."""

from __future__ import annotations

import json
from pathlib import Path


def write_snapshot(
    policies_root: Path,
    slug: str,
    policy_id: str,
    date_str: str,
    text: str,
    *,
    url: str = "https://example.com/privacy",
    policy_label: str = "Example Privacy Policy",
    policy_kind: str = "privacy_policy",
) -> None:
    """Write a synthetic `.txt`/`.meta.json` pair, mirroring scraper layout."""
    policy_dir = policies_root / slug / policy_id
    policy_dir.mkdir(parents=True, exist_ok=True)
    (policy_dir / f"{date_str}.txt").write_text(text, encoding="utf-8")
    meta = {
        "company_slug": slug,
        "policy_kind": policy_kind,
        "policy_label": policy_label,
        "url": url,
        "snapshot_date": date_str,
        "sha256": "fake",
    }
    with (policy_dir / f"{date_str}.meta.json").open("w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
        fh.write("\n")
