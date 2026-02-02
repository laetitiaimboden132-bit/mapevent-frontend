// ============================================
// TEST DIAGNOSTIC INSCRIPTION - Copiez dans la console
// ============================================

(function() {
  console.clear();
  console.log('%c🔍 ===== DIAGNOSTIC INSCRIPTION COMPLET =====', 'font-size: 18px; font-weight: bold; color: #00ffc3;');
  console.log('');
  
  // 1. VÉRIFIER LES INDICATEURS D'ÉTAPES
  console.log('%c📋 INDICATEURS D\'ÉTAPES:', 'font-weight: bold; color: #3b82f6; font-size: 14px;');
  const progressSteps = document.querySelectorAll('.progress-step');
  console.log('  Nombre d\'étapes trouvées:', progressSteps.length);
  
  if (progressSteps.length === 0) {
    console.warn('  ⚠️ AUCUNE ÉTAPE TROUVÉE - Le formulaire n\'est peut-être pas ouvert');
  } else {
    progressSteps.forEach((step, index) => {
      const stepNum = step.getAttribute('data-step');
      const computedStyle = window.getComputedStyle(step);
      const bgColor = computedStyle.backgroundColor;
      const isActive = bgColor.includes('rgb(34, 197, 94)') || bgColor.includes('rgba(34, 197, 94');
      const hasBorder = computedStyle.borderWidth !== '0px' && computedStyle.borderWidth !== '';
      const hasShadow = computedStyle.boxShadow !== 'none';
      
      const circle = step.querySelector('div[style*="border-radius:50%"]');
      const circleContent = circle ? circle.textContent.trim() : '?';
      
      console.log(`  Étape ${stepNum}:`, {
        texte: step.textContent.trim().substring(0, 25),
        cercle: circleContent,
        active: isActive ? '✅ ACTIVE' : '❌ inactive',
        border: hasBorder ? '✅ Avec bordure' : '❌ Sans bordure',
        shadow: hasShadow ? '✅ Avec ombre' : '❌ Sans ombre',
        backgroundColor: bgColor.substring(0, 30)
      });
    });
  }
  
  // 2. VÉRIFIER LE MODAL ACTUEL
  console.log('');
  console.log('%c🪟 MODAL ACTUEL:', 'font-weight: bold; color: #3b82f6; font-size: 14px;');
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
    
    if (hasProgress) {
      const progressDiv = authModal.querySelector('.registration-progress');
      console.log('  Position de l\'indicateur:', progressDiv ? '✅ Trouvé' : '❌ Non trouvé');
      if (progressDiv) {
        const computedStyle = window.getComputedStyle(progressDiv);
        console.log('  Display:', computedStyle.display);
        console.log('  Visibility:', computedStyle.visibility);
        console.log('  Opacity:', computedStyle.opacity);
        console.log('  Margin-bottom:', computedStyle.marginBottom);
      }
    }
    
    const title = authModal.querySelector('h2');
    if (title) {
      console.log('  Titre du modal:', title.textContent.trim().substring(0, 50));
    }
  }
  
  if (backdrop) {
    const computedStyle = window.getComputedStyle(backdrop);
    console.log('  Backdrop display:', computedStyle.display);
    console.log('  Backdrop visibility:', computedStyle.visibility);
    console.log('  Backdrop opacity:', computedStyle.opacity);
  }
  
  // 3. VÉRIFIER LES DONNÉES D'INSCRIPTION
  console.log('');
  console.log('%c📝 DONNÉES D\'INSCRIPTION:', 'font-weight: bold; color: #3b82f6; font-size: 14px;');
  console.log('  pendingRegisterData:', window.pendingRegisterData ? '✅ Présent' : '❌ Absent');
  if (window.pendingRegisterData) {
    console.log('  Email:', window.pendingRegisterData.email || '❌ undefined');
    console.log('  Username:', window.pendingRegisterData.username || '❌ undefined');
    console.log('  photoData:', window.pendingRegisterData.photoData ? `✅ Présent (${window.pendingRegisterData.photoData.length} chars)` : '❌ Absent');
  }
  
  // 4. VÉRIFIER LES TOKENS RETOURNÉS PAR LE BACKEND
  console.log('');
  console.log('%c🔑 TOKENS ET CONNEXION:', 'font-weight: bold; color: #3b82f6; font-size: 14px;');
  console.log('  Pour tester la création de compte:');
  console.log('    createAccountWithoutVerification(window.pendingRegisterData)');
  console.log('');
  console.log('  Pour vérifier les tokens après création:');
  console.log('    const tokens = localStorage.getItem("cognito_tokens");');
  console.log('    console.log("Tokens:", tokens ? JSON.parse(tokens) : "Absent");');
  
  // 5. VÉRIFIER L'ÉTAT DE L'UTILISATEUR
  console.log('');
  console.log('%c👤 ÉTAT UTILISATEUR:', 'font-weight: bold; color: #3b82f6; font-size: 14px;');
  console.log('  currentUser:', window.currentUser ? '✅ Présent' : '❌ Absent');
  if (window.currentUser) {
    console.log('  isLoggedIn:', window.currentUser.isLoggedIn ? '✅ Oui' : '❌ Non');
    console.log('  username:', window.currentUser.username || '❌ undefined');
    console.log('  email:', window.currentUser.email || '❌ undefined');
  }
  
  // 6. COMMANDES DE TEST
  console.log('');
  console.log('%c🧪 COMMANDES DE TEST:', 'font-weight: bold; color: #f59e0b; font-size: 14px;');
  console.log('%c  Pour afficher le choix de vérification:', 'color: #00ffc3;');
  console.log('    showVerificationChoice()');
  console.log('');
  console.log('%c  Pour créer un compte sans vérification:', 'color: #00ffc3;');
  console.log('    createAccountWithoutVerification(window.pendingRegisterData)');
  console.log('');
  console.log('%c  Pour vérifier les tokens:', 'color: #00ffc3;');
  console.log('    const tokens = localStorage.getItem("cognito_tokens");');
  console.log('    if (tokens) { const parsed = JSON.parse(tokens); console.log("access_token:", parsed.access_token ? "✅" : "❌"); }');
  console.log('');
  console.log('%c  Pour vérifier le modal actuel:', 'color: #00ffc3;');
  console.log('    const modal = document.getElementById("authModal");');
  console.log('    console.log("Modal:", modal);');
  console.log('    console.log("Mode:", modal?.getAttribute("data-mode"));');
  console.log('    console.log("Titre:", modal?.querySelector("h2")?.textContent);');
  console.log('');
  console.log('%c  Pour forcer l\'affichage du modal:', 'color: #00ffc3;');
  console.log('    const backdrop = document.getElementById("publish-modal-backdrop");');
  console.log('    if (backdrop) { backdrop.style.display = "flex"; backdrop.style.visibility = "visible"; backdrop.style.opacity = "1"; }');
  console.log('    const modal = document.getElementById("publish-modal-inner") || document.getElementById("authModal");');
  console.log('    if (modal) { modal.style.display = "block"; modal.style.visibility = "visible"; modal.style.opacity = "1"; }');
  
  console.log('');
  console.log('%c✅ ===== FIN DU DIAGNOSTIC =====', 'font-size: 18px; font-weight: bold; color: #22c55e;');
  console.log('');
  
  // Retourner un objet avec toutes les infos
  return {
    progressSteps: Array.from(progressSteps).map(s => ({
      step: s.getAttribute('data-step'),
      text: s.textContent.trim(),
      circle: s.querySelector('div[style*="border-radius:50%"]')?.textContent.trim(),
      active: window.getComputedStyle(s).backgroundColor.includes('rgb(34, 197, 94)')
    })),
    modal: {
      authModal: !!authModal,
      publishModalInner: !!publishModalInner,
      backdrop: !!backdrop,
      mode: authModal?.getAttribute('data-mode'),
      hasProgress: authModal?.querySelector('.registration-progress') !== null,
      title: authModal?.querySelector('h2')?.textContent.trim()
    },
    data: {
      pendingRegisterData: !!window.pendingRegisterData,
      currentUser: !!window.currentUser,
      isLoggedIn: window.currentUser?.isLoggedIn
    }
  };
})();
