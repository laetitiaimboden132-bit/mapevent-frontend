# 🛠️ Créer la Route de Paiement - Guide Complet

## 📋 Ce Qu'il Faut Faire

1. **Créer la route** dans API Gateway
2. **Créer la fonction Lambda** qui gère Stripe
3. **Configurer CORS** pour autoriser `mapevent.world`

## 🚀 Étape 1 : Créer la Route dans API Gateway

### Dans AWS Console

1. **API Gateway** → Trouvez votre API
2. **Resources** (menu de gauche)
3. **Actions** → **Create Resource**
4. **Configure** :
   - **Resource Name** : `payments`
   - **Resource Path** : `/payments`
   - ✅ **Enable API Gateway CORS** (cocher)
5. **Create Resource**

### Créer la Sous-Route

1. **Sélectionnez** `/payments` (que vous venez de créer)
2. **Actions** → **Create Resource**
3. **Configure** :
   - **Resource Name** : `create-checkout-session`
   - **Resource Path** : `/create-checkout-session`
   - ✅ **Enable API Gateway CORS** (cocher)
4. **Create Resource**

### Créer la Méthode POST

1. **Sélectionnez** `/payments/create-checkout-session`
2. **Actions** → **Create Method**
3. **Sélectionnez** `POST`
4. **Configure** :
   - **Integration type** : Lambda Function
   - **Lambda Function** : Créez-en une nouvelle (voir étape 2)
   - ✅ **Use Lambda Proxy integration** (cocher)
5. **Save** → **OK** (autoriser API Gateway à appeler Lambda)

## 🚀 Étape 2 : Créer la Fonction Lambda

### Dans AWS Console

1. **Lambda** → **Create function**
2. **Configure** :
   - **Function name** : `mapevent-payments`
   - **Runtime** : Python 3.11 (ou 3.12)
   - **Architecture** : x86_64
3. **Create function**

### Code Lambda (Python)

**Remplacez tout le code** dans l'éditeur Lambda par :

```python
import json
import os
import stripe

# Récupérer les clés depuis les variables d'environnement
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')

def lambda_handler(event, context):
    # Headers CORS
    headers = {
        'Access-Control-Allow-Origin': 'https://mapevent.world',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Credentials': 'true'
    }
    
    # Gérer la pré-vérification OPTIONS
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    try:
        # Parser le body (si Lambda Proxy)
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        # Récupérer les paramètres
        payment_type = body.get('paymentType', 'contact')
        user_id = body.get('userId')
        email = body.get('email')
        amount = body.get('amount', 1.00)
        currency = body.get('currency', 'CHF')
        
        # Créer la session Stripe Checkout
        session_params = {
            'payment_method_types': ['card'],
            'mode': 'payment',
            'success_url': f'https://mapevent.world/?payment=success&session_id={{CHECKOUT_SESSION_ID}}',
            'cancel_url': 'https://mapevent.world/?payment=canceled',
            'customer_email': email,
            'metadata': {
                'userId': user_id,
                'paymentType': payment_type
            }
        }
        
        # Ajouter les line items selon le type de paiement
        if payment_type == 'contact':
            item_type = body.get('itemType', 'booking')
            item_id = body.get('itemId')
            
            session_params['line_items'] = [{
                'price_data': {
                    'currency': currency.lower(),
                    'product_data': {
                        'name': f'Contact {item_type}',
                        'description': f'Débloquer le contact pour {item_type} #{item_id}'
                    },
                    'unit_amount': int(amount * 100)  # Stripe utilise les centimes
                },
                'quantity': 1
            }]
            session_params['metadata']['itemType'] = item_type
            session_params['metadata']['itemId'] = str(item_id)
            
        elif payment_type == 'cart':
            items = body.get('items', [])
            session_params['line_items'] = []
            for item in items:
                session_params['line_items'].append({
                    'price_data': {
                        'currency': currency.lower(),
                        'product_data': {
                            'name': f'Contact {item.get("type", "item")}',
                            'description': f'Contact #{item.get("id")}'
                        },
                        'unit_amount': int(item.get('price', 1.00) * 100)
                    },
                    'quantity': 1
                })
            session_params['metadata']['items'] = json.dumps(items)
            
        elif payment_type == 'subscription':
            plan = body.get('plan', 'full-premium')
            session_params['mode'] = 'subscription'
            session_params['line_items'] = [{
                'price_data': {
                    'currency': currency.lower(),
                    'product_data': {
                        'name': f'Abonnement {plan}',
                        'description': f'Abonnement mensuel {plan}'
                    },
                    'unit_amount': int(amount * 100),
                    'recurring': {
                        'interval': 'month'
                    }
                },
                'quantity': 1
            }]
            session_params['metadata']['plan'] = plan
        
        # Créer la session Stripe
        session = stripe.checkout.Session.create(**session_params)
        
        # Retourner la réponse
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'sessionId': session.id,
                'publicKey': STRIPE_PUBLISHABLE_KEY
            })
        }
        
    except stripe.error.StripeError as e:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({
                'error': str(e.user_message) if hasattr(e, 'user_message') else str(e)
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': f'Erreur serveur: {str(e)}'
            })
        }
```

### Configurer les Variables d'Environnement Lambda

1. **Configuration** → **Environment variables**
2. **Add environment variable** :
   - **Key** : `STRIPE_SECRET_KEY`
   - **Value** : `sk_live_VOTRE_CLE_SECRETE`
3. **Add environment variable** :
   - **Key** : `STRIPE_PUBLISHABLE_KEY`
   - **Value** : `pk_live_VOTRE_CLE_PUBLIQUE`
4. **Save**

### Installer Stripe dans Lambda

1. **Code** → **Add a layer** (ou créer un package)
2. **Option 1** : Créer un layer avec Stripe
   - Créer un dossier `python` avec `stripe/`
   - Zipper et uploader comme layer
3. **Option 2** : Utiliser un layer public
   - Chercher "stripe" dans les layers publics

**OU** créer un package :

1. **Créer un fichier** `requirements.txt` :
```
stripe>=7.0.0
```

2. **Installer localement** et zipper :
```bash
pip install stripe -t .
zip -r lambda-package.zip .
```

3. **Uploader** dans Lambda

## 🚀 Étape 3 : Configurer CORS

### Dans API Gateway

1. **Sélectionnez** `/payments/create-checkout-session`
2. **Actions** → **Enable CORS**
3. **Configure** :
   - **Access-Control-Allow-Origin** : `https://mapevent.world`
   - **Access-Control-Allow-Methods** : `POST, OPTIONS`
   - **Access-Control-Allow-Headers** : `Content-Type, Authorization`
4. **Enable CORS and replace existing CORS headers**

### Déployer l'API

1. **Actions** → **Deploy API**
2. **Deployment stage** : `default` (ou votre stage)
3. **Deploy**

## 🧪 Tester

1. **Recharger** `https://mapevent.world`
2. **Cliquer** sur un contact
3. **Cliquer** sur "Payer CHF 1.–"
4. **Vérifier** dans la console (F12) :
   - OPTIONS → 200 ✅
   - POST → 200 avec `sessionId` ✅
   - Redirection vers Stripe ✅

## 📋 Checklist Complète

- [ ] Route `/payments` créée dans API Gateway
- [ ] Route `/payments/create-checkout-session` créée
- [ ] Méthode POST créée et liée à Lambda
- [ ] Fonction Lambda créée avec le code Stripe
- [ ] Variables d'environnement Lambda configurées
- [ ] Stripe installé dans Lambda (layer ou package)
- [ ] CORS configuré dans API Gateway
- [ ] API déployée
- [ ] Test réussi

---

**Suivez ces étapes une par une, et votre route de paiement sera créée ! 🚀**

