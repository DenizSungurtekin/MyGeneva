from __future__ import annotations

from typing import Iterator

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from app.config import settings


def _make_engine(url: str) -> Engine:
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(url, echo=False, connect_args=connect_args)


engine: Engine = _make_engine(settings.resolved_database_url)


def init_db() -> None:
    """Create tables directly from the models. Used in tests / quick dev.

    In production, Alembic migrations should be used instead.
    """
    # Import models so SQLModel.metadata knows about them.
    from app import models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
