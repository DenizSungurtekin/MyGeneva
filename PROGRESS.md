# PROGRESS — MyGeneva (session overnight)

Session : 2026-09-23 → 2026-09-24 (nuit).
Objectif : V1 technique du projet MyGeneva (backend, docker, pipeline squelette, mobile, CI).

## Résumé exécutif

Tout ce qui était demandé dans le kickoff est en place. **Backend testé et vert (26 tests pytest)**. Docker Compose, pipeline Airflow et app mobile Expo sont écrits et cohérents, mais **non exécutés localement** parce que Node et Docker ne sont pas installés sur la machine où cette session a tourné. À valider par un humain au réveil sur une machine équipée.

## Ce qui fonctionne et est testé

### Backend (`backend/`) — testé de bout en bout
- FastAPI 0.14x + SQLModel 0.0.47 + Alembic 1.20, Python 3.13.
- Modèles : `events` (catégorie journée/soirée), `restaurants`, `favorites` (POC user_id), `sources` (monitoring).
- Migrations Alembic générées et appliquées avec succès (upgrade + downgrade cyclables) : `alembic/versions/051b966c7e58_initial_schema_*.py`.
- Endpoints implémentés :
  - `GET /events` (filtres `category`, `date` YYYY-MM-DD, tri chronologique, overlap multi-jours géré)
  - `GET /events/{id}`, `POST /events`, `PATCH /events/{id}`, `DELETE /events/{id}`
  - `GET /restaurants` (tri rating desc puis rating_count, filtre `min_rating`, `limit`)
  - `GET /restaurants/{id}`, `POST /restaurants`, `PATCH /restaurants/{id}`, `DELETE /restaurants/{id}`
  - `GET /favorites`, `POST /favorites` (déduplique via `user_id + item_type + item_id`), `DELETE /favorites/{id}`
  - `GET /health`
- CORS configurable via `CORS_ORIGINS` (env), defaults pour Expo (localhost:8081/19006, exp://).
- Seed script `app/seed.py` idempotent : peuple 7 events (Molard, Jazz Sud des Alpes, Balade lac, Jardin Anglais, Parc La Grange, Usine, Gravière) sur 7 jours autour d'aujourd'hui + 3 restaurants (Café des Bains, Buvette des Bains, Chez Ma Cousine) + 3 sources. Flag `--reset`.
- **Tests pytest : 26/26 verts** (`backend/tests/`). Couvre chaque endpoint + le seed idempotent + le tri restaurants + le filtre date + les 404. Chaque test tourne dans une SQLite en mémoire dédiée (fixture).
- `.env.example` fourni ; `.env` déjà dans `.gitignore`.

### Docker Compose (`docker-compose.yml`) — écrit, non exécuté
- Service `postgres` : image `postgis/postgis:16-3.4`, port 5432, healthcheck `pg_isready`.
- Script d'init `scripts/db-init/01-create-airflow-db.sql` : crée la DB `airflow` et active l'extension PostGIS sur `mygeneva`.
- Services Airflow (image `apache/airflow:2.10.3-python3.11`) : `airflow-init` (one-shot db migrate + user admin/admin), `airflow-webserver` (http://localhost:8080), `airflow-scheduler`. Executor Local.
- Volume nommé `mygeneva_postgres_data`.

### Pipeline Airflow (`pipeline/`) — écrit, non exécuté
- DAG démo `demo_fetch_clean_load` illustrant le pattern `fetch → clean → load` sur une source factice (aucun scraping réel — cf. socle §7).
- `pipeline/scripts/source_status.py` : helpers pour marquer succès/échec dans la table `sources` via psycopg (décorrélé du backend, aucune dépendance croisée).
- DAG programmé `@daily`, catchup off, `max_active_runs=1`, timeout 10 min, callback failure pour statuer la source.

### Mobile (`mobile/`) — écrit, non exécuté
- Expo SDK 51, React Native 0.74.5, TypeScript strict.
- 4 écrans (`src/screens/`) fidèles au prototype :
  - **Accueil** : `DayPicker` horizontal + `CategoryTabs` (journée/soirée/restaurant) + preview 3 items + bouton "Voir tout".
  - **Liste** : mêmes tabs qu'à l'accueil (état partagé), scroll complet, cœur favori sur chaque carte (nested Pressable, le touch n'atteint pas la carte).
  - **Détail** : placeholder image + retour + heart overlay, tag catégorie, description, adresse, carte placeholder, footer avec "Itinéraire" (non fonctionnel) + toggle favori dynamique. Retour renvoie vers l'écran d'origine.
  - **Favoris** : mélange events + restaurants, empty state, cœur pour retirer.
- État partagé via `React.Context` (`src/state/AppContext.tsx`) — pas de React Navigation à ce stade, un `screen: ScreenName` détermine l'écran affiché (mimique la mécanique du prototype). Suffisant pour 4 écrans, refactorable plus tard.
- Client API `fetch` (`src/api/client.ts`) qui gère automatiquement le cas émulateur Android (`10.0.2.2`) et accepte `EXPO_PUBLIC_API_URL` pour un device physique.
- Thème centralisé (`src/theme/`) : couleurs, spacings, typographies Fraunces (600) + Work Sans (400/500/600) via `@expo-google-fonts/*`.
- Icônes `@expo/vector-icons` (Feather, thin-stroke) — pas d'emoji.
- `README.md` mobile explique l'installation, le pointage API par plateforme.

### CI (`.github/workflows/backend-tests.yml`) — écrit
- Trigger : push / PR touchant `backend/**` + workflow_dispatch.
- Python 3.13, cache pip, install requirements, upgrade+downgrade Alembic (pour catch downgrade bugs), puis `pytest -ra`.

## Décisions prises pendant la nuit

- **Python 3.13** plutôt que 3.14 (installé aussi) pour la compat écosystème.
- **SQLite pour les tests**, Postgres+PostGIS pour docker-compose. Le backend lit `DATABASE_URL` — SQLite par défaut si absent.
- **PostGIS installé** dans docker-compose et l'extension activée dans le script d'init, mais les modèles MVP utilisent `latitude/longitude: float` (pas encore de type `geography` natif) — ready pour évolution.
- **`user_id` favoris** : constante `POC_USER_ID = "poc-user"` (env-overridable), pas de table `users`.
- **CORS** ouvert par défaut aux origines Expo standard (`localhost:8081`, `localhost:19006`, `exp://`) ; ajustable via env.
- **Pas de React Navigation** : un contexte `screen: ScreenName` suffit pour 4 écrans et évite une dépendance lourde qui rendait le prototype cliquable trivial à reproduire. À refactorer si le nombre d'écrans grimpe.
- **Filtre `date` sur `/events`** : gère l'overlap multi-jours (un événement Ven→Sam apparaît le samedi si demandé), pas uniquement les events démarrant ce jour-là — comportement plus proche de ce qu'attend un utilisateur.
- **Alembic `render_as_batch` conditionnel** : activé pour SQLite (nécessaire pour ALTER TABLE), désactivé pour Postgres.
- **Seed idempotent** : reruns sans dupliquer les rows, upserts sur `title + date_start` pour les events, `title` pour les restaurants/sources.

## Ce qui n'est PAS testé (à valider par un humain équipé)

Motif : la machine où cette session a tourné n'a ni Node ni Docker. La logique et les fichiers sont là, mais je ne peux pas prouver qu'ils s'exécutent.

1. **`docker compose up`** — je n'ai jamais démarré la stack, jamais vu Postgres/PostGIS ni Airflow tourner. Point de vigilance : la syntaxe `depends_on: service_completed_successfully` est bien supportée par Docker Compose v2 récent — vérifier la version côté machine du dev.
2. **DAG Airflow** — jamais rejoué. Le fichier compile côté Python 3.13 (`py_compile` OK), mais la vraie validation se fera dans l'UI Airflow au premier `Trigger`.
3. **App mobile** — jamais lancée. `npm install` puis `npm run start` sont les prochaines commandes à essayer. Attention : les versions `@expo-google-fonts/*` sont épinglées à `^0.2.3` — si l'install échoue, `npm install @expo-google-fonts/fraunces@latest @expo-google-fonts/work-sans@latest` devrait débloquer.
4. **`npm run typecheck`** — pas exécuté. Le code est écrit en TypeScript strict, il peut y avoir 1-2 petits ajustements de types à faire au premier run (probablement autour de `globalThis.process` dans `src/api/client.ts` sur certains setups).

## Prochaines actions au réveil (ordre de priorité)

### 1. Smoke-test le backend en local (2 minutes)
```powershell
cd backend
py -3.13 -m venv .venv           # déjà fait pendant la nuit, sauté si présent
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```
Puis ouvrir http://localhost:8000/docs et jouer 1-2 endpoints. Doit renvoyer les 7 events du jour + les 3 restaurants.

### 2. Démarrer l'app mobile (5–10 minutes)
```powershell
cd mobile
npm install
npm run typecheck                 # confirmer 0 erreur (ou corriger)
npm run start
```
Scanner le QR avec Expo Go depuis le téléphone. **Si le téléphone est sur le même Wi-Fi que le PC**, définir `EXPO_PUBLIC_API_URL` sur l'IP LAN pour que l'app tape le backend :
```powershell
$env:EXPO_PUBLIC_API_URL = "http://192.168.x.x:8000"
npm run start
```
Contrôler la navigation Accueil → Liste → Détail → Favoris et le toggle favori.

### 3. Démarrer la stack Docker (10 minutes, dépend de la présence de Docker Desktop)
```powershell
docker compose up
```
- Vérifier http://localhost:8080 (admin/admin) → activer et trigger `demo_fetch_clean_load` → observer un run vert → SELECT * FROM sources dans Postgres pour confirmer que `last_success_at` a été mis à jour.
- Si tout est OK, ré-orienter le backend vers Postgres :
  ```
  # backend/.env
  DATABASE_URL=postgresql+psycopg://mygeneva:mygeneva@localhost:5432/mygeneva
  ```
  puis `alembic upgrade head` + `python -m app.seed` pour repeupler la DB Postgres.

### Décisions à prendre ensuite (hors périmètre de cette nuit)
- Sources Genève réelles (question légale) → gèle actuellement toute la couche scraping.
- Comptes stores Apple/Google (paiement) → prérequis à un build EAS Submit.
- Hébergement backend (Railway / Render / Fly.io) — Postgres managé et déploiement continu.

## Ajout — 2026-09-26 : deuxième thème "Nuit Douce" + bouton toggle

Refactor de l'app mobile pour supporter deux thèmes visuels côte à côte, avec un bouton de bascule dans le header de l'écran Accueil (icône lune/soleil).

### Ce qui change
- **Deux thèmes** exposés : `lightTheme` (thème d'origine, ivoire + terracotta, Fraunces + Work Sans) et `darkTheme` (Nuit Douce, palette #17181C / accents chauds, Epilogue + Hanken Grotesk).
- **Défaut au démarrage** : `light` (thème d'origine). Le choix **n'est pas persisté** entre lancements (AsyncStorage volontairement pas introduit, restart = light).
- **Bouton toggle** : icône Feather `moon`/`sun` en haut à droite de l'écran d'accueil.
- **Nouvelles polices** : `@expo-google-fonts/epilogue` et `@expo-google-fonts/hanken-grotesk` ajoutées et installées (`npm install` a réussi). Fraunces + Work Sans sont conservées pour le thème light. Les 4 familles sont chargées au démarrage.
- **Architecture** : `src/theme/themes.ts` + `src/theme/ThemeContext.tsx` (`ThemeProvider` + `useTheme()`). Chaque composant a été refactor pour créer ses `StyleSheet` via `useMemo(() => StyleSheet.create({...}), [theme])` — les styles étaient auparavant figés au chargement du module. `src/theme/typography.ts` supprimé (fusionné dans `themes.ts`).
- **StatusBar** : `style` dynamique (`dark` en light, `light` en dark).
- **Corrections d'appearance** : la couleur du cœur favori et l'accent principal sont maintenant deux tokens distincts (`favoriteHeart` vs `accentJournee`) ; les pastilles actives de CategoryTabs et DayPicker utilisent l'inversion texte↔fond au lieu de l'accent (conforme à la spec du prototype).

### Fichiers touchés
- `mobile/package.json` (ajout deps + `npm install`)
- `mobile/App.tsx` (chargement 4 familles de polices, wrap `ThemeProvider`)
- `mobile/src/theme/` : `themes.ts` (nouveau), `ThemeContext.tsx` (nouveau), `colors.ts` (réduit à `CategoryKey` + `categoryLabel`), `typography.ts` (supprimé), `index.ts` (mis à jour)
- `mobile/src/components/` : `CategoryTabs.tsx`, `DayPicker.tsx`, `EventCard.tsx`, `FavoriteHeart.tsx`, `NavBar.tsx`, `Placeholder.tsx`, `RestaurantCard.tsx`, `SectionHeader.tsx`, `Tag.tsx`
- `mobile/src/screens/` : `HomeScreen.tsx` (+ toggle button), `ListScreen.tsx`, `DetailScreen.tsx`, `FavoritesScreen.tsx`

### Ce qui **ne** change **pas**
- `app.json` — le splash reste `#FAF6F0` puisque le démarrage utilise le thème light par défaut.
- Les composants, la navigation, l'API, `AppContext`, les seeds : intacts.

### Validation
- `npm install` OK (2 packages ajoutés).
- `tsc --noEmit --moduleResolution bundler --ignoreDeprecations 6.0` : les seules erreurs restantes sont préexistantes (`expo-constants` non résolu dans `src/api/client.ts`, confirmé sur `HEAD` avant les changements). Aucune erreur induite par le refactor de thème.
- **Non testé sur device/simulateur** : je n'ai pas lancé Expo Go ni un simulateur pour valider visuellement le rendu ni le comportement du toggle. Le rendu final (contraste, lisibilité des polices Epilogue/Hanken Grotesk, position exacte du bouton dans le header) est à vérifier au premier `expo start`.

## Journal chronologique

- **Init** : lecture des 4 fichiers de contexte, création `.gitignore`, `PROGRESS.md`, structure de repo, commit initial.
- **Backend** : models → schemas → routers → main → alembic init → migration autogenerée → 26 tests écrits et verts → commit.
- **Infra** : docker-compose (postgres+postgis+airflow init/web/scheduler) + init SQL pour DB airflow + PostGIS extension.
- **Pipeline** : DAG démo `demo_fetch_clean_load` + helpers `source_status.py` psycopg direct → commit.
- **Mobile** : package.json + theme + api client + state context + composants (DayPicker, CategoryTabs, EventCard, RestaurantCard, FavoriteHeart, Placeholder, Tag, NavBar) + 4 écrans + App entry avec Google Fonts → commit.
- **CI** : workflow GitHub Actions pour pytest → commit.
- Fin de session : re-run pytest → 26/26 verts. Aucune modification pending, arbre propre.
