# TaskBoard — conception

## Invariants et modèle

Une tâche possède un identifiant stable, un responsable, un état et une version. Le graphe autorise todo → doing → review → done avec retours explicites depuis doing et review. Une tâche terminée ne se rouvre pas dans cette version.

Chaque mutation commence par BEGIN IMMEDIATE : lecture de version, modification et insertion d'audit appartiennent à la même transaction. Une version périmée est rejetée, même si la transition aurait autrement été valide. Les commandes du scénario sont des transactions indépendantes, pas un lot atomique.

## Interfaces et persistance

`TaskBoard.apply(command)` retourne la tâche mise à jour. `snapshot()` restitue tâches et journal triés. `--db board.db` conserve les données ; la démo par défaut emploie une base en mémoire pour rester répétable. Rejouer create sur une base existante est une erreur volontaire.

## Scénario de conflit

Deux éditeurs lisent la version 1. Le premier passe la tâche à doing : version 2. Le second envoie version 1 : rejet et aucune entrée d'audit additionnelle. Cette propriété est couverte par les tests.

## Évolution

Ajouter adhésion aux équipes, règles d'autorisation, pagination et migrations versionnées avant d'exposer une API. L'acteur est une information fournie par la CLI, pas une identité authentifiée.

## Limites

Application locale sans serveur HTTP ni authentification. Le journal SQLite peut être modifié par quiconque possède le fichier ; il ne constitue pas une preuve inviolable.
