# 🚀 Accéder à l'OAuth Consent Screen - Guide Rapide

## ⚡ Méthode la PLUS RAPIDE

### Étape 1 : Ouvrir Google Cloud Console
1. **Allez sur** : https://console.cloud.google.com/
2. **Connectez-vous** avec votre compte Google (`laetitiaimboden132@gmail.com`)

### Étape 2 : Sélectionner ou créer un projet
1. **En haut de la page**, regardez le sélecteur de projet (à côté du logo Google Cloud)
2. **Si aucun projet n'est sélectionné** :
   - Cliquez sur le sélecteur de projet
   - Cliquez sur **"New Project"** (Nouveau projet)
   - **Project name** : `Mapevent`
   - Cliquez sur **"Create"**
   - Attendez quelques secondes
   - Sélectionnez le projet `Mapevent` dans la liste

### Étape 3 : Accéder à l'OAuth Consent Screen

**Méthode A : Via la barre de recherche (PLUS RAPIDE)**
1. **En haut de la page**, dans la barre de recherche (où il y a "Search for resources, APIs, docs...")
2. **Tapez** : `oauth consent`
3. **Cliquez sur** : **"OAuth consent screen"** dans les résultats
4. ✅ **VOUS Y ÊTES !**

**Méthode B : Via le menu de gauche**
1. **Menu de gauche** (☰) → Cliquez sur **"APIs & Services"**
2. Dans le sous-menu, cliquez sur **"OAuth consent screen"**
3. ✅ **VOUS Y ÊTES !**

**Méthode C : Lien direct (après avoir sélectionné un projet)**
1. Une fois que vous avez un projet sélectionné, vous pouvez utiliser ce lien :
   ```
   https://console.cloud.google.com/apis/credentials/consent
   ```
2. ✅ **VOUS Y ÊTES !**

---

## 🎯 Ce que vous devriez voir

Une fois sur la page OAuth Consent Screen, vous verrez :

**Si c'est la première fois :**
- Un écran avec **"User Type"** et un bouton **"CREATE"** ou **"NEXT"**
- Sélectionnez **"External"** → Cliquez sur **"CREATE"** ou **"NEXT"**

**Si c'est déjà configuré :**
- Un écran avec les informations de l'application
- Cliquez sur **"EDIT APP"** (Modifier l'application) en haut à droite pour modifier

---

## ❌ Si vous ne voyez pas l'option "OAuth consent screen"

**Vérifiez que :**
1. ✅ Vous êtes connecté avec le bon compte Google
2. ✅ Un projet est sélectionné (pas "Select a project")
3. ✅ Vous avez les permissions nécessaires (Owner ou Editor)

**Si vous ne voyez toujours pas l'option :**
1. Allez dans **"APIs & Services"** → **"Library"**
2. Recherchez **"Google+ API"** ou **"Identity Platform API"**
3. Cliquez dessus → **"Enable"** (Activer)
4. Retournez à **"APIs & Services"** → **"OAuth consent screen"**

---

## 📝 Prochaines étapes

Une fois sur l'OAuth Consent Screen :
1. Configurez les informations de l'application (voir le guide complet)
2. Ajoutez les scopes : `openid`, `email`, `profile`
3. Ajoutez votre email comme test user
4. Créez le Client ID










