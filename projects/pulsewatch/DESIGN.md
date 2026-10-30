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
