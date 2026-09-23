from __future__ import annotations


def _payload(**overrides):
    data = {
        "title": "Café des Bains",
        "description": "Bistrot",
        "location_name": "Carouge",
        "latitude": 46.1817,
        "longitude": 6.136,
        "address": "26 Rue des Bains",
        "opening_hours": "Lu-Ve 11:30-14:30",
        "rating": 4.6,
        "rating_count": 812,
    }
    data.update(overrides)
    return data


def test_create_and_get_restaurant(client):
    response = client.post("/restaurants", json=_payload())
    assert response.status_code == 201, response.text
    restaurant = response.json()
    assert restaurant["rating"] == 4.6
    assert restaurant["title"] == "Café des Bains"

    response = client.get(f"/restaurants/{restaurant['id']}")
    assert response.status_code == 200


def test_list_restaurants_sorted_by_rating(client):
    client.post("/restaurants", json=_payload(title="Low", rating=3.1, rating_count=50))
    client.post("/restaurants", json=_payload(title="High", rating=4.9, rating_count=200))
    client.post("/restaurants", json=_payload(title="Mid", rating=4.2, rating_count=100))

    titles = [r["title"] for r in client.get("/restaurants").json()]
    assert titles == ["High", "Mid", "Low"]


def test_list_restaurants_min_rating(client):
    client.post("/restaurants", json=_payload(title="Low", rating=3.1))
    client.post("/restaurants", json=_payload(title="High", rating=4.9))

    response = client.get("/restaurants", params={"min_rating": 4.0})
    titles = [r["title"] for r in response.json()]
    assert titles == ["High"]


def test_list_restaurants_null_rating_last(client):
    client.post("/restaurants", json=_payload(title="Unrated", rating=None, rating_count=None))
    client.post("/restaurants", json=_payload(title="Good", rating=4.5, rating_count=100))

    titles = [r["title"] for r in client.get("/restaurants").json()]
    assert titles == ["Good", "Unrated"]


def test_get_restaurant_not_found(client):
    assert client.get("/restaurants/9999").status_code == 404


def test_update_restaurant(client):
    created = client.post("/restaurants", json=_payload()).json()
    response = client.patch(f"/restaurants/{created['id']}", json={"rating": 4.8})
    assert response.status_code == 200
    assert response.json()["rating"] == 4.8


def test_delete_restaurant(client):
    created = client.post("/restaurants", json=_payload()).json()
    response = client.delete(f"/restaurants/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/restaurants/{created['id']}").status_code == 404
