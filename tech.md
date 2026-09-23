# Tech.md — Choix techniques du projet

## 1. Mobile

- **Framework** : React Native
  - Choisi plutôt qu'Ionic (WebView, moins performant, moins "natif") ou NativeScript (écosystème trop confidentiel pour un solo dev)
  - Un seul codebase JS/TS pour iOS et Android
- **Surcouche** : Expo
  - Permet de développer et builder sans jamais toucher à Xcode ou Android Studio
  - Build cloud via **EAS Build** : pas besoin de posséder un Mac pour compiler/publier sur iOS
  - Déploiement vers les stores automatisable via **EAS Submit**
- **Comptes nécessaires** (indépendants de la techno, imposés par les stores) :
  - Apple Developer Program (~99$/an)
  - Google Play Console (~25$ paiement unique)

## 2. Web (vitrine)

- **Statut** : mis de côté pour l'instant, à traiter après le MVP mobile
- **Rôle prévu** : vitrine légère uniquement (présentation + lien vers les stores, éventuellement pages événements pour le SEO) — ne doit pas couvrir les fonctionnalités du mobile
- **Pistes à évaluer plus tard** : Next.js (proche de React, bon pour le SEO) vs solution SaaS no-code (Webflow, Framer, Carrd) si le besoin reste purement statique
- **Techniquement séparé** du mobile, mais consommera la même API backend si des pages dynamiques (événements) sont nécessaires

## 3. Backend

- **Langage** : Python
  - Choisi pour la cohérence avec le pipeline d'agrégation (scraping, traitement de données, IA/LLM), écosystème Python dominant sur ces sujets
  - Un seul langage pour l'API et le pipeline d'agrégation
- **Framework API** : FastAPI (moderne, typé, documentation auto-générée)

## 4. Base de données

- **SGBD** : PostgreSQL
- **Extension** : PostGIS (gestion native de la géolocalisation — recherche par rayon, distances)
- **ORM / modèles** : SQLModel (créé par l'auteur de FastAPI, bonne intégration, plus simple que SQLAlchemy pur)
- **Migrations de schéma** : Alembic (versionnement du schéma dans Git, application cohérente en local et en production)

## 5. Environnement de développement local

- **Docker Compose** : utilisé uniquement pour lancer un conteneur PostgreSQL local (+ PostGIS), reproductible en une commande
- Le backend Python tourne directement sur la machine de dev (pas obligatoirement conteneurisé en local)
- Pas d'orchestration de conteneurs en production prévue à ce stade (pas de Kubernetes etc.) — une base de données managée (type Railway/Render/Supabase) est envisagée pour la prod

## 6. Structure du repo (monorepo)

```
/mobile      → App React Native (Expo)
/backend     → API FastAPI + modèles SQLModel + migrations Alembic
/pipeline    → Scripts Python d'agrégation (scraping, IA, nettoyage), écrit dans la même base Postgres
.github/workflows/ → Pipelines CI/CD (GitHub Actions)
```

## 7. CI/CD

- **Outil** : GitHub Actions (choisi plutôt que Jenkins — pas d'infra à gérer soi-même, bien intégré à GitHub et à Expo/EAS)
- **Automatisations prévues** (à détailler plus tard) :
  - Backend : tests + build + déploiement automatique sur push
  - Mobile : déclenchement de build EAS (et soumission aux stores) sur nouvelle version taguée

## 8. Schéma de données (MVP)

Pas d'authentification au MVP → pas de table `users`. Favoris gérés via un `user_id` hardcodé (POC solo), pour éviter un refactoring quand l'authentification sera ajoutée plus tard.

**`events`** (catégories journée / soirée)
- `id`, `title`, `description`
- `category` (enum : `journee` / `soiree`)
- `location_name`, `latitude`, `longitude`, `address`
- `date_start`, `date_end`
- `image_url`
- `source`, `source_url`, `is_verified`
- `created_at`, `updated_at`

**`restaurants`**
- `id`, `title`, `description`
- `location_name`, `latitude`, `longitude`, `address`
- `opening_hours`
- `rating` (note Google), `rating_count` (nombre d'avis Google — sert à pondérer la fiabilité de la note)
- `image_url`
- `source`, `source_url`, `is_verified`
- `created_at`, `updated_at`

**`favorites`**
- `id`
- `user_id` (valeur fixe hardcodée pour le POC)
- `item_type` (enum : `event` / `restaurant`)
- `item_id` (référence vers `events.id` ou `restaurants.id` selon `item_type`)
- `created_at`

**`sources`** (monitoring du pipeline d'agrégation)
- `id`, `name`, `type` (scraping / API / manuel)
- `last_success_at`, `status`

> Note future : l'API Google Places (utilisée pour `rating`/`rating_count`) est payante au-delà d'un certain volume d'appels — négligeable au stade POC, à surveiller si le nombre de restaurants suivis augmente fortement.

## 9. Pipeline d'agrégation

- **Orchestrateur** : Apache Airflow (plutôt que Prefect ou des scripts + cron)
  - Choisi malgré une charge d'infra un peu plus lourde, car déjà maîtrisé par le fondateur (usage professionnel) → pas de courbe d'apprentissage, bénéfice de montée en compétence personnelle
  - Exécution locale via Docker Compose (cohérent avec le Docker Compose déjà prévu pour Postgres)
- **Monitoring** : géré nativement par l'UI Airflow (statut des runs, historique, retries) — complété par la table `sources` côté application pour le suivi métier des sources de données

## 10. Endpoints API (MVP)

**Events**
- `GET /events` — liste, filtrable par `category` et `date`
- `GET /events/{id}` — détail

**Restaurants**
- `GET /restaurants` — liste, triée par `rating`/`rating_count` + localisation
- `GET /restaurants/{id}` — détail

**Favoris**
- `GET /favorites`
- `POST /favorites`
- `DELETE /favorites/{id}`

**Notifications push** (mécanisme backend, pas un endpoint consulté par l'app)
- 2 notifications/jour : 8h (événements du jour), 18h (événements du soir)
- Détail technique (Expo Notifications / Firebase) à définir

**Notés pour plus tard, non implémentés au MVP**
- Filtre géolocalisé "autour de moi"
- Recherche texte (le scroll de découverte est privilégié pour l'instant)

## 11. Points restant à définir (prochaines étapes techniques)

- Détail précis des workflows GitHub Actions (étapes exactes CI/CD)
- Choix technique définitif pour le site vitrine (Next.js vs no-code)
- Hébergement de production (ex: Railway, Render, Fly.io — à confirmer)
- Mécanisme technique des notifications push (Expo Notifications vs Firebase)
