"""DB access for the pipeline.

Local dev defaults to the backend's SQLite file so the scraper writes into
the same DB that FastAPI reads. In Airflow / Docker, set MYGENEVA_DATABASE_URL.
"""
from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SQLITE_PATH = REPO_ROOT / "backend" / "mygeneva.db"


def resolved_db_url() -> str:
    url = os.environ.get("MYGENEVA_DATABASE_URL")
    if url:
        return url
    return f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"


def make_engine() -> Engine:
    url = resolved_db_url()
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, echo=False, connect_args=connect_args)
