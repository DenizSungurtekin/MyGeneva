"""CLI: enrich Place rows with Google Places metadata.

Usage:
  python -m pipeline.enrich_places                # fill empties only
  python -m pipeline.enrich_places --force        # refetch every place
  python -m pipeline.enrich_places --limit 5      # sanity-check a small batch

For each place needing enrichment:
  1. Text search on Google Places using the place's name + address hint,
     biased to Geneva coordinates.
  2. If a place_id is found, fetch its details (name, address, coords,
     editorialSummary, first photo).
  3. Update the DB row. Enrichment is authoritative for the fields we
     populate; source/external_id (ladecadanse link) are preserved.
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import text
from sqlalchemy.engine import Engine

from pipeline.db import make_engine
from pipeline.enrichers.google_places import (
    fetch_place_details,
    find_place_id,
    GooglePlacesConfigError,
    PlaceEnrichment,
)


# Geneva city center — used to bias search results toward the local region.
GENEVA_LAT = 46.204
GENEVA_LNG = 6.143

# Google's terms allow a rate up to ~50 QPS. We stay well below for safety.
INTER_CALL_SLEEP_S = 0.3

log = logging.getLogger("enrich_places")


def _iter_places_needing_enrichment(
    engine: Engine,
    *,
    force: bool,
    limit: Optional[int],
) -> list[dict]:
    if force:
        where = ""
    else:
        # A row is "needy" if we've never enriched it, or if enrichment
        # didn't fill image_url / description (Google may have improved
        # since the last run).
        where = "WHERE google_place_id IS NULL OR image_url IS NULL OR description = ''"
    limit_clause = f" LIMIT {limit}" if limit is not None else ""
    query = text(
        f"SELECT id, name, address FROM places {where} ORDER BY id{limit_clause}"
    )
    with engine.begin() as conn:
        rows = conn.execute(query).all()
    return [{"id": r[0], "name": r[1], "address": r[2]} for r in rows]


def _apply_enrichment(engine: Engine, place_id: int, e: PlaceEnrichment) -> None:
    now = datetime.now(timezone.utc)
    with engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE places SET "
                "google_place_id = :gpid, "
                # Only overwrite name/address/coords if Google returned them.
                "name = COALESCE(:name, name), "
                "address = COALESCE(:address, address), "
                "latitude = COALESCE(:lat, latitude), "
                "longitude = COALESCE(:lng, longitude), "
                # Description + image are what we mainly came for.
                "description = COALESCE(:desc, description), "
                "image_url = COALESCE(:img, image_url), "
                "updated_at = :now "
                "WHERE id = :id"
            ),
            {
                "gpid": e.google_place_id,
                "name": e.name,
                "address": e.address,
                "lat": e.latitude,
                "lng": e.longitude,
                "desc": e.description,
                "img": e.image_url,
                "now": now,
                "id": place_id,
            },
        )


def enrich_all(*, force: bool = False, limit: Optional[int] = None) -> dict:
    engine = make_engine()
    places = _iter_places_needing_enrichment(engine, force=force, limit=limit)
    log.info("%d places to enrich", len(places))
    found = 0
    missing = 0
    for row in places:
        query = f'{row["name"]} {row["address"] or ""}'.strip()
        gpid = find_place_id(
            query,
            location_bias_lat=GENEVA_LAT,
            location_bias_lng=GENEVA_LNG,
        )
        time.sleep(INTER_CALL_SLEEP_S)
        if not gpid:
            log.info("no match for id=%s %s", row["id"], row["name"])
            missing += 1
            continue
        details = fetch_place_details(gpid)
        time.sleep(INTER_CALL_SLEEP_S)
        if details is None:
            log.info("details failed for id=%s gpid=%s", row["id"], gpid)
            missing += 1
            continue
        _apply_enrichment(engine, row["id"], details)
        log.info(
            "enriched id=%s → %s (img=%s desc=%s chars)",
            row["id"],
            details.name,
            "yes" if details.image_url else "no",
            len(details.description or ""),
        )
        found += 1
    return {"attempted": len(places), "enriched": found, "unmatched": missing}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enrich places with Google Places metadata (name, address, coords, description, first photo)."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Refetch every place, even those already enriched.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Cap the number of places processed in this run.",
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        summary = enrich_all(force=args.force, limit=args.limit)
    except GooglePlacesConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(
        f"attempted={summary['attempted']} "
        f"enriched={summary['enriched']} "
        f"unmatched={summary['unmatched']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
