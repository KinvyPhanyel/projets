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


## Approfondissement implémenté

La première version vérifiait des empreintes mais ne sauvegardait rien. Snapshots conserve réellement le contenu binaire dans SQLite. La table blobs déduplique par SHA-256 ; chaque snapshot associe chemins et empreintes dans une transaction. Les snapshots v1 et v2 peuvent partager les blobs inchangés.

read vérifie chaque empreinte avant de rendre les données. restore exige un dossier destination inexistant, refuse les chemins absolus, traversées .. et formes non canoniques, puis crée les fichiers exclusivement. Toutes les empreintes sont vérifiées avant la première écriture de restauration.

La destination et ses parents doivent être contrôlés exclusivement par l'utilisateur local : ce code n'est pas conçu contre un attaquant qui modifie les liens pendant l'opération. Une erreur d'écriture peut laisser une restauration partielle, sans toucher les snapshots. Pas de chiffrement, compression, permissions de fichiers conservées ou collecte directe d'une arborescence dans la CLI JSON. L'API create accepte des octets ; le scénario CLI utilise du texte UTF-8.

Les sections antérieures décrivent le premier `app.py`. Les fonctions de cette section sont livrées dans `advanced.py`.
