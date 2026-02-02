// Script de test pour vérifier que openPublishModal fonctionne
// À exécuter dans la console du navigateur (F12) après avoir chargé la page

console.log('🧪 TEST DU MODAL DE PUBLICATION');
console.log('================================');

// Test 1: Vérifier que la fonction existe
console.log('\n📋 Test 1: Vérification de l\'existence de la fonction');
if (typeof window.openPublishModal === 'function') {
  console.log('✅ window.openPublishModal existe');
} else if (typeof openPublishModal === 'function') {
  console.log('✅ openPublishModal existe (sans window)');
} else {
  console.log('❌ openPublishModal n\'existe pas');
}

// Test 2: Vérifier que les éléments du modal existent
console.log('\n📋 Test 2: Vérification des éléments du modal');
const backdrop = document.getElementById('publish-modal-backdrop');
const inner = document.getElementById('publish-modal-inner');
const modalContainer = document.getElementById('publish-modal');

console.log('Backdrop:', backdrop ? '✅ existe' : '❌ n\'existe pas');
console.log('Inner:', inner ? '✅ existe' : '❌ n\'existe pas');
console.log('Modal Container:', modalContainer ? '✅ existe' : '❌ n\'existe pas');

if (backdrop) {
  console.log('Backdrop display:', backdrop.style.display);
  console.log('Backdrop visibility:', backdrop.style.visibility);
  console.log('Backdrop offsetParent:', backdrop.offsetParent !== null);
}

// Test 3: Vérifier que l'utilisateur est connecté
console.log('\n📋 Test 3: Vérification de la connexion');
if (typeof currentUser !== 'undefined' && currentUser && currentUser.isLoggedIn) {
  console.log('✅ Utilisateur connecté');
  console.log('User ID:', currentUser.id);
  console.log('User email:', currentUser.email);
} else {
  console.log('❌ Utilisateur non connecté');
  console.log('currentUser:', typeof currentUser !== 'undefined' ? currentUser : 'undefined');
}

// Test 4: Vérifier que currentMode existe
console.log('\n📋 Test 4: Vérification de currentMode');
if (typeof currentMode !== 'undefined' && currentMode) {
  console.log('✅ currentMode existe:', currentMode);
} else {
  console.log('❌ currentMode n\'existe pas');
}

// Test 5: Vérifier que window.t() existe
console.log('\n📋 Test 5: Vérification de window.t()');
if (typeof window.t === 'function') {
  console.log('✅ window.t() existe');
} else {
  console.log('❌ window.t() n\'existe pas');
}

// Test 6: Vérifier que buildPublishFormHtml existe
console.log('\n📋 Test 6: Vérification de buildPublishFormHtml');
if (typeof buildPublishFormHtml === 'function') {
  console.log('✅ buildPublishFormHtml existe');
  try {
    const testHtml = buildPublishFormHtml();
    console.log('✅ buildPublishFormHtml retourne:', testHtml ? `${testHtml.length} caractères` : 'vide');
  } catch (e) {
    console.log('❌ Erreur lors de l\'appel à buildPublishFormHtml:', e.message);
  }
} else {
  console.log('❌ buildPublishFormHtml n\'existe pas');
}

// Test 7: Tester l'ouverture du modal
console.log('\n📋 Test 7: Test d\'ouverture du modal');
console.log('Appel de openPublishModal()...');

try {
  if (typeof window.openPublishModal === 'function') {
    window.openPublishModal();
  } else if (typeof openPublishModal === 'function') {
    openPublishModal();
  } else {
    console.log('❌ Impossible d\'appeler openPublishModal - fonction non trouvée');
  }
  
  // Attendre un peu puis vérifier
  setTimeout(() => {
    console.log('\n📋 Vérification après appel:');
    const backdropAfter = document.getElementById('publish-modal-backdrop');
    const innerAfter = document.getElementById('publish-modal-inner');
    
    if (backdropAfter) {
      console.log('Backdrop display après:', backdropAfter.style.display);
      console.log('Backdrop visible après:', backdropAfter.offsetParent !== null);
      const rect = backdropAfter.getBoundingClientRect();
      console.log('Backdrop rect:', rect.width, 'x', rect.height);
    }
    
    if (innerAfter) {
      console.log('Inner HTML longueur après:', innerAfter.innerHTML.length);
      console.log('Inner display après:', innerAfter.style.display);
    }
    
    if (backdropAfter && backdropAfter.style.display === 'flex' && innerAfter && innerAfter.innerHTML.length > 0) {
      console.log('✅✅✅ MODAL AFFICHÉ AVEC SUCCÈS !');
    } else {
      console.log('❌❌❌ MODAL NON AFFICHÉ - Vérifiez les logs ci-dessus');
    }
  }, 500);
  
} catch (e) {
  console.log('❌ Erreur lors de l\'appel:', e.message);
  console.log('Stack:', e.stack);
}

console.log('\n✅ Tests terminés - Vérifiez les résultats ci-dessus');
