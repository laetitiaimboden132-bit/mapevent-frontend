# 🔑 Configuration des Clés API pour la Modération d'Images

## Vue d'ensemble

Le système de modération d'images supporte deux providers:
1. **Google Cloud Vision API** (recommandé)
2. **AWS Rekognition** (fallback)

## 🎯 Option 1: Google Cloud Vision API (Recommandé)

### Étape 1: Créer un projet Google Cloud

1. Allez sur https://console.cloud.google.com/
2. Créez un nouveau projet ou sélectionnez un projet existant
3. Notez le **Project ID**

### Étape 2: Activer l'API Vision

1. Allez dans **APIs & Services** > **Library**
2. Recherchez "Cloud Vision API"
3. Cliquez sur **Enable**

### Étape 3: Créer une clé API

1. Allez dans **APIs & Services** > **Credentials**
2. Cliquez sur **Create Credentials** > **API Key**
3. Copiez la clé API générée
4. (Recommandé) Restreignez la clé API:
   - Cliquez sur la clé créée
   - Dans "API restrictions", sélectionnez "Restrict key"
   - Choisissez "Cloud Vision API"
   - Sauvegardez

### Étape 4: Configurer dans AWS Lambda

```bash
# Ajouter la clé API comme variable d'environnement Lambda
aws lambda update-function-configuration \
    --function-name mapevent-backend \
    --environment Variables="{GOOGLE_CLOUD_VISION_API_KEY=votre_cle_api_ici}" \
    --region eu-west-1
```

Ou via la console AWS:
1. Allez dans Lambda > mapevent-backend > Configuration > Environment variables
2. Ajoutez: `GOOGLE_CLOUD_VISION_API_KEY` = `votre_cle_api`

### 💰 Coûts Google Cloud Vision

- **Gratuit**: 1000 requêtes/mois
- **Payant**: $1.50 par 1000 requêtes supplémentaires
- **Limite**: 1800 requêtes/minute

## 🎯 Option 2: AWS Rekognition (Alternative)

### Étape 1: Activer Rekognition

AWS Rekognition est déjà disponible si vous avez un compte AWS.

### Étape 2: Configurer les permissions IAM

Ajoutez cette politique à votre rôle Lambda:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "rekognition:DetectModerationLabels"
      ],
      "Resource": "*"
    }
  ]
}
```

### Étape 3: Configurer la région

```bash
# Définir la région AWS
aws lambda update-function-configuration \
    --function-name mapevent-backend \
    --environment Variables="{AWS_REGION=eu-west-1}" \
    --region eu-west-1
```

### 💰 Coûts AWS Rekognition

- **Gratuit**: 5000 images/mois (pendant 12 mois)
- **Payant**: $1.00 par 1000 images supplémentaires
- **Limite**: 50 TPS (transactions par seconde)

## 🔄 Configuration des deux providers (Recommandé)

Pour une meilleure disponibilité, configurez les deux providers. Le système utilisera Google Cloud Vision en priorité, et AWS Rekognition en fallback.

```bash
aws lambda update-function-configuration \
    --function-name mapevent-backend \
    --environment Variables="{GOOGLE_CLOUD_VISION_API_KEY=votre_cle_google,AWS_REGION=eu-west-1}" \
    --region eu-west-1
```

## 🧪 Tester la configuration

Utilisez le script de test:

```bash
cd lambda-package
python test_moderation.py
```

Ou testez via l'API:

```bash
curl -X POST https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/social/moderation/image \
  -H "Content-Type: application/json" \
  -d '{
    "imageUrl": "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7",
    "userId": "test_user"
  }'
```

## 🔒 Sécurité

⚠️ **IMPORTANT**: 
- Ne commitez JAMAIS les clés API dans Git
- Utilisez AWS Secrets Manager pour les clés sensibles en production
- Restreignez les clés API aux IPs/domaines autorisés
- Activez la rotation des clés régulièrement

### Utiliser AWS Secrets Manager (Production)

```python
import boto3
import json

def get_api_key_from_secrets():
    secrets_client = boto3.client('secretsmanager', region_name='eu-west-1')
    secret = secrets_client.get_secret_value(SecretId='mapevent/google-vision-api-key')
    return json.loads(secret['SecretString'])['api_key']
```

## 📊 Monitoring

Surveillez l'utilisation via:
- **Google Cloud**: Cloud Console > APIs & Services > Dashboard
- **AWS**: CloudWatch > Metrics > Rekognition

## ✅ Checklist

- [ ] Projet Google Cloud créé (si option 1)
- [ ] API Vision activée (si option 1)
- [ ] Clé API créée et restreinte (si option 1)
- [ ] Permissions IAM configurées (si option 2)
- [ ] Variables d'environnement Lambda configurées
- [ ] Tests de modération réussis
- [ ] Monitoring configuré





