# 💳 Configurer le Paiement - Guide Étape par Étape

## 🎯 Objectif
Faire fonctionner `/api/payments/create-checkout-session` avec CORS.

---

## 📋 ÉTAPE 1 : Vérifier que la route existe dans API Gateway

1. **AWS Console** > **API Gateway**
2. Cliquez sur **votre API**
3. Menu gauche : **"Ressources"**
4. Vérifiez que vous avez :
   - `/api`
   - `/api/payments`
   - `/api/payments/create-checkout-session`

**Si ça n'existe pas :**
- Créez-les (on le fera ensemble si besoin)

**Si ça existe :**
- ✅ Passez à l'étape 2

---

## 📋 ÉTAPE 2 : Vérifier la méthode POST

1. Cliquez sur `/api/payments/create-checkout-session`
2. Vous devez voir **POST** dans la liste des méthodes

**Si POST n'existe pas :**
- Actions > "Créer une méthode" > POST
- Type d'intégration : **Lambda Function**
- Sélectionnez votre fonction Lambda
- **Lambda Proxy integration** : ✅ COCHÉ
- Save

**Si POST existe :**
- ✅ Cliquez sur **POST** pour l'ouvrir
- Passez à l'étape 3

---

## 📋 ÉTAPE 3 : Activer CORS sur POST

1. Vous êtes sur la page de la méthode **POST**
2. En haut à droite, cherchez **"Actions"**
3. Cliquez sur **"Actions"**
4. Dans le menu, cliquez sur **"Activer CORS"** ou **"Enable CORS"**

### Configuration CORS :

1. **Origines autorisées** (Allowed origins) :
   ```
   *
   ```

2. **Méthodes autorisées** (Allowed methods) :
   ```
   POST, OPTIONS
   ```

3. **Headers autorisés** (Allowed headers) :
   ```
   Content-Type, Origin
   ```

4. **Headers exposés** (Exposed headers) :
   ```
   (laissez vide)
   ```

5. **Cochez** : ✅ "Activer CORS et remplacer les valeurs CORS existantes"

6. Cliquez sur **"Activer CORS et remplacer les valeurs CORS existantes"**

---

## 📋 ÉTAPE 4 : Vérifier que OPTIONS a été créé

1. Retournez dans **Ressources**
2. Cliquez sur `/api/payments/create-checkout-session`
3. Vous devez maintenant voir **OPTIONS** dans la liste des méthodes

**Si OPTIONS existe :**
- ✅ Passez à l'étape 5

**Si OPTIONS n'existe pas :**
- Actions > "Créer une méthode" > **OPTIONS**
- Type d'intégration : **Lambda Function**
- Sélectionnez votre fonction Lambda
- **Lambda Proxy integration** : ✅ COCHÉ
- Save
- Activez CORS sur OPTIONS aussi (même configuration)

---

## 📋 ÉTAPE 5 : DÉPLOYER L'API (CRITIQUE !)

1. En haut de l'écran API Gateway (pas dans le panneau de droite)
2. Cherchez le bouton **"Actions"** (en haut, à côté du nom de l'API)
3. Cliquez sur **"Actions"**
4. Dans le menu, cliquez sur **"Déployer l'API"** ou **"Deploy API"**
5. Une fenêtre s'ouvre :
   - **Stage** : Sélectionnez `default` (ou créez un nouveau stage)
   - **Description** : "Activation CORS paiement"
6. Cliquez sur **"Déployer"** ou **"Deploy"**

---

## 📋 ÉTAPE 6 : Attendre et tester

1. **Attendez 30 secondes** après le déploiement
2. Ouvrez `test-routes.html` dans votre navigateur
3. Cliquez sur **"Tester Paiement"**
4. Vérifiez le résultat

---

## ✅ Vérifications finales

### Vérifier que CORS est activé :
1. POST de `/create-checkout-session`
2. Vous devriez voir une **icône CORS** à côté de POST
3. Si vous voyez l'icône → ✅ CORS est activé

### Vérifier que l'API est déployée :
1. En haut de l'écran API Gateway
2. Regardez la **date du dernier déploiement**
3. Si c'est récent (maintenant) → ✅ C'est déployé

---

## 🆘 Si ça ne marche toujours pas

Dites-moi :
1. À quelle étape vous êtes bloqué
2. Ce que vous voyez exactement
3. Si vous voyez l'icône CORS à côté de POST
4. La date du dernier déploiement

Je vous aiderai à résoudre le problème !

---

## 📝 Notes importantes

- ⚠️ **DÉPLOYEZ TOUJOURS** après avoir activé CORS
- ⚠️ **ATTENDEZ 30 SECONDES** après le déploiement
- ⚠️ Les changements ne sont actifs qu'après le déploiement

