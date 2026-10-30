# RoomGuard

Réserver une ressource sans chevauchement, annuler et rejouer une réservation de manière idempotente.

**Domaine :** Réservations et concurrence. **Prérequis :** Python 3.12+, bibliothèque standard. Aucun secret ni service cloud requis. Livrable pédagogique fonctionnel, sans revendication d'exploitation en production.

## Lancer le scénario complet

Depuis la racine du dépôt :

```sh
cd projects/roomguard
python3 app.py --input sample.json
```

Le scénario est modifiable : copier `sample.json` vers un autre fichier puis passer son chemin à `--input`. Les résultats sont écrits en JSON sur la sortie standard. La CLI retourne 0 quand le scénario a été traité ; une décision métier négative peut être un résultat valide (par exemple denied, failed ou unhealthy). Une entrée invalide détectée par l'interface retourne 2.

## Ce qui est implémenté

Voir [la conception détaillée](DESIGN.md) pour les invariants, l'algorithme, les transactions et les limites. Les fonctions sont utilisables directement en Python :

- `instant(text)`
- `Reservations.reserve(self, identifier, resource, owner, start, end)`
- `Reservations.cancel(self, identifier, owner)`
- `Reservations.list(self)`
- `Reservations.close(self)`
- `run(request, db=':memory:')`

## Contrat d'entrée

Le fichier [sample.json](sample.json) donne un exemple complet. Les champs suivants sont consommés au niveau racine :

| Champ | Type | Structure de l'exemple |
| --- | --- | --- |
| `commands` | liste | Champs du premier élément : `action`, `id`, `resource`, `owner`, `start`, `end` |

Les listes de commandes sont traitées dans l'ordre. Les opérations prises en charge et leurs contraintes sont décrites dans DESIGN.md et le code du moteur. Le JSON est une donnée ; il n'est jamais passé à eval ou à un interpréteur de commandes.

## État et répétabilité

Ce projet accepte `--db /tmp/roomguard.db` pour conserver son état. La base est créée si nécessaire. Le comportement de rejeu dépend du contrat métier décrit dans DESIGN.md ; une démo par défaut utilise `:memory:` et repart de zéro.

## Résultat observé

Voir [examples/result.json](examples/result.json), produit par l'exécution réelle du scénario lors de la validation globale. Pour PulseWatch, les ports temporaires et latences sont retirés de l'exemple sauvegardé ; les réponses réseau sont réellement vérifiées.

## Vérifications métier

```sh
python3 -m unittest discover -v
```

Scénarios couverts :

- adjacent and overlap.
- cancel and retry.
- content conflict and timezone.
- two writers cannot double book.

Ces tests ciblent les propriétés livrées ; ils ne constituent ni un audit complet ni une mesure de charge. Le contrôle global du dépôt exécute également les CLI et les dix exemples initiaux.

## Structure

- `app.py` : interface CLI JSON.
- `core.py` : moteur métier indépendant de la CLI.
- `sample.json` : entrée de démonstration fictive.
- `DESIGN.md` : décisions, invariants, coûts et compromis.
- `test_*.py` : cas métier exécutables sans dépendances externes.
- `examples/result.json` : sortie de référence de la démonstration.

## Limites

Sans récurrence, calendrier visuel ni notifications. Les identités sont déclaratives ; la précision des instants utilise des nombres flottants.

## Explorer dans le navigateur

Depuis la racine du dépôt, `python3 automation/serve_lab.py` lance le laboratoire local sur le port 8080. Ouvrir le catalogue, déplier « Manipuler le scénario » puis modifier les données. Le laboratoire exécute ce même moteur ; les sondes PulseWatch y sont volontairement limitées aux cibles de démonstration locales.
