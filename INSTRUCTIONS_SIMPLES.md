# 📋 INSTRUCTIONS SIMPLES - SUPPRIMER TOUS LES COMPTES

## 🎯 CE QUE VOUS DEVEZ FAIRE

### 1. Ouvrir le fichier SQL

J'ai créé le fichier : **`supprimer-tous-comptes.sql`**

### 2. Se connecter à votre base de données PostgreSQL

**Méthode la plus simple : AWS RDS Query Editor (en français)**

1. Allez sur https://console.aws.amazon.com
2. **Changez la langue en Français** (en haut à droite si nécessaire)
3. Dans la **barre de recherche en haut**, tapez **"RDS"**
4. Cliquez sur **"RDS"** dans les résultats
5. Dans le **menu de gauche**, cliquez sur **"Éditeur de requêtes"** (ou "Query Editor")
6. Sélectionnez votre base de données **`mapevent`**
7. Entrez vos identifiants :
   - **Utilisateur** : `postgres`
   - **Mot de passe** : votre mot de passe RDS
8. Cliquez sur **"Se connecter"** (ou "Connect")

### 3. Exécuter le script SQL

1. Ouvrez le fichier `supprimer-tous-comptes.sql`
2. Copiez-collez le contenu dans l'éditeur SQL
3. Exécutez d'abord les requêtes de vérification (SELECT)
4. Quand vous êtes prêt, **décommentez** la ligne `DELETE FROM users;`
5. Exécutez la suppression

### 4. Vérifier

Exécutez :
```sql
SELECT COUNT(*) FROM users;
```

Devrait retourner **0**.

---

## ✅ C'EST TOUT !

Une fois fait :
- ✅ Tous les comptes sont supprimés
- ✅ Vous pouvez créer un nouveau compte admin via l'interface web
- ✅ Le nouveau système professionnel sera automatiquement utilisé

---

## 📝 FICHIERS CRÉÉS

- **`supprimer-tous-comptes.sql`** - Script SQL à exécuter
- **`GUIDE_SUPPRESSION_SQL.md`** - Guide détaillé
- **`GUIDE_AWS_FRANCAIS.md`** - Guide AWS en français (étape par étape)
- **`INSTRUCTIONS_SIMPLES.md`** - Ce fichier (instructions rapides)

---

**C'est la méthode la plus simple et la plus fiable !** 🚀

