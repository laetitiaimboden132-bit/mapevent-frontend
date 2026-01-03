# 🔍 Vérifier les logs Lambda pour diagnostiquer le 403

## 📋 Étapes pour vérifier les logs

### 1. Ouvrir CloudWatch Logs

1. Allez dans **CloudWatch** (AWS Console)
2. Cliquez sur **"Logs"** dans le menu de gauche
3. Cliquez sur **"Log groups"**
4. Cherchez un groupe de logs qui contient le nom de votre fonction Lambda :
   - Ex: `/aws/lambda/mapevent-backend`
   - Ou `/aws/lambda/mapevent-backend-xxx`

### 2. Ouvrir les logs récents

1. Cliquez sur le groupe de logs de votre fonction Lambda
2. Vous verrez des "Log streams" (flux de logs)
3. Cliquez sur le plus récent (en haut de la liste)
4. Regardez les logs

### 3. Tester et observer

1. **Lancez un test** avec PowerShell :
```powershell
Invoke-WebRequest -Uri "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/api/admin/create-tables" -Method POST -Headers @{"Content-Type"="application/json"} -Body "{}"
```

2. **Retournez dans CloudWatch Logs**
3. **Actualisez** la page (F5)
4. **Regardez** si de nouveaux logs apparaissent

### 4. Interprétation

**Si vous voyez de NOUVEAUX logs après le test :**
- ✅ La requête **arrive** à Lambda
- Le problème est peut-être dans la réponse ou les permissions de réponse

**Si vous ne voyez AUCUN nouveau log :**
- ❌ La requête **n'arrive pas** à Lambda
- Le problème est dans API Gateway (permissions, configuration, ou déploiement)

## 🔍 Alternative : Vérifier depuis Lambda directement

### Depuis Lambda Console

1. **Lambda** > Fonction `mapevent-backend`
2. Onglet **"Monitoring"**
3. Regardez les métriques :
   - **Invocations** : Augmente-t-il quand vous testez ?
   - **Errors** : Y a-t-il des erreurs ?

4. Cliquez sur **"View logs in CloudWatch"**
5. Cela vous amène directement aux logs

## 📊 Ce qu'il faut chercher dans les logs

### Si la requête arrive à Lambda, vous verrez :
```
START RequestId: xxx
[INFO] Route appelée: /api/admin/create-tables
[INFO] Création des tables...
```

### Si la requête n'arrive pas, vous ne verrez rien

## ✅ Solution si la requête n'arrive pas

Si aucun log n'apparaît, le problème est dans API Gateway :

1. **Vérifiez les permissions** :
   - Lambda > Fonction > Configuration > Permissions
   - Le rôle IAM doit permettre à API Gateway d'invoquer

2. **Recréez l'intégration** :
   - API Gateway > `/create-tables` > POST
   - Integration Request > Modifier
   - Sauvegarder à nouveau
   - Accepter les permissions
   - Déployer

3. **Vérifiez le nom de la fonction** :
   - Le nom dans API Gateway doit être **exactement** le même que dans Lambda
   - Vérifiez qu'il n'y a pas d'espaces ou de caractères différents

## 🚨 Solution de contournement

En attendant, utilisez Lambda directement (ça fonctionne déjà) :

1. **Lambda** > Fonction `mapevent-backend`
2. Onglet **"Test"**
3. Événement de test :
```json
{
  "path": "/api/admin/create-tables",
  "httpMethod": "POST",
  "body": "{}"
}
```
4. **Test**

Cela créera les tables sans passer par API Gateway.

