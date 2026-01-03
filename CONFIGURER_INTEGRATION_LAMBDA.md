# 🔧 Configurer l'intégration Lambda dans API Gateway

## 📋 Étapes détaillées

### Étape 1 : Sélectionner la méthode

1. Allez dans **API Gateway** (AWS Console)
2. Sélectionnez votre API
3. **Ressources** > `/api` > `/admin` > `/create-tables`
4. Cliquez sur la méthode **POST**

### Étape 2 : Configurer l'intégration

1. Cliquez sur **"Integration Request"** (ou "Intégration" selon la version)
2. Vous verrez plusieurs options :

#### Type d'intégration
- Sélectionnez : **Lambda Function**

#### Lambda Function
- **Lambda Region** : Sélectionnez votre région (ex: `eu-west-1`)
- **Lambda Function** : 
  - Cliquez sur le champ
  - Tapez le nom de votre fonction Lambda (ex: `mapevent-lambda` ou le nom que vous avez donné)
  - Ou sélectionnez-la dans la liste déroulante

#### Use Lambda Proxy integration
- ✅ **Cochez cette case** (important !)
- Cela permet à Lambda de recevoir les headers et le body complets

### Étape 3 : Sauvegarder

1. Cliquez sur **"Save"** (ou "Sauvegarder")
2. Une popup apparaîtra : **"Add Permission to Lambda Function"**
3. Cliquez sur **"OK"** pour autoriser API Gateway à invoquer votre fonction Lambda
4. AWS créera automatiquement les permissions nécessaires

### Étape 4 : Vérifier

1. Après sauvegarde, vous devriez voir :
   - **Integration type** : Lambda Function
   - **Lambda Function** : le nom de votre fonction
   - **Use Proxy Integration** : ✓ (coché)

### Étape 5 : Tester (optionnel)

1. Cliquez sur **"TEST"** (en haut à droite)
2. Méthode : **POST**
3. Body : `{}`
4. Cliquez sur **"Test"**
5. Vous devriez voir la réponse de Lambda

## ⚠️ Points importants

### ✅ Use Lambda Proxy Integration

**Cochez cette case !** Sinon :
- Lambda ne recevra pas les headers correctement
- Le body ne sera pas formaté correctement
- Les réponses ne seront pas correctement renvoyées

### ✅ Permissions Lambda

Quand vous sauvegardez, AWS demande d'ajouter des permissions. **Acceptez !**

Cela ajoute une permission dans le rôle IAM de Lambda pour permettre à API Gateway d'invoquer la fonction.

### ✅ Nom de la fonction Lambda

Le nom doit être **exactement** le même que celui dans Lambda :
- Allez dans **Lambda** > Votre fonction
- Regardez le nom en haut
- Utilisez ce nom exact dans API Gateway

## 🔍 Si vous ne trouvez pas votre fonction Lambda

1. Vérifiez la région :
   - API Gateway et Lambda doivent être dans la **même région**
   - Ex: `eu-west-1` pour les deux

2. Vérifiez les permissions :
   - Votre compte AWS doit avoir les droits pour voir les fonctions Lambda

3. Tapez le nom complet :
   - Parfois la liste ne charge pas
   - Tapez le nom exact de votre fonction

## 📝 Exemple de configuration

```
Integration type: Lambda Function
Lambda Region: eu-west-1
Lambda Function: mapevent-backend-lambda
Use Lambda Proxy integration: ✓ (coché)
```

## ✅ Après configuration

1. **Déployez l'API** :
   - Actions > Déployer l'API
   - Stage: default
   - Déployer

2. **Testez** :
   ```powershell
   Invoke-WebRequest -Uri "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/api/admin/create-tables" -Method POST -Headers @{"Content-Type"="application/json"} -Body "{}"
   ```

## 🚨 Erreurs courantes

### "Lambda function cannot be found"
- Vérifiez le nom de la fonction
- Vérifiez la région
- Vérifiez que la fonction existe dans Lambda

### "Execution failed due to configuration error"
- Vérifiez que "Use Lambda Proxy integration" est coché
- Vérifiez que les permissions ont été ajoutées

### "Internal server error"
- Vérifiez les logs Lambda dans CloudWatch
- Le problème est probablement dans le code Lambda, pas dans l'intégration

