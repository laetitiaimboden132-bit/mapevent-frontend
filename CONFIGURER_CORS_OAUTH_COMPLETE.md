# 🔧 Configurer CORS pour `/api/user/oauth/google/complete`

## ❌ Problème Actuel
L'endpoint `/api/user/oauth/google/complete` renvoie une erreur 403 sur les requêtes OPTIONS (preflight CORS).

## ✅ Solution : Configurer CORS dans API Gateway

### Étape 1 : Accéder à l'endpoint dans API Gateway

1. Allez dans **AWS Console** → **API Gateway**
2. Sélectionnez votre API
3. Naviguez vers **Resources** → `/api` → `/user` → `/oauth` → `/google` → `/complete`
4. Cliquez sur `/complete`

### Étape 2 : Activer CORS pour la méthode POST

1. **Sélectionnez la méthode POST** (si elle existe)
2. Cliquez sur **Actions** → **Enable CORS**
3. Configurez :
   - **Access-Control-Allow-Origin** : `https://mapevent.world`
   - **Access-Control-Allow-Headers** : `Content-Type, Authorization, Origin, X-Requested-With, Accept`
   - **Access-Control-Allow-Methods** : `POST, OPTIONS`
4. Cliquez sur **Enable CORS and replace existing CORS headers**

### Étape 3 : Créer la méthode OPTIONS (CRITIQUE)

**⚠️ IMPORTANT :** La méthode OPTIONS est nécessaire pour CORS !

1. **Cliquez sur `/complete`** (la ressource, pas la méthode POST)
2. **Actions** → **Create Method**
3. **Sélectionnez OPTIONS**
4. **Cliquez sur la coche ✓**
5. **Integration type** : `Mock`
6. **Cliquez sur "Save"**

### Étape 4 : Configurer la réponse OPTIONS

#### Method Response :
1. Cliquez sur **Method Response**
2. **HTTP Status** : `200`
3. **Headers** :
   - `Access-Control-Allow-Origin`
   - `Access-Control-Allow-Headers`
   - `Access-Control-Allow-Methods`

#### Integration Response :
1. Cliquez sur **Integration Response**
2. **Header Mappings** :
   - `Access-Control-Allow-Origin` → `'https://mapevent.world'`
   - `Access-Control-Allow-Headers` → `'Content-Type, Authorization, Origin, X-Requested-With, Accept'`
   - `Access-Control-Allow-Methods` → `'POST, OPTIONS'`

#### Mock Integration Response :
1. Cliquez sur **Integration** → **Integration Response**
2. **HTTP Status** : `200`
3. **Response Body** : (vide ou `{}`)

### Étape 5 : Déployer l'API

1. **Actions** → **Deploy API**
2. Sélectionnez votre **Deployment stage** (probablement `default`)
3. **Cliquez sur "Deploy"**

## ✅ Vérification

Après le déploiement, testez avec :
```bash
curl -X OPTIONS https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/user/oauth/google/complete \
  -H "Origin: https://mapevent.world" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v
```

Vous devriez recevoir :
- **Status Code** : `200`
- **Headers** :
  - `Access-Control-Allow-Origin: https://mapevent.world`
  - `Access-Control-Allow-Methods: POST, OPTIONS`
  - `Access-Control-Allow-Headers: Content-Type, Authorization, Origin, X-Requested-With, Accept`

## 🔄 Alternative : Utiliser le même CORS que les autres endpoints

Si d'autres endpoints fonctionnent déjà avec CORS, vous pouvez :
1. Copier la configuration CORS d'un endpoint qui fonctionne
2. L'appliquer à `/api/user/oauth/google/complete`









