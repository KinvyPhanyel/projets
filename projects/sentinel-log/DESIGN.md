# Conception — Sentinel Log

## Choix principal

**Une file temporelle par couple adresse IP / utilisateur.** Chaque échec est ajouté à une deque. Les événements sortis de la fenêtre sont retirés avant de comparer le nombre d’échecs au seuil. Une alerte est produite au franchissement du seuil, et non à chaque échec supplémentaire.

## Coût et échelle

Tri O(n log n), puis traitement amorti O(n). La mémoire dépend des événements retenus par clé.

## Manipulation guidée

Essayer un succès entre deux échecs, puis des échecs espacés de plus de cinq minutes. Un succès n’efface pas la fenêtre dans cette version.

## Exemple réellement vérifié

La sortie ci-dessous provient du scénario fonctionnel de `automation/check_portfolio.py`. Certains scénarios couvrent des données supplémentaires par rapport à la commande rapide du README.

```json
[
  {
    "ip": "192.0.2.10",
    "user": "demo",
    "attempts": 3,
    "timestamp": "2026-10-30T10:00:02+00:00",
    "rule": "repeated_auth_failure"
  }
]
```

## Questions à préparer pour une présentation

Faux positifs, diversité des horodatages, cardinalité des adresses et données personnelles.

## Limites du livrable

Les règles sont heuristiques. Aucun blocage réseau ni collecte de secrets. Les événements doivent avoir des horodatages compatibles.
