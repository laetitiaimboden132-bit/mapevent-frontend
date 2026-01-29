# CORS : configuration côté AWS

Le handler Python (`handler.py`) ajoute les en-têtes CORS sur **chaque** réponse.
Si la console AWS exige de remplir la section CORS de la Function URL, utilisez **exactement** les valeurs ci-dessous (les mêmes que dans le code).

## Dans la console AWS

1. **Lambda** → fonction `mapevent-backend`
2. **Configuration** → **Function URL** → **Modifier** / **Configure**
3. Section **CORS** – si des champs sont obligatoires, remplir :

| Champ (label possible) | Valeur à mettre |
|------------------------|------------------|
| **Allow origin** / Origine(s) | `https://mapevent.world` |
| **Allow methods** / Méthodes | `*` (toutes) ou `GET, POST, PUT, DELETE, OPTIONS` |
| **Allow headers** / En-têtes | `Content-Type, Authorization, Origin, X-Requested-With, Accept` |
| **Max age** (si demandé) | `3600` ou valeur par défaut |

- Origine : `https://mapevent.world` (une seule).
- Méthodes : `*` ou la liste explicite.
- Headers : `Content-Type, Authorization, Origin, X-Requested-With, Accept` (le code côté Lambda utilise la même liste).

## Ce que le code envoie déjà

Sur chaque réponse, le handler ajoute :

- `Access-Control-Allow-Origin: https://mapevent.world`
- `Access-Control-Allow-Credentials: true`
- `Access-Control-Allow-Headers: Content-Type, Authorization, Origin, X-Requested-With, Accept`
- `Access-Control-Allow-Methods: GET,POST,PUT,DELETE,OPTIONS`

Les requêtes **OPTIONS** (préflight) renvoient `200` avec ces en-têtes et un body vide.

## Si l’interface AWS est différente

Si les libellés ou le format des champs ne correspondent pas (ex. liste à cocher, champs séparés), envoyez une capture d’écran de la section CORS pour adapter les valeurs au formulaire affiché.
