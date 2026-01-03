# 🔍 Vérifier la réponse de Lambda

## ✅ Bonne nouvelle
Les logs montrent que la requête **arrive bien à Lambda** !
- RequestId: d6bf8e16-fc4d-49ca-9fb3-bdff0354858d
- Duration: 596.30 ms

## 🔍 Problème
La requête arrive à Lambda mais API Gateway retourne 403. Le problème est probablement dans la **réponse**.

## 📋 Vérifications à faire

### 1. Voir les logs complets de cette requête

Dans CloudWatch Logs, cherchez les logs **AVANT** le "END" pour voir :
- Le log "START"
- Les logs de votre code (print, logger.info, etc.)
- Les erreurs éventuelles

**Cherchez dans les logs :**
- `START RequestId: d6bf8e16-fc4d-49ca-9fb3-bdff0354858d`
- Les messages de votre code Python
- Les erreurs éventuelles

### 2. Vérifier le format de la réponse Lambda

Avec Lambda Proxy integration, Lambda doit retourner un format spécifique :

```python
{
    "statusCode": 200,
    "headers": {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
    },
    "body": "{\"status\":\"success\",\"message\":\"Tables créées\"}"
}
```

### 3. Vérifier le code de la route create-tables

Le code dans `admin_routes.py` doit retourner le bon format. Vérifiez que Flask retourne bien une réponse JSON.

## 🔧 Solution : Ajouter les headers CORS dans la réponse

Si Lambda retourne une réponse mais sans les headers CORS, API Gateway peut bloquer.

### Option 1 : Vérifier que Flask-CORS est bien configuré

Dans `main.py`, vous avez :
```python
CORS(app)  # Permettre les requêtes cross-origin
```

Cela devrait ajouter automatiquement les headers CORS.

### Option 2 : Vérifier la réponse de méthode dans API Gateway

1. API Gateway > `/api/admin/create-tables` > POST
2. **Réponse de méthode** (Method Response)
3. Vérifiez que le code **200** est présent
4. Si absent, ajoutez-le

### Option 3 : Vérifier la réponse d'intégration

1. **Réponse d'intégration** (Integration Response)
2. Avec Lambda Proxy, cela devrait être automatique
3. Vérifiez qu'il n'y a pas d'erreur de mapping

## 🔍 Diagnostic : Voir les logs complets

Pour voir ce que Lambda retourne vraiment :

1. Dans CloudWatch Logs, cherchez le log **START** correspondant
2. Regardez tous les logs entre START et END
3. Cherchez les erreurs ou les messages de votre code

## ✅ Solution rapide : Tester avec un événement simple

Créez un événement de test dans Lambda avec :
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

Et regardez la réponse. Si Lambda retourne bien une réponse 200, le problème est dans API Gateway (réponse de méthode ou mapping).

## 🚨 Si Lambda retourne une erreur

Si vous voyez une erreur dans les logs (avant le END), corrigez d'abord cette erreur dans le code Lambda.

