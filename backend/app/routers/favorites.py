from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.config import settings
from app.database import get_session
from app.models.event import Event
from app.models.favorite import Favorite, FavoriteItemType
from app.models.place import Place
from app.models.restaurant import Restaurant
from app.schemas.favorite import FavoriteCreate, FavoriteRead

router = APIRouter(prefix="/favorites", tags=["favorites"])


def _target_exists(
    session: Session, item_type: FavoriteItemType, item_id: int
) -> bool:
    if item_type == FavoriteItemType.event:
        return session.get(Event, item_id) is not None
    if item_type == FavoriteItemType.restaurant:
        return session.get(Restaurant, item_id) is not None
    if item_type == FavoriteItemType.place:
        return session.get(Place, item_id) is not None
    return False


@router.get("", response_model=List[FavoriteRead])
def list_favorites(session: Session = Depends(get_session)) -> List[Favorite]:
    query = (
        select(Favorite)
        .where(Favorite.user_id == settings.poc_user_id)
        .order_by(Favorite.created_at.desc())
    )
    return list(session.exec(query).all())


@router.post("", response_model=FavoriteRead, status_code=status.HTTP_201_CREATED)
def create_favorite(
    payload: FavoriteCreate, session: Session = Depends(get_session)
) -> Favorite:
    if not _target_exists(session, payload.item_type, payload.item_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{payload.item_type.value} {payload.item_id} does not exist",
        )

    existing = session.exec(
        select(Favorite).where(
            Favorite.user_id == settings.poc_user_id,
            Favorite.item_type == payload.item_type,
            Favorite.item_id == payload.item_id,
        )
    ).first()
    if existing is not None:
        return existing

    favorite = Favorite(
        user_id=settings.poc_user_id,
        item_type=payload.item_type,
        item_id=payload.item_id,
    )
    session.add(favorite)
    session.commit()
    session.refresh(favorite)
    return favorite


@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_favorite(
    favorite_id: int, session: Session = Depends(get_session)
) -> None:
    favorite = session.get(Favorite, favorite_id)
    if favorite is None or favorite.user_id != settings.poc_user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found"
        )
    session.delete(favorite)
    session.commit()
