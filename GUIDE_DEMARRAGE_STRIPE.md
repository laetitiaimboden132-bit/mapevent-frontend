# 🚀 Guide de Démarrage Stripe - Étape par Étape

## 📋 Vue d'ensemble

Ce guide vous accompagne pour configurer Stripe et tester le système de paiement MapEventAI.

**Temps estimé :** 30-45 minutes

---

## ✅ Étape 1 : Créer le Compte Stripe (5 min)

### 1.1 Aller sur Stripe
- Ouvrir : https://stripe.com
- Cliquer sur **"Créer un compte"** ou **"S'inscrire"**

### 1.2 Remplir les Informations
- **Email** : Votre email professionnel
- **Mot de passe** : Créer un mot de passe sécurisé
- **Dénomination sociale** : `MapEventAI` (ou votre nom si particulier)
- **Pays** : Suisse

### 1.3 Choisir les Options
Cocher **UNIQUEMENT** :
- ✅ **Paiements non récurrents**
- ✅ **Paiements récurrents**

**Ne PAS cocher** les autres options pour l'instant.

### 1.4 Vérifier l'Email
- Vérifier votre boîte mail
- Cliquer sur le lien de confirmation

---

## 🔑 Étape 2 : Obtenir les Clés API (2 min)

### 2.1 Accéder au Dashboard
- Une fois connecté, aller dans **Developers** → **API keys**

### 2.2 Copier les Clés
Vous verrez deux clés :

1. **Publishable key** (commence par `pk_test_...`)
   - ✅ Cette clé peut être publique
   - 📋 **COPIER CETTE CLÉ** (vous en aurez besoin)

2. **Secret key** (commence par `sk_test_...`)
   - ⚠️ **NE JAMAIS PARTAGER CETTE CLÉ**
   - 📋 **COPIER CETTE CLÉ** (vous en aurez besoin)

### 2.3 Noter les Clés
**Important :** Notez ces clés dans un endroit sûr (fichier texte, gestionnaire de mots de passe).

```
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

---

## 💰 Étape 3 : Créer les Produits et Prix (10 min)

### 3.1 Aller dans Products
- Dashboard Stripe → **Products** → **Add product**

### 3.2 Créer Events Explorer (CHF 5.–/mois)

1. **Name** : `Events Explorer`
2. **Description** : `10 alertes personnalisées/mois, Agenda 100 places`
3. **Pricing** :
   - Sélectionner **Recurring**
   - **Price** : `5.00`
   - **Currency** : `CHF`
   - **Billing period** : `Monthly`
4. Cliquer sur **Save product**
5. **COPIER LE PRICE ID** (commence par `price_...`)
   - Exemple : `price_1ABC123...`
   - 📋 Noter : `STRIPE_PRICE_EVENTS_EXPLORER=price_1ABC123...`

### 3.3 Créer Events Alertes Pro (CHF 10.–/mois)

1. **Add product** → **Events Alertes Pro**
2. **Description** : `Alertes illimitées, Agenda 200 places`
3. **Pricing** : Recurring, `10.00 CHF`, Monthly
4. **COPIER LE PRICE ID**
   - 📋 Noter : `STRIPE_PRICE_EVENTS_ALERTS_PRO=price_...`

### 3.4 Créer Service Pro (CHF 12.–/mois)

1. **Add product** → **Service Pro**
2. **Description** : `Contacts illimités, Badge Pro`
3. **Pricing** : Recurring, `12.00 CHF`, Monthly
4. **COPIER LE PRICE ID**
   - 📋 Noter : `STRIPE_PRICE_SERVICE_PRO=price_...`

### 3.5 Créer Service Ultra (CHF 18.–/mois)

1. **Add product** → **Service Ultra**
2. **Description** : `Tout de Pro + Accès API, 10 events gratuits/mois`
3. **Pricing** : Recurring, `18.00 CHF`, Monthly
4. **COPIER LE PRICE ID**
   - 📋 Noter : `STRIPE_PRICE_SERVICE_ULTRA=price_...`

### 3.6 Créer Full Premium (CHF 25.–/mois)

1. **Add product** → **Full Premium**
2. **Description** : `Tout compris - Agenda 250, Alertes illimitées`
3. **Pricing** : Recurring, `25.00 CHF`, Monthly
4. **COPIER LE PRICE ID**
   - 📋 Noter : `STRIPE_PRICE_FULL_PREMIUM=price_...`

---

## ⚙️ Étape 4 : Configurer AWS Lambda (10 min)

### 4.1 Aller dans AWS Lambda
- Console AWS → **Lambda** → Votre fonction `mapevent-backend`

### 4.2 Ajouter les Variables d'Environnement
- Configuration → **Environment variables** → **Edit**

### 4.3 Ajouter Toutes les Variables

Cliquer sur **Add environment variable** pour chaque ligne :

```
STRIPE_SECRET_KEY=sk_test_... (votre clé secrète)
STRIPE_PUBLIC_KEY=pk_test_... (votre clé publique)
STRIPE_WEBHOOK_SECRET= (on le configurera à l'étape 5)
STRIPE_PRICE_EVENTS_EXPLORER=price_... (copié à l'étape 3.2)
STRIPE_PRICE_EVENTS_ALERTS_PRO=price_... (copié à l'étape 3.3)
STRIPE_PRICE_SERVICE_PRO=price_... (copié à l'étape 3.4)
STRIPE_PRICE_SERVICE_ULTRA=price_... (copié à l'étape 3.5)
STRIPE_PRICE_FULL_PREMIUM=price_... (copié à l'étape 3.6)
FRONTEND_URL=https://mapevent.world (ou http://localhost:8000 pour test local)
```

### 4.4 Sauvegarder
- Cliquer sur **Save**

---

## 🔔 Étape 5 : Configurer les Webhooks (5 min)

### 5.1 Aller dans Webhooks Stripe
- Dashboard Stripe → **Developers** → **Webhooks** → **Add endpoint**

### 5.2 Configurer l'Endpoint
- **Endpoint URL** : 
  ```
  https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/payments/webhook
  ```
  (Remplacez par votre URL API Gateway si différente)

### 5.3 Sélectionner les Événements
Cocher ces événements :
- ✅ `checkout.session.completed`
- ✅ `customer.subscription.created`
- ✅ `customer.subscription.updated`
- ✅ `customer.subscription.deleted`
- ✅ `payment_intent.succeeded`

### 5.4 Créer l'Endpoint
- Cliquer sur **Add endpoint**

### 5.5 Copier le Signing Secret
- Une fois créé, cliquer sur l'endpoint
- **Signing secret** → **Reveal** → **COPIER** (commence par `whsec_...`)
- 📋 Noter : `STRIPE_WEBHOOK_SECRET=whsec_...`

### 5.6 Ajouter dans Lambda
- Retourner dans AWS Lambda
- Ajouter `STRIPE_WEBHOOK_SECRET=whsec_...` dans les variables d'environnement

---

## 📦 Étape 6 : Mettre à Jour le Package Lambda (5 min)

### 6.1 Vérifier que Stripe est dans requirements.txt
Le fichier `lambda-package/backend/requirements.txt` doit contenir :
```
stripe==7.8.0
```

### 6.2 Créer le Package ZIP
Si vous avez le script PowerShell :
```powershell
.\aws\creer_package_lambda.ps1
```

Sinon, manuellement :
1. Aller dans `lambda-package/`
2. Créer un ZIP de tout le contenu
3. Nommer `lambda-deployment.zip`

### 6.3 Uploader dans Lambda
1. AWS Lambda → Votre fonction → **Code** → **Upload from** → **.zip file**
2. Sélectionner `lambda-deployment.zip`
3. Cliquer sur **Save**

---

## 🧪 Étape 7 : Tester le Système (10 min)

### 7.1 Tester un Paiement Contact

1. **Ouvrir le site** (local ou déployé)
2. **Se connecter** (ou créer un compte)
3. **Cliquer sur un booking ou service**
4. **Cliquer sur "Obtenir le contact"**
5. **Cliquer sur "Payer CHF 1.–"**
6. **Utiliser la carte de test** :
   - Numéro : `4242 4242 4242 4242`
   - Date : `12/34` (n'importe quelle date future)
   - CVC : `123` (n'importe quel 3 chiffres)
   - Nom : N'importe quel nom
7. **Cliquer sur "Pay"**
8. **Vérifier** :
   - ✅ Retour sur le site
   - ✅ Message "Paiement réussi"
   - ✅ Contact débloqué

### 7.2 Tester un Abonnement

1. **Aller dans "Abonnements"** (icône 💎)
2. **Sélectionner un plan** (ex: Events Explorer)
3. **Cliquer sur "Payer CHF 5.–/mois"**
4. **Utiliser la carte de test** : `4242 4242 4242 4242`
5. **Cliquer sur "Pay"**
6. **Vérifier** :
   - ✅ Retour sur le site
   - ✅ Message "Abonnement activé"
   - ✅ Plan affiché comme actif

### 7.3 Vérifier dans Stripe Dashboard

1. **Dashboard Stripe** → **Payments**
2. **Vérifier** que les paiements apparaissent
3. **Dashboard Stripe** → **Subscriptions**
4. **Vérifier** que les abonnements apparaissent

### 7.4 Vérifier dans AWS CloudWatch

1. **AWS Console** → **CloudWatch** → **Log groups** → Votre fonction Lambda
2. **Vérifier** les logs pour voir si les webhooks sont reçus

---

## ✅ Checklist Finale

Avant de passer en production, vérifier :

- [ ] Compte Stripe créé
- [ ] Clés API copiées et configurées dans Lambda
- [ ] 5 produits/prix créés dans Stripe
- [ ] Tous les Price IDs configurés dans Lambda
- [ ] Webhook configuré et Signing Secret ajouté
- [ ] Package Lambda mis à jour avec Stripe
- [ ] Test paiement contact réussi
- [ ] Test abonnement réussi
- [ ] Paiements visibles dans Stripe Dashboard
- [ ] Webhooks reçus (vérifier les logs)

---

## 🐛 Dépannage

### Erreur "Stripe non disponible"
- Vérifier que Stripe.js est chargé (console navigateur)
- Vérifier que la clé publique est correcte

### Erreur "Stripe price ID not configured"
- Vérifier que tous les Price IDs sont dans les variables d'environnement Lambda
- Vérifier que les noms des variables sont exacts

### Webhooks ne fonctionnent pas
- Vérifier l'URL du webhook dans Stripe
- Vérifier que `STRIPE_WEBHOOK_SECRET` est configuré
- Vérifier les logs Lambda pour les erreurs

### Paiement réussi mais contact non débloqué
- Vérifier que le webhook `checkout.session.completed` est configuré
- Vérifier les logs Lambda
- Vérifier la table `payments` dans la base de données

---

## 🎉 Félicitations !

Si tous les tests passent, votre système de paiement est opérationnel ! 🚀

**Prochaines étapes :**
- Tester avec d'autres cartes de test
- Passer en mode Live quand prêt
- Ajouter la marketplace plus tard si besoin

---

## 📞 Besoin d'aide ?

- **Documentation Stripe** : https://stripe.com/docs
- **Support Stripe** : https://support.stripe.com
- **Logs Lambda** : AWS CloudWatch
- **Logs Stripe** : Dashboard → Developers → Events



