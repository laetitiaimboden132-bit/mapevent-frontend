# 🔧 Corriger l'Erreur 404 - Route Non Trouvée

## ❌ Erreur : "404 Not Found - The requested URL was not found on the server"

**Cela signifie :**
- La route `/api/user/likes` n'existe pas dans API Gateway
- OU l'API n'est pas déployée
- OU la route existe mais n'est pas accessible via l'URL utilisée

---

## ✅ Solution : Vérifier et Créer la Route

### Étape 1 : Vérifier si la Route Existe

1. **Allez dans API Gateway** (console AWS)
2. **Sélectionnez votre API**
3. **Regardez dans le panneau de gauche** la structure des routes
4. **Vérifiez si vous voyez :**
   - `/api`
   - `/api/user`
   - `/api/user/likes`

**Si `/api/user/likes` n'existe pas :** Créez-la (voir guide ci-dessous)

**Si `/api/user/likes` existe :** Passez à l'Étape 2

---

### Étape 2 : Vérifier le Déploiement

**⚠️ IMPORTANT :** Même si la route existe, elle ne sera pas accessible tant que l'API n'est pas déployée !

1. **Dans API Gateway, cliquez sur "Actions"** (en haut)
2. **Sélectionnez "Deploy API"**
3. **Deployment stage :** `default` (ou le stage que vous utilisez)
4. **Cliquez sur "Deploy"**

**⏱️ Attendez quelques secondes** que le déploiement soit terminé.

---

### Étape 3 : Vérifier l'URL

**L'URL doit être :**
```
https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/user/likes
```

**Notez le `/default` dans l'URL !** C'est le nom du stage de déploiement.

**Si votre stage s'appelle différemment :**
- Remplacez `default` par le nom de votre stage
- Ou déployez sur le stage `default`

---

### Étape 4 : Créer la Route si elle n'Existe Pas

**Si la route n'existe pas, créez-la :**

1. **Créer `/api/user` (ressource parent) :**
   - Cliquez sur `/api`
   - **Actions** → **Create Resource**
   - **Resource Name :** `user`
   - **Resource Path :** `user`
   - Cliquez sur **Create Resource**

2. **Créer `/api/user/likes` :**
   - Cliquez sur `/api/user`
   - **Actions** → **Create Resource**
   - **Resource Name :** `likes`
   - **Resource Path :** `likes`
   - Cliquez sur **Create Resource**

3. **Créer la méthode POST :**
   - Cliquez sur `/api/user/likes`
   - **Actions** → **Create Method**
   - Sélectionnez **POST**
   - **Integration type :** `Lambda Function`
   - **Use Lambda Proxy integration :** ✅ **OUI**
   - **Lambda Function :** `mapevent-backend`
   - Cliquez sur **Save**

4. **Configurer CORS :**
   - Cliquez sur la méthode **POST**
   - **Actions** → **Enable CORS**
   - Configurez les headers CORS
   - Cliquez sur **Enable CORS**

5. **Créer la méthode OPTIONS :**
   - Cliquez sur `/api/user/likes`
   - **Actions** → **Create Method** → **OPTIONS**
   - **Integration type :** `Mock`
   - Configurez les headers CORS
   - Cliquez sur **Save**

6. **Déployer l'API :**
   - **Actions** → **Deploy API**
   - **Stage :** `default`
   - Cliquez sur **Deploy**

---

## 🧪 Test de Vérification

**Testez d'abord une route qui devrait exister :**

```javascript
fetch('https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/health')
.then(r => r.json())
.then(data => console.log('✅ Health:', data))
.catch(error => console.error('❌ Erreur:', error))
```

**Si `/api/health` fonctionne :** L'API Gateway fonctionne, il faut juste créer `/api/user/likes`

**Si `/api/health` ne fonctionne pas :** Il y a un problème plus général avec API Gateway

---

## 💡 Checklist

- [ ] La route `/api/user/likes` existe dans API Gateway
- [ ] La méthode POST existe sur `/api/user/likes`
- [ ] La méthode POST est configurée avec Lambda Proxy
- [ ] CORS est configuré sur la méthode POST
- [ ] La méthode OPTIONS existe
- [ ] L'API est déployée sur le stage `default`
- [ ] L'URL utilisée contient `/default/` (nom du stage)

---

## 🚨 Problèmes Courants

### La route existe mais 404 quand même
**→ L'API n'est pas déployée !** Déployez l'API.

### L'URL ne contient pas `/default/`
**→ Ajoutez `/default/` dans l'URL** ou déployez sur le stage `default`.

### La route existe dans une autre région
**→ Vérifiez que vous êtes dans la bonne région AWS** (eu-west-1).



