"""Declarative catalog of the sources we know how to ingest.

Each `Source` binds a scraper function to metadata (kind, category hint,
schedule, trust level). The DAG and the local CLI iterate over `SOURCES`.
To add a new source: write a scraper module under `pipeline.scrapers`,
then add a `Source(...)` entry here.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Callable, Literal

from pipeline.models import EventRaw
from pipeline.scrapers import ladecadanse, villagedusoir


ScraperFn = Callable[[date], list[EventRaw]]

Kind = Literal["event", "restaurant", "both"]
Method = Literal["html_scrape", "rss", "ical", "api", "manual"]
CategoryHint = Literal["journee", "soiree", "restaurant", "mixed"]
Freshness = Literal["realtime", "daily", "weekly"]
Trust = Literal["official", "community", "commercial"]


@dataclass(frozen=True)
class Source:
    name: str                  # stable, lowercase, kebab-case — the FK to sources.name
    scraper: ScraperFn         # fetch(date) → list[EventRaw]
    kind: Kind
    method: Method
    category_hint: CategoryHint
    freshness: Freshness
    trust: Trust
    schedule: str              # cron expression (used by Airflow)
    homepage: str              # public URL, shown to users for attribution
    crawl_delay_s: int = 1     # min seconds between requests (respect the site's Crawl-delay)
    notes: str = ""


SOURCES: list[Source] = [
    Source(
        name="ladecadanse",
        scraper=ladecadanse.fetch,
        kind="event",
        method="html_scrape",
        category_hint="soiree",
        freshness="daily",
        trust="community",
        schedule="0 6 * * *",
        homepage="https://www.ladecadanse.ch/",
        crawl_delay_s=15,
        notes=(
            "Genre 'Fêtes' uniquement. Fenêtre par défaut J → J+7. "
            "robots.txt bloque les crawlers IA nommément mais pas les aggrégateurs "
            "user-agent identifiés — voir PROGRESS.md pour l'analyse juridique."
        ),
    ),
    Source(
        name="villagedusoir",
        scraper=villagedusoir.fetch,
        kind="event",
        method="html_scrape",
        category_hint="soiree",
        freshness="daily",
        trust="community",
        schedule="0 6 * * *",
        homepage="https://www.villagedusoir.com/",
        crawl_delay_s=5,
        notes=(
            "Site sur Odoo, expose schema.org Event microdata. Un seul GET renvoie "
            "toute la liste des events upcoming — le scraper cache le résultat au "
            "niveau module pour éviter des HTTP calls répétés lors du loop per-day "
            "du runner. Pas de venue_name côté source (seulement Commune, Canton) → "
            "pas de matching place_id, dedup avec ladecadanse basé sur "
            "(title, local_date, venue_name normalisé)."
        ),
    ),
]


def by_name(name: str) -> Source:
    for s in SOURCES:
        if s.name == name:
            return s
    raise KeyError(f"Unknown source: {name!r}. Known: {[s.name for s in SOURCES]}")
