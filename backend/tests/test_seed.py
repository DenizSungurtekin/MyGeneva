from __future__ import annotations

from sqlmodel import Session, select

from app.models.event import Event, EventCategory
from app.models.restaurant import Restaurant
from app.models.source import Source
from app.seed import _upsert_events, _upsert_restaurants, _upsert_sources


def test_seed_is_idempotent(session: Session):
    from datetime import date, timedelta

    days = [date(2026, 3, 5) + timedelta(days=i) for i in range(3)]
    first_events = _upsert_events(session, days)
    first_restaurants = _upsert_restaurants(session)
    first_sources = _upsert_sources(session)
    session.commit()

    second_events = _upsert_events(session, days)
    second_restaurants = _upsert_restaurants(session)
    second_sources = _upsert_sources(session)
    session.commit()

    assert first_events > 0
    assert first_restaurants > 0
    assert first_sources > 0
    # Second pass shouldn't add anything — everything gets updated in place.
    assert second_events == 0
    assert second_restaurants == 0
    assert second_sources == 0


def test_seed_covers_both_categories(session: Session):
    from datetime import date

    _upsert_events(session, [date(2026, 3, 5)])
    session.commit()

    journee = session.exec(
        select(Event).where(Event.category == EventCategory.journee)
    ).all()
    soiree = session.exec(
        select(Event).where(Event.category == EventCategory.soiree)
    ).all()
    assert len(journee) >= 3
    assert len(soiree) >= 4


def test_seed_includes_expected_prototype_items(session: Session):
    from datetime import date

    _upsert_events(session, [date(2026, 3, 5)])
    _upsert_restaurants(session)
    session.commit()

    expected_events = {
        "Marché des artisans du Molard",
        "Jazz au Sud des Alpes",
        "Balade à vélo au bord du lac",
    }
    actual_events = {
        e.title for e in session.exec(select(Event)).all()
    }
    assert expected_events.issubset(actual_events)

    expected_restaurants = {"Café des Bains", "La Buvette des Bains", "Chez Ma Cousine"}
    actual_restaurants = {r.title for r in session.exec(select(Restaurant)).all()}
    assert expected_restaurants == actual_restaurants


def test_seed_sources_registered(session: Session):
    _upsert_sources(session)
    session.commit()

    names = {s.name for s in session.exec(select(Source)).all()}
    assert {"seed", "ville-de-geneve", "google-places"}.issubset(names)
