"""Scraper for ladecadanse.ch — Geneva community event board.

Only the 'Fêtes' section is extracted (category `soiree`). Times are
parsed from the Google Calendar export link (which carries an unambiguous
ISO datetime range) rather than from the visible "HH:MM – HH:MM" text.

Respects the site's `Crawl-delay: 15` via the module-level throttle.
User-Agent identifies MyGeneva.
"""
from __future__ import annotations

import logging
import re
import time
from datetime import date, datetime, timedelta
from typing import Optional
from urllib.parse import parse_qs, urlparse
from zoneinfo import ZoneInfo

import httpx
from bs4 import BeautifulSoup, Tag

from pipeline.models import EventRaw

log = logging.getLogger(__name__)

SOURCE_NAME = "ladecadanse"
BASE_URL = "https://www.ladecadanse.ch"
USER_AGENT = "MyGeneva/0.1 (aggregateur genevois; contact: mygeneva@gmail.com)"
CRAWL_DELAY_S = 15
GENRE_WHITELIST = {"fetes"}                # only <h2 id="fetes"> for MVP
LOCAL_TZ = ZoneInfo("Europe/Zurich")

_last_fetch_at: Optional[datetime] = None


def _throttle() -> None:
    """Sleep so we respect Crawl-delay between consecutive GETs."""
    global _last_fetch_at
    now = datetime.now()
    if _last_fetch_at is not None:
        elapsed = (now - _last_fetch_at).total_seconds()
        wait = CRAWL_DELAY_S - elapsed
        if wait > 0:
            time.sleep(wait)
    _last_fetch_at = datetime.now()


def _url_for(target: date) -> str:
    return f"{BASE_URL}/index.php?courant={target.isoformat()}"


def _fetch_html(target: date, *, client: Optional[httpx.Client] = None) -> tuple[str, int]:
    _throttle()
    url = _url_for(target)
    owned_client = client is None
    if owned_client:
        client = httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=30.0)
    try:
        resp = client.get(url)
        return resp.text, resp.status_code
    finally:
        if owned_client:
            client.close()


_GCAL_DATES_RE = re.compile(r"dates=(\d{8}T\d{6})(?:%2F|/)(\d{8}T\d{6})")


def _parse_gcal_dates(article: Tag) -> Optional[tuple[datetime, datetime]]:
    """Extract start/end datetimes from the Google Calendar export link.

    The link carries `dates=YYYYMMDDTHHMMSS/YYYYMMDDTHHMMSS` in the site's
    local time (Europe/Zurich) with no explicit tz. We convert to UTC.
    """
    for a in article.select("a[href*='calendar.google.com']"):
        m = _GCAL_DATES_RE.search(a.get("href", ""))
        if not m:
            continue
        try:
            start_naive = datetime.strptime(m.group(1), "%Y%m%dT%H%M%S")
            end_naive = datetime.strptime(m.group(2), "%Y%m%dT%H%M%S")
        except ValueError:
            continue
        start = start_naive.replace(tzinfo=LOCAL_TZ).astimezone(ZoneInfo("UTC"))
        end = end_naive.replace(tzinfo=LOCAL_TZ).astimezone(ZoneInfo("UTC"))
        return start, end
    return None


def _text(tag: Optional[Tag]) -> str:
    return tag.get_text(" ", strip=True) if tag else ""


def _parse_article(article: Tag, *, genre: str, fallback_date: date) -> Optional[EventRaw]:
    """Convert a single <article class="evenement-short"> block into EventRaw."""
    article_id = article.get("id", "")
    m = re.match(r"event-(\d+)", article_id)
    if not m:
        return None
    external_id = m.group(1)

    title_link = article.select_one("header.titre h3 a")
    if not title_link:
        return None
    title = title_link.get_text(strip=True)
    if not title:
        return None
    source_url = BASE_URL + title_link.get("href", "")

    venue_link = article.select_one("header.titre span.right a")
    venue_name = _text(venue_link)

    address = _text(article.select_one("div.pratique span.left"))
    description = _text(article.select_one("div.event-media div.description p"))

    img = article.select_one("div.event-media figure img")
    image_url = ""
    if img and img.get("src"):
        src = img["src"]
        image_url = src if src.startswith("http") else BASE_URL + src

    times = _parse_gcal_dates(article)
    if times is not None:
        date_start, date_end = times
    else:
        # Fallback: use fallback_date at 20:00 local — better than dropping the event.
        local_start = datetime.combine(fallback_date, datetime.min.time()).replace(
            hour=20, tzinfo=LOCAL_TZ
        )
        date_start = local_start.astimezone(ZoneInfo("UTC"))
        date_end = None

    return EventRaw(
        source_name=SOURCE_NAME,
        external_id=external_id,
        title=title,
        date_start=date_start,
        date_end=date_end,
        genre=genre,
        venue_name=venue_name,
        address=address,
        description=description,
        source_url=source_url,
        image_url=image_url,
    )


def parse_html(html: str, *, fallback_date: date) -> list[EventRaw]:
    """Parse a rendered ladecadanse day page. Returns only whitelisted genres."""
    soup = BeautifulSoup(html, "lxml")
    events: list[EventRaw] = []
    for section in soup.select("section.genre"):
        heading = section.select_one("h2[id]")
        if heading is None:
            continue
        genre = heading.get("id", "").strip().lower()
        if genre not in GENRE_WHITELIST:
            continue
        for article in section.select("article.evenement-short"):
            raw = _parse_article(article, genre=genre, fallback_date=fallback_date)
            if raw is not None:
                events.append(raw)
    return events


def fetch(target: date) -> list[EventRaw]:
    """Fetch and parse one day. Respects Crawl-delay."""
    html, status = _fetch_html(target)
    if status != 200:
        log.warning("ladecadanse GET %s → HTTP %s", target, status)
        return []
    return parse_html(html, fallback_date=target)
