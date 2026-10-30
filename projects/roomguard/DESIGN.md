# RoomGuard — conception

## Intervalles et dates

Les intervalles sont semi-ouverts [début, fin[ : une réservation à 10 h peut suivre celle qui se termine à 10 h. Le conflit s'écrit `existing.start < new.end AND existing.end > new.start`. Les dates sans fuseau sont rejetées et les instants sont stockés en secondes UTC.

## Concurrence et idempotence

BEGIN IMMEDIATE sérialise vérification et insertion entre connexions SQLite. L'identifiant de réservation est également une clé idempotente : le même contenu retourne l'enregistrement, un contenu différent est rejeté. Rejouer une réservation annulée retourne son état annulé, sans la réactiver.

## Propriété de l'annulation

L'annulation requiert le propriétaire déclaré de la réservation. Elle est logique : l'historique reste présent et un nouveau créneau peut être réservé. Cette vérification n'authentifie pas le propriétaire.

## Scénarios à explorer

Réserver la même salle sur un intervalle chevauchant, une salle différente au même moment et le même intervalle après annulation. Vérifier également des dates équivalentes exprimées avec deux décalages UTC.

## Passage à une API

Ajouter authentification, contrôle de taille, gestion de contention et validation des ressources. En PostgreSQL, une contrainte d'exclusion sur une plage peut remplacer le verrou global SQLite.

## Limites

Sans récurrence, calendrier visuel ni notifications. Les identités sont déclaratives ; la précision des instants utilise des nombres flottants.
