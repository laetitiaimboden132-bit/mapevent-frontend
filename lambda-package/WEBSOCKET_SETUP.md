# 🔌 Configuration API Gateway WebSocket pour MapEventAI

## Vue d'ensemble

Pour activer les notifications et messages en temps réel, vous devez configurer une API Gateway WebSocket API séparée de l'API REST Lambda actuelle.

## 📋 Prérequis

- AWS CLI configuré
- Permissions IAM pour créer API Gateway et Lambda
- Lambda function existante pour le backend REST

## 🚀 Étapes de configuration

### 1. Créer une Lambda Function pour WebSocket

```bash
# Créer une nouvelle fonction Lambda pour WebSocket
aws lambda create-function \
    --function-name mapevent-websocket-handler \
    --runtime python3.11 \
    --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role \
    --handler websocket_handler.lambda_handler \
    --zip-file fileb://websocket-handler.zip \
    --region eu-west-1
```

### 2. Créer l'API Gateway WebSocket API

```bash
# Créer l'API WebSocket
aws apigatewayv2 create-api \
    --name mapevent-websocket-api \
    --protocol-type WEBSOCKET \
    --route-selection-expression '$request.body.action' \
    --region eu-west-1
```

Notez l'`ApiId` retourné.

### 3. Créer les routes WebSocket

```bash
# Route pour la connexion
aws apigatewayv2 create-route \
    --api-id YOUR_API_ID \
    --route-key '$connect' \
    --target integrations/YOUR_INTEGRATION_ID

# Route pour la déconnexion
aws apigatewayv2 create-route \
    --api-id YOUR_API_ID \
    --route-key '$disconnect' \
    --target integrations/YOUR_INTEGRATION_ID

# Route pour les messages
aws apigatewayv2 create-route \
    --api-id YOUR_API_ID \
    --route-key '$default' \
    --target integrations/YOUR_INTEGRATION_ID
```

### 4. Créer les intégrations Lambda

```bash
# Intégration pour connect
aws apigatewayv2 create-integration \
    --api-id YOUR_API_ID \
    --integration-type AWS_PROXY \
    --integration-uri arn:aws:lambda:eu-west-1:YOUR_ACCOUNT_ID:function:mapevent-websocket-handler \
    --integration-method POST

# Répéter pour disconnect et default
```

### 5. Déployer l'API

```bash
# Créer un stage
aws apigatewayv2 create-stage \
    --api-id YOUR_API_ID \
    --stage-name production \
    --auto-deploy

# Obtenir l'URL WebSocket
aws apigatewayv2 get-api \
    --api-id YOUR_API_ID \
    --query 'ApiEndpoint' \
    --output text
```

### 6. Mettre à jour le frontend

Dans `public/map_logic.js`, remplacez le polling par une vraie connexion WebSocket:

```javascript
function initWebSocket() {
  if (!currentUser.isLoggedIn) return;
  
  const wsUrl = 'wss://YOUR_API_ID.execute-api.eu-west-1.amazonaws.com/production';
  
  socket = new WebSocket(wsUrl);
  
  socket.onopen = () => {
    console.log('✅ WebSocket connecté');
    socket.send(JSON.stringify({
      action: 'connect',
      userId: currentUser.id
    }));
  };
  
  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'notification') {
      // Traiter la notification
      handleNotification(data);
    } else if (data.type === 'new_message') {
      // Traiter le nouveau message
      handleNewMessage(data);
    } else if (data.type === 'reaction_update') {
      // Traiter la mise à jour de réaction
      handleReactionUpdate(data);
    }
  };
  
  socket.onerror = (error) => {
    console.error('Erreur WebSocket:', error);
  };
  
  socket.onclose = () => {
    console.log('WebSocket fermé, reconnexion...');
    setTimeout(initWebSocket, 5000);
  };
}
```

## 📝 Handler Lambda WebSocket

Créez `lambda-package/websocket_lambda_handler.py`:

```python
import json
import boto3

def lambda_handler(event, context):
    route_key = event.get('requestContext', {}).get('routeKey')
    connection_id = event.get('requestContext', {}).get('connectionId')
    
    if route_key == '$connect':
        # Enregistrer la connexion
        # TODO: Stocker connection_id dans DynamoDB avec userId
        return {'statusCode': 200}
    
    elif route_key == '$disconnect':
        # Supprimer la connexion
        # TODO: Supprimer connection_id de DynamoDB
        return {'statusCode': 200}
    
    elif route_key == '$default':
        # Traiter le message
        body = json.loads(event.get('body', '{}'))
        action = body.get('action')
        
        # Router vers le bon handler
        if action == 'join_group':
            # TODO: Implémenter join_group
            pass
        elif action == 'send_message':
            # TODO: Diffuser le message à tous les membres du groupe
            pass
        
        return {'statusCode': 200}
    
    return {'statusCode': 400}
```

## 🔐 Permissions IAM requises

Votre rôle Lambda doit avoir:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "execute-api:ManageConnections"
      ],
      "Resource": "arn:aws:execute-api:eu-west-1:*:*/*/@connections/*"
    }
  ]
}
```

## 💰 Coûts estimés

- **API Gateway WebSocket**: 
  - $1.00 par million de messages
  - Gratuit jusqu'à 1 million de messages/mois
- **Lambda**: 
  - $0.20 par million de requêtes
  - Gratuit jusqu'à 1 million de requêtes/mois

## ✅ Checklist de déploiement

- [ ] Lambda function créée pour WebSocket
- [ ] API Gateway WebSocket API créée
- [ ] Routes configurées ($connect, $disconnect, $default)
- [ ] Intégrations Lambda créées
- [ ] Stage déployé
- [ ] URL WebSocket obtenue
- [ ] Frontend mis à jour avec l'URL WebSocket
- [ ] Permissions IAM configurées
- [ ] Tests de connexion effectués

## 🐛 Dépannage

**Erreur: "Forbidden"**
- Vérifiez les permissions IAM du rôle Lambda
- Vérifiez que l'intégration Lambda est correcte

**Connexion échoue**
- Vérifiez l'URL WebSocket (doit commencer par `wss://`)
- Vérifiez les CORS si nécessaire
- Vérifiez les logs CloudWatch de Lambda

**Messages non reçus**
- Vérifiez que la route `$default` est configurée
- Vérifiez que le handler Lambda traite correctement les messages
- Vérifiez les logs CloudWatch





