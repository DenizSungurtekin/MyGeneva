"""Compute deterministic dedup keys so different sources describing the same
real-world event resolve to the same row.

The key is a sha1 over three normalized signals:
  1. Normalized title (lowercased, whitespace-collapsed, accents stripped).
  2. Local date (Europe/Zurich) of `date_start` — a party listed as Fri 23:00
     on ladecadanse and Fri 23:00 on villagedusoir should hash the same even
     if one source stores UTC and the other local.
  3. Place signature — the concrete `place_id` when we have it; otherwise a
     normalized venue-name fallback. Prevents different events with the same
     title on the same day at different venues from collapsing.

Notes:
- The hash is stable across runs (deterministic normalization).
- If a source doesn't supply either place_id or venue_name, the signature
  segment is empty — key is still valid but weaker (title + date only).
- We do NOT attempt fuzzy matching on titles: intentional. Cross-source
  merges should only happen when the input clearly matches. False negatives
  (duplicates) are a smaller UX cost than false positives (merging two
  distinct events).
"""
from __future__ import annotations

import hashlib
import re
import unicodedata
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo


LOCAL_TZ = ZoneInfo("Europe/Zurich")
_WHITESPACE_RE = re.compile(r"\s+")


def _normalize_text(s: str) -> str:
    if not s:
        return ""
    # Strip accents: "Pâquis" → "Paquis"
    stripped = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return _WHITESPACE_RE.sub(" ", stripped.lower().strip())


def compute_dedup_key(
    title: str,
    date_start: datetime,
    *,
    place_id: Optional[int] = None,
    venue_name: str = "",
) -> str:
    """Return the sha1 hex digest that identifies this real-world event."""
    local_date = date_start.astimezone(LOCAL_TZ).date().isoformat()
    if place_id is not None:
        place_sig = f"pid:{place_id}"
    else:
        place_sig = f"venue:{_normalize_text(venue_name)}"
    payload = "|".join([_normalize_text(title), local_date, place_sig])
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()
