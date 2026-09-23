from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class RestaurantCreate(BaseModel):
    title: str
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
    is_verified: bool = False


class RestaurantUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    opening_hours: Optional[str] = None
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    image_url: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    is_verified: Optional[bool] = None


class RestaurantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    location_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: str
    opening_hours: Optional[str] = None
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    image_url: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    is_verified: bool
    created_at: datetime
    updated_at: datetime
