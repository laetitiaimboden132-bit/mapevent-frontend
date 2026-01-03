# 🔐 Configuration OAuth - Guide Simple

## 🎯 Objectif

Activer les connexions Google et Facebook pour que vos utilisateurs puissent se connecter rapidement.

## ⚡ Étapes Rapides

### 1️⃣ Google OAuth (5 minutes)

1. Allez sur https://console.cloud.google.com/
2. Créez un projet (ou utilisez un existant)
3. Allez dans **APIs & Services** > **Credentials**
4. Cliquez **Create Credentials** > **OAuth client ID**
5. Choisissez **Web application**
6. Configurez :
   - **Name**: MapEventAI
   - **Authorized JavaScript origins**: `https://mapevent.world`
   - **Authorized redirect URIs**: `https://mapevent.world`
7. **Copiez le Client ID** (ex: `123456789-abc.apps.googleusercontent.com`)

### 2️⃣ Facebook Login (5 minutes)

1. Allez sur https://developers.facebook.com/
2. Cliquez **My Apps** > **Create App**
3. Choisissez **Consumer**
4. Allez dans **Settings** > **Basic**
5. **Copiez l'App ID**

### 3️⃣ Configurer dans le Code

Ouvrez `public/map_logic.js` et cherchez (ligne ~17208) :

```javascript
const OAUTH_CONFIG = {
  google: {
    clientId: 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com'
  },
  facebook: {
    appId: 'YOUR_FACEBOOK_APP_ID'
  }
};
```

**Remplacez** :
- `YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com` → Votre Client ID Google
- `YOUR_FACEBOOK_APP_ID` → Votre App ID Facebook

### 4️⃣ Déployer

```powershell
.\deploy-frontend.ps1
```

## ✅ C'est tout !

Les boutons Google et Facebook apparaîtront automatiquement dans le formulaire d'inscription.

## 🆘 Besoin d'aide ?

- Guide détaillé : `OAUTH_CONFIGURATION.md`
- Problème ? Vérifiez que les domaines autorisés sont bien `https://mapevent.world`







