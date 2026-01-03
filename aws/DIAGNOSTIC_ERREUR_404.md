# 🔍 Diagnostic Erreur NetworkError

## ❌ Erreur : "NetworkError when attempting to fetch resource"

**Cette erreur signifie généralement :**
- La route n'existe pas dans API Gateway (404)
- L'API n'est pas déployée
- Problème CORS (mais l'erreur serait différente)

---

## 🧪 Test 1 : Vérifier si la route existe

**Testez avec une requête GET (pour voir l'erreur exacte) :**

```javascript
fetch('https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/user/likes')
.then(r => {
  console.log('Status:', r.status);
  return r.text();
})
.then(text => console.log('Réponse:', text))
.catch(error => console.error('Erreur:', error))
```

**Résultats possibles :**
- **404** → La route n'existe pas
- **405 Method Not Allowed** → La route existe mais pas pour GET
- **403** → Problème de permissions
- **CORS error** → CORS non configuré

---

## ✅ Solution : Créer la Route dans API Gateway

### Étape 1 : Vérifier si la route existe

1. Allez dans **API Gateway** (console AWS)
2. Sélectionnez votre API
3. Regardez si `/api/user/likes` existe

### Étape 2 : Créer la route si elle n'existe pas

**Voir le guide :** `aws/CREER_ROUTES_API_GATEWAY.md`

**Résumé rapide :**
1. Créer `/api/user` (ressource parent)
2. Créer `/api/user/likes` (ressource)
3. Créer méthode **POST** avec **Lambda Proxy**
4. Configurer **CORS**
5. Créer méthode **OPTIONS**
6. **Déployer l'API**

---

## 🚨 Erreurs Courantes

### Erreur 404 - Missing Authentication Token
**Cause :** La route n'existe pas dans API Gateway

**Solution :** Créer la route dans API Gateway

### Erreur CORS
**Cause :** CORS non configuré

**Solution :** Configurer CORS dans API Gateway

### Erreur 500 - Internal Server Error
**Cause :** Erreur dans le code Lambda

**Solution :** Vérifier les logs CloudWatch

---

## 💡 Test Rapide

**Testez d'abord une route qui existe déjà :**

```javascript
// Test /api/health (cette route devrait exister)
fetch('https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/health')
.then(r => r.json())
.then(data => console.log('✅ Health check:', data))
.catch(error => console.error('❌ Erreur:', error))
```

**Si ça fonctionne :** L'API Gateway fonctionne, il faut juste créer les routes `/api/user/*`

**Si ça ne fonctionne pas :** Il y a un problème plus général avec API Gateway



