from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.restaurant import Restaurant
from app.schemas.restaurant import RestaurantCreate, RestaurantRead, RestaurantUpdate

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


@router.get("", response_model=List[RestaurantRead])
def list_restaurants(
    min_rating: Optional[float] = Query(default=None, ge=0, le=5),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
) -> List[Restaurant]:
    query = select(Restaurant)
    if min_rating is not None:
        query = query.where(Restaurant.rating >= min_rating)
    # Rating sort: prioritize higher rating, then higher review count (proxy for
    # reliability). NULLs go last on both fields.
    query = query.order_by(
        Restaurant.rating.desc().nulls_last(),
        Restaurant.rating_count.desc().nulls_last(),
    ).limit(limit)
    return list(session.exec(query).all())


@router.get("/{restaurant_id}", response_model=RestaurantRead)
def get_restaurant(
    restaurant_id: int, session: Session = Depends(get_session)
) -> Restaurant:
    restaurant = session.get(Restaurant, restaurant_id)
    if restaurant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found"
        )
    return restaurant


@router.post("", response_model=RestaurantRead, status_code=status.HTTP_201_CREATED)
def create_restaurant(
    payload: RestaurantCreate, session: Session = Depends(get_session)
) -> Restaurant:
    restaurant = Restaurant(**payload.model_dump())
    session.add(restaurant)
    session.commit()
    session.refresh(restaurant)
    return restaurant


@router.patch("/{restaurant_id}", response_model=RestaurantRead)
def update_restaurant(
    restaurant_id: int,
    payload: RestaurantUpdate,
    session: Session = Depends(get_session),
) -> Restaurant:
    restaurant = session.get(Restaurant, restaurant_id)
    if restaurant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found"
        )
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(restaurant, key, value)
    restaurant.updated_at = datetime.now(timezone.utc)
    session.add(restaurant)
    session.commit()
    session.refresh(restaurant)
    return restaurant


@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_restaurant(
    restaurant_id: int, session: Session = Depends(get_session)
) -> None:
    restaurant = session.get(Restaurant, restaurant_id)
    if restaurant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found"
        )
    session.delete(restaurant)
    session.commit()
