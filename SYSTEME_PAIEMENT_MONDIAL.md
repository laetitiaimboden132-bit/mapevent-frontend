# 💳 Système de Paiement Mondial - État Actuel & Plan

## ⚠️ État Actuel

### ✅ Ce qui existe (simulé)
1. **Frontend** :
   - `openPaymentModal()` - Modal pour acheter des contacts
   - `simulatePayment()` - Simulation de paiement contact
   - `checkoutCart()` - Simulation de checkout panier
   - `openPremiumPaymentModal()` - Modal pour abonnements
   - `simulatePremiumPayment()` - Simulation de paiement abonnement
   - Panier fonctionnel (ajout, retrait, affichage)

2. **UI/UX** :
   - Modals de paiement bien conçues
   - Affichage des prix en CHF
   - Son de paiement (`popopo.m4a`)
   - Gestion du panier

### ❌ Ce qui manque (réel)
1. **Intégration Stripe** :
   - Pas de SDK Stripe.js
   - Pas de création de sessions de paiement
   - Pas de gestion des webhooks

2. **Backend** :
   - Pas d'endpoints `/api/payments/*`
   - Pas de gestion des abonnements récurrents
   - Pas de stockage des transactions

3. **Méthodes de paiement** :
   - Carte bancaire (via Stripe)
   - Twint (via Stripe - Suisse)
   - PayPal (optionnel)
   - Autres méthodes locales selon région

4. **Sécurité** :
   - Pas de validation côté serveur
   - Pas de gestion des webhooks sécurisés
   - Pas de stockage sécurisé des informations de paiement

---

## 🎯 Plan d'Implémentation

### Phase 1 : Intégration Stripe (Priorité Haute)

#### 1.1 Frontend - Stripe.js
```javascript
// Ajouter dans map_logic.js
const STRIPE_PUBLIC_KEY = "pk_live_..."; // Clé publique Stripe

// Charger Stripe.js
const stripe = Stripe(STRIPE_PUBLIC_KEY);
```

#### 1.2 Backend - Endpoints de paiement
```python
# backend/main.py

@app.route('/api/payments/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """
    Crée une session Stripe Checkout pour :
    - Achat de contact (one-time)
    - Abonnement (recurring)
    """
    pass

@app.route('/api/payments/webhook', methods=['POST'])
def stripe_webhook():
    """
    Gère les webhooks Stripe :
    - payment_intent.succeeded
    - customer.subscription.created
    - customer.subscription.updated
    - customer.subscription.deleted
    """
    pass

@app.route('/api/payments/subscription-status', methods=['GET'])
def get_subscription_status():
    """Récupère le statut de l'abonnement d'un utilisateur"""
    pass
```

#### 1.3 Base de données
```sql
-- Tables à créer dans schema.sql

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    stripe_customer_id VARCHAR(255),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CHF',
    status VARCHAR(50) NOT NULL, -- pending, succeeded, failed, refunded
    payment_type VARCHAR(50) NOT NULL, -- contact, subscription, donation
    item_type VARCHAR(50), -- booking, service, subscription_plan
    item_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    stripe_subscription_id VARCHAR(255) UNIQUE NOT NULL,
    plan VARCHAR(50) NOT NULL, -- events-explorer, events-alerts-pro, etc.
    status VARCHAR(50) NOT NULL, -- active, canceled, past_due
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_stripe_payment_intent_id ON payments(stripe_payment_intent_id);
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_stripe_subscription_id ON subscriptions(stripe_subscription_id);
```

---

### Phase 2 : Remplacement des fonctions simulées

#### 2.1 `simulatePayment()` → `processContactPayment()`
```javascript
async function processContactPayment(type, id) {
  try {
    // Créer une session Stripe Checkout
    const response = await fetch(`${API_BASE_URL}/api/payments/create-checkout-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId: currentUser.id,
        paymentType: 'contact',
        itemType: type,
        itemId: id,
        amount: 1.00, // CHF 1.–
        currency: 'CHF'
      })
    });
    
    const { sessionId } = await response.json();
    
    // Rediriger vers Stripe Checkout
    const result = await stripe.redirectToCheckout({ sessionId });
    
    if (result.error) {
      showNotification(`❌ Erreur : ${result.error.message}`, "error");
    }
  } catch (error) {
    console.error('Erreur paiement:', error);
    showNotification("❌ Erreur lors du paiement", "error");
  }
}
```

#### 2.2 `simulatePremiumPayment()` → `processSubscriptionPayment()`
```javascript
async function processSubscriptionPayment(plan, price) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/payments/create-checkout-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId: currentUser.id,
        paymentType: 'subscription',
        plan: plan,
        amount: price,
        currency: 'CHF'
      })
    });
    
    const { sessionId } = await response.json();
    const result = await stripe.redirectToCheckout({ sessionId });
    
    if (result.error) {
      showNotification(`❌ Erreur : ${result.error.message}`, "error");
    }
  } catch (error) {
    console.error('Erreur abonnement:', error);
    showNotification("❌ Erreur lors de l'abonnement", "error");
  }
}
```

#### 2.3 `checkoutCart()` → `processCartCheckout()`
```javascript
async function processCartCheckout() {
  if (cart.length === 0) return;
  
  const total = cart.reduce((sum, item) => sum + item.price, 0);
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/payments/create-checkout-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId: currentUser.id,
        paymentType: 'cart',
        items: cart.map(item => ({
          type: item.type,
          id: item.id,
          price: item.price
        })),
        amount: total,
        currency: 'CHF'
      })
    });
    
    const { sessionId } = await response.json();
    const result = await stripe.redirectToCheckout({ sessionId });
    
    if (result.error) {
      showNotification(`❌ Erreur : ${result.error.message}`, "error");
    }
  } catch (error) {
    console.error('Erreur checkout:', error);
    showNotification("❌ Erreur lors du paiement", "error");
  }
}
```

---

### Phase 3 : Gestion des retours Stripe

#### 3.1 Page de succès
```javascript
// Vérifier l'URL après retour de Stripe
if (window.location.search.includes('session_id=')) {
  const sessionId = new URLSearchParams(window.location.search).get('session_id');
  
  // Vérifier le statut du paiement
  const response = await fetch(`${API_BASE_URL}/api/payments/verify-session?session_id=${sessionId}`);
  const { success, paymentType, items } = await response.json();
  
  if (success) {
    if (paymentType === 'contact' || paymentType === 'cart') {
      // Débloquer les contacts
      items.forEach(item => {
        const key = `${item.type}:${item.id}`;
        if (!paidContacts.includes(key)) {
          paidContacts.push(key);
        }
      });
      showNotification("✅ Paiement réussi ! Contacts débloqués.", "success");
    } else if (paymentType === 'subscription') {
      // Mettre à jour l'abonnement
      await loadUserSubscription();
      showNotification("✅ Abonnement activé !", "success");
    }
  }
}
```

#### 3.2 Chargement de l'abonnement
```javascript
async function loadUserSubscription() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/payments/subscription-status?userId=${currentUser.id}`);
    const { subscription, status } = await response.json();
    
    if (subscription) {
      currentUser.subscription = subscription.plan;
      currentUser.agendaLimit = getAgendaLimit();
      currentUser.alertLimit = getAlertLimit();
      updateSubscriptionBadge();
    }
  } catch (error) {
    console.error('Erreur chargement abonnement:', error);
  }
}
```

---

### Phase 4 : Support Multi-Méthodes de Paiement

#### 4.1 Configuration par région
```javascript
const PAYMENT_METHODS = {
  'CH': ['card', 'twint'], // Suisse : Carte + Twint
  'EU': ['card', 'sepa_debit'], // Europe : Carte + Prélèvement SEPA
  'US': ['card', 'us_bank_account'], // USA : Carte + Compte bancaire
  'GB': ['card'], // UK : Carte uniquement
  'default': ['card'] // Par défaut : Carte uniquement
};

function getPaymentMethods() {
  // Détecter la région de l'utilisateur
  const region = detectUserRegion(); // À implémenter
  return PAYMENT_METHODS[region] || PAYMENT_METHODS['default'];
}
```

#### 4.2 Modal de sélection de méthode
```javascript
function openPaymentMethodModal(type, id, action) {
  const methods = getPaymentMethods();
  
  const html = `
    <div style="padding:10px;">
      <h2>Choisissez votre méthode de paiement</h2>
      ${methods.map(method => `
        <button onclick="selectPaymentMethod('${method}', '${type}', ${id})">
          ${getPaymentMethodIcon(method)} ${getPaymentMethodName(method)}
        </button>
      `).join('')}
    </div>
  `;
  // ...
}
```

---

### Phase 5 : Sécurité & Conformité

#### 5.1 Validation côté serveur
- Vérifier que l'utilisateur est authentifié
- Vérifier que l'item existe et est disponible
- Vérifier les prix (ne jamais faire confiance au frontend)
- Valider les webhooks Stripe (signature)

#### 5.2 Conformité PCI-DSS
- Stripe gère la conformité PCI-DSS
- Ne jamais stocker les numéros de carte
- Utiliser Stripe Elements pour les formulaires de carte (si nécessaire)

#### 5.3 Gestion des erreurs
- Gérer les paiements échoués
- Gérer les abonnements en retard
- Notifier l'utilisateur en cas de problème

---

## 📋 Checklist d'Implémentation

### Backend
- [ ] Installer `stripe` Python package
- [ ] Créer les tables `payments` et `subscriptions`
- [ ] Implémenter `/api/payments/create-checkout-session`
- [ ] Implémenter `/api/payments/webhook`
- [ ] Implémenter `/api/payments/subscription-status`
- [ ] Implémenter `/api/payments/verify-session`
- [ ] Configurer les webhooks Stripe dans le dashboard
- [ ] Tester les webhooks en local (Stripe CLI)

### Frontend
- [ ] Ajouter Stripe.js (`<script src="https://js.stripe.com/v3/"></script>`)
- [ ] Remplacer `simulatePayment()` par `processContactPayment()`
- [ ] Remplacer `simulatePremiumPayment()` par `processSubscriptionPayment()`
- [ ] Remplacer `checkoutCart()` par `processCartCheckout()`
- [ ] Ajouter la gestion du retour Stripe (page succès)
- [ ] Ajouter `loadUserSubscription()` au login
- [ ] Tester tous les flux de paiement

### Configuration
- [ ] Créer un compte Stripe
- [ ] Obtenir les clés API (test + production)
- [ ] Configurer les produits/prix dans Stripe Dashboard
- [ ] Configurer les webhooks Stripe
- [ ] Tester en mode test avec cartes de test

---

## 💰 Prix des Plans (à configurer dans Stripe)

| Plan | Prix/mois | Stripe Product ID |
|------|-----------|-------------------|
| Events Explorer | CHF 5.– | `prod_events_explorer` |
| Events Alertes Pro | CHF 10.– | `prod_events_alerts_pro` |
| Service Pro | CHF 12.– | `prod_service_pro` |
| Service Ultra | CHF 18.– | `prod_service_ultra` |
| Full Premium | CHF 25.– | `prod_full_premium` |

---

## 🔗 Ressources

- **Stripe Documentation** : https://stripe.com/docs
- **Stripe Checkout** : https://stripe.com/docs/payments/checkout
- **Stripe Subscriptions** : https://stripe.com/docs/billing/subscriptions/overview
- **Stripe Webhooks** : https://stripe.com/docs/webhooks
- **Stripe Testing** : https://stripe.com/docs/testing

---

## ⚠️ Notes Importantes

1. **Mode Test** : Utiliser les clés de test (`pk_test_...`, `sk_test_...`) pendant le développement
2. **Webhooks** : Utiliser Stripe CLI pour tester les webhooks en local : `stripe listen --forward-to localhost:5005/api/payments/webhook`
3. **Sécurité** : Ne jamais exposer la clé secrète Stripe (`sk_...`) dans le frontend
4. **Conformité** : Stripe gère la conformité PCI-DSS, mais il faut respecter les règles de sécurité
5. **70% Mission Planète** : Implémenter la logique de don automatique après chaque paiement réussi

---

## 🚀 Prochaines Étapes

1. **Créer un compte Stripe** (si pas déjà fait)
2. **Installer Stripe Python** : `pip install stripe`
3. **Créer les tables de base de données**
4. **Implémenter les endpoints backend**
5. **Intégrer Stripe.js dans le frontend**
6. **Tester en mode test**
7. **Configurer les webhooks**
8. **Passer en production**



