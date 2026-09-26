from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.event import Event, EventCategory
from app.schemas.event import EventCreate, EventRead, EventUpdate

router = APIRouter(prefix="/events", tags=["events"])


def _apply_day_filter(query, day: date):
    """Keep events relevant to the given day (UTC boundaries).

    Category-aware:
    - `journee`: overlap. A marché running Sat–Sun appears on both days.
    - `soiree`: start-day only. A Friday-night party ending Saturday 04h stays
      on Friday — that's the natural "vendredi soir" mental model.
    """
    day_start = datetime.combine(day, time.min, tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1)

    starts_within_day = (Event.date_start >= day_start) & (Event.date_start < day_end)
    spans_across_day = (
        (Event.date_start < day_end)
        & (Event.date_end.is_not(None))
        & (Event.date_end > day_start)
    )

    journee_match = (Event.category == EventCategory.journee) & (
        starts_within_day | spans_across_day
    )
    soiree_match = (Event.category == EventCategory.soiree) & starts_within_day
    return query.where(journee_match | soiree_match)


@router.get("", response_model=List[EventRead])
def list_events(
    category: Optional[EventCategory] = Query(default=None),
    day: Optional[date] = Query(default=None, alias="date"),
    session: Session = Depends(get_session),
) -> List[Event]:
    query = select(Event)
    if category is not None:
        query = query.where(Event.category == category)
    if day is not None:
        query = _apply_day_filter(query, day)
    query = query.order_by(Event.date_start.asc())
    return list(session.exec(query).all())


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
