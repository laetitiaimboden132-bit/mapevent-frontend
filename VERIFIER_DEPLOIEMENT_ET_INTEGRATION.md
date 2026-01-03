# 🔍 Vérifier le déploiement et l'intégration

## ✅ Autorisation : NONE (correct)

L'autorisation est bonne. Vérifions maintenant :

## 📋 Vérifications

### 1. L'API est-elle déployée ?

1. **API Gateway** > Votre API
2. En haut de l'écran, regardez le stage actif
3. Vous devriez voir : **"default"** ou un autre stage
4. Regardez la **date du dernier déploiement**

**Si c'est ancien (avant vos modifications) :**
- L'API n'est pas déployée avec les dernières modifications
- Il faut déployer

**Pour déployer :**
1. **Actions** (en haut) > **"Déployer l'API"**
2. **Stage** : `default`
3. **Description** : "Déploiement create-tables"
4. Cliquez **"Déployer"**

### 2. L'intégration Lambda est-elle correcte ?

1. **API Gateway** > `/api/admin/create-tables` > POST
2. Cliquez sur **"Integration Request"** (ou "Requête d'intégration")
3. Vérifiez :
   - **Integration type** : `Lambda Function`
   - **Lambda Function** : le nom exact de votre fonction (ex: `mapevent-backend`)
   - **Use Lambda Proxy integration** : ✓ (coché)

**Si quelque chose n'est pas correct :**
- Corrigez
- Sauvegardez
- Déployez l'API

### 3. Faire un nouveau test

Après avoir vérifié et déployé :

1. **Attendez 30 secondes**
2. Faites un nouveau test :
```powershell
Invoke-WebRequest -Uri "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/api/admin/create-tables" -Method POST -Headers @{"Content-Type"="application/json"} -Body "{}"
```

3. **Regardez les logs CloudWatch** :
   - Lambda > Monitoring > View logs in CloudWatch
   - Changez la plage : "Last 5 minutes"
   - Actualisez (F5)
   - Cherchez un **nouveau RequestId**
   - Cherchez les logs 🔍

## 🔍 Si vous voyez toujours les anciens logs

Cela signifie que la requête n'atteint toujours pas Lambda. Vérifiez :

1. **L'URL est-elle correcte ?**
   - `https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/api/admin/create-tables`
   - Pas `/default/api/admin/create-tables`

2. **La route existe-t-elle vraiment dans API Gateway ?**
   - Ressources > `/api` > `/admin` > `/create-tables` > POST
   - Vérifiez que tout existe

3. **L'intégration Lambda est-elle sauvegardée ?**
   - Après avoir configuré l'intégration, avez-vous cliqué sur "Save" ?
   - Avez-vous accepté les permissions Lambda ?

## ✅ Action immédiate

1. **Vérifiez la date du dernier déploiement** de l'API
2. **Si c'est ancien, déployez l'API**
3. **Vérifiez l'intégration Lambda** (nom de fonction correct)
4. **Attendez 30 secondes**
5. **Retestez**
6. **Regardez les logs CloudWatch**

Dites-moi :
- Quelle est la date du dernier déploiement de l'API ?
- Le nom de la fonction Lambda dans l'intégration est-il correct ?

