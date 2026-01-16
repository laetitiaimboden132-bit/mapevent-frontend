# ✅ Finaliser CORS pour `/api/user/oauth/google/complete`

## ✅ Ce qui a été fait automatiquement

1. ✅ **Méthode OPTIONS créée** et configurée avec Mock Integration
2. ✅ **Headers CORS ajoutés à OPTIONS** (preflight)
3. ✅ **API déployée** sur le stage `default`

## ⚠️ Ce qui reste à faire manuellement (2 minutes)

### Ajouter les headers CORS à POST

1. **Allez dans AWS Console** → **API Gateway**
2. **Sélectionnez votre API** : `mapevent-backend-API`
3. **Naviguez** : Resources → `/api` → `/user` → `/oauth` → `/google` → `/complete`
4. **Cliquez sur POST** (la méthode, pas la ressource)
5. **Cliquez sur "Integration Response"** (dans le panneau de gauche)
6. **Cliquez sur "200"** (le status code)
7. **Dans "Header Mappings"**, ajoutez :

   | Name | Mapped from |
   |------|-------------|
   | `Access-Control-Allow-Origin` | `'*'` |
   | `Access-Control-Allow-Headers` | `'Content-Type,Authorization,Origin,X-Requested-With,Accept'` |
   | `Access-Control-Allow-Methods` | `'POST,OPTIONS'` |

8. **Cliquez sur "Save"**

### Ajouter les headers dans Method Response aussi

1. **Toujours sur POST**, cliquez sur **"Method Response"**
2. **Cliquez sur "200"**
3. **Dans "Response Headers"**, ajoutez :
   - `Access-Control-Allow-Origin` (type: String)
   - `Access-Control-Allow-Headers` (type: String)
   - `Access-Control-Allow-Methods` (type: String)
4. **Cliquez sur "Save"**

### Déployer l'API

1. **En haut de la page**, cliquez sur **"Actions"**
2. **Sélectionnez "Deploy API"**
3. **Deployment stage** : `default`
4. **Description** : "CORS headers for POST /api/user/oauth/google/complete"
5. **Cliquez sur "Deploy"**

## ✅ Vérification

Après le déploiement, testez le formulaire sur https://mapevent.world

Le formulaire devrait maintenant pouvoir créer le compte sans erreur CORS !

## 🔍 Si ça ne fonctionne toujours pas

Vérifiez dans la console du navigateur (F12) :
- L'erreur CORS devrait disparaître
- La requête POST devrait retourner 200 avec les données utilisateur









