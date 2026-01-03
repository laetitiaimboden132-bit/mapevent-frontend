# 🔑 Clé d'Accès Stripe - Quelle Clé Donner ?

## ❓ Question

Stripe demande une "clé d'accès" - quelle clé donner ?

## ✅ Réponse

**OUI, vous donnez la MÊME clé secrète que vous avez mise dans Lambda !**

## 🔑 Les Deux Types de Clés Stripe

### 1. Clé Publique (Publishable Key)
- Commence par : `pk_test_...` ou `pk_live_...`
- ✅ **Peut être exposée** dans le frontend
- ✅ **Sécurisée** à partager publiquement
- ❌ **Ne fonctionne PAS** pour les opérations serveur

### 2. Clé Secrète (Secret Key) ⭐
- Commence par : `sk_test_...` ou `sk_live_...`
- ❌ **NE JAMAIS exposer** publiquement
- ✅ **Utilisée dans le backend** (Lambda)
- ✅ **C'est celle que Stripe demande** pour les opérations serveur

## 📋 Où Trouver vos Clés

1. **Connectez-vous à Stripe Dashboard** : https://dashboard.stripe.com
2. **Allez dans** : **Developers** → **API keys**
3. **Vous verrez** :
   - **Publishable key** : `pk_test_...` ou `pk_live_...`
   - **Secret key** : `sk_test_...` ou `sk_live_...` (cliquez sur "Reveal" pour la voir)

## 🔧 Configuration

### Dans AWS Lambda (Backend)
```
STRIPE_SECRET_KEY=sk_live_VOTRE_CLE_SECRETE
STRIPE_PUBLISHABLE_KEY=pk_live_VOTRE_CLE_PUBLIQUE
```

### Quand Stripe Demande une Clé d'Accès
**Donnez la clé SECRÈTE** (`sk_live_...` ou `sk_test_...`)

C'est la même que celle dans Lambda !

## ⚠️ Important

### Sécurité
- ✅ **Clé Publique** (`pk_...`) : Peut être dans le frontend
- ❌ **Clé Secrète** (`sk_...`) : 
  - Uniquement dans le backend (Lambda)
  - Ne JAMAIS dans le code frontend
  - Ne JAMAIS dans Git
  - Ne JAMAIS partager publiquement

### Mode TEST vs PRODUCTION
- **Mode TEST** : Utilisez `sk_test_...` et `pk_test_...`
- **Mode PRODUCTION** : Utilisez `sk_live_...` et `pk_live_...`

## 🎯 Cas d'Usage

### Stripe Dashboard
- Vous vous connectez avec **email/mot de passe**
- Pas besoin de clé pour accéder au dashboard

### Webhooks Stripe
- Stripe peut demander une clé pour vérifier l'authenticité
- Utilisez la **clé secrète** (`sk_...`)

### Intégrations Tierces
- Si vous connectez Stripe à un autre service
- Utilisez la **clé secrète** (`sk_...`)

### API Stripe Directe
- Pour appeler l'API Stripe depuis votre code
- Utilisez la **clé secrète** (`sk_...`)

## 📝 Résumé

| Où | Quelle Clé |
|---|---|
| **Lambda (Backend)** | `sk_live_...` (clé secrète) |
| **Frontend** | `pk_live_...` (clé publique) - récupérée depuis backend |
| **Stripe demande clé d'accès** | `sk_live_...` (clé secrète) - **MÊME que Lambda** |

## ✅ Checklist

- [ ] Clé secrète dans Lambda : `sk_live_...` ou `sk_test_...`
- [ ] Clé publique dans Lambda : `pk_live_...` ou `pk_test_...`
- [ ] Quand Stripe demande une clé : Donner la **clé secrète** (même que Lambda)
- [ ] Mode correct : TEST ou LIVE selon vos besoins

---

**En résumé : OUI, donnez la même clé secrète (`sk_...`) que celle dans Lambda ! 🔐**

