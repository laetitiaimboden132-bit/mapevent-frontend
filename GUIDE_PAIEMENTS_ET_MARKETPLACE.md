# 💳 Guide : Paiements Non-Récurrents, Récurrents & Marketplace

## 📊 Types de Paiements dans MapEventAI

### 1. Paiements Non-Récurrents (One-Time Payments)

**Utilisés pour :**
- ✅ Achat de contact (booking/service) : CHF 1.–
- ✅ Panier (plusieurs contacts) : CHF X.–
- ✅ Donations Mission Planète : Montant libre

**Caractéristiques :**
- Paiement unique, non répété
- Déblocage immédiat après paiement
- Pas d'abonnement

**Dans notre code :**
```python
# Backend : mode='payment' dans create_checkout_session
session = stripe.checkout.Session.create(
    mode='payment',  # ← Paiement unique
    line_items=[...],
    ...
)
```

**Frontend :**
- `processContactPayment()` - Achat d'un contact
- `processCartCheckout()` - Paiement du panier

---

### 2. Paiements Récurrents (Subscriptions)

**Utilisés pour :**
- ✅ Events Explorer : CHF 5.–/mois
- ✅ Events Alertes Pro : CHF 10.–/mois
- ✅ Service Pro : CHF 12.–/mois
- ✅ Service Ultra : CHF 18.–/mois
- ✅ Full Premium : CHF 25.–/mois

**Caractéristiques :**
- Paiement automatique chaque mois
- Renouvellement automatique
- Peut être annulé à tout moment
- Accès aux fonctionnalités pendant la durée de l'abonnement

**Dans notre code :**
```python
# Backend : mode='subscription' dans create_checkout_session
session = stripe.checkout.Session.create(
    mode='subscription',  # ← Abonnement récurrent
    line_items=[{
        'price': price_id,  # ← Price ID d'un produit récurrent
        'quantity': 1
    }],
    ...
)
```

**Frontend :**
- `processSubscriptionPayment()` - Achat d'un abonnement

---

## 🏪 Marketplace : Qu'est-ce que c'est ?

Une **marketplace** est une plateforme où plusieurs vendeurs peuvent vendre leurs produits/services, et la plateforme prend une commission sur chaque transaction.

### Exemple : MapEventAI en Marketplace

**Scénario actuel :**
- MapEventAI vend directement les contacts (CHF 1.–)
- MapEventAI vend directement les abonnements

**Scénario Marketplace :**
- Les organisateurs d'événements peuvent vendre leurs événements
- Les artistes peuvent vendre leurs services directement
- MapEventAI prend une commission (ex: 10-20%) sur chaque vente
- Les vendeurs reçoivent le reste directement sur leur compte Stripe

---

## 🔧 Implémentation Marketplace avec Stripe Connect

### Architecture Marketplace

```
Utilisateur → MapEventAI → Stripe Connect → Vendeur
              (commission)    (paiement)
```

### 1. Stripe Connect : Deux Modèles

#### A. Stripe Connect "Standard" (Recommandé pour commencer)
- Les vendeurs créent leur compte Stripe
- MapEventAI crée un "Connect Account" pour chaque vendeur
- Les paiements vont directement au vendeur
- MapEventAI prend une commission via "Application Fee"

#### B. Stripe Connect "Express" (Plus simple)
- Les vendeurs s'inscrivent via MapEventAI
- Stripe gère les comptes automatiquement
- Interface simplifiée pour les vendeurs

---

## 🚀 Implémentation Marketplace pour MapEventAI

### Scénario : Organisateurs vendent leurs événements

**Exemple :**
- Un organisateur crée un événement payant (CHF 20.–)
- MapEventAI prend 15% de commission (CHF 3.–)
- L'organisateur reçoit CHF 17.–

### Étapes d'implémentation

#### 1. Backend : Créer un compte Connect pour le vendeur

```python
# Nouvel endpoint : /api/marketplace/create-connect-account
@app.route('/api/marketplace/create-connect-account', methods=['POST'])
def create_connect_account():
    """Crée un compte Stripe Connect pour un vendeur."""
    try:
        data = request.get_json()
        user_id = data.get('userId')
        email = data.get('email')
        
        # Créer un compte Connect Express
        account = stripe.Account.create(
            type='express',
            country='CH',  # Suisse
            email=email,
            capabilities={
                'card_payments': {'requested': True},
                'transfers': {'requested': True},
            },
        )
        
        # Enregistrer le compte_id dans la base de données
        # (créer une table user_stripe_accounts)
        
        # Créer un lien d'onboarding pour le vendeur
        account_link = stripe.AccountLink.create(
            account=account.id,
            refresh_url=f"{FRONTEND_URL}/marketplace/onboarding/refresh",
            return_url=f"{FRONTEND_URL}/marketplace/onboarding/success",
            type='account_onboarding',
        )
        
        return jsonify({
            'accountId': account.id,
            'onboardingUrl': account_link.url
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur create_connect_account: {e}")
        return jsonify({'error': str(e)}), 500
```

#### 2. Backend : Créer un paiement avec commission

```python
# Modifier /api/payments/create-checkout-session pour marketplace
@app.route('/api/payments/create-checkout-session', methods=['POST'])
def create_checkout_session():
    # ... code existant ...
    
    # Si c'est un paiement marketplace (vendeur)
    if data.get('isMarketplace') and data.get('sellerAccountId'):
        seller_account_id = data.get('sellerAccountId')
        commission_percent = 15  # 15% de commission
        
        # Calculer la commission
        total_amount = amount
        commission = int(total_amount * commission_percent / 100)
        seller_amount = total_amount - commission
        
        # Créer le paiement avec Application Fee
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[...],
            mode='payment',
            payment_intent_data={
                'application_fee_amount': commission * 100,  # En centimes
                'on_behalf_of': seller_account_id,
                'transfer_data': {
                    'destination': seller_account_id,
                },
            },
            ...
        )
```

#### 3. Base de données : Table pour les comptes vendeurs

```sql
-- Table pour les comptes Stripe Connect des vendeurs
CREATE TABLE IF NOT EXISTS user_stripe_accounts (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL UNIQUE,
    stripe_account_id VARCHAR(255) UNIQUE NOT NULL,
    account_type VARCHAR(50) DEFAULT 'express', -- express, standard
    status VARCHAR(50) DEFAULT 'pending', -- pending, active, restricted
    onboarding_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_user_stripe_accounts_user ON user_stripe_accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_user_stripe_accounts_stripe ON user_stripe_accounts(stripe_account_id);
```

#### 4. Frontend : Interface pour devenir vendeur

```javascript
// Nouvelle fonction : Devenir vendeur
async function becomeSeller() {
  if (!currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}/marketplace/create-connect-account`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId: currentUser.id.toString(),
        email: currentUser.email
      })
    });
    
    const { onboardingUrl } = await response.json();
    
    // Rediriger vers Stripe pour compléter l'onboarding
    window.location.href = onboardingUrl;
  } catch (error) {
    showNotification(`❌ Erreur : ${error.message}`, "error");
  }
}
```

---

## 💰 Gestion des Commissions

### Options de Commission

1. **Commission fixe** : CHF 1.– par transaction
2. **Commission pourcentage** : 15% de chaque transaction
3. **Commission variable** : Selon le type de vente

### Exemple : Événement payant

```
Prix événement : CHF 50.–
Commission MapEventAI (15%) : CHF 7.50
Vendeur reçoit : CHF 42.50
```

### Paiement au vendeur

- **Automatique** : Stripe transfère automatiquement au vendeur
- **Délai** : Généralement 2-7 jours ouvrables
- **Frais Stripe** : Déduits automatiquement (ex: 2.9% + CHF 0.30)

---

## 📋 Checklist Marketplace

### Phase 1 : Préparation
- [ ] Activer Stripe Connect dans le Dashboard Stripe
- [ ] Choisir le modèle (Standard ou Express)
- [ ] Définir la structure de commission
- [ ] Créer la table `user_stripe_accounts`

### Phase 2 : Backend
- [ ] Endpoint `/api/marketplace/create-connect-account`
- [ ] Endpoint `/api/marketplace/get-account-status`
- [ ] Modifier `/api/payments/create-checkout-session` pour marketplace
- [ ] Webhook pour `account.updated` (statut du compte)

### Phase 3 : Frontend
- [ ] Interface "Devenir vendeur"
- [ ] Page d'onboarding Stripe
- [ ] Dashboard vendeur (ventes, revenus)
- [ ] Modifier les popups pour permettre la vente d'événements

### Phase 4 : Tests
- [ ] Tester la création de compte Connect
- [ ] Tester un paiement avec commission
- [ ] Vérifier que le vendeur reçoit bien son paiement
- [ ] Tester les webhooks

---

## 🎯 Cas d'Usage MapEventAI

### 1. Événements Payants
- Organisateur crée un événement payant (CHF 20.–)
- MapEventAI prend 15% (CHF 3.–)
- Organisateur reçoit CHF 17.–

### 2. Services Premium
- Artiste propose un service premium (CHF 50.–)
- MapEventAI prend 20% (CHF 10.–)
- Artiste reçoit CHF 40.–

### 3. Abonnements Organisateurs
- Organisateur vend un abonnement à ses événements (CHF 10.–/mois)
- MapEventAI prend 15% (CHF 1.50/mois)
- Organisateur reçoit CHF 8.50/mois

---

## ⚠️ Important

### Avant de créer une marketplace

1. **Vérifier les réglementations**
   - Conformité fiscale (Suisse)
   - Obligations de déclaration
   - TVA si applicable

2. **Stripe Connect nécessite**
   - Compte Stripe vérifié
   - Informations bancaires complètes
   - Politique de confidentialité
   - Conditions générales de vente

3. **Gestion des litiges**
   - Politique de remboursement
   - Support client
   - Résolution des conflits

---

## 🔗 Ressources

- **Stripe Connect** : https://stripe.com/docs/connect
- **Stripe Connect Express** : https://stripe.com/docs/connect/express-accounts
- **Application Fees** : https://stripe.com/docs/connect/charges#application-fee
- **Marketplace Guide** : https://stripe.com/docs/connect/overview

---

## 💡 Recommandation

**Pour commencer :**
1. ✅ Garder le système actuel (paiements directs)
2. ✅ Tester les paiements non-récurrents et récurrents
3. ✅ Une fois stable, ajouter Stripe Connect pour marketplace
4. ✅ Commencer avec quelques vendeurs de test

**Avantages d'attendre :**
- Système plus stable
- Meilleure compréhension des besoins
- Moins de complexité au démarrage



