# 🚀 Exécuter le Script SQL - Instructions PowerShell

## 📍 Vous êtes dans le mauvais répertoire !

Le script `creer-colonnes-users.ps1` est dans le dossier `frontend`.

## ✅ Solution Rapide

### Option 1 : Naviguer vers le bon répertoire

```powershell
cd C:\MapEventAI_NEW\frontend
.\creer-colonnes-users.ps1
```

### Option 2 : Utiliser le chemin complet

```powershell
C:\MapEventAI_NEW\frontend\creer-colonnes-users.ps1
```

### Option 3 : Si psql n'est pas installé (Alternative)

Si vous n'avez pas PostgreSQL installé localement, utilisez **pgAdmin** ou **DBeaver** :

1. **Téléchargez pgAdmin** : https://www.pgadmin.org/download/
2. **Connectez-vous à votre base de données RDS** :
   - Host: `mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com`
   - Port: `5432`
   - Database: `mapevent`
   - User: `postgres`
   - Password: (votre mot de passe RDS)
3. **Ouvrez le fichier** `CREER_COLONNES_USERS.sql`
4. **Exécutez le script** (F5 ou bouton "Execute")

## 🔍 Vérifier que le fichier existe

```powershell
cd C:\MapEventAI_NEW\frontend
ls creer-colonnes-users.ps1
ls CREER_COLONNES_USERS.sql
```

## ✅ Après exécution

Une fois le script SQL exécuté, testez la connexion Google :
1. Videz le cache (Ctrl+Shift+Delete)
2. Allez sur https://mapevent.world
3. Cliquez sur "Compte" → "Connexion avec Google"









