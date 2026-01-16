# ✅ SOLUTION SIMPLE : Supprimer les comptes

## 🎯 Problème actuel

Il y a une erreur de syntaxe dans `main.py` ligne 2433 qui empêche Lambda de fonctionner correctement.

## ✅ SOLUTION TEMPORAIRE : Utiliser directement PostgreSQL

Puisque toutes les méthodes de connexion échouent (timeout, API Gateway non configuré, erreur Lambda), **la solution la plus simple est d'utiliser AWS RDS Data API ou d'attendre que Lambda soit corrigé**.

## 🚀 SOLUTION RECOMMANDÉE : Corriger Lambda d'abord

**Avant de pouvoir supprimer les comptes, il faut corriger l'erreur dans Lambda.**

### Étape 1 : Corriger l'erreur dans `main.py`

L'erreur est à la ligne 2433. Il faut vérifier la structure du bloc `try/except`.

### Étape 2 : Redéployer Lambda

Une fois corrigé, redéployez Lambda avec `deploy-complet.ps1`.

### Étape 3 : Utiliser le script PowerShell

Une fois Lambda corrigé, utilisez `supprimer-comptes-direct-lambda.ps1` pour supprimer les comptes.

---

## 🆘 SOLUTION ALTERNATIVE : Utiliser pgAdmin (si la connexion fonctionne)

Si vous pouvez installer et configurer pgAdmin avec les identifiants RDS, vous pouvez exécuter le SQL directement :

```sql
-- Voir tous les comptes
SELECT email, username, role FROM users;

-- Supprimer tous sauf un
DELETE FROM users WHERE email != 'VOTRE-EMAIL-ADMIN@example.com';
```

---

## 📋 RÉSUMÉ

1. **Corriger l'erreur dans `main.py` ligne 2433**
2. **Redéployer Lambda**
3. **Utiliser `supprimer-comptes-direct-lambda.ps1`**

**OU**

1. **Installer pgAdmin**
2. **Se connecter à RDS**
3. **Exécuter le SQL manuellement**

---

**Je vais corriger l'erreur dans `main.py` maintenant !**

