# Slack notifier – python

Alertes pour éditeurs Web / community managers basées sur des flux RSS ou API.

Fonctions du script:
* [x] chaque 10-15 min: charger un flux RSS, retourner les nouveaux articles publiés
* [x] identifier la rubrique / les tags de chaque entrée
* [x]  pour les dernières entrées: charger les données de l’article via une API
  * [x] préciser si l’article est réservé aux abonnés
  * [x] évt. autres précisions > heure, rubrique
* [x] filter les articles à slacker (critères: p. ex. payant, rubrique)
* [x] boucle: publier chaque article sur Slack
