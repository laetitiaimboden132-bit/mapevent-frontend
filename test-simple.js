// Test simple du modal de publication
// Copiez TOUT ce fichier dans la console

(function() {
  console.log('=== TEST MODAL PUBLICATION ===');
  
  // Test 1: Fonction existe?
  console.log('\n1. Fonction openPublishModal:');
  if (typeof window.openPublishModal === 'function') {
    console.log('   OK - window.openPublishModal existe');
  } else if (typeof openPublishModal === 'function') {
    console.log('   OK - openPublishModal existe');
  } else {
    console.log('   ERREUR - fonction non trouvee');
  }
  
  // Test 2: Elements existent?
  console.log('\n2. Elements du modal:');
  const backdrop = document.getElementById('publish-modal-backdrop');
  const inner = document.getElementById('publish-modal-inner');
  console.log('   Backdrop:', backdrop ? 'OK' : 'MANQUANT');
  console.log('   Inner:', inner ? 'OK' : 'MANQUANT');
  
  // Test 3: Utilisateur connecte?
  console.log('\n3. Utilisateur:');
  if (typeof currentUser !== 'undefined' && currentUser && currentUser.isLoggedIn) {
    console.log('   OK - Connecte');
    console.log('   Email:', currentUser.email || 'N/A');
  } else {
    console.log('   NON CONNECTE - Le bouton ne devrait pas fonctionner');
  }
  
  // Test 4: Bouton existe?
  console.log('\n4. Bouton Publier:');
  const btn = document.getElementById('map-publish-btn');
  if (btn) {
    console.log('   OK - Bouton trouve');
    const styles = window.getComputedStyle(btn);
    console.log('   Display:', styles.display);
    console.log('   Visible:', btn.offsetParent !== null);
  } else {
    console.log('   ERREUR - Bouton non trouve');
  }
  
  // Test 5: Tester ouverture
  console.log('\n5. Test ouverture modal:');
  try {
    if (typeof window.openPublishModal === 'function') {
      console.log('   Appel de window.openPublishModal()...');
      window.openPublishModal();
    } else if (typeof openPublishModal === 'function') {
      console.log('   Appel de openPublishModal()...');
      openPublishModal();
    }
    
    setTimeout(function() {
      console.log('\n6. Verification apres 500ms:');
      const b = document.getElementById('publish-modal-backdrop');
      const i = document.getElementById('publish-modal-inner');
      
      if (b) {
        const s = window.getComputedStyle(b);
        console.log('   Backdrop display:', s.display);
        console.log('   Backdrop visible:', b.offsetParent !== null);
        const r = b.getBoundingClientRect();
        console.log('   Backdrop taille:', r.width + 'x' + r.height);
      }
      
      if (i) {
        console.log('   Inner HTML longueur:', i.innerHTML.length);
        if (i.innerHTML.length > 0) {
          console.log('   Inner HTML (100 premiers chars):', i.innerHTML.substring(0, 100));
        }
      }
      
      if (b && window.getComputedStyle(b).display !== 'none' && i && i.innerHTML.length > 100) {
        console.log('\n   SUCCES - Modal affiche!');
      } else {
        console.log('\n   ECHEC - Modal non affiche');
      }
    }, 500);
    
  } catch (e) {
    console.log('   ERREUR:', e.message);
  }
  
  console.log('\n=== FIN DES TESTS ===');
})();
