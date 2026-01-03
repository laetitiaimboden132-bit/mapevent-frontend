# 🔐 Mot de Passe RDS

## 📍 Emplacement

Le mot de passe RDS est stocké dans : `lambda-package/lambda.env`

## 🔑 Mot de Passe Actuel

```
RDS_PASSWORD=666666Laeti69!
```

## ✅ Utilisation

### Option 1 : Script Automatique (Recommandé)

Le script `creer-colonnes-users.ps1` récupère automatiquement le mot de passe depuis `lambda.env` :

```powershell
cd C:\MapEventAI_NEW\frontend
.\creer-colonnes-users.ps1
```

### Option 2 : Manuellement avec pgAdmin

1. **Téléchargez pgAdmin** : https://www.pgadmin.org/download/pgadmin-4-windows/
2. **Connectez-vous** :
   - Host: `mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com`
   - Port: `5432`
   - Database: `mapevent`
   - Username: `postgres`
   - **Password: `666666Laeti69!`**
3. **Exécutez** `CREER_COLONNES_USERS.sql`

### Option 3 : Avec psql en ligne de commande

```powershell
$env:PGPASSWORD = "666666Laeti69!"
psql -h mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com -U postgres -d mapevent -f CREER_COLONNES_USERS.sql
```

## 🔒 Sécurité

⚠️ **Important** : Ne partagez jamais ce mot de passe publiquement. Il est uniquement pour votre usage personnel.


