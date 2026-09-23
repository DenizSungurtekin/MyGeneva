from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Restaurant(SQLModel, table=True):
    __tablename__ = "restaurants"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str = ""

    location_name: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: str = ""

    opening_hours: Optional[str] = None
    rating: Optional[float] = None
    rating_count: Optional[int] = None

    image_url: Optional[str] = None

    source: Optional[str] = None
    source_url: Optional[str] = None
    is_verified: bool = Field(default=False)

    created_at: datetime = Field(default_factory=_utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=_utcnow, nullable=False)
