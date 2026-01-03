# ✅ SOLUTION DIRECTE CORS - 3 ÉTAPES

## 🎯 Le problème
API Gateway bloque les requêtes OPTIONS avant qu'elles n'atteignent Lambda.

## ✅ SOLUTION EN 3 ÉTAPES

### ÉTAPE 1 : Déployer le nouveau handler Lambda

**Option A : Via l'interface AWS (RECOMMANDÉ)**

1. Ouvrez **AWS Lambda Console** (console.aws.amazon.com > Lambda)
2. Trouvez votre fonction Lambda (celle liée à API Gateway)
3. Cliquez dessus
4. Dans l'onglet **"Code"**, ouvrez le fichier `handler.py`
5. **Remplacez TOUT le contenu** par le contenu de `lambda-package/handler.py` (dans votre projet)
6. Cliquez **"Deploy"** (en haut à droite)

**Option B : Via AWS CLI (si vous avez AWS CLI installé)**

```powershell
cd lambda-package
Compress-Archive -Path * -DestinationPath ../lambda-deploy.zip -Force
aws lambda update-function-code --function-name VOTRE_FONCTION_LAMBDA --zip-file fileb://../lambda-deploy.zip
```

### ÉTAPE 2 : Créer la méthode OPTIONS dans API Gateway

1. **API Gateway** > Votre API > **Ressources**
2. `/api/payments/create-checkout-session`
3. **Actions** > **"Créer une méthode"**
4. Sélectionnez **OPTIONS**
5. **Type d'intégration** : **Lambda Function**
6. **Lambda Function** : Sélectionnez votre fonction Lambda
7. **Use Lambda Proxy integration** : ✅ **COCHEZ**
8. **Save** > **OK** (autoriser l'accès)

### ÉTAPE 3 : DÉPLOYER L'API

1. **Actions** (en haut) > **"Déployer l'API"**
2. **Stage** : `default`
3. **Description** : "Ajout OPTIONS pour CORS"
4. **Déployer**
5. **Attendez 30 secondes**

## ✅ TESTER

Ouvrez `test-routes.html` et testez. Ça devrait fonctionner !

## 🔍 Si ça ne marche toujours pas

Vérifiez dans API Gateway :
1. `/api/payments/create-checkout-session` > **OPTIONS** existe ?
2. OPTIONS a **Lambda Proxy integration** activé ?
3. L'API a été **déployée** récemment ?

## 📝 Note importante

Le handler Lambda gère maintenant OPTIONS directement et retourne les headers CORS. Même si API Gateway ne passe pas OPTIONS à Lambda, les autres méthodes (POST) retourneront les bons headers CORS.

