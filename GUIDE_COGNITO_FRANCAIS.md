# 🔐 Guide Configuration Cognito en Français - Connexion Google

## 📍 Navigation dans Cognito (Interface Française)

### Étape 1 : Accéder à votre User Pool

1. Allez sur [AWS Console Cognito](https://console.aws.amazon.com/cognito/)
2. Dans le menu de gauche, cliquez sur **Pools d'utilisateurs** (User pools)
3. Cliquez sur votre User Pool (celui avec le domaine `eu-west-19o9j6xsdr`)

### Étape 2 : Trouver les Applications Client

Dans votre User Pool, vous verrez plusieurs onglets dans le menu de gauche :

- **Utilisateurs** (Users)
- **Groupes** (Groups) ← Vous êtes peut-être ici
- **Intégration d'application** ← **C'EST ICI QU'IL FAUT ALLER !**
- **Expérience de connexion** (Sign-in experience)
- **Attributs utilisateur** (User attributes)
- etc.

**Action :** Cliquez sur **Intégration d'application** dans le menu de gauche

### Étape 3 : Configurer l'Application Client

Dans **Intégration d'application**, vous verrez :

1. **Applications client et analyses** → Cliquez dessus
2. Vous verrez votre Application Client : `63rm6h0m26q41lotbho6704dod`
3. Cliquez sur le nom de l'Application Client (ou sur l'icône d'édition)

### Étape 4 : Activer les Scopes OAuth

Dans la page de l'Application Client, cherchez la section **Interface utilisateur hébergée** :

1. **Interface utilisateur hébergée** : Doit être **activé** (bascule ON)

2. **Types d'octroi OAuth 2.0** : Cochez :
   - ✅ **Octroi de code d'autorisation** (Authorization code grant)
   - (Optionnel) Octroi implicite (Implicit grant)

3. **Scopes OpenID Connect** : Cochez **TOUS** :
   - ✅ **openid** (obligatoire)
   - ✅ **email**
   - ✅ **profile**

4. **URL de rappel autorisées** : Ajoutez :
   ```
   https://mapevent.world/
   https://mapevent.world
   ```

5. **URL de déconnexion autorisées** : Ajoutez :
   ```
   https://mapevent.world/
   https://mapevent.world
   ```

6. Cliquez sur **Enregistrer les modifications** (Save changes)

### Étape 5 : Configurer Google comme Fournisseur d'Identité

1. Retournez dans le menu de gauche de votre User Pool
2. Cliquez sur **Expérience de connexion** (Sign-in experience)
3. Dans **Connexion avec fournisseur d'identité fédéré**, vous verrez :
   - **Ajouter un fournisseur d'identité** (si Google n'est pas encore configuré)
   - Ou la liste des fournisseurs (si Google est déjà là)

**Si Google n'est pas configuré :**
1. Cliquez sur **Ajouter un fournisseur d'identité**
2. Sélectionnez **Google**
3. Remplissez :
   - **ID client d'application** : Votre Google Client ID (format: `xxxxx.apps.googleusercontent.com`)
   - **Secret client d'application** : Votre Google Client Secret
   - **Scopes autorisés** : `openid email profile`
   - **Mappage d'attributs** :
     - `email` → `email`
     - `name` → `name`
     - `picture` → `picture`
     - `sub` → `sub`
4. Cliquez sur **Enregistrer les modifications**

**Si Google est déjà configuré :**
1. Cliquez sur **Google** dans la liste
2. Vérifiez que les scopes autorisés sont : `openid email profile`
3. Vérifiez le Mappage d'attributs

### Étape 6 : Vérifier le Domaine

1. Dans **Intégration d'application**, cliquez sur **Domaine**
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

## 🆘 Si vous ne trouvez pas "Intégration d'application"

Si vous ne voyez pas **Intégration d'application** dans le menu :

1. Vérifiez que vous êtes bien dans un **Pool d'utilisateurs** (pas dans Pools d'identité)
2. Vérifiez que vous êtes dans la bonne région (eu-west-1)
3. Essayez de rafraîchir la page
4. Vérifiez que vous avez les permissions nécessaires

## 📝 Résumé des paramètres à vérifier

- ✅ **Application Client** : `63rm6h0m26q41lotbho6704dod`
- ✅ **Interface utilisateur hébergée** : Activé
- ✅ **Types d'octroi OAuth** : Octroi de code d'autorisation
- ✅ **Scopes OAuth** : openid, email, profile
- ✅ **URL de rappel** : `https://mapevent.world/`
- ✅ **Fournisseur d'identité Google** : Configuré avec scopes `openid email profile`

## 🎯 Chemin complet dans l'interface

```
AWS Console → Cognito → Pools d'utilisateurs → [Votre Pool]
  → Intégration d'application (menu gauche)
    → Applications client et analyses
      → [63rm6h0m26q41lotbho6704dod]
        → Section "Interface utilisateur hébergée"
          → Cocher les scopes : openid, email, profile
          → Ajouter callback URL : https://mapevent.world/
          → Enregistrer les modifications
```




