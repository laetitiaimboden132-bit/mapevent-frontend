// Test du bouton Publier
// Copiez dans la console

(function() {
  console.log('=== TEST BOUTON PUBLIER ===');
  
  // Test 1: Bouton existe?
  const btn = document.getElementById('map-publish-btn');
  console.log('1. Bouton:', btn ? 'TROUVÉ' : 'NON TROUVÉ');
  
  if (btn) {
    console.log('   - Parent:', btn.parentElement?.tagName);
    console.log('   - Display:', window.getComputedStyle(btn).display);
    console.log('   - Visible:', btn.offsetParent !== null);
    console.log('   - onclick:', btn.onclick ? 'PRÉSENT' : 'ABSENT');
    
    // Test 2: Utilisateur connecté?
    const userOk = typeof currentUser !== 'undefined' && currentUser && currentUser.isLoggedIn;
    console.log('2. Utilisateur:', userOk ? 'CONNECTÉ' : 'NON CONNECTÉ');
    if (typeof currentUser !== 'undefined' && currentUser) {
      console.log('   - isLoggedIn:', currentUser.isLoggedIn);
      console.log('   - email:', currentUser.email || 'N/A');
    }
    
    // Test 3: Fonction existe?
    const funcOk = typeof window.openPublishModal === 'function';
    console.log('3. Fonction:', funcOk ? 'EXISTE' : 'MANQUANTE');
    
    // Test 4: Simuler un clic
    console.log('4. Test clic...');
    btn.click();
    
    // Test 5: Vérifier après 500ms
    setTimeout(() => {
      console.log('5. Vérification après clic:');
      const b = document.getElementById('publish-modal-backdrop');
      const i = document.getElementById('publish-modal-inner');
      
      if (b) {
        const s = window.getComputedStyle(b);
        console.log('   - Backdrop display:', s.display);
        console.log('   - Backdrop visibility:', s.visibility);
        console.log('   - Backdrop opacity:', s.opacity);
      } else {
        console.log('   - Backdrop: NON TROUVÉ');
      }
      
      if (i) {
        console.log('   - Inner HTML:', i.innerHTML.length, 'chars');
      } else {
        console.log('   - Inner: NON TROUVÉ');
      }
      
      if (!userOk) {
        console.log('⚠️ PROBLÈME: Utilisateur non connecté - Le bouton ne devrait rien faire');
      } else if (!funcOk) {
        console.log('⚠️ PROBLÈME: Fonction openPublishModal non trouvée');
      } else if (!b || window.getComputedStyle(b).display === 'none') {
        console.log('⚠️ PROBLÈME: Modal non ouvert après clic');
      } else {
        console.log('✅ Modal ouvert');
      }
    }, 500);
  } else {
    console.log('❌ Bouton non trouvé dans le DOM');
  }
})();
