from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PlaceCreate(BaseModel):
    name: str
    address: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None
    description: str = ""
    source: Optional[str] = None
    external_id: Optional[str] = None


class PlaceUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    external_id: Optional[str] = None


class PlaceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None
    description: str
    source: Optional[str] = None
    external_id: Optional[str] = None
    google_place_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
