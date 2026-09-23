# Design-reference.md — Charte visuelle et logique d'interaction (issues de la maquette validée)

Ce document reprend ce qui a été validé sur le prototype cliquable (Claude Design). L'app React Native doit reproduire ce comportement et ce style, pas les réinventer.

## 1. Charte visuelle

**Polices** (Google Fonts)
- Titres/display : `Fraunces` (poids 560–650) — via `@expo-google-fonts/fraunces` ou chargement de police Expo
- Texte courant : `Work Sans` (poids 400–600) — via `@expo-google-fonts/work-sans`

**Couleurs**
| Rôle | Hex |
|---|---|
| Fond principal | `#FAF6F0` |
| Fond des cartes | `#FFFFFF` |
| Bordures | `#E5DACB` |
| Texte principal | `#1F1B16` |
| Texte secondaire / meta | `#6B6153` |
| Accent principal (catégorie Journée, CTA) | `#C1622D` |
| Accent secondaire (catégorie Soirée, tags) | `#2F4858` |
| Accent restaurant (note, icône) | `#4B7A6F` |
| Fond placeholder image événement | `#EFE3D3` |
| Fond placeholder image restaurant | `#E4EBE8` |

**Style général**
- Coins arrondis généreux (14–16px sur les cartes, 999px sur les pills/boutons ronds)
- Pas d'ombres marquées, bordures fines plutôt que shadow
- Icônes en traits fins (stroke), jamais d'emoji

## 2. Écrans et logique de navigation (état partagé)

L'app doit gérer un état de navigation similaire à celui du prototype : écran actif (`accueil` / `liste` / `détail` / `favoris`), catégorie sélectionnée (`journée` / `soirée` / `restaurant`), item sélectionné, et liste de favoris — partagés entre écrans (pas de perte d'état en naviguant).

### Écran Accueil
- Header : jour du en cours + sélecteur de jour (pills horizontales, scroll)
- Tabs catégorie (Journée / Soirée / Restaurant) — bascule dynamique du contenu affiché en dessous, sans rechargement d'écran
- Aperçu de 3 items max pour la catégorie sélectionnée
- Bouton "Voir tout" → écran Liste (catégorie conservée)
- Nav bar basse : Accueil / Favoris

### Écran Liste
- Même sélecteur de catégorie qu'à l'accueil (état partagé)
- Liste complète (scroll) des items de la catégorie sélectionnée
- Chaque carte : icône type, titre, meta (horaire pour événements, note pour restaurants), localisation
- Bouton favori (cœur) directement sur chaque carte, sans ouvrir le détail (stopPropagation du clic)
- Retour → Accueil

### Écran Détail
- Image/placeholder en haut avec bouton retour et bouton favori en overlay
- Tag catégorie, titre, meta (horaire ou note), localisation, description, adresse + bloc carte (placeholder à ce stade)
- Boutons bas d'écran : "Itinéraire" (non fonctionnel pour l'instant) + bouton favori dynamique ("Ajouter aux favoris" / "Ajouté aux favoris")
- Retour arrière → renvoie vers l'écran d'origine (Accueil, Liste ou Favoris), pas systématiquement vers Accueil

### Écran Favoris
- Liste des items favoris, mélangeant événements et restaurants, avec tag de type par item
- Bouton favori sur chaque carte pour retirer directement de la liste
- État vide si aucun favori : message d'invitation à en ajouter
- Nav bar basse : Accueil / Favoris

## 3. Modèle de données d'exemple (pour le seed backend et les tests mobile)

Reprendre ces exemples (déjà utilisés dans la maquette) comme données de seed, pour une cohérence entre le prototype validé et l'app réelle :

**Journée**
- Marché des artisans du Molard — 10h–18h — Vieille-Ville
- Balade à vélo au bord du lac — 14h–16h — Quai Gustave-Ador
- Visite guidée du Jardin Anglais — 11h — Jardin Anglais

**Soirée**
- Jazz au Sud des Alpes — 20h30–23h00 — Plainpalais
- Projection en plein air — Parc La Grange — 21h15
- Soirée salsa — L'Usine — 22h
- Concert rock — La Gravière — 19h45 — La Jonction

**Restaurants**
- Café des Bains — 4.6 — Carouge
- La Buvette des Bains — 4.3 — Pâquis
- Chez Ma Cousine — 4.4 — Vieille-Ville

## 4. Ce qui n'est volontairement pas dans la maquette (à garder simple aussi côté app)
- Pas de barre de recherche
- Pas de filtre géolocalisé "autour de moi"
- Pas d'authentification (favoris liés à un `user_id` unique/hardcodé)
