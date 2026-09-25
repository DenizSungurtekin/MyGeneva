# Pipeline

Ingestion des sources externes vers la DB MyGeneva.

## Structure

- `sources/registry.py` — catalogue déclaratif de toutes les sources connues (`SOURCES`).
- `scrapers/` — un module par source, chacun exposant `fetch(target: date) -> list[EventRaw]`.
- `models.py` — dataclass `EventRaw` (forme intermédiaire, avant mapping DB).
- `mapping.py` — conversion `EventRaw` → colonnes `events`. Contient la table `genre → category`.
- `runner.py` — orchestrateur (fenêtre de dates, dédoublonnage, logs `scrape_runs`, statut `sources`).
- `run_source.py` — CLI local (`python -m pipeline.run_source <source>`).
- `dags/scrape_sources.py` — DAG Airflow qui appelle `runner.run_source` pour chaque source du registry.
- `dags/demo_fetch_clean_load.py` — DAG d'illustration (préservé pour référence pédagogique).
- `scripts/source_status.py` — helpers psycopg pour la table `sources` (utilisés par le DAG démo).

## Sources actives

| Source | Kind | Category hint | Trust | Schedule | Notes |
|---|---|---|---|---|---|
| `ladecadanse` | event | soiree | community | `0 6 * * *` | Genre "Fêtes" uniquement, crawl-delay 15s |

## Installation locale

Depuis le venv du backend :

```powershell
cd backend
.venv\Scripts\Activate.ps1
pip install -r ..\pipeline\requirements.txt
```

## Lancer un scrape local

```powershell
# depuis la racine du repo
python -m pipeline.run_source ladecadanse --start 2026-09-26 --days 7
```

Sortie attendue : `parsed=N inserted=X updated=Y empty_days=Z`. Rerun immédiat → `inserted=0 updated=N` (idempotent).

Chaque run laisse une ligne par jour dans `scrape_runs` (source_name, target_date, parsed_count, inserted_count, updated_count, status, error) et met à jour `sources.last_success_at` / `records_last_run` / `status`.

## Ajouter une nouvelle source

1. Écrire `pipeline/scrapers/<name>.py` avec `fetch(target: date) -> list[EventRaw]`.
2. Ajouter une entrée `Source(...)` dans `pipeline/sources/registry.py`.
3. Optionnel : ajouter le mapping `genre → category` dans `pipeline/mapping.py` si le vocabulaire de la source diffère.
4. Écrire un test (`pipeline/tests/test_<name>.py`) avec une fixture HTML minimale.

Le DAG et le CLI la découvrent automatiquement via le registry.

## DAG Airflow

`dags/scrape_sources.py` boucle sur `SOURCES` et lance un `PythonOperator` par source. Programmé quotidien à 06:00 UTC. Prérequis image : `httpx`, `beautifulsoup4`, `lxml`, `sqlalchemy` (via `_PIP_ADDITIONAL_REQUIREMENTS` dans `docker-compose.yml`, à ajouter lorsque la stack Docker sera exercée).

## Éthique & droit

Voir `PROGRESS.md`. Résumé : User-Agent identifié `MyGeneva/0.1 (aggregateur genevois; contact: mygeneva@gmail.com)`, respect strict du `Crawl-delay`, attribution en app, retrait immédiat sur demande.
