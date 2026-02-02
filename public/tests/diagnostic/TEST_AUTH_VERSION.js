/**
 * SCRIPT DE DIAGNOSTIC - VERSION AUTH.JS
 * 
 * Exécutez ce script dans la console du navigateur pour diagnostiquer
 * si la bonne version de auth.js est chargée et si askRememberMeAndConnect est correctement désactivée.
 * 
 * Copiez-collez tout ce script dans la console et appuyez sur Entrée.
 */

(function() {
  console.log('🔍🔍🔍 DIAGNOSTIC VERSION AUTH.JS 🔍🔍🔍');
  console.log('==========================================');
  
  // 1. Vérifier si auth.js est chargé
  console.log('\n1️⃣ Vérification chargement auth.js:');
  const authScript = Array.from(document.querySelectorAll('script')).find(s => 
    s.src && s.src.includes('auth.js')
  );
  
  if (authScript) {
    console.log('✅ Script auth.js trouvé dans le DOM');
    console.log('   URL:', authScript.src);
    const versionMatch = authScript.src.match(/auth\.js\?v=(\d{8}-\d{6})/);
    if (versionMatch) {
      console.log('   Version cache-busting:', versionMatch[1]);
    } else {
      console.warn('   ⚠️ Pas de version cache-busting trouvée');
    }
  } else {
    console.error('❌ Script auth.js NON trouvé dans le DOM');
  }
  
  // 2. Vérifier si les fonctions globales existent
  console.log('\n2️⃣ Vérification fonctions globales:');
  console.log('   window.askRememberMeAndConnect:', typeof window.askRememberMeAndConnect);
  console.log('   window.connectUser:', typeof window.connectUser);
  console.log('   window.logout:', typeof window.logout);
  console.log('   window.performLogout:', typeof window.performLogout);
  
  // 3. Vérifier le code source de askRememberMeAndConnect
  console.log('\n3️⃣ Analyse fonction askRememberMeAndConnect:');
  if (typeof window.askRememberMeAndConnect === 'function') {
    const funcString = window.askRememberMeAndConnect.toString();
    console.log('   Longueur du code:', funcString.length, 'caractères');
    console.log('   Premiers 500 caractères:', funcString.substring(0, 500));
    
    // Vérifier si la protection est présente
    if (funcString.includes('connectUser(user, tokens, true)') && funcString.includes('return;')) {
      console.log('   ✅ PROTECTION DÉTECTÉE: La fonction appelle connectUser et retourne immédiatement');
    } else {
      console.error('   ❌ PROTECTION NON DÉTECTÉE: La fonction ne semble pas avoir la protection');
    }
    
    if (funcString.includes('VERSION CORRIGÉE')) {
      console.log('   ✅ Log de version détecté dans le code');
    } else {
      console.warn('   ⚠️ Log de version NON détecté dans le code');
    }
    
    if (funcString.includes('Modal HTML injecté')) {
      console.warn('   ⚠️ Code du modal détecté - La fonction peut encore afficher le modal');
    } else {
      console.log('   ✅ Code du modal NON détecté - La fonction ne devrait pas afficher le modal');
    }
  } else {
    console.error('   ❌ askRememberMeAndConnect n\'existe pas ou n\'est pas une fonction');
  }
  
  // 4. Vérifier les logs dans la console
  console.log('\n4️⃣ Vérification logs de version:');
  console.log('   Cherchez dans la console les messages suivants:');
  console.log('   - 🚨🚨🚨 [AUTH] VERSION 2026-01-15 23:23');
  console.log('   - 🔥🔥🔥 [AUTH] ✅✅✅ VERSION CORRIGÉE');
  console.log('   - [AUTH] API_BASE_URL:');
  
  // 5. Test de la fonction askRememberMeAndConnect
  console.log('\n5️⃣ Test de la fonction askRememberMeAndConnect:');
  if (typeof window.askRememberMeAndConnect === 'function') {
    console.log('   Test avec des données fictives...');
    const testUser = { email: 'test@example.com', username: 'testuser', id: 'test123' };
    const testTokens = { access_token: 'test_token', refresh_token: 'test_refresh' };
    
    // Sauvegarder les fonctions originales pour ne pas perturber
    const originalConnectUser = window.connectUser;
    let connectUserCalled = false;
    let connectUserArgs = null;
    
    // Intercepter connectUser pour voir si elle est appelée
    window.connectUser = function(user, tokens, rememberMe) {
      connectUserCalled = true;
      connectUserArgs = { user, tokens, rememberMe };
      console.log('   ✅ connectUser appelée avec:', { 
        email: user.email, 
        rememberMe 
      });
      if (originalConnectUser) {
        // Restaurer la fonction originale
        window.connectUser = originalConnectUser;
      }
    };
    
    try {
      window.askRememberMeAndConnect(testUser, testTokens);
      
      if (connectUserCalled) {
        console.log('   ✅✅✅ SUCCÈS: askRememberMeAndConnect appelle connectUser directement');
        console.log('   ✅✅✅ Le modal ne devrait PAS être affiché');
      } else {
        console.error('   ❌❌❌ ÉCHEC: askRememberMeAndConnect n\'a PAS appelé connectUser');
        console.error('   ❌❌❌ Le modal pourrait être affiché');
      }
    } catch (error) {
      console.error('   ❌ ERREUR lors du test:', error);
      console.error('   ❌ Détails de l\'erreur:', error.message);
      console.error('   ❌ Stack trace:', error.stack);
    } finally {
      // Restaurer la fonction originale
      if (originalConnectUser) {
        window.connectUser = originalConnectUser;
      }
    }
  } else {
    console.error('   ❌❌❌ ERREUR: askRememberMeAndConnect n\'existe pas ou n\'est pas une fonction');
    console.error('   ❌ Type actuel:', typeof window.askRememberMeAndConnect);
    console.error('   ❌ Cela signifie que auth.js n\'est peut-être pas chargé correctement');
    console.error('   ❌ Vérifiez:');
    console.error('      1. Que auth.js est bien chargé dans l\'onglet Network');
    console.error('      2. Qu\'il n\'y a pas d\'erreurs JavaScript dans la console');
    console.error('      3. Que la page est complètement chargée avant d\'exécuter ce script');
    console.error('   💡 Solution: Attendez que la page soit complètement chargée, puis réessayez');
  }
  
  // 6. Vérifier le Network
  console.log('\n6️⃣ Instructions pour vérifier dans l\'onglet Network:');
  console.log('   1. Ouvrez l\'onglet Network (F12 > Network)');
  console.log('   2. Rechargez la page (Ctrl+F5)');
  console.log('   3. Recherchez "auth.js" dans la liste');
  console.log('   4. Vérifiez que l\'URL contient "auth.js?v=20260115-234450" ou plus récent');
  console.log('   5. Cliquez sur auth.js et vérifiez l\'onglet Response');
  console.log('   6. Recherchez "VERSION 2026-01-15 23:23" dans le contenu');
  
  console.log('\n==========================================');
  console.log('🔍🔍🔍 FIN DU DIAGNOSTIC 🔍🔍🔍');
  console.log('\n📋 RÉSUMÉ:');
  console.log('   - Si vous voyez "✅✅✅ SUCCÈS" au point 5, la protection fonctionne');
  console.log('   - Si vous voyez "❌❌❌ ÉCHEC" au point 5, la protection ne fonctionne pas');
  console.log('   - Vérifiez aussi l\'onglet Network pour confirmer quelle version est chargée');
})();
