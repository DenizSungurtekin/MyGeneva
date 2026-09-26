from __future__ import annotations

from datetime import datetime, timezone

from pipeline.mapping import resolve_category, to_event_kwargs
from pipeline.models import EventRaw
from pipeline.sources.registry import by_name


def _raw(genre: str = "fetes", hour_utc: int = 21) -> EventRaw:
    """Default: 21h UTC on Sept 26 = 23h Europe/Zurich (CEST) → soirée."""
    return EventRaw(
        source_name="ladecadanse",
        external_id="42",
        title="Test",
        date_start=datetime(2026, 9, 26, hour_utc, 0, tzinfo=timezone.utc),
        date_end=None,
        genre=genre,
        venue_name="Café Vibes",
        address="Rue X 1 - Genève",
        description="d",
        source_url="https://example.com",
    )


def test_soiree_when_local_hour_at_or_after_17():
    """21h UTC in September = 23h CEST → soirée."""
    src = by_name("ladecadanse")
    assert resolve_category(_raw(hour_utc=21), src) == "soiree"


def test_journee_when_local_hour_before_17():
    """06h UTC in September = 08h CEST → journée (e.g. Désalpe de St-Cergue)."""
    src = by_name("ladecadanse")
    assert resolve_category(_raw(hour_utc=6), src) == "journee"


def test_cutoff_at_17_local_is_soiree():
    """15h UTC in September = 17h CEST — exactly the cutoff → soirée."""
    src = by_name("ladecadanse")
    assert resolve_category(_raw(hour_utc=15), src) == "soiree"


def test_cutoff_just_before_17_local_is_journee():
    """14:59 UTC in September = 16:59 CEST → still journée."""
    src = by_name("ladecadanse")
    raw = _raw()
    raw = EventRaw(
        source_name=raw.source_name,
        external_id=raw.external_id,
        title=raw.title,
        date_start=datetime(2026, 9, 26, 14, 59, tzinfo=timezone.utc),
        date_end=None,
        genre=raw.genre,
        venue_name=raw.venue_name,
        address=raw.address,
        description=raw.description,
        source_url=raw.source_url,
    )
    assert resolve_category(raw, src) == "journee"


def test_midnight_party_is_soiree():
    """22h UTC = 00h CEST → still soirée (party extending past midnight)."""
    src = by_name("ladecadanse")
    assert resolve_category(_raw(hour_utc=22), src) == "soiree"


def test_early_morning_after_night_end_is_journee():
    """04h UTC = 06h CEST → past the night cutoff → journée again."""
    src = by_name("ladecadanse")
    assert resolve_category(_raw(hour_utc=4), src) == "journee"


def test_category_ignores_genre_when_hour_available():
    """Genre alone doesn't drive category anymore — the local hour does."""
    src = by_name("ladecadanse")
    assert resolve_category(_raw(genre="fetes", hour_utc=6), src) == "journee"
    assert resolve_category(_raw(genre="expos", hour_utc=21), src) == "soiree"


def test_kwargs_carry_source_and_external_id():
    src = by_name("ladecadanse")
    kw = to_event_kwargs(_raw(), src)
    assert kw["source"] == "ladecadanse"
    assert kw["external_id"] == "42"
    assert kw["category"] == "soiree"
    assert kw["is_verified"] is False
