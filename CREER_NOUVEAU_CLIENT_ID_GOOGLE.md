# 🆕 Créer un Nouveau Client ID Google - Guide Simple

## 🎯 Objectif

Créer un nouveau Client ID Google depuis zéro avec toutes les bonnes configurations.

---

## 📋 Étape 1 : Aller dans Google Cloud Console

1. **Allez sur** : https://console.cloud.google.com/
2. **Connectez-vous** avec votre compte Google
3. **Sélectionnez votre projet** en haut

---

## 📋 Étape 2 : Aller dans Credentials

1. **Dans la barre de recherche en haut**, tapez : `credentials`
2. **Cliquez sur "Credentials"** dans les résultats
3. OU menu de gauche → **"APIs & Services"** → **"Credentials"**

---

## 📋 Étape 3 : Créer un Nouveau Client ID

1. **En haut de la page**, cliquez sur **"Create Credentials"** (Créer des identifiants)
2. **Sélectionnez "OAuth client ID"** (Identifiant client OAuth)

---

## 📋 Étape 4 : Configurer l'OAuth Consent Screen (si demandé)

Si c'est la première fois, Google vous demandera de configurer l'OAuth Consent Screen :

1. **User Type** : Sélectionnez **"External"** (Externe)
2. **Cliquez sur "Create"** (Créer)

### Étape 4.1 : Informations de l'application

1. **App name** : `Mapevent`
2. **User support email** : Votre email (`laetitia.imboden132@gmail.com`)
3. **App logo** : Laissez vide (optionnel)
4. **Application home page** : `https://mapevent.world`
5. **Application privacy policy link** : Laissez vide (optionnel)
6. **Application terms of service link** : Laissez vide (optionnel)
7. **Authorized domains** : Ajoutez `mapevent.world`
8. **Developer contact information** : Votre email (`laetitia.imboden132@gmail.com`)
9. **Cliquez sur "Save and Continue"** (Enregistrer et continuer)

### Étape 4.2 : Scopes

1. **Cliquez sur "Add or Remove Scopes"** (Ajouter ou supprimer des portées)
2. **Dans "Manually add scopes"**, ajoutez ces trois scopes un par un :
   - `openid`
   - `email`
   - `profile`
3. **Cliquez sur "Update"** (Mettre à jour)
4. **Cliquez sur "Save and Continue"** (Enregistrer et continuer)

### Étape 4.3 : Test users (si en mode Testing)

1. **Cliquez sur "Add Users"** (Ajouter des utilisateurs)
2. **Ajoutez votre email** : `laetitia.imboden132@gmail.com`
3. **Cliquez sur "Add"** (Ajouter)
4. **Cliquez sur "Save and Continue"** (Enregistrer et continuer)

### Étape 4.4 : Résumé

1. **Vérifiez** que tout est correct
2. **Cliquez sur "Back to Dashboard"** (Retour au tableau de bord)

---

## 📋 Étape 5 : Créer le Client ID

Maintenant vous pouvez créer le Client ID :

1. **Application type** : Sélectionnez **"Web application"** (Application Web)
2. **Name** : `Mapevent Cognito NEW`
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

## 📋 Étape 8 : Attendre et Tester

1. **Attendez 10 minutes** pour que les changements se propagent
2. **Videz le cache du navigateur** (Ctrl+Shift+Delete)
3. **Fermez tous les onglets** de mapevent.world
4. **Ouvrez un nouvel onglet**
5. **Allez sur** `https://mapevent.world`
6. **Cliquez sur "Continuer avec Google"**
7. **Testez**

---

## ✅ Checklist

- [ ] OAuth Consent Screen configuré avec scopes `openid`, `email`, `profile`
- [ ] Test user ajouté si en mode Testing
- [ ] Nouveau Client ID créé avec le nom "Mapevent Cognito NEW"
- [ ] Authorized JavaScript origins : `https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com`
- [ ] Authorized redirect URIs : `https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com/oauth2/idpresponse`
- [ ] Client ID et Secret copiés depuis Google Cloud Console
- [ ] Client ID et Secret collés dans Cognito
- [ ] Cognito sauvegardé
- [ ] Attendu 10 minutes
- [ ] Cache vidé
- [ ] Testé

---

## 🆘 Si ça ne fonctionne toujours pas

Si après avoir créé un nouveau Client ID ça ne fonctionne toujours pas, le problème peut venir d'autre part. Dans ce cas, envoyez-moi :
- Le message d'erreur exact dans la console du navigateur
- Une capture d'écran de la page Google Cloud Console avec le nouveau Client ID
- Une capture d'écran de la page Cognito avec le nouveau Client ID



