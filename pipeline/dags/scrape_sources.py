"""Airflow DAG: iterate all enabled sources and scrape J → J+7 each day.

Delegates every non-Airflow concern to `pipeline.runner.run_source`. The
DAG stays thin so the same logic can be exercised locally via
`python -m pipeline.run_source <name>` without Airflow.

Prerequisite in the Airflow image: `httpx`, `beautifulsoup4`, `lxml`,
`sqlalchemy`, and the repo mounted so `pipeline` and `backend` imports
resolve. Add via `_PIP_ADDITIONAL_REQUIREMENTS` in docker-compose.
"""
from __future__ import annotations

import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator


REPO_ROOT = Path("/opt/airflow/repo")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


DEFAULT_DAYS = 7


def _scrape(source_name: str, **_) -> dict:
    from pipeline.runner import run_source

    summary = run_source(source_name, start=date.today(), days=DEFAULT_DAYS)
    return {
        "source": summary.source_name,
        "parsed": summary.parsed,
        "inserted": summary.inserted,
        "updated": summary.updated,
        "empty_days": summary.empty_days,
        "errors": summary.errors,
    }


def _list_sources() -> list[str]:
    """Called at DAG-parse time — must not require heavy imports at module top."""
    from pipeline.sources.registry import SOURCES

    return [s.name for s in SOURCES]


default_args = {
    "owner": "mygeneva",
    "depends_on_past": False,
    "retries": 0,
}


with DAG(
    dag_id="scrape_sources",
    description="Iterate active sources and upsert events over a rolling window.",
    default_args=default_args,
    schedule="0 6 * * *",
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    catchup=False,
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=30),
    tags=["mygeneva", "scrape"],
) as dag:
    for source_name in _list_sources():
        PythonOperator(
            task_id=f"scrape_{source_name}",
            python_callable=_scrape,
            op_kwargs={"source_name": source_name},
        )
