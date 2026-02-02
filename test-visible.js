// Test VISIBLE - Affiche les resultats directement sur la page
// Copiez TOUT ce code dans la console

(function() {
  // Creer un div pour afficher les resultats
  let resultDiv = document.getElementById('test-results-div');
  if (!resultDiv) {
    resultDiv = document.createElement('div');
    resultDiv.id = 'test-results-div';
    resultDiv.style.cssText = 'position:fixed !important; top:10px !important; left:10px !important; z-index:999999 !important; background:#1e293b !important; color:#00ffc3 !important; padding:20px !important; border:2px solid #00ffc3 !important; border-radius:8px !important; max-width:600px !important; max-height:80vh !important; overflow-y:auto !important; font-family:monospace !important; font-size:12px !important; box-shadow:0 10px 40px rgba(0,0,0,0.9) !important;';
    document.body.appendChild(resultDiv);
  }
  
  function addResult(text, color) {
    const p = document.createElement('div');
    p.textContent = text;
    p.style.cssText = 'margin:5px 0 !important; padding:5px !important; background:' + (color || '#0f172a') + ' !important; border-left:3px solid ' + (color === 'red' ? '#ef4444' : '#00ffc3') + ' !important;';
    resultDiv.appendChild(p);
    console.log(text);
  }
  
  resultDiv.innerHTML = '';
  addResult('=== TEST MODAL PUBLICATION ===', '#0f172a');
  
  // Test 1: Utilisateur
  const userOk = typeof currentUser !== 'undefined' && currentUser && currentUser.isLoggedIn;
  addResult('1. Utilisateur connecte: ' + (userOk ? 'OUI' : 'NON'), userOk ? '#0f172a' : 'red');
  if (typeof currentUser !== 'undefined' && currentUser) {
    addResult('   - currentUser.isLoggedIn: ' + currentUser.isLoggedIn);
    addResult('   - currentUser.email: ' + (currentUser.email || 'N/A'));
  }
  
  // Test 2: Fonction
  const funcOk = typeof window.openPublishModal === 'function';
  addResult('2. Fonction openPublishModal: ' + (funcOk ? 'EXISTE' : 'MANQUANTE'), funcOk ? '#0f172a' : 'red');
  
  // Test 3: Elements avant
  const backdropBefore = document.getElementById('publish-modal-backdrop');
  const innerBefore = document.getElementById('publish-modal-inner');
  addResult('3. Elements AVANT appel:', '#0f172a');
  addResult('   - Backdrop: ' + (backdropBefore ? 'EXISTE' : 'MANQUANT'));
  addResult('   - Inner: ' + (innerBefore ? 'EXISTE' : 'MANQUANT'));
  
  if (backdropBefore) {
    const s = window.getComputedStyle(backdropBefore);
    addResult('   - Backdrop display avant: ' + s.display);
  }
  
  if (innerBefore) {
    addResult('   - Inner HTML avant: ' + innerBefore.innerHTML.length + ' chars');
  }
  
  // Test 4: Appel
  if (funcOk && userOk) {
    addResult('4. Appel openPublishModal()...', '#0f172a');
    try {
      window.openPublishModal();
      addResult('   - Appel termine sans erreur', '#0f172a');
    } catch (e) {
      addResult('   - ERREUR: ' + e.message, 'red');
    }
  } else {
    addResult('4. Appel: SKIP (pre-requis non remplis)', 'red');
    if (!userOk) addResult('   - Raison: Utilisateur non connecte', 'red');
    if (!funcOk) addResult('   - Raison: Fonction non trouvee', 'red');
  }
  
  // Verification apres 100ms
  setTimeout(() => {
    addResult('5. Verification apres 100ms:', '#0f172a');
    const b = document.getElementById('publish-modal-backdrop');
    const i = document.getElementById('publish-modal-inner');
    
    if (b) {
      const s = window.getComputedStyle(b);
      addResult('   - Backdrop display: ' + s.display);
      addResult('   - Backdrop visibility: ' + s.visibility);
      addResult('   - Backdrop z-index: ' + s.zIndex);
      addResult('   - Backdrop visible: ' + (b.offsetParent !== null ? 'OUI' : 'NON'));
      const rect = b.getBoundingClientRect();
      addResult('   - Backdrop taille: ' + rect.width + 'x' + rect.height);
    } else {
      addResult('   - Backdrop: MANQUANT', 'red');
    }
    
    if (i) {
      addResult('   - Inner HTML: ' + i.innerHTML.length + ' chars');
      if (i.innerHTML.length > 0) {
        addResult('   - Inner HTML debut: ' + i.innerHTML.substring(0, 100) + '...');
      }
    } else {
      addResult('   - Inner: MANQUANT', 'red');
    }
  }, 100);
  
  // Verification finale apres 500ms
  setTimeout(() => {
    addResult('6. Verification FINALE apres 500ms:', '#0f172a');
    const b = document.getElementById('publish-modal-backdrop');
    const i = document.getElementById('publish-modal-inner');
    
    if (b && i) {
      const s = window.getComputedStyle(b);
      const rect = b.getBoundingClientRect();
      const isVisible = s.display !== 'none' && b.offsetParent !== null && rect.width > 0 && rect.height > 0;
      const hasContent = i.innerHTML.length > 100;
      
      addResult('   - Backdrop display: ' + s.display);
      addResult('   - Backdrop visible: ' + (isVisible ? 'OUI' : 'NON'));
      addResult('   - Inner HTML: ' + (hasContent ? i.innerHTML.length + ' chars (OK)' : i.innerHTML.length + ' chars (TROP COURT)'));
      
      if (isVisible && hasContent) {
        addResult('=== RESULTAT FINAL: SUCCES - Modal affiche! ===', '#0f172a');
        alert('✅ SUCCES!\n\nLe modal est affiche correctement.\n\nBackdrop display: ' + s.display + '\nInner HTML: ' + i.innerHTML.length + ' chars');
      } else {
        let problems = [];
        if (s.display === 'none') problems.push('display=none');
        if (b.offsetParent === null) problems.push('offsetParent=null');
        if (rect.width === 0 || rect.height === 0) problems.push('taille=0');
        if (!hasContent) problems.push('HTML vide ou trop court (' + i.innerHTML.length + ' chars)');
        
        addResult('=== RESULTAT FINAL: ECHEC - Modal non affiche ===', 'red');
        addResult('   Problemes detectes:', 'red');
        problems.forEach(p => addResult('   - ' + p, 'red'));
        
        alert('❌ ECHEC!\n\nLe modal ne s\'affiche pas.\n\nProblemes:\n- ' + problems.join('\n- ') + '\n\nBackdrop display: ' + s.display + '\nInner HTML: ' + i.innerHTML.length + ' chars');
      }
    } else {
      addResult('=== RESULTAT FINAL: ECHEC - Elements manquants ===', 'red');
      addResult('   - Backdrop: ' + (b ? 'OK' : 'MANQUANT'), b ? '#0f172a' : 'red');
      addResult('   - Inner: ' + (i ? 'OK' : 'MANQUANT'), i ? '#0f172a' : 'red');
      alert('❌ ECHEC!\n\nElements manquants.\n\nBackdrop: ' + (b ? 'OK' : 'MANQUANT') + '\nInner: ' + (i ? 'OK' : 'MANQUANT'));
    }
    
    // Ajouter un bouton pour fermer
    const closeBtn = document.createElement('button');
    closeBtn.textContent = 'FERMER CE PANEL';
    closeBtn.style.cssText = 'margin-top:10px !important; padding:10px 20px !important; background:#00ffc3 !important; color:#000 !important; border:none !important; border-radius:8px !important; cursor:pointer !important; font-weight:600 !important;';
    closeBtn.onclick = () => resultDiv.remove();
    resultDiv.appendChild(closeBtn);
    
  }, 500);
  
})();
