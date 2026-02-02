// Script pour forcer l'affichage de la photo dans le bloc compte
// Copiez-collez ce script dans la console du navigateur (F12 > Console)

(function() {
  console.log('%c🔧 === FORCER AFFICHAGE PHOTO BLOC COMPTE ===', 'color: #00ffc3; font-size: 16px; font-weight: bold;');
  console.log('');
  
  // 1. Vérifier les données
  const userStr = localStorage.getItem('currentUser');
  if (!userStr) {
    console.error('❌ Aucun currentUser dans localStorage');
    return;
  }
  
  const user = JSON.parse(userStr);
  const photoUrl = user.profilePhoto || user.profile_photo_url || user.avatar;
  
  console.log('📦 Données utilisateur:', {
    isLoggedIn: user.isLoggedIn,
    googleValidated: user.googleValidated,
    profilePhoto: photoUrl?.substring(0, 80),
    profile_photo_url: user.profile_photo_url?.substring(0, 80),
    avatar: user.avatar?.substring(0, 80)
  });
  
  if (!photoUrl || (!photoUrl.startsWith('http') && !photoUrl.startsWith('data:image'))) {
    console.warn('⚠️ Aucune URL photo valide trouvée');
    return;
  }
  
  // 2. Forcer l'affichage de la photo
  const avatar = document.getElementById('account-avatar');
  const name = document.getElementById('account-name');
  
  if (!avatar || !name) {
    console.error('❌ account-avatar ou account-name non trouvé');
    return;
  }
  
  console.log('🔄 Mise à jour forcée du bloc compte...');
  
  // Nettoyer
  avatar.innerHTML = '';
  avatar.style.background = 'transparent';
  avatar.style.border = 'none';
  
  // Créer l'image
  const img = document.createElement('img');
  img.src = photoUrl;
  img.style.width = '100%';
  img.style.height = '100%';
  img.style.borderRadius = '50%';
  img.style.objectFit = 'cover';
  img.style.display = 'block';
  
  img.onload = function() {
    console.log('%c✅ Photo chargée avec succès!', 'color: #22c55e; font-weight: bold;');
  };
  
  img.onerror = function() {
    console.error('❌ Erreur chargement photo:', photoUrl.substring(0, 80));
    avatar.innerHTML = '';
    avatar.textContent = "👤";
    avatar.style.background = 'rgba(0, 255, 195, 0.1)';
    avatar.style.border = '1px solid rgba(0, 255, 195, 0.2)';
  };
  
  avatar.appendChild(img);
  
  // Mettre à jour le nom
  const cleanName = (text) => {
    if (!text || typeof text !== 'string') return text;
    let cleaned = text.replace(/^om\/[^\s]*\s*/gi, '').replace(/om\/[^\s]*/gi, '');
    cleaned = cleaned.replace(/[αβεγδεζηθικλμνξοπρστυφχψω]/gi, '');
    cleaned = cleaned.replace(/[^\w\s\u00C0-\u017F\u00E0-\u00FF]/g, '');
    return cleaned.replace(/\/+/g, '').replace(/\s+/g, ' ').trim();
  };
  
  const displayName = user.username || cleanName(user.name) || user.email?.split('@')[0] || "Compte";
  name.textContent = displayName;
  name.innerHTML = displayName;
  
  console.log('✅ Bloc compte mis à jour avec:', {
    photo: photoUrl.substring(0, 50) + '...',
    name: displayName
  });
  
  console.log('');
  console.log('%c✅ === FIN ===', 'color: #00ffc3; font-size: 16px; font-weight: bold;');
})();




