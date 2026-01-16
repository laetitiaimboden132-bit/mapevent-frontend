// VERSION SIMPLE - Copiez-collez dans la console (F12)

console.log('=== RECHERCHE ERREUR SYNTAXE ===\n');

// 1. Afficher toutes les erreurs de la console
console.log('1. ERREURS DANS LA CONSOLE:');
console.log('   Regardez les messages en rouge ci-dessus');
console.log('   Cliquez sur chaque erreur pour voir le fichier et la ligne\n');

// 2. Vérifier les scripts chargés
console.log('2. SCRIPTS CHARGÉS:');
document.querySelectorAll('script[src]').forEach((s, i) => {
  console.log(`   ${i+1}. ${s.src.split('/').pop()}`);
  const version = s.src.match(/v=([^&]+)/)?.[1];
  if (version) console.log(`      Version: ${version}`);
});
console.log('');

// 3. Tester les fonctions AUTH
console.log('3. FONCTIONS AUTH:');
['openAuthModal', 'performLogin', 'logout', 'getAuthToken'].forEach(f => {
  const exists = typeof window[f] === 'function';
  console.log(`   ${exists ? '✅' : '❌'} ${f}()`);
});
console.log('');

// 4. Instructions pour trouver l'erreur exacte
console.log('4. POUR TROUVER L\'ERREUR EXACTE:');
console.log('   a) Regardez les erreurs en rouge dans la console');
console.log('   b) Cliquez sur chaque erreur');
console.log('   c) Notez:');
console.log('      - Le nom du fichier (ex: map_logic.js)');
console.log('      - Le numéro de ligne (ex: ligne 2562)');
console.log('   d) Ouvrez ce fichier dans l\'éditeur à cette ligne');
console.log('   e) Cherchez un caractère "x" isolé ou une syntaxe invalide');
console.log('');

console.log('=== FIN ===');
