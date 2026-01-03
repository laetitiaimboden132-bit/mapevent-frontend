# 🔍 Diagnostic CORS - Erreur 403

## ❌ Erreur actuelle
```
CORS Missing Allow Origin
Code d'état : 403
```

## 🔍 Vérifications à faire MAINTENANT

### 1. Vérifier dans API Gateway

**Allez dans API Gateway et vérifiez :**

1. **Ressources** > `/api` > `/payments` > `/create-checkout-session`
2. **Regardez les méthodes disponibles :**
   - ✅ Doit avoir **POST**
   - ✅ Doit avoir **OPTIONS**
   - Si OPTIONS n'existe pas → **PROBLÈME !**

3. **Cliquez sur la méthode POST :**
   - Regardez si vous voyez une icône **CORS** à côté
   - Si pas d'icône CORS → CORS n'est pas activé

4. **Cliquez sur la méthode OPTIONS :**
   - Vérifiez qu'elle existe
   - Vérifiez qu'elle a une intégration (Lambda ou Mock)

### 2. Si CORS n'est pas activé

**Sur la méthode POST :**
1. Actions > "Activer CORS"
2. Configurer :
   - Origines : `*`
   - Méthodes : `POST, OPTIONS`
   - Headers : `Content-Type, Origin`
3. Cliquer "Activer CORS et remplacer..."
4. **DÉPLOYER l'API** (Actions > Déployer l'API > default)

### 3. Si OPTIONS n'existe pas

**Créer OPTIONS manuellement :**
1. Cliquez sur `/create-checkout-session`
2. Actions > "Créer une méthode"
3. Sélectionnez **OPTIONS**
4. Type d'intégration : **Lambda Function**
5. Même fonction Lambda que POST
6. Actions > "Activer CORS" sur OPTIONS aussi
7. **DÉPLOYER l'API**

### 4. Vérifier le déploiement

**En haut de l'écran API Gateway :**
- Regardez le stage actif (devrait être "default")
- Vérifiez la date du dernier déploiement
- Si ancien → **DÉPLOYER MAINTENANT**

## 🧪 Test depuis le navigateur

### Option 1 : Tester depuis un serveur local

Au lieu de `file://`, utilisez un serveur local :

```bash
# Dans le dossier frontend/public
python -m http.server 8000
```

Puis ouvrez : `http://localhost:8000/test-api.html`

### Option 2 : Tester depuis la console du navigateur

Ouvrez la console (F12) et testez directement :

```javascript
fetch('https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/api/payments/create-checkout-session', {
  method: 'OPTIONS',
  headers: {
    'Origin': 'https://mapevent.world',
    'Access-Control-Request-Method': 'POST',
    'Access-Control-Request-Headers': 'Content-Type'
  }
}).then(r => {
  console.log('Status:', r.status);
  console.log('Headers:', {
    'Access-Control-Allow-Origin': r.headers.get('Access-Control-Allow-Origin'),
    'Access-Control-Allow-Methods': r.headers.get('Access-Control-Allow-Methods'),
    'Access-Control-Allow-Headers': r.headers.get('Access-Control-Allow-Headers')
  });
  return r.text();
}).then(console.log);
```

**Si OPTIONS retourne 403 :**
- La méthode OPTIONS n'existe pas ou n'est pas configurée
- Créez-la manuellement

**Si OPTIONS retourne 200 mais sans headers CORS :**
- CORS n'est pas activé sur OPTIONS
- Activez CORS sur OPTIONS aussi

## ✅ Checklist finale

- [ ] Méthode POST existe sous `/create-checkout-session`
- [ ] Méthode OPTIONS existe sous `/create-checkout-session`
- [ ] CORS activé sur POST (icône visible)
- [ ] CORS activé sur OPTIONS (icône visible)
- [ ] API déployée sur stage "default"
- [ ] Dernier déploiement < 5 minutes
- [ ] Test depuis serveur local (pas file://)

## 🚨 Si ça ne marche toujours pas

1. **Supprimez CORS et réactivez-le :**
   - Actions > "Désactiver CORS" (si disponible)
   - Puis "Activer CORS" à nouveau
   - Déployez

2. **Vérifiez l'intégration Lambda :**
   - La fonction Lambda doit retourner les headers CORS aussi
   - Vérifiez le code Lambda

3. **Testez directement l'URL OPTIONS :**
   ```bash
   curl -X OPTIONS https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/api/payments/create-checkout-session \
     -H "Origin: https://mapevent.world" \
     -H "Access-Control-Request-Method: POST" \
     -v
   ```
   
   Doit retourner :
   ```
   Access-Control-Allow-Origin: *
   Access-Control-Allow-Methods: POST, OPTIONS
   ```

