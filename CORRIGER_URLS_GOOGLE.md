# 🔧 Corriger les URLs de Redirection Google

## ❌ Erreur : "flowName=GeneralOAuthFlow"

Cette erreur signifie généralement que les **URLs de redirection** dans Google Cloud Console ne sont pas correctement configurées.

## ✅ Solution : Configurer les URLs dans Google Cloud Console

### Étape 1 : Aller dans Google Cloud Console

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Sélectionnez votre projet
3. Allez dans **APIs & Services** > **Credentials**
4. Cliquez sur votre **OAuth 2.0 Client ID** (celui que vous utilisez dans Cognito)

### Étape 2 : Configurer les URLs autorisées

Dans la page de votre Client ID, vous verrez deux sections :

#### 1. **Authorized JavaScript origins**

Cliquez sur **"Add URI"** et ajoutez :
```
https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com
```

#### 2. **Authorized redirect URIs**

Cliquez sur **"Add URI"** et ajoutez **EXACTEMENT** :
```
https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com/oauth2/idpresponse
```

⚠️ **IMPORTANT** : L'URL de redirection doit être **exactement** celle-ci, avec le chemin `/oauth2/idpresponse` à la fin.

### Étape 3 : Sauvegarder

1. Cliquez sur **"Save"** en bas de la page
2. Attendez quelques secondes pour la propagation

### Étape 4 : Vérifier dans Cognito

Dans AWS Cognito > **Fournisseurs sociaux et externes** > **Google**, vérifiez que :
- ✅ **ID client d'application** : Votre Google Client ID
- ✅ **Secret client d'application** : Votre Google Client Secret
- ✅ **Scopes autorisés** : `openid email profile`

## 🔍 Vérification complète

### Dans Google Cloud Console :
- ✅ **Authorized JavaScript origins** : `https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com`
- ✅ **Authorized redirect URIs** : `https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com/oauth2/idpresponse`

### Dans Cognito :
- ✅ **Client d'application** : Scopes OIDC (openid, email, profile)
- ✅ **Google Identity Provider** : Client ID et Secret corrects, scopes `openid email profile`

## ⚠️ Erreurs courantes

1. **URL de redirection incorrecte** : Doit être `/oauth2/idpresponse` et non `/oauth2/token` ou autre
2. **HTTPS manquant** : Toutes les URLs doivent commencer par `https://`
3. **Trailing slash** : Ne pas mettre de `/` à la fin de l'URL de redirection
4. **Propagation** : Attendre 2-3 minutes après modification

## 🧪 Test

Après avoir configuré les URLs :
1. Attendez 2-3 minutes
2. Videz le cache du navigateur (Ctrl+Shift+R)
3. Testez la connexion Google sur mapevent.world




