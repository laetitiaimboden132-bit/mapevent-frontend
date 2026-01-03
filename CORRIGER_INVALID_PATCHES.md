# Corriger l'erreur "invalid patches"

Si vous avez toujours l'erreur "invalid" même après avoir ajouté le modèle, il faut **supprimer et recréer** la réponse d'intégration.

## 🔧 Solution : Supprimer et recréer OPTIONS Integration Response

### **Étape 1 : Supprimer la réponse existante**

1. Dans **OPTIONS → Réponse d'intégration**
2. Cliquez sur **200**
3. En bas de la page, cliquez sur **Supprimer** (Delete)
4. Confirmez la suppression

### **Étape 2 : Recréer proprement**

1. Toujours dans **OPTIONS → Réponse d'intégration**
2. Cliquez sur **Ajouter une réponse d'intégration** (Add Integration Response)
3. **Code de statut HTTP** : Sélectionnez `200`
4. Cliquez sur **Enregistrer**

### **Étape 3 : Ajouter les mappages d'en-têtes (dans l'ordre)**

Maintenant que la réponse est créée, ajoutez les mappages **un par un** :

**Mapping 1 - Access-Control-Allow-Origin :**
1. Dans **Mappages d'en-têtes**, cliquez sur **Ajouter un mappage d'en-tête**
2. **Nom de l'en-tête** : Tapez exactement :
   ```
   Access-Control-Allow-Origin
   ```
3. **Mappage** : Tapez exactement (avec guillemets simples) :
   ```
   'https://mapevent.world'
   ```
4. Cliquez sur ✓
5. Cliquez sur **Enregistrer** (en haut de la page)

**Mapping 2 - Access-Control-Allow-Methods :**
1. Cliquez à nouveau sur **Ajouter un mappage d'en-tête**
2. **Nom de l'en-tête** :
   ```
   Access-Control-Allow-Methods
   ```
3. **Mappage** :
   ```
   'POST,OPTIONS'
   ```
4. Cliquez sur ✓
5. Cliquez sur **Enregistrer**

**Mapping 3 - Access-Control-Allow-Headers :**
1. Cliquez à nouveau sur **Ajouter un mappage d'en-tête**
2. **Nom de l'en-tête** :
   ```
   Access-Control-Allow-Headers
   ```
3. **Mappage** :
   ```
   'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token'
   ```
4. Cliquez sur ✓
5. Cliquez sur **Enregistrer**

### **Étape 4 : Ajouter le modèle de corps**

1. Dans **Modèles de mappage de corps**, cliquez sur **Ajouter un modèle de mappage**
2. **Type de contenu** : Tapez exactement :
   ```
   application/json
   ```
3. **Modèle** : Tapez exactement :
   ```
   ""
   ```
   (Deux guillemets doubles, rien d'autre)
4. Cliquez sur **Enregistrer**

---

## ⚠️ Points critiques

1. **Guillemets simples** dans les mappages : `'...'` (pas doubles `"...`)
2. **Pas d'espaces** avant/après les valeurs
3. **Enregistrer après chaque mapping** (ne pas tout ajouter d'un coup)
4. **Le modèle de corps doit être ajouté en dernier**

---

## 🔄 Alternative : Utiliser l'option "Activer CORS" si disponible

Si vous voyez toujours l'erreur, essayez cette méthode :

1. Revenez à la **ressource** `/api/user/oauth/google` (pas la méthode)
2. Cliquez sur **Actions** (en haut)
3. Cherchez **"Activer CORS"** ou **"CORS"** ou **"Enable CORS"**
4. Si vous le trouvez :
   - Origines autorisées : `https://mapevent.world`
   - Méthodes : `POST,OPTIONS`
   - En-têtes : `Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token`
   - Cochez **Remplacer les en-têtes CORS existants**
   - Cliquez sur **Activer**

---

## 📝 Vérification

Après avoir recréé, vous devriez avoir :
- ✅ 3 mappages d'en-têtes dans **Mappages d'en-têtes**
- ✅ 1 modèle dans **Modèles de mappage de corps** avec `""`
- ✅ Pas d'erreur "invalid"

Essayez de supprimer et recréer, puis dites-moi si ça fonctionne !


