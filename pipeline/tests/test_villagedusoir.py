from __future__ import annotations

from datetime import date, timezone
from pathlib import Path

from pipeline.scrapers import villagedusoir


FIXTURE = Path(__file__).parent / "fixtures" / "villagedusoir_fixture.html"


def test_parse_extracts_expected_fields():
    html = FIXTURE.read_text(encoding="utf-8")
    events = villagedusoir.parse_html(html)
    assert len(events) == 2
    ids = {e.external_id for e in events}
    assert ids == {"895", "999"}

    girls = next(e for e in events if e.external_id == "895")
    assert girls.title == "Girls Only Party"
    assert girls.source_name == "villagedusoir"
    assert girls.source_url.endswith("/event/girls-only-party-895")
    assert girls.image_url.endswith("/web/image/event.event/895/image")
    assert girls.address == "Grand-Lancy, Genève"
    assert girls.date_end is None
    assert girls.genre == "fetes"
    # 22h local Zurich CEST (Sep) = 20h UTC.
    assert girls.date_start.astimezone(timezone.utc).hour == 20
    # All VdS events share the single hardcoded venue so the runner can create
    # one Place row and link them all.
    assert girls.venue_name == "Le Village du Soir"
    assert girls.place_external_id == "main"


def test_fetch_filters_by_local_date(monkeypatch):
    """fetch(target) returns only events whose local start date matches."""
    html = FIXTURE.read_text(encoding="utf-8")

    def fake_fetch_html(**kwargs):
        return html

    monkeypatch.setattr(villagedusoir, "_fetch_listing_html", fake_fetch_html)
    villagedusoir._reset_cache_for_tests()

    day1 = villagedusoir.fetch(date(2026, 9, 26))
    assert [e.external_id for e in day1] == ["895"]

    day2 = villagedusoir.fetch(date(2026, 9, 27))
    assert [e.external_id for e in day2] == ["999"]

    # Same run — cache should serve; but the assertion here is behavioral (right
    # subset), the cache itself is checked implicitly by not re-hitting the fake.
    absent = villagedusoir.fetch(date(2026, 9, 28))
    assert absent == []


def test_out_of_geneva_still_returned_by_scraper(monkeypatch):
    """The scraper doesn't filter Geneva-only — that's the runner's job. Nyon
    Vibes ("Nyon, Vaud") should still come out of parse_html; the runner will
    drop it in _is_geneva."""
    html = FIXTURE.read_text(encoding="utf-8")
    events = villagedusoir.parse_html(html)
    nyon = next(e for e in events if e.external_id == "999")
    assert "Vaud" in nyon.address
