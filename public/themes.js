// ============================================================
// themes.js - Themes UI & carte (color picker, hsvToRgb, drawSVCanvas, cycleUITheme, cycleMapTheme, applyMapTheme)
// Extrait de map_logic.js pour meilleure lisibilité
// ============================================================

        // Récupérer l'URL de l'image uploadée vers S3
        if (result.image_url) {
          data.newItem.image_url = result.image_url;
          data.newItem.imageUrl = result.image_url;
          console.log('[PUBLISH] ✅ Image URL S3 reçue:', result.image_url.substring(0, 80) + '...');
        }
      } catch (e) {
        console.warn('[PUBLISH] Impossible de parser la réponse:', e);
      }
      console.log('[PUBLISH] ✅ Événement créé avec succès dans le backend');
    } else {
      console.error('[PUBLISH] ❌ Erreur backend:', response.status, responseText);
      showNotification(`❌ Erreur serveur (${response.status}): ${responseText}`, "error");
    }
  } catch (error) {
    console.error('[PUBLISH] ❌ Erreur réseau:', error);
    showNotification("❌ Erreur réseau lors de la publication. Vérifiez votre connexion.", "error");
  }
  
  // Ajouter aux données locales SEULEMENT si backend OK
  if (backendSuccess) {
    if (data.mode === "event") {
      eventsData.push(data.newItem);
    } else if (data.mode === "booking") {
      bookingsData.push(data.newItem);
    } else if (data.mode === "service") {
      servicesData.push(data.newItem);
    }
    
    // Fermer le modal et rafraîchir
    closePublishModal();
    refreshMarkers();
    refreshListView();
    
    // Centrer la carte sur le nouveau point
    if (map && data.lat && data.lng) {
      map.setView([data.lat, data.lng], 14);
    }
    
    // Message de succès
    showNotification(`✅ Paiement reçu ! ${data.mode === 'event' ? 'Événement' : data.mode === 'booking' ? 'Booking' : 'Service'} publié avec succès !`, "success");
  }
  
  // Nettoyer dans tous les cas
  window.pendingPublishData = null;
}

// ============================================
// THÈMES UI + MAP
// ============================================
// VERROUILLÉ: Le fond reste TOUJOURS noir. Seuls les pointeurs, le bouton Publier et le halo du logo changent.
function cycleUITheme() {
  // Ne fait plus rien - le fond reste noir, les couleurs se changent via le color picker
  openColorPickerModal();
}

function applyUITheme(i) {
  // VERROUILLÉ: on ne change PLUS les variables CSS globales (fond, cartes, popups, filtres = toujours noir)
  // Seul applyCustomColors() modifie les éléments autorisés
  applyCustomColors();
}

// Appliquer les couleurs custom UNIQUEMENT sur : pointeurs regroupés, bouton Publier, halo logo
// JAMAIS sur : fond, popups, filtres, blocs intérieurs, topbar, textes
function applyCustomColors() {
  const cfg = window.customThemeConfig;
  if (!cfg) return;
  
  // 1. Bouton Publier - seulement le fond du bouton
  if (cfg.markerColors && cfg.markerColors.length > 0) {
    const publishBtn = document.getElementById('map-publish-btn');
    if (publishBtn) {
      const grad = cfg.markerColors.length > 1
        ? `linear-gradient(135deg, ${cfg.markerColors.join(', ')})`
        : cfg.markerColors[0];
      publishBtn.style.background = grad;
    }
  }
  
  // 2. Halo du logo - suit la couleur accent du marqueur
  if (cfg.markerColors && cfg.markerColors.length > 0) {
    const haloColor = cfg.markerColors[0];
    const halo1 = document.getElementById('logo-halo-1');
    const halo2 = document.getElementById('logo-halo-2');
    if (halo1) halo1.setAttribute('stroke', haloColor);
    if (halo2) halo2.setAttribute('stroke', haloColor);
    // Gradient du logo SVG
    const stop0 = document.querySelector('#logoGrad stop:first-child');
    const stop1 = document.querySelector('#logoGrad stop:last-child');
    if (stop0) stop0.setAttribute('stop-color', cfg.markerColors[0]);
    if (stop1) stop1.setAttribute('stop-color', cfg.markerColors[cfg.markerColors.length > 1 ? 1 : 0]);
  }
  
  // 3. Les pointeurs regroupés (clusters + geo-clusters) sont gérés par getThemeMarkerColors() + iconCreateFunction + showGeoClusters
  // Pas besoin de code ici - ils lisent window.customThemeConfig directement
}

// ============================================
// COLOR PICKER PRO - HSV + Modal
// ============================================

// Conversion HSV -> RGB -> Hex
function hsvToRgb(h, s, v) {
  let r, g, b;
  const i = Math.floor(h / 60) % 6;
  const f = h / 60 - Math.floor(h / 60);
  const p = v * (1 - s);
  const q = v * (1 - f * s);
  const t = v * (1 - (1 - f) * s);
  switch (i) {
    case 0: r = v; g = t; b = p; break;
    case 1: r = q; g = v; b = p; break;
    case 2: r = p; g = v; b = t; break;
    case 3: r = p; g = q; b = v; break;
    case 4: r = t; g = p; b = v; break;
    case 5: r = v; g = p; b = q; break;
  }
  return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
}

function rgbToHex(r, g, b) {
  return '#' + [r, g, b].map(x => x.toString(16).padStart(2, '0')).join('');
}

function hexToRgb(hex) {
  hex = hex.replace('#', '');
  if (hex.length === 3) hex = hex.split('').map(c => c + c).join('');
  return [parseInt(hex.slice(0,2),16), parseInt(hex.slice(2,4),16), parseInt(hex.slice(4,6),16)];
}

function rgbToHsv(r, g, b) {
  r /= 255; g /= 255; b /= 255;
  const max = Math.max(r, g, b), min = Math.min(r, g, b);
  const d = max - min;
  let h = 0, s = max === 0 ? 0 : d / max, v = max;
  if (d !== 0) {
    switch (max) {
      case r: h = ((g - b) / d + (g < b ? 6 : 0)) * 60; break;
      case g: h = ((b - r) / d + 2) * 60; break;
      case b: h = ((r - g) / d + 4) * 60; break;
    }
  }
  return [h, s, v];
}

// Dessiner le carre SV sur un canvas
function drawSVCanvas(canvas, hue) {
  const ctx = canvas.getContext('2d');
  const w = canvas.width, h = canvas.height;
  for (let x = 0; x < w; x++) {
    for (let y = 0; y < h; y++) {
      const s = x / w;
      const v = 1 - y / h;
      const [r, g, b] = hsvToRgb(hue, s, v);
      ctx.fillStyle = `rgb(${r},${g},${b})`;
      ctx.fillRect(x, y, 1, 1);
    }
  }
}

// Dessiner le slider Hue (vertical arc-en-ciel)
function drawHueSlider(canvas) {
  const ctx = canvas.getContext('2d');
  const h = canvas.height;
  for (let y = 0; y < h; y++) {
    const hue = (y / h) * 360;
    const [r, g, b] = hsvToRgb(hue, 1, 1);
    ctx.fillStyle = `rgb(${r},${g},${b})`;
    ctx.fillRect(0, y, canvas.width, 1);
  }
}

// Variable globale du color picker
let _cpState = { hue: 0, sat: 1, val: 1, callback: null };

function openColorPickerModal() {
  // Fermer le settings modal si ouvert
  const settingsModal = document.getElementById('modal-overlay');
  if (settingsModal) settingsModal.style.display = 'none';
  
  // Config actuelle ou defaut
  const cfg = window.customThemeConfig || {
    markerColors: ['#00ffc3'],
    markerBorder: '#ffffff'
  };
  
  // Copie de travail (seulement marqueur)
  const draft = {
    markerColors: cfg.markerColors ? [...cfg.markerColors] : ['#00ffc3'],
    markerBorder: cfg.markerBorder || '#ffffff'
  };
  
  let existingModal = document.getElementById('color-picker-modal');
  if (existingModal) existingModal.remove();
  
  // Quel slot est actif pour le HSV picker
  let activeSlotType = null; // 'interior-0', 'interior-1', 'interior-2', 'border'
  
  const modal = document.createElement('div');
  modal.id = 'color-picker-modal';
  modal.style.cssText = 'position:fixed;inset:0;z-index:10000;background:rgba(0,0,0,0.8);display:flex;align-items:center;justify-content:center;backdrop-filter:blur(6px);';
  
  modal.innerHTML = `
    <div style="background:#0f172a;border-radius:18px;border:1px solid rgba(255,255,255,0.08);width:360px;max-width:92vw;max-height:88vh;overflow-y:auto;padding:20px;color:#e2e8f0;font-family:system-ui,-apple-system,sans-serif;">
      
      <!-- Header -->
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
        <span style="font-size:15px;font-weight:700;">Personnaliser le pointeur</span>
        <button id="cp-close" style="background:none;border:none;color:#64748b;font-size:20px;cursor:pointer;padding:2px 6px;line-height:1;">&times;</button>
      </div>
      
      <!-- PREVIEW LIVE du marqueur - cliquable pour voir le resultat -->
      <div style="text-align:center;margin-bottom:18px;padding:20px 16px;background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:14px;border:1px solid rgba(255,255,255,0.05);">
        <div id="cp-preview" style="display:flex;align-items:flex-end;justify-content:center;gap:20px;min-height:70px;"></div>
      </div>
      
      <!-- INTERIEUR DU MARQUEUR : 1-3 couleurs pour le degrade -->
      <div style="margin-bottom:16px;">
        <div style="font-size:11px;color:#94a3b8;margin-bottom:8px;font-weight:600;letter-spacing:0.3px;">COULEURS INTERIEUR <span style="color:#475569;font-weight:400;">(cliquer pour changer, + pour ajouter)</span></div>
        <div id="cp-interior-slots" style="display:flex;gap:8px;align-items:center;"></div>
      </div>
      
      <!-- BORDURE DU MARQUEUR -->
      <div style="margin-bottom:16px;">
        <div style="font-size:11px;color:#94a3b8;margin-bottom:8px;font-weight:600;letter-spacing:0.3px;">COULEUR BORDURE</div>
        <div id="cp-border-slot" style="display:flex;gap:8px;align-items:center;"></div>
      </div>
      
      <!-- HSV PICKER (apparait quand on clique sur un slot) -->
      <div id="cp-hsv-area" style="display:none;margin-bottom:16px;padding:14px;background:#1e293b;border-radius:12px;">
        <div style="display:flex;gap:10px;">
          <canvas id="cp-sv-canvas" width="200" height="200" style="border-radius:8px;cursor:crosshair;flex-shrink:0;"></canvas>
          <canvas id="cp-hue-slider" width="28" height="200" style="border-radius:8px;cursor:pointer;flex-shrink:0;"></canvas>
        </div>
        <div style="display:flex;align-items:center;gap:8px;margin-top:10px;">
          <div id="cp-swatch" style="width:30px;height:30px;border-radius:8px;border:2px solid rgba(255,255,255,0.2);flex-shrink:0;"></div>
          <input id="cp-hex" type="text" maxlength="7" style="background:#0f172a;border:1px solid rgba(255,255,255,0.1);border-radius:8px;color:#e2e8f0;padding:6px 10px;font-size:13px;font-family:monospace;width:85px;" placeholder="#00ffc3">
          <button id="cp-hex-ok" style="background:#334155;border:none;color:#e2e8f0;padding:6px 12px;border-radius:8px;font-size:12px;cursor:pointer;font-weight:600;">OK</button>
        </div>
      </div>
      
      <!-- BOUTONS -->
      <div style="display:flex;gap:10px;margin-top:4px;">
        <button id="cp-validate" style="flex:1;padding:11px;border-radius:12px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:700;font-size:13px;cursor:pointer;transition:transform 0.15s;" onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">Valider</button>
        <button id="cp-reset" style="padding:11px 16px;border-radius:12px;border:1px solid rgba(255,255,255,0.1);background:transparent;color:#64748b;font-size:12px;cursor:pointer;">Reset</button>
      </div>
    </div>
  `;
  
  document.body.appendChild(modal);
  
  // --- HSV picker setup ---
  const svCanvas = document.getElementById('cp-sv-canvas');
  const hueSlider = document.getElementById('cp-hue-slider');
  const hexInput = document.getElementById('cp-hex');
  const swatch = document.getElementById('cp-swatch');
  const hsvArea = document.getElementById('cp-hsv-area');
  
  drawHueSlider(hueSlider);
  drawSVCanvas(svCanvas, _cpState.hue);
  
  function updatePickerUI() {
    const [r, g, b] = hsvToRgb(_cpState.hue, _cpState.sat, _cpState.val);
    const hex = rgbToHex(r, g, b);
    hexInput.value = hex;
    swatch.style.background = hex;
    if (_cpState.callback) _cpState.callback(hex);
  }
  
  // SV canvas drag
  function handleSV(e) {
    const rect = svCanvas.getBoundingClientRect();
    _cpState.sat = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    _cpState.val = 1 - Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height));
    updatePickerUI();
  }
  let svDrag = false;
  svCanvas.addEventListener('mousedown', e => { svDrag = true; handleSV(e); });
  svCanvas.addEventListener('touchstart', e => { svDrag = true; handleSV(e.touches[0]); e.preventDefault(); }, {passive:false});
  document.addEventListener('mousemove', e => { if (svDrag) handleSV(e); });
  document.addEventListener('touchmove', e => { if (svDrag) handleSV(e.touches[0]); }, {passive:false});
  document.addEventListener('mouseup', () => svDrag = false);
  document.addEventListener('touchend', () => svDrag = false);
  
  // Hue slider drag
  function handleHue(e) {
    const rect = hueSlider.getBoundingClientRect();
    _cpState.hue = Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height)) * 360;
    drawSVCanvas(svCanvas, _cpState.hue);
    updatePickerUI();
  }
  let hueDrag = false;
  hueSlider.addEventListener('mousedown', e => { hueDrag = true; handleHue(e); });
  hueSlider.addEventListener('touchstart', e => { hueDrag = true; handleHue(e.touches[0]); e.preventDefault(); }, {passive:false});
  document.addEventListener('mousemove', e => { if (hueDrag) handleHue(e); });
  document.addEventListener('touchmove', e => { if (hueDrag) handleHue(e.touches[0]); }, {passive:false});
  document.addEventListener('mouseup', () => hueDrag = false);
  document.addEventListener('touchend', () => hueDrag = false);
  
  // Hex manual input
  document.getElementById('cp-hex-ok').addEventListener('click', () => {
    const hex = hexInput.value.trim();
    if (/^#[0-9a-fA-F]{6}$/.test(hex)) {
      const [r, g, b] = hexToRgb(hex);
      const [h, s, v] = rgbToHsv(r, g, b);
      _cpState.hue = h; _cpState.sat = s; _cpState.val = v;
      drawSVCanvas(svCanvas, _cpState.hue);
      updatePickerUI();
    }
  });
  
  // --- Preview du marqueur live ---
  function updatePreview() {
    const preview = document.getElementById('cp-preview');
    if (!preview) return;
    const grad = buildMarkerGradient(draft.markerColors, 135);
    const bg = grad || draft.markerColors[0];
    const border = draft.markerBorder;
    preview.innerHTML = `
      <div style="display:flex;flex-direction:column;align-items:center;">
        <div style="width:42px;height:42px;border-radius:50%;background:${bg};border:3px solid ${border};box-shadow:0 3px 12px rgba(0,0,0,0.5);display:flex;align-items:center;justify-content:center;font-size:16px;">🎵</div>
        <div style="width:0;height:0;border-left:7px solid transparent;border-right:7px solid transparent;border-top:10px solid ${border};margin-top:-2px;"></div>
        <div style="font-size:9px;color:#64748b;margin-top:6px;">Marqueur</div>
      </div>
      <div style="display:flex;flex-direction:column;align-items:center;">
        <div style="width:48px;height:48px;border-radius:50%;background:${bg};border:2.5px solid ${border};box-shadow:0 3px 12px rgba(0,0,0,0.5);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:14px;color:#fff;text-shadow:0 1px 3px rgba(0,0,0,0.6);">247</div>
        <div style="font-size:9px;color:#64748b;margin-top:6px;">Cluster</div>
      </div>
      <div style="display:flex;flex-direction:column;align-items:center;">
        <div style="position:relative;width:32px;height:32px;">
          <svg width="32" height="32" viewBox="0 0 42 42">
            <circle cx="21" cy="21" r="18" fill="none" stroke="${draft.markerColors[0]}" stroke-width="2" opacity="0.5">
              <animate attributeName="r" values="16;19;16" dur="2s" repeatCount="indefinite"/>
              <animate attributeName="opacity" values="0.3;0.6;0.3" dur="2s" repeatCount="indefinite"/>
            </circle>
            <circle cx="21" cy="21" r="10" fill="url(#logoGrad)" stroke="rgba(255,255,255,0.3)" stroke-width="1"/>
            <text x="21" y="25" text-anchor="middle" font-weight="900" font-size="12" fill="#fff">M</text>
          </svg>
        </div>
        <div style="font-size:9px;color:#64748b;margin-top:6px;">Halo</div>
      </div>
    `;
  }
  
  // --- Ouvrir le HSV pour un slot ---
  function activatePickerFor(color, onChange) {
    hsvArea.style.display = 'block';
    const [r, g, b] = hexToRgb(color);
    const [h, s, v] = rgbToHsv(r, g, b);
    _cpState.hue = h; _cpState.sat = s; _cpState.val = v;
    _cpState.callback = onChange;
    drawSVCanvas(svCanvas, _cpState.hue);
    updatePickerUI();
  }
  
  // --- Rendre les slots interieurs ---
  function renderInteriorSlots() {
    const c = document.getElementById('cp-interior-slots');
    c.innerHTML = '';
    draft.markerColors.forEach((color, i) => {
      const slot = document.createElement('div');
      slot.style.cssText = `width:36px;height:36px;border-radius:10px;background:${color};border:2px solid rgba(255,255,255,0.25);cursor:pointer;transition:transform 0.15s,box-shadow 0.15s;position:relative;`;
      slot.addEventListener('mouseenter', () => { slot.style.transform = 'scale(1.12)'; slot.style.boxShadow = '0 0 14px rgba(255,255,255,0.3)'; });
      slot.addEventListener('mouseleave', () => { slot.style.transform = 'scale(1)'; slot.style.boxShadow = 'none'; });
      slot.addEventListener('click', () => {
        activeSlotType = 'interior-' + i;
        // Highlight active slot
        c.querySelectorAll('div[data-slot]').forEach(s => s.style.outline = 'none');
        slot.style.outline = '2px solid #00ffc3';
        slot.style.outlineOffset = '2px';
        activatePickerFor(color, (hex) => {
          draft.markerColors[i] = hex;
          slot.style.background = hex;
          updatePreview();
        });
      });
      slot.setAttribute('data-slot', 'interior');
      // Bouton supprimer (si >1 couleur)
      if (draft.markerColors.length > 1) {
        const rm = document.createElement('div');
        rm.style.cssText = 'position:absolute;top:-6px;right:-6px;width:16px;height:16px;border-radius:50%;background:#ef4444;color:#fff;font-size:10px;font-weight:bold;display:flex;align-items:center;justify-content:center;cursor:pointer;line-height:1;';
        rm.textContent = 'x';
        rm.addEventListener('click', e => { e.stopPropagation(); draft.markerColors.splice(i, 1); renderInteriorSlots(); updatePreview(); });
        slot.appendChild(rm);
      }
      c.appendChild(slot);
    });
    // Bouton + (si <3 couleurs)
    if (draft.markerColors.length < 3) {
      const addBtn = document.createElement('div');
      addBtn.style.cssText = 'width:36px;height:36px;border-radius:10px;border:2px dashed rgba(255,255,255,0.15);cursor:pointer;display:flex;align-items:center;justify-content:center;color:#475569;font-size:20px;transition:border-color 0.2s;';
      addBtn.textContent = '+';
      addBtn.addEventListener('mouseenter', () => addBtn.style.borderColor = 'rgba(255,255,255,0.4)');
      addBtn.addEventListener('mouseleave', () => addBtn.style.borderColor = 'rgba(255,255,255,0.15)');
      addBtn.addEventListener('click', () => { draft.markerColors.push('#ffffff'); renderInteriorSlots(); updatePreview(); });
      c.appendChild(addBtn);
    }
  }
  
  // --- Rendre le slot bordure ---
  function renderBorderSlot() {
    const c = document.getElementById('cp-border-slot');
    c.innerHTML = '';
    const slot = document.createElement('div');
    slot.style.cssText = `width:36px;height:36px;border-radius:10px;background:${draft.markerBorder};border:2px solid rgba(255,255,255,0.25);cursor:pointer;transition:transform 0.15s,box-shadow 0.15s;`;
    slot.setAttribute('data-slot', 'border');
    slot.addEventListener('mouseenter', () => { slot.style.transform = 'scale(1.12)'; slot.style.boxShadow = '0 0 14px rgba(255,255,255,0.3)'; });
    slot.addEventListener('mouseleave', () => { slot.style.transform = 'scale(1)'; slot.style.boxShadow = 'none'; });
    slot.addEventListener('click', () => {
      activeSlotType = 'border';
      document.querySelectorAll('[data-slot]').forEach(s => s.style.outline = 'none');
      slot.style.outline = '2px solid #00ffc3';
      slot.style.outlineOffset = '2px';
      activatePickerFor(draft.markerBorder, (hex) => {
        draft.markerBorder = hex;
        slot.style.background = hex;
        hexLabel.textContent = hex;
        updatePreview();
      });
    });
    c.appendChild(slot);
    const hexLabel = document.createElement('span');
    hexLabel.style.cssText = 'font-size:11px;color:#475569;font-family:monospace;';
    hexLabel.textContent = draft.markerBorder;
    c.appendChild(hexLabel);
  }
  
  // Init
  renderInteriorSlots();
  renderBorderSlot();
  updatePreview();
  
  // --- Fermer ---
  document.getElementById('cp-close').addEventListener('click', () => modal.remove());
  modal.addEventListener('click', e => { if (e.target === modal) modal.remove(); });
  
  // --- VALIDER ---
  document.getElementById('cp-validate').addEventListener('click', async () => {
    window.customThemeConfig = { markerColors: [...draft.markerColors], markerBorder: draft.markerBorder };
    applyCustomColors();
    
    // IMPORTANT: Vider TOUS les marqueurs existants pour les recréer avec les nouvelles couleurs
    // Sans cela, loadedEventIds empêche la recréation des marqueurs (bug couleur bordure ignorée)
    if (markersLayer) markersLayer.clearLayers();
    markerMap = {};
    loadedEventIds.clear();
    eventsData = [];
    window.eventsData = eventsData;
    
    // Rafraichir geo-clusters et clusters Leaflet SANS bouger la map
    lastViewportKey = '';
    if (typeof loadViewportData === 'function' && map) loadViewportData();
    
    // Sauvegarder en BDD si connecte
    try {
      const token = typeof getAuthToken === 'function' ? getAuthToken() : null;
      if (token) {
        await fetch(`${window.API_BASE_URL}/user/theme`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify(window.customThemeConfig)
        });
        showNotification('Couleurs sauvegardees !', 'success');
      } else {
        showNotification('Connectez-vous pour sauvegarder vos couleurs', 'info');
      }
    } catch (e) {
      console.warn('[THEME] Erreur sauvegarde:', e);
    }
    modal.remove();
  });
  
  // --- RESET ---
  document.getElementById('cp-reset').addEventListener('click', () => {
    window.customThemeConfig = null;
    localStorage.removeItem('customThemeConfig');
    // Reset halo logo aux couleurs par defaut
    const halo1 = document.getElementById('logo-halo-1');
    const halo2 = document.getElementById('logo-halo-2');
    if (halo1) halo1.setAttribute('stroke', '#00ffc3');
    if (halo2) halo2.setAttribute('stroke', '#00ffc3');
    // Reset bouton publier
    const pubBtn = document.getElementById('map-publish-btn');
    if (pubBtn) pubBtn.style.background = '';
    // IMPORTANT: Vider TOUS les marqueurs pour les recréer avec les couleurs par défaut
    if (markersLayer) markersLayer.clearLayers();
    markerMap = {};
    loadedEventIds.clear();
    eventsData = [];
    window.eventsData = eventsData;
    // Rafraichir
    lastViewportKey = '';
    if (typeof loadViewportData === 'function' && map) loadViewportData();
    // Supprimer en BDD si connecte
    try {
      const token = typeof getAuthToken === 'function' ? getAuthToken() : null;
      if (token) {
        fetch(`${window.API_BASE_URL}/user/theme`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify(null)
        });
      }
    } catch(e) {}
    showNotification('Couleurs par defaut restaurees', 'success');
    modal.remove();
  });
}

function cycleMapTheme() {
  mapThemeIndex = (mapThemeIndex + 1) % MAP_THEMES.length;
  applyMapTheme(mapThemeIndex);
}

function applyMapTheme(i) {
  const theme = MAP_THEMES[i];
  if (tileLayer) map.removeLayer(tileLayer);
  tileLayer = L.tileLayer(theme.url, {
    maxZoom: theme.maxZoom,
    attribution: theme.attribution
  });
  tileLayer.addTo(map);
}

// ============================================
// DÉMO AUTOMATIQUE – 400 ÉVÉNEMENTS VARIÉS
// ============================================

const EVENT_TITLES = {
  "Techno": ["Rave Underground", "Techno Warehouse", "Dark Room", "Industrial Night", "Bunker Session", "Acid Night", "Minimal Monday", "Peak Time", "Detroit Calling", "Berghain Vibes"],
  "House": ["Deep House Sunday", "Funky Groove", "Soulful Sessions", "Beach House Party", "Disco Revival", "Tech House Fiesta", "Progressive Journey", "Tribal Gathering"],
  "Trance": ["Psytrance Forest", "Goa Experience", "Uplifting Night", "Full Moon Party", "Spiritual Journey", "Hi-Tech Madness", "Progressive Paradise"],
  "Rap": ["Hip-Hop Night", "Freestyle Battle", "Urban Beats", "Trap House", "Drill Session", "Boom Bap Revival", "Old School vs New"],
  "Rock": ["Rock the Night", "Metal Fest", "Punk Rebellion", "Indie Showcase", "Alternative Scene", "Grunge Night", "Classic Rock Party"],
  "Jazz": ["Jazz Club Night", "Smooth Sessions", "Swing Dance", "Blues Café", "Fusion Night", "New Orleans Style"],
  "Festival": ["Summer Festival", "Music Days", "Urban Fest", "Lake Festival", "Mountain Sounds", "City Beats Festival"],
  "Marché": ["Marché de Noël", "Brocante du Dimanche", "Marché artisanal", "Foire aux vins", "Marché bio", "Antiquités"],
  "Cinéma": ["Ciné en plein air", "Avant-première", "Nuit du cinéma", "Court-métrage Festival", "Ciné-concert"],
  "Théâtre": ["Comédie moderne", "Drame classique", "Stand-up Comedy", "Improvisation", "One Man Show"],
  "Sport": ["Marathon urbain", "Trail des Alpes", "Tournoi de foot", "CrossFit Challenge", "Yoga au parc", "Course nocturne"],
  "Food": ["Street Food Festival", "Wine & Dine", "Brunch Party", "BBQ géant", "Dégustation", "Food Truck Rally"],
  "Expo": ["Art contemporain", "Photographie", "Vernissage", "Installation interactive", "Street Art Show"]
};

const VENUES = [
  "D! Club", "Usine", "Moods", "Kaufleuten", "Hive", "Supermarket", "MAD", "Folklor",
  "Les Docks", "L'Usine", "Espace culturel", "Salle communale", "Centre ville",
  "Parc des Bastions", "Plaine de Plainpalais", "Jardin Anglais", "Place Fédérale",
  "Vieille ville", "Bord du lac", "Zone industrielle", "Ancien hangar"
];

const DESCRIPTIONS = [
  "Une soirée exceptionnelle avec les meilleurs artistes locaux et internationaux.",
  "Rejoignez-nous pour une expérience unique dans un cadre incomparable.",
  "L'événement incontournable de la saison, ne manquez pas ça !",
  "Ambiance garantie, sound system de qualité, dancefloor enflammé.",
  "Une programmation éclectique pour tous les goûts.",
  "Venez découvrir les talents émergents de la scène suisse.",
  "Un moment de partage et de convivialité entre passionnés.",
  "Production visuelle et sonore de haute qualité.",
  "L'endroit parfait pour passer une soirée mémorable.",
  "Événement organisé par des professionnels de l'événementiel."
];

