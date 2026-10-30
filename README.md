# Laboratoire de projets · Génie informatique

Dix démonstrateurs autonomes pour explorer la cybersécurité, les données, les transactions et les algorithmes. Chaque dossier contient du code exécutable, une documentation de conception, un exemple et des limites explicites.

**Statut :** premières versions pédagogiques générées avec assistance IA. Ce dépôt ne prétend pas démontrer une expérience professionnelle, des utilisateurs réels ou des performances non mesurées. Comprendre, modifier et approfondir les projets avant de les défendre en entretien.

## Catalogue

| Projet | Domaine | Fonction |
| --- | --- | --- |
| [Sentinel Log](projects/sentinel-log/README.md) | Cybersécurité | Détecter les échecs de connexion répétés dans des journaux JSONL. |
| [StockPilot](projects/stockpilot/README.md) | Gestion et bases de données | Gérer un stock SQLite avec journal de mouvements et prévention des sorties impossibles. |
| [BudgetLens](projects/budgetlens/README.md) | Finance personnelle | Analyser des dépenses CSV avec des montants décimaux exacts et des plafonds par catégorie. |
| [DocuIndex](projects/docuindex/README.md) | Recherche et traitement du texte | Indexer des documents locaux et classer les résultats avec un score TF-IDF. |
| [CleanData](projects/cleandata/README.md) | Ingénierie des données | Valider et dédupliquer un fichier de mesures, en isolant chaque ligne rejetée. |
| [PulseWatch](projects/pulsewatch/README.md) | Observabilité et réseau | Mesurer le statut et la latence d’une URL HTTP avec des délais bornés. |
| [FlowDAG](projects/flowdag/README.md) | Algorithmique et orchestration | Calculer l’ordre d’exécution d’un graphe de tâches et détecter les cycles. |
| [RouteCraft](projects/routecraft/README.md) | Optimisation et logistique | Trouver un chemin de coût minimal avec l’algorithme de Dijkstra. |
| [SensorScope](projects/sensorscope/README.md) | IoT et statistiques | Détecter des anomalies par médiane et écart absolu médian dans une série de capteurs. |
| [VaultCheck](projects/vaultcheck/README.md) | Intégrité et sauvegardes | Créer et vérifier un manifeste SHA-256 de fichiers locaux. |

## Démarrage

Prérequis : Python **3.12+**, Git et un terminal. Aucune bibliothèque externe, aucun compte cloud et aucune clé API ne sont nécessaires.

```sh
cd /workspace/projets
python3 -m http.server 8080 --bind 127.0.0.1 --directory site
```

Le catalogue statique est servi sur le port 8080. Il permet de chercher les projets et de consulter les résultats enregistrés. **Il n’exécute pas les scripts Python dans le navigateur.** Pour manipuler une application, suivre son README depuis son dossier.

Sur votre machine après clonage, remplacer `/workspace/projets` par le chemin du dépôt.

## Vérification fonctionnelle

```sh
python3 automation/check_portfolio.py
```

Ce contrôle exerce les dix projets, notamment un retrait de stock refusé, un graphe cyclique, une détection d’altération et des réponses HTTP 200/503 via un serveur local temporaire. Ce n’est pas une suite exhaustive ni une certification de production. Pour actualiser les résultats du catalogue :

```sh
python3 automation/check_portfolio.py --output site/demo-results.json
```

Les résultats sont déterministes : les relancer sans changement ne produit pas artificiellement de nouvelles données.

## Organisation et publication

Un dépôt contient ici dix dossiers indépendants. Un dossier pourra être extrait en dépôt séparé lorsqu’il aura sa propre interface, des évolutions substantielles et un historique utile.

Voir [le guide de visibilité et démonstration](docs/PUBLICATION.md), [les choix de sujets et leurs sources](docs/PROJECT_SELECTION.md) et [le parcours de progression](docs/LEARNING_PATH.md).

La configuration du serveur, les comptes externes, une automatisation quotidienne et la chaîne YouTube sont reportés à une étape ultérieure. Aucun de ces services n’est activé par ce dépôt.
