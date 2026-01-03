# 🔧 Où Activer CORS dans API Gateway

## ✅ Réponse : Les Deux Fonctionnent !

Vous pouvez activer CORS **à deux endroits**, mais il y a une **meilleure option**.

## 🎯 Option 1 : Sur `/create-checkout-session` (RECOMMANDÉ)

### Pourquoi ?
- ✅ **Plus précis** : CORS seulement sur cette route
- ✅ **Plus sûr** : Pas de CORS inutile sur d'autres routes
- ✅ **Plus simple** : Directement sur la route qui en a besoin

### Comment faire :
1. **Sélectionnez** `/api/payments/create-checkout-session`
2. **Actions** → **Enable CORS**
3. **Configure** :
   - **Access-Control-Allow-Origin** : `https://mapevent.world`
   - **Access-Control-Allow-Methods** : `POST, OPTIONS`
   - **Access-Control-Allow-Headers** : `Content-Type, Authorization`
4. **Enable CORS and replace existing CORS headers**

## 🎯 Option 2 : Sur `/payments` (Alternative)

### Pourquoi ?
- ✅ **Applique à toutes les routes** sous `/payments`
- ✅ **Une seule configuration** pour plusieurs routes
- ⚠️ **Moins précis** : CORS sur toutes les routes même si pas nécessaire

### Comment faire :
1. **Sélectionnez** `/api/payments`
2. **Actions** → **Enable CORS**
3. **Configure** (même chose)
4. **Enable CORS**

## 💡 Recommandation

**Activez CORS sur `/create-checkout-session`** (Option 1) :
- C'est la route qui en a besoin
- Plus précis et sécurisé
- Plus facile à gérer

## 📋 Étapes Exactes

### Sur `/create-checkout-session`

1. **API Gateway** → Votre API
2. **Resources** → `/api` → `/payments` → `/create-checkout-session`
3. **Cliquez** sur `/create-checkout-session`
4. **Actions** (en haut) → **Enable CORS**
5. **Remplissez** :
   ```
   Access-Control-Allow-Origin: https://mapevent.world
   Access-Control-Allow-Methods: POST, OPTIONS
   Access-Control-Allow-Headers: Content-Type, Authorization
   ```
6. **Cliquez** sur "Enable CORS and replace existing CORS headers"
7. **Actions** → **Deploy API** → **Deploy**

## ⚠️ Important

### Après Activation CORS

**N'OUBLIEZ PAS** de **déployer l'API** :
1. **Actions** → **Deploy API**
2. **Deployment stage** : `default` (ou votre stage)
3. **Deploy**

Sans déploiement, les changements ne sont pas actifs !

## 🧪 Tester

1. **Recharger** `https://mapevent.world`
2. **Console** (F12) → Network
3. **Faire un paiement**
4. **Vérifier** :
   - OPTIONS → **200** ✅
   - POST → **200** ✅

## 📋 Résumé

| Où | Avantage | Inconvénient |
|---|---|---|
| **`/create-checkout-session`** | Plus précis, plus sûr | Une route à la fois |
| **`/payments`** | Toutes les routes d'un coup | Moins précis |

**Recommandation** : Activez sur **`/create-checkout-session`** ✅

---

**En résumé : Activez CORS sur `/create-checkout-session` (la route spécifique), c'est plus précis et plus sûr ! 🔧**

