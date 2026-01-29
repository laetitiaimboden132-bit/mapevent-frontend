# 🔍 Analyser CloudWatch pour comprendre « je n’ai pas pu me connecter »

## Où regarder

- **Log group** : `/aws/lambda/mapevent-backend`
- **Région** : `eu-west-1`
- **Fonction** : `mapevent-backend` (Lambda appelée par le front via l’API)

---

## Ce que le backend log quand vous vous connectez

Lors d’une connexion (Google ou email/mdp), le backend enregistre notamment :

| Étape | Message à chercher dans les logs |
|-------|-----------------------------------|
| Démarrage Lambda | `INIT_START` ou `START RequestId` |
| Connexion base RDS | `Connexion RDS reussie` ou `Tentative de connexion à RDS` |
| Échec base | `Erreur connexion DB` ou `Connexion DB échouée` |
| OAuth Google | Requête vers `/api/user/oauth/google` ou `/api/user/oauth/google/complete` |
| Profil utilisateur | `/api/user/me` (reconnexion auto, token JWT) |
| Erreurs Python | `ERROR`, `Traceback`, `Exception` |
| Redis (rate limit, etc.) | `Erreur connexion Redis` ou `Redis non disponible` |

---

## Procédure rapide (console AWS)

1. **Ouvrir CloudWatch**
   - AWS Console → rechercher **CloudWatch** → **Logs** → **Log groups**.

2. **Ouvrir les logs de la Lambda**
   - Cliquer sur **`/aws/lambda/mapevent-backend`**.
   - Choisir le **Log stream** le plus récent (date/heure la plus haute).

3. **Filtrer sur la connexion**
   - Dans la zone de recherche/filtre des logs, tester :
     - `Connexion RDS`
     - `Erreur connexion`
     - `oauth`
     - `user/me`
     - `ERROR`
     - `Traceback`
     - `502`
     - `CORS`

4. **Choisir la bonne plage de temps**
   - Sélecteur en haut : **Last 15 minutes** ou **Last 1 hour** (ou **Custom range** autour de l’heure où vous avez essayé de vous connecter).
   - Puis **Refresh** pour mettre à jour.

---

## Avec le script PowerShell (depuis le projet)

Depuis la racine du projet :

```powershell
# Dernières 15 minutes, tous les logs
.\voir-logs-lambda-final.ps1 -Minutes 15

# Ou avec le script qui accepte un filtre (voir-logs-lambda.ps1)
.\voir-logs-lambda.ps1 -Minutes 15 -Filter "oauth|Connexion|ERROR|Traceback|user/me|Erreur"
```

Les logs sont aussi écrits en UTF-8 dans un fichier temporaire (voir le chemin affiché à la fin).

---

## Causes fréquentes de « pas pu me connecter »

| Cause | Où ça apparaît (CloudWatch / front) |
|-------|-------------------------------------|
| **Lambda pas invoquée** | Aucun `START RequestId` à l’heure du test → vérifier URL de l’API, CORS, ou erreur réseau côté front. |
| **Base RDS injoignable** | `Erreur connexion DB` ou `Connexion DB échouée` → RDS, sécurité réseau (SG / VPC), timeout. |
| **Redis indisponible** | `Erreur connexion Redis` ou `Redis non disponible` → souvent rate-limit/optionnel, pas toujours bloquant pour la connexion. |
| **Erreur dans la route OAuth / user/me** | `Traceback`, `ERROR`, ou message d’exception dans les lignes juste après une requête vers `oauth` ou `user/me`. |
| **502 Bad Gateway** | Souvent timeout ou crash de la Lambda avant de renvoyer une réponse → regarder les lignes juste avant la fin du stream. |
| **CORS / 403** | Requête bloquée avant la Lambda ou renvoyée en 403 → peu ou pas de log backend pour cette requête ; vérifier en revanche les requêtes « préflight » ou les réponses 4xx dans le navigateur (onglet Network). |

---

## Checklist à l’heure où vous avez essayé de vous connecter

- [ ] Il y a bien des lignes de log à ce moment-là (sinon la Lambda n’a pas été appelée).
- [ ] Vous voyez `Connexion RDS reussie` (sinon, problème base).
- [ ] Pour une connexion Google : une requête vers `oauth/google` ou `oauth/google/complete` et pas d’`ERROR` / `Traceback` juste après.
- [ ] Pour « rester connecté » / reconnexion : une requête vers `/api/user/me` et pas d’`ERROR` / `Traceback` juste après.

Si vous collez ici (ou dans un fichier) les **extraits de logs** autour de l’heure du test (avec les lignes contenant `Connexion`, `Erreur`, `oauth`, `user/me`, `ERROR`, `Traceback`), on pourra cibler la cause exacte.

---

## Si le script PowerShell échoue (proxy / AWS CLI)

Lors d’un test, la commande `aws logs tail` a échoué avec :
`Failed to connect to proxy URL: "http://127.0.0.1:9"`.

Dans ce cas :
1. **Désactiver le proxy** pour AWS si vous n’en utilisez pas :  
   `$env:HTTP_PROXY=''; $env:HTTPS_PROXY=''` puis relancer `.\voir-logs-connexion.ps1 -Minutes 30`
2. **Ou utiliser la console AWS** : CloudWatch → Log groups → `/aws/lambda/mapevent-backend` → dernier stream → filtrer avec les mots-clés ci-dessus.
