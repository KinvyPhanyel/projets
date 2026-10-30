# CacheCraft — conception

## Éviction et expiration

OrderedDict maintient l'ordre LRU → MRU. Une lecture réussie rend la clé récente sans prolonger son TTL. L'expiration est paresseuse et supprime toutes les entrées expirées à la prochaine opération. Le budget est une somme de poids explicitement fournis, pas une mesure des octets Python.

## Single-flight

Le premier demandeur d'une clé crée un Future et charge la valeur hors du verrou. Les suivants attendent ce même résultat. Une exception est propagée à tous les demandeurs ; le vol est retiré pour permettre une tentative future. Deux clés différentes peuvent être chargées en parallèle.

## Compromis

Une écriture explicite pendant un chargement peut être remplacée par le résultat du chargeur : aucune cohérence forte avec une source externe n'est promise. Un chargeur ne doit pas rappeler récursivement get_or_load sur la même clé ; il s'attendrait lui-même.

## Mesures

hits compte les lectures servies par le cache, misses toutes les demandes non servies immédiatement et loads les chargeurs effectivement invoqués. L'expiration complète coûte O(n), contrairement aux caches utilisant une seconde structure de priorité.

## Tests de concurrence

Utiliser un chargeur bloqué par un Event, lancer plusieurs lecteurs, puis libérer le chargeur. Une seule invocation doit avoir lieu, sans attendre de délai arbitraire.

## Limites

Cache local non distribué, sans invalidation externe ni taille mémoire mesurée. Les valeurs retournées peuvent être mutables ; le client doit gérer ce partage.
