# EventRail — conception

## Stockage et concurrence optimiste

Chaque flux possède une version continue commençant à 1. append demande la version lue par le client et écrit un lot atomique. Une seconde écriture avec une version périmée est rejetée. Le numéro global seq permettrait une projection multi-flux ; la projection livrée est par flux.

## Canonicalisation et chaîne

Les objets sont sérialisés avec clés triées, sans NaN, puis l'empreinte SHA-256 inclut stream, version, contenu et empreinte précédente. verify recalcule la chaîne et vérifie la continuité. Le rejeu métier refuse une chaîne incohérente.

## Projection métier

Les événements deposit et withdraw possèdent un entier positif. La projection somme les mouvements ; un solde négatif reste autorisé. L'event store est générique et peut conserver d'autres types, mais cette projection les refuse.

## Garanties et limites

La chaîne détecte une modification accidentelle sans recalcul de toutes les empreintes suivantes. Elle ne détecte pas la suppression d'une fin de flux sans ancrage externe. Un administrateur peut réécrire toute la chaîne : ce n'est pas une blockchain ni une signature.

## Évolution

Ajouter des checkpoints signés, un outbox transactionnel, des projections avec offset persistant et une politique d'évolution des schémas d'événements.

## Limites

Pas de broker, réplication, signatures ou garantie exactly-once. Le journal est append-only par l’API, pas contre un accès direct au fichier SQLite.
