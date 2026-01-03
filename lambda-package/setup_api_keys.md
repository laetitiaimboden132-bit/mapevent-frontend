# 🔑 Configuration des Clés API pour la Modération d'Images

## Option 1: Google Cloud Vision API (Recommandé)

### Étape 1: Créer un projet Google Cloud

1. Allez sur https://console.cloud.google.com/
2. Cliquez sur "Sélectionner un projet" > "Nouveau projet"
3. Nommez-le "MapEventAI" (ou autre)
4. Notez le **Project ID**

### Étape 2: Activer l'API Vision

1. Dans le menu, allez dans **APIs & Services** > **Library**
2. Recherchez "Cloud Vision API"
3. Cliquez sur **Enable**

### Étape 3: Créer une clé API

1. Allez dans **APIs & Services** > **Credentials**
2. Cliquez sur **Create Credentials** > **API Key**
3. Copiez la clé API générée
4. **IMPORTANT**: Cliquez sur la clé créée pour la restreindre:
   - Dans "API restrictions", sélectionnez "Restrict key"
   - Choisissez "Cloud Vision API"
   - Sauvegardez

### Étape 4: Ajouter à Lambda

Ajoutez la clé dans votre fichier `lambda.env`:

```
GOOGLE_CLOUD_VISION_API_KEY=votre_cle_api_ici
```

Puis exécutez:

```powershell
.\configure_lambda_env.ps1
```

## Option 2: AWS Rekognition (Alternative)

AWS Rekognition est déjà disponible si vous avez un compte AWS.

### Étape 1: Vérifier les permissions IAM

Votre rôle Lambda doit avoir cette politique:

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

### Étape 2: Configurer la région

Dans `lambda.env`:

```
AWS_REGION=eu-west-1
```

## Option 3: Les deux (Recommandé pour production)

Configurez les deux pour avoir un fallback automatique:

```
GOOGLE_CLOUD_VISION_API_KEY=votre_cle_google
AWS_REGION=eu-west-1
```

Le système utilisera Google Cloud Vision en priorité, et AWS Rekognition en cas d'échec.

## 💰 Coûts

### Google Cloud Vision
- **Gratuit**: 1000 requêtes/mois
- **Payant**: $1.50 par 1000 requêtes supplémentaires

### AWS Rekognition
- **Gratuit**: 5000 images/mois (12 premiers mois)
- **Payant**: $1.00 par 1000 images supplémentaires

## 🧪 Tester la configuration

Une fois configuré, testez avec:

```powershell
python test_moderation.py
```

Ou via l'API:

```powershell
$body = @{
    imageUrl = "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7"
    userId = "test_user"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/social/moderation/image" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

## 🔒 Sécurité

⚠️ **IMPORTANT**: 
- Ne commitez JAMAIS les clés API dans Git
- Utilisez AWS Secrets Manager en production
- Restreignez les clés API aux IPs/domaines autorisés
- Activez la rotation des clés régulièrement





