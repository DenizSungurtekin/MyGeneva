from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class EventCategory(str, Enum):
    journee = "journee"
    soiree = "soiree"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Event(SQLModel, table=True):
    __tablename__ = "events"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str = ""
    category: EventCategory = Field(index=True)

    location_name: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: str = ""

    date_start: datetime = Field(index=True)
    date_end: Optional[datetime] = None

    image_url: Optional[str] = None

    source: Optional[str] = Field(default=None, index=True)
    source_url: Optional[str] = None
    external_id: Optional[str] = Field(default=None, index=True)
    place_id: Optional[int] = Field(default=None, foreign_key="places.id", index=True)
    is_verified: bool = Field(default=False)
    is_promoted: bool = Field(default=False, index=True)
    # Deterministic hash across sources — used to detect that two scrapers
    # picked up the same real-world event. Populated by the runner from
    # (normalized_title, local_date, place_signature). Indexed for fast lookup.
    dedup_key: Optional[str] = Field(default=None, index=True)
    # JSON array of alternate source URLs discovered by later scrapers that
    # matched this event's dedup_key. Persisted as text on SQLite / jsonb on
    # Postgres via SQLModel's default JSON handling.
    alt_source_urls: Optional[str] = None

    created_at: datetime = Field(default_factory=_utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=_utcnow, nullable=False)
