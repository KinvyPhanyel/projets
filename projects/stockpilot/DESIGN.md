# Conception — StockPilot

## Choix principal

**Une transaction SQLite par mouvement.** Deux tables séparent l’état courant et les mouvements. Les requêtes paramétrées évitent la concaténation de SQL. La contrainte CHECK empêche un stock négatif et le journal est enregistré dans la même transaction.

## Coût et échelle

Recherche d’un SKU via clé primaire. Écritures sérialisées par SQLite ; aucune promesse de débit n’est faite.

## Manipulation guidée

Ajouter cinq claviers, en retirer deux, tenter d’en retirer quatre. La dernière opération doit échouer sans ajouter de mouvement.

## Exemple réellement vérifié

La sortie ci-dessous provient du scénario fonctionnel de `automation/check_portfolio.py`. Certains scénarios couvrent des données supplémentaires par rapport à la commande rapide du README.

```json
{
  "sku": "keyboard",
  "quantity": 3,
  "rejected_overdraft": true
}
```

## Questions à préparer pour une présentation

Transactions concurrentes, inventaire initial, corrections auditables et limite d’une base SQLite locale.

## Limites du livrable

Prototype local sans authentification ni gestion multi-entrepôts. Chaque répétition de move ajoute un mouvement.
