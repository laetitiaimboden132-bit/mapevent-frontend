// ============================================
// DIAGNOSTIC USERNAME - COPIEZ-COLLEZ DANS LA CONSOLE
// ============================================
// Copiez TOUT le code ci-dessous (de "console.log" jusqu'à "})();") et collez-le dans la console

console.log('%c🔍 DIAGNOSTIC USERNAME', 'color: #00ffc3; font-size: 16px; font-weight: bold;');
console.log('='.repeat(80));

// 1. localStorage
const pendingLS = localStorage.getItem('pendingRegisterDataForGoogle');
const currentUserLS = localStorage.getItem('currentUser');

console.log('\n📦 LOCALSTORAGE:');
if (pendingLS) {
  const p = JSON.parse(pendingLS);
  console.log('  ✅ pendingRegisterDataForGoogle trouvé');
  console.log('     username:', p.username || '❌ MANQUANT');
  console.log('     email:', p.email || '❌ MANQUANT');
  console.log('     hasPhotoData:', !!p.photoData);
  console.log('     (complet):', p);
} else {
  console.log('  ❌ pendingRegisterDataForGoogle: NON TROUVÉ');
}

if (currentUserLS) {
  const c = JSON.parse(currentUserLS);
  console.log('  ✅ currentUser trouvé');
  console.log('     username:', c.username || '❌ MANQUANT');
  console.log('     email:', c.email || '❌ MANQUANT');
} else {
  console.log('  ❌ currentUser: NON TROUVÉ');
}

// 2. sessionStorage
const pendingSS = sessionStorage.getItem('pendingRegisterDataForGoogle');
const currentUserSS = sessionStorage.getItem('currentUser');

console.log('\n📦 SESSIONSTORAGE:');
if (pendingSS) {
  const p = JSON.parse(pendingSS);
  console.log('  ✅ pendingRegisterDataForGoogle trouvé');
  console.log('     username:', p.username || '❌ MANQUANT');
  console.log('     (complet):', p);
} else {
  console.log('  ❌ pendingRegisterDataForGoogle: NON TROUVÉ');
}

if (currentUserSS) {
  const c = JSON.parse(currentUserSS);
  console.log('  ✅ currentUser trouvé');
  console.log('     username:', c.username || '❌ MANQUANT');
} else {
  console.log('  ❌ currentUser: NON TROUVÉ');
}

// 3. window.currentUser
console.log('\n🌐 WINDOW.CURRENTUSER:');
if (window.currentUser) {
  console.log('  ✅ window.currentUser existe');
  console.log('     username:', window.currentUser.username || '❌ MANQUANT');
  console.log('     email:', window.currentUser.email || '❌ MANQUANT');
  console.log('     name:', window.currentUser.name || '❌ MANQUANT');
  console.log('     firstName:', window.currentUser.firstName || '❌ MANQUANT');
  const isValid = window.currentUser.username && 
                  window.currentUser.username !== 'null' && 
                  window.currentUser.username !== '' &&
                  !window.currentUser.username.includes('@');
  console.log('     isValid:', isValid ? '✅ VALIDE' : '❌ INVALIDE');
  console.log('     (complet):', window.currentUser);
} else {
  console.log('  ❌ window.currentUser N\'EXISTE PAS');
}

// 4. window.pendingRegisterData
console.log('\n🌐 WINDOW.PENDINGREGISTERDATA:');
if (window.pendingRegisterData) {
  console.log('  ✅ window.pendingRegisterData existe');
  console.log('     username:', window.pendingRegisterData.username || '❌ MANQUANT');
  console.log('     (complet):', window.pendingRegisterData);
} else {
  console.log('  ❌ window.pendingRegisterData N\'EXISTE PAS');
}

// 5. getUserDisplayName
console.log('\n👤 GETUSERDISPLAYNAME:');
if (typeof getUserDisplayName === 'function') {
  if (window.currentUser) {
    const displayName = getUserDisplayName(window.currentUser);
    console.log('  ✅ Fonction disponible');
    console.log('     Résultat:', displayName);
    const source = window.currentUser.username && !window.currentUser.username.includes('@') ? 'username' :
                   window.currentUser.firstName ? 'firstName' :
                   window.currentUser.name ? 'name' :
                   window.currentUser.email ? 'email (split)' : 'Utilisateur';
    console.log('     Source utilisée:', source);
  } else {
    console.log('  ⚠️ window.currentUser n\'existe pas');
  }
} else {
  console.log('  ❌ getUserDisplayName N\'EST PAS DÉFINIE');
}

// 6. ProfileValidator
console.log('\n🔧 PROFILEVALIDATOR:');
if (window.ProfileValidator) {
  console.log('  ✅ ProfileValidator existe');
  if (window.ProfileValidator.getValidUsername && window.currentUser) {
    const savedPendingData = pendingLS ? JSON.parse(pendingLS) : 
                            pendingSS ? JSON.parse(pendingSS) : 
                            window.pendingRegisterData || {};
    const validUsername = window.ProfileValidator.getValidUsername(
      window.currentUser,
      savedPendingData,
      {}
    );
    console.log('     getValidUsername():', validUsername);
  }
} else {
  console.log('  ❌ ProfileValidator N\'EXISTE PAS');
}

// 7. Bloc compte
console.log('\n📱 BLOC COMPTE (DOM):');
const accountBtn = document.getElementById('account-topbar-btn');
const accountName = document.getElementById('account-name');
if (accountBtn) {
  console.log('  ✅ account-topbar-btn trouvé');
  console.log('     textContent:', accountBtn.textContent);
} else {
  console.log('  ❌ account-topbar-btn NON TROUVÉ');
}

if (accountName) {
  console.log('  ✅ account-name trouvé');
  console.log('     textContent:', accountName.textContent);
} else {
  console.log('  ❌ account-name NON TROUVÉ');
}

// 8. Résumé
console.log('\n📊 RÉSUMÉ:');
let found = false;
let source = '';
let value = '';

if (pendingLS) {
  const p = JSON.parse(pendingLS);
  if (p.username && p.username !== 'null' && p.username !== '' && !p.username.includes('@')) {
    found = true;
    source = 'localStorage (pendingRegisterDataForGoogle)';
    value = p.username;
  }
}

if (!found && pendingSS) {
  const p = JSON.parse(pendingSS);
  if (p.username && p.username !== 'null' && p.username !== '' && !p.username.includes('@')) {
    found = true;
    source = 'sessionStorage (pendingRegisterDataForGoogle)';
    value = p.username;
  }
}

if (!found && window.pendingRegisterData) {
  if (window.pendingRegisterData.username && 
      window.pendingRegisterData.username !== 'null' && 
      window.pendingRegisterData.username !== '' &&
      !window.pendingRegisterData.username.includes('@')) {
    found = true;
    source = 'window.pendingRegisterData';
    value = window.pendingRegisterData.username;
  }
}

if (!found && window.currentUser) {
  if (window.currentUser.username && 
      window.currentUser.username !== 'null' && 
      window.currentUser.username !== '' &&
      !window.currentUser.username.includes('@')) {
    found = true;
    source = 'window.currentUser';
    value = window.currentUser.username;
  }
}

if (found) {
  console.log('  ✅ Username trouvé:', value, 'dans', source);
} else {
  console.log('  ❌ Aucun username valide trouvé');
  console.log('     Le système utilisera probablement l\'email ou "Utilisateur"');
}

if (accountName) {
  console.log('  📱 Affiché dans le bloc compte:', accountName.textContent);
  if (found && accountName.textContent !== value) {
    console.log('  ⚠️ PROBLÈME: Le username trouvé ne correspond pas à celui affiché !');
    console.log('     Trouvé:', value);
    console.log('     Affiché:', accountName.textContent);
  } else if (found) {
    console.log('  ✅ Le username affiché correspond à celui trouvé');
  }
}

console.log('\n💡 Commandes utiles:');
console.log('  - window.updateAccountBlockLegitimately() : Forcer la mise à jour');
console.log('  - getUserDisplayName(window.currentUser) : Voir le username qui sera affiché');
console.log('  - localStorage.getItem("pendingRegisterDataForGoogle") : Voir les données du formulaire');
console.log('  - window.currentUser : Voir l\'utilisateur actuel');

console.log('\n' + '='.repeat(80));
console.log('%c✅ Diagnostic terminé', 'color: #22c55e; font-weight: bold;');
