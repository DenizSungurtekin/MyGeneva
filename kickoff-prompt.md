# Prompt de lancement — Claude Code (session overnight non supervisée)

## Instructions d'utilisation
1. Place ce fichier ainsi que `socle.md`, `tech.md`, `screens.md` et `design-reference.md` à la racine d'un dossier vide.
2. `git init` dans ce dossier avant de lancer Claude Code.
3. Lance Claude Code avec exécution automatique des commandes/éditions activée (mode non-interactif), pour qu'aucune confirmation ne bloque le run pendant la nuit.
4. Colle le prompt ci-dessous.

---

## PROMPT

Tu vas construire, de façon autonome et sans interruption cette nuit, la V1 technique d'un projet appelé **"MyGeneva"**. Le contexte métier et technique complet est dans `socle.md`, `tech.md`, `screens.md` et `design-reference.md` — lis-les intégralement avant de commencer.

**Important** : `design-reference.md` documente un prototype cliquable déjà construit et validé (charte visuelle exacte, logique de navigation entre écrans, données d'exemple). L'app mobile de cette session doit reproduire fidèlement ce comportement et ce style — ce ne sont pas des suggestions parmi d'autres, mais ce qui a déjà été approuvé et qui ne doit pas être réinventé.

### Règles de fonctionnement pour ce run autonome
- Tu travailles seul, sans supervision humaine cette nuit. Ne pose aucune question : si un point est ambigu, prends la décision la plus raisonnable, note-la dans `PROGRESS.md`, et continue.
- **Committe après chaque étape fonctionnelle** (message clair, en français ou anglais au choix, peu importe). Ne laisse jamais l'état du repo cassé entre deux commits.
- Tiens à jour un fichier `PROGRESS.md` à la racine : ce que tu as fait, les décisions prises, ce qui reste à faire, et tout problème rencontré.
- Priorise la robustesse et le fait que chaque étape soit testée avant de passer à la suivante, plutôt que la vitesse.
- Si tu bloques totalement sur un point après plusieurs tentatives, documente le blocage dans `PROGRESS.md`, committe l'état actuel, et passe à la tâche suivante plutôt que de rester bloqué toute la nuit dessus.

### Périmètre de cette session (dans cet ordre de priorité)

**1. Backend (FastAPI + PostgreSQL/PostGIS)**
- Structure `/backend` : FastAPI, SQLModel, Alembic
- Modèles : `events`, `restaurants`, `favorites` (voir schéma dans `tech.md`)
- Migrations Alembic fonctionnelles
- Script de seed avec des données de test réalistes pour Genève (reprends les exemples utilisés dans `screens.md`/les maquettes : Marché du Molard, Jazz au Sud des Alpes, Café des Bains, etc.)
- Endpoints définis dans `tech.md` (`GET/POST/DELETE /events`, `/restaurants`, `/favorites`)
- Tests automatisés (pytest) couvrant chaque endpoint, doivent passer avant de committer cette étape
- `.env.example` avec toutes les variables nécessaires, `.env` dans `.gitignore`

**2. Environnement local (Docker Compose)**
- `docker-compose.yml` à la racine : service Postgres+PostGIS, service Airflow (webserver+scheduler minimal)
- Doit démarrer avec une seule commande (`docker compose up`)

**3. Pipeline d'agrégation (squelette Airflow)**
- Structure `/pipeline`
- Un DAG d'exemple illustrant le pattern fetch → clean → load, sur une source factice (pas de vrai scraping Genève à ce stade, les sources réelles ne sont pas encore validées légalement)
- Écriture dans la table `sources` (monitoring) à chaque run du DAG

**4. App mobile (Expo / React Native)**
- Structure `/mobile`, projet Expo
- Les 4 écrans définis dans `screens.md` (Accueil avec navigation par jour + catégories, Liste, Détail, Favoris), fidèles au comportement du prototype déjà validé (bascule de catégorie dynamique, favoris fonctionnels, navigation complète)
- Favoris gérés via un `user_id` hardcodé côté backend (pas d'authentification à ce stade)
- Connexion à l'API locale (`http://localhost:8000` ou équivalent), pas de données mockées en dur dans l'app une fois le backend prêt
- Style cohérent avec les maquettes (typographie, couleurs) sans nécessité de pixel-perfect

**5. CI (GitHub Actions)**
- Un workflow simple : lance les tests backend à chaque push

### Explicitement hors périmètre cette nuit (ne pas essayer)
- Vraies sources de données Genève / scraping réel — la question légale n'est pas tranchée
- Publication sur les stores Apple/Google — nécessite des comptes créés manuellement
- Site vitrine web
- Authentification utilisateur
- Hébergement de production

### À la fin de la session
Termine `PROGRESS.md` par un résumé clair : ce qui fonctionne et est testé, ce qui reste à faire, et les 2-3 prochaines actions les plus importantes à faire avec un humain (moi) au réveil.
