from __future__ import annotations

from datetime import datetime, timezone

from pipeline.mapping import resolve_category, to_event_kwargs
from pipeline.models import EventRaw
from pipeline.sources.registry import by_name


def _raw(genre: str = "fetes") -> EventRaw:
    return EventRaw(
        source_name="ladecadanse",
        external_id="42",
        title="Test",
        date_start=datetime(2026, 9, 26, 21, 0, tzinfo=timezone.utc),
        date_end=None,
        genre=genre,
        venue_name="Café Vibes",
        address="Rue X 1",
        description="d",
        source_url="https://example.com",
    )


def test_category_from_fetes_is_soiree():
    src = by_name("ladecadanse")
    assert resolve_category(_raw("fetes"), src) == "soiree"


def test_category_from_expos_is_journee():
    src = by_name("ladecadanse")
    assert resolve_category(_raw("expos"), src) == "journee"


def test_category_from_unknown_genre_uses_source_hint():
    src = by_name("ladecadanse")   # category_hint = "soiree"
    assert resolve_category(_raw("unknown-genre"), src) == "soiree"


def test_kwargs_carry_source_and_external_id():
    src = by_name("ladecadanse")
    kw = to_event_kwargs(_raw(), src)
    assert kw["source"] == "ladecadanse"
    assert kw["external_id"] == "42"
    assert kw["category"] == "soiree"
    assert kw["is_verified"] is False
