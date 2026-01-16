# 📊 ANALYSE COMPLÈTE : PERSISTANCE UTILISATEUR & AUTHENTIFICATION

## 🔍 1. STOCKAGE DES DONNÉES UTILISATEUR

### ✅ Source de vérité : PostgreSQL (table `users`)

**Structure de la table `users` :**
```sql
CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,              -- Format: "user_{timestamp}_{hex}"
    email VARCHAR(255) UNIQUE,                 -- Email unique
    username VARCHAR(255),                     -- Nom d'utilisateur
    first_name VARCHAR(100),                   -- Prénom
    last_name VARCHAR(100),                    -- Nom de famille
    subscription VARCHAR(50) DEFAULT 'free',    -- 'free', 'vip_plus', etc.
    role VARCHAR(50) DEFAULT 'user',           -- 'user', 'director', 'pro', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Champs supplémentaires (détectés dans le code) :**
- `profile_photo_url` (ajouté dynamiquement si absent)
- `avatar` (emoji ou URL)
- `avatar_emoji` (emoji par défaut)
- `avatar_description` (description de l'avatar)
- `password_hash` (pour authentification email/password)
- `postal_address` (adresse postale pour alertes)
- `postal_city`, `postal_zip`, `postal_country`

**Tables liées :**
- `user_profiles` : Bio, photos, vidéos, liens
- `subscriptions` : Abonnements Stripe (stripe_customer_id, stripe_subscription_id)
- `user_likes`, `user_favorites`, `user_agenda` : Actions utilisateur

---

## 🔐 2. SYSTÈME D'AUTHENTIFICATION

### ❌ PROBLÈME IDENTIFIÉ : Pas de système de session centralisé

**État actuel :**
- ✅ **OAuth Google** : Fonctionne via Cognito
- ✅ **OAuth Facebook** : Endpoint présent (`/api/user/oauth/facebook`)
- ✅ **Email/Password** : Endpoint `/api/user/login` et `/api/user/register`
- ❌ **Pas de JWT** : Aucun token JWT généré ou vérifié
- ❌ **Pas de cookies de session** : Pas de gestion de session serveur
- ❌ **Pas d'endpoint `/api/me`** : Impossible de récupérer le profil courant

**Flux d'authentification actuel :**
1. **OAuth Google** :
   - Frontend → Cognito → Callback avec `code`
   - Frontend envoie `code` + données Google au backend `/api/user/oauth/google`
   - Backend crée/met à jour l'utilisateur dans PostgreSQL
   - Backend retourne les données utilisateur
   - Frontend stocke dans `localStorage.setItem('currentUser', ...)`

2. **Email/Password** :
   - Frontend envoie email + password hash au backend `/api/user/login`
   - Backend vérifie le hash dans PostgreSQL
   - Backend retourne les données utilisateur
   - Frontend stocke dans `localStorage`

**Problèmes identifiés :**
- ❌ Pas de vérification de session côté serveur
- ❌ L'utilisateur peut modifier `localStorage` et se faire passer pour quelqu'un d'autre
- ❌ Pas de rafraîchissement automatique du profil depuis le serveur
- ❌ Pas de déconnexion côté serveur (seulement suppression de `localStorage`)

---

## 🔄 3. RECONNAISSANCE AUTOMATIQUE

### ❌ PROBLÈME : Pas d'endpoint pour récupérer le profil courant

**Endpoints existants :**
- ✅ `/api/user/register` : Créer un compte
- ✅ `/api/user/login` : Se connecter
- ✅ `/api/user/oauth/google` : OAuth Google
- ✅ `/api/user/oauth/google/complete` : Compléter l'inscription OAuth
- ✅ `/api/user/profile` (PUT) : Mettre à jour le profil
- ✅ `/api/user/<user_id>/avatar` (GET) : Récupérer l'avatar
- ❌ **MANQUE : `/api/user/me` ou `/api/user/current`** : Récupérer le profil courant

**Reconnaissance actuelle (frontend) :**
```javascript
// Au chargement de la page
const savedUser = localStorage.getItem('currentUser');
if (savedUser) {
  try {
    currentUser = JSON.parse(savedUser);
    // ❌ PROBLÈME : Pas de vérification côté serveur
    // ❌ PROBLÈME : Les données peuvent être obsolètes
  } catch (e) {
    currentUser = null;
  }
}
```

**Ce qui manque :**
- Endpoint `/api/user/me` qui :
  - Vérifie un token JWT ou un cookie de session
  - Retourne les données utilisateur à jour depuis PostgreSQL
  - Met à jour `localStorage` côté frontend

---

## 👥 4. GESTION DES RÔLES / COMPTES PRO

### ✅ Structure présente dans PostgreSQL

**Champ `role` :**
- Valeurs possibles : `'user'`, `'director'`, `'pro'` (détecté dans le code)
- Défaut : `'user'`
- Stocké dans la table `users`

**Champ `subscription` :**
- Valeurs possibles : `'free'`, `'vip_plus'`, etc.
- Défaut : `'free'`
- Stocké dans la table `users`

**Intégration Stripe :**
- Table `subscriptions` avec :
  - `stripe_customer_id` : ID client Stripe
  - `stripe_subscription_id` : ID abonnement Stripe
  - `plan` : Plan d'abonnement
  - `status` : Statut de l'abonnement
  - `current_period_start`, `current_period_end` : Période courante

**Lien avec Stripe :**
- ✅ Webhooks Stripe configurés (`/api/payments/webhook`)
- ✅ Mise à jour automatique de `subscription` et `role` via webhooks
- ✅ Endpoints de paiement présents (`/api/payments/create-checkout-session`)

**Problèmes identifiés :**
- ❌ Pas de synchronisation automatique `subscription` ↔ `role`
- ❌ Le `role` n'est pas automatiquement mis à jour lors d'un changement d'abonnement
- ❌ Pas de vérification côté serveur du statut pro avant d'accéder aux fonctionnalités pro

---

## 💻 5. FRONTEND : PERSISTANCE DE SESSION

### ✅ Mécanisme actuel : localStorage

**Chargement au démarrage :**
```javascript
// Ligne ~589 dans map_logic.js
const savedUser = localStorage.getItem('currentUser');
if (savedUser) {
  try {
    currentUser = JSON.parse(savedUser);
    // Utilisé pour afficher le bloc compte, etc.
  } catch (e) {
    currentUser = null;
  }
}
```

**Sauvegarde après connexion :**
```javascript
// Après OAuth Google ou login
localStorage.setItem("currentUser", JSON.stringify(currentUser));
```

**Déconnexion :**
```javascript
// Fonction logout()
localStorage.removeItem("currentUser");
currentUser = null;
```

**Problèmes identifiés :**
- ❌ Pas de rafraîchissement automatique depuis le serveur
- ❌ Les données peuvent être obsolètes (changement d'abonnement, etc.)
- ❌ Pas de vérification de validité de session
- ❌ Pas de gestion d'expiration de session

---

## 🎯 6. RECOMMANDATIONS

### ✅ À IMPLÉMENTER URGAMMENT

#### 1. **Créer l'endpoint `/api/user/me`**
```python
@app.route('/api/user/me', methods=['GET'])
def get_current_user():
    """
    Récupère le profil de l'utilisateur courant.
    Vérifie un token JWT ou un cookie de session.
    """
    # TODO: Vérifier le token JWT ou cookie
    # TODO: Récupérer l'utilisateur depuis PostgreSQL
    # TODO: Retourner les données à jour
    pass
```

#### 2. **Implémenter JWT ou cookies de session**
- Option A : **JWT** (recommandé pour Lambda)
  - Générer un JWT après connexion
  - Stocker dans `localStorage` ou `httpOnly` cookie
  - Vérifier le JWT dans chaque requête
  
- Option B : **Cookies de session**
  - Générer un token de session après connexion
  - Stocker dans Redis (déjà présent dans le code)
  - Vérifier le cookie dans chaque requête

#### 3. **Rafraîchissement automatique côté frontend**
```javascript
// Au chargement de la page
async function loadCurrentUser() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/user/me`, {
      credentials: 'include' // Pour envoyer les cookies
    });
    if (response.ok) {
      const user = await response.json();
      currentUser = user;
      localStorage.setItem('currentUser', JSON.stringify(user));
    } else {
      // Session expirée, déconnecter
      localStorage.removeItem('currentUser');
      currentUser = null;
    }
  } catch (error) {
    console.error('Erreur chargement utilisateur:', error);
  }
}
```

#### 4. **Synchronisation subscription ↔ role**
- Mettre à jour automatiquement le `role` lors d'un changement d'abonnement Stripe
- Vérifier le statut pro avant d'accéder aux fonctionnalités pro

#### 5. **Middleware d'authentification**
```python
def require_auth(f):
    """Décorateur pour protéger les routes nécessitant une authentification"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Vérifier le JWT ou cookie
        # Récupérer l'utilisateur depuis PostgreSQL
        # Passer l'utilisateur à la fonction
        pass
    return decorated_function
```

---

## 📋 7. CHECKLIST D'IMPLÉMENTATION

### Phase 1 : Authentification de base
- [ ] Créer l'endpoint `/api/user/me`
- [ ] Implémenter JWT ou cookies de session
- [ ] Middleware d'authentification
- [ ] Rafraîchissement automatique côté frontend

### Phase 2 : Sécurité
- [ ] Vérification de session sur toutes les routes protégées
- [ ] Expiration de session
- [ ] Déconnexion côté serveur
- [ ] Protection CSRF

### Phase 3 : Synchronisation
- [ ] Synchronisation subscription ↔ role
- [ ] Webhooks Stripe pour mise à jour automatique
- [ ] Rafraîchissement périodique du profil

---

## 🔗 8. RÉFÉRENCES CODE

**Fichiers clés :**
- `lambda-package/backend/main.py` : Backend Flask
- `public/map_logic.js` : Frontend (lignes ~589, ~405, ~794 pour localStorage)
- `lambda-package/backend/database/schema.sql` : Schéma PostgreSQL

**Endpoints à créer/modifier :**
- `/api/user/me` : **À CRÉER**
- `/api/user/login` : Existe, à améliorer avec JWT
- `/api/user/logout` : **À CRÉER**

---

## ✅ CONCLUSION

**État actuel :**
- ✅ Base de données PostgreSQL bien structurée
- ✅ OAuth Google fonctionnel
- ✅ Intégration Stripe présente
- ❌ Pas de système de session centralisé
- ❌ Pas de vérification côté serveur
- ❌ Pas de rafraîchissement automatique

**Priorité :**
1. **URGENT** : Créer `/api/user/me` et système JWT/cookies
2. **IMPORTANT** : Rafraîchissement automatique côté frontend
3. **MOYEN** : Synchronisation subscription ↔ role




