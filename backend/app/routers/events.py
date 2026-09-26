from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from typing import List, Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, func
from sqlmodel import Session, select

from app.database import get_session
from app.models.event import Event, EventCategory
from app.models.favorite import Favorite, FavoriteItemType
from app.schemas.event import EventCreate, EventRead, EventUpdate

router = APIRouter(prefix="/events", tags=["events"])


LOCAL_TZ = ZoneInfo("Europe/Zurich")

# Hours that split day / evening in local Zurich time.
DAY_MORNING_HOUR = 8      # Multi-day journée events show on day+1 only if they last past this hour.
EVENING_START_HOUR = 17   # Same-day journée events also appear in the soirée list if they end at/after this hour.


def _to_utc(day_ref: date, hour: int) -> datetime:
    return datetime.combine(day_ref, time(hour, 0), tzinfo=LOCAL_TZ).astimezone(timezone.utc)


def _apply_day_filter(query, day: date, category: Optional[EventCategory]):
    """Filter events relevant to the given day, with category-aware semantics.

    Rules:
    - **Journée on day Y**: event starts on Y, OR started before Y and its
      `date_end` exceeds Y 08h local (multi-day event still running past
      morning). An event that ended before 08h local on Y is treated as
      finished (it's the tail of yesterday's day).
    - **Soirée on day Y**: event starts on Y and has category `soiree`. Never
      duplicated on day+1 — a Fri-night party ending Sat morning stays on Fri.
    - **Double category**: a `journee` event that starts on Y and ends at/after
      17h local on Y **also** appears in the soirée list for Y. Rock'n'roll
      parties starting at 15h are the poster child.
    """
    day_start = datetime.combine(day, time.min, tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1)
    day_8h_local = _to_utc(day, DAY_MORNING_HOUR)
    day_17h_local = _to_utc(day, EVENING_START_HOUR)

    starts_within_day = (Event.date_start >= day_start) & (Event.date_start < day_end)
    # Multi-day journée that reaches past this morning's 08h local.
    reaches_past_morning = (
        (Event.date_start < day_start)
        & (Event.date_end.is_not(None))
        & (Event.date_end > day_8h_local)
    )
    journee_day = (Event.category == EventCategory.journee) & (
        starts_within_day | reaches_past_morning
    )
    # Soirée events keep their strict start-day filter — no overlap into day+1.
    soiree_day = (Event.category == EventCategory.soiree) & starts_within_day
    # Journée events that ALSO deserve to be in the soirée list because they
    # last into the evening of the same day.
    journee_bleeds_into_soiree = (
        (Event.category == EventCategory.journee)
        & starts_within_day
        & (Event.date_end.is_not(None))
        & (Event.date_end >= day_17h_local)
    )

    if category == EventCategory.soiree:
        return query.where(soiree_day | journee_bleeds_into_soiree)
    if category == EventCategory.journee:
        return query.where(journee_day)
    # No category filter → return primary-category matches only (no double count).
    return query.where(journee_day | soiree_day)


SEARCH_MIN_CHARS = 3


@router.get("", response_model=List[EventRead])
def list_events(
    category: Optional[EventCategory] = Query(default=None),
    day: Optional[date] = Query(default=None, alias="date"),
    search: Optional[str] = Query(default=None, min_length=0, max_length=200),
    session: Session = Depends(get_session),
) -> List[Event]:
    query = select(Event)
    search_active = search is not None and len(search.strip()) >= SEARCH_MIN_CHARS
    if search_active:
        pattern = f"%{search.strip()}%"
        query = query.where(
            Event.title.ilike(pattern) | Event.description.ilike(pattern)
        )
        if category is not None:
            query = query.where(Event.category == category)
        # Search is global — deliberately ignores the day filter so users can
        # find an event across the whole scraped window with one keyword.
    elif day is not None:
        query = _apply_day_filter(query, day, category)
    elif category is not None:
        query = query.where(Event.category == category)
    query = query.order_by(Event.date_start.asc())
    return list(session.exec(query).all())


@router.get("/highlights", response_model=List[EventRead])
def list_event_highlights(
    category: Optional[EventCategory] = Query(default=None),
    day: Optional[date] = Query(default=None, alias="date"),
    limit: int = Query(default=3, ge=1, le=20),
    session: Session = Depends(get_session),
) -> List[Event]:
    """Top `limit` events for the given day + category, ranked by favorites.

    Ordering: primary by number of favorites (desc), tiebreak by RANDOM()
    (so events with the same favorite count — including all events with 0
    favorites — get shuffled). Reuses the same day-window semantics as
    /events (double-category, 8h next-day rule for journée).
    """
    fav_count = func.count(Favorite.id).label("fav_count")
    query = (
        select(Event, fav_count)
        .outerjoin(
            Favorite,
            and_(
                Favorite.item_type == FavoriteItemType.event,
                Favorite.item_id == Event.id,
            ),
        )
        .group_by(Event.id)
        .order_by(desc(fav_count), func.random())
        .limit(limit)
    )
    if day is not None:
        query = _apply_day_filter(query, day, category)
    elif category is not None:
        query = query.where(Event.category == category)
    rows = session.exec(query).all()
    return [row[0] for row in rows]


@router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: int, session: Session = Depends(get_session)) -> Event:
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(payload: EventCreate, session: Session = Depends(get_session)) -> Event:
    event = Event(**payload.model_dump())
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.patch("/{event_id}", response_model=EventRead)
def update_event(
    event_id: int,
    payload: EventUpdate,
    session: Session = Depends(get_session),
) -> Event:
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(event, key, value)
    event.updated_at = datetime.now(timezone.utc)
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, session: Session = Depends(get_session)) -> None:
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    session.delete(event)
    session.commit()
