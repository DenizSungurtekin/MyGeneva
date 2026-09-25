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

## Autres pistes évoquées en session, à formaliser plus tard

- **Purge `scrape_runs.raw_html`** : la colonne est prête mais non peuplée (le scraper n'y envoie rien pour l'instant). Si on l'active, prévoir un job Airflow qui garde les N dernières runs par source, sinon la table grossit d'~1 MB/jour.
- **Hébergement backend** (Railway/Fly.io + Postgres managé) : nécessaire pour tester l'app mobile hors du LAN local.
- **Persistance du choix de thème** (light/dark toggle) via AsyncStorage — actuellement le thème repart en `light` à chaque lancement.
- **Vraie table `users`** — le POC utilise `POC_USER_ID = "poc-user"` en constante. À remplacer par un vrai user_id dès qu'on ajoute l'auth.
- **Géocodage** des adresses scrapées vers `(latitude, longitude)` pour la carte : Nominatim (gratuit) ou Google Geocoding (payant). À faire en post-processing du scraper.
