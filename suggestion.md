# Suggestions — pistes de développement à traiter plus tard

Idées et améliorations mises de côté volontairement, avec le contexte de la décision. À reprendre quand la session le permet.

---

## Attribution "Source: La Décadanse" dans l'app mobile

**Statut** : reporté (2026-09-26).
**Contexte** : le scraper `ladecadanse` peuple `events.source` et `events.source_url` pour chaque ligne. Cette info n'est pas encore affichée dans l'écran détail de l'app mobile — l'utilisateur ne voit pas d'où vient l'événement ni comment retomber sur la fiche originale.
**Pourquoi c'est important** : c'est le pilier de la défense éthique/juridique. On drive du trafic vers la source, on identifie clairement l'origine, on ne s'approprie pas leur travail. Sans ça, on est plus exposé sur le terrain de la concurrence déloyale (art. 5 LCD).

**Ce qu'il faut faire côté mobile** :

- Dans `mobile/src/screens/DetailScreen.tsx`, ajouter un bloc en bas du contenu principal (avant le footer boutons) :
  - Label eyebrow "Source"
  - Nom lisible de la source (mapping depuis `event.source` → "La Décadanse", "Ville de Genève"…)
  - Un `Pressable` avec icône `external-link` qui ouvre `event.source_url` via `Linking.openURL(...)` de React Native
- Ajouter `source: Optional[str]` et `source_url: Optional[str]` au schéma TS `EventItem` dans `mobile/src/types/api.ts` (peut-être déjà là — à vérifier).
- Backend : le champ `source` existe déjà, remonté par les endpoints `/events/{id}` et `/events`. Rien à changer.

**Effort estimé** : 30 min–1h.

---

## Ajouter d'autres sources Genève

**Statut** : reporté, ordre de priorité indicatif ci-dessous.
**Contexte** : le registry pipeline (`pipeline/sources/registry.py`) est prêt à accueillir plusieurs sources. Chacune = 1 module `pipeline/scrapers/<name>.py` + 1 entrée `Source(...)`. Les tests + le DAG + le CLI la découvrent automatiquement.

### Sources candidates par ordre de facilité juridique / effort

**1. opendata.swiss / Ville de Genève — événements culturels officiels**
- Prio 1. Open data, pas de question juridique. À explorer via `https://opendata.swiss/fr/organization/ville-de-geneve` — chercher datasets "événements", "manifestations", "agenda".
- Format probable : CSV/JSON téléchargeable ou API REST. → méthode `api` dans le registry.
- `category_hint` : `mixed` (culture, sport, expos…). Le mapping `genre → category` du fichier `pipeline/mapping.py` devra sûrement être étendu.
- `trust` : `official`. Utile pour prioriser sur les doublons.

**2. Eventfrog.ch — API publique**
- Prio 2. Ils fournissent une API publique documentée. Zero ambiguïté juridique.
- Couvre toute la Suisse dont Genève. Filtrer par ville dans le fetch.
- Recherche : "eventfrog api docs" — vérifier auth (clé gratuite probablement).

**3. Genève Tourisme (agenda.geneve.ch ou similaire)**
- Prio 3. Leur mission est justement la diffusion, donc ils devraient avoir un flux RSS ou iCal. À vérifier.
- Si pas de flux, contact direct — vu leur rôle promotionnel, ils ont peu d'intérêt à bloquer.

**4. Agenda.ch, sortir.ch, coucou.ch**
- Prio 4. Sites communautaires suisses. Vérifier robots.txt et ToS. Même approche que ladecadanse (UA identifié, attribution, retrait sur demande).

### Ce qu'il faudra probablement toucher au-delà d'ajouter un scraper

- **`pipeline/mapping.py`** : la table `_GENRE_TO_CATEGORY` est calibrée pour le vocabulaire de ladecadanse. Une source `mixed` (opendata) risque d'utiliser un tout autre vocabulaire ("Sport", "Musique classique", "Marché"…). Élargir le mapping ou déléguer au scraper le calcul de `category` dans `EventRaw`.
- **Restaurants** : `kind="restaurant"` prévu dans le registry mais aucune source pour l'instant. Google Places API (coût), TripAdvisor (scraping fragile), OpenStreetMap (gratuit mais qualité inégale). À trancher après le pilote événements.

---

## Config `geneva_only` par source (à ajouter au registry le jour venu)

**Statut** : reporté (2026-09-26).
**Contexte** : `pipeline/runner.py::_is_geneva` filtre en dur toute event dont l'adresse ne se termine pas par "Genève". C'est bien pour ladecadanse (qui liste le Grand Bassin genevois entier — Vaud, France voisine), mais ça devient contre-productif si on ajoute une source déjà pré-filtrée sur Genève (opendata.swiss Ville de Genève, par exemple), ou une source où on veut au contraire couvrir le Grand Genève transfrontalier.

**Ce qu'il faut faire** :
- Ajouter `geneva_only: bool = True` sur la dataclass `Source` dans `pipeline/sources/registry.py`.
- Dans `runner.py::run_source`, remplacer `if not _is_geneva(raw)` par `if source.geneva_only and not _is_geneva(raw)`.
- Une source pré-filtrée (opendata Ville de GE) déclarerait `geneva_only=False` — pas besoin de re-filtrer.

**Effort** : 5 min. À faire quand on ajoute la 2ᵉ source.

## Intégration carte Google Maps sur l'écran détail

**Statut** : planifié (2026-09-26), pas encore commencé.
**Contexte** : `DetailScreen.tsx` affiche aujourd'hui un `<MapPlaceholder />` — un rectangle gris avec l'icône `map` et le texte "Carte à venir". On veut remplacer par une vraie carte interactive centrée sur le lieu de l'événement, avec un marker.

### Prérequis bloquants (à faire avant tout code)

**1. Géocoder les adresses**

Les colonnes `events.latitude` / `events.longitude` existent mais sont toutes `NULL` — ladecadanse ne fournit que des chaînes d'adresse ("Rue des Deux-Ponts 29 (Jonction) - Genève"). Sans coords, pas de marker.

Deux options :
- **Nominatim (OpenStreetMap)** — gratuit, rate-limité à 1 req/sec, licence permissive, mais qualité inégale sur les adresses genevoises fines. Requiert un User-Agent identifié et le respect de leur "Usage Policy". Bon pour un MVP.
- **Google Geocoding API** — payant après un free tier (~$200/mois de crédits Maps Platform = ~40k geocoding calls). Très précis. À utiliser si Nominatim rate trop d'adresses.

Ma reco : Nominatim d'abord. Ajouter au scraper (`pipeline/scrapers/ladecadanse.py`) une étape de géocoding **avec cache** (une table `geocoded_addresses(address_hash, latitude, longitude, resolver, resolved_at)`) pour ne pas re-géocoder les adresses stables. Marquer les events avec `geocode_status` ∈ {`pending`, `resolved`, `not_found`} pour pouvoir retry.

**2. Configurer Google Maps Platform** (si carte réelle Google, pas OSM)

- Créer un projet GCP, activer "Maps SDK for Android", "Maps SDK for iOS", et si on utilise Google Geocoding, "Geocoding API".
- Créer une clé API, la **restreindre** par bundle identifier (iOS) et SHA-1 (Android) — sinon quelqu'un peut te la ré-utiliser.
- Free tier : ~$200/mois de crédit Maps Platform. Un mobile MapView = ~$7 pour 1000 loads. Pour un MVP c'est confortable.
- Stocker la clé dans `mobile/app.json` :
  ```json
  "ios":     { "config": { "googleMapsApiKey": "..." } },
  "android": { "config": { "googleMaps": { "apiKey": "..." } } }
  ```

**3. Point de vigilance Expo Go**

`react-native-maps` avec provider Google **ne marche pas dans Expo Go sur iOS** (contrainte Apple — l'app doit être signée avec la clé). Deux voies :
- **EAS Build** : générer un "dev client" custom qui inclut react-native-maps + notre clé Google. On garde le workflow Expo (JS reload) mais on installe cet APK/IPA sur le téléphone au lieu d'Expo Go.
- **expo-maps** (nouveau, expérimental) — peut fonctionner dans Expo Go, mais surface encore limitée. À évaluer.

Ma reco : commencer avec **EAS Build dev client** — c'est la voie officielle et stable.

### Plan d'implémentation (une fois les 3 prérequis résolus)

1. **Backend** :
   - Migration : ajouter `events.geocode_status: str` (default `'pending'`), table `geocoded_addresses` pour le cache.
   - Task Airflow séparée `geocode_pending_events` — cron horaire, prend les 100 events les plus anciens avec `geocode_status='pending'`, call Nominatim (avec throttle 1 req/s + UA `MyGeneva/0.1 mygeneva@gmail.com`), écrit lat/long + status.

2. **Mobile** :
   - `mobile/src/components/EventMap.tsx` — MapView 200px de haut, provider Google, centré sur `(latitude, longitude)` avec zoom 15, un marker au point.
   - Fallback dans `DetailScreen` : si `latitude` ou `longitude` null → garder le placeholder actuel + un bouton **"Ouvrir dans Maps"** qui fait `Linking.openURL('https://www.google.com/maps/?q=' + encodeURIComponent(address))`. C'est déjà une amélioration nette sur "Carte à venir" et ça marche sans clé API pour les adresses non géocodées.
   - Web (`react-native-web`) : `react-native-maps` n'a pas de support web. Deux options :
     - iframe Google Maps Embed (`https://www.google.com/maps/embed/v1/place?key=X&q=lat,lng`) — nécessite un embed key différent.
     - Simplement afficher le placeholder + bouton "Ouvrir dans Maps" en web, garder MapView pour natif. C'est acceptable et sans coût.

### Effort estimé

- Prérequis geocoding : **2 h** (Nominatim client, migration, backfill).
- Setup GCP + EAS dev client : **1 h** de config + **20 min** de build (async).
- Composant MapView + fallback : **2 h**.
- Total : **~1 journée**.

---

## Sélection du jour — mise en avant par nombre de favoris

**Statut** : planifié (2026-09-26).
**Contexte** : `HomeScreen.tsx` fait aujourd'hui `preview = items.slice(0, PREVIEW_LIMIT)` — juste les 3 premiers events dans l'ordre chronologique. Objectif : mettre en avant les événements que d'autres utilisateurs ont favoris, avec un fallback aléatoire quand on n'a pas assez de signaux.

### Règle validée

Pour le jour + la catégorie sélectionnés :
1. Ranger les events par **nombre de favoris décroissant**.
2. Si moins de 3 events ont au moins un favori, compléter les slots restants avec des events **aléatoires** du même jour+catégorie (qui n'ont pas encore été retenus).
3. Renvoyer 3 events.

Cas limite : personne n'a mis un event en favori → tous ont un compte à 0 → l'ordre est intégralement aléatoire. Cohérent avec l'intention.

Ties (plusieurs events avec le même nombre de favoris) : départage aléatoire (`RANDOM()` en SQL).

### Implémentation

**Nouveau endpoint** `GET /events/highlights?date=YYYY-MM-DD&category=soiree&limit=3` — plus lisible que d'ajouter un `sort=highlights` sur `/events` (la sémantique du filtre est trop différente).

Requête SQL (approximation) :

```sql
SELECT e.*, COUNT(f.id) AS fav_count
FROM events e
LEFT JOIN favorites f
  ON f.item_type = 'event'
 AND f.item_id = e.id
WHERE <filtres jour + catégorie identiques à /events aujourd'hui>
GROUP BY e.id
ORDER BY fav_count DESC, RANDOM()
LIMIT 3
```

En SQLAlchemy/SQLModel :

```python
from sqlalchemy import and_, desc, func
from app.models.favorite import Favorite

fav_count = func.count(Favorite.id).label("fav_count")
query = (
    select(Event, fav_count)
    .outerjoin(
        Favorite,
        and_(Favorite.item_type == FavoriteItemType.event, Favorite.item_id == Event.id),
    )
    .group_by(Event.id)
    .order_by(desc(fav_count), func.random())
    .limit(limit)
)
```

Réutiliser `_apply_day_filter` (le même que `/events`) pour la fenêtre temporelle + double-catégorie + rule 08h — comme ça la sémantique de la sélection est cohérente avec ce que voit la liste complète.

**Mobile** :
- Dans `HomeScreen.tsx`, remplacer `preview = items.slice(0, PREVIEW_LIMIT)` par un appel à `GET /events/highlights?date=&category=&limit=3`.
- Ajouter à `AppContext.tsx` un `highlights: EventItem[] | RestaurantItem[]` + son loading state, refetché quand `selectedDay` ou `category` change.

### Tests à écrire

- 3 events avec 2, 1, 0 favoris → renvoyés dans cet ordre.
- 1 event avec 1 favori + 5 events sans favoris → l'event favori d'abord, 2 des 5 autres aléatoirement.
- 0 event avec favori + 5 events → 3 des 5 tirés au hasard.
- Cas vide (0 event pour le jour) → réponse vide.
- Ties : 3 events avec 1 favori chacun → les 3 renvoyés (dans un ordre aléatoire).

### Effort estimé

- Endpoint + tests : **1 h 30**.
- Mobile switch : **20 min**.
- Total : **~2 h**.

**Note** : cette feature n'aura un effet visible qu'après quelques favorites générés par de vrais utilisateurs. À date le `POC_USER_ID = "poc-user"` est unique — donc au max 1 favori par event, tous les events avec un favori sont ex-æquo. C'est OK, le comportement dégénère proprement en "aléatoire", qui est le comportement voulu du fallback.

---

## Autres pistes évoquées en session, à formaliser plus tard

- **Purge `scrape_runs.raw_html`** : la colonne est prête mais non peuplée (le scraper n'y envoie rien pour l'instant). Si on l'active, prévoir un job Airflow qui garde les N dernières runs par source, sinon la table grossit d'~1 MB/jour.
- **Hébergement backend** (Railway/Fly.io + Postgres managé) : nécessaire pour tester l'app mobile hors du LAN local.
- **Persistance du choix de thème** (light/dark toggle) via AsyncStorage — actuellement le thème repart en `light` à chaque lancement.
- **Vraie table `users`** — le POC utilise `POC_USER_ID = "poc-user"` en constante. À remplacer par un vrai user_id dès qu'on ajoute l'auth.
- **Géocodage** des adresses scrapées vers `(latitude, longitude)` pour la carte : Nominatim (gratuit) ou Google Geocoding (payant). À faire en post-processing du scraper.
