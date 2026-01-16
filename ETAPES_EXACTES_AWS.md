# 📋 ÉTAPES EXACTES - AWS RDS EN FRANÇAIS

## 🎯 ÉTAPE PAR ÉTAPE

### 1. Accéder à RDS

1. Allez sur **https://console.aws.amazon.com**
2. Connectez-vous
3. Changez la langue en **Français** (en haut à droite)
4. Dans la barre de recherche, tapez **"RDS"**
5. Cliquez sur **"RDS"**

---

### 2. Ouvrir l'Éditeur de requêtes

1. Dans le menu de gauche, cliquez sur **"Éditeur de requêtes"** (Query Editor)

---

### 3. Sélectionner votre base de données

**OUI, vous devez cliquer sur "mapevent-db" !**

1. Dans l'éditeur de requêtes, vous verrez une liste de bases de données
2. **Cliquez sur "mapevent-db"** (c'est votre instance RDS)
3. OU si vous voyez directement un formulaire de connexion :
   - **Base de données** : Sélectionnez `mapevent-db`
   - **Utilisateur** : `postgres`
   - **Mot de passe** : Votre mot de passe RDS
   - Cliquez sur **"Se connecter"**

---

### 4. Si vous ne voyez pas "mapevent-db"

Si vous ne voyez pas votre base de données dans la liste :

1. Vérifiez que vous êtes dans la bonne **région AWS** (en haut à droite)
   - Votre base est probablement en **eu-west-1** (Irlande)
2. Vérifiez que votre base de données est **en cours d'exécution** (status "Disponible")
3. Si nécessaire, allez dans **"Bases de données"** dans le menu de gauche pour voir toutes vos bases

---

### 5. Une fois connecté

1. Vous verrez l'éditeur SQL
2. Ouvrez le fichier **`supprimer-tous-comptes.sql`**
3. Copiez tout le contenu
4. Collez-le dans l'éditeur
5. Exécutez les requêtes une par une

---

## ✅ RÉSUMÉ

- **OUI**, cliquez sur **"mapevent-db"** ✅
- C'est votre instance de base de données PostgreSQL
- Une fois sélectionnée, vous pourrez vous connecter et exécuter le SQL

---

**Suivez ces étapes et vous y arriverez !** 🚀



