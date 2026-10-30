# Conception — VaultCheck

## Choix principal

**Manifeste de contenu SHA-256.** Chaque fichier ordinaire est lu par blocs de 64 Kio. Le manifeste associe chemin relatif et empreinte. La vérification distingue fichiers ajoutés, absents et modifiés. Le manifeste est créé hors du dossier analysé.

## Coût et échelle

O(total des octets), mémoire O(nombre de fichiers) et un bloc par lecture.

## Manipulation guidée

Créer le manifeste, modifier note.txt et vérifier : changed doit contenir note.txt et le processus doit sortir avec le code 1.

## Exemple réellement vérifié

La sortie ci-dessous provient du scénario fonctionnel de `automation/check_portfolio.py`. Certains scénarios couvrent des données supplémentaires par rapport à la commande rapide du README.

```json
{
  "algorithm": "SHA-256",
  "modification_detected": true
}
```

## Questions à préparer pour une présentation

Intégrité contre authenticité, manifeste signé, liens symboliques, fichiers modifiés pendant la lecture et restauration effective.

## Limites du livrable

SHA-256 détecte les modifications mais ne chiffre et ne signe pas les fichiers. Conserver le manifeste en lieu sûr. Les liens symboliques sont ignorés ; fichiers supposés stables pendant la lecture.
