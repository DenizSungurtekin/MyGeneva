from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class SourceType(str, Enum):
    scraping = "scraping"
    api = "api"
    manuel = "manuel"


class SourceStatus(str, Enum):
    ok = "ok"
    warning = "warning"
    error = "error"
    unknown = "unknown"


class Source(SQLModel, table=True):
    __tablename__ = "sources"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    type: SourceType = Field(default=SourceType.scraping)
    enabled: bool = Field(default=True)
    homepage: Optional[str] = None
    category_hint: Optional[str] = None
    trust: Optional[str] = None
    schedule: Optional[str] = None
    last_success_at: Optional[datetime] = None
    last_error: Optional[str] = None
    records_last_run: Optional[int] = None
    status: SourceStatus = Field(default=SourceStatus.unknown)
