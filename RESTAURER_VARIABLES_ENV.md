# 🔧 Restaurer les Variables d'Environnement Lambda

## ❌ Problème

Les variables d'environnement ont été perdues lors de l'upload du ZIP :
- `RDS_HOST` = vide
- `RDS_USER` = vide  
- `RDS_PASSWORD` = vide
- `RDS_PORT` = vide
- `RDS_DB` = vide

## ✅ Solution : Reconfigurer toutes les variables

Dans AWS Lambda Console :

1. **Lambda > `mapevent-backend` > Configuration > Environment variables**
2. Cliquer sur **"Edit"**
3. **Ajouter toutes les variables suivantes** :

### Variables RDS
- `RDS_HOST` = `mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com`
- `RDS_PORT` = `5432`
- `RDS_DB` = `mapevent`
- `RDS_USER` = `postgres`
- `RDS_PASSWORD` = `666666Laeti69!`

### Variables Redis
- `REDIS_HOST` = `mapevent-cache-0001-001.mapevent-cache.jqxmjs.euw1.cache.amazonaws.com`
- `REDIS_PORT` = `6379`

### Variables Stripe
- `STRIPE_SECRET_KEY` = `sk_test_...` (votre clé)
- `STRIPE_PUBLIC_KEY` = `pk_test_...` (votre clé)
- `STRIPE_WEBHOOK_SECRET` = `whsec_...` (votre secret)

### Variables Autres
- `FLASK_ENV` = `production`
- `GOOGLE_CLOUD_VISION_API_KEY` = (vide si pas utilisé)
- `S3_AVATARS_BUCKET` = `mapevent-avatars` ⚠️ **N'oubliez pas cette variable !**

4. Cliquer sur **"Save"**

## 📋 Checklist

- [ ] RDS_HOST configuré
- [ ] RDS_PORT configuré
- [ ] RDS_DB configuré
- [ ] RDS_USER configuré
- [ ] RDS_PASSWORD configuré
- [ ] REDIS_HOST configuré
- [ ] REDIS_PORT configuré
- [ ] STRIPE_SECRET_KEY configuré
- [ ] STRIPE_PUBLIC_KEY configuré
- [ ] STRIPE_WEBHOOK_SECRET configuré
- [ ] FLASK_ENV configuré
- [ ] S3_AVATARS_BUCKET configuré ⚠️ **IMPORTANT**

## ⚠️ Important

**Ne pas oublier** `S3_AVATARS_BUCKET` = `mapevent-avatars` qui est la nouvelle variable pour S3 !






