// Script de diagnostic pour le bouton Publier
// À exécuter dans la console du navigateur (F12)

console.log('🔍 DIAGNOSTIC BOUTON PUBLIER');
console.log('================================');

// 1. Vérifier si le bouton existe
const publishBtn = document.getElementById("map-publish-btn");
console.log('1. Bouton trouvé:', publishBtn ? '✅ OUI' : '❌ NON');

if (publishBtn) {
  // 2. Vérifier les styles
  const styles = window.getComputedStyle(publishBtn);
  console.log('2. Styles du bouton:', {
    display: styles.display,
    visibility: styles.visibility,
    opacity: styles.opacity,
    zIndex: styles.zIndex,
    pointerEvents: styles.pointerEvents,
    position: styles.position,
    top: styles.top,
    right: styles.right,
    width: styles.width,
    height: styles.height
  });
  
  // 3. Vérifier si le bouton est visible
  const rect = publishBtn.getBoundingClientRect();
  console.log('3. Position du bouton:', {
    x: rect.x,
    y: rect.y,
    width: rect.width,
    height: rect.height,
    visible: rect.width > 0 && rect.height > 0
  });
  
  // 4. Vérifier les listeners
  console.log('4. Listeners sur le bouton:', publishBtn.onclick ? 'onclick présent' : 'pas d\'onclick');
  
  // 5. Vérifier si openPublishModal existe
  console.log('5. openPublishModal existe:', typeof openPublishModal === 'function' ? '✅ OUI' : '❌ NON');
  
  // 6. Tester un clic programmatique
  console.log('6. Test de clic programmatique...');
  publishBtn.click();
  
  // 7. Vérifier s'il y a des éléments qui bloquent
  const elementAtPoint = document.elementFromPoint(rect.x + rect.width / 2, rect.y + rect.height / 2);
  console.log('7. Élément au centre du bouton:', elementAtPoint?.id || elementAtPoint?.className || 'autre');
  if (elementAtPoint !== publishBtn) {
    console.warn('⚠️ Un autre élément est au-dessus du bouton !');
  }
} else {
  console.error('❌ Le bouton n\'existe pas dans le DOM');
}

console.log('================================');
