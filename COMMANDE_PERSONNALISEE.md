# 📋 COMMANDE PERSONNALISÉE POUR VOUS

## 🎯 ÉTAPE 1 : TROUVER VOTRE COMPTE

**Exécutez cette requête dans pgAdmin :**

```sql
SELECT email, username, role, first_name, last_name 
FROM users 
ORDER BY created_at DESC;
```

**Regardez les résultats et notez :**
- **Votre email** (celui que vous utilisez)
- **Votre nom** (first_name, last_name)

---

## 🎯 ÉTAPE 2 : ME DIRE QUEL EMAIL GARDER

**Une fois que vous avez vu vos comptes, dites-moi :**
- "Je veux garder le compte avec l'email : [votre-email]"

**Et je vous donnerai la commande exacte !**

---

## 🎯 ÉTAPE 3 : COMMANDE EXACTE (à venir)

**Une fois que vous me donnez l'email, je vous donnerai cette commande :**

```sql
DELETE FROM users WHERE email != 'VOTRE-EMAIL-ICI@example.com';
```

**Remplacez `VOTRE-EMAIL-ICI@example.com` par votre email réel.**

---

## ✅ EXEMPLE

**Si votre email est `admin@mapevent.world`, la commande sera :**

```sql
DELETE FROM users WHERE email != 'admin@mapevent.world';
```

---

**Exécutez la première requête, regardez vos comptes, et dites-moi quel email vous voulez garder !** 🚀



