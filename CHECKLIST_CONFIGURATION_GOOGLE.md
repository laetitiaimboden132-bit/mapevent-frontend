# ✅ Checklist Complète - Configuration Google OAuth avec Cognito

## 🔍 Vérifications à faire

### 1. Dans Google Cloud Console

**OAuth 2.0 Client ID** :
- ✅ **Authorized JavaScript origins** :
  ```
  https://mapevent.world
  https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com
  ```

- ✅ **Authorized redirect URIs** :
  ```
  https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com/oauth2/idpresponse
  ```

### 2. Dans AWS Cognito - App Client

**Client d'application** : `63rm6h0m26q41lotbho6704dod`
- ✅ **Interface utilisateur hébergée** : Activé
- ✅ **Types d'octroi OAuth** : Octroi de code d'autorisation
- ✅ **Portées OIDC** : openid, email, profile
- ✅ **URL de rappel** : `https://mapevent.world/`

### 3. Dans AWS Cognito - Identity Provider (Google)

**Fournisseurs sociaux et externes** > **Google** :
- ✅ **ID client d'application** : Votre Google Client ID (format: `xxxxx.apps.googleusercontent.com`)
- ✅ **Secret client d'application** : Votre Google Client Secret
- ✅ **Scopes autorisés** : `openid email profile`
- ✅ **Mappage d'attributs** :
  - email → email
  - username → sub
  - name → name (ou attribut personnalisé)
  - picture → picture (optionnel)

### 4. OAuth Consent Screen (Google Cloud Console)

Vérifiez que votre **OAuth consent screen** est configuré :
1. Allez dans **APIs & Services** > **OAuth consent screen**
2. Vérifiez que :
   - **User Type** : External (ou Internal selon votre cas)
   - **App name** : MapEvent
   - **Authorized domains** : `mapevent.world` et `eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com`
   - **Scopes** : `openid`, `email`, `profile`

## ⚠️ Problèmes courants

### Erreur "flowName=GeneralOAuthFlow" sans détails

Cela peut signifier :
1. **OAuth Consent Screen non configuré** : Vérifiez dans Google Cloud Console
2. **Scopes manquants dans Consent Screen** : Ajoutez openid, email, profile
3. **Propagation** : Attendez 5-10 minutes après modifications

### Test direct de l'URL Cognito

Testez directement l'URL Cognito Hosted UI :
```
https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com/login?client_id=63rm6h0m26q41lotbho6704dod&response_type=code&scope=openid+email+profile&redirect_uri=https://mapevent.world/
```

Si cette URL fonctionne et affiche le choix Google, alors le problème vient du code frontend.
Si cette URL ne fonctionne pas, le problème vient de la configuration Cognito.

## 🧪 Test étape par étape

1. **Test de l'URL Cognito directe** (ci-dessus)
2. **Test depuis mapevent.world** : Cliquez sur "Continuer avec Google"
3. **Vérifiez la console** (F12) pour les erreurs détaillées




