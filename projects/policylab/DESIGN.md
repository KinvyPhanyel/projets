# PolicyLab — conception

## Politique d'évaluation

Les rôles héritent des permissions de leurs parents. Un parcours DFS développe cet héritage et refuse les cycles. Les règles utilisent des motifs fnmatch pour action et ressource, plus des conditions de données eq ou in. Aucune expression Python n'est évaluée.

Un refus explicite prévaut sur toute permission. Sans règle applicable autorisant l'action, la décision est default_deny. Un attribut absent fait échouer la condition : il ne vaut pas implicitement null.

## Traçabilité

Le résultat contient les rôles développés et les indices de toutes les règles correspondantes. Cela permet d'expliquer un refus même si une autre règle autorisait l'action.

## Frontière de confiance

Le moteur ne détermine pas les rôles d'un utilisateur. Une application doit les charger depuis une identité authentifiée, construire les attributs côté serveur et contrôler chaque accès à la ressource réelle. Des rôles envoyés librement par un navigateur seraient une faille.

## Scénarios

Un éditeur hérite de read, peut écrire pour la bonne équipe, mais ne peut pas accéder aux secrets même avec une règle allow générale. Les tests couvrent aussi le cycle de rôles et l'absence d'attribut.

## Complexité

O(V+E+R×C) par décision pour l'héritage et les conditions ; une compilation des rôles peut éviter le parcours répété.

## Limites

Moteur de politiques local sans fournisseur d’identité ni middleware HTTP. Les motifs ne normalisent pas des chemins de fichiers : l’application doit fournir des identifiants de ressources canoniques.
