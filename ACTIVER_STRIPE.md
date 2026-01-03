# 🔓 Activer votre Compte Stripe pour les Paiements Réels

## ⚠️ Problème Actuel

Si vous avez une **erreur lors du paiement**, c'est probablement parce que votre compte Stripe n'est pas encore **activé** pour recevoir des paiements réels.

## ✅ Solution : Activer le Compte Stripe

### 1. Connectez-vous à Stripe Dashboard

Allez sur : **https://dashboard.stripe.com/login**

### 2. Activez votre Compte

1. **Cliquez sur "Activer votre compte"** (bouton en haut)
2. **Remplissez les informations requises** :
   - ✅ Informations personnelles
   - ✅ Informations business
   - ✅ Numéro de téléphone (vérification)
   - ✅ Adresse
   - ✅ Informations bancaires (IBAN pour recevoir les paiements)

### 3. Vérifiez le Mode

En haut à droite du Dashboard Stripe :
- **Mode TEST** : Pour tester avec des cartes de test
- **Mode LIVE** : Pour recevoir de vrais paiements

### 4. Récupérez vos Clés de Production

Une fois activé, allez dans :
**Developers → API keys**

Vous verrez :
- **Publishable key** : `pk_live_...` (à mettre dans Lambda)
- **Secret key** : `sk_live_...` (à mettre dans Lambda)

## 🔧 Configuration dans AWS Lambda

### Variables d'Environnement à Configurer

Dans AWS Lambda Console → Votre fonction → Configuration → Variables d'environnement :

```
STRIPE_SECRET_KEY=sk_live_VOTRE_CLE_SECRETE
STRIPE_PUBLISHABLE_KEY=pk_live_VOTRE_CLE_PUBLIQUE
```

## 🧪 Tester avec Mode TEST (Recommandé d'abord)

Avant de passer en production, testez en mode TEST :

1. **Dans Stripe Dashboard** : Passer en mode **TEST**
2. **Dans Lambda** : Utiliser les clés `sk_test_...` et `pk_test_...`
3. **Tester avec une carte de test** :
   - Numéro : `4242 4242 4242 4242`
   - Date : N'importe quelle date future
   - CVC : N'importe quel 3 chiffres

## ❌ Erreurs Courantes

### Erreur : "Your account cannot currently make live charges"

**Solution** : Votre compte n'est pas activé. Suivez les étapes ci-dessus.

### Erreur : "Invalid API Key"

**Solution** : 
- Vérifiez que vous utilisez les bonnes clés (test vs live)
- Vérifiez que les clés sont bien dans les variables d'environnement Lambda
- Redéployez votre fonction Lambda après avoir changé les variables

### Erreur : "No such payment_intent"

**Solution** : 
- Vérifiez que votre backend crée bien la session Stripe
- Vérifiez les logs Lambda pour voir l'erreur exacte

## 📋 Checklist Activation

- [ ] Compte Stripe créé et connecté
- [ ] Informations personnelles complétées
- [ ] Informations business complétées
- [ ] Numéro de téléphone vérifié
- [ ] Adresse complétée
- [ ] IBAN bancaire ajouté (pour recevoir les paiements)
- [ ] Compte activé (bouton "Activer" dans le dashboard)
- [ ] Clés de production récupérées (`pk_live_` et `sk_live_`)
- [ ] Clés configurées dans AWS Lambda
- [ ] Test d'un paiement réussi

## 🚀 Après Activation

Une fois votre compte activé :

1. **Testez d'abord en mode TEST** avec une carte de test
2. **Passez en mode LIVE** quand vous êtes prêt
3. **Testez avec un petit montant réel** (CHF 1.–)
4. **Vérifiez dans Stripe Dashboard** que le paiement apparaît

## 💡 Important

- ⚠️ **Mode TEST** : Les paiements ne sont pas réels, utilisez des cartes de test
- ✅ **Mode LIVE** : Les paiements sont réels, vous recevez vraiment l'argent
- 🔒 **Sécurité** : Ne partagez JAMAIS votre clé secrète (`sk_live_`)

## 📞 Support

Si vous avez des problèmes :
- **Stripe Support** : https://support.stripe.com
- **Documentation** : https://stripe.com/docs

---

**Une fois activé, vos paiements fonctionneront ! 🎉**

