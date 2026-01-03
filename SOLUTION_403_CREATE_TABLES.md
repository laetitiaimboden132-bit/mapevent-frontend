# ✅ Solution pour corriger l'erreur 403 sur create-tables

## 🔍 Le problème

L'erreur 403 "Forbidden" vient d'**API Gateway**, pas de Lambda. API Gateway bloque la requête avant qu'elle n'atteigne votre fonction Lambda.

## ✅ Solution en 5 étapes

### Étape 1 : Vérifier que la route existe dans API Gateway

1. Allez dans **API Gateway** (AWS Console)
2. Sélectionnez votre API
3. Cliquez sur **"Ressources"**
4. Vérifiez la structure :
   ```
   /api
     /admin
       /create-tables
         POST
   ```

**Si `/admin` n'existe pas :**
- Cliquez sur `/api`
- Actions > "Créer une ressource"
- Nom : `admin`
- Créez

**Si `/create-tables` n'existe pas :**
- Cliquez sur `/admin`
- Actions > "Créer une ressource"
- Nom : `create-tables`
- Créez

**Si la méthode POST n'existe pas :**
- Cliquez sur `/create-tables`
- Actions > "Créer une méthode"
- Sélectionnez **POST**
- Créez

### Étape 2 : Configurer l'autorisation sur NONE

1. Cliquez sur la méthode **POST** de `/create-tables`
2. Cliquez sur **"Method Request"** (ou "Authorization" selon la version)
3. Dans **"Authorization"**, sélectionnez **"NONE"**
4. Cliquez sur l'icône ✓ pour sauvegarder

### Étape 3 : Configurer l'intégration Lambda

1. Cliquez sur **"Integration Request"**
2. Type d'intégration : **Lambda Function**
3. Lambda Region : votre région (ex: `eu-west-1`)
4. Lambda Function : sélectionnez votre fonction Lambda
5. Cliquez sur **"Save"**
6. Confirmez l'ajout des permissions si demandé

### Étape 4 : Activer CORS (optionnel mais recommandé)

1. Cliquez sur la méthode **POST**
2. Actions > **"Activer CORS"**
3. Configurez :
   - Origines autorisées : `*`
   - Méthodes autorisées : `POST, OPTIONS`
   - Headers autorisés : `Content-Type`
4. Cliquez **"Activer CORS et remplacer les valeurs CORS existantes"**
5. Vérifiez que la méthode **OPTIONS** a été créée automatiquement

### Étape 5 : DÉPLOYER l'API (CRITIQUE !)

1. En haut de l'écran API Gateway
2. Cliquez sur **"Actions"**
3. Sélectionnez **"Déployer l'API"**
4. Stage : **default** (ou votre stage)
5. Description : "Ajout route create-tables"
6. Cliquez **"Déployer"**

### Étape 6 : Attendre et tester

1. Attendez **30 secondes** après le déploiement
2. Testez avec PowerShell :
```powershell
Invoke-WebRequest -Uri "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/api/admin/create-tables" -Method POST -Headers @{"Content-Type"="application/json"} -Body "{}"
```

## 🔍 Si ça ne marche toujours pas

### Vérifier les logs Lambda

1. Allez dans **Lambda** > Votre fonction
2. Onglet **"Monitoring"** > **"View logs in CloudWatch"**
3. Regardez si la requête arrive à Lambda

**Si vous ne voyez AUCUN log :**
- La requête n'atteint pas Lambda
- Problème dans API Gateway (route, autorisation, ou intégration)

**Si vous voyez des logs :**
- La requête arrive à Lambda
- Le problème est dans le code Lambda ou la base de données

### Vérifier les permissions Lambda

1. Lambda > Votre fonction
2. Onglet **"Configuration"** > **"Permissions"**
3. Vérifiez le rôle IAM
4. Vérifiez que API Gateway peut invoquer la fonction

## ✅ Checklist finale

- [ ] Route `/api/admin/create-tables` existe
- [ ] Méthode POST existe
- [ ] Autorisation = NONE
- [ ] Intégration Lambda configurée
- [ ] CORS activé (optionnel)
- [ ] API déployée sur stage default
- [ ] Attendu 30 secondes
- [ ] Retesté

## 🚨 Solution rapide si vous êtes pressé

Si vous voulez juste créer les tables rapidement, vous pouvez :

1. **Utiliser AWS Lambda directement** :
   - Lambda > Votre fonction
   - Onglet "Test"
   - Créez un événement de test avec :
   ```json
   {
     "path": "/api/admin/create-tables",
     "httpMethod": "POST",
     "body": "{}"
   }
   ```
   - Exécutez le test

2. **Ou utiliser AWS CLI** :
```bash
aws lambda invoke --function-name VOTRE_FONCTION --payload '{"path":"/api/admin/create-tables","httpMethod":"POST","body":"{}"}' response.json
```

Ces méthodes contournent API Gateway et appellent Lambda directement.

