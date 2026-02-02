// Script de diagnostic pour identifier l'origine de "om/ε" dans le bloc compte
// À exécuter dans la console du navigateur (F12 > Console)

console.log('🔍 === DIAGNOSTIC BLOC COMPTE ===\n');

// 1. Vérifier les données dans localStorage
console.log('📦 1. DONNÉES DANS LOCALSTORAGE:');
try {
  const currentUserStr = localStorage.getItem('currentUser');
  if (currentUserStr) {
    const currentUser = JSON.parse(currentUserStr);
    console.log('✅ currentUser trouvé:', {
      isLoggedIn: currentUser.isLoggedIn,
      username: currentUser.username,
      name: currentUser.name,
      firstName: currentUser.firstName,
      lastName: currentUser.lastName,
      email: currentUser.email,
      avatar: currentUser.avatar,
      profilePhoto: currentUser.profilePhoto,
      profile_photo_url: currentUser.profile_photo_url
    });
    
    // Vérifier si "om/" ou "ε" est présent
    const fieldsToCheck = ['username', 'name', 'firstName', 'lastName', 'avatar'];
    let foundOmEpsilon = false;
    
    fieldsToCheck.forEach(field => {
      const value = currentUser[field];
      if (value && typeof value === 'string') {
        if (value.includes('om/') || value.includes('ε') || value.includes('om/ε')) {
          console.warn(`⚠️ "${field}" contient "om/" ou "ε":`, value);
          foundOmEpsilon = true;
        }
      }
    });
    
    if (!foundOmEpsilon) {
      console.log('✅ Aucun "om/" ou "ε" trouvé dans les champs textuels');
    }
  } else {
    console.log('❌ Aucun currentUser dans localStorage');
  }
} catch (e) {
  console.error('❌ Erreur lors de la lecture de currentUser:', e);
}

console.log('\n');

// 2. Vérifier l'état actuel du DOM
console.log('🌐 2. ÉTAT ACTUEL DU DOM:');
const accountAvatar = document.getElementById('account-avatar');
const accountName = document.getElementById('account-name');
const accountBtn = document.getElementById('account-topbar-btn');

if (accountAvatar) {
  const avatarText = accountAvatar.textContent || accountAvatar.innerHTML || '';
  const avatarHasImage = accountAvatar.querySelector('img');
  console.log('account-avatar:', {
    textContent: accountAvatar.textContent,
    innerHTML: accountAvatar.innerHTML,
    hasImage: !!avatarHasImage,
    imageSrc: avatarHasImage ? avatarHasImage.src : null,
    containsOm: avatarText.includes('om/') || avatarText.includes('ε'),
    fullContent: avatarText
  });
  
  if (avatarText.includes('om/') || avatarText.includes('ε')) {
    console.warn('⚠️ account-avatar contient "om/" ou "ε"');
  }
} else {
  console.log('❌ account-avatar non trouvé dans le DOM');
}

if (accountName) {
  const nameText = accountName.textContent || accountName.innerHTML || '';
  console.log('account-name:', {
    textContent: accountName.textContent,
    innerHTML: accountName.innerHTML,
    containsOm: nameText.includes('om/') || nameText.includes('ε'),
    fullContent: nameText
  });
  
  if (nameText.includes('om/') || nameText.includes('ε')) {
    console.warn('⚠️ account-name contient "om/" ou "ε":', nameText);
  }
} else {
  console.log('❌ account-name non trouvé dans le DOM');
}

if (accountBtn) {
  console.log('account-topbar-btn:', {
    fullText: accountBtn.textContent,
    containsOm: accountBtn.textContent.includes('om/') || accountBtn.textContent.includes('ε')
  });
  
  if (accountBtn.textContent.includes('om/') || accountBtn.textContent.includes('ε')) {
    console.warn('⚠️ account-topbar-btn contient "om/" ou "ε":', accountBtn.textContent);
  }
} else {
  console.log('❌ account-topbar-btn non trouvé dans le DOM');
}

console.log('\n');

// 3. Vérifier les fonctions de nettoyage
console.log('🧹 3. FONCTIONS DE NETTOYAGE:');
try {
  // Vérifier si cleanAccountText existe
  if (typeof cleanAccountText === 'function') {
    console.log('✅ cleanAccountText existe');
    
    // Tester avec des exemples
    const testCases = [
      'om/ε Laetibibi',
      'om/Laetibibi',
      'Laetibibi om/ε',
      'om/test/ε',
      'Laetibibi'
    ];
    
    console.log('Tests de nettoyage:');
    testCases.forEach(test => {
      const cleaned = cleanAccountText(test);
      console.log(`  "${test}" → "${cleaned}"`);
    });
  } else {
    console.warn('⚠️ cleanAccountText n\'existe pas (peut être dans une closure)');
  }
  
  // Vérifier si getUserAvatar existe
  if (typeof getUserAvatar === 'function') {
    console.log('✅ getUserAvatar existe');
    try {
      const avatar = getUserAvatar();
      console.log('  Avatar actuel:', avatar);
    } catch (e) {
      console.warn('  Erreur lors de l\'appel:', e.message);
    }
  } else {
    console.warn('⚠️ getUserAvatar n\'existe pas (peut être dans une closure)');
  }
  
  // Vérifier si getUserDisplayName existe
  if (typeof getUserDisplayName === 'function') {
    console.log('✅ getUserDisplayName existe');
    try {
      const name = getUserDisplayName();
      console.log('  Nom actuel:', name);
    } catch (e) {
      console.warn('  Erreur lors de l\'appel:', e.message);
    }
  } else {
    console.warn('⚠️ getUserDisplayName n\'existe pas (peut être dans une closure)');
  }
} catch (e) {
  console.error('❌ Erreur lors de la vérification des fonctions:', e);
}

console.log('\n');

// 4. Vérifier les MutationObservers
console.log('👁️ 4. MUTATION OBSERVERS:');
try {
  // Vérifier si des observers sont actifs sur account-avatar et account-name
  const avatarObservers = [];
  const nameObservers = [];
  
  // Note: On ne peut pas directement lister les observers, mais on peut vérifier les modifications
  console.log('ℹ️ Les MutationObservers ne peuvent pas être listés directement');
  console.log('ℹ️ Mais on peut vérifier si le bloc est protégé en tentant une modification');
  
  // Test de modification (sera immédiatement restauré par le MutationObserver)
  if (accountName) {
    const originalText = accountName.textContent;
    accountName.textContent = 'TEST_MODIFICATION';
    setTimeout(() => {
      const currentText = accountName.textContent;
      if (currentText === 'TEST_MODIFICATION') {
        console.warn('⚠️ Le MutationObserver ne semble pas actif - la modification persiste');
      } else {
        console.log('✅ Le MutationObserver est actif - la modification a été restaurée');
      }
    }, 100);
  }
} catch (e) {
  console.error('❌ Erreur lors de la vérification des observers:', e);
}

console.log('\n');

// 5. Vérifier l'historique des modifications
console.log('📜 5. HISTORIQUE DES MODIFICATIONS:');
console.log('ℹ️ Vérification des appels récents à updateAccountButton ou updateUserUI...');
console.log('ℹ️ Ces fonctions ont été supprimées, donc aucun appel ne devrait exister');

// Vérifier si les fonctions supprimées existent encore
if (typeof updateAccountButton === 'function') {
  console.warn('⚠️ updateAccountButton existe encore (devrait être supprimée)');
} else {
  console.log('✅ updateAccountButton n\'existe pas (correctement supprimée)');
}

if (typeof updateUserUI === 'function') {
  console.warn('⚠️ updateUserUI existe encore (devrait être supprimée)');
} else {
  console.log('✅ updateUserUI n\'existe pas (correctement supprimée)');
}

console.log('\n');

// 6. Recommandations
console.log('💡 6. RECOMMANDATIONS:');
console.log('');

const recommendations = [];

if (accountName && (accountName.textContent.includes('om/') || accountName.textContent.includes('ε'))) {
  recommendations.push('Nettoyer le localStorage et se reconnecter');
  recommendations.push('Vérifier que le backend nettoie correctement les données');
}

try {
  const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
  const hasOmEpsilon = ['username', 'name', 'firstName', 'lastName'].some(field => {
    const value = currentUser[field];
    return value && typeof value === 'string' && (value.includes('om/') || value.includes('ε'));
  });
  
  if (hasOmEpsilon) {
    recommendations.push('Les données dans localStorage contiennent "om/ε" - nettoyer manuellement');
    recommendations.push('Exécuter: localStorage.removeItem("currentUser") puis se reconnecter');
  }
} catch (e) {
  // Ignorer
}

if (recommendations.length === 0) {
  console.log('✅ Aucun problème détecté - le bloc compte devrait fonctionner correctement');
} else {
  console.log('⚠️ Actions recommandées:');
  recommendations.forEach((rec, index) => {
    console.log(`   ${index + 1}. ${rec}`);
  });
}

console.log('\n');

// 7. Fonction de nettoyage manuel
console.log('🔧 7. FONCTION DE NETTOYAGE MANUEL:');
console.log('Exécutez cette fonction pour nettoyer manuellement les données:');
console.log(`
function nettoyerDonneesUtilisateur() {
  try {
    const currentUserStr = localStorage.getItem('currentUser');
    if (currentUserStr) {
      const currentUser = JSON.parse(currentUserStr);
      
      // Fonction de nettoyage
      const clean = (text) => {
        if (!text || typeof text !== 'string') return text;
        let cleaned = text.replace(/^om\\/[^\\s]*\\s*/gi, '');
        cleaned = cleaned.replace(/om\\/[^\\s]*/gi, '');
        cleaned = cleaned.replace(/[αβεγδεζηθικλμνξοπρστυφχψω]/gi, '');
        cleaned = cleaned.replace(/[^\\w\\s\\u00C0-\\u017F\\u00E0-\\u00FF]/g, '');
        cleaned = cleaned.replace(/\\/+/g, '');
        cleaned = cleaned.replace(/\\s+/g, ' ').trim();
        return cleaned;
      };
      
      // Nettoyer les champs textuels
      if (currentUser.username) currentUser.username = clean(currentUser.username);
      if (currentUser.name) currentUser.name = clean(currentUser.name);
      if (currentUser.firstName) currentUser.firstName = clean(currentUser.firstName);
      if (currentUser.lastName) currentUser.lastName = clean(currentUser.lastName);
      
      // Sauvegarder
      localStorage.setItem('currentUser', JSON.stringify(currentUser));
      console.log('✅ Données nettoyées:', currentUser);
      
      // Recharger la page
      location.reload();
    }
  } catch (e) {
    console.error('❌ Erreur:', e);
  }
}
`);

console.log('\n🔍 === FIN DU DIAGNOSTIC ===\n');




