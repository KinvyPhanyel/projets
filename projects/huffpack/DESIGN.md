# HuffPack — conception

## Construction et codes canoniques

Un tas fusionne les deux fréquences les plus basses jusqu'à l'arbre Huffman. Une règle de départage stable rend la compression reproductible. Seules les longueurs sont stockées : les codes canoniques sont reconstruits par ordre (longueur, symbole).

## Format binaire HFP1

L'en-tête big-endian contient magic (4 octets), taille originale (8), nombre de bits utiles (8), SHA-256 original (32), nombre de symboles (2), puis couples symbole/longueur et flux de bits. Le dernier octet est complété à zéro. Le décodeur exige la taille exacte et rejette les octets supplémentaires.

## Décompression défensive

Le décodeur borne la sortie annoncée, refuse les tables sursouscrites, symboles dupliqués, codes inconnus, padding non nul et flux tronqués. Il vérifie taille décodée et empreinte. Les tests couvrent octets arbitraires, entrée vide, alphabet unique et corruption.

## Compromis

Un petit fichier peut grossir à cause de l'en-tête. Ce codec enseigne la compression entropique ; il n'égale pas les codecs combinant dictionnaires et codage entropique. L'empreinte détecte la corruption, pas un attaquant pouvant réécrire tout le fichier.

## Coûts

Construction O(n + A log A), où A ≤ 256. Les données et le résultat sont en mémoire ; pas de mode streaming ou de format standard interopérable.

## Limites

Format expérimental local, sans chiffrement. Le décodeur borne la sortie mais attend que le fichier compressé ait déjà été chargé en mémoire ; prévoir aussi une limite d’entrée dans une API.
