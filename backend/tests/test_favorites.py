from __future__ import annotations

from datetime import datetime, timezone


def _event(client, title="Concert"):
    payload = {
        "title": title,
        "description": "",
        "category": "soiree",
        "date_start": datetime(2026, 3, 5, 20, 0, tzinfo=timezone.utc).isoformat(),
    }
    return client.post("/events", json=payload).json()


def _restaurant(client, title="Bistrot"):
    payload = {"title": title, "rating": 4.5, "rating_count": 100}
    return client.post("/restaurants", json=payload).json()


def test_add_and_list_favorite_event(client):
    event = _event(client)
    response = client.post(
        "/favorites", json={"item_type": "event", "item_id": event["id"]}
    )
    assert response.status_code == 201
    favorite = response.json()
    assert favorite["item_type"] == "event"
    assert favorite["item_id"] == event["id"]
    assert favorite["user_id"] == "poc-user"

    response = client.get("/favorites")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_add_favorite_restaurant(client):
    restaurant = _restaurant(client)
    response = client.post(
        "/favorites", json={"item_type": "restaurant", "item_id": restaurant["id"]}
    )
    assert response.status_code == 201


def test_duplicate_favorite_returns_existing(client):
    event = _event(client)
    first = client.post(
        "/favorites", json={"item_type": "event", "item_id": event["id"]}
    ).json()
    second = client.post(
        "/favorites", json={"item_type": "event", "item_id": event["id"]}
    ).json()
    assert first["id"] == second["id"]

    response = client.get("/favorites")
    assert len(response.json()) == 1


def test_add_favorite_unknown_item_404(client):
    response = client.post(
        "/favorites", json={"item_type": "event", "item_id": 9999}
    )
    assert response.status_code == 404


def test_delete_favorite(client):
    event = _event(client)
    favorite = client.post(
        "/favorites", json={"item_type": "event", "item_id": event["id"]}
    ).json()

    response = client.delete(f"/favorites/{favorite['id']}")
    assert response.status_code == 204
    assert client.get("/favorites").json() == []


def test_delete_favorite_not_found(client):
    assert client.delete("/favorites/9999").status_code == 404


def test_favorites_ordered_newest_first(client):
    event_a = _event(client, title="A")
    event_b = _event(client, title="B")
    fav_a = client.post("/favorites", json={"item_type": "event", "item_id": event_a["id"]}).json()
    fav_b = client.post("/favorites", json={"item_type": "event", "item_id": event_b["id"]}).json()

    ids = [f["id"] for f in client.get("/favorites").json()]
    # Newest first.
    assert ids[0] == fav_b["id"]
    assert ids[1] == fav_a["id"]
