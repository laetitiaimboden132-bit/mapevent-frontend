# 🔍 Vérifier la Structure de la Route dans API Gateway

## ⚠️ Erreur "Missing Authentication Token"

**Cette erreur signifie qu'API Gateway ne trouve PAS la route avant même d'appeler Lambda.**

---

## 📋 Vérifications à Faire

### 1. Structure de la Route

**La route doit être exactement :**
```
/api
  └── user
      └── likes
          ├── POST (méthode)
          └── OPTIONS (méthode)
```

**❌ PAS comme ça :**
```
/api
  └── user/likes  ← ❌ FAUX (ressource plate)
```

---

### 2. Vérifier dans API Gateway

**Dans API Gateway, vous devriez voir :**

1. **Ressource `/api`** (existe déjà)
2. **Ressource `/api/user`** (doit exister)
3. **Ressource `/api/user/likes`** (doit exister)
4. **Méthode POST** sur `/api/user/likes`
5. **Méthode OPTIONS** sur `/api/user/likes`

---

### 3. Vérifier le Path

**L'URL complète est :**
```
https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/user/likes
```

**Le path envoyé à Lambda est :** `/api/user/likes`

**Le handler Lambda doit recevoir ce path exactement.**

---

## 🔧 Solution : Vérifier la Structure

### Étape 1 : Vérifier `/api/user` Existe

1. **Dans API Gateway**, cliquez sur `/api`
2. **Vérifiez qu'il y a une ressource `user`** sous `/api`
3. **Si elle n'existe pas**, créez-la :
   - Cliquez sur `/api`
   - Actions → Create Resource
   - Resource Name : `user`
   - Resource Path : `user`
   - Cliquez sur Create Resource

### Étape 2 : Vérifier `/api/user/likes` Existe

1. **Cliquez sur `/api/user`**
2. **Vérifiez qu'il y a une ressource `likes`** sous `/api/user`
3. **Si elle n'existe pas**, créez-la :
   - Cliquez sur `/api/user`
   - Actions → Create Resource
   - Resource Name : `likes`
   - Resource Path : `likes`
   - Cliquez sur Create Resource

### Étape 3 : Vérifier les Méthodes

1. **Cliquez sur `/api/user/likes`**
2. **Vérifiez qu'il y a :**
   - ✅ Méthode POST
   - ✅ Méthode OPTIONS

### Étape 4 : Vérifier l'Intégration Lambda

1. **Cliquez sur la méthode POST**
2. **Vérifiez :**
   - Integration type : Lambda Function
   - Use Lambda Proxy integration : ✅ OUI
   - Lambda Function : `mapevent-backend`
   - Lambda Region : `eu-west-1`

### Étape 5 : Déployer

1. **Actions** → **Deploy API**
2. **Stage :** `default`
3. **Cliquez sur Deploy**

---

## 🚨 Problème Courant

**Si vous avez créé `/api/user/likes` directement sous `/api` (sans créer `/api/user` d'abord) :**

**La structure serait :**
```
/api
  └── user/likes  ← ❌ FAUX
```

**Au lieu de :**
```
/api
  └── user
      └── likes  ← ✅ CORRECT
```

**Dans ce cas, API Gateway cherche `/api/user/likes` mais trouve `/api/user/likes` comme ressource plate, ce qui ne fonctionne pas avec Lambda Proxy.**

---

## ✅ Solution Rapide

**Si la structure est incorrecte :**

1. **Supprimez la ressource `/api/user/likes`** (si elle existe directement sous `/api`)
2. **Créez `/api/user`** d'abord
3. **Créez `/api/user/likes`** sous `/api/user`
4. **Créez les méthodes POST et OPTIONS**
5. **Déployez l'API**

---

## 📝 Vérification Finale

**Après avoir créé la structure correcte :**

1. **Dans API Gateway**, vous devriez voir :
   ```
   /api
     └── user
         └── likes
             ├── POST
             └── OPTIONS
   ```

2. **Testez l'URL :**
   ```
   https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/user/likes
   ```

3. **Ça devrait fonctionner !**



