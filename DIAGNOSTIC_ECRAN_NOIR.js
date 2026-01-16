// Script pour diagnostiquer l'écran noir
// Copiez-collez dans la console (F12)

console.log('%c=== DIAGNOSTIC ÉCRAN NOIR ===', 'color: #ef4444; font-size: 16px; font-weight: bold;');
console.log('');

// 1. Vérifier les erreurs
console.log('1. ERREURS DANS LA CONSOLE:');
console.log('   Regardez les messages en rouge ci-dessus');
console.log('   Notez le fichier et la ligne de chaque erreur');
console.log('');

// 2. Vérifier si le DOM est chargé
console.log('2. ÉTAT DU DOM:');
console.log('   document.readyState:', document.readyState);
console.log('   document.body existe:', !!document.body);
if (document.body) {
  console.log('   document.body.style.display:', document.body.style.display);
  console.log('   document.body.style.visibility:', document.body.style.visibility);
  console.log('   document.body.style.opacity:', document.body.style.opacity);
}
console.log('');

// 3. Vérifier les overlays d'erreur
console.log('3. OVERLAYS D\'ERREUR:');
const errorOverlays = document.querySelectorAll('[style*="position:fixed"][style*="background"][style*="rgba(0,0,0"]');
if (errorOverlays.length > 0) {
  console.error('   ⚠️ Overlay d\'erreur détecté:', errorOverlays.length);
  errorOverlays.forEach((overlay, i) => {
    console.log(`   Overlay ${i + 1}:`, overlay);
    console.log(`   Display: ${window.getComputedStyle(overlay).display}`);
    console.log(`   Visibility: ${window.getComputedStyle(overlay).visibility}`);
  });
} else {
  console.log('   ✅ Aucun overlay d\'erreur détecté');
}
console.log('');

// 4. Vérifier les scripts chargés
console.log('4. SCRIPTS CHARGÉS:');
const scripts = Array.from(document.querySelectorAll('script[src]'));
scripts.forEach((script, i) => {
  const src = script.src;
  if (src.includes('auth.js') || src.includes('map_logic.js')) {
    console.log(`   ${i + 1}. ${src.split('/').pop()}`);
    const version = src.match(/v=([^&]+)/);
    if (version) console.log(`      Version: ${version[1]}`);
  }
});
console.log('');

// 5. Tester les fonctions critiques
console.log('5. FONCTIONS CRITIQUES:');
const criticalFuncs = ['openAuthModal', 'getAuthToken', 'currentUser'];
criticalFuncs.forEach(func => {
  if (func === 'currentUser') {
    const exists = typeof window[func] !== 'undefined';
    console.log(`   ${exists ? '✅' : '❌'} ${func}: ${exists ? typeof window[func] : 'MANQUANT'}`);
  } else {
    const exists = typeof window[func] === 'function';
    console.log(`   ${exists ? '✅' : '❌'} ${func}(): ${exists ? 'OK' : 'MANQUANT'}`);
  }
});
console.log('');

// 6. Vérifier le contenu visible
console.log('6. CONTENU VISIBLE:');
const mainContent = document.querySelector('main') || document.querySelector('#app') || document.querySelector('body');
if (mainContent) {
  const style = window.getComputedStyle(mainContent);
  console.log('   Element principal trouvé:', mainContent.tagName);
  console.log('   Display:', style.display);
  console.log('   Visibility:', style.visibility);
  console.log('   Opacity:', style.opacity);
  console.log('   Z-index:', style.zIndex);
} else {
  console.error('   ❌ Aucun élément principal trouvé');
}
console.log('');

// 7. Instructions
console.log('%c7. INSTRUCTIONS:', 'color: #ef4444; font-weight: bold;');
console.log('   Si vous voyez un overlay noir:');
console.log('   1. Regardez les erreurs en rouge dans la console');
console.log('   2. Cliquez sur chaque erreur pour voir le fichier et la ligne');
console.log('   3. Notez le fichier et la ligne de l\'erreur');
console.log('   4. Partagez ces informations');
console.log('');

console.log('=== FIN DU DIAGNOSTIC ===');
