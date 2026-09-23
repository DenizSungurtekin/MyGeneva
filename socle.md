# Socle projet — App d'agrégation événements & restaurants (Genève)

## 1. Contexte et origine

Recherche d'une idée de side project rentable, portée par un profil ingénieur full stack / data, en solo, sans contrainte financière immédiate (revenu principal assuré par ailleurs). Format cible : SaaS / app mobile.

Idée initiale : une app qui recense ce qu'il y a à faire dans une ville (journée/soirée) et des suggestions de restaurants.

## 2. Étude de marché (résumé)

Le marché des "apps de sortie" est déjà saturé sur des usages spécifiques et bien établis :
- Cinéma → AlloCiné
- Réservation resto → TheFork
- Concerts → DICE, Bandsintown
- Soirées/festivals → Shotgun
- Billetterie généraliste → Eventbrite
- Rencontres/sorties spontanées → Timeleft, Toot Sweet

En revanche, l'**agrégation événements + lieux à visiter, ville par ville**, est un marché fragmenté :
- Dominé par des apps officielles de villes/offices de tourisme (Cannes Agenda, Alsace Explorer, Paris je t'aime, Lorient mon Agglo) : isolées par territoire, souvent peu innovantes côté produit, portées par des collectivités.
- Quelques apps privées multi-villes existent (MyEvent à Lyon, ToDoWiz'U) mais aucune identifiée pour Genève.
- De nombreux sites web agrégateurs existent, preuve que le besoin de centralisation est réel, mais aucun n'a percé sur mobile de façon dominante.

**Conclusion marché** : le vide identifié est spécifique à Genève (pas d'équivalent à MyEvent/Cannes Agenda), et plus largement, aucun acteur n'a construit un "agrégateur automatisé multi-villes" avec une vraie UX mobile moderne — la plupart des apps existantes reposent sur une saisie manuelle, ville par ville.

## 3. Problème identifié

Pour savoir "qu'est-ce que je fais ce soir / ce week-end à Genève", il faut aujourd'hui jongler entre plusieurs sources dispersées (office du tourisme, Google Maps, Instagram, bouche-à-oreille, presse locale). Aucune source n'est pensée pour répondre directement à "je suis dispo, qu'est-ce qui se passe près de moi, maintenant ou bientôt".

## 4. Utilisateurs cibles

- Habitants de Genève cherchant à sortir de leur routine
- Nouveaux arrivants (expats, étudiants, déménagement récent)
- Touristes / visiteurs de courte durée
- Professionnels de passage avec du temps libre

## 5. Proposition de valeur

- Une seule app plutôt que plusieurs sources à consulter
- Contenu tenu à jour en continu (contrairement aux apps officielles souvent à l'abandon)
- Catégorisation par usage réel : sortir ce soir ≠ activité en famille ≠ envie de resto
- Couverture large : au-delà de l'événementiel "officiel", inclusion des bars, restos, marchés, activités diverses

## 6. Stratégie de scaling

Décision : **scaling en profondeur plutôt que géographique**, cohérent avec une exécution solo.

- Démarrage exclusif sur Genève (ville connue par le fondateur, réseau local potentiel, capacité à juger soi-même la qualité du contenu)
- Extension à d'autres villes envisageable plus tard, uniquement après validation du ratio automatisation / charge manuelle sur Genève
- Le scaling géographique rapide est jugé trop risqué à ce stade pour une personne seule (charge de vérification et de correction par ville)

## 7. Approche contenu

- Objectif : automatiser le plus possible la collecte de données (web scraping, recherche via IA)
- Mise en place d'un système de monitoring pour identifier rapidement les sources en échec
- Mécanismes de fallback pour limiter l'impact des ruptures de collecte
- Une couche IA pour réduire les erreurs / trous de couverture
- Le travail manuel reste, dans un premier temps, entièrement porté par le fondateur (pas de contribution communautaire prévue au lancement)
- Point de vigilance produit : gérer l'écart possible entre "source à jour" et "réalité terrain" (annulation, changement de dernière minute) — envisager un indicateur de fraîcheur/fiabilité de l'info à termes

## 8. Modèle économique

- Gratuit pour l'utilisateur final, au moins dans un premier temps
- Monétisation future envisagée : mise en avant payante de restaurants/événements auprès des établissements, une fois l'audience et l'usage prouvés
- Pas de pression financière immédiate sur le fondateur : la preuve d'usage prime sur la monétisation précoce

## 9. Marketing

- Budget disponible pour un test marketing initial (pas de contrainte forte)
- Canaux à étudier plus tard : réseaux sociaux locaux (Instagram/TikTok), influenceurs genevois, partenariats locaux — plutôt que du SEO

## 10. Périmètre du MVP

### Fonctionnalités core
- Liste/carte des événements et lieux à Genève
- 3 catégories : **Journée / Soirée / Restaurant**
- Pour chaque item : titre, description courte, localisation (carte), horaire/date, catégorie, photo (optionnel)
- Navigation par jour (calendrier jour par jour, pas de blocs "aujourd'hui/week-end/à venir"), avec "aujourd'hui" par défaut à l'ouverture

### Fonctionnalités incluses au lancement
- Favoris / liste "à voir plus tard"
- Partage d'un événement (lien ou capture)
- Notification push hebdomadaire ("ce qui se passe cette semaine/ce week-end")

### Explicitement exclu du MVP
- Réservation intégrée / paiement / mise en avant payante
- Fonctionnalités sociales (amis, groupes, type Timeleft)
- Multi-villes, multi-langues
- Compte utilisateur complexe (login simple ou usage sans compte au départ)
- Signalement communautaire (type Waze) — envisageable plus tard une fois une base d'utilisateurs établie

### Périmètre géographique et volumétrie de lancement
- Toute la ville de Genève, sans découpage par quartier au lancement
- Volume cible avant ouverture au public :
  - 1 à 5 activités "journée" par jour
  - 1 à 5 activités "soirée" par jour
  - 5 à 10 restaurants par jour

### Critère de succès du MVP
Le test central n'est pas la robustesse technique mais l'usage : **est-ce qu'un utilisateur revient consulter l'app, au moins une fois par semaine, pour décider de sa sortie ?**
Si l'usage ne prend pas, l'hypothèse à challenger en priorité est la fraîcheur/qualité du contenu ou l'absence d'habitude créée — pas nécessairement le manque de fonctionnalités.

## 11. Prochaine étape

Passage à la définition technique : architecture, sources de données pour Genève, structure du système d'agrégation/monitoring.
