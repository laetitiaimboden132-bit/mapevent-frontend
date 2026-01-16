// COPIEZ-COLLEZ TOUT CE QUI EST EN DESSOUS DANS LA CONSOLE (F12)
// (sans cette première ligne de commentaire)

console.log('=== VERIFICATION COMPLETE ===');

let okCount = 0;
let failCount = 0;

console.log('\n1. SCRIPTS CHARGES:');
const scripts = Array.from(document.querySelectorAll('script[src]'));
let authFound = false;

scripts.forEach(function(script) {
  const src = script.src;
  if (src.includes('auth.js')) {
    authFound = true;
    const version = src.match(/v=([^&]+)/);
    const versionStr = version ? version[1] : 'N/A';
    console.log('  OK auth.js trouve (v=' + versionStr + ')');
  } else if (src.includes('map_logic.js')) {
    const version = src.match(/v=([^&]+)/);
    const versionStr = version ? version[1] : 'N/A';
    if (versionStr.includes('20260107')) {
      console.error('  ATTENTION map_logic.js: v=' + versionStr + ' (ANCIENNE VERSION)');
    } else {
      console.log('  OK map_logic.js: v=' + versionStr);
    }
  }
});

if (!authFound) {
  console.error('  ERREUR auth.js NON TROUVE!');
  failCount++;
}

console.log('\n2. FONCTIONS AUTH:');
const funcs = ['openAuthModal', 'performLogin', 'performRegister', 'logout', 'loadSavedUser', 'closeAuthModal', 'getAuthToken', 'getRefreshToken', 'setAuthTokens', 'startGoogleLogin', 'handleCognitoCallbackIfPresent'];

funcs.forEach(function(func) {
  if (typeof window[func] === 'function') {
    console.log('  OK ' + func + '()');
    okCount++;
  } else {
    console.error('  ERREUR ' + func + '() - MANQUANTE');
    failCount++;
  }
});

console.log('\nResultat: ' + okCount + '/' + funcs.length + ' OK');

if (failCount === 0 && authFound) {
  console.log('\n=== TOUT EST CORRECT! ===');
} else {
  console.log('\n=== PROBLEMES DETECTES ===');
  if (!authFound) {
    console.log('Solution: Redeplyez avec .\\deploy-force-cache-bust.ps1');
  }
}
