# 🔍 Vérifier les Paramètres OAuth de l'App Client Cognito

## ✅ Bonne Nouvelle

Votre App Client est **Public** (pas de secret) ✅

Mais il faut vérifier les **paramètres OAuth/Hosted UI** pour que la connexion Google fonctionne.

---

## 📋 Étape 1 : Aller dans les Paramètres Hosted UI

1. **AWS Console** → **Cognito** → Votre User Pool
2. **App integration** → **App clients** → Votre client (`63rm6h0m26q41lotbho6704dod`)
3. **Cherchez la section "Hosted UI"** ou **"Hosted UI settings"**
4. **Cliquez dessus** ou **"Edit"** (Modifier)

---

## 📋 Étape 2 : Vérifier les Paramètres OAuth

Dans les paramètres Hosted UI, vous devez avoir :

### OAuth 2.0 grant types (Types d'octroi OAuth 2.0)

✅ **"Authorization code grant"** doit être **COCHÉ**

### OpenID Connect scopes (Portées OpenID Connect)

✅ Ces scopes doivent être **COCHÉS** :
- `openid`
- `email`
- `profile`

### Allowed callback URLs (URLs de rappel autorisées)

✅ Doit contenir **exactement** :
```
https://mapevent.world/
```

⚠️ **IMPORTANT** :
- Pas d'espace avant/après
- Avec le slash final `/`
- HTTPS obligatoire

### Allowed sign-out URLs (URLs de déconnexion autorisées)

Peut être vide ou contenir :
```
https://mapevent.world/
```

---

## 📋 Étape 3 : Vérifier les Fournisseurs d'Identité

1. Dans la même page Hosted UI, cherchez **"Identity providers"** (Fournisseurs d'identité)
2. **Google** doit être **SÉLECTIONNÉ** (coché)

---

## 📋 Étape 4 : Sauvegarder

1. **Vérifiez** que tous les paramètres ci-dessus sont corrects
2. **Cliquez sur "Save"** (Enregistrer) en bas de la page
3. **Attendez 5 minutes** pour la propagation

---

## ✅ Checklist Complète

- [ ] App Client est Public (pas de secret) ✅ (déjà vérifié)
- [ ] OAuth 2.0 grant types : "Authorization code grant" est coché
- [ ] OpenID Connect scopes : `openid`, `email`, `profile` sont cochés
- [ ] Allowed callback URLs : `https://mapevent.world/` est présent
- [ ] Identity providers : Google est sélectionné
- [ ] Sauvegardé et attendu 5 minutes

---

## 🧪 Test

Après avoir vérifié et corrigé les paramètres :

1. **Videz le cache du navigateur** (Ctrl+Shift+Delete)
2. **Fermez tous les onglets**
3. **Ouvrez un nouvel onglet en navigation privée**
4. **Allez sur** `https://mapevent.world`
5. **Ouvrez la console** (F12 → Console)
6. **Cliquez sur "Continuer avec Google"**
7. **Regardez les logs** dans la console

---

## 🆘 Si vous ne trouvez pas la section "Hosted UI"

1. **Dans la page de votre App Client**, cherchez un onglet ou un lien **"Hosted UI"**
2. OU **App integration** → **Domain** → Vérifiez que le domaine Cognito est configuré
3. OU **App integration** → **App client settings** → Cherchez les paramètres OAuth

---

## 📞 Besoin d'aide ?

Dites-moi ce que vous voyez dans la section "Hosted UI" ou "OAuth settings" de votre App Client, et je pourrai vous guider plus précisément.



