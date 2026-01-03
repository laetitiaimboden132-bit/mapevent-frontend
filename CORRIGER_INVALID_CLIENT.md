# 🔧 Corriger l'erreur "The OAuth client was not found" / "invalid_client"

## ❌ Problème

L'erreur **"The OAuth client was not found"** ou **"Erreur 401 : invalid_client"** signifie que le **Client ID Google** configuré dans AWS Cognito n'existe pas ou est incorrect dans Google Cloud Console.

---

## ✅ Solution Étape par Étape

### Étape 1 : Vérifier le Client ID dans Cognito

1. **AWS Console** → **Cognito** → Votre User Pool
2. **Federated identity providers** → **Google**
3. **Notez le Client ID** affiché (ex: `123456789-abc.apps.googleusercontent.com`)

### Étape 2 : Vérifier dans Google Cloud Console

1. Allez sur **https://console.cloud.google.com/**
2. Sélectionnez votre projet
3. **APIs & Services** → **Credentials**
4. Cherchez votre **OAuth 2.0 Client ID**
5. **Comparez avec le Client ID dans Cognito**

#### ⚠️ Si le Client ID ne correspond PAS :

**Option A : Utiliser le Client ID existant**
1. Copiez le **Client ID** depuis Google Cloud Console
2. Allez dans Cognito → **Google Identity Provider**
3. **Modifiez** le Client ID pour utiliser celui de Google Cloud Console
4. **Copiez aussi le Client Secret** depuis Google Cloud Console
5. **Sauvegardez**

**Option B : Créer un nouveau Client ID**
1. Dans Google Cloud Console → **Credentials**
2. **Create Credentials** → **OAuth client ID**
3. **Application type** : `Web application`
4. **Name** : `MapEvent Cognito`
5. **Authorized JavaScript origins** :
   ```
   https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com
   ```
6. **Authorized redirect URIs** :
   ```
   https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com/oauth2/idpresponse
   ```
7. **Créer**
8. **Copiez le Client ID et le Client Secret**
9. Allez dans Cognito → **Google Identity Provider**
10. **Collez le nouveau Client ID et Secret**
11. **Sauvegardez**

---

### Étape 3 : Vérifier les URLs autorisées dans Google Cloud Console

Dans Google Cloud Console → Votre OAuth Client ID → **Vérifiez que ces URLs sont EXACTEMENT configurées :**

#### Authorized JavaScript origins :
```
https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com
```

#### Authorized redirect URIs :
```
https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com/oauth2/idpresponse
```

⚠️ **IMPORTANT** :
- Pas de slash final (`/`) à la fin
- Pas d'espaces avant/après
- HTTPS obligatoire
- Le domaine doit être exactement `eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com`

---

### Étape 4 : Vérifier le Client Secret

1. Dans Google Cloud Console → Votre OAuth Client ID
2. Cliquez sur l'icône **👁️** pour voir le **Client Secret**
3. **Copiez-le**
4. Dans Cognito → **Google Identity Provider**
5. **Collez le Client Secret**
6. **Sauvegardez**

⚠️ **Note** : Si vous avez créé un nouveau Client ID, vous devez utiliser le nouveau Secret correspondant.

---

### Étape 5 : Vérifier l'OAuth Consent Screen

1. Google Cloud Console → **APIs & Services** → **OAuth consent screen**
2. Vérifiez que :
   - **App name** : `mapevent` (ou votre nom)
   - **User support email** : Votre email
   - **Scopes** : `openid`, `email`, `profile` sont ajoutés
   - **Publishing status** : 
     - Si **"Testing"** : Ajoutez votre email dans **Test users**
     - Si **"In production"** : Pas besoin de test users

---

### Étape 6 : Attendre la propagation (5-10 minutes)

Après avoir modifié les configurations :
- **Google Cloud Console** : Changements immédiats
- **AWS Cognito** : Peut prendre quelques minutes

**Attendez 5-10 minutes** avant de retester.

---

### Étape 7 : Tester

1. **Videz le cache du navigateur** (Ctrl+Shift+Delete)
2. Allez sur `https://mapevent.world`
3. Cliquez sur **"Continuer avec Google"**
4. Vérifiez la console du navigateur (F12) pour les erreurs

---

## 🔍 Vérifications supplémentaires

### Vérifier que le projet Google Cloud est actif

1. Google Cloud Console → **APIs & Services** → **Enabled APIs**
2. Vérifiez que ces APIs sont activées :
   - ✅ **Google+ API** (ou **Google Identity Services**)
   - ✅ **People API** (optionnel mais recommandé)

### Vérifier les quotas

1. Google Cloud Console → **APIs & Services** → **Quotas**
2. Vérifiez que vous n'avez pas dépassé les limites

---

## 📝 Checklist Complète

- [ ] Client ID dans Cognito = Client ID dans Google Cloud Console
- [ ] Client Secret dans Cognito = Client Secret dans Google Cloud Console
- [ ] Authorized JavaScript origins : `https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com`
- [ ] Authorized redirect URIs : `https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com/oauth2/idpresponse`
- [ ] OAuth Consent Screen configuré avec scopes `openid`, `email`, `profile`
- [ ] Test user ajouté si en mode "Testing"
- [ ] Attente de 5-10 minutes après modifications
- [ ] Cache du navigateur vidé

---

## 🆘 Si l'erreur persiste

1. **Créez un nouveau Client ID** dans Google Cloud Console
2. **Utilisez-le dans Cognito** (remplacez l'ancien)
3. **Vérifiez toutes les URLs** (copiez-collez pour éviter les erreurs de frappe)
4. **Attendez 10 minutes**
5. **Testez à nouveau**

---

## 📞 Informations de débogage

Quand vous testez, notez :
- Le **Client ID** affiché dans Cognito
- Le **Client ID** affiché dans Google Cloud Console
- Les **URLs autorisées** dans Google Cloud Console
- Le **message d'erreur exact** dans la console du navigateur

Ces informations aideront à identifier le problème exact.



