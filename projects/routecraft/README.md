# RouteCraft

Trouver un chemin de coût minimal avec l’algorithme de Dijkstra.

**Domaine :** Optimisation et logistique. **Statut :** démonstrateur pédagogique, Python 3.12+, bibliothèque standard uniquement.

## Exécution

Depuis `projects/routecraft` :

```sh
python3 app.py sample.json campus centre
```

Pour l’aide : `python3 app.py --help`.

## Architecture

`app.py` contient l’algorithme et une interface CLI. Les fonctions métier peuvent être importées indépendamment. Les données d’exemple sont fictives. L’application ne nécessite aucun secret.

## À expliquer en entretien

Présenter le problème, suivre une entrée jusqu’au résultat et justifier la structure de données utilisée. Modifier les données pour explorer un cas limite. Le code généré est une base d’apprentissage à comprendre et personnaliser avant de le présenter comme une compétence acquise.

## Limites

Graphe orienté fourni manuellement ; pas de données cartographiques, de trafic ni de distances réelles.

## Suite possible

Ajouter des tests métier approfondis, une interface dédiée et des mesures sur un jeu de données représentatif. Consigner les résultats observés, sans annoncer de performances non mesurées.

## Conception et résultat

Voir [DESIGN.md](DESIGN.md) pour les choix techniques, le coût algorithmique, un exercice et un résultat vérifié.
