# Conception — CleanData

## Choix principal

**Validation explicite et quarantaine des lignes.** Une ligne valide possède un identifiant non vide, un horodatage ISO et une valeur numérique finie. Un identifiant déjà accepté est rejeté. Les lignes invalides conservent leur numéro et une raison exploitable.

## Coût et échelle

O(n) en temps et mémoire, car résultats et identifiants sont conservés.

## Manipulation guidée

Corriger la date invalide de sample.csv puis comparer les compteurs. Une première occurrence invalide ne réserve pas son identifiant.

## Exemple réellement vérifié

La sortie ci-dessous provient du scénario fonctionnel de `automation/check_portfolio.py`. Certains scénarios couvrent des données supplémentaires par rapport à la commande rapide du README.

```json
{
  "accepted": [
    {
      "id": "a",
      "timestamp": "2026-10-30T10:00:00",
      "value": 21.5
    },
    {
      "id": "c",
      "timestamp": "2026-10-30T12:00:00",
      "value": 23.0
    }
  ],
  "rejected": [
    {
      "line": 3,
      "reason": "identifiant dupliqué",
      "row": {
        "id": "a",
        "timestamp": "2026-10-30T11:00:00",
        "value": "22"
      }
    },
    {
      "line": 4,
      "reason": "Invalid isoformat string: 'invalid'",
      "row": {
        "id": "b",
        "timestamp": "invalid",
        "value": "10"
      }
    }
  ],
  "counts": {
    "accepted": 2,
    "rejected": 2
  }
}
```

## Questions à préparer pour une présentation

Schémas, idempotence d’un lot, stockage des rejets et passage au traitement en flux.

## Limites du livrable

Traitement par lot en mémoire ; la première occurrence valide d’un identifiant est conservée.
