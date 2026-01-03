# 🔧 Configurer la Route de Paiement Existante

## ✅ Bonne Nouvelle !

Votre backend a **DÉJÀ** la route `/api/payments/create-checkout-session` ! 

Il faut juste la **configurer dans API Gateway** et **activer CORS**.

## 📋 Étape 1 : Vérifier dans API Gateway

### Dans AWS Console

1. **API Gateway** → Trouvez votre API
2. **Resources** (menu de gauche)
3. **Cherchez** si vous avez déjà :
   - `/api` ou `/default/api`
   - `/payments` ou `/api/payments`
   - `/create-checkout-session` ou `/payments/create-checkout-session`

### Si la Route Existe Déjà

Si vous voyez `/api/payments/create-checkout-session` :
- ✅ La route existe !
- ⚠️ Il faut juste **configurer CORS** (voir étape 2)

### Si la Route N'Existe PAS

Si vous ne voyez pas la route :
- ⚠️ Il faut la **créer** (voir étape 3)

## 🚀 Étape 2 : Configurer CORS (Si Route Existe)

### Dans API Gateway

1. **Sélectionnez** `/api/payments/create-checkout-session` (ou votre route)
2. **Actions** → **Enable CORS**
3. **Configure** :
   - **Access-Control-Allow-Origin** : `https://mapevent.world`
   - **Access-Control-Allow-Methods** : `POST, GET, OPTIONS`
   - **Access-Control-Allow-Headers** : `Content-Type, Authorization`
   - **Access-Control-Allow-Credentials** : `true` (si nécessaire)
4. **Enable CORS and replace existing CORS headers**

### Déployer

1. **Actions** → **Deploy API**
2. **Deployment stage** : `default` (ou votre stage)
3. **Deploy**

## 🚀 Étape 3 : Créer la Route (Si Elle N'Existe Pas)

### Créer la Structure

1. **API Gateway** → Votre API
2. **Resources** → **Actions** → **Create Resource**

#### Créer `/api` (si n'existe pas)

- **Resource Name** : `api`
- **Resource Path** : `/api`
- ✅ **Enable API Gateway CORS**
- **Create Resource**

#### Créer `/payments` (si n'existe pas)

- **Sélectionnez** `/api`
- **Actions** → **Create Resource**
- **Resource Name** : `payments`
- **Resource Path** : `/payments`
- ✅ **Enable API Gateway CORS**
- **Create Resource**

#### Créer `/create-checkout-session`

- **Sélectionnez** `/api/payments`
- **Actions** → **Create Resource**
- **Resource Name** : `create-checkout-session`
- **Resource Path** : `/create-checkout-session`
- ✅ **Enable API Gateway CORS**
- **Create Resource**

### Créer la Méthode POST

1. **Sélectionnez** `/api/payments/create-checkout-session`
2. **Actions** → **Create Method**
3. **Sélectionnez** `POST`
4. **Configure** :
   - **Integration type** : Lambda Function
   - **Lambda Function** : Votre fonction Lambda qui contient le code backend
   - ✅ **Use Lambda Proxy integration** (cocher)
5. **Save** → **OK** (autoriser API Gateway)

## 🔍 Étape 4 : Vérifier la Fonction Lambda

### Vérifier que Lambda a le Code

1. **Lambda** → Trouvez votre fonction
2. **Vérifiez** que le code contient :
   - `@app.route('/api/payments/create-checkout-session', methods=['POST'])`
   - Gestion de Stripe
   - Headers CORS

### Si Lambda Utilise Flask (comme votre code)

Votre code utilise **Flask**, donc Lambda doit être configuré pour Flask.

**Vérifiez** :
- ✅ Le handler Lambda pointe vers votre fonction Flask
- ✅ Les variables d'environnement sont configurées :
  - `STRIPE_SECRET_KEY`
  - `STRIPE_PUBLIC_KEY` (ou `STRIPE_PUBLISHABLE_KEY`)

## 🚀 Étape 5 : Vérifier CORS dans le Code

Votre code backend a déjà `CORS(app)` (ligne 24), mais vérifiez :

### Dans `main.py`

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # ✅ Déjà là !
```

### Si CORS Ne Fonctionne Pas

Ajoutez une configuration plus spécifique :

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://mapevent.world", "https://www.mapevent.world"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

## 🧪 Tester

1. **Recharger** `https://mapevent.world`
2. **Console** (F12) → Network
3. **Faire un paiement**
4. **Vérifier** :
   - OPTIONS → **200** ✅
   - POST → **200** avec `sessionId` ✅

## 📋 Checklist

- [ ] Route `/api/payments/create-checkout-session` existe dans API Gateway
- [ ] Méthode POST créée et liée à Lambda
- [ ] CORS activé dans API Gateway
- [ ] API déployée
- [ ] Variables d'environnement Lambda configurées
- [ ] Test : OPTIONS retourne 200
- [ ] Test : POST retourne 200 avec sessionId

## ⚠️ Si Problème Persiste

### Vérifier les Logs Lambda

1. **Lambda** → Votre fonction
2. **Monitor** → **View logs in CloudWatch**
3. **Voir** les erreurs exactes

### Vérifier API Gateway Logs

1. **API Gateway** → Votre API
2. **Settings** → **CloudWatch Log role ARN**
3. **Activer** les logs si nécessaire

---

**Votre backend existe déjà ! Il faut juste configurer la route dans API Gateway et activer CORS. 🚀**

