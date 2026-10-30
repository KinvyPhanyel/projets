# StockPilot

Gérer un stock SQLite avec journal de mouvements et prévention des sorties impossibles.

**Domaine :** Gestion et bases de données. **Statut :** démonstrateur pédagogique, Python 3.12+, bibliothèque standard uniquement.

## Exécution

Depuis `projects/stockpilot` :

```sh
python3 app.py --db /tmp/stockpilot-demo.db move clavier 5
```

Pour l’aide : `python3 app.py --help`.

## Architecture

`app.py` contient l’algorithme et une interface CLI. Les fonctions métier peuvent être importées indépendamment. Les données d’exemple sont fictives. L’application ne nécessite aucun secret.

## À expliquer en entretien

Présenter le problème, suivre une entrée jusqu’au résultat et justifier la structure de données utilisée. Modifier les données pour explorer un cas limite. Le code généré est une base d’apprentissage à comprendre et personnaliser avant de le présenter comme une compétence acquise.

## Limites

Prototype local sans authentification ni gestion multi-entrepôts. Chaque répétition de move ajoute un mouvement.

## Suite possible

Ajouter des tests métier approfondis, une interface dédiée et des mesures sur un jeu de données représentatif. Consigner les résultats observés, sans annoncer de performances non mesurées.

## Conception et résultat

Voir [DESIGN.md](DESIGN.md) pour les choix techniques, le coût algorithmique, un exercice et un résultat vérifié.
