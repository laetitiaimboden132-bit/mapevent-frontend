// ============================================================
// registration.js
// Formulaire d'inscription 3 étapes (openLoginModal, showProRegisterForm, completeRegistration, verifyEmailCode)
// Extrait de map_logic.js (lignes 14995-20850)
// ============================================================

function openLoginModal() {
  // ⚠️⚠️⚠️ SIMPLE : Appeler directement window.openLoginModal de auth.js
  if (typeof window.openLoginModal === 'function') {
    const authFn = window.openLoginModal;
    const fnSource = authFn.toString();
    // ⚠️⚠️⚠️ VÉRIFICATION : Si ce n'est pas le wrapper lui-même, l'appeler
    if (!fnSource.includes('openLoginModalCalling')) {
      return authFn();
    }
  }
  
  // Si auth.js n'est pas encore chargé, attendre un peu
  setTimeout(() => {
    if (typeof window.openLoginModal === 'function') {
      const authFn = window.openLoginModal;
      const fnSource = authFn.toString();
      if (!fnSource.includes('openLoginModalCalling')) {
        return authFn();
      }
    }
    // Fallback vers openAuthModal si nécessaire
    if (typeof window.openAuthModal === 'function') {
      return window.openAuthModal('login');
    }
  }, 100);
}

// ⚠️⚠️⚠️ CRITIQUE : NE JAMAIS faire window.openLoginModal = openLoginModal ici !
// Cela créerait une récursion infinie car le wrapper s'appellerait lui-même
// ⚠️⚠️⚠️ SUPPRIMÉ : window.openLoginModal = openLoginModal; (ligne supprimée pour éviter la récursion)

function openRegisterModal() {
  console.log('[AUTH] openRegisterModal (wrapper) called');
  if (typeof window.openAuthModal === 'function') {
    return window.openAuthModal('register');
  } else if (typeof window.openRegisterModal === 'function') {
    // Fallback : utiliser directement window.openRegisterModal si disponible
    return window.openRegisterModal();
  } else {
    console.error('[AUTH] ERREUR: window.openAuthModal non disponible (auth.js non chargé ?)');
  }
}

// ⚠️⚠️⚠️ CRITIQUE : NE JAMAIS écraser window.openLoginModal ici !
// Cela créerait une récursion infinie car le wrapper s'appellerait lui-même via window.openLoginModal()
// window.openLoginModal doit rester la fonction de auth.js uniquement !
// window.openLoginModal = openLoginModal; // ⚠️⚠️⚠️ SUPPRIMÉ pour éviter la récursion infinie
window.openRegisterModal = openRegisterModal;

// REMOVED: Les wrappers openLoginModal et openRegisterModal ne doivent PAS être exposés ici
// car ces fonctions sont déjà dans auth.js et exposées globalement
// Ces wrappers locaux sont conservés pour compatibilité mais ne doivent pas écraser ceux de auth.js

// Fonction pour créer un compte depuis le modal auth
// Gère l'upload de photo dans le formulaire d'inscription
window.handleRegisterPhotoUpload = function(event) {
  const file = event.target.files[0];
  if (!file) return;
  
  if (file.size > 5 * 1024 * 1024) {
    showNotification('⚠️ La photo doit faire moins de 5MB', 'warning');
    return;
  }
  
  const reader = new FileReader();
  reader.onload = function(e) {
    const previewContainer = document.getElementById('register-photo-preview-container');
    const previewImg = document.getElementById('register-photo-preview');
    
    if (previewImg) {
      previewImg.src = e.target.result;
    }
    if (previewContainer) {
      previewContainer.style.display = 'block';
    }
    
    // Stocker temporairement la photo pour l'envoi
    window.registerPhotoData = e.target.result;
    window.registerPhotoFile = file;
  };
  reader.readAsDataURL(file);
};

// Configure l'autocomplete d'adresse pour le formulaire d'inscription
function setupRegisterAddressAutocomplete(inputElement) {
  let timeout;
  const suggestionsContainer = document.getElementById('register-address-suggestions');
  
  inputElement.addEventListener('input', function(e) {
    const query = e.target.value.trim();
    
    clearTimeout(timeout);
    
    if (query.length < 3) {
      if (suggestionsContainer) {
        suggestionsContainer.style.display = 'none';
      }
      return;
    }
    
    // OPTIMISATION: Debounce plus court (300ms) pour réactivité, mais validation stricte maintenue
    timeout = setTimeout(async () => {
      try {
        // VALIDATION STRICTE + PERFORMANCE: Paramètres optimisés pour recherche rapide et exacte
        // addressdetails=1 pour validation complète, limit=5 pour rapidité, language=fr pour pertinence
        // ⚠️⚠️⚠️ RECHERCHE MONDIALE - Pas de restriction de pays, support multilingue
        const langCode = (navigator.language || 'fr').split('-')[0];
        const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=10&addressdetails=1&accept-language=${langCode},en&dedupe=1`, {
          headers: {
            'User-Agent': 'MapEventAI/1.0',
            'Accept-Language': `${langCode},en,fr`
          }
        });
        
        // Gestion d'erreur pour Nominatim (503, timeout, etc.)
        if (!response.ok) {
          console.warn('[REGISTER] Nominatim erreur HTTP:', response.status, response.statusText);
          if (suggestionsContainer) {
            suggestionsContainer.style.display = 'none';
          }
          return;
        }
        
        const text = await response.text();
        let results;
        try {
          results = JSON.parse(text);
        } catch (parseError) {
          console.error('[REGISTER] Erreur parsing JSON Nominatim:', parseError, 'Response:', text.substring(0, 100));
          if (suggestionsContainer) {
            suggestionsContainer.style.display = 'none';
          }
          return;
        }
        
        if (suggestionsContainer && results.length > 0) {
          // TRI INTELLIGENT: Prioriser les résultats avec adresse complète (road + house_number)
          const sortedResults = results.sort((a, b) => {
            const aHasFullAddress = a.address?.road && (a.address?.house_number || a.address?.house);
            const bHasFullAddress = b.address?.road && (b.address?.house_number || b.address?.house);
            if (aHasFullAddress && !bHasFullAddress) return -1;
            if (!aHasFullAddress && bHasFullAddress) return 1;
            return 0;
          });
          
          suggestionsContainer.innerHTML = sortedResults.map(result => {
            const hasFullAddress = result.address?.road && (result.address?.house_number || result.address?.house);
            const addressQuality = hasFullAddress ? '✅' : '📍';
            return `
            <div class="register-address-suggestion" style="padding:12px;cursor:pointer;border-bottom:1px solid rgba(255,255,255,0.1);transition:background 0.2s;" 
                 onmouseover="this.style.background='rgba(0,255,195,0.1)'" 
                 onmouseout="this.style.background='transparent'"
                 data-lat="${result.lat}" 
                 data-lng="${result.lon}"
                 data-label="${result.display_name}"
                 data-country="${result.address?.country_code?.toUpperCase() || ''}"
                 data-city="${result.address?.city || result.address?.town || result.address?.village || ''}"
                 data-postcode="${result.address?.postcode || ''}"
                 data-street="${result.address?.road || ''}">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
                <span style="font-size:14px;">${addressQuality}</span>
                <div style="font-weight:600;color:var(--ui-text-main);font-size:13px;flex:1;">${result.display_name}</div>
              </div>
              <div style="font-size:11px;color:var(--ui-text-muted);padding-left:22px;">${result.address?.country || ''}${result.address?.postcode ? ' • ' + result.address.postcode : ''}</div>
            </div>
          `;
          }).join('');
          
          suggestionsContainer.style.display = 'block';
          
          // Attacher les event listeners aux suggestions
          suggestionsContainer.querySelectorAll('.register-address-suggestion').forEach(suggestion => {
            suggestion.addEventListener('click', function() {
              selectRegisterAddressSuggestion({
                lat: parseFloat(this.dataset.lat),
                lng: parseFloat(this.dataset.lng),
                label: this.dataset.label,
                country_code: this.dataset.country,
                city: this.dataset.city,
                postcode: this.dataset.postcode,
                street: this.dataset.street
              });
            });
          });
        } else if (suggestionsContainer) {
          suggestionsContainer.style.display = 'none';
        }
      } catch (error) {
        console.error('[REGISTER] Erreur autocomplete adresse:', error);
      }
    }, 300);
  });
}

// Sélectionne une adresse depuis les suggestions dans le formulaire d'inscription
function selectRegisterAddressSuggestion(addressData) {
  window.registerSelectedAddress = addressData;
  
  const input = document.getElementById('register-address-input');
  const suggestionsContainer = document.getElementById('register-address-suggestions');
  const selectedDisplay = document.getElementById('register-selected-address-display');
  const selectedLabel = document.getElementById('register-selected-address-label');
  const selectedDetails = document.getElementById('register-selected-address-details');
  
  if (input) {
    input.value = addressData.label;
  }
  if (suggestionsContainer) {
    suggestionsContainer.style.display = 'none';
  }
  if (selectedDisplay) {
    selectedDisplay.style.display = 'block';
  }
  if (selectedLabel) {
    selectedLabel.textContent = addressData.label;
  }
  if (selectedDetails) {
    selectedDetails.textContent = `${addressData.city || ''} ${addressData.postcode || ''} - ${addressData.country_code || ''}`;
  }
}

// Fonction pour afficher l'erreur de timeout d'inscription
function showRegisterTimeoutError(email, username) {
  const authModal = document.getElementById('authModal');
  if (!authModal) return;
  
  const html = `
    <div style="text-align:center;padding:40px 20px;position:relative;">
      <!-- Bouton X (croix) pour fermer -->
      <button onclick="closeAuthModal()" style="position:absolute;top:16px;right:16px;background:none;border:none;color:var(--ui-text-muted);font-size:24px;cursor:pointer;padding:8px;width:40px;height:40px;display:flex;align-items:center;justify-content:center;border-radius:50%;transition:all 0.2s;z-index:10;" onmouseover="this.style.background='rgba(239,68,68,0.2)';this.style.color='#ef4444';this.style.transform='scale(1.1)';" onmouseout="this.style.background='none';this.style.color='var(--ui-text-muted)';this.style.transform='scale(1)';" title="Fermer">✕</button>
      
      <div style="font-size:64px;margin-bottom:20px;">⏱️</div>
      <h2 style="margin:0 0 12px;font-size:24px;font-weight:700;color:#fff;">Quelque chose cloche...</h2>
      <p style="margin:0 0 24px;font-size:14px;color:var(--ui-text-muted);line-height:1.6;">
        L'inscription prend trop de temps (cold start probable).<br>
        Veuillez réessayer ou vous connecter si vous avez déjà un compte.
      </p>
      <div style="display:flex;flex-direction:column;gap:12px;">
        <button onclick="closeAuthModal(); setTimeout(() => { openAuthModal('register'); const el = document.getElementById('register-email'); if (el && '${email}') el.value = '${email}'; const el2 = document.getElementById('register-username'); if (el2 && '${username}') el2.value = '${username}'; }, 200);" style="width:100%;padding:14px;border-radius:12px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:700;font-size:15px;cursor:pointer;">
          🔄 Réessayer
        </button>
        <button onclick="closeAuthModal(); setTimeout(() => openAuthModal('login'), 200);" style="width:100%;padding:14px;border-radius:12px;border:2px solid rgba(255,255,255,0.2);background:transparent;color:#fff;font-weight:600;font-size:15px;cursor:pointer;">
          🔐 Se connecter
        </button>
        <button onclick="closeAuthModal()" style="width:100%;padding:12px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:transparent;color:var(--ui-text-muted);font-weight:600;font-size:14px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(255,255,255,0.3)';this.style.color='var(--ui-text-main)';" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)';this.style.color='var(--ui-text-muted)';">
          Annuler
        </button>
      </div>
    </div>
  `;
  
  authModal.innerHTML = html;
}

// Fonction pour afficher l'erreur de conflit (409)
function showRegisterConflictError(errorData, email) {
  const authModal = document.getElementById('authModal');
  if (!authModal) return;
  
  // Message clair selon le champ en conflit
  let errorMsg = 'Un compte existe déjà avec cet email.';
  let isEmailConflict = false;
  
  if (errorData.code === 'USERNAME_ALREADY_EXISTS') {
    errorMsg = 'Ce nom d\'utilisateur est déjà pris.';
  } else if (errorData.code === 'EMAIL_ALREADY_EXISTS' || errorData.field === 'email') {
    errorMsg = 'Un compte existe déjà avec cet email.';
    isEmailConflict = true;
  } else if (errorData.error) {
    errorMsg = errorData.error;
  }
  
  const html = `
    <div style="text-align:center;padding:40px 20px;position:relative;">
      <!-- Bouton X (croix) pour fermer -->
      <button onclick="closeAuthModal()" style="position:absolute;top:16px;right:16px;background:none;border:none;color:var(--ui-text-muted);font-size:24px;cursor:pointer;padding:8px;width:40px;height:40px;display:flex;align-items:center;justify-content:center;border-radius:50%;transition:all 0.2s;z-index:10;" onmouseover="this.style.background='rgba(239,68,68,0.2)';this.style.color='#ef4444';this.style.transform='scale(1.1)';" onmouseout="this.style.background='none';this.style.color='var(--ui-text-muted)';this.style.transform='scale(1)';" title="Fermer">✕</button>
      
      <div style="font-size:64px;margin-bottom:20px;">⚠️</div>
      <h2 style="margin:0 0 12px;font-size:24px;font-weight:700;color:#fff;">Compte déjà existant</h2>
      <p style="margin:0 0 24px;font-size:14px;color:var(--ui-text-muted);line-height:1.6;">
        ${errorMsg}<br>
        ${isEmailConflict ? 'Connecte-toi avec ton compte existant.' : 'Veuillez choisir un autre nom d\'utilisateur.'}
      </p>
      <div style="display:flex;flex-direction:column;gap:12px;">
        ${isEmailConflict ? `
          <button onclick="closeAuthModal(); setTimeout(() => { openAuthModal('login'); setTimeout(() => { const el = document.getElementById('login-email'); if (el && '${email}') el.value = '${email}'; }, 300); }, 200);" style="width:100%;padding:14px;border-radius:12px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:700;font-size:15px;cursor:pointer;">
            🔐 Se connecter
          </button>
          <button onclick="showNotification('Fonctionnalité à venir', 'info')" style="width:100%;padding:12px;border-radius:12px;border:none;background:transparent;color:var(--ui-text-muted);font-weight:500;font-size:14px;cursor:pointer;">
            🔑 Mot de passe oublié
          </button>
        ` : `
          <button onclick="closeAuthModal(); setTimeout(() => openAuthModal('register'), 200);" style="width:100%;padding:14px;border-radius:12px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:700;font-size:15px;cursor:pointer;">
            🔄 Réessayer avec un autre nom
          </button>
        `}
        <button onclick="closeAuthModal()" style="width:100%;padding:12px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:transparent;color:var(--ui-text-muted);font-weight:600;font-size:14px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(255,255,255,0.3)';this.style.color='var(--ui-text-main)';" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)';this.style.color='var(--ui-text-muted)';">
          Annuler
        </button>
      </div>
    </div>
  `;
  
  authModal.innerHTML = html;
}

// REMOVED: performRegister() est maintenant dans auth.js et exposé via window.performRegister
// La fonction complète (~335 lignes) a été supprimée

// REMOVED: performLogin() est maintenant dans auth.js et exposé via window.performLogin

// Ancien alias pour compatibilité
async function simulateLogin() {
  if (typeof window.performLogin === 'function') {
    await window.performLogin();
  }
}

// ============================================
// FORMULAIRE D'INSCRIPTION 3 ÉTAPES
// ============================================
// NOTE: registerStep et registerData sont déclarées dans auth.js et exposées via window.registerStep et window.registerData
// Vérifier que les variables globales existent
if (typeof window.registerStep === 'undefined') {
  window.registerStep = 1;
}
if (typeof window.registerData === 'undefined') {
  window.registerData = {
    email: '',
    username: '',
    password: '',
    avatarId: 1,
    avatarDescription: '',
    addresses: [],
    emailVerificationCode: null,
    emailVerified: false,
    verificationAttempts: 0,
    lastVerificationAttempt: null,
    registrationAttempts: 0,
    lastRegistrationAttempt: null
  };
}

// NOTE: openRegisterModal() est déjà définie plus haut (ligne 9881)
// Cette fonction est supprimée pour éviter les conflits
// Utiliser openAuthModal('register') directement

// Formulaire professionnel style Facebook
function showProRegisterForm() {
  console.log('🎯 showProRegisterForm called');
  
  // Exposer globalement pour le fallback
  if (typeof window !== 'undefined') {
    window.showProRegisterForm = showProRegisterForm;
  }
  
  const backdrop = document.getElementById('publish-modal-backdrop');
  const modal = document.getElementById('publish-modal-inner');

  if (!backdrop) {
    console.error('❌ Backdrop not found');
    return;
  }
  
  if (!modal) {
    console.error('❌ Modal inner not found');
    return;
  }
  
  console.log('✅ Modal elements found, displaying form...');
  
  // S'assurer que registerData est initialisé
  if (!window.registerData) {
    window.registerData = {
      email: '',
      username: '',
      password: '',
      passwordConfirm: '',
      firstName: '', // Optionnel - pas utilisé dans le formulaire pro
      lastName: '', // Optionnel - pas utilisé dans le formulaire pro
      profilePhoto: '',
      photoData: '', // Initialiser photoData aussi
      postalAddress: '',
      avatarId: 1
    };
    console.log('[REGISTER] registerData initialisé dans showProRegisterForm');
  } else {
    // S'assurer que photoData existe même si registerData existe déjà
    // CORRECTION: Vérifier aussi si photoData est une chaîne vide
    if ((!window.registerData.photoData || window.registerData.photoData.length === 0) && 
        window.registerData.profilePhoto && window.registerData.profilePhoto.length > 0) {
      window.registerData.photoData = window.registerData.profilePhoto;
      console.log('[REGISTER] ✅ photoData copié depuis profilePhoto dans showProRegisterForm');
    }
  }
  
  // Forcer l'affichage du modal
  backdrop.style.display = 'flex';
  backdrop.style.visibility = 'visible';
  backdrop.style.opacity = '1';
  backdrop.style.zIndex = '9999';
  modal.style.display = 'block';
  modal.style.visibility = 'visible';
  modal.style.opacity = '1';

  const html = `
    <style>
      @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }
      @keyframes slideUp {
        from { opacity: 0; transform: translateY(-5px); }
        to { opacity: 1; transform: translateY(0); }
      }
      @keyframes slideDown {
        from { opacity: 1; transform: translateY(0); }
        to { opacity: 0; transform: translateY(-5px); }
      }
      .pro-register-error {
        color: #ef4444;
        font-size: 12px;
        margin-top: 4px;
        display: none;
        animation: slideUp 0.3s ease;
      }
      .pro-register-success {
        color: #22c55e;
        font-size: 12px;
        margin-top: 4px;
        display: none;
        animation: slideUp 0.3s ease;
      }
      .pro-register-input.field-error {
        border-color: #ef4444 !important;
        box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1) !important;
      }
      .pro-register-input.field-success {
        border-color: #22c55e !important;
        box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1) !important;
      }
      .pro-register-password-strength-fill {
        height: 4px;
        border-radius: 2px;
        transition: all 0.3s ease;
      }
      .pro-register-password-strength-fill.weak {
        background-color: #ef4444;
      }
      .pro-register-password-strength-fill.medium {
        background-color: #f59e0b;
      }
      .pro-register-password-strength-fill.strong {
        background-color: #22c55e;
      }
    </style>
    <div class="pro-register-container" style="position:relative;">
      <!-- Bouton X (croix) pour fermer -->
      <button onclick="closeAuthModal()" style="position:absolute;top:16px;right:16px;background:none;border:none;color:var(--ui-text-muted);font-size:24px;cursor:pointer;padding:8px;width:40px;height:40px;display:flex;align-items:center;justify-content:center;border-radius:50%;transition:all 0.2s;z-index:10;" onmouseover="this.style.background='rgba(239,68,68,0.2)';this.style.color='#ef4444';this.style.transform='scale(1.1)';" onmouseout="this.style.background='none';this.style.color='var(--ui-text-muted)';this.style.transform='scale(1)';" title="Fermer">✕</button>
      
      <div class="pro-register-header">
        <div class="pro-register-logo">🌍</div>
        <h1 class="pro-register-title">Créer un compte</h1>
        <p class="pro-register-subtitle">Rejoignez MapEvent et découvrez les événements près de chez vous</p>
      </div>
      
      <!-- Progress Indicator -->
      <div class="registration-progress" style="display:flex;justify-content:space-between;margin-bottom:24px;padding:0 8px;">
        <div class="progress-step" data-step="1" style="flex:1;text-align:center;padding:8px;border-radius:8px;background:rgba(34,197,94,0.2);color:#22c55e;font-weight:600;font-size:12px;transition:all 0.3s;">
          <div style="width:32px;height:32px;border-radius:50%;background:#22c55e;color:#fff;display:flex;align-items:center;justify-content:center;margin:0 auto 4px;font-weight:bold;">1</div>
          Informations
        </div>
        <div class="progress-step" data-step="2" style="flex:1;text-align:center;padding:8px;border-radius:8px;background:rgba(255,255,255,0.05);color:var(--ui-text-muted);font-size:12px;margin:0 8px;transition:all 0.3s;">
          <div style="width:32px;height:32px;border-radius:50%;background:rgba(255,255,255,0.1);color:var(--ui-text-muted);display:flex;align-items:center;justify-content:center;margin:0 auto 4px;font-weight:bold;">2</div>
          Vérification
        </div>
        <div class="progress-step" data-step="3" style="flex:1;text-align:center;padding:8px;border-radius:8px;background:rgba(255,255,255,0.05);color:var(--ui-text-muted);font-size:12px;transition:all 0.3s;">
          <div style="width:32px;height:32px;border-radius:50%;background:rgba(255,255,255,0.1);color:var(--ui-text-muted);display:flex;align-items:center;justify-content:center;margin:0 auto 4px;font-weight:bold;">3</div>
          Confirmation
        </div>
      </div>

      <form class="pro-register-form" onsubmit="handleProRegisterSubmit(event)">
        <!-- HONEYPOT FIELD (Anti-Bot) - Invisible pour les humains -->
        <input 
          type="text" 
          name="website" 
          id="pro-website-honeypot"
          style="position:absolute;left:-9999px;opacity:0;pointer-events:none;tabindex:-1;"
          autocomplete="off"
          aria-hidden="true"
        >
        
        <!-- Email -->
        <div class="pro-register-field">
          <label class="pro-register-label">
            Email <span class="required">*</span>
          </label>
          <input 
            type="email" 
            id="pro-email" 
            class="pro-register-input" 
            placeholder="votre@email.com"
            required
            value="${window.registerData.email || ''}"
            oninput="if(window.registerData) window.registerData.email = this.value; if(typeof window.validateProField === 'function') window.validateProField('email', this.value)"
          >
          <div id="pro-email-error" class="pro-register-error"></div>
          <div id="pro-email-success" class="pro-register-success"></div>
        </div>

        <!-- Nom d'utilisateur -->
        <div class="pro-register-field">
          <label class="pro-register-label">
            Nom d'utilisateur <span class="required">*</span>
          </label>
          <input 
            type="text" 
            id="pro-username" 
            class="pro-register-input" 
            placeholder="Votre pseudo (3-20 caractères)"
            required
            value="${window.registerData.username || ''}"
            oninput="if(window.registerData) window.registerData.username = this.value; if(typeof window.validateProField === 'function') window.validateProField('username', this.value); if(typeof autoSaveRegistrationForm === 'function') autoSaveRegistrationForm();"
          >
          <div id="pro-username-error" class="pro-register-error"></div>
          <div id="pro-username-success" class="pro-register-success"></div>
        </div>

        <!-- Photo de profil -->
        <div class="pro-register-field">
          <label class="pro-register-label">
            Photo de profil <span class="required">*</span>
          </label>
          <div class="pro-register-photo-upload" onclick="event.stopPropagation();event.stopImmediatePropagation();const input = document.getElementById('pro-photo-input'); if(input) input.click(); return false;">
            <img id="pro-photo-preview" class="pro-register-photo-preview" src="${window.registerData.profilePhoto || ''}" alt="Preview">
            <div class="pro-register-photo-placeholder" id="pro-photo-placeholder" style="${window.registerData.profilePhoto ? 'display:none' : 'display:flex'}">
              📷
            </div>
            <div class="pro-register-photo-text">
              ${window.registerData.profilePhoto ? 'Cliquez pour changer la photo' : 'Cliquez pour ajouter une photo'}
            </div>
            <input 
              type="file" 
              id="pro-photo-input" 
              class="pro-register-photo-input" 
              accept="image/*"
              onchange="event.preventDefault();event.stopPropagation();event.stopImmediatePropagation();handleProPhotoUpload(event);return false;"
            >
          </div>
          <div id="pro-photo-error" class="pro-register-error"></div>
        </div>

        <!-- Mot de passe -->
        <div class="pro-register-field">
          <label class="pro-register-label">
            Mot de passe <span class="required">*</span>
          </label>
          <div class="pro-register-password-container">
            <input 
              type="password" 
              id="pro-password" 
              class="pro-register-input" 
              placeholder="Minimum 8 caractères"
              required
            value="${window.registerData.password || ''}"
            oninput="if(window.registerData) window.registerData.password = this.value; if(typeof validateProPassword === 'function') validateProPassword(this.value)"
            >
            <button type="button" class="pro-register-password-toggle" onclick="event.preventDefault();event.stopPropagation();toggleProPasswordVisibility('pro-password', event);return false;">👁️</button>
          </div>
          <div class="pro-register-password-strength">
            <div id="pro-password-strength-fill" class="pro-register-password-strength-fill"></div>
          </div>
          <div id="pro-password-error" class="pro-register-error"></div>
        </div>

        <!-- Confirmation mot de passe -->
        <div class="pro-register-field">
          <label class="pro-register-label">
            Confirmer le mot de passe <span class="required">*</span>
          </label>
          <div class="pro-register-password-container">
            <input 
              type="password" 
              id="pro-password-confirm" 
              class="pro-register-input" 
              placeholder="Répétez le mot de passe"
              required
              value="${window.window.window.registerData.passwordConfirm || ''}"
              oninput="window.window.registerData.passwordConfirm = this.value; validateProPasswordMatch()"
            >
            <button type="button" class="pro-register-password-toggle" onclick="event.preventDefault();event.stopPropagation();toggleProPasswordVisibility('pro-password-confirm', event);return false;">👁️</button>
          </div>
          <div id="pro-password-confirm-error" class="pro-register-error"></div>
          <div id="pro-password-confirm-success" class="pro-register-success"></div>
        </div>

        <!-- Adresse postale pour les alertes (avec autocomplete OpenStreetMap) -->
        <div class="pro-register-field" style="margin-bottom: 20px;">
          <label class="pro-register-label">
            Adresse postale
            <span style="font-weight: normal; color: var(--ui-text-muted); font-size: 12px;">(pour recevoir les alertes)</span>
          </label>
          <div style="position: relative; z-index: 1;">
            <input 
              type="text" 
              id="pro-postal-address" 
              class="pro-register-input" 
              placeholder="Commencez à taper votre adresse..."
              value="${window.window.registerData.postalAddress || ''}"
              autocomplete="off"
              oninput="if(typeof autoSaveRegistrationForm === 'function') autoSaveRegistrationForm();"
            >
            <div id="pro-address-suggestions-wrapper" style="position:absolute;top:100%;left:0;right:0;z-index:10001;margin-top:4px;display:none;">
              <div id="pro-address-suggestions" class="address-suggestions" style="display:none;position:relative;width:100%;background:#050810;background-color:#050810;border:2px solid rgba(255,255,255,0.7);border-radius:8px;max-height:120px;overflow-y:auto;opacity:1;backdrop-filter:none;isolation:isolate;mix-blend-mode:normal;box-shadow:0 8px 40px rgba(0,0,0,1), inset 0 0 0 2px rgba(0,0,0,0.5);"></div>
            </div>
            <input type="hidden" id="pro-address-lat" value="${window.registerData.addressLat || ''}">
            <input type="hidden" id="pro-address-lng" value="${window.registerData.addressLng || ''}">
            <input type="hidden" id="pro-address-country" value="${window.registerData.addressCountry || ''}">
            <input type="hidden" id="pro-address-label" value="${window.registerData.addressLabel || ''}">
          </div>
          <div id="pro-postal-address-error" class="pro-register-error"></div>
          <div id="pro-address-status" style="font-size: 12px; color: var(--ui-text-muted); margin-top: 4px;"></div>
          <label style="display: flex; align-items: center; gap: 8px; margin-top: 8px; cursor: pointer; font-size: 13px; color: var(--ui-text-muted);">
            <input 
              type="checkbox" 
              id="pro-skip-address" 
              onchange="updatePostalAddressRequired()"
              style="cursor: pointer;"
            >
            <span>Pas pour l'instant, je vérifierai mon adresse plus tard</span>
          </label>
        </div>

        <!-- Consentement RGPD -->
        <div class="pro-register-field" style="margin-top: 51px; position: relative; z-index: 10002;">
          <label style="display: flex; align-items: flex-start; gap: 8px; cursor: pointer; font-size: 13px; color: var(--ui-text-main);">
            <input 
              type="checkbox" 
              id="pro-consent-terms" 
              required
              style="cursor: pointer; margin-top: 2px; flex-shrink: 0;"
            >
            <span>
              J'accepte les <a href="#" onclick="event.preventDefault();event.stopPropagation();if(typeof window.showTermsModal==='function'){window.showTermsModal();}else if(typeof showTermsModal==='function'){showTermsModal();}return false;" style="color: #3b82f6; text-decoration: underline; cursor: pointer;">Conditions d'utilisation</a> <span style="color: #ef4444;">*</span>
            </span>
          </label>
        </div>
        
        <div class="pro-register-field" style="margin-top: 8px;">
          <label style="display: flex; align-items: flex-start; gap: 8px; cursor: pointer; font-size: 13px; color: var(--ui-text-main);">
            <input 
              type="checkbox" 
              id="pro-consent-privacy" 
              required
              style="cursor: pointer; margin-top: 2px; flex-shrink: 0;"
            >
            <span>
              J'accepte la <a href="#" onclick="event.preventDefault();event.stopPropagation();if(typeof window.showPrivacyModal==='function'){window.showPrivacyModal();}else if(typeof showPrivacyModal==='function'){showPrivacyModal();}return false;" style="color: #3b82f6; text-decoration: underline; cursor: pointer;">Politique de confidentialité</a> <span style="color: #ef4444;">*</span>
            </span>
          </label>
        </div>

        <!-- Bouton de soumission -->
        <div class="pro-register-actions">
          <button type="submit" class="pro-register-btn-primary" id="pro-submit-btn">
            Créer le compte
          </button>
          <button type="button" id="auth-cancel-btn-pro" class="pro-register-btn-secondary" onclick="console.log('[ANNULER PRO] Click detecte');const e=event||window.event;if(e){e.preventDefault();e.stopPropagation();e.stopImmediatePropagation();}if(typeof window.fermerModalAuth==='function'){window.fermerModalAuth();}else if(typeof closeAuthModal==='function'){closeAuthModal();}else{const b=document.getElementById('publish-modal-backdrop');const m=document.getElementById('publish-modal-inner');if(b){b.style.display='none';b.style.visibility='hidden';b.style.opacity='0';}if(m){m.innerHTML='';m.style.display='none';}}return false;" style="cursor:pointer;pointer-events:auto;z-index:10001;position:relative;">
            Annuler
          </button>
        </div>
      </form>
    </div>
  `;

  // S'assurer que le modal est visible
  modal.innerHTML = html;
  
  // Forcer l'affichage du backdrop avec tous les styles nécessaires
  backdrop.style.display = "flex";
  backdrop.style.visibility = "visible";
  backdrop.style.opacity = "1";
  backdrop.style.zIndex = "99999";
  backdrop.style.position = "fixed";
  backdrop.style.top = "0";
  backdrop.style.left = "0";
  backdrop.style.width = "100%";
  backdrop.style.height = "100%";
  backdrop.style.background = "rgba(0, 0, 0, 0.8)";
  backdrop.style.alignItems = "center";
  backdrop.style.justifyContent = "center";
  
  // Forcer l'affichage du modal inner
  modal.style.display = "block";
  modal.style.visibility = "visible";
  modal.style.opacity = "1";
  
  console.log('✅ Formulaire professionnel affiché');
  console.log('✅ Backdrop display:', backdrop.style.display);
  console.log('✅ Backdrop computed display:', window.getComputedStyle(backdrop).display);
  console.log('✅ Modal inner HTML length:', modal.innerHTML.length);
  console.log('✅ Modal inner first 200 chars:', modal.innerHTML.substring(0, 200));

  // SOLUTION ULTRA-ROBUSTE : Utiliser la même fonction nommée que dans openAuthModal
  // Supprimer l'ancien event listener si il existe déjà (de openAuthModal)
  if (window._authModalCancelHandler) {
    backdrop.removeEventListener('click', window._authModalCancelHandler, true);
  }
  
  // La fonction _authModalCancelHandler est déjà définie dans openAuthModal
  // Si elle n'existe pas encore, la créer
  if (!window._authModalCancelHandler) {
    window._authModalCancelHandler = function(e) {
      const target = e.target;
      
      // DEBUG : Logger tous les clics sur les boutons
      if (target.tagName === 'BUTTON' || target.closest('button')) {
        const btn = target.tagName === 'BUTTON' ? target : target.closest('button');
        console.log('[PRO REGISTER] 🖱️ CLIC DETECTE sur bouton:', {
          id: btn.id,
          text: btn.textContent?.trim(),
          onclick: btn.hasAttribute('onclick'),
          isCancelBtn: btn.id === 'auth-cancel-btn' || btn.id === 'auth-cancel-btn-pro'
        });
      }
      
      const isCancelButton = target.id === 'auth-cancel-btn' || 
                            target.id === 'auth-cancel-btn-pro' ||
                            target.closest('#auth-cancel-btn') ||
                            target.closest('#auth-cancel-btn-pro') ||
                            (target.tagName === 'BUTTON' && target.textContent?.trim() === 'Annuler') ||
                            (target.closest('button') && target.closest('button').textContent?.trim() === 'Annuler');
      
      if (isCancelButton) {
        console.log('[PRO REGISTER] 🔥🔥🔥 BOUTON ANNULER CLIQUE (via event delegation) - FERMETURE IMMEDIATE');
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        e.cancelBubble = true;
        
        const b = document.getElementById('publish-modal-backdrop');
        const m = document.getElementById('publish-modal-inner');
        const a = document.getElementById('authModal');
        const o = document.getElementById('onboardingModal');
        
        if (b) {
          b.style.display = 'none';
          b.style.visibility = 'hidden';
          b.style.opacity = '0';
          b.style.zIndex = '-1';
          b.setAttribute('style', 'display:none!important;visibility:hidden!important;opacity:0!important;z-index:-1!important;');
        }
        if (m) {
          m.innerHTML = '';
          m.style.display = 'none';
          m.setAttribute('style', 'display:none!important;');
        }
        if (a) {
          a.remove();
        }
        if (o) {
          o.remove();
        }
        
        window.pendingRegisterPhoto = null;
        window.registerSelectedAddress = null;
        window.registerPhotoData = null;
        window.registerPhotoFile = null;
        window.isGoogleLoginInProgress = false;
        
        console.log('[PRO REGISTER] ✅ Modal ferme COMPLETEMENT (via event delegation)');
        return false;
      }
      
      // Si on clique directement sur le backdrop (pas sur ses enfants), fermer le modal
      // ⚠️⚠️⚠️ IMPORTANT : Ignorer TOUS les éléments du formulaire d'inscription
      const isClickOnChild = target.closest('button') || 
                            target.closest('input') || 
                            target.closest('a') || 
                            target.closest('.pro-register-container') ||
                            target.closest('#publish-modal-inner') ||
                            target.closest('#authModal') ||
                            target.closest('.pro-register-photo-upload') ||
                            target.closest('#pro-photo-input') ||
                            target.closest('#pro-photo-preview') ||
                            target.closest('.pro-register-photo-placeholder') ||
                            target.closest('.pro-register-field') ||
                            target.closest('.pro-register-input') ||
                            target.closest('.pro-register-password-container') ||
                            target.closest('.pro-register-password-toggle') ||
                            target.closest('form') ||
                            target.id === 'pro-photo-input' ||
                            target.id === 'pro-photo-preview' ||
                            target.classList?.contains('pro-register-photo-upload') ||
                            target.classList?.contains('pro-register-photo-input') ||
                            target.classList?.contains('pro-register-password-toggle') ||
                            target.classList?.contains('pro-register-password-container');
      
      if (target === backdrop && !isClickOnChild) {
        console.log('[PRO REGISTER] Backdrop click detecte - Fermeture via closeAuthModal');
        closeAuthModal();
      } else if (isClickOnChild) {
        console.log('[PRO REGISTER] Clic sur élément du formulaire - IGNORÉ (pas de fermeture)');
      }
    };
  }
  
  // Attacher l'event listener avec useCapture=true pour s'exécuter AVANT tout le monde
  backdrop.addEventListener('click', window._authModalCancelHandler, true);
  console.log('[PRO REGISTER] ✅ Event delegation attachee avec useCapture=true');
  
  // VERIFIER et corriger le bouton Annuler dans showProRegisterForm
  // AUGMENTER le délai pour s'assurer que le HTML est complètement injecté
  console.log('[PRO REGISTER] ⏰ setTimeout PROGRAMMÉ pour 200ms...');
  setTimeout(() => {
    console.log('[PRO REGISTER] 🔍🔍🔍 setTimeout EXÉCUTÉ (200ms), recherche des éléments...');
    const modalInner = document.getElementById('publish-modal-inner');
    console.log('[PRO REGISTER] Modal inner existe:', !!modalInner);
    console.log('[PRO REGISTER] Modal inner HTML length:', modalInner?.innerHTML?.length || 0);
    console.log('[PRO REGISTER] Modal inner contient "pro-photo-input":', modalInner?.innerHTML?.includes('pro-photo-input') || false);
    const cancelBtnPro = document.getElementById('auth-cancel-btn-pro');
    if (cancelBtnPro) {
      console.log('[PRO REGISTER] ✅ Bouton Annuler trouve (auth-cancel-btn-pro)');
      cancelBtnPro.style.pointerEvents = 'auto';
      cancelBtnPro.style.cursor = 'pointer';
      cancelBtnPro.style.zIndex = '10001';
      
      // Ajouter un onclick direct aussi
      cancelBtnPro.onclick = function(e) {
        e = e || window.event;
        if (e) {
          e.preventDefault();
          e.stopPropagation();
          e.stopImmediatePropagation();
        }
        console.log('[PRO REGISTER] 🔥 ONCLICK DIRECT EXECUTE - FERMETURE');
        const b = document.getElementById('publish-modal-backdrop');
        const m = document.getElementById('publish-modal-inner');
        if (b) {
          b.style.display = 'none';
          b.style.visibility = 'hidden';
          b.style.opacity = '0';
        }
        if (m) {
          m.innerHTML = '';
          m.style.display = 'none';
        }
        if (typeof closeAuthModal === 'function') {
          closeAuthModal();
        }
        return false;
      };
      console.log('[PRO REGISTER] ✅ ONCLICK DIRECT attache au bouton Annuler');
    } else {
      console.warn('[PRO REGISTER] ⚠️ Bouton Annuler non trouve');
    }
    
    // CORRECTION: Attacher aussi un event listener programmatique pour l'input photo
    try {
      console.log('[PRO REGISTER] 🔥🔥🔥 AVANT recherche pro-photo-input - Code toujours actif');
      console.log('[PRO REGISTER] 🔍 Recherche de pro-photo-input...');
    console.log('[PRO REGISTER] document.getElementById existe:', typeof document.getElementById);
    const photoInput = document.getElementById('pro-photo-input');
    console.log('[PRO REGISTER] Résultat getElementById:', photoInput);
    if (photoInput) {
      console.log('[PRO REGISTER] ✅✅✅ Input photo TROUVÉ!', photoInput);
      console.log('[PRO REGISTER] Type:', photoInput.type, 'ID:', photoInput.id);
      console.log('[PRO REGISTER] Parent:', photoInput.parentElement?.id || 'pas de parent');
      console.log('[PRO REGISTER] Visible:', photoInput.offsetParent !== null);
      
      // Vérifier si handleProPhotoUpload existe
      console.log('[PRO REGISTER] handleProPhotoUpload existe:', typeof handleProPhotoUpload);
      console.log('[PRO REGISTER] window.handleProPhotoUpload existe:', typeof window.handleProPhotoUpload);
      
      // Supprimer l'ancien listener s'il existe
      photoInput.removeEventListener('change', handleProPhotoUpload);
      
      // Créer une fonction wrapper pour capturer l'événement
      const photoChangeHandler = function(e) {
        console.log('[PRO REGISTER] 🔥🔥🔥🔥🔥 EVENT CHANGE DÉTECTÉ sur pro-photo-input!', e);
        console.log('[PRO REGISTER] Fichiers sélectionnés:', e.target.files ? e.target.files.length : 0);
        e.stopPropagation(); // Empêcher la propagation vers closePublishModal
        
        // Appeler handleProPhotoUpload directement (elle doit être définie globalement)
        if (typeof window.handleProPhotoUpload === 'function') {
          console.log('[PRO REGISTER] ✅ Appel de window.handleProPhotoUpload...');
          window.handleProPhotoUpload(e);
        } else {
          console.error('[PRO REGISTER] ❌❌❌ window.handleProPhotoUpload n\'est PAS une fonction!', typeof window.handleProPhotoUpload);
          // Définir inline si elle n'existe pas encore
          window.handleProPhotoUpload = function(event) {
            console.log('[PHOTO] 🔥🔥🔥 handleProPhotoUpload INLINE APPELÉE!', event);
            const file = event.target.files[0];
            if (!file) return;
            if (file.size > 5 * 1024 * 1024) {
              showError('pro-photo-error', 'La photo est trop grande (max 5MB)');
              return;
            }
            if (!file.type.startsWith('image/')) {
              showError('pro-photo-error', 'Veuillez sélectionner une image');
              return;
            }
            const reader = new FileReader();
            reader.onload = function(e) {
              const base64 = e.target.result;
              if (!window.registerData) window.registerData = {};
              window.registerData.profilePhoto = base64;
              window.registerData.photoData = base64;
              console.log('[PHOTO] ✅✅✅ Photo sauvegardée (INLINE) - photoData:', base64.length, 'chars');
              const preview = document.getElementById('pro-photo-preview');
              const placeholder = document.getElementById('pro-photo-placeholder');
              if (preview) {
                preview.src = base64;
                preview.style.display = 'block';
                preview.classList.add('show');
              }
              if (placeholder) placeholder.style.display = 'none';
              showError('pro-photo-error', '');
            };
            reader.readAsDataURL(file);
          };
          console.log('[PRO REGISTER] ✅ handleProPhotoUpload définie inline, appel...');
          window.handleProPhotoUpload(e);
        }
      };
      
      // Ajouter le nouveau listener avec capture pour s'assurer qu'il est appelé AVANT closePublishModal
      photoInput.addEventListener('change', photoChangeHandler, true); // useCapture=true
      photoInput.addEventListener('input', photoChangeHandler, true); // Aussi sur 'input' au cas où
      console.log('[PRO REGISTER] ✅✅✅✅✅ Event listeners change ET input attachés a pro-photo-input avec useCapture=true');
      
      // Vérifier aussi l'attribut onchange
      if (photoInput.getAttribute('onchange')) {
        console.log('[PRO REGISTER] ✅ Attribut onchange présent:', photoInput.getAttribute('onchange'));
      } else {
        console.warn('[PRO REGISTER] ⚠️ Attribut onchange manquant, ajout programmatique');
        photoInput.setAttribute('onchange', 'handleProPhotoUpload(event)');
      }
      
      // Empêcher le clic sur l'input de déclencher closePublishModal
      photoInput.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        if (e.cancelBubble !== undefined) {
          e.cancelBubble = true;
        }
        console.log('[PRO REGISTER] 🔥 Clic sur input photo, propagation stoppée');
        return false;
      }, true);
    } else {
      console.error('[PRO REGISTER] ❌❌❌ Input photo NON TROUVÉ!');
      console.error('[PRO REGISTER] Tous les éléments avec "photo" dans l\'ID:');
      const allElements = document.querySelectorAll('[id*="photo"]');
      allElements.forEach(el => console.log('[PRO REGISTER]   -', el.id, el.tagName));
      
      // Réessayer plusieurs fois avec des délais croissants
      [300, 500, 1000].forEach((delay, index) => {
        setTimeout(() => {
          console.log(`[PRO REGISTER] 🔄 Retry ${index + 1} après ${delay}ms...`);
          const retryInput = document.getElementById('pro-photo-input');
          if (retryInput) {
            console.log(`[PRO REGISTER] ✅✅✅ Input photo trouvé au retry ${index + 1}!`);
            const photoChangeHandler = function(e) {
              console.log('[PRO REGISTER] 🔥 EVENT CHANGE (retry)', e);
              e.stopPropagation();
              if (typeof handleProPhotoUpload === 'function') {
                handleProPhotoUpload(e);
              } else if (typeof window.handleProPhotoUpload === 'function') {
                window.handleProPhotoUpload(e);
              }
            };
            retryInput.addEventListener('change', photoChangeHandler, true);
            retryInput.addEventListener('click', function(e) {
              e.stopPropagation();
              console.log('[PRO REGISTER] 🔥 Clic sur input photo (retry), propagation stoppée');
            }, true);
            console.log(`[PRO REGISTER] ✅ Event listeners attachés au retry ${index + 1}`);
          } else {
            console.warn(`[PRO REGISTER] ⚠️ Input photo toujours non trouvé au retry ${index + 1}`);
          }
        }, delay);
      });
    }
    } catch (error) {
      console.error('[PRO REGISTER] ❌❌❌ ERREUR lors de l\'attachement de l\'event listener photo:', error);
      console.error('[PRO REGISTER] Stack trace:', error.stack);
    }
  }, 200); // Augmenté à 200ms pour laisser plus de temps au DOM

  // ⚠️⚠️⚠️ NOUVEAU : Attacher un event listener sur la zone de photo pour ouvrir le sélecteur
  setTimeout(() => {
    const photoUploadArea = document.querySelector('.pro-register-photo-upload');
    const photoInput = document.getElementById('pro-photo-input');
    
    if (photoUploadArea && photoInput) {
      // Supprimer l'ancien listener s'il existe
      photoUploadArea.removeEventListener('click', window._photoUploadClickHandler);
      
      // Créer un nouveau handler qui ouvre le sélecteur sans fermer le formulaire
      window._photoUploadClickHandler = function(e) {
        console.log('[PHOTO] Clic sur zone de photo détecté');
        e.stopPropagation();
        e.stopImmediatePropagation();
        if (e.cancelBubble !== undefined) {
          e.cancelBubble = true;
        }
        
        // Ouvrir le sélecteur de fichiers
        if (photoInput) {
          photoInput.click();
        }
        
        return false;
      };
      
      // Attacher le listener avec useCapture pour intercepter avant les autres
      photoUploadArea.addEventListener('click', window._photoUploadClickHandler, true);
      console.log('[PHOTO] ✅ Event listener attaché sur zone de photo');
    }
  }, 300);
  
  // Initialiser l'autocomplete d'adresse pour le formulaire pro
  setTimeout(() => {
    const addressInput = document.getElementById('pro-postal-address');
    if (addressInput) {
      setupProAddressAutocomplete(addressInput);
    } else {
      console.warn('[PRO REGISTER] ⚠️ Champ pro-postal-address non trouvé');
    }
  }, 100);

  // Restaurer le formulaire depuis localStorage si un draft existe
  setTimeout(() => {
    if (typeof restoreRegistrationForm === 'function') {
      const restored = restoreRegistrationForm();
      if (restored) {
        console.log('[PRO REGISTER] ✅ Formulaire restauré depuis localStorage');
      }
    }
  }, 200);
  
  // Focus sur le premier champ (email au lieu de firstname car firstname n'existe peut-être pas)
  // Utiliser requestAnimationFrame pour s'assurer que le DOM est prêt
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      // Chercher dans l'ordre : email, username, password
      const firstInput = document.getElementById("pro-email") || 
                        document.getElementById("pro-username") || 
                        document.getElementById("pro-password");
      if (firstInput) {
        firstInput.focus();
        console.log('✅ Focus sur le premier champ:', firstInput.id);
      } else {
        console.warn('⚠️ Premier champ non trouvé (pro-email, pro-username, pro-password)');
        // Lister tous les inputs pour debug
        const modalInner = document.getElementById('publish-modal-inner');
        if (modalInner) {
          const allInputs = document.querySelectorAll('#publish-modal-inner input:not([type="hidden"]):not([id*="honeypot"])');
          console.log('[PRO REGISTER] Tous les inputs trouvés:', Array.from(allInputs).map(i => ({id: i.id, type: i.type, visible: i.offsetParent !== null})));
          // Essayer de focuser le premier input trouvé
          if (allInputs.length > 0) {
            const firstFound = allInputs[0];
            firstFound.focus();
            console.log('✅ Focus sur le premier input trouvé:', firstFound.id);
          }
        }
      }
    });
  });
  
  // CORRECTION: Attacher l'event listener pour l'input photo IMMÉDIATEMENT après l'injection HTML
  // Ne pas attendre le setTimeout, mais utiliser requestAnimationFrame pour s'assurer que le DOM est prêt
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      console.log('[PRO REGISTER] 🔍🔍🔍 Recherche IMMÉDIATE de pro-photo-input (via requestAnimationFrame)');
      const photoInput = document.getElementById('pro-photo-input');
      if (photoInput) {
        console.log('[PRO REGISTER] ✅✅✅ Input photo TROUVÉ IMMÉDIATEMENT!');
        const photoChangeHandler = function(e) {
          console.log('[PRO REGISTER] 🔥🔥🔥 EVENT CHANGE DÉTECTÉ sur pro-photo-input!');
          e.stopPropagation();
          if (typeof handleProPhotoUpload === 'function') {
            handleProPhotoUpload(e);
          } else if (typeof window.handleProPhotoUpload === 'function') {
            window.handleProPhotoUpload(e);
          }
        };
        photoInput.addEventListener('change', photoChangeHandler, true);
        photoInput.addEventListener('click', function(e) {
          e.stopPropagation();
          console.log('[PRO REGISTER] 🔥 Clic sur input photo, propagation stoppée');
        }, true);
        console.log('[PRO REGISTER] ✅✅✅ Event listeners attachés IMMÉDIATEMENT');
      } else {
        console.warn('[PRO REGISTER] ⚠️ Input photo non trouvé immédiatement, retry dans setTimeout');
      }
    });
  });
}

// Fonction d'autocomplete d'adresse pour le formulaire pro (Nominatim)
function setupProAddressAutocomplete(input) {
  if (!input) {
    console.error('[PRO ADDRESS] ❌ Input non fourni à setupProAddressAutocomplete');
    return;
  }
  
  console.log('[PRO ADDRESS] ✅ Initialisation autocomplete pour:', input.id);
  
  let searchTimeout = null;
  const suggestionsWrapper = document.getElementById('pro-address-suggestions-wrapper');
  const suggestionsDiv = document.getElementById('pro-address-suggestions');
  
  if (!suggestionsDiv || !suggestionsWrapper) {
    console.error('[PRO ADDRESS] ❌ Div suggestions ou wrapper non trouvé');
    return;
  }
  
  // Gérer la saisie
  input.addEventListener('input', function(e) {
    const query = e.target.value.trim();
    
    // Effacer le timeout précédent
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }
    
    // Masquer les suggestions si vide
    if (!query || query.length < 3) {
      suggestionsWrapper.style.display = 'none';
      suggestionsDiv.style.display = 'none';
      // Supprimer l'overlay
      const overlay = document.getElementById('pro-address-suggestions-overlay');
      if (overlay) overlay.remove();
      // Réinitialiser les champs cachés
      const latInput = document.getElementById('pro-address-lat');
      const lngInput = document.getElementById('pro-address-lng');
      const countryInput = document.getElementById('pro-address-country');
      const labelInput = document.getElementById('pro-address-label');
      if (latInput) latInput.setAttribute('value', '');
      if (lngInput) lngInput.setAttribute('value', '');
      if (countryInput) countryInput.setAttribute('value', '');
      if (labelInput) labelInput.setAttribute('value', '');
      return;
    }
    
    // Rechercher après 500ms de pause
    searchTimeout = setTimeout(() => {
      searchAddressNominatim(query);
    }, 500);
  });
  
  // Fonction de recherche Nominatim
  async function searchAddressNominatim(query) {
    try {
      console.log('[PRO ADDRESS] 🔍 Recherche Nominatim pour:', query);
      
      // ⚠️⚠️⚠️ CRITIQUE : Recherche MONDIALE - pas de restriction de pays
      // Nominatim supporte toutes les adresses du monde (Afrique, Asie, Amériques, Océanie, etc.)
      // Détection automatique de la langue depuis le navigateur pour traduction Google
      const userLanguage = navigator.language || navigator.userLanguage || 'fr';
      const langCode = userLanguage.split('-')[0]; // 'fr', 'en', 'ar', 'sw', 'zh', etc.
      
      console.log('[PRO ADDRESS] 🌍 Langue détectée:', langCode, '- Recherche MONDIALE activée');
      
      // ⚠️⚠️⚠️ RECHERCHE MONDIALE - Pas de restriction de pays
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=10&addressdetails=1&accept-language=${langCode},en`,
        {
          headers: {
            'Accept-Language': `${langCode},en,fr`,
            'User-Agent': 'MapEvent/1.0'
          }
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const results = await response.json();
      console.log('[PRO ADDRESS] ✅ Résultats Nominatim:', results.length, 'résultats');
      
      if (results.length === 0) {
        // Afficher le wrapper et les suggestions avec fond opaque (hauteur de ~2 adresses)
        suggestionsWrapper.style.display = 'block';
        // ⚠️⚠️⚠️ Message clair : adresse non trouvée (peut être une adresse très reculée)
        const langCode = (navigator.language || navigator.userLanguage || 'fr').split('-')[0];
        const messages = {
          'fr': 'Aucune adresse trouvée. Essayez avec un nom de ville ou un point de repère proche.',
          'en': 'No address found. Try with a city name or nearby landmark.',
          'ar': 'لم يتم العثور على عنوان. جرب اسم المدينة أو معلم قريب.',
          'sw': 'Hakuna anwani iliyopatikana. Jaribu jina la jiji au alama ya karibu.',
          'es': 'No se encontró ninguna dirección. Pruebe con un nombre de ciudad o un punto de referencia cercano.',
          'pt': 'Nenhum endereço encontrado. Tente com um nome de cidade ou um ponto de referência próximo.',
          'zh': '未找到地址。请尝试使用城市名称或附近的地标。'
        };
        const message = messages[langCode] || messages['en'];
        suggestionsDiv.innerHTML = `<div class="address-suggestion" style="padding:12px;color:#a0a0a0;background:#050810;background-color:#050810;opacity:1;mix-blend-mode:normal;">${message}</div>`;
        suggestionsDiv.style.cssText = 'display:block;position:relative;width:100%;background:#050810;background-color:#050810;border:2px solid rgba(255,255,255,0.7);border-radius:8px;max-height:120px;overflow-y:auto;opacity:1;backdrop-filter:none;isolation:isolate;mix-blend-mode:normal;box-shadow:0 8px 40px rgba(0,0,0,1), inset 0 0 0 2px rgba(0,0,0,0.5);';
        return;
      }
      
      // Afficher le wrapper avec fond opaque
      suggestionsWrapper.style.display = 'block';
      
      // Afficher les suggestions avec fond opaque
      suggestionsDiv.innerHTML = results.map((result, index) => {
        const displayName = result.display_name || '';
        const lat = parseFloat(result.lat);
        const lng = parseFloat(result.lon);
        const country = result.address?.country_code?.toUpperCase() || ''; // Pas de pays par défaut - mondial
        const city = result.address?.city || result.address?.town || result.address?.village || '';
        const postcode = result.address?.postcode || '';
        const street = result.address?.road || result.address?.street || '';
        
        return `
          <div class="address-suggestion" data-index="${index}" style="padding:12px;cursor:pointer;border-bottom:1px solid rgba(255,255,255,0.2);transition:background 0.2s;background:#050810;background-color:#050810;opacity:1;backdrop-filter:none;isolation:isolate;mix-blend-mode:normal;" 
               onmouseover="this.style.background='rgba(0,255,195,0.3)';this.style.backgroundColor='rgba(0,255,195,0.3)';" 
               onmouseout="this.style.background='#050810';this.style.backgroundColor='#050810';"
               onclick="selectProAddress(${index}, '${displayName.replace(/'/g, "\\'")}', ${lat}, ${lng}, '${country}', '${city}', '${postcode}', '${street.replace(/'/g, "\\'")}')">
            <div style="font-weight:600;color:#ffffff;margin-bottom:4px;background:transparent;background-color:transparent;">${displayName}</div>
            <div style="font-size:12px;color:#a0a0a0;background:transparent;background-color:transparent;">${city}${postcode ? ' ' + postcode : ''}${country ? ', ' + country : ''}</div>
          </div>
        `;
      }).join('');
      
      // Forcer le style du conteneur avec fond opaque COMPLET (hauteur de ~2 adresses avec scroll)
      suggestionsDiv.style.cssText = 'display:block;position:relative;width:100%;background:#050810;background-color:#050810;border:2px solid rgba(255,255,255,0.7);border-radius:8px;max-height:120px;overflow-y:auto;opacity:1;backdrop-filter:none;isolation:isolate;mix-blend-mode:normal;box-shadow:0 8px 40px rgba(0,0,0,1), inset 0 0 0 2px rgba(0,0,0,0.5);';
      
    } catch (error) {
      console.error('[PRO ADDRESS] ❌ Erreur Nominatim:', error);
      suggestionsWrapper.style.display = 'block';
      suggestionsDiv.innerHTML = '<div class="address-suggestion" style="padding:12px;color:#ef4444;background:#050810;background-color:#050810;opacity:1;mix-blend-mode:normal;">Erreur de recherche. Veuillez réessayer.</div>';
      suggestionsDiv.style.cssText = 'display:block;position:relative;width:100%;background:#050810;background-color:#050810;border:2px solid rgba(255,255,255,0.7);border-radius:8px;max-height:120px;overflow-y:auto;opacity:1;backdrop-filter:none;isolation:isolate;mix-blend-mode:normal;box-shadow:0 8px 40px rgba(0,0,0,1), inset 0 0 0 2px rgba(0,0,0,0.5);';
    }
  }
  
  // Fonction de sélection d'adresse
  window.selectProAddress = function(index, label, lat, lng, country, city, postcode, street) {
    console.log('[PRO ADDRESS] ✅ Adresse sélectionnée:', { label, lat, lng, country });
    
    // Masquer les suggestions
    const suggestionsWrapper = document.getElementById('pro-address-suggestions-wrapper');
    const suggestionsDiv = document.getElementById('pro-address-suggestions');
    if (suggestionsWrapper) suggestionsWrapper.style.display = 'none';
    if (suggestionsDiv) suggestionsDiv.style.display = 'none';
    
    // Supprimer l'overlay s'il existe
    const overlay = document.getElementById('pro-address-suggestions-overlay');
    if (overlay) overlay.remove();
    
    // Mettre à jour le champ input
    const addressInput = document.getElementById('pro-postal-address');
    if (addressInput) addressInput.value = label;
    
    // Mettre à jour les champs cachés
    const latInput = document.getElementById('pro-address-lat');
    const lngInput = document.getElementById('pro-address-lng');
    const countryInput = document.getElementById('pro-address-country');
    const labelInput = document.getElementById('pro-address-label');
    
    if (latInput) latInput.setAttribute('value', lat);
    if (lngInput) lngInput.setAttribute('value', lng);
    if (countryInput) countryInput.setAttribute('value', country);
    if (labelInput) labelInput.setAttribute('value', label);
    
    // Sauvegarder dans registerData
    if (!window.registerData) {
      window.registerData = {};
    }
    window.registerData.postalAddress = label;
    window.registerData.addressLat = lat;
    window.registerData.addressLng = lng;
    window.registerData.addressCountry = country;
    window.registerData.addressCity = city;
    window.registerData.addressPostcode = postcode;
    window.registerData.addressStreet = street;
    
    // Masquer les suggestions
    suggestionsDiv.style.display = 'none';
    
    // Valider le champ
    if (typeof window.validateProField === 'function') {
      window.validateProField('postalAddress', label);
    }
    
    console.log('[PRO ADDRESS] ✅ Adresse sauvegardée dans registerData');
  };
  
  // Masquer les suggestions si on clique ailleurs
  document.addEventListener('click', function(e) {
    const suggestionsWrapper = document.getElementById('pro-address-suggestions-wrapper');
    if (suggestionsWrapper && !input.contains(e.target) && !suggestionsWrapper.contains(e.target)) {
      suggestionsWrapper.style.display = 'none';
      suggestionsDiv.style.display = 'none';
      // Supprimer l'overlay s'il existe
      const overlay = document.getElementById('pro-address-suggestions-overlay');
      if (overlay) overlay.remove();
    }
  });
}

// Exposer globalement
window.setupProAddressAutocomplete = setupProAddressAutocomplete;

// Gestion de l'upload de photo de profil
function handleProPhotoUpload(event) {
  // ⚠️⚠️⚠️ CRITIQUE : Empêcher TOUTE propagation pour éviter la fermeture du formulaire
  if (event) {
    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation();
    if (event.cancelBubble !== undefined) {
      event.cancelBubble = true;
    }
  }
  console.log('[PHOTO] 🔥🔥🔥 handleProPhotoUpload APPELÉE!', event);
  const file = event.target.files[0];
  if (!file) {
    console.log('[PHOTO] Aucun fichier sélectionné');
    return;
  }

  console.log('[PHOTO] 📁 Fichier détecté:', { name: file.name, size: file.size, type: file.type });

  // Vérifier la taille (max 5MB)
  if (file.size > 5 * 1024 * 1024) {
    showError('pro-photo-error', 'La photo est trop grande (max 5MB)');
    console.error('[PHOTO] Fichier trop grand:', file.size);
    return;
  }

  // Vérifier le type
  if (!file.type.startsWith('image/')) {
    showError('pro-photo-error', 'Veuillez sélectionner une image');
    console.error('[PHOTO] Type de fichier invalide:', file.type);
    return;
  }

  console.log('[PHOTO] ✅ Fichier valide, début conversion en base64...');

  // Lire et convertir en Base64
  const reader = new FileReader();
  reader.onload = function(e) {
    const base64 = e.target.result;
    console.log('[PHOTO] ✅ Photo convertie en base64, longueur:', base64.length);
    
    // S'assurer que registerData existe
    if (!window.registerData) {
      window.registerData = {};
      console.log('[PHOTO] ⚠️ registerData créé car n\'existait pas');
    }
    
    // Sauvegarder dans registerData.profilePhoto ET registerData.photoData
    window.registerData.profilePhoto = base64;
    window.registerData.photoData = base64; // AUSSI dans photoData pour compatibilité
    
    console.log('[PHOTO] ✅✅✅ Photo sauvegardée dans registerData.profilePhoto ET registerData.photoData');
    console.log('[PHOTO] registerData.profilePhoto existe:', !!window.registerData.profilePhoto);
    console.log('[PHOTO] registerData.photoData existe:', !!window.registerData.photoData);
    console.log('[PHOTO] registerData.photoData longueur:', window.registerData.photoData ? window.registerData.photoData.length : 0);
    console.log('[PHOTO] registerData.photoData début:', window.registerData.photoData ? (window.registerData.photoData.substring(0, 50) + '...') : 'null');
    
    // Afficher la preview
    const preview = document.getElementById('pro-photo-preview');
    const placeholder = document.getElementById('pro-photo-placeholder');
    const photoText = document.querySelector('.pro-register-photo-text');
    
    if (preview) {
      preview.src = base64;
      preview.style.display = 'block';
      preview.classList.add('show');
      console.log('[PHOTO] ✅ Preview mise à jour avec base64');
    } else {
      console.warn('[PHOTO] ⚠️ Preview non trouvée');
    }
    if (placeholder) {
      placeholder.style.display = 'none';
    }
    if (photoText) {
      photoText.textContent = 'Cliquez pour changer la photo';
    }
    
    // Cacher l'erreur
    showError('pro-photo-error', '');
    
    // Vérification finale
    setTimeout(() => {
      console.log('[PHOTO] 🔍 VÉRIFICATION FINALE après 100ms:');
      console.log('[PHOTO] registerData existe:', !!window.registerData);
      console.log('[PHOTO] registerData.photoData:', window.registerData?.photoData ? 'PRÉSENT (' + window.registerData.photoData.length + ' chars)' : 'NULL');
      console.log('[PHOTO] registerData.profilePhoto:', window.registerData?.profilePhoto ? 'PRÉSENT (' + window.registerData.profilePhoto.length + ' chars)' : 'NULL');
    }, 100);
  };
  
  reader.onerror = function(error) {
    console.error('[PHOTO] ❌ Erreur lors de la lecture du fichier:', error);
    showError('pro-photo-error', 'Erreur lors de la lecture de la photo');
  };
  
  reader.readAsDataURL(file);
  console.log('[PHOTO] 📖 FileReader.readAsDataURL() appelé');
}

// Exposer globalement
// Exposer handleProPhotoUpload globalement AVANT qu'elle soit utilisée
window.handleProPhotoUpload = handleProPhotoUpload;
console.log('[PHOTO] ✅ handleProPhotoUpload exposée globalement');

// Fonctions globales pour éviter les erreurs "is not defined" (PRIORITÉ 0)
window.handleAddressInput = function(event) {
  // Cette fonction est gérée par setupProAddressAutocomplete
  // Mais on la définit globalement pour éviter les erreurs si appelée inline
  const input = event.target;
  if (input && input.id === 'pro-postal-address') {
    // L'autocomplete est géré par setupProAddressAutocomplete
    return;
  }
};

window.handleAddressFocus = function(event) {
  // Fonction vide pour éviter les erreurs - l'autocomplete gère le focus
};

window.handleAddressBlur = function(event) {
  // Fonction vide pour éviter les erreurs - l'autocomplete gère le blur
};

// ⚠️⚠️⚠️ FONCTION DUPLIQUÉE SUPPRIMÉE - La fonction setupProAddressAutocomplete est déjà définie ligne 12439
// Cette fonction clonait l'input et cassait l'autocomplete, elle a été supprimée
// Utiliser la fonction définie ligne 12439 à la place
function setupProAddressAutocomplete_DUPLICATE_REMOVED(inputElement) {
  // Cette fonction a été supprimée car elle clonait l'input et cassait l'autocomplete
  // Utiliser la fonction définie ligne 12439 à la place
  console.warn('[PRO ADDRESS] ⚠️ Fonction dupliquée appelée - redirection vers la fonction principale');
  const mainFunction = window.setupProAddressAutocomplete;
  if (mainFunction && typeof mainFunction === 'function') {
    return mainFunction(inputElement);
  }
  return;
  
  /* CODE SUPPRIMÉ - Utiliser la fonction ligne 12439
  let timeout;
  const suggestionsContainer = document.getElementById('pro-address-suggestions');
  
  if (!inputElement || !suggestionsContainer) {
    console.warn('[PRO ADDRESS] Input ou container non trouvé');
    return;
  }
  
  // Supprimer les anciens listeners pour éviter les doublons
  const newInput = inputElement.cloneNode(true);
  inputElement.parentNode.replaceChild(newInput, inputElement);
  
  newInput.addEventListener('input', function(e) {
    const query = e.target.value.trim();
    
    clearTimeout(timeout);
    
    if (query.length < 3) {
      if (suggestionsContainer) {
        suggestionsContainer.style.display = 'none';
      }
      return;
    }
    
    timeout = setTimeout(async () => {
      try {
        // ⚠️⚠️⚠️ RECHERCHE MONDIALE - Pas de restriction de pays, support multilingue
        const langCode = (navigator.language || 'fr').split('-')[0];
        const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=10&addressdetails=1&accept-language=${langCode},en&dedupe=1`, {
          headers: {
            'User-Agent': 'MapEventAI/1.0',
            'Accept-Language': `${langCode},en,fr`
          }
        });
        
        if (!response.ok) {
          console.warn('[PRO ADDRESS] Nominatim erreur HTTP:', response.status);
          if (suggestionsContainer) {
            suggestionsContainer.style.display = 'none';
          }
          return;
        }
        
        const text = await response.text();
        let results;
        try {
          results = JSON.parse(text);
        } catch (parseError) {
          console.error('[PRO ADDRESS] Erreur parsing JSON:', parseError);
          if (suggestionsContainer) {
            suggestionsContainer.style.display = 'none';
          }
          return;
        }
        
        if (suggestionsContainer && results.length > 0) {
          const sortedResults = results.sort((a, b) => {
            const aHasFullAddress = a.address?.road && (a.address?.house_number || a.address?.house);
            const bHasFullAddress = b.address?.road && (b.address?.house_number || b.address?.house);
            if (aHasFullAddress && !bHasFullAddress) return -1;
            if (!aHasFullAddress && bHasFullAddress) return 1;
            return 0;
          });
          
          suggestionsContainer.innerHTML = sortedResults.map(result => {
            const hasFullAddress = result.address?.road && (result.address?.house_number || result.address?.house);
            const addressQuality = hasFullAddress ? '✅' : '📍';
            return `
            <div class="pro-address-suggestion" style="padding:12px;cursor:pointer;border-bottom:1px solid rgba(255,255,255,0.1);transition:background 0.2s;" 
                 onmouseover="this.style.background='rgba(0,255,195,0.1)'" 
                 onmouseout="this.style.background='transparent'"
                 data-lat="${result.lat}" 
                 data-lng="${result.lon}"
                 data-label="${result.display_name}"
                 data-country="${result.address?.country_code?.toUpperCase() || ''}"
                 data-city="${result.address?.city || result.address?.town || result.address?.village || ''}"
                 data-postcode="${result.address?.postcode || ''}"
                 data-street="${result.address?.road || ''}">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
                <span style="font-size:14px;">${addressQuality}</span>
                <div style="font-weight:600;color:var(--ui-text-main);font-size:13px;flex:1;">${result.display_name}</div>
              </div>
              <div style="font-size:11px;color:var(--ui-text-muted);padding-left:22px;">${result.address?.country || ''}${result.address?.postcode ? ' • ' + result.address.postcode : ''}</div>
            </div>
          `;
          }).join('');
          
          suggestionsContainer.style.display = 'block';
          
          suggestionsContainer.querySelectorAll('.pro-address-suggestion').forEach(suggestion => {
            suggestion.addEventListener('click', function() {
              const addressData = {
                lat: parseFloat(this.dataset.lat),
                lng: parseFloat(this.dataset.lng),
                label: this.dataset.label,
                country_code: this.dataset.country,
                city: this.dataset.city,
                postcode: this.dataset.postcode,
                street: this.dataset.street
              };
              
              newInput.value = addressData.label;
              document.getElementById('pro-address-lat').value = addressData.lat;
              document.getElementById('pro-address-lng').value = addressData.lng;
              document.getElementById('pro-address-country').value = addressData.country_code;
              document.getElementById('pro-address-label').value = addressData.label;
              
              if (suggestionsContainer) {
                suggestionsContainer.style.display = 'none';
              }
            });
          });
        } else if (suggestionsContainer) {
          suggestionsContainer.style.display = 'none';
        }
      } catch (error) {
        console.error('[PRO ADDRESS] Erreur autocomplete:', error);
      }
    }, 300);
  });
  
  // CODE SUPPRIMÉ - Cette fonction dupliquée cassait l'autocomplete en clonant l'input
}

// Gestion de l'upload de photo
// DÉPLACÉ: Cette fonction est déjà définie plus haut (ligne ~12164)
// La définition ci-dessus était un doublon qui écrasait la première version
// et ne sauvegardait pas photoData. Supprimée pour éviter les conflits.

// Validation des champs
async function validateProField(fieldName, value) {
  const errorEl = document.getElementById(`pro-${fieldName}-error`);
  const successEl = document.getElementById(`pro-${fieldName}-success`);
  const inputEl = document.getElementById(`pro-${fieldName}`);
  
  if (!errorEl || !inputEl) return true;

  // Réinitialiser les états visuels
  inputEl.classList.remove('field-error', 'field-success');
  inputEl.style.borderColor = '';
  inputEl.style.boxShadow = '';
  showError(`pro-${fieldName}-error`, '');
  showSuccess(`pro-${fieldName}-success`, '');

  let isValid = true;
  let errorMsg = '';
  let successMsg = '';

  switch(fieldName) {
    case 'firstname':
    case 'lastname':
      if (!value || value.trim().length < 2) {
        isValid = false;
        errorMsg = '⚠️ Minimum 2 caractères requis';
      } else if (value.length > 50) {
        isValid = false;
        errorMsg = '⚠️ Maximum 50 caractères';
      } else if (!/^[a-zA-ZàáâäãåèéêëìíîïòóôöõùúûüýÿñçÀÁÂÄÃÅÈÉÊËÌÍÎÏÒÓÔÖÕÙÚÛÜÝŸÑÇ\s-]+$/.test(value)) {
        isValid = false;
        errorMsg = '⚠️ Seules les lettres sont autorisées';
      } else {
        successMsg = '✓ Format valide';
      }
      break;
    
    case 'email':
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!value) {
        isValid = false;
        errorMsg = '⚠️ Email requis';
      } else if (!emailRegex.test(value)) {
        isValid = false;
        errorMsg = '⚠️ Format email invalide (ex: nom@exemple.com)';
      } else {
        // Vérifier la disponibilité avec debounce
        clearTimeout(validationTimers[fieldName]);
        validationTimers[fieldName] = setTimeout(async () => {
          showLoading(`pro-${fieldName}-success`, 'Vérification disponibilité...');
          
          try {
            const response = await fetch(`${window.API_BASE_URL}/user/exists?email=${encodeURIComponent(value)}`);
            
            // Gérer les erreurs 502/503 du backend
            if (!response.ok) {
              if (response.status === 502 || response.status === 503) {
                console.warn('Backend temporairement indisponible pour vérification email');
                showSuccess(`pro-${fieldName}-success`, '✓ Format valide (vérification indisponible)');
                return; // Ne pas bloquer l'utilisateur
              }
              throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.exists) {
              showError(`pro-${fieldName}-error`, '⚠️ Cet email est déjà utilisé');
              showSuccess(`pro-${fieldName}-success`, '');
              inputEl.classList.add('field-error');
            } else {
              showError(`pro-${fieldName}-error`, '');
              showSuccess(`pro-${fieldName}-success`, '✓ Email disponible');
              inputEl.classList.add('field-success');
            }
          } catch (error) {
            console.error('Erreur vérification email:', error);
            // En cas d'erreur, ne pas bloquer - juste afficher format valide
            showSuccess(`pro-${fieldName}-success`, '✓ Format valide');
          }
        }, 500);
        
        successMsg = '✓ Format valide';
      }
      break;
    
    case 'username':
      if (!value) {
        isValid = false;
        errorMsg = '⚠️ Nom d\'utilisateur requis';
      } else if (value.length < 3) {
        isValid = false;
        errorMsg = '⚠️ Minimum 3 caractères';
      } else if (value.length > 20) {
        isValid = false;
        errorMsg = '⚠️ Maximum 20 caractères';
      } else if (!/^[a-zA-Z0-9_-]+$/.test(value)) {
        isValid = false;
        errorMsg = '⚠️ Caractères autorisés: lettres, chiffres, _ et -';
      } else {
        // Vérifier la disponibilité avec debounce
        clearTimeout(validationTimers[fieldName]);
        validationTimers[fieldName] = setTimeout(async () => {
          showLoading(`pro-${fieldName}-success`, 'Vérification disponibilité...');
          
          try {
            const response = await fetch(`${window.API_BASE_URL}/user/exists?username=${encodeURIComponent(value)}`);
            
            // Gérer les erreurs 502/503 du backend
            if (!response.ok) {
              if (response.status === 502 || response.status === 503) {
                console.warn('Backend temporairement indisponible pour vérification username');
                showSuccess(`pro-${fieldName}-success`, '✓ Format valide (vérification indisponible)');
                return; // Ne pas bloquer l'utilisateur
              }
              throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.exists) {
              showError(`pro-${fieldName}-error`, '⚠️ Ce nom d\'utilisateur est déjà pris');
              showSuccess(`pro-${fieldName}-success`, '');
              inputEl.classList.add('field-error');
            } else {
              showError(`pro-${fieldName}-error`, '');
              showSuccess(`pro-${fieldName}-success`, '✓ Disponible');
              inputEl.classList.add('field-success');
            }
          } catch (error) {
            console.error('Erreur vérification username:', error);
            // En cas d'erreur, ne pas bloquer - juste afficher format valide
            showSuccess(`pro-${fieldName}-success`, '✓ Format valide');
          }
        }, 500);
        
        successMsg = '✓ Format valide';
      }
      break;
    
    case 'postalAddress':
      const skipAddress = document.getElementById('pro-skip-address')?.checked;
      if (!skipAddress && (!value || value.trim().length < 5)) {
        isValid = false;
        errorMsg = '⚠️ Adresse complète requise (minimum 5 caractères)';
      } else if (!skipAddress && value && value.trim().length < 5) {
        isValid = false;
        errorMsg = '⚠️ Adresse trop courte (minimum 5 caractères)';
      } else if (!skipAddress && value) {
        successMsg = '✓ Adresse valide';
      }
      break;
  }

  if (errorMsg) {
    showError(`pro-${fieldName}-error`, errorMsg);
  } else if (successMsg && !validationTimers[fieldName]) {
    showSuccess(`pro-${fieldName}-success`, successMsg);
  }
  
  return isValid;
}

// Fonction pour vérifier si un mot de passe a été compromis via Have I Been Pwned
// NOTE: L'API HIBP ne supporte pas CORS depuis le navigateur, donc on désactive temporairement
// La vérification devrait être faite côté backend pour être efficace
// ⚠️⚠️⚠️ DÉFINIE DIRECTEMENT SUR window POUR ÉVITER LES PROBLÈMES DE SCOPE
window.checkPasswordPwned = async function checkPasswordPwned(password) {
  // DÉSACTIVÉ : CORS bloque les requêtes depuis le navigateur
  // TODO: Implémenter la vérification côté backend
  console.log('[HIBP] Vérification désactivée côté frontend (CORS) - à implémenter côté backend');
  return { pwned: false, count: 0 };
  
  /* CODE DÉSACTIVÉ - CORS bloque les requêtes
  try {
    // Créer un hash SHA-1 du mot de passe
    const encoder = new TextEncoder();
    const data = encoder.encode(password);
    const hashBuffer = await crypto.subtle.digest('SHA-1', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('').toUpperCase();
    
    // Utiliser k-anonymity : envoyer seulement les 5 premiers caractères
    const hashPrefix = hashHex.substring(0, 5);
    const hashSuffix = hashHex.substring(5);
    
    // Appeler l'API Have I Been Pwned via un proxy backend (à implémenter)
    // Pour l'instant, désactivé car CORS bloque les requêtes directes
    const response = await fetch(`${window.API_BASE_URL}/check-password-pwned`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ hashPrefix: hashPrefix, hashSuffix: hashSuffix })
    });
    
    if (!response.ok) {
      console.warn('Have I Been Pwned API non disponible');
      return { pwned: false, count: 0 };
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Erreur vérification Have I Been Pwned:', error);
    return { pwned: false, count: 0 };
  }
  */
};

// Validation du mot de passe avec feedback visuel amélioré et vérification Have I Been Pwned
async function validateProPassword(password) {
  const errorEl = document.getElementById('pro-password-error');
  const strengthEl = document.getElementById('pro-password-strength-fill');
  const inputEl = document.getElementById('pro-password');
  
  if (!password) {
    if (strengthEl) {
      strengthEl.className = 'pro-register-password-strength-fill';
      strengthEl.style.width = '0%';
      strengthEl.style.transition = 'all 0.3s ease';
    }
    if (inputEl) {
      inputEl.classList.remove('field-error', 'field-success');
      inputEl.style.borderColor = '';
      inputEl.style.boxShadow = '';
    }
    showError('pro-password-error', '');
    
    // Réinitialiser le label de force
    const strengthLabelEl = document.getElementById('pro-password-strength-label');
    if (strengthLabelEl) {
      strengthLabelEl.textContent = '';
    }
    
    return false;
  }

  let strength = 0;
  let errorMsg = '';
  let strengthPercent = 0;
  let strengthLabel = '';
  let strengthColor = '';

  // Vérifier les critères avec poids
  const hasLength = password.length >= 12; // Minimum 12 caractères pour sécurité renforcée
  const hasLength8 = password.length >= 8;
  const hasUpper = /[A-Z]/.test(password);
  const hasLower = /[a-z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  const hasSpecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);
  const hasLongLength = password.length >= 16;

  // Calcul de la force avec poids
  if (hasLength8) strength += 1;
  if (hasLength) strength += 1;
  if (hasLongLength) strength += 1;
  if (hasUpper) strength += 1;
  if (hasLower) strength += 1;
  if (hasNumber) strength += 1;
  if (hasSpecial) strength += 1;

  // Calcul du pourcentage et du label
  if (strength <= 2) {
    strengthPercent = (strength / 7) * 33;
    strengthLabel = 'Faible';
    strengthColor = '#ef4444';
  } else if (strength <= 4) {
    strengthPercent = 33 + ((strength - 2) / 5) * 33;
    strengthLabel = 'Moyen';
    strengthColor = '#f59e0b';
  } else {
    strengthPercent = 66 + ((strength - 4) / 3) * 34;
    strengthLabel = 'Fort';
    strengthColor = '#22c55e';
  }

  // Mettre à jour la barre de force avec animation
  if (strengthEl) {
    strengthEl.className = `pro-register-password-strength-fill ${strength <= 2 ? 'weak' : strength <= 4 ? 'medium' : 'strong'}`;
    strengthEl.style.width = `${strengthPercent}%`;
    strengthEl.style.backgroundColor = strengthColor;
    strengthEl.style.transition = 'all 0.3s ease';
    
    // Ajouter un label de force si nécessaire
    const strengthLabelEl = document.getElementById('pro-password-strength-label');
    if (!strengthLabelEl && password.length > 0) {
      const label = document.createElement('div');
      label.id = 'pro-password-strength-label';
      label.style.cssText = 'font-size:12px;color:var(--ui-text-muted);margin-top:4px;';
      strengthEl.parentElement.appendChild(label);
    }
    if (strengthLabelEl) {
      strengthLabelEl.textContent = password.length > 0 ? `Force: ${strengthLabel}` : '';
      strengthLabelEl.style.color = strengthColor;
    }
  }

  // Messages d'erreur contextuels
  const missingCriteria = [];
  if (!hasLength8) {
    missingCriteria.push('8 caractères minimum');
  } else if (!hasLength) {
    missingCriteria.push('12 caractères recommandés');
  }
  if (!hasUpper) missingCriteria.push('une majuscule');
  if (!hasLower) missingCriteria.push('une minuscule');
  if (!hasNumber) missingCriteria.push('un chiffre');
  if (!hasSpecial) missingCriteria.push('un caractère spécial');

  if (missingCriteria.length > 0 && password.length > 0) {
    errorMsg = `⚠️ Ajoutez: ${missingCriteria.slice(0, 3).join(', ')}${missingCriteria.length > 3 ? '...' : ''}`;
  } else if (strength >= 5 && password.length >= 12) {
    // Mot de passe fort - vérifier Have I Been Pwned
    // Debounce pour éviter trop d'appels API
    clearTimeout(validationTimers['password-pwned']);
    validationTimers['password-pwned'] = setTimeout(async () => {
      // Utiliser window.checkPasswordPwned directement pour éviter les problèmes de scope
      const checkFn = typeof window.checkPasswordPwned === 'function' ? window.checkPasswordPwned : null;
      if (!checkFn) {
        console.warn('[PASSWORD] checkPasswordPwned non disponible, skip vérification HIBP');
        return;
      }
      try {
        const pwnedCheck = await checkFn(password);
        
        if (pwnedCheck.pwned) {
          const countText = pwnedCheck.count > 0 ? ` (${pwnedCheck.count.toLocaleString()} fois)` : '';
          showError('pro-password-error', `🔒 Ce mot de passe a été compromis dans une fuite de données${countText}. Veuillez en choisir un autre.`);
          if (inputEl) {
            inputEl.classList.add('field-error');
            inputEl.classList.remove('field-success');
            inputEl.style.borderColor = '#ef4444';
            inputEl.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)';
          }
        } else {
          // Mot de passe fort et non compromis
          if (inputEl) {
            inputEl.classList.add('field-success');
            inputEl.classList.remove('field-error');
            inputEl.style.borderColor = '#22c55e';
            inputEl.style.boxShadow = '0 0 0 3px rgba(34, 197, 94, 0.1)';
          }
          showError('pro-password-error', '');
        }
      } catch (error) {
        console.error('[PASSWORD] Erreur vérification HIBP:', error);
        // Ne pas bloquer l'utilisateur en cas d'erreur
      }
    }, 1000); // Attendre 1 seconde après la dernière saisie
    
    // Afficher temporairement un message de vérification
    if (password.length >= 12 && strength >= 5) {
      showError('pro-password-error', '🔍 Vérification de sécurité...');
    }
  }

  if (!errorMsg || password.length < 12 || strength < 5) {
    showError('pro-password-error', errorMsg);
  }
  
  // Vérifier aussi la correspondance si la confirmation est remplie
  const confirmValue = document.getElementById('pro-password-confirm')?.value;
  if (confirmValue) {
    validateProPasswordMatch();
  }

  return strength >= 5 && password.length >= 12;
}

// Validation de la correspondance des mots de passe avec feedback visuel amélioré
function validateProPasswordMatch() {
  const password = window.registerData.password;
  const confirm = document.getElementById('pro-password-confirm')?.value || window.window.registerData.passwordConfirm;
  const errorEl = document.getElementById('pro-password-confirm-error');
  const successEl = document.getElementById('pro-password-confirm-success');
  const inputEl = document.getElementById('pro-password-confirm');

  if (!confirm) {
    showError('pro-password-confirm-error', '');
    showSuccess('pro-password-confirm-success', '');
    if (inputEl) {
      inputEl.classList.remove('field-error', 'field-success');
      inputEl.style.borderColor = '';
      inputEl.style.boxShadow = '';
    }
    return false;
  }

  if (password !== confirm) {
    showError('pro-password-confirm-error', '⚠️ Les mots de passe ne correspondent pas');
    showSuccess('pro-password-confirm-success', '');
    if (inputEl) {
      inputEl.classList.add('field-error');
      inputEl.classList.remove('field-success');
      inputEl.style.borderColor = '#ef4444';
      inputEl.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)';
    }
    return false;
  } else {
    showError('pro-password-confirm-error', '');
    showSuccess('pro-password-confirm-success', '✓ Les mots de passe correspondent');
    if (inputEl) {
      inputEl.classList.add('field-success');
      inputEl.classList.remove('field-error');
      inputEl.style.borderColor = '#22c55e';
      inputEl.style.boxShadow = '0 0 0 3px rgba(34, 197, 94, 0.1)';
    }
    return true;
  }
}

// Sauvegarde automatique du formulaire d'inscription dans localStorage
let autoSaveTimer = null;
function autoSaveRegistrationForm() {
  // Debounce : sauvegarder seulement après 500ms d'inactivité
  clearTimeout(autoSaveTimer);
  autoSaveTimer = setTimeout(() => {
    try {
      if (!window.registerData) {
        return;
      }
      
      // Collecter toutes les données du formulaire
      const formData = {
        email: document.getElementById('pro-email')?.value || window.registerData.email || '',
        username: document.getElementById('pro-username')?.value || window.registerData.username || '',
        password: document.getElementById('pro-password')?.value || window.registerData.password || '',
        passwordConfirm: document.getElementById('pro-password-confirm')?.value || window.registerData.passwordConfirm || '',
        firstName: document.getElementById('pro-firstname')?.value || window.registerData.firstName || '',
        lastName: document.getElementById('pro-lastname')?.value || window.registerData.lastName || '',
        postalAddress: document.getElementById('pro-postal-address')?.value || window.registerData.postalAddress || '',
        addressLat: document.getElementById('pro-address-lat')?.value || window.registerData.addressLat || '',
        addressLng: document.getElementById('pro-address-lng')?.value || window.registerData.addressLng || '',
        addressCountry: document.getElementById('pro-address-country')?.value || window.registerData.addressCountry || '',
        addressLabel: document.getElementById('pro-address-label')?.value || window.registerData.addressLabel || '',
        profilePhoto: window.registerData.profilePhoto || '',
        photoData: window.registerData.photoData || '',
        avatarId: window.registerData.avatarId || 1,
        avatarDescription: window.registerData.avatarDescription || '',
        timestamp: Date.now()
      };
      
      // Sauvegarder dans localStorage avec gestion de quota
      try {
        localStorage.setItem('registerFormDraft', JSON.stringify(formData));
        
        // Mettre à jour window.registerData avec les nouvelles valeurs
        Object.assign(window.registerData, formData);
      } catch (quotaError) {
        // Si le localStorage est plein, nettoyer les données non essentielles
        if (quotaError.name === 'QuotaExceededError' || quotaError.message.includes('quota')) {
          console.warn('[AUTO-SAVE] localStorage plein - nettoyage automatique...');
          try {
            // Supprimer les données volumineuses non essentielles
            localStorage.removeItem('eventsData');
            localStorage.removeItem('bookingsData');
            localStorage.removeItem('servicesData');
            // Réessayer
            localStorage.setItem('registerFormDraft', JSON.stringify(formData));
            Object.assign(window.registerData, formData);
            console.log('[AUTO-SAVE] ✅ Sauvegarde réussie après nettoyage');
          } catch (e2) {
            // Si toujours plein, continuer sans sauvegarder (les données sont dans window.registerData)
            console.warn('[AUTO-SAVE] ⚠️ localStorage toujours plein - continuation sans sauvegarde');
            Object.assign(window.registerData, formData); // Mettre à jour quand même en mémoire
          }
        } else {
          throw quotaError;
        }
      }
      
    } catch (error) {
      console.warn('[AUTO-SAVE] Erreur sauvegarde:', error);
    }
  }, 500);
}

// Restaurer le formulaire depuis localStorage
function restoreRegistrationForm() {
  try {
    const saved = localStorage.getItem('registerFormDraft');
    if (!saved) {
      return false;
    }
    
    const formData = JSON.parse(saved);
    
    // Vérifier si le draft n'est pas trop ancien (max 7 jours)
    const maxAge = 7 * 24 * 60 * 60 * 1000; // 7 jours en millisecondes
    if (formData.timestamp && (Date.now() - formData.timestamp) > maxAge) {
      localStorage.removeItem('registerFormDraft');
      return false;
    }
    
    // Restaurer les valeurs dans les champs
    if (formData.email && document.getElementById('pro-email')) {
      document.getElementById('pro-email').value = formData.email;
      window.registerData.email = formData.email;
    }
    if (formData.username && document.getElementById('pro-username')) {
      document.getElementById('pro-username').value = formData.username;
      window.registerData.username = formData.username;
    }
    if (formData.firstName && document.getElementById('pro-firstname')) {
      document.getElementById('pro-firstname').value = formData.firstName;
      window.registerData.firstName = formData.firstName;
    }
    if (formData.lastName && document.getElementById('pro-lastname')) {
      document.getElementById('pro-lastname').value = formData.lastName;
      window.registerData.lastName = formData.lastName;
    }
    if (formData.postalAddress && document.getElementById('pro-postal-address')) {
      document.getElementById('pro-postal-address').value = formData.postalAddress;
      window.registerData.postalAddress = formData.postalAddress;
    }
    
    // Restaurer les données cachées
    if (formData.addressLat && document.getElementById('pro-address-lat')) {
      document.getElementById('pro-address-lat').value = formData.addressLat;
      window.registerData.addressLat = formData.addressLat;
    }
    if (formData.addressLng && document.getElementById('pro-address-lng')) {
      document.getElementById('pro-address-lng').value = formData.addressLng;
      window.registerData.addressLng = formData.addressLng;
    }
    if (formData.addressCountry && document.getElementById('pro-address-country')) {
      document.getElementById('pro-address-country').value = formData.addressCountry;
      window.registerData.addressCountry = formData.addressCountry;
    }
    if (formData.addressLabel && document.getElementById('pro-address-label')) {
      document.getElementById('pro-address-label').value = formData.addressLabel;
      window.registerData.addressLabel = formData.addressLabel;
    }
    
    // Restaurer la photo si elle existe
    console.log('[RESTORE] 🔍 Restauration photo depuis localStorage:');
    console.log('[RESTORE] formData.photoData:', formData.photoData ? `PRÉSENT (${formData.photoData.length} chars)` : 'NULL');
    console.log('[RESTORE] formData.profilePhoto:', formData.profilePhoto ? `PRÉSENT (${formData.profilePhoto.length} chars)` : 'NULL');
    
    if (window.registerData) {
      // Restaurer profilePhoto si présent
      if (formData.profilePhoto && formData.profilePhoto.length > 0) {
        window.registerData.profilePhoto = formData.profilePhoto;
        console.log('[RESTORE] ✅ profilePhoto restauré depuis localStorage');
      }
      
      // Restaurer photoData si présent, sinon utiliser profilePhoto
      if (formData.photoData && formData.photoData.length > 0) {
        window.registerData.photoData = formData.photoData;
        console.log('[RESTORE] ✅ photoData restauré depuis localStorage');
      } else if (formData.profilePhoto && formData.profilePhoto.length > 0) {
        window.registerData.photoData = formData.profilePhoto;
        console.log('[RESTORE] ✅ photoData copié depuis profilePhoto (photoData manquant dans localStorage)');
      }
      
      const photoPreview = document.getElementById('pro-photo-preview');
      const photoPlaceholder = document.getElementById('pro-photo-placeholder');
      if (photoPreview && window.registerData.profilePhoto && window.registerData.profilePhoto.length > 0) {
        photoPreview.src = window.registerData.profilePhoto;
        photoPreview.style.display = 'block';
        photoPreview.classList.add('show');
        if (photoPlaceholder) {
          photoPlaceholder.style.display = 'none';
        }
        console.log('[RESTORE] ✅ Preview mise à jour avec photo restaurée');
      }
      
      console.log('[RESTORE] registerData.photoData APRÈS restauration:', window.registerData.photoData ? `PRÉSENT (${window.registerData.photoData.length} chars)` : 'NULL');
      console.log('[RESTORE] registerData.profilePhoto APRÈS restauration:', window.registerData.profilePhoto ? `PRÉSENT (${window.registerData.profilePhoto.length} chars)` : 'NULL');
    }
    
    // Mettre à jour window.registerData avec toutes les données restaurées
    Object.assign(window.registerData, formData);
    
    // CORRECTION: S'assurer que photoData existe même après Object.assign
    if (window.registerData && window.registerData.profilePhoto && window.registerData.profilePhoto.length > 0) {
      if (!window.registerData.photoData || window.registerData.photoData.length === 0) {
        window.registerData.photoData = window.registerData.profilePhoto;
        console.log('[RESTORE] ✅✅✅ photoData FORCÉ depuis profilePhoto après Object.assign');
      }
    }
    
    return true;
  } catch (error) {
    console.warn('[RESTORE] Erreur restauration:', error);
    return false;
  }
}

// Exposer les fonctions globalement
window.autoSaveRegistrationForm = autoSaveRegistrationForm;
window.restoreRegistrationForm = restoreRegistrationForm;

// Toggle visibilité mot de passe
function toggleProPasswordVisibility(inputId, event) {
  // ⚠️⚠️⚠️ CRITIQUE : Empêcher la propagation pour éviter la fermeture du formulaire
  if (event) {
    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation();
  }
  
  const input = document.getElementById(inputId);
  if (!input) {
    console.warn('[PASSWORD TOGGLE] Input non trouvé:', inputId);
    return false;
  }
  
  if (input.type === 'password') {
    input.type = 'text';
  } else {
    input.type = 'password';
  }
  
  return false; // Empêcher tout comportement par défaut
}

// Toggle password visibility pour les champs register (auth modal)
function toggleRegisterPasswordVisibility(inputId) {
  console.log('[PASSWORD TOGGLE] toggleRegisterPasswordVisibility appelé:', inputId);
  const input = document.getElementById(inputId);
  if (!input) {
    console.warn('[PASSWORD TOGGLE] Input non trouvé:', inputId);
    return;
  }
  
  if (input.type === 'password') {
    input.type = 'text';
    console.log('[PASSWORD TOGGLE] Type changé en text');
  } else {
    input.type = 'password';
    console.log('[PASSWORD TOGGLE] Type changé en password');
  }
}

// Validation du mot de passe en temps réel
function validateRegisterPassword(password) {
  const rulesDiv = document.getElementById('register-password-rules');
  if (!rulesDiv) return;
  
  const rules = [];
  let isValid = true;
  
  // Règles de validation
  if (password.length < 8) {
    rules.push('❌ Au moins 8 caractères');
    isValid = false;
  } else {
    rules.push('✅ Au moins 8 caractères');
  }
  
  if (!/[A-Z]/.test(password)) {
    rules.push('❌ Au moins une majuscule');
    isValid = false;
  } else {
    rules.push('✅ Au moins une majuscule');
  }
  
  if (!/[a-z]/.test(password)) {
    rules.push('❌ Au moins une minuscule');
    isValid = false;
  } else {
    rules.push('✅ Au moins une minuscule');
  }
  
  if (!/[0-9]/.test(password)) {
    rules.push('❌ Au moins un chiffre');
    isValid = false;
  } else {
    rules.push('✅ Au moins un chiffre');
  }
  
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    rules.push('❌ Au moins un caractère spécial');
    isValid = false;
  } else {
    rules.push('✅ Au moins un caractère spécial');
  }
  
  rulesDiv.innerHTML = rules.map(rule => `<div style="margin:2px 0;">${rule}</div>`).join('');
  
  // Mettre à jour la couleur de bordure
  const passwordInput = document.getElementById('register-password');
  if (passwordInput) {
    if (isValid && password.length > 0) {
      passwordInput.style.borderColor = '#22c55e';
    } else if (password.length > 0) {
      passwordInput.style.borderColor = '#ef4444';
    } else {
      passwordInput.style.borderColor = 'rgba(255,255,255,0.1)';
    }
  }
  
  // Vérifier aussi la correspondance si le champ de confirmation existe
  const confirmInput = document.getElementById('register-password-confirm');
  if (confirmInput && confirmInput.value) {
    validateRegisterPasswordMatch();
  }
}

// Validation de la correspondance des mots de passe
function validateRegisterPasswordMatch() {
  const password = document.getElementById('register-password')?.value || '';
  const confirm = document.getElementById('register-password-confirm')?.value || '';
  const matchDiv = document.getElementById('register-password-match');
  const confirmInput = document.getElementById('register-password-confirm');
  
  if (!matchDiv || !confirmInput) return;
  
  if (confirm.length === 0) {
    matchDiv.style.display = 'none';
    confirmInput.style.borderColor = 'rgba(255,255,255,0.1)';
    return;
  }
  
  if (password === confirm && password.length > 0) {
    matchDiv.style.display = 'block';
    matchDiv.textContent = '✓ Les mots de passe correspondent';
    matchDiv.style.color = '#22c55e';
    confirmInput.style.borderColor = '#22c55e';
  } else {
    matchDiv.style.display = 'block';
    matchDiv.textContent = '❌ Les mots de passe ne correspondent pas';
    matchDiv.style.color = '#ef4444';
    confirmInput.style.borderColor = '#ef4444';
  }
}

// Exposer les fonctions globalement pour les onclick
window.toggleRegisterPasswordVisibility = toggleRegisterPasswordVisibility;
window.toggleProPasswordVisibility = toggleProPasswordVisibility;
window.validateRegisterPassword = validateRegisterPassword;
window.validateRegisterPasswordMatch = validateRegisterPasswordMatch;

// Helper pour afficher les erreurs
// Debounce timers pour éviter trop d'appels API
const validationTimers = {};

function showError(elementId, message) {
  const el = document.getElementById(elementId);
  if (!el) return;
  
  if (message) {
    el.textContent = message;
    el.style.display = 'block';
    el.style.opacity = '0';
    el.style.transform = 'translateY(-5px)';
    
    // Animation d'apparition
    requestAnimationFrame(() => {
      el.style.transition = 'all 0.3s ease';
      el.style.opacity = '1';
      el.style.transform = 'translateY(0)';
    });
    
    // Ajouter classe d'erreur au champ parent
    const input = document.getElementById(elementId.replace('-error', ''));
    if (input) {
      input.classList.add('field-error');
      input.style.borderColor = '#ef4444';
      input.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)';
    }
  } else {
    el.textContent = '';
    el.style.display = 'none';
    
    // Retirer classe d'erreur du champ parent
    const input = document.getElementById(elementId.replace('-error', ''));
    if (input) {
      input.classList.remove('field-error');
      input.style.borderColor = '';
      input.style.boxShadow = '';
    }
  }
}

function showSuccess(elementId, message) {
  const el = document.getElementById(elementId);
  if (!el) return;
  
  if (message) {
    el.textContent = message;
    el.style.display = 'block';
    el.style.opacity = '0';
    el.style.transform = 'translateY(-5px)';
    
    // Animation d'apparition
    requestAnimationFrame(() => {
      el.style.transition = 'all 0.3s ease';
      el.style.opacity = '1';
      el.style.transform = 'translateY(0)';
    });
    
    // Ajouter classe de succès au champ parent
    const input = document.getElementById(elementId.replace('-success', ''));
    if (input) {
      input.classList.add('field-success');
      input.style.borderColor = '#22c55e';
      input.style.boxShadow = '0 0 0 3px rgba(34, 197, 94, 0.1)';
    }
  } else {
    el.textContent = '';
    el.style.display = 'none';
    
    // Retirer classe de succès du champ parent
    const input = document.getElementById(elementId.replace('-success', ''));
    if (input) {
      input.classList.remove('field-success');
      input.style.borderColor = '';
      input.style.boxShadow = '';
    }
  }
}

function showLoading(elementId, message = 'Vérification...') {
  const el = document.getElementById(elementId);
  if (!el) return;
  
  el.innerHTML = `<span style="display:inline-flex;align-items:center;gap:6px;"><span style="display:inline-block;width:12px;height:12px;border:2px solid rgba(59,130,246,0.3);border-top-color:#3b82f6;border-radius:50%;animation:spin 0.6s linear infinite;"></span>${message}</span>`;
  el.style.display = 'block';
  el.style.opacity = '1';
}

// Fonction pour mettre à jour l'état requis de l'adresse postale
function updatePostalAddressRequired() {
  const skipAddress = document.getElementById('pro-skip-address')?.checked || false;
  const addressInput = document.getElementById('pro-postal-address');
  if (addressInput) {
    if (skipAddress) {
      addressInput.removeAttribute('required');
      addressInput.disabled = true;
      addressInput.style.opacity = '0.5';
      addressInput.style.cursor = 'not-allowed';
      window.registerData.postalAddress = '';
      showError('pro-postal-address-error', '');
    } else {
      addressInput.setAttribute('required', 'required');
      addressInput.disabled = false;
      addressInput.style.opacity = '1';
      addressInput.style.cursor = 'text';
      if (addressInput.value) {
        if (typeof window.validateProField === 'function') {
          window.validateProField('postalAddress', addressInput.value);
        }
      }
    }
  }
}

// Soumission du formulaire
// Guard contre double-submit
// NOTE: isSubmittingProRegister est déclarée dans auth.js et exposée via window.isSubmittingProRegister

async function handleProRegisterSubmit(event) {
  event.preventDefault();
  
  // GUARD: Éviter double-submit et double clic
  if (window.isSubmittingProRegister) {
    console.warn('⚠️ Soumission déjà en cours - double clic ignoré');
    return;
  }
  
  // VÉRIFICATION CRITIQUE : Si le profil est déjà complet, ne pas permettre la soumission
  if (currentUser && currentUser.profileComplete === true && currentUser.isLoggedIn === true) {
    console.warn('⚠️ Tentative de soumission formulaire alors que le profil est déjà complet');
    showNotification('✅ Votre compte est déjà créé et complet. Vous êtes connecté !', 'success');
    closePublishModal();
    return;
  }
  
  // Marquer comme en cours de soumission
  window.isSubmittingProRegister = true;
  
  // S'assurer que registerData existe et est initialisé
  if (!window.registerData) {
    window.registerData = {};
    console.log('[REGISTER] registerData initialisé');
  }
  
  // Récupérer toutes les valeurs
  // ⚠️ firstName et lastName sont OPTIONNELS (comme les leaders mondiaux : Twitter, Instagram, TikTok)
  // Seul le username est requis pour l'identification
  window.registerData.firstName = ''; // Optionnel - pas de champ dans le formulaire
  window.registerData.lastName = ''; // Optionnel - pas de champ dans le formulaire
  window.registerData.email = document.getElementById('pro-email')?.value.trim() || '';
  window.registerData.username = document.getElementById('pro-username')?.value.trim() || '';
  window.registerData.password = document.getElementById('pro-password')?.value || '';
  window.window.registerData.passwordConfirm = document.getElementById('pro-password-confirm')?.value || '';
  const skipAddress = document.getElementById('pro-skip-address')?.checked || false;
  window.registerData.postalAddress = skipAddress ? '' : (document.getElementById('pro-postal-address')?.value.trim() || '');
  
  // S'assurer que registerData existe
  if (!window.registerData) {
    window.registerData = {};
  }
  
  // Récupérer les données d'adresse vérifiée (si disponible)
  const addressLat = document.getElementById('pro-address-lat')?.value;
  const addressLng = document.getElementById('pro-address-lng')?.value;
  const addressCountry = document.getElementById('pro-address-country')?.value;
  const addressLabel = document.getElementById('pro-address-label')?.value;
  
  // Préparer le tableau addresses pour le backend
  let addresses = [];
  if (!skipAddress && window.registerData.postalAddress && addressLat && addressLng && addressCountry) {
    // Adresse vérifiée via Nominatim
    addresses = [{
      label: addressLabel || window.registerData.postalAddress,
      lat: parseFloat(addressLat),
      lng: parseFloat(addressLng),
      addressDetails: {
        country_code: addressCountry,
        city: '', // Peut être enrichi plus tard
        postcode: '',
        street: ''
      }
    }];
  } else if (!skipAddress && window.registerData.postalAddress && window.registerData.postalAddress.trim().length > 0) {
    // Adresse saisie mais non vérifiée - accepter quand même avec une adresse basique
    console.log('[REGISTER] Adresse tapée directement (sans coordonnées) - acceptée');
    addresses = [{
      label: window.registerData.postalAddress,
      address: window.registerData.postalAddress,
      lat: null,
      lng: null,
      addressDetails: {
        country_code: addressCountry || '', // Pas de pays par défaut - mondial
        city: '',
        postcode: '',
        street: ''
      }
    }];
  }

  // Validation complète
  let isValid = true;
  if (typeof window.validateProField === 'function') {
    isValid = window.validateProField('email', window.registerData.email) && isValid;
    isValid = window.validateProField('username', window.registerData.username) && isValid;
  }
  isValid = validateProPassword(window.registerData.password) && isValid;
  isValid = validateProPasswordMatch() && isValid;
  // L'adresse postale est optionnelle si "Pas pour l'instant" est coché
  // Si elle est saisie, accepter même sans coordonnées (l'utilisateur peut l'avoir tapée directement)
  if (!skipAddress && window.registerData.postalAddress && window.registerData.postalAddress.trim().length > 0) {
    // Si l'adresse a des coordonnées, les utiliser
    if (addressLat && addressLng && addressCountry) {
      // Adresse vérifiée avec coordonnées - parfait
      console.log('[REGISTER] Adresse vérifiée avec coordonnées');
    } else {
      // Adresse tapée directement sans sélectionner depuis les suggestions
      // Accepter quand même mais logger un avertissement
      console.log('[REGISTER] Adresse tapée directement (sans coordonnées) - acceptée');
      // Créer une adresse basique avec les données disponibles
      if (!addresses || addresses.length === 0) {
        addresses = [{
          address: window.registerData.postalAddress,
          city: window.registerData.postalAddress.split(',')[0] || '',
          lat: null,
          lng: null,
          country: window.registerData.addressCountry || '', // Pas de pays par défaut - mondial
          isPrimary: true
        }];
      }
    }
  }

  // Vérifier la photo - VÉRIFIER photoData, profilePhoto ET l'image preview
  const photoPreview = document.getElementById('pro-photo-preview');
  const photoPlaceholder = document.getElementById('pro-photo-placeholder');
  const hasPhotoPreview = photoPreview && photoPreview.src && !photoPreview.src.includes('placeholder') && photoPreview.style.display !== 'none';
  
  // CORRECTION CRITIQUE ABSOLUE: Copier photoData depuis profilePhoto OU preview AVANT TOUTE VÉRIFICATION
  console.log('[REGISTER] 🔥🔥🔥🔥🔥 CORRECTION PHOTO - AVANT VÉRIFICATION');
  console.log('[REGISTER] registerData existe:', !!window.registerData);
  console.log('[REGISTER] registerData.profilePhoto:', window.registerData?.profilePhoto ? `PRÉSENT (${window.registerData.profilePhoto.length} chars)` : 'NULL');
  console.log('[REGISTER] registerData.photoData AVANT:', window.registerData?.photoData ? `PRÉSENT (${window.registerData.photoData?.length || 0} chars)` : 'NULL');
  console.log('[REGISTER] photoPreview existe:', !!photoPreview);
  console.log('[REGISTER] photoPreview.src:', photoPreview?.src ? `PRÉSENT (${photoPreview.src.length} chars, startsWith data:image: ${photoPreview.src.startsWith('data:image')})` : 'NULL');
  
  // FORCER la copie de photoData depuis profilePhoto OU preview
  if (window.registerData) {
    let photoCopied = false;
    
    // 1. Si profilePhoto existe, l'utiliser
    if (window.registerData.profilePhoto && 
        window.registerData.profilePhoto.length > 0 &&
        (!window.registerData.photoData || 
         window.registerData.photoData === 'null' || 
         window.registerData.photoData === '' ||
         window.registerData.photoData.length === 0)) {
      window.registerData.photoData = window.registerData.profilePhoto;
      console.log('[REGISTER] ✅✅✅✅✅ photoData FORCÉ depuis profilePhoto!');
      photoCopied = true;
    }
    
    // 2. Si photoData est toujours vide, utiliser la preview
    if ((!window.registerData.photoData || window.registerData.photoData.length === 0) &&
        photoPreview && photoPreview.src && photoPreview.src.startsWith('data:image') && photoPreview.src.length > 100) {
      window.registerData.photoData = photoPreview.src;
      // Copier aussi dans profilePhoto si vide
      if (!window.registerData.profilePhoto || window.registerData.profilePhoto.length === 0) {
        window.registerData.profilePhoto = photoPreview.src;
        console.log('[REGISTER] ✅✅✅ profilePhoto ET photoData copiés depuis preview.src');
      } else {
        console.log('[REGISTER] ✅✅✅ photoData copié depuis preview.src');
      }
      photoCopied = true;
    }
    
    if (!photoCopied) {
      console.log('[REGISTER] ⚠️ Aucune copie effectuée - photoData existe déjà ou aucune source disponible');
    }
  }
  
  console.log('[REGISTER] registerData.photoData APRÈS:', window.registerData?.photoData ? `PRÉSENT (${window.registerData.photoData.length} chars)` : 'NULL');
  
  const hasPhotoData = window.registerData.photoData && 
                       window.registerData.photoData !== 'null' && 
                       window.registerData.photoData !== '' &&
                       window.registerData.photoData.length > 0;
  const hasProfilePhoto = window.registerData.profilePhoto && 
                         window.registerData.profilePhoto !== 'null' && 
                         window.registerData.profilePhoto !== '' &&
                         window.registerData.profilePhoto.length > 0;
  const hasPhoto = hasPhotoData || hasProfilePhoto || hasPhotoPreview;
  
  // CORRECTION ABSOLUE FINALE: Si photoData est toujours null mais que profilePhoto ou preview existe, FORCER la copie
  if (!hasPhotoData && (hasProfilePhoto || hasPhotoPreview)) {
    console.log('[REGISTER] ⚠️⚠️⚠️ DERNIÈRE CHANCE: photoData est null mais profilePhoto/preview existe, FORCER copie!');
    if (window.registerData.profilePhoto && window.registerData.profilePhoto.length > 0) {
      window.registerData.photoData = window.registerData.profilePhoto;
      console.log('[REGISTER] ✅✅✅✅✅✅✅ photoData FORCÉ depuis profilePhoto (DERNIÈRE CHANCE)!');
      hasPhotoData = true;
    } else if (hasPhotoPreview && photoPreview && photoPreview.src && photoPreview.src.startsWith('data:image') && photoPreview.src.length > 100) {
      window.registerData.photoData = photoPreview.src;
      if (!window.registerData.profilePhoto || window.registerData.profilePhoto.length === 0) {
        window.registerData.profilePhoto = photoPreview.src;
      }
      console.log('[REGISTER] ✅✅✅✅✅✅✅ photoData FORCÉ depuis preview.src (DERNIÈRE CHANCE)!');
      hasPhotoData = true;
    }
  }
  
  console.log('[REGISTER] Vérification photo FINALE - photoData:', hasPhotoData ? 'présent' : 'null', 'profilePhoto:', hasProfilePhoto ? 'présent' : 'null', 'preview:', hasPhotoPreview ? 'visible' : 'non visible');
  console.log('[REGISTER] hasPhoto (validation):', hasPhoto);
  console.log('[REGISTER] registerData.photoData FINAL:', window.registerData?.photoData ? `PRÉSENT (${window.registerData.photoData.length} chars)` : 'NULL');
  
  if (!hasPhoto) {
    showError('pro-photo-error', '⚠️ Veuillez ajouter une photo de profil');
    isValid = false;
  } else {
    showError('pro-photo-error', ''); // Effacer l'erreur si la photo est présente
  }
  
  // Vérifier consentement RGPD
  const consentTerms = document.getElementById('pro-consent-terms')?.checked;
  const consentPrivacy = document.getElementById('pro-consent-privacy')?.checked;
  if (!consentTerms || !consentPrivacy) {
    console.log('[REGISTER] ⚠️ Consentement RGPD manquant - consentTerms:', consentTerms, 'consentPrivacy:', consentPrivacy);
    showNotification('⚠️ Vous devez accepter les conditions d\'utilisation et la politique de confidentialité', 'warning');
    isValid = false;
  } else {
    console.log('[REGISTER] ✅ Consentement RGPD accepté');
  }

  if (!isValid) {
    console.log('[REGISTER] ⚠️ Validation échouée - formulaire non soumis');
    window.isSubmittingProRegister = false; // Réactiver le bouton
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Créer le compte';
    }
    showNotification('⚠️ Veuillez corriger les erreurs dans le formulaire', 'warning');
    return;
  }
  
  console.log('[REGISTER] ✅✅✅ Validation réussie - soumission du formulaire...');
  
  // Arrêter l'auto-save avant soumission
  if (typeof stopAutoSave === 'function') {
    stopAutoSave();
  }
  
  // Supprimer le draft après soumission réussie
  localStorage.removeItem('registration_draft');

  // Désactiver le bouton
  const submitBtn = document.getElementById('pro-submit-btn');
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.textContent = 'Création du compte...';
  }

  // NOUVEAU FLUX: Après validation du formulaire, afficher le choix de vérification AVANT de créer le compte
  try {
    // Stocker les données du formulaire pour utilisation ultérieure
    const selectedAddress = addresses && addresses.length > 0 ? addresses[0] : null;
    
    // CORRECTION CRITIQUE ABSOLUE: S'assurer que photoData existe avant de créer pendingRegisterData
    console.log('[REGISTER] 🔥🔥🔥 VÉRIFICATION AVANT pendingRegisterData:');
    console.log('[REGISTER] registerData existe:', !!window.registerData);
    console.log('[REGISTER] registerData.profilePhoto:', window.registerData?.profilePhoto ? `PRÉSENT (${window.registerData.profilePhoto.length} chars)` : 'NULL');
    console.log('[REGISTER] registerData.photoData AVANT:', window.registerData?.photoData ? `PRÉSENT (${window.registerData.photoData?.length || 0} chars)` : 'NULL');
    
    // Vérifier aussi la preview au cas où
    const photoPreview = document.getElementById('pro-photo-preview');
    if (photoPreview && photoPreview.src && photoPreview.src.startsWith('data:image') && photoPreview.src.length > 100) {
      console.log('[REGISTER] Preview a une source base64, longueur:', photoPreview.src.length);
      // Si profilePhoto est vide mais la preview a une image, utiliser la preview
      if (!window.registerData.profilePhoto || window.registerData.profilePhoto.length === 0) {
        window.registerData.profilePhoto = photoPreview.src;
        console.log('[REGISTER] ✅ profilePhoto copié depuis preview.src');
      }
    }
    
    // FORCER la copie de photoData depuis profilePhoto si nécessaire
    if (window.registerData) {
      // Si profilePhoto existe et photoData n'existe pas ou est vide
      if (window.registerData.profilePhoto && 
          window.registerData.profilePhoto.length > 0 &&
          (!window.registerData.photoData || 
           window.registerData.photoData === 'null' || 
           window.registerData.photoData === '' ||
           window.registerData.photoData.length === 0)) {
        window.registerData.photoData = window.registerData.profilePhoto;
        console.log('[REGISTER] ✅✅✅✅✅ photoData FORCÉ depuis profilePhoto avant pendingRegisterData');
      }
      
      // Si photoData est toujours vide mais que la preview a une image
      if ((!window.registerData.photoData || window.registerData.photoData.length === 0) &&
          photoPreview && photoPreview.src && photoPreview.src.startsWith('data:image') && photoPreview.src.length > 100) {
        window.registerData.photoData = photoPreview.src;
        console.log('[REGISTER] ✅✅✅ photoData copié depuis preview.src');
      }
    }
    
    console.log('[REGISTER] registerData.photoData APRÈS:', window.registerData?.photoData ? `PRÉSENT (${window.registerData.photoData.length} chars)` : 'NULL');
    
    // Récupérer photoData depuis registerData (photo uploadée) - utiliser profilePhoto comme fallback
    const photoData = window.registerData.photoData || window.registerData.profilePhoto || null;
    console.log('[REGISTER] photoData FINAL récupéré pour pendingRegisterData:', photoData ? `PRÉSENT (${photoData.length} chars)` : 'NULL');
    
    // Détecter si c'est un utilisateur Google OAuth (connexion OAuth)
    const isGoogleUser = currentUser && (
      currentUser.provider === 'google' || 
      currentUser.googleValidated === true ||
      (currentUser.sub && currentUser.email === window.registerData.email) ||
      (currentUser.email === window.registerData.email && window.registerData.email.includes('@gmail.com'))
    );
    
    // Si c'est un utilisateur Google OAuth, créer directement le compte sans vérification supplémentaire
    if (isGoogleUser) {
      console.log('[REGISTER] Utilisateur Google OAuth détecté - création directe du compte');
      
      // Préparer le payload pour Google OAuth complete
      const payload = {
        email: window.registerData.email,
        username: window.registerData.username,
        password: window.registerData.password || '',
        firstName: window.registerData.firstName || '',
        lastName: window.registerData.lastName || '',
        profilePhoto: photoData || '',
        addresses: addresses || [],
        userId: currentUser?.id || null,
        googleSub: currentUser?.sub || null,
        sub: currentUser?.sub || null
      };
      
      // Si une adresse a été sélectionnée, l'ajouter
      if (selectedAddress) {
        payload.postalAddress = selectedAddress.label || window.registerData.postalAddress || '';
      }
      
      console.log('[REGISTER] Création compte Google OAuth avec payload:', {
        email: payload.email,
        username: payload.username,
        hasPhoto: !!payload.profilePhoto,
        hasAddresses: addresses.length > 0
      });
      
      try {
        const response = await fetch(`${window.API_BASE_URL}/user/oauth/google/complete`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        
        if (response.ok) {
          const data = await response.json();
          console.log('[REGISTER] Compte créé avec succès:', data);
          
          // Mettre à jour currentUser avec les données du compte créé
          if (data.user) {
            const slimUser = {
              id: data.user.id || currentUser.id,
              email: data.user.email || window.registerData.email,
              username: data.user.username || window.registerData.username,
              firstName: data.user.firstName || data.user.first_name || window.registerData.firstName,
              lastName: data.user.lastName || data.user.last_name || window.registerData.lastName,
              role: data.user.role || 'user',
              subscription: data.user.subscription || 'free',
              profile_photo_url: data.user.profile_photo_url || null,
              hasPassword: data.user.hasPassword || false,
              hasPostalAddress: data.user.hasPostalAddress || false,
              profileComplete: data.user.profileComplete !== undefined ? data.user.profileComplete : true,
              isLoggedIn: true
            };
            
            currentUser = { ...currentUser, ...slimUser };
            
            // Sauvegarder dans localStorage
            try {
              const slimJson = JSON.stringify(slimUser);
              localStorage.setItem('currentUser', slimJson);
            } catch (e) {
              try { sessionStorage.setItem('currentUser', slimJson); } catch (e2) {}
            }
            
            // Mettre à jour l'UI
            if (typeof updateAuthUI === 'function') {
              updateAuthUI(slimUser);
            }
            
            showNotification('✅ Compte créé avec succès ! Vous êtes maintenant connecté.', 'success');
            closePublishModal();
          }
        } else {
          const errorData = await response.json().catch(() => ({ error: 'Erreur lors de la création du compte' }));
          console.error('[REGISTER] Erreur création compte:', errorData);
          showNotification(`❌ Erreur: ${errorData.error || 'Erreur lors de la création du compte'}`, 'error');
          
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Créer le compte';
          }
        }
      } catch (error) {
        console.error('[REGISTER] Erreur lors de la création du compte:', error);
        showNotification('❌ Erreur de connexion. Veuillez réessayer.', 'error');
        
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Créer le compte';
        }
      }
      
      return; // Sortir ici pour les utilisateurs Google OAuth
    }
    
    // Pour les utilisateurs normaux (non Google OAuth), utiliser le flux de vérification
    window.pendingRegisterData = {
      email: window.registerData.email,
      username: window.registerData.username,
      password: window.registerData.password,
      firstName: window.registerData.firstName || '',
      lastName: window.registerData.lastName || '',
      photoData: photoData, // INCLURE photoData (photo uploadée lors de la création)
      photoLater: false,
      addressLater: !selectedAddress,
      selectedAddress: selectedAddress,
      addresses: addresses || [],
      avatarId: window.registerData.avatarId || 1
    };
    
    console.log('[REGISTER] pendingRegisterData créé avec photoData:', window.pendingRegisterData.photoData ? (window.pendingRegisterData.photoData.substring(0, 50) + '...') : 'null');
    console.log('[REGISTER] Formulaire validé, affichage choix de vérification');
    
    // Réactiver le bouton
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Créer mon compte';
    }
    
    // Afficher le choix de méthode de vérification (Google, Facebook bientôt, Email)
    console.log('[REGISTER] Vérification disponibilité showVerificationChoice...');
    console.log('[REGISTER] typeof showVerificationChoice:', typeof showVerificationChoice);
    console.log('[REGISTER] typeof window.showVerificationChoice:', typeof window.showVerificationChoice);
    
    if (typeof showVerificationChoice === 'function') {
      console.log('[REGISTER] Appel showVerificationChoice() direct');
      showVerificationChoice();
    } else if (typeof window.showVerificationChoice === 'function') {
      console.log('[REGISTER] Appel window.showVerificationChoice()');
      window.showVerificationChoice();
    } else {
      console.error('[REGISTER] showVerificationChoice non disponible, fallback vers vérification email');
      showEmailVerificationModal(window.registerData.email, window.registerData.username || 'Utilisateur');
    }
    
    return; // NE PAS créer le compte maintenant, attendre le choix de vérification
  } catch (error) {
    console.error('❌ Erreur lors de la préparation du formulaire:', error);
    showNotification('❌ Erreur lors de la préparation du formulaire', 'error');
    
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Créer le compte';
    }
  }
  
  // ============================================
  // ANCIEN CODE DÉSACTIVÉ (ne sera plus exécuté)
  // Le compte sera créé après le choix de vérification (Google ou Email)
  // ============================================
  /*
  try {
    // Détecter si c'est un utilisateur Google (connexion OAuth)
    const isGoogleUser = currentUser && (
      currentUser.provider === 'google' || 
      currentUser.googleValidated === true ||
      (currentUser.sub && currentUser.email === window.registerData.email) ||
      (currentUser.email === window.registerData.email && window.registerData.email.includes('@gmail.com'))
    );
    
    // API_BASE_URL contient déjà '/api', donc pas besoin de l'ajouter à nouveau
    const endpoint = isGoogleUser ? `${window.API_BASE_URL}/user/oauth/google/complete` : `${window.API_BASE_URL}/user/register`;
    
    // Préparer le payload selon le type d'utilisateur
    const basePayload = {
      email: window.registerData.email,
      username: window.registerData.username,
      password: window.registerData.password,
      firstName: window.registerData.firstName,
      lastName: window.registerData.lastName,
      profilePhoto: window.registerData.profilePhoto,
      addresses: addresses
    };
    
    const payload = isGoogleUser ? {
      ...basePayload,
      userId: currentUser?.id || null,
      googleSub: currentUser?.sub || null,
      sub: currentUser?.sub || null
    } : {
      ...basePayload,
      avatarId: window.registerData.avatarId || 1
    };
    
    console.log(`📤 Envoi formulaire ${isGoogleUser ? 'Google OAuth' : 'inscription standard'} vers ${endpoint}`);
    
    // Envoyer au backend
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (response.ok) {
      const data = await response.json();
      console.log('[REGISTER] Réponse backend reçue:', { ok: data.ok, hasUser: !!data.user, userKeys: data.user ? Object.keys(data.user) : [] });
      
      // PRIORITY HOTFIX: Créer slimUser uniquement avec les champs essentiels
      // Ne jamais stocker la réponse complète du backend
      let slimUser = null;
      if (data.user) {
        slimUser = {
          id: data.user.id || currentUser?.id,
          email: data.user.email || window.registerData.email,
          username: data.user.username || window.registerData.username,
          role: data.user.role || 'user',
          subscription: data.user.subscription || 'free',
          profile_photo_url: data.user.profile_photo_url || null,
          hasPassword: data.user.hasPassword || false,
          hasPostalAddress: data.user.hasPostalAddress || false,
          profileComplete: data.user.profileComplete !== undefined ? data.user.profileComplete : true
        };
      } else {
        // Fallback minimal si pas de data.user
        slimUser = {
          id: data.user?.id || Date.now(),
          email: window.registerData.email,
          username: window.registerData.username,
          role: 'user',
          subscription: 'free',
          profileComplete: true
        };
      }
      
      // PRIORITY HOTFIX: Mettre à jour l'UI "logged-in" IMMÉDIATEMENT AVANT toute écriture storage
      // Cela garantit que l'UI reflète l'état connecté même si storage échoue
      console.log('[REGISTER] Mise à jour UI logged-in AVANT storage...');
      updateAuthUI(slimUser);
      
      // Afficher le message de bienvenue
      const welcomeName = slimUser.username || slimUser.email?.split('@')[0] || 'Utilisateur';
      
      // Afficher le modal de vérification d'email au lieu de fermer directement
      showEmailVerificationModal(window.registerData.email, welcomeName);
      
      // PRIORITY HOTFIX: Sauvegarder uniquement slimUser dans localStorage
      // Fallback vers sessionStorage si localStorage plein
      try {
        const slimJson = JSON.stringify(slimUser);
        try {
          localStorage.setItem('currentUser', slimJson);
          console.log('✅ User slim sauvegardé dans localStorage');
        } catch (localStorageError) {
          if (localStorageError.name === 'QuotaExceededError' || localStorageError.message.includes('quota')) {
            console.warn('⚠️ localStorage plein - tentative sessionStorage...');
            try {
              sessionStorage.setItem('currentUser', slimJson);
              console.log('✅ User slim sauvegardé dans sessionStorage (fallback)');
              showNotification('⚠️ Données sauvegardées temporairement (session)', 'info');
            } catch (sessionStorageError) {
              console.warn('⚠️ sessionStorage aussi plein - user gardé en mémoire (window.currentUser)');
              // User déjà en window.currentUser, UI déjà mise à jour - continuer
            }
          } else {
            throw localStorageError;
          }
        }
      } catch (storageError) {
        console.warn('⚠️ Erreur storage (non bloquant):', storageError);
        // User déjà en window.currentUser, UI déjà mise à jour - continuer
      }
      
      // Charger les données utilisateur (optionnel, peut échouer sans bloquer)
      try {
        await loadUserDataOnLogin();
      } catch (loadError) {
        console.warn('⚠️ Erreur loadUserDataOnLogin (non bloquant):', loadError);
        // Continuer - l'utilisateur est déjà connecté et l'UI mise à jour
      }
      
      // Réinitialiser le flag de soumission
      window.isSubmittingProRegister = false;
    } else {
      // Gérer les erreurs HTTP
      let errorMessage = 'Impossible de créer le compte';
      let errorData = null;
      
      try {
        const errorText = await response.text();
        console.error(`❌ Erreur serveur ${response.status}:`, errorText);
        
        try {
          errorData = JSON.parse(errorText);
          errorMessage = errorData.error || errorMessage;
        } catch (e) {
          // Si ce n'est pas du JSON, utiliser le texte brut
          if (errorText && errorText.length < 200) {
            errorMessage = errorText;
          }
        }
      } catch (e) {
        console.error('Erreur lecture réponse:', e);
      }
      
      // PRIORITÉ 3 FIX: Gérer USERNAME_ALREADY_EXISTS avec message clair
      if (errorData && errorData.code === 'USERNAME_ALREADY_EXISTS') {
        errorMessage = 'Ce nom d\'utilisateur est déjà pris. Choisissez-en un autre ou contactez le support si c\'est votre compte.';
        showNotification(`⚠️ ${errorMessage}`, 'warning');
        
        // Focus sur le champ username pour permettre la modification
        const usernameInput = document.getElementById('pro-username') || document.getElementById('register-username');
        if (usernameInput) {
          usernameInput.focus();
          usernameInput.select();
        }
        return; // Ne pas fermer le modal, permettre la correction
      }
      
      // Messages spécifiques selon le code d'erreur
      if (response.status === 502) {
        errorMessage = 'Erreur serveur (502). Le serveur est temporairement indisponible. Veuillez réessayer dans quelques instants.';
      } else if (response.status === 500) {
        errorMessage = 'Erreur serveur (500). Veuillez réessayer.';
      } else if (response.status === 400) {
        errorMessage = errorMessage || 'Données invalides. Vérifiez vos informations.';
      } else if (response.status === 404) {
        errorMessage = 'Utilisateur non trouvé. Veuillez d\'abord vous connecter avec Google.';
      }
      
      console.error(`❌ Échec création compte: ${response.status} - ${errorMessage}`);
      showNotification(`❌ ${errorMessage}`, 'error');
      
      // Réinitialiser le flag de soumission
      window.isSubmittingProRegister = false;
      
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Créer le compte';
      }
    }
  } catch (error) {
    console.error('❌ Erreur création compte:', error);
    console.error('Détails erreur:', error.message, error.stack);
    
    // Réinitialiser le flag de soumission
    isSubmittingProRegister = false;
    
    let errorMessage = 'Erreur réseau. Veuillez réessayer.';
    if (error.message && error.message.includes('Failed to fetch')) {
      errorMessage = 'Erreur de connexion. Vérifiez votre connexion internet.';
    } else if (error.message && error.message.includes('timeout')) {
      errorMessage = 'Timeout de connexion. Le serveur met trop de temps à répondre.';
    }
    
    showNotification(`❌ ${errorMessage}`, 'error');
    
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Créer le compte';
    }
  }
  */
}

// Fonction pour afficher le modal de vérification d'email après inscription
// Fonction pour afficher un formulaire photo uniquement (quand photo manquante)
function showPhotoUploadForm(userData) {
  console.log('[PHOTO UPLOAD] Affichage formulaire photo uniquement pour:', userData?.email);
  
  const backdrop = document.getElementById('publish-modal-backdrop');
  const modal = document.getElementById('publish-modal-inner');
  
  if (!backdrop || !modal) {
    console.error('[PHOTO UPLOAD] Modal elements not found');
    return;
  }
  
  let selectedPhoto = null;
  let photoPreview = null;
  
  const html = `
    <div style="padding:40px;max-width:500px;margin:0 auto;text-align:center;position:relative;">
      <!-- Bouton X (croix) pour fermer -->
      <button onclick="closeAuthModal()" style="position:absolute;top:16px;right:16px;background:none;border:none;color:var(--ui-text-muted);font-size:24px;cursor:pointer;padding:8px;width:40px;height:40px;display:flex;align-items:center;justify-content:center;border-radius:50%;transition:all 0.2s;z-index:10;" onmouseover="this.style.background='rgba(239,68,68,0.2)';this.style.color='#ef4444';this.style.transform='scale(1.1)';" onmouseout="this.style.background='none';this.style.color='var(--ui-text-muted)';this.style.transform='scale(1)';" title="Fermer">✕</button>
      
      <div style="font-size:64px;margin-bottom:20px;">📷</div>
      <h2 style="margin:0 0 12px;font-size:24px;font-weight:700;color:#fff;">Photo de profil requise</h2>
      <p style="margin:0 0 32px;font-size:14px;color:var(--ui-text-muted);line-height:1.6;">
        Une photo de profil est obligatoire pour compléter votre compte.<br>
        Vous pouvez ajouter une photo maintenant ou passer cette étape et la configurer plus tard depuis votre profil.
      </p>
      
      <!-- Zone d'aperçu photo -->
      <div id="photo-preview-container" style="width:150px;height:150px;margin:0 auto 24px;border-radius:50%;background:rgba(15,23,42,0.5);border:3px solid rgba(255,255,255,0.2);display:flex;align-items:center;justify-content:center;overflow:hidden;cursor:pointer;transition:all 0.3s;" onclick="document.getElementById('photo-upload-oauth-input').click();" onmouseover="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(15,23,42,0.8)';" onmouseout="this.style.borderColor='rgba(255,255,255,0.2)';this.style.background='rgba(15,23,42,0.5)';">
        <div style="font-size:48px;color:var(--ui-text-muted);">📷</div>
      </div>
      
      <input type="file" id="photo-upload-oauth-input" accept="image/*" style="display:none;" onchange="handleOAuthPhotoUpload(event)">
      
      <div id="photo-upload-feedback" style="min-height:24px;margin-bottom:24px;font-size:13px;color:var(--ui-text-muted);"></div>
      
      <div style="display:flex;flex-direction:column;gap:12px;">
        <button onclick="uploadOAuthPhoto()" id="upload-photo-btn" disabled style="width:100%;padding:14px;border-radius:12px;border:none;background:rgba(255,255,255,0.2);color:rgba(255,255,255,0.5);font-weight:700;font-size:15px;cursor:not-allowed;transition:all 0.3s;">
          Ajouter la photo
        </button>
        <button onclick="skipPhotoUpload()" style="width:100%;padding:12px;border-radius:12px;border:2px solid rgba(255,255,255,0.2);background:transparent;color:#fff;font-weight:600;font-size:14px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(255,255,255,0.4)';this.style.background='rgba(255,255,255,0.05)';" onmouseout="this.style.borderColor='rgba(255,255,255,0.2)';this.style.background='transparent';">
          Passer cette étape (pour plus tard)
        </button>
        <button onclick="closeAuthModal()" style="width:100%;padding:12px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:transparent;color:var(--ui-text-muted);font-weight:600;font-size:14px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(255,255,255,0.3)';this.style.color='var(--ui-text-main)';" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)';this.style.color='var(--ui-text-muted)';">
          Annuler
        </button>
      </div>
    </div>
  `;
  
  modal.innerHTML = html;
  backdrop.style.display = 'flex';
  
  // Stocker les données utilisateur pour l'upload
  window.oauthPhotoUploadData = userData;
}

// Gérer l'upload de photo pour OAuth
window.handleOAuthPhotoUpload = function(event) {
  const file = event.target.files[0];
  if (!file) return;
  
  // Vérifier que c'est une image
  if (!file.type.startsWith('image/')) {
    document.getElementById('photo-upload-feedback').innerHTML = '<span style="color:var(--ui-text-error);">⚠️ Veuillez sélectionner une image</span>';
    return;
  }
  
  // Vérifier la taille (max 5MB)
  if (file.size > 5 * 1024 * 1024) {
    document.getElementById('photo-upload-feedback').innerHTML = '<span style="color:var(--ui-text-error);">⚠️ L\'image est trop volumineuse (max 5MB)</span>';
    return;
  }
  
  // Afficher l'aperçu
  const reader = new FileReader();
  reader.onload = function(e) {
    const previewContainer = document.getElementById('photo-preview-container');
    if (previewContainer) {
      previewContainer.innerHTML = `<img src="${e.target.result}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;" alt="Photo preview">`;
    }
    
    // Activer le bouton d'upload
    const uploadBtn = document.getElementById('upload-photo-btn');
    if (uploadBtn) {
      uploadBtn.disabled = false;
      uploadBtn.style.background = 'linear-gradient(135deg,#00ffc3,#3b82f6)';
      uploadBtn.style.color = '#000';
      uploadBtn.style.cursor = 'pointer';
    }
    
    document.getElementById('photo-upload-feedback').innerHTML = '<span style="color:var(--ui-text-success);">✅ Photo sélectionnée</span>';
  };
  reader.readAsDataURL(file);
  
  // Stocker le fichier
  window.oauthPhotoFile = file;
};

// Uploader la photo pour OAuth
window.uploadOAuthPhoto = async function() {
  const file = window.oauthPhotoFile;
  const userData = window.oauthPhotoUploadData;
  
  if (!file || !userData) {
    showNotification('❌ Erreur: Fichier ou données utilisateur manquants', 'error');
    return;
  }
  
  const uploadBtn = document.getElementById('upload-photo-btn');
  const feedback = document.getElementById('photo-upload-feedback');
  
  if (uploadBtn) {
    uploadBtn.disabled = true;
    uploadBtn.textContent = 'Upload en cours...';
  }
  
  if (feedback) {
    feedback.innerHTML = '<span style="color:var(--ui-text-info);">⏳ Upload en cours...</span>';
  }
  
  try {
    // Convertir l'image en base64
    const reader = new FileReader();
    reader.onload = async function(e) {
      const base64Photo = e.target.result;
      
      // Appeler l'endpoint de complétion OAuth avec la photo
      const response = await fetch(`${window.API_BASE_URL}/user/oauth/google/complete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: userData.id,
          email: userData.email,
          username: userData.username || userData.email?.split('@')[0]?.substring(0, 20),
          firstName: userData.firstName || userData.first_name || '',
          lastName: userData.lastName || userData.last_name || '',
          profilePhoto: base64Photo
        })
      });
      
      const result = await response.json();
      
      if (response.ok && result.ok) {
        // Mettre à jour currentUser et UI
        if (result.user) {
          const slimUser = {
            id: result.user.id || userData.id,
            email: result.user.email || userData.email,
            username: result.user.username || userData.username,
            firstName: result.user.firstName || result.user.first_name || '',
            lastName: result.user.lastName || result.user.last_name || '',
            role: result.user.role || 'user',
            subscription: result.user.subscription || 'free',
            profile_photo_url: result.user.profile_photo_url || base64Photo,
            hasPassword: result.user.hasPassword || false,
            hasPostalAddress: result.user.hasPostalAddress || false,
            profileComplete: true,
            isLoggedIn: true
          };
          
          currentUser = { ...currentUser, ...slimUser, isLoggedIn: true };
          updateAuthUI(slimUser);
          
          try {
            const slimJson = JSON.stringify(slimUser);
            localStorage.setItem('currentUser', slimJson);
          } catch (e) {
            try { sessionStorage.setItem('currentUser', slimJson); } catch (e2) {}
          }
        }
        
        closeAuthModal();
        closePublishModal();
        
        // Si besoin confirmation email, afficher le modal
        if (result.needsEmailVerification) {
          showEmailVerificationModal(userData.email, userData.username || 'Utilisateur');
        } else {
          const displayName = userData.username || userData.firstName || userData.email?.split('@')[0] || 'Utilisateur';
          showNotification(`✅ Bienvenue ${displayName} ! Vous êtes connecté.`, 'success');
        }
        
        // Nettoyer
        delete window.oauthPhotoFile;
        delete window.oauthPhotoUploadData;
      } else {
        throw new Error(result.error || 'Erreur lors de l\'upload de la photo');
      }
    };
    reader.readAsDataURL(file);
  } catch (error) {
    console.error('❌ Erreur upload photo OAuth:', error);
    if (feedback) {
      feedback.innerHTML = `<span style="color:var(--ui-text-error);">❌ ${error.message || 'Erreur lors de l\'upload'}</span>`;
    }
    if (uploadBtn) {
      uploadBtn.disabled = false;
      uploadBtn.textContent = 'Ajouter la photo';
    }
    showNotification(`❌ ${error.message || 'Erreur lors de l\'upload de la photo'}`, 'error');
  }
};

// Passer l'étape photo (rediriger vers le formulaire complet)
window.skipPhotoUpload = function() {
  const userData = window.oauthPhotoUploadData;
  if (!userData) {
    closeAuthModal();
    return;
  }
  
  // Fermer le modal photo et afficher le formulaire complet d'inscription
  closeAuthModal();
  
  // Afficher le formulaire d'inscription complet avec les données Google pré-remplies
  if (typeof showProRegisterForm === 'function') {
    showProRegisterForm();
  } else if (typeof window.showProRegisterForm === 'function') {
    window.showProRegisterForm();
  }
  
  // Pré-remplir avec les données Google
  window.registerData = {
    email: userData.email || '',
    username: userData.username || userData.email?.split('@')[0]?.substring(0, 20) || '',
    password: '',
    passwordConfirm: '',
    firstName: userData.firstName || userData.first_name || '',
    lastName: userData.lastName || userData.last_name || '',
    profilePhoto: '', // Photo à ajouter dans le formulaire complet
    postalAddress: '',
    avatarId: 1,
    avatarDescription: '',
    addresses: [],
    emailVerificationCode: null,
    emailVerified: false,
    verificationAttempts: 0,
    lastVerificationAttempt: null,
    registrationAttempts: 0,
    lastRegistrationAttempt: null,
    captchaAnswer: null,
    codeSentAt: null,
    codeExpiresAt: null,
    resendCountdown: 0,
    lastResendAttempt: null
  };
  
  showNotification('⚠️ Une photo de profil est obligatoire. Veuillez compléter votre profil.', 'warning');
  
  // Nettoyer
  delete window.oauthPhotoFile;
  delete window.oauthPhotoUploadData;
};

// Exposer globalement
window.showPhotoUploadForm = showPhotoUploadForm;

function showEmailVerificationModal(email, username) {
  console.log('[EMAIL VERIFICATION] Affichage modal de vérification pour:', email);
  
  const backdrop = document.getElementById('publish-modal-backdrop');
  const modal = document.getElementById('publish-modal-inner');
  
  if (!backdrop || !modal) {
    console.error('[EMAIL VERIFICATION] Modal elements not found');
    return;
  }
  
  // Générer un code à 6 chiffres
  const verificationCode = Math.floor(100000 + Math.random() * 900000).toString();
  
  // Stocker le code temporairement (sera vérifié par le backend)
  window.pendingEmailVerification = {
    email: email,
    code: verificationCode,
    expiresAt: Date.now() + (15 * 60 * 1000) // 15 minutes
  };
  
  // Envoyer le code par email via le backend
  fetch(`${window.API_BASE_URL}/user/send-verification-code`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, code: verificationCode, username })
  }).catch(err => {
    console.warn('[EMAIL VERIFICATION] Erreur envoi code (non bloquant):', err);
    // En mode développement, afficher le code dans la console
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      console.log(`🔐 CODE DE VÉRIFICATION (DEV ONLY): ${verificationCode}`);
    }
  });
  
  // Afficher le code dans la console en développement
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log(`🔐 CODE DE VÉRIFICATION (DEV ONLY): ${verificationCode}`);
  }
  
  let codeInputs = '';
  for (let i = 0; i < 6; i++) {
    codeInputs += `
      <input 
        type="text" 
        id="email-code-digit-${i}" 
        maxlength="1" 
        class="email-code-input"
        style="width:45px;height:55px;text-align:center;font-size:24px;font-weight:700;border:2px solid rgba(255,255,255,0.2);background:rgba(15,23,42,0.5);color:#fff;border-radius:10px;transition:all 0.2s;"
        oninput="handleEmailCodeInput(${i}, event)"
        onkeydown="handleEmailCodeKeydown(${i}, event)"
        onfocus="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(15,23,42,0.8)';"
        onblur="this.style.borderColor='rgba(255,255,255,0.2)';this.style.background='rgba(15,23,42,0.5)';"
      >
    `;
  }
  
  const html = `
    <div style="padding:40px;max-width:500px;margin:0 auto;text-align:center;position:relative;">
      <!-- Bouton X (croix) pour fermer -->
      <button onclick="closeAuthModal()" style="position:absolute;top:16px;right:16px;background:none;border:none;color:var(--ui-text-muted);font-size:24px;cursor:pointer;padding:8px;width:40px;height:40px;display:flex;align-items:center;justify-content:center;border-radius:50%;transition:all 0.2s;z-index:10;" onmouseover="this.style.background='rgba(239,68,68,0.2)';this.style.color='#ef4444';this.style.transform='scale(1.1)';" onmouseout="this.style.background='none';this.style.color='var(--ui-text-muted)';this.style.transform='scale(1)';" title="Fermer">✕</button>
      
      <div style="font-size:64px;margin-bottom:20px;">📧</div>
      <h2 style="margin:0 0 12px;font-size:24px;font-weight:700;color:#fff;">Vérifiez votre email</h2>
      <p style="margin:0 0 32px;font-size:14px;color:var(--ui-text-muted);line-height:1.6;">
        Nous avons envoyé un code de vérification à 6 chiffres à<br>
        <strong style="color:#00ffc3;">${email}</strong><br><br>
        Entrez le code ci-dessous pour confirmer votre adresse email.
      </p>
      
      <div style="display:flex;justify-content:center;gap:12px;margin-bottom:24px;">
        ${codeInputs}
      </div>
      
      <div id="email-code-feedback" style="min-height:24px;margin-bottom:24px;font-size:13px;"></div>
      
      <div style="display:flex;flex-direction:column;gap:12px;">
        <button onclick="verifyEmailCode()" style="width:100%;padding:14px;border-radius:12px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:700;font-size:15px;cursor:pointer;">
          Vérifier
        </button>
        <button onclick="resendEmailVerificationCode()" style="width:100%;padding:12px;border-radius:12px;border:2px solid rgba(255,255,255,0.2);background:transparent;color:#fff;font-weight:600;font-size:14px;cursor:pointer;">
          Renvoyer le code
        </button>
        <button onclick="closeAuthModal()" style="width:100%;padding:12px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:transparent;color:var(--ui-text-muted);font-weight:600;font-size:14px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(255,255,255,0.3)';this.style.color='var(--ui-text-main)';" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)';this.style.color='var(--ui-text-muted)';">
          Annuler
        </button>
      </div>
    </div>
  `;
  
  modal.innerHTML = html;
  backdrop.style.display = 'flex';
  
  // Focus sur le premier champ
  setTimeout(() => {
    const firstInput = document.getElementById('email-code-digit-0');
    if (firstInput) firstInput.focus();
  }, 100);
}

// Gestion de la saisie du code de vérification
window.handleEmailCodeInput = function(index, event) {
  const input = event.target;
  const value = input.value.replace(/[^0-9]/g, '');
  input.value = value;
  
  if (value && index < 5) {
    const nextInput = document.getElementById(`email-code-digit-${index + 1}`);
    if (nextInput) nextInput.focus();
  }
  
  // Vérifier si tous les champs sont remplis
  checkEmailCodeComplete();
};

window.handleEmailCodeKeydown = function(index, event) {
  if (event.key === 'Backspace' && !event.target.value && index > 0) {
    const prevInput = document.getElementById(`email-code-digit-${index - 1}`);
    if (prevInput) prevInput.focus();
  }
};

function checkEmailCodeComplete() {
  let code = '';
  for (let i = 0; i < 6; i++) {
    const input = document.getElementById(`email-code-digit-${i}`);
    if (input) code += input.value;
  }
  
  if (code.length === 6) {
    verifyEmailCode(code);
  }
}

// Vérifier le code d'email
async function verifyEmailCode(providedCode) {
  if (!providedCode) {
    // Récupérer le code depuis les inputs
    let code = '';
    for (let i = 0; i < 6; i++) {
      const input = document.getElementById(`email-code-digit-${i}`);
      if (input) code += input.value;
    }
    providedCode = code;
  }
  
  if (providedCode.length !== 6) {
    showNotification('⚠️ Veuillez entrer un code à 6 chiffres', 'warning');
    return;
  }
  
  const feedbackEl = document.getElementById('email-code-feedback');
  if (feedbackEl) {
    feedbackEl.textContent = 'Vérification en cours...';
    feedbackEl.style.color = 'var(--ui-text-muted)';
  }
  
  try {
    // Vérifier le code via le backend
    const response = await fetch(`${window.API_BASE_URL}/user/verify-email`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: window.pendingEmailVerification?.email,
        code: providedCode
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      
      // Marquer l'email comme vérifié
      if (currentUser) {
        currentUser.emailVerified = true;
        safeSetItem('currentUser', JSON.stringify(currentUser));
      }
      
      // Afficher le succès
      if (feedbackEl) {
        feedbackEl.textContent = '✅ Email vérifié avec succès !';
        feedbackEl.style.color = '#22c55e';
      }
      
      // Mettre à jour les inputs en vert
      for (let i = 0; i < 6; i++) {
        const input = document.getElementById(`email-code-digit-${i}`);
        if (input) {
          input.style.borderColor = '#22c55e';
          input.style.background = 'rgba(34,197,94,0.1)';
        }
      }
      
      showNotification('✅ Email vérifié avec succès !', 'success');
      
      // Fermer le modal et mettre à jour le bloc compte
      setTimeout(() => {
        closeAuthModal();
        if (typeof updateAccountBlockLegitimately === 'function') {
          updateAccountBlockLegitimately();
        }
      }, 1000);
    } else {
      const errorData = await response.json().catch(() => ({}));
      if (feedbackEl) {
        feedbackEl.textContent = errorData.error || 'Code incorrect';
        feedbackEl.style.color = '#ef4444';
      }
      
      // Mettre à jour les inputs en rouge
      for (let i = 0; i < 6; i++) {
        const input = document.getElementById(`email-code-digit-${i}`);
        if (input) {
          input.style.borderColor = '#ef4444';
          input.style.background = 'rgba(239,68,68,0.1)';
        }
      }
      
      showNotification('❌ Code incorrect. Veuillez réessayer.', 'error');
    }
  } catch (error) {
    console.error('[EMAIL VERIFICATION] Erreur:', error);
    if (feedbackEl) {
      feedbackEl.textContent = 'Erreur de connexion. Veuillez réessayer.';
      feedbackEl.style.color = '#ef4444';
    }
    showNotification('❌ Erreur de connexion. Veuillez réessayer.', 'error');
  }
}

// Renvoyer le code de vérification
async function resendEmailVerificationCode() {
  if (!window.pendingEmailVerification) {
    showNotification('⚠️ Aucune vérification en cours', 'warning');
    return;
  }
  
  const { email } = window.pendingEmailVerification;
  const newCode = Math.floor(100000 + Math.random() * 900000).toString();
  
  window.pendingEmailVerification.code = newCode;
  window.pendingEmailVerification.expiresAt = Date.now() + (15 * 60 * 1000);
  
  try {
    await fetch(`${window.API_BASE_URL}/user/send-verification-code`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, code: newCode })
    });
    
    showNotification('✅ Code renvoyé ! Vérifiez votre boîte email.', 'success');
    
    // En mode développement, afficher le code
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      console.log(`🔐 NOUVEAU CODE DE VÉRIFICATION (DEV ONLY): ${newCode}`);
    }
  } catch (error) {
    console.error('[EMAIL VERIFICATION] Erreur renvoi code:', error);
    showNotification('⚠️ Erreur lors du renvoi du code', 'error');
  }
}

// Exposer les fonctions globalement
window.showEmailVerificationModal = showEmailVerificationModal;
window.verifyEmailCode = verifyEmailCode;
window.resendEmailVerificationCode = resendEmailVerificationCode;

function showRegisterStep1() {
  console.log('🎯 showRegisterStep1 called - REDIRECTION VERS FORMULAIRE PRO');
  // Rediriger vers le formulaire professionnel
  showProRegisterForm();
  return;
}

// Authentification sociale
function socialLogin(provider) {
  showNotification(`🔐 Connexion avec ${provider}...`, "info");
  // TODO: Implémenter l'authentification sociale réelle
  // Pour l'instant, simulation
  setTimeout(() => {
    showNotification(`✅ Connexion ${provider} bientôt disponible ! Utilisez l'inscription par email pour l'instant.`, "info");
  }, 1000);
}

function showRegisterStep2() {
  console.log('🎯 showRegisterStep2 called - starting registration step 2');
  window.registerStep = 2;
  
  // Générer la grille d'avatars
  const avatarGrid = AVAILABLE_AVATARS.map(av => `
    <div data-avatar-id="${av.id}"
         id="avatar-option-${av.id}"
         class="register-avatar-option ${window.registerData.avatarId === av.id ? 'selected' : ''}"
         title="${av.name}">
      ${av.emoji}
    </div>
  `).join('');
  
  const selectedAvatar = AVAILABLE_AVATARS.find(av => av.id === window.registerData.avatarId) || AVAILABLE_AVATARS[0];
  
  const html = `
    <div class="register-step2-container">
      <div class="register-step2-header">
        <div class="register-avatar-preview">${selectedAvatar.emoji}</div>
        <h2 class="register-step2-title">Créez votre profil</h2>
        <p class="register-step2-subtitle">Étape 2/3 - Informations & Avatar</p>

        <div class="register-step-indicator">
          <div class="register-step-dot active"></div>
          <div class="register-step-dot"></div>
          <div class="register-step-dot"></div>
        </div>
      </div>
      
      <!-- PRÉNOM ET NOM -->
      <div class="register-name-fields">
        <div class="register-field">
          <label class="register-field-label">
            Prénom <span class="register-required">*</span>
            <span id="firstname-status" class="register-field-status"></span>
          </label>
          <input type="text" id="register-firstname" placeholder="Votre prénom" required
                 value="${window.registerData.firstName}"
                 oninput="validateNameRealTime('firstname', this.value)"
                 class="register-input">
          <div id="firstname-feedback" class="register-feedback"></div>
        </div>
        <div class="register-field">
          <label class="register-field-label">
            Nom <span class="register-required">*</span>
            <span id="lastname-status" class="register-field-status"></span>
          </label>
          <input type="text" id="register-lastname" placeholder="Votre nom" required
                 value="${window.registerData.lastName}"
                 oninput="validateNameRealTime('lastname', this.value)"
                 class="register-input">
          <div id="lastname-feedback" class="register-feedback"></div>
        </div>
      </div>
      
      <!-- EMAIL AVEC VALIDATION -->
      <div class="register-field-wrapper">
        <label class="register-field-label">
          Email <span class="register-required">*</span>
          <span id="email-status" class="register-field-status"></span>
        </label>
        <input type="email" id="register-email" placeholder="votre@email.com" required
               value="${window.registerData.email}"
               oninput="validateEmailRealTime(this.value)"
               class="register-input">
        <div id="email-feedback" class="register-feedback"></div>
      </div>
      
      <!-- USERNAME AVEC VALIDATION -->
      <div class="register-field-wrapper">
        <label class="register-field-label">
          Nom d'utilisateur <span class="register-required">*</span>
          <span id="username-status" class="register-field-status"></span>
        </label>
        <input type="text" id="register-username" placeholder="Votre pseudo (3-20 caractères)" required
               value="${window.registerData.username}"
               oninput="validateUsernameRealTime(this.value)"
               class="register-input">
        <div id="username-feedback" class="register-feedback"></div>
      </div>
      
      <!-- MOT DE PASSE AVEC INDICATEUR DE FORCE -->
      <div class="register-field-wrapper">
        <label class="register-field-label">
          Mot de passe <span class="register-required">*</span>
          <span id="password-strength-label" class="register-field-status"></span>
        </label>
        <div class="register-password-container">
          <input type="password" id="register-password" placeholder="Minimum 8 caractères" required
                 value="${window.registerData.password}"
                 oninput="checkPasswordStrength(this.value)"
                 class="register-input register-password-input">
          <button type="button" onclick="togglePasswordVisibility()" class="register-password-toggle">👁️</button>
        </div>
        <!-- BARRE DE FORCE DU MOT DE PASSE -->
        <div id="password-strength-bar" class="register-password-strength-bar">
          <div id="password-strength-fill" class="register-password-strength-fill"></div>
        </div>
        <div id="password-feedback" class="register-feedback"></div>
        <div id="password-requirements" class="register-password-requirements">
          <div id="req-length" class="register-password-req">✓ Au moins 8 caractères</div>
          <div id="req-upper" class="register-password-req">✓ Une majuscule</div>
          <div id="req-lower" class="register-password-req">✓ Une minuscule</div>
          <div id="req-number" class="register-password-req">✓ Un chiffre</div>
          <div id="req-special" class="register-password-req">✓ Un caractère spécial (!@#$%^&*)</div>
        </div>
      </div>
      
      <!-- CHOIX D'AVATAR -->
      <div class="register-field-wrapper">
        <label class="register-field-label">
          Choisissez votre avatar <span class="register-required">*</span>
          <span class="register-avatar-name">(${selectedAvatar.name})</span>
        </label>
        <div class="register-avatar-grid">
          ${avatarGrid}
        </div>
      </div>
      
      <!-- DESCRIPTION AVATAR (optionnel) -->
      <div class="register-field-wrapper">
        <label class="register-field-label">
          Description de votre avatar <span class="register-optional">(optionnel)</span>
        </label>
        <textarea id="register-avatar-desc" placeholder="Ex: Fan de techno, toujours partant pour les festivals !" maxlength="150"
                  oninput="document.getElementById('avatar-desc-count').textContent = this.value.length + '/150'"
                  class="register-textarea">${window.registerData.avatarDescription || ''}</textarea>
        <div class="register-textarea-counter">
          <span id="avatar-desc-count">${(window.registerData.avatarDescription || '').length}/150</span>
        </div>
      </div>
      
      <!-- ACCEPTATION CGU/RGPD -->
      <div class="register-terms-container">
        <label class="register-terms-label">
          <input type="checkbox" id="accept-terms" class="register-terms-checkbox">
          <div class="register-terms-text">
            J'accepte les <a href="#" onclick="showTermsModal();return false;" class="register-terms-link">Conditions d'utilisation</a>
            et la <a href="#" onclick="showPrivacyModal();return false;" class="register-terms-link">Politique de confidentialité</a> <span class="register-required">*</span>
          </div>
        </label>
      </div>
      
      <div class="register-step-buttons">
        <button onclick="showRegisterStep1()" class="register-btn-secondary">
          ← Précédent
        </button>
        <button onclick="validateStep2()" class="register-btn-primary">
          Suivant →
        </button>
      </div>
    </div>
  `;
  
  console.log('🎯 showRegisterStep2 - setting HTML, length:', html.length);
  document.getElementById("publish-modal-inner").innerHTML = html;
  const backdrop = document.getElementById("publish-modal-backdrop");
  if (backdrop) {
    backdrop.setAttribute('data-auth-modal', 'true');
    backdrop.style.display = "flex";
    backdrop.style.paddingTop = "40px";
    backdrop.style.paddingBottom = "40px";
    backdrop.style.boxSizing = "border-box";
    backdrop.style.paddingTop = "40px";
    backdrop.style.paddingBottom = "40px";
    backdrop.style.boxSizing = "border-box";
  }
  console.log('🎯 showRegisterStep2 - HTML set successfully and modal displayed');

  // Attacher les event listeners pour les avatars (éviter CSP)
  AVAILABLE_AVATARS.forEach(av => {
    const avatarEl = document.getElementById(`avatar-option-${av.id}`);
    if (avatarEl) {
      avatarEl.addEventListener('click', () => selectAvatar(av.id));
      avatarEl.addEventListener('mouseover', function() {
        this.classList.add('hover');
      });
      avatarEl.addEventListener('mouseout', function() {
        this.classList.remove('hover');
      });
    }
  });

  // Attacher les event listeners pour la liaison temps réel avec registerData
  const firstnameInput = document.getElementById('register-firstname');
  const lastnameInput = document.getElementById('register-lastname');
  const emailInput = document.getElementById('register-email');
  const usernameInput = document.getElementById('register-username');
  const passwordInput = document.getElementById('register-password');
  const avatarDescInput = document.getElementById('register-avatar-desc');

  if (firstnameInput) firstnameInput.addEventListener('input', (e) => window.registerData.firstName = e.target.value);
  if (lastnameInput) lastnameInput.addEventListener('input', (e) => window.registerData.lastName = e.target.value);
  if (emailInput) {
    emailInput.addEventListener('input', (e) => window.registerData.email = e.target.value);
  }
  if (usernameInput) usernameInput.addEventListener('input', (e) => window.registerData.username = e.target.value);
  if (passwordInput) passwordInput.addEventListener('input', (e) => window.registerData.password = e.target.value);
  if (avatarDescInput) avatarDescInput.addEventListener('input', (e) => window.registerData.avatarDescription = e.target.value);
  
  // Initialiser les validations
  if (window.registerData.firstName) validateNameRealTime('firstname', window.registerData.firstName);
  if (window.registerData.lastName) validateNameRealTime('lastname', window.registerData.lastName);
  if (window.registerData.email) validateEmailRealTime(window.registerData.email);
  if (window.registerData.username) validateUsernameRealTime(window.registerData.username);
  if (window.registerData.password) checkPasswordStrength(window.registerData.password);

  console.log('✅ showRegisterStep2 completed successfully');
}

// Sélectionner un avatar
function selectAvatar(avatarId) {
  // IMPORTANT: Sauvegarder les valeurs actuelles du formulaire AVANT de régénérer
  const currentFormValues = {
    firstName: document.getElementById('register-firstname')?.value || window.registerData.firstName || '',
    lastName: document.getElementById('register-lastname')?.value || window.registerData.lastName || '',
    email: document.getElementById('register-email')?.value || window.registerData.email || '',
    username: document.getElementById('register-username')?.value || window.registerData.username || '',
    password: document.getElementById('register-password')?.value || window.registerData.password || '',
    avatarDescription: document.getElementById('register-avatar-desc')?.value || window.registerData.avatarDescription || ''
  };

  // Mettre à jour registerData avec les valeurs actuelles du formulaire
  window.registerData.firstName = currentFormValues.firstName;
  window.registerData.lastName = currentFormValues.lastName;
  window.registerData.email = currentFormValues.email;
  window.registerData.username = currentFormValues.username;
  window.registerData.password = currentFormValues.password;
  window.registerData.avatarDescription = currentFormValues.avatarDescription;

  // Mettre à jour l'avatarId
  window.registerData.avatarId = avatarId;

  // Rafraîchir l'affichage
  showRegisterStep2();
}

// VALIDATION EN TEMPS RÉEL
function validateEmailRealTime(email) {
  const emailInput = document.getElementById("register-email");
  const statusEl = document.getElementById("email-status");
  const feedbackEl = document.getElementById("email-feedback");
  
  if (!email || email.trim() === '') {
    if (statusEl) statusEl.textContent = '';
    if (feedbackEl) feedbackEl.textContent = '';
    if (emailInput) emailInput.style.borderColor = 'var(--ui-card-border)';
    return false;
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const isValid = emailRegex.test(email);
  
  if (statusEl) {
    statusEl.textContent = isValid ? '✅' : '❌';
    statusEl.style.color = isValid ? '#22c55e' : '#ef4444';
  }
  
  if (feedbackEl) {
    if (isValid) {
      feedbackEl.textContent = '';
      feedbackEl.style.color = '#22c55e';
    } else {
      feedbackEl.textContent = 'Format d\'email invalide';
      feedbackEl.style.color = '#ef4444';
    }
  }
  
  if (emailInput) {
    emailInput.style.borderColor = isValid ? '#22c55e' : '#ef4444';
  }
  
  return isValid;
}

function validateUsernameRealTime(username) {
  const usernameInput = document.getElementById("register-username");
  const statusEl = document.getElementById("username-status");
  const feedbackEl = document.getElementById("username-feedback");
  
  if (!username || username.trim() === '') {
    if (statusEl) statusEl.textContent = '';
    if (feedbackEl) feedbackEl.textContent = '';
    if (usernameInput) usernameInput.style.borderColor = 'var(--ui-card-border)';
    return false;
  }
  
  const usernameRegex = /^[a-zA-Z0-9_-]{3,20}$/;
  const isValid = usernameRegex.test(username);
  
  if (statusEl) {
    statusEl.textContent = isValid ? '✅' : '❌';
    statusEl.style.color = isValid ? '#22c55e' : '#ef4444';
  }
  
  if (feedbackEl) {
    if (isValid) {
      feedbackEl.textContent = '';
      feedbackEl.style.color = '#22c55e';
    } else {
      if (username.length < 3) {
        feedbackEl.textContent = 'Minimum 3 caractères';
      } else if (username.length > 20) {
        feedbackEl.textContent = 'Maximum 20 caractères';
      } else {
        feedbackEl.textContent = 'Caractères autorisés : lettres, chiffres, _ et -';
      }
      feedbackEl.style.color = '#ef4444';
    }
  }
  
  if (usernameInput) {
    usernameInput.style.borderColor = isValid ? '#22c55e' : '#ef4444';
  }
  
  return isValid;
}

function checkPasswordStrength(password) {
  const passwordInput = document.getElementById("register-password");
  const strengthBar = document.getElementById("password-strength-fill");
  const strengthLabel = document.getElementById("password-strength-label");
  const feedbackEl = document.getElementById("password-feedback");
  const requirements = {
    length: document.getElementById("req-length"),
    upper: document.getElementById("req-upper"),
    lower: document.getElementById("req-lower"),
    number: document.getElementById("req-number"),
    special: document.getElementById("req-special")
  };
  
  if (!password || password.length === 0) {
    if (strengthBar) strengthBar.style.width = '0%';
    if (strengthLabel) strengthLabel.textContent = '';
    if (feedbackEl) feedbackEl.textContent = '';
    Object.values(requirements).forEach(el => {
      if (el) el.style.color = 'var(--ui-text-muted)';
    });
    if (passwordInput) passwordInput.style.borderColor = 'var(--ui-card-border)';
    return 0;
  }
  
  // Vérifier les critères
  const hasLength = password.length >= 8;
  const hasUpper = /[A-Z]/.test(password);
  const hasLower = /[a-z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);
  
  // Mettre à jour les indicateurs de critères
  if (requirements.length) requirements.length.style.color = hasLength ? '#22c55e' : 'var(--ui-text-muted)';
  if (requirements.upper) requirements.upper.style.color = hasUpper ? '#22c55e' : 'var(--ui-text-muted)';
  if (requirements.lower) requirements.lower.style.color = hasLower ? '#22c55e' : 'var(--ui-text-muted)';
  if (requirements.number) requirements.number.style.color = hasNumber ? '#22c55e' : 'var(--ui-text-muted)';
  if (requirements.special) requirements.special.style.color = hasSpecial ? '#22c55e' : 'var(--ui-text-muted)';
  
  // Calculer la force (0-100)
  const criteriaMet = [hasLength, hasUpper, hasLower, hasNumber, hasSpecial].filter(Boolean).length;
  const strength = (criteriaMet / 5) * 100;
  
  // Déterminer le niveau de force
  let strengthText = '';
  let strengthColor = '#ef4444';
  
  if (strength < 40) {
    strengthText = 'Faible';
    strengthColor = '#ef4444';
  } else if (strength < 60) {
    strengthText = 'Moyen';
    strengthColor = '#f59e0b';
  } else if (strength < 80) {
    strengthText = 'Fort';
    strengthColor = '#3b82f6';
  } else {
    strengthText = 'Très fort';
    strengthColor = '#22c55e';
  }
  
  // Mettre à jour la barre et le label
  if (strengthBar) {
    strengthBar.style.width = strength + '%';
    strengthBar.style.background = strengthColor;
  }
  
  if (strengthLabel) {
    strengthLabel.textContent = strengthText;
    strengthLabel.style.color = strengthColor;
  }
  
  if (feedbackEl) {
    feedbackEl.textContent = `${criteriaMet}/5 critères remplis`;
    feedbackEl.style.color = strengthColor;
  }
  
  if (passwordInput) {
    passwordInput.style.borderColor = strength >= 60 ? '#22c55e' : strength >= 40 ? '#f59e0b' : '#ef4444';
  }
  
  return strength;
}

function togglePasswordVisibility() {
  const passwordInput = document.getElementById("register-password");
  if (!passwordInput) return;
  
  if (passwordInput.type === 'password') {
    passwordInput.type = 'text';
  } else {
    passwordInput.type = 'password';
  }
}

// Validation du nom/prénom en temps réel
function validateNameRealTime(type, value) {
  const inputId = type === 'firstname' ? 'register-firstname' : 'register-lastname';
  const statusId = type === 'firstname' ? 'firstname-status' : 'lastname-status';
  const feedbackId = type === 'firstname' ? 'firstname-feedback' : 'lastname-feedback';
  
  const nameInput = document.getElementById(inputId);
  const statusEl = document.getElementById(statusId);
  const feedbackEl = document.getElementById(feedbackId);
  
  if (!value || value.trim() === '') {
    if (statusEl) statusEl.textContent = '';
    if (feedbackEl) feedbackEl.textContent = '';
    if (nameInput) nameInput.style.borderColor = 'var(--ui-card-border)';
    return false;
  }
  
  const trimmed = value.trim();
  
  // Vérifier que ce n'est pas juste des caractères aléatoires
  // Un nom/prénom valide doit avoir au moins 2 caractères et contenir principalement des lettres
  const nameRegex = /^[a-zA-ZàáâäãåèéêëìíîïòóôöõùúûüýÿñçÀÁÂÄÃÅÈÉÊËÌÍÎÏÒÓÔÖÕÙÚÛÜÝŸÑÇ\s-]{2,30}$/;
  const isValid = nameRegex.test(trimmed) && trimmed.length >= 2 && trimmed.length <= 30;
  
  // Vérifier qu'il n'y a pas trop de caractères spéciaux ou de chiffres
  const hasTooManyNumbers = (trimmed.match(/\d/g) || []).length > trimmed.length * 0.1; // Max 10% de chiffres
  const hasTooManySpecial = (trimmed.match(/[^a-zA-ZàáâäãåèéêëìíîïòóôöõùúûüýÿñçÀÁÂÄÃÅÈÉÊËÌÍÎÏÒÓÔÖÕÙÚÛÜÝŸÑÇ\s-]/g) || []).length > 0;
  
  // Vérifier qu'il y a au moins une majuscule (nom propre)
  const hasCapital = /[A-ZÀÁÂÄÃÅÈÉÊËÌÍÎÏÒÓÔÖÕÙÚÛÜÝŸÑÇ]/.test(trimmed);
  
  // Vérifier que c'est principalement des lettres (au moins 70%)
  const letterCount = (trimmed.match(/[a-zA-ZàáâäãåèéêëìíîïòóôöõùúûüýÿñçÀÁÂÄÃÅÈÉÊËÌÍÎÏÒÓÔÖÕÙÚÛÜÝŸÑÇ]/g) || []).length;
  const isMostlyLetters = letterCount >= trimmed.length * 0.7;
  
  const finalValid = isValid && !hasTooManyNumbers && !hasTooManySpecial && hasCapital && isMostlyLetters;
  
  if (statusEl) {
    statusEl.textContent = finalValid ? '✅' : '❌';
    statusEl.style.color = finalValid ? '#22c55e' : '#ef4444';
  }
  
  if (feedbackEl) {
    if (finalValid) {
      feedbackEl.textContent = '';
      feedbackEl.style.color = '#22c55e';
    } else {
      if (trimmed.length < 2) {
        feedbackEl.textContent = 'Minimum 2 caractères';
      } else if (trimmed.length > 30) {
        feedbackEl.textContent = 'Maximum 30 caractères';
      } else if (!hasCapital) {
        feedbackEl.textContent = 'Doit commencer par une majuscule';
      } else if (hasTooManyNumbers) {
        feedbackEl.textContent = 'Un nom ne doit pas contenir de chiffres';
      } else if (hasTooManySpecial) {
        feedbackEl.textContent = 'Caractères spéciaux non autorisés';
      } else if (!isMostlyLetters) {
        feedbackEl.textContent = 'Doit contenir principalement des lettres';
      } else {
        feedbackEl.textContent = 'Format invalide';
      }
      feedbackEl.style.color = '#ef4444';
    }
  }
  
  if (nameInput) {
    nameInput.style.borderColor = finalValid ? '#22c55e' : '#ef4444';
  }
  
  return finalValid;
}

async function validateStep2() {
  const firstName = document.getElementById("register-firstname")?.value.trim();
  const lastName = document.getElementById("register-lastname")?.value.trim();
  const email = document.getElementById("register-email")?.value.trim();
  const username = document.getElementById("register-username")?.value.trim();
  const password = document.getElementById("register-password")?.value;
  const avatarDesc = document.getElementById("register-avatar-desc")?.value.trim() || '';
  const acceptTerms = document.getElementById("accept-terms")?.checked;
  
  // Validation prénom
  if (!firstName || !validateNameRealTime('firstname', firstName)) {
    showNotification("⚠️ Veuillez entrer un prénom valide (2-30 caractères, lettres uniquement)", "warning");
    return;
  }
  
  // Validation nom
  if (!lastName || !validateNameRealTime('lastname', lastName)) {
    showNotification("⚠️ Veuillez entrer un nom valide (2-30 caractères, lettres uniquement)", "warning");
    return;
  }
  
  // Validation email
  if (!email || !validateEmailRealTime(email)) {
    showNotification("⚠️ Veuillez entrer une adresse email valide", "warning");
    return;
  }
  
  // Validation username
  if (!username || !validateUsernameRealTime(username)) {
    showNotification("⚠️ Le nom d'utilisateur doit contenir 3-20 caractères (lettres, chiffres, _ et -)", "warning");
    return;
  }
  
  // Validation mot de passe
  if (!password) {
    showNotification("⚠️ Veuillez entrer un mot de passe", "warning");
    return;
  }
  
  const passwordStrength = checkPasswordStrength(password);
  if (passwordStrength < 40) {
    showNotification("⚠️ Le mot de passe est trop faible. Veuillez renforcer votre mot de passe.", "warning");
    return;
  }
  
  // Validation avatar
  if (!window.registerData.avatarId) {
    showNotification("⚠️ Veuillez choisir un avatar", "warning");
    return;
  }
  
  // Validation CGU
  if (!acceptTerms) {
    showNotification("⚠️ Vous devez accepter les Conditions d'utilisation et la Politique de confidentialité", "warning");
    return;
  }
  
  // Vérifier le rate limiting
  const now = Date.now();
  if (window.registerData.lastRegistrationAttempt && (now - window.registerData.lastRegistrationAttempt) < 60000) {
    const remainingSeconds = Math.ceil((60000 - (now - window.registerData.lastRegistrationAttempt)) / 1000);
    showNotification(`⏱️ Veuillez patienter ${remainingSeconds} secondes avant de réessayer`, "warning");
    return;
  }
  
  window.registerData.firstName = firstName;
  window.registerData.lastName = lastName;
  window.registerData.email = email;
  window.registerData.username = username;
  window.registerData.password = password;
  window.registerData.avatarDescription = avatarDesc;
  window.registerData.lastRegistrationAttempt = now;
  window.registerData.registrationAttempts++;
  
  // Vérifier si l'email existe déjà
  try {
    const checkResponse = await fetch(`${window.API_BASE_URL}/user/check-email`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email })
    });
    
    if (checkResponse.ok) {
      const checkData = await checkResponse.json();
      if (checkData.exists) {
        showNotification("⚠️ Cet email est déjà utilisé. Veuillez vous connecter ou utiliser un autre email.", "warning");
        return;
      }
    }
  } catch (error) {
    console.error('Erreur vérification email:', error);
    // Continuer même si la vérification échoue
  }
  
  // Passer à l'étape de vérification d'email
  showRegisterStep2_5();
}

// ÉTAPE 2.5 : VÉRIFICATION D'EMAIL
function showRegisterStep2_5() {
  window.registerStep = 2.5;
  
  // Générer et envoyer le code si pas déjà fait
  if (!window.window.registerData.emailVerificationCode) {
    sendVerificationCode();
  }
  
  const maskedEmail = window.registerData.email.replace(/(.{2})(.*)(@.*)/, '$1***$3');
  let countdown = window.registerData.resendCountdown || 0;
  
  const html = `
    <div style="padding:24px;max-width:550px;margin:0 auto;max-height:85vh;overflow-y:auto;animation:fadeIn 0.3s ease-in;">
      <div style="text-align:center;margin-bottom:28px;">
        <div style="font-size:64px;margin-bottom:16px;animation:scaleIn 0.4s ease-out;">📧</div>
        <h2 style="margin:0;font-size:24px;font-weight:700;color:#fff;">Vérifiez votre email</h2>
        <p style="color:var(--ui-text-muted);margin-top:12px;font-size:15px;line-height:1.6;">
          Nous avons envoyé un code de vérification à 6 chiffres à<br>
          <strong style="color:#fff;">${maskedEmail}</strong>
        </p>
        <div style="display:flex;justify-content:center;gap:8px;margin-top:20px;">
          <div style="width:60px;height:4px;background:var(--ui-card-border);border-radius:2px;"></div>
          <div style="width:60px;height:4px;background:linear-gradient(135deg,#3b82f6,#2563eb);border-radius:2px;"></div>
          <div style="width:60px;height:4px;background:var(--ui-card-border);border-radius:2px;"></div>
        </div>
      </div>
      
      <!-- CAPTCHA SIMPLE -->
      <div id="captcha-container" style="margin-bottom:20px;padding:16px;background:rgba(59,130,246,0.1);border-radius:12px;border:1px solid rgba(59,130,246,0.3);">
        <div style="font-size:13px;font-weight:600;color:#3b82f6;margin-bottom:12px;">🔒 Vérification anti-spam</div>
        <div id="captcha-question" style="font-size:14px;color:var(--ui-text-main);margin-bottom:12px;"></div>
        <input type="text" id="captcha-answer" placeholder="Votre réponse" 
               style="width:100%;padding:12px;border-radius:8px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:15px;">
        <div id="captcha-feedback" style="margin-top:8px;font-size:12px;"></div>
      </div>
      
      <!-- CODE DE VÉRIFICATION -->
      <div style="margin-bottom:24px;">
        <label style="display:block;font-size:14px;font-weight:600;color:#fff;margin-bottom:12px;text-align:center;">
          Code de vérification <span style="color:#ef4444;">*</span>
        </label>
        <div style="display:flex;justify-content:center;gap:8px;margin-bottom:12px;">
          ${[0,1,2,3,4,5].map(i => `
            <input type="text" 
                   id="code-digit-${i}" 
                   maxlength="1" 
                   pattern="[0-9]"
                   oninput="handleCodeInput(${i}, this.value)"
                   onkeydown="handleCodeKeydown(${i}, event)"
                   style="width:50px;height:60px;text-align:center;font-size:28px;font-weight:700;border-radius:10px;border:2px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:#fff;transition:all 0.2s;"
                   onfocus="this.style.borderColor='#3b82f6';this.style.boxShadow='0 0 0 3px rgba(59,130,246,0.2)'"
                   onblur="this.style.borderColor='var(--ui-card-border)';this.style.boxShadow='none'">
          `).join('')}
        </div>
        <div id="code-feedback" style="text-align:center;font-size:13px;margin-top:12px;"></div>
        <div id="code-attempts" style="text-align:center;font-size:12px;color:var(--ui-text-muted);margin-top:8px;"></div>
      </div>
      
      <!-- BOUTON RENVOYER -->
      <div style="text-align:center;margin-bottom:24px;">
        <button id="resend-button" onclick="resendVerificationCode()" 
                style="padding:10px 20px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-size:13px;transition:all 0.2s;"
                onmouseover="this.style.background='rgba(15,23,42,0.5)'" 
                onmouseout="this.style.background='transparent'">
          📨 Renvoyer le code
        </button>
        <div id="resend-countdown" style="margin-top:8px;font-size:12px;color:var(--ui-text-muted);"></div>
      </div>
      
      <!-- MESSAGE D'INFORMATION -->
      <div style="background:rgba(0,255,195,0.1);border:1px solid rgba(0,255,195,0.3);border-radius:12px;padding:16px;margin-bottom:24px;">
        <div style="font-size:12px;color:var(--ui-text-muted);line-height:1.6;">
          <strong style="color:#00ffc3;">💡 Astuce :</strong> Vérifiez votre dossier spam si vous ne recevez pas l'email dans les 2 minutes.
          <br><br>
          Le code expire dans <strong style="color:#fff;">15 minutes</strong>.
        </div>
      </div>
      
      <div style="display:flex;gap:12px;">
        <button onclick="showRegisterStep2()" style="flex:1;padding:14px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-weight:600;transition:all 0.2s;" onmouseover="this.style.background='rgba(15,23,42,0.5)'" onmouseout="this.style.background='transparent'">
          ← Précédent
        </button>
        <button onclick="verifyEmailCode()" style="flex:1;padding:14px;border-radius:999px;border:none;background:linear-gradient(135deg,#22c55e,#16a34a);color:#fff;font-weight:700;cursor:pointer;box-shadow:0 4px 15px rgba(34,197,94,0.4);transition:all 0.2s;" onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 6px 20px rgba(34,197,94,0.6)'" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 4px 15px rgba(34,197,94,0.4)'">
          Vérifier →
        </button>
      </div>
    </div>
    <style>
      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }
      @keyframes scaleIn {
        from { transform: scale(0.8); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
      }
    </style>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
  
  // Générer un CAPTCHA simple
  generateCaptcha();
  
  // Focus sur le premier champ de code
  setTimeout(() => {
    const firstInput = document.getElementById("code-digit-0");
    if (firstInput) firstInput.focus();
  }, 100);
  
  // Mettre à jour le compteur de tentatives
  updateCodeAttemptsDisplay();
  
  // Démarrer le countdown pour le renvoi
  if (countdown > 0) {
    startResendCountdown(countdown);
  }
}

// Générer un CAPTCHA simple
function generateCaptcha() {
  const num1 = Math.floor(Math.random() * 10) + 1;
  const num2 = Math.floor(Math.random() * 10) + 1;
  const operators = ['+', '-', '×'];
  const operator = operators[Math.floor(Math.random() * operators.length)];
  
  let question = '';
  let answer = 0;
  
  if (operator === '+') {
    question = `${num1} + ${num2} = ?`;
    answer = num1 + num2;
  } else if (operator === '-') {
    question = `${num1} - ${num2} = ?`;
    answer = num1 - num2;
  } else {
    question = `${num1} × ${num2} = ?`;
    answer = num1 * num2;
  }
  
  window.registerData.captchaAnswer = answer;
  
  const questionEl = document.getElementById("captcha-question");
  if (questionEl) {
    questionEl.textContent = question;
  }
}

// Gérer la saisie du code
function handleCodeInput(index, value) {
  if (!/^\d$/.test(value) && value !== '') return;
  
  const currentInput = document.getElementById(`code-digit-${index}`);
  if (currentInput && value) {
    currentInput.value = value;
    currentInput.style.borderColor = '#3b82f6';
    
    // Passer au champ suivant
    if (index < 5) {
      const nextInput = document.getElementById(`code-digit-${index + 1}`);
      if (nextInput) {
        nextInput.focus();
      }
    }
  }
  
  // Vérifier si tous les champs sont remplis
  checkCodeComplete();
}

function handleCodeKeydown(index, event) {
  if (event.key === 'Backspace' && !event.target.value && index > 0) {
    const prevInput = document.getElementById(`code-digit-${index - 1}`);
    if (prevInput) {
      prevInput.focus();
      prevInput.value = '';
    }
  }
}

function checkCodeComplete() {
  let code = '';
  for (let i = 0; i < 6; i++) {
    const input = document.getElementById(`code-digit-${i}`);
    if (input && input.value) {
      code += input.value;
    } else {
      return false;
    }
  }
  
  // Auto-vérification si le code est complet
  if (code.length === 6) {
    verifyEmailCode(code);
  }
  
  return true;
}

// Envoyer le code de vérification
async function sendVerificationCode() {
  try {
    showNotification("📧 Envoi du code de vérification...", "info");
    
    // Générer un code à 6 chiffres
    const code = Math.floor(100000 + Math.random() * 900000).toString();
    window.window.registerData.emailVerificationCode = code;
    window.registerData.codeSentAt = Date.now();
    window.registerData.codeExpiresAt = Date.now() + (15 * 60 * 1000); // 15 minutes
    
    // Envoyer via le backend
    const response = await fetch(`${window.API_BASE_URL}/user/send-verification-code`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: window.registerData.email,
        code: code,
        username: window.registerData.username
      })
    });
    
    if (response.ok) {
      showNotification("✅ Code envoyé ! Vérifiez votre boîte email.", "success");
      
      // En mode développement, afficher le code dans la console
      if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.log(`🔐 CODE DE VÉRIFICATION (DEV ONLY): ${code}`);
      }
    } else {
      // En cas d'erreur backend, utiliser le code généré localement
      console.warn('Backend non disponible, utilisation du code local');
      showNotification("✅ Code généré ! (Mode développement)", "success");
      console.log(`🔐 CODE DE VÉRIFICATION (DEV ONLY): ${code}`);
    }
  } catch (error) {
    console.error('Erreur envoi code:', error);
    // En cas d'erreur, générer quand même un code pour le développement
    const code = Math.floor(100000 + Math.random() * 900000).toString();
    window.window.registerData.emailVerificationCode = code;
    window.registerData.codeSentAt = Date.now();
    window.registerData.codeExpiresAt = Date.now() + (15 * 60 * 1000);
    showNotification("✅ Code généré ! (Mode développement - vérifiez la console)", "info");
    console.log(`🔐 CODE DE VÉRIFICATION (DEV ONLY): ${code}`);
  }
}

// Renvoyer le code
async function resendVerificationCode() {
  const now = Date.now();
  const lastResend = window.registerData.lastResendAttempt || 0;
  
  // Rate limiting : 60 secondes entre chaque renvoi
  if (now - lastResend < 60000) {
    const remaining = Math.ceil((60000 - (now - lastResend)) / 1000);
    showNotification(`⏱️ Veuillez patienter ${remaining} secondes avant de renvoyer`, "warning");
    return;
  }
  
  window.registerData.lastResendAttempt = now;
  window.window.registerData.emailVerificationCode = null; // Réinitialiser
  
  await sendVerificationCode();
  
  // Démarrer le countdown
  window.registerData.resendCountdown = 60;
  startResendCountdown(60);
}

function startResendCountdown(seconds) {
  const resendButton = document.getElementById("resend-button");
  const countdownEl = document.getElementById("resend-countdown");
  
  if (!resendButton || !countdownEl) return;
  
  resendButton.disabled = true;
  resendButton.style.opacity = '0.5';
  resendButton.style.cursor = 'not-allowed';
  
  let remaining = seconds;
  
  const interval = setInterval(() => {
    remaining--;
    window.registerData.resendCountdown = remaining;
    
    if (countdownEl) {
      countdownEl.textContent = `Vous pourrez renvoyer dans ${remaining} secondes`;
    }
    
    if (remaining <= 0) {
      clearInterval(interval);
      resendButton.disabled = false;
      resendButton.style.opacity = '1';
      resendButton.style.cursor = 'pointer';
      if (countdownEl) countdownEl.textContent = '';
      window.registerData.resendCountdown = 0;
    }
  }, 1000);
}

// Vérifier le code
async function verifyEmailCode(providedCode) {
  // Vérifier le CAPTCHA d'abord
  const captchaInput = document.getElementById("captcha-answer");
  const captchaFeedback = document.getElementById("captcha-feedback");
  
  if (!captchaInput || !captchaInput.value) {
    if (captchaFeedback) {
      captchaFeedback.textContent = "⚠️ Veuillez répondre au CAPTCHA";
      captchaFeedback.style.color = "#ef4444";
    }
    return;
  }
  
  const captchaAnswer = parseInt(captchaInput.value.trim());
  if (captchaAnswer !== window.registerData.captchaAnswer) {
    if (captchaFeedback) {
      captchaFeedback.textContent = "❌ Réponse incorrecte";
      captchaFeedback.style.color = "#ef4444";
    }
    generateCaptcha(); // Régénérer le CAPTCHA
    captchaInput.value = '';
    return;
  }
  
  if (captchaFeedback) {
    captchaFeedback.textContent = "✅ CAPTCHA correct";
    captchaFeedback.style.color = "#22c55e";
  }
  
  // Récupérer le code saisi
  if (!providedCode) {
    providedCode = '';
    for (let i = 0; i < 6; i++) {
      const input = document.getElementById(`code-digit-${i}`);
      if (input) {
        providedCode += input.value || '';
      }
    }
  }
  
  if (providedCode.length !== 6) {
    const feedbackEl = document.getElementById("code-feedback");
    if (feedbackEl) {
      feedbackEl.textContent = "⚠️ Veuillez entrer les 6 chiffres";
      feedbackEl.style.color = "#ef4444";
    }
    return;
  }
  
  // Vérifier le rate limiting
  const now = Date.now();
  if (window.registerData.lastVerificationAttempt) {
    const timeSinceLastAttempt = now - window.registerData.lastVerificationAttempt;
    if (timeSinceLastAttempt < 2000) { // 2 secondes entre chaque tentative
      showNotification("⏱️ Veuillez patienter avant de réessayer", "warning");
      return;
    }
  }
  
  window.registerData.lastVerificationAttempt = now;
  window.registerData.verificationAttempts++;
  
  // Vérifier si le code a expiré
  if (window.registerData.codeExpiresAt && now > window.registerData.codeExpiresAt) {
    showNotification("⏰ Le code a expiré. Veuillez en demander un nouveau.", "warning");
    window.window.registerData.emailVerificationCode = null;
    return;
  }
  
  // Vérifier le code
  if (providedCode === window.window.registerData.emailVerificationCode) {
    window.window.registerData.emailVerified = true;
    
    // Mettre à jour l'affichage
    for (let i = 0; i < 6; i++) {
      const input = document.getElementById(`code-digit-${i}`);
      if (input) {
        input.style.borderColor = '#22c55e';
        input.style.background = 'rgba(34,197,94,0.1)';
      }
    }
    
    const feedbackEl = document.getElementById("code-feedback");
    if (feedbackEl) {
      feedbackEl.textContent = "✅ Code vérifié avec succès !";
      feedbackEl.style.color = "#22c55e";
    }
    
    showNotification("✅ Email vérifié !", "success");
    
    // Passer à l'étape suivante après un court délai
    setTimeout(() => {
      showRegisterStep3();
    }, 1000);
  } else {
    // Code incorrect
    window.registerData.verificationAttempts++;
    
    // Bloquer après 5 tentatives
    if (window.registerData.verificationAttempts >= 5) {
      showNotification("🚫 Trop de tentatives échouées. Veuillez renvoyer un nouveau code.", "error");
      window.window.registerData.emailVerificationCode = null;
      window.registerData.verificationAttempts = 0;
      showRegisterStep2_5();
      return;
    }
    
    // Afficher l'erreur
    const feedbackEl = document.getElementById("code-feedback");
    if (feedbackEl) {
      feedbackEl.textContent = `❌ Code incorrect (${window.registerData.verificationAttempts}/5 tentatives)`;
      feedbackEl.style.color = "#ef4444";
    }
    
    // Effacer les champs
    for (let i = 0; i < 6; i++) {
      const input = document.getElementById(`code-digit-${i}`);
      if (input) {
        input.value = '';
        input.style.borderColor = '#ef4444';
        setTimeout(() => {
          input.style.borderColor = 'var(--ui-card-border)';
        }, 1000);
      }
    }
    
    // Focus sur le premier champ
    const firstInput = document.getElementById("code-digit-0");
    if (firstInput) firstInput.focus();
    
    updateCodeAttemptsDisplay();
  }
}

function updateCodeAttemptsDisplay() {
  const attemptsEl = document.getElementById("code-attempts");
  if (attemptsEl && window.registerData.verificationAttempts > 0) {
    attemptsEl.textContent = `${window.registerData.verificationAttempts}/5 tentatives utilisées`;
    attemptsEl.style.color = window.registerData.verificationAttempts >= 3 ? "#ef4444" : "var(--ui-text-muted)";
  }
}

function showRegisterStep3() {
  window.registerStep = 3;
  const addressCount = window.window.registerData.addresses.length || 1;
  
  // S'assurer qu'il y a au moins un champ d'adresse
  if (window.registerData.addresses.length === 0) {
    window.registerData.addresses = [{ address: '', city: '', lat: null, lng: null, isPrimary: true }];
  }
  
  const html = `
    <div style="padding:20px;max-width:600px;margin:0 auto;max-height:80vh;overflow-y:auto;">
      <div style="text-align:center;margin-bottom:24px;">
        <div style="font-size:32px;margin-bottom:8px;">📍</div>
        <h2 style="margin:0;font-size:22px;font-weight:700;color:#fff;">Vos adresses</h2>
        <p style="color:var(--ui-text-muted);margin-top:8px;font-size:13px;">Étape 3/3 - Au moins 1 adresse requise (max 2)</p>
        <div style="display:flex;justify-content:center;gap:8px;margin-top:16px;">
          <div style="width:60px;height:4px;background:var(--ui-card-border);border-radius:2px;"></div>
          <div style="width:60px;height:4px;background:var(--ui-card-border);border-radius:2px;"></div>
          <div style="width:60px;height:4px;background:linear-gradient(135deg,#22c55e,#16a34a);border-radius:2px;"></div>
        </div>
      </div>
      
      <div style="background:rgba(0,255,195,0.1);border:1px solid rgba(0,255,195,0.3);border-radius:12px;padding:16px;margin-bottom:20px;">
        <div style="font-size:13px;font-weight:600;color:#00ffc3;margin-bottom:8px;">💡 À quoi servent vos adresses ?</div>
        <div style="font-size:12px;color:var(--ui-text-muted);line-height:1.6;">
          Nous utilisons vos adresses pour vous envoyer des <strong style="color:#00ffc3;">alertes de proximité</strong> dans le bloc "Alertes" de la barre de titre.
          <br><br>
          Vous recevrez une notification si un <strong>booking, service, organisateur ou événement</strong> que vous avez <strong>liké</strong> se trouve dans un rayon de <strong style="color:#00ffc3;">70 km</strong> de l'une de vos adresses.
          <br><br>
          Vos données sont sécurisées et ne sont utilisées que pour ce service.
        </div>
      </div>
      
      <div id="addresses-container">
        ${window.registerData.addresses.map((addr, index) => `
          <div id="address-field-${index}" style="background:rgba(15,23,42,0.5);border:1px solid var(--ui-card-border);border-radius:12px;padding:16px;margin-bottom:12px;">
            ${index === 0 ? '<div style="font-size:11px;color:#00ffc3;margin-bottom:8px;font-weight:600;">📍 Adresse principale</div>' : ''}
            <div style="margin-bottom:12px;">
              <label style="display:block;font-size:12px;font-weight:600;color:#fff;margin-bottom:6px;">Adresse complète *</label>
              <input type="text" id="address-${index}" placeholder="Rue, numéro, ville" required
                     value="${addr.address}"
                     onchange="window.registerData.addresses[${index}].address = this.value"
                     style="width:100%;padding:10px;border-radius:8px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:14px;">
            </div>
            <div style="display:flex;gap:8px;align-items:end;">
              <div style="flex:1;">
                <label style="display:block;font-size:12px;font-weight:600;color:#fff;margin-bottom:6px;">Ville *</label>
                <input type="text" id="city-${index}" placeholder="Ville" required
                       value="${addr.city}"
                       onchange="window.registerData.addresses[${index}].city = this.value"
                       style="width:100%;padding:10px;border-radius:8px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:14px;">
              </div>
              <button onclick="geocodeAddress(${index})" style="padding:10px 16px;border-radius:8px;border:none;background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff;font-weight:600;cursor:pointer;font-size:13px;white-space:nowrap;">
                🔍 Géocoder
              </button>
            </div>
            ${addr.lat && addr.lng ? `
              <div style="margin-top:8px;font-size:11px;color:#22c55e;">
                ✅ Coordonnées : ${addr.lat.toFixed(6)}, ${addr.lng.toFixed(6)}
              </div>
            ` : `
              <div style="margin-top:8px;font-size:11px;color:var(--ui-text-muted);">
                ⚠️ Cliquez sur "Géocoder" pour obtenir les coordonnées
              </div>
            `}
            ${index > 0 ? `
              <button onclick="removeAddressField(${index})" style="margin-top:8px;padding:6px 12px;border-radius:6px;border:1px solid rgba(239,68,68,0.5);background:rgba(239,68,68,0.1);color:#ef4444;cursor:pointer;font-size:12px;">
                🗑️ Supprimer
              </button>
            ` : ''}
          </div>
        `).join('')}
      </div>
      
      ${window.registerData.addresses.length < 2 ? `
        <button onclick="addAddressField()" style="width:100%;padding:10px;border-radius:8px;border:1px dashed var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-size:13px;margin-bottom:20px;">
          + Ajouter une adresse (${window.registerData.addresses.length}/2)
        </button>
      ` : ''}
      
      <div style="display:flex;gap:12px;">
        <button onclick="showRegisterStep2()" style="flex:1;padding:12px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-weight:600;">
          Précédent
        </button>
        <button onclick="completeRegistration()" style="flex:1;padding:12px;border-radius:999px;border:none;background:linear-gradient(135deg,#22c55e,#16a34a);color:#fff;font-weight:700;cursor:pointer;">
          Créer mon compte
        </button>
      </div>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
  const backdrop = document.getElementById("publish-modal-backdrop");
  if (backdrop) {
    backdrop.setAttribute('data-auth-modal', 'true');
    backdrop.style.display = "flex";
    backdrop.style.paddingTop = "40px";
    backdrop.style.paddingBottom = "40px";
    backdrop.style.boxSizing = "border-box";
  }
}

function addAddressField() {
  if (window.registerData.addresses.length >= 2) {
    showNotification("⚠️ Maximum 2 adresses autorisées", "warning");
    return;
  }
  
  window.registerData.addresses.push({ address: '', city: '', lat: null, lng: null, isPrimary: false });
  showRegisterStep3();
}

function removeAddressField(index) {
  if (window.registerData.addresses.length <= 1) {
    showNotification("⚠️ Au moins une adresse est requise", "warning");
    return;
  }
  
  window.registerData.addresses.splice(index, 1);
  showRegisterStep3();
}

async function geocodeAddress(addressIndex) {
  const addressInput = document.getElementById(`address-${addressIndex}`);
  const cityInput = document.getElementById(`city-${addressIndex}`);
  
  if (!addressInput || !cityInput) return;
  
  const address = addressInput.value.trim();
  const city = cityInput.value.trim();
  
  if (!address || !city) {
    showNotification("⚠️ Veuillez remplir l'adresse et la ville", "warning");
    return;
  }
  
  const fullAddress = `${address}, ${city}, Switzerland`;
  
  try {
    showNotification("🔍 Vérification de l'adresse...", "info");
    
    // Utiliser Nominatim avec plus de détails pour vérifier que l'adresse est réelle
    // VALIDATION STRICTE + PERFORMANCE: Paramètres optimisés pour recherche rapide et exacte
    // ⚠️⚠️⚠️ RECHERCHE MONDIALE - Pas de restriction de pays, support multilingue
    const langCode = (navigator.language || 'fr').split('-')[0];
    const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(fullAddress)}&limit=10&addressdetails=1&extratags=1&accept-language=${langCode},en&dedupe=1`, {
      headers: {
        'User-Agent': 'MapEventAI/1.0',
        'Accept-Language': `${langCode},en,fr`
      }
    });
    
    if (!response.ok) {
      throw new Error('Erreur de géocodage');
    }
    
    const data = await response.json();
    
    if (data.length === 0) {
      showNotification("⚠️ Adresse introuvable. Veuillez vérifier que l'adresse existe réellement.", "warning");
      return;
    }
    
    // Prendre le résultat le plus pertinent (généralement le premier)
    const result = data[0];
    
    // Vérifier que le résultat correspond bien à une adresse réelle
    const resultType = result.type || '';
    const resultClass = result.class || '';
    const addressDetails = result.address || {};
    
    // Vérifier que c'est bien une adresse (pas juste une ville ou un pays)
    const isValidAddress = resultType === 'house' || 
                          resultType === 'building' || 
                          resultType === 'residential' ||
                          resultClass === 'place' ||
                          (addressDetails.house_number && addressDetails.road);
    
    if (!isValidAddress && data.length > 1) {
      // Chercher un résultat plus précis
      const betterResult = data.find(r => 
        r.type === 'house' || 
        r.type === 'building' || 
        (r.address && r.address.house_number)
      );
      if (betterResult) {
        Object.assign(result, betterResult);
      }
    }
    
    const lat = parseFloat(result.lat);
    const lng = parseFloat(result.lon);
    
    // Vérifier que les coordonnées sont valides
    if (isNaN(lat) || isNaN(lng) || lat < -90 || lat > 90 || lng < -180 || lng > 180) {
      showNotification("⚠️ Coordonnées invalides. L'adresse semble incorrecte.", "warning");
      return;
    }
    
    // Vérifier que l'adresse est en Suisse (ou pays autorisé)
    const country = addressDetails.country_code?.toUpperCase() || '';
    if (country && country !== 'CH' && country !== 'FR' && country !== 'DE' && country !== 'IT' && country !== 'AT') {
      showNotification(`⚠️ L'adresse doit être en Suisse ou dans un pays voisin (actuellement: ${country}).`, "warning");
      return;
    }
    
    // Détecter le pays pour l'enregistrement (utiliser la première adresse)
    if (!registerData.registeredCountry && country) {
      registerData.registeredCountry = country;
    }
    
    // Stocker les informations complètes pour vérification backend
    window.registerData.addresses[addressIndex].lat = lat;
    window.registerData.addresses[addressIndex].lng = lng;
    window.registerData.addresses[addressIndex].address = address;
    window.registerData.addresses[addressIndex].city = city;
    window.registerData.addresses[addressIndex].verified = true;
    window.registerData.addresses[addressIndex].addressDetails = {
      house_number: addressDetails.house_number || '',
      road: addressDetails.road || '',
      postcode: addressDetails.postcode || '',
      country: addressDetails.country || '',
      country_code: country
    };
    
    showNotification("✅ Adresse vérifiée et validée !", "success");
    showRegisterStep3(); // Rafraîchir pour afficher les coordonnées
  } catch (error) {
    console.error('Erreur géocodage:', error);
    showNotification("❌ Erreur lors de la vérification. Réessayez plus tard.", "error");
  }
}

async function completeRegistration() {
  // Vérifier que l'email est vérifié
  if (!window.window.registerData.emailVerified) {
    showContextualError('EMAIL_NOT_VERIFIED', 'Email non vérifié');
    return;
  }
  
  // Vérifier qu'au moins une adresse a des coordonnées
  const validAddresses = window.registerData.addresses.filter(addr => 
    addr.address && addr.city && addr.lat && addr.lng
  );
  
  if (validAddresses.length === 0) {
    showContextualError('VALIDATION_ERROR', 'Adresse postale requise', {
      details: 'Veuillez ajouter et géocoder au moins une adresse postale.',
      fieldId: 'pro-postal-address'
    });
    return;
  }
  
  // Vérifier le rate limiting final
  const now = Date.now();
  if (window.registerData.lastRegistrationAttempt && (now - window.registerData.lastRegistrationAttempt) < 30000) {
    const remainingSeconds = Math.ceil((30000 - (now - window.registerData.lastRegistrationAttempt)) / 1000);
    showContextualError('RATE_LIMITED', 'Trop de tentatives', { retryAfter: remainingSeconds });
    return;
  }
  
  // Récupérer l'avatar sélectionné
  const selectedAvatar = AVAILABLE_AVATARS.find(av => av.id === window.registerData.avatarId) || AVAILABLE_AVATARS[0];
  
  // Créer l'utilisateur
  const userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  const createdAt = new Date().toISOString();
  
  currentUser = {
    id: userId,
    name: window.registerData.username,
    firstName: window.registerData.firstName,
    lastName: window.registerData.lastName,
    email: window.registerData.email,
    avatar: selectedAvatar.emoji,
    avatarId: selectedAvatar.id,
    avatarName: selectedAvatar.name,
    avatarDescription: window.registerData.avatarDescription || '',
    bio: '',
    isLoggedIn: true,
    favorites: [],
    agenda: [],
    likes: [],
    participating: [],
    alerts: [],
    reviews: {},
    subscription: "free",
    agendaLimit: 20,
    alertLimit: 2,
    eventStatusHistory: {},
    addresses: validAddresses.map((addr, index) => ({
      address: addr.address,
      city: addr.city,
      lat: addr.lat,
      lng: addr.lng,
      isPrimary: index === 0
    })),
    registeredCountry: registerData.registeredCountry || 'CH',
    registeredCountry: registerData.registeredCountry || 'CH',
    smsNotifications: 0,
    smsLimit: 0,
    emailNotifications: 0,
    notificationPreferences: {
      email: true,
      sms: false
    },
    // Nouvelles propriétés sociales
    friends: [],
    friendRequests: [],
    sentRequests: [],
    blockedUsers: [],
    conversations: [],
    groups: [],
    lastSeen: createdAt,
    profileLinks: [],
    profilePhotos: [],
    createdAt: createdAt,
    lastLoginAt: createdAt
  };
  
  // Initialiser historique et photos si inexistants
  if (!currentUser.history) currentUser.history = [];
  if (!currentUser.photos) currentUser.photos = [];
  
  // Ajouter l'événement de création de compte à l'historique
  currentUser.history.unshift({
    action: "Compte créé",
    icon: "🎉",
    timestamp: createdAt
  });
  
  // Sauvegarder dans localStorage
  try {
    localStorage.setItem('currentUser', JSON.stringify(currentUser));
  } catch (e) {
    console.error('Erreur sauvegarde utilisateur:', e);
  }
  
  // INTERDICTION : Ne pas modifier le bloc compte - fonctions supprimées
  
  // Sauvegarder dans le backend (OBLIGATOIRE - vérification côté serveur)
  try {
    const response = await fetch(`${window.API_BASE_URL}/user/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: window.registerData.email,
        username: window.registerData.username,
        password: window.registerData.password, // Le backend hash le mot de passe
        firstName: window.registerData.firstName,
        lastName: window.registerData.lastName,
        avatarId: selectedAvatar.id,
        avatarEmoji: selectedAvatar.emoji,
        avatarDescription: window.registerData.avatarDescription || '',
        addresses: currentUser.addresses.map(addr => ({
          ...addr,
          addressDetails: window.registerData.addresses.find(a => a.address === addr.address && a.city === addr.city)?.addressDetails || {}
        })),
        verificationCode: window.window.registerData.emailVerificationCode // Envoyer le code pour double vérification
      })
    });
    
    const result = await response.json();
    
    if (!response.ok) {
      // Erreur côté backend - utiliser messages contextuels
      if (result.code === 'EMAIL_NOT_VERIFIED') {
        showContextualError('EMAIL_NOT_VERIFIED', result.error || 'Email non vérifié');
        return;
      } else if (result.code === 'EMAIL_ALREADY_EXISTS' || result.error?.includes('email') || result.error?.includes('Email')) {
        showContextualError('EMAIL_ALREADY_EXISTS', result.error || 'Email déjà utilisé', { email: window.registerData.email });
        return;
      } else if (result.code === 'USERNAME_ALREADY_EXISTS' || result.error?.includes('username') || result.error?.includes('nom d\'utilisateur')) {
        showContextualError('USERNAME_ALREADY_EXISTS', result.error || 'Nom d\'utilisateur déjà pris', { username: window.registerData.username });
        return;
      } else if (result.rate_limited) {
        showContextualError('RATE_LIMITED', result.error || 'Trop de tentatives', { retryAfter: result.retry_after || 300 });
        return;
      } else if (result.error?.includes('mot de passe') || result.error?.includes('password')) {
        showContextualError('PASSWORD_TOO_WEAK', result.error || 'Mot de passe invalide', { details: result.error });
        return;
      } else {
        // Erreur générique avec suggestion de réessayer
        showContextualError('NETWORK_ERROR', result.error || 'Erreur lors de la création du compte', {
          retryCallback: () => completeRegistration()
        });
        return;
      }
    }
    
    // Utiliser l'ID utilisateur retourné par le backend
    if (result.userId) {
      currentUser.id = result.userId;
    }
    
    console.log('✅ Compte créé avec succès dans le backend:', result);
  } catch (error) {
    console.error('Erreur enregistrement backend:', error);
    showContextualError('NETWORK_ERROR', 'Erreur de connexion au serveur', {
      retryCallback: () => completeRegistration()
    });
    return; // Ne pas continuer si le backend échoue
  }
  
  showNotification("✅ Compte créé avec succès !", "success");
  closePublishModal();
  // INTERDICTION : Ne pas modifier le bloc compte - fonctions supprimées
  
  // Charger les données utilisateur
  await loadUserDataOnLogin();
}

// Alias pour compatibilité
function showRegisterForm() {
  openRegisterModal();
}

// Modales CGU/RGPD
function showTermsModal() {
  console.log('[MODAL] showTermsModal appelée');
  
  // Ouvrir le modal d'abord
  const backdrop = document.getElementById('publish-modal-backdrop');
  const modal = document.getElementById('publish-modal-inner');
  
  if (!backdrop || !modal) {
    console.error('[MODAL] Éléments modal non trouvés');
    return false;
  }
  
  const html = `
    <div style="padding:24px;max-width:700px;margin:0 auto;max-height:85vh;overflow-y:auto;">
      <h2 style="margin:0 0 20px;font-size:24px;font-weight:700;color:#fff;">Conditions d'utilisation</h2>
      <div style="color:var(--ui-text-main);line-height:1.8;font-size:14px;">
        <p><strong>Dernière mise à jour :</strong> ${new Date().toLocaleDateString('fr-FR')}</p>
        <p>En utilisant MapEventAI, vous acceptez les présentes conditions d'utilisation.</p>
        <h3 style="color:#fff;margin-top:24px;margin-bottom:12px;">1. Acceptation des conditions</h3>
        <p>En accédant et en utilisant cette plateforme, vous acceptez d'être lié par ces conditions d'utilisation.</p>
        <h3 style="color:#fff;margin-top:24px;margin-bottom:12px;">2. Utilisation du service</h3>
        <p>Vous vous engagez à utiliser MapEventAI de manière légale et conforme à ces conditions. Toute utilisation abusive est interdite.</p>
        <h3 style="color:#fff;margin-top:24px;margin-bottom:12px;">3. Propriété intellectuelle</h3>
        <p>Tous les contenus de la plateforme sont protégés par les droits de propriété intellectuelle.</p>
        <h3 style="color:#fff;margin-top:24px;margin-bottom:12px;">4. Limitation de responsabilité</h3>
        <p>MapEventAI ne peut être tenu responsable des dommages résultant de l'utilisation de la plateforme.</p>
      </div>
      <button onclick="if(typeof window.showProRegisterForm==='function'){window.showProRegisterForm();}else if(typeof showProRegisterForm==='function'){showProRegisterForm();}return false;" style="width:100%;padding:14px;border-radius:999px;border:none;background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff;font-weight:700;cursor:pointer;margin-top:24px;">
        Fermer et revenir au formulaire
      </button>
    </div>
  `;
  
  backdrop.style.display = 'flex';
  modal.style.display = 'block';
  modal.innerHTML = html;
  console.log('[MODAL] Modal Conditions d\'utilisation affiché');
  return false;
}

function showPrivacyModal() {
  console.log('[MODAL] ✅ showPrivacyModal appelée');
  
  // Ouvrir le modal d'abord
  const backdrop = document.getElementById('publish-modal-backdrop');
  const modal = document.getElementById('publish-modal-inner');
  
  if (!backdrop || !modal) {
    console.error('[MODAL] ❌ Éléments modal non trouvés pour showPrivacyModal');
    return false;
  }
  
  console.log('[MODAL] ✅ Éléments trouvés, ouverture du modal');
  
  const html = `
    <div style="padding:24px;max-width:700px;margin:0 auto;max-height:85vh;overflow-y:auto;">
      <h2 style="margin:0 0 20px;font-size:24px;font-weight:700;color:#fff;">Politique de confidentialité</h2>
      <div style="color:var(--ui-text-main);line-height:1.8;font-size:14px;">
        <p><strong>Dernière mise à jour :</strong> ${new Date().toLocaleDateString('fr-FR')}</p>
        <p>MapEventAI s'engage à protéger votre vie privée et vos données personnelles.</p>
        <h3 style="color:#fff;margin-top:24px;margin-bottom:12px;">1. Données collectées</h3>
        <p>Nous collectons les données nécessaires au fonctionnement du service : email, nom d'utilisateur, adresses (pour les alertes de proximité), et préférences.</p>
        <h3 style="color:#fff;margin-top:24px;margin-bottom:12px;">2. Utilisation des données</h3>
        <p>Vos données sont utilisées uniquement pour :</p>
        <ul style="padding-left:24px;margin:12px 0;">
          <li>Fournir les services de la plateforme</li>
          <li>Envoyer des alertes de proximité (rayon de 70km)</li>
          <li>Améliorer nos services</li>
        </ul>
        <h3 style="color:#fff;margin-top:24px;margin-bottom:12px;">3. Sécurité</h3>
        <p>Nous mettons en œuvre des mesures de sécurité appropriées pour protéger vos données contre tout accès non autorisé.</p>
        <h3 style="color:#fff;margin-top:24px;margin-bottom:12px;">4. Vos droits</h3>
        <p>Conformément au RGPD, vous disposez d'un droit d'accès, de rectification, de suppression et de portabilité de vos données.</p>
      </div>
      <button onclick="if(typeof window.showProRegisterForm==='function'){window.showProRegisterForm();}else if(typeof showProRegisterForm==='function'){showProRegisterForm();}return false;" style="width:100%;padding:14px;border-radius:999px;border:none;background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff;font-weight:700;cursor:pointer;margin-top:24px;">
        Fermer et revenir au formulaire
      </button>
    </div>
  `;
  
  backdrop.style.display = 'flex';
  modal.style.display = 'block';
  modal.innerHTML = html;
  console.log('[MODAL] Modal Politique de confidentialité affiché');
  return false;
}

function openReviewModal(type, id) {
  const key = `${type}:${id}`;
  const reviews = currentUser.reviews[key] || [];
  const reviewsPerPage = 10;
  let currentPage = 1;
  
  // Initialiser si nécessaire
  if (!currentUser.reviews[key]) {
    currentUser.reviews[key] = [];
  }
  
  function renderReviews(page = 1) {
    const start = (page - 1) * reviewsPerPage;
    const end = start + reviewsPerPage;
    const pageReviews = reviews.slice(start, end);
    const totalPages = Math.ceil(reviews.length / reviewsPerPage);
    
    const reviewsHtml = pageReviews.length === 0 ? `
      <div style="text-align:center;padding:40px;color:var(--ui-text-muted);">
        <div style="font-size:48px;margin-bottom:16px;">💬</div>
        <p>Aucun avis pour le moment</p>
        <p style="font-size:12px;margin-top:8px;">Soyez le premier à laisser un avis !</p>
      </div>
    ` : pageReviews.map(review => {
      const repliesHtml = (review.replies || []).map(reply => `
        <div style="margin-left:40px;margin-top:8px;padding:8px;background:rgba(15,23,42,0.5);border-radius:8px;border-left:3px solid #3b82f6;">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
            <div style="width:24px;height:24px;border-radius:50%;background:linear-gradient(135deg,${reply.avatarColor || '#3b82f6'},${reply.avatarColor2 || '#8b5cf6'});display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;">
              ${reply.avatar || reply.userName.charAt(0).toUpperCase()}
            </div>
            <span style="font-weight:600;font-size:12px;">${escapeHtml(reply.userName)}</span>
            <span style="font-size:10px;color:var(--ui-text-muted);">${formatDate(reply.date)}</span>
          </div>
          <div style="font-size:13px;color:var(--ui-text-main);">${escapeHtml(reply.text)}</div>
        </div>
      `).join('');
      
      return `
        <div style="padding:12px;background:rgba(15,23,42,0.5);border-radius:12px;margin-bottom:12px;border:1px solid var(--ui-card-border);">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
            <div style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,${review.avatarColor || '#00ffc3'},${review.avatarColor2 || '#3b82f6'});display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700;">
              ${review.avatar || review.userName.charAt(0).toUpperCase()}
            </div>
            <div style="flex:1;">
              <div style="display:flex;align-items:center;gap:8px;">
                <span style="font-weight:600;font-size:14px;">${escapeHtml(review.userName)}</span>
                ${review.rating ? `<span style="font-size:12px;color:#facc15;">${'⭐'.repeat(review.rating)}</span>` : ''}
              </div>
              <div style="font-size:11px;color:var(--ui-text-muted);">${formatDate(review.date)}</div>
            </div>
          </div>
          <div style="font-size:14px;color:var(--ui-text-main);line-height:1.5;margin-bottom:8px;">${escapeHtml(review.text)}</div>
          ${repliesHtml}
          <button onclick="showReplyForm('${review.id}', '${type}', ${id})" style="margin-top:8px;padding:4px 12px;border-radius:6px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-size:12px;">
            💬 Répondre
          </button>
        </div>
      `;
    }).join('');
    
    const paginationHtml = totalPages > 1 ? `
      <div style="display:flex;justify-content:center;align-items:center;gap:8px;margin-top:16px;">
        <button onclick="loadReviewPage(${Math.max(1, page - 1)})" ${page === 1 ? 'disabled' : ''} style="padding:6px 12px;border-radius:6px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-size:12px;${page === 1 ? 'opacity:0.5;cursor:not-allowed;' : ''}">
          ← Précédent
        </button>
        <span style="font-size:12px;color:var(--ui-text-muted);">Page ${page}/${totalPages}</span>
        <button onclick="loadReviewPage(${Math.min(totalPages, page + 1)})" ${page === totalPages ? 'disabled' : ''} style="padding:6px 12px;border-radius:6px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-size:12px;${page === totalPages ? 'opacity:0.5;cursor:not-allowed;' : ''}">
          Suivant →
        </button>
      </div>
    ` : '';
    
    const container = document.getElementById('reviews-list-container');
    if (container) {
      container.innerHTML = reviewsHtml + paginationHtml;
    }
  }
  
  const html = `
    <div style="padding:10px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
        <h2 style="margin:0;font-size:18px;">⭐ Avis et Discussions (${reviews.length})</h2>
        <button onclick="closePublishModal()" style="background:none;border:none;font-size:20px;cursor:pointer;color:var(--ui-text-muted);">✕</button>
      </div>
      
      <!-- Liste des avis avec pagination -->
      <div id="reviews-list-container" style="max-height:calc(80vh - 250px);overflow-y:auto;margin-bottom:16px;padding-right:8px;">
        ${reviews.length === 0 ? `
          <div style="text-align:center;padding:40px;color:var(--ui-text-muted);">
            <div style="font-size:48px;margin-bottom:16px;">💬</div>
            <p>Aucun avis pour le moment</p>
            <p style="font-size:12px;margin-top:8px;">Soyez le premier à laisser un avis !</p>
          </div>
        ` : reviews.slice(0, reviewsPerPage).map(review => {
          const repliesHtml = (review.replies || []).map(reply => `
            <div style="margin-left:40px;margin-top:8px;padding:8px;background:rgba(15,23,42,0.5);border-radius:8px;border-left:3px solid #3b82f6;">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
                <div style="width:24px;height:24px;border-radius:50%;background:linear-gradient(135deg,${reply.avatarColor || '#3b82f6'},${reply.avatarColor2 || '#8b5cf6'});display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;">
                  ${reply.avatar || reply.userName.charAt(0).toUpperCase()}
                </div>
                <span style="font-weight:600;font-size:12px;">${escapeHtml(reply.userName)}</span>
                <span style="font-size:10px;color:var(--ui-text-muted);">${formatDate(reply.date)}</span>
              </div>
              <div style="font-size:13px;color:var(--ui-text-main);">${escapeHtml(reply.text)}</div>
            </div>
          `).join('');
          
          return `
            <div style="padding:12px;background:rgba(15,23,42,0.5);border-radius:12px;margin-bottom:12px;border:1px solid var(--ui-card-border);">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                <div style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,${review.avatarColor || '#00ffc3'},${review.avatarColor2 || '#3b82f6'});display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700;">
                  ${review.avatar || review.userName.charAt(0).toUpperCase()}
                </div>
                <div style="flex:1;">
                  <div style="display:flex;align-items:center;gap:8px;">
                    <span style="font-weight:600;font-size:14px;">${escapeHtml(review.userName)}</span>
                    ${review.rating ? `<span style="font-size:12px;color:#facc15;">${'⭐'.repeat(review.rating)}</span>` : ''}
                  </div>
                  <div style="font-size:11px;color:var(--ui-text-muted);">${formatDate(review.date)}</div>
                </div>
              </div>
              <div style="font-size:14px;color:var(--ui-text-main);line-height:1.5;margin-bottom:8px;">${escapeHtml(review.text)}</div>
              ${repliesHtml}
              <button onclick="showReplyForm('${review.id}', '${type}', ${id})" style="margin-top:8px;padding:4px 12px;border-radius:6px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-size:12px;">
                💬 Répondre
              </button>
            </div>
          `;
        }).join('')}
      </div>
      ${reviews.length > reviewsPerPage ? `
        <div style="display:flex;justify-content:center;align-items:center;gap:8px;margin-bottom:16px;">
          <button onclick="loadReviewPage(1)" style="padding:6px 12px;border-radius:6px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-size:12px;">
            ← Précédent
          </button>
          <span style="font-size:12px;color:var(--ui-text-muted);">Page 1/${Math.ceil(reviews.length / reviewsPerPage)}</span>
          <button onclick="loadReviewPage(2)" style="padding:6px 12px;border-radius:6px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-size:12px;">
            Suivant →
          </button>
        </div>
      ` : ''}
      
      <!-- Formulaire pour laisser un avis -->
      <div style="padding:12px;background:rgba(15,23,42,0.5);border-radius:12px;border:1px solid var(--ui-card-border);margin-top:16px;">
        <h3 style="margin:0 0 12px;font-size:14px;">Laisser un avis</h3>
        <div style="display:flex;gap:8px;margin-bottom:12px;justify-content:center;">
          ${[1,2,3,4,5].map(n => `
            <button onclick="setRating(${n})" class="rating-star" data-rating="${n}" style="font-size:24px;background:none;border:none;cursor:pointer;transition:transform 0.1s;">⭐</button>
          `).join('')}
        </div>
        <textarea id="review-text" rows="3" placeholder="Partagez votre expérience..." style="width:100%;padding:10px;border-radius:8px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);resize:none;font-size:13px;"></textarea>
        <button onclick="submitReview('${type}', ${id})" style="width:100%;margin-top:8px;padding:10px;border-radius:999px;border:none;background:var(--btn-main-bg);color:var(--btn-main-text);font-weight:600;cursor:pointer;font-size:13px;">
          Publier l'avis
        </button>
      </div>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
  const backdrop = document.getElementById("publish-modal-backdrop");
  if (backdrop) {
    backdrop.setAttribute('data-auth-modal', 'true');
    backdrop.style.display = "flex";
    backdrop.style.paddingTop = "40px";
    backdrop.style.paddingBottom = "40px";
    backdrop.style.boxSizing = "border-box";
    backdrop.style.paddingTop = "40px";
    backdrop.style.paddingBottom = "40px";
    backdrop.style.boxSizing = "border-box";
  }
  
  // Stocker les données pour la pagination
  window.reviewsData = { key, reviews, currentPage: 1, reviewsPerPage };
  window.renderReviews = renderReviews;
}

function loadReviewPage(page) {
  if (!window.reviewsData) return;
  const { key, reviews, reviewsPerPage } = window.reviewsData;
  window.reviewsData.currentPage = page;
  window.renderReviews(page);
}

function showReplyForm(reviewId, type, id) {
  const replyFormHtml = `
    <div id="reply-form-${reviewId}" style="margin-top:8px;padding:8px;background:rgba(15,23,42,0.7);border-radius:8px;border:1px solid var(--ui-card-border);">
      <textarea id="reply-text-${reviewId}" rows="2" placeholder="Votre réponse..." style="width:100%;padding:8px;border-radius:6px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);resize:none;font-size:12px;margin-bottom:6px;"></textarea>
      <div style="display:flex;gap:6px;">
        <button onclick="submitReply('${reviewId}', '${type}', ${id})" style="flex:1;padding:6px;border-radius:6px;border:none;background:var(--btn-main-bg);color:var(--btn-main-text);font-weight:600;cursor:pointer;font-size:12px;">
          Envoyer
        </button>
        <button onclick="document.getElementById('reply-form-${reviewId}').remove()" style="padding:6px 12px;border-radius:6px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-size:12px;">
          Annuler
        </button>
      </div>
    </div>
  `;
  
  const existingForm = document.getElementById(`reply-form-${reviewId}`);
  if (existingForm) {
    existingForm.remove();
  } else {
    const reviewElement = document.querySelector(`[data-review-id="${reviewId}"]`);
    if (reviewElement) {
      reviewElement.insertAdjacentHTML('beforeend', replyFormHtml);
    }
  }
}

function submitReply(reviewId, type, id) {
  const text = document.getElementById(`reply-text-${reviewId}`)?.value;
  if (!text || !text.trim()) {
    showNotification("⚠️ Veuillez écrire une réponse", "warning");
    return;
  }
  
  if (!currentUser || !currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  
  const key = `${type}:${id}`;
  const reviews = currentUser.reviews[key] || [];
  const review = reviews.find(r => r.id === reviewId);
  
  if (!review) return;
  
  if (!review.replies) review.replies = [];
  
  const avatarColors = ['#00ffc3', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444', '#22c55e'];
  const avatarColors2 = ['#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444', '#22c55e', '#00ffc3'];
  const colorIndex = Math.floor(Math.random() * avatarColors.length);
  
  review.replies.push({
    id: Date.now(),
    userId: currentUser.id,
    userName: currentUser.name,
    avatar: currentUser.avatar,
    avatarColor: avatarColors[colorIndex],
    avatarColor2: avatarColors2[colorIndex],
    text: text.trim(),
    date: new Date().toISOString()
  });
  
  showNotification("✅ Réponse publiée !", "success");
  openReviewModal(type, id); // Rafraîchir
}

let currentRating = 0;
function setRating(n) {
  currentRating = n;
  document.querySelectorAll(".rating-star").forEach((star, i) => {
    star.style.transform = i < n ? "scale(1.2)" : "scale(1)";
    star.style.filter = i < n ? "none" : "grayscale(1)";
  });
}

function submitReview(type, id) {
  const text = document.getElementById("review-text")?.value;
  if (!text || !text.trim() || currentRating === 0) {
    showNotification("⚠️ Veuillez donner une note et écrire un avis", "warning");
    return;
  }
  
  if (!currentUser || !currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  
  const key = `${type}:${id}`;
  if (!currentUser.reviews[key]) {
    currentUser.reviews[key] = [];
  }
  
  const avatarColors = ['#00ffc3', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444', '#22c55e'];
  const avatarColors2 = ['#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444', '#22c55e', '#00ffc3'];
  const colorIndex = Math.floor(Math.random() * avatarColors.length);
  
  const review = {
    id: Date.now(),
    userId: currentUser.id,
    userName: currentUser.name,
    avatar: currentUser.avatar,
    avatarColor: avatarColors[colorIndex],
    avatarColor2: avatarColors2[colorIndex],
    rating: currentRating,
    text: text.trim(),
    date: new Date().toISOString(),
    replies: []
  };
  
  currentUser.reviews[key].unshift(review); // Ajouter au début
  
  // Mettre à jour le rating moyen de l'item
  const data = type === "event" ? eventsData : type === "booking" ? bookingsData : servicesData;
  const item = data.find(i => i.id === parseInt(id));
  if (item) {
    const allRatings = currentUser.reviews[key].map(r => r.rating).filter(r => r > 0);
    if (allRatings.length > 0) {
      item.rating = (allRatings.reduce((a, b) => a + b, 0) / allRatings.length).toFixed(1);
    }
  }
  
  showNotification("✅ Avis publié avec succès !", "success");
  currentRating = 0;
  openReviewModal(type, id); // Rafraîchir pour afficher le nouvel avis
}

async function openDiscussionModal(type, id) {
  // Échappement HTML sûr (au cas où escapeHtml n'est pas encore défini)
  const esc = (typeof escapeHtml === 'function') ? escapeHtml : function(s) {
    if (s == null || s === undefined) return '';
    const t = String(s);
    return t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  };
  
  let item = null;
  if (type === 'event') item = eventsData.find(e => e.id === id);
  else if (type === 'booking') item = bookingsData.find(b => b.id === id);
  else if (type === 'service') item = servicesData.find(s => s.id === id);
  
  const itemTitle = item?.title || item?.name || 'Événement';
  
  // Charger depuis l'API backend (persistant) avec fallback localStorage pour migration
  const postsKey = `discussion_${type}_${id}`;
  let posts = [];
  
  // Charger les posts de manière asynchrone mais afficher un loading
  window._discussionLoadingType = type;
  window._discussionLoadingId = id;
  
  // Tentative de chargement depuis l'API
  try {
    const resp = await fetch(`${window.API_BASE_URL}/discussions/${type}/${id}`);
    if (resp.ok) {
      const data = await resp.json();
      if (data.posts && Array.isArray(data.posts) && data.posts.length > 0) {
        posts = data.posts;
        console.log(`[Discussion] ${posts.length} posts charges depuis API`);
      } else {
        // Fallback : migrer depuis localStorage si existe
        const localPosts = JSON.parse(localStorage.getItem(postsKey) || '[]');
        if (localPosts.length > 0) {
          posts = localPosts;
          // Migrer vers le backend
          fetch(`${window.API_BASE_URL}/discussions/${type}/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ posts: localPosts })
          }).then(() => {
            localStorage.removeItem(postsKey);
            console.log('[Discussion] Migration localStorage -> API OK');
          }).catch(e => console.warn('[Discussion] Migration echouee:', e));
        }
      }
    }
  } catch(e) {
    console.warn('[Discussion] API indisponible, fallback localStorage:', e);
    posts = JSON.parse(localStorage.getItem(postsKey) || '[]');
  }
  
  // PROTECTION : Filtrer les posts corrompus
  const isPostCorrupted = (post) => {
    if (!post || !post.text) return true;
    const text = post.text;
    if (text.length > 5000) return true;
    if (/[A-Za-z0-9+/=]{100,}/.test(text)) return true;
    if (/function\s*\(|const\s+\w+\s*=|window\.|document\./.test(text)) return true;
    return false;
  };
  
  const originalLength = posts.length;
  posts = posts.filter(p => !isPostCorrupted(p));
  if (posts.length !== originalLength) {
    console.log(`[Discussion] ${originalLength - posts.length} posts corrompus supprimes`);
  }
  
  // Fonction pour formater le temps
  const formatTime = (timestamp) => {
    const now = Date.now();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'À l\'instant';
    if (minutes < 60) return `Il y a ${minutes} min`;
    if (hours < 24) return `Il y a ${hours}h`;
    if (days < 7) return `Il y a ${days}j`;
    return new Date(timestamp).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
  };
  
  // Fonction pour compter toutes les réponses récursives
  const countAllReplies = (replies) => {
    if (!replies || replies.length === 0) return 0;
    let count = replies.length;
    replies.forEach(reply => {
      if (reply.replies && reply.replies.length > 0) {
        count += countAllReplies(reply.replies);
      }
    });
    return count;
  };
  
  // Fonction récursive pour rendre une réponse (style Facebook authentique - compact et professionnel)
  const renderReply = (reply, postId, parentPath = '', depth = 0, showAllNested = false) => {
    const replyPath = parentPath ? `${parentPath}-${reply.id}` : reply.id;
    const avatarSize = 32; // Taille fixe pour toutes les réponses (plus petit que le post)
    const nestedReplies = reply.replies || [];
    
    // Trier les réponses imbriquées par timestamp (plus anciennes en premier)
    const sortedNested = [...nestedReplies].sort((a, b) => (a.timestamp || 0) - (b.timestamp || 0));
    const maxVisibleNested = 2; // Afficher seulement 2 réponses imbriquées par défaut
    const visibleNested = showAllNested ? sortedNested : sortedNested.slice(0, maxVisibleNested);
    const hiddenNestedCount = sortedNested.length - maxVisibleNested;
    
    return `
      <div style="margin-bottom:4px;min-width:0;overflow:hidden;">
        <div style="display:flex;gap:8px;min-width:0;">
          <div style="width:${avatarSize}px;height:${avatarSize}px;border-radius:50%;background:linear-gradient(135deg,#1877f2,#42a5f5);display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;font-weight:700;color:#fff;">
            ${reply.avatar || '👤'}
          </div>
          <div style="flex:1;min-width:0;overflow:hidden;">
            <div style="background:rgba(30,41,59,0.6);border-radius:18px;padding:8px 12px;max-width:100%;overflow-wrap:break-word;word-break:break-word;">
              <span style="font-weight:600;font-size:13px;color:#e4e6eb;margin-right:4px;">${esc(reply.author || 'Utilisateur')}</span>
              <span style="font-size:13px;color:#e4e6eb;line-height:1.33;white-space:pre-wrap;word-wrap:break-word;overflow-wrap:break-word;word-break:break-word;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">${esc(reply.text)}</span>
            </div>
            <div style="display:flex;align-items:center;gap:12px;margin-top:4px;margin-left:12px;">
              <span style="font-size:12px;color:#b0b3b8;font-weight:600;cursor:pointer;" onclick="toggleReplyLike('${type}', '${id}', '${postId}', '${replyPath}')">J'aime</span>
              <button onclick="showReplyForm('${postId}', '${replyPath}')" style="background:none;border:none;color:#b0b3b8;font-size:12px;font-weight:600;cursor:pointer;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;" onmouseover="this.style.textDecoration='underline'" onmouseout="this.style.textDecoration='none'">
                Répondre
              </button>
              <span style="font-size:12px;color:#b0b3b8;">${formatTime(reply.timestamp || Date.now())}</span>
            </div>
          </div>
        </div>
        <!-- Formulaire de réponse -->
        <div id="reply-form-${postId}-${replyPath}" style="display:none;margin-left:${avatarSize + 8}px;margin-top:6px;">
          <div style="display:flex;gap:8px;align-items:flex-start;">
            <div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#1877f2,#42a5f5);display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;font-weight:700;color:#fff;">
              ${currentUser?.avatar || '👤'}
            </div>
            <div style="flex:1;position:relative;">
              <textarea id="reply-input-${postId}-${replyPath}" placeholder="Répondre à ${esc(reply.author || 'Utilisateur')}..." style="width:100%;min-height:36px;max-height:100px;padding:8px 12px;border-radius:20px;border:none;background:rgba(15,23,42,0.8);color:#e4e6eb;font-size:14px;resize:none;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;line-height:1.33;" onkeydown="if(event.key==='Enter' && !event.shiftKey) { event.preventDefault(); submitReply('${type}', '${id}', '${postId}', '${replyPath}'); }" oninput="this.style.height='auto';this.style.height=Math.min(this.scrollHeight,100)+'px';"></textarea>
            </div>
          </div>
        </div>
        <!-- Réponses imbriquées (récursif) - style Facebook compact -->
        ${sortedNested.length > 0 ? `
          <div style="margin-left:${avatarSize + 8}px;margin-top:4px;" data-post-id="${postId}" data-parent-path="${replyPath}">
            ${visibleNested.map(nestedReply => {
              // Vérifier si les réponses imbriquées de niveau 2 doivent être affichées
              const nested2ShowAllKey = `showAllNestedReplies_${type}_${id}_${postId}_${replyPath}-${nestedReply.id}`;
              const nested2ShowAll = sessionStorage.getItem(nested2ShowAllKey) === 'true';
              return renderReply(nestedReply, postId, replyPath, depth + 1, nested2ShowAll);
            }).join('')}
            ${hiddenNestedCount > 0 && !showAllNested ? `
              <button onclick="showAllNestedReplies('${postId}', '${replyPath}')" style="background:none;border:none;color:#1877f2;font-size:12px;font-weight:600;cursor:pointer;padding:4px 0;margin-top:4px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;" onmouseover="this.style.textDecoration='underline'" onmouseout="this.style.textDecoration='none'">
                Voir ${hiddenNestedCount} réponse${hiddenNestedCount > 1 ? 's' : ''} supplémentaire${hiddenNestedCount > 1 ? 's' : ''}
              </button>
            ` : ''}
          </div>
        ` : ''}
      </div>
    `;
  };
  
  // Fonction pour rendre un post (style Facebook authentique)
  const renderPost = (post) => {
    const isLiked = (post.likes || []).includes(currentUser?.id || currentUser?.username);
    const likesCount = post.likes ? post.likes.length : 0;
    const repliesCount = post.replies ? post.replies.length : 0;
    
    return `
      <div style="background:rgba(30,41,59,0.8);border-radius:8px;padding:12px;margin-bottom:12px;min-width:0;overflow:hidden;border:1px solid rgba(255,255,255,0.06);">
        <!-- En-tête du post -->
        <div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:8px;min-width:0;">
          <div style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#1877f2,#42a5f5);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;font-weight:700;color:#fff;">
            ${post.avatar || '👤'}
          </div>
          <div style="flex:1;min-width:0;overflow:hidden;">
            <div style="font-weight:600;font-size:15px;color:#e4e6eb;line-height:1.2;overflow-wrap:break-word;word-break:break-word;">${escapeHtml(post.author || 'Utilisateur')}</div>
            <div style="font-size:13px;color:#b0b3b8;line-height:1.2;">${formatTime(post.timestamp || Date.now())}</div>
          </div>
        </div>
        
        <!-- Contenu du post -->
        <div style="font-size:15px;color:#e4e6eb;line-height:1.33;margin-bottom:8px;white-space:pre-wrap;word-wrap:break-word;overflow-wrap:break-word;word-break:break-word;min-width:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
          ${escapeHtml(post.text)}
        </div>
        
        <!-- Compteurs (likes, commentaires) -->
        ${(likesCount > 0 || repliesCount > 0) ? `
          <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.1);margin-bottom:4px;">
            ${likesCount > 0 ? `
              <div style="display:flex;align-items:center;gap:4px;font-size:13px;color:#b0b3b8;">
                <span style="font-size:16px;">👍</span>
                <span>${likesCount}</span>
              </div>
            ` : '<div></div>'}
            ${repliesCount > 0 ? `
              <div style="font-size:13px;color:#b0b3b8;cursor:pointer;" onclick="document.getElementById('reply-form-${post.id}').style.display='block';document.getElementById('reply-input-${post.id}').focus();">
                ${repliesCount} commentaire${repliesCount > 1 ? 's' : ''}
              </div>
            ` : '<div></div>'}
          </div>
        ` : ''}
        
        <!-- Actions du post (Like, Commenter) style Facebook -->
        <div style="display:flex;align-items:center;gap:4px;padding:4px 0;border-top:1px solid rgba(255,255,255,0.1);">
          <button onclick="togglePostLike('${type}', '${id}', '${post.id}')" style="flex:1;display:flex;align-items:center;justify-content:center;gap:6px;background:none;border:none;color:${isLiked ? '#1877f2' : '#b0b3b8'};font-size:14px;font-weight:600;cursor:pointer;padding:6px;border-radius:4px;transition:all 0.15s;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='none'">
            <span style="font-size:18px;">${isLiked ? '👍' : '👍'}</span>
            <span>J'aime</span>
          </button>
          <button onclick="showReplyForm('${post.id}')" style="flex:1;display:flex;align-items:center;justify-content:center;gap:6px;background:none;border:none;color:#b0b3b8;font-size:14px;font-weight:600;cursor:pointer;padding:6px;border-radius:4px;transition:all 0.15s;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='none'">
            <span style="font-size:18px;">💬</span>
            <span>Commenter</span>
          </button>
        </div>
        
        <!-- Formulaire de réponse (caché par défaut) style Facebook -->
        <div id="reply-form-${post.id}" style="display:none;margin-top:8px;padding-top:8px;">
          <div style="display:flex;gap:8px;align-items:flex-start;">
            <div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#1877f2,#42a5f5);display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;font-weight:700;color:#fff;">
              ${currentUser?.avatar || '👤'}
            </div>
            <div style="flex:1;position:relative;">
              <textarea id="reply-input-${post.id}" placeholder="Écrivez un commentaire..." style="width:100%;min-height:36px;max-height:100px;padding:8px 12px;border-radius:20px;border:none;background:rgba(15,23,42,0.8);color:#e4e6eb;font-size:14px;resize:none;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;line-height:1.33;" onkeydown="if(event.key==='Enter' && !event.shiftKey) { event.preventDefault(); submitReply('${type}', '${id}', '${post.id}'); }" oninput="this.style.height='auto';this.style.height=Math.min(this.scrollHeight,100)+'px';"></textarea>
            </div>
          </div>
        </div>
        
        <!-- Réponses au post (style Facebook - triées chronologiquement) -->
        ${post.replies && post.replies.length > 0 ? `
          <div style="margin-top:8px;">
            ${(() => {
              // Trier les réponses par timestamp (plus anciennes en premier, comme Facebook)
              const sortedReplies = [...post.replies].sort((a, b) => (a.timestamp || 0) - (b.timestamp || 0));
              const totalReplies = countAllReplies(sortedReplies);
              const maxVisible = 3; // Afficher seulement 3 réponses par défaut
              const visibleReplies = sortedReplies.slice(0, maxVisible);
              const hiddenCount = sortedReplies.length - maxVisible;
              
              // Vérifier si on doit afficher toutes les réponses
              const showAllKey = `showAllReplies_${type}_${id}_${post.id}_`;
              const showAll = sessionStorage.getItem(showAllKey) === 'true';
              const finalVisibleReplies = showAll ? sortedReplies : visibleReplies;
              const finalHiddenCount = showAll ? 0 : hiddenCount;
              
              return `
                ${finalVisibleReplies.map(reply => {
                  // Vérifier si les réponses imbriquées doivent être affichées
                  const nestedShowAllKey = `showAllNestedReplies_${type}_${id}_${post.id}_${reply.id}`;
                  const nestedShowAll = sessionStorage.getItem(nestedShowAllKey) === 'true';
                  return renderReply(reply, post.id, '', 0, nestedShowAll);
                }).join('')}
                ${finalHiddenCount > 0 ? `
                  <button onclick="showAllReplies('${post.id}', '')" style="background:none;border:none;color:#1877f2;font-size:13px;font-weight:600;cursor:pointer;padding:4px 0;margin-top:4px;margin-left:48px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;" onmouseover="this.style.textDecoration='underline'" onmouseout="this.style.textDecoration='none'">
                    Voir ${finalHiddenCount} réponse${finalHiddenCount > 1 ? 's' : ''} supplémentaire${finalHiddenCount > 1 ? 's' : ''}
                  </button>
                ` : ''}
              `;
            })()}
          </div>
        ` : ''}
      </div>
    `;
  };
  
  // Stocker le type et id pour pouvoir revenir à la popup
  window.currentDiscussionType = type;
  window.currentDiscussionId = id;
  
  const html = `
    <div style="display:flex;flex-direction:column;height:100%;max-height:90vh;">
      <!-- En-tête style Facebook -->
      <div style="display:flex;align-items:center;gap:12px;padding:16px 20px;border-bottom:1px solid rgba(255,255,255,0.1);background:var(--ui-card-bg, #0f172a);flex-shrink:0;">
        <button onclick="closeDiscussionAndReturnToPopup()" style="background:none;border:none;color:#b0b3b8;font-size:20px;cursor:pointer;padding:4px;border-radius:50%;width:36px;height:36px;display:flex;align-items:center;justify-content:center;transition:all 0.15s;" onmouseover="this.style.background='rgba(255,255,255,0.1)';this.style.color='#fff'" onmouseout="this.style.background='none';this.style.color='#b0b3b8'">←</button>
        <div style="flex:1;">
          <div style="font-weight:600;font-size:16px;color:#e4e6eb;">Discussion</div>
          <div style="font-size:13px;color:#b0b3b8;">${esc(itemTitle)}</div>
        </div>
        <button onclick="closeDiscussionAndReturnToPopup()" style="background:none;border:none;color:#b0b3b8;font-size:20px;cursor:pointer;padding:4px;border-radius:50%;width:36px;height:36px;display:flex;align-items:center;justify-content:center;transition:all 0.15s;" onmouseover="this.style.background='rgba(239,68,68,0.2)';this.style.color='#ef4444'" onmouseout="this.style.background='none';this.style.color='#b0b3b8'">✕</button>
      </div>
      
      <!-- Zone de scroll avec posts -->
      <div id="discussion-posts-container" style="flex:1;overflow-y:auto;overflow-x:hidden;padding:16px 20px;background:var(--ui-card-bg, #020617);">
        ${posts.length > 0 ? posts.map(p => renderPost(p)).join('') : `
          <div style="text-align:center;padding:80px 20px;color:#b0b3b8;font-size:14px;">
            <div style="font-size:64px;margin-bottom:16px;opacity:0.5;">💬</div>
            <div style="font-weight:600;margin-bottom:8px;color:#e4e6eb;font-size:16px;">Aucune publication</div>
            <div style="font-size:13px;color:#b0b3b8;">Soyez le premier à partager quelque chose !</div>
          </div>
        `}
      </div>
      
      <!-- Zone de création de post (fixe en bas) style Facebook -->
      <div style="padding:12px 20px;border-top:1px solid rgba(255,255,255,0.1);background:var(--ui-card-bg);flex-shrink:0;">
        <div style="display:flex;gap:8px;align-items:flex-end;">
          <div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#1877f2,#42a5f5);display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;font-weight:700;color:#fff;">
            ${currentUser?.avatar || '👤'}
          </div>
          <div style="flex:1;position:relative;">
            <textarea id="discussion-input" placeholder="Écrivez un commentaire..." style="width:100%;min-height:38px;max-height:120px;padding:8px 12px;border-radius:20px;border:1px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.8);color:#e4e6eb;font-size:15px;resize:none;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;line-height:1.33;" onkeydown="if(event.key==='Enter' && !event.shiftKey) { event.preventDefault(); submitDiscussionComment('${type}', '${id}'); }" oninput="this.style.height='auto';this.style.height=Math.min(this.scrollHeight,120)+'px';"></textarea>
          </div>
          <button onclick="submitDiscussionComment('${type}', '${id}')" style="padding:8px 16px;border-radius:18px;border:none;background:#1877f2;color:#fff;cursor:pointer;font-size:14px;font-weight:600;transition:all 0.2s;flex-shrink:0;" onmouseover="this.style.background='#166fe5'" onmouseout="this.style.background='#1877f2'">
            Publier
          </button>
        </div>
      </div>
    </div>
  `;
  
  // Ouvrir la discussion : dans la popup si ouverte, sinon modal central visible
  const popupBackdrop = document.getElementById("popup-modal-backdrop");
  const popupContent = document.getElementById("popup-modal-content");
  const publishInner = document.getElementById("publish-modal-inner");
  const publishBackdrop = document.getElementById("publish-modal-backdrop");
  
  const popupIsOpen = popupBackdrop && popupContent && (popupBackdrop.style.display === "flex" || popupBackdrop.contains(popupContent));
  
  if (popupBackdrop && popupContent && popupIsOpen) {
    window.discussionOpenedInPopup = true;
    popupContent.innerHTML = html;
    popupContent.style.maxHeight = "85vh";
    popupContent.style.overflow = "hidden";
    popupContent.style.display = "flex";
    popupContent.style.flexDirection = "column";
    popupContent.style.visibility = "visible";
    popupContent.style.opacity = "1";
    // Forcer la fenêtre visible immédiatement
    popupBackdrop.style.display = "flex";
    popupBackdrop.style.visibility = "visible";
    popupBackdrop.style.opacity = "1";
    popupBackdrop.style.zIndex = "99999";
    popupBackdrop.style.pointerEvents = "auto";
  } else if (publishInner && publishBackdrop) {
    window.discussionOpenedInPopup = false;
    publishInner.innerHTML = html;
    publishBackdrop.setAttribute('data-auth-modal', 'true');
    publishBackdrop.style.display = "flex";
    publishBackdrop.style.visibility = "visible";
    publishBackdrop.style.opacity = "1";
    publishBackdrop.style.zIndex = "99999";
    publishBackdrop.style.pointerEvents = "auto";
    publishBackdrop.style.paddingTop = "40px";
    publishBackdrop.style.paddingBottom = "40px";
    publishBackdrop.style.boxSizing = "border-box";
    const publishModal = document.getElementById("publish-modal");
    if (publishModal) {
      publishModal.style.display = "block";
      publishModal.style.visibility = "visible";
      publishModal.style.opacity = "1";
    }
  }
  
  setTimeout(() => {
    const input = document.getElementById("discussion-input");
    if (input) input.focus();
  }, 100);
}

// Fermer la discussion et retourner à la popup de l'événement
function closeDiscussionAndReturnToPopup() {
  const type = window.currentDiscussionType;
  const id = window.currentDiscussionId;
  const openedInPopup = window.discussionOpenedInPopup;
  
  if (type && id) {
    const item = getItemById(type, id);
    if (item) {
      let popupHtml = "";
      if (type === "event") popupHtml = buildEventPopup(item);
      else if (type === "booking") popupHtml = buildBookingPopup(item);
      else if (type === "service") popupHtml = buildServicePopup(item);
      
      if (popupHtml) openPopupModal(popupHtml, item);
    }
  }
  
  if (!openedInPopup && typeof closePublishModal === "function") closePublishModal();
}

window.closeDiscussionAndReturnToPopup = closeDiscussionAndReturnToPopup;

// Helper : Sauvegarder les posts de discussion en API (avec fallback localStorage)
async function saveDiscussionToAPI(type, id, posts) {
  try {
    const resp = await fetch(`${window.API_BASE_URL}/discussions/${type}/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ posts })
    });
    if (resp.ok) {
      console.log('[Discussion] Sauvegarde API OK');
      // Nettoyer localStorage si migration OK
      try { localStorage.removeItem(`discussion_${type}_${id}`); } catch(e) {}
      return true;
    }
  } catch(e) {
