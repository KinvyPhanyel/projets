# Conception — FlowDAG

## Choix principal

**Tri topologique déterministe avec file de priorité.** Le graphe associe chaque tâche à ses dépendances. Les tâches disponibles sont prises dans un tas lexical. Retirer une dépendance peut rendre une tâche disponible. Un résultat incomplet signale un cycle.

## Coût et échelle

La version pédagogique rescane les tâches après chaque extraction : O(V²+E), plus les opérations du tas. Un index des successeurs permettrait O(V+E+V log V).

## Manipulation guidée

Créer un cycle entre extract et report puis observer le rejet. Ajouter une branche indépendante pour vérifier l’ordre lexical.

## Exemple réellement vérifié

La sortie ci-dessous provient du scénario fonctionnel de `automation/check_portfolio.py`. Certains scénarios couvrent des données supplémentaires par rapport à la commande rapide du README.

```json
{
  "order": [
    "extract",
    "validate",
    "report"
  ],
  "cycle_rejected": true
}
```

## Questions à préparer pour une présentation

Tri topologique, déterminisme, gestion des échecs, planification et différence entre planifier et exécuter.

## Limites du livrable

Planificateur déterministe, sans exécution de commandes, parallélisme ou reprise après panne.
