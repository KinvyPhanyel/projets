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


## Approfondissement implémenté

Le module avancé normalise les dates en instants et trie les événements, y compris des fuseaux différents. Une deque par couple IP/utilisateur détecte la brute force ; une seconde par IP compte les utilisateurs distincts pour le spraying. Un succès après le seuil émet une alerte de sévérité élevée puis réinitialise les échecs du couple.

Les règles brute force et spray restent désarmées tant que le seuil reste franchi, pour éviter une alerte par ligne. Les réseaux de confiance CIDR sont filtrés avant corrélation et le compteur d'événements ignorés est exposé. L'identité d'un utilisateur et les événements doivent venir de journaux fiables.

L'algorithme est un traitement de lot : tri O(n log n), mémoire liée aux clés et événements retenus. Les utilisateurs distincts sont recomptés à chaque événement, ce qui est coûteux pour une IP très active. Il n'y a pas de stockage persistant, de gestion de retard en flux ou de notification. Les tests couvrent les trois règles et le filtre CIDR.

Les sections antérieures décrivent le premier `app.py`. Les fonctions de cette section sont livrées dans `advanced.py`.
