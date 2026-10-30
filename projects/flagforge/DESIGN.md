# FlagForge — conception

## Ordre des décisions

Flag absent → false. Interrupteur global désactivé → false. Ensuite, première règle correspondante. Enfin, appartenance au déploiement progressif ; hors déploiement, valeur default (false par défaut). Une règle explicite prévaut donc sur le pourcentage.

## Cohortes stables

Le hachage SHA-256 utilise nom du flag, sel et identifiant du sujet, séparés par un octet nul. Les 64 premiers bits donnent un compartiment parmi 10 000. Augmenter le pourcentage conserve les sujets déjà dans la cohorte. Changer le sel la redistribue.

## Explicabilité

Chaque résultat indique reason, et selon le cas numéro de règle ou bucket. Les types incompatibles dans une comparaison ne correspondent pas. Un attribut absent n'est pas implicitement égal à null.

## Expérimentation

Définir un flag à 0 %, 100 %, puis comparer la même personne entre deux évaluations. Vérifier qu'un ciblage beta passe même à 0 %. Le hachage ne constitue ni une randomisation clinique ni une garantie cryptographique de confidentialité des identifiants.

## Évolution

Ajouter versions de configuration, signatures des règles, métriques d'exposition et allocation de variantes pour de vrais tests A/B.

## Limites

Moteur local sans console d’administration ni synchronisation. Les règles doivent provenir d’une configuration de confiance ; les feature flags ne remplacent jamais un contrôle d’accès.
