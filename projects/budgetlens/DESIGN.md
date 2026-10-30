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
