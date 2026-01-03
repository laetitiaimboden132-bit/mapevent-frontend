# 🔐 Configuration AWS Cognito pour Google Login

## ❌ Erreur actuelle : `invalid_scope`

L'erreur `invalid_scope` signifie que les scopes demandés ne sont pas autorisés dans votre configuration Cognito.

## ✅ Solution : Configurer Cognito correctement

### Étape 1 : Vérifier votre User Pool Cognito

1. Allez sur [AWS Console](https://console.aws.amazon.com/cognito/)
2. Sélectionnez votre User Pool : `eu-west-19o9j6xsdr`
3. Allez dans **App integration** > **App clients**
4. Cliquez sur votre App Client : `63rm6h0m26q41lotbho6704dod`

### Étape 2 : Configurer les OAuth Scopes

Dans la section **Hosted UI** de votre App Client :

1. **OAuth 2.0 grant types** : Cochez :
   - ✅ **Authorization code grant**
   - ✅ **Implicit grant** (optionnel)

2. **OpenID Connect scopes** : Cochez :
   - ✅ **openid** (obligatoire)
   - ✅ **email**
   - ✅ **profile**
   - ✅ **aws.cognito.signin.user.admin** (optionnel, pour certaines opérations)

3. **Allowed callback URLs** : Ajoutez :
   ```
   https://mapevent.world/
   https://mapevent.world
   ```

4. **Allowed sign-out URLs** : Ajoutez :
   ```
   https://mapevent.world/
   https://mapevent.world
   ```

### Étape 3 : Configurer Google comme Identity Provider

1. Dans votre User Pool, allez dans **Sign-in experience** > **Federated identity provider sign-in**
2. Cliquez sur **Add identity provider**
3. Sélectionnez **Google**
4. Configurez :
   - **App client ID** : Votre Google Client ID (format: `xxxxx.apps.googleusercontent.com`)
   - **App client secret** : Votre Google Client Secret
   - **Authorized scopes** : `openid email profile`
   - **Attribute mapping** :
     - `email` → `email`
     - `name` → `name`
     - `picture` → `picture`
     - `sub` → `sub`

### Étape 4 : Vérifier les App Client Settings

Dans **App integration** > **App clients** > Votre App Client :

1. **Hosted UI** : Doit être activé
2. **Callback URLs** : Doit contenir `https://mapevent.world/`
3. **Sign-out URLs** : Doit contenir `https://mapevent.world/`
4. **OAuth flows** : 
   - ✅ Authorization code grant
   - ✅ PKCE (recommandé pour sécurité)

### Étape 5 : Vérifier le Domain Cognito

1. Dans **App integration** > **Domain**
2. Vérifiez que le domaine est : `eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com`
3. Si nécessaire, configurez un domaine personnalisé

## 🔍 Vérification

Après configuration, testez :

1. Allez sur `https://mapevent.world/`
2. Cliquez sur "Créer un compte gratuit"
3. Cliquez sur "Continuer avec Google"
4. Vous devriez être redirigé vers Cognito Hosted UI
5. Sélectionnez Google
6. Autorisez l'application
7. Vous devriez être redirigé vers `https://mapevent.world/` avec un code

## ⚠️ Problèmes courants

### Erreur : `invalid_scope`
- **Cause** : Les scopes ne sont pas activés dans App Client Settings
- **Solution** : Activez `openid`, `email`, `profile` dans OAuth scopes

### Erreur : `redirect_uri_mismatch`
- **Cause** : L'URL de callback ne correspond pas
- **Solution** : Vérifiez que `https://mapevent.world/` est dans Allowed callback URLs

### Erreur : `unauthorized_client`
- **Cause** : Le Client ID n'est pas correct ou l'App Client n'est pas activé
- **Solution** : Vérifiez le Client ID et que Hosted UI est activé

## 📝 Notes importantes

- Les scopes doivent être activés **à la fois** dans :
  1. App Client Settings (OAuth scopes)
  2. Identity Provider (Google) Authorized scopes
- Le domaine Cognito doit être accessible publiquement
- Les URLs de callback doivent correspondre exactement (avec/sans slash final)

## 🆘 Besoin d'aide ?

Si les erreurs persistent :
1. Vérifiez les logs CloudWatch pour votre User Pool
2. Vérifiez la console du navigateur (F12) pour les erreurs détaillées
3. Testez avec l'URL Hosted UI directement : `https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com/login?client_id=63rm6h0m26q41lotbho6704dod&response_type=code&scope=openid+email+profile&redirect_uri=https://mapevent.world/`




