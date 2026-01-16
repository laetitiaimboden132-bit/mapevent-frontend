# 🔍 Vérifier les Paramètres OAuth Cognito - Guide en Français

## ✅ Ce qui est Déjà Bon

- ✅ App Client est Public (pas de secret) 
- ✅ OAuth 2.0 Authorization code grant est coché
- ✅ Fournisseur Google a un secret (c'est normal, c'est le Client Secret de Google Cloud Console)

---

## 📋 Étape 1 : Aller dans les Paramètres de l'App Client

1. **AWS Console** → **Cognito** → Votre User Pool
2. **Intégration d'application** → **Clients d'application** → Votre client (`63rm6h0m26q41lotbho6704dod`)
3. **Cliquez sur votre client** pour voir ses détails

---

## 📋 Étape 2 : Trouver les Paramètres OAuth

Dans la page de votre App Client, cherchez :

### Option A : Onglet "Interface utilisateur hébergée" ou "Hosted UI"

1. **Cherchez un onglet** qui s'appelle :
   - "Interface utilisateur hébergée"
   - "Hosted UI"
   - "OAuth"
   - "Paramètres OAuth"

2. **Cliquez dessus**

### Option B : Lien "Modifier" ou "Configurer"

1. **Cherchez un bouton** "Modifier" ou "Configurer" en haut de la page
2. **Cliquez dessus**
3. Les paramètres OAuth devraient apparaître

### Option C : Section dans la page principale

1. **Descendez dans la page** de votre App Client
2. **Cherchez une section** qui parle de :
   - "URLs de rappel autorisées"
   - "Portées OpenID Connect"
   - "Types d'octroi OAuth"

---

## 📋 Étape 3 : Vérifier les Paramètres OAuth

Une fois que vous avez trouvé les paramètres OAuth, vérifiez :

### 1. Portées OpenID Connect (OpenID Connect scopes)

Vous devez voir une liste avec des cases à cocher. **Cochez** :
- ✅ `openid`
- ✅ `email`
- ✅ `profile`

### 2. URLs de rappel autorisées (Allowed callback URLs)

Vous devez voir un champ texte ou une liste. **Vérifiez** qu'il contient :
```
https://mapevent.world/
```

⚠️ **IMPORTANT** :
- Avec le slash final `/`
- Pas d'espaces avant/après
- HTTPS obligatoire

### 3. Fournisseurs d'identité (Identity providers)

Vous devez voir une liste avec des cases à cocher. **Cochez** :
- ✅ **Google**

---

## 📋 Étape 4 : Si vous ne trouvez pas ces paramètres

### Essayez cette méthode :

1. **Dans la page de votre App Client**, cherchez un lien ou un bouton qui dit :
   - "Afficher les détails"
   - "Voir plus"
   - "Modifier"
   - "Configurer"

2. **OU** allez dans :
   - **Intégration d'application** → **Domaine**
   - Vérifiez que le domaine Cognito est configuré

3. **OU** cherchez dans le menu de gauche de votre User Pool :
   - **Intégration d'application** → **Pages** (pour configurer les pages de connexion)

---

## 📋 Étape 5 : Sauvegarder

1. **Vérifiez** que tous les paramètres sont corrects :
   - ✅ Portées : `openid`, `email`, `profile` cochées
   - ✅ Callback URL : `https://mapevent.world/` présent
   - ✅ Fournisseur Google : coché

2. **Cliquez sur "Enregistrer"** ou "Save" en bas de la page

3. **Attendez 5 minutes** pour la propagation

---

## ✅ Checklist Complète

- [ ] App Client est Public (pas de secret) ✅
- [ ] OAuth 2.0 Authorization code grant est coché ✅
- [ ] Portées OpenID Connect : `openid`, `email`, `profile` sont cochées
- [ ] URLs de rappel autorisées : `https://mapevent.world/` est présent
- [ ] Fournisseurs d'identité : Google est coché
- [ ] Sauvegardé et attendu 5 minutes

---

## 🆘 Si vous ne trouvez toujours pas

Dites-moi **exactement** ce que vous voyez dans la page de votre App Client :

1. **Quels onglets** voyez-vous en haut de la page ?
2. **Quelles sections** voyez-vous dans la page ?
3. **Y a-t-il un bouton "Modifier"** quelque part ?

Avec ces informations, je pourrai vous guider plus précisément dans l'interface française d'AWS Cognito.

---

## 💡 Astuce

Dans l'interface AWS Cognito en français, les termes peuvent être :
- "Portées" = Scopes
- "URLs de rappel" = Callback URLs
- "Fournisseurs d'identité" = Identity Providers
- "Types d'octroi" = Grant Types
- "Interface utilisateur hébergée" = Hosted UI

Cherchez ces termes dans votre interface !










