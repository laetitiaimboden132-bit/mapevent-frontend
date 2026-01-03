# 📋 Ordre de Création d'une Route dans API Gateway

## ✅ Ordre Recommandé (Plus Rapide)

### 1. Créer la Ressource
- Cliquez sur `/api/user`
- **Actions** → **Create Resource**
- Nom : `favorites`
- Cliquez sur **Create Resource**

### 2. Créer la Méthode POST
- Cliquez sur `/api/user/favorites`
- **Actions** → **Create Method** → **POST**
- Configuration Lambda Proxy
- Cliquez sur **Save**

### 3. Créer la Méthode OPTIONS (pour CORS)
- Cliquez sur `/api/user/favorites`
- **Actions** → **Create Method** → **OPTIONS**
- Integration type : **Mock**
- Configurez les headers CORS
- Cliquez sur **Save**

### 4. Déployer l'API (UNE SEULE FOIS)
- **Actions** → **Deploy API**
- Stage : `default`
- Cliquez sur **Deploy**

---

## ⚠️ IMPORTANT

**Vous DEVEZ déployer l'API après avoir créé les méthodes !**

Sans déploiement, les routes ne seront **PAS accessibles**, même si elles existent dans API Gateway.

---

## 🔄 Alternative : Déployer Après Chaque Étape

Si vous voulez tester au fur et à mesure :

1. Créer POST → **Déployer** → Tester
2. Créer OPTIONS → **Déployer** → Tester

Mais c'est plus long, donc l'Option 1 est recommandée.

---

## ✅ Vérification

**Après le déploiement, la route doit être accessible :**
```
https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/user/favorites
```

**Test :**
```json
POST /api/user/favorites
{
  "userId": "1",
  "itemId": 1,
  "itemMode": "event",
  "action": "add"
}
```

---

## 📝 Note

**Pour `/api/user/likes` :**
- Si vous avez déjà créé POST et OPTIONS
- Il faut juste **déployer** l'API maintenant
- Puis créer `/api/user/favorites` de la même manière



