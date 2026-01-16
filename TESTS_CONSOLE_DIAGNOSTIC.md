# 🔍 Tests Console pour Diagnostic

## 📋 Copiez-collez ces tests dans la console (F12)

### 1️⃣ TEST TOKEN ET AUTHENTIFICATION

```javascript
// ============================================
// TEST 1 : Vérifier les tokens stockés
// ============================================
console.log("🔐 TEST 1 : TOKENS");
console.log("localStorage.getItem('accessToken'):", localStorage.getItem('accessToken'));
console.log("localStorage.getItem('refreshToken'):", localStorage.getItem('refreshToken'));
console.log("localStorage.getItem('cognito_tokens'):", localStorage.getItem('cognito_tokens'));
console.log("sessionStorage.getItem('accessToken'):", sessionStorage.getItem('accessToken'));
console.log("window.currentUser:", window.currentUser);
console.log("window.currentUser?.accessToken:", window.currentUser?.accessToken);
console.log("typeof getAuthToken:", typeof getAuthToken);
if (typeof getAuthToken === 'function') {
  console.log("getAuthToken():", getAuthToken());
}
```

### 2️⃣ TEST CURRENT USER

```javascript
// ============================================
// TEST 2 : Vérifier currentUser
// ============================================
console.log("👤 TEST 2 : CURRENT USER");
console.log("window.currentUser:", window.currentUser);
console.log("window.currentUser?.isLoggedIn:", window.currentUser?.isLoggedIn);
console.log("window.currentUser?.id:", window.currentUser?.id);
console.log("window.currentUser?.email:", window.currentUser?.email);
console.log("window.currentUser?.username:", window.currentUser?.username);
console.log("window.currentUser?.profile_photo_url:", window.currentUser?.profile_photo_url);
console.log("window.currentUser?.photoData:", window.currentUser?.photoData ? "PRÉSENT" : "ABSENT");
console.log("JSON.stringify(window.currentUser):", JSON.stringify(window.currentUser));
```

### 3️⃣ TEST AVATAR ET IMAGE

```javascript
// ============================================
// TEST 3 : Vérifier l'avatar/image
// ============================================
console.log("🖼️ TEST 3 : AVATAR");
console.log("typeof getUserAvatar:", typeof getUserAvatar);
if (typeof getUserAvatar === 'function') {
  const avatar = getUserAvatar();
  console.log("getUserAvatar():", avatar);
  console.log("Type avatar:", typeof avatar);
  console.log("Avatar length:", avatar?.length);
  console.log("Avatar commence par 'data:':", avatar?.startsWith('data:'));
  console.log("Avatar commence par 'http':", avatar?.startsWith('http'));
}

// Vérifier l'élément DOM avatar
const avatarEl = document.getElementById('account-avatar');
console.log("Element #account-avatar:", avatarEl);
if (avatarEl) {
  console.log("Avatar innerHTML:", avatarEl.innerHTML);
  console.log("Avatar children:", avatarEl.children);
  const img = avatarEl.querySelector('img');
  console.log("Image dans avatar:", img);
  if (img) {
    console.log("Image src:", img.src);
    console.log("Image complete:", img.complete);
    console.log("Image naturalWidth:", img.naturalWidth);
  }
}
```

### 4️⃣ TEST POPUP ET MODAL

```javascript
// ============================================
// TEST 4 : Vérifier les popups/modals
// ============================================
console.log("📱 TEST 4 : POPUPS/MODALS");
console.log("Element #publish-modal-backdrop:", document.getElementById('publish-modal-backdrop'));
console.log("Element #auth-modal-backdrop:", document.getElementById('auth-modal-backdrop'));
console.log("Element #publish-modal-inner:", document.getElementById('publish-modal-inner'));
console.log("Element #auth-modal:", document.getElementById('auth-modal'));

// Vérifier les styles
const backdrop = document.getElementById('publish-modal-backdrop');
if (backdrop) {
  const style = window.getComputedStyle(backdrop);
  console.log("Backdrop display:", style.display);
  console.log("Backdrop visibility:", style.visibility);
  console.log("Backdrop opacity:", style.opacity);
  console.log("Backdrop z-index:", style.zIndex);
}

// Vérifier les fonctions
console.log("typeof openAuthModal:", typeof openAuthModal);
console.log("typeof openAccountModal:", typeof openAccountModal);
console.log("typeof window.openAuthModal:", typeof window.openAuthModal);
console.log("typeof window.openAccountModal:", typeof window.openAccountModal);
```

### 5️⃣ TEST ACTIONS POPUP (PARTICIPER)

```javascript
// ============================================
// TEST 5 : Vérifier les actions popup
// ============================================
console.log("⚡ TEST 5 : ACTIONS POPUP");
console.log("typeof onAction:", typeof onAction);
console.log("typeof window.onAction:", typeof window.onAction);
console.log("typeof toggleRepeatOptions:", typeof toggleRepeatOptions);
console.log("typeof window.toggleRepeatOptions:", typeof window.toggleRepeatOptions);

// Vérifier les boutons d'action
const actionBtns = document.querySelectorAll('[onclick*="onAction"], [onclick*="toggleRepeat"]');
console.log("Boutons d'action trouvés:", actionBtns.length);
actionBtns.forEach((btn, i) => {
  console.log(`Bouton ${i}:`, btn.id, btn.onclick, btn.getAttribute('onclick'));
});
```

### 6️⃣ TEST DÉCONNEXION

```javascript
// ============================================
// TEST 6 : Vérifier la déconnexion
// ============================================
console.log("🚪 TEST 6 : DÉCONNEXION");
console.log("typeof logout:", typeof logout);
console.log("typeof window.logout:", typeof window.logout);
console.log("Element bouton déconnexion:", document.querySelector('[onclick*="logout"], [onclick*="Logout"]'));

// Tester manuellement la déconnexion
if (typeof window.logout === 'function') {
  console.log("✅ window.logout disponible");
} else {
  console.error("❌ window.logout NON disponible");
}
```

### 7️⃣ TEST API ET REQUÊTES

```javascript
// ============================================
// TEST 7 : Vérifier les appels API
// ============================================
console.log("🌐 TEST 7 : API");
console.log("window.API_BASE_URL:", window.API_BASE_URL);
console.log("typeof fetch:", typeof fetch);

// Tester un appel API simple
if (window.API_BASE_URL && typeof fetch === 'function') {
  console.log("Test appel API /api/user/me...");
  fetch(`${window.API_BASE_URL}/user/me`, {
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`
    }
  })
  .then(r => {
    console.log("✅ API /user/me Status:", r.status);
    return r.json();
  })
  .then(data => {
    console.log("✅ API /user/me Response:", data);
  })
  .catch(err => {
    console.error("❌ API /user/me Error:", err);
  });
}
```

### 8️⃣ TEST COMPLET - DIAGNOSTIC GLOBAL

```javascript
// ============================================
// TEST 8 : DIAGNOSTIC COMPLET
// ============================================
console.log("🔍 DIAGNOSTIC COMPLET");
console.log("============================================");

// 1. Auth
const token = getAuthToken();
const user = window.currentUser;
console.log("1. AUTH:", {
  token: token ? "✅ PRÉSENT" : "❌ ABSENT",
  tokenLength: token?.length,
  user: user ? "✅ PRÉSENT" : "❌ ABSENT",
  isLoggedIn: user?.isLoggedIn,
  userId: user?.id
});

// 2. Avatar
const avatar = typeof getUserAvatar === 'function' ? getUserAvatar() : null;
console.log("2. AVATAR:", {
  function: typeof getUserAvatar === 'function' ? "✅" : "❌",
  value: avatar ? "✅ PRÉSENT" : "❌ ABSENT",
  type: typeof avatar,
  isImage: avatar?.startsWith('data:') || avatar?.startsWith('http'),
  domElement: document.getElementById('account-avatar') ? "✅" : "❌"
});

// 3. Popup
const backdrop = document.getElementById('publish-modal-backdrop');
const modal = document.getElementById('publish-modal-inner');
console.log("3. POPUP:", {
  backdrop: backdrop ? "✅" : "❌",
  backdropDisplay: backdrop ? window.getComputedStyle(backdrop).display : "N/A",
  modal: modal ? "✅" : "❌",
  openAuthModal: typeof window.openAuthModal === 'function' ? "✅" : "❌",
  openAccountModal: typeof window.openAccountModal === 'function' ? "✅" : "❌"
});

// 4. Actions
console.log("4. ACTIONS:", {
  onAction: typeof window.onAction === 'function' ? "✅" : "❌",
  toggleRepeatOptions: typeof window.toggleRepeatOptions === 'function' ? "✅" : "❌"
});

// 5. Logout
console.log("5. LOGOUT:", {
  logout: typeof window.logout === 'function' ? "✅" : "❌"
});

console.log("============================================");
```

### 9️⃣ TEST MANUEL - FORCER L'AFFICHAGE

```javascript
// ============================================
// TEST 9 : FORCER L'AFFICHAGE (TEST MANUEL)
// ============================================
console.log("🔧 TEST 9 : FORCER AFFICHAGE");

// Forcer l'avatar
if (typeof getUserAvatar === 'function' && typeof updateAccountBlockLegitimately === 'function') {
  console.log("Tentative de forcer l'avatar...");
  updateAccountBlockLegitimately();
}

// Forcer la popup
if (typeof window.openAccountModal === 'function') {
  console.log("Tentative d'ouvrir le modal compte...");
  window.openAccountModal();
}

// Forcer la déconnexion
if (typeof window.logout === 'function') {
  console.log("Tentative de déconnexion...");
  // Décommentez la ligne suivante pour tester :
  // window.logout();
}
```

### 🔟 TEST LOCALSTORAGE COMPLET

```javascript
// ============================================
// TEST 10 : INSPECTER TOUT LE LOCALSTORAGE
// ============================================
console.log("💾 TEST 10 : LOCALSTORAGE COMPLET");
console.log("Toutes les clés localStorage:", Object.keys(localStorage));
console.log("Toutes les clés sessionStorage:", Object.keys(sessionStorage));

// Afficher toutes les valeurs
Object.keys(localStorage).forEach(key => {
  const value = localStorage.getItem(key);
  console.log(`${key}:`, value?.substring(0, 100) + (value?.length > 100 ? '...' : ''));
});
```

## 📊 INTERPRÉTATION DES RÉSULTATS

### ✅ Si TOKEN = "❌ ABSENT"
- Problème : Le token n'est pas sauvegardé après login
- Solution : Vérifier `saveSession()` dans `auth.js`

### ✅ Si AVATAR = "❌ ABSENT"
- Problème : `getUserAvatar()` ne retourne rien
- Solution : Vérifier `photoData`, `profile_photo_url`, `picture` dans `currentUser`

### ✅ Si POPUP = "display: none"
- Problème : Le modal est masqué par CSS
- Solution : Vérifier `z-index`, `display`, `visibility` dans les styles

### ✅ Si ACTIONS = "❌"
- Problème : Les fonctions ne sont pas exposées globalement
- Solution : Vérifier `window.onAction = onAction` dans `map_logic.js`

### ✅ Si LOGOUT = "❌"
- Problème : `window.logout` n'est pas défini
- Solution : Vérifier `window.logout = logout` dans `auth.js`
