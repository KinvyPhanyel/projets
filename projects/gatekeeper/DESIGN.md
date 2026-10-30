# GateKeeper — conception

## Modèle mathématique

Avant chaque décision : tokens = min(capacité, tokens + temps écoulé × débit). Une demande coûte un nombre positif de jetons. Si le solde est insuffisant, aucun jeton n'est consommé et retry_after = (coût − tokens) / débit.

## Concurrence

Un verrou protège lecture d'horloge, recharge et débit : deux threads ne peuvent pas consommer le dernier jeton simultanément. L'horloge par défaut est monotone ; une horloge injectable rend les tests indépendants du temps réel.

## Mémoire bornée

Le nombre de clients est limité. Au plafond, seuls les seaux entièrement rechargés peuvent être supprimés ; supprimer un seau partiellement vide aurait réinitialisé sa capacité et contourné la limite. Si aucune entrée n'est éligible, le nouveau client est refusé avec client_capacity.

## Intégration HTTP envisagée

Traduire rate_limited en HTTP 429 et arrondir retry_after vers le haut pour l'en-tête Retry-After. La sélection de la clé nécessite une identité fiable, pas un en-tête client arbitraire. Le plafond de clients est une protection locale, pas une défense DDoS.

## Complexité

O(1) par demande habituelle ; O(nombre de clients) lors d'une tentative de récupération au plafond.

## Limites

États locaux à un processus et perdus au redémarrage. Plusieurs serveurs nécessitent un état partagé et une opération atomique, par exemple dans Redis.
