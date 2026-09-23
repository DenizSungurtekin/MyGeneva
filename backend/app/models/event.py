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

    source: Optional[str] = None
    source_url: Optional[str] = None
    is_verified: bool = Field(default=False)

    created_at: datetime = Field(default_factory=_utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=_utcnow, nullable=False)
