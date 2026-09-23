# PROGRESS — MyGeneva (session overnight)

Session démarrée : 2026-09-23.
Objectif : V1 technique — backend FastAPI, docker compose (Postgres+PostGIS+Airflow), pipeline squelette Airflow, app mobile Expo, CI GitHub Actions.

## Décisions prises pendant la nuit

- **Runtime Python** : 3.13 (via `py -3.13`). Python 3.14 est installé sur la machine mais 3.13 offre une meilleure compatibilité avec l'écosystème SQLModel/psycopg au moment de la session.
- **DB en dev/tests** : SQLite pour les tests unitaires (rapide, sans dépendance), Postgres+PostGIS pour le run local via docker compose. Le backend lit `DATABASE_URL` — SQLite par défaut si absent.
- **PostGIS** : l'extension est présente dans docker-compose (image `postgis/postgis`), mais les modèles MVP n'utilisent pas encore de type géographique natif (lat/lon simples float). Prêt pour une évolution ultérieure.
- **Environnement de test** : aucune dépendance à Postgres pour la CI — on utilise SQLite, ce qui garde la CI rapide et fiable.
- **Node / Docker non disponibles localement** : la machine où tourne cette session n'a ni Node ni Docker. Les artefacts mobile (Expo) et docker-compose sont produits mais non "smoke-testés" en exécution — validés par lecture et cohérence. À valider par un humain au réveil sur une machine équipée.
- **`user_id` favoris** : hardcodé à la constante `POC_USER_ID = "poc-user"` côté backend (paramétrable via env var pour tests).

## Journal

_Suivi chronologique au fil des étapes._
