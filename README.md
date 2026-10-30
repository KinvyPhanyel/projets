# Laboratoire informatique — 22 projets

Douze nouveaux projets et dix projets approfondis, avec moteurs métier autonomes, scénarios modifiables, documentation de conception et tests. Les thèmes couvrent sécurité, transactions, systèmes, données, optimisation et apprentissage automatique.

Ces projets ont été réalisés avec assistance IA. Ce sont des implémentations pédagogiques exécutables : aucun utilisateur réel, déploiement en production ou résultat de performance n'est revendiqué. Le dossier de chaque projet décrit précisément ses garanties et ses limites.

## Essayer dans le navigateur

Python **3.12+** suffit, sans installation de dépendance :

```sh
cd /workspace/projets
python3 automation/serve_lab.py
```

Sur votre machine, remplacer le chemin par celui du dépôt cloné. Le laboratoire écoute seulement sur l'interface locale, port **8080**. Le catalogue permet de filtrer les 22 projets, lire les résultats vérifiés, modifier le scénario JSON et exécuter le moteur Python. Les données SQLite des démonstrations web sont en mémoire et isolées à chaque exécution.

Le mode statique reste disponible avec `python3 -m http.server 8080 --bind 127.0.0.1 --directory site` : descriptions et résultats sont consultables, mais l'exécution interactive nécessite serve_lab.py. Aucun hébergement distant n'est activé.

## Catalogue

| Projet | Domaine | Fonctions livrées |
| --- | --- | --- |
| [Sentinel Log](projects/sentinel-log/README.md) | Cybersécurité | Corrélation de trois règles : brute force, password spraying et connexion réussie après échecs ; fenêtres UTC et réseaux de confiance. |
| [StockPilot](projects/stockpilot/README.md) | Gestion et bases de données | Stock multi-entrepôts avec transferts atomiques, audit et idempotence des opérations. |
| [BudgetLens](projects/budgetlens/README.md) | Finance personnelle | Analyse mensuelle avec revenus, dépenses, remboursements et projection explicite de fin de mois. |
| [DocuIndex](projects/docuindex/README.md) | Recherche et traitement du texte | Recherche BM25 sur index inversé, requêtes ET/OU, expressions exactes et index exportable. |
| [CleanData](projects/cleandata/README.md) | Ingénierie des données | Pipeline à schéma configurable avec typage, normalisation, bornes, déduplication et métriques de qualité. |
| [PulseWatch](projects/pulsewatch/README.md) | Observabilité et réseau | Sondes multi-cibles concurrentes avec reprises bornées, historique des tentatives et agrégats de disponibilité instantanée. |
| [FlowDAG](projects/flowdag/README.md) | Algorithmique et orchestration | Exécution réelle des DAG avec concurrence bornée, reprises et distinction entre tâches échouées et ignorées. |
| [RouteCraft](projects/routecraft/README.md) | Optimisation et logistique | Routage avec sommets bloqués, poids négatifs et détection des cycles négatifs qui influencent la destination. |
| [SensorScope](projects/sensorscope/README.md) | IoT et statistiques | Détection par capteur sur fenêtres historiques, confirmation des alertes et récupération avec hystérésis. |
| [VaultCheck](projects/vaultcheck/README.md) | Intégrité et sauvegardes | Snapshots de contenu persistants, déduplication SHA-256 et restauration vérifiée dans un nouveau dossier. |
| [TaskBoard](projects/taskboard/README.md) | Gestion de projet | Tableau de tâches persistant avec transitions contrôlées, versions optimistes et audit transactionnel. |
| [RoomGuard](projects/roomguard/README.md) | Réservations et concurrence | Réserver une ressource sans chevauchement, annuler et rejouer une réservation de manière idempotente. |
| [LedgerCore](projects/ledgercore/README.md) | Comptabilité et transactions | Journal en partie double avec montants entiers, idempotence, balances et contre-passation. |
| [FlagForge](projects/flagforge/README.md) | Livraison logicielle | Moteur de feature flags déterministes avec règles de ciblage, groupes de déploiement et explications. |
| [GateKeeper](projects/gatekeeper/README.md) | Réseau et contrôle de débit | Limiteur à jetons par client avec horloge injectable, synchronisation et délais de reprise calculés. |
| [EventRail](projects/eventrail/README.md) | Architecture événementielle | Event store SQLite à versions optimistes avec hachage chaîné, rejeu et projection de comptes. |
| [CacheCraft](projects/cachecraft/README.md) | Systèmes et performance | Cache LRU pondéré avec expiration, verrouillage et fusion des chargements concurrents par clé. |
| [JobForge](projects/jobforge/README.md) | Traitement asynchrone | File SQLite avec prise atomique, bail, tentatives bornées, reprise et jetons de possession. |
| [PolicyLab](projects/policylab/README.md) | Sécurité et autorisations | Évaluateur RBAC/ABAC avec héritage de rôles, priorité au refus et trace des décisions. |
| [MatchMaker](projects/matchmaker/README.md) | Optimisation et affectation | Affectation stable candidats/établissements à capacités multiples avec vérification des paires bloquantes. |
| [LearnLab](projects/learnlab/README.md) | Apprentissage automatique | Régression logistique explicable avec séparation stratifiée, standardisation apprise sur entraînement et métriques. |
| [HuffPack](projects/huffpack/README.md) | Compression et formats binaires | Codec Huffman canonique avec en-tête binaire, contrôle de corruption et limites de décompression. |

## Profondeur des projets

Les dix premiers conservent leur CLI initiale et ajoutent `advanced.py` : corrélation multi-règles, transferts atomiques, budget mensuel, index BM25, schémas de validation, sondes concurrentes, exécution DAG, Bellman-Ford, surveillance par capteur et vrais snapshots de sauvegarde.

Les douze suivants séparent `core.py` et `app.py`. Ils incluent entre autres contrôle de concurrence optimiste, exclusion de réservation, comptabilité en partie double, idempotence, cache single-flight, files avec baux, héritage de rôles et compression binaire vérifiée.

Chaque dossier fournit README, DESIGN, scénario JSON, tests et sortie réelle de référence. Les invariants et cas d'échec sont décrits et vérifiés, sans cacher les fonctions manquantes.

## Vérifier l'ensemble

```sh
python3 automation/check_portfolio.py
```

Le contrôle découvre les tests de chaque dossier, refuse une suite vide, exécute les 22 scénarios CLI et conserve les contrôles fonctionnels des dix exemples initiaux. Les tests de concurrence emploient aussi des connexions SQLite indépendantes.

Pour régénérer les résultats du catalogue et les exemples :

```sh
python3 automation/check_portfolio.py --output site/demo-results.json --export-examples
```

Pour un seul projet : suivre son README puis lancer `python3 -m unittest discover -v` dans son dossier.

## Architecture du dépôt

```text
projects/<nom>/   moteur, CLI, scénario, conception, tests, résultat
site/            catalogue statique et interface du laboratoire
                  (les scripts Python restent côté serveur local)
automation/      validation et serveur de démonstration local
docs/            publication, progression et choix des sujets
```

Voir [l'architecture et les limites du laboratoire](docs/LAB.md), [la matrice des fonctions](docs/FEATURE_MATRIX.md), [le guide de publication](docs/PUBLICATION.md) et [le parcours d'apprentissage](docs/LEARNING_PATH.md).

Le serveur personnel, l'agent quotidien et YouTube restent hors de cette étape. Le code peut être public ou privé indépendamment d'une future vitrine ; aucune publication de site n'est effectuée ici.
