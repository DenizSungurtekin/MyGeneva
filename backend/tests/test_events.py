from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.models.favorite import Favorite, FavoriteItemType


def _event_payload(**overrides):
    now = datetime(2026, 9, 23, 20, 0, tzinfo=timezone.utc)
    payload = {
        "title": "Jazz au Sud des Alpes",
        "description": "Live jazz",
        "category": "soiree",
        "location_name": "Plainpalais",
        "latitude": 46.1953,
        "longitude": 6.142,
        "address": "10 Rue des Alpes",
        "date_start": now.isoformat(),
        "date_end": (now + timedelta(hours=2)).isoformat(),
        "image_url": None,
        "source": "seed",
    }
    payload.update(overrides)
    return payload


def test_create_and_get_event(client):
    response = client.post("/events", json=_event_payload())
    assert response.status_code == 201, response.text
    event = response.json()
    assert event["id"] > 0
    assert event["title"] == "Jazz au Sud des Alpes"
    assert event["category"] == "soiree"

    response = client.get(f"/events/{event['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Jazz au Sud des Alpes"


def test_list_events_filter_by_category(client):
    client.post("/events", json=_event_payload(title="A", category="journee"))
    client.post("/events", json=_event_payload(title="B", category="soiree"))
    client.post("/events", json=_event_payload(title="C", category="soiree"))

    response = client.get("/events", params={"category": "soiree"})
    assert response.status_code == 200
    titles = sorted(item["title"] for item in response.json())
    assert titles == ["B", "C"]


def test_list_events_filter_by_date(client):
    day1 = datetime(2026, 3, 5, 10, 0, tzinfo=timezone.utc)
    day2 = datetime(2026, 3, 6, 10, 0, tzinfo=timezone.utc)
    client.post("/events", json=_event_payload(title="Day1", date_start=day1.isoformat(), date_end=None))
    client.post("/events", json=_event_payload(title="Day2", date_start=day2.isoformat(), date_end=None))

    response = client.get("/events", params={"date": "2026-03-05"})
    assert response.status_code == 200
    titles = [item["title"] for item in response.json()]
    assert titles == ["Day1"]


def test_list_events_date_overlap_journee(client):
    # Multi-day journée event (marché Sat–Sun): should appear on the middle day too.
    start = datetime(2026, 3, 4, 22, 0, tzinfo=timezone.utc)
    end = datetime(2026, 3, 6, 2, 0, tzinfo=timezone.utc)
    client.post(
        "/events",
        json=_event_payload(
            title="Overlap",
            category="journee",
            date_start=start.isoformat(),
            date_end=end.isoformat(),
        ),
    )

    response = client.get("/events", params={"date": "2026-03-05"})
    titles = [item["title"] for item in response.json()]
    assert titles == ["Overlap"]


def test_journee_reaching_evening_appears_in_soiree_list(client):
    """A 'party' starting at 15h and ending at 22h should show under BOTH days."""
    start = datetime(2026, 3, 5, 13, 0, tzinfo=timezone.utc)   # 14h CET = 15h in Zurich once DST
    end = datetime(2026, 3, 5, 21, 0, tzinfo=timezone.utc)     # 22h CET
    client.post(
        "/events",
        json=_event_payload(
            title="Long Party",
            category="journee",
            date_start=start.isoformat(),
            date_end=end.isoformat(),
        ),
    )

    j = client.get("/events", params={"date": "2026-03-05", "category": "journee"}).json()
    assert [e["title"] for e in j] == ["Long Party"]

    s = client.get("/events", params={"date": "2026-03-05", "category": "soiree"}).json()
    assert [e["title"] for e in s] == ["Long Party"]


def test_journee_short_daytime_not_in_soiree_list(client):
    """A workshop 10h-14h stays journée only — no bleed into soirée."""
    start = datetime(2026, 3, 5, 9, 0, tzinfo=timezone.utc)    # 10h CET
    end = datetime(2026, 3, 5, 13, 0, tzinfo=timezone.utc)     # 14h CET
    client.post(
        "/events",
        json=_event_payload(
            title="Workshop",
            category="journee",
            date_start=start.isoformat(),
            date_end=end.isoformat(),
        ),
    )
    assert client.get("/events", params={"date": "2026-03-05", "category": "soiree"}).json() == []


def test_multi_day_journee_shows_on_next_day_only_if_past_8h(client):
    """A journée event that runs Sat 10h → Sun 03h should NOT appear on Sunday.

    Rationale: 03h Sunday is really the tail of Saturday's session. If the same
    fête has a proper Sunday listing, it belongs there, not here.
    """
    start = datetime(2026, 3, 7, 9, 0, tzinfo=timezone.utc)    # Sat 10h CET
    end = datetime(2026, 3, 8, 2, 0, tzinfo=timezone.utc)      # Sun 03h CET
    client.post(
        "/events",
        json=_event_payload(
            title="LateJournee",
            category="journee",
            date_start=start.isoformat(),
            date_end=end.isoformat(),
        ),
    )
    on_sat = client.get("/events", params={"date": "2026-03-07", "category": "journee"}).json()
    assert [e["title"] for e in on_sat] == ["LateJournee"]

    on_sun = client.get("/events", params={"date": "2026-03-08", "category": "journee"}).json()
    assert on_sun == []


def test_multi_day_journee_shows_on_next_day_if_past_8h(client):
    """A journée event Sat 10h → Sun 12h (marché long) DOES appear on Sunday."""
    start = datetime(2026, 3, 7, 9, 0, tzinfo=timezone.utc)    # Sat 10h CET
    end = datetime(2026, 3, 8, 11, 0, tzinfo=timezone.utc)     # Sun 12h CET
    client.post(
        "/events",
        json=_event_payload(
            title="LongMarket",
            category="journee",
            date_start=start.isoformat(),
            date_end=end.isoformat(),
        ),
    )
    on_sun = client.get("/events", params={"date": "2026-03-08", "category": "journee"}).json()
    assert [e["title"] for e in on_sun] == ["LongMarket"]


def test_list_events_soiree_stays_on_start_day(client):
    """A Fri-night party ending Sat morning belongs to Friday, not Saturday."""
    start = datetime(2026, 3, 5, 21, 0, tzinfo=timezone.utc)   # Thu 21h UTC = Fri 22h CET
    end = datetime(2026, 3, 6, 4, 0, tzinfo=timezone.utc)      # crosses midnight
    client.post(
        "/events",
        json=_event_payload(
            title="Night",
            category="soiree",
            date_start=start.isoformat(),
            date_end=end.isoformat(),
        ),
    )

    # Present on the start day.
    on_start = client.get("/events", params={"date": "2026-03-05"}).json()
    assert [e["title"] for e in on_start] == ["Night"]

    # Absent on the next day — even though the event technically spans into it.
    on_next = client.get("/events", params={"date": "2026-03-06"}).json()
    assert [e["title"] for e in on_next] == []


def test_get_event_not_found(client):
    response = client.get("/events/9999")
    assert response.status_code == 404


def test_update_event(client):
    created = client.post("/events", json=_event_payload()).json()
    response = client.patch(f"/events/{created['id']}", json={"title": "Renamed"})
    assert response.status_code == 200
    assert response.json()["title"] == "Renamed"
    # Untouched fields preserved.
    assert response.json()["location_name"] == "Plainpalais"


def test_delete_event(client):
    created = client.post("/events", json=_event_payload()).json()
    response = client.delete(f"/events/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/events/{created['id']}").status_code == 404


def _seed_favorites(session, event_id: int, count: int) -> None:
    """Insert `count` favorite rows for one event, each with a unique user_id.

    Bypasses the POST /favorites endpoint (which enforces uniqueness per
    user_id) so tests can simulate real popularity across many users.
    """
    for i in range(count):
        session.add(
            Favorite(
                user_id=f"user-{event_id}-{i}",
                item_type=FavoriteItemType.event,
                item_id=event_id,
            )
        )
    session.commit()


def test_highlights_orders_by_favorite_count(client, session):
    day = "2026-05-01"
    a = client.post("/events", json=_event_payload(title="A", date_start=f"{day}T18:00:00+00:00", date_end=None)).json()
    b = client.post("/events", json=_event_payload(title="B", date_start=f"{day}T19:00:00+00:00", date_end=None)).json()
    c = client.post("/events", json=_event_payload(title="C", date_start=f"{day}T20:00:00+00:00", date_end=None)).json()
    _seed_favorites(session, a["id"], 0)
    _seed_favorites(session, b["id"], 2)
    _seed_favorites(session, c["id"], 1)

    resp = client.get("/events/highlights", params={"date": day, "limit": 3})
    assert resp.status_code == 200
    titles = [e["title"] for e in resp.json()]
    assert titles == ["B", "C", "A"]


def test_highlights_random_when_no_favorites(client):
    """With 0 favorites everywhere, we still get `limit` events (order random)."""
    day = "2026-05-02"
    for name in ("A", "B", "C", "D", "E"):
        client.post(
            "/events",
            json=_event_payload(title=name, date_start=f"{day}T18:00:00+00:00", date_end=None),
        )
    resp = client.get("/events/highlights", params={"date": day, "limit": 3})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 3
    assert all(e["title"] in {"A", "B", "C", "D", "E"} for e in body)


def test_highlights_one_favorite_pinned_others_random(client, session):
    day = "2026-05-03"
    starred = client.post(
        "/events",
        json=_event_payload(title="Starred", date_start=f"{day}T18:00:00+00:00", date_end=None),
    ).json()
    for name in ("A", "B", "C"):
        client.post(
            "/events",
            json=_event_payload(title=name, date_start=f"{day}T19:00:00+00:00", date_end=None),
        )
    _seed_favorites(session, starred["id"], 1)

    resp = client.get("/events/highlights", params={"date": day, "limit": 3})
    body = resp.json()
    assert body[0]["title"] == "Starred"
    assert len(body) == 3


def test_highlights_respects_category_filter(client, session):
    day = "2026-05-04"
    j = client.post(
        "/events",
        json=_event_payload(title="Jday", category="journee", date_start=f"{day}T10:00:00+00:00", date_end=None),
    ).json()
    s = client.post(
        "/events",
        json=_event_payload(title="Snight", category="soiree", date_start=f"{day}T22:00:00+00:00", date_end=None),
    ).json()
    _seed_favorites(session, j["id"], 5)   # journée is very popular
    _seed_favorites(session, s["id"], 1)

    resp = client.get(
        "/events/highlights", params={"date": day, "category": "soiree", "limit": 3}
    )
    titles = [e["title"] for e in resp.json()]
    assert titles == ["Snight"]           # journée doesn't leak into soirée query


def test_highlights_empty_day_returns_empty(client):
    resp = client.get("/events/highlights", params={"date": "2026-05-05", "limit": 3})
    assert resp.status_code == 200
    assert resp.json() == []


def test_search_matches_title_case_insensitive(client):
    client.post("/events", json=_event_payload(title="Sven Väth au Motel Campo"))
    client.post("/events", json=_event_payload(title="Marché du Molard"))
    resp = client.get("/events", params={"search": "sven"})
    titles = [e["title"] for e in resp.json()]
    assert titles == ["Sven Väth au Motel Campo"]


def test_search_matches_description(client):
    client.post(
        "/events",
        json=_event_payload(title="Anonymous", description="Concert techno berlin scene"),
    )
    client.post("/events", json=_event_payload(title="Anonymous 2", description="Yoga en plein air"))
    resp = client.get("/events", params={"search": "techno"})
    titles = [e["title"] for e in resp.json()]
    assert titles == ["Anonymous"]


def test_search_ignored_below_min_chars(client):
    client.post("/events", json=_event_payload(title="Only match"))
    # 2-char query is below the threshold — falls back to the default listing.
    resp = client.get("/events", params={"search": "ma"})
    assert len(resp.json()) == 1     # everything returned, filter not applied


def test_search_respects_day_filter(client):
    """Search narrows the current day + category view, not the whole DB."""
    day1 = "2026-05-01"
    day2 = "2026-05-02"
    client.post(
        "/events",
        json=_event_payload(title="Sven at Motel", date_start=f"{day1}T21:00:00+00:00", date_end=None),
    )
    # Query on day2: the day1 event is out of scope.
    resp = client.get("/events", params={"date": day2, "search": "sven"})
    assert resp.json() == []
    # Query on day1: the day1 event matches.
    resp = client.get("/events", params={"date": day1, "search": "sven"})
    titles = [e["title"] for e in resp.json()]
    assert titles == ["Sven at Motel"]


def test_search_combined_with_category(client):
    client.post(
        "/events",
        json=_event_payload(title="Techno gig", category="soiree", date_end=None),
    )
    client.post(
        "/events",
        json=_event_payload(title="Techno lunch talk", category="journee", date_end=None),
    )
    resp = client.get("/events", params={"search": "techno", "category": "soiree"})
    titles = [e["title"] for e in resp.json()]
    assert titles == ["Techno gig"]


def test_events_sorted_by_start(client):
    later = datetime(2026, 3, 5, 20, 0, tzinfo=timezone.utc)
    earlier = datetime(2026, 3, 5, 10, 0, tzinfo=timezone.utc)
    client.post("/events", json=_event_payload(title="Later", date_start=later.isoformat()))
    client.post("/events", json=_event_payload(title="Earlier", date_start=earlier.isoformat()))

    titles = [e["title"] for e in client.get("/events").json()]
    assert titles == ["Earlier", "Later"]
