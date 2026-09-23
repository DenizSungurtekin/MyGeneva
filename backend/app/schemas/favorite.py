from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.favorite import FavoriteItemType


class FavoriteCreate(BaseModel):
    item_type: FavoriteItemType
    item_id: int


class FavoriteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    item_type: FavoriteItemType
    item_id: int
    created_at: datetime
