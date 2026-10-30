# Conception — RouteCraft

## Choix principal

**Dijkstra avec tas et reconstruction du chemin.** Les coûts doivent être finis et positifs ou nuls. Le tas fournit le prochain sommet au coût minimal. Les entrées périmées sont ignorées ; les prédécesseurs reconstruisent le trajet.

## Coût et échelle

O((V+E) log V) pour un graphe usuel, mémoire O(V+E). Les sommets sont des chaînes JSON.

## Manipulation guidée

Comparer campus→centre direct (9) au trajet par gare (4+2). Supprimer l’arête gare→centre et observer le trajet direct.

## Exemple réellement vérifié

La sortie ci-dessous provient du scénario fonctionnel de `automation/check_portfolio.py`. Certains scénarios couvrent des données supplémentaires par rapport à la commande rapide du README.

```json
{
  "cost": 6,
  "path": [
    "campus",
    "gare",
    "centre"
  ]
}
```

## Questions à préparer pour une présentation

Pourquoi les poids négatifs sont rejetés, graphes orientés, sommets inaccessibles et différence avec A*.

## Limites du livrable

Graphe orienté fourni manuellement ; pas de données cartographiques, de trafic ni de distances réelles.
