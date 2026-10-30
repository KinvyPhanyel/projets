# Matrice des fonctions livrées

| Projet | Fonctions | État |
| --- | --- | --- |
| [Sentinel Log](../projects/sentinel-log/README.md) | Corrélation de trois règles : brute force, password spraying et connexion réussie après échecs ; fenêtres UTC et réseaux de confiance. | Mémoire / scénario |
| [StockPilot](../projects/stockpilot/README.md) | Stock multi-entrepôts avec transferts atomiques, audit et idempotence des opérations. | SQLite via --db |
| [BudgetLens](../projects/budgetlens/README.md) | Analyse mensuelle avec revenus, dépenses, remboursements et projection explicite de fin de mois. | Mémoire / scénario |
| [DocuIndex](../projects/docuindex/README.md) | Recherche BM25 sur index inversé, requêtes ET/OU, expressions exactes et index exportable. | Mémoire / scénario |
| [CleanData](../projects/cleandata/README.md) | Pipeline à schéma configurable avec typage, normalisation, bornes, déduplication et métriques de qualité. | Mémoire / scénario |
| [PulseWatch](../projects/pulsewatch/README.md) | Sondes multi-cibles concurrentes avec reprises bornées, historique des tentatives et agrégats de disponibilité instantanée. | Mémoire / scénario |
| [FlowDAG](../projects/flowdag/README.md) | Exécution réelle des DAG avec concurrence bornée, reprises et distinction entre tâches échouées et ignorées. | Mémoire / scénario |
| [RouteCraft](../projects/routecraft/README.md) | Routage avec sommets bloqués, poids négatifs et détection des cycles négatifs qui influencent la destination. | Mémoire / scénario |
| [SensorScope](../projects/sensorscope/README.md) | Détection par capteur sur fenêtres historiques, confirmation des alertes et récupération avec hystérésis. | Mémoire / scénario |
| [VaultCheck](../projects/vaultcheck/README.md) | Snapshots de contenu persistants, déduplication SHA-256 et restauration vérifiée dans un nouveau dossier. | SQLite via --db |
| [TaskBoard](../projects/taskboard/README.md) | Tableau de tâches persistant avec transitions contrôlées, versions optimistes et audit transactionnel. | SQLite via --db |
| [RoomGuard](../projects/roomguard/README.md) | Réserver une ressource sans chevauchement, annuler et rejouer une réservation de manière idempotente. | SQLite via --db |
| [LedgerCore](../projects/ledgercore/README.md) | Journal en partie double avec montants entiers, idempotence, balances et contre-passation. | SQLite via --db |
| [FlagForge](../projects/flagforge/README.md) | Moteur de feature flags déterministes avec règles de ciblage, groupes de déploiement et explications. | Mémoire / scénario |
| [GateKeeper](../projects/gatekeeper/README.md) | Limiteur à jetons par client avec horloge injectable, synchronisation et délais de reprise calculés. | Mémoire / scénario |
| [EventRail](../projects/eventrail/README.md) | Event store SQLite à versions optimistes avec hachage chaîné, rejeu et projection de comptes. | SQLite via --db |
| [CacheCraft](../projects/cachecraft/README.md) | Cache LRU pondéré avec expiration, verrouillage et fusion des chargements concurrents par clé. | Mémoire / scénario |
| [JobForge](../projects/jobforge/README.md) | File SQLite avec prise atomique, bail, tentatives bornées, reprise et jetons de possession. | SQLite via --db |
| [PolicyLab](../projects/policylab/README.md) | Évaluateur RBAC/ABAC avec héritage de rôles, priorité au refus et trace des décisions. | Mémoire / scénario |
| [MatchMaker](../projects/matchmaker/README.md) | Affectation stable candidats/établissements à capacités multiples avec vérification des paires bloquantes. | Mémoire / scénario |
| [LearnLab](../projects/learnlab/README.md) | Régression logistique explicable avec séparation stratifiée, standardisation apprise sur entraînement et métriques. | Mémoire / scénario |
| [HuffPack](../projects/huffpack/README.md) | Codec Huffman canonique avec en-tête binaire, contrôle de corruption et limites de décompression. | Mémoire / scénario |

Chaque projet possède un scénario JSON modifiable, une sortie de référence, une interface CLI, des tests métier et une conception détaillée. Le laboratoire web orchestre les mêmes CLI ; il ne remplace pas une interface métier dédiée pour chaque domaine.
