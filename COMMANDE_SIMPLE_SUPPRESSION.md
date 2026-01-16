# 🎯 COMMANDE SIMPLE - GARDER VOTRE COMPTE ADMIN

## 📋 MÉTHODE ULTRA-SIMPLE

### 1. Voir tous vos comptes

Exécutez cette requête pour voir tous les comptes :

```sql
SELECT email, username, role FROM users;
```

### 2. Notez l'email de VOTRE compte (celui que vous voulez garder)

Par exemple : `admin@mapevent.world` ou `votre-email@gmail.com`

### 3. Supprimez tous les autres

Remplacez `'votre-email@example.com'` par VOTRE email réel :

```sql
DELETE FROM users WHERE email != 'votre-email@example.com';
```

**Exemple concret :**
```sql
DELETE FROM users WHERE email != 'admin@mapevent.world';
```

### 4. Vérifiez

```sql
SELECT email, username, role FROM users;
```

Vous devriez voir **uniquement votre compte**.

### 5. Mettez le rôle en 'director' si nécessaire

```sql
UPDATE users SET role = 'director' WHERE email = 'votre-email@example.com';
```

---

## ✅ C'EST TOUT !

Après ça :
- ✅ Vous gardez votre compte
- ✅ Tous les autres comptes sont supprimés
- ✅ Vous pouvez créer de nouveaux comptes avec le nouveau système
- ✅ Votre compte peut servir d'admin pour gérer les autres

---

**C'est la méthode la plus simple !** 🚀



