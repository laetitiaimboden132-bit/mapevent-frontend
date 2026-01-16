# 🗑️ GUIDE : SUPPRIMER TOUS LES COMPTES VIA SQL

## 📋 MÉTHODE LA PLUS SIMPLE ET FIABLE

Cette méthode supprime directement tous les comptes dans la base de données PostgreSQL (RDS).

---

## ✅ ÉTAPES

### Étape 1 : Se connecter à PostgreSQL

**Option A : Via AWS RDS Query Editor** (recommandé - EN FRANÇAIS)
1. Ouvrez la console AWS : https://console.aws.amazon.com
2. En haut à droite, changez la langue en **Français** si nécessaire
3. Dans la barre de recherche en haut, tapez **"RDS"**
4. Cliquez sur **"RDS"** dans les résultats
5. Dans le menu de gauche, cliquez sur **"Éditeur de requêtes"** (Query Editor)
6. Sélectionnez votre base de données `mapevent`
7. Entrez vos identifiants (utilisateur : `postgres`, mot de passe : votre mot de passe RDS)
8. Cliquez sur **"Se connecter"**

**Option B : Via psql (ligne de commande)**
```bash
psql -h mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com -U postgres -d mapevent
```

**Option C : Via un client PostgreSQL** (pgAdmin, DBeaver, etc.)
- Host: `mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com`
- Port: `5432`
- Database: `mapevent`
- User: `postgres`
- Password: (votre mot de passe RDS)

---

### Étape 2 : Vérifier les comptes existants

Exécutez d'abord cette requête pour voir combien de comptes existent :

```sql
SELECT COUNT(*) as nombre_utilisateurs FROM users;
```

Pour voir la liste complète :

```sql
SELECT id, email, username, role, created_at FROM users ORDER BY created_at DESC;
```

---

### Étape 3 : Supprimer tous les comptes

**⚠️ ATTENTION : Cette opération est IRRÉVERSIBLE !**

Exécutez cette commande :

```sql
DELETE FROM users;
```

**Ce qui sera supprimé automatiquement (CASCADE) :**
- ✅ Tous les utilisateurs
- ✅ Tous les mots de passe (`user_passwords`)
- ✅ Tous les likes (`user_likes`)
- ✅ Tous les favoris (`user_favorites`)
- ✅ Toutes les entrées d'agenda (`user_agenda`)
- ✅ Toutes les participations (`user_participations`)
- ✅ Tous les avis (`user_reviews`)
- ✅ Tous les abonnements (`subscriptions`)
- ✅ Toutes les données associées

---

### Étape 4 : Vérifier que tout a été supprimé

```sql
SELECT COUNT(*) as nombre_utilisateurs_restants FROM users;
```

Devrait retourner **0**.

---

## 📝 SCRIPT COMPLET

J'ai créé le fichier `supprimer-tous-comptes.sql` que vous pouvez :
1. Ouvrir dans votre client PostgreSQL
2. Exécuter étape par étape
3. Décommenter la ligne `DELETE FROM users;` quand vous êtes prêt

---

## ✅ APRÈS LA SUPPRESSION

Une fois tous les comptes supprimés :

1. **Tous les nouveaux comptes** bénéficieront automatiquement du nouveau système professionnel
2. **Vous pourrez créer un compte admin** via l'interface web
3. **Le système sera prêt** avec toutes les mesures de sécurité

---

## 🎯 RÉSUMÉ

1. ✅ Se connecter à PostgreSQL (RDS)
2. ✅ Vérifier les comptes existants
3. ✅ Exécuter `DELETE FROM users;`
4. ✅ Vérifier que tout est supprimé (COUNT = 0)
5. ✅ Créer un nouveau compte admin via l'interface web

**C'est la méthode la plus rapide et la plus fiable !** 🚀

