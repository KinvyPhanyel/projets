# PulseWatch

Mesurer le statut et la latence d’une URL HTTP avec des délais bornés.

**Domaine :** Observabilité et réseau. **Statut :** démonstrateur pédagogique, Python 3.12+, bibliothèque standard uniquement.

## Exécution

Depuis `projects/pulsewatch` :

```sh
python3 app.py http://127.0.0.1:8080/
```

La commande suppose que le catalogue est déjà lancé depuis la racine du dépôt : `python3 -m http.server 8080 --bind 127.0.0.1 --directory site`. Une URL inaccessible produit un résultat en erreur et un code de sortie 1.

Pour l’aide : `python3 app.py --help`.

## Architecture

`app.py` contient l’algorithme et une interface CLI. Les fonctions métier peuvent être importées indépendamment. Les données d’exemple sont fictives. L’application ne nécessite aucun secret.

## À expliquer en entretien

Présenter le problème, suivre une entrée jusqu’au résultat et justifier la structure de données utilisée. Modifier les données pour explorer un cas limite. Le code généré est une base d’apprentissage à comprendre et personnaliser avant de le présenter comme une compétence acquise.

## Limites

À utiliser sur des services autorisés. CLI locale, pas une API publique : n’exposez pas une sonde acceptant des URL arbitraires sans protection SSRF. Certains serveurs refusent HEAD.

## Suite possible

Ajouter des tests métier approfondis, une interface dédiée et des mesures sur un jeu de données représentatif. Consigner les résultats observés, sans annoncer de performances non mesurées.

## Conception et résultat

Voir [DESIGN.md](DESIGN.md) pour les choix techniques, le coût algorithmique, un exercice et un résultat vérifié.
