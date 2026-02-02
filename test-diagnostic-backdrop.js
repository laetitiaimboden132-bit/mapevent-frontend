// DIAGNOSTIC COMPLET DU BACKDROP
// Copiez dans la console

(function() {
  const b = document.getElementById('publish-modal-backdrop');
  if (!b) {
    alert('❌ Backdrop non trouve');
    return;
  }
  
  let msg = 'DIAGNOSTIC BACKDROP:\n\n';
  
  // Position dans le DOM
  msg += '1. POSITION DOM:\n';
  msg += '   Parent: ' + (b.parentElement ? b.parentElement.tagName + (b.parentElement.id ? ' #' + b.parentElement.id : '') : 'NULL') + '\n';
  msg += '   Dans body: ' + (b.parentElement === document.body ? 'OUI' : 'NON') + '\n';
  msg += '   offsetParent: ' + (b.offsetParent ? b.offsetParent.tagName : 'NULL (normal pour fixed)') + '\n\n';
  
  // Styles calculés
  const s = window.getComputedStyle(b);
  msg += '2. STYLES CALCULES:\n';
  msg += '   display: ' + s.display + '\n';
  msg += '   visibility: ' + s.visibility + '\n';
  msg += '   opacity: ' + s.opacity + '\n';
  msg += '   position: ' + s.position + '\n';
  msg += '   z-index: ' + s.zIndex + '\n';
  msg += '   top: ' + s.top + '\n';
  msg += '   left: ' + s.left + '\n';
  msg += '   width: ' + s.width + '\n';
  msg += '   height: ' + s.height + '\n\n';
  
  // Styles inline
  msg += '3. STYLES INLINE:\n';
  msg += '   style.display: ' + (b.style.display || 'NON DEFINI') + '\n';
  msg += '   style.visibility: ' + (b.style.visibility || 'NON DEFINI') + '\n';
  msg += '   style.opacity: ' + (b.style.opacity || 'NON DEFINI') + '\n';
  msg += '   hidden attribute: ' + (b.hidden ? 'OUI' : 'NON') + '\n\n';
  
  // Rect
  const r = b.getBoundingClientRect();
  msg += '4. RECTANGLE:\n';
  msg += '   width: ' + r.width + '\n';
  msg += '   height: ' + r.height + '\n';
  msg += '   top: ' + r.top + '\n';
  msg += '   left: ' + r.left + '\n\n';
  
  // Vérification parents
  msg += '5. PARENTS (jusqu\'au body):\n';
  let p = b.parentElement;
  let level = 0;
  while (p && p !== document.body && level < 10) {
    const ps = window.getComputedStyle(p);
    msg += '   Niveau ' + level + ': ' + p.tagName;
    if (p.id) msg += ' #' + p.id;
    if (p.className) msg += ' .' + p.className.split(' ')[0];
    msg += '\n';
    msg += '      display: ' + ps.display + '\n';
    msg += '      visibility: ' + ps.visibility + '\n';
    msg += '      opacity: ' + ps.opacity + '\n';
    if (ps.display === 'none' || ps.visibility === 'hidden' || ps.opacity === '0') {
      msg += '      ⚠️ PROBLÈME DÉTECTÉ!\n';
    }
    p = p.parentElement;
    level++;
  }
  if (p === document.body) {
    msg += '   ✅ Atteint body\n';
  }
  
  // Conclusion
  msg += '\n6. CONCLUSION:\n';
  const isVisible = s.display !== 'none' && s.visibility !== 'hidden' && s.opacity !== '0' && r.width > 0 && r.height > 0;
  if (isVisible) {
    msg += '   ✅ Backdrop devrait etre visible\n';
    msg += '   Si vous ne le voyez pas, probleme de z-index ou autre element par-dessus\n';
  } else {
    msg += '   ❌ Backdrop invisible\n';
    if (s.display === 'none') msg += '   - display est none\n';
    if (s.visibility === 'hidden') msg += '   - visibility est hidden\n';
    if (s.opacity === '0') msg += '   - opacity est 0\n';
    if (r.width === 0 || r.height === 0) msg += '   - taille est 0\n';
  }
  
  alert(msg);
})();
