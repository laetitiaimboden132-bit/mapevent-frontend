# 🚀 Déploiement Manuel - Instructions

Étant donné les problèmes avec le script automatique, voici comment déployer manuellement :

## Option 1 : Déploiement via AWS Console (RECOMMANDÉ)

### 1. Créer le package ZIP

Le code est déjà modifié dans `lambda-package/backend/`. Il suffit de créer un ZIP.

**Via PowerShell** (depuis le dossier `lambda-package`) :
```powershell
cd lambda-package
Compress-Archive -Path backend,services,handler.py -DestinationPath lambda-deploy.zip -Force
```

### 2. Uploader dans Lambda

1. Aller dans **AWS Console > Lambda > `mapevent-backend`**
2. Onglet **"Code"**
3. Cliquer sur **"Upload from"** > **".zip file"**
4. Sélectionner le fichier `lambda-deploy.zip` créé
5. Cliquer sur **"Save"**

### ⚠️ Important

Le package Lambda utilise des **Layers** pour les dépendances (boto3, etc.), donc vous n'avez pas besoin d'inclure toutes les dépendances dans le ZIP. Juste votre code.

## Option 2 : Vérifier que le code est à jour

Le code S3 est déjà dans les fichiers :
- ✅ `lambda-package/backend/services/s3_service.py` (créé)
- ✅ `lambda-package/backend/main.py` (modifié pour utiliser S3)

**Il suffit de créer le ZIP avec le code source uniquement** (sans les dépendances car elles sont dans les Layers).

## 🧪 Test après déploiement

1. Se connecter avec OAuth Google
2. Vérifier les logs CloudWatch pour voir : `✅ Avatar uploadé vers S3`
3. Vérifier dans S3 : `aws s3 ls s3://mapevent-avatars/avatars/`






