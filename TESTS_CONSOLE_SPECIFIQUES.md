# 🔍 Tests Console Spécifiques - Diagnostic Problèmes

## 🎯 PROBLÈME 1 : TOKEN UNDEFINED

```javascript
// ============================================
// TEST A : Vérifier getAuthToken()
// ============================================
console.log("🔐 TEST A : GETAUTHTOKEN");
console.log("typeof getAuthToken:", typeof getAuthToken);
console.log("typeof window.getAuthToken:", typeof window.getAuthToken);
console.log("getAuthToken():", typeof getAuthToken === 'function' ? getAuthToken() : "FONCTION ABSENTE");
console.log("window.getAuthToken():", typeof window.getAuthToken === 'function' ? window.getAuthToken() : "FONCTION ABSENTE");

// Vérifier les sources de token
console.log("localStorage.getItem('accessToken'):", localStorage.getItem('accessToken'));
console.log("localStorage.getItem('cognito_tokens'):", localStorage.getItem('cognito_tokens'));
const cognitoTokens = localStorage.getItem('cognito_tokens');
if (cognitoTokens) {
  try {
    const parsed = JSON.parse(cognitoTokens);
    console.log("cognito_tokens.access_token:", parsed.access_token ? "✅" : "❌");
    console.log("cognito_tokens.id_token:", parsed.id_token ? "✅" : "❌");
  } catch(e) {
    console.error("Erreur parsing cognito_tokens:", e);
  }
}
console.log("sessionStorage.getItem('accessToken'):", sessionStorage.getItem('accessToken'));
console.log("window.currentUser?.accessToken:", window.currentUser?.accessToken);
console.log("localStorage.getItem('rememberMe'):", localStorage.getItem('rememberMe'));
```

## 🎯 PROBLÈME 2 : PHOTODATA = "null" (STRING)

```javascript
// ============================================
// TEST B : Vérifier photoData
// ============================================
console.log("🖼️ TEST B : PHOTODATA");
console.log("window.currentUser.photoData:", window.currentUser?.photoData);
console.log("Type photoData:", typeof window.currentUser?.photoData);
console.log("photoData === 'null':", window.currentUser?.photoData === 'null');
console.log("photoData === null:", window.currentUser?.photoData === null);
console.log("photoData length:", window.currentUser?.photoData?.length);

// Vérifier pendingRegisterData
console.log("window.pendingRegisterData:", window.pendingRegisterData);
console.log("window.pendingRegisterData?.photoData:", window.pendingRegisterData?.photoData);

// Vérifier localStorage
const savedUser = localStorage.getItem('currentUser');
if (savedUser) {
  try {
    const parsed = JSON.parse(savedUser);
    console.log("localStorage currentUser.photoData:", parsed.photoData);
    console.log("localStorage currentUser.photoData type:", typeof parsed.photoData);
  } catch(e) {
    console.error("Erreur parsing currentUser:", e);
  }
}

// Vérifier registerData
console.log("window.registerData:", window.registerData);
console.log("window.registerData?.photoData:", window.registerData?.photoData);
```

## 🎯 PROBLÈME 3 : AVATAR UTILISE GOOGLE AU LIEU DE PHOTO UPLOADÉE

```javascript
// ============================================
// TEST C : Vérifier la priorité avatar
// ============================================
console.log("🖼️ TEST C : PRIORITÉ AVATAR");
const user = window.currentUser || {};
console.log("1. photoData:", user.photoData ? "✅" : "❌", typeof user.photoData);
console.log("2. profile_photo_url:", user.profile_photo_url ? "✅" : "❌", user.profile_photo_url?.substring(0, 50));
console.log("3. profile_photo_url is S3:", user.profile_photo_url?.includes('amazonaws.com') ? "✅" : "❌");
console.log("4. profile_photo_url is Google:", user.profile_photo_url?.includes('googleusercontent.com') ? "✅" : "❌");
console.log("5. profilePhoto:", user.profilePhoto ? "✅" : "❌");
console.log("6. avatar:", user.avatar ? "✅" : "❌");

// Tester getUserAvatar
if (typeof getUserAvatar === 'function') {
  const avatar = getUserAvatar();
  console.log("getUserAvatar() retourne:", avatar?.substring(0, 50));
  console.log("getUserAvatar() is Google:", avatar?.includes('googleusercontent.com') ? "✅" : "❌");
  console.log("getUserAvatar() is S3:", avatar?.includes('amazonaws.com') ? "✅" : "❌");
  console.log("getUserAvatar() is base64:", avatar?.startsWith('data:image') ? "✅" : "❌");
}
```

## 🎯 PROBLÈME 4 : POPUP NE S'AFFICHE PAS

```javascript
// ============================================
// TEST D : Vérifier la popup
// ============================================
console.log("📱 TEST D : POPUP");
const backdrop = document.getElementById('publish-modal-backdrop');
const modal = document.getElementById('publish-modal-inner');
const authBackdrop = document.getElementById('auth-modal-backdrop');
const authModal = document.getElementById('auth-modal');

console.log("publish-modal-backdrop:", backdrop ? "✅" : "❌");
if (backdrop) {
  const style = window.getComputedStyle(backdrop);
  console.log("  display:", style.display);
  console.log("  visibility:", style.visibility);
  console.log("  opacity:", style.opacity);
  console.log("  z-index:", style.zIndex);
  console.log("  pointer-events:", style.pointerEvents);
}

console.log("publish-modal-inner:", modal ? "✅" : "❌");
if (modal) {
  const style = window.getComputedStyle(modal);
  console.log("  display:", style.display);
  console.log("  visibility:", style.visibility);
}

console.log("auth-modal-backdrop:", authBackdrop ? "✅" : "❌");
console.log("auth-modal:", authModal ? "✅" : "❌");

// Vérifier les fonctions
console.log("typeof openAccountModal:", typeof openAccountModal);
console.log("typeof window.openAccountModal:", typeof window.openAccountModal);
```

## 🎯 PROBLÈME 5 : ACTIONS POPUP NE FONCTIONNENT PAS

```javascript
// ============================================
// TEST E : Vérifier les actions popup
// ============================================
console.log("⚡ TEST E : ACTIONS POPUP");
console.log("typeof onAction:", typeof onAction);
console.log("typeof window.onAction:", typeof window.onAction);
console.log("typeof toggleRepeatOptions:", typeof toggleRepeatOptions);
console.log("typeof window.toggleRepeatOptions:", typeof window.toggleRepeatOptions);

// Vérifier les boutons dans le modal
const modal = document.getElementById('publish-modal-inner');
if (modal) {
  const actionBtns = modal.querySelectorAll('button[onclick*="onAction"], button[onclick*="toggleRepeat"]');
  console.log("Boutons d'action trouvés:", actionBtns.length);
  actionBtns.forEach((btn, i) => {
    console.log(`Bouton ${i}:`, {
      id: btn.id,
      onclick: btn.getAttribute('onclick'),
      visible: btn.offsetParent !== null
    });
  });
}
```

## 🎯 PROBLÈME 6 : DÉCONNEXION NE FONCTIONNE PAS

```javascript
// ============================================
// TEST F : Vérifier la déconnexion
// ============================================
console.log("🚪 TEST F : DÉCONNEXION");
console.log("typeof logout:", typeof logout);
console.log("typeof window.logout:", typeof window.logout);

// Vérifier le bouton déconnexion
const logoutBtns = document.querySelectorAll('[onclick*="logout"], [onclick*="Logout"], button:contains("Déconnexion")');
console.log("Boutons déconnexion trouvés:", logoutBtns.length);
logoutBtns.forEach((btn, i) => {
  console.log(`Bouton ${i}:`, {
    id: btn.id,
    text: btn.textContent,
    onclick: btn.getAttribute('onclick')
  });
});

// Tester manuellement (décommentez pour tester)
// if (typeof window.logout === 'function') {
//   console.log("Test logout...");
//   window.logout();
// }
```

## 🔧 TESTS DE CORRECTION MANUELLE

```javascript
// ============================================
// TEST G : CORRECTION MANUELLE photoData
// ============================================
console.log("🔧 TEST G : CORRECTION PHOTODATA");

// 1. Normaliser photoData si c'est "null" (string)
if (window.currentUser && window.currentUser.photoData === 'null') {
  console.log("Correction: photoData 'null' → null");
  window.currentUser.photoData = null;
  localStorage.setItem('currentUser', JSON.stringify(window.currentUser));
  console.log("✅ photoData corrigé");
}

// 2. Vérifier si photoData existe dans pendingRegisterData
if (window.pendingRegisterData && window.pendingRegisterData.photoData && window.pendingRegisterData.photoData !== 'null') {
  console.log("Photo trouvée dans pendingRegisterData, copie vers currentUser...");
  window.currentUser.photoData = window.pendingRegisterData.photoData;
  localStorage.setItem('currentUser', JSON.stringify(window.currentUser));
  console.log("✅ photoData copié depuis pendingRegisterData");
}

// 3. Forcer la mise à jour de l'avatar
if (typeof updateAccountBlockLegitimately === 'function') {
  console.log("Mise à jour avatar...");
  updateAccountBlockLegitimately();
  console.log("✅ Avatar mis à jour");
}
```

## 🔧 TEST CORRECTION TOKEN

```javascript
// ============================================
// TEST H : CORRECTION TOKEN
// ============================================
console.log("🔧 TEST H : CORRECTION TOKEN");

// Vérifier cognito_tokens
const cognitoTokens = localStorage.getItem('cognito_tokens');
if (cognitoTokens) {
  try {
    const parsed = JSON.parse(cognitoTokens);
    if (parsed.access_token && !localStorage.getItem('accessToken')) {
      console.log("Copie access_token depuis cognito_tokens...");
      localStorage.setItem('accessToken', parsed.access_token);
      console.log("✅ accessToken copié");
    }
  } catch(e) {
    console.error("Erreur:", e);
  }
}

// Vérifier getAuthToken après correction
if (typeof getAuthToken === 'function') {
  const token = getAuthToken();
  console.log("getAuthToken() après correction:", token ? "✅" : "❌", token?.substring(0, 20));
}
```

## 📊 TEST COMPLET - RÉSUMÉ

```javascript
// ============================================
// TEST FINAL : RÉSUMÉ COMPLET
// ============================================
console.log("📊 RÉSUMÉ COMPLET");
console.log("============================================");

const issues = [];

// 1. Token
const token = typeof getAuthToken === 'function' ? getAuthToken() : null;
if (!token) {
  issues.push("❌ TOKEN: Absent");
} else {
  console.log("✅ TOKEN: Présent");
}

// 2. photoData
const photoData = window.currentUser?.photoData;
if (!photoData || photoData === 'null') {
  issues.push("❌ PHOTODATA: Absent ou 'null' (string)");
} else {
  console.log("✅ PHOTODATA: Présent");
}

// 3. Avatar utilise Google
const avatar = typeof getUserAvatar === 'function' ? getUserAvatar() : null;
if (avatar && avatar.includes('googleusercontent.com') && photoData && photoData !== 'null') {
  issues.push("❌ AVATAR: Utilise Google au lieu de photo uploadée");
} else if (avatar) {
  console.log("✅ AVATAR: Correct");
}

// 4. Popup
const backdrop = document.getElementById('publish-modal-backdrop');
if (!backdrop || window.getComputedStyle(backdrop).display === 'none') {
  issues.push("❌ POPUP: Masquée ou absente");
} else {
  console.log("✅ POPUP: Visible");
}

// 5. Actions
if (typeof window.onAction !== 'function') {
  issues.push("❌ ACTIONS: onAction non disponible");
} else {
  console.log("✅ ACTIONS: Disponibles");
}

// 6. Logout
if (typeof window.logout !== 'function') {
  issues.push("❌ LOGOUT: Fonction absente");
} else {
  console.log("✅ LOGOUT: Disponible");
}

console.log("============================================");
if (issues.length > 0) {
  console.error("PROBLÈMES DÉTECTÉS:", issues);
} else {
  console.log("✅ TOUT EST OK !");
}
```
