// Script pour surveiller les modifications du backdrop
// Copiez dans la console AVANT de cliquer sur "Publier"

(function() {
  const b = document.getElementById('publish-modal-backdrop');
  if (!b) {
    alert('Backdrop non trouve - attendez que la page charge');
    return;
  }
  
  console.log('🔍 Surveillance du backdrop active...');
  
  // Créer un MutationObserver pour surveiller les changements d'attributs
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
        const s = window.getComputedStyle(b);
        console.log('⚠️ STYLE MODIFIÉ:', {
          display: s.display,
          visibility: s.visibility,
          opacity: s.opacity,
          zIndex: s.zIndex,
          stack: new Error().stack
        });
      }
    });
  });
  
  observer.observe(b, {
    attributes: true,
    attributeFilter: ['style', 'class', 'hidden']
  });
  
  // Surveiller aussi les changements de propriétés style
  const originalSetProperty = b.style.setProperty;
  b.style.setProperty = function(...args) {
    console.log('⚠️ setProperty appelé:', args);
    return originalSetProperty.apply(this, args);
  };
  
  const originalCssTextSetter = Object.getOwnPropertyDescriptor(CSSStyleDeclaration.prototype, 'cssText').set;
  Object.defineProperty(b.style, 'cssText', {
    set: function(value) {
      console.log('⚠️ cssText modifié:', value);
      return originalCssTextSetter.call(this, value);
    },
    get: function() {
      return originalCssTextSetter;
    }
  });
  
  alert('✅ Surveillance active!\n\nCliquez maintenant sur "Publier" et regardez la console pour voir qui modifie les styles.');
})();
