# Test Rapide des Fonctions AUTH

## Test ultra-simple (copiez-collez dans la console F12)

```javascript
// Test rapide
const tests = ['openAuthModal', 'performLogin', 'performRegister', 'logout', 'loadSavedUser', 'closeAuthModal', 'getAuthToken', 'getRefreshToken', 'setAuthTokens'];
let ok = 0, fail = 0;
tests.forEach(f => {
  if (typeof window[f] === 'function') {
    console.log(`✅ ${f}()`); ok++;
  } else {
    console.error(`❌ ${f}()`); fail++;
  }
});
console.log(`\nRésultat: ${ok}/${tests.length} OK`);
if (fail === 0) console.log('✅ TOUT EST BON !');
```

## Vérification de l'ordre de chargement

```javascript
// Vérifier que auth.js est chargé avant map_logic.js
const scripts = Array.from(document.querySelectorAll('script[src]')).map(s => s.src);
const authIndex = scripts.findIndex(s => s.includes('auth.js'));
const mapLogicIndex = scripts.findIndex(s => s.includes('map_logic.js'));

if (authIndex < mapLogicIndex && authIndex >= 0) {
  console.log('✅ Ordre correct: auth.js avant map_logic.js');
} else {
  console.error('❌ Ordre incorrect ou auth.js non trouvé');
  console.log('Scripts:', scripts);
}
```

## Vérification que les fonctions viennent de auth.js

```javascript
// Vérifier que les fonctions ne sont pas dupliquées
console.log('Vérification des fonctions AUTH:');
['openAuthModal', 'performLogin', 'performRegister', 'logout', 'loadSavedUser', 'closeAuthModal'].forEach(f => {
  const func = window[f];
  if (func) {
    const source = func.toString().substring(0, 100);
    console.log(`${f}: ${source.includes('auth.js') || source.includes('REMOVED') ? '✅' : '⚠️'}`);
  } else {
    console.log(`${f}: ❌ MANQUANTE`);
  }
});
```
