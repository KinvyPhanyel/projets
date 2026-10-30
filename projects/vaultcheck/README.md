# VaultCheck

Créer et vérifier un manifeste SHA-256 de fichiers locaux.

**Domaine :** Intégrité et sauvegardes. **Statut :** démonstrateur pédagogique, Python 3.12+, bibliothèque standard uniquement.

## Exécution

Depuis `projects/vaultcheck` :

```sh
python3 app.py create documents /tmp/vaultcheck-demo.json
```

Le manifeste doit être inexistant lors de `create` ; choisir un nouveau nom si nécessaire. Pour contrôler ensuite les fichiers :

```sh
python3 app.py verify documents /tmp/vaultcheck-demo.json
```

Pour l’aide : `python3 app.py --help`.

## Architecture

`app.py` contient l’algorithme et une interface CLI. Les fonctions métier peuvent être importées indépendamment. Les données d’exemple sont fictives. L’application ne nécessite aucun secret.

## À expliquer en entretien

Présenter le problème, suivre une entrée jusqu’au résultat et justifier la structure de données utilisée. Modifier les données pour explorer un cas limite. Le code généré est une base d’apprentissage à comprendre et personnaliser avant de le présenter comme une compétence acquise.

## Limites

SHA-256 détecte les modifications mais ne chiffre et ne signe pas les fichiers. Conserver le manifeste en lieu sûr. Les liens symboliques sont ignorés ; fichiers supposés stables pendant la lecture.

## Suite possible

Ajouter des tests métier approfondis, une interface dédiée et des mesures sur un jeu de données représentatif. Consigner les résultats observés, sans annoncer de performances non mesurées.

## Conception et résultat

Voir [DESIGN.md](DESIGN.md) pour les choix techniques, le coût algorithmique, un exercice et un résultat vérifié.
