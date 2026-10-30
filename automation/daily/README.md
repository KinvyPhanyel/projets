# Maintenance quotidienne du portfolio

Tâche planifiée sans API IA ni processus permanent. Elle exécute les vérifications réelles des 22 projets et publie un rapport de maintenance explicitement automatisé. Elle ne développe pas des fonctionnalités toute seule, ne crée pas de commits vides et ne fait pas varier un compteur pour simuler une contribution.

## Comportement

1. Verrouiller le dossier d'état pour empêcher deux exécutions simultanées.
2. Vérifier que le clone dédié est propre et sur la branche configurée.
3. Récupérer la branche distante et avancer uniquement en fast-forward.
4. Si une publication précédente a échoué, publier ses commits de rapports reconnus avant toute nouvelle exécution. Une divergence arrête la tâche sans reset, rebase ou force-push.
5. S'il existe déjà un rapport réussi du jour pour cette révision du code, ne pas relancer les tests ni créer de commit.
6. Exécuter les tests et scénarios, avec un délai maximal de cinq minutes ; une expiration interrompt aussi les sous-processus de vérification.
7. Écrire `maintenance/daily/AAAA-MM-JJ.json` : jour réel à Douala, révision du code vérifié, statut, nombres de contrôles réussis et empreinte du résultat complet. En cas d'échec, ne pas prétendre que les projets passent.
8. Conserver 90 jours, committer uniquement les rapports, puis pousser sur `portfolio-projets`.

Les détails de vérification restent dans `runtime/last-check.log` sur le serveur. Les erreurs de Git et les identifiants d'accès ne sont pas incorporés au rapport publié. Les états Git contradictoires exigent une intervention ; aucune modification utilisateur n'est effacée.

## Horaire et ressources

Le timer système lance la tâche à **19 h, heure de Douala (UTC+1)**, avec jusqu'à 15 minutes de décalage aléatoire. `Persistent=true` permet un rattrapage au redémarrage ; les jours où le serveur était arrêté ne sont pas antidatés.

| Paramètre | Réglage |
| --- | --- |
| Exécution entre deux passages | Aucun processus de l'agent |
| CPU | Quota de 25 % d'un cœur |
| Mémoire maximale du service | 256 Mio |
| Priorité CPU | Nice 15 |
| Durée maximale du service | 8 minutes |
| Reprises d'erreur d'infrastructure | Toutes les 15 minutes, au plus 4 départs sur 6 h |
| Échec des tests | Rapport failed, code 20 ; pas de boucle automatique sur ce défaut |
| Journaux | systemd journal + dernier log de vérification local |

Une erreur de push laisse le commit local pour la prochaine tentative. Un échec de test déjà publié ne doit pas déclencher des commits répétés : l'identité du rapport reste stable. Une relance manuelle est possible après correction. Les limites systemd sont fournies et vérifiées syntaxiquement ; la consommation sur votre serveur doit être observée lors du premier lancement.

## Prérequis du serveur

- Ubuntu/Debian avec Python **3.12+**, Git, systemd et sudo pour installer les unités.
- Un utilisateur de service non root, propriétaire de son dossier personnel.
- Authentification GitHub **non interactive**, avec lecture et écriture sur `KinvyPhanyel/projets`, déjà configurée pour cet utilisateur. Une clé de déploiement limitée à ce dépôt convient ; ne pas réutiliser un token GitLab. Ne pas mettre le secret dans une URL Git, le JSON, un argument ou ce dépôt.
- Si SSH est utilisé pour GitHub, clé d'hôte vérifiée et clé privée accessible au compte de service sans dépendre d'un agent de terminal temporaire. Le service ne désactive pas la vérification d'hôte.
- Une adresse d'auteur liée au compte GitHub. Le programme n'est pas en mesure de confirmer l'association de cette adresse au compte.

Le script de connexion au VPS n'est pas inclus. Le document de connexion fourni concerne aussi une autre application : ses commandes de migration et de redémarrage ne sont pas utilisées ici.

## Installation

Sur le serveur, depuis le dépôt contenant cette version :

```sh
sudo python3 automation/daily/install.py \
  --user "$(id -un)" \
  --author-name 'KinvyPhanyel' \
  --author-email 'VOTRE_ADRESSE_GIT_VERIFIEE'
```

Si l'authentification GitHub du serveur utilise une clé SSH, ajouter :

```sh
--git-url 'git@github.com:KinvyPhanyel/projets.git'
```

L'installeur crée un **clone dédié**, distinct des applications existantes, dans `~/.local/state/portfolio-agent/repository`. Il vérifie un push à blanc, écrit la configuration privée dans `~/.config/portfolio-agent/config.json`, installe les deux unités système puis effectue un premier lancement réel. Le timer n'est activé que si ce lancement réussit. Une configuration existante différente est conservée et signalée. Les unités remplacées sont sauvegardées avec un suffixe `.backup-...`.

Le programme se met à jour au lancement lorsque la branche distante avance. Une modification des unités ou de la configuration requiert de relancer l'installation ; la mise à jour du code seule ne modifie pas systemd.

## Vérification et arrêt

```sh
systemctl list-timers portfolio-maintenance.timer
systemctl status portfolio-maintenance.service
journalctl -u portfolio-maintenance.service -n 60 --no-pager
sudo systemctl start portfolio-maintenance.service
```

Pour arrêter la récurrence, puis une éventuelle exécution courante :

```sh
sudo systemctl disable --now portfolio-maintenance.timer
sudo systemctl stop portfolio-maintenance.service
```

Le clone, les rapports et la configuration restent présents. Aucune base de données, configuration nginx ou application PM2 existante n'est touchée.

## Mode de validation hors réseau

Créer un clone de test dédié et un JSON basé sur `config.example.json`, puis :

```sh
python3 automation/daily/agent.py --config /chemin/config.json --offline
```

Ce mode exécute les contrôles et crée un commit local de rapport, mais n'effectue ni fetch ni push. Ne pas l'utiliser dans un checkout contenant du travail non committé. Les tests de l'agent utilisent des dépôts temporaires et des remotes locaux :

```sh
python3 -m unittest discover -s automation/daily -p 'test_*.py' -v
```

Ils couvrent idempotence du jour, erreurs réelles, rattrapage d'un push, historique divergent, fichiers utilisateur, rétention, verrou, sortie invalide et expiration du contrôle.

## Calendrier GitHub

Un push sans nouveau commit ne crée pas de contribution. Les commits vides sont identifiables dans l'historique. Les rapports de cet agent restent clairement des rapports d'automatisation.

Les commits sur `portfolio-projets` ne sont pas garantis de compter dans le calendrier : les règles GitHub demandent notamment une branche éligible (généralement la branche par défaut) et une adresse associée au compte. Aucune fusion dans `main`, modification de branche par défaut, antidatation ou garantie de case verte n'est effectuée par cet agent. Une intégration des projets dans la branche principale doit être décidée séparément.
