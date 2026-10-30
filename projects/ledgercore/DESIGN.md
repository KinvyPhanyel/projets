# LedgerCore — conception

## Convention monétaire

Les montants sont des entiers en unités mineures d'une seule devise choisie hors du programme. Le signe encode un débit ou un crédit ; la somme d'un journal doit être zéro. Les flottants et booléens ne sont pas acceptés comme montants. Chaque ligne est bornée à 10¹² unités mineures.

## Atomicité et rejeu

Les journaux portent une clé unique et une représentation canonique des lignes ordonnées. Un rejeu exact ne crée aucune ligne ; une même clé avec un contenu différent est rejetée. Journal et lignes sont insérés dans une transaction verrouillée.

## Correction des erreurs

`reverse(original, new_id)` publie des montants opposés plutôt que de modifier les lignes originales. Une même contre-passation rejouée avec son identifiant est idempotente. Le service permet plusieurs contre-passations portant des identifiants différents : l'unicité d'une annulation métier reste à ajouter si nécessaire.

## Contrôles à mener

Tester une écriture déséquilibrée, un rejeu, un montant flottant et une contre-passation. La balance globale doit rester nulle. Une balance négative par compte est autorisée : le moteur est un journal, pas un contrôle de découvert.

## Coûts

La publication dépend du nombre de lignes. La balance utilise une agrégation SQL ; pour une forte volumétrie, prévoir des vues matérialisées réconciliables.

## Limites

Grand livre pédagogique non certifié, sans rapprochement bancaire, fiscalité ni multi-devise. SQLite n’empêche pas un administrateur de modifier directement les écritures.
