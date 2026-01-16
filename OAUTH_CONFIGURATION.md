# 🔐 Configuration OAuth - Google, Facebook, Apple

## 📋 Vue d'ensemble

Ce guide explique comment configurer l'authentification OAuth pour permettre aux utilisateurs de se connecter avec Google, Facebook ou Apple.

## 🔵 Google OAuth

### 1. Créer un projet Google Cloud

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet ou sélectionnez un projet existant
3. Activez l'API "Google+ API" (ou "Google Identity Services")

### 2. Créer des identifiants OAuth 2.0

1. Allez dans **APIs & Services** > **Credentials**
2. Cliquez sur **Create Credentials** > **OAuth client ID**
3. Choisissez **Web application**
4. Configurez :
   - **Name**: MapEventAI
   - **Authorized JavaScript origins**: 
     - `https://mapevent.world`
     - `http://localhost:8000` (pour développement)
   - **Authorized redirect URIs**:
     - `https://mapevent.world`
     - `http://localhost:8000` (pour développement)
5. Copiez le **Client ID** (format: `xxxxx.apps.googleusercontent.com`)

### 3. Configurer dans le code

Ouvrez `public/map_logic.js` et remplacez :

```javascript
const OAUTH_CONFIG = {
  google: {
    clientId: 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com' // ← Remplacez ici
  },
  // ...
};
```

## 📘 Facebook Login

### 1. Créer une application Facebook

1. Allez sur [Facebook Developers](https://developers.facebook.com/)
2. Cliquez sur **My Apps** > **Create App**
3. Choisissez **Consumer** comme type d'application
4. Remplissez les informations de base

### 2. Configurer Facebook Login

1. Dans le tableau de bord de l'application, allez dans **Products** > **Facebook Login** > **Settings**
2. Configurez :
   - **Valid OAuth Redirect URIs**:
     - `https://mapevent.world`
     - `http://localhost:8000` (pour développement)
   - **Deauthorize Callback URL**: `https://mapevent.world`
3. Copiez l'**App ID** et l'**App Secret**

### 3. Configurer dans le code

Ouvrez `public/map_logic.js` et remplacez :

```javascript
const OAUTH_CONFIG = {
  facebook: {
    appId: 'YOUR_FACEBOOK_APP_ID' // ← Remplacez ici
  },
  // ...
};
```

## 🍎 Apple Sign In

### 1. Créer un Service ID Apple

1. Allez sur [Apple Developer](https://developer.apple.com/account/)
2. Allez dans **Certificates, Identifiers & Profiles** > **Identifiers**
3. Créez un nouveau **Services ID**
4. Activez **Sign in with Apple**
5. Configurez les **Return URLs**:
   - `https://mapevent.world`
   - `http://localhost:8000` (pour développement)

### 2. Configurer dans le code

Ouvrez `public/map_logic.js` et remplacez :

```javascript
const OAUTH_CONFIG = {
  apple: {
    clientId: 'YOUR_APPLE_CLIENT_ID' // ← Remplacez ici
  },
  // ...
};
```

## ✅ Vérification

Une fois configuré, les boutons OAuth dans le formulaire d'inscription devraient fonctionner :

1. **Google** : Ouvre la popup Google pour se connecter
2. **Facebook** : Ouvre la popup Facebook pour se connecter
3. **Apple** : Ouvre la popup Apple pour se connecter

## 🔒 Sécurité

- ⚠️ **Ne commitez JAMAIS** les Client IDs dans le code source public
- ✅ Utilisez des variables d'environnement pour la production
- ✅ Limitez les domaines autorisés dans les configurations OAuth
- ✅ Activez la vérification d'email même pour les connexions OAuth

## 📝 Notes

- La vérification d'email est **obligatoire** pour l'inscription par email
- Les connexions OAuth sont automatiquement vérifiées (email vérifié par le fournisseur)
- Les utilisateurs OAuth peuvent toujours ajouter une adresse pour les alertes de proximité














