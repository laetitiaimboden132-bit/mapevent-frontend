# Corriger l'erreur CORS pour les méthodes POST

L'erreur "Échec de la mise à jour des en-têtes CORS pour 2 méthodes" indique que les headers n'ont pas pu être ajoutés aux méthodes **POST** pour les deux endpoints.

## 🔍 Diagnostic

Les headers OPTIONS sont OK ✅, mais les headers POST ont échoué ❌.

## ✅ Solution : Ajouter manuellement les headers CORS aux méthodes POST

### **Pour `/api/user/oauth/google` - Méthode POST :**

#### **Étape 1 : Method Response**

1. Dans API Gateway Console, allez sur `/api/user/oauth/google`
2. Cliquez sur la méthode **POST**
3. Cliquez sur **Method Response**
4. Pour **chaque code de statut** (200, 400, 500, etc.) :
   - Cliquez sur le code de statut (ex: **200**)
   - Dans **Response Headers for 200**, cliquez sur **Add header**
   - Entrez : `Access-Control-Allow-Origin`
   - Type : **String**
   - Cochez **Required** (optionnel mais recommandé)
   - Cliquez sur **Save**
   - Répétez pour tous les autres codes de statut (400, 500, etc.)

#### **Étape 2 : Integration Response**

1. Toujours dans la méthode **POST**, cliquez sur **Integration Response**
2. Pour **chaque code de statut** (200, 400, 500, etc.) :
   - Cliquez sur le code de statut (ex: **200**)
   - Dans **Header Mappings**, cliquez sur **Add header mapping**
   - **Header name** : `Access-Control-Allow-Origin`
   - **Mapping** : `'https://mapevent.world'` ⚠️ **IMPORTANT : Utilisez des guillemets simples**
   - Cliquez sur la coche ✓
   - Cliquez sur **Save**
   - Répétez pour tous les autres codes de statut

#### **Étape 3 : Répéter pour `/api/user/oauth/google/complete`**

Répétez exactement les mêmes étapes (Étape 1 et 2) pour :
- `/api/user/oauth/google/complete` → Méthode **POST**

---

## ⚠️ Points critiques

### **Format du Mapping :**
- ✅ **Correct** : `'https://mapevent.world'` (guillemets simples)
- ❌ **Incorrect** : `https://mapevent.world` (sans guillemets)
- ❌ **Incorrect** : `"https://mapevent.world"` (guillemets doubles)

### **Vérifications importantes :**

1. **Method Response** : Les headers doivent être déclarés ici
2. **Integration Response** : Les valeurs doivent être mappées ici
3. **Tous les codes de statut** : Ajoutez les headers pour 200, 400, 500, etc.

---

## 🔧 Si l'erreur persiste

### **Option 1 : Supprimer et recréer**

Si les headers existent déjà mais sont mal configurés :

1. Dans **Method Response** :
   - Cliquez sur le code de statut
   - Supprimez le header `Access-Control-Allow-Origin` s'il existe
   - Recréez-le avec les bonnes valeurs

2. Dans **Integration Response** :
   - Cliquez sur le code de statut
   - Supprimez le mapping `Access-Control-Allow-Origin` s'il existe
   - Recréez-le avec le mapping : `'https://mapevent.world'`

### **Option 2 : Vérifier les permissions**

Assurez-vous que votre utilisateur AWS a les permissions :
- `apigateway:PUT`
- `apigateway:PATCH`
- `apigateway:GET`

### **Option 3 : Utiliser l'action "Enable CORS"**

1. Sélectionnez la ressource `/api/user/oauth/google`
2. Cliquez sur **Actions** → **Enable CORS**
3. Configurez :
   - **Access-Control-Allow-Origin** : `https://mapevent.world`
   - **Access-Control-Allow-Headers** : `Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token`
   - **Access-Control-Allow-Methods** : `POST,OPTIONS`
4. Cochez **Replace existing CORS headers**
5. Cliquez sur **Enable CORS and replace existing CORS headers**
6. Répétez pour `/api/user/oauth/google/complete`

⚠️ **Note** : Cette méthode peut écraser certaines configurations. Utilisez-la seulement si la méthode manuelle ne fonctionne pas.

---

## ✅ Après correction

1. **Déployez l'API** :
   - **Actions** → **Deploy API**
   - Stage : **default**
   - Cliquez sur **Deploy**

2. **Testez** :
   - Ouvrez la console développeur (F12)
   - Allez sur l'onglet **Network**
   - Cliquez sur "Connexion avec Google"
   - Vérifiez que les requêtes POST retournent :
     - `Access-Control-Allow-Origin: https://mapevent.world`

---

## 📝 Checklist finale

Pour chaque endpoint (`/api/user/oauth/google` et `/api/user/oauth/google/complete`) :

- [ ] Méthode OPTIONS : Method Response avec 3 headers ✅
- [ ] Méthode OPTIONS : Integration Response avec 3 mappings ✅
- [ ] Méthode POST : Method Response avec `Access-Control-Allow-Origin` pour tous les codes de statut
- [ ] Méthode POST : Integration Response avec mapping `'https://mapevent.world'` pour tous les codes de statut
- [ ] API déployée sur le stage `default`

Une fois tout coché, les erreurs CORS devraient être résolues ! 🎉


