# Conception — PulseWatch

## Choix principal

**Sonde HTTP HEAD bornée par un délai.** La sonde accepte HTTP et HTTPS sans identifiants dans l’URL. Les codes 2xx et 3xx sont considérés sains après les redirections suivies par urllib. Les erreurs HTTP, réseau et délais sont rendus dans le résultat.

## Coût et échelle

Une requête par invocation. La durée dépend du serveur et des redirections ; le délai urllib n’est pas un budget global strict.

## Manipulation guidée

Lancer le catalogue local et sonder sa racine, puis demander un fichier absent : la seconde sonde doit sortir avec un code non nul.

## Exemple réellement vérifié

La sortie ci-dessous provient du scénario fonctionnel de `automation/check_portfolio.py`. Certains scénarios couvrent des données supplémentaires par rapport à la commande rapide du README.

```json
{
  "healthy_status": 200,
  "unhealthy_status": 503,
  "both_cases_checked": true
}
```

## Questions à préparer pour une présentation

SLO, disponibilité, refus HEAD, politique de redirection, SSRF et distinction entre un service joignable et fonctionnel.

## Limites du livrable

À utiliser sur des services autorisés. CLI locale, pas une API publique : n’exposez pas une sonde acceptant des URL arbitraires sans protection SSRF. Certains serveurs refusent HEAD.


## Approfondissement implémenté

Un ThreadPoolExecutor borne le nombre de sondes simultanées. Chaque cible possède un historique de tentatives et un backoff exponentiel limité à cinq essais. La réussite arrête ses tentatives ; les autres cibles continuent indépendamment. L'ordre des résultats suit celui des entrées.

L'agrégat décrit une observation instantanée : proportion de cibles saines et p95 par rang le plus proche des latences finales. Ce n'est pas un SLO temporel ; deux cibles ne suffisent pas pour une statistique représentative. Les tests injectent une sonde contrôlée sans dépendre d'Internet et testent une récupération à la seconde tentative.

Le scénario avancé attend le serveur de catalogue sur le port 8080 ; une cible volontairement absente illustre l'erreur. Les contrôles réseau restent locaux au développement. Pas d'API publique acceptant des URL, de planificateur périodique ou de stockage des séries temporelles.

Les sections antérieures décrivent le premier `app.py`. Les fonctions de cette section sont livrées dans `advanced.py`.
