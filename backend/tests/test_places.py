from __future__ import annotations

from datetime import datetime, timedelta, timezone


def _place_payload(**overrides):
    payload = {
        "name": "Motel Campo",
        "address": "Route des Jeunes 12 - Genève",
        "latitude": 46.20,
        "longitude": 6.14,
        "image_url": None,
        "description": "",
        "source": "manual",
        "external_id": None,
    }
    payload.update(overrides)
    return payload


def _event_payload_for_place(place_id: int, **overrides):
    now = datetime(2026, 9, 26, 22, 0, tzinfo=timezone.utc)
    payload = {
        "title": "Test party",
        "description": "",
        "category": "soiree",
        "location_name": "",
        "address": "",
        "date_start": now.isoformat(),
        "date_end": (now + timedelta(hours=4)).isoformat(),
        "image_url": None,
        "source": "manual",
        "place_id": place_id,
        "is_verified": False,
    }
    payload.update(overrides)
    return payload


def test_create_and_get_place(client):
    resp = client.post("/places", json=_place_payload())
    assert resp.status_code == 201, resp.text
    place = resp.json()
    assert place["id"] > 0
    assert place["name"] == "Motel Campo"

    resp = client.get(f"/places/{place['id']}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Motel Campo"


def test_list_places_ordered_by_favorite_count(client, session):
    from app.models.favorite import Favorite, FavoriteItemType

    popular = client.post("/places", json=_place_payload(name="Popular Place")).json()
    quiet = client.post("/places", json=_place_payload(name="Quiet Place")).json()

    # 3 users favorited the popular place, 0 for the quiet one.
    for i in range(3):
        session.add(
            Favorite(
                user_id=f"user-{i}",
                item_type=FavoriteItemType.place,
                item_id=popular["id"],
            )
        )
    session.commit()

    body = client.get("/places").json()
    names = [p["name"] for p in body]
    assert names == ["Popular Place", "Quiet Place"]


def test_list_places_search_filters_by_name_and_address(client):
    client.post("/places", json=_place_payload(name="Motel Campo", address="Route X - Genève"))
    client.post("/places", json=_place_payload(name="Le Chat Noir", address="rue Vautier - Carouge - Genève"))
    client.post("/places", json=_place_payload(name="AMR", address="Sud des Alpes - Genève"))

    resp = client.get("/places", params={"search": "motel"})
    names = [p["name"] for p in resp.json()]
    assert names == ["Motel Campo"]

    # Search matches the address too.
    resp = client.get("/places", params={"search": "carouge"})
    names = [p["name"] for p in resp.json()]
    assert names == ["Le Chat Noir"]

    # Under the 3-char threshold → filter is ignored (returns everything).
    resp = client.get("/places", params={"search": "mo"})
    assert len(resp.json()) == 3


def test_place_events_future_only_by_default(client):
    place = client.post("/places", json=_place_payload(name="Somewhere")).json()

    past = datetime.now(timezone.utc) - timedelta(days=10)
    future = datetime.now(timezone.utc) + timedelta(days=10)
    client.post(
        "/events",
        json=_event_payload_for_place(place["id"], title="Old", date_start=past.isoformat(), date_end=None),
    )
    client.post(
        "/events",
        json=_event_payload_for_place(place["id"], title="Soon", date_start=future.isoformat(), date_end=None),
    )

    resp = client.get(f"/places/{place['id']}/events").json()
    titles = [e["title"] for e in resp]
    assert titles == ["Soon"]

    # include_past=true returns everything.
    resp = client.get(f"/places/{place['id']}/events", params={"include_past": True}).json()
    titles = sorted(e["title"] for e in resp)
    assert titles == ["Old", "Soon"]


def test_update_place_image_url(client):
    place = client.post("/places", json=_place_payload(name="Curated")).json()
    resp = client.patch(f"/places/{place['id']}", json={"image_url": "https://example.com/img.jpg"})
    assert resp.status_code == 200
    assert resp.json()["image_url"] == "https://example.com/img.jpg"


def test_delete_place(client):
    place = client.post("/places", json=_place_payload(name="Doomed")).json()
    resp = client.delete(f"/places/{place['id']}")
    assert resp.status_code == 204
    assert client.get(f"/places/{place['id']}").status_code == 404


def test_get_place_not_found(client):
    assert client.get("/places/9999").status_code == 404


def test_place_events_not_found_returns_404(client):
    assert client.get("/places/9999/events").status_code == 404


def test_favorite_place(client):
    place = client.post("/places", json=_place_payload(name="Favme")).json()
    resp = client.post("/favorites", json={"item_type": "place", "item_id": place["id"]})
    assert resp.status_code == 201, resp.text
    fav = resp.json()
    assert fav["item_type"] == "place"
    assert fav["item_id"] == place["id"]


def test_favorite_place_not_found(client):
    resp = client.post("/favorites", json={"item_type": "place", "item_id": 9999})
    assert resp.status_code == 404
