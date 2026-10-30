# DocuIndex

Indexer des documents locaux et classer les résultats avec un score TF-IDF.

**Domaine :** Recherche et traitement du texte. **Statut :** démonstrateur pédagogique, Python 3.12+, bibliothèque standard uniquement.

## Exécution

Depuis `projects/docuindex` :

```sh
python3 app.py documents "sécurité données"
```

Pour l’aide : `python3 app.py --help`.

## Architecture

`app.py` contient l’algorithme et une interface CLI. Les fonctions métier peuvent être importées indépendamment. Les données d’exemple sont fictives. L’application ne nécessite aucun secret.

## À expliquer en entretien

Présenter le problème, suivre une entrée jusqu’au résultat et justifier la structure de données utilisée. Modifier les données pour explorer un cas limite. Le code généré est une base d’apprentissage à comprendre et personnaliser avant de le présenter comme une compétence acquise.

## Limites

Recherche lexicale explicable, sans LLM, embeddings ou compréhension sémantique. Charge les documents en mémoire.

## Suite possible

Ajouter des tests métier approfondis, une interface dédiée et des mesures sur un jeu de données représentatif. Consigner les résultats observés, sans annoncer de performances non mesurées.

## Conception et résultat

Voir [DESIGN.md](DESIGN.md) pour les choix techniques, le coût algorithmique, un exercice et un résultat vérifié.
