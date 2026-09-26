from __future__ import annotations

from datetime import date, timezone
from pathlib import Path

from pipeline.scrapers import ladecadanse


FIXTURE = Path(__file__).parent / "fixtures" / "ladecadanse_fixture.html"


def test_parse_only_returns_fetes_genre():
    html = FIXTURE.read_text(encoding="utf-8")
    events = ladecadanse.parse_html(html, fallback_date=date(2026, 9, 26))
    # 2 events in fetes; concerts section is filtered out.
    assert len(events) == 2
    external_ids = {e.external_id for e in events}
    assert external_ids == {"999001", "999002"}


def test_parse_extracts_title_venue_address_and_source_url():
    html = FIXTURE.read_text(encoding="utf-8")
    events = ladecadanse.parse_html(html, fallback_date=date(2026, 9, 26))
    e = next(e for e in events if e.external_id == "999001")
    assert e.title == "Nuit techno au Motel Campo"
    assert e.venue_name == "Motel Campo"
    assert e.address == "Route des Jeunes 12 - Genève"
    assert e.source_url == "https://www.ladecadanse.ch/event/evenement.php?idE=999001"
    # Full-res URL (from <a href>), not the thumbnail (<img src>).
    assert e.image_url.endswith("999001_big.jpg")
    assert e.description.startswith("DJ set")
    assert e.genre == "fetes"


def test_gcal_dates_parsed_into_utc():
    """Local 23:00 Europe/Zurich in September (CEST = UTC+2) → 21:00 UTC."""
    html = FIXTURE.read_text(encoding="utf-8")
    events = ladecadanse.parse_html(html, fallback_date=date(2026, 9, 26))
    e = next(e for e in events if e.external_id == "999001")
    assert e.date_start.tzinfo is not None
    assert e.date_start.astimezone(timezone.utc).hour == 21     # 23h CEST → 21h UTC
    assert e.date_end is not None
    assert e.date_end.astimezone(timezone.utc).hour == 3        # 05h CEST → 03h UTC (J+1)


def test_missing_gcal_falls_back_to_target_date():
    """Event without Google Calendar link still gets a plausible date_start."""
    html = FIXTURE.read_text(encoding="utf-8")
    events = ladecadanse.parse_html(html, fallback_date=date(2026, 9, 26))
    e = next(e for e in events if e.external_id == "999002")
    # Fallback: the given target date at 20:00 local.
    assert e.date_start.astimezone(timezone.utc).date() == date(2026, 9, 26)
    assert e.date_end is None
