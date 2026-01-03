# 🔍 Diagnostic 403 Persistant

## ❌ Problème
L'API est déployée mais retourne toujours 403 Forbidden.

## 🔍 Vérifications à faire

### 1. Vérifier les permissions Lambda

1. **Lambda** > Fonction `mapevent-backend`
2. Onglet **"Configuration"** > **"Permissions"**
3. Cliquez sur le **rôle IAM**
4. Vérifiez les politiques attachées :
   - Doit avoir une politique qui permet à API Gateway d'invoquer Lambda
   - Ou une politique avec `lambda:InvokeFunction`

**Si les permissions manquent :**
- Dans API Gateway, quand vous avez configuré l'intégration Lambda
- AWS devrait avoir demandé d'ajouter les permissions
- Si vous avez refusé, il faut les ajouter manuellement

**Solution :**
1. Lambda > Fonction `mapevent-backend` > Configuration > Permissions
2. Cliquez sur le rôle IAM
3. Ajoutez une politique inline :
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "apigateway.amazonaws.com"
      },
      "Action": "lambda:InvokeFunction",
      "Resource": "arn:aws:lambda:eu-west-1:818127249940:function:mapevent-backend"
    }
  ]
}
```

### 2. Vérifier les logs Lambda

1. **Lambda** > Fonction `mapevent-backend`
2. Onglet **"Monitoring"** > **"View logs in CloudWatch"**
3. Regardez les logs récents

**Si vous ne voyez AUCUN log quand vous testez via API Gateway :**
- La requête n'atteint pas Lambda
- Problème de permissions ou de configuration API Gateway

**Si vous voyez des logs :**
- La requête arrive à Lambda
- Le problème est peut-être dans la réponse

### 3. Vérifier la réponse de méthode

1. API Gateway > Votre API
2. Ressources > `/api/admin/create-tables` > Méthode POST
3. Cliquez sur **"Réponse de méthode"** (Method Response)
4. Vérifiez que le code **200** est présent
5. Si absent, ajoutez-le :
   - Cliquez sur **"Ajouter une réponse de modèle"**
   - Code de statut HTTP : **200**
   - Ajoutez

### 4. Vérifier la réponse d'intégration

1. Cliquez sur **"Réponse d'intégration"** (Integration Response)
2. Avec Lambda Proxy, cela devrait être automatique
3. Vérifiez qu'il n'y a pas d'erreur

### 5. Tester directement depuis API Gateway

1. API Gateway > Votre API
2. Ressources > `/api/admin/create-tables` > Méthode POST
3. Cliquez sur **"TEST"** (en haut à droite)
4. Méthode : **POST**
5. Body : `{}`
6. Cliquez sur **"Test"**

**Si ça fonctionne dans le test API Gateway :**
- La configuration est correcte
- Le problème est peut-être dans l'URL ou le déploiement

**Si ça ne fonctionne pas :**
- Problème dans la configuration
- Vérifiez les logs d'erreur dans le test

## ✅ Solution alternative : Réconfigurer l'intégration

Parfois, il faut recréer l'intégration :

1. API Gateway > `/api/admin/create-tables` > POST
2. **Integration Request**
3. Cliquez sur **"Modifier"**
4. Vérifiez :
   - Integration type : `Lambda Function`
   - Lambda Function : `mapevent-backend`
   - Use Lambda Proxy integration : ✓
5. **Save**
6. **Acceptez** l'ajout des permissions si demandé
7. **Déployez** l'API à nouveau

## 🚨 Solution de contournement

Si rien ne fonctionne, utilisez Lambda directement :

1. **Lambda** > Fonction `mapevent-backend`
2. Onglet **"Test"**
3. Créez un événement de test :
```json
{
  "path": "/api/admin/create-tables",
  "httpMethod": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{}"
}
```
4. Cliquez **"Test"**

Cela fonctionne déjà (vous l'avez testé), donc vous pouvez créer les tables ainsi.

