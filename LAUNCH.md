# LAUNCH — Comment démarrer la stack MyGeneva en local

Runbook pour un dev qui reprend la machine et veut tout allumer.

## Qu'est-ce qui tourne où

La stack est **hybride** : deux services tournent dans Docker, deux tournent en natif sur le PC.

| Service | Où | Comment on le démarre |
|---|---|---|
| Postgres (données + métadonnées Airflow) | **Docker** | `docker compose up -d postgres` |
| Airflow (init + webserver + scheduler) | **Docker** | `docker compose up -d airflow-init airflow-webserver airflow-scheduler` |
| Backend FastAPI | **Natif Windows** | `uvicorn` depuis `backend\.venv` |
| App mobile — Expo (Metro pour Expo Go, dev server web pour navigateur) | **Natif Windows** | `npx expo start …` |

Traduction : `docker compose up -d` te démarre uniquement Postgres + Airflow. Le backend et Expo, tu les lances chacun dans **un terminal PowerShell dédié sur ta machine**. Ils ne sont pas dans Docker.

## Vue d'ensemble des ports

| Service | Port | URL principale | Auth |
|---|---|---|---|
| Postgres | 5432 | `jdbc:postgresql://localhost:5432/mygeneva` | mygeneva / mygeneva |
| Backend FastAPI | 8000 | http://localhost:8000 | — |
| Backend — Swagger docs | 8000 | http://localhost:8000/docs | — |
| Backend — health | 8000 | http://localhost:8000/health | — |
| Airflow UI | 8080 | http://localhost:8080 | admin / admin |
| Expo Metro (Expo Go) | 8081 | `exp://<ip-lan>:8081` | — |
| Expo dev server web (navigateur) | 19006 | http://localhost:19006 | — |

## Prérequis (installés une fois)

- **Docker Desktop** — pour Postgres et Airflow.
- **Node.js** — pour Expo.
- **Python 3.13** avec le venv `backend/.venv` déjà créé (`pip install -r backend/requirements.txt` + `pip install -r pipeline/requirements.txt`).

**Trouver ton IP LAN** (utile pour Expo Go sur téléphone) :
```powershell
(Get-NetIPAddress -AddressFamily IPv4 |
  Where-Object { $_.InterfaceAlias -eq 'Wi-Fi' -and $_.IPAddress -notmatch '^169\.' }
).IPAddress
```
Exemple récent : `192.168.1.118`. Cette valeur revient plusieurs fois plus bas, **remplace-la par la tienne** à chaque bloc.

---

## 1. Postgres + Airflow (dans Docker)

Un seul terminal, une seule commande — les containers tournent en background :

```powershell
cd C:\Users\deniz\Desktop\Project\MyGeneva
docker compose up -d
```

Au **premier boot**, l'image Airflow installe `beautifulsoup4 lxml httpx` via `_PIP_ADDITIONAL_REQUIREMENTS` — compte 30–60s avant que le scheduler ne réponde. Suivre :
```powershell
docker compose logs -f airflow-scheduler
# Ctrl+C sort des logs sans arrêter le service
```

Vérifs :
```powershell
docker ps                                      # les 3 containers doivent tourner (airflow-init est "Exited" c'est normal)
docker exec mygeneva-postgres pg_isready -U mygeneva -d mygeneva
```

**Airflow UI** → http://localhost:8080 (admin / admin). Le DAG `scrape_sources` est déjà unpause.

**Trigger un scrape manuel** (aujourd'hui uniquement, `MYGENEVA_SCRAPE_DAYS=1` dans `docker-compose.yml`) :
```powershell
docker exec mygeneva-airflow-scheduler airflow dags trigger scrape_sources
```
Puis dans l'UI, cliquer sur le run pour voir les logs de la tâche `scrape_ladecadanse`.

Pour passer en fenêtre 7 jours en prod : éditer `MYGENEVA_SCRAPE_DAYS: "7"` dans `docker-compose.yml`, puis :
```powershell
docker compose up -d --force-recreate airflow-webserver airflow-scheduler
```
(Un simple `restart` ne relit pas les env, il faut `--force-recreate`.)

---

## 2. Backend FastAPI (en natif, un terminal dédié)

Nouveau terminal PowerShell. Laisser tourner en foreground pour voir les requêtes en direct :

```powershell
cd C:\Users\deniz\Desktop\Project\MyGeneva\backend
$env:DATABASE_URL = "postgresql+psycopg://mygeneva:mygeneva@localhost:5432/mygeneva"
.\.venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --reload
```

**⚠️ L'export `$env:DATABASE_URL` est obligatoire.** Sans lui, le backend retombe sur la SQLite locale `backend/mygeneva.db` (qui contient encore le seed factice « Marché du Molard », « Jazz Sud des Alpes », etc.). Toujours l'exporter dans le terminal **avant** de lancer `uvicorn`.

Vérifs :
- http://localhost:8000/health → `{"status":"ok"}`
- http://localhost:8000/docs → Swagger interactif
- http://localhost:8000/events → liste JSON des events scrapés

Pour arrêter : `Ctrl+C` dans son terminal.

---

## 3. Scraper CLI local (optionnel, hors Airflow)

Utile pour peupler la DB rapidement sans passer par l'UI Airflow, ou pour un backfill sur un range précis :

```powershell
cd C:\Users\deniz\Desktop\Project\MyGeneva
$env:MYGENEVA_DATABASE_URL = "postgresql+psycopg://mygeneva:mygeneva@localhost:5432/mygeneva"
.\backend\.venv\Scripts\python.exe -m pipeline.run_source ladecadanse --start 2026-09-26 --days 7
```

Output : `parsed=N inserted=X updated=Y empty_days=Z`. Idempotent — rerun sans dupliquer (upsert sur `(source, external_id)`).

---

## 4. App mobile — Expo (en natif, un ou deux terminaux dédiés)

**Deux serveurs indépendants** peuvent coexister (ports différents) :
- **Metro Bundler** (port 8081) → sert le bundle React Native pour Expo Go sur téléphone.
- **Dev server web** (port 19006) → sert un bundle React Native Web pour navigateur.

Tu peux lancer l'un, l'autre, ou les deux en parallèle.

### 4a. Accès via navigateur PC (le plus rapide)

Nouveau terminal :
```powershell
cd C:\Users\deniz\Desktop\Project\MyGeneva\mobile
$env:EXPO_PUBLIC_API_URL = "http://localhost:8000"
npx expo start --web --port 19006
```

Attend ~10–30s (Metro Bundler démarre), puis ouvre → **http://localhost:19006/**

### 4b. Accès via téléphone (Expo Go)

Sur le téléphone : installer **Expo Go** (Play Store / App Store), phone **sur le même Wi-Fi** que le PC.

Nouveau terminal sur le PC :
```powershell
cd C:\Users\deniz\Desktop\Project\MyGeneva\mobile
$env:EXPO_PUBLIC_API_URL = "http://192.168.1.118:8000"   # ton IP LAN
npx expo start --lan --port 8081
```

Un QR code apparaît dans le terminal. Trois façons de charger l'app :
1. **Android** — scanner le QR directement avec Expo Go.
2. **iOS** — scanner avec l'app Appareil Photo (elle propose d'ouvrir dans Expo Go).
3. **Fallback manuel** — Expo Go → "Enter URL manually" → tape `exp://192.168.1.118:8081`.

L'app se télécharge (~30s) puis démarre.

**Pré-requis firewall Windows** : les ports 8000 (backend) et 8081 (Metro) doivent être ouverts sur ton adaptateur Wi-Fi. Test depuis le téléphone : ouvrir `http://192.168.1.118:8000/health` dans le navigateur mobile → doit renvoyer `{"status":"ok"}`. Sinon, ajouter une règle inbound TCP 8000/8081.

### 4c. Les deux en parallèle (web + phone)

Deux terminaux PowerShell, un par serveur (chacun avec sa propre valeur d'`EXPO_PUBLIC_API_URL` — l'URL est bakké dans le bundle au démarrage) :

Terminal A :
```powershell
cd C:\Users\deniz\Desktop\Project\MyGeneva\mobile
$env:EXPO_PUBLIC_API_URL = "http://localhost:8000"
npx expo start --web --port 19006
```

Terminal B :
```powershell
cd C:\Users\deniz\Desktop\Project\MyGeneva\mobile
$env:EXPO_PUBLIC_API_URL = "http://192.168.1.118:8000"
npx expo start --lan --port 8081
```

⚠️ **Ne charge pas le bundle web depuis ton téléphone** (`http://192.168.1.118:19006`) : ce bundle a `localhost:8000` bakké → localhost = ton téléphone lui-même → échec. Utilise le port et le bundle prévus pour chaque device.

---

## 5. DataGrip (Postgres)

Nouveau data source → PostgreSQL :

| Champ | Valeur |
|---|---|
| Host | `localhost` |
| Port | `5432` |
| User | `mygeneva` |
| Password | `mygeneva` |
| Database | `mygeneva` |
| URL JDBC | `jdbc:postgresql://localhost:5432/mygeneva` |

Tables intéressantes : `events`, `sources`, `scrape_runs`. La même instance héberge aussi la DB `airflow` (métadonnées Airflow) — dans les propriétés du data source → onglet **Schemas**, cocher `airflow` en plus si tu veux la voir.

---

## Ordre de démarrage recommandé (from scratch)

```powershell
# --- Terminal 1 : Docker (Postgres + Airflow) ---
cd C:\Users\deniz\Desktop\Project\MyGeneva
docker compose up -d
# attendre 30–60s au premier boot (Airflow installe les deps)

# --- Terminal 2 : Backend FastAPI ---
cd C:\Users\deniz\Desktop\Project\MyGeneva\backend
$env:DATABASE_URL = "postgresql+psycopg://mygeneva:mygeneva@localhost:5432/mygeneva"
.\.venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --reload

# --- Terminal 3 : Expo web ---
cd C:\Users\deniz\Desktop\Project\MyGeneva\mobile
$env:EXPO_PUBLIC_API_URL = "http://localhost:8000"
npx expo start --web --port 19006

# --- Terminal 4 (optionnel) : Expo LAN pour Expo Go ---
cd C:\Users\deniz\Desktop\Project\MyGeneva\mobile
$env:EXPO_PUBLIC_API_URL = "http://192.168.1.118:8000"   # ton IP LAN
npx expo start --lan --port 8081
```

Au final tu ouvres :
- **App dans le navigateur** → http://localhost:19006/
- **API docs** → http://localhost:8000/docs
- **Airflow** → http://localhost:8080 (admin/admin)
- **Expo Go sur téléphone** → `exp://192.168.1.118:8081` (via QR ou saisie manuelle)

---

## Tout couper

```powershell
# Docker
cd C:\Users\deniz\Desktop\Project\MyGeneva
docker compose down             # arrête, garde le volume Postgres
docker compose down -v          # arrête ET détruit le volume (repart de zéro)

# Backend : Ctrl+C dans son terminal
# Expo web : Ctrl+C dans son terminal
# Expo LAN : Ctrl+C dans son terminal (deux fois si ça résiste)
```

---

## Troubleshooting rapide

| Symptôme | Cause probable | Fix |
|---|---|---|
| L'app mobile affiche des events "Molard, Jazz Sud des Alpes"… | Backend lit la SQLite locale, pas Postgres | Ctrl+C `uvicorn`, exporter `$env:DATABASE_URL`, relancer |
| Expo Go ne charge pas / timeout | Firewall Windows bloque 8000/8081 sur le Wi-Fi | Autoriser inbound TCP 8000 et 8081 sur l'adaptateur Wi-Fi (ou test rapide : désactiver le pare-feu privé temporairement) |
| http://localhost:19006 refuse la connexion | Le dev server web n'a pas été lancé (ou killed) | Relancer `npx expo start --web --port 19006` |
| Metro sur 8081 refuse la connexion | Le LAN Expo n'a pas été lancé (ou killed) | Relancer `npx expo start --lan --port 8081` |
| DAG Airflow reste "queued" indéfiniment | Le scheduler n'a pas fini d'installer les deps | `docker compose logs -f airflow-scheduler`, attendre "Serving" |
| `sqlalchemy.exc.NoSuchModuleError: postgresql.psycopg` dans les logs DAG | SQLAlchemy 1.4 d'Airflow ne connaît pas le dialecte psycopg3 | Utiliser `postgresql+psycopg2://` dans `docker-compose.yml` (déjà en place) |
| Le DAG a un import error | `sqlalchemy` ou `sqlmodel` ont été ajoutés à `_PIP_ADDITIONAL_REQUIREMENTS` | Retirer — Airflow embarque sa propre SQLAlchemy 1.4, ne pas la surcharger |
| Un env var dans `docker-compose.yml` n'est pas pris | `docker compose restart` ne relit pas le compose file | `docker compose up -d --force-recreate <service>` |
| L'IP LAN change (nouvel emplacement Wi-Fi) | DHCP a réassigné une adresse | Re-run le snippet PowerShell en tête de doc, mettre à jour `EXPO_PUBLIC_API_URL` |
