# 🆕 Créer un Nouveau Client ID Google - Guide Complet

## 🎯 Objectif

Créer un nouveau Client ID Google depuis zéro pour résoudre l'erreur "The OAuth client was not found".

---

## 🗺️ Navigation Rapide dans Google Cloud Console

**Pour trouver l'OAuth Consent Screen :**
```
Google Cloud Console
  └─ Menu de gauche ☰
      └─ APIs & Services
          └─ OAuth consent screen ← VOUS ÊTES ICI
```

**OU utilisez la barre de recherche en haut :**
- Tapez : `oauth consent`
- Cliquez sur : "OAuth consent screen"

**Pour trouver Credentials :**
```
Google Cloud Console
  └─ Menu de gauche ☰
      └─ APIs & Services
          └─ Credentials ← VOUS ÊTES ICI
```

**OU utilisez la barre de recherche en haut :**
- Tapez : `credentials`
- Cliquez sur : "Credentials"

---

## 📋 Étape 1 : Aller dans Google Cloud Console

1. **Allez sur** : https://console.cloud.google.com/
2. **Connectez-vous** avec votre compte Google (`laetitiaimboden132@gmail.com`)
3. **Sélectionnez votre projet** en haut (ou créez-en un si nécessaire)

---

## 📋 Étape 2 : Aller dans Credentials (ou OAuth Consent Screen)

**Option A : Configurer d'abord l'OAuth Consent Screen (RECOMMANDÉ)**
1. **Menu de gauche** → **"APIs & Services"** → **"OAuth consent screen"**
2. OU **barre de recherche en haut** → tapez `oauth consent` → cliquez sur "OAuth consent screen"
3. Suivez l'**Étape 4** ci-dessous pour le configurer

**Option B : Aller directement dans Credentials**
1. **Dans la barre de recherche en haut**, tapez : `credentials`
2. **Cliquez sur "Credentials"** dans les résultats
3. OU menu de gauche → **"APIs & Services"** → **"Credentials"**
4. Si Google vous demande de configurer l'OAuth Consent Screen, cliquez sur le lien fourni

---

## 📋 Étape 3 : Créer un Nouveau Client ID

1. **En haut de la page**, cliquez sur **"Create Credentials"** (Créer des identifiants)
2. **Sélectionnez "OAuth client ID"** (Identifiant client OAuth)

---

## 📋 Étape 4 : Configurer l'OAuth Consent Screen

⚠️ **IMPORTANT** : Vous DEVEZ configurer l'OAuth Consent Screen AVANT de créer le Client ID !

### Comment accéder à l'OAuth Consent Screen ?

**Méthode 1 : Via le menu de gauche**
1. Dans Google Cloud Console, **menu de gauche** → **"APIs & Services"**
2. Cliquez sur **"OAuth consent screen"** (Écran de consentement OAuth)

**Méthode 2 : Via la barre de recherche**
1. **En haut de la page**, dans la barre de recherche, tapez : `oauth consent`
2. Cliquez sur **"OAuth consent screen"** dans les résultats

**Méthode 3 : Depuis Credentials**
1. Si vous êtes sur la page Credentials et que vous essayez de créer un OAuth client ID
2. Google vous affichera un message : **"To create an OAuth client ID, you must first configure the consent screen"**
3. Cliquez sur le lien **"CONFIGURE CONSENT SCREEN"** (Configurer l'écran de consentement)

---

### ⚠️ PROBLÈME : Les champs sont grisés / Je ne peux pas entrer de données

Si vous voyez l'écran OAuth Consent Screen mais que vous ne pouvez pas entrer de données :

**Solution 1 : Vérifier que vous avez un projet sélectionné**
1. **En haut de la page Google Cloud Console**, regardez le nom du projet (à côté du logo Google Cloud)
2. Si vous voyez **"Select a project"** ou **"No project selected"** :
   - Cliquez dessus
   - **Sélectionnez un projet existant** OU **créez un nouveau projet**
   - Pour créer un nouveau projet : Cliquez sur **"New Project"** → Nom : `Mapevent` → **"Create"**

**Solution 2 : Vérifier que vous êtes le propriétaire du projet**
1. **Menu de gauche** → **"IAM & Admin"** → **"IAM"**
2. Vérifiez que votre email (`laetitiaimboden132@gmail.com`) a le rôle **"Owner"** ou **"Editor"**
3. Si vous n'avez pas les bonnes permissions, vous devez être ajouté comme propriétaire

**Solution 3 : Créer un nouveau projet (RECOMMANDÉ si vous n'avez pas de projet)**
1. **En haut de la page**, cliquez sur le sélecteur de projet (à côté du logo Google Cloud)
2. Cliquez sur **"New Project"** (Nouveau projet)
3. **Project name** : `Mapevent`
4. **Cliquez sur "Create"** (Créer)
5. **Attendez quelques secondes** que le projet soit créé
6. **Sélectionnez ce nouveau projet** dans le sélecteur en haut
7. **Retournez à** "APIs & Services" → "OAuth consent screen"
8. Maintenant vous devriez pouvoir entrer des données !

**Solution 4 : Activer l'API OAuth si nécessaire**
1. **Menu de gauche** → **"APIs & Services"** → **"Library"** (Bibliothèque)
2. **Recherchez** : `Google+ API` ou `Identity Platform API`
3. **Cliquez dessus** → **"Enable"** (Activer)
4. **Retournez à** "OAuth consent screen"

---

Une fois que vous pouvez entrer des données sur la page "OAuth consent screen", configurez-le :

### 4.1 Informations de l'application

**Sur la page "OAuth consent screen", vous verrez soit :**

**A) Un écran avec "User Type" et un bouton "CREATE" (Première configuration)**
- C'est normal ! Vous devez d'abord créer la configuration

**B) Un écran avec des informations déjà remplies (Configuration existante)**
- Cliquez sur **"EDIT APP"** (Modifier l'application) en haut à droite pour modifier

---

**Si c'est la première fois (écran A) :**

1. **User Type** (Type d'utilisateur) : 
   - Sélectionnez **"External"** (Externe) 
   - ⚠️ Si vous voyez "Internal", changez-le en "External"
   - Cliquez sur **"CREATE"** (Créer) ou **"NEXT"** (Suivant)

2. **App information** (Informations de l'application) :
   - **App name** : `Mapevent`
   - **User support email** : `laetitiaimboden132@gmail.com`
   - **App logo** : Laissez vide (optionnel)
   - **Application home page** : `https://mapevent.world`
   - **Application privacy policy link** : Laissez vide (optionnel)
   - **Application terms of service link** : Laissez vide (optionnel)
   - **Authorized domains** : Cliquez sur **"Add Domain"** → Ajoutez `mapevent.world`
   - **Developer contact information** : `laetitiaimboden132@gmail.com`
   - **Cliquez sur "Save and Continue"** (Enregistrer et continuer) en bas de la page

### 4.2 Scopes

1. **Cliquez sur "Add or Remove Scopes"** (Ajouter ou supprimer des portées)
2. **Dans "Manually add scopes"**, ajoutez ces trois scopes un par un :
   - `openid`
   - `email`
   - `profile`
3. **Cliquez sur "Update"** (Mettre à jour)
4. **Cliquez sur "Save and Continue"** (Enregistrer et continuer)

### 4.3 Test users

1. **Cliquez sur "Add Users"** (Ajouter des utilisateurs)
2. **Ajoutez votre email** : `laetitiaimboden132@gmail.com`
3. **Cliquez sur "Add"** (Ajouter)
4. **Cliquez sur "Save and Continue"** (Enregistrer et continuer)

### 4.4 Résumé

1. **Vérifiez** que tout est correct
2. **Cliquez sur "Back to Dashboard"** (Retour au tableau de bord)

---

## 📋 Étape 5 : Créer le Client ID

Maintenant vous pouvez créer le Client ID :

1. **Application type** : Sélectionnez **"Web application"** (Application Web)
2. **Name** : `Mapevent Cognito NEW` (ou un nom de votre choix)
3. **Authorized JavaScript origins** :
   - Cliquez sur **"Add URI"** (Ajouter URI)
   - Collez exactement : `https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com`
   - **Pas de slash à la fin !**
4. **Authorized redirect URIs** :
   - Cliquez sur **"Add URI"** (Ajouter URI)
   - Collez exactement : `https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com/oauth2/idpresponse`
   - **Pas de slash à la fin !**
5. **Cliquez sur "Create"** (Créer)

---

## 📋 Étape 6 : Copier le Client ID et Secret

Une popup va apparaître avec :

- **Your Client ID** : `123456789-abc.apps.googleusercontent.com`
- **Your Client Secret** : `GOCSPX-xxxxxxxxxxxxx`

⚠️ **IMPORTANT** : Le Client Secret ne s'affichera qu'une seule fois !

1. **Copiez le Client ID** (sélectionnez-le et Ctrl+C)
2. **Notez-le** quelque part temporairement
3. **Copiez le Client Secret** (sélectionnez-le et Ctrl+C)
4. **Notez-le** quelque part temporairement
5. **Cliquez sur "OK"** pour fermer la popup

---

## 📋 Étape 7 : Mettre à Jour Cognito

1. **AWS Console** → **Cognito** → Votre User Pool
2. **Federated identity providers** → **Google**
3. **Cliquez sur "Edit"** (Modifier) si nécessaire
4. **Collez le nouveau Client ID** dans le champ "Client ID"
5. **Collez le nouveau Client Secret** dans le champ "Client secret"
6. **Cliquez sur "Save"** (Enregistrer)

---

## 📋 Étape 8 : Mettre à Jour le Code (si nécessaire)

Si vous avez créé un nouveau Client ID et que vous voulez le garder, vérifiez que le Client ID dans le code correspond toujours à celui de Cognito.

Le code utilise actuellement : `63rm6h0m26q41lotbho6704dod`

Si vous utilisez le même App Client Cognito, vous n'avez pas besoin de changer le code.

---

## 📋 Étape 9 : Attendre et Tester

1. **Attendez 10 minutes** pour que les changements se propagent
2. **Videz le cache du navigateur** (Ctrl+Shift+Delete)
3. **Fermez tous les onglets** de mapevent.world
4. **Ouvrez un nouvel onglet en navigation privée** (Ctrl+Shift+N)
5. **Allez sur** `https://mapevent.world`
6. **Ouvrez la console** (F12 → Console)
7. **Cliquez sur "Continuer avec Google"**
8. **Autorisez** sur Google
9. **Regardez les logs** dans la console

---

## ✅ Checklist Complète

- [ ] OAuth Consent Screen configuré avec scopes `openid`, `email`, `profile`
- [ ] Test user ajouté : `laetitiaimboden132@gmail.com`
- [ ] Nouveau Client ID créé avec le nom "Mapevent Cognito NEW"
- [ ] Authorized JavaScript origins : `https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com`
- [ ] Authorized redirect URIs : `https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com/oauth2/idpresponse`
- [ ] Client ID et Secret copiés depuis Google Cloud Console
- [ ] Client ID et Secret collés dans Cognito → Google
- [ ] Cognito sauvegardé
- [ ] Attendu 10 minutes
- [ ] Cache vidé
- [ ] Testé en navigation privée

---

## 🆘 Si l'erreur persiste

Si après avoir créé un nouveau Client ID l'erreur "The OAuth client was not found" persiste :

1. **Vérifiez que vous êtes dans le bon projet Google Cloud** (en haut de la page)
2. **Vérifiez que le Client ID dans Cognito correspond EXACTEMENT** à celui dans Google Cloud Console
3. **Vérifiez que le Client Secret correspond EXACTEMENT**
4. **Vérifiez que les URLs autorisées sont EXACTEMENT** comme indiqué (copiez-collez)
5. **Attendez 15 minutes** (parfois la propagation prend plus de temps)

---

## 📞 Informations de Débogage

Quand vous testez, notez :
- Le **Client ID** affiché dans Google Cloud Console
- Le **Client ID** affiché dans Cognito
- Les **URLs autorisées** dans Google Cloud Console
- Le **message d'erreur exact** dans la console du navigateur

Ces informations aideront à identifier le problème exact.

