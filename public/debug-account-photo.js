// Script de débogage pour diagnostiquer pourquoi la photo ne s'affiche pas
// Copiez-collez ce script dans la console du navigateur (F12 > Console)

(function() {
  console.log('%c🔍 === DIAGNOSTIC PHOTO BLOC COMPTE ===', 'color: #00ffc3; font-size: 16px; font-weight: bold;');
  console.log('');
  
  // 1. Vérifier les données utilisateur
  console.log('%c📦 1. DONNÉES UTILISATEUR:', 'color: #3b82f6; font-weight: bold;');
  try {
    const userStr = localStorage.getItem('currentUser');
    if (userStr) {
      const user = JSON.parse(userStr);
      console.log('currentUser:', {
        isLoggedIn: user.isLoggedIn,
        profilePhoto: user.profilePhoto?.substring(0, 80),
        profile_photo_url: user.profile_photo_url?.substring(0, 80),
        avatar: user.avatar?.substring(0, 80),
        username: user.username,
        name: user.name
      });
      
      // Vérifier quelle URL devrait être utilisée
      const photoUrl = user.profilePhoto || user.profile_photo_url || user.avatar;
      if (photoUrl && (photoUrl.startsWith('http') || photoUrl.startsWith('data:image'))) {
        console.log('%c✅ URL photo trouvée:', 'color: #22c55e; font-weight: bold;', photoUrl.substring(0, 100));
      } else {
        console.warn('%c⚠️ Aucune URL photo valide trouvée', 'color: #f59e0b; font-weight: bold;');
      }
    } else {
      console.log('❌ Aucun currentUser dans localStorage');
    }
  } catch(e) {
    console.error('❌ Erreur:', e);
  }
  
  console.log('');
  
  // 2. Vérifier le DOM
  console.log('%c🌐 2. ÉTAT DU DOM:', 'color: #3b82f6; font-weight: bold;');
  const avatar = document.getElementById('account-avatar');
  const name = document.getElementById('account-name');
  const btn = document.getElementById('account-topbar-btn');
  
  if (avatar) {
    const img = avatar.querySelector('img');
    console.log('account-avatar:', {
      textContent: avatar.textContent,
      innerHTML: avatar.innerHTML.substring(0, 100),
      hasImage: !!img,
      imageSrc: img ? img.src?.substring(0, 80) : null,
      computedStyles: {
        width: getComputedStyle(avatar).width,
        height: getComputedStyle(avatar).height,
        background: getComputedStyle(avatar).background,
        border: getComputedStyle(avatar).border
      }
    });
    
    if (img) {
      console.log('Image trouvée:', {
        src: img.src?.substring(0, 80),
        complete: img.complete,
        naturalWidth: img.naturalWidth,
        naturalHeight: img.naturalHeight,
        onerror: typeof img.onerror
      });
    }
  } else {
    console.log('❌ account-avatar non trouvé');
  }
  
  if (name) {
    console.log('account-name:', {
      textContent: name.textContent,
      innerHTML: name.innerHTML
    });
  }
  
  if (btn) {
    console.log('account-topbar-btn:', {
      width: btn.offsetWidth,
      height: btn.offsetHeight,
      computedStyles: {
        minWidth: getComputedStyle(btn).minWidth,
        maxWidth: getComputedStyle(btn).maxWidth,
        padding: getComputedStyle(btn).padding
      }
    });
  }
  
  console.log('');
  
  // 3. Tester la fonction updateAccountBlock
  console.log('%c🔧 3. TEST FONCTION:', 'color: #3b82f6; font-weight: bold;');
  if (typeof window.updateAccountBlock === 'function') {
    console.log('✅ window.updateAccountBlock existe');
    console.log('Exécution de updateAccountBlock()...');
    try {
      window.updateAccountBlock();
      console.log('✅ updateAccountBlock() exécutée');
      
      // Vérifier après un court délai
      setTimeout(() => {
        const img = document.getElementById('account-avatar')?.querySelector('img');
        if (img) {
          console.log('%c✅ Image créée après updateAccountBlock:', 'color: #22c55e; font-weight: bold;', {
            src: img.src?.substring(0, 80),
            complete: img.complete
          });
        } else {
          console.warn('%c⚠️ Aucune image créée après updateAccountBlock', 'color: #f59e0b; font-weight: bold;');
        }
      }, 500);
    } catch(e) {
      console.error('❌ Erreur lors de l\'exécution:', e);
    }
  } else {
    console.warn('⚠️ window.updateAccountBlock n\'existe pas');
    console.log('La fonction peut être dans une closure. Essayez de recharger la page.');
  }
  
  console.log('');
  console.log('%c💡 SOLUTION MANUELLE:', 'color: #f59e0b; font-weight: bold;');
  console.log('Si la photo ne s\'affiche pas, exécutez:');
  console.log('%c  window.updateAccountBlock()', 'color: #00ffc3; font-weight: bold;');
  console.log('');
  console.log('%c🔍 === FIN DU DIAGNOSTIC ===', 'color: #00ffc3; font-size: 16px; font-weight: bold;');
})();




