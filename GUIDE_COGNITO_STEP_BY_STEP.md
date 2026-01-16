# 🔐 Guide Étape par Étape - Configuration Cognito pour Google Login

## 📍 Où trouver les paramètres dans AWS Cognito

### Étape 1 : Accéder à votre User Pool

1. Allez sur [AWS Cognito Console](https://console.aws.amazon.com/cognito/)
2. Dans le menu de gauche, cliquez sur **User pools**
3. Cliquez sur votre User Pool (celui avec le domaine `eu-west-19o9j6xsdr`)

### Étape 2 : Trouver les App Clients

Dans votre User Pool, vous verrez plusieurs onglets dans le menu de gauche :

- **Users** (utilisateurs)
- **Groups** (groupes) ← Vous êtes peut-être ici
- **App integration** ← **C'EST ICI QU'IL FAUT ALLER !**
- **Sign-in experience**
- **User attributes**
- etc.

**Action :** Cliquez sur **App integration** dans le menu de gauche

### Étape 3 : Configurer l'App Client

Dans **App integration**, vous verrez :

1. **App clients and analytics** → Cliquez dessus
2. Vous verrez votre App Client : `63rm6h0m26q41lotbho6704dod`
3. Cliquez sur le nom de l'App Client (ou sur l'icône d'édition)

### Étape 4 : Activer les OAuth Scopes

Dans la page de l'App Client, cherchez la section **Hosted UI** :

1. **Hosted UI** : Doit être **activé** (toggle ON)

2. **OAuth 2.0 grant types** : Cochez :
   - ✅ **Authorization code grant**
   - (Optionnel) Implicit grant

3. **OpenID Connect scopes** : Cochez **TOUS** :
   - ✅ **openid** (obligatoire)
   - ✅ **email**
   - ✅ **profile**

4. **Allowed callback URLs** : Ajoutez :
   ```
   https://mapevent.world/
   https://mapevent.world
   ```

5. **Allowed sign-out URLs** : Ajoutez :
   ```
   https://mapevent.world/
   https://mapevent.world
   ```

6. Cliquez sur **Save changes**

### Étape 5 : Configurer Google comme Identity Provider

1. Retournez dans le menu de gauche de votre User Pool
2. Cliquez sur **Sign-in experience**
3. Dans **Federated identity provider sign-in**, vous verrez :
   - **Add identity provider** (si Google n'est pas encore configuré)
   - Ou la liste des providers (si Google est déjà là)

**Si Google n'est pas configuré :**
1. Cliquez sur **Add identity provider**
2. Sélectionnez **Google**
3. Remplissez :
   - **App client ID** : Votre Google Client ID (format: `xxxxx.apps.googleusercontent.com`)
   - **App client secret** : Votre Google Client Secret
   - **Authorized scopes** : `openid email profile`
   - **Attribute mapping** :
     - `email` → `email`
     - `name` → `name`
     - `picture` → `picture`
     - `sub` → `sub`
4. Cliquez sur **Save changes**

**Si Google est déjà configuré :**
1. Cliquez sur **Google** dans la liste
2. Vérifiez que les scopes autorisés sont : `openid email profile`
3. Vérifiez l'Attribute mapping

### Étape 6 : Vérifier le Domain

1. Dans **App integration**, cliquez sur **Domain**
2. Vérifiez que le domaine est : `eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com`
3. Si nécessaire, configurez un domaine personnalisé

## ✅ Vérification finale

Après avoir configuré tout ça, testez :

1. Allez sur `https://mapevent.world/`
2. Cliquez sur "Créer un compte gratuit"
3. Cliquez sur "Continuer avec Google"
4. Vous devriez être redirigé vers Cognito Hosted UI
5. Sélectionnez Google
6. Autorisez l'application
7. Vous devriez être redirigé vers `https://mapevent.world/` avec un code

## 🆘 Si vous ne trouvez pas "App integration"

Si vous ne voyez pas **App integration** dans le menu :

1. Vérifiez que vous êtes bien dans un **User Pool** (pas dans Identity Pools)
2. Vérifiez que vous êtes dans la bonne région (eu-west-1)
3. Essayez de rafraîchir la page
4. Vérifiez que vous avez les permissions nécessaires

## 📝 Résumé des paramètres à vérifier

- ✅ **App Client** : `63rm6h0m26q41lotbho6704dod`
- ✅ **Hosted UI** : Activé
- ✅ **OAuth grant types** : Authorization code grant
- ✅ **OAuth scopes** : openid, email, profile
- ✅ **Callback URLs** : `https://mapevent.world/`
- ✅ **Google Identity Provider** : Configuré avec scopes `openid email profile`











