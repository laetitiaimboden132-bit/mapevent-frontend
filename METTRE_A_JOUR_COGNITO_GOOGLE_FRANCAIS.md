# 🔧 Mettre à Jour Cognito avec les Valeurs Google - Guide en Français

## 🎯 Objectif

Mettre à jour AWS Cognito avec le Client ID et Client Secret de Google Cloud Console.

---

## 📋 Étape 1 : Obtenir le Client ID et Secret depuis Google Cloud Console

### 1.1 Aller dans Google Cloud Console

1. **Ouvrez votre navigateur**
2. **Allez sur** : https://console.cloud.google.com/
3. **Connectez-vous** avec votre compte Google
4. **Sélectionnez votre projet** en haut

### 1.2 Trouver le Client ID et Secret

1. Menu de gauche → **"APIs et services"** → **"Identifiants"**
2. **Cliquez sur votre Client OAuth** (celui nommé "Mapevent" ou similaire)
3. **En haut de la page**, vous verrez :
   - **Client ID** : quelque chose comme `123456789-abc.apps.googleusercontent.com`
   - **Client secret** : cliquez sur 👁️ pour le voir, quelque chose comme `GOCSPX-xxxxx`

### 1.3 Copier les Valeurs

1. **Sélectionnez le Client ID** avec votre souris
2. **Copiez-le** (Ctrl+C ou clic droit → Copier)
3. **Notez-le** quelque part temporairement
4. **Cliquez sur 👁️** à côté du Client Secret
5. **Sélectionnez le Client Secret** avec votre souris
6. **Copiez-le** (Ctrl+C)
7. **Notez-le** quelque part temporairement

⚠️ **Important** : Le Client Secret ne s'affiche qu'une seule fois. Si vous ne le voyez plus, vous devrez le régénérer (voir plus bas).

---

## 📋 Étape 2 : Aller dans AWS Cognito

1. **Ouvrez un nouvel onglet** dans votre navigateur
2. **Allez sur** : https://console.aws.amazon.com/
3. **Connectez-vous** à votre compte AWS
4. **Cherchez "Cognito"** dans la barre de recherche en haut
5. **Cliquez sur "Cognito"**

---

## 📋 Étape 3 : Trouver votre User Pool

1. Dans le menu de gauche, cliquez sur **"User pools"** (Groupes d'utilisateurs)
2. **Cliquez sur votre User Pool** (celui que vous utilisez pour mapevent)

---

## 📋 Étape 4 : Aller dans les Fournisseurs d'Identité Google

1. Dans le menu de gauche de votre User Pool, cherchez **"Federated identity providers"** (Fournisseurs d'identité fédérés)
2. **Cliquez dessus**
3. Vous verrez une liste avec **"Google"**
4. **Cliquez sur "Google"**

---

## 📋 Étape 5 : Voir les Champs Client ID et Secret

Sur la page Google dans Cognito, vous devriez voir :

- Un champ **"Client ID"** (peut être vide ou avoir une valeur)
- Un champ **"Client secret"** (peut être vide ou avoir une valeur avec des points •••)

Si vous ne voyez pas ces champs, c'est peut-être que :
- Le fournisseur Google n'est pas encore configuré
- Vous êtes sur la mauvaise page

### Si vous ne voyez PAS les champs :

1. **Cherchez un bouton "Edit"** (Modifier) ou **"Configure"** (Configurer)
2. **Cliquez dessus**
3. Les champs devraient apparaître

---

## 📋 Étape 6 : Mettre à Jour le Client ID

1. **Cliquez dans le champ "Client ID"** dans Cognito
2. **Effacez** tout ce qui est dedans (sélectionnez tout avec Ctrl+A puis Suppr)
3. **Collez** le Client ID que vous avez copié depuis Google Cloud Console (Ctrl+V)
4. **Vérifiez** qu'il n'y a pas d'espaces avant ou après

---

## 📋 Étape 7 : Mettre à Jour le Client Secret

1. **Cliquez dans le champ "Client secret"** dans Cognito
2. **Effacez** tout ce qui est dedans (sélectionnez tout avec Ctrl+A puis Suppr)
3. **Collez** le Client Secret que vous avez copié depuis Google Cloud Console (Ctrl+V)
4. **Vérifiez** qu'il n'y a pas d'espaces avant ou après

---

## 📋 Étape 8 : Sauvegarder

1. **Descendez en bas de la page** dans Cognito
2. **Cherchez le bouton "Save"** (Enregistrer) ou **"Save changes"** (Enregistrer les modifications)
3. **Cliquez dessus**
4. Vous devriez voir un message de confirmation

---

## 📋 Étape 9 : Attendre et Tester

1. **Attendez 5 minutes** pour que les changements se propagent
2. **Videz le cache du navigateur** (Ctrl+Shift+Delete)
3. **Fermez tous les onglets** de mapevent.world
4. **Ouvrez un nouvel onglet**
5. **Allez sur** `https://mapevent.world`
6. **Cliquez sur "Continuer avec Google"**
7. **Autorisez** sur la page Google
8. **Vérifiez** si vous êtes redirigé correctement

---

## 🆘 Si vous ne voyez plus le Client Secret dans Google Cloud Console

Si vous ne voyez plus le Client Secret dans Google Cloud Console, vous devez le régénérer :

1. **Retournez dans Google Cloud Console** → Votre Client OAuth
2. **Cherchez un bouton "Reset secret"** (Réinitialiser le secret) ou **"Regenerate"** (Régénérer)
3. **Cliquez dessus**
4. **Confirmez** que vous voulez régénérer le secret
5. Un **nouveau secret** sera créé
6. **Copiez-le immédiatement** (il ne s'affichera qu'une seule fois)
7. **Collez-le dans Cognito** → Google → Client secret
8. **Sauvegardez**

---

## 🆘 Si vous ne voyez pas les champs dans Cognito

Si vous ne voyez pas les champs Client ID et Client Secret dans Cognito :

### Option 1 : Le fournisseur Google n'existe pas encore

1. Dans Cognito → **Federated identity providers**
2. **Cherchez un bouton "Add identity provider"** (Ajouter un fournisseur d'identité) ou **"Create provider"** (Créer un fournisseur)
3. **Sélectionnez "Google"**
4. Les champs Client ID et Client Secret apparaîtront
5. **Collez les valeurs** depuis Google Cloud Console
6. **Sauvegardez**

### Option 2 : Vous êtes sur la mauvaise page

1. **Vérifiez** que vous êtes bien dans : Cognito → User Pool → Federated identity providers → Google
2. **Cherchez un bouton "Edit"** (Modifier) en haut de la page
3. **Cliquez dessus** pour voir les champs

---

## 📝 Résumé des Étapes

1. ✅ **Google Cloud Console** → Copier Client ID et Secret
2. ✅ **AWS Cognito** → User Pool → Federated identity providers → Google
3. ✅ **Coller** le Client ID dans Cognito
4. ✅ **Coller** le Client Secret dans Cognito
5. ✅ **Sauvegarder**
6. ✅ **Attendre 5 minutes**
7. ✅ **Tester**

---

## 💡 Astuce

**Gardez les deux pages ouvertes** (Google Cloud Console et Cognito) dans deux onglets différents pour pouvoir copier-coller facilement.

---

## ❓ Besoin d'aide ?

Si vous avez des problèmes, dites-moi :
- Ce que vous voyez exactement dans Cognito (y a-t-il un bouton "Edit" ?)
- Si les champs Client ID et Secret sont visibles ou non
- Si vous voyez un message d'erreur

Je pourrai vous aider plus précisément !










