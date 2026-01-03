# 💳 Passage Stripe en Mode Production

## ✅ État Actuel

**Frontend** : ✅ **PRÊT** - Aucun changement nécessaire
- Le frontend récupère automatiquement la clé publique Stripe depuis le backend
- Pas de clé hardcodée dans le code
- Compatible test et production

## 🔧 Configuration Backend (À FAIRE)

### 1. Dans votre Backend Lambda (AWS)

Trouvez où sont configurées les clés Stripe dans votre backend :

**Fichier probable** : `lambda-package/backend/main.py` ou variables d'environnement Lambda

### 2. Récupérer vos Clés Stripe Production

1. **Connectez-vous à Stripe Dashboard** : https://dashboard.stripe.com
2. **Activez le mode Live** (bouton en haut à droite)
3. **Récupérez vos clés** :
   - **Clé Publique (Publishable Key)** : Commence par `pk_live_...`
   - **Clé Secrète (Secret Key)** : Commence par `sk_live_...`

### 3. Configurer le Backend

#### Option A : Variables d'Environnement Lambda (RECOMMANDÉ)

Dans AWS Lambda Console → Configuration → Variables d'environnement :

```
STRIPE_SECRET_KEY=sk_live_VOTRE_CLE_SECRETE
STRIPE_PUBLISHABLE_KEY=pk_live_VOTRE_CLE_PUBLIQUE
STRIPE_MODE=live
```

#### Option B : Dans le Code Backend

Si vous utilisez des variables hardcodées (moins sécurisé), remplacez :

```python
# AVANT (TEST)
STRIPE_SECRET_KEY = "sk_test_..."
STRIPE_PUBLISHABLE_KEY = "pk_test_..."

# APRÈS (PRODUCTION)
STRIPE_SECRET_KEY = "sk_live_..."
STRIPE_PUBLISHABLE_KEY = "pk_live_..."
```

### 4. Vérifier l'Endpoint Backend

Votre endpoint `/payments/create-checkout-session` doit retourner :

```json
{
  "sessionId": "cs_live_...",
  "publicKey": "pk_live_..."
}
```

Le frontend utilisera automatiquement cette clé publique.

## 🔐 Sécurité

⚠️ **IMPORTANT** :
- ✅ **Clé Publique (pk_live_)** : Peut être exposée dans le frontend (c'est normal)
- ❌ **Clé Secrète (sk_live_)** : JAMAIS dans le frontend, uniquement dans le backend
- ✅ Utilisez des **variables d'environnement** pour la clé secrète
- ✅ Ne commitez JAMAIS les clés dans Git

## 📋 Checklist Avant Production

- [ ] Compte Stripe activé en mode **Live**
- [ ] Informations business complétées dans Stripe Dashboard
- [ ] Clés de production récupérées (`pk_live_` et `sk_live_`)
- [ ] Backend configuré avec les clés de production
- [ ] Variables d'environnement Lambda mises à jour
- [ ] Webhooks Stripe configurés en production (si nécessaire)
- [ ] Test d'un paiement réel avec une petite somme
- [ ] Vérification des emails de confirmation Stripe

## 🧪 Tester en Production

1. **Faire un test avec une vraie carte** (petit montant)
2. **Vérifier dans Stripe Dashboard** → Paiements → Voir le paiement
3. **Vérifier les webhooks** (si configurés)
4. **Tester les différents types de paiement** :
   - Contact unique (CHF 1.–)
   - Panier
   - Abonnements

## 🔄 Retour en Mode Test

Si vous devez revenir en test temporairement :

1. Dans Stripe Dashboard : Passer en mode **Test**
2. Dans Lambda : Remettre les clés `sk_test_` et `pk_test_`
3. Redéployer le backend

## 📞 Support Stripe

- **Documentation** : https://stripe.com/docs
- **Support** : https://support.stripe.com
- **Dashboard** : https://dashboard.stripe.com

## ✅ Résumé

**Frontend** : ✅ Aucun changement nécessaire
**Backend** : ⚠️ Changer les clés Stripe de `test` à `live`

Une fois le backend configuré avec les clés de production, tout fonctionnera automatiquement ! 🚀

