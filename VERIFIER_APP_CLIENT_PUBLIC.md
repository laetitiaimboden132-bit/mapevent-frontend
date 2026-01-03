# 🔍 Vérifier que l'App Client Cognito est Public (sans secret)

## ⚠️ Problème Identifié

L'erreur "invalid_request" peut venir du fait que votre **App Client Cognito a un "Client Secret" activé**.

Pour une **SPA (Single Page Application)** comme votre site, l'App Client **DOIT être "Public"** (sans secret).

Les secrets ne doivent **JAMAIS** être utilisés côté navigateur (ils sont pour les applications backend uniquement).

---

## ✅ Solution : Vérifier et Corriger l'App Client

### Étape 1 : Aller dans Cognito App Clients

1. **AWS Console** → **Cognito** → Votre User Pool
2. **App integration** → **App clients**
3. **Cliquez sur votre App Client** (celui avec l'ID `63rm6h0m26q41lotbho6704dod`)

### Étape 2 : Vérifier le Type d'App Client

Sur la page de votre App Client, cherchez :

- **"Client type"** ou **"App client type"**
- **"Client authentication"** ou **"Authentication flows"**

### Étape 3 : Vérifier si un Secret est Configuré

Cherchez un champ **"Client secret"** :

- **Si vous voyez un Client Secret** (avec des points ••• ou une valeur) :
  - ❌ **PROBLÈME** : Votre App Client n'est pas "Public"
  - Vous devez créer un **nouveau App Client "Public"** (sans secret)

- **Si vous ne voyez PAS de Client Secret** ou il est vide :
  - ✅ **BON** : Votre App Client est "Public"
  - Vous pouvez continuer avec celui-ci

---

## 🔧 Si votre App Client a un Secret : Créer un Nouveau App Client Public

### Option 1 : Créer un Nouveau App Client Public

1. **Cognito** → Votre User Pool → **App integration** → **App clients**
2. **Cliquez sur "Create app client"** (Créer un client d'application)
3. **App client name** : `mapevent-world-public` (ou un nom de votre choix)
4. **⚠️ IMPORTANT** : Décochez **"Generate client secret"** (Générer un secret client)
   - Cette option doit être **DÉSACTIVÉE** pour une SPA
5. **Authentication flows** : Cochez **"Authorization code grant"** (Octroi de code d'autorisation)
6. **OAuth 2.0 grant types** : Cochez **"Authorization code grant"**
7. **OpenID Connect scopes** : Cochez `openid`, `email`, `profile`
8. **Allowed callback URLs** : `https://mapevent.world/`
9. **Allowed sign-out URLs** : (peut être vide)
10. **Cliquez sur "Create app client"** (Créer)

### Option 2 : Mettre à Jour le Code avec le Nouveau Client ID

Une fois le nouveau App Client créé :

1. **Notez le nouveau Client ID** (ex: `nouveau123456789`)
2. **Dans votre code** (`public/map_logic.js`), ligne ~49, remplacez :
   ```javascript
   clientId: "63rm6h0m26q41lotbho6704dod",
   ```
   Par :
   ```javascript
   clientId: "nouveau123456789", // Remplacez par votre nouveau Client ID
   ```
3. **Déployez** : `.\deploy-frontend.ps1`
4. **Testez**

---

## ✅ Vérifications Finales

Votre App Client doit avoir :

- ✅ **Client type** : "Public" (pas de secret)
- ✅ **Authentication flows** : "Authorization code grant" activé
- ✅ **OAuth 2.0 grant types** : "Authorization code grant" activé
- ✅ **OpenID Connect scopes** : `openid`, `email`, `profile` activés
- ✅ **Allowed callback URLs** : `https://mapevent.world/`
- ✅ **PKCE** : Supporté (automatique pour Public Client)

---

## 🧪 Test

Après avoir créé un App Client Public :

1. **Videz le cache du navigateur** (Ctrl+Shift+Delete)
2. **Fermez tous les onglets**
3. **Ouvrez un nouvel onglet**
4. **Allez sur** `https://mapevent.world`
5. **Ouvrez la console** (F12 → Console)
6. **Cliquez sur "Continuer avec Google"**
7. **Regardez les logs** dans la console

Vous devriez voir :
- `🔐 startGoogleLogin() appelé`
- `✅ State OAuth sauvegardé`
- `✅ PKCE verifier sauvegardé`
- Redirection vers Cognito → Google
- Après autorisation : `🔍 handleCognitoCallbackIfPresent() appelé`
- `✅ Tokens reçus`
- `✅ Connecté: [Votre nom]`

---

## 🆘 Si l'erreur persiste

Si après avoir créé un App Client Public l'erreur persiste :

1. **Vérifiez les logs** dans la console du navigateur
2. **Vérifiez que le nouveau Client ID** est bien dans le code et déployé
3. **Vérifiez que PKCE est activé** dans l'App Client (automatique pour Public)
4. **Vérifiez les URLs** dans Google Cloud Console et Cognito

---

## 📝 Résumé

**Le problème principal** : Si votre App Client Cognito a un "Client Secret", il ne peut pas être utilisé depuis le navigateur (SPA).

**La solution** : Créer un App Client "Public" (sans secret) avec PKCE activé.

**Important** : Ne JAMAIS utiliser un App Client avec secret dans une application frontend (SPA).



