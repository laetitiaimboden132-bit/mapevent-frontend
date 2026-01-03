# 🔧 Corriger l'Erreur CORS 403

## ❌ Erreur : "échec de la réponse de pré-vérification des requêtes CORS. Code d'état : 403"

**Cela signifie :**
- La route existe probablement ✅
- Mais CORS n'est pas configuré correctement ❌
- La méthode OPTIONS (preflight) échoue avec un 403

---

## ✅ Solution : Configurer CORS Correctement

### Étape 1 : Vérifier la Route

1. Allez dans **API Gateway** (console AWS)
2. Sélectionnez votre API
3. Vérifiez que `/api/user/likes` existe

### Étape 2 : Configurer CORS pour la Méthode POST

1. **Cliquez sur `/api/user/likes`**
2. **Cliquez sur la méthode POST**
3. **Actions** → **Enable CORS**
4. **Configurez :**
   - **Access-Control-Allow-Origin :** `*`
   - **Access-Control-Allow-Headers :** `Content-Type, Authorization`
   - **Access-Control-Allow-Methods :** `POST, OPTIONS`
5. **Cliquez sur "Enable CORS and replace existing CORS headers"**
6. **Confirmez** en cliquant sur "Yes, replace existing values"

### Étape 3 : Créer la Méthode OPTIONS (CRITIQUE)

**⚠️ IMPORTANT :** La méthode OPTIONS est nécessaire pour CORS !

1. **Cliquez sur `/api/user/likes`** (la ressource, pas la méthode)
2. **Actions** → **Create Method**
3. **Sélectionnez OPTIONS**
4. **Cliquez sur la coche ✓**
5. **Integration type :** `Mock`
6. **Cliquez sur "Save"**

7. **Configurer la réponse OPTIONS :**
   - **Method Response** :
     - **HTTP Status :** `200`
     - **Headers :**
       - `Access-Control-Allow-Origin`
       - `Access-Control-Allow-Headers`
       - `Access-Control-Allow-Methods`
   
   - **Integration Response** :
     - **Header Mappings :**
       - `Access-Control-Allow-Origin` → `'*'`
       - `Access-Control-Allow-Headers` → `'Content-Type, Authorization'`
       - `Access-Control-Allow-Methods` → `'POST, OPTIONS'`

8. **Mock Integration Response :**
   - **HTTP Status :** `200`
   - **Response Body :** (vide ou `{}`)

### Étape 4 : Déployer l'API

1. **Actions** → **Deploy API**
2. **Deployment stage :** `default` (ou le stage que vous utilisez)
3. **Cliquez sur "Deploy"**

**⏱️ Attendez quelques secondes** que le déploiement soit terminé.

---

## 🚨 Configuration OPTIONS Simplifiée (Alternative)

**Si la configuration ci-dessus est trop complexe :**

1. **Créez la méthode OPTIONS**
2. **Integration type :** `Mock`
3. **Dans "Integration Response" → "Header Mappings" :**
   ```
   Access-Control-Allow-Origin: '*'
   Access-Control-Allow-Headers: 'Content-Type, Authorization'
   Access-Control-Allow-Methods: 'POST, OPTIONS'
   ```
4. **Response Body :** `{}`
5. **HTTP Status :** `200`

---

## ✅ Vérification

**Après avoir configuré CORS et déployé :**

1. **Rafraîchissez la page de test** (F5)
2. **Cliquez sur "Test Likes"**
3. **Ça devrait fonctionner !**

---

## 💡 Si ça ne fonctionne toujours pas

**Vérifiez dans les logs CloudWatch :**
- Y a-t-il des erreurs dans Lambda ?
- La requête arrive-t-elle à Lambda ?

**Vérifiez aussi :**
- La méthode OPTIONS existe-t-elle ?
- CORS est-il activé sur la méthode POST ?
- L'API est-elle déployée ?



