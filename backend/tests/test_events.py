from __future__ import annotations

from datetime import datetime, timedelta, timezone


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


def test_list_events_date_overlap(client):
    # Multi-day event: starts day 4, ends day 6. Querying day 5 should include it.
    start = datetime(2026, 3, 4, 22, 0, tzinfo=timezone.utc)
    end = datetime(2026, 3, 6, 2, 0, tzinfo=timezone.utc)
    client.post(
        "/events",
        json=_event_payload(title="Overlap", date_start=start.isoformat(), date_end=end.isoformat()),
    )

    response = client.get("/events", params={"date": "2026-03-05"})
    titles = [item["title"] for item in response.json()]
    assert titles == ["Overlap"]


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


def test_events_sorted_by_start(client):
    later = datetime(2026, 3, 5, 20, 0, tzinfo=timezone.utc)
    earlier = datetime(2026, 3, 5, 10, 0, tzinfo=timezone.utc)
    client.post("/events", json=_event_payload(title="Later", date_start=later.isoformat()))
    client.post("/events", json=_event_payload(title="Earlier", date_start=earlier.isoformat()))

    titles = [e["title"] for e in client.get("/events").json()]
    assert titles == ["Earlier", "Later"]
