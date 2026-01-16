# 📋 COMMANDES SQL COMPLÈTES - COPIER-COLLER

## 🎯 ÉTAPE 1 : VOIR TOUS VOS COMPTES

**Copiez et collez cette commande dans pgAdmin :**

```sql
SELECT email, username, role FROM users;
```

**Cliquez sur ▶️ (Execute) ou appuyez sur F5**

**Vous verrez tous vos comptes dans un tableau !**

---

## 🎯 ÉTAPE 2 : SUPPRIMER TOUS LES COMPTES SAUF LE VÔTRE

**Remplacez `'VOTRE-EMAIL@example.com'` par VOTRE email réel :**

```sql
DELETE FROM users WHERE email != 'VOTRE-EMAIL@example.com';
```

**Exemple :**
```sql
DELETE FROM users WHERE email != 'admin@mapevent.world';
```

**Cliquez sur ▶️ (Execute) ou appuyez sur F5**

---

## 🎯 ÉTAPE 3 : VÉRIFIER

**Copiez et collez :**

```sql
SELECT email, username, role FROM users;
```

**Vous devriez voir uniquement votre compte !**

---

## 🎯 ÉTAPE 4 : METTRE LE RÔLE EN 'director' (si nécessaire)

**Remplacez l'email par le vôtre :**

```sql
UPDATE users SET role = 'director' WHERE email = 'VOTRE-EMAIL@example.com';
```

**Cliquez sur ▶️ (Execute)**

---

## ✅ RÉSUMÉ

1. **Installez pgAdmin** (https://www.pgadmin.org/download/)
2. **Connectez-vous** avec les informations de votre base
3. **Ouvrez Query Tool** (clic droit sur "mapevent" > "Query Tool")
4. **Exécutez les commandes ci-dessus** une par une

**C'est tout !** 🚀



