# 📋 Guide : Créer la route `/api/user/agenda` dans API Gateway

## 🎯 Objectif
Créer la route `/api/user/agenda` pour permettre aux utilisateurs d'ajouter/retirer des événements de leur agenda.

---

## 📝 Étapes détaillées

### 1️⃣ **Créer la ressource `/agenda`**

1. Dans API Gateway, allez dans votre API
2. Dans le panneau de gauche, trouvez `/api/user`
3. Cliquez sur **"Actions"** → **"Créer une ressource"**
4. **Nom de la ressource** : `agenda`
5. **Chemin de la ressource** : `/agenda` (rempli automatiquement)
6. ✅ **Cocher** : "Activer le proxy de ressources API Gateway"
7. Cliquez sur **"Créer une ressource"**

**Résultat :** Vous avez maintenant `/api/user/agenda`

---

### 2️⃣ **Créer la méthode POST**

1. Sélectionnez la ressource `/agenda` que vous venez de créer
2. Cliquez sur **"Actions"** → **"Créer une méthode"**
3. Dans le menu déroulant, sélectionnez **POST**
4. Cliquez sur la coche ✅

**Configuration de l'intégration :**
- **Type d'intégration** : Fonction Lambda
- ✅ **Cocher** : "Utiliser l'intégration de proxy Lambda"
- **Région Lambda** : `eu-west-1`
- **Fonction Lambda** : `mapevent-backend`
- Cliquez sur **"Enregistrer"**
- Confirmez l'ajout de l'autorisation Lambda

---

### 3️⃣ **Activer CORS pour POST**

1. Sélectionnez la méthode **POST** sous `/agenda`
2. Cliquez sur **"Actions"** → **"Activer CORS"**
3. **Origine d'accès autorisée** : `*`
4. **En-têtes d'accès autorisés** : `Content-Type, Authorization`
5. **Méthodes d'accès autorisées** : `POST, OPTIONS`
6. Cliquez sur **"Activer CORS et remplacer les en-têtes CORS existants"**
7. Confirmez le remplacement

**⚠️ IMPORTANT :** Cette action va créer automatiquement la méthode OPTIONS !

---

### 4️⃣ **Vérifier la méthode OPTIONS**

1. Vérifiez que la méthode **OPTIONS** a été créée automatiquement sous `/agenda`
2. Si elle existe, c'est parfait ! ✅
3. Si elle n'existe pas, créez-la manuellement :
   - Cliquez sur **"Actions"** → **"Créer une méthode"**
   - Sélectionnez **OPTIONS**
   - Type d'intégration : **Mock**
   - Cliquez sur **"Enregistrer"**

---

### 5️⃣ **Déployer l'API**

1. Cliquez sur **"Actions"** → **"Déployer l'API"**
2. **Étape de déploiement** : `default`
3. **Description du déploiement** : `Ajout route /api/user/agenda`
4. Cliquez sur **"Déployer"**

---

## ✅ Vérification

Une fois déployé, testez avec `test_api.html` :

1. Ouvrez `http://localhost:8000/test_api.html` dans votre navigateur
2. Cliquez sur **"Test Agenda (Add)"**
3. Vous devriez voir :
   ```
   Status: 200
   Réponse: {"action":"added","success":true}
   ```

---

## 🎉 C'est terminé !

La route `/api/user/agenda` est maintenant opérationnelle !

**URL complète :**
```
https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/user/agenda
```

---

## 📋 Résumé des routes créées

- ✅ `/api/user/likes`
- ✅ `/api/user/favorites`
- ✅ `/api/user/participate`
- ✅ `/api/user/agenda` ← **Vous êtes ici !**



