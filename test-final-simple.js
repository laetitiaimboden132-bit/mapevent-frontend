// TEST FINAL SIMPLE - Copiez TOUT dans la console
const u = typeof currentUser !== 'undefined' && currentUser && currentUser.isLoggedIn;
const f = typeof window.openPublishModal === 'function';
let msg = 'RESULTAT:\n\n1. User: ' + (u ? 'OUI' : 'NON') + '\n2. Fonction: ' + (f ? 'EXISTE' : 'MANQUANTE') + '\n';
if (f && u) {
  try {
    window.openPublishModal();
    setTimeout(() => {
      const b = document.getElementById('publish-modal-backdrop');
      const i = document.getElementById('publish-modal-inner');
      if (b && i) {
        const s = window.getComputedStyle(b);
        const r = b.getBoundingClientRect();
        const v = s.display !== 'none' && b.offsetParent !== null && r.width > 0;
        const c = i.innerHTML.length > 100;
        msg += '3. Display: ' + s.display + '\n4. Visible: ' + (v ? 'OUI' : 'NON') + '\n5. HTML: ' + i.innerHTML.length + ' chars\n\n';
        if (v && c) {
          msg += '✅✅✅ SUCCES!';
        } else {
          msg += '❌❌❌ ECHEC\n\nProblemes:\n';
          if (s.display === 'none') msg += '- display=none\n';
          if (b.offsetParent === null) msg += '- invisible\n';
          if (!c) msg += '- HTML trop court\n';
        }
        alert(msg);
      } else {
        alert(msg + '3. ECHEC - Elements manquants');
      }
    }, 500);
  } catch (e) {
    alert(msg + '3. ERREUR: ' + e.message);
  }
} else {
  alert(msg + '3. SKIP - Pre-requis non remplis');
}
