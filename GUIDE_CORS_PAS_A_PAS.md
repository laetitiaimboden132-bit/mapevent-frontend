# Guide CORS - Pas à pas détaillé pour la console AWS

## ⚠️ Si vous voyez "invalid patches" ou "invalide"

Cela signifie généralement qu'il manque le **Body Mapping Template** ou que le format des guillemets est incorrect.

---

## 📋 Configuration OPTIONS - Étape par étape

### **Étape 1 : Accéder à OPTIONS**

1. API Gateway → Votre API → **Ressources**
2. Cliquez sur `/api/user/oauth/google`
3. Cliquez sur la méthode **OPTIONS**

### **Étape 2 : Réponse de méthode (Method Response)**

1. Cliquez sur **Réponse de méthode** (Method Response)
2. Cliquez sur **200**
3. Dans **En-têtes de réponse pour 200**, cliquez sur **Ajouter un en-tête**
4. Ajoutez ces 3 en-têtes **un par un** :

   **Premier en-tête :**
   - Nom : `Access-Control-Allow-Headers`
   - Type : **Chaîne** (String)
   - Cliquez sur **Enregistrer**

   **Deuxième en-tête :**
   - Nom : `Access-Control-Allow-Methods`
   - Type : **Chaîne** (String)
   - Cliquez sur **Enregistrer**

   **Troisième en-tête :**
   - Nom : `Access-Control-Allow-Origin`
   - Type : **Chaîne** (String)
   - Cliquez sur **Enregistrer**

### **Étape 3 : Réponse d'intégration (Integration Response)**

1. Cliquez sur **Réponse d'intégration** (Integration Response)
2. Cliquez sur **200**

#### **3.1 : Mappages d'en-têtes (Header Mappings)**

Cliquez sur **Mappages d'en-têtes** → **Ajouter un mappage d'en-tête**

**Mapping 1 :**
- **Nom de l'en-tête** : `Access-Control-Allow-Origin`
- **Mappage** : Tapez exactement ceci (avec les guillemets simples) :
  ```
  'https://mapevent.world'
  ```
- Cliquez sur ✓ puis **Enregistrer**

**Mapping 2 :**
- **Nom de l'en-tête** : `Access-Control-Allow-Methods`
- **Mappage** : Tapez exactement ceci :
  ```
  'POST,OPTIONS'
  ```
- Cliquez sur ✓ puis **Enregistrer**

**Mapping 3 :**
- **Nom de l'en-tête** : `Access-Control-Allow-Headers`
- **Mappage** : Tapez exactement ceci :
  ```
  'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token'
  ```
- Cliquez sur ✓ puis **Enregistrer**

#### **3.2 : Modèles de mappage de corps (Body Mapping Templates)**

⚠️ **CETTE ÉTAPE EST CRITIQUE - C'est souvent ce qui manque !**

1. Dans **Réponse d'intégration** → **200**, trouvez **Modèles de mappage de corps**
2. Cliquez sur **Ajouter un modèle de mappage**
3. Dans **Type de contenu**, entrez exactement :
  ```
  application/json
  ```
4. Dans le champ **Modèle**, entrez exactement ceci :
  ```
  ""
  ```
  (Deux guillemets doubles, rien d'autre, pas d'espaces)
5. Cliquez sur **Enregistrer**

### **Étape 4 : Vérification OPTIONS**

Vous devriez maintenant avoir :
- ✅ 3 en-têtes dans **Réponse de méthode**
- ✅ 3 mappages dans **Mappages d'en-têtes**
- ✅ 1 modèle dans **Modèles de mappage de corps** avec `""`

---

## 📋 Configuration POST - Étape par étape

### **Étape 1 : Accéder à POST**

1. Revenez à la ressource `/api/user/oauth/google`
2. Cliquez sur la méthode **POST**

### **Étape 2 : Réponse de méthode (Method Response)**

1. Cliquez sur **Réponse de méthode**
2. Pour **chaque code de statut** (200, 400, 500, etc.) :
   - Cliquez sur le code de statut (ex: **200**)
   - Dans **En-têtes de réponse**, cliquez sur **Ajouter un en-tête**
   - Nom : `Access-Control-Allow-Origin`
   - Type : **Chaîne** (String)
   - Cliquez sur **Enregistrer**
   - Répétez pour les autres codes (400, 500, etc.)

### **Étape 3 : Réponse d'intégration (Integration Response)**

1. Cliquez sur **Réponse d'intégration**
2. Pour **chaque code de statut** (200, 400, 500, etc.) :
   - Cliquez sur le code de statut (ex: **200**)
   - Dans **Mappages d'en-têtes**, cliquez sur **Ajouter un mappage d'en-tête**
   - **Nom de l'en-tête** : `Access-Control-Allow-Origin`
   - **Mappage** : Tapez exactement ceci :
     ```
     'https://mapevent.world'
     ```
   - Cliquez sur ✓ puis **Enregistrer**
   - Répétez pour les autres codes

---

## 🔄 Répéter pour le deuxième endpoint

Répétez **toutes les étapes** pour :
- `/api/user/oauth/google/complete`

---

## 🚀 Déployer

1. Une fois tout configuré, cliquez sur **Actions** (en haut)
2. Sélectionnez **Déployer l'API**
3. **Étape de déploiement** : `default`
4. Cliquez sur **Déployer**

---

## ✅ Checklist finale

Pour chaque endpoint (`/api/user/oauth/google` et `/api/user/oauth/google/complete`) :

**OPTIONS :**
- [ ] Réponse de méthode : 3 en-têtes ajoutés
- [ ] Réponse d'intégration : 3 mappages d'en-têtes
- [ ] Réponse d'intégration : 1 modèle de corps avec `""`

**POST :**
- [ ] Réponse de méthode : `Access-Control-Allow-Origin` pour tous les codes
- [ ] Réponse d'intégration : Mapping `'https://mapevent.world'` pour tous les codes

**Déploiement :**
- [ ] API déployée sur `default`

---

## 🆘 Si ça ne fonctionne toujours pas

1. **Vérifiez les guillemets** : Utilisez des guillemets simples `'...'` pas doubles `"..."`
2. **Vérifiez le modèle de corps** : Doit être exactement `""` (deux guillemets doubles)
3. **Vérifiez que vous avez bien déployé** après chaque modification
4. **Videz le cache du navigateur** avant de tester

Une fois tout coché, ça devrait fonctionner ! 🎉


