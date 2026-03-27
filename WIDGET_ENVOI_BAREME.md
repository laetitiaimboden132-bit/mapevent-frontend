# Bareme d'envoi widget (obligatoire)

Ce bareme sert a decider si une ville est assez "remplie" pour recevoir la campagne widget.

## Regle de base (reference Paris / Geneve)

- Reference 1: `Paris`
- Reference 2: `Geneve`
- On calcule le taux `events_par_habitant` pour chaque reference:
  - `taux_paris = events_paris / population_paris`
  - `taux_geneve = events_geneve / population_geneve`
- On retient le taux le plus bas (plus juste): `taux_base = min(taux_paris, taux_geneve)`
- Tolerance autorisee: `-20%`
  - `taux_min_envoi = taux_base * 0.8`

## Critere d'envoi

Pour une ville donnee:

- `events_requis = ceil(population_ville * taux_min_envoi)`
- La ville est eligibile si `events_ville >= events_requis`

## Politique d'execution

- Toujours verifier ce bareme avant envoi.
- Ne pas envoyer si la population est inconnue (tant que non renseignee).
- Ne pas envoyer si `events_ville < events_requis`.
- Envoi autorise uniquement si le seuil est atteint.

## Implementation projet

- Script d'analyse: `frontend/analyse_map_widget_policy.py`
- Rapport json genere: `frontend/widget_send_eligibility_report.json`

Ce fichier est la reference de validation avant chaque campagne widget.
