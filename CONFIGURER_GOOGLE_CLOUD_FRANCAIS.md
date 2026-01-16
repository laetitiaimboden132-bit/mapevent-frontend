# 🔐 Configurer Google Cloud Console - Guide en Français

## 🎯 Objectif

Configurer Google Cloud Console pour que la connexion Google fonctionne avec AWS Cognito.

---

## 📋 Étape 1 : Aller dans Google Cloud Console

1. **Ouvrez votre navigateur**
2. **Allez sur** : https://console.cloud.google.com/
3. **Connectez-vous** avec votre compte Google (`laetitia.imboden132@gmail.com` ou `laetitiaimboden132@gmail.com`)
4. **Sélectionnez votre projet** (ou créez-en un si vous n'en avez pas)

---

## 📋 Étape 2 : Aller dans les Credentials (Identifiants)

1. Dans le menu de gauche, cliquez sur **"APIs & Services"** (APIs et services)
2. Cliquez sur **"Credentials"** (Identifiants)
3. Vous verrez la liste de vos identifiants OAuth

---

## 📋 Étape 3 : Vérifier ou Créer un OAuth Client ID

### Option A : Si vous avez déjà un Client ID

1. **Cliquez sur votre OAuth 2.0 Client ID** (celui qui est configuré dans Cognito)
2. **Notez le Client ID** (ex: `123456789-abc.apps.googleusercontent.com`)
3. **Passez à l'Étape 4**

### Option B : Si vous n'avez pas de Client ID ou voulez en créer un nouveau

1. Cliquez sur **"Create Credentials"** (Créer des identifiants) en haut de la page
2. Sélectionnez **"OAuth client ID"** (Identifiant client OAuth)
3. Si c'est la première fois, vous devrez configurer l'**OAuth Consent Screen** :
   - **User Type** : Choisissez **"External"** (Externe)
   - Cliquez sur **"Create"** (Créer)
   - **App name** : `mapevent` (ou votre nom)
   - **User support email** : Votre email (`laetitia.imboden132@gmail.com`)
   - **Developer contact information** : Votre email (`laetitia.imboden132@gmail.com`)
   - Cliquez sur **"Save and Continue"** (Enregistrer et continuer)
   - **Scopes** : Cliquez sur **"Add or Remove Scopes"**
     - Cochez : `openid`, `email`, `profile`
     - Cliquez sur **"Update"** (Mettre à jour)
   - Cliquez sur **"Save and Continue"** (Enregistrer et continuer)
   - **Test users** : Si vous êtes en mode "Testing", ajoutez votre email
   - Cliquez sur **"Save and Continue"** (Enregistrer et continuer)
   - Cliquez sur **"Back to Dashboard"** (Retour au tableau de bord)

4. **Créer le Client ID** :
   - **Application type** : Sélectionnez **"Web application"** (Application Web)
   - **Name** : `MapEvent Cognito` (ou un nom de votre choix)
   - Cliquez sur **"Create"** (Créer)
   - **Copiez le Client ID** (ex: `123456789-abc.apps.googleusercontent.com`)
   - **Copiez le Client Secret** (cliquez sur l'icône 👁️ pour le voir)

---

## 📋 Étape 4 : Configurer les URLs Autorisées

**C'est la partie la plus importante !**

Dans la page de votre OAuth Client ID, vous devez configurer **exactement** ces URLs :

### Authorized JavaScript origins (Origines JavaScript autorisées)

Cliquez sur **"Add URI"** (Ajouter URI) et ajoutez **exactement** :

```
https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com
```

⚠️ **IMPORTANT** :
- Pas de slash (`/`) à la fin
- Pas d'espaces avant ou après
- Commence par `https://`
- Copiez-collez pour éviter les erreurs de frappe

### Authorized redirect URIs (URI de redirection autorisées)

Cliquez sur **"Add URI"** (Ajouter URI) et ajoutez **exactement** :

```
https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com/oauth2/idpresponse
```

⚠️ **IMPORTANT** :
- Pas de slash (`/`) à la fin
- Pas d'espaces avant ou après
- Le chemin exact : `/oauth2/idpresponse`
- Commence par `https://`
- Copiez-collez pour éviter les erreurs de frappe

### Optionnel : Ajouter aussi votre site

Vous pouvez aussi ajouter (optionnel) :

```
https://mapevent.world
```

---

## 📋 Étape 5 : Sauvegarder

1. Cliquez sur **"Save"** (Enregistrer) en bas de la page
2. **Attendez 5 minutes** pour que les changements se propagent

---

## 📋 Étape 6 : Configurer dans AWS Cognito

1. **AWS Console** → **Cognito** → Votre User Pool
2. **Federated identity providers** → **Google**
3. **Collez le Client ID** depuis Google Cloud Console
4. **Collez le Client Secret** depuis Google Cloud Console
5. Cliquez sur **"Save"** (Enregistrer)

---

## 📋 Étape 7 : Vérifier Cognito App Client Settings

1. **AWS Console** → **Cognito** → Votre User Pool
2. **App integration** → **App clients** → Votre client
3. **Hosted UI** → Vérifiez que :
   - ✅ **Allowed callback URLs** contient : `https://mapevent.world/`
   - ✅ **OAuth grant types** : `Authorization code grant` est coché
   - ✅ **OpenID Connect scopes** : `openid`, `email`, `profile` sont cochés

---

## ✅ Checklist Complète

Avant de tester, vérifiez que vous avez :

- [ ] Client ID créé dans Google Cloud Console
- [ ] Client Secret copié depuis Google Cloud Console
- [ ] Authorized JavaScript origins : `https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com`
- [ ] Authorized redirect URIs : `https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com/oauth2/idpresponse`
- [ ] OAuth Consent Screen configuré avec scopes `openid`, `email`, `profile`
- [ ] Client ID collé dans Cognito
- [ ] Client Secret collé dans Cognito
- [ ] Cognito App Client : Callback URL = `https://mapevent.world/`
- [ ] Attendu 5 minutes après les modifications
- [ ] Cache du navigateur vidé (Ctrl+Shift+Delete)

---

## 🧪 Tester

1. **Videz le cache du navigateur** (Ctrl+Shift+Delete)
2. Allez sur `https://mapevent.world`
3. Cliquez sur **"Continuer avec Google"**
4. Autorisez sur la page Google
5. Vous devriez être redirigé vers mapevent.world et voir le formulaire de création d'avatar

---

## 🆘 Si ça ne fonctionne toujours pas

1. **Vérifiez les logs du navigateur** (F12 → Console)
2. **Vérifiez que les URLs sont EXACTEMENT comme indiqué** (copiez-collez)
3. **Attendez 10 minutes** après les modifications
4. **Testez avec un autre navigateur** (Chrome, Firefox, Safari)
5. **Vérifiez que vous êtes connecté avec le bon compte Google** dans Google Cloud Console

---

## 📞 Besoin d'aide ?

Si vous avez des problèmes, notez :
- Le **message d'erreur exact** dans la console du navigateur
- Les **URLs configurées** dans Google Cloud Console
- Le **statut de l'OAuth Consent Screen** (Testing ou In production)

Ces informations aideront à identifier le problème exact.










