# LearnLab — conception

## Modèle et optimisation

La probabilité vaut sigmoid(w·x+b). La sigmoid est calculée avec deux branches pour éviter exp d'un très grand nombre positif. La descente de gradient plein lot minimise l'entropie croisée avec pénalité L2 sur les poids, pas sur le biais.

## Prévention des fuites

La séparation stratifiée utilise une graine locale. Moyennes et écarts-types sont calculés uniquement sur l'entraînement, puis réutilisés à l'identique pour les observations de test. Les colonnes constantes ont une échelle 1.

## Évaluation

Le seuil 0,5 donne matrice de confusion, précision, rappel et accuracy. La log-loss utilise les probabilités avec bornes numériques pour le logarithme. Le fichier sample est volontairement minuscule : ses métriques n'estiment aucune performance métier.

## Reproductibilité

La graine du split et les hyperparamètres sont présents dans le scénario. Le modèle exporte standardisation, poids et biais. Pour une vraie étude, conserver aussi provenance des données, distribution des classes et protocole de validation croisée.

## Limites scientifiques

Le modèle ne capture qu'une frontière linéaire dans les variables standardisées. Il ne gère pas automatiquement valeurs manquantes, variables catégorielles, déséquilibre, dérive ou calibration. Le coût est O(epochs × observations × variables).

## Limites

Données synthétiques ; aucun modèle médical, financier ou d’évaluation des personnes. Pas de dépendance ML, d’accélération ni de revendication de performance réelle.
