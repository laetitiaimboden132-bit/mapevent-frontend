# 🚀 Déploiement Complet S3 pour Avatars

## 📋 Étapes de Déploiement

### Étape 1 : Configuration S3 (Automatique)

Exécutez le script PowerShell :

```powershell
.\setup-s3-avatars.ps1
```

Ce script va :
- ✅ Créer le bucket S3 `mapevent-avatars`
- ✅ Configurer les permissions (lecture publique)
- ✅ Configurer CORS
- ✅ Désactiver le blocage d'accès public

### Étape 2 : Configuration Variables d'Environnement Lambda

**Option A - Automatique :**

Modifiez `setup-lambda-env-vars.ps1` avec le nom de votre fonction Lambda, puis :

```powershell
.\setup-lambda-env-vars.ps1
```

**Option B - Manuelle (AWS Console) :**

1. Allez dans **AWS Console > Lambda > Fonctions > [Votre fonction Lambda]**
2. **Configuration > Variables d'environnement**
3. Ajoutez :
   - `S3_AVATARS_BUCKET` = `mapevent-avatars`
   - `AWS_REGION` = `eu-west-1`

### Étape 3 : Configuration Permissions IAM Lambda

**Option A - Automatique :**

Modifiez `setup-lambda-iam.ps1` avec le nom de votre fonction Lambda, puis :

```powershell
.\setup-lambda-iam.ps1
```

**Option B - Manuelle (AWS Console) :**

1. Allez dans **AWS Console > Lambda > Fonctions > [Votre fonction Lambda]**
2. **Configuration > Permissions**
3. Cliquez sur le **Rôle IAM**
4. **Ajouter des permissions > Attacher des politiques**
5. Créez une politique personnalisée avec ce JSON :

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::mapevent-avatars",
        "arn:aws:s3:::mapevent-avatars/*"
      ]
    }
  ]
}
```

### Étape 4 : Déployer le Backend

Déployez le backend avec le nouveau code qui inclut le service S3.

### Étape 5 : Test

1. **Test de connexion OAuth Google** : Connectez-vous et vérifiez que l'avatar est uploadé vers S3
2. **Test de mise à jour de profil** : Modifiez votre photo de profil et vérifiez l'upload S3
3. **Vérifier dans S3** :

```powershell
aws s3 ls s3://mapevent-avatars/avatars/
```

## ✅ Checklist

- [ ] Bucket S3 créé (`mapevent-avatars`)
- [ ] Permissions bucket configurées (lecture publique)
- [ ] CORS configuré
- [ ] Variables d'environnement Lambda configurées
- [ ] Permissions IAM Lambda configurées
- [ ] Backend déployé avec le nouveau code
- [ ] Test de connexion OAuth Google réussi
- [ ] Test de mise à jour de profil réussi
- [ ] Vérification des URLs S3 dans la base de données

## 🔍 Vérification

### Vérifier le bucket S3

```powershell
aws s3 ls s3://mapevent-avatars/avatars/
```

### Vérifier les permissions

```powershell
aws s3api get-bucket-policy --bucket mapevent-avatars
aws s3api get-bucket-cors --bucket mapevent-avatars
```

### Vérifier les variables d'environnement Lambda

```powershell
aws lambda get-function-configuration --function-name [VOTRE_FONCTION] --query 'Environment.Variables'
```

## 🐛 Dépannage

### Erreur : "Access Denied" lors de l'upload

- Vérifiez les permissions IAM de la fonction Lambda
- Vérifiez que la politique IAM est bien attachée au rôle

### Erreur : "Bucket does not exist"

- Vérifiez que le bucket a été créé : `aws s3 ls`
- Vérifiez le nom du bucket dans les variables d'environnement

### Erreur : "CORS policy"

- Vérifiez la configuration CORS du bucket
- Vérifiez que votre domaine est dans la liste `AllowedOrigins`

### Les avatars ne s'affichent pas

- Vérifiez que les permissions du bucket permettent la lecture publique
- Vérifiez que le blocage d'accès public est désactivé
- Vérifiez l'URL S3 dans la base de données

## 📞 Support

Si vous rencontrez des problèmes, vérifiez :
1. Les logs CloudWatch de la fonction Lambda
2. Les logs S3 (si activés)
3. Les erreurs dans la console du navigateur

