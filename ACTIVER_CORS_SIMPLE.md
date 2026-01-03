# 🔧 Activer CORS - Guide Simple

## 🎯 Objectif
Activer CORS sur `/api/payments/create-checkout-session` pour que le site fonctionne.

## ✅ Étapes SIMPLES

### Étape 1 : Aller dans API Gateway

1. **AWS Console** > Cherchez **"API Gateway"**
2. Cliquez sur **"API Gateway"**
3. Sélectionnez **votre API**

### Étape 2 : Trouver la route

1. Cliquez sur **"Ressources"** (dans le menu de gauche)
2. Cliquez sur **`/api`**
3. Cliquez sur **`/payments`**
4. Cliquez sur **`/create-checkout-session`**
5. Cliquez sur la méthode **POST** (pas OPTIONS)

### Étape 3 : Activer CORS

1. En haut à droite, cherchez **"Actions"** (bouton)
2. Cliquez sur **"Actions"**
3. Dans le menu, cliquez sur **"Activer CORS"** ou **"Enable CORS"**

### Étape 4 : Configurer CORS

Dans le formulaire qui s'ouvre :

1. **Origines autorisées** : Tapez `*`
2. **Méthodes autorisées** : Tapez `POST, OPTIONS`
3. **Headers autorisés** : Tapez `Content-Type, Origin`
4. **Headers exposés** : Laissez vide ou mettez `*`

5. **Cochez** : "Activer CORS et remplacer les valeurs CORS existantes"
6. Cliquez sur **"Activer CORS et remplacer les valeurs CORS existantes"**

### Étape 5 : Vérifier OPTIONS

1. Regardez si la méthode **OPTIONS** a été créée automatiquement
2. Si oui → ✅ C'est bon
3. Si non → Créez-la manuellement (voir ci-dessous)

### Étape 6 : DÉPLOYER (OBLIGATOIRE !)

1. En haut de l'écran API Gateway
2. Cliquez sur **"Actions"** (bouton en haut, pas celui de la méthode)
3. Dans le menu, cliquez sur **"Déployer l'API"** ou **"Deploy API"**
4. **Stage** : Sélectionnez `default`
5. **Description** : "Activation CORS paiement"
6. Cliquez sur **"Déployer"** ou **"Deploy"**

### Étape 7 : Attendre

- Attendez **30 secondes** après le déploiement

### Étape 8 : Retester

1. Retestez avec `test-routes.html`
2. Ça devrait fonctionner maintenant !

## ⚠️ Si OPTIONS n'existe pas

1. Cliquez sur `/create-checkout-session`
2. **Actions** > "Créer une méthode"
3. Sélectionnez **OPTIONS**
4. Liez-la à la même intégration Lambda que POST
5. Activez CORS sur OPTIONS aussi
6. Déployez

## ✅ Checklist

- [ ] Route `/api/payments/create-checkout-session` trouvée
- [ ] Méthode POST sélectionnée
- [ ] CORS activé (Actions > Activer CORS)
- [ ] Origines : `*`
- [ ] Méthodes : `POST, OPTIONS`
- [ ] Headers : `Content-Type, Origin`
- [ ] Méthode OPTIONS créée (automatiquement ou manuellement)
- [ ] API **DÉPLOYÉE** sur stage `default`
- [ ] Attendu 30 secondes
- [ ] Retesté

## 🚨 Points critiques

1. **Sélectionnez POST** (pas OPTIONS, pas la ressource)
2. **DÉPLOYEZ** après avoir activé CORS
3. **Attendez 30 secondes** après le déploiement

## 📞 Si ça ne marche toujours pas

Dites-moi à quelle étape vous êtes bloqué et je vous aiderai !

