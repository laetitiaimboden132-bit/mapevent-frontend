// TEST FINAL - Vérifie tout et affiche le résultat
// Copiez dans la console, puis cliquez sur "Publier"

(function() {
  // Attendre que l'utilisateur clique sur "Publier"
  alert('✅ Script de test actif!\n\nCliquez maintenant sur le bouton "Publier" puis attendez 1 seconde.');
  
  setTimeout(() => {
    const b = document.getElementById('publish-modal-backdrop');
    const i = document.getElementById('publish-modal-inner');
    
    if (!b) {
      alert('❌ Backdrop non trouvé - Le modal n\'a pas été créé');
      return;
    }
    
    const s = window.getComputedStyle(b);
    const r = b.getBoundingClientRect();
    
    let msg = 'RESULTAT FINAL:\n\n';
    msg += '1. BACKDROP:\n';
    msg += '   Display: ' + s.display + '\n';
    msg += '   Visibility: ' + s.visibility + '\n';
    msg += '   Opacity: ' + s.opacity + '\n';
    msg += '   Z-index: ' + s.zIndex + '\n';
    msg += '   Taille: ' + r.width + 'x' + r.height + '\n';
    msg += '   data-publish-modal: ' + (b.getAttribute('data-publish-modal') || 'NON') + '\n\n';
    
    msg += '2. INNER:\n';
    if (i) {
      msg += '   HTML: ' + i.innerHTML.length + ' chars\n';
      msg += '   Display: ' + window.getComputedStyle(i).display + '\n';
    } else {
      msg += '   ❌ MANQUANT\n';
    }
    
    msg += '\n3. CONCLUSION:\n';
    const isVisible = s.display === 'flex' && s.visibility === 'visible' && s.opacity === '1' && parseInt(s.zIndex) > 0;
    const hasContent = i && i.innerHTML.length > 100;
    
    if (isVisible && hasContent) {
      msg += '✅✅✅ SUCCES - Modal devrait être visible!\n\n';
      msg += 'Si vous ne le voyez pas, vérifiez:\n';
      msg += '- Un autre élément par-dessus (z-index)\n';
      msg += '- Le modal est hors écran\n';
      msg += '- Un filtre CSS appliqué';
    } else {
      msg += '❌❌❌ ECHEC - Modal invisible\n\n';
      msg += 'Problèmes:\n';
      if (s.display !== 'flex') msg += '- display: ' + s.display + ' (devrait être flex)\n';
      if (s.visibility !== 'visible') msg += '- visibility: ' + s.visibility + ' (devrait être visible)\n';
      if (s.opacity !== '1') msg += '- opacity: ' + s.opacity + ' (devrait être 1)\n';
      if (parseInt(s.zIndex) <= 0) msg += '- z-index: ' + s.zIndex + ' (devrait être > 0)\n';
      if (!hasContent) msg += '- HTML vide ou trop court\n';
      
      msg += '\n🔧 SOLUTION:\n';
      msg += 'Un script modifie les styles après openPublishModal().\n';
      msg += 'Vérifiez la console pour voir qui.';
    }
    
    alert(msg);
  }, 1000);
})();
