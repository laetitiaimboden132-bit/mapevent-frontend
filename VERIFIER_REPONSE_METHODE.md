# ✅ Vérifier la réponse de méthode

## Configuration actuelle (correcte)
- ✅ Autorisation : NONE
- ✅ Intégration Lambda : configurée
- ✅ Fonction Lambda : mapevent-backend
- ✅ Use Lambda Proxy integration : Vrai

## 🔍 Vérifications supplémentaires

### 1. Vérifier la réponse de méthode

1. Cliquez sur **"Réponse de méthode"** (Method Response)
2. Vérifiez les codes de statut HTTP :
   - **200** doit être présent
   - Si pas présent, ajoutez-le :
     - Cliquez sur **"Ajouter une réponse de modèle"**
     - Code de statut HTTP : **200**
     - Ajoutez

### 2. Vérifier la réponse d'intégration

1. Cliquez sur **"Réponse d'intégration"** (Integration Response)
2. Avec Lambda Proxy, cela devrait être automatique
3. Vérifiez qu'il n'y a pas d'erreur de mapping

### 3. DÉPLOYER l'API (CRITIQUE !)

1. En haut de l'écran API Gateway
2. **Actions** > **"Déployer l'API"**
3. **Stage** : `default`
4. **Description** : "Configuration create-tables"
5. Cliquez **"Déployer"**

### 4. Attendre et retester

1. Attendez **30 secondes** après le déploiement
2. Retestez avec PowerShell :
```powershell
Invoke-WebRequest -Uri "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/api/admin/create-tables" -Method POST -Headers @{"Content-Type"="application/json"} -Body "{}"
```

## 🔍 Si ça ne marche toujours pas

### Vérifier les permissions Lambda

1. **Lambda** > Fonction `mapevent-backend`
2. Onglet **"Configuration"** > **"Permissions"**
3. Vérifiez le rôle IAM
4. Vérifiez que API Gateway peut invoquer la fonction

### Vérifier les logs Lambda

1. **Lambda** > Fonction `mapevent-backend`
2. Onglet **"Monitoring"** > **"View logs in CloudWatch"**
3. Regardez si la requête arrive à Lambda quand vous testez via API Gateway

**Si vous ne voyez AUCUN log :**
- La requête n'atteint pas Lambda
- Problème dans API Gateway (déploiement ou configuration)

**Si vous voyez des logs :**
- La requête arrive à Lambda
- Le problème est peut-être dans la réponse

## ✅ Checklist finale

- [ ] Réponse de méthode : Code 200 présent
- [ ] Réponse d'intégration : Configurée (automatique avec Proxy)
- [ ] API **DÉPLOYÉE** sur stage `default`
- [ ] Attendu 30 secondes
- [ ] Retesté avec PowerShell

