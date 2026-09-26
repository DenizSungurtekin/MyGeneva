# DEPLOY — Production deployment pipeline

Roadmap from "runs on my machine" to "installable via App Store + Play Store".

## Where we are

- **Backend** : FastAPI, Postgres, deployable to Railway. Ready as of this commit (Procfile, runtime.txt, env normalization for Railway's DATABASE_URL).
- **Mobile** : Expo app, bundle IDs already set to `com.mygeneva.app`, uses `EXPO_PUBLIC_API_URL` at bundle time.
- **Pipeline** : local Docker for now, will migrate to Railway cron later.

## Total cost — first year

| Item | Amount | Notes |
|---|---|---|
| Apple Developer Program | 99 USD | Renews annually |
| Google Play Console | 25 USD | One-off, valid forever |
| Backend (Railway free tier) | 0 | Enough for a small user base |
| EAS Build (Expo cloud) | 0 | 30 free builds / month |
| Domain (optional) | ~10 EUR/year | Add later if you want mygeneva.ch instead of railway.app |

## Step-by-step

### 1. Backend on Railway (~1 h, gratuit)

**You do**:
1. Push the repo to GitHub (private is fine — Railway supports private repos).
2. Sign up at railway.app with your GitHub account.
3. New Project → Deploy from GitHub → choose the MyGeneva repo.
4. In Railway's UI, set the **Root Directory** to `backend`.
5. Add a plugin: **PostgreSQL**. Railway auto-injects `DATABASE_URL`.
6. Under Variables, add:
   - `MYGENEVA_GOOGLE_MAPS_KEY` (same key as `mobile/.env.local`)
   - `POC_USER_ID=poc-user`
   - `CORS_ORIGINS` (leave empty for wildcard, or add specific Expo dev origins if needed)
7. Deploy. First build takes ~4 min. Migrations run automatically (Procfile).
8. Note the public URL, e.g. `mygeneva.up.railway.app`.

**Verify**:
- `curl https://mygeneva.up.railway.app/health` → `{"status":"ok"}`
- `curl https://mygeneva.up.railway.app/version` → commit + env
- `curl https://mygeneva.up.railway.app/places | jq length` → should return the count of places you have in your Railway Postgres (probably 0 until you backfill — see below).

**Backfill data**:
Point the pipeline CLI at Railway's Postgres instead of local:
```powershell
$env:MYGENEVA_DATABASE_URL = "postgresql+psycopg://<user>:<pw>@<host>.railway.app:<port>/<db>"
$env:MYGENEVA_GOOGLE_MAPS_KEY = "AIzaSy..."
python -m pipeline.run_source ladecadanse --lookback 2 --days 7
python -m pipeline.run_source villagedusoir --lookback 2 --days 7
python -m pipeline.enrich_places
```

### 2. Store developer accounts (~30 min + validation delays)

Both are only doable by you.

**Google Play Console** (~2 h approval):
- play.google.com/console → 25 USD → verify identity → create an app "MyGeneva".
- Under App content, note the package name `com.mygeneva.app`.

**Apple Developer Program** (~24-48 h approval):
- developer.apple.com → 99 USD → verify identity (passport / photo ID). Apple manually reviews.
- Once approved, appstoreconnect.apple.com → create a new app "MyGeneva" with bundle id `com.mygeneva.app`.

Both accounts must be validated **before** the first store build. Start now.

### 3. Restrict the Google Maps API key (~10 min, do before first build)

Currently the key allows any HTTP referer. Once bundled into store builds, anyone can extract it. Add app restrictions in GCP → APIs & Services → Credentials:
- **Android apps**: package name `com.mygeneva.app`, SHA-1 fingerprint (EAS gives it to you after the first Android build). Add it after the first build.
- **iOS apps**: bundle id `com.mygeneva.app`.
- Keep **API restrictions** as they are (Maps Static + Places API only).

### 4. EAS build + submit (~2 h once accounts are ready)

**You do**:
1. `npm install -g eas-cli` on your machine.
2. `cd mobile && eas login` (Expo account, free — you may already have one).
3. `eas init` — links the project to your Expo account.
4. First build: `eas build --platform android --profile production` (~10 min in the cloud).
5. `eas submit --platform android --track internal` — pushes the AAB to Play Console under the Internal Testing track.
6. Once Apple validation is done, repeat for iOS: `eas build --platform ios --profile production` then `eas submit --platform ios` (uploads to TestFlight).
7. First TestFlight build goes through Apple beta review — ~24-48 h. Subsequent updates: ~2 h.

**I'll set up** (next step in this pipeline):
- `mobile/eas.json` with dev / preview / production profiles
- `mobile/.env.production` pointing at your Railway URL
- Adjust `mobile/app.json` for versioning
- Privacy policy template

### 5. Invite friends to test

**Android (Internal Testing)**:
- Play Console → your app → Internal testing → Testers → paste Gmail addresses.
- Copy the opt-in URL, send it to them. They tap it, opt in, and the app appears in their Play Store.
- Propagation: ~15 min.

**iOS (TestFlight)**:
- App Store Connect → your app → TestFlight → External Testers → create a group "amis" → add their Apple ID emails.
- Apple reviews the FIRST build (~24-48 h). After that, adding testers to existing builds is instant.
- Testers install the "TestFlight" app from the App Store, then get an invite email + a redeem code. Your app appears in TestFlight.

## Post-deployment hygiene

- Set a **Budget alert** on Google Cloud (Maps + Places): $5/month → email alert. You currently have this, keep it.
- Set a **Quota cap** on Places API + Maps Static in GCP → hard limit at 1000 calls/day per SKU. Impossible to overspend.
- Once Railway free tier runs out (500h/month = essentially 24/7 for 1 service), the paid tier is $5/month for a "Hobby" plan. Well within reason.
- Push new backend versions via `git push` — Railway auto-redeploys and runs migrations.
- Push new mobile versions via `eas build && eas submit` — new TestFlight/Internal build available in minutes.

## What still lives on your machine

- **The scraping pipeline** (`pipeline/run_source.py` + `pipeline/enrich_places.py`). Runs manually or via local Airflow. Writes to Railway Postgres over HTTPS.

Later phase: move the pipeline to Railway cron (a scheduled task in Railway that runs `python -m pipeline.run_source ...` every night). ~1 h of setup, removes the "your PC must be on for events to refresh" dependency.
