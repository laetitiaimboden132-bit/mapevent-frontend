# 📋 EXTRACTION COMPLÈTE DES FONCTIONS AUTH - PLAN D'ACTION

## 🎯 OBJECTIF
Extraire TOUTES les fonctions AUTH de `map_logic.js` (~24500 lignes) dans `auth.js` pour optimiser le code.

## 📊 STATISTIQUES
- **Fichier actuel** : `map_logic.js` (~24500 lignes)
- **Fonctions AUTH identifiées** : ~30 fonctions
- **Lignes de code AUTH** : ~4000 lignes
- **Fichier cible** : `auth.js` (~4000 lignes après extraction complète)

## ✅ FONCTIONS DÉJÀ DANS auth.js
1. ✅ Configuration (API_BASE_URL, COGNITO)
2. ✅ Utilitaires PKCE (base64UrlEncode, randomString, sha256, pkceChallengeFromVerifier)
3. ✅ Storage helpers (authSave, authLoad, authClearTemp, safeSetJSON, safeGetJSON, clearAuthStorage)
4. ✅ User management (saveUserSlim, updateAuthUI, getUserDisplayName)
5. ✅ Token management (getAuthToken, getRefreshToken, setAuthTokens)
6. ✅ OAuth Google (startGoogleLogin)

## ⏳ FONCTIONS À EXTRAIRE DANS auth.js

### 1. **OAuth Google (lignes 438-900)**
- `saveSession(tokens)` - ligne 438
- `loadSession()` - ligne 441
- `clearSession()` - ligne 445
- `decodeJwtPayload(token)` - ligne 449
- `handleCognitoCallbackIfPresent()` - lignes 499-900 (~400 lignes) ⚠️ CRITIQUE

### 2. **Modals AUTH (lignes 7882-11182)**
- `closeAuthModal()` - lignes 7882-7976 (~100 lignes)
- `openAuthModal(mode)` - lignes 10413-11182 (~770 lignes) ⚠️ ÉNORME
- `window.fermerModalAuth()` - lignes 7954-7976

### 3. **Login/Register (lignes 12131-13842)**
- `performRegister()` - lignes 12131-12287 (~150 lignes)
- `performLogin()` - lignes 12467-12587 (~120 lignes)
- `showRegisterTimeoutError()` - lignes 12047-12077
- `showRegisterConflictError()` - lignes 12080-12129
- `handleProRegisterSubmit(event)` - lignes 13540-13842 (~300 lignes) ⚠️ CRITIQUE

### 4. **Formulaire inscription (lignes 12619-13540)**
- `showProRegisterForm()` - lignes 12619-13183 (~500 lignes) ⚠️ ÉNORME
- `handleProPhotoUpload(event)` - lignes 13183-13220
- `setupRegisterAddressAutocomplete()` - lignes 11911-12017
- `selectRegisterAddressSuggestion()` - lignes 12020-12046

### 5. **Validation (lignes 13223-13511)**
- `validateProField(fieldName, value)` - lignes 13223-13289
- `validateProPassword(password)` - lignes 13292-13347
- `validateProPasswordMatch()` - lignes 13350-13370
- `validateRegisterPassword(password)` - lignes 13406-13468
- `validateRegisterPasswordMatch()` - lignes 13471-13496
- `toggleRegisterPasswordVisibility()` - lignes 13388-13403
- `toggleProPasswordVisibility()` - lignes 13373-13385
- `showError(elementId, message)` - lignes 13505-13510

### 6. **Email Verification (lignes 14103-14367)**
- `showEmailVerificationModal(email, username)` - lignes 14103-14200 (~100 lignes)
- `handleEmailCodeInput(index, event)` - lignes 14203-14215
- `handleEmailCodeKeydown(index, event)` - lignes 14217-14222
- `checkEmailCodeComplete()` - lignes 14224-14234
- `verifyEmailCode(providedCode)` - lignes 14237-14329 (~100 lignes)
- `resendEmailVerificationCode()` - lignes 14332-14361

### 7. **Photo Upload (lignes 13846-14095)**
- `showPhotoUploadForm(userData)` - lignes 13846-13900
- `handleOAuthPhotoUpload(event)` - lignes 13903-13942
- `uploadOAuthPhoto()` - lignes 13945-14047
- `skipPhotoUpload()` - lignes 14050-14095

### 8. **User Management (lignes 19051-20347)**
- `loadSavedUser()` - lignes 19051-19176 (~125 lignes)
- `logout()` - lignes 20286-20347 (~60 lignes)
- `getDefaultUser()` - lignes 1781-1858 (~80 lignes)
- `isLoggedIn()` - lignes 1861-1863
- `safeSetItem(key, value)` - lignes 209-300 (~90 lignes)
- `safeGetItem(key)` - à trouver

### 9. **Variables globales**
- `let registerData = {...}` - ligne 12599
- `let isSubmittingProRegister = false` - ligne 13538
- `let registerStep = 1` - ligne 12598

### 10. **Autres fonctions**
- `openLoginModal()` - wrapper ligne 11851
- `openRegisterModal()` - wrapper ligne 11857
- `socialLogin(provider)` - ligne 14376
- `showRegisterStep1()`, `showRegisterStep2()`, etc. - lignes 14368-15402

## 🔗 DÉPENDANCES CRITIQUES

### Variables globales (DOIVENT RESTER dans map_logic.js)
- `currentUser` (ligne 1866) - DOIT RESTER dans map_logic.js (utilisé partout)
- `registerData` - PEUT être dans auth.js
- `isSubmittingProRegister` - PEUT être dans auth.js

### Fonctions externes (DOIVENT être dans map_logic.js)
- `showNotification()` - fonction globale (utilisée partout)
- `updateAuthButtons()` - fonction globale
- `updateAccountBlockLegitimately()` - fonction globale
- `closePublishModal()` - fonction globale
- `loadUserDataOnLogin()` - fonction globale
- `showStatusChangeNotifications()` - fonction globale
- `getUserAvatar()` - fonction globale
- `showAccountBlockContent()` - fonction globale
- `escapeHtml()` - fonction utilitaire

## ⚠️ STRATÉGIE D'EXTRACTION

### APPROCHE RECOMMANDÉE : Extraction progressive par priorité

**Phase 1 : Fonctions utilitaires (SANS RISQUE) ✅ FAIT**
- ✅ authSave, authLoad, authClearTemp
- ✅ saveUserSlim, updateAuthUI
- ✅ getAuthToken, getRefreshToken
- ✅ startGoogleLogin

**Phase 2 : OAuth Callback (RISQUE MOYEN)**
- ⏳ handleCognitoCallbackIfPresent() (~400 lignes)
- ⏳ saveSession, loadSession, clearSession, decodeJwtPayload

**Phase 3 : Modals (RISQUE MOYEN)**
- ⏳ closeAuthModal() (~100 lignes)
- ⏳ openAuthModal() (~770 lignes) ⚠️ ÉNORME

**Phase 4 : Login/Register (RISQUE ÉLEVÉ)**
- ⏳ performLogin() (~120 lignes)
- ⏳ performRegister() (~150 lignes)
- ⏳ handleProRegisterSubmit() (~300 lignes)

**Phase 5 : Validation (RISQUE FAIBLE)**
- ⏳ Toutes les fonctions de validation
- ⏳ Toggle password visibility

**Phase 6 : Email/Photo (RISQUE MOYEN)**
- ⏳ showEmailVerificationModal et fonctions associées
- ⏳ showPhotoUploadForm et fonctions associées

**Phase 7 : User Management (RISQUE FAIBLE)**
- ⏳ loadSavedUser() (~125 lignes)
- ⏳ logout() (~60 lignes)
- ⏳ getDefaultUser(), isLoggedIn()

## 🚀 ACTION IMMÉDIATE

Vu la taille et la complexité, je recommande :
1. ✅ **Continuer avec extraction progressive** (plus sûr)
2. ⏳ **OU extraire TOUT en une fois** (plus rapide mais plus risqué)

**RECOMMANDATION** : Extraire TOUT en une fois comme demandé par l'utilisateur, puis tester intensivement.
