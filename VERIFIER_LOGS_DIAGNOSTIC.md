# 🔍 Vérifier les logs de diagnostic

## 📋 Étapes

### 1. Ouvrir CloudWatch Logs

1. **Lambda** > Fonction `mapevent-backend`
2. Onglet **"Monitoring"**
3. Cliquez sur **"View logs in CloudWatch"**
4. Ou allez directement dans **CloudWatch** > **Logs** > **Log groups** > `/aws/lambda/mapevent-backend`

### 2. Trouver les logs récents

1. Cliquez sur le **log stream** le plus récent (en haut de la liste)
2. Regardez les logs après votre dernier test PowerShell

### 3. Chercher les logs de diagnostic

Vous devriez voir des logs qui commencent par `🔍` :

```
🔍 Path reçu: /api/admin/create-tables
🔍 Path traité: /api/admin/create-tables
🔍 Méthode: POST
🔍 Body: {}
🔍 Appel Flask: POST /api/admin/create-tables
🔍 Réponse Flask: 200
🔍 Body réponse: {...}
```

## 🔍 Interprétation

### Si vous voyez les logs 🔍 :
- ✅ La requête **arrive** à Lambda
- ✅ Le handler Lambda **fonctionne**
- Le problème est peut-être dans la réponse ou API Gateway

### Si vous ne voyez AUCUN log 🔍 :
- ❌ Lambda n'a pas été redéployé avec le nouveau code
- Ou la requête n'arrive pas à Lambda

### Si vous voyez une erreur :
- Regardez l'erreur complète
- Cela vous dira où est le problème

## 📤 Envoyez-moi

Copiez-collez ici **TOUS les logs** que vous voyez dans CloudWatch après votre test PowerShell, surtout ceux qui commencent par `🔍`.

Cela me permettra de voir exactement ce qui se passe !

