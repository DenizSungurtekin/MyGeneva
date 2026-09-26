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
                date_start=datetime(2026, 9, 26, 19, 0, tzinfo=timezone.utc),
                date_end=None,
                genre="fetes",
                venue_name="Venue A",
                address="Rue A - Genève",
                description="",
                source_url="https://example.com/1",
            ),
            EventRaw(
                source_name="fakesrc",
                external_id="2",
                title="Event B",
                date_start=datetime(2026, 9, 26, 20, 0, tzinfo=timezone.utc),
                date_end=None,
                genre="fetes",
                venue_name="Venue B",
                address="Rue B - Meyrin - Genève",
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


def test_non_geneva_events_are_skipped(engine, monkeypatch):
    """Events with an address outside canton GE must not land in the DB."""
    start = date(2026, 9, 26)
    events_map = {
        start: [
            EventRaw(
                source_name="fakesrc",
                external_id="1",
                title="Désalpe de St-Cergue",
                date_start=datetime(2026, 9, 26, 8, 0, tzinfo=timezone.utc),
                date_end=None,
                genre="fetes",
                venue_name="Place du Vallon",
                address="Place du Vallon - St-Cergue - Vaud",
                description="",
                source_url="",
            ),
            EventRaw(
                source_name="fakesrc",
                external_id="2",
                title="Ferney bal",
                date_start=datetime(2026, 9, 26, 20, 0, tzinfo=timezone.utc),
                date_end=None,
                genre="fetes",
                venue_name="Château",
                address="All. du Château - Ferney-Voltaire - France",
                description="",
                source_url="",
            ),
            EventRaw(
                source_name="fakesrc",
                external_id="3",
                title="Genève soirée",
                date_start=datetime(2026, 9, 26, 21, 0, tzinfo=timezone.utc),
                date_end=None,
                genre="fetes",
                venue_name="Motel Campo",
                address="Route des Jeunes - Genève",
                description="",
                source_url="",
            ),
        ]
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

    summary = runner.run_source("fakesrc", start=start, days=1, engine=engine)

    assert summary.parsed == 3            # scraper found 3
    assert summary.inserted == 1          # only the GE one landed
    assert summary.skipped == 2           # St-Cergue + Ferney rejected

    with engine.begin() as c:
        rows = c.execute(text("SELECT title FROM events")).all()
    assert [r[0] for r in rows] == ["Genève soirée"]

    with engine.begin() as c:
        scrape = c.execute(
            text("SELECT parsed_count, inserted_count, skipped_count FROM scrape_runs")
        ).one()
    assert scrape == (3, 1, 2)


def test_corrupted_dates_are_skipped(engine, monkeypatch):
    """Events whose date_end precedes date_start are rejected outright."""
    start = date(2026, 9, 26)
    events_map = {
        start: [
            EventRaw(
                source_name="fakesrc",
                external_id="broken",
                title="Vice Party (bad dates)",
                date_start=datetime(2026, 9, 26, 21, 0, tzinfo=timezone.utc),
                date_end=datetime(2026, 9, 26, 6, 0, tzinfo=timezone.utc),   # 15h AVANT
                genre="fetes",
                venue_name="",
                address="Halle W - Vernier - Genève",
                description="",
                source_url="",
            ),
            EventRaw(
                source_name="fakesrc",
                external_id="ok",
                title="Fine event",
                date_start=datetime(2026, 9, 26, 20, 0, tzinfo=timezone.utc),
                date_end=datetime(2026, 9, 26, 22, 0, tzinfo=timezone.utc),
                genre="fetes",
                venue_name="",
                address="Rue - Genève",
                description="",
                source_url="",
            ),
        ]
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

    summary = runner.run_source("fakesrc", start=start, days=1, engine=engine)
    assert summary.parsed == 2
    assert summary.inserted == 1
    assert summary.skipped == 1
    with engine.begin() as c:
        rows = c.execute(text("SELECT external_id FROM events")).all()
    assert [r[0] for r in rows] == ["ok"]


def test_dedup_across_sources_merges_second(engine, monkeypatch):
    """Two sources describing the same event → one row, second URL kept as alt."""
    start = date(2026, 9, 26)
    same_start = datetime(2026, 9, 26, 22, 0, tzinfo=timezone.utc)
    src1_event = EventRaw(
        source_name="src1",
        external_id="ext1",
        title="Nuit Techno",
        date_start=same_start,
        date_end=None,
        genre="fetes",
        venue_name="Motel Campo",
        address="Rue X - Genève",
        description="",
        source_url="https://source1.example/event/1",
    )
    src2_event = EventRaw(
        source_name="src2",
        external_id="ext2",
        title="Nuit Techno",  # same title
        date_start=same_start,  # same date
        date_end=None,
        genre="fetes",
        venue_name="Motel Campo",  # same venue (no place_id, falls back to venue_name)
        address="Rue X - Genève",
        description="",
        source_url="https://source2.example/event/xyz",
    )
    src1 = Source(
        name="src1",
        scraper=_fake_events_factory({start: [src1_event]}),
        kind="event",
        method="html_scrape",
        category_hint="soiree",
        freshness="daily",
        trust="community",
        schedule="0 6 * * *",
        homepage="https://source1.example",
        crawl_delay_s=0,
    )
    src2 = Source(
        name="src2",
        scraper=_fake_events_factory({start: [src2_event]}),
        kind="event",
        method="html_scrape",
        category_hint="soiree",
        freshness="daily",
        trust="community",
        schedule="0 6 * * *",
        homepage="https://source2.example",
        crawl_delay_s=0,
    )
    monkeypatch.setattr(reg, "SOURCES", [src1, src2])

    s1 = runner.run_source("src1", start=start, days=1, engine=engine)
    s2 = runner.run_source("src2", start=start, days=1, engine=engine)

    assert s1.inserted == 1
    assert s2.inserted == 0        # not inserted — dedup hit
    assert s2.merged == 1          # counted as merged
    with engine.begin() as c:
        rows = c.execute(
            text("SELECT source, source_url, alt_source_urls FROM events")
        ).all()
    assert len(rows) == 1
    row = rows[0]
    assert row[0] == "src1"                        # primary source untouched
    assert row[1] == "https://source1.example/event/1"
    assert "https://source2.example/event/xyz" in (row[2] or "")


def test_disabled_source_is_skipped(engine, fake_source):
    _src, start = fake_source
    # First run creates the sources row.
    runner.run_source("fakesrc", start=start, days=1, engine=engine)
    with engine.begin() as c:
        c.execute(text("UPDATE sources SET enabled=0 WHERE name='fakesrc'"))
    summary = runner.run_source("fakesrc", start=start, days=1, engine=engine)
    assert summary.parsed == 0
    assert summary.inserted == 0
