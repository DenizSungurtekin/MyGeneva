from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.event import EventCategory


class EventCreate(BaseModel):
    title: str
    description: str = ""
    category: EventCategory
    location_name: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: str = ""
    date_start: datetime
    date_end: Optional[datetime] = None
    image_url: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    place_id: Optional[int] = None
    is_verified: bool = False


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[EventCategory] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    date_start: Optional[datetime] = None
    date_end: Optional[datetime] = None
    image_url: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    place_id: Optional[int] = None
    is_verified: Optional[bool] = None


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    category: EventCategory
    location_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: str
    date_start: datetime
    date_end: Optional[datetime] = None
    image_url: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    place_id: Optional[int] = None
    is_verified: bool
    is_promoted: bool = False
    created_at: datetime
    updated_at: datetime
