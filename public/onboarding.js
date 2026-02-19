// ============================================================
// onboarding.js
// Système d'onboarding complet (checkProfileCompleteness, openOnboardingModal, uploadProfilePhoto)
// Extrait de map_logic.js (lignes 14326-14990)
// ============================================================

// SYSTÈME D'ONBOARDING COMPLET
// ============================================
// Vérifie si le profil est complet et lance l'onboarding si nécessaire

/**
 * Vérifie si le profil utilisateur est complet
 * @returns {Object} { isComplete: boolean, missingSteps: string[] }
 */
function checkProfileCompleteness(user) {
  const missingSteps = [];
  
  // Vérifier la photo de profil
  if (!user.profile_photo_url || user.profile_photo_url === '' || user.profile_photo_url === '👤') {
    missingSteps.push('photo');
  }
  
  // Vérifier l'adresse postale (doit être vérifiée)
  if (!user.address_verified || !user.address_lat || !user.address_lng) {
    missingSteps.push('address');
  }
  
  return {
    isComplete: missingSteps.length === 0,
    missingSteps: missingSteps
  };
}

/**
 * Démarre l'onboarding si le profil est incomplet
 * @param {Object} user - L'utilisateur connecté
 * @param {boolean} force - Forcer l'onboarding même si le profil est complet
 */
function startOnboardingIfNeeded(user, force = false) {
  if (!user || !user.isLoggedIn) {
    return;
  }
  
  const profileCheck = checkProfileCompleteness(user);
  
  if (force || !profileCheck.isComplete) {
    console.log('[ONBOARDING] Profil incomplet, demarrage onboarding. Etapes manquantes:', profileCheck.missingSteps);
    openOnboardingModal(profileCheck.missingSteps);
  } else {
    console.log('[ONBOARDING] Profil complet, pas d\'onboarding necessaire');
  }
}

/**
 * Ouvre le modal d'onboarding avec les étapes manquantes
 * @param {string[]} missingSteps - Liste des étapes manquantes ['photo', 'address']
 */
function openOnboardingModal(missingSteps = []) {
  console.log('[ONBOARDING] Ouverture modal onboarding, etapes:', missingSteps);
  console.log('[ONBOARDING] missingSteps.length:', missingSteps.length);
  
  let backdrop = document.getElementById('publish-modal-backdrop');
  let modal = document.getElementById('publish-modal-inner');
  
  if (!backdrop || !modal) {
    console.warn('[ONBOARDING] Modal elements not found - creation...');
    // Créer les éléments si ils n'existent pas
    if (!backdrop) {
      backdrop = document.createElement('div');
      backdrop.id = 'publish-modal-backdrop';
      backdrop.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.8);backdrop-filter:blur(8px);z-index:99998;display:flex;align-items:center;justify-content:center;';
      backdrop.onclick = function(e) {
        if (e.target === backdrop) closePublishModal();
      };
      document.body.appendChild(backdrop);
      console.log('[ONBOARDING] Backdrop cree');
    }
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'publish-modal-inner';
      modal.style.cssText = 'position:relative;max-width:90vw;max-height:90vh;overflow-y:auto;';
      if (backdrop) backdrop.appendChild(modal);
      console.log('[ONBOARDING] Modal inner cree');
    }
  }
  
  if (!backdrop || !modal) {
    console.error('[ONBOARDING] ERREUR: Impossible de creer les elements modal');
    return;
  }
  
  // Déterminer l'étape actuelle
  let currentStep = 0;
  if (missingSteps.includes('photo')) {
    currentStep = 1; // Étape photo
  } else if (missingSteps.includes('address')) {
    currentStep = 2; // Étape adresse
  }
  
  // Générer le HTML pour l'étape actuelle
  let stepHTML = '';
  let stepTitle = '';
  let stepSubtitle = '';
  
  if (currentStep === 1) {
    // Étape photo
    stepTitle = '📸 Ajoutez votre photo de profil';
    stepSubtitle = 'Votre photo vous aidera à être reconnu(e) par la communauté MapEvent';
    stepHTML = renderOnboardingPhotoStep();
  } else if (currentStep === 2) {
    // Étape adresse
    stepTitle = '📍 Vérifiez votre adresse postale';
    stepSubtitle = 'Votre adresse nous permet de vous envoyer des alertes personnalisées pour les événements près de chez vous';
    stepHTML = renderOnboardingAddressStep();
  } else {
    // Toutes les étapes sont complètes
    stepTitle = '✅ Profil complété !';
    stepSubtitle = 'Votre profil est maintenant complet. Vous pouvez accéder à toutes les fonctionnalités.';
    stepHTML = renderOnboardingCompleteStep();
  }
  
  const html = `
    <div id="onboardingModal" class="onboarding-modal" data-onboarding="true" data-step="${currentStep}" data-onboarding-active="true" style="padding:40px;max-width:500px;margin:0 auto;text-align:center;">
      <!-- Indicateur de progression -->
      <div style="margin-bottom:32px;">
        <div style="display:flex;justify-content:center;gap:8px;margin-bottom:16px;">
          <div style="width:40px;height:4px;background:${currentStep >= 1 ? '#00ffc3' : 'rgba(255,255,255,0.2)'};border-radius:2px;"></div>
          <div style="width:40px;height:4px;background:${currentStep >= 2 ? '#00ffc3' : 'rgba(255,255,255,0.2)'};border-radius:2px;"></div>
        </div>
        <h2 style="margin:0 0 8px;font-size:24px;font-weight:800;color:#fff;">${stepTitle}</h2>
        <p style="margin:0;font-size:14px;color:var(--ui-text-muted);">${stepSubtitle}</p>
      </div>
      
      ${stepHTML}
    </div>
  `;
  
  modal.innerHTML = html;
  backdrop.style.display = "flex";
  
  // Attacher les event listeners après injection
  attachOnboardingEventListeners(currentStep);
}

/**
 * Génère le HTML pour l'étape photo
 */
function renderOnboardingPhotoStep() {
  return `
    <div style="text-align:left;">
      <!-- Zone d'upload -->
      <div id="photo-upload-zone" style="border:2px dashed rgba(0,255,195,0.5);border-radius:12px;padding:40px;text-align:center;background:rgba(0,255,195,0.05);margin-bottom:20px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(0,255,195,0.8)';this.style.background='rgba(0,255,195,0.1)';" onmouseout="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(0,255,195,0.05)';">
        <div style="font-size:48px;margin-bottom:12px;">📷</div>
        <div style="color:var(--ui-text-main);margin-bottom:8px;font-weight:600;">Cliquez pour sélectionner une photo</div>
        <div style="color:var(--ui-text-muted);font-size:12px;">JPG, PNG ou GIF (max 5MB)</div>
        <input type="file" id="onboarding-photo-input" accept="image/*" style="display:none;" onchange="handleOnboardingPhotoUpload(event)">
      </div>
      
      <!-- Preview de la photo -->
      <div id="photo-preview-container" style="display:none;margin-bottom:20px;">
        <img id="photo-preview" src="" style="width:150px;height:150px;border-radius:50%;object-fit:cover;border:3px solid #00ffc3;margin:0 auto;display:block;">
      </div>
      
      <!-- Option "Plus tard" -->
      <div style="margin-bottom:20px;">
        <label style="display:flex;align-items:center;gap:8px;cursor:pointer;color:var(--ui-text-muted);font-size:13px;">
          <input type="checkbox" id="photo-later-checkbox" style="cursor:pointer;">
          <span>Ajouter ma photo plus tard</span>
        </label>
      </div>
      
      <!-- Boutons -->
      <div style="display:flex;gap:12px;">
        <button id="onboarding-skip-photo" style="flex:1;padding:12px;border-radius:12px;border:1px solid rgba(255,255,255,0.2);background:transparent;color:var(--ui-text-muted);font-weight:600;cursor:pointer;">Passer</button>
        <button id="onboarding-continue-photo" style="flex:1;padding:12px;border-radius:12px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:700;cursor:pointer;display:none;">Continuer</button>
      </div>
    </div>
  `;
}

/**
 * Génère le HTML pour l'étape adresse
 */
function renderOnboardingAddressStep() {
  return `
    <div style="text-align:left;">
      <!-- Champ adresse avec autocomplete -->
      <div style="margin-bottom:16px;">
        <label style="display:block;font-size:13px;font-weight:600;color:var(--ui-text-main);margin-bottom:8px;">📍 Adresse postale</label>
        <input type="text" id="onboarding-address-input" placeholder="Commencez à taper votre adresse..." style="width:100%;padding:12px 16px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:var(--ui-text-main);font-size:14px;">
        <div id="address-suggestions" style="margin-top:8px;display:none;max-height:200px;overflow-y:auto;background:rgba(15,23,42,0.9);border-radius:8px;border:1px solid rgba(255,255,255,0.1);"></div>
      </div>
      
      <!-- Adresse sélectionnée (affichée après sélection) -->
      <div id="selected-address-display" style="display:none;padding:12px;background:rgba(0,255,195,0.1);border:1px solid rgba(0,255,195,0.3);border-radius:10px;margin-bottom:16px;">
        <div style="display:flex;align-items:start;gap:8px;">
          <span style="font-size:20px;">✅</span>
          <div style="flex:1;">
            <div style="font-weight:600;color:#00ffc3;margin-bottom:4px;" id="selected-address-label"></div>
            <div style="font-size:12px;color:var(--ui-text-muted);" id="selected-address-details"></div>
          </div>
        </div>
      </div>
      
      <!-- Option "Plus tard" -->
      <div style="margin-bottom:20px;">
        <label style="display:flex;align-items:center;gap:8px;cursor:pointer;color:var(--ui-text-muted);font-size:13px;">
          <input type="checkbox" id="address-later-checkbox" style="cursor:pointer;">
          <span>Vérifier mon adresse plus tard</span>
        </label>
      </div>
      
      <!-- Boutons -->
      <div style="display:flex;gap:12px;">
        <button id="onboarding-skip-address" style="flex:1;padding:12px;border-radius:12px;border:1px solid rgba(255,255,255,0.2);background:transparent;color:var(--ui-text-muted);font-weight:600;cursor:pointer;">Passer</button>
        <button id="onboarding-continue-address" style="flex:1;padding:12px;border-radius:12px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:700;cursor:pointer;display:none;">Continuer</button>
      </div>
    </div>
  `;
}

/**
 * Génère le HTML pour l'étape complétée
 */
function renderOnboardingCompleteStep() {
  return `
    <div style="text-align:center;">
      <div style="font-size:64px;margin-bottom:16px;">🎉</div>
      <p style="color:var(--ui-text-main);margin-bottom:24px;">Votre profil est maintenant complet !</p>
      <button id="onboarding-finish" style="width:100%;padding:14px;border-radius:12px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:700;cursor:pointer;">Commencer à explorer</button>
    </div>
  `;
}

/**
 * Attache les event listeners pour l'onboarding
 */
function attachOnboardingEventListeners(step) {
  if (step === 1) {
    // Étape photo
    const uploadZone = document.getElementById('photo-upload-zone');
    const photoInput = document.getElementById('onboarding-photo-input');
    const skipBtn = document.getElementById('onboarding-skip-photo');
    const continueBtn = document.getElementById('onboarding-continue-photo');
    const laterCheckbox = document.getElementById('photo-later-checkbox');
    
    if (uploadZone && photoInput) {
      uploadZone.addEventListener('click', () => photoInput.click());
    }
    
    if (skipBtn) {
      skipBtn.addEventListener('click', () => {
        skipOnboardingStep('photo');
      });
    }
    
    if (continueBtn) {
      continueBtn.addEventListener('click', () => {
        continueOnboardingStep('photo');
      });
    }
    
    if (laterCheckbox) {
      laterCheckbox.addEventListener('change', (e) => {
        if (e.target.checked) {
          skipOnboardingStep('photo');
        }
      });
    }
  } else if (step === 2) {
    // Étape adresse
    const addressInput = document.getElementById('onboarding-address-input');
    const skipBtn = document.getElementById('onboarding-skip-address');
    const continueBtn = document.getElementById('onboarding-continue-address');
    const laterCheckbox = document.getElementById('address-later-checkbox');
    
    if (addressInput) {
      // Intégrer l'autocomplete d'adresse (OpenStreetMap/Nominatim)
      setupAddressAutocomplete(addressInput);
    }
    
    if (skipBtn) {
      skipBtn.addEventListener('click', () => {
        skipOnboardingStep('address');
      });
    }
    
    if (continueBtn) {
      continueBtn.addEventListener('click', () => {
        continueOnboardingStep('address');
      });
    }
    
    if (laterCheckbox) {
      laterCheckbox.addEventListener('change', (e) => {
        if (e.target.checked) {
          skipOnboardingStep('address');
        }
      });
    }
  } else {
    // Étape complétée
    const finishBtn = document.getElementById('onboarding-finish');
    if (finishBtn) {
      finishBtn.addEventListener('click', () => {
        closePublishModal();
        showNotification('🎉 Bienvenue sur MapEvent !', 'success');
      });
    }
  }
}

/**
 * Gère l'upload de photo dans l'onboarding
 */
window.handleOnboardingPhotoUpload = function(event) {
  const file = event.target.files[0];
  if (!file) return;
  
  if (file.size > 5 * 1024 * 1024) {
    showNotification('⚠️ La photo doit faire moins de 5MB', 'warning');
    return;
  }
  
  const reader = new FileReader();
  reader.onload = function(e) {
    const previewContainer = document.getElementById('photo-preview-container');
    const previewImg = document.getElementById('photo-preview');
    const continueBtn = document.getElementById('onboarding-continue-photo');
    
    if (previewImg) {
      previewImg.src = e.target.result;
    }
    if (previewContainer) {
      previewContainer.style.display = 'block';
    }
    if (continueBtn) {
      continueBtn.style.display = 'block';
    }
    
    // Stocker temporairement la photo pour l'upload
    window.onboardingPhotoData = e.target.result;
    window.onboardingPhotoFile = file;
  };
  reader.readAsDataURL(file);
};

/**
 * Passe à l'étape suivante de l'onboarding
 */
function continueOnboardingStep(step) {
  if (step === 'photo') {
    // Uploader la photo
    if (window.onboardingPhotoData && window.onboardingPhotoFile) {
      uploadProfilePhoto(window.onboardingPhotoFile).then(() => {
        // Passer à l'étape suivante
        const missingSteps = checkProfileCompleteness(currentUser).missingSteps;
        if (missingSteps.includes('address')) {
          openOnboardingModal(['address']);
        } else {
          openOnboardingModal([]); // Afficher l'étape complétée
        }
      }).catch(error => {
        console.error('[ONBOARDING] Erreur upload photo:', error);
        showNotification('⚠️ Erreur lors de l\'upload de la photo', 'error');
      });
    }
  } else if (step === 'address') {
    // Sauvegarder l'adresse
    const selectedAddress = window.onboardingSelectedAddress;
    if (selectedAddress) {
      saveUserAddress(selectedAddress).then(() => {
        // Afficher l'étape complétée
        openOnboardingModal([]);
      }).catch(error => {
        console.error('[ONBOARDING] Erreur sauvegarde adresse:', error);
        showNotification('⚠️ Erreur lors de la sauvegarde de l\'adresse', 'error');
      });
    }
  }
}

/**
 * Passe l'étape de l'onboarding
 */
function skipOnboardingStep(step) {
  if (step === 'photo') {
    // Marquer comme "plus tard"
    const missingSteps = checkProfileCompleteness(currentUser).missingSteps.filter(s => s !== 'photo');
    if (missingSteps.length > 0) {
      openOnboardingModal(missingSteps);
    } else {
      openOnboardingModal([]); // Afficher l'étape complétée
    }
  } else if (step === 'address') {
    // Marquer comme "plus tard" (address_verified = false)
    const missingSteps = checkProfileCompleteness(currentUser).missingSteps.filter(s => s !== 'address');
    if (missingSteps.length > 0) {
      openOnboardingModal(missingSteps);
    } else {
      openOnboardingModal([]); // Afficher l'étape complétée
    }
  }
}

/**
 * Upload la photo de profil vers S3
 */
async function uploadProfilePhoto(file) {
  console.log('[ONBOARDING] Upload photo vers S3...');
  
  const accessToken = getAuthToken();
  if (!accessToken) {
    throw new Error('Non authentifié');
  }
  
  // Convertir le fichier en base64
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = async function(e) {
      const base64Data = e.target.result;
      
      try {
        const response = await fetch(`${window.API_BASE_URL}/user/upload-photo`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`
          },
          body: JSON.stringify({
            photo: base64Data
          })
        });
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ error: 'Erreur inconnue' }));
          throw new Error(errorData.error || 'Erreur upload photo');
        }
        
        const data = await response.json();
        const photoUrl = data.photo_url || data.user?.profile_photo_url;
        
        if (!photoUrl) {
          throw new Error('URL photo non retournée par le serveur');
        }
        
        // Mettre à jour currentUser
        currentUser.profile_photo_url = photoUrl;
        safeSetItem('currentUser', JSON.stringify(currentUser));
        
        console.log('[ONBOARDING] Photo uploadée avec succès:', photoUrl);
        resolve(photoUrl);
      } catch (error) {
        console.error('[ONBOARDING] Erreur upload photo:', error);
        reject(error);
      }
    };
    reader.onerror = function(error) {
      reject(new Error('Erreur lecture fichier'));
    };
    reader.readAsDataURL(file);
  });
}

/**
 * Sauvegarde l'adresse de l'utilisateur
 */
async function saveUserAddress(addressData) {
  const accessToken = getAuthToken();
  if (!accessToken) {
    throw new Error('Non authentifié');
  }
  
  const response = await fetch(`${window.API_BASE_URL}/user/address`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`
    },
    body: JSON.stringify({
      address_label: addressData.label,
      address_lat: addressData.lat,
      address_lng: addressData.lng,
      address_country_code: addressData.country_code,
      address_city: addressData.city,
      address_postcode: addressData.postcode,
      address_street: addressData.street,
      address_verified: true
    })
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Erreur inconnue' }));
    throw new Error(errorData.error || 'Erreur sauvegarde adresse');
  }
  
  const data = await response.json();
  // Mettre à jour currentUser avec les données retournées
  if (data.user) {
    Object.assign(currentUser, data.user);
    safeSetItem('currentUser', JSON.stringify(currentUser));
  }
  
  console.log('[ONBOARDING] Adresse sauvegardée avec succès');
}

/**
 * Configure l'autocomplete d'adresse avec OpenStreetMap/Nominatim
 */
function setupAddressAutocomplete(inputElement) {
  let timeout;
  const suggestionsContainer = document.getElementById('address-suggestions');
  
  inputElement.addEventListener('input', function(e) {
    const query = e.target.value.trim();
    
    clearTimeout(timeout);
    
    if (query.length < 3) {
      if (suggestionsContainer) {
        suggestionsContainer.style.display = 'none';
      }
      return;
    }
    
    // OPTIMISATION: Debounce réduit à 300ms pour réactivité améliorée
    timeout = setTimeout(async () => {
      try {
        // VALIDATION STRICTE + PERFORMANCE: Paramètres optimisés pour recherche rapide et exacte
        // addressdetails=1 pour validation complète, limit=5 pour rapidité, language=fr pour pertinence, dedupe=1 pour éviter doublons
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
          console.warn('[ONBOARDING] Nominatim erreur HTTP:', response.status, response.statusText);
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
          console.error('[ONBOARDING] Erreur parsing JSON Nominatim:', parseError, 'Response:', text.substring(0, 100));
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
            <div class="address-suggestion" style="padding:12px;cursor:pointer;border-bottom:1px solid rgba(255,255,255,0.1);transition:background 0.2s;"
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
                <div style="font-weight:600;color:var(--ui-text-main);flex:1;">${result.display_name}</div>
              </div>
              <div style="font-size:11px;color:var(--ui-text-muted);padding-left:22px;">${result.address?.country || ''}${result.address?.postcode ? ' • ' + result.address.postcode : ''}</div>
            </div>
          `;
          }).join('');
          
          suggestionsContainer.style.display = 'block';
          
          // Attacher les event listeners aux suggestions
          suggestionsContainer.querySelectorAll('.address-suggestion').forEach(suggestion => {
            suggestion.addEventListener('click', function() {
              selectAddressSuggestion({
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
        console.error('[ONBOARDING] Erreur autocomplete adresse:', error);
      }
    }, 300);
  });
}

/**
 * Sélectionne une adresse depuis les suggestions
 */
function selectAddressSuggestion(addressData) {
  window.onboardingSelectedAddress = addressData;
  
  const input = document.getElementById('onboarding-address-input');
  const suggestionsContainer = document.getElementById('address-suggestions');
  const selectedDisplay = document.getElementById('selected-address-display');
  const selectedLabel = document.getElementById('selected-address-label');
  const selectedDetails = document.getElementById('selected-address-details');
  const continueBtn = document.getElementById('onboarding-continue-address');
  
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
  if (continueBtn) {
    continueBtn.style.display = 'block';
  }
}

// Exposer les fonctions globalement
window.handleOnboardingPhotoUpload = handleOnboardingPhotoUpload;
window.startOnboardingIfNeeded = startOnboardingIfNeeded;
window.startOnboarding = startOnboardingIfNeeded; // Alias
window.openOnboardingModal = openOnboardingModal;
window.checkProfileCompleteness = checkProfileCompleteness;

// Hook de test pour ouvrir l'onboarding directement (sans login)
// Usage: window.testOnboarding() ou window.testOnboarding(['photo']) ou window.testOnboarding(['address'])
window.testOnboarding = function(missingSteps = ['photo', 'address']) {
  console.log('[ONBOARDING] Hook de test: testOnboarding() appelé avec missingSteps:', missingSteps);
  if (typeof openOnboardingModal === 'function') {
    return openOnboardingModal(missingSteps);
  } else {
    console.error('[ONBOARDING] openOnboardingModal n\'est pas disponible');
  }
};

// Exposer les fonctions globalement IMMÉDIATEMENT après leur définition
