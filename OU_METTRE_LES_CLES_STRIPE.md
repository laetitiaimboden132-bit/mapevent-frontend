# 🔑 Où Mettre les Clés API Stripe

## 📋 Les 2 Clés API

Quand vous allez dans Stripe Dashboard → Developers → API keys, vous voyez :

1. **Publishable key** (commence par `pk_test_...`)
   - ✅ Peut être publique (visible dans le code frontend)
   - 📍 **OÙ :** Optionnel dans le frontend (le backend la renvoie automatiquement)

2. **Secret key** (commence par `sk_test_...`)
   - ⚠️ **JAMAIS dans le frontend !**
   - 📍 **OÙ :** Variables d'environnement AWS Lambda uniquement

---

## 🎯 Où Mettre la Secret Key (OBLIGATOIRE)

### Dans AWS Lambda - Variables d'Environnement

1. **Aller dans AWS Console**
   - https://console.aws.amazon.com
   - Lambda → Votre fonction `mapevent-backend`

2. **Configuration → Environment variables → Edit**

3. **Ajouter une nouvelle variable :**
   - **Key** : `STRIPE_SECRET_KEY`
   - **Value** : `sk_test_...` (votre clé secrète complète)

4. **Cliquer sur Save**

**⚠️ IMPORTANT :** 
- Ne jamais mettre cette clé dans le code
- Ne jamais la commiter dans Git
- Uniquement dans les variables d'environnement Lambda

---

## 🎯 Où Mettre la Publishable Key (OPTIONNEL)

### Option 1 : Le Backend la Renvoie Automatiquement (RECOMMANDÉ)

**Vous n'avez RIEN à faire !** 

Le backend récupère automatiquement la clé publique depuis les variables d'environnement et la renvoie au frontend lors de la création d'une session de paiement.

**Dans Lambda, ajouter aussi :**
- **Key** : `STRIPE_PUBLIC_KEY`
- **Value** : `pk_test_...` (votre clé publique)

Le code backend fait déjà ça automatiquement :
```python
# Dans create_checkout_session
return jsonify({
    'sessionId': session.id,
    'publicKey': app.config['STRIPE_PUBLIC_KEY']  # ← Renvoyé automatiquement
})
```

### Option 2 : Directement dans le Frontend (Alternative)

Si vous préférez, vous pouvez aussi la mettre directement dans `map_logic.js` :

```javascript
// En haut du fichier map_logic.js
const STRIPE_PUBLIC_KEY = "pk_test_..."; // Votre clé publique

// Initialiser Stripe
if (typeof Stripe !== 'undefined') {
  stripe = Stripe(STRIPE_PUBLIC_KEY);
}
```

**Mais ce n'est pas nécessaire** car le backend la renvoie déjà !

---

## 📝 Résumé : Ce qu'il Faut Faire

### ✅ OBLIGATOIRE - Dans AWS Lambda

Ajouter ces 2 variables d'environnement :

```
STRIPE_SECRET_KEY=sk_test_... (votre clé secrète)
STRIPE_PUBLIC_KEY=pk_test_... (votre clé publique)
```

### ✅ Le Code Fait le Reste

- Le backend utilise `STRIPE_SECRET_KEY` pour créer les sessions
- Le backend renvoie `STRIPE_PUBLIC_KEY` au frontend
- Le frontend utilise la clé publique pour rediriger vers Stripe

---

## 🔍 Comment Vérifier que C'est Bon

### 1. Vérifier dans Lambda
- Configuration → Environment variables
- Vérifier que `STRIPE_SECRET_KEY` et `STRIPE_PUBLIC_KEY` sont présents

### 2. Tester un Paiement
- Ouvrir le site
- Essayer de payer un contact
- Si ça redirige vers Stripe = ✅ C'est bon !
- Si erreur "Stripe non disponible" = ❌ Vérifier les clés

### 3. Vérifier les Logs
- AWS CloudWatch → Logs de votre fonction Lambda
- Chercher les erreurs liées à Stripe

---

## ⚠️ Erreurs Courantes

### Erreur "Invalid API Key"
- Vérifier que vous avez copié la clé complète (sans espaces)
- Vérifier que c'est bien la clé de TEST (commence par `sk_test_`)
- Vérifier qu'elle est bien dans les variables d'environnement Lambda

### Erreur "Stripe non disponible"
- Vérifier que Stripe.js est chargé (console navigateur)
- Vérifier que le backend renvoie bien la clé publique
- Vérifier les logs Lambda

---

## 🎯 Checklist

- [ ] Clé secrète (`sk_test_...`) ajoutée dans Lambda → `STRIPE_SECRET_KEY`
- [ ] Clé publique (`pk_test_...`) ajoutée dans Lambda → `STRIPE_PUBLIC_KEY`
- [ ] Variables sauvegardées dans Lambda
- [ ] Test d'un paiement pour vérifier

---

## 💡 Astuce

**Pour copier les clés facilement :**
- Dans Stripe Dashboard, cliquer sur "Reveal" pour voir la clé secrète
- Cliquer sur l'icône de copie à côté de chaque clé
- Coller directement dans Lambda (attention aux espaces en début/fin)

---

## 🔒 Sécurité

**NE JAMAIS :**
- ❌ Mettre la clé secrète dans le code
- ❌ Commiter les clés dans Git
- ❌ Partager les clés publiquement
- ❌ Mettre la clé secrète dans le frontend

**TOUJOURS :**
- ✅ Utiliser les variables d'environnement Lambda
- ✅ Utiliser des clés de TEST en développement
- ✅ Changer les clés si elles sont exposées



