# JobForge — conception

## Machine d'états

pending → running → done. Une erreur remet le travail en pending après un délai exponentiel, jusqu'à max_attempts, puis dead. Une prise dont le bail expire est récupérable. Une reprise compte une nouvelle tentative ; un dernier bail expiré devient dead.

## Prise exclusive

BEGIN IMMEDIATE protège récupération des baux et sélection du prochain travail. Chaque prise reçoit un jeton aléatoire. finish exige le jeton courant et un bail encore valide : un ancien travailleur ne peut pas terminer un travail repris par un autre.

## Garanties

Un effet externe peut se produire avant que le travailleur tombe en panne. Le travail sera alors rejoué : la livraison est au moins une fois. Les destinataires doivent accepter une clé idempotente. Il n'y a ni exécution automatique de programmes arbitraires ni promesse exactly-once.

## Rejeu et persistance

L'enqueue d'un identifiant avec la même charge et la même limite est idempotent. Un contenu différent est rejeté. Le temps est fourni explicitement à l'API pour les tests ; un service réel doit employer une source d'heure partagée avec une politique de dérive.

## Limites opérationnelles

Pas de prolongation de bail, priorités ou daemon livré. SQLite convient à un exercice local et à une charge modeste ; il sérialise les producteurs et consommateurs pendant leurs mutations.

## Limites

File locale sans broker ni exécuteur de tâches. Les jetons protègent les clôtures dans la file, mais ne peuvent annuler un effet externe déjà commencé.
