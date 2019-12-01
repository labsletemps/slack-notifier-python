# Slack notifier – python

Alertes pour éditeurs Web / community managers basées sur des flux RSS ou API.

Fonctions du script:
* (ok) charger un flux RSS, retourner les articles publiés dans un intervalle de x minutes
* (ok) identifier la rubrique / les tags de chaque entrée
* (ok) pour les dernières entrées: charger les données de l’article via une API
  * préciser si l’article est réservé aux abonnés
  * évt. autres précisions
* filter les articles à slacker (critères: p. ex. payant, rubrique)
* boucle: publier chaque article sur Slack
