# 🔍 Vérifier l'autorisation dans API Gateway

## 📋 Étapes

### 1. Aller dans API Gateway

1. **API Gateway** (dans AWS Console)
2. Sélectionnez votre API
3. **Ressources** (dans le menu de gauche)

### 2. Trouver la route

1. Cliquez sur `/api`
2. Cliquez sur `/admin`
3. Cliquez sur `/create-tables`
4. Cliquez sur la méthode **POST**

### 3. Vérifier l'autorisation

1. Dans le panneau de droite, cherchez **"Method Request"** (ou "Requête de méthode")
2. Cliquez dessus
3. Regardez **"Authorization"** (Autorisation)
4. **Doit être : NONE**

### 4. Si ce n'est pas NONE

1. Cliquez sur le champ "Authorization"
2. Sélectionnez **"NONE"** dans le menu déroulant
3. Cliquez sur l'icône **✓** (checkmark) pour sauvegarder

### 5. Déployer l'API

1. En haut de l'écran API Gateway
2. Cliquez sur **"Actions"** (bouton)
3. Sélectionnez **"Déployer l'API"**
4. **Stage** : `default`
5. **Description** : "Correction autorisation create-tables"
6. Cliquez **"Déployer"**

### 6. Attendre et retester

1. Attendez **30 secondes**
2. Faites un nouveau test :
```powershell
Invoke-WebRequest -Uri "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/api/admin/create-tables" -Method POST -Headers @{"Content-Type"="application/json"} -Body "{}"
```

3. Regardez les logs CloudWatch
4. Vous devriez voir un **nouveau RequestId** et les logs 🔍

## 🔍 Si l'autorisation est déjà sur NONE

Alors le problème est ailleurs. Vérifiez :

1. **L'intégration Lambda** est-elle bien configurée ?
2. **L'API est-elle déployée** sur le stage default ?
3. **Le nom de la fonction Lambda** est-il correct dans l'intégration ?

## ✅ Action immédiate

1. **Vérifiez l'autorisation** dans API Gateway (doit être NONE)
2. **Si ce n'est pas NONE**, changez en NONE
3. **Déployez l'API**
4. **Attendez 30 secondes**
5. **Retestez**
6. **Regardez les logs CloudWatch** pour voir un nouveau RequestId

Dites-moi ce que vous voyez pour l'autorisation dans API Gateway !

