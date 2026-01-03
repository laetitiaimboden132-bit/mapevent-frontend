# 🔐 Guide Complet : Autoriser votre IP dans RDS (Français)

## 📋 Objectif
Autoriser votre ordinateur à se connecter directement à la base de données RDS pour pouvoir exécuter des scripts SQL.

---

## Étape 1 : Trouver votre Adresse IP Publique

1. **Ouvrez votre navigateur** (Chrome, Firefox, Edge, etc.)
2. **Allez sur** : https://www.whatismyip.com/
3. **Notez votre IPv4** (exemple : `123.45.67.89`)
   - C'est votre adresse IP publique
   - Vous en aurez besoin dans quelques instants

---

## Étape 2 : Se Connecter à AWS Console

1. **Ouvrez** : https://console.aws.amazon.com/
2. **Connectez-vous** avec vos identifiants AWS
3. **Sélectionnez la région** : `eu-west-1` (Europe - Irlande)
   - En haut à droite, vérifiez que c'est bien "Europe (Ireland)"

---

## Étape 3 : Accéder à RDS

1. **Dans la barre de recherche** (en haut), tapez : `RDS`
2. **Cliquez sur** "RDS" dans les résultats
3. Vous arrivez sur la page principale de RDS

---

## Étape 4 : Trouver votre Base de Données

1. **Dans le menu de gauche**, cliquez sur **"Databases"** (Bases de données)
2. **Dans la liste**, trouvez `mapevent-db`
3. **Cliquez sur le nom** `mapevent-db` (pas sur la case à cocher)
4. Vous arrivez sur la page de détails de la base de données

---

## Étape 5 : Accéder aux Security Groups

1. **Faites défiler** jusqu'à la section **"Connectivity & security"** (Connectivité et sécurité)
2. **Trouvez** "VPC security groups" (Groupes de sécurité VPC)
3. Vous verrez quelque chose comme : `sg-xxxxxxxxx (default)`
4. **Cliquez sur le nom du Security Group** (ex: `sg-xxxxxxxxx`)

---

## Étape 6 : Modifier les Règles Entrantes (Inbound Rules)

1. **Vous arrivez sur la page du Security Group**
2. **Cliquez sur l'onglet** "Inbound rules" (Règles entrantes)
3. **Cliquez sur le bouton** "Edit inbound rules" (Modifier les règles entrantes)

---

## Étape 7 : Ajouter une Nouvelle Règle

1. **Cliquez sur** "Add rule" (Ajouter une règle)
2. **Remplissez les champs** :
   - **Type** : Sélectionnez `PostgreSQL` dans le menu déroulant
   - **Protocol** : Devrait être automatiquement `TCP`
   - **Port range** : `5432`
   - **Source** : 
     - Option 1 : Cliquez sur "My IP" (Mon IP) - AWS détecte automatiquement votre IP
     - Option 2 : Sélectionnez "Custom" et entrez votre IP avec `/32` à la fin
       - Exemple : `123.45.67.89/32`
       - Le `/32` signifie "cette IP exacte uniquement"
   - **Description** : `Accès administration depuis mon ordinateur` (optionnel mais recommandé)

3. **Vérifiez** que tout est correct
4. **Cliquez sur** "Save rules" (Enregistrer les règles)

---

## Étape 8 : Vérifier que ça Marche

1. **Retournez dans RDS** → Databases → `mapevent-db`
2. **Notez l'endpoint** (ex: `mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com`)
3. **Testez la connexion** avec pgAdmin ou le script Python

---

## ✅ C'est Fait !

Votre IP est maintenant autorisée à se connecter à RDS.

### Prochaines Étapes

1. **Installez pgAdmin** : https://www.pgadmin.org/download/pgadmin-4-windows/
2. **Configurez la connexion** avec les informations :
   - Host: `mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com`
   - Port: `5432`
   - Database: `mapevent`
   - Username: `postgres`
   - Password: `666666Laeti69!`
3. **Exécutez** `CREER_COLONNES_USERS.sql`

---

## ⚠️ Notes Importantes

- **Sécurité** : Cette règle autorise SEULEMENT votre IP actuelle
- **IP changeante** : Si votre IP change (nouveau WiFi, VPN), vous devrez réautoriser
- **Utilisateurs** : Les utilisateurs du site ne sont PAS affectés (ils passent par Lambda)
- **Temps** : Les règles peuvent prendre quelques secondes à s'appliquer

---

## 🆘 En Cas de Problème

### "My IP" ne fonctionne pas
- Utilisez l'option "Custom" et entrez votre IP manuellement avec `/32`
- Vérifiez votre IP sur https://www.whatismyip.com/

### La connexion ne marche toujours pas
1. Vérifiez que votre IP est bien dans les règles entrantes
2. Attendez 30 secondes (les règles peuvent prendre du temps)
3. Vérifiez que le Security Group est bien attaché à votre base de données RDS
4. Vérifiez que le port est bien `5432`

### Vous ne trouvez pas le Security Group
- Dans la page de détails de `mapevent-db`, section "Connectivity & security"
- Cliquez directement sur le nom du Security Group (ex: `sg-xxxxxxxxx`)

---

## 📸 Aperçu Visuel (Description)

**Page RDS Databases** :
- Liste des bases de données
- Cliquez sur `mapevent-db`

**Page Détails Base de Données** :
- Section "Connectivity & security"
- "VPC security groups" → Cliquez sur le nom

**Page Security Group** :
- Onglet "Inbound rules"
- Bouton "Edit inbound rules"
- "Add rule" → Remplissez → "Save rules"

---

**Bon courage ! 🚀**


