// TRACE TOUS LES APPELS A askRememberMeAndConnect
// Copiez-collez dans la console AVANT de créer le compte

(function() {
  console.log('🔍 TRACE askRememberMeAndConnect - Installation...');
  
  const originalFunc = window.askRememberMeAndConnect;
  if (!originalFunc) {
    console.error('❌ askRememberMeAndConnect n existe pas');
    return;
  }
  
  // Intercepter tous les appels
  window.askRememberMeAndConnect = function(user, tokens) {
    console.error('🚨🚨🚨 APPEL DETECTE a askRememberMeAndConnect');
    console.error('🚨 Stack trace:', new Error().stack);
    console.error('🚨 User:', user?.email || 'N/A');
    console.error('🚨 Appele depuis:', arguments.callee.caller?.name || 'inconnu');
    
    // Appeler la fonction originale
    return originalFunc.apply(this, arguments);
  };
  
  console.log('✅ Trace installee - Tous les appels seront logges');
  console.log('📋 Maintenant, creez un compte et regardez les logs');
})();
