// Test complet - Version sans conflit de variables
console.log('=== DIAGNOSTIC COMPLET ===');
const publishBtn = document.getElementById("map-publish-btn");
console.log('1. Bouton existe:', publishBtn ? 'OUI' : 'NON');

if (publishBtn) {
  console.log('2. Parent:', publishBtn.parentElement?.tagName, publishBtn.parentElement?.id);
  console.log('3. Styles calculés:', {
    display: getComputedStyle(publishBtn).display,
    visibility: getComputedStyle(publishBtn).visibility,
    opacity: getComputedStyle(publishBtn).opacity,
    zIndex: getComputedStyle(publishBtn).zIndex,
    position: getComputedStyle(publishBtn).position
  });
  
  const rect = publishBtn.getBoundingClientRect();
  console.log('4. Rectangle:', rect);
  console.log('5. Visible:', rect.width > 0 && rect.height > 0);
  
  // Forcer l'affichage
  publishBtn.style.cssText = 'position:fixed !important; top:80px !important; right:20px !important; z-index:9999 !important; display:block !important; visibility:visible !important; opacity:1 !important;';
  console.log('6. Styles forcés');
  
  // Tester le clic
  publishBtn.onclick = function(e) {
    console.log('7. ✅ CLIC DÉTECTÉ !');
    e.preventDefault();
    e.stopPropagation();
    if (typeof openPublishModal === 'function') {
      console.log('8. Appel openPublishModal...');
      openPublishModal();
    } else {
      console.error('8. ❌ openPublishModal n\'existe pas');
    }
  };
  
  console.log('9. onclick défini, test clic...');
  setTimeout(() => publishBtn.click(), 100);
} else {
  console.error('❌ Le bouton n\'existe pas dans le DOM !');
}
