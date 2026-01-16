# ✅ Résumé de la Configuration S3 pour les Avatars

## 🎯 Ce qui a été fait

### 1. ✅ Bucket S3 créé
- **Nom** : `mapevent-avatars`
- **Région** : `eu-west-1`
- **Statut** : ✅ Créé avec succès

### 2. ✅ CORS configuré
- **Origines autorisées** :
  - `https://mapevent.world`
  - `http://localhost:8000`
  - `http://localhost:3000`
- **Méthodes** : GET, PUT, POST, DELETE, HEAD
- **Statut** : ✅ Configuré avec succès

### 3. ✅ Variables d'environnement Lambda
- **S3_AVATARS_BUCKET** : `mapevent-avatars`
- **AWS_REGION** : `eu-west-1`
- **Statut** : ✅ Ajoutées à la fonction Lambda `mapevent-backend`

### 4. ⚠️ Permissions publiques du bucket

**Problème** : Le Block Public Access empêche de mettre une politique publique directement.

**Solution** : Les avatars seront uploadés avec `ACL='public-read'` dans le code, ce qui devrait fonctionner si le Block Public Access est correctement configuré.

**Action requise** : Vérifier dans la console AWS S3 que le Block Public Access permet les objets publics (pas les politiques de bucket publiques).

## 📋 Checklist Finale

- [x] Bucket S3 créé (`mapevent-avatars`)
- [x] CORS configuré
- [x] Variables d'environnement Lambda configurées
- [ ] **À FAIRE** : Vérifier les permissions IAM Lambda pour S3
- [ ] **À FAIRE** : Déployer le backend avec le nouveau code S3
- [ ] **À FAIRE** : Tester l'upload d'un avatar

## 🔧 Permissions IAM Lambda Requises

La fonction Lambda doit avoir les permissions suivantes dans son rôle IAM :

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
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::mapevent-avatars/*"
    }
  ]
}
```

## 🚀 Prochaines Étapes

1. **Vérifier les permissions IAM** :
   - Aller dans AWS Console > IAM > Rôles
   - Trouver le rôle de la fonction Lambda `mapevent-backend`
   - Ajouter la politique S3 ci-dessus

2. **Déployer le backend** :
   ```powershell
   cd lambda-package
   .\deploy.ps1
   ```

3. **Tester** :
   - Se connecter avec OAuth Google
   - Vérifier qu'un avatar est uploadé vers S3
   - Vérifier que l'URL S3 est stockée dans la base de données

## 📊 Vérification

### Vérifier le bucket S3
```bash
aws s3 ls s3://mapevent-avatars/avatars/
```

### Vérifier les variables Lambda
```bash
aws lambda get-function-configuration --function-name mapevent-backend --region eu-west-1 --query "Environment.Variables" --output json
```

### Vérifier CORS
```bash
aws s3api get-bucket-cors --bucket mapevent-avatars
```






