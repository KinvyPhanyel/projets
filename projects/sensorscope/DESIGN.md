# Conception — SensorScope

## Choix principal

**Score robuste fondé sur médiane et MAD.** Le centre est la médiane et l’échelle la médiane des écarts absolus. Le score modifié utilise le facteur 0,67448975. Quand le MAD est nul, les valeurs différentes du centre sont signalées par une politique explicite.

## Coût et échelle

O(n log n) avec le calcul des médianes par tri, O(n) de mémoire.

## Manipulation guidée

Remplacer 85 par 21, puis construire une série constante. Comparer le nombre de points signalés.

## Exemple réellement vérifié

La sortie ci-dessous provient du scénario fonctionnel de `automation/check_portfolio.py`. Certains scénarios couvrent des données supplémentaires par rapport à la commande rapide du README.

```json
{
  "median": 21,
  "mad": 1,
  "zero_mad_policy": "flag values different from median",
  "points": [
    {
      "index": 0,
      "value": 20,
      "score": 0.6745,
      "anomaly": false
    },
    {
      "index": 1,
      "value": 21,
      "score": 0.0,
      "anomaly": false
    },
    {
      "index": 2,
      "value": 20,
      "score": 0.6745,
      "anomaly": false
    },
    {
      "index": 3,
      "value": 22,
      "score": 0.6745,
      "anomaly": false
    },
    {
      "index": 4,
      "value": 21,
      "score": 0.0,
      "anomaly": false
    },
    {
      "index": 5,
      "value": 85,
      "score": 43.1673,
      "anomaly": true
    },
    {
      "index": 6,
      "value": 20,
      "score": 0.6745,
      "anomaly": false
    }
  ]
}
```

## Questions à préparer pour une présentation

Seuils métier, saisonnalité, dérive, cas MAD nul et distinction entre anomalie statistique et panne.

## Limites du livrable

Analyse statistique hors ligne, sans modèle entraîné ni validation clinique ou industrielle. Un contexte métier est nécessaire pour qualifier une anomalie.


## Approfondissement implémenté

Chaque mesure est comparée uniquement au passé de son capteur. La phase warmup remplit la référence sans signaler d'anomalie. Ensuite, médiane et MAD d'une fenêtre glissante donnent un score robuste ; min_scale fournit un plancher explicite lorsque la dispersion est presque nulle.

Les points anormaux ne mettent pas à jour la référence, pour éviter qu'une pointe la contamine. confirmation anomalies consécutives ouvrent une alerte ; recovery observations normales la ferment. Cette hystérésis réduit les oscillations d'état. Les dates doivent être strictement croissantes par capteur et inclure un fuseau.

Une dérive durable peut maintenir l'alerte indéfiniment puisque les anomalies sont exclues : un mécanisme de réapprentissage approuvé serait nécessaire. Les tests couvrent ouverture, récupération et isolation entre capteurs. Les états sont en mémoire, sans MQTT ni matériel physique.

Les sections antérieures décrivent le premier `app.py`. Les fonctions de cette section sont livrées dans `advanced.py`.
