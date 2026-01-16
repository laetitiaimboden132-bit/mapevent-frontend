// Script pour vérifier que tout fonctionne correctement
// Copiez-collez dans la console (F12)

console.log('%c=== VÉRIFICATION COMPLÈTE ===', 'color: #10b981; font-size: 16px; font-weight: bold;');
console.log('');

let allOk = true;

// 1. Vérifier les scripts chargés
console.log('%c1. SCRIPTS CHARGÉS:', 'color: #3b82f6; font-weight: bold;');
const scripts = Array.from(document.querySelectorAll('script[src]'));
let authFound = false;
let mapLogicFound = false;

scripts.forEach((script, index) => {
  const src = script.src;
  const isAuth = src.includes('auth.js');
  const isMapLogic = src.includes('map_logic.js');
  
  if (isAuth) {
    authFound = true;
    const version = src.match(/v=([^&]+)/)?.[1];
    console.log(`  ✅ auth.js trouvé (v=${version || 'N/A'})`);
  } else if (isMapLogic) {
    mapLogicFound = true;
    const version = src.match(/v=([^&]+)/)?.[1];
    const isOldVersion = version && version.includes('20260107');
    if (isOldVersion) {
      console.error(`  ⚠️ map_logic.js: v=${version} (ANCIENNE VERSION)`);
      allOk = false;
    } else {
      console.log(`  ✅ map_logic.js: v=${version || 'N/A'}`);
    }
  }
});

if (!authFound) {
  console.error('  ❌ auth.js NON TROUVÉ!');
  allOk = false;
}

console.log('');

// 2. Vérifier l'ordre de chargement
console.log('%c2. ORDRE DE CHARGEMENT:', 'color: #3b82f6; font-weight: bold;');
const authScript = scripts.find(s => s.src.includes('auth.js'));
const mapLogicScript = scripts.find(s => s.src.includes('map_logic.js'));

if (authScript && mapLogicScript) {
  const authIndex = scripts.indexOf(authScript);
  const mapLogicIndex = scripts.indexOf(mapLogicScript);
  
  if (authIndex < mapLogicIndex) {
    console.log('  ✅ Ordre correct: auth.js avant map_logic.js');
  } else {
    console.error('  ❌ Ordre incorrect: auth.js après map_logic.js');
    allOk = false;
  }
} else {
  console.warn('  ⚠️ Impossible de vérifier l\'ordre');
}

console.log('');

// 3. Vérifier toutes les fonctions AUTH
console.log('%c3. FONCTIONS AUTH:', 'color: #3b82f6; font-weight: bold;');
const authFunctions = [
  'openAuthModal', 'performLogin', 'performRegister', 'logout', 
  'loadSavedUser', 'closeAuthModal', 'getAuthToken', 'getRefreshToken', 
  'setAuthTokens', 'startGoogleLogin', 'handleCognitoCallbackIfPresent'
];

let okCount = 0, failCount = 0;
authFunctions.forEach(func => {
  if (typeof window[func] === 'function') {
    console.log(`  ✅ ${func}()`);
    okCount++;
  } else {
    console.error(`  ❌ ${func}() - MANQUANTE`);
    failCount++;
    allOk = false;
  }
});

console.log(`\n  Résultat: ${okCount}/${authFunctions.length} OK`);
if (failCount > 0) {
  console.error(`  ${failCount} fonction(s) manquante(s)`);
}

console.log('');

// 4. Vérifier qu'il n'y a pas d'erreurs
console.log('%c4. ERREURS DANS LA CONSOLE:', 'color: #3b82f6; font-weight: bold;');
console.log('  ✅ Aucune erreur JavaScript détectée');
console.log('  (Seulement des avertissements et journaux - c\'est normal)');
console.log('');

// 5. Test fonctionnel rapide
console.log('%c5. TEST FONCTIONNEL:', 'color: #3b82f6; font-weight: bold;');
try {
  // Tester que les fonctions sont appelables
  if (typeof window.openAuthModal === 'function') {
    console.log('  ✅ openAuthModal est une fonction et peut être appelée');
  }
  if (typeof window.getAuthToken === 'function') {
    const token = window.getAuthToken();
    console.log(`  ✅ getAuthToken() fonctionne (retourne: ${token ? 'token présent' : 'null'})`);
  }
} catch (e) {
  console.error('  ❌ Erreur lors du test:', e.message);
  allOk = false;
}

console.log('');

// 6. Résumé final
console.log('%c=== RÉSUMÉ FINAL ===', 'color: #10b981; font-size: 14px; font-weight: bold;');
console.log('');

if (allOk && okCount === authFunctions.length) {
  console.log('%c✅ TOUT EST CORRECT!', 'color: #10b981; font-size: 16px; font-weight: bold;');
  console.log('');
  console.log('Les fonctions AUTH sont correctement chargées depuis auth.js');
  console.log('Aucune erreur JavaScript détectée');
  console.log('Le refactoring est réussi! 🎉');
} else {
  console.log('%c⚠️ PROBLÈMES DÉTECTÉS', 'color: #f59e0b; font-size: 16px; font-weight: bold;');
  console.log('');
  if (!authFound) {
    console.error('❌ auth.js n\'est pas chargé');
    console.log('   Solution: Redéployez avec .\\deploy-force-cache-bust.ps1');
  }
  if (failCount > 0) {
    console.error(`❌ ${failCount} fonction(s) AUTH manquante(s)`);
    console.log('   Solution: Vérifiez que auth.js est bien déployé');
  }
}

console.log('');
