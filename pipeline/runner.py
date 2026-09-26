"""Orchestrator: iterate a date window, call a source's scraper, upsert events.

Idempotent: rerunning is safe and won't create duplicates. Dedup key is
(events.source, events.external_id). Every run appends one row per target
date to `scrape_runs` for troubleshooting.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import text
from sqlalchemy.engine import Engine

from pipeline.db import make_engine
from pipeline.mapping import to_event_kwargs
from pipeline.models import EventRaw
from pipeline.sources.registry import Source, by_name

log = logging.getLogger(__name__)


@dataclass
class RunSummary:
    source_name: str
    days: int
    parsed: int
    inserted: int
    updated: int
    skipped: int
    empty_days: int
    errors: list[str]


# Address strings from ladecadanse follow the pattern
#   "Street - Commune - Canton/Country"
# The canton/country is always the last " - "-separated segment. An event whose
# last segment is "Genève" (or a bare " - Genève" with no commune) is in canton
# GE — covers Meyrin, Carouge, Plan-les-Ouates, etc. Anything else (Vaud, France,
# etc.) gets filtered out.
def _is_geneva(raw: EventRaw) -> bool:
    address = (raw.address or "").strip()
    if not address:
        return False
    last_segment = address.rsplit(" - ", 1)[-1].strip().lower()
    return last_segment == "genève"


def _has_valid_dates(raw: EventRaw) -> bool:
    """Reject events whose end is before their start.

    Some source entries have a buggy Google Calendar link where the day of
    date_end wasn't incremented (e.g. `20260926T230000/20260926T080000` for a
    party that actually ends Sunday morning). We can't heuristically fix these
    from the description without breaking on edge cases, so we drop them.
    """
    if raw.date_end is None:
        return True
    return raw.date_end > raw.date_start


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _sync_source_row(engine: Engine, source: Source) -> None:
    """Upsert the source's declarative metadata into the `sources` table."""
    with engine.begin() as conn:
        row = conn.execute(
            text("SELECT id FROM sources WHERE name = :name"),
            {"name": source.name},
        ).first()
        payload = {
            "name": source.name,
            "type": "scraping" if source.method == "html_scrape" else source.method,
            "enabled": True,
            "homepage": source.homepage,
            "category_hint": source.category_hint,
            "trust": source.trust,
            "schedule": source.schedule,
        }
        if row is None:
            conn.execute(
                text(
                    "INSERT INTO sources (name, type, enabled, homepage, "
                    "category_hint, trust, schedule, status) "
                    "VALUES (:name, :type, :enabled, :homepage, :category_hint, "
                    ":trust, :schedule, 'unknown')"
                ),
                payload,
            )
        else:
            conn.execute(
                text(
                    "UPDATE sources SET type=:type, homepage=:homepage, "
                    "category_hint=:category_hint, trust=:trust, schedule=:schedule "
                    "WHERE name=:name"
                ),
                payload,
            )


def _is_enabled(engine: Engine, source_name: str) -> bool:
    with engine.begin() as conn:
        row = conn.execute(
            text("SELECT enabled FROM sources WHERE name = :n"),
            {"n": source_name},
        ).first()
    return bool(row[0]) if row else True


def _upsert_place(engine: Engine, raw: EventRaw) -> Optional[int]:
    """Upsert the event's venue as a Place row and return its id.

    Dedup key is (source, external_id). If the raw event doesn't carry a
    place_external_id (source didn't expose a stable venue id), we don't
    create a place — the event stays place_id=NULL.
    """
    if not raw.place_external_id or not raw.venue_name:
        return None
    now = _utcnow()
    with engine.begin() as conn:
        existing = conn.execute(
            text(
                "SELECT id FROM places WHERE source = :source AND external_id = :ext"
            ),
            {"source": raw.source_name, "ext": raw.place_external_id},
        ).first()
        if existing is not None:
            # Refresh name + address if they've drifted (keep image_url as-is —
            # that's the curated field the user may have manually set).
            conn.execute(
                text(
                    "UPDATE places SET name=:name, address=:address, "
                    "updated_at=:now WHERE id=:id"
                ),
                {
                    "name": raw.venue_name,
                    "address": raw.address or "",
                    "now": now,
                    "id": existing[0],
                },
            )
            return int(existing[0])
        result = conn.execute(
            text(
                "INSERT INTO places (name, address, description, source, "
                "external_id, created_at, updated_at) VALUES "
                "(:name, :address, '', :source, :external_id, :now, :now) "
                "RETURNING id"
            ),
            {
                "name": raw.venue_name,
                "address": raw.address or "",
                "source": raw.source_name,
                "external_id": raw.place_external_id,
                "now": now,
            },
        )
        return int(result.scalar_one())


def _upsert_event(engine: Engine, source: Source, raw: EventRaw) -> str:
    """Return 'inserted' or 'updated'."""
    kwargs = to_event_kwargs(raw, source)
    place_id = _upsert_place(engine, raw)
    kwargs["place_id"] = place_id
    now = _utcnow()
    with engine.begin() as conn:
        existing = conn.execute(
            text(
                "SELECT id FROM events WHERE source = :source "
                "AND external_id = :external_id"
            ),
            {"source": raw.source_name, "external_id": raw.external_id},
        ).first()
        if existing is None:
            conn.execute(
                text(
                    "INSERT INTO events (title, description, category, "
                    "location_name, address, date_start, date_end, image_url, "
                    "source, source_url, external_id, place_id, is_verified, "
                    "created_at, updated_at) "
                    "VALUES (:title, :description, :category, :location_name, "
                    ":address, :date_start, :date_end, :image_url, :source, "
                    ":source_url, :external_id, :place_id, :is_verified, "
                    ":created_at, :updated_at)"
                ),
                {**kwargs, "created_at": now, "updated_at": now},
            )
            return "inserted"
        conn.execute(
            text(
                "UPDATE events SET title=:title, description=:description, "
                "category=:category, location_name=:location_name, "
                "address=:address, date_start=:date_start, date_end=:date_end, "
                "image_url=:image_url, source_url=:source_url, place_id=:place_id, "
                "updated_at=:updated_at WHERE id=:id"
            ),
            {**kwargs, "id": existing[0], "updated_at": now},
        )
        return "updated"


def _log_run(
    engine: Engine,
    *,
    source_name: str,
    target: date,
    url: str,
    parsed: int,
    inserted: int,
    updated: int,
    skipped: int,
    status: str,
    error: Optional[str],
    started_at: datetime,
    raw_html: Optional[str] = None,
) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO scrape_runs (source_name, target_date, url, "
                "http_status, raw_html, parsed_count, inserted_count, "
                "updated_count, skipped_count, status, error, started_at, "
                "finished_at) VALUES (:source_name, :target_date, :url, 200, "
                ":raw_html, :parsed, :inserted, :updated, :skipped, :status, "
                ":error, :started_at, :finished_at)"
            ),
            {
                "source_name": source_name,
                "target_date": datetime.combine(target, datetime.min.time(), tzinfo=timezone.utc),
                "url": url,
                "raw_html": raw_html,
                "parsed": parsed,
                "inserted": inserted,
                "updated": updated,
                "skipped": skipped,
                "status": status,
                "error": error,
                "started_at": started_at,
                "finished_at": _utcnow(),
            },
        )


def _mark_source_finished(
    engine: Engine,
    source_name: str,
    *,
    records: int,
    error: Optional[str],
) -> None:
    now = _utcnow()
    status = "error" if error else "ok"
    with engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE sources SET last_success_at=:ts, status=:status, "
                "last_error=:err, records_last_run=:n WHERE name=:name"
            ),
            {
                "ts": now if not error else None,
                "status": status,
                "err": error,
                "n": records,
                "name": source_name,
            },
        )


def run_source(
    source_name: str,
    *,
    start: date,
    days: int = 7,
    engine: Optional[Engine] = None,
    store_raw_html: bool = True,
) -> RunSummary:
    """Fetch `days` days starting from `start` and upsert events. Idempotent."""
    engine = engine or make_engine()
    source = by_name(source_name)
    _sync_source_row(engine, source)
    if not _is_enabled(engine, source_name):
        log.info("source %s disabled, skipping", source_name)
        return RunSummary(source_name, days, 0, 0, 0, 0, 0, [])

    parsed = inserted = updated = skipped = empty = 0
    errors: list[str] = []

    for offset in range(days):
        target = start + timedelta(days=offset)
        started = _utcnow()
        try:
            events = source.scraper(target)
        except Exception as exc:  # noqa: BLE001 — one bad day shouldn't kill the run
            msg = f"{target}: {type(exc).__name__}: {exc}"
            log.exception("scrape failed for %s / %s", source_name, target)
            errors.append(msg)
            _log_run(
                engine,
                source_name=source_name,
                target=target,
                url=f"https://www.ladecadanse.ch/index.php?courant={target.isoformat()}",
                parsed=0,
                inserted=0,
                updated=0,
                skipped=0,
                status="failure",
                error=msg,
                started_at=started,
            )
            continue

        if not events:
            empty += 1

        day_inserted = day_updated = day_skipped = 0
        for raw in events:
            if not _has_valid_dates(raw):
                log.info(
                    "skip corrupted dates for %s/%s: %s → %s",
                    raw.source_name, raw.external_id, raw.date_start, raw.date_end,
                )
                day_skipped += 1
                continue
            if not _is_geneva(raw):
                day_skipped += 1
                continue
            outcome = _upsert_event(engine, source, raw)
            if outcome == "inserted":
                day_inserted += 1
            else:
                day_updated += 1
        parsed += len(events)
        inserted += day_inserted
        updated += day_updated
        skipped += day_skipped

        _log_run(
            engine,
            source_name=source_name,
            target=target,
            url=f"https://www.ladecadanse.ch/index.php?courant={target.isoformat()}",
            parsed=len(events),
            inserted=day_inserted,
            updated=day_updated,
            skipped=day_skipped,
            status="success",
            error=None,
            started_at=started,
            raw_html=None,  # not captured by the scraper today — placeholder for future
        )

    _mark_source_finished(
        engine,
        source_name,
        records=inserted + updated,   # records that actually landed in the DB
        error="; ".join(errors) if errors else None,
    )

    return RunSummary(
        source_name=source_name,
        days=days,
        parsed=parsed,
        inserted=inserted,
        updated=updated,
        skipped=skipped,
        empty_days=empty,
        errors=errors,
    )
