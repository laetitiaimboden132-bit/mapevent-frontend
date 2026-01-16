# 🔍 TROUVER VOTRE COMPTE ADMIN

## ❓ JE NE PEUX PAS SAVOIR QUEL EST VOTRE COMPTE

Je n'ai pas accès à votre base de données, donc je ne peux pas savoir quel est votre compte admin.

**Mais je peux vous aider à le trouver !** 🎯

---

## 🔍 MÉTHODE POUR TROUVER VOTRE COMPTE

### Étape 1 : Voir tous vos comptes

**Dans pgAdmin, exécutez cette requête :**

```sql
SELECT email, username, role, first_name, last_name, created_at 
FROM users 
ORDER BY created_at DESC;
```

**Cela vous montrera :**
- Tous vos comptes
- Leur email
- Leur username
- Leur rôle (user, director, admin)
- Leur nom
- La date de création

---

### Étape 2 : Identifier votre compte

**Cherchez :**
- ✅ **Votre email** (celui que vous utilisez normalement)
- ✅ **Votre nom** (first_name, last_name)
- ✅ **Le compte le plus récent** (probablement le vôtre si vous venez de le créer)

---

### Étape 3 : Vérifier le rôle

**Si votre compte a le rôle "user" au lieu de "director" ou "admin" :**

C'est normal ! Vous devrez le mettre en "director" après avoir supprimé les autres comptes.

---

## 📝 SCRIPT PRÊT À UTILISER

J'ai créé le fichier **`identifier-compte-admin.sql`** avec plusieurs requêtes utiles :

1. **Voir tous les comptes** (avec leur rôle)
2. **Voir uniquement les admins** (si vous en avez)
3. **Compter les comptes par rôle**
4. **Voir le compte le plus récent** (probablement le vôtre)

---

## 🎯 CE QUE VOUS DEVEZ FAIRE

1. **Installez pgAdmin** (si pas encore fait)
2. **Connectez-vous** à votre base de données
3. **Ouvrez Query Tool**
4. **Exécutez la première requête** du fichier `identifier-compte-admin.sql`
5. **Regardez les résultats** et identifiez votre compte (par email ou nom)
6. **Notez l'email** de votre compte
7. **Supprimez les autres** avec : `DELETE FROM users WHERE email != 'VOTRE-EMAIL@example.com';`

---

## 💡 ASTUCE

**Le compte le plus récent** (created_at le plus récent) est probablement le vôtre si vous venez de le créer récemment.

---

**Exécutez la requête et vous verrez tous vos comptes ! Ensuite, dites-moi quel email vous voulez garder et je vous donnerai la commande exacte.** 🚀



