// Script pour vérifier si auth.js est chargé
// Copiez-collez dans la console (F12)

console.log('%c=== VÉRIFICATION AUTH.JS ===', 'color: #3b82f6; font-size: 16px; font-weight: bold;');
console.log('');

// 1. Vérifier si auth.js est dans les scripts chargés
console.log('1. SCRIPTS CHARGÉS:');
const scripts = Array.from(document.querySelectorAll('script[src]'));
let authFound = false;
let mapLogicFound = false;

scripts.forEach((script, index) => {
  const src = script.src;
  const isAuth = src.includes('auth.js');
  const isMapLogic = src.includes('map_logic.js');
  
  if (isAuth) {
    authFound = true;
    console.log(`  ✅ ${index + 1}. auth.js trouvé: ${src}`);
    const version = src.match(/v=([^&]+)/)?.[1];
    if (version) console.log(`     Version: ${version}`);
  } else if (isMapLogic) {
    mapLogicFound = true;
    console.log(`  ${index + 1}. map_logic.js: ${src}`);
    const version = src.match(/v=([^&]+)/)?.[1];
    if (version) console.log(`     Version: ${version}`);
  }
});

if (!authFound) {
  console.error('  ❌ auth.js NON TROUVÉ dans les scripts chargés!');
  console.error('     Vérifiez que <script src="auth.js"> est présent dans mapevent.html');
}

console.log('');

// 2. Vérifier l'ordre de chargement
console.log('2. ORDRE DE CHARGEMENT:');
const authScript = scripts.find(s => s.src.includes('auth.js'));
const mapLogicScript = scripts.find(s => s.src.includes('map_logic.js'));

if (authScript && mapLogicScript) {
  const authIndex = scripts.indexOf(authScript);
  const mapLogicIndex = scripts.indexOf(mapLogicScript);
  
  if (authIndex < mapLogicIndex) {
    console.log('  ✅ Ordre correct: auth.js avant map_logic.js');
  } else {
    console.error('  ❌ Ordre incorrect: auth.js est chargé APRÈS map_logic.js!');
    console.error('     auth.js doit être chargé AVANT map_logic.js');
  }
} else {
  console.warn('  ⚠️ Impossible de vérifier l\'ordre (scripts non trouvés)');
}

console.log('');

// 3. Vérifier les fonctions AUTH
console.log('3. FONCTIONS AUTH:');
const authFunctions = {
  'openAuthModal': 'auth.js',
  'performLogin': 'auth.js',
  'performRegister': 'auth.js',
  'logout': 'auth.js',
  'loadSavedUser': 'auth.js',
  'closeAuthModal': 'auth.js',
  'getAuthToken': 'auth.js',
  'getRefreshToken': 'auth.js',
  'setAuthTokens': 'auth.js',
  'startGoogleLogin': 'auth.js',
  'handleCognitoCallbackIfPresent': 'auth.js'
};

let okCount = 0, failCount = 0;
Object.keys(authFunctions).forEach(func => {
  if (typeof window[func] === 'function') {
    console.log(`  ✅ ${func}()`);
    okCount++;
  } else {
    console.error(`  ❌ ${func}() - MANQUANTE (devrait être dans ${authFunctions[func]})`);
    failCount++;
  }
});

console.log(`\n  Résultat: ${okCount}/${Object.keys(authFunctions).length} OK`);
console.log('');

// 4. Vérifier si les fonctions viennent de auth.js ou map_logic.js
console.log('4. ORIGINE DES FONCTIONS:');
if (typeof window.openAuthModal === 'function') {
  const funcStr = window.openAuthModal.toString();
  if (funcStr.includes('auth.js') || funcStr.length > 1000) {
    console.log('  ✅ openAuthModal semble venir de auth.js');
  } else {
    console.warn('  ⚠️ openAuthModal pourrait venir de map_logic.js (ancienne version)');
  }
}

console.log('');

// 5. Résumé
console.log('%c=== RÉSUMÉ ===', 'color: #10b981; font-weight: bold;');
if (!authFound) {
  console.error('❌ auth.js n\'est PAS chargé!');
  console.error('   Solution: Vérifiez que <script src="auth.js"> est dans mapevent.html');
} else if (failCount > 0) {
  console.warn(`⚠️ ${failCount} fonction(s) AUTH manquante(s)`);
  console.warn('   Solution: Redéployez les fichiers avec .\\deploy-force-cache-bust.ps1');
} else {
  console.log('✅ Tout semble correct!');
}

console.log('');
console.log('Le serveur charge encore map_logic.js?v=20260107-56 (ancienne version)');
console.log('Il faut redéployer pour mettre à jour vers v=20260111-120000');
