# 🗄️ Création de RDS et Redis pour MapEventAI

## Option 1: Via AWS Console (Recommandé pour débutants)

### Créer une instance RDS PostgreSQL

1. Allez sur https://console.aws.amazon.com/rds/
2. Cliquez sur **"Create database"**
3. Choisissez:
   - **Engine**: PostgreSQL
   - **Version**: 15.x ou 16.x (recommandé)
   - **Template**: Free tier (si disponible) ou Dev/Test
   - **DB instance identifier**: `mapevent-db`
   - **Master username**: `admin` (ou autre)
   - **Master password**: Choisissez un mot de passe fort
   - **Instance class**: `db.t3.micro` (gratuit) ou `db.t3.small`
   - **Storage**: 20 GB (gratuit) ou plus
   - **Region**: `eu-west-1` (Irlande)
4. Cliquez sur **"Create database"**
5. Attendez 5-10 minutes que l'instance soit créée
6. Notez l'**Endpoint** (ex: `mapevent-db.xxxxx.eu-west-1.rds.amazonaws.com`)

### Créer un cluster ElastiCache Redis

1. Allez sur https://console.aws.amazon.com/elasticache/
2. Cliquez sur **"Create"** > **"Redis cluster"**
3. Choisissez:
   - **Name**: `mapevent-redis`
   - **Engine version**: Latest
   - **Node type**: `cache.t3.micro` (gratuit) ou `cache.t3.small`
   - **Number of nodes**: 1
   - **Region**: `eu-west-1`
4. Cliquez sur **"Create"**
5. Attendez 5-10 minutes
6. Notez l'**Primary endpoint** (ex: `mapevent-redis.xxxxx.cache.amazonaws.com`)

## Option 2: Via AWS CLI

### Créer RDS

```powershell
aws rds create-db-instance `
    --db-instance-identifier mapevent-db `
    --db-instance-class db.t3.micro `
    --engine postgres `
    --engine-version 15.4 `
    --master-username admin `
    --master-user-password VotreMotDePasse123! `
    --allocated-storage 20 `
    --storage-type gp3 `
    --vpc-security-group-ids sg-xxxxx `
    --db-subnet-group-name default `
    --backup-retention-period 7 `
    --region eu-west-1
```

**Note**: Remplacez `sg-xxxxx` par votre Security Group ID.

### Créer Redis

```powershell
aws elasticache create-cache-cluster `
    --cache-cluster-id mapevent-redis `
    --cache-node-type cache.t3.micro `
    --engine redis `
    --engine-version 7.0 `
    --num-cache-nodes 1 `
    --region eu-west-1
```

## Option 3: Utiliser le script automatique

```powershell
.\find_aws_resources.ps1
```

Ce script va:
1. Chercher les instances RDS existantes
2. Chercher les clusters Redis existants
3. Vous permettre de sélectionner ou créer
4. Mettre à jour automatiquement `lambda.env`

## ⚙️ Configuration après création

### 1. Configurer les Security Groups

**RDS Security Group** doit autoriser:
- Port 5432 depuis votre Lambda (ou 0.0.0.0/0 pour test)
- Source: Votre VPC ou Security Group Lambda

**Redis Security Group** doit autoriser:
- Port 6379 depuis votre Lambda
- Source: Votre VPC ou Security Group Lambda

### 2. Créer la base de données

Connectez-vous à RDS et exécutez:

```sql
CREATE DATABASE mapevent;
```

Puis exécutez le schéma:

```powershell
psql -h votre-rds-endpoint -U admin -d mapevent -f backend/database/schema.sql
```

### 3. Mettre à jour lambda.env

```env
RDS_HOST=votre-rds-endpoint.eu-west-1.rds.amazonaws.com
RDS_PORT=5432
RDS_DB=mapevent
RDS_USER=admin
RDS_PASSWORD=VotreMotDePasse123!

REDIS_HOST=votre-redis-endpoint.cache.amazonaws.com
REDIS_PORT=6379
```

### 4. Configurer Lambda

```powershell
.\configure_lambda_env.ps1
```

## 💰 Coûts estimés

### RDS db.t3.micro (Free Tier)
- **Gratuit**: 750 heures/mois pendant 12 mois
- **Payant**: ~$15/mois après

### Redis cache.t3.micro (Free Tier)
- **Gratuit**: 750 heures/mois pendant 12 mois
- **Payant**: ~$12/mois après

## ✅ Checklist

- [ ] Instance RDS créée
- [ ] Cluster Redis créé
- [ ] Security Groups configurés
- [ ] Base de données `mapevent` créée
- [ ] Schéma SQL exécuté
- [ ] lambda.env mis à jour
- [ ] Variables d'environnement Lambda configurées
- [ ] Test de connexion réussi

## 🐛 Dépannage

**Erreur de connexion RDS**
- Vérifiez les Security Groups
- Vérifiez que l'instance est dans le même VPC que Lambda
- Vérifiez le mot de passe

**Erreur de connexion Redis**
- Vérifiez les Security Groups
- Vérifiez que le cluster est accessible depuis Lambda
- Vérifiez le port (6379)





