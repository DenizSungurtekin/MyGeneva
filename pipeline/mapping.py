"""Convert an EventRaw (source-shape) into kwargs for the backend Event model."""
from __future__ import annotations

from typing import Literal
from zoneinfo import ZoneInfo

from pipeline.models import EventRaw
from pipeline.sources.registry import Source


Category = Literal["journee", "soiree"]


# A local start-hour in [SOIREE_EVENING_START, 24) ∪ [0, SOIREE_NIGHT_END) is a
# soirée. The two intervals cover both the "starting in the evening" case (17h+)
# and the "starting after midnight but still nightlife" case (a party listed at
# Sat 00:00 that's really the extension of Fri night).
SOIREE_EVENING_START = 17
SOIREE_NIGHT_END = 5
LOCAL_TZ = ZoneInfo("Europe/Zurich")


def resolve_category(raw: EventRaw, source: Source) -> Category:
    """Category is decided by local start hour, not by the source's genre label.

    An 08h désalpe classified by the source as "fêtes" is a daytime event; a
    22h vernissage listed under "expos" is a soirée; a midnight techno set is
    a soirée even though `hour == 0`. The hour is authoritative.
    Falls back to the source's `category_hint` only if start hour is missing.
    """
    if raw.date_start is not None:
        local_hour = raw.date_start.astimezone(LOCAL_TZ).hour
        is_night = local_hour >= SOIREE_EVENING_START or local_hour < SOIREE_NIGHT_END
        return "soiree" if is_night else "journee"
    if source.category_hint in ("journee", "soiree"):
        return source.category_hint  # type: ignore[return-value]
    return "journee"


def to_event_kwargs(raw: EventRaw, source: Source) -> dict:
    """Fields that get written to the `events` table."""
    return {
        "title": raw.title,
        "description": raw.description[:2000],
        "category": resolve_category(raw, source),
        "location_name": raw.venue_name,
        "address": raw.address,
        "date_start": raw.date_start,
        "date_end": raw.date_end,
        "image_url": raw.image_url or None,
        "source": raw.source_name,
        "source_url": raw.source_url or None,
        "external_id": raw.external_id,
        "is_verified": False,
    }
