# 🚀 INSTALLER PGADMIN - GUIDE ULTRA-SIMPLE

## 📥 ÉTAPE 1 : TÉLÉCHARGER PGADMIN

1. Allez sur : **https://www.pgadmin.org/download/**
2. Cliquez sur **"Download pgAdmin 4"**
3. Choisissez **"Windows"**
4. Téléchargez **"pgAdmin 4 for Windows"** (le fichier .exe)
5. **Installez-le** (double-cliquez sur le fichier téléchargé, suivez les instructions)

---

## 🔌 ÉTAPE 2 : SE CONNECTER À VOTRE BASE DE DONNÉES

### 2.1 Ouvrir pgAdmin

1. **Ouvrez pgAdmin** (icône sur le bureau ou dans le menu Démarrer)
2. Une fenêtre s'ouvre avec un panneau de gauche

### 2.2 Créer la connexion

1. Dans le **panneau de gauche**, faites un **clic droit** sur **"Servers"** (ou "Serveurs")
2. Cliquez sur **"Create"** > **"Server..."** (ou "Créer" > "Serveur...")

### 2.3 Remplir les informations

**Onglet "General" (Général) :**
- **Name** : `MapEvent` (ou n'importe quel nom)

**Onglet "Connection" (Connexion) :**
- **Host name/address** : `mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com`
- **Port** : `5432`
- **Maintenance database** : `mapevent`
- **Username** : `postgres`
- **Password** : `666666Laeti69!`
- ✅ Cochez **"Save password"** (Sauvegarder le mot de passe)

**Cliquez sur "Save" (Enregistrer)**

---

## 📝 ÉTAPE 3 : EXÉCUTER UNE REQUÊTE SQL

### 3.1 Ouvrir l'outil de requête

1. Dans le **panneau de gauche**, développez :
   - **Servers** > **MapEvent** > **Databases** > **mapevent**
2. **Clic droit** sur **"mapevent"**
3. Cliquez sur **"Query Tool"** (ou "Outil de requête")

### 3.2 Une nouvelle fenêtre s'ouvre

Vous verrez :
- **En haut** : Une grande zone de texte blanche (c'est l'éditeur SQL)
- **En bas** : Une zone vide (pour les résultats)

### 3.3 Exécuter votre première requête

1. **Dans la zone blanche en haut**, tapez ou collez :
   ```sql
   SELECT email, username, role FROM users;
   ```

2. **Cliquez sur le bouton "Execute" (Exécuter)** :
   - C'est le bouton avec l'icône **▶️** (play) en haut de la fenêtre
   - OU appuyez sur **F5**

3. **Regardez en bas** : Vous verrez un tableau avec tous vos comptes !

---

## ✅ C'EST TOUT !

Maintenant vous pouvez :
- ✅ Voir tous vos comptes
- ✅ Exécuter n'importe quelle requête SQL
- ✅ Supprimer les comptes que vous voulez

---

## 🎯 PROCHAINES ÉTAPES

Une fois que vous voyez vos comptes :

1. **Notez l'email de votre compte admin** (celui que vous voulez garder)
2. **Exécutez cette commande** (remplacez l'email) :
   ```sql
   DELETE FROM users WHERE email != 'VOTRE-EMAIL@example.com';
   ```
3. **Vérifiez** :
   ```sql
   SELECT email, username, role FROM users;
   ```

---

**pgAdmin est beaucoup plus simple que l'éditeur AWS ! Installez-le et suivez ces étapes.** 🚀



