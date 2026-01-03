# 🔧 Corriger l'erreur Google OAuth dans Cognito

## ❌ Erreur actuelle : "The OAuth client was not found"

Cette erreur signifie que le **Google Client ID** configuré dans Cognito n'est pas valide ou n'existe pas.

## ✅ Solution : Vérifier et corriger la configuration Google

### Étape 1 : Vérifier votre Google Client ID

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Sélectionnez votre projet
3. Allez dans **APIs & Services** > **Credentials**
4. Vérifiez que vous avez un **OAuth 2.0 Client ID** de type **Web application**
5. **Copiez le Client ID** (format: `xxxxx.apps.googleusercontent.com`)
6. **Copiez le Client Secret**

### Étape 2 : Configurer Google dans Cognito

1. Dans AWS Cognito, allez dans votre **User Pool**
2. Cliquez sur **Expérience de connexion** (Sign-in experience)
3. Dans **Connexion avec fournisseur d'identité fédéré**, cliquez sur **Google**

**Si Google n'est pas configuré :**
1. Cliquez sur **Ajouter un fournisseur d'identité**
2. Sélectionnez **Google**
3. Remplissez :
   - **ID client d'application** : Collez votre Google Client ID
   - **Secret client d'application** : Collez votre Google Client Secret
   - **Scopes autorisés** : `openid email profile`
   - **Mappage d'attributs** :
     - `email` → `email`
     - `name` → `name`
     - `picture` → `picture`
     - `sub` → `sub`
4. Cliquez sur **Enregistrer les modifications**

**Si Google est déjà configuré :**
1. Cliquez sur **Google** dans la liste
2. Vérifiez que :
   - **ID client d'application** correspond à votre Google Client ID
   - **Secret client d'application** correspond à votre Google Client Secret
   - **Scopes autorisés** contient : `openid email profile`
3. Si nécessaire, modifiez et **Enregistrez les modifications**

### Étape 3 : Vérifier les URLs autorisées dans Google

Dans Google Cloud Console > Credentials > votre OAuth Client ID :

1. **Authorized JavaScript origins** : Ajoutez :
   ```
   https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com
   ```

2. **Authorized redirect URIs** : Ajoutez :
   ```
   https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com/oauth2/idpresponse
   ```

### Étape 4 : Attendre la propagation

Après avoir modifié les paramètres dans Cognito :
- Attendez **2-5 minutes** pour que les changements soient propagés
- Videz le cache de votre navigateur (Ctrl+Shift+R)
- Testez à nouveau

## 🔍 Vérification finale

Vérifiez que vous avez :

✅ **Dans Cognito App Client** :
- Scopes OIDC : openid, email, profile
- Types d'octroi : Octroi de code d'autorisation
- Callback URL : https://mapevent.world/

✅ **Dans Cognito Identity Provider (Google)** :
- ID client d'application : Votre Google Client ID valide
- Secret client d'application : Votre Google Client Secret valide
- Scopes autorisés : `openid email profile`

✅ **Dans Google Cloud Console** :
- Authorized redirect URIs : `https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com/oauth2/idpresponse`

## 🆘 Si vous n'avez pas de Google Client ID

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet ou sélectionnez un projet existant
3. Activez l'API "Google+ API" ou "Google Identity Services"
4. Créez des identifiants OAuth 2.0 :
   - Type : Web application
   - Name : MapEvent
   - Authorized JavaScript origins : `https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com`
   - Authorized redirect URIs : `https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com/oauth2/idpresponse`
5. Copiez le Client ID et le Client Secret
6. Configurez-les dans Cognito comme décrit ci-dessus




