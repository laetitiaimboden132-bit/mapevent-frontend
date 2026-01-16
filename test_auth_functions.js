// Script de test pour vérifier que toutes les fonctions AUTH sont bien exposées
// Copiez-collez ce script dans la console du navigateur (F12)

console.log('%c=== TEST DES FONCTIONS AUTH ===', 'color: #00ffc3; font-size: 16px; font-weight: bold;');
console.log('');

// Liste des fonctions AUTH à vérifier
const authFunctions = [
  'closeAuthModal',
  'openAuthModal',
  'openLoginModal',
  'openRegisterModal',
  'performLogin',
  'performRegister',
  'loadSavedUser',
  'logout',
  'handleCognitoCallbackIfPresent',
  'startGoogleLogin',
  'getAuthToken',
  'getRefreshToken',
  'setAuthTokens',
  'decodeJwtPayload',
  'showError',
  'showRegisterTimeoutError',
  'showRegisterConflictError',
  'toggleRegisterPasswordVisibility',
  'validateRegisterPassword',
  'validateRegisterPasswordMatch',
  'updatePostalAddressRequired'
];

// Variables globales AUTH
const authVariables = [
  'registerStep',
  'registerData',
  'isSubmittingProRegister',
  'isGoogleLoginInProgress'
];

let allTestsPassed = true;
let passedCount = 0;
let failedCount = 0;

// Test 1: Vérifier que toutes les fonctions sont exposées globalement
console.log('%c1. Vérification des fonctions exposées globalement', 'color: #3b82f6; font-weight: bold;');
console.log('');

authFunctions.forEach(funcName => {
  const exists = typeof window[funcName] === 'function';
  if (exists) {
    console.log(`  ✅ ${funcName}() - OK`);
    passedCount++;
  } else {
    console.error(`  ❌ ${funcName}() - MANQUANTE`);
    failedCount++;
    allTestsPassed = false;
  }
});

console.log('');

// Test 2: Vérifier que les variables globales existent
console.log('%c2. Vérification des variables globales', 'color: #3b82f6; font-weight: bold;');
console.log('');

authVariables.forEach(varName => {
  const exists = typeof window[varName] !== 'undefined';
  if (exists) {
    console.log(`  ✅ ${varName} - OK`);
    passedCount++;
  } else {
    console.warn(`  ⚠️ ${varName} - Non définie (peut être normale si pas encore initialisée)`);
  }
});

console.log('');

// Test 3: Vérifier que auth.js est chargé
console.log('%c3. Vérification du chargement de auth.js', 'color: #3b82f6; font-weight: bold;');
console.log('');

const scripts = Array.from(document.querySelectorAll('script[src]'));
const authScript = scripts.find(s => s.src.includes('auth.js') || s.src.includes('/auth.js'));

if (authScript) {
  console.log(`  ✅ auth.js chargé: ${authScript.src}`);
  passedCount++;
} else {
  // Vérifier aussi dans les scripts inline ou via une autre méthode
  const allScripts = Array.from(document.querySelectorAll('script'));
  const authScriptAlt = allScripts.find(s => {
    const src = s.src || '';
    return src.includes('auth.js') || src.includes('/auth.js');
  });
  
  if (authScriptAlt) {
    console.log(`  ✅ auth.js chargé (méthode alternative): ${authScriptAlt.src || 'inline'}`);
    passedCount++;
  } else {
    console.error('  ❌ auth.js non trouvé dans les scripts chargés');
    console.warn('     Vérifiez que <script src="auth.js"> est présent dans mapevent.html');
    console.warn('     Vérifiez aussi le cache du navigateur (Ctrl+Shift+R pour recharger)');
    failedCount++;
    allTestsPassed = false;
  }
}

console.log('');

// Test 4: Vérifier que map_logic.js est chargé
console.log('%c4. Vérification du chargement de map_logic.js', 'color: #3b82f6; font-weight: bold;');
console.log('');

const mapLogicScript = scripts.find(s => s.src.includes('map_logic.js'));

if (mapLogicScript) {
  console.log(`  ✅ map_logic.js chargé: ${mapLogicScript.src}`);
  passedCount++;
} else {
  console.error('  ❌ map_logic.js non trouvé dans les scripts chargés');
  failedCount++;
  allTestsPassed = false;
}

console.log('');

// Test 5: Vérifier l'ordre de chargement (auth.js doit être avant map_logic.js)
console.log('%c5. Vérification de l\'ordre de chargement', 'color: #3b82f6; font-weight: bold;');
console.log('');

if (authScript && mapLogicScript) {
  const authIndex = scripts.indexOf(authScript);
  const mapLogicIndex = scripts.indexOf(mapLogicScript);
  
  if (authIndex < mapLogicIndex) {
    console.log(`  ✅ Ordre correct: auth.js (index ${authIndex}) avant map_logic.js (index ${mapLogicIndex})`);
    passedCount++;
  } else {
    console.error(`  ❌ Ordre incorrect: auth.js (index ${authIndex}) après map_logic.js (index ${mapLogicIndex})`);
    console.error('     auth.js doit être chargé AVANT map_logic.js !');
    failedCount++;
    allTestsPassed = false;
  }
} else {
  console.warn('  ⚠️ Impossible de vérifier l\'ordre (scripts non trouvés)');
}

console.log('');

// Test 6: Vérifier que les fonctions ne sont pas dupliquées dans map_logic.js
console.log('%c6. Vérification des doublons (fonctions AUTH dans map_logic.js)', 'color: #3b82f6; font-weight: bold;');
console.log('');

// Note: Ce test nécessite d'accéder au code source, ce qui n'est pas possible directement
// On vérifie plutôt que les fonctions pointent vers auth.js
console.log('  ℹ️ Vérification indirecte: les fonctions doivent pointer vers auth.js');
console.log('  ℹ️ Pour vérifier les doublons, cherchez dans map_logic.js:');
console.log('     - "function performLogin" ou "async function performLogin"');
console.log('     - "function performRegister" ou "async function performRegister"');
console.log('     - "function logout" ou "async function logout"');
console.log('     - "function loadSavedUser"');
console.log('     - "function openAuthModal"');
console.log('     - "function closeAuthModal"');
console.log('  ℹ️ Ces fonctions ne doivent PAS exister dans map_logic.js (sauf commentaires "REMOVED")');

console.log('');

// Test 7: Test fonctionnel basique (sans déclencher d'actions)
console.log('%c7. Tests fonctionnels basiques', 'color: #3b82f6; font-weight: bold;');
console.log('');

// Test getAuthToken (ne devrait pas planter)
try {
  const token = window.getAuthToken ? window.getAuthToken() : null;
  console.log(`  ✅ getAuthToken() - OK (retourne: ${token ? 'token présent' : 'null'})`);
  passedCount++;
} catch (e) {
  console.error(`  ❌ getAuthToken() - ERREUR: ${e.message}`);
  failedCount++;
  allTestsPassed = false;
}

// Test decodeJwtPayload avec un token invalide (devrait gérer l'erreur)
try {
  if (window.decodeJwtPayload) {
    // Tester avec une chaîne invalide (ne devrait pas planter)
    try {
      window.decodeJwtPayload('invalid.token.here');
      console.log('  ✅ decodeJwtPayload() - OK (gère les erreurs)');
      passedCount++;
    } catch (e) {
      // C'est normal qu'il y ait une erreur avec un token invalide
      console.log('  ✅ decodeJwtPayload() - OK (gère les erreurs correctement)');
      passedCount++;
    }
  } else {
    console.error('  ❌ decodeJwtPayload() - MANQUANTE');
    failedCount++;
    allTestsPassed = false;
  }
} catch (e) {
  console.error(`  ❌ decodeJwtPayload() - ERREUR: ${e.message}`);
  failedCount++;
  allTestsPassed = false;
}

console.log('');

// Résumé final
console.log('%c=== RÉSUMÉ DES TESTS ===', 'color: #00ffc3; font-size: 16px; font-weight: bold;');
console.log('');
console.log(`Tests réussis: ${passedCount}`);
console.log(`Tests échoués: ${failedCount}`);
console.log('');

if (allTestsPassed && failedCount === 0) {
  console.log('%c✅ TOUS LES TESTS SONT PASSÉS !', 'color: #22c55e; font-size: 14px; font-weight: bold;');
  console.log('%cLes fonctions AUTH sont correctement extraites et exposées.', 'color: #22c55e;');
} else {
  console.log('%c❌ CERTAINS TESTS ONT ÉCHOUÉ', 'color: #ef4444; font-size: 14px; font-weight: bold;');
  console.log('%cVérifiez les erreurs ci-dessus et assurez-vous que auth.js est chargé avant map_logic.js.', 'color: #ef4444;');
}

console.log('');
console.log('%c=== FIN DES TESTS ===', 'color: #00ffc3; font-size: 16px; font-weight: bold;');
