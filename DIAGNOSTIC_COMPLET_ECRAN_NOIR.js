// Diagnostic complet pour l'écran noir
// Copiez-collez dans la console (F12)

console.log('%c=== DIAGNOSTIC COMPLET ÉCRAN NOIR ===', 'color: #ef4444; font-size: 16px; font-weight: bold;');
console.log('');

// 1. Vérifier les erreurs JavaScript
console.log('%c1. ERREURS JAVASCRIPT:', 'color: #3b82f6; font-weight: bold;');
console.log('   ⚠️ REGARDEZ LES ERREURS EN ROUGE CI-DESSUS DANS LA CONSOLE');
console.log('   Notez le fichier et le numéro de ligne de chaque erreur');
console.log('');

// 2. État du DOM
console.log('%c2. ÉTAT DU DOM:', 'color: #3b82f6; font-weight: bold;');
console.log('   document.readyState:', document.readyState);
console.log('   document.body existe:', !!document.body);
console.log('   document.documentElement existe:', !!document.documentElement);

if (document.body) {
  const bodyStyle = window.getComputedStyle(document.body);
  console.log('   body.display:', bodyStyle.display);
  console.log('   body.visibility:', bodyStyle.visibility);
  console.log('   body.opacity:', bodyStyle.opacity);
  console.log('   body.height:', bodyStyle.height);
  console.log('   body.backgroundColor:', bodyStyle.backgroundColor);
  console.log('   body.children.length:', document.body.children.length);
}

if (document.documentElement) {
  const htmlStyle = window.getComputedStyle(document.documentElement);
  console.log('   html.display:', htmlStyle.display);
  console.log('   html.visibility:', htmlStyle.visibility);
  console.log('   html.opacity:', htmlStyle.opacity);
  console.log('   html.height:', htmlStyle.height);
}

console.log('');

// 3. Vérifier le contenu principal
console.log('%c3. CONTENU PRINCIPAL:', 'color: #3b82f6; font-weight: bold;');
const mainSelectors = [
  'main',
  '#app',
  '#root',
  '#map',
  '.map-container',
  '[id*="map"]',
  '[class*="map"]',
  'body > div:first-child'
];

let mainFound = false;
mainSelectors.forEach(selector => {
  const el = document.querySelector(selector);
  if (el && !mainFound) {
    mainFound = true;
    const style = window.getComputedStyle(el);
    console.log(`   ✅ Élément trouvé: ${selector}`);
    console.log(`      Display: ${style.display}`);
    console.log(`      Visibility: ${style.visibility}`);
    console.log(`      Opacity: ${style.opacity}`);
    console.log(`      Width: ${style.width}`);
    console.log(`      Height: ${style.height}`);
    console.log(`      Z-index: ${style.zIndex}`);
    console.log(`      Position: ${style.position}`);
    console.log(`      Background: ${style.backgroundColor}`);
  }
});

if (!mainFound) {
  console.error('   ❌ Aucun conteneur principal trouvé!');
  console.log('   Structure du DOM:');
  if (document.body) {
    console.log('   Body children:', document.body.children.length);
    Array.from(document.body.children).slice(0, 5).forEach((child, i) => {
      console.log(`     ${i + 1}. ${child.tagName} (id="${child.id}", class="${child.className}")`);
    });
  }
}

console.log('');

// 4. Vérifier les scripts chargés
console.log('%c4. SCRIPTS CHARGÉS:', 'color: #3b82f6; font-weight: bold;');
const scripts = Array.from(document.querySelectorAll('script[src]'));
let authJsFound = false;
let mapLogicFound = false;

scripts.forEach(script => {
  const src = script.src;
  if (src.includes('auth.js')) {
    authJsFound = true;
    const version = src.match(/v=([^&]+)/)?.[1];
    console.log(`   ✅ auth.js (v=${version || 'N/A'})`);
  } else if (src.includes('map_logic.js')) {
    mapLogicFound = true;
    const version = src.match(/v=([^&]+)/)?.[1];
    console.log(`   ✅ map_logic.js (v=${version || 'N/A'})`);
    if (version && version.includes('20260107')) {
      console.error(`      ⚠️ ANCIENNE VERSION!`);
    }
  }
});

if (!authJsFound) console.error('   ❌ auth.js NON TROUVÉ!');
if (!mapLogicFound) console.error('   ❌ map_logic.js NON TROUVÉ!');

console.log('');

// 5. Vérifier les fonctions critiques
console.log('%c5. FONCTIONS CRITIQUES:', 'color: #3b82f6; font-weight: bold;');
const criticalFuncs = {
  'openAuthModal': 'function',
  'getAuthToken': 'function',
  'currentUser': 'any',
  'initMap': 'function',
  'loadSavedUser': 'function'
};

Object.entries(criticalFuncs).forEach(([func, expectedType]) => {
  const exists = typeof window[func] !== 'undefined';
  const actualType = typeof window[func];
  const isCorrect = exists && (expectedType === 'any' || actualType === expectedType);
  
  if (isCorrect) {
    console.log(`   ✅ ${func}: ${actualType}`);
  } else {
    console.error(`   ❌ ${func}: ${exists ? actualType : 'MANQUANT'} (attendu: ${expectedType})`);
  }
});

console.log('');

// 6. Vérifier les styles CSS chargés
console.log('%c6. STYLES CSS:', 'color: #3b82f6; font-weight: bold;');
const stylesheets = Array.from(document.querySelectorAll('link[rel="stylesheet"]'));
console.log(`   ${stylesheets.length} feuille(s) de style trouvée(s)`);
stylesheets.forEach((link, i) => {
  const href = link.href.split('/').pop();
  console.log(`   ${i + 1}. ${href}`);
});

console.log('');

// 7. Tester si la carte est initialisée
console.log('%c7. INITIALISATION DE LA CARTE:', 'color: #3b82f6; font-weight: bold;');
if (typeof window.map !== 'undefined') {
  console.log('   ✅ window.map existe');
  if (window.map && typeof window.map.getZoom === 'function') {
    console.log('   ✅ La carte Leaflet est initialisée');
    console.log(`   Zoom: ${window.map.getZoom()}`);
  } else {
    console.error('   ❌ window.map existe mais n\'est pas une carte Leaflet valide');
  }
} else {
  console.error('   ❌ window.map n\'existe pas (la carte n\'est pas initialisée)');
}

console.log('');

// 8. Instructions pour résoudre
console.log('%c8. RÉSOLUTION:', 'color: #ef4444; font-weight: bold;');
console.log('   1. REGARDEZ LES ERREURS EN ROUGE dans la console');
console.log('   2. Cliquez sur chaque erreur pour voir:');
console.log('      - Le nom du fichier (ex: map_logic.js)');
console.log('      - Le numéro de ligne (ex: ligne 2562)');
console.log('      - Le message d\'erreur');
console.log('   3. Partagez ces informations (screenshot ou copier-coller)');
console.log('');

// 9. Test de forcer l'affichage
console.log('%c9. TEST FORCER AFFICHAGE:', 'color: #3b82f6; font-weight: bold;');
console.log('   Tentative de forcer l\'affichage...');

try {
  if (document.body) {
    document.body.style.display = 'block';
    document.body.style.visibility = 'visible';
    document.body.style.opacity = '1';
    document.body.style.height = '100vh';
    document.body.style.width = '100vw';
    console.log('   ✅ Body forcé visible');
  }
  
  if (document.documentElement) {
    document.documentElement.style.display = 'block';
    document.documentElement.style.visibility = 'visible';
    document.documentElement.style.opacity = '1';
    console.log('   ✅ HTML forcé visible');
  }
  
  // Chercher et forcer les conteneurs principaux
  const mainContainers = document.querySelectorAll('main, #app, #root, #map, [id*="map"], [class*="map"]');
  mainContainers.forEach(container => {
    const style = window.getComputedStyle(container);
    if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
      container.style.display = 'block';
      container.style.visibility = 'visible';
      container.style.opacity = '1';
      console.log(`   ✅ Conteneur ${container.tagName} forcé visible`);
    }
  });
} catch (e) {
  console.error('   ❌ Erreur lors du forçage:', e.message);
}

console.log('');
console.log('%c=== FIN DU DIAGNOSTIC ===', 'color: #10b981; font-size: 14px; font-weight: bold;');
console.log('');
console.log('%cIMPORTANT:', 'color: #ef4444; font-weight: bold;');
console.log('Si l\'écran est toujours noir après ce diagnostic:');
console.log('1. Prenez un screenshot de la console avec toutes les erreurs');
console.log('2. Partagez le screenshot ou copiez-collez toutes les erreurs');
console.log('3. Notez particulièrement les erreurs qui mentionnent:');
console.log('   - "SyntaxError"');
console.log('   - "TypeError"');
console.log('   - "ReferenceError"');
console.log('   - Un fichier spécifique (ex: map_logic.js)');
