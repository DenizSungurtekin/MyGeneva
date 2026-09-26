from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Place(SQLModel, table=True):
    __tablename__ = "places"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    address: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None
    description: str = ""

    # source = "ladecadanse" | "manual" (curated by hand)
    # external_id = idL from ladecadanse when source-scraped, null for manual entries
    source: Optional[str] = Field(default=None, index=True)
    external_id: Optional[str] = Field(default=None, index=True)

    created_at: datetime = Field(default_factory=_utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=_utcnow, nullable=False)
