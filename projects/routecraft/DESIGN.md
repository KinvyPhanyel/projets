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


## Approfondissement implémenté

Le nouveau moteur utilise Bellman-Ford et complète Dijkstra plutôt que de l'altérer. Les arêtes négatives sont autorisées, par exemple pour des remises modélisées comme coûts. Les sommets bloqués sont retirés avant relaxation.

Après V−1 passes, les arêtes encore relaxables identifient les zones affectées par un cycle négatif atteignable. Cette influence est propagée ; la requête échoue seulement si la destination en dépend. Un cycle inaccessible, ou sans chemin vers la destination, ne rend pas automatiquement la réponse invalide.

Les prédécesseurs reconstruisent le chemin. Une destination inaccessible retourne cost=null et path vide. Le coût est O(VE), mémoire O(V+E). Le scénario montre un trajet moins cher via gare, puis le trajet direct quand gare est fermée. Il ne s'agit pas de routage GPS ni de trafic en temps réel.

Les sections antérieures décrivent le premier `app.py`. Les fonctions de cette section sont livrées dans `advanced.py`.
