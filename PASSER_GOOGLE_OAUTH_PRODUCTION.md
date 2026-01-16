# 🚀 Passer Google OAuth en Mode Production

## 📋 Objectif

Activer Google OAuth en mode **PRODUCTION** pour que **TOUS** les utilisateurs puissent se connecter, pas seulement les utilisateurs de test.

## ⚠️ État Actuel

Votre application Google OAuth est actuellement en mode **TESTING**, ce qui limite l'accès aux seuls utilisateurs de test que vous avez ajoutés.

## ✅ Solution Complète

### Étape 1 : Passer l'Application Google en Production

1. **Allez sur Google Cloud Console** : https://console.cloud.google.com/
2. **Sélectionnez votre projet** (celui avec le Client ID OAuth)
3. **Allez dans "APIs & Services"** → **"OAuth consent screen"**
4. **Vérifiez les informations** :
   - **App name** : MapEvent (ou votre nom)
   - **User support email** : Votre email
   - **Developer contact information** : Votre email
5. **Faites défiler jusqu'à "Publishing status"**
6. **Cliquez sur "PUBLISH APP"** (Publier l'application)
7. **Confirmez** en cliquant sur "CONFIRM"

⚠️ **Important** : Google peut demander une vérification si vous demandez des scopes sensibles. Pour `openid`, `email`, `profile`, c'est généralement automatique.

### Étape 2 : Vérifier les Domaines Autorisés

1. **Dans "OAuth consent screen"**, vérifiez que ces domaines sont listés :
   - `mapevent.world`
   - `eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com` (Cognito)

### Étape 3 : Vérifier les Identifiants OAuth

1. **Allez dans "APIs & Services"** → **"Credentials"**
2. **Trouvez votre OAuth 2.0 Client ID** (celui utilisé dans Cognito)
3. **Vérifiez les "Authorized JavaScript origins"** :
   ```
   https://mapevent.world
   https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com
   ```
4. **Vérifiez les "Authorized redirect URIs"** :
   ```
   https://mapevent.world/
   https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com/oauth2/idpresponse
   ```

### Étape 4 : Créer les Colonnes de Base de Données

Exécutez ce script SQL sur votre base de données PostgreSQL :

```sql
-- Voir le fichier CREER_COLONNES_USERS.sql
```

Ou exécutez directement dans votre base de données :

```powershell
# Se connecter à votre base de données RDS
aws rds describe-db-instances --region eu-west-1 --query "DBInstances[?DBName=='mapevent'].Endpoint.Address" --output text
```

Puis utilisez un client PostgreSQL (pgAdmin, DBeaver, ou psql) pour exécuter le script `CREER_COLONNES_USERS.sql`.

### Étape 5 : Vérifier AWS Cognito

1. **Allez sur AWS Console** → **Cognito**
2. **Sélectionnez votre User Pool**
3. **Allez dans "App integration"** → **"App client"**
4. **Vérifiez que votre App Client est "Public"** (pas Confidential)
5. **Vérifiez les "Allowed callback URLs"** :
   ```
   https://mapevent.world/
   ```
6. **Vérifiez les "Allowed sign-out URLs"** :
   ```
   https://mapevent.world/
   ```
7. **Dans "Sign-in experience"** → **"Federated identity provider sign-in"**, vérifiez que **Google** est activé

### Étape 6 : Tester la Connexion

1. **Videz le cache du navigateur** (Ctrl+Shift+Delete)
2. **Allez sur https://mapevent.world**
3. **Cliquez sur "Compte"** → **"Connexion avec Google"**
4. **Connectez-vous avec n'importe quel compte Google** (pas seulement les utilisateurs de test)
5. **Le formulaire d'inscription MapEvent devrait s'afficher**

## 🔍 Vérification PowerShell

Pour vérifier rapidement si votre application est en production :

```powershell
# Vérifier les logs CloudWatch après une tentative de connexion
aws logs tail /aws/lambda/mapevent-backend --since 2m --region eu-west-1 --format short --filter-pattern "ERROR"
```

## ✅ Checklist Finale

- [ ] Application Google OAuth publiée (mode Production)
- [ ] Domaines autorisés configurés correctement
- [ ] Colonnes de base de données créées (voir CREER_COLONNES_USERS.sql)
- [ ] AWS Cognito configuré avec les bonnes URLs
- [ ] Test de connexion réussi avec un compte Google quelconque

## 🆘 Si ça ne fonctionne toujours pas

1. **Vérifiez les logs CloudWatch** pour voir l'erreur exacte
2. **Vérifiez que l'application Google est bien en "Production"** (pas "Testing")
3. **Attendez 5-10 minutes** après avoir publié l'application (propagation Google)
4. **Vérifiez que le Client ID dans Cognito correspond** à celui dans Google Cloud Console

## 📞 Support

Si vous avez besoin d'aide supplémentaire, envoyez-moi :
- Les logs CloudWatch récents
- Une capture d'écran de la page "OAuth consent screen" dans Google Cloud Console
- Une capture d'écran de la configuration Cognito









