# 🔍 Vérifier la Configuration Google OAuth

## ❌ Erreur "flowName=GeneralOAuthFlow"

Cette erreur indique que Google essaie de traiter votre requête OAuth mais échoue. Voici comment vérifier et corriger :

---

## ✅ Étape 1 : Vérifier Google Cloud Console

### 1.1 Aller dans Google Cloud Console

1. Allez sur https://console.cloud.google.com/
2. Sélectionnez votre projet (ou créez-en un)
3. Allez dans **APIs & Services** > **Credentials**

### 1.2 Vérifier le Client ID OAuth

1. Trouvez votre **OAuth 2.0 Client ID** (celui configuré dans Cognito)
2. Cliquez dessus pour voir les détails
3. **Vérifiez que ces URLs sont EXACTEMENT configurées :**

#### Authorized JavaScript origins :
```
https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com
```

#### Authorized redirect URIs :
```
https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com/oauth2/idpresponse
```

⚠️ **IMPORTANT** : Ces URLs doivent être **EXACTEMENT** comme ci-dessus, sans slash final supplémentaire.

---

## ✅ Étape 2 : Vérifier OAuth Consent Screen

### 2.1 Aller dans OAuth Consent Screen

1. Dans Google Cloud Console → **APIs & Services** > **OAuth consent screen**
2. Vérifiez que :
   - **App name** : `mapevent` (ou votre nom d'app)
   - **User support email** : Votre email
   - **Developer contact information** : Votre email

### 2.2 Vérifier les Scopes

Dans **Scopes**, vous devez avoir :
- ✅ `openid`
- ✅ `email`
- ✅ `profile`

### 2.3 Vérifier le Statut de Publication

- Si **"Testing"** : Ajoutez votre email (`laetitiaimboden132@gmail.com`) dans **Test users**
- Si **"In production"** : Pas besoin de test users

---

## ✅ Étape 3 : Vérifier AWS Cognito

### 3.1 Vérifier le Client ID et Secret

1. AWS Console → **Cognito** → Votre User Pool
2. **Federated identity providers** → **Google**
3. Vérifiez que :
   - **Client ID** : Correspond au Client ID de Google Cloud Console
   - **Client secret** : Correspond au Secret de Google Cloud Console

### 3.2 Vérifier les App Client Settings

1. **App integration** → **App clients** → Votre client
2. **Hosted UI** → Vérifiez :
   - ✅ **Allowed callback URLs** : `https://mapevent.world/`
   - ✅ **Allowed sign-out URLs** : (peut être vide)
   - ✅ **OAuth grant types** : `Authorization code grant`
   - ✅ **OpenID Connect scopes** : `openid`, `email`, `profile`

---

## 🔧 Solution si l'erreur persiste

### Option 1 : Vérifier les logs du navigateur

1. Ouvrez la console du navigateur (F12)
2. Cliquez sur "Continuer avec Google"
3. Regardez les logs qui commencent par `🔐`
4. Copiez l'URL complète affichée et vérifiez qu'elle est correcte

### Option 2 : Tester directement l'URL Cognito

Testez cette URL directement dans votre navigateur (remplacez les valeurs si nécessaire) :

```
https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com/oauth2/authorize?client_id=63rm6h0m26q41lotbho6704dod&response_type=code&scope=openid%20email%20profile&redirect_uri=https%3A%2F%2Fmapevent.world%2F
```

Si cette URL fonctionne, le problème vient du code frontend.
Si cette URL ne fonctionne pas, le problème vient de la configuration Cognito/Google.

### Option 3 : Vérifier les domaines autorisés

Dans Google Cloud Console → **OAuth consent screen** → **Authorized domains**, vous devez avoir :
- ✅ `mapevent.world`
- ✅ `eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com`

---

## 📝 Checklist Complète

- [ ] Client ID Google correct dans Cognito
- [ ] Client Secret Google correct dans Cognito
- [ ] Authorized JavaScript origins : `https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com`
- [ ] Authorized redirect URIs : `https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com/oauth2/idpresponse`
- [ ] OAuth Consent Screen configuré avec scopes `openid`, `email`, `profile`
- [ ] Test user ajouté si en mode "Testing"
- [ ] Cognito App Client : Callback URL = `https://mapevent.world/`
- [ ] Cognito App Client : OAuth grant types = `Authorization code grant`
- [ ] Cognito App Client : Scopes = `openid`, `email`, `profile`

---

## 🆘 Si rien ne fonctionne

1. **Vérifiez les logs du navigateur** (F12 → Console)
2. **Vérifiez les logs Cognito** dans AWS Console → CloudWatch
3. **Testez avec un autre navigateur** (Chrome, Firefox, Safari)
4. **Videz le cache du navigateur** (Ctrl+Shift+Delete)

---

## 📞 Informations de débogage

Quand vous testez, notez :
- L'URL complète affichée dans les logs (commence par `🔗 URL complète:`)
- Le message d'erreur exact de Google
- Le statut de l'OAuth Consent Screen (Testing/Production)

Ces informations aideront à identifier le problème exact.



