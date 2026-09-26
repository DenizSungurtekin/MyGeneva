from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class FavoriteItemType(str, Enum):
    event = "event"
    restaurant = "restaurant"
    place = "place"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Favorite(SQLModel, table=True):
    __tablename__ = "favorites"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    item_type: FavoriteItemType = Field(index=True)
    item_id: int = Field(index=True)
    created_at: datetime = Field(default_factory=_utcnow, nullable=False)
