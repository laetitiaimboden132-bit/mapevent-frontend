// Script pour corriger l'écran noir
// Copiez-collez dans la console (F12)

console.log('=== CORRECTION ÉCRAN NOIR ===');

// 1. Supprimer les overlays d'erreur
console.log('1. Suppression des overlays d\'erreur...');
const overlays = document.querySelectorAll('[style*="position:fixed"]');
let removed = 0;
overlays.forEach(overlay => {
  const style = window.getComputedStyle(overlay);
  if (style.position === 'fixed' && (style.background.includes('rgba(0,0,0') || style.background.includes('rgb(0,0,0'))) {
    overlay.remove();
    removed++;
    console.log('  Overlay supprimé');
  }
});
console.log(`  ${removed} overlay(s) supprimé(s)`);

// 2. Vérifier le body
console.log('\n2. Vérification du body...');
if (document.body) {
  document.body.style.display = 'block';
  document.body.style.visibility = 'visible';
  document.body.style.opacity = '1';
  console.log('  Body visible');
} else {
  console.error('  Body non trouvé!');
}

// 3. Vérifier les erreurs
console.log('\n3. Vérification des erreurs...');
console.log('  Regardez les erreurs en rouge dans la console');
console.log('  Cliquez sur chaque erreur pour voir le fichier et la ligne');

// 4. Test rapide des fonctions
console.log('\n4. Test des fonctions:');
console.log('  openAuthModal:', typeof window.openAuthModal === 'function' ? 'OK' : 'MANQUANT');
console.log('  getAuthToken:', typeof window.getAuthToken === 'function' ? 'OK' : 'MANQUANT');

console.log('\n=== FIN ===');
console.log('Si l\'écran est toujours noir, regardez les erreurs en rouge dans la console');
