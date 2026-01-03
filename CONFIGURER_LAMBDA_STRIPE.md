# 🔧 Configurer Stripe dans AWS Lambda

## ✅ OUI - Mettre la Clé dans Lambda

**Mais PAS dans le code source !** Utilisez les **variables d'environnement**.

## 📋 Méthode 1 : Variables d'Environnement (Recommandé)

### Étape 1 : Dans AWS Lambda Console

1. **Allez dans votre fonction Lambda**
2. **Configuration** → **Variables d'environnement**
3. **Ajoutez** :

```
STRIPE_SECRET_KEY = sk_live_VOTRE_CLE_SECRETE
STRIPE_PUBLISHABLE_KEY = pk_live_VOTRE_CLE_PUBLIQUE
```

### Étape 2 : Dans votre Code Lambda (Python)

**NE PAS faire ça** ❌ :
```python
stripe_secret = "sk_live_1234567890"  # ❌ JAMAIS dans le code !
```

**Faire ça** ✅ :
```python
import os

stripe_secret = os.environ.get('STRIPE_SECRET_KEY')
stripe_public = os.environ.get('STRIPE_PUBLISHABLE_KEY')
```

### Étape 3 : Utiliser dans votre Code

```python
import stripe
import os

# Récupérer depuis les variables d'environnement
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Créer une session Checkout
session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[{
        'price_data': {
            'currency': 'chf',
            'product_data': {
                'name': 'Contact',
            },
            'unit_amount': 100,  # CHF 1.00
        },
        'quantity': 1,
    }],
    mode='payment',
    success_url='https://mapevent.world/?payment=success',
    cancel_url='https://mapevent.world/?payment=canceled',
)

# Retourner la clé publique au frontend
return {
    'sessionId': session.id,
    'publicKey': os.environ.get('STRIPE_PUBLISHABLE_KEY')
}
```

## 📋 Méthode 2 : AWS Systems Manager Parameter Store (Plus Sécurisé)

### Étape 1 : Créer les Paramètres

1. **AWS Console** → **Systems Manager** → **Parameter Store**
2. **Create parameter** :
   - **Name** : `/mapevent/stripe/secret-key`
   - **Type** : **SecureString** (chiffré)
   - **Value** : `sk_live_VOTRE_CLE_SECRETE`

3. **Create parameter** :
   - **Name** : `/mapevent/stripe/publishable-key`
   - **Type** : **String**
   - **Value** : `pk_live_VOTRE_CLE_PUBLIQUE`

### Étape 2 : Donner Accès à Lambda

Dans **IAM** → **Roles** → Votre rôle Lambda :

Ajoutez la politique :
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ssm:GetParameter",
                "ssm:GetParameters"
            ],
            "Resource": [
                "arn:aws:ssm:*:*:parameter/mapevent/stripe/*"
            ]
        }
    ]
}
```

### Étape 3 : Dans votre Code Lambda

```python
import boto3
import os

# Récupérer depuis Parameter Store
ssm = boto3.client('ssm')

def get_stripe_keys():
    secret_key = ssm.get_parameter(
        Name='/mapevent/stripe/secret-key',
        WithDecryption=True
    )['Parameter']['Value']
    
    public_key = ssm.get_parameter(
        Name='/mapevent/stripe/publishable-key'
    )['Parameter']['Value']
    
    return secret_key, public_key

# Utiliser
stripe_secret, stripe_public = get_stripe_keys()
stripe.api_key = stripe_secret
```

## ⚠️ Ce qu'il NE FAUT PAS Faire

### ❌ Dans le Code Source
```python
# ❌ JAMAIS faire ça !
STRIPE_KEY = "sk_live_1234567890abcdef"
```

### ❌ Dans Git
```python
# ❌ Ne JAMAIS commiter les clés
# Même dans un fichier .env qui est dans .gitignore
```

### ❌ En Dur dans le Code
```python
# ❌ Même avec un commentaire "à changer"
stripe_key = "sk_live_..."  # ❌
```

## ✅ Checklist Configuration

- [ ] Clé secrète dans **Variables d'environnement Lambda** (ou Parameter Store)
- [ ] Clé publique dans **Variables d'environnement Lambda** (ou Parameter Store)
- [ ] Code Lambda utilise `os.environ.get()` pour récupérer les clés
- [ ] **AUCUNE clé** dans le code source
- [ ] **AUCUNE clé** dans Git
- [ ] IAM Role a les permissions nécessaires (si Parameter Store)

## 🔐 Sécurité

### Variables d'Environnement
- ✅ Pas dans le code
- ⚠️ Visible dans la console AWS (si quelqu'un a accès)
- ✅ Recommandé pour débuter

### Parameter Store
- ✅ Chiffré automatiquement
- ✅ Accès contrôlé par IAM
- ✅ Historique des changements
- ✅ **Plus sécurisé** pour production

## 📝 Exemple Complet Lambda

```python
import json
import os
import stripe

def lambda_handler(event, context):
    # Récupérer les clés depuis les variables d'environnement
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
    public_key = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    
    # Vérifier que les clés existent
    if not stripe.api_key or not public_key:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Stripe keys not configured'})
        }
    
    try:
        # Créer une session Checkout
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'chf',
                    'product_data': {'name': 'Contact'},
                    'unit_amount': 100,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://mapevent.world/?payment=success&session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://mapevent.world/?payment=canceled',
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'sessionId': session.id,
                'publicKey': public_key
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

## 🎯 Résumé

| Où | Comment |
|---|---|
| **Clé secrète** | Variables d'environnement Lambda : `STRIPE_SECRET_KEY` |
| **Clé publique** | Variables d'environnement Lambda : `STRIPE_PUBLISHABLE_KEY` |
| **Dans le code** | `os.environ.get('STRIPE_SECRET_KEY')` |
| **Dans Git** | ❌ **JAMAIS** |

---

**En résumé : OUI, mettez les clés dans Lambda via les variables d'environnement, PAS directement dans le code ! 🔐**

