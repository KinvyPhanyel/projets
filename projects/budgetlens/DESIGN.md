# Conception — BudgetLens

## Choix principal

**Agrégation par catégorie avec Decimal.** Le CSV est lu avec DictReader. Chaque montant doit être fini et non négatif. Decimal préserve les centimes ; le dépassement est strictement supérieur au plafond.

## Coût et échelle

O(n) en temps et O(c) en mémoire pour c catégories.

## Manipulation guidée

Changer le plafond transport dans budgets.json. Vérifier les dépenses égales au plafond et les montants comportant des centimes.

## Exemple réellement vérifié

La sortie ci-dessous provient du scénario fonctionnel de `automation/check_portfolio.py`. Certains scénarios couvrent des données supplémentaires par rapport à la commande rapide du README.

```json
[
  {
    "category": "transport",
    "spent": "2500.30",
    "limit": "2000",
    "over_budget": true
  }
]
```

## Questions à préparer pour une présentation

Devise, remboursements, arrondis, plafonds absents et confidentialité des dépenses.

## Limites du livrable

Montants dans une seule devise choisie par l’utilisateur ; pas de connexion bancaire ni de conseil financier.


## Approfondissement implémenté

Les transactions distinguent income, expense et refund. Une dépense et un remboursement sont saisis comme montants non négatifs ; le sens est porté par kind, ce qui évite des doubles négations. Les montants utilisent Decimal et refusent plus de deux décimales.

Le rapport inclut uniquement les dates du mois de as_of jusqu'à cette date. Il affiche la dépense nette, le reste du plafond, les revenus et le flux net. Les catégories budgétées sans dépenses restent visibles. La projection extrapole la moyenne journalière à la durée réelle du mois, y compris février bissextile.

Cette projection n'est pas un modèle prédictif : elle ignore les charges à venir et peut être négative si les remboursements dépassent les dépenses du mois. Les tests contrôlent filtrage temporel, remboursement et précision monétaire. Pas de multi-devise ni de connexion bancaire.

Les sections antérieures décrivent le premier `app.py`. Les fonctions de cette section sont livrées dans `advanced.py`.
