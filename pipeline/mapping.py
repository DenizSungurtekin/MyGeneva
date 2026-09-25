"""Convert an EventRaw (source-shape) into kwargs for the backend Event model."""
from __future__ import annotations

from typing import Literal

from pipeline.models import EventRaw
from pipeline.sources.registry import Source


Category = Literal["journee", "soiree"]


# Genre → target category. Sources can add their own genres over time; a
# genre absent from this table falls back to the source's `category_hint`.
_GENRE_TO_CATEGORY: dict[str, Category] = {
    "fetes": "soiree",
    "concerts": "soiree",
    "cine": "journee",
    "theatre": "journee",
    "expos": "journee",
    "divers": "journee",
}


def resolve_category(raw: EventRaw, source: Source) -> Category:
    cat = _GENRE_TO_CATEGORY.get(raw.genre)
    if cat is not None:
        return cat
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
