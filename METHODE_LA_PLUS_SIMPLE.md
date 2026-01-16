# 🎯 MÉTHODE LA PLUS SIMPLE - GARDER UN COMPTE ADMIN

## ✅ OUI, GARDEZ UN COMPTE ADMIN !

C'est la méthode la plus simple : **garder votre compte admin et supprimer tous les autres**.

---

## 📋 ÉTAPES SIMPLES

### Étape 1 : Voir tous les comptes

Dans l'éditeur SQL (AWS ou pgAdmin), exécutez :

```sql
SELECT id, email, username, role, created_at 
FROM users 
ORDER BY created_at DESC;
```

Cela vous montrera **tous les comptes** avec leur rôle.

---

### Étape 2 : Identifier votre compte admin

Regardez la liste et trouvez :
- **Votre compte principal** (celui que vous utilisez)
- OU un compte avec le rôle **"director"** ou **"admin"**

**Notez l'EMAIL** de ce compte (exemple : `admin@mapevent.world`)

---

### Étape 3 : Supprimer tous les autres comptes

Exécutez cette commande en remplaçant l'email :

```sql
DELETE FROM users WHERE email != 'VOTRE-EMAIL-ADMIN@example.com';
```

**Exemple :**
```sql
DELETE FROM users WHERE email != 'admin@mapevent.world';
```

Cela supprimera **tous les comptes sauf celui que vous gardez**.

---

### Étape 4 : Vérifier

```sql
SELECT id, email, username, role FROM users;
```

Vous devriez voir **uniquement votre compte admin**.

---

### Étape 5 : S'assurer que c'est bien un admin

Si votre compte n'a pas le rôle "director" ou "admin", modifiez-le :

```sql
UPDATE users SET role = 'director' WHERE email = 'VOTRE-EMAIL-ADMIN@example.com';
```

---

## 📝 SCRIPT PRÊT À UTILISER

J'ai créé le fichier **`supprimer-comptes-sauf-admin.sql`** qui contient toutes ces étapes.

1. Ouvrez ce fichier
2. Copiez-collez dans l'éditeur SQL
3. Exécutez étape par étape
4. Modifiez l'email dans la commande DELETE

---

## ✅ AVANTAGES

- ✅ Vous gardez votre compte
- ✅ Pas besoin de recréer un compte admin
- ✅ Plus simple et plus rapide
- ✅ Vous pouvez continuer à utiliser votre compte immédiatement

---

## 🎯 RÉSUMÉ

1. **Voir tous les comptes** : `SELECT * FROM users;`
2. **Noter l'email de votre compte admin**
3. **Supprimer les autres** : `DELETE FROM users WHERE email != 'votre-email@example.com';`
4. **Vérifier** : `SELECT * FROM users;` (devrait retourner 1 seul compte)
5. **Mettre le rôle en 'director'** si nécessaire : `UPDATE users SET role = 'director' WHERE email = 'votre-email@example.com';`

**C'est la méthode la plus simple !** 🚀



