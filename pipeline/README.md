# Pipeline

DAGs Airflow d'agrégation pour MyGeneva.

Ce dossier est monté dans les containers Airflow via `docker-compose.yml` :

- `dags/`     : DAGs Python
- `scripts/`  : utilitaires réutilisés par les DAGs
- `logs/`     : logs runtime (gitignoré)
- `plugins/`  : plugins Airflow (vide au démarrage)

## DAGs présents

- `demo_fetch_clean_load` — DAG d'illustration `fetch → clean → load` sur une source factice. Écrit dans `sources.last_success_at` à chaque succès. **Aucun scraping réel** : les sources Genève ne sont pas encore validées légalement.

## Lancer

```
docker compose up airflow-webserver
# UI : http://localhost:8080  (admin / admin)
```

Depuis l'UI, activer le DAG `demo_fetch_clean_load` puis "Trigger". Le run doit passer en vert et incrémenter `sources.last_success_at` pour `demo-fake-source` dans la table `sources`.

## Ajouter une nouvelle source

1. Créer un nouveau DAG dans `dags/` (copier `demo_fetch_clean_load.py` comme squelette).
2. Enregistrer la source dans la table `sources` (via le seed backend ou une migration Alembic).
3. Utiliser `scripts/source_status.py` pour mettre à jour `last_success_at`/`status` en fin de run.
