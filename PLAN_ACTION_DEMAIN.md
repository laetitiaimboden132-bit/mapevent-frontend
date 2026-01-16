# 🎯 PLAN D'ACTION - SESSION DEMAIN

## ✅ STATUT ACTUEL

### Backend (COMPLET ✅)
- ✅ Nettoyage terminé (~11 lignes supprimées)
- ✅ Architecture optimisée (fonctions centralisées, modules séparés)
- ✅ Aucun doublon identifié
- ✅ Code propre et maintenable

### Frontend (EN COURS ⏳)
- ✅ `auth.js` créé avec fonctions de base (~287 lignes)
- ⏳ Extraction complète des fonctions AUTH à terminer (~4000 lignes restantes)

---

## 🚀 TÂCHES PRIORITAIRES DEMAIN

### 1. EXTRACTION COMPLÈTE AUTH (URGENT)
**Fichier :** `public/auth.js`

**Fonctions critiques à extraire de `map_logic.js` :**
- [ ] `handleCognitoCallbackIfPresent()` (~550 lignes, ligne 499)
- [ ] `closeAuthModal()` (~70 lignes, ligne 7882)
- [ ] `loadSavedUser()` (~125 lignes, ligne 19051)
- [ ] `logout()` (~60 lignes, ligne 20286)
- [ ] `openAuthModal()` (~600 lignes, ligne 10413)
- [ ] `performLogin()` (~120 lignes, ligne 12467)
- [ ] `performRegister()` (~300 lignes, ligne 12131)
- [ ] `showProRegisterForm()` (~700 lignes, ligne 12619)
- [ ] `showEmailVerificationModal()` (~300 lignes, ligne 14103)
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
- [ ] `showRegisterConflictError()` (~50 lignes, ligne 12079)
- [ ] `showRegisterTimeoutError()` (~30 lignes, ligne 12047)
- [ ] `saveSession()` (~5 lignes, ligne 438)
- [ ] `decodeJwtPayload()` (~10 lignes, ligne 449)
- [ ] `safeSetItem()` (~230 lignes, ligne 209)
- [ ] `verifyEmailCode()` (~100 lignes, ligne 14237)
- [ ] `checkEmailCodeComplete()` (~15 lignes, ligne 14224)
- [ ] `handleEmailCodeInput()` (~15 lignes, ligne 14202)
- [ ] `handleEmailCodeKeydown()` (~5 lignes, ligne 14217)
- [ ] `resendEmailVerificationCode()` (~30 lignes, ligne 14303)

**Fonctions utilitaires à extraire :**
- [ ] `updatePostalAddressRequired()` (~25 lignes, ligne 13513)
- [ ] `showError()` (~5 lignes, ligne 13505)

**Variables globales à déplacer :**
- [ ] `isSubmittingProRegister` (ligne 13538)
- [ ] `registerData` (ligne 12599)
- [ ] `registerStep` (ligne 12598)

**Estimation totale :** ~4000 lignes à extraire

---

### 2. NETTOYAGE `map_logic.js` (APRÈS EXTRACTION)
- [ ] Supprimer toutes les fonctions AUTH dupliquées
- [ ] Supprimer les constantes dupliquées (`API_BASE_URL`, `COGNITO`)
- [ ] Vérifier que toutes les dépendances sont satisfaites
- [ ] S'assurer que `map_logic.js` importe bien `auth.js` (via HTML)

---

### 3. EXPOSITION GLOBALE DES FONCTIONS
- [ ] Exposer toutes les fonctions AUTH via `window.*`
- [ ] Vérifier que toutes les fonctions sont accessibles depuis `map_logic.js`
- [ ] Tester que les `onclick` inline fonctionnent toujours

---

### 4. VÉRIFICATIONS ET TESTS
- [ ] Vérifier que `auth.js` est chargé AVANT `map_logic.js` dans `mapevent.html`
- [ ] Tester le login/register standard
- [ ] Tester OAuth Google
- [ ] Tester email verification
- [ ] Tester "Rester connecté"
- [ ] Tester fermeture modals (bouton "Annuler", bouton "X")
- [ ] Vérifier que le bloc compte s'affiche correctement après connexion

---

## 🔍 AMÉLIORATIONS SUPPLÉMENTAIRES IDENTIFIÉES

### Backend (`main.py`)
- [ ] **Gestion connexions DB** : Créer un contexte manager (`with db_connection() as conn:`) pour éviter les fuites de connexions
- [ ] **Cache Redis** : Mettre en cache les requêtes fréquentes (ex: `build_user_slim`)
- [ ] **Pagination** : Implémenter pagination sur les endpoints list (actuellement limitée)
- [ ] **Rate limiting** : Ajouter rate limiting sur endpoints publics (prévenir abus)
- [ ] **Logging structuré** : Améliorer le logging avec JSON pour CloudWatch
- [ ] **Validation inputs** : Centraliser la validation des inputs (éviter duplication)
- [ ] **Error handling** : Créer une fonction centralisée pour formater les erreurs API

### Frontend (`map_logic.js`)
- [ ] **Séparation modules** : Extraire aussi les modules ONBOARDING, MAP, EVENTS, etc. dans des fichiers séparés
- [ ] **Gestion d'état** : Implémenter un state manager (Redux-like simple) pour éviter les variables globales
- [ ] **Lazy loading** : Charger les modules on-demand pour réduire le temps de chargement initial
- [ ] **Debounce/throttle** : Ajouter debounce sur les recherches d'adresse (Nominatim) pour réduire les appels API
- [ ] **Error boundaries** : Ajouter try-catch autour des fonctions critiques pour éviter les crashes
- [ ] **Performance** : Analyser et optimiser les boucles répétitives (ex: `ensureDemoPoints()`)

### Infrastructure
- [ ] **CDN** : Optimiser le cache CloudFront pour les assets statiques
- [ ] **Compression** : Activer gzip/brotli compression sur CloudFront
- [ ] **Monitoring** : Ajouter CloudWatch dashboards pour monitoring des endpoints
- [ ] **Alertes** : Configurer des alertes CloudWatch pour erreurs 5xx

---

## 📋 CHECKLIST FINALE

### Avant de terminer la session demain :
- [ ] Toutes les fonctions AUTH extraites dans `auth.js`
- [ ] Tous les doublons supprimés de `map_logic.js`
- [ ] Toutes les fonctions exposées globalement
- [ ] Tests complets passés (login, register, OAuth, email verification)
- [ ] Aucune régression introduite
- [ ] Code propre et commenté
- [ ] Documentation à jour

---

## 📝 NOTES IMPORTANTES

### Dépendances externes dans `auth.js` (doivent être définies dans `map_logic.js`) :
- `currentUser` (variable globale)
- `showNotification()` (fonction globale)
- `updateAuthButtons()` (fonction globale)
- `updateAccountBlockLegitimately()` (fonction globale)
- `closePublishModal()` (fonction globale)
- `loadUserDataOnLogin()` (fonction globale, si existe)
- `showStatusChangeNotifications()` (fonction globale, si existe)
- `getDefaultUser()` (fonction globale, si existe)

### Ordre de chargement dans `mapevent.html` :
```html
<script src="auth.js?v=20260111-002"></script>
<script src="map_logic.js?v=20260111-002"></script>
```

### Cache busting :
- Mettre à jour le version parameter à chaque modification importante
- Forcer refresh navigateur (Ctrl+Shift+R) après déploiement

---

## 🎯 OBJECTIF FINAL

**Réduire `map_logic.js` de ~24500 lignes à ~20000 lignes** en extrayant toutes les fonctions AUTH (~4000 lignes) dans `auth.js`.

**Résultat attendu :**
- Code plus maintenable
- Séparation des responsabilités
- Réduction des doublons
- Meilleure performance (fichiers plus petits)
- Facilité de debugging

---

## 💡 PRIORITÉS DEMAIN

1. **URGENT** : Extraction complète AUTH (sinon code reste non optimisé)
2. **IMPORTANT** : Tests complets (sinon risque de régressions)
3. **NICE TO HAVE** : Améliorations supplémentaires (si temps disponible)

---

**Bon travail aujourd'hui ! À demain pour continuer ! 🚀**
