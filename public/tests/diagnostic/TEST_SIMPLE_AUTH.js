/**
 * TEST SIMPLE - Vérification askRememberMeAndConnect
 * 
 * Copiez-collez ce script dans la console du navigateur (F12)
 * pour vérifier si askRememberMeAndConnect appelle connectUser directement
 */

(function() {
  console.log('========================================');
  console.log('TEST SIMPLE - askRememberMeAndConnect');
  console.log('========================================\n');
  
  // Vérifier que la fonction existe
  if (typeof window.askRememberMeAndConnect !== 'function') {
    console.error('❌ ERREUR: askRememberMeAndConnect n\'existe pas');
    return;
  }
  
  console.log('✅ askRememberMeAndConnect existe\n');
  
  // Sauvegarder la fonction originale
  const originalConnectUser = window.connectUser;
  let connectUserCalled = false;
  let connectUserArgs = null;
  
  // Intercepter connectUser
  window.connectUser = function(user, tokens, rememberMe) {
    connectUserCalled = true;
    connectUserArgs = { user, tokens, rememberMe };
    console.log('>>> connectUser APPELÉE avec:');
    console.log('   - email:', user.email);
    console.log('   - rememberMe:', rememberMe);
  };
  
  // Test
  console.log('Test en cours...\n');
  try {
    const testUser = { email: 'test@example.com', username: 'testuser', id: 'test123' };
    const testTokens = { access_token: 'test_token', refresh_token: 'test_refresh' };
    
    window.askRememberMeAndConnect(testUser, testTokens);
    
    console.log('\n========================================');
    if (connectUserCalled) {
      console.log('✅✅✅ SUCCÈS !');
      console.log('✅ connectUser a été appelée directement');
      console.log('✅ Le modal ne sera PAS affiché');
      console.log('✅ La protection fonctionne correctement !');
    } else {
      console.log('❌❌❌ ÉCHEC !');
      console.log('❌ connectUser n\'a PAS été appelée');
      console.log('❌ Le modal pourrait être affiché');
      console.log('❌ La protection ne fonctionne PAS');
    }
    console.log('========================================\n');
    
  } catch (error) {
    console.error('\n❌ ERREUR lors du test:', error);
    console.error('Détails:', error.message);
  } finally {
    // Restaurer la fonction originale
    window.connectUser = originalConnectUser;
  }
})();
