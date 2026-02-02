// ⚠️⚠️⚠️ SOLUTION ULTRA-SIMPLE - Bouton Publier qui fonctionne TOUJOURS
// Ce fichier est chargé en dernier et garantit que le bouton fonctionne

(function() {
  'use strict';
  
  console.log('[PUBLISH FIX] ✅ Script de fix chargé');
  
  // Fonction ULTRA-SIMPLE pour ouvrir le modal
  function openPublishModalSimple() {
    console.log('[PUBLISH FIX] ✅✅✅ openPublishModalSimple appelée');
    
    // Vérifier connexion
    const user = window.currentUser || currentUser;
    if (!user || !user.isLoggedIn) {
      console.log('[PUBLISH FIX] ⚠️ Utilisateur non connecté');
      return;
    }
    
    // Fermer le filtre
    if (typeof explorerOpen !== 'undefined') {
      explorerOpen = false;
    }
    const leftPanel = document.getElementById("left-panel");
    if (leftPanel) {
      leftPanel.style.display = "none";
    }
    
    // Récupérer ou créer les éléments
    let backdrop = document.getElementById("publish-modal-backdrop");
    if (!backdrop) {
      backdrop = document.createElement('div');
      backdrop.id = 'publish-modal-backdrop';
      backdrop.onclick = function(e) {
        if (e.target === backdrop) {
          backdrop.style.display = 'none';
        }
      };
      document.body.appendChild(backdrop);
    }
    
    let modalContainer = document.getElementById("publish-modal");
    if (!modalContainer) {
      modalContainer = document.createElement('div');
      modalContainer.id = 'publish-modal';
      backdrop.appendChild(modalContainer);
    }
    
    let inner = document.getElementById("publish-modal-inner");
    if (!inner) {
      inner = document.createElement('div');
      inner.id = 'publish-modal-inner';
      modalContainer.appendChild(inner);
    }
    
    // Construire le HTML du formulaire
    let formHtml = '';
    if (typeof buildPublishFormHtml === 'function') {
      try {
        formHtml = buildPublishFormHtml();
      } catch (e) {
        console.error('[PUBLISH FIX] Erreur buildPublishFormHtml:', e);
      }
    }
    
    if (!formHtml || formHtml.length < 100) {
      formHtml = '<div style="padding:20px;color:#fff;"><h2>Formulaire de publication</h2><p>Le formulaire se charge...</p></div>';
    }
    
    inner.innerHTML = formHtml;
    
    // FORCER l'affichage avec des styles ULTRA-AGRESSIFS
    backdrop.setAttribute('data-publish-modal', 'true');
    backdrop.style.cssText = 'position:fixed !important; inset:0 !important; display:flex !important; visibility:visible !important; opacity:1 !important; z-index:99999 !important; background:rgba(0,0,0,0.8) !important; align-items:flex-start !important; justify-content:flex-end !important; padding:80px 20px 20px 20px !important; pointer-events:auto !important;';
    
    modalContainer.style.cssText = 'position:relative !important; width:100% !important; max-width:520px !important; background:#1e293b !important; border-radius:16px !important; padding:16px !important; color:#fff !important; max-height:calc(100vh - 100px) !important; overflow-y:auto !important; border:2px solid #00ffc3 !important;';
    
    inner.style.cssText = 'display:block !important; visibility:visible !important; opacity:1 !important; color:#fff !important;';
    
    console.log('[PUBLISH FIX] ✅✅✅ Modal affiché !');
  }
  
  // Attacher le bouton - Essayer plusieurs fois
  function attachButton() {
    const btn = document.getElementById("map-publish-btn");
    if (btn) {
      console.log('[PUBLISH FIX] ✅ Bouton trouvé, attachement du listener...');
      
      // Supprimer tous les anciens listeners
      const newBtn = btn.cloneNode(true);
      btn.parentNode.replaceChild(newBtn, btn);
      
      // Attacher le nouveau listener
      newBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        console.log('[PUBLISH FIX] ✅✅✅ CLIC DÉTECTÉ !');
        openPublishModalSimple();
      }, true);
      
      // Ajouter aussi l'onclick comme fallback
      newBtn.setAttribute('onclick', 'if(typeof window.openPublishModalSimple==="function"){window.openPublishModalSimple();}else if(typeof openPublishModalSimple==="function"){openPublishModalSimple();}');
      
      console.log('[PUBLISH FIX] ✅✅✅ Listener attaché !');
      return true;
    }
    return false;
  }
  
  // Exposer la fonction globalement
  window.openPublishModalSimple = openPublishModalSimple;
  
  // Essayer d'attacher immédiatement
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      setTimeout(attachButton, 100);
      setTimeout(attachButton, 500);
      setTimeout(attachButton, 1000);
    });
  } else {
    attachButton();
    setTimeout(attachButton, 100);
    setTimeout(attachButton, 500);
    setTimeout(attachButton, 1000);
  }
  
  // Surveiller les changements du DOM pour réattacher si le bouton est recréé
  const observer = new MutationObserver(function(mutations) {
    const btn = document.getElementById("map-publish-btn");
    if (btn && !btn.hasAttribute('data-fix-attached')) {
      console.log('[PUBLISH FIX] 🔍 Bouton recréé détecté, réattachement...');
      btn.setAttribute('data-fix-attached', 'true');
      attachButton();
    }
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
  
  console.log('[PUBLISH FIX] ✅✅✅ Script de fix complètement chargé');
})();
