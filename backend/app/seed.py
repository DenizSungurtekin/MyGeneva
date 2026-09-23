"""Seed the database with realistic Geneva test data.

Data uses the exact examples listed in design-reference.md so the app stays
consistent with the validated prototype.

Idempotent: running the script multiple times is safe — existing rows are
matched on their `title` and updated in-place.

Usage:
    python -m app.seed              # seed today (relative dates centered on today)
    python -m app.seed --reset      # wipe all events/restaurants/favorites/sources first
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, time, timedelta, timezone
from typing import Iterable, List

from sqlmodel import Session, delete, select

from app.database import engine, init_db
from app.models.event import Event, EventCategory
from app.models.favorite import Favorite
from app.models.restaurant import Restaurant
from app.models.source import Source, SourceStatus, SourceType


def _utc(day: date, hour: int, minute: int = 0) -> datetime:
    return datetime.combine(day, time(hour, minute), tzinfo=timezone.utc)


def _events_for(day: date) -> List[dict]:
    """Events spanning a single calendar day (day+evening)."""
    return [
        # --- Journée ---
        dict(
            title="Marché des artisans du Molard",
            description=(
                "Marché hebdomadaire d'artisans en plein cœur de la Vieille-Ville. "
                "Producteurs locaux, créations artisanales et petite restauration sur place."
            ),
            category=EventCategory.journee,
            location_name="Vieille-Ville",
            latitude=46.2044,
            longitude=6.1479,
            address="Place du Molard, 1204 Genève",
            date_start=_utc(day, 10),
            date_end=_utc(day, 18),
            image_url=None,
            source="seed",
            source_url=None,
            is_verified=True,
        ),
        dict(
            title="Balade à vélo au bord du lac",
            description=(
                "Parcours guidé le long du quai jusqu'au Jet d'eau, avec arrêts "
                "photo et anecdotes sur l'histoire de la rade."
            ),
            category=EventCategory.journee,
            location_name="Quai Gustave-Ador",
            latitude=46.2071,
            longitude=6.1636,
            address="Quai Gustave-Ador, 1207 Genève",
            date_start=_utc(day, 14),
            date_end=_utc(day, 16),
            image_url=None,
            source="seed",
            is_verified=True,
        ),
        dict(
            title="Visite guidée du Jardin Anglais",
            description=(
                "Découverte du Jardin Anglais et de son horloge fleurie avec un "
                "guide de l'Office du tourisme."
            ),
            category=EventCategory.journee,
            location_name="Jardin Anglais",
            latitude=46.2050,
            longitude=6.1503,
            address="Quai du Général-Guisan, 1204 Genève",
            date_start=_utc(day, 11),
            date_end=_utc(day, 12),
            image_url=None,
            source="seed",
            is_verified=True,
        ),
        # --- Soirée ---
        dict(
            title="Jazz au Sud des Alpes",
            description=(
                "Concert de jazz dans l'iconique club du Sud des Alpes. "
                "Programmation internationale et acoustique intimiste."
            ),
            category=EventCategory.soiree,
            location_name="Plainpalais",
            latitude=46.1953,
            longitude=6.1420,
            address="10 Rue des Alpes, 1201 Genève",
            date_start=_utc(day, 20, 30),
            date_end=_utc(day, 23, 0),
            image_url=None,
            source="seed",
            is_verified=True,
        ),
        dict(
            title="Projection en plein air — Parc La Grange",
            description=(
                "Cinéma sous les étoiles au Parc La Grange. "
                "Entrée libre, apporter une couverture."
            ),
            category=EventCategory.soiree,
            location_name="Parc La Grange",
            latitude=46.2085,
            longitude=6.1729,
            address="Parc La Grange, 1207 Genève",
            date_start=_utc(day, 21, 15),
            date_end=_utc(day, 23, 30),
            image_url=None,
            source="seed",
            is_verified=True,
        ),
        dict(
            title="Soirée salsa — L'Usine",
            description=(
                "Soirée salsa mensuelle à L'Usine avec DJ live et cours "
                "d'initiation en début de soirée."
            ),
            category=EventCategory.soiree,
            location_name="L'Usine",
            latitude=46.2044,
            longitude=6.1409,
            address="4 Place des Volontaires, 1204 Genève",
            date_start=_utc(day, 22, 0),
            date_end=_utc(day + timedelta(days=1), 2, 0),
            image_url=None,
            source="seed",
            is_verified=False,
        ),
        dict(
            title="Concert rock — La Gravière",
            description=(
                "Soirée rock avec deux groupes locaux en première partie, "
                "puis tête d'affiche à 21h."
            ),
            category=EventCategory.soiree,
            location_name="La Jonction",
            latitude=46.1988,
            longitude=6.1279,
            address="9 Rue des Vieux-Grenadiers, 1205 Genève",
            date_start=_utc(day, 19, 45),
            date_end=_utc(day, 23, 30),
            image_url=None,
            source="seed",
            is_verified=False,
        ),
    ]


RESTAURANTS: List[dict] = [
    dict(
        title="Café des Bains",
        description=(
            "Institution de Carouge, cuisine du marché et carte des vins soignée."
        ),
        location_name="Carouge",
        latitude=46.1817,
        longitude=6.1360,
        address="26 Rue des Bains, 1205 Genève",
        opening_hours="Lu-Ve 11:30-14:30, 18:30-23:00 · Sa 18:30-23:00",
        rating=4.6,
        rating_count=812,
        image_url=None,
        source="seed",
        is_verified=True,
    ),
    dict(
        title="La Buvette des Bains",
        description=(
            "Cuisine simple, terrasse face au lac aux Bains des Pâquis. "
            "Fondue en hiver, salades l'été."
        ),
        location_name="Pâquis",
        latitude=46.2109,
        longitude=6.1548,
        address="30 Quai du Mont-Blanc, 1201 Genève",
        opening_hours="Tous les jours 09:00-22:30",
        rating=4.3,
        rating_count=2450,
        image_url=None,
        source="seed",
        is_verified=True,
    ),
    dict(
        title="Chez Ma Cousine",
        description=(
            "Le poulet-frites-salade en Vieille-Ville, à prix imbattable."
        ),
        location_name="Vieille-Ville",
        latitude=46.2005,
        longitude=6.1489,
        address="6 Place du Bourg-de-Four, 1204 Genève",
        opening_hours="Tous les jours 11:00-23:00",
        rating=4.4,
        rating_count=1730,
        image_url=None,
        source="seed",
        is_verified=True,
    ),
]


SOURCES: List[dict] = [
    dict(name="seed", type=SourceType.manuel, status=SourceStatus.ok),
    dict(name="ville-de-geneve", type=SourceType.scraping, status=SourceStatus.unknown),
    dict(name="google-places", type=SourceType.api, status=SourceStatus.unknown),
]


def _upsert_events(session: Session, days: Iterable[date]) -> int:
    count = 0
    for day in days:
        for payload in _events_for(day):
            existing = session.exec(
                select(Event).where(
                    Event.title == payload["title"],
                    Event.date_start == payload["date_start"],
                )
            ).first()
            if existing is None:
                session.add(Event(**payload))
                count += 1
            else:
                for key, value in payload.items():
                    setattr(existing, key, value)
                existing.updated_at = datetime.now(timezone.utc)
                session.add(existing)
    return count


def _upsert_restaurants(session: Session) -> int:
    count = 0
    for payload in RESTAURANTS:
        existing = session.exec(
            select(Restaurant).where(Restaurant.title == payload["title"])
        ).first()
        if existing is None:
            session.add(Restaurant(**payload))
            count += 1
        else:
            for key, value in payload.items():
                setattr(existing, key, value)
            existing.updated_at = datetime.now(timezone.utc)
            session.add(existing)
    return count


def _upsert_sources(session: Session) -> int:
    count = 0
    for payload in SOURCES:
        existing = session.exec(
            select(Source).where(Source.name == payload["name"])
        ).first()
        if existing is None:
            session.add(Source(**payload))
            count += 1
        else:
            for key, value in payload.items():
                setattr(existing, key, value)
            session.add(existing)
    return count


def seed(*, reset: bool = False, days_around_today: int = 3) -> dict:
    init_db()

    with Session(engine) as session:
        if reset:
            session.exec(delete(Favorite))
            session.exec(delete(Event))
            session.exec(delete(Restaurant))
            session.exec(delete(Source))
            session.commit()

        today = datetime.now(timezone.utc).date()
        days = [
            today + timedelta(days=offset)
            for offset in range(-days_around_today, days_around_today + 1)
        ]

        events_added = _upsert_events(session, days)
        restaurants_added = _upsert_restaurants(session)
        sources_added = _upsert_sources(session)
        session.commit()

    return {
        "events_added": events_added,
        "restaurants_added": restaurants_added,
        "sources_added": sources_added,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Wipe all events/restaurants/favorites/sources before seeding.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=3,
        help="Seed events for [today - days, today + days] (default: 3).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    result = seed(reset=args.reset, days_around_today=args.days)
    print("Seed complete:", result)


if __name__ == "__main__":
    main()
