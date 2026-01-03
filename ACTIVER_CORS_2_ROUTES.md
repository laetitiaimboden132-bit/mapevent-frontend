# 🔧 Activer CORS pour les 2 routes

## ❌ Erreur actuelle
```
Access-Control-Allow-Origin manquant
Code d'état : 403
```

Sur les 2 routes :
- `/api/payments/create-checkout-session`
- `/api/admin/create-tables`

## ✅ Solution - Activer CORS sur les 2 routes

### Route 1 : `/api/payments/create-checkout-session`

1. **API Gateway** > Votre API
2. **Ressources** > `/api` > `/payments` > `/create-checkout-session`
3. **Sélectionnez la méthode POST**
4. **Actions** > **"Activer CORS"**
5. Configurez :
   - **Origines autorisées** : `*`
   - **Méthodes autorisées** : `POST, OPTIONS`
   - **Headers autorisés** : `Content-Type, Origin`
6. Cliquez **"Activer CORS et remplacer les valeurs CORS existantes"**
7. **Vérifiez** que la méthode **OPTIONS** a été créée automatiquement

### Route 2 : `/api/admin/create-tables`

1. **API Gateway** > Votre API
2. **Ressources** > `/api` > `/admin` > `/create-tables`
3. **Sélectionnez la méthode POST**
4. **Actions** > **"Activer CORS"**
5. Configurez :
   - **Origines autorisées** : `*`
   - **Méthodes autorisées** : `POST, OPTIONS`
   - **Headers autorisés** : `Content-Type, Origin`
6. Cliquez **"Activer CORS et remplacer les valeurs CORS existantes"**
7. **Vérifiez** que la méthode **OPTIONS** a été créée automatiquement

### ⚠️ DÉPLOYER L'API (CRITIQUE !)

**Après avoir activé CORS sur les 2 routes :**

1. En haut de l'écran API Gateway
2. **Actions** > **"Déployer l'API"**
3. **Stage** : `default`
4. **Description** : "Activation CORS paiement et create-tables"
5. Cliquez **"Déployer"**

### ⏱️ Attendre

- Attendez **30 secondes** après le déploiement
- Les changements prennent quelques secondes à se propager

### ✅ Vérifier

1. Retestez avec `test-routes.html`
2. Les 2 routes doivent maintenant fonctionner
3. Si toujours 403, vérifiez :
   - Que CORS est bien activé (icône visible)
   - Que l'API est bien déployée
   - Que les méthodes OPTIONS existent

## 📋 Checklist

- [ ] CORS activé sur `/api/payments/create-checkout-session` (POST)
- [ ] Méthode OPTIONS créée pour `/create-checkout-session`
- [ ] CORS activé sur `/api/admin/create-tables` (POST)
- [ ] Méthode OPTIONS créée pour `/create-tables`
- [ ] API **DÉPLOYÉE** sur stage `default`
- [ ] Attendu 30 secondes
- [ ] Retesté les 2 routes

