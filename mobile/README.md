# Mobile — MyGeneva (Expo / React Native)

App mobile de MyGeneva. Reproduit à l'identique la logique de navigation et la charte visuelle du prototype validé (voir `design-reference.md`).

## Prérequis

- Node.js ≥ 18 (LTS)
- npm ou pnpm
- Expo Go sur ton téléphone (iOS/Android) OU un simulateur

## Démarrage

```
npm install
npm run start
```

Puis scanner le QR code avec Expo Go.

## Connexion à l'API

Par défaut l'app pointe sur `http://localhost:8000` (voir `app.json` → `extra.apiUrl`).

- **Simulateur iOS** : `localhost` marche.
- **Émulateur Android** : `localhost` est réécrit en `10.0.2.2` par `src/api/client.ts`.
- **Téléphone physique** : `localhost` ne marche pas. Utilise l'IP LAN de ta machine :

  ```
  EXPO_PUBLIC_API_URL=http://192.168.x.x:8000 npm run start
  ```

  Sur Windows PowerShell :
  ```
  $env:EXPO_PUBLIC_API_URL="http://192.168.x.x:8000"; npm run start
  ```

## Architecture

- `src/state/AppContext.tsx` — état partagé entre écrans (écran actif, catégorie, jour, favoris). Pas de React Navigation : la V1 imite la logique du prototype (un seul contexte, `screen` détermine l'écran actif). Suffisant pour 4 écrans.
- `src/api/` — client fetch + endpoints par domaine.
- `src/theme/` — couleurs, typographies, spacings (miroir de `design-reference.md`).
- `src/components/` — cartes, tabs, sélecteur de jour, cœur favori réutilisable.
- `src/screens/` — 4 écrans : Accueil, Liste, Détail, Favoris.

## Type-check

```
npm run typecheck
```
