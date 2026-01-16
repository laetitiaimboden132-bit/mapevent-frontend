# 🇫🇷 GUIDE AWS EN FRANÇAIS - SUPPRIMER TOUS LES COMPTES

## 📋 ÉTAPES DÉTAILLÉES EN FRANÇAIS

### Étape 1 : Accéder à AWS Console

1. Ouvrez votre navigateur
2. Allez sur : **https://console.aws.amazon.com**
3. Connectez-vous avec vos identifiants AWS

---

### Étape 2 : Changer la langue en Français (si nécessaire)

1. En haut à droite de la page, cliquez sur le menu déroulant avec votre nom
2. Cherchez l'option **"Langue"** ou **"Language"**
3. Sélectionnez **"Français"** ou **"French"**
4. La page se rafraîchira en français

---

### Étape 3 : Accéder à RDS

1. En haut de la page, dans la **barre de recherche**, tapez : **"RDS"**
2. Cliquez sur **"RDS"** dans les résultats de recherche
3. Vous serez redirigé vers la page RDS

---

### Étape 4 : Ouvrir l'Éditeur de requêtes

1. Dans le **menu de gauche**, cherchez **"Éditeur de requêtes"** (ou "Query Editor")
2. Cliquez dessus
3. Si c'est la première fois, vous devrez peut-être activer l'éditeur de requêtes

---

### Étape 5 : Se connecter à votre base de données

1. Dans l'éditeur de requêtes, vous verrez un formulaire de connexion
2. **Sélectionnez votre base de données** : `mapevent` (ou le nom de votre base)
3. **Utilisateur** : `postgres`
4. **Mot de passe** : Entrez votre mot de passe RDS
5. Cliquez sur **"Se connecter"** (ou "Connect")

---

### Étape 6 : Exécuter le script SQL

1. Une fois connecté, vous verrez l'éditeur SQL
2. Ouvrez le fichier **`supprimer-tous-comptes.sql`** que j'ai créé
3. **Copiez tout le contenu** du fichier
4. **Collez-le** dans l'éditeur SQL d'AWS
5. **Exécutez d'abord les requêtes SELECT** pour voir combien de comptes existent :
   - Cliquez sur la première requête `SELECT COUNT(*)...`
   - Cliquez sur le bouton **"Exécuter"** (ou "Run")
   - Notez le nombre de comptes

6. **Quand vous êtes prêt à supprimer** :
   - Dans le script, trouvez la ligne : `-- DELETE FROM users;`
   - **Enlevez les `--`** au début pour décommenter : `DELETE FROM users;`
   - **Sélectionnez uniquement cette ligne**
   - Cliquez sur **"Exécuter"** (ou "Run")
   - Confirmez si demandé

---

### Étape 7 : Vérifier que tout est supprimé

1. Exécutez la dernière requête du script :
   ```sql
   SELECT COUNT(*) as nombre_utilisateurs_restants FROM users;
   ```
2. Le résultat devrait être **0**

---

## ⚠️ ATTENTION

- Cette opération est **IRRÉVERSIBLE**
- Tous les comptes et leurs données seront supprimés
- Les données associées (likes, favoris, etc.) seront supprimées automatiquement

---

## ✅ APRÈS LA SUPPRESSION

Une fois terminé :
- ✅ Tous les comptes sont supprimés
- ✅ Vous pouvez créer un nouveau compte admin via l'interface web
- ✅ Le nouveau système professionnel sera automatiquement utilisé

---

## 🆘 EN CAS DE PROBLÈME

### "Éditeur de requêtes" non disponible

Si vous ne voyez pas "Éditeur de requêtes" dans le menu :
1. Vérifiez que votre base de données RDS est bien active
2. Vérifiez que vous avez les permissions nécessaires
3. Essayez de rafraîchir la page

### Impossible de se connecter

1. Vérifiez que votre mot de passe RDS est correct
2. Vérifiez que votre Security Group autorise votre IP
3. Vérifiez que la base de données est bien en cours d'exécution

---

**C'est tout ! Suivez ces étapes et vous aurez supprimé tous les comptes.** 🚀



