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


## Approfondissement implémenté

Le graphe est validé avant toute exécution. Une tâche est soumise quand toutes ses dépendances sont done. Les résultats des parents sont transmis sous forme de dictionnaire ; l'état et les sorties sont modifiés par le seul thread d'ordonnancement.

Une exception entraîne au plus retries reprises additionnelles. Un échec définitif rend ses descendants skipped ; les branches indépendantes peuvent terminer. Les sorties distinguent états, tentatives, résultats et erreurs. La CLI n'exécute que quatre opérations enregistrées (value, sum, multiply, fail), jamais du code fourni par le JSON.

L'API Python execute accepte des handlers applicatifs de confiance. Les reprises peuvent répéter leurs effets : les handlers doivent être idempotents. Il n'y a pas de kill des threads bloqués, de délai global ou de persistance après crash. La concurrence est adaptée aux entrées/sorties, pas une promesse d'accélération CPU.

Les sections antérieures décrivent le premier `app.py`. Les fonctions de cette section sont livrées dans `advanced.py`.
