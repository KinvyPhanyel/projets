# RouteCraft

Routage avec sommets bloqués, poids négatifs et détection des cycles négatifs qui influencent la destination.

**Domaine :** Optimisation et logistique. **Prérequis :** Python 3.12+, bibliothèque standard. Aucun secret ni service cloud requis. Livrable pédagogique fonctionnel, sans revendication d'exploitation en production.

## Lancer le scénario complet

Depuis la racine du dépôt :

```sh
cd projects/routecraft
python3 advanced.py --input advanced-sample.json
```

Le premier `app.py` reste disponible avec ses exemples initiaux. `advanced.py` ajoute les fonctions détaillées ci-dessous.

Le scénario est modifiable : copier `advanced-sample.json` vers un autre fichier puis passer son chemin à `--input`. Les résultats sont écrits en JSON sur la sortie standard. La CLI retourne 0 quand le scénario a été traité ; une décision métier négative peut être un résultat valide (par exemple denied, failed ou unhealthy). Une entrée invalide détectée par l'interface retourne 2.

## Ce qui est implémenté

Voir [la conception détaillée](DESIGN.md) pour les invariants, l'algorithme, les transactions et les limites. Les fonctions sont utilisables directement en Python :

- `bellman_ford(graph, start, end, blocked=())`
- `run(request, db=':memory:')`

## Contrat d'entrée

Le fichier [advanced-sample.json](advanced-sample.json) donne un exemple complet. Les champs suivants sont consommés au niveau racine :

| Champ | Type | Structure de l'exemple |
| --- | --- | --- |
| `graph` | objet | Clés de l’exemple : `campus`, `gare`, `centre` |
| `queries` | liste | Champs du premier élément : `start`, `end` |

Les listes de commandes sont traitées dans l'ordre. Les opérations prises en charge et leurs contraintes sont décrites dans DESIGN.md et le code du moteur. Le JSON est une donnée ; il n'est jamais passé à eval ou à un interpréteur de commandes.

## État et répétabilité

Ce projet travaille en mémoire ; `--db` est accepté par l’interface uniforme mais n’est pas utilisé. Aucun état ne survit à la fin du processus.

## Résultat observé

Voir [examples/result.json](examples/result.json), produit par l'exécution réelle du scénario lors de la validation globale. Pour PulseWatch, les ports temporaires et latences sont retirés de l'exemple sauvegardé ; les réponses réseau sont réellement vérifiées.

## Vérifications métier

```sh
python3 -m unittest discover -v
```

Scénarios couverts :

- negative edge and blocked node.
- relevant negative cycle.
- irrelevant cycle and unreachable.

Ces tests ciblent les propriétés livrées ; ils ne constituent ni un audit complet ni une mesure de charge. Le contrôle global du dépôt exécute également les CLI et les dix exemples initiaux.

## Structure

- `advanced.py` : interface CLI et moteur avancé.
- `advanced-sample.json` : entrée de démonstration fictive.
- `DESIGN.md` : décisions, invariants, coûts et compromis.
- `test_*.py` : cas métier exécutables sans dépendances externes.
- `examples/result.json` : sortie de référence de la démonstration.

## Limites

Graphes fournis par scénario ; pas de cartographie, trafic ou calcul géographique.

## Explorer dans le navigateur

Depuis la racine du dépôt, `python3 automation/serve_lab.py` lance le laboratoire local sur le port 8080. Ouvrir le catalogue, déplier « Manipuler le scénario » puis modifier les données. Le laboratoire exécute ce même moteur ; les sondes PulseWatch y sont volontairement limitées aux cibles de démonstration locales.
