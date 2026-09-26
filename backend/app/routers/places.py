from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from typing import List, Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func
from sqlmodel import Session, select

from app.database import get_session
from app.models.event import Event
from app.models.place import Place
from app.schemas.event import EventRead
from app.schemas.place import PlaceCreate, PlaceRead, PlaceUpdate

router = APIRouter(prefix="/places", tags=["places"])


LOCAL_TZ = ZoneInfo("Europe/Zurich")
ACTIVITY_WINDOW_DAYS = 30


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@router.get("", response_model=List[PlaceRead])
def list_places(session: Session = Depends(get_session)) -> List[Place]:
    """List places, ordered by number of upcoming events (next 30 days).

    Ties broken alphabetically by name. Places with zero upcoming events
    fall to the bottom of the list.
    """
    now = _utcnow()
    horizon = now + timedelta(days=ACTIVITY_WINDOW_DAYS)
    upcoming_count = func.count(Event.id).label("upcoming_count")
    query = (
        select(Place, upcoming_count)
        .outerjoin(
            Event,
            (Event.place_id == Place.id)
            & (Event.date_start >= now)
            & (Event.date_start < horizon),
        )
        .group_by(Place.id)
        .order_by(desc(upcoming_count), Place.name.asc())
    )
    rows = session.exec(query).all()
    return [row[0] for row in rows]


@router.get("/{place_id}", response_model=PlaceRead)
def get_place(place_id: int, session: Session = Depends(get_session)) -> Place:
    place = session.get(Place, place_id)
    if place is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
    return place


@router.get("/{place_id}/events", response_model=List[EventRead])
def list_place_events(
    place_id: int,
    include_past: bool = Query(default=False),
    session: Session = Depends(get_session),
) -> List[Event]:
    """Events happening at this place. Future-only by default, chronological."""
    place = session.get(Place, place_id)
    if place is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
    query = select(Event).where(Event.place_id == place_id)
    if not include_past:
        # Same logic as favorites screen: an event is "future" if its end (or
        # start when no end) is still ahead of now.
        query = query.where(
            (Event.date_end.is_not(None) & (Event.date_end >= _utcnow()))
            | (Event.date_end.is_(None) & (Event.date_start >= _utcnow()))
        )
    query = query.order_by(Event.date_start.asc())
    return list(session.exec(query).all())


@router.post("", response_model=PlaceRead, status_code=status.HTTP_201_CREATED)
def create_place(payload: PlaceCreate, session: Session = Depends(get_session)) -> Place:
    place = Place(**payload.model_dump())
    session.add(place)
    session.commit()
    session.refresh(place)
    return place


@router.patch("/{place_id}", response_model=PlaceRead)
def update_place(
    place_id: int,
    payload: PlaceUpdate,
    session: Session = Depends(get_session),
) -> Place:
    place = session.get(Place, place_id)
    if place is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(place, key, value)
    place.updated_at = _utcnow()
    session.add(place)
    session.commit()
    session.refresh(place)
    return place


@router.delete("/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_place(place_id: int, session: Session = Depends(get_session)) -> None:
    place = session.get(Place, place_id)
    if place is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
    session.delete(place)
    session.commit()
