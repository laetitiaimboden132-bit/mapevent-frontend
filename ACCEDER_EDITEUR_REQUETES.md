# 📋 COMMENT ACCÉDER À L'ÉDITEUR DE REQUÊTES

## 🎯 DEPUIS LA PAGE DE VOTRE BASE DE DONNÉES

Vous êtes actuellement sur la page de récapitulatif de **mapevent-db**.

### Méthode 1 : Via le menu de gauche (le plus simple)

1. **Regardez le menu de gauche** (à gauche de la page)
2. Cherchez **"Éditeur de requêtes"** ou **"Query Editor"**
3. Cliquez dessus
4. Si c'est la première fois, vous devrez peut-être :
   - Activer l'éditeur de requêtes
   - Créer une connexion

### Méthode 2 : Via le menu en haut

1. En haut de la page, vous verrez des onglets
2. Cherchez **"Éditeur de requêtes"** ou **"Query Editor"**
3. Cliquez dessus

### Méthode 3 : Depuis le menu principal RDS

1. Dans le **menu de gauche**, cliquez sur **"Bases de données"** (vous y êtes peut-être déjà)
2. Ensuite, cherchez **"Éditeur de requêtes"** dans le menu de gauche
3. Cliquez dessus

---

## 🔍 SI VOUS NE VOYEZ PAS "ÉDITEUR DE REQUÊTES"

L'éditeur de requêtes peut ne pas être disponible dans toutes les régions ou pour tous les types d'instances.

### Alternative : Utiliser un client PostgreSQL

Si l'éditeur de requêtes n'est pas disponible, vous pouvez utiliser :

1. **pgAdmin** (gratuit) : https://www.pgadmin.org/
2. **DBeaver** (gratuit) : https://dbeaver.io/
3. **psql** (ligne de commande)

**Informations de connexion :**
- **Host** : `mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com`
- **Port** : `5432`
- **Database** : `mapevent`
- **User** : `postgres`
- **Password** : `666666Laeti69!`

---

## 📝 UNE FOIS DANS L'ÉDITEUR DE REQUÊTES

1. Vous verrez un formulaire de connexion
2. **Sélectionnez** : `mapevent-db`
3. **Utilisateur** : `postgres`
4. **Mot de passe** : `666666Laeti69!`
5. Cliquez sur **"Se connecter"**
6. Ouvrez le fichier **`supprimer-tous-comptes.sql`**
7. Copiez-collez le contenu
8. Exécutez les requêtes

---

## 🆘 SI L'ÉDITEUR N'EST PAS DISPONIBLE

Utilisez un client PostgreSQL comme **pgAdmin** ou **DBeaver** avec les informations ci-dessus.



