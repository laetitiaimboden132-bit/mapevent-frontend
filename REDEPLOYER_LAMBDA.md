# 🔄 Redéployer Lambda avec les nouveaux logs

## 📋 Étapes pour redéployer Lambda

### 1. Créer le package Lambda

Si vous utilisez un script de déploiement, exécutez-le. Sinon :

```bash
cd lambda-package
zip -r ../lambda-deployment.zip . -x "*.pyc" -x "__pycache__/*" -x "*.git/*"
```

### 2. Uploader dans Lambda

1. **Lambda** > Fonction `mapevent-backend`
2. Onglet **"Code"**
3. Cliquez sur **"Upload from"** > **".zip file"**
4. Sélectionnez le fichier `lambda-deployment.zip`
5. Cliquez sur **"Save"**

### 3. Tester

1. Retestez avec PowerShell :
```powershell
Invoke-WebRequest -Uri "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/api/admin/create-tables" -Method POST -Headers @{"Content-Type"="application/json"} -Body "{}"
```

2. Regardez les logs CloudWatch
3. Vous devriez maintenant voir les logs de diagnostic :
   - `🔍 Path reçu: ...`
   - `🔍 Path traité: ...`
   - `🔍 Méthode: ...`
   - `🔍 Appel Flask: ...`
   - `🔍 Réponse Flask: ...`

Ces logs vous diront exactement ce qui se passe !

## 🔍 Ce qu'il faut chercher dans les logs

### Si vous voyez :
```
🔍 Path reçu: /api/admin/create-tables
🔍 Path traité: /api/admin/create-tables
🔍 Méthode: POST
🔍 Appel Flask: POST /api/admin/create-tables
🔍 Réponse Flask: 200
```

→ Tout fonctionne, le problème est ailleurs (peut-être dans API Gateway)

### Si vous voyez :
```
🔍 Path reçu: /default/api/admin/create-tables
🔍 Path traité: /api/admin/create-tables
```

→ Le path est correctement traité

### Si vous voyez une erreur :
```
Error: ...
```

→ Le problème est dans le code, regardez l'erreur

## ✅ Après avoir vu les logs

Envoyez-moi ce que vous voyez dans les logs CloudWatch après le redéploiement, et je pourrai vous dire exactement où est le problème !

