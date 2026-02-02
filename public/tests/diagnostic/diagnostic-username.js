/**
 * @fileoverview Script de diagnostic pour vérifier le username
 * Usage: Copier-coller dans la console du navigateur
 */

(function() {
  'use strict';
  
  console.log('%c🔍 DIAGNOSTIC USERNAME - Vérification complète', 'color: #00ffc3; font-size: 16px; font-weight: bold;');
  console.log('='.repeat(80));
  
  // 1. Vérifier localStorage
  console.log('\n%c1️⃣ LOCALSTORAGE', 'color: #3b82f6; font-weight: bold;');
  const pendingDataLocalStorage = localStorage.getItem('pendingRegisterDataForGoogle');
  if (pendingDataLocalStorage) {
    try {
      const parsed = JSON.parse(pendingDataLocalStorage);
      console.log('✅ pendingRegisterDataForGoogle trouvé:', {
        username: parsed.username || 'MANQUANT',
        hasPhotoData: !!parsed.photoData,
        photoDataLength: parsed.photoData ? parsed.photoData.length : 0,
        allKeys: Object.keys(parsed)
      });
    } catch (e) {
      console.error('❌ Erreur parsing localStorage:', e);
    }
  } else {
    console.warn('⚠️ pendingRegisterDataForGoogle NON TROUVÉ dans localStorage');
  }
  
  const currentUserLocalStorage = localStorage.getItem('currentUser');
  if (currentUserLocalStorage) {
    try {
      const parsed = JSON.parse(currentUserLocalStorage);
      console.log('✅ currentUser trouvé dans localStorage:', {
        username: parsed.username || 'MANQUANT',
        email: parsed.email || 'MANQUANT',
        hasPhotoData: !!parsed.photoData,
        allKeys: Object.keys(parsed)
      });
    } catch (e) {
      console.error('❌ Erreur parsing currentUser localStorage:', e);
    }
  } else {
    console.warn('⚠️ currentUser NON TROUVÉ dans localStorage');
  }
  
  // 2. Vérifier sessionStorage
  console.log('\n%c2️⃣ SESSIONSTORAGE', 'color: #3b82f6; font-weight: bold;');
  const pendingDataSessionStorage = sessionStorage.getItem('pendingRegisterDataForGoogle');
  if (pendingDataSessionStorage) {
    try {
      const parsed = JSON.parse(pendingDataSessionStorage);
      console.log('✅ pendingRegisterDataForGoogle trouvé:', {
        username: parsed.username || 'MANQUANT',
        hasPhotoData: !!parsed.photoData,
        photoDataLength: parsed.photoData ? parsed.photoData.length : 0,
        allKeys: Object.keys(parsed)
      });
    } catch (e) {
      console.error('❌ Erreur parsing sessionStorage:', e);
    }
  } else {
    console.warn('⚠️ pendingRegisterDataForGoogle NON TROUVÉ dans sessionStorage');
  }
  
  const currentUserSessionStorage = sessionStorage.getItem('currentUser');
  if (currentUserSessionStorage) {
    try {
      const parsed = JSON.parse(currentUserSessionStorage);
      console.log('✅ currentUser trouvé dans sessionStorage:', {
        username: parsed.username || 'MANQUANT',
        email: parsed.email || 'MANQUANT',
        hasPhotoData: !!parsed.photoData,
        allKeys: Object.keys(parsed)
      });
    } catch (e) {
      console.error('❌ Erreur parsing currentUser sessionStorage:', e);
    }
  } else {
    console.warn('⚠️ currentUser NON TROUVÉ dans sessionStorage');
  }
  
  // 3. Vérifier window.currentUser
  console.log('\n%c3️⃣ WINDOW.CURRENTUSER', 'color: #3b82f6; font-weight: bold;');
  if (typeof window !== 'undefined' && window.currentUser) {
    console.log('✅ window.currentUser existe:', {
      username: window.currentUser.username || 'MANQUANT',
      email: window.currentUser.email || 'MANQUANT',
      name: window.currentUser.name || 'MANQUANT',
      firstName: window.currentUser.firstName || 'MANQUANT',
      lastName: window.currentUser.lastName || 'MANQUANT',
      hasPhotoData: !!window.currentUser.photoData,
      photoDataLength: window.currentUser.photoData ? window.currentUser.photoData.length : 0,
      isLoggedIn: window.currentUser.isLoggedIn || false,
      allKeys: Object.keys(window.currentUser)
    });
    
    // Vérifier si le username est valide
    const username = window.currentUser.username;
    if (username && username !== 'null' && username !== '' && !username.includes('@')) {
      console.log('✅ Username VALIDE:', username);
    } else {
      console.warn('⚠️ Username INVALIDE ou MANQUANT:', username);
    }
  } else {
    console.warn('⚠️ window.currentUser N\'EXISTE PAS');
  }
  
  // 4. Vérifier window.pendingRegisterData
  console.log('\n%c4️⃣ WINDOW.PENDINGREGISTERDATA', 'color: #3b82f6; font-weight: bold;');
  if (typeof window !== 'undefined' && window.pendingRegisterData) {
    console.log('✅ window.pendingRegisterData existe:', {
      username: window.pendingRegisterData.username || 'MANQUANT',
      hasPhotoData: !!window.pendingRegisterData.photoData,
      photoDataLength: window.pendingRegisterData.photoData ? window.pendingRegisterData.photoData.length : 0,
      allKeys: Object.keys(window.pendingRegisterData)
    });
  } else {
    console.warn('⚠️ window.pendingRegisterData N\'EXISTE PAS');
  }
  
  // 5. Vérifier getUserDisplayName
  console.log('\n%c5️⃣ GETUSERDISPLAYNAME', 'color: #3b82f6; font-weight: bold;');
  if (typeof getUserDisplayName === 'function') {
    if (window.currentUser) {
      const displayName = getUserDisplayName(window.currentUser);
      console.log('✅ getUserDisplayName(window.currentUser):', displayName);
      console.log('   Username utilisé:', window.currentUser.username || 'MANQUANT');
      console.log('   Email utilisé:', window.currentUser.email || 'MANQUANT');
    } else {
      console.warn('⚠️ window.currentUser n\'existe pas, impossible de tester getUserDisplayName');
    }
  } else {
    console.warn('⚠️ getUserDisplayName N\'EST PAS DÉFINIE');
  }
  
  // 6. Vérifier ProfileValidator
  console.log('\n%c6️⃣ PROFILEVALIDATOR', 'color: #3b82f6; font-weight: bold;');
  if (typeof window !== 'undefined' && window.ProfileValidator) {
    console.log('✅ ProfileValidator existe:', {
      isValidUsername: typeof window.ProfileValidator.isValidUsername === 'function',
      getValidUsername: typeof window.ProfileValidator.getValidUsername === 'function',
      validateRequiredFields: typeof window.ProfileValidator.validateRequiredFields === 'function'
    });
    
    if (window.currentUser) {
      const savedPendingData = pendingDataLocalStorage ? JSON.parse(pendingDataLocalStorage) : 
                              pendingDataSessionStorage ? JSON.parse(pendingDataSessionStorage) : 
                              window.pendingRegisterData || {};
      
      if (window.ProfileValidator.getValidUsername) {
        const validUsername = window.ProfileValidator.getValidUsername(
          window.currentUser,
          savedPendingData,
          {}
        );
        console.log('✅ ProfileValidator.getValidUsername():', validUsername);
      }
    }
  } else {
    console.warn('⚠️ ProfileValidator N\'EST PAS DÉFINI');
  }
  
  // 7. Vérifier le bloc compte dans le DOM
  console.log('\n%c7️⃣ BLOC COMPTE (DOM)', 'color: #3b82f6; font-weight: bold;');
  const accountBtn = document.getElementById('account-topbar-btn');
  const accountName = document.getElementById('account-name');
  if (accountBtn) {
    console.log('✅ account-topbar-btn trouvé:', {
      textContent: accountBtn.textContent,
      innerHTML: accountBtn.innerHTML,
      display: window.getComputedStyle(accountBtn).display,
      visibility: window.getComputedStyle(accountBtn).visibility
    });
  } else {
    console.warn('⚠️ account-topbar-btn NON TROUVÉ');
  }
  
  if (accountName) {
    console.log('✅ account-name trouvé:', {
      textContent: accountName.textContent,
      innerHTML: accountName.innerHTML
    });
  } else {
    console.warn('⚠️ account-name NON TROUVÉ');
  }
  
  // 8. Vérifier updateAccountBlockLegitimately
  console.log('\n%c8️⃣ UPDATEACCOUNTBLOCKLEGITIMATELY', 'color: #3b82f6; font-weight: bold;');
  if (typeof window !== 'undefined' && typeof window.updateAccountBlockLegitimately === 'function') {
    console.log('✅ updateAccountBlockLegitimately existe');
    console.log('   Pour tester: window.updateAccountBlockLegitimately()');
  } else {
    console.warn('⚠️ updateAccountBlockLegitimately N\'EST PAS DÉFINIE');
  }
  
  // 9. Résumé et recommandations
  console.log('\n%c📊 RÉSUMÉ', 'color: #22c55e; font-size: 14px; font-weight: bold;');
  console.log('='.repeat(80));
  
  let usernameFound = false;
  let usernameSource = '';
  
  // Vérifier les sources dans l'ordre de priorité
  if (pendingDataLocalStorage) {
    const parsed = JSON.parse(pendingDataLocalStorage);
    if (parsed.username && parsed.username !== 'null' && !parsed.username.includes('@')) {
      usernameFound = true;
      usernameSource = 'localStorage (pendingRegisterDataForGoogle)';
      console.log('✅ Username trouvé dans:', usernameSource, '→', parsed.username);
    }
  }
  
  if (!usernameFound && pendingDataSessionStorage) {
    const parsed = JSON.parse(pendingDataSessionStorage);
    if (parsed.username && parsed.username !== 'null' && !parsed.username.includes('@')) {
      usernameFound = true;
      usernameSource = 'sessionStorage (pendingRegisterDataForGoogle)';
      console.log('✅ Username trouvé dans:', usernameSource, '→', parsed.username);
    }
  }
  
  if (!usernameFound && window.pendingRegisterData) {
    if (window.pendingRegisterData.username && 
        window.pendingRegisterData.username !== 'null' && 
        !window.pendingRegisterData.username.includes('@')) {
      usernameFound = true;
      usernameSource = 'window.pendingRegisterData';
      console.log('✅ Username trouvé dans:', usernameSource, '→', window.pendingRegisterData.username);
    }
  }
  
  if (!usernameFound && window.currentUser) {
    if (window.currentUser.username && 
        window.currentUser.username !== 'null' && 
        !window.currentUser.username.includes('@')) {
      usernameFound = true;
      usernameSource = 'window.currentUser';
      console.log('✅ Username trouvé dans:', usernameSource, '→', window.currentUser.username);
    }
  }
  
  if (!usernameFound) {
    console.warn('❌ Aucun username valide trouvé dans les sources vérifiées');
    console.log('   Le système utilisera probablement l\'email ou "Utilisateur"');
  }
  
  // Afficher le username actuellement affiché
  if (accountName) {
    console.log('\n%c📱 USERNAME ACTUELLEMENT AFFICHÉ:', 'color: #f59e0b; font-weight: bold;');
    console.log('   Dans le bloc compte:', accountName.textContent);
  }
  
  console.log('\n%c💡 COMMANDES UTILES', 'color: #8b5cf6; font-weight: bold;');
  console.log('   - window.updateAccountBlockLegitimately() : Forcer la mise à jour du bloc compte');
  console.log('   - getUserDisplayName(window.currentUser) : Voir le username qui sera affiché');
  console.log('   - localStorage.getItem("pendingRegisterDataForGoogle") : Voir les données du formulaire');
  console.log('   - window.currentUser : Voir l\'utilisateur actuel');
  
  console.log('\n' + '='.repeat(80));
  console.log('%c✅ Diagnostic terminé', 'color: #22c55e; font-weight: bold;');
})();
