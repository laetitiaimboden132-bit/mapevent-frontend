# 📋 PLAN D'EXTRACTION DES FONCTIONS AUTH

## 🎯 Objectif
Extraire toutes les fonctions AUTH de `map_logic.js` (~24500 lignes) dans un nouveau fichier `auth.js` pour optimiser et organiser le code.

## 📊 Statistiques
- **Fichier actuel** : `map_logic.js` (~24500 lignes)
- **Fonctions AUTH identifiées** : 33+ fonctions
- **Fichier cible** : `auth.js` (~2000-3000 lignes estimées)

## 🔍 Fonctions AUTH à Extraire

### 1. **Fonctions de base (lignes 72-210)**
- `authSave(key, val)`
- `authLoad(key)`
- `authClearTemp()`
- `saveUserSlim(userObj)`
- `updateAuthUI(slimUser)`
- `getAuthToken()`
- `getRefreshToken()`
- `clearAuthStorage()`
- `safeSetJSON(key, value)`
- `safeGetJSON(key)`
- `safeSetItem(key, value)`
- `safeGetItem(key)`

### 2. **OAuth Google (lignes 461-850)**
- `startGoogleLogin()`
- `handleCognitoCallbackIfPresent()`
- Variables: `COGNITO`, `isGoogleLoginInProgress`

### 3. **Modals AUTH (lignes 7882-11850)**
- `closeAuthModal()`
- `openAuthModal(mode)`
- `openLoginModal()`
- `openRegisterModal()`
- `fermerModalAuth()` (fonction globale)

### 4. **Inscription/Connexion (lignes 11911-16000)**
- `performRegister()`
- `performLogin()`
- `showProRegisterForm()`
- `handleProRegisterSubmit(event)`
- `handleProPhotoUpload(event)`
- `setupRegisterAddressAutocomplete()`
- `selectRegisterAddressSuggestion()`
- `showRegisterTimeoutError()`
- `showRegisterConflictError()`
- `showRegisterStep1()`
- `showRegisterStep2()`
- `showRegisterStep2_5()`
- `showRegisterStep3()`
- `showRegisterForm()`
- `toggleRegisterPasswordVisibility()`
- `validateRegisterPassword()`
- `validateRegisterPasswordMatch()`

### 5. **Email Verification (ligne 14103)**
- `showEmailVerificationModal(email, username)`

### 6. **User Management (lignes 19051-20286)**
- `loadSavedUser()`
- `logout()`
- `setLoggedInUserFromAPI()`

## 🔗 Dépendances à Gérer

### Variables Globales Nécessaires
- `currentUser` (variable globale)
- `API_BASE_URL` (constante)
- `COGNITO` (configuration)
- `registerData` (objet global pour formulaire)

### Fonctions Externes Nécessaires
- `showNotification()` (depuis map_logic.js)
- `updateAuthButtons()` (depuis map_logic.js)
- `updateAccountBlockLegitimately()` (depuis map_logic.js)
- `randomString()` (utilitaire)
- `pkceChallengeFromVerifier()` (PKCE)

## ⚠️ STRATÉGIE D'EXTRACTION

### Phase 1 : Variables et Constantes (SANS RISQUE)
- Extraire `COGNITO` config
- Extraire `API_BASE_URL`
- Extraire variables globales AUTH

### Phase 2 : Fonctions Utilitaires (SANS RISQUE)
- `authSave`, `authLoad`, `authClearTemp`
- `saveUserSlim`, `updateAuthUI`
- `getAuthToken`, `getRefreshToken`
- Storage helpers

### Phase 3 : OAuth (RISQUE MOYEN)
- `startGoogleLogin()`
- `handleCognitoCallbackIfPresent()`

### Phase 4 : Modals (RISQUE MOYEN)
- `openAuthModal()`, `closeAuthModal()`
- `openLoginModal()`, `openRegisterModal()`

### Phase 5 : Forms (RISQUE ÉLEVÉ - beaucoup de dépendances)
- `performLogin()`, `performRegister()`
- `showProRegisterForm()`
- Validation functions

## ✅ VÉRIFICATIONS POST-EXTRACTION

1. ✅ Toutes les fonctions exposées globalement (`window.xxx`)
2. ✅ Variables globales partagées (`currentUser`)
3. ✅ Dépendances externes (`showNotification`, etc.)
4. ✅ Imports dans `mapevent.html` (ajouter `<script src="auth.js">`)
5. ✅ Ordre de chargement (auth.js avant map_logic.js)

## 🚀 APPROCHE RECOMMANDÉE

Vu la taille du fichier, il serait mieux de:
1. **Créer `auth.js` avec les fonctions de base d'abord**
2. **Tester que tout fonctionne**
3. **Extraire progressivement les autres fonctions**
4. **OU** : Garder les fonctions dans `map_logic.js` mais les organiser en sections claires

**RECOMMANDATION** : Pour éviter de casser quelque chose, je propose de créer un fichier `auth.js` avec UNIQUEMENT les fonctions de base (Phase 1 + 2) d'abord, puis tester.
