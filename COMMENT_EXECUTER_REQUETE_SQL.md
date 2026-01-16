# 📋 COMMENT EXÉCUTER UNE REQUÊTE SQL - GUIDE VISUEL

## 🎯 DANS L'ÉDITEUR DE REQUÊTES AWS

### Si vous êtes dans l'éditeur de requêtes AWS :

1. **Vous verrez une grande zone de texte blanche** (c'est l'éditeur SQL)
2. **Tapez ou collez votre requête** dans cette zone
   - Exemple : `SELECT email, username, role FROM users;`
3. **Sélectionnez la requête** (cliquez et glissez pour sélectionner le texte)
4. **Cherchez le bouton "Exécuter"** ou "Run" :
   - Il peut être en haut de l'éditeur (icône ▶️ ou bouton vert)
   - Ou dans un menu "Exécuter" / "Run"
   - Ou utilisez le raccourci clavier : **F5** ou **Ctrl+Enter**
5. **Cliquez sur "Exécuter"** ou appuyez sur **F5**

---

## 🎯 DANS PGADMIN (si vous utilisez pgAdmin)

### Étape 1 : Ouvrir l'outil de requête

1. Dans le panneau de gauche, développez :
   - **Servers** > **MapEvent RDS** > **Databases** > **mapevent**
2. **Clic droit** sur **"mapevent"**
3. Cliquez sur **"Query Tool"** (ou **"Outil de requête"** en français)

### Étape 2 : Exécuter la requête

1. **Une nouvelle fenêtre s'ouvre** avec un éditeur SQL
2. **Tapez ou collez votre requête** :
   ```sql
   SELECT email, username, role FROM users;
   ```
3. **Cliquez sur le bouton "Exécuter"** (icône ▶️ en haut)
   - OU appuyez sur **F5**
   - OU utilisez le menu : **Query** > **Execute** (ou **Requête** > **Exécuter**)

### Étape 3 : Voir les résultats

Les résultats apparaissent dans un **tableau en bas** de la fenêtre.

---

## 🎯 DANS DBEAVER (si vous utilisez DBeaver)

### Étape 1 : Ouvrir l'éditeur SQL

1. **Clic droit** sur votre connexion "mapevent"
2. Cliquez sur **"SQL Editor"** > **"New SQL Script"**

### Étape 2 : Exécuter

1. **Tapez ou collez votre requête**
2. **Sélectionnez la requête** (ou laissez le curseur dedans)
3. **Cliquez sur le bouton "Exécuter"** (icône ▶️)
   - OU appuyez sur **Ctrl+Enter**
   - OU menu : **SQL** > **Execute SQL Statement**

---

## 📝 EXEMPLE CONCRET

### Requête à exécuter :

```sql
SELECT email, username, role FROM users;
```

### Comment faire :

1. **Copiez** cette ligne complète (avec le point-virgule `;`)
2. **Collez-la** dans l'éditeur SQL
3. **Sélectionnez-la** (cliquez et glissez)
4. **Appuyez sur F5** ou cliquez sur "Exécuter"

### Résultat attendu :

Vous devriez voir un **tableau** avec les colonnes :
- email
- username  
- role

Et les lignes avec tous vos comptes.

---

## 🆘 SI VOUS NE VOYEZ PAS L'ÉDITEUR

### Option 1 : Utiliser pgAdmin (le plus simple)

1. Téléchargez : https://www.pgadmin.org/download/
2. Installez
3. Connectez-vous avec :
   - Host : `mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com`
   - Port : `5432`
   - Database : `mapevent`
   - User : `postgres`
   - Password : `666666Laeti69!`
4. Clic droit sur "mapevent" > "Query Tool"
5. Collez votre requête
6. Cliquez sur ▶️ (bouton Exécuter)

### Option 2 : Utiliser DBeaver

1. Téléchargez : https://dbeaver.io/download/
2. Installez
3. Créez une connexion PostgreSQL avec les mêmes informations
4. Ouvrez un nouvel éditeur SQL
5. Collez votre requête
6. Cliquez sur ▶️

---

## ✅ RACCOURCIS CLAVIER

- **F5** : Exécuter la requête (fonctionne dans la plupart des éditeurs)
- **Ctrl+Enter** : Exécuter (dans certains éditeurs)
- **Ctrl+Shift+Enter** : Exécuter tout le script

---

**Dites-moi quel outil vous utilisez (AWS Query Editor, pgAdmin, DBeaver) et je vous guiderai plus précisément !** 🚀



