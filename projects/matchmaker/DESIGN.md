# MatchMaker — conception

## Problème

Chaque candidat classe les établissements acceptables ; chaque établissement classe les candidats acceptables et possède une capacité. Les préférences sont strictes, sans égalités. Un couple n'est acceptable que si les deux côtés l'ont classé.

## Admission différée

Les candidats proposent dans leur ordre de préférence. Un établissement conserve les meilleurs candidats dans sa capacité et libère le moins bien classé. Un candidat ne propose jamais deux fois au même établissement ; le nombre de propositions est donc borné par le nombre de préférences.

## Vérificateur indépendant

blocking examine chaque établissement que le candidat préfère à son affectation. Une paire bloque si l'établissement a une place disponible ou préfère le candidat à un admis. Le vérificateur contrôle aussi les capacités et l'acceptabilité des affectations fournies.

## Garanties et compromis

Sous ces hypothèses, l'admission différée produit une affectation stable et favorable aux candidats parmi les affectations stables. Elle ne maximise pas nécessairement une somme de scores, ni une notion d'équité entre groupes.

## Coûts

Au plus E propositions. Cette implémentation trie la liste d'admis à chaque proposition, soit un facteur lié à la capacité. Un tas améliorerait les grandes capacités.

## Limites

Préférences synthétiques et strictes. Pas de gestion des couples, contraintes géographiques, quotas de diversité ou protection contre des déclarations stratégiques.
