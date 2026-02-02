// Test ULTRA SIMPLE - Force l'affichage
// Copiez TOUT ce code dans la console

// ETAPE 1: Verifier l'utilisateur
alert('ETAPE 1: Verification utilisateur');
const userOk = typeof currentUser !== 'undefined' && currentUser && currentUser.isLoggedIn;
alert('Utilisateur connecte: ' + (userOk ? 'OUI' : 'NON'));

if (!userOk) {
  alert('❌ ARRET - Vous devez etre connecte pour tester le modal!\n\nConnectez-vous d\'abord avec le bouton "Compte"');
} else {
  // ETAPE 2: Verifier la fonction
  alert('ETAPE 2: Verification fonction');
  const funcOk = typeof window.openPublishModal === 'function';
  alert('Fonction openPublishModal: ' + (funcOk ? 'EXISTE' : 'MANQUANTE'));
  
  if (!funcOk) {
    alert('❌ ERREUR - La fonction openPublishModal n\'existe pas!');
  } else {
    // ETAPE 3: Verifier les elements avant
    alert('ETAPE 3: Verification elements AVANT appel');
    const backdropBefore = document.getElementById('publish-modal-backdrop');
    const innerBefore = document.getElementById('publish-modal-inner');
    alert('Backdrop: ' + (backdropBefore ? 'EXISTE' : 'MANQUANT') + '\nInner: ' + (innerBefore ? 'EXISTE' : 'MANQUANT'));
    
    // ETAPE 4: Appel de la fonction
    alert('ETAPE 4: Appel de openPublishModal()...\n\nAppuyez sur OK pour continuer.');
    try {
      window.openPublishModal();
      alert('Appel termine sans erreur');
    } catch (e) {
      alert('❌ ERREUR lors de l\'appel: ' + e.message);
    }
    
    // ETAPE 5: Verification apres 500ms
    setTimeout(() => {
      alert('ETAPE 5: Verification apres 500ms');
      const b = document.getElementById('publish-modal-backdrop');
      const i = document.getElementById('publish-modal-inner');
      
      if (!b || !i) {
        alert('❌ ECHEC - Elements manquants apres appel\n\nBackdrop: ' + (b ? 'OK' : 'MANQUANT') + '\nInner: ' + (i ? 'OK' : 'MANQUANT'));
      } else {
        const s = window.getComputedStyle(b);
        const rect = b.getBoundingClientRect();
        const isVisible = s.display !== 'none' && b.offsetParent !== null && rect.width > 0 && rect.height > 0;
        const hasContent = i.innerHTML.length > 100;
        
        let result = 'RESULTAT FINAL:\n\n';
        result += 'Backdrop display: ' + s.display + '\n';
        result += 'Backdrop visible: ' + (isVisible ? 'OUI' : 'NON') + '\n';
        result += 'Backdrop taille: ' + rect.width + 'x' + rect.height + '\n';
        result += 'Inner HTML: ' + i.innerHTML.length + ' chars\n\n';
        
        if (isVisible && hasContent) {
          result += '✅✅✅ SUCCES - Modal affiche!';
        } else {
          result += '❌❌❌ ECHEC - Modal non affiche\n\n';
          result += 'Problemes:\n';
          if (s.display === 'none') result += '- display=none\n';
          if (b.offsetParent === null) result += '- offsetParent=null\n';
          if (rect.width === 0 || rect.height === 0) result += '- taille=0\n';
          if (!hasContent) result += '- HTML trop court (' + i.innerHTML.length + ' chars)\n';
        }
        
        alert(result);
      }
    }, 500);
  }
}
