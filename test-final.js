// Test FINAL - Collecte tous les resultats et les affiche
// Copiez TOUT ce code dans la console

(function() {
  let results = [];
  
  function addResult(label, value) {
    results.push(label + ': ' + value);
    console.log(label + ':', value);
  }
  
  addResult('=== DEBUT DU TEST ===', '');
  
  // Test 1: Utilisateur
  const userOk = typeof currentUser !== 'undefined' && currentUser && currentUser.isLoggedIn;
  addResult('1. Utilisateur connecte', userOk ? 'OUI' : 'NON');
  if (typeof currentUser !== 'undefined' && currentUser) {
    addResult('   currentUser.isLoggedIn', currentUser.isLoggedIn);
    addResult('   currentUser.email', currentUser.email || 'N/A');
  }
  
  // Test 2: Fonction
  const funcOk = typeof window.openPublishModal === 'function';
  addResult('2. Fonction openPublishModal', funcOk ? 'EXISTE' : 'MANQUANTE');
  
  // Test 3: Elements avant
  const backdropBefore = document.getElementById('publish-modal-backdrop');
  const innerBefore = document.getElementById('publish-modal-inner');
  addResult('3. Elements AVANT appel', '');
  addResult('   Backdrop', backdropBefore ? 'EXISTE' : 'MANQUANT');
  addResult('   Inner', innerBefore ? 'EXISTE' : 'MANQUANT');
  
  if (backdropBefore) {
    const s = window.getComputedStyle(backdropBefore);
    addResult('   Backdrop display avant', s.display);
  }
  
  if (innerBefore) {
    addResult('   Inner HTML longueur avant', innerBefore.innerHTML.length + ' chars');
  }
  
  // Test 4: Appel de la fonction
  if (funcOk && userOk) {
    addResult('4. Appel openPublishModal()', 'EN COURS...');
    try {
      window.openPublishModal();
      addResult('   Appel', 'TERMINE SANS ERREUR');
    } catch (e) {
      addResult('   ERREUR', e.message);
    }
  } else {
    addResult('4. Appel', 'SKIP (pre-requis non remplis)');
  }
  
  // Test 5: Verification apres 100ms
  setTimeout(() => {
    addResult('5. Verification apres 100ms', '');
    const b = document.getElementById('publish-modal-backdrop');
    const i = document.getElementById('publish-modal-inner');
    
    if (b) {
      const s = window.getComputedStyle(b);
      addResult('   Backdrop display', s.display);
      addResult('   Backdrop visibility', s.visibility);
      addResult('   Backdrop opacity', s.opacity);
      addResult('   Backdrop z-index', s.zIndex);
      addResult('   Backdrop offsetParent', b.offsetParent !== null ? 'OUI' : 'NON');
      const rect = b.getBoundingClientRect();
      addResult('   Backdrop rect', rect.width + 'x' + rect.height + ' a (' + rect.left + ',' + rect.top + ')');
    } else {
      addResult('   Backdrop', 'MANQUANT');
    }
    
    if (i) {
      addResult('   Inner HTML longueur', i.innerHTML.length + ' chars');
      if (i.innerHTML.length > 0) {
        addResult('   Inner HTML debut', i.innerHTML.substring(0, 150) + '...');
      }
      const s = window.getComputedStyle(i);
      addResult('   Inner display', s.display);
      addResult('   Inner visibility', s.visibility);
    } else {
      addResult('   Inner', 'MANQUANT');
    }
  }, 100);
  
  // Test 6: Verification finale apres 500ms
  setTimeout(() => {
    addResult('6. Verification FINALE apres 500ms', '');
    const b = document.getElementById('publish-modal-backdrop');
    const i = document.getElementById('publish-modal-inner');
    
    if (b && i) {
      const s = window.getComputedStyle(b);
      const rect = b.getBoundingClientRect();
      const isVisible = s.display !== 'none' && b.offsetParent !== null && rect.width > 0 && rect.height > 0;
      const hasContent = i.innerHTML.length > 100;
      
      addResult('   Backdrop display', s.display);
      addResult('   Backdrop visible', isVisible ? 'OUI' : 'NON');
      addResult('   Inner HTML', hasContent ? 'PRESENT (' + i.innerHTML.length + ' chars)' : 'VIDE OU TROP COURT (' + i.innerHTML.length + ' chars)');
      
      if (isVisible && hasContent) {
        addResult('=== RESULTAT FINAL', 'SUCCES - Modal affiche!');
        alert('SUCCES - Modal affiche!\n\nBackdrop display: ' + s.display + '\nInner HTML: ' + i.innerHTML.length + ' chars');
      } else {
        let problem = [];
        if (s.display === 'none') problem.push('display=none');
        if (b.offsetParent === null) problem.push('offsetParent=null');
        if (rect.width === 0 || rect.height === 0) problem.push('taille=0');
        if (!hasContent) problem.push('HTML vide ou trop court');
        addResult('=== RESULTAT FINAL', 'ECHEC - Modal non affiche');
        addResult('   Problemes detectes', problem.join(', '));
        alert('ECHEC - Modal non affiche\n\nProblemes:\n- ' + problem.join('\n- ') + '\n\nBackdrop display: ' + s.display + '\nInner HTML: ' + i.innerHTML.length + ' chars');
      }
    } else {
      addResult('=== RESULTAT FINAL', 'ECHEC - Elements manquants');
      alert('ECHEC - Elements manquants\n\nBackdrop: ' + (b ? 'OK' : 'MANQUANT') + '\nInner: ' + (i ? 'OK' : 'MANQUANT'));
    }
    
    // Afficher tous les resultats
    console.log('\n=== TOUS LES RESULTATS ===');
    results.forEach(r => console.log(r));
    console.log('=== FIN DES RESULTATS ===\n');
    
  }, 500);
  
})();
