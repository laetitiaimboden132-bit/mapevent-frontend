# 📊 RÉCAPITULATIF EXTRACTION AUTH - STATUT ACTUEL

**Date :** 2025-01-11  
**État :** Fonctions critiques extraites ✅ (~57% complété)

---

## ✅ FONCTIONS EXTRACTÉES DANS `auth.js` (~2273 lignes)

### Utilitaires de base
- ✅ PKCE utilities (`base64UrlEncode`, `randomString`, `sha256`, `pkceChallengeFromVerifier`)
- ✅ Storage helpers (`authSave`, `authLoad`, `authClearTemp`, `safeSetJSON`, `safeGetJSON`, `clearAuthStorage`, `safeSetItem`)
- ✅ JWT & Session (`decodeJwtPayload`, `saveSession`, `loadSession`, `clearSession`)

### User Management
- ✅ `saveUserSlim()`
- ✅ `updateAuthUI()`
- ✅ `getUserDisplayName()`
- ✅ `getAuthToken()`, `getRefreshToken()`, `setAuthTokens()`

### OAuth Google
- ✅ `startGoogleLogin()`
- ✅ `handleCognitoCallbackIfPresent()` (~550 lignes) ⭐

### Modals AUTH
- ✅ `closeAuthModal()` (~70 lignes)
- ✅ `openAuthModal()` (~600 lignes) ⭐
- ✅ `openLoginModal()` (wrapper)
- ✅ `openRegisterModal()` (wrapper)

### Login/Register
- ✅ `performLogin()` (~120 lignes)
- ✅ `performRegister()` (~300 lignes)

### Variables globales
- ✅ `registerStep`
- ✅ `registerData`
- ✅ `isSubmittingProRegister`
- ✅ `isGoogleLoginInProgress`

### Fonctions exposées globalement
- ✅ `window.startGoogleLogin`
- ✅ `window.closeAuthModal`
- ✅ `window.loadSavedUser`
- ✅ `window.logout`
- ✅ `window.openAuthModal`
- ✅ `window.openLoginModal`
- ✅ `window.openRegisterModal`
- ✅ `window.performLogin`
- ✅ `window.performRegister`
- ✅ `window.handleCognitoCallbackIfPresent`
- ✅ `window.fermerModalAuth`

---

## ⏳ FONCTIONS RESTANTES À EXTRAIRE (~2300 lignes)

### Fonctions utilitaires register (~200 lignes)
- [ ] `showError()` (~5 lignes, ligne 13505)
- [ ] `showRegisterTimeoutError()` (~30 lignes, ligne 12047)
- [ ] `showRegisterConflictError()` (~50 lignes, ligne 12079)
- [ ] `setupRegisterAddressAutocomplete()` (~50 lignes, ligne 11911)
- [ ] `selectRegisterAddressSuggestion()` (~30 lignes, ligne 12020)
- [ ] `toggleRegisterPasswordVisibility()` (~15 lignes, ligne 13388)
- [ ] `validateRegisterPassword()` (~60 lignes, ligne 13406)
- [ ] `validateRegisterPasswordMatch()` (~20 lignes, ligne 13471)

### Fonctions PRO register (~1500 lignes)
- [ ] `showProRegisterForm()` (~700 lignes, ligne 12619) ⭐⭐⭐
- [ ] `handleProRegisterSubmit()` (~500 lignes, ligne 13540) ⭐⭐
- [ ] `handleProPhotoUpload()` (~40 lignes, ligne 13183)
- [ ] `validateProField()` (~60 lignes, ligne 13223)
- [ ] `validateProPassword()` (~60 lignes, ligne 13292)
- [ ] `validateProPasswordMatch()` (~20 lignes, ligne 13350)
- [ ] `toggleProPasswordVisibility()` (~15 lignes, ligne 13373)
- [ ] `updatePostalAddressRequired()` (~25 lignes, ligne 13513)
- [ ] `showPhotoUploadForm()` (~100 lignes, ligne 13846)
- [ ] `handleOAuthPhotoUpload()` (~40 lignes, ligne 13902)
- [ ] `uploadOAuthPhoto()` (~100 lignes, ligne 13945)
- [ ] `skipPhotoUpload()` (~20 lignes, ligne 14049)

### Fonctions email verification (~400 lignes)
- [ ] `showEmailVerificationModal()` (~300 lignes, ligne 14103) ⭐⭐
- [ ] `verifyEmailCode()` (~100 lignes, ligne 14237)
- [ ] `checkEmailCodeComplete()` (~15 lignes, ligne 14224)
- [ ] `handleEmailCodeInput()` (~15 lignes, ligne 14202)
- [ ] `handleEmailCodeKeydown()` (~5 lignes, ligne 14217)
- [ ] `resendEmailVerificationCode()` (~30 lignes, ligne 14303)

### Fonctions register steps (optionnel, si utilisées)
- [ ] `showRegisterStep1()` (~10 lignes, ligne 14368)
- [ ] `showRegisterStep2()` (~200 lignes, ligne 14385)
- [ ] `showRegisterStep2_5()` (~200 lignes, ligne 14960)
- [ ] `showRegisterStep3()` (~200 lignes, ligne 15402)
- [ ] `showRegisterForm()` (~200 lignes, ligne 15794)
- [ ] `socialLogin()` (~10 lignes, ligne 14376)

---

## 🎯 PROCHAINES ÉTAPES RECOMMANDÉES

### Option 1 : Test et validation (RECOMMANDÉ)
1. Tester les fonctions critiques extraites (login, register, modals, OAuth)
2. Vérifier qu'aucune régression n'a été introduite
3. Poursuivre l'extraction des fonctions restantes après validation

### Option 2 : Extraction complète (si test OK)
1. Extraire les fonctions utilitaires simples (showError, showRegisterTimeoutError, etc.)
2. Extraire les fonctions email verification
3. Extraire les fonctions PRO register (les plus complexes)
4. Supprimer les doublons de `map_logic.js`
5. Tests finaux complets

---

## 📋 CONFIGURATION ACTUELLE

- ✅ `auth.js` créé avec fonctions critiques (~2273 lignes)
- ✅ `auth.js` chargé AVANT `map_logic.js` dans `mapevent.html`
- ✅ Version parameter mis à jour (`?v=20260111-004`)
- ✅ Aucune erreur de lint
- ⏳ Fonctions restantes : ~2300 lignes (~43% restant)

---

## ⚠️ DÉPENDANCES EXTERNES

Les fonctions dans `auth.js` dépendent de fonctions/variables définies dans `map_logic.js` :
- `currentUser` (variable globale)
- `showNotification()` (fonction globale)
- `updateAuthButtons()` (fonction globale)
- `updateAccountBlockLegitimately()` (fonction globale)
- `closePublishModal()` (fonction globale)
- `getDefaultUser()` (fonction globale)
- `loadUserDataOnLogin()` (fonction globale)
- `showStatusChangeNotifications()` (fonction globale)
- `checkProfileCompleteness()` (fonction globale)
- `startOnboardingIfNeeded()` (fonction globale)
- `uploadProfilePhoto()` (fonction globale)
- `loadCurrentUserFromAPI()` (fonction globale)
- `showProRegisterForm()` (fonction globale - PAS ENCORE EXTRAITE)
- `showPhotoUploadForm()` (fonction globale - PAS ENCORE EXTRAITE)
- `showEmailVerificationModal()` (fonction globale - PAS ENCORE EXTRAITE)
- `showRegisterTimeoutError()` (fonction globale - PAS ENCORE EXTRAITE)
- `showRegisterConflictError()` (fonction globale - PAS ENCORE EXTRAITE)
- `setupRegisterAddressAutocomplete()` (fonction globale - PAS ENCORE EXTRAITE)

---

## 💡 RECOMMANDATION

**Les fonctions critiques sont extraites** (login, register, modals, OAuth callback).  
**Recommandation :** Tester d'abord ce qui est en place, puis continuer avec les fonctions restantes.

---

**Dernière mise à jour :** 2025-01-11  
**État :** ~57% complété - Fonctions critiques extraites ✅
