# 🔍 Vérifier les Portées et le Mappage d'Attributs

## ✅ Ce que vous avez

- ✅ Portées : `openid`, `email`, `profile`, `phone`
- ✅ Mappage : `email`, `name`, `picture`, `username`

---

## ⚠️ Problème Potentiel : Scope "phone"

Le scope `phone` peut causer des problèmes avec Google OAuth car :

1. **Google ne fournit pas toujours le numéro de téléphone** dans les tokens OAuth
2. Si Google ne fournit pas le phone et que Cognito l'attend, ça peut causer une erreur "invalid_request"

### Solution : Retirer "phone" des Portées (temporairement)

1. **Dans Cognito** → Votre App Client → Paramètres OAuth
2. **Portées OpenID Connect** : Décochez `phone`
3. **Gardez seulement** : `openid`, `email`, `profile`
4. **Sauvegardez**

---

## ✅ Vérifier le Mappage d'Attributs

Dans Cognito → Fournisseurs d'identité → Google → **Mappage d'attributs** :

### Attributs Google → Attributs Cognito

Vous devez avoir :

- `email` → `email` ✅
- `name` → `name` ✅
- `picture` → `picture` ✅
- `username` → `username` (ou `preferred_username`) ✅

### ⚠️ Important

- **`username`** : Google ne fournit pas directement `username`, mais vous pouvez mapper `email` vers `username` aussi
- **`picture`** : Google fournit `picture` dans le token, c'est bon

---

## 📋 Checklist Complète

### Portées OpenID Connect (dans App Client)

- [x] `openid` ✅
- [x] `email` ✅
- [x] `profile` ✅
- [ ] `phone` ❌ (retirer temporairement pour tester)

### Mappage d'Attributs (dans Fournisseur Google)

- [x] `email` → `email` ✅
- [x] `name` → `name` ✅
- [x] `picture` → `picture` ✅
- [x] `username` → `username` ou `preferred_username` ✅

### URLs de Rappel

- [x] `https://mapevent.world/` présent ✅

---

## 🔧 Action Immédiate

1. **Retirez `phone` des Portées OpenID Connect** dans votre App Client
2. **Gardez seulement** : `openid`, `email`, `profile`
3. **Sauvegardez**
4. **Attendez 5 minutes**
5. **Videz le cache du navigateur**
6. **Testez à nouveau**

---

## 🧪 Test

Après avoir retiré `phone` :

1. **Videz le cache** (Ctrl+Shift+Delete)
2. **Fermez tous les onglets**
3. **Ouvrez un nouvel onglet en navigation privée**
4. **Allez sur** `https://mapevent.world`
5. **Ouvrez la console** (F12 → Console)
6. **Cliquez sur "Continuer avec Google"**
7. **Regardez les logs**

---

## 💡 Pourquoi retirer "phone" ?

Google OAuth ne garantit pas de fournir le numéro de téléphone. Si Cognito attend `phone` mais que Google ne le fournit pas, ça peut causer l'erreur "invalid_request".

Une fois que la connexion fonctionne avec `openid`, `email`, `profile`, vous pourrez réessayer d'ajouter `phone` plus tard si nécessaire.

---

## 📞 Résultat

Dites-moi si après avoir retiré `phone` des portées, la connexion fonctionne !










