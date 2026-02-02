// Test DIRECT avec alertes pour forcer l'affichage
// Copiez ce code dans la console

alert('DEBUT DU TEST');

const b = document.getElementById('publish-modal-backdrop');
const i = document.getElementById('publish-modal-inner');
const btn = document.getElementById('map-publish-btn');

let msg = 'Elements:\n';
msg += 'Backdrop: ' + (b ? 'OK' : 'MANQUANT') + '\n';
msg += 'Inner: ' + (i ? 'OK' : 'MANQUANT') + '\n';
msg += 'Bouton: ' + (btn ? 'OK' : 'MANQUANT') + '\n';
msg += 'Utilisateur: ' + (typeof currentUser !== 'undefined' && currentUser && currentUser.isLoggedIn ? 'CONNECTE' : 'NON CONNECTE');

alert(msg);

if (typeof window.openPublishModal === 'function') {
  alert('Fonction trouvee, appel...');
  window.openPublishModal();
  
  setTimeout(() => {
    const b2 = document.getElementById('publish-modal-backdrop');
    const i2 = document.getElementById('publish-modal-inner');
    
    let result = 'Resultat apres 500ms:\n';
    if (b2) {
      const s = window.getComputedStyle(b2);
      result += 'Backdrop display: ' + s.display + '\n';
      result += 'Backdrop visible: ' + (b2.offsetParent !== null ? 'OUI' : 'NON') + '\n';
      result += 'Inner HTML: ' + (i2 ? i2.innerHTML.length + ' chars' : 'MANQUANT') + '\n';
      
      if (s.display !== 'none' && i2 && i2.innerHTML.length > 100) {
        result += '\nSUCCES - Modal affiche!';
      } else {
        result += '\nECHEC - Modal non affiche';
      }
    } else {
      result += 'Backdrop MANQUANT';
    }
    
    alert(result);
  }, 500);
} else {
  alert('ERREUR - openPublishModal non trouvee');
}
