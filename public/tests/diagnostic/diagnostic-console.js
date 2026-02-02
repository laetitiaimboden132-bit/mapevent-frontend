// 🔍 SCRIPT DE DIAGNOSTIC BLOC COMPTE
// Copiez-collez ce script dans la console du navigateur (F12 > Console)
// Il fonctionne directement sans fichier externe

(function() {
  console.log('%c🔍 === DIAGNOSTIC BLOC COMPTE ===', 'color: #00ffc3; font-size: 16px; font-weight: bold;');
  console.log('');

  // Fonction de nettoyage (copie de celle dans map_logic.js)
  function cleanAccountText(text) {
    if (!text || typeof text !== 'string') return text;
    let cleaned = text;
    cleaned = cleaned.replace(/^om\/[^\s]*\s*/gi, '');
    cleaned = cleaned.replace(/om\/[^\s]*/gi, '');
    cleaned = cleaned.replace(/^[a-z]+\/[^\s]*\s*/gi, '');
    cleaned = cleaned.replace(/^[A-Z]+\/[^\s]*\s*/g, '');
    cleaned = cleaned.replace(/[αβεγδεζηθικλμνξοπρστυφχψω]/gi, '');
    cleaned = cleaned.replace(/[^\w\s\u00C0-\u017F\u00E0-\u00FF\u00E9\u00E8\u00EA\u00EB\u00E0\u00E2\u00E7\u00F9\u00FB\u00FC]/g, '');
    cleaned = cleaned.replace(/\/+/g, '');
    cleaned = cleaned.replace(/\s+/g, ' ');
    cleaned = cleaned.trim();
    return cleaned;
  }

  // 1. Vérifier les données dans localStorage
  console.log('%c📦 1. DONNÉES DANS LOCALSTORAGE:', 'color: #3b82f6; font-weight: bold;');
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

  console.log('');

  // 2. Vérifier l'état actuel du DOM
  console.log('%c🌐 2. ÉTAT ACTUEL DU DOM:', 'color: #3b82f6; font-weight: bold;');
  const accountAvatar = document.getElementById('account-avatar');
  const accountName = document.getElementById('account-name');
  const accountBtn = document.getElementById('account-topbar-btn');

  if (accountAvatar) {
    const avatarText = accountAvatar.textContent || accountAvatar.innerHTML || '';
    const avatarHasImage = accountAvatar.querySelector('img');
    console.log('account-avatar:', {
      textContent: accountAvatar.textContent,
      innerHTML: accountAvatar.innerHTML.substring(0, 100),
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

  console.log('');

  // 3. Tester la fonction de nettoyage
  console.log('%c🧹 3. TEST DE LA FONCTION DE NETTOYAGE:', 'color: #3b82f6; font-weight: bold;');
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
    const passed = !cleaned.includes('om/') && !cleaned.includes('ε');
    console.log(`  ${passed ? '✅' : '❌'} "${test}" → "${cleaned}"`);
  });

  console.log('');

  // 4. Recommandations
  console.log('%c💡 4. RECOMMANDATIONS:', 'color: #3b82f6; font-weight: bold;');
  console.log('');

  const recommendations = [];
  let needsCleaning = false;

  // Vérifier localStorage
  try {
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
    const hasOmEpsilon = ['username', 'name', 'firstName', 'lastName'].some(field => {
      const value = currentUser[field];
      return value && typeof value === 'string' && (value.includes('om/') || value.includes('ε'));
    });
    
    if (hasOmEpsilon) {
      recommendations.push('Les données dans localStorage contiennent "om/ε"');
      needsCleaning = true;
    }
  } catch (e) {
    // Ignorer
  }

  // Vérifier DOM
  if (accountName && (accountName.textContent.includes('om/') || accountName.textContent.includes('ε'))) {
    recommendations.push('Le DOM affiche "om/ε" dans account-name');
    needsCleaning = true;
  }

  if (recommendations.length === 0) {
    console.log('✅ Aucun problème détecté - le bloc compte devrait fonctionner correctement');
  } else {
    console.log('⚠️ Problèmes détectés:');
    recommendations.forEach((rec, index) => {
      console.log(`   ${index + 1}. ${rec}`);
    });
    console.log('');
    console.log('🔧 SOLUTION: Exécutez la fonction suivante pour nettoyer:');
    console.log('');
    console.log('%cwindow.nettoyerDonneesUtilisateur()', 'color: #00ffc3; font-weight: bold; font-size: 14px;');
  }

  console.log('');

  // 5. Exposer la fonction de nettoyage globalement
  window.nettoyerDonneesUtilisateur = function() {
    console.log('%c🧹 Nettoyage des données utilisateur...', 'color: #f59e0b; font-weight: bold;');
    
    try {
      const currentUserStr = localStorage.getItem('currentUser');
      if (currentUserStr) {
        const currentUser = JSON.parse(currentUserStr);
        let modified = false;
        
        // Nettoyer les champs textuels
        const fieldsToClean = ['username', 'name', 'firstName', 'lastName'];
        fieldsToClean.forEach(field => {
          if (currentUser[field] && typeof currentUser[field] === 'string') {
            const oldValue = currentUser[field];
            const newValue = cleanAccountText(oldValue);
            if (oldValue !== newValue) {
              currentUser[field] = newValue;
              modified = true;
              console.log(`✅ "${field}" nettoyé: "${oldValue}" → "${newValue}"`);
            }
          }
        });
        
        if (modified) {
          // Sauvegarder
          localStorage.setItem('currentUser', JSON.stringify(currentUser));
          console.log('%c✅ Données nettoyées et sauvegardées!', 'color: #22c55e; font-weight: bold;');
          console.log('%c🔄 Rechargez la page pour voir les changements', 'color: #3b82f6; font-weight: bold;');
          console.log('');
          console.log('Exécutez: location.reload()');
        } else {
          console.log('ℹ️ Aucune modification nécessaire');
        }
      } else {
        console.log('❌ Aucun currentUser dans localStorage');
      }
    } catch (e) {
      console.error('❌ Erreur:', e);
    }
  };

  // 6. Exposer la fonction de rechargement
  window.rechargerPage = function() {
    console.log('🔄 Rechargement de la page...');
    location.reload();
  };

  console.log('%c🔧 FONCTIONS DISPONIBLES:', 'color: #3b82f6; font-weight: bold;');
  console.log('  • window.nettoyerDonneesUtilisateur() - Nettoie les données dans localStorage');
  console.log('  • window.rechargerPage() - Recharge la page');
  console.log('');

  console.log('%c🔍 === FIN DU DIAGNOSTIC ===', 'color: #00ffc3; font-size: 16px; font-weight: bold;');
  console.log('');
  console.log('%c💡 ASTUCE:', 'color: #f59e0b; font-weight: bold;');
  console.log('Si des problèmes sont détectés, exécutez:');
  console.log('%c  window.nettoyerDonneesUtilisateur()', 'color: #00ffc3; font-weight: bold;');
  console.log('Puis:');
  console.log('%c  window.rechargerPage()', 'color: #00ffc3; font-weight: bold;');
  console.log('');

})();




