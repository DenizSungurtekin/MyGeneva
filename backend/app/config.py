from __future__ import annotations

from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parent.parent


def _normalize_pg_scheme(url: str) -> str:
    """Rewrite Railway / Heroku-style Postgres URLs to a scheme SQLAlchemy 2.x
    recognises. Their `DATABASE_URL` injectors use ``postgres://`` or
    ``postgresql://``, both of which SQLAlchemy 2 refuses unless we pin the
    driver. Everything else (SQLite, mysql+…, an already-explicit
    postgresql+psycopg…) is passed through unchanged."""
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"):]
    if url.startswith("postgresql://") and "+psycopg" not in url and "+psycopg2" not in url:
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(default="")
    poc_user_id: str = Field(default="poc-user")
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:8081",
            "http://localhost:19006",
            "http://localhost:19000",
            "exp://localhost:19000",
        ]
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return _normalize_pg_scheme(self.database_url)
        sqlite_path = BACKEND_DIR / "mygeneva.db"
        return f"sqlite:///{sqlite_path.as_posix()}"


settings = Settings()
