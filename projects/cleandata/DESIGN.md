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


## Approfondissement implémenté

Le schéma pilote quatre conversions : texte, nombre fini, entier strict et horodatage ISO. Les règles required, lowercase, min, max et choices sont appliquées avant de considérer une ligne acceptée. Une ligne peut porter plusieurs erreurs : la quarantaine ne s'arrête pas au premier champ invalide.

La clé unique porte sur la valeur normalisée : A entouré d'espaces et a peuvent être identiques avec lowercase. Les clés ne sont mémorisées qu'après validation complète, pour qu'une ligne invalide ne réserve pas un identifiant.

Le rapport sépare taux de validité et nombres d'erreurs par champ. Pour un lot vide, le taux est null, pas un succès à 100 %. Les sorties restent en mémoire : ce module n'est pas encore un pipeline streaming. Un schéma constitue une configuration de confiance et doit être versionné dans une intégration.

Les sections antérieures décrivent le premier `app.py`. Les fonctions de cette section sont livrées dans `advanced.py`.
