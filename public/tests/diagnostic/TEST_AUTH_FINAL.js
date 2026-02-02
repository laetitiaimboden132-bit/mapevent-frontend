// TEST SIMPLE - Copiez-collez dans la console
console.log('TEST VERSION AUTH.JS');
const func = window.askRememberMeAndConnect;
if (!func) {
  console.error('askRememberMeAndConnect n existe pas');
} else {
  const code = func.toString();
  const hasProtection = code.includes('connectUser(user, tokens, true)') && code.includes('return;') && code.indexOf('return;') < code.indexOf('console.log');
  const hasModal = code.includes('Modal HTML injecté');
  console.log('Longueur:', code.length);
  console.log('Protection presente:', hasProtection ? 'OUI' : 'NON');
  console.log('Code modal presente:', hasModal ? 'OUI' : 'NON');
  console.log('Premiers 400 caracteres:', code.substring(0, 400));
  
  // Test fonctionnel
  let connectCalled = false;
  const orig = window.connectUser;
  window.connectUser = function() { connectCalled = true; if(orig) orig.apply(this, arguments); };
  try {
    func({email:'test@test.com', username:'test', id:'1'}, {access_token:'t', refresh_token:'t'});
  } catch(e) { console.error('Erreur:', e); }
  console.log('Test fonctionnel - connectUser appelee:', connectCalled ? 'OUI (OK)' : 'NON (PROBLEME)');
  if(orig) window.connectUser = orig;
}
