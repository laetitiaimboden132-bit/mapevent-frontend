# 💳 Configuration Stripe - Guide Complet

## ✅ Ce qui a été implémenté

### Backend
- ✅ Tables `payments` et `subscriptions` dans la base de données
- ✅ Endpoints `/api/payments/*` :
  - `POST /api/payments/create-checkout-session` - Crée une session Stripe
  - `GET /api/payments/verify-session` - Vérifie le statut d'un paiement
  - `GET /api/payments/subscription-status` - Récupère l'abonnement d'un utilisateur
  - `POST /api/payments/webhook` - Gère les webhooks Stripe
- ✅ Package `stripe==7.8.0` ajouté à `requirements.txt`

### Frontend
- ✅ Stripe.js intégré (`https://js.stripe.com/v3/`)
- ✅ `processContactPayment()` - Paiement pour débloquer un contact
- ✅ `processSubscriptionPayment()` - Paiement pour un abonnement
- ✅ `processCartCheckout()` - Paiement pour le panier
- ✅ Gestion du retour Stripe après paiement
- ✅ `loadUserSubscription()` - Charge l'abonnement depuis le backend

---

## 🔧 Configuration Requise

### 1. Créer un compte Stripe

1. Aller sur https://stripe.com
2. Créer un compte (gratuit)
3. Activer le mode test pour commencer

### 2. Obtenir les clés API

1. Dans le Dashboard Stripe → **Developers** → **API keys**
2. Copier :
   - **Publishable key** (commence par `pk_test_...` ou `pk_live_...`)
   - **Secret key** (commence par `sk_test_...` ou `sk_live_...`)

### 3. Configurer les variables d'environnement Lambda

Dans AWS Lambda → Configuration → Variables d'environnement, ajouter :

```
STRIPE_SECRET_KEY=sk_test_... (ou sk_live_... en production)
STRIPE_PUBLIC_KEY=pk_test_... (ou pk_live_... en production)
STRIPE_WEBHOOK_SECRET=whsec_... (voir section Webhooks)
```

**Note** : La clé publique sera renvoyée par le backend lors de la création de la session, mais vous pouvez aussi la mettre dans le frontend directement si vous préférez.

### 4. Créer les produits et prix dans Stripe

Dans Stripe Dashboard → **Products** → **Add product** :

#### Events Explorer (CHF 5.–/mois)
- **Name** : Events Explorer
- **Description** : 10 alertes personnalisées/mois, Agenda 100 places
- **Pricing** : Recurring, CHF 5.00, Monthly
- **Copier le Price ID** (commence par `price_...`)
- Ajouter dans les variables d'environnement : `STRIPE_PRICE_EVENTS_EXPLORER=price_...`

#### Events Alertes Pro (CHF 10.–/mois)
- **Name** : Events Alertes Pro
- **Description** : Alertes illimitées, Agenda 200 places
- **Pricing** : Recurring, CHF 10.00, Monthly
- **Copier le Price ID**
- Ajouter : `STRIPE_PRICE_EVENTS_ALERTS_PRO=price_...`

#### Service Pro (CHF 12.–/mois)
- **Name** : Service Pro
- **Description** : Contacts illimités, Badge Pro
- **Pricing** : Recurring, CHF 12.00, Monthly
- **Copier le Price ID**
- Ajouter : `STRIPE_PRICE_SERVICE_PRO=price_...`

#### Service Ultra (CHF 18.–/mois)
- **Name** : Service Ultra
- **Description** : Tout de Pro + Accès API, 10 events gratuits/mois
- **Pricing** : Recurring, CHF 18.00, Monthly
- **Copier le Price ID**
- Ajouter : `STRIPE_PRICE_SERVICE_ULTRA=price_...`

#### Full Premium (CHF 25.–/mois)
- **Name** : Full Premium
- **Description** : Tout compris - Agenda 250, Alertes illimitées, Contacts illimités
- **Pricing** : Recurring, CHF 25.00, Monthly
- **Copier le Price ID**
- Ajouter : `STRIPE_PRICE_FULL_PREMIUM=price_...`

### 5. Configurer les Webhooks Stripe

#### En développement local (avec Stripe CLI)

1. Installer Stripe CLI : https://stripe.com/docs/stripe-cli
2. Se connecter : `stripe login`
3. Écouter les webhooks : 
   ```bash
   stripe listen --forward-to http://localhost:5005/api/payments/webhook
   ```
4. Copier le **Webhook signing secret** (commence par `whsec_...`)
5. Ajouter dans les variables d'environnement : `STRIPE_WEBHOOK_SECRET=whsec_...`

#### En production (AWS Lambda)

1. Dans Stripe Dashboard → **Developers** → **Webhooks**
2. Cliquer sur **Add endpoint**
3. **Endpoint URL** : `https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/payments/webhook`
4. Sélectionner les événements :
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `payment_intent.succeeded`
5. Copier le **Signing secret** (commence par `whsec_...`)
6. Ajouter dans les variables d'environnement Lambda : `STRIPE_WEBHOOK_SECRET=whsec_...`

### 6. Configurer l'URL du frontend

Dans les variables d'environnement Lambda, ajouter :

```
FRONTEND_URL=https://mapevent.world
```

(ou `http://localhost:8000` en développement)

---

## 🧪 Tester le système

### Mode Test Stripe

Stripe fournit des cartes de test :

- **Succès** : `4242 4242 4242 4242`
- **Échec** : `4000 0000 0000 0002`
- **3D Secure** : `4000 0025 0000 3155`
- **Date d'expiration** : N'importe quelle date future (ex: `12/34`)
- **CVC** : N'importe quel 3 chiffres (ex: `123`)

### Tester un paiement contact

1. Ouvrir le site
2. Se connecter
3. Cliquer sur un booking/service
4. Cliquer sur "Obtenir le contact"
5. Cliquer sur "Payer CHF 1.–"
6. Utiliser la carte de test `4242 4242 4242 4242`
7. Vérifier que le contact est débloqué après retour

### Tester un abonnement

1. Ouvrir le site
2. Se connecter
3. Aller dans "Abonnements"
4. Sélectionner un plan (ex: Events Explorer)
5. Cliquer sur "Payer CHF 5.–/mois"
6. Utiliser la carte de test `4242 4242 4242 4242`
7. Vérifier que l'abonnement est activé après retour

### Tester le panier

1. Ajouter plusieurs contacts au panier
2. Ouvrir le panier
3. Cliquer sur "Payer X CHF"
4. Utiliser la carte de test
5. Vérifier que tous les contacts sont débloqués

---

## 🔒 Sécurité

### Variables d'environnement

⚠️ **NE JAMAIS** :
- Commiter les clés Stripe dans Git
- Exposer la clé secrète (`sk_...`) dans le frontend
- Partager les clés publiquement

✅ **TOUJOURS** :
- Utiliser les variables d'environnement Lambda
- Utiliser des clés de test en développement
- Activer le mode production uniquement quand prêt

### Validation des webhooks

Le backend valide automatiquement la signature des webhooks Stripe pour s'assurer qu'ils viennent bien de Stripe.

---

## 📊 Monitoring

### Dashboard Stripe

- **Payments** : Voir tous les paiements
- **Subscriptions** : Voir tous les abonnements
- **Events** : Voir tous les événements (webhooks, etc.)
- **Logs** : Voir les logs des webhooks

### Base de données

Les paiements et abonnements sont enregistrés dans :
- Table `payments` : Tous les paiements (contacts, paniers, donations)
- Table `subscriptions` : Tous les abonnements actifs/annulés

---

## 🚀 Passage en production

1. **Activer le mode Live dans Stripe**
   - Dashboard → Toggle "Test mode" → "Live mode"

2. **Obtenir les clés Live**
   - Copier les nouvelles clés (commencent par `pk_live_...` et `sk_live_...`)

3. **Mettre à jour les variables d'environnement Lambda**
   - Remplacer toutes les clés de test par les clés live

4. **Créer les produits Live**
   - Créer les mêmes produits dans le mode Live
   - Mettre à jour les Price IDs dans les variables d'environnement

5. **Configurer les webhooks Live**
   - Créer un nouvel endpoint webhook pour la production
   - Copier le nouveau signing secret

6. **Tester avec une vraie carte**
   - Utiliser une vraie carte de test (Stripe fournit des cartes de test même en mode Live)

---

## 🆘 Dépannage

### Erreur "Stripe non disponible"
- Vérifier que Stripe.js est chargé : `typeof Stripe !== 'undefined'`
- Vérifier la console du navigateur pour les erreurs

### Erreur "Stripe price ID not configured"
- Vérifier que les variables d'environnement `STRIPE_PRICE_*` sont configurées
- Vérifier que les Price IDs sont corrects dans Stripe Dashboard

### Webhooks ne fonctionnent pas
- Vérifier que `STRIPE_WEBHOOK_SECRET` est configuré
- Vérifier l'URL du webhook dans Stripe Dashboard
- Vérifier les logs Lambda pour voir les erreurs

### Paiement réussi mais contact non débloqué
- Vérifier que le webhook `checkout.session.completed` est bien configuré
- Vérifier les logs Lambda pour voir si le webhook est reçu
- Vérifier que la table `payments` est mise à jour

---

## 📝 Notes

- Les paiements de contacts (CHF 1.–) sont des paiements uniques
- Les abonnements sont récurrents (mensuels)
- Les webhooks sont essentiels pour mettre à jour la base de données
- Le frontend vérifie le statut du paiement au retour, mais les webhooks sont la source de vérité

---

## 🔗 Ressources

- **Documentation Stripe** : https://stripe.com/docs
- **Stripe Checkout** : https://stripe.com/docs/payments/checkout
- **Stripe Subscriptions** : https://stripe.com/docs/billing/subscriptions/overview
- **Stripe Webhooks** : https://stripe.com/docs/webhooks
- **Stripe Testing** : https://stripe.com/docs/testing



