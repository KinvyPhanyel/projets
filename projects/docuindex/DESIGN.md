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


## Approfondissement implémenté

L'index inversé associe un terme aux documents et fréquences. La recherche ne reparcourt donc pas tous les documents pour calculer chaque fréquence documentaire. Le score BM25 utilise k1=1,2 et b=0,75 ; il normalise la longueur sans diviser linéairement la pertinence comme la première version.

Les termes ordinaires utilisent ET ou OU. Les groupes entre guillemets ajoutent un filtre de présence contiguë après tokenisation. L'extrait est un préfixe de 160 caractères, pas un surlignage contextuel. Les égalités sont départagées par identifiant.

L'export JSON versionné conserve les documents et reconstruit l'index à la restauration, afin de ne pas maintenir deux représentations pouvant diverger. Il contient donc le texte en clair. Les tests couvrent expression exacte, absence, mode ET et round-trip. Pas de stemming, analyse linguistique ou mise à jour incrémentale.

Les sections antérieures décrivent le premier `app.py`. Les fonctions de cette section sont livrées dans `advanced.py`.
