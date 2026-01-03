# 🔧 Corriger l'erreur 403 Forbidden sur create-tables

## ❌ Erreur actuelle
```
{"message":"Forbidden"}
Code: 403
```

## 🔍 Causes possibles

### 1. Route n'existe pas dans API Gateway
La route `/api/admin/create-tables` n'est peut-être pas créée dans API Gateway.

**Vérification :**
- API Gateway > Votre API
- Ressources > `/api` > `/admin` > `/create-tables`
- Vérifiez que la méthode **POST** existe

**Si elle n'existe pas :**
1. Créez la ressource `/admin` sous `/api`
2. Créez la ressource `/create-tables` sous `/admin`
3. Créez la méthode **POST**
4. Liez-la à votre fonction Lambda
5. Déployez l'API

### 2. Autorisation requise dans API Gateway
La route peut avoir une autorisation configurée (clé API, IAM, etc.).

**Vérification :**
- Sélectionnez la méthode POST de `/create-tables`
- Onglet **"Méthode Request"** ou **"Authorization"**
- Vérifiez le type d'autorisation :
  - **NONE** = Pas d'autorisation (recommandé pour route admin temporaire)
  - **AWS_IAM** = Nécessite des credentials AWS
  - **API_KEY** = Nécessite une clé API

**Solution :**
- Changez l'autorisation en **NONE**
- Déployez l'API

### 3. Intégration Lambda incorrecte
La méthode n'est peut-être pas liée à Lambda.

**Vérification :**
- Sélectionnez la méthode POST
- Onglet **"Intégration Request"**
- Type d'intégration doit être : **Lambda Function**
- Nom de la fonction : votre fonction Lambda

**Solution :**
- Configurez l'intégration Lambda
- Déployez l'API

### 4. Permissions Lambda
La fonction Lambda n'a peut-être pas les permissions pour être invoquée par API Gateway.

**Vérification :**
- Lambda > Votre fonction
- Onglet **"Configuration"** > **"Permissions"**
- Vérifiez le rôle IAM
- Vérifiez que API Gateway peut invoquer la fonction

## ✅ Solution étape par étape

### Étape 1 : Vérifier que la route existe
1. API Gateway > Votre API
2. Ressources > Vérifiez la structure :
   ```
   /api
     /admin
       /create-tables
         POST
   ```

### Étape 2 : Vérifier l'autorisation
1. Sélectionnez la méthode **POST** de `/create-tables`
2. Onglet **"Method Request"** ou **"Authorization"**
3. **Authorization** : **NONE**
4. Sauvegardez

### Étape 3 : Vérifier l'intégration
1. Onglet **"Integration Request"**
2. Type : **Lambda Function**
3. Lambda Function : votre fonction Lambda
4. Sauvegardez

### Étape 4 : Déployer
1. Actions > **"Déployer l'API"**
2. Stage : **default**
3. Déployer

### Étape 5 : Retester
```powershell
Invoke-WebRequest -Uri "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/api/admin/create-tables" -Method POST -Headers @{"Content-Type"="application/json"} -Body "{}"
```

## 🔍 Diagnostic

Si ça ne marche toujours pas, vérifiez dans CloudWatch :
- Lambda > Votre fonction > Onglet **"Monitoring"** > **"View logs in CloudWatch"**
- Regardez les logs pour voir si la requête arrive à Lambda

