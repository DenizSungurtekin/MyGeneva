"""Scraper for villagedusoir.com — Geneva-region nightlife listings.

Site runs on Odoo Website; the events page uses schema.org Event microdata
which makes parsing straightforward and stable.

Design differences vs the ladecadanse scraper:
- ONE HTTP request returns every upcoming event (no per-day pagination).
  We memoise the fetched list at module level so the runner's per-day loop
  doesn't re-download for each call.
- The listing exposes only `addressLocality` (Commune, Canton) — no street.
  So we can't map to a Place row via a stable venue id. Events land with
  `place_id=None`, and dedup with ladecadanse falls back on
  (title + local_date + normalized venue_name).
- No `endDate` in the microdata → date_end = None.
"""
from __future__ import annotations

import logging
import re
import time
from datetime import date, datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

import httpx
from bs4 import BeautifulSoup, Tag

from pipeline.models import EventRaw

log = logging.getLogger(__name__)

SOURCE_NAME = "villagedusoir"
BASE_URL = "https://www.villagedusoir.com"
LISTING_URL = f"{BASE_URL}/event?date=upcoming&country=all&type=all"
USER_AGENT = "MyGeneva/0.1 (aggregateur genevois; contact: mygeneva@gmail.com)"
LOCAL_TZ = ZoneInfo("Europe/Zurich")
CRAWL_DELAY_S = 5
CACHE_TTL_S = 300   # a single CLI run rarely runs longer than this

# Every VdS event happens at the same physical venue — Le Village du Soir
# at Grand-Lancy. Hardcode a name + stable external_id so the runner's
# _upsert_place creates one shared Place row for all VdS events. Google
# Places enrichment (POST /places/{id}/refresh) can then fill in the exact
# address, photo, and description from the venue's real listing.
VENUE_NAME = "Le Village du Soir"
VENUE_EXTERNAL_ID = "main"

_cache: dict = {"fetched_at": 0.0, "events": None}


def _fetch_listing_html(*, client: Optional[httpx.Client] = None) -> str:
    owned = client is None
    if owned:
        client = httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=30.0)
    try:
        resp = client.get(LISTING_URL)
        return resp.text
    finally:
        if owned:
            client.close()


def _parse_event_article(article: Tag) -> Optional[EventRaw]:
    """Convert one <article itemscope> block into an EventRaw."""
    # External id from the cover container's data-res-id.
    cover = article.select_one("[data-res-id]")
    if cover is None:
        return None
    external_id = cover.get("data-res-id")
    if not external_id:
        return None

    # Title from itemprop=name.
    title_tag = article.select_one("[itemprop='name']")
    title = title_tag.get_text(strip=True) if title_tag else ""
    if not title:
        return None

    # Start date from <meta itemprop="startDate" content="2026-09-26T16:00:00"/>.
    # The site emits local Zurich time with no timezone suffix — attach LOCAL_TZ.
    start_meta = article.select_one("meta[itemprop='startDate']")
    if start_meta is None or not start_meta.get("content"):
        return None
    try:
        naive_start = datetime.fromisoformat(start_meta["content"])
    except ValueError:
        return None
    if naive_start.tzinfo is None:
        naive_start = naive_start.replace(tzinfo=LOCAL_TZ)
    date_start = naive_start.astimezone(ZoneInfo("UTC"))

    # Address: itemprop=addressLocality gives "Commune,   Canton". Whitespace
    # is inconsistent; collapse runs of spaces to keep _is_geneva happy.
    locality_tag = article.select_one("[itemprop='addressLocality']")
    address = ""
    if locality_tag:
        raw = locality_tag.get_text(" ", strip=True)
        address = re.sub(r"\s+", " ", raw).strip()

    # Detail URL from the wrapping <a>. Site uses /event/<slug>-<id>/register.
    # We strip /register to point users at the public page.
    detail_url = ""
    parent_link = article.find_parent("a")
    if parent_link and parent_link.get("href"):
        href = parent_link["href"]
        if href.endswith("/register"):
            href = href[: -len("/register")]
        detail_url = href if href.startswith("http") else BASE_URL + href

    # Cover image from background-image style on .o_record_cover_image.
    image_url = ""
    cover_image = article.select_one(".o_record_cover_image")
    if cover_image and cover_image.get("style"):
        m = re.search(r'url\(&#34;([^"&]+)&#34;\)', cover_image["style"]) or re.search(
            r"url\(['\"]([^'\"]+)['\"]\)", cover_image["style"]
        )
        if m:
            src = m.group(1)
            image_url = src if src.startswith("http") else BASE_URL + src

    return EventRaw(
        source_name=SOURCE_NAME,
        external_id=str(external_id),
        title=title,
        date_start=date_start,
        date_end=None,
        genre="fetes",              # VdS is nightlife-focused; all listings are "soirée"
        venue_name=VENUE_NAME,      # every VdS event is at this single venue
        address=address,
        description="",
        source_url=detail_url,
        image_url=image_url,
        place_external_id=VENUE_EXTERNAL_ID,
    )


def parse_html(html: str) -> list[EventRaw]:
    soup = BeautifulSoup(html, "lxml")
    events: list[EventRaw] = []
    for article in soup.select("article[itemscope][itemtype*='schema.org/Event']"):
        raw = _parse_event_article(article)
        if raw is not None:
            events.append(raw)
    return events


def _cached_events(*, client: Optional[httpx.Client] = None) -> list[EventRaw]:
    now = time.time()
    if _cache["events"] is not None and (now - _cache["fetched_at"]) < CACHE_TTL_S:
        return _cache["events"]
    html = _fetch_listing_html(client=client)
    events = parse_html(html)
    _cache["events"] = events
    _cache["fetched_at"] = now
    return events


def fetch(target: date) -> list[EventRaw]:
    """Return events whose local start-date equals `target`.

    The scraper's contract with the runner is per-day, but VdS gives us the
    whole upcoming list in one shot — we cache and slice locally.
    """
    all_events = _cached_events()
    return [
        e
        for e in all_events
        if e.date_start.astimezone(LOCAL_TZ).date() == target
    ]


def _reset_cache_for_tests() -> None:
    """Hook used by tests to force a re-fetch."""
    _cache["events"] = None
    _cache["fetched_at"] = 0.0
