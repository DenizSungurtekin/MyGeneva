from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from typing import List, Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, func
from sqlmodel import Session, select

from app.database import get_session
from app.models.event import Event
from app.models.favorite import Favorite, FavoriteItemType
from app.models.place import Place
from app.schemas.event import EventRead
from app.schemas.place import PlaceCreate, PlaceRead, PlaceUpdate

router = APIRouter(prefix="/places", tags=["places"])


LOCAL_TZ = ZoneInfo("Europe/Zurich")
ACTIVITY_WINDOW_DAYS = 30
SEARCH_MIN_CHARS = 3


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@router.get("", response_model=List[PlaceRead])
def list_places(
    search: Optional[str] = Query(default=None, min_length=0, max_length=200),
    session: Session = Depends(get_session),
) -> List[Place]:
    """List places, ordered by overall popularity (favorites count desc),
    alphabetical name as tiebreak. Accepts a `search` keyword (ILIKE on name).

    Client-side reordering can float the current user's own favorites to the
    top on top of this baseline. We keep that layer in the mobile app so the
    endpoint stays user-agnostic (no auth needed).
    """
    fav_count = func.count(Favorite.id).label("fav_count")
    query = (
        select(Place, fav_count)
        .outerjoin(
            Favorite,
            and_(
                Favorite.item_type == FavoriteItemType.place,
                Favorite.item_id == Place.id,
            ),
        )
        .group_by(Place.id)
        .order_by(desc(fav_count), Place.name.asc())
    )
    if search is not None and len(search.strip()) >= SEARCH_MIN_CHARS:
        pattern = f"%{search.strip()}%"
        query = query.where(Place.name.ilike(pattern) | Place.address.ilike(pattern))
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
