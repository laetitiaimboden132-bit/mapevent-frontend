# ✅ SOLUTION ALTERNATIVE : AWS CloudShell

## 🎯 Utiliser AWS CloudShell (Terminal Web - Pas besoin d'installation !)

AWS CloudShell est un terminal dans votre navigateur qui peut se connecter à RDS.

---

## 📋 ÉTAPES

### 1️⃣ Ouvrir CloudShell

1. **En haut de l'écran AWS Console**, cherchez l'icône **"CloudShell"** (☁️ avec un symbole `>_`)
2. **OU** allez directement sur : https://console.aws.amazon.com/cloudshell/home
3. **Cliquez sur** l'icône CloudShell

**⏱️ Première fois :** CloudShell peut prendre 30-60 secondes pour démarrer.

---

### 2️⃣ Installer psql (si nécessaire)

**Dans CloudShell, exécutez :**

```bash
sudo yum install -y postgresql15
```

**OU si ça ne marche pas :**

```bash
sudo yum install -y postgresql
```

---

### 3️⃣ Se connecter à la base de données

**Exécutez cette commande** (remplacez le mot de passe par le vôtre) :

```bash
PGPASSWORD='VOTRE_MOT_DE_PASSE_RDS' psql -h mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com -U postgres -d postgres
```

**Remplacez `VOTRE_MOT_DE_PASSE_RDS` par votre vrai mot de passe !**

**Exemple :**
```bash
PGPASSWORD='MonMotDePasse123!' psql -h mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com -U postgres -d postgres
```

---

### 4️⃣ Voir tous vos comptes

**Une fois connecté, exécutez :**

```sql
SELECT id, email, username, COALESCE(role, 'user') as role, created_at 
FROM users 
ORDER BY created_at DESC;
```

**📝 Notez l'EMAIL de votre compte admin** (celui que vous voulez garder)

---

### 5️⃣ Supprimer tous les comptes SAUF l'admin

**⚠️ Remplacez `'admin@example.com'` par l'email de votre compte admin !**

```sql
BEGIN;

-- Supprimer les données liées
DELETE FROM user_favorites
WHERE user_id NOT IN (SELECT id FROM users WHERE email = 'VOTRE-EMAIL-ADMIN@example.com');

DELETE FROM user_agenda
WHERE user_id NOT IN (SELECT id FROM users WHERE email = 'VOTRE-EMAIL-ADMIN@example.com');

DELETE FROM user_likes
WHERE user_id NOT IN (SELECT id FROM users WHERE email = 'VOTRE-EMAIL-ADMIN@example.com');

DELETE FROM subscriptions
WHERE user_id NOT IN (SELECT id FROM users WHERE email = 'VOTRE-EMAIL-ADMIN@example.com');

DELETE FROM user_passwords
WHERE user_id NOT IN (SELECT id FROM users WHERE email = 'VOTRE-EMAIL-ADMIN@example.com');

DELETE FROM user_profiles
WHERE user_id NOT IN (SELECT id FROM users WHERE email = 'VOTRE-EMAIL-ADMIN@example.com');

-- Supprimer les comptes
DELETE FROM users
WHERE email != 'VOTRE-EMAIL-ADMIN@example.com';

COMMIT;

-- Vérifier
SELECT email, username, role FROM users;
```

---

### 6️⃣ Quitter

**Tapez :**

```sql
\q
```

---

## ✅ Avantages de CloudShell

- ✅ **Pas besoin d'installation** (tout dans le navigateur)
- ✅ **Pas besoin de configurer le firewall** (CloudShell est dans AWS)
- ✅ **Pas de problème d'IP** (CloudShell a accès au VPC)
- ✅ **Gratuit** (inclus dans AWS)

---

## 🆘 Si CloudShell ne démarre pas

**Essayez la méthode Lambda ci-dessous !**

