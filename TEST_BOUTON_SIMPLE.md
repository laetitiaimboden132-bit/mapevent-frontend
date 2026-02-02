# Test simple du bouton Publier

Copiez-collez ce code dans la console (F12) :

```javascript
// Test 1 : Vérifier si le bouton existe
console.log('=== TEST 1 ===');
const testBtn = document.getElementById("map-publish-btn");
console.log('Bouton trouvé:', testBtn ? 'OUI' : 'NON');

// Test 2 : Si le bouton existe, vérifier ses propriétés
if (testBtn) {
  console.log('=== TEST 2 ===');
  console.log('Tag:', testBtn.tagName);
  console.log('Parent:', testBtn.parentElement?.tagName);
  console.log('Display:', getComputedStyle(testBtn).display);
  console.log('Visible:', testBtn.offsetParent !== null);
  
  // Test 3 : Forcer l'affichage
  console.log('=== TEST 3 ===');
  testBtn.style.cssText = 'position:fixed !important; top:80px !important; right:20px !important; z-index:99999 !important; display:block !important; visibility:visible !important; opacity:1 !important; background:red !important; color:white !important; padding:20px !important;';
  console.log('Styles forcés - Le bouton devrait être ROUGE maintenant');
  
  // Test 4 : Tester le clic
  console.log('=== TEST 4 ===');
  testBtn.onclick = function() {
    console.log('CLIC DÉTECTÉ !');
    alert('Bouton cliqué !');
    if (typeof window.openPublishModal === 'function') {
      window.openPublishModal();
    } else if (typeof openPublishModal === 'function') {
      openPublishModal();
    } else {
      alert('openPublishModal non disponible');
    }
  };
  console.log('onclick défini');
  
  // Test 5 : Clic programmatique
  console.log('=== TEST 5 ===');
  setTimeout(() => {
    console.log('Clic programmatique...');
    testBtn.click();
  }, 1000);
} else {
  console.error('❌ Le bouton n\'existe pas dans le DOM !');
  console.log('Recherche de tous les boutons...');
  const allButtons = document.querySelectorAll('button');
  console.log('Nombre de boutons:', allButtons.length);
  allButtons.forEach((btn, i) => {
    if (btn.textContent.includes('Publier') || btn.id.includes('publish')) {
      console.log(`Bouton ${i}:`, btn.id, btn.textContent);
    }
  });
}
```
