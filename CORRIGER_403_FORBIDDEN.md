# 🔧 Corriger l'erreur 403 Forbidden

## ❌ Erreur actuelle
```
{"message":"Forbidden"}
Code: 403
```

Cela signifie que la route existe mais qu'API Gateway bloque l'accès.

## 🔍 Vérifications à faire MAINTENANT

### 1. La route existe-t-elle ?

**API Gateway** > Votre API > **Ressources**

Vérifiez la structure :
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

### 2. L'autorisation est-elle sur NONE ?

1. Cliquez sur la méthode **POST** de `/create-tables`
2. Cliquez sur **"Method Request"** (ou "Authorization")
3. Regardez **"Authorization"** :
   - Doit être : **NONE**
   - Si c'est **AWS_IAM** ou **API_KEY** → Changez en **NONE**
4. Cliquez sur l'icône ✓ pour sauvegarder

### 3. L'intégration Lambda est-elle configurée ?

1. Cliquez sur **"Integration Request"**
2. Vérifiez :
   - **Integration type** : `Lambda Function`
   - **Lambda Function** : le nom de votre fonction
   - **Use Lambda Proxy integration** : ✓ (coché)
3. Si ce n'est pas configuré :
   - Configurez l'intégration Lambda
   - Sauvegardez
   - Acceptez les permissions

### 4. L'API est-elle déployée ?

1. En haut de l'écran API Gateway
2. Regardez la date du dernier déploiement
3. Si ancien ou pas déployé :
   - Actions > "Déployer l'API"
   - Stage : `default`
   - Déployer

## ✅ Solution étape par étape

### Étape 1 : Créer la route si elle n'existe pas

1. API Gateway > Votre API
2. Ressources > `/api`
3. Actions > "Créer une ressource"
4. Nom : `admin` > Créer
5. Cliquez sur `/admin`
6. Actions > "Créer une ressource"
7. Nom : `create-tables` > Créer
8. Cliquez sur `/create-tables`
9. Actions > "Créer une méthode"
10. Sélectionnez **POST** > Créer

### Étape 2 : Configurer l'autorisation

1. Cliquez sur la méthode **POST**
2. **Method Request** > **Authorization** : **NONE**
3. Sauvegardez

### Étape 3 : Configurer l'intégration Lambda

1. **Integration Request**
2. **Integration type** : `Lambda Function`
3. **Lambda Region** : `eu-west-1`
4. **Lambda Function** : tapez le nom de votre fonction Lambda
5. ✅ **Cochez "Use Lambda Proxy integration"**
6. **Save** > Acceptez les permissions

### Étape 4 : Déployer

1. Actions > "Déployer l'API"
2. Stage : `default`
3. Déployer

### Étape 5 : Retester

```powershell
Invoke-WebRequest -Uri "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/api/admin/create-tables" -Method POST -Headers @{"Content-Type"="application/json"} -Body "{}"
```

## 🔍 Diagnostic

### Si vous obtenez toujours 403

1. **Vérifiez les logs Lambda** :
   - Lambda > Votre fonction > Monitoring > View logs
   - Si vous ne voyez AUCUN log → La requête n'atteint pas Lambda
   - Problème dans API Gateway (route, autorisation, ou intégration)

2. **Vérifiez le nom de la fonction Lambda** :
   - Lambda > Votre fonction
   - Regardez le nom exact
   - Utilisez ce nom exact dans API Gateway

3. **Vérifiez les permissions Lambda** :
   - Lambda > Configuration > Permissions
   - Vérifiez que API Gateway peut invoquer la fonction

## 🚨 Solution alternative : Appeler Lambda directement

Si API Gateway pose problème, appelez Lambda directement :

1. **Lambda** > Votre fonction
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

Cela contourne API Gateway et appelle Lambda directement.

