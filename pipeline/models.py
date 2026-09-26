from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class EventRaw:
    """One event as extracted by a scraper, before mapping to the DB schema.

    `external_id` is required — it's the site's own stable identifier and
    the key we use for idempotent upserts (composite key with `source_name`).

    `place_external_id` is the source's own venue identifier (e.g. `idL`
    on ladecadanse). When set, the runner upserts a Place row keyed by
    (source_name, place_external_id) and links the event via place_id.
    """

    source_name: str
    external_id: str
    title: str
    date_start: datetime            # UTC
    date_end: Optional[datetime]    # UTC
    genre: str                      # source-specific label (e.g. "fetes", "concerts")
    venue_name: str = ""
    address: str = ""
    description: str = ""
    source_url: str = ""
    image_url: str = ""
    place_external_id: Optional[str] = None
    extras: dict = field(default_factory=dict)
