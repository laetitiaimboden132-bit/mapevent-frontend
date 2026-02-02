// Script de test COMPLET pour diagnostiquer le problème du modal de publication
// À exécuter dans la console du navigateur (F12) après avoir chargé la page

console.log('🧪 ========================================');
console.log('🧪 TEST COMPLET DU MODAL DE PUBLICATION');
console.log('🧪 ========================================');

// Test 1: Vérifier que la fonction existe
console.log('\n📋 Test 1: Vérification de l\'existence de la fonction');
const hasWindowOpenPublishModal = typeof window.openPublishModal === 'function';
const hasOpenPublishModal = typeof openPublishModal === 'function';
console.log('window.openPublishModal:', hasWindowOpenPublishModal ? '✅ existe' : '❌ n\'existe pas');
console.log('openPublishModal:', hasOpenPublishModal ? '✅ existe' : '❌ n\'existe pas');

// Test 2: Vérifier que les éléments du modal existent
console.log('\n📋 Test 2: Vérification des éléments du modal');
const backdrop = document.getElementById('publish-modal-backdrop');
const inner = document.getElementById('publish-modal-inner');
const modalContainer = document.getElementById('publish-modal');

console.log('Backdrop:', backdrop ? '✅ existe' : '❌ n\'existe pas');
console.log('Inner:', inner ? '✅ existe' : '❌ n\'existe pas');
console.log('Modal Container:', modalContainer ? '✅ existe' : '❌ n\'existe pas');

if (backdrop) {
  const backdropStyles = window.getComputedStyle(backdrop);
  console.log('Backdrop styles:', {
    display: backdropStyles.display,
    visibility: backdropStyles.visibility,
    opacity: backdropStyles.opacity,
    zIndex: backdropStyles.zIndex,
    position: backdropStyles.position,
    width: backdropStyles.width,
    height: backdropStyles.height
  });
  console.log('Backdrop offsetParent:', backdrop.offsetParent !== null ? '✅ visible' : '❌ invisible');
  console.log('Backdrop rect:', backdrop.getBoundingClientRect());
}

if (inner) {
  console.log('Inner HTML longueur:', inner.innerHTML.length);
  console.log('Inner HTML (premiers 200 chars):', inner.innerHTML.substring(0, 200));
}

// Test 3: Vérifier que l'utilisateur est connecté
console.log('\n📋 Test 3: Vérification de la connexion');
if (typeof currentUser !== 'undefined' && currentUser && currentUser.isLoggedIn) {
  console.log('✅ Utilisateur connecté');
  console.log('User ID:', currentUser.id);
  console.log('User email:', currentUser.email);
  console.log('User name:', currentUser.name);
} else {
  console.log('❌ Utilisateur non connecté');
  console.log('currentUser:', typeof currentUser !== 'undefined' ? currentUser : 'undefined');
  console.log('⚠️ Le bouton Publier ne devrait PAS fonctionner si vous n\'êtes pas connecté');
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
  try {
    const testTranslation = window.t('test');
    console.log('Test translation:', testTranslation);
  } catch (e) {
    console.log('❌ Erreur lors de l\'appel à window.t():', e.message);
  }
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
    if (testHtml && testHtml.length > 0) {
      console.log('Premiers 200 chars:', testHtml.substring(0, 200));
    }
  } catch (e) {
    console.log('❌ Erreur lors de l\'appel à buildPublishFormHtml:', e.message);
    console.log('Stack:', e.stack);
  }
} else {
  console.log('❌ buildPublishFormHtml n\'existe pas');
}

// Test 7: Vérifier le bouton Publier
console.log('\n📋 Test 7: Vérification du bouton Publier');
const publishBtn = document.getElementById('map-publish-btn');
if (publishBtn) {
  console.log('✅ Bouton Publier trouvé');
  const btnStyles = window.getComputedStyle(publishBtn);
  console.log('Styles du bouton:', {
    display: btnStyles.display,
    visibility: btnStyles.visibility,
    opacity: btnStyles.opacity,
    zIndex: btnStyles.zIndex,
    pointerEvents: btnStyles.pointerEvents,
    position: btnStyles.position
  });
  console.log('Bouton onclick:', publishBtn.onclick ? '✅ a un onclick' : '❌ pas d\'onclick');
  console.log('Bouton rect:', publishBtn.getBoundingClientRect());
} else {
  console.log('❌ Bouton Publier non trouvé');
}

// Test 8: Tester l'ouverture du modal
console.log('\n📋 Test 8: Test d\'ouverture du modal');
console.log('Appel de openPublishModal()...');

try {
  if (hasWindowOpenPublishModal) {
    console.log('Appel via window.openPublishModal()...');
    window.openPublishModal();
  } else if (hasOpenPublishModal) {
    console.log('Appel via openPublishModal()...');
    openPublishModal();
  } else {
    console.log('❌ Impossible d\'appeler openPublishModal - fonction non trouvée');
  }
  
  // Attendre un peu puis vérifier
  setTimeout(() => {
    console.log('\n📋 Vérification après appel (500ms):');
    const backdropAfter = document.getElementById('publish-modal-backdrop');
    const innerAfter = document.getElementById('publish-modal-inner');
    const modalContainerAfter = document.getElementById('publish-modal');
    
    if (backdropAfter) {
      const backdropStylesAfter = window.getComputedStyle(backdropAfter);
      console.log('Backdrop display après:', backdropStylesAfter.display);
      console.log('Backdrop visibility après:', backdropStylesAfter.visibility);
      console.log('Backdrop visible après:', backdropAfter.offsetParent !== null);
      const rect = backdropAfter.getBoundingClientRect();
      console.log('Backdrop rect après:', rect.width, 'x', rect.height, 'à', rect.left, ',', rect.top);
      console.log('Backdrop z-index:', backdropStylesAfter.zIndex);
    } else {
      console.log('❌ Backdrop non trouvé après appel');
    }
    
    if (innerAfter) {
      console.log('Inner HTML longueur après:', innerAfter.innerHTML.length);
      const innerStylesAfter = window.getComputedStyle(innerAfter);
      console.log('Inner display après:', innerStylesAfter.display);
      console.log('Inner visibility après:', innerStylesAfter.visibility);
      if (innerAfter.innerHTML.length > 0) {
        console.log('Inner HTML (premiers 300 chars):', innerAfter.innerHTML.substring(0, 300));
      }
    } else {
      console.log('❌ Inner non trouvé après appel');
    }
    
    if (modalContainerAfter) {
      const containerStylesAfter = window.getComputedStyle(modalContainerAfter);
      console.log('Modal Container display après:', containerStylesAfter.display);
      console.log('Modal Container visible après:', modalContainerAfter.offsetParent !== null);
      const containerRect = modalContainerAfter.getBoundingClientRect();
      console.log('Modal Container rect après:', containerRect.width, 'x', containerRect.height);
    }
    
    // Vérification finale
    if (backdropAfter && 
        (backdropStylesAfter.display === 'flex' || backdropStylesAfter.display === 'block') && 
        innerAfter && 
        innerAfter.innerHTML.length > 100) {
      console.log('\n✅✅✅ MODAL AFFICHÉ AVEC SUCCÈS !');
    } else {
      console.log('\n❌❌❌ MODAL NON AFFICHÉ - Vérifiez les logs ci-dessus');
      if (!backdropAfter) {
        console.log('   → Backdrop n\'existe pas');
      } else if (backdropStylesAfter.display === 'none') {
        console.log('   → Backdrop display = none');
      } else if (!innerAfter) {
        console.log('   → Inner n\'existe pas');
      } else if (innerAfter.innerHTML.length < 100) {
        console.log('   → Inner HTML trop court ou vide');
      }
    }
  }, 500);
  
} catch (e) {
  console.log('❌ Erreur lors de l\'appel:', e.message);
  console.log('Stack:', e.stack);
}

console.log('\n✅ Tests terminés - Vérifiez les résultats ci-dessus');
console.log('📋 Si le modal ne s\'affiche pas, copiez TOUS les logs ci-dessus et partagez-les');
