# 🧪 Test Direct de Cognito - Diagnostic

## 🎯 Objectif

Tester directement l'URL Cognito pour voir si le problème vient de Google ou de Cognito.

---

## 📋 Test 1 : Tester l'URL Cognito Directement

1. **Ouvrez un nouvel onglet** dans votre navigateur
2. **Copiez-collez cette URL** dans la barre d'adresse :

```
https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com/oauth2/authorize?client_id=63rm6h0m26q41lotbho6704dod&response_type=code&scope=openid%20email%20profile&redirect_uri=https%3A%2F%2Fmapevent.world%2F
```

3. **Appuyez sur Entrée**
4. **Regardez ce qui se passe** :
   - Si vous voyez la page Cognito avec le bouton Google → Le problème vient peut-être de Google
   - Si vous voyez une erreur Cognito → Le problème vient de Cognito
   - Si vous êtes redirigé vers Google → C'est bon signe !

---

## 📋 Test 2 : Si vous arrivez sur Google

1. **Autorisez** sur la page Google
2. **Regardez où vous êtes redirigé** :
   - Si vous êtes redirigé vers `https://mapevent.world/?code=...` → Ça fonctionne !
   - Si vous voyez une erreur → Notez le message d'erreur exact

---

## 🔍 Diagnostic

### Si vous voyez une erreur "invalid_client" sur la page Cognito

→ Le problème vient de Cognito. Vérifiez :
- Que le Client ID dans Cognito correspond à celui de Google Cloud Console
- Que le Client Secret dans Cognito correspond à celui de Google Cloud Console

### Si vous voyez une erreur "The OAuth client was not found" sur Google

→ Le problème vient de Google Cloud Console. Vérifiez :
- Que le Client ID existe bien dans Google Cloud Console
- Que les URLs autorisées sont correctes

### Si vous voyez "Invalid state"

→ Le problème vient du state. C'est normal si vous testez directement l'URL, mais dans l'application ça devrait fonctionner.

---

## 💡 Solution Alternative : Créer un Nouveau Client ID

Si rien ne fonctionne, créons un nouveau Client ID depuis zéro :

1. **Google Cloud Console** → **Credentials**
2. **Create Credentials** → **OAuth client ID**
3. **Application type** : Web application
4. **Name** : `Mapevent Cognito NEW`
5. **Authorized JavaScript origins** :
   ```
   https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com
   ```
6. **Authorized redirect URIs** :
   ```
   https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com/oauth2/idpresponse
   ```
7. **Create**
8. **Copiez le nouveau Client ID et Secret**
9. **Dans Cognito** → **Google Identity Provider** → **Collez les nouvelles valeurs**
10. **Sauvegardez**
11. **Attendez 10 minutes**
12. **Testez**

---

## 📞 Résultat du Test

Dites-moi ce qui se passe quand vous testez l'URL directement. Cela m'aidera à identifier le problème exact.



