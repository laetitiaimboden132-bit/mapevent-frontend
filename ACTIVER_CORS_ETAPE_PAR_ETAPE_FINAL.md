# 🔧 Activer CORS - Guide Étape par Étape FINAL

## 🎯 Objectif
Activer CORS sur `/api/payments/create-checkout-session` pour que le site fonctionne.

## ✅ ÉTAPE PAR ÉTAPE (suivez exactement)

### ÉTAPE 1 : Ouvrir API Gateway

1. Allez sur **AWS Console** (console.aws.amazon.com)
2. Dans la barre de recherche en haut, tapez : **"API Gateway"**
3. Cliquez sur **"API Gateway"**
4. Cliquez sur **votre API** (celle qui contient `j33osy4bvj`)

### ÉTAPE 2 : Aller dans Ressources

1. Dans le menu de gauche, cliquez sur **"Ressources"** (Resources)
2. Vous verrez une arborescence de routes

### ÉTAPE 3 : Naviguer vers la route

1. Cliquez sur **`/api`**
2. Cliquez sur **`/payments`**
3. Cliquez sur **`/create-checkout-session`**
4. Vous verrez les méthodes : **POST** et peut-être **OPTIONS**

### ÉTAPE 4 : Sélectionner POST

1. **Cliquez sur la méthode POST** (pas OPTIONS, pas la ressource `/create-checkout-session`)
2. Le panneau de droite s'ouvre avec les détails de POST

### ÉTAPE 5 : Activer CORS

1. En haut à droite du panneau, cherchez le bouton **"Actions"**
2. Cliquez sur **"Actions"**
3. Dans le menu déroulant, cliquez sur **"Activer CORS"** ou **"Enable CORS"**

### ÉTAPE 6 : Configurer CORS

Un formulaire s'ouvre. Remplissez :

1. **Origines autorisées** (Allowed origins) :
   - Tapez : `*`

2. **Méthodes autorisées** (Allowed methods) :
   - Tapez : `POST, OPTIONS`

3. **Headers autorisés** (Allowed headers) :
   - Tapez : `Content-Type, Origin`

4. **Headers exposés** (Exposed headers) :
   - Laissez vide ou tapez : `*`

5. **Cochez la case** : "Activer CORS et remplacer les valeurs CORS existantes"

6. Cliquez sur le bouton **"Activer CORS et remplacer les valeurs CORS existantes"**

### ÉTAPE 7 : Vérifier OPTIONS

1. Retournez dans **Ressources** > `/api/payments/create-checkout-session`
2. Vérifiez si la méthode **OPTIONS** existe maintenant
3. Si oui → ✅ C'est bon, passez à l'étape 8
4. Si non → Créez-la (voir ci-dessous)

**Si OPTIONS n'existe pas :**
1. Cliquez sur `/create-checkout-session`
2. **Actions** > "Créer une méthode"
3. Sélectionnez **OPTIONS**
4. Type d'intégration : **Lambda Function**
5. Même fonction Lambda que POST
6. **Use Lambda Proxy integration** : ✓
7. Sauvegardez
8. Activez CORS sur OPTIONS aussi (même configuration)

### ÉTAPE 8 : DÉPLOYER L'API (CRITIQUE !)

1. En haut de l'écran API Gateway (pas dans le panneau de droite)
2. Cherchez le bouton **"Actions"** (en haut, à côté du nom de l'API)
3. Cliquez sur **"Actions"**
4. Dans le menu, cliquez sur **"Déployer l'API"** ou **"Deploy API"**
5. Une fenêtre s'ouvre :
   - **Stage** : Sélectionnez `default`
   - **Description** : "Activation CORS paiement"
6. Cliquez sur **"Déployer"** ou **"Deploy"**

### ÉTAPE 9 : Attendre

- Attendez **30 secondes** après le déploiement
- Les changements prennent du temps à se propager

### ÉTAPE 10 : Retester

1. Retestez avec `test-routes.html`
2. La route de paiement devrait maintenant fonctionner !

## ⚠️ Points critiques

1. ✅ **Sélectionnez POST** (pas OPTIONS, pas la ressource)
2. ✅ **DÉPLOYEZ** après avoir activé CORS
3. ✅ **Attendez 30 secondes** après le déploiement
4. ✅ **Vérifiez OPTIONS** existe

## 🔍 Vérifications

### Vérifier que CORS est activé

1. Sélectionnez POST de `/create-checkout-session`
2. Vous devriez voir une **icône CORS** à côté de POST
3. Si vous voyez l'icône → ✅ CORS est activé

### Vérifier que l'API est déployée

1. En haut de l'écran API Gateway
2. Regardez la **date du dernier déploiement**
3. Si c'est récent (maintenant) → ✅ C'est déployé

## 📞 Si ça ne marche toujours pas

Dites-moi :
1. À quelle étape vous êtes bloqué
2. Ce que vous voyez exactement
3. Si vous voyez l'icône CORS à côté de POST
4. La date du dernier déploiement

Je vous aiderai à résoudre le problème !

