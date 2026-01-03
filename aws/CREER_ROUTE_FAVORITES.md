# 🔧 Créer la Route /api/user/favorites dans API Gateway

## 📋 Étapes

### 1. Créer la Ressource `/api/user/favorites`

**Si `/api/user` n'existe pas encore :**
1. Cliquez sur `/api`
2. **Actions** → **Create Resource**
3. **Resource Name :** `user`
4. **Resource Path :** `user`
5. Cliquez sur **Create Resource**

**Ensuite :**
1. Cliquez sur `/api/user`
2. **Actions** → **Create Resource**
3. **Resource Name :** `favorites`
4. **Resource Path :** `favorites`
5. Cliquez sur **Create Resource**

---

### 2. Créer la Méthode POST

1. Cliquez sur `/api/user/favorites`
2. **Actions** → **Create Method**
3. Sélectionnez **POST**
4. **Integration type :** `Lambda Function`
5. **Use Lambda Proxy integration :** ✅ **OUI**
6. **Lambda Function :** `mapevent-backend`
7. **Lambda Region :** `eu-west-1`
8. Cliquez sur **Save**

---

### 3. Configurer CORS

**Option 1 : Menu Actions de la Ressource**
1. Cliquez sur `/api/user/favorites` (la ressource, pas la méthode)
2. **Actions** (en haut à droite)
3. **Enable CORS**
4. Configurez les headers CORS
5. Cliquez sur **Enable CORS**

**Option 2 : Créer la Méthode OPTIONS**
1. Cliquez sur `/api/user/favorites`
2. **Actions** → **Create Method** → **OPTIONS**
3. **Integration type :** `Mock`
4. Configurez les headers CORS dans la réponse
5. Cliquez sur **Save**

---

### 4. Déployer l'API

1. **Actions** → **Deploy API**
2. **Deployment stage :** `default`
3. Cliquez sur **Deploy**

---

## ✅ Vérification

**Structure attendue :**
```
/api
  └── user
      ├── likes
      │   ├── POST
      │   └── OPTIONS
      └── favorites
          ├── POST
          └── OPTIONS
```

---

## 🧪 Test

**URL de test :**
```
https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/user/favorites
```

**Body de test :**
```json
{
  "userId": "1",
  "itemId": 1,
  "itemMode": "event",
  "action": "add"
}
```

---

## 📝 Notes

- La route `/api/user/favorites` existe déjà dans le backend Lambda
- L'endpoint gère les actions `add` et `remove`
- CORS doit être configuré pour permettre les requêtes depuis le frontend



