// Script de diagnostic pour trouver les erreurs de syntaxe
// Copiez-collez ce script dans la console (F12) et appuyez sur Entrée

console.log('%c=== DIAGNOSTIC ERREURS SYNTAXE ===', 'color: #ef4444; font-size: 16px; font-weight: bold;');
console.log('');

// 1. Vérifier les scripts chargés
console.log('%c1. SCRIPTS CHARGÉS:', 'color: #3b82f6; font-weight: bold;');
const scripts = Array.from(document.querySelectorAll('script[src]'));
scripts.forEach((script, index) => {
  const src = script.src;
  const isAuth = src.includes('auth.js');
  const isMapLogic = src.includes('map_logic.js');
  console.log(`  ${index + 1}. ${src}`);
  if (isAuth || isMapLogic) {
    console.log(`     Version: ${src.match(/v=([^&]+)/)?.[1] || 'N/A'}`);
  }
});
console.log('');

// 2. Vérifier si les fonctions AUTH sont accessibles
console.log('%c2. VÉRIFICATION FONCTIONS AUTH:', 'color: #3b82f6; font-weight: bold;');
const authFunctions = ['openAuthModal', 'performLogin', 'performRegister', 'logout', 'loadSavedUser', 'closeAuthModal', 'getAuthToken', 'getRefreshToken', 'setAuthTokens'];
let okCount = 0, failCount = 0;
authFunctions.forEach(func => {
  if (typeof window[func] === 'function') {
    console.log(`  ✅ ${func}()`);
    okCount++;
  } else {
    console.log(`  ❌ ${func}()`);
    failCount++;
  }
});
console.log(`\n  Résultat: ${okCount}/${authFunctions.length} OK`);
console.log('');

// 3. Vérifier les erreurs JavaScript récentes
console.log('%c3. ERREURS RÉCENTES:', 'color: #3b82f6; font-weight: bold;');
console.log('  Vérifiez l\'onglet "Console" pour les erreurs en rouge');
console.log('  Cliquez sur chaque erreur pour voir le fichier et la ligne');
console.log('');

// 4. Tester la syntaxe des fonctions principales
console.log('%c4. TEST SYNTAXE FONCTIONS:', 'color: #3b82f6; font-weight: bold;');
try {
  if (typeof window.openAuthModal === 'function') {
    const funcStr = window.openAuthModal.toString();
    console.log('  ✅ openAuthModal: syntaxe OK');
    console.log(`     Longueur: ${funcStr.length} caractères`);
  } else {
    console.log('  ❌ openAuthModal: non disponible');
  }
} catch (e) {
  console.error('  ❌ Erreur lors de la vérification:', e);
}
console.log('');

// 5. Vérifier le contenu des scripts chargés
console.log('%c5. VÉRIFICATION CONTENU SCRIPTS:', 'color: #3b82f6; font-weight: bold;');
console.log('  Pour vérifier le contenu d\'un script:');
console.log('  - Ouvrez l\'onglet "Network" (Réseau) dans DevTools');
console.log('  - Rechargez la page (F5)');
console.log('  - Cliquez sur "map_logic.js" ou "auth.js"');
console.log('  - Allez dans l\'onglet "Response" ou "Réponse"');
console.log('  - Cherchez des caractères isolés comme "x" seul sur une ligne');
console.log('');

// 6. Vérifier les erreurs de parsing
console.log('%c6. TEST PARSING:', 'color: #3b82f6; font-weight: bold;');
try {
  // Tester si on peut accéder aux fonctions sans erreur
  const testFuncs = ['openAuthModal', 'performLogin', 'logout'];
  testFuncs.forEach(func => {
    try {
      if (typeof window[func] === 'function') {
        const funcCode = window[func].toString();
        // Chercher des patterns suspects
        if (funcCode.match(/\sx\s/) || funcCode.match(/^\s*x\s*$/m)) {
          console.warn(`  ⚠️ ${func}: contient un "x" isolé suspect`);
        } else {
          console.log(`  ✅ ${func}: pas de "x" isolé détecté`);
        }
      }
    } catch (e) {
      console.error(`  ❌ ${func}: erreur -`, e.message);
    }
  });
} catch (e) {
  console.error('  ❌ Erreur lors du test de parsing:', e);
}
console.log('');

// 7. Instructions pour trouver l'erreur exacte
console.log('%c7. INSTRUCTIONS POUR TROUVER L\'ERREUR:', 'color: #ef4444; font-weight: bold;');
console.log('  1. Regardez l\'onglet "Console"');
console.log('  2. Cherchez les erreurs en rouge qui mentionnent "SyntaxError"');
console.log('  3. Cliquez sur chaque erreur pour voir:');
console.log('     - Le nom du fichier (ex: map_logic.js)');
console.log('     - Le numéro de ligne (ex: ligne 2562)');
console.log('     - Le code autour de l\'erreur');
console.log('  4. Si l\'erreur dit "debugger eval code", c\'est du code collé dans la console');
console.log('  5. Si l\'erreur dit "map_logic.js:2562", ouvrez ce fichier à cette ligne');
console.log('');

// 8. Vérifier les sources chargées
console.log('%c8. SOURCES CHARGÉES:', 'color: #3b82f6; font-weight: bold;');
console.log('  Pour voir les sources:');
console.log('  - Ouvrez l\'onglet "Sources" (Sources) dans DevTools');
console.log('  - Cherchez "map_logic.js" et "auth.js"');
console.log('  - Vérifiez qu\'ils contiennent bien le code attendu');
console.log('');

console.log('%c=== FIN DU DIAGNOSTIC ===', 'color: #10b981; font-size: 14px; font-weight: bold;');
console.log('');
console.log('%cIMPORTANT:', 'color: #ef4444; font-weight: bold;');
console.log('Si vous voyez des erreurs "SyntaxError: expected ... got \'x\'":');
console.log('1. Notez le nom du fichier et le numéro de ligne');
console.log('2. Ouvrez ce fichier dans l\'éditeur à cette ligne');
console.log('3. Cherchez un caractère "x" isolé ou une syntaxe invalide');
console.log('4. Redéployez les fichiers si nécessaire: .\\deploy-force-cache-bust.ps1');
console.log('');
