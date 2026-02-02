// TEST FINAL CLEAN - Copiez TOUT dans la console
(function() {
  const u = typeof currentUser !== 'undefined' && currentUser && currentUser.isLoggedIn;
  const f = typeof window.openPublishModal === 'function';
  let resultMsg = 'RESULTAT:\n\n1. User: ' + (u ? 'OUI' : 'NON') + '\n2. Fonction: ' + (f ? 'EXISTE' : 'MANQUANTE') + '\n';
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
          resultMsg += '3. Display: ' + s.display + '\n4. Visible: ' + (v ? 'OUI' : 'NON') + '\n5. HTML: ' + i.innerHTML.length + ' chars\n\n';
          if (v && c) {
            resultMsg += '✅✅✅ SUCCES!';
          } else {
            resultMsg += '❌❌❌ ECHEC\n\nProblemes:\n';
            if (s.display === 'none') resultMsg += '- display=none\n';
            if (b.offsetParent === null) resultMsg += '- invisible\n';
            if (!c) resultMsg += '- HTML trop court\n';
          }
          alert(resultMsg);
        } else {
          alert(resultMsg + '3. ECHEC - Elements manquants');
        }
      }, 500);
    } catch (e) {
      alert(resultMsg + '3. ERREUR: ' + e.message);
    }
  } else {
    alert(resultMsg + '3. SKIP - Pre-requis non remplis');
  }
})();
