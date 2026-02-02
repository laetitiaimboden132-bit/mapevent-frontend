// ============================================
// DIAGNOSTIC COMPLET - INSCRIPTION ET VÉRIFICATION
// ============================================
// Copiez-collez ce script dans la console du navigateur (F12)

console.log('\n🔍 ===== DIAGNOSTIC INSCRIPTION =====\n');

// 1. VÉRIFIER LES ÉTAPES DU FORMULAIRE
console.log('📋 INDICATEUR D\'ÉTAPES:');
const progressSteps = document.querySelectorAll('.progress-step');
console.log('  Nombre d\'étapes trouvées:', progressSteps.length);
progressSteps.forEach((step, index) => {
  const stepNum = step.getAttribute('data-step');
  const isActive = step.style.background.includes('rgba(34,197,94');
  console.log(`  Étape ${stepNum}:`, {
    texte: step.textContent.trim(),
    active: isActive ? '✅' : '❌',
    display: window.getComputedStyle(step).display
  });
});

// 2. VÉRIFIER LE MODAL ACTUEL
console.log('\n🪟 MODAL ACTUEL:');
const authModal = document.getElementById('authModal');
const publishModalInner = document.getElementById('publish-modal-inner');
const backdrop = document.getElementById('publish-modal-backdrop');
console.log('  authModal trouvé:', authModal ? '✅' : '❌');
console.log('  publish-modal-inner trouvé:', publishModalInner ? '✅' : '❌');
console.log('  backdrop trouvé:', backdrop ? '✅' : '❌');
if (authModal) {
  const mode = authModal.getAttribute('data-mode');
  console.log('  Mode du modal:', mode || 'non défini');
  console.log('  Contenu modal (premiers 200 chars):', authModal.innerHTML.substring(0, 200));
}
if (backdrop) {
  console.log('  Backdrop display:', window.getComputedStyle(backdrop).display);
  console.log('  Backdrop visibility:', window.getComputedStyle(backdrop).visibility);
  console.log('  Backdrop opacity:', window.getComputedStyle(backdrop).opacity);
}

// 3. VÉRIFIER LES DONNÉES D'INSCRIPTION
console.log('\n📝 DONNÉES D\'INSCRIPTION:');
console.log('  pendingRegisterData:', window.pendingRegisterData ? '✅ Présent' : '❌ Absent');
if (window.pendingRegisterData) {
  console.log('  Email:', window.pendingRegisterData.email || '❌ undefined');
  console.log('  Username:', window.pendingRegisterData.username || '❌ undefined');
  console.log('  photoData:', window.pendingRegisterData.photoData ? `✅ Présent (${window.pendingRegisterData.photoData.length} chars)` : '❌ Absent');
}
console.log('  registerData:', window.registerData ? '✅ Présent' : '❌ Absent');
if (window.registerData) {
  console.log('  Email:', window.registerData.email || '❌ undefined');
  console.log('  Username:', window.registerData.username || '❌ undefined');
}

// 4. VÉRIFIER LES FONCTIONS DISPONIBLES
console.log('\n🔧 FONCTIONS DISPONIBLES:');
console.log('  showVerificationChoice:', typeof showVerificationChoice === 'function' ? '✅' : '❌');
console.log('  window.showVerificationChoice:', typeof window.showVerificationChoice === 'function' ? '✅' : '❌');
console.log('  handleVerificationChoice:', typeof handleVerificationChoice === 'function' ? '✅' : '❌');
console.log('  window.handleVerificationChoice:', typeof window.handleVerificationChoice === 'function' ? '✅' : '❌');
console.log('  createAccountWithoutVerification:', typeof createAccountWithoutVerification === 'function' ? '✅' : '❌');
console.log('  askRememberMeAndConnect:', typeof askRememberMeAndConnect === 'function' ? '✅' : '❌');
console.log('  connectUser:', typeof connectUser === 'function' ? '✅' : '❌');
console.log('  closeAuthModal:', typeof closeAuthModal === 'function' ? '✅' : '❌');

// 5. VÉRIFIER L'ÉTAT DE L'UTILISATEUR
console.log('\n👤 ÉTAT UTILISATEUR:');
console.log('  currentUser:', window.currentUser ? '✅ Présent' : '❌ Absent');
if (window.currentUser) {
  console.log('  isLoggedIn:', window.currentUser.isLoggedIn ? '✅ Oui' : '❌ Non');
  console.log('  username:', window.currentUser.username || '❌ undefined');
  console.log('  email:', window.currentUser.email || '❌ undefined');
  console.log('  photoData:', window.currentUser.photoData ? `✅ Présent` : '❌ Absent');
}

// 6. VÉRIFIER LES TOKENS
console.log('\n🔑 TOKENS:');
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
console.log('\n🔔 NOTIFICATIONS:');
console.log('  showNotification:', typeof showNotification === 'function' ? '✅ Disponible' : '❌ Non disponible');

// 8. COMMANDES DE TEST
console.log('\n🧪 COMMANDES DE TEST:');
console.log('  Pour afficher le choix de vérification:');
console.log('    showVerificationChoice()');
console.log('  Pour créer un compte sans vérification:');
console.log('    createAccountWithoutVerification(window.pendingRegisterData)');
console.log('  Pour vérifier l\'état actuel:');
console.log('    console.log("Modal:", document.getElementById("authModal"));');
console.log('    console.log("Backdrop:", document.getElementById("publish-modal-backdrop"));');
console.log('    console.log("pendingRegisterData:", window.pendingRegisterData);');

console.log('\n✅ ===== FIN DU DIAGNOSTIC =====\n');
