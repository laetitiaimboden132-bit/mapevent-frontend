# ✅ SOLUTION LA PLUS SIMPLE : AWS RDS Query Editor

## 🎯 Pas besoin de connexion locale ! (Contourne McAfee, firewall, etc.)

---

## 📋 ÉTAPE PAR ÉTAPE

### 1️⃣ Ouvrir l'éditeur de requêtes AWS

1. **Allez sur** : https://console.aws.amazon.com
2. **Cherchez** "RDS" dans la barre de recherche
3. **Cliquez sur** "Bases de données" dans le menu de gauche
4. **Cliquez sur** `mapevent-db`
5. **Cliquez sur** **"Query Editor"** ou **"Éditeur de requêtes"** (en haut de la page)

---

### 2️⃣ Se connecter à la base

1. **Identifiant de connexion** : `postgres` (ou votre identifiant principal)
2. **Mot de passe** : Votre mot de passe RDS principal (celui que vous avez configuré)
3. **Base de données** : `postgres` (généralement)
4. **Cliquez sur** "Se connecter"

---

### 3️⃣ Voir tous vos comptes (POUR IDENTIFIER VOTRE ADMIN)

**Copiez et collez cette requête :**

```sql
SELECT 
    id,
    email,
    username,
    first_name,
    last_name,
    COALESCE(role, 'user') as role,
    created_at
FROM users 
ORDER BY created_at DESC;
```

**Cliquez sur "Exécuter" ou "Run"**

**📝 Notez l'EMAIL de votre compte admin** (celui que vous voulez garder)

---

### 4️⃣ Supprimer tous les comptes SAUF l'admin

**Ouvrez le fichier** `supprimer-comptes-sauf-admin.sql`

**⚠️ IMPORTANT :** Remplacez `'admin@example.com'` par **L'EMAIL DE VOTRE COMPTE ADMIN** dans toutes les lignes qui contiennent cette adresse.

**Exemple :**
- Si votre email admin est `mon.email@gmail.com`
- Remplacez toutes les occurrences de `'admin@example.com'` par `'mon.email@gmail.com'`

**Puis copiez-collez TOUT le script dans l'éditeur AWS**

**Cliquez sur "Exécuter" ou "Run"**

---

### 5️⃣ Vérifier

**Après l'exécution, vous devriez voir UN SEUL compte :**

```sql
SELECT email, username, role FROM users;
```

**Vous devriez voir uniquement votre compte admin !**

---

### 6️⃣ (Optionnel) Mettre le rôle en 'director' si nécessaire

**Si votre compte n'a pas le rôle 'director' ou 'admin' :**

```sql
UPDATE users 
SET role = 'director' 
WHERE email = 'VOTRE-EMAIL-ADMIN@example.com';
```

**Remplacez l'email par le vôtre !**

---

## ✅ Avantages de cette méthode

- ✅ **Pas besoin de connexion locale** (contourne McAfee, firewall, IP, etc.)
- ✅ **Interface graphique simple** dans AWS Console
- ✅ **Exécution directe sur AWS** (pas de timeout réseau)
- ✅ **Voir les résultats immédiatement** dans l'éditeur
- ✅ **Sécurisé** (utilise vos identifiants AWS)

---

## 🆘 Si vous ne trouvez pas "Query Editor"

**Alternative 1 : AWS CloudShell**
1. AWS Console > **CloudShell** (icône dans la barre supérieure)
2. Connectez-vous avec `psql` :
   ```bash
   psql -h mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com -U postgres -d postgres
   ```

**Alternative 2 : pgAdmin**
1. Installez pgAdmin : https://www.pgadmin.org/download/
2. Connectez-vous avec les informations RDS
3. Utilisez Query Tool

---

## 📝 Résumé

1. **AWS Console > RDS > mapevent-db > Query Editor**
2. **Connectez-vous** (postgres + votre mot de passe)
3. **Exécutez** : `SELECT * FROM users;` pour voir tous les comptes
4. **Notez l'email** de votre compte admin
5. **Modifiez** `supprimer-comptes-sauf-admin.sql` (remplacez l'email)
6. **Copiez-collez** le script dans l'éditeur AWS
7. **Exécutez** le script
8. **Vérifiez** : `SELECT * FROM users;` (doit afficher 1 seul compte)

**C'est la méthode la plus simple !** 🚀

