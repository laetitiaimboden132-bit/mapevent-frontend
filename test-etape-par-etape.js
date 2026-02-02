// Test ETAPE PAR ETAPE - Copiez dans la console
// Ce script teste chaque étape individuellement

console.log('=== TEST ETAPE PAR ETAPE ===');

// ETAPE 1: Vérifier les éléments
console.log('\nETAPE 1: Elements du DOM');
const backdrop = document.getElementById('publish-modal-backdrop');
const inner = document.getElementById('publish-modal-inner');
const btn = document.getElementById('map-publish-btn');

console.log('Backdrop:', backdrop);
console.log('Inner:', inner);
console.log('Bouton:', btn);

// ETAPE 2: Vérifier l'utilisateur
console.log('\nETAPE 2: Utilisateur');
console.log('currentUser existe:', typeof currentUser !== 'undefined');
if (typeof currentUser !== 'undefined') {
  console.log('currentUser:', currentUser);
  console.log('currentUser.isLoggedIn:', currentUser?.isLoggedIn);
}

// ETAPE 3: Vérifier la fonction
console.log('\nETAPE 3: Fonction openPublishModal');
console.log('window.openPublishModal:', typeof window.openPublishModal);
console.log('openPublishModal:', typeof openPublishModal);

// ETAPE 4: Tester l'appel DIRECT
console.log('\nETAPE 4: Appel direct de openPublishModal');
if (typeof window.openPublishModal === 'function') {
  console.log('Appel en cours...');
  try {
    window.openPublishModal();
    console.log('Appel termine sans erreur');
  } catch (e) {
    console.error('ERREUR lors de l\'appel:', e);
  }
} else {
  console.log('Fonction non disponible');
}

// ETAPE 5: Vérifier IMMEDIATEMENT après l'appel
console.log('\nETAPE 5: Verification immediate (0ms)');
setTimeout(() => {
  const b = document.getElementById('publish-modal-backdrop');
  const i = document.getElementById('publish-modal-inner');
  
  if (b) {
    const s = window.getComputedStyle(b);
    console.log('Backdrop display:', s.display);
    console.log('Backdrop visibility:', s.visibility);
    console.log('Backdrop opacity:', s.opacity);
    console.log('Backdrop z-index:', s.zIndex);
    console.log('Backdrop position:', s.position);
    console.log('Backdrop offsetParent:', b.offsetParent);
    const rect = b.getBoundingClientRect();
    console.log('Backdrop rect:', rect);
  }
  
  if (i) {
    console.log('Inner HTML longueur:', i.innerHTML.length);
    if (i.innerHTML.length > 0) {
      console.log('Inner HTML (200 premiers chars):', i.innerHTML.substring(0, 200));
    }
    const s = window.getComputedStyle(i);
    console.log('Inner display:', s.display);
    console.log('Inner visibility:', s.visibility);
  }
}, 0);

// ETAPE 6: Vérifier après 100ms
setTimeout(() => {
  console.log('\nETAPE 6: Verification apres 100ms');
  const b = document.getElementById('publish-modal-backdrop');
  const i = document.getElementById('publish-modal-inner');
  
  if (b) {
    const s = window.getComputedStyle(b);
    console.log('Backdrop display:', s.display);
    console.log('Backdrop visible:', b.offsetParent !== null);
    console.log('Backdrop rect:', b.getBoundingClientRect());
  }
  
  if (i) {
    console.log('Inner HTML longueur:', i.innerHTML.length);
  }
}, 100);

// ETAPE 7: Vérifier après 500ms
setTimeout(() => {
  console.log('\nETAPE 7: Verification apres 500ms');
  const b = document.getElementById('publish-modal-backdrop');
  const i = document.getElementById('publish-modal-inner');
  
  if (b) {
    const s = window.getComputedStyle(b);
    console.log('Backdrop display:', s.display);
    console.log('Backdrop visible:', b.offsetParent !== null);
    const rect = b.getBoundingClientRect();
    console.log('Backdrop rect:', rect.width, 'x', rect.height);
    
    if (s.display === 'none' || rect.width === 0 || rect.height === 0) {
      console.log('PROBLEME: Backdrop invisible ou taille 0');
    } else {
      console.log('OK: Backdrop visible');
    }
  }
  
  if (i) {
    console.log('Inner HTML longueur:', i.innerHTML.length);
    if (i.innerHTML.length < 100) {
      console.log('PROBLEME: Inner HTML trop court ou vide');
    } else {
      console.log('OK: Inner HTML present');
    }
  }
  
  console.log('\n=== FIN DU TEST ===');
}, 500);
