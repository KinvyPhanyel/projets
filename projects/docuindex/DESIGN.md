# Conception — DocuIndex

## Choix principal

**Index lexical en mémoire et score TF-IDF simplifié.** Les documents .txt sont tokenisés en minuscules. Le score cumule fréquence relative et inverse de fréquence documentaire lissée pour les mots de la requête. Les égalités sont départagées par nom de fichier.

## Coût et échelle

Cette version recalcule les fréquences documentaires à la recherche ; coût approximatif O(D×Q×D) dans la boucle de classement, à optimiser avec un index inversé.

## Manipulation guidée

Ajouter un document contenant sécurité et relancer la recherche. Chercher un mot absent pour obtenir une liste vide.

## Exemple réellement vérifié

La sortie ci-dessous provient du scénario fonctionnel de `automation/check_portfolio.py`. Certains scénarios couvrent des données supplémentaires par rapport à la commande rapide du README.

```json
[
  {
    "document": "security.txt",
    "score": 0.156163
  }
]
```

## Questions à préparer pour une présentation

Accents, synonymes, longueur des documents, classement lexical et différence avec la recherche vectorielle.

## Limites du livrable

Recherche lexicale explicable, sans LLM, embeddings ou compréhension sémantique. Charge les documents en mémoire.
