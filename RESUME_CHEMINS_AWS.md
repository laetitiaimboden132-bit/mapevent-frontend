# 📍 RÉSUMÉ DES CHEMINS AWS - MAPEVENT

## 🌍 RÉGION AWS
**Région principale :** `eu-west-1` (Europe - Irlande)

---

## 🔗 DOMAINE PRINCIPAL
**URL de production :** `https://mapevent.world`

---

## 🚀 API GATEWAY

### Informations générales
- **API Gateway ID :** `j33osy4bvj`
- **Stage :** `default`
- **Région :** `eu-west-1`
- **URL de base :** `https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default`

### Endpoints principaux

#### Authentification OAuth Google
- **Endpoint :** `https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/user/oauth/google`
- **Méthode :** `POST`
- **Resource ID :** `k70u2t`
- **CORS :** Configuré pour `https://mapevent.world`

#### Complétion profil Google
- **Endpoint :** `https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/user/oauth/google/complete`
- **Méthode :** `POST`
- **Resource ID :** `rjh1m4`
- **CORS :** Configuré pour `https://mapevent.world`

#### Autres endpoints (tous sous `/api/...`)
- Base : `https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api`

---

## ⚡ LAMBDA FUNCTION

### Informations
- **Nom de la fonction :** `mapevent-backend`
- **Région :** `eu-west-1`
- **Handler :** `lambda_function.lambda_handler`
- **Runtime :** Python 3.12 (ou similaire)
- **Timeout :** 15 minutes (max)
- **Memory :** Variable (à vérifier)

### Logs CloudWatch
- **Log Group :** `/aws/lambda/mapevent-backend`
- **Région :** `eu-west-1`
- **Commande pour voir les logs :**
  ```powershell
  aws logs tail /aws/lambda/mapevent-backend --follow --region eu-west-1
  ```

### Variables d'environnement Lambda
Voir `lambda-package/lambda.env` pour les valeurs complètes :
- `RDS_HOST`
- `RDS_PORT`
- `RDS_DB`
- `RDS_USER`
- `RDS_PASSWORD`
- `REDIS_HOST`
- `REDIS_PORT`
- `AWS_REGION`
- `GOOGLE_CLOUD_VISION_API_KEY` (optionnel)
- `STRIPE_SECRET_KEY` (optionnel)
- `STRIPE_PUBLIC_KEY` (optionnel)
- `STRIPE_WEBHOOK_SECRET` (optionnel)
- `FLASK_ENV`

---

## 🗄️ BASE DE DONNÉES RDS (PostgreSQL)

### Informations de connexion
- **Endpoint :** `mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com`
- **Port :** `5432`
- **Base de données :** `mapevent`
- **Utilisateur :** `postgres`
- **Mot de passe :** (voir `lambda-package/lambda.env`)
- **Région :** `eu-west-1`
- **Engine :** PostgreSQL
- **Instance ID :** `mapevent-db`

### Connexion depuis Lambda
- Les variables d'environnement Lambda contiennent les credentials
- Connexion via `psycopg2` avec SSL (`sslmode='require'`)

---

## 🔴 REDIS (ElastiCache)

### Informations
- **Endpoint :** `mapevent-cache-0001-001.mapevent-cache.jqxmjs.euw1.cache.amazonaws.com`
- **Port :** `6379`
- **Région :** `eu-west-1`
- **Cluster ID :** `mapevent-cache`

---

## 🔐 AWS COGNITO (Authentification Google OAuth)

### Informations
- **Cognito Domain :** `eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com`
- **URL complète :** `https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com`
- **Région :** `eu-west-1`
- **User Pool ID :** (à récupérer depuis la console AWS Cognito)
- **App Client ID :** (à récupérer depuis la console AWS Cognito)
- **Redirect URI :** `https://mapevent.world/`

### Configuration OAuth
- **Provider :** Google
- **Flow :** PKCE (Proof Key for Code Exchange) pour SPA
- **Scopes :** `openid email profile`

### Console AWS Cognito
- **URL Console :** https://console.aws.amazon.com/cognito/
- **Région :** `eu-west-1`
- Chercher le User Pool avec le domaine `eu-west-19o9j6xsdr`

---

## ☁️ CLOUDFRONT (Distribution CDN)

### Informations
- **Domain :** `mapevent.world`
- **Distribution ID :** (à récupérer depuis la console CloudFront)
- **Origin :** (S3 bucket ou autre)
- **Région :** `eu-west-1` (ou global)

### Console CloudFront
- **URL Console :** https://console.aws.amazon.com/cloudfront/
- Chercher la distribution pour `mapevent.world`

---

## 📦 S3 (Stockage Frontend - si applicable)

### Informations
- **Bucket Name :** (à vérifier - probablement `mapevent-world` ou similaire)
- **Région :** `eu-west-1` (ou autre selon configuration)
- **Website Endpoint :** (si configuré comme site statique)

---

## 🔑 CERTIFICAT SSL (ACM - AWS Certificate Manager)

### Informations
- **Domain :** `mapevent.world`
- **Région :** `us-east-1` (pour CloudFront) ou `eu-west-1` (pour API Gateway)
- **Status :** Validé (probablement)

### Console ACM
- **URL Console :** https://console.aws.amazon.com/acm/
- Chercher le certificat pour `mapevent.world`

---

## 📊 ROUTE 53 (DNS)

### Informations
- **Domain :** `mapevent.world`
- **Hosted Zone :** (à récupérer depuis Route 53)
- **Nameservers :** (configurés chez le registrar Namecheap)

### Enregistrements DNS principaux
- **A Record :** Pointant vers CloudFront ou autre
- **CNAME :** (si applicable)
- **NS Records :** Pointant vers les nameservers AWS

### Console Route 53
- **URL Console :** https://console.aws.amazon.com/route53/
- Chercher la Hosted Zone pour `mapevent.world`

---

## 🛠️ LAMBDA LAYERS

### Stripe Layer
- **Nom :** (probablement `mapevent-stripe-layer` ou similaire)
- **Région :** `eu-west-1`
- **Contenu :** Bibliothèque Stripe Python

### Autres Layers
- (À vérifier s'il y en a d'autres)

---

## 📝 FICHIERS DE CONFIGURATION LOCAUX

### Backend
- **Fichier env :** `lambda-package/lambda.env`
- **Script de déploiement :** `lambda-package/deploy_backend.py`
- **Handler principal :** `lambda-package/handler.py`
- **Lambda function entry point :** `lambda-package/lambda_function.py`
- **Backend Flask :** `lambda-package/backend/main.py`

### Frontend
- **Fichier principal :** `public/mapevent.html`
- **Logique JavaScript :** `public/map_logic.js`
- **URL API dans le code :** `https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api`

---

## 🔍 COMMANDES UTILES AWS CLI

### Voir les logs Lambda
```powershell
aws logs tail /aws/lambda/mapevent-backend --follow --region eu-west-1
```

### Mettre à jour les variables d'environnement Lambda
```powershell
aws lambda update-function-configuration `
    --function-name mapevent-backend `
    --environment Variables="{RDS_HOST=...,RDS_PORT=5432,...}" `
    --region eu-west-1
```

### Lister les fonctions Lambda
```powershell
aws lambda list-functions --region eu-west-1 --query "Functions[?contains(FunctionName, 'mapevent')]"
```

### Voir les détails d'une fonction Lambda
```powershell
aws lambda get-function --function-name mapevent-backend --region eu-west-1
```

### Voir les APIs Gateway
```powershell
aws apigateway get-rest-apis --region eu-west-1 --query "items[?contains(name, 'mapevent') || contains(id, 'j33osy4bvj')]"
```

### Voir les ressources d'une API Gateway
```powershell
aws apigateway get-resources --rest-api-id j33osy4bvj --region eu-west-1
```

### Voir les instances RDS
```powershell
aws rds describe-db-instances --region eu-west-1 --query "DBInstances[?contains(DBInstanceIdentifier, 'mapevent')]"
```

### Voir les clusters ElastiCache
```powershell
aws elasticache describe-cache-clusters --region eu-west-1 --query "CacheClusters[?contains(CacheClusterId, 'mapevent')]"
```

### Voir les User Pools Cognito
```powershell
aws cognito-idp list-user-pools --max-results 10 --region eu-west-1
```

---

## 🎯 RÉSUMÉ DES URLS IMPORTANTES

### Production
- **Site web :** https://mapevent.world
- **API Gateway :** https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default
- **API Base :** https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api

### Authentification
- **Cognito Domain :** https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com
- **OAuth Google :** https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/user/oauth/google
- **Complete Profile :** https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/user/oauth/google/complete

### Bases de données
- **RDS PostgreSQL :** `mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com:5432`
- **Redis :** `mapevent-cache-0001-001.mapevent-cache.jqxmjs.euw1.cache.amazonaws.com:6379`

---

## 🔐 CREDENTIALS ET SECRETS

⚠️ **ATTENTION :** Les mots de passe et clés secrètes sont dans `lambda-package/lambda.env`
- Ne jamais commiter ce fichier dans Git
- Utiliser des variables d'environnement ou AWS Secrets Manager en production

### Secrets à récupérer depuis AWS Console
- **Cognito User Pool ID :** Console Cognito → User Pools
- **Cognito App Client ID :** Console Cognito → User Pools → App clients
- **CloudFront Distribution ID :** Console CloudFront
- **Route 53 Hosted Zone ID :** Console Route 53
- **ACM Certificate ARN :** Console ACM

---

## 📚 DOCUMENTATION AWS CONSOLE

### Liens directs (eu-west-1)
- **Lambda :** https://eu-west-1.console.aws.amazon.com/lambda/
- **API Gateway :** https://eu-west-1.console.aws.amazon.com/apigateway/
- **RDS :** https://eu-west-1.console.aws.amazon.com/rds/
- **ElastiCache :** https://eu-west-1.console.aws.amazon.com/elasticache/
- **Cognito :** https://eu-west-1.console.aws.amazon.com/cognito/
- **CloudFront :** https://console.aws.amazon.com/cloudfront/ (global)
- **Route 53 :** https://console.aws.amazon.com/route53/ (global)
- **ACM :** https://eu-west-1.console.aws.amazon.com/acm/ (ou us-east-1 pour CloudFront)
- **CloudWatch Logs :** https://eu-west-1.console.aws.amazon.com/cloudwatch/

---

**Dernière mise à jour :** 31 décembre 2024
**Région principale :** eu-west-1 (Europe - Irlande)

