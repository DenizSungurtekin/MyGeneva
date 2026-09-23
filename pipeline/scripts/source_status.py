"""Helpers to update the `sources` monitoring table from Airflow tasks.

We intentionally use raw SQL via psycopg (rather than importing the backend's
SQLModel models) so the pipeline stays decoupled from the backend package —
Airflow containers don't need to install the whole backend to update source
health.
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Iterator, Optional

try:
    import psycopg  # noqa: F401
except ImportError as exc:  # pragma: no cover
    raise RuntimeError(
        "psycopg is required in the Airflow image. Install it via a "
        "_PIP_ADDITIONAL_REQUIREMENTS env var or a custom image."
    ) from exc

import psycopg


DEFAULT_URL = "postgresql://mygeneva:mygeneva@postgres:5432/mygeneva"


def _connection_url() -> str:
    # AIRFLOW_CONN_MYGENEVA_DB uses SQLAlchemy syntax (psycopg2 driver); psycopg
    # itself doesn't understand that prefix, so we normalise it here.
    raw = os.environ.get("AIRFLOW_CONN_MYGENEVA_DB") or os.environ.get(
        "MYGENEVA_DATABASE_URL", DEFAULT_URL
    )
    return (
        raw.replace("postgresql+psycopg2://", "postgresql://")
        .replace("postgresql+psycopg://", "postgresql://")
    )


@contextmanager
def _connect() -> Iterator[psycopg.Connection]:
    with psycopg.connect(_connection_url(), autocommit=True) as conn:
        yield conn


def ensure_source(
    name: str,
    *,
    source_type: str = "scraping",
    status: str = "unknown",
) -> None:
    """Insert the source row if missing — safe to call from any DAG task."""
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO sources (name, type, status)
            VALUES (%s, %s, %s)
            ON CONFLICT (name) DO NOTHING
            """,
            (name, source_type, status),
        )


def mark_success(name: str, at: Optional[datetime] = None) -> None:
    at = at or datetime.now(timezone.utc)
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            UPDATE sources
               SET last_success_at = %s,
                   status = 'ok'
             WHERE name = %s
            """,
            (at, name),
        )


def mark_failure(name: str, *, status: str = "error") -> None:
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE sources SET status = %s WHERE name = %s",
            (status, name),
        )
