# 📋 CSP et Gestion de Session - État Actuel

## 🔒 Content Security Policy (CSP) Actuelle

### Valeur CSP configurée (CloudFront Response Headers Policy)

**Fichier**: `csp-policy.json`

```http
Content-Security-Policy: default-src * 'unsafe-inline' 'unsafe-eval' 'unsafe-hashes' 'unsafe-allow-redirects' data: blob: http: https: ws: wss:; script-src * 'unsafe-inline' 'unsafe-eval' 'unsafe-hashes' data: blob: http: https:; script-src-elem * 'unsafe-inline' 'unsafe-eval' 'unsafe-hashes' data: blob: http: https:; script-src-attr * 'unsafe-inline' 'unsafe-hashes'; style-src * 'unsafe-inline' 'unsafe-hashes' data: blob: http: https:; style-src-elem * 'unsafe-inline' 'unsafe-hashes' data: blob: http: https:; style-src-attr * 'unsafe-inline' 'unsafe-hashes'; img-src * data: blob: http: https:; font-src * data: blob: http: https:; connect-src * data: blob: wss: ws: http: https:; frame-src * data: blob: http: https:; object-src * data: blob:; base-uri *; form-action *; worker-src * blob: data: http: https:; media-src * data: blob: http: https:; manifest-src *; upgrade-insecure-requests;
```

**⚠️ Note**: Cette CSP est **ultra permissive** (utilise `*` partout) et n'est probablement **pas appliquée** actuellement car :
- Dans `mapevent.html` ligne 7-8 : commentaire indique que la CSP a été supprimée du HTML
- Pas de header CSP visible dans le backend Lambda (`lambda-package/backend/main.py`)
- La CSP devrait être appliquée via CloudFront Response Headers Policy, mais il faut vérifier si elle est active

### Headers actuels envoyés par le backend Lambda

**Fichier**: `lambda-package/backend/main.py` (lignes 248-253) et `lambda-package/handler.py` (lignes 85-90)

```http
Access-Control-Allow-Origin: https://mapevent.world
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
Access-Control-Allow-Headers: Content-Type, Authorization, Origin, X-Requested-With, Accept
Access-Control-Max-Age: 3600
Access-Control-Allow-Credentials: false
```

**❌ Pas de header CSP envoyé par le backend Lambda**

---

## 🔐 Gestion de Session

### Méthode actuelle : **localStorage + sessionStorage** (pas de cookies)

**Fichier**: `public/map_logic.js`

#### 1. **Tokens Cognito OAuth (PKCE)** → `sessionStorage`
```javascript
// Lignes 72-77
function authSave(key, val) {
  sessionStorage.setItem(key, val);
}
function authLoad(key) {
  return sessionStorage.getItem(key);
}
```

**Stockage**:
- `pkce_verifier` → `sessionStorage`
- `oauth_state` → `sessionStorage`

#### 2. **Tokens JWT Cognito** → `localStorage`
```javascript
// Ligne 408
function saveSession(tokens) {
  safeSetItem("cognito_tokens", JSON.stringify(tokens));
}
```

**Stockage**:
- `cognito_tokens` (id_token, access_token, refresh_token) → `localStorage`

#### 3. **Données utilisateur** → `localStorage` (avec fallback sessionStorage → mémoire)
```javascript
// Lignes 142-165
function safeSetJSON(key, value) {
  // Fallback: localStorage → sessionStorage → mémoire
}

// Stockage
currentUser → localStorage (slim, ~1KB)
```

**Stockage**:
- `currentUser` (objet slim) → `localStorage` (avec fallback sessionStorage → `window.__MEMORY_STORE__`)

### ❌ Pas de cookies HTTP-only
- Aucun `Set-Cookie` dans le backend
- Aucun cookie utilisé pour l'authentification
- Tous les tokens sont accessibles via JavaScript (XSS risk)

---

## 📊 Résumé

| Élément | Valeur Actuelle |
|---------|----------------|
| **CSP Header** | ❌ Non envoyé par le backend<br>⚠️ Configuré dans CloudFront mais statut inconnu |
| **CSP dans HTML** | ❌ Supprimée (commentaire ligne 7-8 de mapevent.html) |
| **Session** | ✅ localStorage + sessionStorage (pas de cookies) |
| **Tokens JWT** | ✅ localStorage (`cognito_tokens`) |
| **Tokens OAuth PKCE** | ✅ sessionStorage (`pkce_verifier`, `oauth_state`) |
| **Données utilisateur** | ✅ localStorage (`currentUser` slim) |
| **Cookies HTTP-only** | ❌ Aucun |

---

## 🔍 Vérification nécessaire

Pour confirmer la CSP réellement envoyée, vérifier :
1. **CloudFront Response Headers Policy** : Est-elle attachée à la distribution ?
2. **Headers réels** : Utiliser DevTools → Network → Headers pour voir si `Content-Security-Policy` est présent


