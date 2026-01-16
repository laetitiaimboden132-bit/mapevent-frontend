# 🔐 Autoriser votre IP dans les Security Groups RDS

## Problème
Le script Python ne peut pas se connecter à RDS car votre IP n'est pas autorisée.

## Solution : Autoriser votre IP dans AWS

### Étape 1 : Trouver votre IP publique

1. Ouvrez votre navigateur
2. Allez sur : https://www.whatismyip.com/
3. Notez votre **IPv4 Address** (ex: `123.45.67.89`)

### Étape 2 : Autoriser votre IP dans AWS Console

1. **Connectez-vous à AWS Console** : https://console.aws.amazon.com/
2. **Allez dans RDS** :
   - Recherchez "RDS" dans la barre de recherche
   - Cliquez sur "RDS"
3. **Trouvez votre base de données** :
   - Dans le menu de gauche, cliquez sur "Databases"
   - Trouvez `mapevent-db` dans la liste
   - Cliquez sur le nom de la base de données
4. **Accédez aux Security Groups** :
   - Dans l'onglet "Connectivity & security"
   - Trouvez "VPC security groups"
   - Cliquez sur le Security Group (ex: `sg-xxxxxxxxx`)
5. **Modifiez les règles entrantes** :
   - Cliquez sur l'onglet "Inbound rules"
   - Cliquez sur "Edit inbound rules"
   - Cliquez sur "Add rule"
   - Configurez :
     - **Type** : PostgreSQL
     - **Protocol** : TCP
     - **Port** : 5432
     - **Source** : My IP (ou entrez votre IP manuellement : `123.45.67.89/32`)
   - Cliquez sur "Save rules"

### Étape 3 : Réessayer le script

```powershell
cd C:\MapEventAI_NEW\frontend
python creer-colonnes-users.py
```

## Alternative : Utiliser pgAdmin (Plus simple)

Si vous préférez utiliser une interface graphique :

1. **Téléchargez pgAdmin** : https://www.pgadmin.org/download/pgadmin-4-windows/
2. **Installez pgAdmin**
3. **Connectez-vous** :
   - Host: `mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com`
   - Port: `5432`
   - Database: `mapevent`
   - Username: `postgres`
   - Password: `666666Laeti69!`
4. **Ouvrez** le fichier `C:\MapEventAI_NEW\frontend\CREER_COLONNES_USERS.sql`
5. **Exécutez** le script (F5 ou bouton "Execute")

## Note importante

⚠️ **Sécurité** : Après avoir autorisé votre IP, assurez-vous de :
- Ne pas partager votre mot de passe
- Révoquer l'accès si vous changez d'emplacement
- Utiliser un VPN si vous êtes sur un réseau public









