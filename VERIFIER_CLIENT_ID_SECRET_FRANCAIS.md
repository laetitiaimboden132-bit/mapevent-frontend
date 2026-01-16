# 🔍 Vérifier le Client ID et Client Secret - Guide en Français

## 📋 Étape 1 : Aller dans Google Cloud Console

1. **Ouvrez votre navigateur**
2. **Allez sur** : https://console.cloud.google.com/
3. **Connectez-vous** avec votre compte Google
4. **Sélectionnez votre projet** en haut de la page

---

## 📋 Étape 2 : Trouver vos Identifiants (Credentials)

1. Dans le menu de gauche, cherchez **"APIs et services"** (ou "APIs & Services")
2. Cliquez dessus
3. Cliquez sur **"Identifiants"** (ou "Credentials")

---

## 📋 Étape 3 : Ouvrir votre Client OAuth

1. Vous verrez une liste avec vos identifiants
2. **Cherchez celui qui s'appelle "Mapevent"** (ou le nom que vous avez donné)
3. **Cliquez dessus** pour l'ouvrir

---

## 📋 Étape 4 : Voir le Client ID

Une fois que vous avez cliqué sur votre Client OAuth, vous verrez une page avec les détails.

**Le Client ID est visible directement**, il ressemble à ça :
```
123456789-abc123def456.apps.googleusercontent.com
```

**Notez ce Client ID** (ou gardez cette page ouverte).

---

## 📋 Étape 5 : Voir le Client Secret

Sur la même page, vous verrez un champ **"Client secret"** (ou "Client Secret").

1. **Cliquez sur l'icône 👁️** (œil) à côté du Client Secret
2. Le secret apparaîtra, il ressemble à ça :
```
GOCSPX-xxxxxxxxxxxxxxxxxxxxx
```

**Notez ce Client Secret** (ou gardez cette page ouverte).

⚠️ **Attention** : Le Client Secret ne s'affiche qu'une seule fois quand vous le créez. Si vous ne le voyez plus, vous devrez peut-être en créer un nouveau.

---

## 📋 Étape 6 : Aller dans AWS Cognito

1. **Ouvrez un nouvel onglet** dans votre navigateur
2. **Allez sur** : https://console.aws.amazon.com/
3. **Connectez-vous** à votre compte AWS
4. **Cherchez "Cognito"** dans la barre de recherche en haut
5. **Cliquez sur "Cognito"**

---

## 📋 Étape 7 : Trouver votre User Pool

1. Dans le menu de gauche, cliquez sur **"User pools"** (Groupes d'utilisateurs)
2. **Cliquez sur votre User Pool** (celui que vous utilisez pour mapevent)

---

## 📋 Étape 8 : Aller dans les Fournisseurs d'Identité

1. Dans le menu de gauche de votre User Pool, cherchez **"Federated identity providers"** (Fournisseurs d'identité fédérés)
2. **Cliquez dessus**
3. Vous verrez une liste avec **"Google"**
4. **Cliquez sur "Google"**

---

## 📋 Étape 9 : Comparer le Client ID

Sur la page Google dans Cognito, vous verrez un champ **"Client ID"**.

**Comparez** :
- Le Client ID dans Cognito
- Le Client ID dans Google Cloud Console (que vous avez noté à l'Étape 4)

**Ils doivent être EXACTEMENT identiques.**

---

## 📋 Étape 10 : Comparer le Client Secret

Sur la même page Cognito, vous verrez un champ **"Client secret"**.

1. **Cliquez sur l'icône 👁️** (œil) pour voir le secret
2. **Comparez** :
   - Le Client Secret dans Cognito
   - Le Client Secret dans Google Cloud Console (que vous avez noté à l'Étape 5)

**Ils doivent être EXACTEMENT identiques.**

---

## ✅ Si les valeurs correspondent

**Parfait !** Votre configuration est correcte. Passez aux autres vérifications.

---

## ❌ Si les valeurs NE correspondent PAS

Vous devez mettre à jour Cognito avec les valeurs de Google Cloud Console :

### Comment faire :

1. **Retournez dans Google Cloud Console** (l'onglet que vous avez gardé ouvert)
2. **Copiez le Client ID** (sélectionnez-le et Ctrl+C)
3. **Retournez dans Cognito** (l'autre onglet)
4. **Collez le Client ID** dans le champ "Client ID" (Ctrl+V)
5. **Retournez dans Google Cloud Console**
6. **Cliquez sur 👁️ pour voir le Client Secret**
7. **Copiez le Client Secret** (sélectionnez-le et Ctrl+C)
8. **Retournez dans Cognito**
9. **Collez le Client Secret** dans le champ "Client secret" (Ctrl+V)
10. **Cliquez sur "Enregistrer"** (ou "Save") en bas de la page
11. **Attendez 5 minutes**
12. **Testez à nouveau**

---

## 🆘 Si vous ne voyez plus le Client Secret dans Google

Si vous ne voyez plus le Client Secret dans Google Cloud Console, vous devez en créer un nouveau :

1. Dans Google Cloud Console → Votre Client OAuth
2. Cliquez sur **"Reset secret"** (Réinitialiser le secret) ou **"Regenerate"** (Régénérer)
3. Un nouveau secret sera créé
4. **Copiez-le immédiatement** (il ne s'affichera qu'une seule fois)
5. **Collez-le dans Cognito** → Google → Client secret
6. **Sauvegardez**

---

## 📝 Résumé

**À vérifier :**
- ✅ Client ID Google Cloud = Client ID Cognito
- ✅ Client Secret Google Cloud = Client Secret Cognito

**Si différent :**
- Copiez depuis Google Cloud Console
- Collez dans Cognito
- Sauvegardez
- Attendez 5 minutes
- Testez

---

## 💡 Astuce

Pour éviter les erreurs :
- **Copiez-collez** au lieu de taper manuellement
- **Vérifiez qu'il n'y a pas d'espaces** avant ou après
- **Gardez les deux pages ouvertes** pour comparer facilement










