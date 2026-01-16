# 🚀 Commandes PowerShell à Exécuter

## 📍 Étape 1 : Naviguer vers le bon répertoire

```powershell
cd C:\MapEventAI_NEW\frontend
```

## 📋 Étape 2 : Vérifier que les fichiers existent

```powershell
ls CREER_COLONNES_USERS.sql
ls creer-colonnes-users.ps1
```

## ✅ Étape 3 : Exécuter le script

### Option A : Si vous avez PostgreSQL installé (psql)

```powershell
.\creer-colonnes-users.ps1
```

Le script vous demandera le mot de passe de la base de données.

### Option B : Si vous n'avez pas psql (Recommandé)

**Utilisez pgAdmin ou DBeaver** :

1. **Téléchargez pgAdmin** : https://www.pgadmin.org/download/pgadmin-4-windows/
2. **Installez pgAdmin**
3. **Connectez-vous à votre base de données RDS** :
   - Cliquez droit sur "Servers" → "Create" → "Server"
   - **General** → Name: `MapEvent RDS`
   - **Connection** :
     - Host: `mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com`
     - Port: `5432`
     - Database: `mapevent`
     - Username: `postgres`
     - Password: (votre mot de passe RDS)
   - Cliquez sur "Save"
4. **Ouvrez le fichier SQL** :
   - Dans pgAdmin, cliquez droit sur votre base de données `mapevent`
   - "Query Tool"
   - Ouvrez le fichier `C:\MapEventAI_NEW\frontend\CREER_COLONNES_USERS.sql`
   - Cliquez sur "Execute" (F5)

## 🔍 Vérifier que ça a fonctionné

Après exécution, testez la connexion Google :
1. Videz le cache (Ctrl+Shift+Delete)
2. Allez sur https://mapevent.world
3. Cliquez sur "Compte" → "Connexion avec Google"

## 📝 Si vous préférez une solution plus simple

Je peux créer un script qui exécute directement les commandes SQL via AWS CLI si vous préférez.









