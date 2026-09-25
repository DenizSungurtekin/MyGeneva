from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class ScrapeRunStatus(str, Enum):
    success = "success"
    partial = "partial"
    failure = "failure"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ScrapeRun(SQLModel, table=True):
    __tablename__ = "scrape_runs"

    id: Optional[int] = Field(default=None, primary_key=True)
    source_name: str = Field(index=True)
    target_date: Optional[datetime] = Field(default=None, index=True)
    url: str = ""
    http_status: Optional[int] = None
    raw_html: Optional[str] = None
    parsed_count: int = 0
    inserted_count: int = 0
    updated_count: int = 0
    skipped_count: int = 0
    status: ScrapeRunStatus = Field(default=ScrapeRunStatus.success)
    error: Optional[str] = None
    started_at: datetime = Field(default_factory=_utcnow, nullable=False)
    finished_at: Optional[datetime] = None
