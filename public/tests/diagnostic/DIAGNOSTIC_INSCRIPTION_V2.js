// ============================================
// DIAGNOSTIC COMPLET V2 - INSCRIPTION ET VÉRIFICATION
// ============================================
// Copiez-collez ce script dans la console du navigateur (F12)

(function() {
  console.clear();
  console.log('%c🔍 ===== DIAGNOSTIC INSCRIPTION V2 =====', 'font-size: 16px; font-weight: bold; color: #00ffc3;');
  console.log('');
  
  // 1. VÉRIFIER LES ÉTAPES DU FORMULAIRE
  console.log('%c📋 INDICATEUR D\'ÉTAPES:', 'font-weight: bold; color: #3b82f6;');
  const progressSteps = document.querySelectorAll('.progress-step');
  console.log('  Nombre d\'étapes trouvées:', progressSteps.length);
  if (progressSteps.length === 0) {
    console.warn('  ⚠️ AUCUNE ÉTAPE TROUVÉE - Le formulaire n\'est peut-être pas ouvert');
  } else {
    progressSteps.forEach((step, index) => {
      const stepNum = step.getAttribute('data-step');
      const computedStyle = window.getComputedStyle(step);
      const isActive = computedStyle.backgroundColor.includes('rgb(34, 197, 94)') || step.style.background.includes('rgba(34,197,94');
      console.log(`  Étape ${stepNum}:`, {
        texte: step.textContent.trim().substring(0, 30),
        active: isActive ? '✅' : '❌',
        display: computedStyle.display,
        backgroundColor: computedStyle.backgroundColor
      });
    });
  }
  
  // 2. VÉRIFIER LE MODAL ACTUEL
  console.log('');
  console.log('%c🪟 MODAL ACTUEL:', 'font-weight: bold; color: #3b82f6;');
  const authModal = document.getElementById('authModal');
  const publishModalInner = document.getElementById('publish-modal-inner');
  const backdrop = document.getElementById('publish-modal-backdrop');
  
  console.log('  authModal trouvé:', authModal ? '✅' : '❌');
  console.log('  publish-modal-inner trouvé:', publishModalInner ? '✅' : '❌');
  console.log('  backdrop trouvé:', backdrop ? '✅' : '❌');
  
  if (authModal) {
    const mode = authModal.getAttribute('data-mode');
    console.log('  Mode du modal:', mode || 'non défini');
    const hasProgress = authModal.querySelector('.registration-progress') !== null;
    console.log('  Indicateur d\'étapes dans modal:', hasProgress ? '✅ Présent' : '❌ Absent');
    console.log('  Contenu modal (premiers 300 chars):', authModal.innerHTML.substring(0, 300));
  }
  
  if (backdrop) {
    const computedStyle = window.getComputedStyle(backdrop);
    console.log('  Backdrop display:', computedStyle.display);
    console.log('  Backdrop visibility:', computedStyle.visibility);
    console.log('  Backdrop opacity:', computedStyle.opacity);
    console.log('  Backdrop z-index:', computedStyle.zIndex);
  }
  
  // 3. VÉRIFIER LES DONNÉES D'INSCRIPTION
  console.log('');
  console.log('%c📝 DONNÉES D\'INSCRIPTION:', 'font-weight: bold; color: #3b82f6;');
  console.log('  pendingRegisterData:', window.pendingRegisterData ? '✅ Présent' : '❌ Absent');
  if (window.pendingRegisterData) {
    console.log('  Email:', window.pendingRegisterData.email || '❌ undefined');
    console.log('  Username:', window.pendingRegisterData.username || '❌ undefined');
    console.log('  photoData:', window.pendingRegisterData.photoData ? `✅ Présent (${window.pendingRegisterData.photoData.length} chars)` : '❌ Absent');
    console.log('  password:', window.pendingRegisterData.password ? '✅ Présent' : '❌ Absent');
  }
  console.log('  registerData:', window.registerData ? '✅ Présent' : '❌ Absent');
  if (window.registerData) {
    console.log('  Email:', window.registerData.email || '❌ undefined');
    console.log('  Username:', window.registerData.username || '❌ undefined');
    console.log('  photoData:', window.registerData.photoData ? `✅ Présent` : '❌ Absent');
  }
  
  // 4. VÉRIFIER LES FONCTIONS DISPONIBLES
  console.log('');
  console.log('%c🔧 FONCTIONS DISPONIBLES:', 'font-weight: bold; color: #3b82f6;');
  const functions = [
    'showVerificationChoice',
    'window.showVerificationChoice',
    'handleVerificationChoice',
    'window.handleVerificationChoice',
    'createAccountWithoutVerification',
    'askRememberMeAndConnect',
    'connectUser',
    'closeAuthModal',
    'updateAuthUI',
    'updateAccountBlockLegitimately'
  ];
  
  functions.forEach(funcName => {
    const parts = funcName.split('.');
    let func;
    if (parts.length === 1) {
      func = window[funcName];
    } else {
      func = window[parts[1]];
    }
    const available = typeof func === 'function' ? '✅' : '❌';
    console.log(`  ${funcName}:`, available);
  });
  
  // 5. VÉRIFIER L'ÉTAT DE L'UTILISATEUR
  console.log('');
  console.log('%c👤 ÉTAT UTILISATEUR:', 'font-weight: bold; color: #3b82f6;');
  console.log('  currentUser:', window.currentUser ? '✅ Présent' : '❌ Absent');
  if (window.currentUser) {
    console.log('  isLoggedIn:', window.currentUser.isLoggedIn ? '✅ Oui' : '❌ Non');
    console.log('  username:', window.currentUser.username || '❌ undefined');
    console.log('  email:', window.currentUser.email || '❌ undefined');
    console.log('  photoData:', window.currentUser.photoData ? `✅ Présent` : '❌ Absent');
    console.log('  profile_photo_url:', window.currentUser.profile_photo_url ? '✅ Présent' : '❌ Absent');
  }
  
  // 6. VÉRIFIER LES TOKENS
  console.log('');
  console.log('%c🔑 TOKENS:', 'font-weight: bold; color: #3b82f6;');
  const token = window.getAuthToken ? window.getAuthToken() : null;
  console.log('  Token:', token ? `✅ Présent (${token.substring(0, 30)}...)` : '❌ Absent');
  const cognitoTokens = localStorage.getItem('cognito_tokens');
  if (cognitoTokens) {
    try {
      const parsed = JSON.parse(cognitoTokens);
      console.log('  cognito_tokens.access_token:', parsed.access_token ? '✅ Présent' : '❌ Absent');
    } catch(e) {
      console.log('  cognito_tokens:', '❌ Erreur parsing');
    }
  } else {
    console.log('  cognito_tokens:', '❌ Absent');
  }
  
  // 7. VÉRIFIER LES NOTIFICATIONS
  console.log('');
  console.log('%c🔔 NOTIFICATIONS:', 'font-weight: bold; color: #3b82f6;');
  console.log('  showNotification:', typeof showNotification === 'function' ? '✅ Disponible' : '❌ Non disponible');
  
  // 8. COMMANDES DE TEST
  console.log('');
  console.log('%c🧪 COMMANDES DE TEST:', 'font-weight: bold; color: #f59e0b;');
  console.log('%c  Pour afficher le choix de vérification:', 'color: #00ffc3;');
  console.log('    showVerificationChoice()');
  console.log('%c  Pour créer un compte sans vérification:', 'color: #00ffc3;');
  console.log('    createAccountWithoutVerification(window.pendingRegisterData)');
  console.log('%c  Pour tester la connexion:', 'color: #00ffc3;');
  console.log('    connectUser(window.currentUser, {access_token: "test", refresh_token: "test"}, true)');
  console.log('%c  Pour vérifier l\'état actuel:', 'color: #00ffc3;');
  console.log('    console.log("Modal:", document.getElementById("authModal"));');
  console.log('    console.log("Backdrop:", document.getElementById("publish-modal-backdrop"));');
  console.log('    console.log("pendingRegisterData:", window.pendingRegisterData);');
  console.log('    console.log("currentUser:", window.currentUser);');
  
  // 9. TEST AUTOMATIQUE DU FLUX
  console.log('');
  console.log('%c🔄 TEST AUTOMATIQUE DU FLUX:', 'font-weight: bold; color: #ef4444;');
  
  if (!window.pendingRegisterData) {
    console.warn('  ⚠️ pendingRegisterData absent - Le formulaire n\'a pas été soumis');
  } else {
    console.log('  ✅ pendingRegisterData présent - Le formulaire a été soumis');
    console.log('  Pour tester la création du compte:');
    console.log('    createAccountWithoutVerification(window.pendingRegisterData)');
  }
  
  if (!window.currentUser || !window.currentUser.isLoggedIn) {
    console.warn('  ⚠️ Utilisateur non connecté');
  } else {
    console.log('  ✅ Utilisateur connecté:', window.currentUser.username || window.currentUser.email);
  }
  
  console.log('');
  console.log('%c✅ ===== FIN DU DIAGNOSTIC =====', 'font-size: 16px; font-weight: bold; color: #22c55e;');
  console.log('');
  
  // Retourner un objet avec toutes les infos pour inspection
  return {
    progressSteps: Array.from(progressSteps).map(s => ({
      step: s.getAttribute('data-step'),
      text: s.textContent.trim(),
      active: window.getComputedStyle(s).backgroundColor.includes('rgb(34, 197, 94)')
    })),
    modal: {
      authModal: !!authModal,
      publishModalInner: !!publishModalInner,
      backdrop: !!backdrop,
      mode: authModal?.getAttribute('data-mode'),
      hasProgress: authModal?.querySelector('.registration-progress') !== null
    },
    data: {
      pendingRegisterData: !!window.pendingRegisterData,
      registerData: !!window.registerData,
      currentUser: !!window.currentUser,
      isLoggedIn: window.currentUser?.isLoggedIn
    },
    functions: {
      showVerificationChoice: typeof showVerificationChoice === 'function',
      handleVerificationChoice: typeof handleVerificationChoice === 'function',
      createAccountWithoutVerification: typeof createAccountWithoutVerification === 'function',
      connectUser: typeof connectUser === 'function'
    }
  };
})();
