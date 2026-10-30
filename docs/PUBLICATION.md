# Montrer les projets

## Ce qu’un visiteur peut faire

Un dépôt public expose les fichiers et leur historique. Le README explique l’objectif, le lancement et les limites. GitHub affiche le code mais n’exécute pas automatiquement une application serveur.

Le dossier `site/` est un catalogue statique : il montre des descriptions et des sorties de démonstration enregistrées. Il peut être hébergé séparément du code. GitHub Pages convient à ces fichiers statiques ; il ne peut pas exécuter les applications Python. Sa disponibilité pour un dépôt privé dépend du plan GitHub.

Les 22 projets proposent une CLI et un laboratoire local avec scénarios JSON modifiables (`automation/serve_lab.py`). Ce serveur exécute les moteurs Python pour afficher leur résultat. Il reste réservé au développement local ; le publier demande une architecture adaptée, détaillée dans [LAB.md](LAB.md). Les applications ne possèdent pas encore chacune une interface métier graphique dédiée.

## Code privé, vitrine publique

Dans un dépôt privé, les visiteurs non autorisés ne voient pas le code ni son README. Pour montrer les noms et descriptions sans le code, publier uniquement `site/` sur un hébergement public, ou dans un dépôt de vitrine séparé. Les sorties enregistrées dans ce dossier doivent rester des données fictives.

## Présentation recommandée

Pour chaque projet approfondi : problème concret, capture ou courte vidéo, commande reproductible, décisions techniques, limites et démonstration d’un cas d’échec. Ajouter un lien public seulement après avoir réellement déployé et vérifié le service. Épingler les projets que vous savez expliquer sur votre profil.

## Contributions GitHub

Le calendrier dépend des règles GitHub : les commits doivent notamment être associés à une adresse e-mail liée au compte et être sur une branche éligible, généralement la branche par défaut ou `gh-pages`. Un simple push n’assure pas une case verte. Le profil peut afficher un décompte de contributions privées sans révéler leur contenu si cette option est activée.

Aucun commit antidaté, vide ou planificateur de push n’est inclus. Le serveur et l’automatisation seront traités séparément.
