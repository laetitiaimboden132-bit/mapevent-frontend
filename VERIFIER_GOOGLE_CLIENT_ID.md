# 🔍 Vérifier et Corriger le Google Client ID dans Cognito

## ❌ Erreur : "The OAuth client was not found" / "invalid_client"

Cette erreur signifie que le **Google Client ID** configuré dans Cognito n'existe pas ou n'est pas valide.

## ✅ Solution : Vérifier le Google Client ID

### Étape 1 : Vérifier dans Google Cloud Console

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Sélectionnez votre projet
3. Allez dans **APIs & Services** > **Credentials**
4. Cherchez vos **OAuth 2.0 Client IDs**
5. Vérifiez que vous avez un Client ID de type **Web application**

### Étape 2 : Vérifier le Client ID dans Cognito

1. Dans AWS Cognito, allez dans **Fournisseurs sociaux et externes** > **Google**
2. Regardez le **ID client d'application**
3. Comparez-le avec celui dans Google Cloud Console

**Ils doivent correspondre exactement !**

### Étape 3 : Si le Client ID ne correspond pas

**Option A : Utiliser un Client ID existant**
1. Dans Google Cloud Console, copiez un Client ID valide
2. Dans Cognito, modifiez Google et collez le bon Client ID
3. Collez aussi le **Secret client** correspondant
4. Enregistrez

**Option B : Créer un nouveau Client ID Google**

1. Dans Google Cloud Console > **Credentials**
2. Cliquez sur **Create Credentials** > **OAuth client ID**
3. Choisissez **Web application**
4. Configurez :
   - **Name** : MapEvent Cognito
   - **Authorized JavaScript origins** :
     ```
     https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com
     ```
   - **Authorized redirect URIs** :
     ```
     https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com/oauth2/idpresponse
     ```
5. Cliquez sur **Create**
6. **Copiez le Client ID** et le **Client Secret**
7. Dans Cognito, modifiez Google et collez ces nouvelles valeurs
8. Enregistrez

### Étape 4 : Vérifier les URLs dans Google Cloud Console

Dans votre OAuth Client ID Google, vérifiez que vous avez :

**Authorized JavaScript origins** :
```
https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com
```

**Authorized redirect URIs** :
```
https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com/oauth2/idpresponse
```

## 🔍 Vérification dans Cognito

Dans **Fournisseurs sociaux et externes** > **Google**, vous devez avoir :

- ✅ **ID client d'application** : Un Client ID valide (format: `xxxxx.apps.googleusercontent.com`)
- ✅ **Secret client d'application** : Le Secret correspondant
- ✅ **Scopes autorisés** : `openid email profile`

## ⚠️ Important

- Le Client ID et le Secret doivent être **exactement les mêmes** dans Cognito et Google Cloud Console
- Les URLs de redirection dans Google Cloud Console doivent inclure le domaine Cognito
- Attendez 2-3 minutes après modification pour la propagation











