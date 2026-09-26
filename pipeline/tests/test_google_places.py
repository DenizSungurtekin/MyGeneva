"""Unit tests for the Google Places enricher.

httpx is stubbed via a MockTransport so the tests don't hit the network
and don't need a real API key.
"""
from __future__ import annotations

import json

import httpx
import pytest

from pipeline.enrichers import google_places


@pytest.fixture(autouse=True)
def _api_key(monkeypatch):
    monkeypatch.setenv("MYGENEVA_GOOGLE_MAPS_KEY", "test-key")


def _client_returning(responses: dict[str, httpx.Response]) -> httpx.Client:
    """Build an httpx client that returns canned responses keyed by request path."""
    def handler(request: httpx.Request) -> httpx.Response:
        # match by "path + method" for simplicity
        key = f"{request.method} {request.url.path}"
        if key in responses:
            return responses[key]
        return httpx.Response(404, text=f"unmocked: {key}")
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_find_place_returns_top_place_id():
    client = _client_returning(
        {
            "POST /v1/places:searchText": httpx.Response(
                200,
                content=json.dumps({"places": [{"id": "ChIJfake"}]}),
                headers={"Content-Type": "application/json"},
            ),
        }
    )
    gpid = google_places.find_place_id("Motel Campo Genève", client=client)
    assert gpid == "ChIJfake"


def test_find_place_returns_none_when_no_match():
    client = _client_returning(
        {
            "POST /v1/places:searchText": httpx.Response(
                200,
                content=json.dumps({"places": []}),
                headers={"Content-Type": "application/json"},
            ),
        }
    )
    assert google_places.find_place_id("nothing exists", client=client) is None


def test_find_place_returns_none_on_http_error():
    client = _client_returning(
        {
            "POST /v1/places:searchText": httpx.Response(429, text="rate limited"),
        }
    )
    assert google_places.find_place_id("foo", client=client) is None


def test_fetch_place_details_parses_full_payload():
    payload = {
        "displayName": {"text": "Motel Campo", "languageCode": "fr"},
        "formattedAddress": "Route des Jeunes 12, 1227 Genève",
        "location": {"latitude": 46.20, "longitude": 6.14},
        "editorialSummary": {
            "text": "Club de nuit à Genève avec programmation techno.",
            "languageCode": "fr",
        },
        "photos": [
            {"name": "places/ChIJfake/photos/AT1234", "widthPx": 3000, "heightPx": 2000},
        ],
    }
    client = _client_returning(
        {
            "GET /v1/places/ChIJfake": httpx.Response(
                200,
                content=json.dumps(payload),
                headers={"Content-Type": "application/json"},
            ),
        }
    )
    e = google_places.fetch_place_details("ChIJfake", client=client)
    assert e is not None
    assert e.google_place_id == "ChIJfake"
    assert e.name == "Motel Campo"
    assert e.address == "Route des Jeunes 12, 1227 Genève"
    assert e.latitude == 46.20
    assert e.longitude == 6.14
    assert e.description == "Club de nuit à Genève avec programmation techno."
    assert e.image_url is not None
    assert "places/ChIJfake/photos/AT1234/media" in e.image_url
    assert "maxWidthPx=800" in e.image_url
    assert "key=test-key" in e.image_url


def test_fetch_place_details_handles_missing_optional_fields():
    """Some places have no editorial summary and no photos — the enricher
    should still return an object with those fields as None."""
    payload = {
        "displayName": {"text": "Empty Place", "languageCode": "fr"},
        "formattedAddress": "Rue X, Genève",
    }
    client = _client_returning(
        {
            "GET /v1/places/ChIJempty": httpx.Response(
                200,
                content=json.dumps(payload),
                headers={"Content-Type": "application/json"},
            ),
        }
    )
    e = google_places.fetch_place_details("ChIJempty", client=client)
    assert e is not None
    assert e.name == "Empty Place"
    assert e.address == "Rue X, Genève"
    assert e.description is None
    assert e.image_url is None
    assert e.latitude is None
    assert e.longitude is None


def test_translates_english_description_to_french(monkeypatch):
    """When editorialSummary comes back in a non-fr language, we translate."""
    calls: list[tuple[str, str, str]] = []

    def fake_translate(text: str, source_lang: str):
        calls.append((text, source_lang, "fr"))
        return f"[fr]{text}"

    monkeypatch.setattr(google_places, "_translate_to_french", fake_translate)

    payload = {
        "displayName": {"text": "Motel Campo", "languageCode": "fr"},
        "formattedAddress": "Route des Jeunes",
        "editorialSummary": {
            "text": "A former petrochemical space hosts this electronic club.",
            "languageCode": "en",
        },
    }
    client = _client_returning(
        {
            "GET /v1/places/ChIJx": httpx.Response(
                200,
                content=json.dumps(payload),
                headers={"Content-Type": "application/json"},
            ),
        }
    )
    e = google_places.fetch_place_details("ChIJx", client=client)
    assert e is not None
    assert e.description == "[fr]A former petrochemical space hosts this electronic club."
    # Called once, with the right source language.
    assert calls == [("A former petrochemical space hosts this electronic club.", "en", "fr")]


def test_no_translation_when_already_french(monkeypatch):
    called = []
    monkeypatch.setattr(
        google_places,
        "_translate_to_french",
        lambda text, lang: called.append(True) or "NEVER",
    )
    payload = {
        "displayName": {"text": "X", "languageCode": "fr"},
        "editorialSummary": {"text": "Déjà en français.", "languageCode": "fr"},
    }
    client = _client_returning(
        {
            "GET /v1/places/x": httpx.Response(
                200,
                content=json.dumps(payload),
                headers={"Content-Type": "application/json"},
            ),
        }
    )
    e = google_places.fetch_place_details("x", client=client)
    assert e is not None
    assert e.description == "Déjà en français."
    assert called == []


def test_translation_failure_falls_back_to_original(monkeypatch):
    """If deep-translator returns None (network hiccup), we keep the source text."""
    monkeypatch.setattr(google_places, "_translate_to_french", lambda t, l: None)
    payload = {
        "displayName": {"text": "X", "languageCode": "fr"},
        "editorialSummary": {"text": "Original english text.", "languageCode": "en"},
    }
    client = _client_returning(
        {
            "GET /v1/places/x": httpx.Response(
                200,
                content=json.dumps(payload),
                headers={"Content-Type": "application/json"},
            ),
        }
    )
    e = google_places.fetch_place_details("x", client=client)
    assert e is not None
    assert e.description == "Original english text."


def test_missing_api_key_raises():
    """Config error surfaces immediately, before any HTTP call."""
    import os

    saved = os.environ.pop("MYGENEVA_GOOGLE_MAPS_KEY", None)
    try:
        with pytest.raises(google_places.GooglePlacesConfigError):
            google_places.find_place_id("anything")
    finally:
        if saved is not None:
            os.environ["MYGENEVA_GOOGLE_MAPS_KEY"] = saved
