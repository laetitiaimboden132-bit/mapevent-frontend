# 🔧 Corriger CORS - Guide Simple Étape par Étape

## ❌ Le Problème

Quand vous cliquez sur "Payer", ça ne marche pas à cause d'une erreur CORS 403.

## ✅ La Solution Simple

Il faut autoriser votre site `mapevent.world` à communiquer avec votre API Lambda.

## 📋 Étapes dans AWS Console

### Étape 1 : Aller dans API Gateway

1. **Connectez-vous** à AWS Console : https://console.aws.amazon.com
2. **Cherchez** "API Gateway" dans la barre de recherche
3. **Cliquez** sur "API Gateway"

### Étape 2 : Trouver Votre API

1. **Cherchez** votre API dans la liste
   - Elle devrait s'appeler quelque chose comme "api" ou avoir l'ID `j33osy4bvj`
2. **Cliquez** dessus pour l'ouvrir

### Étape 3 : Trouver la Route de Paiement

1. Dans le menu de gauche, **cherchez** "Resources" ou "Ressources"
2. **Cherchez** la route `/payments` ou `/payments/create-checkout-session`
3. **Cliquez** dessus

### Étape 4 : Activer CORS

1. **Cliquez** sur "Actions" (en haut)
2. **Sélectionnez** "Enable CORS" ou "Activer CORS"
3. **Remplissez** :
   - **Access-Control-Allow-Origin** : `https://mapevent.world`
   - **Access-Control-Allow-Methods** : Cochez `POST`, `GET`, `OPTIONS`
   - **Access-Control-Allow-Headers** : `Content-Type, Authorization`
4. **Cliquez** sur "Enable CORS and replace existing CORS headers"

### Étape 5 : Déployer l'API

1. **Cliquez** sur "Actions" (en haut)
2. **Sélectionnez** "Deploy API" ou "Déployer l'API"
3. **Sélectionnez** votre stage : `default` (ou le nom de votre stage)
4. **Cliquez** sur "Deploy"

## 🎯 C'est Tout !

Après ça, les paiements devraient fonctionner.

## 🧪 Tester

1. **Rechargez** `https://mapevent.world`
2. **Cliquez** sur un contact (booking/service)
3. **Cliquez** sur "Payer CHF 1.–"
4. **Ça devrait fonctionner** maintenant ! ✅

## ⚠️ Si Vous Ne Trouvez Pas

### Option Alternative : Contacter le Développeur Backend

Si vous ne trouvez pas API Gateway ou si c'est trop compliqué :

**Demandez au développeur backend de** :
1. Ajouter les headers CORS dans le code Lambda
2. Gérer la requête OPTIONS (retourner 200)

### Code à Ajouter dans Lambda (pour le développeur)

```python
def lambda_handler(event, context):
    # Headers CORS
    headers = {
        'Access-Control-Allow-Origin': 'https://mapevent.world',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    
    # Gérer OPTIONS
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    # Votre code existant...
    # ...
    
    # Retourner avec headers CORS
    return {
        'statusCode': 200,
        'headers': headers,  # ⚠️ Important !
        'body': json.dumps({...})
    }
```

## 📞 Besoin d'Aide ?

Si vous êtes bloqué :
1. **Prenez une capture d'écran** de ce que vous voyez dans API Gateway
2. **Envoyez-la** au développeur backend
3. Il pourra vous guider ou le faire pour vous

## ✅ Résumé Simple

1. **AWS Console** → **API Gateway**
2. **Trouver votre API**
3. **Trouver** `/payments/create-checkout-session`
4. **Actions** → **Enable CORS**
5. **Mettre** : `https://mapevent.world`
6. **Actions** → **Deploy API**
7. **Tester** sur le site

---

**C'est tout ! Si vous êtes bloqué, demandez au développeur backend de le faire. 🔧**

