# 🔧 Corriger l'Erreur 404 sur la Route de Paiement

## ❌ Problème Actuel

```
POST https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/payments/create-checkout-session
[HTTP/2 404]
```

**La route retourne 404** = La route n'existe pas dans API Gateway.

## 🔍 Vérification

### Le Chemin Complet

Votre frontend appelle :
```
https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/payments/create-checkout-session
```

Cela signifie :
- **Stage** : `default`
- **Chemin** : `/api/payments/create-checkout-session`

### Dans API Gateway

Vous devez avoir cette structure :
```
/ (root)
  └── api
      └── payments
          └── create-checkout-session (POST)
```

## ✅ Solution : Créer la Route

### Étape 1 : Vérifier la Structure Actuelle

1. **API Gateway** → Votre API
2. **Resources** (menu de gauche)
3. **Regardez** ce que vous avez :
   - `/` (root)
   - `/api` ? (si oui, continuez)
   - `/payments` ? (si oui, continuez)
   - `/create-checkout-session` ? (si oui, c'est bon !)

### Étape 2 : Créer `/api` (si n'existe pas)

1. **Sélectionnez** `/` (root)
2. **Actions** → **Create Resource**
3. **Configure** :
   - **Resource Name** : `api`
   - **Resource Path** : `/api`
   - ✅ **Enable API Gateway CORS**
4. **Create Resource**

### Étape 3 : Créer `/payments` (si n'existe pas)

1. **Sélectionnez** `/api`
2. **Actions** → **Create Resource**
3. **Configure** :
   - **Resource Name** : `payments`
   - **Resource Path** : `/payments`
   - ✅ **Enable API Gateway CORS**
4. **Create Resource**

### Étape 4 : Créer `/create-checkout-session`

1. **Sélectionnez** `/api/payments`
2. **Actions** → **Create Resource**
3. **Configure** :
   - **Resource Name** : `create-checkout-session`
   - **Resource Path** : `/create-checkout-session`
   - ✅ **Enable API Gateway CORS**
4. **Create Resource**

### Étape 5 : Créer la Méthode POST

1. **Sélectionnez** `/api/payments/create-checkout-session`
2. **Actions** → **Create Method**
3. **Sélectionnez** `POST`
4. **Configure** :
   - **Integration type** : Lambda Function
   - **Lambda Function** : Sélectionnez votre fonction Lambda (celle avec le code backend)
   - ✅ **Use Lambda Proxy integration** (cocher)
5. **Save** → **OK** (autoriser API Gateway)

### Étape 6 : Activer CORS

1. **Sélectionnez** `/api/payments/create-checkout-session`
2. **Actions** → **Enable CORS**
3. **Configure** :
   - **Access-Control-Allow-Origin** : `https://mapevent.world`
   - **Access-Control-Allow-Methods** : `POST, OPTIONS`
   - **Access-Control-Allow-Headers** : `Content-Type, Authorization`
4. **Enable CORS and replace existing CORS headers**

### Étape 7 : Déployer l'API

1. **Actions** → **Deploy API**
2. **Deployment stage** : `default` (important !)
3. **Deploy**

## 🔍 Vérifier que Lambda est Correctement Configuré

### Vérifier le Handler Lambda

1. **Lambda** → Votre fonction
2. **Configuration** → **Runtime settings**
3. **Handler** doit pointer vers votre fonction Flask

**Si vous utilisez Flask** (comme votre code), le handler doit être quelque chose comme :
- `lambda_function.lambda_handler` (si vous avez un wrapper)
- Ou votre fonction Flask adaptée pour Lambda

### Vérifier les Variables d'Environnement Lambda

1. **Configuration** → **Environment variables**
2. **Vérifiez** :
   - `STRIPE_SECRET_KEY` = `sk_live_...`
   - `STRIPE_PUBLIC_KEY` = `pk_live_...` (ou `STRIPE_PUBLISHABLE_KEY`)

## 🧪 Tester Après Configuration

1. **Recharger** `https://mapevent.world`
2. **Console** (F12) → Network
3. **Faire un paiement**
4. **Vérifier** :
   - OPTIONS → **200** ✅
   - POST → **200** (pas 404) ✅
   - Réponse avec `sessionId` ✅

## ⚠️ Autres Problèmes dans les Logs

### "Aucune donnée disponible pour le mode event"

- ⚠️ Les événements ne se chargent pas
- **Cause** : `ensureDemoPoints()` ne génère pas les événements
- **Solution** : Vérifier les logs dans la console (on a ajouté des logs de diagnostic)

### Erreurs 404 pour Images

- ⚠️ Images manquantes : `Dub.jpg`, `Dub.jpeg`, etc.
- **Cause** : Images non uploadées dans S3
- **Solution** : Uploader les images manquantes dans `public/assets/category_images/`

### Erreurs CSP Stripe

- ✅ **Normales** (avertissements, pas d'erreurs bloquantes)
- **Pas besoin de corriger** pour l'instant

## 📋 Checklist Complète

- [ ] Route `/api` créée dans API Gateway
- [ ] Route `/api/payments` créée
- [ ] Route `/api/payments/create-checkout-session` créée
- [ ] Méthode POST créée et liée à Lambda
- [ ] CORS activé sur `/create-checkout-session`
- [ ] API déployée sur stage `default`
- [ ] Variables d'environnement Lambda configurées
- [ ] Test : POST retourne 200 (pas 404)

## 💡 Si Vous Utilisez Flask dans Lambda

Votre code utilise Flask. Assurez-vous que Lambda est configuré pour Flask :

### Option 1 : Utiliser un Wrapper Lambda

Créez un fichier `lambda_function.py` :

```python
from backend.main import create_app

app = create_app()

def lambda_handler(event, context):
    # Adapter l'événement API Gateway pour Flask
    from awsgi import response
    
    return response(app, event, context)
```

### Option 2 : Utiliser awsgi

Installer `awsgi` dans Lambda :
- Créer un layer avec `awsgi`
- Ou inclure dans le package Lambda

---

**Le problème principal est que la route n'existe pas dans API Gateway. Créez-la étape par étape comme indiqué ci-dessus ! 🔧**

