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


def _to_utc(day_ref: date, hour: int) -> datetime:
    return datetime.combine(day_ref, time(hour, 0), tzinfo=LOCAL_TZ).astimezone(timezone.utc)


def _apply_day_filter(query, day: date, category: Optional[EventCategory]):
    """Filter events strictly by category for the given day.

    Rules:
    - **Journée on day Y**: event starts on Y, OR started before Y and its
      `date_end` exceeds Y 08h local (multi-day event still running past
      morning). An event that ended before 08h local on Y is treated as
      finished (it's the tail of yesterday's day).
    - **Soirée on day Y**: event starts on Y and has category `soiree`. Never
      duplicated on day+1 — a Fri-night party ending Sat morning stays on Fri.

    The earlier "double category" bleed (journée event running past 17h also
    showing in soirée) was reverted — in practice it confused users more than
    it helped, and the category chip on the card made the feed look wrong.
    """
    day_start = datetime.combine(day, time.min, tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1)
    day_8h_local = _to_utc(day, DAY_MORNING_HOUR)

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
    soiree_day = (Event.category == EventCategory.soiree) & starts_within_day

    if category == EventCategory.soiree:
        return query.where(soiree_day)
    if category == EventCategory.journee:
        return query.where(journee_day)
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
    # Apply day + category filters first (they carry the double-cat / 8h rules).
    if day is not None:
        query = _apply_day_filter(query, day, category)
    elif category is not None:
        query = query.where(Event.category == category)
    # Then narrow further with the search keyword if it's long enough.
    search_active = search is not None and len(search.strip()) >= SEARCH_MIN_CHARS
    if search_active:
        pattern = f"%{search.strip()}%"
        query = query.where(
            Event.title.ilike(pattern) | Event.description.ilike(pattern)
        )
    query = query.order_by(Event.date_start.asc())
    return list(session.exec(query).all())


@router.get("/for-you", response_model=List[EventRead])
def list_event_feed(
    category: Optional[EventCategory] = Query(default=None),
    day: Optional[date] = Query(default=None, alias="date"),
    search: Optional[str] = Query(default=None, min_length=0, max_length=200),
    limit: Optional[int] = Query(default=None, ge=1, le=200),
    session: Session = Depends(get_session),
) -> List[Event]:
    """Personalised feed of events for a day+category.

    Current ranking (weakest → strongest tiebreak):
      1. RANDOM() — baseline shuffle for events with the same favorite count.
      2. COUNT(favorites) DESC — popular events float up.

    Reserved for later:
      - is_promoted DESC (Phase 4) — commercial partnerships.
      - favorite-place membership DESC (Phase 3) — events at places the user
        already favorited.

    Reuses the same day-window semantics as /events (double-category rule,
    8h next-day cutoff for journée). Accepts a `search` keyword that filters
    by title|description ILIKE.
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
        # Ranking priority (top → bottom):
        #   1. promoted events (commercial partnerships)
        #   2. events with the most favorites
        #   3. RANDOM() tiebreak
        # Reserved for later: favorite-place membership between (1) and (2).
        .order_by(desc(Event.is_promoted), desc(fav_count), func.random())
    )
    if day is not None:
        query = _apply_day_filter(query, day, category)
    elif category is not None:
        query = query.where(Event.category == category)
    if search is not None and len(search.strip()) >= SEARCH_MIN_CHARS:
        pattern = f"%{search.strip()}%"
        query = query.where(
            Event.title.ilike(pattern) | Event.description.ilike(pattern)
        )
    if limit is not None:
        query = query.limit(limit)
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


@router.patch("/{event_id}/promote", response_model=EventRead)
def set_event_promoted(
    event_id: int,
    promoted: bool = Query(default=True),
    session: Session = Depends(get_session),
) -> Event:
    """Toggle the commercial-partnership flag on an event.

    No auth today — the endpoint is open. Note this in docs when adding
    real users. Backend calls this manually via curl / DataGrip until
    an admin surface exists.
    """
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    event.is_promoted = promoted
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
