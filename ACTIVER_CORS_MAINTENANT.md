# 🚨 ACTIVER CORS MAINTENANT - Instructions rapides

## ❌ Erreur actuelle
```
CORS Missing Allow Origin
Code d'état : 403
```

Sur les 2 routes :
- `/api/payments/create-checkout-session`
- `/api/admin/create-tables`

## ✅ SOLUTION - Activer CORS sur les 2 routes

### Route 1 : `/api/payments/create-checkout-session`

1. **API Gateway** > Votre API
2. **Ressources** > `/api` > `/payments` > `/create-checkout-session`
3. **Sélectionnez la méthode POST** (pas OPTIONS)
4. **Actions** (en haut à droite) > **"Activer CORS"**
5. Dans le formulaire :
   - **Origines autorisées** : `*`
   - **Méthodes autorisées** : `POST, OPTIONS`
   - **Headers autorisés** : `Content-Type, Origin`
   - **Headers exposés** : (laissez vide ou mettez `*`)
6. Cliquez **"Activer CORS et remplacer les valeurs CORS existantes"**
7. **Vérifiez** que la méthode **OPTIONS** a été créée automatiquement

### Route 2 : `/api/admin/create-tables`

1. **API Gateway** > Votre API
2. **Ressources** > `/api` > `/admin` > `/create-tables`
3. **Sélectionnez la méthode POST** (pas OPTIONS)
4. **Actions** (en haut à droite) > **"Activer CORS"**
5. Dans le formulaire :
   - **Origines autorisées** : `*`
   - **Méthodes autorisées** : `POST, OPTIONS`
   - **Headers autorisés** : `Content-Type, Origin`
   - **Headers exposés** : (laissez vide ou mettez `*`)
6. Cliquez **"Activer CORS et remplacer les valeurs CORS existantes"**
7. **Vérifiez** que la méthode **OPTIONS** a été créée automatiquement

### ⚠️ DÉPLOYER L'API (OBLIGATOIRE !)

**Après avoir activé CORS sur les 2 routes :**

1. En haut de l'écran API Gateway
2. Cliquez sur **"Actions"** (bouton en haut)
3. Sélectionnez **"Déployer l'API"**
4. **Stage** : `default` (ou votre stage)
5. **Description** : "Activation CORS paiement et create-tables"
6. Cliquez **"Déployer"**

### ⏱️ Attendre

- Attendez **30 secondes** après le déploiement
- Les changements prennent quelques secondes à se propager

### ✅ Retester

1. Retestez avec `test-routes.html`
2. Les 2 routes doivent maintenant fonctionner

## 🔍 Vérifications

### Vérifier que CORS est activé

Pour chaque route, vous devriez voir :
- Une icône **CORS** à côté de la méthode POST
- Une méthode **OPTIONS** créée automatiquement

### Si OPTIONS n'existe pas

1. Cliquez sur `/create-checkout-session` (ou `/create-tables`)
2. Vérifiez si **OPTIONS** apparaît dans les méthodes
3. Si non, créez-la manuellement :
   - Actions > "Créer une méthode" > OPTIONS
   - Liez-la à la même intégration Lambda que POST
   - Activez CORS sur OPTIONS aussi

## 📋 Checklist

- [ ] CORS activé sur `/api/payments/create-checkout-session` (POST)
- [ ] Méthode OPTIONS créée pour `/create-checkout-session`
- [ ] CORS activé sur `/api/admin/create-tables` (POST)
- [ ] Méthode OPTIONS créée pour `/create-tables`
- [ ] API **DÉPLOYÉE** sur stage `default`
- [ ] Attendu 30 secondes
- [ ] Retesté les 2 routes

## 🚨 Si ça ne marche toujours pas

1. **Vérifiez dans la console (F12) > Network** :
   - Cherchez la requête OPTIONS (preflight)
   - Elle doit retourner **Status 200**
   - Headers de réponse doivent contenir `Access-Control-Allow-Origin: *`

2. **Vérifiez que l'API est bien déployée** :
   - En haut de l'écran API Gateway
   - Regardez la date du dernier déploiement
   - Si ancien, redéployez

3. **Vérifiez les permissions Lambda** :
   - Lambda doit pouvoir être invoquée par API Gateway
   - Vérifiez le rôle IAM de Lambda

