// ============================================
// DIAGNOSTIC CONNEXION AUTOMATIQUE
// ============================================
// Copiez ce script dans la console APRÈS avoir créé un compte

(function() {
  console.clear();
  console.log('%c🔍 ===== DIAGNOSTIC CONNEXION AUTOMATIQUE =====', 'font-size: 18px; font-weight: bold; color: #00ffc3;');
  console.log('');
  
  // 1. VÉRIFIER LES TOKENS DANS LOCALSTORAGE/SESSIONSTORAGE
  console.log('%c🔑 TOKENS:', 'font-weight: bold; color: #3b82f6; font-size: 14px;');
  const cognitoTokens = localStorage.getItem('cognito_tokens');
  const sessionTokens = sessionStorage.getItem('cognito_tokens');
  const localAccessToken = localStorage.getItem('accessToken');
  const sessionAccessToken = sessionStorage.getItem('accessToken');
  
  console.log('  cognito_tokens (localStorage):', cognitoTokens ? '✅ Présent' : '❌ Absent');
  if (cognitoTokens) {
    try {
      const parsed = JSON.parse(cognitoTokens);
      console.log('    access_token:', parsed.access_token ? `✅ ${parsed.access_token.substring(0, 30)}...` : '❌ Absent');
      console.log('    refresh_token:', parsed.refresh_token ? `✅ ${parsed.refresh_token.substring(0, 30)}...` : '❌ Absent');
    } catch(e) {
      console.error('    Erreur parsing:', e);
    }
  }
  
  console.log('  cognito_tokens (sessionStorage):', sessionTokens ? '✅ Présent' : '❌ Absent');
  console.log('  accessToken (localStorage):', localAccessToken ? `✅ ${localAccessToken.substring(0, 30)}...` : '❌ Absent');
  console.log('  accessToken (sessionStorage):', sessionAccessToken ? `✅ ${sessionAccessToken.substring(0, 30)}...` : '❌ Absent');
  
  // 2. VÉRIFIER L'UTILISATEUR
  console.log('');
  console.log('%c👤 UTILISATEUR:', 'font-weight: bold; color: #3b82f6; font-size: 14px;');
  console.log('  currentUser:', window.currentUser ? '✅ Présent' : '❌ Absent');
  if (window.currentUser) {
    console.log('    isLoggedIn:', window.currentUser.isLoggedIn ? '✅ Oui' : '❌ Non');
    console.log('    username:', window.currentUser.username || '❌ undefined');
    console.log('    email:', window.currentUser.email || '❌ undefined');
    console.log('    id:', window.currentUser.id || '❌ undefined');
  }
  
  const localUser = localStorage.getItem('currentUser');
  const sessionUser = sessionStorage.getItem('currentUser');
  console.log('  currentUser (localStorage):', localUser ? '✅ Présent' : '❌ Absent');
  if (localUser) {
    try {
      const parsed = JSON.parse(localUser);
      console.log('    username:', parsed.username || '❌ undefined');
      console.log('    isLoggedIn:', parsed.isLoggedIn ? '✅ Oui' : '❌ Non');
    } catch(e) {
      console.error('    Erreur parsing:', e);
    }
  }
  console.log('  currentUser (sessionStorage):', sessionUser ? '✅ Présent' : '❌ Absent');
  
  // 3. VÉRIFIER LES DONNÉES D'INSCRIPTION
  console.log('');
  console.log('%c📝 DONNÉES INSCRIPTION:', 'font-weight: bold; color: #3b82f6; font-size: 14px;');
  console.log('  pendingRegisterData:', window.pendingRegisterData ? '✅ Présent' : '❌ Absent');
  if (window.pendingRegisterData) {
    console.log('    email:', window.pendingRegisterData.email || '❌ undefined');
    console.log('    username:', window.pendingRegisterData.username || '❌ undefined');
  }
  
  // 4. TESTER LA FONCTION getAuthToken
  console.log('');
  console.log('%c🧪 TEST getAuthToken:', 'font-weight: bold; color: #f59e0b; font-size: 14px;');
  if (typeof window.getAuthToken === 'function') {
    const token = window.getAuthToken();
    console.log('  Token récupéré:', token ? `✅ ${token.substring(0, 30)}...` : '❌ null/undefined');
  } else {
    console.log('  getAuthToken:', '❌ Fonction non disponible');
  }
  
  // 5. VÉRIFIER LE BLOC COMPTE
  console.log('');
  console.log('%c🎯 BLOC COMPTE:', 'font-weight: bold; color: #3b82f6; font-size: 14px;');
  const accountBtn = document.getElementById('account-topbar-btn');
  const accountName = document.getElementById('account-name');
  const accountAvatar = document.getElementById('account-avatar');
  
  console.log('  account-topbar-btn:', accountBtn ? '✅ Trouvé' : '❌ Non trouvé');
  console.log('  account-name:', accountName ? `✅ "${accountName.textContent.trim()}"` : '❌ Non trouvé');
  console.log('  account-avatar:', accountAvatar ? '✅ Trouvé' : '❌ Non trouvé');
  
  if (accountBtn) {
    const btnText = accountBtn.textContent.trim();
    console.log('    Texte du bouton:', btnText);
    console.log('    Est "Connexion"?', btnText === 'Connexion' ? '✅ Oui' : '❌ Non');
  }
  
  // 6. COMMANDES DE TEST
  console.log('');
  console.log('%c🧪 COMMANDES DE TEST:', 'font-weight: bold; color: #f59e0b; font-size: 14px;');
  console.log('%c  Pour forcer la connexion manuelle:', 'color: #00ffc3;');
  console.log('    const user = { id: "test", email: "test@test.com", username: "test", isLoggedIn: true };');
  console.log('    const tokens = { access_token: "test", refresh_token: "test" };');
  console.log('    connectUser(user, tokens, true);');
  console.log('');
  console.log('%c  Pour vérifier updateAccountBlockLegitimately:', 'color: #00ffc3;');
  console.log('    if (typeof updateAccountBlockLegitimately === "function") updateAccountBlockLegitimately();');
  console.log('');
  console.log('%c  Pour tester getAuthToken:', 'color: #00ffc3;');
  console.log('    window.getAuthToken()');
  console.log('');
  console.log('%c  Pour voir tous les tokens:', 'color: #00ffc3;');
  console.log('    console.log("localStorage cognito_tokens:", localStorage.getItem("cognito_tokens"));');
  console.log('    console.log("sessionStorage cognito_tokens:", sessionStorage.getItem("cognito_tokens"));');
  console.log('    console.log("localStorage currentUser:", localStorage.getItem("currentUser"));');
  console.log('    console.log("sessionStorage currentUser:", sessionStorage.getItem("currentUser"));');
  
  console.log('');
  console.log('%c✅ ===== FIN DU DIAGNOSTIC =====', 'font-size: 18px; font-weight: bold; color: #22c55e;');
  console.log('');
  
  // Retourner un objet avec toutes les infos
  return {
    tokens: {
      cognitoTokens: !!cognitoTokens,
      sessionTokens: !!sessionTokens,
      localAccessToken: !!localAccessToken,
      sessionAccessToken: !!sessionAccessToken
    },
    user: {
      currentUser: !!window.currentUser,
      isLoggedIn: window.currentUser?.isLoggedIn,
      username: window.currentUser?.username,
      localUser: !!localUser,
      sessionUser: !!sessionUser
    },
    accountBlock: {
      buttonFound: !!accountBtn,
      nameFound: !!accountName,
      avatarFound: !!accountAvatar,
      buttonText: accountBtn?.textContent.trim()
    }
  };
})();
