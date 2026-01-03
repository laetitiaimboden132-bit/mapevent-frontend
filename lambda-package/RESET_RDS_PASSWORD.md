# 🔑 Réinitialiser le Mot de Passe RDS

## Option 1: Via AWS Console (Recommandé)

### Étape 1: Accéder à RDS

1. Allez sur https://console.aws.amazon.com/rds/
2. Cliquez sur **"Databases"** dans le menu de gauche
3. Sélectionnez votre instance `mapevent-db`

### Étape 2: Modifier le mot de passe

1. Cliquez sur **"Modify"** (Modifier) en haut à droite
2. Dans la section **"Settings"**, trouvez **"Master password"**
3. Cliquez sur **"Change master password"**
4. Entrez votre nouveau mot de passe (minimum 8 caractères)
5. Cliquez sur **"Continue"** en bas
6. Choisissez **"Apply immediately"** (Appliquer immédiatement)
7. Cliquez sur **"Modify DB instance"**

⚠️ **Attention**: L'instance sera redémarrée, ce qui peut prendre 2-5 minutes.

### Étape 3: Mettre à jour lambda.env

Une fois le mot de passe modifié, mettez à jour `lambda.env`:

```env
RDS_PASSWORD=VotreNouveauMotDePasse123!
```

Puis exécutez:

```powershell
.\configure_lambda_env.ps1
```

## Option 2: Via AWS CLI

```powershell
aws rds modify-db-instance `
    --db-instance-identifier mapevent-db `
    --master-user-password VotreNouveauMotDePasse123! `
    --apply-immediately `
    --region eu-west-1
```

⚠️ **Attention**: L'instance sera redémarrée.

## Option 3: Créer un Nouvel Utilisateur (Sans Redémarrage)

Si vous ne voulez pas redémarrer l'instance, vous pouvez créer un nouvel utilisateur avec un nouveau mot de passe:

### Via psql (si vous avez accès)

```sql
-- Se connecter en tant que postgres
psql -h mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com -U postgres -d postgres

-- Créer un nouvel utilisateur
CREATE USER mapevent_user WITH PASSWORD 'VotreNouveauMotDePasse123!';

-- Donner les permissions
GRANT ALL PRIVILEGES ON DATABASE mapevent TO mapevent_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mapevent_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO mapevent_user;

-- Mettre à jour lambda.env avec le nouvel utilisateur
```

Puis dans `lambda.env`:

```env
RDS_USER=mapevent_user
RDS_PASSWORD=VotreNouveauMotDePasse123!
```

## 🔍 Vérifier le Mot de Passe Actuel

Malheureusement, AWS ne permet pas de voir le mot de passe actuel pour des raisons de sécurité. Vous avez deux options:

1. **Réinitialiser le mot de passe** (redémarre l'instance)
2. **Créer un nouvel utilisateur** (pas de redémarrage)

## ✅ Après Réinitialisation

1. Attendez que l'instance soit disponible (status: Available)
2. Testez la connexion:
   ```powershell
   psql -h mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com -U postgres -d mapevent
   ```
3. Mettez à jour `lambda.env`
4. Exécutez `.\configure_lambda_env.ps1`
5. Testez les endpoints Lambda

## 🐛 Dépannage

**Erreur "password authentication failed"**
- Vérifiez que le mot de passe est correct dans `lambda.env`
- Vérifiez que l'instance est disponible (pas en "modifying")
- Attendez quelques minutes après la modification

**Instance en "modifying"**
- Attendez 2-5 minutes
- Vérifiez les événements dans la console RDS





