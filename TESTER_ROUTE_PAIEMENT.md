# 🧪 Tester la Route de Paiement

## 📋 Tests à Faire

### Test 1 : Tester Directement dans le Navigateur

1. **Ouvrez** `https://mapevent.world`
2. **Ouvrez la console** (F12)
3. **Onglet Network** (Réseau)
4. **Cliquez** sur un contact (booking/service)
5. **Cliquez** sur "Payer CHF 1.–"
6. **Regardez** dans Network :
   - **OPTIONS** → Doit retourner **200** ✅
   - **POST** → Doit retourner **200** avec `sessionId` ✅

### Test 2 : Tester avec curl (Terminal)

**Windows PowerShell** :

```powershell
# Test OPTIONS (pré-vérification CORS)
Invoke-WebRequest -Uri "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/payments/create-checkout-session" -Method OPTIONS -Headers @{"Origin"="https://mapevent.world"}

# Test POST (création session)
$body = @{
    userId = "1"
    paymentType = "contact"
    itemType = "booking"
    itemId = "1"
    amount = 1.00
    currency = "CHF"
    email = "test@mapevent.ch"
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/payments/create-checkout-session" -Method POST -Headers @{"Content-Type"="application/json"; "Origin"="https://mapevent.world"} -Body $body
```

### Test 3 : Tester dans la Console du Navigateur

**Ouvrez la console** (F12) et tapez :

```javascript
// Test de la route
fetch('https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/payments/create-checkout-session', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Origin': 'https://mapevent.world'
  },
  body: JSON.stringify({
    userId: '1',
    paymentType: 'contact',
    itemType: 'booking',
    itemId: 1,
    amount: 1.00,
    currency: 'CHF',
    email: 'test@mapevent.ch'
  })
})
.then(response => response.json())
.then(data => {
  console.log('✅ Succès:', data);
  if (data.sessionId) {
    console.log('✅ Session ID:', data.sessionId);
  }
  if (data.publicKey) {
    console.log('✅ Public Key:', data.publicKey);
  }
})
.catch(error => {
  console.error('❌ Erreur:', error);
});
```

## ✅ Résultats Attendus

### Si Ça Fonctionne

```json
{
  "sessionId": "cs_live_...",
  "publicKey": "pk_live_..."
}
```

**Et dans Network** :
- OPTIONS → **200** ✅
- POST → **200** ✅
- Headers CORS présents ✅

### Si Ça Ne Fonctionne Pas

**Erreur CORS 403** :
- ⚠️ CORS pas activé ou pas déployé
- **Solution** : Vérifier CORS et déployer l'API

**Erreur 500** :
- ⚠️ Problème dans Lambda
- **Solution** : Vérifier les logs Lambda

**Erreur 404** :
- ⚠️ Route n'existe pas
- **Solution** : Créer la route dans API Gateway

## 🔍 Vérifier les Logs

### Dans Lambda

1. **Lambda** → Votre fonction
2. **Monitor** → **View logs in CloudWatch**
3. **Voir** les erreurs exactes

### Dans API Gateway

1. **API Gateway** → Votre API
2. **Stages** → `default` → **Logs**
3. **Voir** les requêtes et réponses

## 📋 Checklist de Test

- [ ] Test dans le navigateur (F12 → Network)
- [ ] OPTIONS retourne 200
- [ ] POST retourne 200
- [ ] Réponse contient `sessionId`
- [ ] Réponse contient `publicKey`
- [ ] Pas d'erreur CORS
- [ ] Redirection vers Stripe fonctionne

## 🎯 Test Complet

1. **Ouvrir** `https://mapevent.world`
2. **Console** (F12) → Network
3. **Cliquer** sur un contact
4. **Cliquer** sur "Payer CHF 1.–"
5. **Vérifier** :
   - ✅ OPTIONS → 200
   - ✅ POST → 200 avec sessionId
   - ✅ Redirection vers Stripe Checkout
   - ✅ Formulaire de paiement s'affiche

---

**Testez maintenant et dites-moi ce que vous voyez ! 🧪**

