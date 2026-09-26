"""Google Places API (New) enricher.

Queries Google Places API for a place (matching a name + address hint from
our DB) and returns canonical metadata: display name, formatted address,
coordinates, editorial summary, first photo URL.

- Endpoints: https://places.googleapis.com/v1/places:searchText (find),
  https://places.googleapis.com/v1/places/{id} (details).
- Auth: X-Goog-Api-Key header. Key comes from MYGENEVA_GOOGLE_MAPS_KEY env.
- Field mask (X-Goog-FieldMask): required — we ask for only what we store.
- Language: 'fr' so editorial_summary comes in French when available.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Optional

import httpx

log = logging.getLogger(__name__)


API_BASE = "https://places.googleapis.com/v1"
LANGUAGE = "fr"


class GooglePlacesConfigError(RuntimeError):
    """Raised when the API key is missing or malformed."""


def _get_api_key() -> str:
    key = os.environ.get("MYGENEVA_GOOGLE_MAPS_KEY")
    if not key:
        raise GooglePlacesConfigError(
            "MYGENEVA_GOOGLE_MAPS_KEY env var is not set. Export your Google "
            "Maps Platform API key (the one you already use for Maps Static) "
            "before running the enricher."
        )
    return key


@dataclass(frozen=True)
class PlaceEnrichment:
    google_place_id: str
    name: Optional[str]
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    description: Optional[str]
    image_url: Optional[str]


def find_place_id(
    query: str,
    *,
    location_bias_lat: Optional[float] = None,
    location_bias_lng: Optional[float] = None,
    client: Optional[httpx.Client] = None,
) -> Optional[str]:
    """Return the top-match Google place_id for a free-text query, or None.

    A location bias (Geneva by default) narrows results to the right region —
    matters when a place name is ambiguous ("La Gravière" exists elsewhere).
    """
    key = _get_api_key()
    owned = client is None
    client = client or httpx.Client(timeout=15.0)
    body: dict = {
        "textQuery": query,
        "languageCode": LANGUAGE,
        "maxResultCount": 1,
    }
    if location_bias_lat is not None and location_bias_lng is not None:
        body["locationBias"] = {
            "circle": {
                "center": {"latitude": location_bias_lat, "longitude": location_bias_lng},
                "radius": 30000.0,   # 30km around Geneva covers canton + border
            }
        }
    try:
        resp = client.post(
            f"{API_BASE}/places:searchText",
            headers={
                "X-Goog-Api-Key": key,
                "X-Goog-FieldMask": "places.id",
                "Content-Type": "application/json",
            },
            json=body,
        )
        if resp.status_code != 200:
            log.warning("SearchText %s → HTTP %s: %s", query, resp.status_code, resp.text[:200])
            return None
        payload = resp.json()
        places = payload.get("places") or []
        if not places:
            return None
        return places[0].get("id")
    finally:
        if owned:
            client.close()


def fetch_place_details(
    google_place_id: str,
    *,
    photo_max_width_px: int = 800,
    client: Optional[httpx.Client] = None,
) -> Optional[PlaceEnrichment]:
    """Fetch canonical details for a Google place_id.

    Field mask asks only for what we store, which keeps the response small
    and the SKU billing tier honest (fewer fields = cheaper SKU class).
    """
    key = _get_api_key()
    owned = client is None
    client = client or httpx.Client(timeout=15.0)
    try:
        resp = client.get(
            f"{API_BASE}/places/{google_place_id}",
            headers={
                "X-Goog-Api-Key": key,
                "X-Goog-FieldMask": (
                    "displayName,formattedAddress,location,editorialSummary,photos"
                ),
                "Accept-Language": LANGUAGE,
            },
        )
        if resp.status_code != 200:
            log.warning(
                "Place Details %s → HTTP %s: %s",
                google_place_id, resp.status_code, resp.text[:200],
            )
            return None
        p = resp.json()
        loc = p.get("location") or {}
        display = p.get("displayName") or {}
        editorial = p.get("editorialSummary") or {}
        photos = p.get("photos") or []
        photo_url: Optional[str] = None
        if photos:
            # The `name` is the opaque handle; we build the media URL that
            # returns image bytes (Google redirects to a googleusercontent
            # URL under the hood).
            photo_name = photos[0].get("name")
            if photo_name:
                photo_url = (
                    f"{API_BASE}/{photo_name}/media"
                    f"?maxWidthPx={photo_max_width_px}&key={key}"
                )
        return PlaceEnrichment(
            google_place_id=google_place_id,
            name=display.get("text"),
            address=p.get("formattedAddress"),
            latitude=loc.get("latitude"),
            longitude=loc.get("longitude"),
            description=editorial.get("text"),
            image_url=photo_url,
        )
    finally:
        if owned:
            client.close()
