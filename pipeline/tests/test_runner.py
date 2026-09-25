"""End-to-end runner test with a fake scraper and an in-memory SQLite DB."""
from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

from pipeline import runner
from pipeline.models import EventRaw
from pipeline.sources import registry as reg
from pipeline.sources.registry import Source


BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent / "backend"


def _apply_backend_schema(engine) -> None:
    """Create the tables the runner writes to, using the backend's models.

    We use SQLModel.metadata rather than alembic here so this test is fast
    and doesn't hit the disk-backed alembic version tracking.
    """
    import sys

    sys.path.insert(0, str(BACKEND_ROOT))
    from sqlmodel import SQLModel

    from app import models  # noqa: F401 — registers tables

    SQLModel.metadata.create_all(engine)


def _fake_events_factory(events_by_day: dict[date, list[EventRaw]]):
    def _fetch(target: date) -> list[EventRaw]:
        return events_by_day.get(target, [])

    return _fetch


@pytest.fixture()
def engine():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    _apply_backend_schema(engine)
    return engine


@pytest.fixture()
def fake_source(monkeypatch, engine):
    """Inject a fake source into the registry so we don't hit the real site."""
    start_day = date(2026, 9, 26)
    events_map = {
        start_day: [
            EventRaw(
                source_name="fakesrc",
                external_id="1",
                title="Event A",
                date_start=datetime(2026, 9, 26, 22, 0, tzinfo=timezone.utc),
                date_end=None,
                genre="fetes",
                venue_name="Venue A",
                address="Rue A",
                description="",
                source_url="https://example.com/1",
            ),
            EventRaw(
                source_name="fakesrc",
                external_id="2",
                title="Event B",
                date_start=datetime(2026, 9, 26, 23, 0, tzinfo=timezone.utc),
                date_end=None,
                genre="fetes",
                venue_name="Venue B",
                address="",
                description="",
                source_url="",
            ),
        ],
    }
    src = Source(
        name="fakesrc",
        scraper=_fake_events_factory(events_map),
        kind="event",
        method="html_scrape",
        category_hint="soiree",
        freshness="daily",
        trust="community",
        schedule="0 6 * * *",
        homepage="https://fake.example",
        crawl_delay_s=0,
    )
    monkeypatch.setattr(reg, "SOURCES", [src])
    return src, start_day


def test_first_run_inserts_events(engine, fake_source):
    _src, start = fake_source
    summary = runner.run_source("fakesrc", start=start, days=1, engine=engine)
    assert summary.inserted == 2
    assert summary.updated == 0
    with engine.begin() as c:
        rows = c.execute(text("SELECT external_id, source, category FROM events")).all()
    assert len(rows) == 2
    assert {r[0] for r in rows} == {"1", "2"}
    assert all(r[1] == "fakesrc" for r in rows)
    assert all(r[2] == "soiree" for r in rows)


def test_second_run_updates_no_duplicates(engine, fake_source):
    _src, start = fake_source
    runner.run_source("fakesrc", start=start, days=1, engine=engine)
    summary2 = runner.run_source("fakesrc", start=start, days=1, engine=engine)
    assert summary2.inserted == 0
    assert summary2.updated == 2
    with engine.begin() as c:
        count = c.execute(text("SELECT COUNT(*) FROM events")).scalar()
    assert count == 2


def test_run_logs_scrape_run_row_per_day(engine, fake_source):
    _src, start = fake_source
    runner.run_source("fakesrc", start=start, days=3, engine=engine)
    with engine.begin() as c:
        rows = c.execute(
            text("SELECT parsed_count, inserted_count, status FROM scrape_runs ORDER BY id")
        ).all()
    assert len(rows) == 3
    assert rows[0] == (2, 2, "success")           # day 1: 2 events
    assert rows[1] == (0, 0, "success")           # day 2: empty
    assert rows[2] == (0, 0, "success")           # day 3: empty


def test_empty_days_reported(engine, fake_source):
    _src, start = fake_source
    summary = runner.run_source("fakesrc", start=start, days=3, engine=engine)
    assert summary.empty_days == 2


def test_disabled_source_is_skipped(engine, fake_source):
    _src, start = fake_source
    # First run creates the sources row.
    runner.run_source("fakesrc", start=start, days=1, engine=engine)
    with engine.begin() as c:
        c.execute(text("UPDATE sources SET enabled=0 WHERE name='fakesrc'"))
    summary = runner.run_source("fakesrc", start=start, days=1, engine=engine)
    assert summary.parsed == 0
    assert summary.inserted == 0
