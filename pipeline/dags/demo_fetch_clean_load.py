"""Demo DAG: fetch → clean → load on a fake source.

Illustrates the pattern every real source scraper will follow once the legal
question is settled. Writes to the `sources` monitoring table on every
successful run so the operator can see the source is healthy.

Explicitly NOT a real scraper — see PROGRESS.md and socle.md §7.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from airflow import DAG
from airflow.operators.python import PythonOperator

# Airflow adds /opt/airflow/scripts to sys.path via the volume mount below —
# the DAG lives in /opt/airflow/dags so relative imports don't work.
import sys

sys.path.insert(0, "/opt/airflow/scripts")

from source_status import ensure_source, mark_failure, mark_success  # noqa: E402


SOURCE_NAME = "demo-fake-source"


def fetch(**_) -> list[dict]:
    """Simulate hitting an external source. Deterministic fake payload."""
    ensure_source(SOURCE_NAME, source_type="scraping")
    return [
        {
            "title": "Marché des artisans du Molard",
            "raw_when": "10h - 18h",
            "raw_where": "Vieille-Ville",
        },
        {
            "title": "Jazz au Sud des Alpes",
            "raw_when": "20h30 - 23h",
            "raw_where": "Plainpalais",
        },
    ]


def clean(ti, **_) -> list[dict]:
    raw = ti.xcom_pull(task_ids="fetch")
    cleaned = []
    for item in raw:
        cleaned.append(
            {
                "title": item["title"].strip(),
                "location_name": item["raw_where"].strip(),
                # In a real pipeline we'd parse `raw_when` into a proper
                # datetime and geocode the location here.
                "notes": f"seen at {item['raw_when']}",
            }
        )
    return cleaned


def load(ti, **_) -> None:
    """In a real DAG this would upsert into `events`. Here we just log and mark success."""
    cleaned = ti.xcom_pull(task_ids="clean")
    print(f"[demo] would load {len(cleaned)} rows into `events`")
    mark_success(SOURCE_NAME)


def _on_failure(context) -> None:  # pragma: no cover
    mark_failure(SOURCE_NAME)


default_args = {
    "owner": "mygeneva",
    "depends_on_past": False,
    "retries": 0,
    "on_failure_callback": _on_failure,
}


with DAG(
    dag_id="demo_fetch_clean_load",
    description="Illustrative fetch→clean→load pattern on a fake source.",
    default_args=default_args,
    schedule="@daily",
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    catchup=False,
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=10),
    tags=["mygeneva", "demo"],
) as dag:
    fetch_task = PythonOperator(task_id="fetch", python_callable=fetch)
    clean_task = PythonOperator(task_id="clean", python_callable=clean)
    load_task = PythonOperator(task_id="load", python_callable=load)

    fetch_task >> clean_task >> load_task
