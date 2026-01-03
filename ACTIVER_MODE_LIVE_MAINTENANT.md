# 🚀 Activer le Mode LIVE Maintenant - Guide Complet

## ✅ Excellente Idée !

Activer le mode LIVE maintenant permet de :
- ✅ Tout configurer une fois pour toutes
- ✅ Ne plus avoir à y revenir plus tard
- ✅ Avoir les vraies clés dès le début
- ✅ Tester directement avec les vraies clés

---

## 🔄 Étape 1 : Activer le Mode LIVE dans Stripe

### 1.1 Aller dans Stripe
- Ouvrir votre compte Stripe
- En haut à droite, vous voyez un toggle **"Mode test"** / **"Mode live"**

### 1.2 Activer le Mode LIVE
- Cliquer sur le toggle pour passer en **"Mode live"**
- Stripe va vous demander de compléter les informations

---

## 📝 Étape 2 : Compléter les Informations Requises

Stripe va vous demander plusieurs informations :

### 2.1 Informations de Base
- ✅ **Dénomination sociale** : `MapEventAI` (ou votre nom d'entreprise)
- ✅ **Email** : Votre email professionnel
- ✅ **Téléphone** : Votre numéro
- ✅ **Adresse complète** : Rue, numéro, code postal, ville, pays

### 2.2 Informations Bancaires
- ✅ **IBAN** : Votre numéro de compte bancaire (pour recevoir les paiements)
- ✅ **Nom du titulaire** : Nom exact sur le compte bancaire
- ✅ **Banque** : Nom de votre banque

### 2.3 Informations Fiscales (Suisse)
- ✅ **Numéro TVA** : Si vous en avez un (sinon laissez vide)
- ✅ **Type d'entreprise** :
  - Particulier / Auto-entrepreneur
  - Sàrl (Société à responsabilité limitée)
  - SA (Société anonyme)
  - Association
  - Autre

### 2.4 Informations sur l'Activité
- ✅ **Description** : "Plateforme événementielle en ligne - MapEventAI"
- ✅ **Site web** : `https://mapevent.world` (ou votre site)
- ✅ **Catégorie** : "Services en ligne" ou "Plateforme événementielle"

### 2.5 Documents à Fournir
Stripe peut demander :
- ✅ **Pièce d'identité** : Passeport ou carte d'identité
- ✅ **Justificatif d'adresse** : Facture, relevé bancaire, etc.
- ✅ **Preuve d'entreprise** : Si vous avez une entreprise enregistrée

---

## 🔑 Étape 3 : Obtenir les Nouvelles Clés LIVE

### 3.1 Une Fois le Mode LIVE Activé
- Aller dans **Développeurs** → **Clés API**
- Vous verrez maintenant **2 sections** :
  - **Clés de test** (pour tester)
  - **Clés en direct** (pour la production)

### 3.2 Copier les Clés LIVE
1. Dans la section **"Clés en direct"** :
   - **Clé publiable** : `pk_live_...` (COPIER)
   - **Clé secrète** : `sk_live_...` (Cliquer sur "Révéler" puis COPIER)

2. 📋 Noter ces clés (elles remplaceront les clés de test)

---

## ⚙️ Étape 4 : Mettre à Jour AWS Lambda

### 4.1 Remplacer les Clés dans Lambda
- AWS Lambda → Votre fonction → **Configuration** → **Variables d'environnement**

### 4.2 Modifier les Variables
Remplacer les valeurs existantes :

**Anciennes (TEST) :**
```
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
```

**Nouvelles (LIVE) :**
```
STRIPE_SECRET_KEY=sk_live_... (votre nouvelle clé LIVE)
STRIPE_PUBLIC_KEY=pk_live_... (votre nouvelle clé LIVE)
```

### 4.3 Sauvegarder
- Cliquer sur **Enregistrer**

---

## 💰 Étape 5 : Créer les Produits en Mode LIVE

### 5.1 Vérifier que Vous Êtes en Mode LIVE
- En haut à droite dans Stripe, vous devez voir **"Mode live"**

### 5.2 Créer les 5 Produits
Créer les mêmes produits qu'en mode TEST, mais cette fois en mode LIVE :

1. **Events Explorer** - CHF 5.–/mois
2. **Events Alertes Pro** - CHF 10.–/mois
3. **Service Pro** - CHF 12.–/mois
4. **Service Ultra** - CHF 18.–/mois
5. **Full Premium** - CHF 25.–/mois

### 5.3 Copier les Nouveaux ID de Prix
- **COPIER LES ID DE PRIX** (ils seront différents des prix de test)
- Ils commencent toujours par `price_...`

### 5.4 Mettre à Jour Lambda
Ajouter/mettre à jour dans Lambda :
```
STRIPE_PRICE_EVENTS_EXPLORER=price_... (nouveau ID LIVE)
STRIPE_PRICE_EVENTS_ALERTS_PRO=price_... (nouveau ID LIVE)
STRIPE_PRICE_SERVICE_PRO=price_... (nouveau ID LIVE)
STRIPE_PRICE_SERVICE_ULTRA=price_... (nouveau ID LIVE)
STRIPE_PRICE_FULL_PREMIUM=price_... (nouveau ID LIVE)
```

---

## 🔔 Étape 6 : Configurer les Webhooks en Mode LIVE

### 6.1 Créer le Webhook LIVE
- **Développeurs** → **Webhooks** → **Ajouter un point de terminaison**

### 6.2 Configurer
- **URL** : `https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api/payments/webhook`
- **Événements** : Les mêmes qu'en mode TEST
- **Créer**

### 6.3 Copier le Nouveau Secret
- **Secret de signature** → **Révéler** → **COPIER** (`whsec_...`)
- C'est différent du secret de test

### 6.4 Mettre à Jour Lambda
```
STRIPE_WEBHOOK_SECRET=whsec_... (nouveau secret LIVE)
```

---

## ⚠️ Important : Vérification Stripe

### Processus de Vérification
Après avoir activé le mode LIVE, Stripe va :
1. **Vérifier vos informations** (peut prendre 1-3 jours)
2. **Vérifier votre identité** (si demandé)
3. **Vérifier votre compte bancaire** (test de micro-dépôt)

### Pendant la Vérification
- ✅ Vous pouvez toujours utiliser le mode TEST
- ✅ Vous pouvez créer les produits/prix
- ✅ Vous pouvez configurer Lambda
- ⚠️ Les paiements LIVE peuvent être bloqués jusqu'à vérification

### Une Fois Vérifié
- ✅ Vous recevrez un email de confirmation
- ✅ Les paiements LIVE fonctionneront
- ✅ Vous pourrez recevoir de l'argent réel

---

## 🧪 Étape 7 : Tester (Optionnel)

### 7.1 Tester avec une Carte Réelle
⚠️ **ATTENTION** : En mode LIVE, les paiements sont RÉELS !

Pour tester sans risque :
- Utiliser une carte avec un petit montant (ex: CHF 1.–)
- Ou tester d'abord en mode TEST, puis passer en LIVE

### 7.2 Vérifier dans Stripe
- **Paiements** → Vérifier que les paiements apparaissent
- **Abonnements** → Vérifier que les abonnements apparaissent

---

## 📋 Checklist Complète

### Configuration Stripe
- [ ] Mode LIVE activé
- [ ] Toutes les informations complétées
- [ ] Documents fournis (si demandés)
- [ ] Compte bancaire configuré
- [ ] Clés LIVE copiées

### Configuration Lambda
- [ ] `STRIPE_SECRET_KEY` = clé LIVE (`sk_live_...`)
- [ ] `STRIPE_PUBLIC_KEY` = clé LIVE (`pk_live_...`)
- [ ] `STRIPE_WEBHOOK_SECRET` = secret LIVE (`whsec_...`)
- [ ] Tous les Price IDs LIVE configurés
- [ ] Variables sauvegardées

### Produits Stripe
- [ ] 5 produits créés en mode LIVE
- [ ] Tous les ID de prix copiés
- [ ] Tous les ID de prix dans Lambda

### Webhooks
- [ ] Webhook LIVE créé
- [ ] Secret de signature copié
- [ ] Secret dans Lambda

### Vérification
- [ ] Compte Stripe vérifié (peut prendre quelques jours)
- [ ] Test d'un paiement (optionnel, avec vraie carte)

---

## 🎯 Avantages d'Activer Maintenant

✅ **Tout configuré une fois pour toutes**
- Plus besoin de changer les clés plus tard
- Plus besoin de recréer les produits
- Tout est prêt pour la production

✅ **Pas de double travail**
- Pas besoin de configurer TEST puis LIVE
- Une seule configuration

✅ **Prêt pour le lancement**
- Dès que le site est prêt, les paiements fonctionnent
- Pas de transition à faire

---

## ⚠️ Points d'Attention

### Vérification Peut Prendre du Temps
- Stripe peut prendre 1-3 jours pour vérifier
- Pendant ce temps, certains paiements peuvent être bloqués
- Vous pouvez toujours utiliser le mode TEST en parallèle

### Paiements RÉELS
- En mode LIVE, les paiements sont RÉELS
- Testez avec précaution
- Utilisez de petits montants pour tester

### Frais Stripe
- Stripe prend des frais sur chaque paiement (2.9% + CHF 0.30)
- Les frais sont déduits automatiquement
- Vous recevez le montant net

---

## 🚀 Résumé : Actions à Faire

1. ✅ **Activer le mode LIVE** dans Stripe
2. ✅ **Compléter toutes les informations** demandées
3. ✅ **Fournir les documents** si demandés
4. ✅ **Obtenir les clés LIVE** (`pk_live_...` et `sk_live_...`)
5. ✅ **Créer les 5 produits** en mode LIVE
6. ✅ **Copier les ID de prix** LIVE
7. ✅ **Mettre à jour Lambda** avec les clés et prix LIVE
8. ✅ **Configurer le webhook** LIVE
9. ✅ **Attendre la vérification** Stripe (1-3 jours)
10. ✅ **Tester** (avec précaution, vrais paiements)

---

## 💡 Astuce

**Pendant la vérification :**
- Vous pouvez garder le mode TEST actif aussi
- Tester en mode TEST pendant que Stripe vérifie
- Une fois vérifié, tout fonctionnera en LIVE

**Double configuration :**
- Certains gardent TEST et LIVE configurés
- TEST pour développer, LIVE pour production
- Vous pouvez faire pareil si vous voulez

---

## ✅ Conclusion

**Oui, activer le mode LIVE maintenant est une excellente idée !**

Cela permet de :
- ✅ Tout configurer une fois
- ✅ Être prêt pour la production
- ✅ Ne plus avoir à y revenir

**Suivez simplement les étapes ci-dessus et tout sera configuré !** 🚀



