# 🗄️ UTILISER UN CLIENT POSTGRESQL (ALTERNATIVE)

Si l'éditeur de requêtes AWS n'est pas disponible, utilisez un client PostgreSQL.

## 📥 INSTALLER PGADMIN (RECOMMANDÉ - GRATUIT)

### Étape 1 : Télécharger pgAdmin

1. Allez sur : **https://www.pgadmin.org/download/**
2. Téléchargez **pgAdmin 4** pour Windows
3. Installez-le (suivez les instructions d'installation)

### Étape 2 : Se connecter à votre base de données

1. Ouvrez **pgAdmin**
2. Dans le panneau de gauche, faites un **clic droit** sur **"Servers"**
3. Cliquez sur **"Create"** > **"Server..."**
4. Dans l'onglet **"General"** :
   - **Name** : `MapEvent RDS`
5. Dans l'onglet **"Connection"** :
   - **Host name/address** : `mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com`
   - **Port** : `5432`
   - **Maintenance database** : `mapevent`
   - **Username** : `postgres`
   - **Password** : `666666Laeti69!`
   - Cochez **"Save password"** si vous voulez
6. Cliquez sur **"Save"**

### Étape 3 : Exécuter le script SQL

1. Une fois connecté, dans le panneau de gauche :
   - Développez **"Servers"** > **"MapEvent RDS"** > **"Databases"** > **"mapevent"**
2. Faites un **clic droit** sur **"mapevent"**
3. Cliquez sur **"Query Tool"** (ou **"Outil de requête"**)
4. Ouvrez le fichier **`supprimer-tous-comptes.sql`**
5. **Copiez tout le contenu**
6. **Collez-le** dans l'éditeur SQL
7. Exécutez d'abord les requêtes SELECT pour voir combien de comptes existent
8. Quand vous êtes prêt, **décommentez** `DELETE FROM users;` et exécutez

---

## 📥 INSTALLER DBEAVER (ALTERNATIVE - GRATUIT)

### Étape 1 : Télécharger DBeaver

1. Allez sur : **https://dbeaver.io/download/**
2. Téléchargez **DBeaver Community Edition** pour Windows
3. Installez-le

### Étape 2 : Se connecter

1. Ouvrez **DBeaver**
2. Cliquez sur **"Nouvelle connexion"** (icône prise)
3. Sélectionnez **"PostgreSQL"**
4. Cliquez sur **"Suivant"**
5. Remplissez :
   - **Host** : `mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com`
   - **Port** : `5432`
   - **Database** : `mapevent`
   - **Username** : `postgres`
   - **Password** : `666666Laeti69!`
6. Cliquez sur **"Terminer"**

### Étape 3 : Exécuter le script

1. Faites un **clic droit** sur votre connexion
2. Cliquez sur **"SQL Editor"** > **"New SQL Script"**
3. Ouvrez le fichier **`supprimer-tous-comptes.sql`**
4. **Copiez-collez** le contenu
5. Exécutez les requêtes

---

## ✅ RÉSUMÉ

**Informations de connexion :**
- **Host** : `mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com`
- **Port** : `5432`
- **Database** : `mapevent`
- **User** : `postgres`
- **Password** : `666666Laeti69!`

**Une fois connecté, exécutez le script `supprimer-tous-comptes.sql` !**



