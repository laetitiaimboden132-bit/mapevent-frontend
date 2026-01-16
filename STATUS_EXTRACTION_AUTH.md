# 📊 STATUT EXTRACTION AUTH - EN COURS

## ✅ FONCTIONS DÉJÀ EXTRACTÉES DANS `auth.js`

### Utilitaires de base (~287 lignes initiales)
- ✅ `base64UrlEncode()`
- ✅ `randomString()`
- ✅ `sha256()`
- ✅ `pkceChallengeFromVerifier()`
- ✅ `authSave()`, `authLoad()`, `authClearTemp()`
- ✅ `safeSetJSON()`, `safeGetJSON()`
- ✅ `clearAuthStorage()`
- ✅ `saveUserSlim()`
- ✅ `updateAuthUI()`
- ✅ `getUserDisplayName()`
- ✅ `getAuthToken()`, `getRefreshToken()`, `setAuthTokens()`
- ✅ `startGoogleLogin()`

### Utilitaires JWT & Session (~50 lignes ajoutées)
- ✅ `decodeJwtPayload()`
- ✅ `saveSession()`
- ✅ `loadSession()`
- ✅ `clearSession()`
- ✅ `safeSetItem()` (avec gestion quota complète)

### Variables globales (~30 lignes ajoutées)
- ✅ `registerStep`
- ✅ `registerData`
- ✅ `isSubmittingProRegister`
- ✅ `isGoogleLoginInProgress`

### Fonctions principales (~250 lignes ajoutées)
- ✅ `closeAuthModal()` (~70 lignes)
- ✅ `loadSavedUser()` (~125 lignes)
- ✅ `logout()` (~60 lignes)
- ✅ `window.fermerModalAuth()` (fonction globale pour onclick inline)

**Total extrait jusqu'à présent : ~617 lignes**

---

## ⏳ FONCTIONS CRITIQUES RESTANTES À EXTRAIRE

### Fonctions modales (~600 lignes)
- [ ] `openAuthModal(mode)` (~600 lignes, ligne 10413)
- [ ] `openLoginModal()` (~5 lignes, ligne 11851)
- [ ] `openRegisterModal()` (~10 lignes, ligne 11857)

### Fonctions login/register (~420 lignes)
- [ ] `performLogin()` (~120 lignes, ligne 12467)
- [ ] `performRegister()` (~300 lignes, ligne 12131)

### OAuth Google callback (~550 lignes)
- [ ] `handleCognitoCallbackIfPresent()` (~550 lignes, ligne 499)

### Fonctions PRO register (~1500 lignes)
- [ ] `showProRegisterForm()` (~700 lignes, ligne 12619)
- [ ] `handleProRegisterSubmit()` (~500 lignes, ligne 13540)
- [ ] `handleProPhotoUpload()` (~40 lignes, ligne 13183)
- [ ] `validateProField()` (~60 lignes, ligne 13223)
- [ ] `validateProPassword()` (~60 lignes, ligne 13292)
- [ ] `validateProPasswordMatch()` (~20 lignes, ligne 13350)
- [ ] `toggleProPasswordVisibility()` (~15 lignes, ligne 13373)
- [ ] `showPhotoUploadForm()` (~100 lignes, ligne 13846)
- [ ] `handleOAuthPhotoUpload()` (~40 lignes, ligne 13902)
- [ ] `uploadOAuthPhoto()` (~100 lignes, ligne 13945)
- [ ] `skipPhotoUpload()` (~20 lignes, ligne 14049)
- [ ] `updatePostalAddressRequired()` (~25 lignes, ligne 13513)

### Fonctions email verification (~400 lignes)
- [ ] `showEmailVerificationModal()` (~300 lignes, ligne 14103)
- [ ] `verifyEmailCode()` (~100 lignes, ligne 14237)
- [ ] `checkEmailCodeComplete()` (~15 lignes, ligne 14224)
- [ ] `handleEmailCodeInput()` (~15 lignes, ligne 14202)
- [ ] `handleEmailCodeKeydown()` (~5 lignes, ligne 14217)
- [ ] `resendEmailVerificationCode()` (~30 lignes, ligne 14303)

### Fonctions utilitaires register (~200 lignes)
- [ ] `showRegisterConflictError()` (~50 lignes, ligne 12079)
- [ ] `showRegisterTimeoutError()` (~30 lignes, ligne 12047)
- [ ] `setupRegisterAddressAutocomplete()` (~50 lignes, ligne 11911)
- [ ] `selectRegisterAddressSuggestion()` (~30 lignes, ligne 12020)
- [ ] `toggleRegisterPasswordVisibility()` (~15 lignes, ligne 13388)
- [ ] `validateRegisterPassword()` (~60 lignes, ligne 13406)
- [ ] `validateRegisterPasswordMatch()` (~20 lignes, ligne 13471)
- [ ] `showError()` (~5 lignes, ligne 13505)

### Fonctions register steps (~400 lignes)
- [ ] `showRegisterStep1()` (~10 lignes, ligne 14368)
- [ ] `showRegisterStep2()` (~200 lignes, ligne 14385)
- [ ] `showRegisterStep2_5()` (~200 lignes, ligne 14960)
- [ ] `showRegisterStep3()` (~200 lignes, ligne 15402)
- [ ] `showRegisterForm()` (~200 lignes, ligne 15794)
- [ ] `socialLogin()` (~10 lignes, ligne 14376)

**Total restant : ~4000 lignes**

---

## 📋 PROCHAINES ÉTAPES

1. **URGENT** : Extraire `openAuthModal()`, `performLogin()`, `performRegister()` (fonctions critiques)
2. **IMPORTANT** : Extraire `handleCognitoCallbackIfPresent()` (OAuth Google)
3. **IMPORTANT** : Extraire toutes les fonctions PRO register
4. **IMPORTANT** : Extraire toutes les fonctions email verification
5. **NICE TO HAVE** : Extraire les fonctions utilitaires restantes

---

## 🔧 CONFIGURATION ACTUELLE

- ✅ `auth.js` créé avec fonctions de base (~617 lignes)
- ✅ `auth.js` chargé AVANT `map_logic.js` dans `mapevent.html`
- ✅ Version parameter mis à jour (`?v=20260111-003`)
- ✅ Fonctions exposées globalement : `startGoogleLogin`, `closeAuthModal`, `loadSavedUser`, `logout`

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

---

**Dernière mise à jour : 2025-01-11**
**État : EN COURS - ~15% complété**
