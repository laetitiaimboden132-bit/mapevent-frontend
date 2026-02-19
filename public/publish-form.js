// ============================================================
// publish-form.js
// Formulaire publier (buildPublishFormHtml, openPublishModal, onSubmitPublishForm, Stripe)
// Extrait de map_logic.js (lignes 10172-12464)
// ============================================================

// FORMULAIRE PUBLIER (inchangé)
// ============================================
function buildPublishFormHtml() {
  // Utiliser window.t() pour éviter les erreurs TDZ
  // NE JAMAIS créer de variable locale 't' - utiliser directement window.t() pour éviter toute TDZ
  const modeLabel = currentMode.charAt(0).toUpperCase() + currentMode.slice(1);
  const hasDates = currentMode === "event";

  const categoriesBlock = `
    <div style="margin-bottom:10px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
        <label style="font-size:12px;font-weight:600;color:#e2e8f0;">${window.t("main_category")} *</label>
        <button type="button" id="pub-open-filter-btn" onclick="openFilterForPublish()" style="padding:4px 10px;border-radius:6px;border:1px solid rgba(0,255,195,0.5);background:rgba(0,255,195,0.1);color:#00ffc3;font-size:11px;cursor:pointer;font-weight:600;transition:all 0.2s;" onmouseover="this.style.background='rgba(0,255,195,0.2)';this.style.borderColor='rgba(0,255,195,0.8)'" onmouseout="this.style.background='rgba(0,255,195,0.1)';this.style.borderColor='rgba(0,255,195,0.5)'">🔍 Ouvrir filtre</button>
      </div>
      <input id="pub-main-category" placeholder="1ère catégorie (obligatoire)"
               style="width:100%;padding:8px 10px;border-radius:8px;border:2px solid #334155;background:#0f172a !important;color:#00ffc3 !important;font-size:13px;font-weight:600;-webkit-text-fill-color:#00ffc3 !important;">
      <input id="pub-main-category-2" placeholder="2ème catégorie (optionnel)"
               style="width:100%;padding:8px 10px;border-radius:8px;border:2px solid #334155;background:#0f172a !important;color:#00ffc3 !important;font-size:13px;margin-top:6px;-webkit-text-fill-color:#00ffc3 !important;">
      <div id="pub-category-suggestions" style="display:none;margin-top:4px;max-height:150px;overflow-y:auto;border:1px solid #334155;border-radius:8px;background:#0f172a;padding:4px;position:relative;z-index:1000;"></div>
    </div>
  `;

  const datesBlock = hasDates
    ? `
      <div style="display:flex;gap:8px;margin-bottom:10px;">
        <div style="flex:1;">
          <label id="pub-start-label" style="font-size:12px;font-weight:600;color:#e2e8f0;">${window.t("start")} <span id="pub-start-star" style="color:#ff4444;">*</span></label>
          <input type="datetime-local" id="pub-start" required onchange="validateEventDates()" style="width:100%;padding:8px;border-radius:8px;border:2px solid #334155;background:#0f172a;color:#fff;color-scheme:dark;">
          <div id="pub-start-error" style="display:none;font-size:10px;color:#ff4444;margin-top:2px;">⚠️ Date/heure invalide</div>
        </div>
        <div style="flex:1;">
          <label id="pub-end-label" style="font-size:12px;font-weight:600;color:#e2e8f0;">${window.t("end")} <span id="pub-end-star" style="color:#ff4444;">*</span></label>
          <input type="datetime-local" id="pub-end" required onchange="validateEventDates()" style="width:100%;padding:8px;border-radius:8px;border:2px solid #334155;background:#0f172a;color:#fff;color-scheme:dark;">
          <div id="pub-end-error" style="display:none;font-size:10px;color:#ff4444;margin-top:2px;">⚠️ Date/heure invalide</div>
        </div>
      </div>
      
      <!-- RÉPÉTITIONS D'ÉVÉNEMENTS - Hebdomadaire ou Mensuel uniquement -->
      <div style="margin-bottom:12px;padding:10px;background:rgba(0,255,195,0.05);border:1px solid rgba(0,255,195,0.2);border-radius:10px;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
          <div style="display:flex;align-items:center;gap:8px;">
            <input type="checkbox" id="pub-repeat-enabled" onchange="toggleRepeatOptions()" style="width:18px;height:18px;accent-color:#00ffc3;cursor:pointer;">
            <label for="pub-repeat-enabled" style="font-size:12px;font-weight:600;color:#00ffc3;cursor:pointer;">🔄 Répéter cet événement</label>
          </div>
          <span id="pub-repeat-price-badge" style="display:none;padding:3px 8px;background:rgba(255,200,0,0.2);border:1px solid rgba(255,200,0,0.5);border-radius:12px;font-size:10px;color:#ffc800;font-weight:600;">+0.-</span>
        </div>
        
        <div id="pub-repeat-options" style="display:none;margin-top:10px;">
          <div style="margin-bottom:8px;">
            <label style="font-size:11px;font-weight:600;color:var(--ui-text-muted);margin-bottom:4px;display:block;">Fréquence</label>
            <select id="pub-repeat-frequency" onchange="updateRepeatPricing()" style="width:100%;padding:6px;border-radius:8px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:12px;cursor:pointer;">
              <option value="weekly">📅 Hebdomadaire (+15.- CHF)</option>
              <option value="monthly">📆 Mensuel (+4.- CHF)</option>
            </select>
          </div>
          
          <div style="display:flex;gap:8px;margin-bottom:8px;">
            <div style="flex:1;">
              <label style="font-size:11px;font-weight:600;color:var(--ui-text-muted);margin-bottom:4px;display:block;">Répéter jusqu'au</label>
              <input type="date" id="pub-repeat-until" onchange="updateRepeatPricing()" style="width:100%;padding:6px;border-radius:8px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:12px;">
            </div>
          </div>
          
          <div id="pub-repeat-preview" style="padding:8px;background:rgba(0,255,195,0.1);border-radius:6px;font-size:11px;color:#00ffc3;min-height:20px;">
            <span>💡 Le point réapparaîtra automatiquement chaque semaine/mois jusqu'à la date finale.</span>
          </div>
        </div>
      </div>
    `
    : "";

  const audioBlock =
    currentMode === "booking" || currentMode === "service"
      ? `
      <div style="margin-bottom:10px;">
        <label style="font-size:12px;font-weight:600;">🎵 Liens Sons (écoute directe)</label>
        <div style="display:flex;gap:8px;margin-bottom:6px;">
          <textarea id="pub-audio" rows="3" placeholder="SoundCloud, Spotify, Mixcloud, Audius... (un lien par ligne, plusieurs pistes possibles)"
                    oninput="updateAudioPreview()" style="flex:1;padding:6px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);font-size:13px;"></textarea>
          <button type="button" onclick="pasteAudioLinks()" style="height:40px;padding:0 14px;border-radius:8px;border:1px solid var(--ui-card-border);background:rgba(139,92,246,0.2);color:#a78bfa;cursor:pointer;font-size:12px;font-weight:600;white-space:nowrap;flex-shrink:0;" title="Coller depuis le presse-papiers">📋 Coller</button>
        </div>
        <div style="font-size:10px;color:var(--ui-text-muted);margin-top:2px;">💡 Les visiteurs pourront écouter directement depuis la fiche</div>
        <div id="pub-audio-preview" style="margin-top:10px;display:none;"></div>
      </div>
    `
      : "";

  const bookingLevel =
    currentMode === "booking"
      ? `
      <div style="margin-bottom:10px;">
        <label style="font-size:12px;font-weight:600;">${window.t("level")}</label>
        <input id="pub-level" placeholder="${window.t("level")}"
               style="width:100%;padding:6px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);">
      </div>

      <div style="margin-bottom:10px;">
        <label style="font-size:12px;font-weight:600;">${window.t("price_estimate")}</label>
        <input id="pub-price-estimate" placeholder="${window.t("price_example")}"
               style="width:100%;padding:6px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);">
        <div style="font-size:11px;color:var(--ui-text-muted);margin-top:3px;">
          ${window.t("price_not_detected")}
        </div>
      </div>
    `
      : "";

  const paymentBlock = `
    <div style="margin-top:6px;padding:10px;border-radius:10px;border:1px dashed var(--ui-card-border);font-size:12px;color:var(--ui-text-muted);">
      <div style="font-weight:600;margin-bottom:6px;">${window.t("visibility_choice")}</div>
      <div style="display:flex;flex-direction:column;gap:6px;">
        <label style="display:flex;align-items:center;gap:8px;padding:6px;border-radius:6px;cursor:pointer;transition:background 0.2s;" onmouseover="this.style.background='rgba(0,255,195,0.05)'" onmouseout="this.style.background='transparent'">
          <input type="radio" name="pub-boost" value="standard" checked onchange="updateTotalPrice()" style="accent-color:#00ffc3;">
          <span><b>Standard</b> - Point basique (inclus)</span>
        </label>
        <label style="display:flex;align-items:center;gap:8px;padding:6px;border-radius:6px;cursor:pointer;transition:background 0.2s;" onmouseover="this.style.background='rgba(205,127,50,0.1)'" onmouseout="this.style.background='transparent'">
          <input type="radio" name="pub-boost" value="bronze" onchange="updateTotalPrice()" style="accent-color:#cd7f32;">
          <span><b style="color:#cd7f32;">🥉 Bronze</b> - +5.- CHF (légère mise en avant)</span>
        </label>
        <label style="display:flex;align-items:center;gap:8px;padding:6px;border-radius:6px;cursor:pointer;transition:background 0.2s;" onmouseover="this.style.background='rgba(192,192,192,0.1)'" onmouseout="this.style.background='transparent'">
          <input type="radio" name="pub-boost" value="silver" onchange="updateTotalPrice()" style="accent-color:#c0c0c0;">
          <span><b style="color:#c0c0c0;">🥈 Silver</b> - +10.- CHF (bonne visibilité)</span>
        </label>
        <label style="display:flex;align-items:center;gap:8px;padding:6px;border-radius:6px;cursor:pointer;transition:background 0.2s;" onmouseover="this.style.background='rgba(139,92,246,0.1)'" onmouseout="this.style.background='transparent'">
          <input type="radio" name="pub-boost" value="platinum" onchange="updateTotalPrice(); openPlatinumAuctionModal()" style="accent-color:#8b5cf6;">
          <span><b style="color:#8b5cf6;">💎 Platinum (Top 10)</b> - Enchères (voir prix actuels)</span>
        </label>
      </div>
    </div>
    
    <!-- AFFICHAGE PRIX TOTAL -->
    <div id="pub-total-price-block" style="margin-top:12px;padding:12px;background:linear-gradient(135deg,rgba(0,255,195,0.1),rgba(59,130,246,0.05));border:2px solid rgba(0,255,195,0.4);border-radius:12px;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <div style="font-size:11px;color:#e2e8f0;margin-bottom:2px;">Prix de publication</div>
          <div style="font-size:10px;color:#94a3b8;" id="pub-price-details">Base: 1.-</div>
        </div>
        <div style="text-align:right;">
          <div style="font-size:22px;font-weight:700;color:#00ffc3;" id="pub-total-price">1.- CHF</div>
        </div>
      </div>
    </div>
    
    <!-- PLACEHOLDER ENCHÈRE PLATINUM -->
    <div id="pub-platinum-bid-info" style="display:none;margin-top:8px;padding:10px;background:rgba(139,92,246,0.1);border:1px solid rgba(139,92,246,0.3);border-radius:8px;">
      <div style="font-size:11px;color:#a78bfa;font-weight:600;">💎 Votre enchère Platinum</div>
      <div style="font-size:14px;color:#fff;font-weight:700;" id="pub-platinum-bid-amount">-</div>
    </div>
  `;

  return `
    <form onsubmit="return onSubmitPublishForm(event)" style="display:flex;flex-direction:column;min-height:100%;">
      <div style="flex:1;overflow-y:auto;padding-bottom:16px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
        <h2 style="margin:0;font-size:16px;">${window.t("publish_mode")} ${modeLabel}</h2>
        <div style="display:flex;gap:8px;align-items:center;">
          <button type="button" onclick="resetPublishForm()" style="padding:4px 10px;border-radius:6px;border:1px solid #475569;background:transparent;color:#94a3b8;font-size:11px;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.background='rgba(255,100,100,0.1)';this.style.borderColor='#ff4444';this.style.color='#ff4444'" onmouseout="this.style.background='transparent';this.style.borderColor='#475569';this.style.color='#94a3b8'" title="Effacer toutes les données">🔄 Réinitialiser</button>
          <button type="button" onclick="closePublishModal(event)" style="background:none;border:none;color:var(--ui-text-muted);font-size:24px;cursor:pointer;padding:4px 8px;border-radius:6px;transition:all 0.15s;line-height:1;width:32px;height:32px;display:flex;align-items:center;justify-content:center;" onmouseover="this.style.background='rgba(255,255,255,0.1)';this.style.color='#fff'" onmouseout="this.style.background='none';this.style.color='var(--ui-text-muted)'" title="Fermer (données conservées)">✕</button>
        </div>
      </div>

      <div style="margin-bottom:10px;">
        <label style="font-size:12px;font-weight:600;color:#e2e8f0;display:block;margin-bottom:4px;">${window.t("title_name")}</label>
        <input id="pub-title" required
               style="width:100%;padding:8px 10px;border-radius:8px;border:2px solid #334155;background:#0f172a;color:#fff;font-size:13px;">
      </div>

      ${categoriesBlock}
      ${datesBlock}

      <div style="margin-bottom:10px;position:relative;">
        <label id="pub-address-label" style="font-size:12px;font-weight:600;color:#e2e8f0;">${window.t("full_address")} <span id="pub-address-star" style="color:#ff4444;">*</span></label>
        <textarea id="pub-address" name="pub-location-search-${Date.now()}" required oninput="debounceAddressSearch()" onblur="validateAddress()"
               placeholder="Ex: 15 Rue de la Paix, Paris"
               rows="2"
               autocomplete="new-password" autocorrect="off" autocapitalize="off" spellcheck="false" data-lpignore="true" data-form-type="other"
               style="width:100%;padding:8px 10px;border-radius:8px;border:2px solid #334155;background:#0f172a;color:#fff;font-size:13px;resize:none;font-family:inherit;"></textarea>
        <div id="pub-address-suggestions" style="display:none;position:absolute;top:100%;left:0;right:0;z-index:1001;max-height:200px;overflow-y:auto;border:1px solid #334155;border-radius:8px;background:#0f172a;margin-top:2px;box-shadow:0 4px 12px rgba(0,0,0,0.3);"></div>
        <div id="pub-address-status" style="display:none;font-size:10px;margin-top:2px;"></div>
        <input type="hidden" id="pub-address-lat">
        <input type="hidden" id="pub-address-lng">
      </div>

      <div style="display:flex;gap:8px;margin-bottom:10px;">
        ${currentMode !== "booking" && currentMode !== "service" ? `
        <div style="flex:1;">
          <label style="font-size:12px;font-weight:600;">${window.t("phone")}</label>
          <input id="pub-phone"
                 style="width:100%;padding:6px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);font-size:13px;">
        </div>
        ` : ''}
        <div style="flex:1;">
          <label style="font-size:12px;font-weight:600;">${window.t("email")} *</label>
          <input id="pub-email" type="email" required
                 style="width:100%;padding:6px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);font-size:13px;">
        </div>
      </div>

      <div style="margin-bottom:10px;">
        <label style="font-size:12px;font-weight:600;">${window.t("full_description")} *</label>
        <textarea id="pub-description" rows="4" required
                  style="width:100%;padding:6px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);"></textarea>
      </div>

      <div style="margin-bottom:10px;">
        <label style="font-size:12px;font-weight:600;">${window.t("main_photo")} *</label>
        <input id="pub-image" type="file" accept="image/*" required
               style="width:100%;font-size:12px;color:var(--ui-text-muted);">
      </div>

      ${
        currentMode === "event"
          ? `
        <div style="margin-bottom:10px;">
          <label style="font-size:12px;font-weight:600;">${window.t("ticketing")}</label>
          <input id="pub-ticket" placeholder="${window.t("ticket_link")}"
                 style="width:100%;padding:6px;border-radius:8px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:#fff;">
        </div>
        
        <!-- LIENS SONS - SoundCloud, Spotify, etc. (événements) -->
        <div style="margin-bottom:10px;">
          <label style="font-size:12px;font-weight:600;">🎵 Liens Sons (écoute directe)</label>
          <textarea id="pub-audio-links" rows="3" placeholder="SoundCloud, Spotify, Mixcloud, Audius... (un lien par ligne, plusieurs pistes possibles)"
                    style="width:100%;padding:6px;border-radius:8px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:#fff;font-size:12px;"></textarea>
          <div style="font-size:10px;color:var(--ui-text-muted);margin-top:2px;">
            💡 Les visiteurs pourront écouter directement depuis la fiche événement
          </div>
        </div>
      `
          : ""
      }

      <div style="margin-bottom:10px;">
        <label style="font-size:12px;font-weight:600;">${window.t("social_links")}</label>
        <textarea id="pub-social" rows="2" placeholder="Facebook, Instagram…"
                  style="width:100%;padding:6px;border-radius:8px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:#fff;"></textarea>
      </div>

      <div style="margin-bottom:10px;">
        <label style="font-size:12px;font-weight:600;">${window.t("video_links")}</label>
        <textarea id="pub-videos" rows="2" placeholder="YouTube, Vimeo…"
                  style="width:100%;padding:6px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);"></textarea>
      </div>

      ${audioBlock}
      ${bookingLevel}
      ${paymentBlock}
      
      <div style="margin-top:16px;padding:12px;background:linear-gradient(135deg,rgba(139,92,246,0.15),rgba(59,130,246,0.1));border:2px solid rgba(139,92,246,0.4);border-radius:12px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <div>
            <div style="font-weight:700;font-size:14px;color:#a78bfa;margin-bottom:4px;">💎 ${window.t("subscription_recommended")}</div>
            <div style="font-size:11px;color:var(--ui-text-muted);">
              ${currentMode === 'event' ? window.t("save_on_events") : window.t("unlimited_contacts")}
            </div>
          </div>
          <button type="button" onclick="openSubscriptionModal()" style="padding:8px 16px;border-radius:999px;border:2px solid #a78bfa;background:rgba(139,92,246,0.2);color:#a78bfa;font-weight:600;cursor:pointer;font-size:12px;">
            ${window.t("view_subs")}
          </button>
        </div>
        <div style="font-size:10px;color:var(--ui-text-muted);text-align:center;margin-top:6px;">
          ${currentMode === 'event' ? 'Events Explorer: 5.–/mois • Events Alertes Pro: 10.–/mois' : 'Booking/Service Pro: 10.–/mois • Ultra: 18.–/mois'}
        </div>
      </div>

      </div>
      <div id="publish-form-footer" style="flex-shrink:0;padding:12px 0;border-top:1px solid var(--ui-card-border);margin-top:auto;background:var(--ui-card-bg);">
        <div style="display:flex;gap:10px;justify-content:flex-end;">
          <button type="button" onclick="closePublishModal()" style="
            padding:10px 20px;border-radius:999px;background:transparent;border:1px solid var(--ui-card-border);color:var(--ui-text-main);cursor:pointer;">
            ${window.t("cancel")}
          </button>
          <button type="submit" style="
            padding:10px 24px;border-radius:999px;border:none;
            background:var(--btn-main-bg);color:var(--btn-main-text);font-weight:700;cursor:pointer;">
            ${window.t("publish_and_pay")}
          </button>
        </div>
      </div>
    </form>
  `;
}

function openPublishModal() {
  console.log('[PUBLISH] 🔍 openPublishModal appelé - currentUser:', currentUser);
  console.log('[PUBLISH] 🔍 isLoggedIn:', currentUser?.isLoggedIn);
  
  // ⚠️⚠️⚠️ VÉRIFIER SI L'UTILISATEUR EST CONNECTÉ
  if (!currentUser || !currentUser.isLoggedIn) {
    console.log('[PUBLISH] ❌ Utilisateur non connecté - Ouverture modal connexion');
    // Afficher le modal de connexion avec callback pour ouvrir le formulaire après
    if (typeof window.openAuthModal === 'function') {
      window.openAuthModal('login');
    } else if (typeof openAuthModal === 'function') {
      openAuthModal('login');
    } else {
      showNotification('❌ Veuillez vous connecter pour publier', 'error');
    }
    return;
  }
  
  console.log('[PUBLISH] ✅ Utilisateur connecté - Ouverture formulaire publication');
  
  try {
    const backdrop = document.getElementById("publish-modal-backdrop");
    const inner = document.getElementById("publish-modal-inner");
    console.log('[PUBLISH] 🔍 backdrop:', !!backdrop, 'inner:', !!inner);
    
    if (!backdrop || !inner) {
      console.error('[PUBLISH] ❌ Éléments DOM non trouvés:', { backdrop: !!backdrop, inner: !!inner });
      return;
    }
    
    console.log('[PUBLISH] 🔍 Appel buildPublishFormHtml...');
    const formHtml = buildPublishFormHtml();
    console.log('[PUBLISH] 🔍 HTML généré, longueur:', formHtml?.length || 0);
    
    inner.innerHTML = formHtml;
    console.log('[PUBLISH] 🔍 innerHTML assigné');
    
    // ⚠️⚠️⚠️ FORCER l'affichage avec !important pour écraser les styles de closeAuthModal
    backdrop.setAttribute('style', 'display: flex !important; visibility: visible !important; opacity: 1 !important; z-index: 100 !important; position: fixed !important; inset: 0 !important; background: rgba(0,0,0,0.3) !important; align-items: flex-start !important; justify-content: flex-end !important;');
    
    // Forcer aussi les styles du modal et inner
    const modal = document.getElementById('publish-modal');
    if (modal) {
      modal.style.display = 'block';
      modal.style.visibility = 'visible';
      modal.style.opacity = '1';
      modal.style.height = 'auto';
      modal.style.minHeight = '400px';
    }
    inner.style.display = 'block';
    inner.style.visibility = 'visible';
    inner.style.opacity = '1';
    inner.style.height = 'auto';
    
    console.log('[PUBLISH] ✅ Modal affiché avec display:flex (forcé avec !important)');
  } catch (error) {
    console.error('[PUBLISH] ❌ ERREUR:', error);
  }
  
  // Ouvrir automatiquement le filtre pour aider à choisir la catégorie
  if (!explorerOpen) {
    explorerOpen = true;
    const panel = document.getElementById("left-panel");
    if (panel) {
      panel.style.display = "block";
      // ⚠️⚠️⚠️ IMPORTANT: Donner un z-index plus élevé au panneau pour qu'il soit au-dessus du backdrop
      panel.style.zIndex = "150";
      panel.style.position = "relative";
      loadExplorerTree();
      console.log('[PUBLISH] ✅ Filtre ouvert pour aide catégorie (z-index: 150)');
    }
  } else {
    // Même si le filtre est déjà ouvert, s'assurer qu'il a le bon z-index
    const panel = document.getElementById("left-panel");
    if (panel) {
      panel.style.zIndex = "150";
      panel.style.position = "relative";
    }
  }
  
  // Initialiser les gestionnaires d'événements pour les répétitions
  if (currentMode === "event") {
    setTimeout(() => {
      initRepeatHandlers();
      initMultipleImagesHandler();
    }, 100);
  }
  
  // ⚠️⚠️⚠️ NOUVEAU : Configurer le champ catégorie avec autocomplétion
  setTimeout(() => {
    setupCategoryInputWithFilter();
  }, 200);
  
  // ⚠️⚠️⚠️ RESTAURER les données du formulaire si elles existent
  setTimeout(() => {
    restorePublishFormData();
  }, 300);
}

// ⚠️⚠️⚠️ NOUVEAU : Fonction pour ouvrir le filtre depuis le bouton Publier
function openFilterForPublish() {
  if (!explorerOpen) {
    explorerOpen = true;
    const panel = document.getElementById("left-panel");
    if (panel) {
      panel.style.display = "block";
      loadExplorerTree();
    }
  }
}

// ⚠️⚠️⚠️ NOUVEAU : Configuration du champ catégorie avec autocomplétion et recherche
function setupCategoryInputWithFilter() {
  const categoryInput = document.getElementById("pub-main-category");
  const suggestionsDiv = document.getElementById("pub-category-suggestions");
  
  if (!categoryInput || !suggestionsDiv) return;
  
  // Fonction pour obtenir toutes les catégories de l'arbre
  function getAllCategories(tree, prefix = "") {
    const categories = [];
    if (!tree) return categories;
    
    if (Array.isArray(tree)) {
      // Feuilles
      tree.forEach(cat => {
        categories.push(prefix ? `${prefix} > ${cat}` : cat);
      });
    } else {
      // Dossiers
      for (const key in tree) {
        const fullPath = prefix ? `${prefix} > ${key}` : key;
        categories.push(fullPath);
        
        if (tree[key] && !Array.isArray(tree[key])) {
          // Sous-catégories
          categories.push(...getAllCategories(tree[key], fullPath));
        } else if (Array.isArray(tree[key])) {
          // Feuilles dans ce dossier
          tree[key].forEach(cat => {
            categories.push(`${fullPath} > ${cat}`);
          });
        }
      }
    }
    return categories;
  }
  
  // Fonction pour filtrer les catégories selon la recherche
  function filterCategories(query) {
    if (!query || query.length < 2) return [];
    
    const allCats = getAllCategories(explorerTree || EVENTS_TREE || BOOKING_TREE || SERVICE_TREE);
    const lowerQuery = query.toLowerCase();
    
    return allCats.filter(cat => 
      cat.toLowerCase().includes(lowerQuery)
    ).slice(0, 10); // Limiter à 10 résultats
  }
  
  // Fonction pour afficher les suggestions
  function showSuggestions(matches) {
    if (!matches || matches.length === 0) {
      suggestionsDiv.style.display = "none";
      return;
    }
    
    suggestionsDiv.innerHTML = matches.map(cat => {
      const safe = escapeHtml(cat);
      return `
        <div onclick="event.stopPropagation(); selectCategoryForPublish('${safe}')" 
             style="padding:8px;cursor:pointer;border-radius:4px;transition:background 0.15s;font-size:12px;color:var(--ui-text-main);background:transparent;"
             onmouseover="this.style.background='rgba(0,255,195,0.2)';this.style.color='#00ffc3'"
             onmouseout="this.style.background='transparent';this.style.color='var(--ui-text-main)'">
          ${safe}
        </div>
      `;
    }).join("");
    suggestionsDiv.style.display = "block";
  }
  
  const categoryInput2 = document.getElementById("pub-main-category-2");
  const onInput = function(e) {
    const query = e.target.value.trim();
    if (query.length >= 2) {
      if (!explorerOpen) openFilterForPublish();
      showSuggestions(filterCategories(query));
    } else {
      suggestionsDiv.style.display = "none";
    }
  };
  categoryInput.addEventListener("input", onInput);
  if (categoryInput2) categoryInput2.addEventListener("input", onInput);
  
  document.addEventListener("click", function(e) {
    const inCat1 = categoryInput && categoryInput.contains(e.target);
    const inCat2 = categoryInput2 && categoryInput2.contains(e.target);
    if (!inCat1 && !inCat2 && !suggestionsDiv.contains(e.target)) {
      suggestionsDiv.style.display = "none";
    }
  });
  
  if (categoryInput) categoryInput.focus();
}

// ⚠️⚠️⚠️ NOUVEAU : Sélectionner une catégorie depuis les suggestions (1ère ou 2ème)
function selectCategoryForPublish(category) {
  const cat1 = document.getElementById("pub-main-category");
  const cat2 = document.getElementById("pub-main-category-2");
  const suggestionsDiv = document.getElementById("pub-category-suggestions");
  
  const finalCategory = (category || "").trim();
  let targetInput = null;
  
  if (cat1 && !cat1.value.trim()) {
    targetInput = cat1;
  } else if (cat2 && !cat2.value.trim()) {
    targetInput = cat2;
  } else if (cat2) {
    targetInput = cat2;
  } else {
    targetInput = cat1;
  }
  
  if (targetInput) {
    targetInput.value = finalCategory;
    targetInput.style.background = 'rgba(0, 255, 195, 0.2)';
    targetInput.style.borderColor = '#00ffc3';
    setTimeout(() => {
      targetInput.style.background = '';
      targetInput.style.borderColor = '';
    }, 500);
  }
  
  if (suggestionsDiv) suggestionsDiv.style.display = "none";
}

// Fonction pour gérer les répétitions
function toggleRepeatOptions() {
  const checkbox = document.getElementById("pub-repeat-enabled");
  const options = document.getElementById("pub-repeat-options");
  const priceBadge = document.getElementById("pub-repeat-price-badge");
  
  if (checkbox && options) {
    options.style.display = checkbox.checked ? "block" : "none";
    if (priceBadge) {
      priceBadge.style.display = checkbox.checked ? "inline-block" : "none";
    }
    if (checkbox.checked) {
      updateRepeatPricing();
    } else {
      updateTotalPrice();
    }
  }
}

// ⚠️⚠️⚠️ VALIDATION DES DATES - Refuser les dates passées
function validateEventDates() {
  const startInput = document.getElementById("pub-start");
  const endInput = document.getElementById("pub-end");
  const startError = document.getElementById("pub-start-error");
  const endError = document.getElementById("pub-end-error");
  const startStar = document.getElementById("pub-start-star");
  const endStar = document.getElementById("pub-end-star");
  
  const now = new Date();
  let isValid = true;
  
  // Valider la date de début
  if (startInput && startInput.value) {
    const startDate = new Date(startInput.value);
    if (startDate < now) {
      // Date dans le passé - invalide
      startInput.style.borderColor = "#ff4444";
      startInput.style.background = "rgba(255,68,68,0.1)";
      if (startError) startError.style.display = "block";
      if (startStar) startStar.style.color = "#ff4444";
      isValid = false;
    } else {
      // Date valide
      startInput.style.borderColor = "var(--ui-card-border)";
      startInput.style.background = "rgba(15,23,42,0.9)";
      if (startError) startError.style.display = "none";
      if (startStar) startStar.style.color = "inherit";
    }
  }
  
  // Valider la date de fin
  if (endInput && endInput.value) {
    const endDate = new Date(endInput.value);
    const startDate = startInput?.value ? new Date(startInput.value) : now;
    
    if (endDate < now) {
      // Date dans le passé - invalide
      endInput.style.borderColor = "#ff4444";
      endInput.style.background = "rgba(255,68,68,0.1)";
      if (endError) {
        endError.textContent = "⚠️ Date invalide (passée)";
        endError.style.display = "block";
      }
      if (endStar) endStar.style.color = "#ff4444";
      isValid = false;
    } else if (endDate < startDate) {
      // Fin avant début - invalide
      endInput.style.borderColor = "#ff4444";
      endInput.style.background = "rgba(255,68,68,0.1)";
      if (endError) {
        endError.textContent = "⚠️ Fin avant début";
        endError.style.display = "block";
      }
      if (endStar) endStar.style.color = "#ff4444";
      isValid = false;
    } else {
      // Date valide
      endInput.style.borderColor = "var(--ui-card-border)";
      endInput.style.background = "rgba(15,23,42,0.9)";
      if (endError) endError.style.display = "none";
      if (endStar) endStar.style.color = "inherit";
    }
  }
  
  return isValid;
}

// ⚠️⚠️⚠️ CALCUL DU PRIX DE RÉPÉTITION
function updateRepeatPricing() {
  const frequency = document.getElementById("pub-repeat-frequency")?.value || "weekly";
  const priceBadge = document.getElementById("pub-repeat-price-badge");
  const preview = document.getElementById("pub-repeat-preview");
  const until = document.getElementById("pub-repeat-until")?.value;
  
  // Prix selon la fréquence
  const repeatPrice = frequency === "weekly" ? 15 : 4;
  
  if (priceBadge) {
    priceBadge.textContent = `+${repeatPrice}.- CHF`;
    priceBadge.style.display = "inline-block";
  }
  
  // Aperçu
  if (preview) {
    const freqText = frequency === "weekly" ? "chaque semaine" : "chaque mois";
    let previewText = `💡 Le point réapparaîtra automatiquement ${freqText}`;
    if (until) {
      const untilDate = new Date(until);
      previewText += ` jusqu'au ${untilDate.toLocaleDateString("fr-FR")}`;
    }
    preview.innerHTML = `<span style="color:#00ffc3;">${previewText}</span>`;
  }
  
  updateTotalPrice();
}

// ⚠️⚠️⚠️ CALCUL DU PRIX TOTAL
// Variable globale pour stocker le montant de l'enchère Platinum
let currentPlatinumBid = 0;

function updateTotalPrice() {
  const basePrice = 1;
  let totalPrice = basePrice;
  let details = ["Base: 1.-"];
  
  // Prix de répétition
  const repeatEnabled = document.getElementById("pub-repeat-enabled")?.checked;
  if (repeatEnabled) {
    const frequency = document.getElementById("pub-repeat-frequency")?.value || "weekly";
    const repeatPrice = frequency === "weekly" ? 15 : 4;
    totalPrice += repeatPrice;
    details.push(`Répétition ${frequency === "weekly" ? "hebdo" : "mensuelle"}: +${repeatPrice}.-`);
  }
  
  // Prix du boost
  const boostRadio = document.querySelector('input[name="pub-boost"]:checked');
  if (boostRadio) {
    if (boostRadio.value === 'platinum' && currentPlatinumBid > 0) {
      // Platinum avec enchère
      totalPrice += currentPlatinumBid;
      details.push(`Enchère Platinum: +${currentPlatinumBid}.-`);
      
      // Afficher l'info de l'enchère
      const bidInfo = document.getElementById("pub-platinum-bid-info");
      const bidAmount = document.getElementById("pub-platinum-bid-amount");
      if (bidInfo) bidInfo.style.display = "block";
      if (bidAmount) bidAmount.textContent = `${currentPlatinumBid}.- CHF`;
    } else {
      // Boost standard (Bronze, Silver)
      const boostPrices = { standard: 0, bronze: 5, silver: 10 };
      const boostPrice = boostPrices[boostRadio.value] || 0;
      if (boostPrice > 0) {
        totalPrice += boostPrice;
        details.push(`Boost ${boostRadio.value}: +${boostPrice}.-`);
      }
      
      // Cacher l'info de l'enchère
      const bidInfo = document.getElementById("pub-platinum-bid-info");
      if (bidInfo) bidInfo.style.display = "none";
    }
  }
  
  // Afficher le prix total
  const totalDisplay = document.getElementById("pub-total-price");
  const detailsDisplay = document.getElementById("pub-price-details");
  
  if (totalDisplay) {
    totalDisplay.textContent = `${totalPrice}.- CHF`;
  }
  if (detailsDisplay) {
    detailsDisplay.textContent = details.join(" • ");
  }
  
  // Stocker le prix total pour le paiement
  window.currentPublishPrice = totalPrice;
}

// ⚠️⚠️⚠️ MODAL ENCHÈRES PLATINUM (TOP 10)
function openPlatinumAuctionModal() {
  // Fermer d'abord le modal de publication temporairement
  const publishBackdrop = document.getElementById("publish-modal-backdrop");
  
  // Créer le modal d'enchères
  const auctionHtml = `
    <div id="platinum-auction-modal" style="position:fixed;inset:0;z-index:10000;background:rgba(0,0,0,0.8);display:flex;align-items:center;justify-content:center;padding:20px;">
      <div style="background:linear-gradient(135deg,#1e1b4b,#0f172a);border:2px solid #8b5cf6;border-radius:16px;max-width:450px;width:100%;max-height:80vh;overflow-y:auto;box-shadow:0 0 50px rgba(139,92,246,0.3);">
        <div style="padding:20px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
            <h2 style="margin:0;font-size:18px;color:#a78bfa;">💎 Enchères Platinum - Top 10</h2>
            <button onclick="closePlatinumAuctionModal()" style="background:none;border:none;color:#94a3b8;font-size:20px;cursor:pointer;">✕</button>
          </div>
          
          <p style="font-size:12px;color:#94a3b8;margin-bottom:16px;">
            Les 10 événements avec les enchères les plus élevées apparaissent en première position sur la carte.
          </p>
          
          <!-- TOP 10 ACTUEL -->
          <div style="margin-bottom:16px;">
            <div style="font-size:11px;font-weight:600;color:#e2e8f0;margin-bottom:8px;">📊 Enchères actuelles (Top 10)</div>
            <div id="platinum-top-10-list" style="background:rgba(0,0,0,0.3);border-radius:8px;padding:8px;max-height:200px;overflow-y:auto;">
              ${generateTop10List()}
            </div>
          </div>
          
          <!-- PLACER UNE ENCHÈRE -->
          <div style="background:rgba(139,92,246,0.1);border:1px solid rgba(139,92,246,0.3);border-radius:10px;padding:12px;">
            <div style="font-size:11px;font-weight:600;color:#a78bfa;margin-bottom:8px;">💰 Placer votre enchère</div>
            <div style="font-size:10px;color:#94a3b8;margin-bottom:8px;">
              Minimum: <b style="color:#00ffc3;">25.- CHF</b> pour entrer dans le Top 10
            </div>
            <div style="display:flex;gap:8px;align-items:center;">
              <input type="number" id="platinum-bid-input" min="25" step="1" value="25" 
                     style="flex:1;padding:8px;border-radius:8px;border:1px solid #8b5cf6;background:#1e1b4b;color:#fff;font-size:14px;font-weight:600;text-align:center;">
              <span style="color:#e2e8f0;font-weight:600;">CHF</span>
            </div>
            
            <button onclick="confirmPlatinumBid()" style="width:100%;margin-top:12px;padding:10px;border-radius:8px;border:none;background:linear-gradient(135deg,#8b5cf6,#6d28d9);color:#fff;font-weight:700;cursor:pointer;font-size:13px;transition:transform 0.2s;" onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
              ✅ Confirmer l'enchère
            </button>
          </div>
          
          <button onclick="cancelPlatinumBid()" style="width:100%;margin-top:10px;padding:8px;border-radius:8px;border:1px solid #475569;background:transparent;color:#94a3b8;cursor:pointer;font-size:12px;">
            Annuler (choisir un autre boost)
          </button>
        </div>
      </div>
    </div>
  `;
  
  document.body.insertAdjacentHTML('beforeend', auctionHtml);
}

function generateTop10List() {
  // Simuler des enchères actuelles (à remplacer par des données réelles du backend)
  const mockAuctions = [
    { position: 1, title: "Festival Électro Genève", bid: 85 },
    { position: 2, title: "Concert Jazz Lausanne", bid: 72 },
    { position: 3, title: "Soirée Techno Zurich", bid: 65 },
    { position: 4, title: "Exposition Art Basel", bid: 58 },
    { position: 5, title: "Open Air Montreux", bid: 52 },
    { position: 6, title: "Club Night Bern", bid: 45 },
    { position: 7, title: "Vernissage Fribourg", bid: 38 },
    { position: 8, title: "Rave Underground", bid: 32 },
    { position: 9, title: "Apéro Concert Neuchâtel", bid: 28 },
    { position: 10, title: "DJ Set Sion", bid: 25 }
  ];
  
  return mockAuctions.map(a => `
    <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 8px;border-bottom:1px solid rgba(255,255,255,0.05);font-size:11px;">
      <div style="display:flex;align-items:center;gap:8px;">
        <span style="color:#8b5cf6;font-weight:700;width:20px;">#${a.position}</span>
        <span style="color:#e2e8f0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:180px;">${a.title}</span>
      </div>
      <span style="color:#00ffc3;font-weight:600;">${a.bid}.-</span>
    </div>
  `).join('');
}

function closePlatinumAuctionModal() {
  const modal = document.getElementById("platinum-auction-modal");
  if (modal) modal.remove();
}

function confirmPlatinumBid() {
  const bidInput = document.getElementById("platinum-bid-input");
  const bid = parseInt(bidInput?.value) || 25;
  
  if (bid < 25) {
    showNotification("⚠️ L'enchère minimum est de 25.- CHF", "warning");
    return;
  }
  
  currentPlatinumBid = bid;
  closePlatinumAuctionModal();
  updateTotalPrice();
  showNotification(`💎 Enchère de ${bid}.- CHF confirmée!`, "success");
}

function cancelPlatinumBid() {
  currentPlatinumBid = 0;
  closePlatinumAuctionModal();
  
  // Revenir au standard
  const standardRadio = document.querySelector('input[name="pub-boost"][value="standard"]');
  if (standardRadio) standardRadio.checked = true;
  
  updateTotalPrice();
}

function updateRepeatPreview() {
  // Appeler la nouvelle fonction de pricing
  updateRepeatPricing();
}

// ⚠️⚠️⚠️ SAUVEGARDE ET RESTAURATION DES DONNÉES DU FORMULAIRE
function savePublishFormData() {
  try {
    const formData = {
      mode: currentMode,
      title: document.getElementById("pub-title")?.value || "",
      mainCategory: document.getElementById("pub-main-category")?.value || "",
      mainCategory2: document.getElementById("pub-main-category-2")?.value || "",
      mainCategory2: document.getElementById("pub-main-category-2")?.value || "",
      address: document.getElementById("pub-address")?.value || "",
      addressLat: document.getElementById("pub-address-lat")?.value || "",
      addressLng: document.getElementById("pub-address-lng")?.value || "",
      email: document.getElementById("pub-email")?.value || "",
      description: document.getElementById("pub-description")?.value || "",
      startDate: document.getElementById("pub-start")?.value || "",
      endDate: document.getElementById("pub-end")?.value || "",
      repeatEnabled: document.getElementById("pub-repeat-enabled")?.checked || false,
      repeatFrequency: document.getElementById("pub-repeat-frequency")?.value || "weekly",
      repeatUntil: document.getElementById("pub-repeat-until")?.value || "",
      capacity: document.getElementById("pub-capacity")?.value || "",
      price: document.getElementById("pub-price")?.value || "",
      eventType: document.getElementById("pub-event-type")?.value || "",
      ticketLink: document.getElementById("pub-ticket-link")?.value || "",
      audioLinks: document.getElementById("pub-audio-links")?.value || "",
      audio: document.getElementById("pub-audio")?.value || "",
      socialLinks: document.getElementById("pub-social-links")?.value || "",
      website: document.getElementById("pub-website")?.value || "",
      tags: document.getElementById("pub-tags")?.value || "",
      boost: document.querySelector('input[name="pub-boost"]:checked')?.value || "standard",
      platinumBid: currentPlatinumBid || 0,
      timestamp: Date.now()
    };
    
    localStorage.setItem("publishFormData", JSON.stringify(formData));
    console.log('[FORM] ✅ Données du formulaire sauvegardées');
  } catch (error) {
    console.error('[FORM] Erreur sauvegarde:', error);
  }
}

async function pasteAudioLinks() {
  try {
    const text = await navigator.clipboard.readText();
    const ta = document.getElementById("pub-audio");
    if (ta) {
      ta.value = ta.value ? ta.value.trim() + "\n" + text.trim() : text.trim();
      updateAudioPreview();
      if (typeof showNotification === 'function') showNotification('✅ Liens collés', 'success');
    }
  } catch (e) {
    if (typeof showNotification === 'function') showNotification('❌ Accès presse-papiers refusé', 'error');
  }
}

function updateAudioPreview() {
  const ta = document.getElementById("pub-audio");
  const preview = document.getElementById("pub-audio-preview");
  if (!ta || !preview) return;
  const links = ta.value.split('\n').map(l => l.trim()).filter(l => l && (l.startsWith('http://') || l.startsWith('https://')));
  if (links.length === 0) {
    preview.style.display = 'none';
    preview.innerHTML = '';
    return;
  }
  preview.style.display = 'block';
  preview.innerHTML = `
    <div style="font-size:11px;color:#a78bfa;font-weight:600;margin-bottom:8px;">🎧 Aperçu (${links.length} piste${links.length > 1 ? 's' : ''})</div>
    <div style="display:flex;flex-direction:column;gap:6px;max-height:120px;overflow-y:auto;">
      ${links.slice(0, 5).map((url, i) => {
        const safe = (url || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
        return `
        <div style="display:flex;align-items:center;gap:8px;padding:6px 10px;background:rgba(0,0,0,0.3);border-radius:8px;">
          <audio id="preview-audio-${i}" src="${safe}" preload="none" style="display:none;"></audio>
          <button type="button" onclick="event.stopPropagation();var a=document.getElementById('preview-audio-${i}');a.paused?a.play():a.pause();this.innerHTML=a.paused?'▶':'⏸';" style="width:28px;height:28px;border-radius:50%;border:none;background:#a78bfa;color:white;cursor:pointer;font-size:10px;display:flex;align-items:center;justify-content:center;">▶</button>
          <span style="font-size:11px;color:var(--ui-text-muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">Piste ${i + 1} • ${url.includes('audius') ? 'Audius' : url.includes('soundcloud') ? 'SoundCloud' : url.includes('spotify') ? 'Spotify' : 'Audio'}</span>
        </div>`;
      }).join('')}
    </div>
  `;
}

window.pasteAudioLinks = pasteAudioLinks;
window.updateAudioPreview = updateAudioPreview;

function restorePublishFormData() {
  try {
    const savedData = localStorage.getItem("publishFormData");
    if (!savedData) return;
    
    const formData = JSON.parse(savedData);
    
    // Vérifier si les données ne sont pas trop vieilles (24h max)
    if (formData.timestamp && Date.now() - formData.timestamp > 24 * 60 * 60 * 1000) {
      localStorage.removeItem("publishFormData");
      return;
    }
    
    // Restaurer les valeurs
    setTimeout(() => {
      const setVal = (id, val) => {
        const el = document.getElementById(id);
        if (el && val) el.value = val;
      };
      
      setVal("pub-title", formData.title);
      setVal("pub-main-category", formData.mainCategory);
      setVal("pub-main-category-2", formData.mainCategory2 || "");
      setVal("pub-main-category-2", formData.mainCategory2 || "");
      setVal("pub-address", formData.address);
      setVal("pub-address-lat", formData.addressLat);
      setVal("pub-address-lng", formData.addressLng);
      setVal("pub-email", formData.email);
      setVal("pub-description", formData.description);
      setVal("pub-start", formData.startDate);
      setVal("pub-end", formData.endDate);
      setVal("pub-repeat-frequency", formData.repeatFrequency);
      setVal("pub-repeat-until", formData.repeatUntil);
      setVal("pub-capacity", formData.capacity);
      setVal("pub-price", formData.price);
      setVal("pub-event-type", formData.eventType);
      setVal("pub-ticket-link", formData.ticketLink);
      setVal("pub-audio-links", formData.audioLinks);
      setVal("pub-audio", formData.audio || "");
      setVal("pub-social-links", formData.socialLinks);
      setVal("pub-website", formData.website);
      setVal("pub-tags", formData.tags);
      
      // Checkbox répétition
      const repeatCheckbox = document.getElementById("pub-repeat-enabled");
      if (repeatCheckbox && formData.repeatEnabled) {
        repeatCheckbox.checked = true;
        toggleRepeatOptions();
      }
      
      // Boost sélectionné
      const boostRadio = document.querySelector(`input[name="pub-boost"][value="${formData.boost}"]`);
      if (boostRadio) boostRadio.checked = true;
      
      // Enchère Platinum
      if (formData.platinumBid) {
        currentPlatinumBid = formData.platinumBid;
      }
      
      if (formData.audio && typeof updateAudioPreview === 'function') updateAudioPreview();
      
      // Style pour la catégorie
      const catInput = document.getElementById("pub-main-category");
      if (catInput && formData.mainCategory) {
        catInput.style.background = '#0f172a';
        catInput.style.color = '#00ffc3';
        catInput.style.webkitTextFillColor = '#00ffc3';
      }
      
      updateTotalPrice();
      console.log('[FORM] ✅ Données du formulaire restaurées');
    }, 100);
    
  } catch (error) {
    console.error('[FORM] Erreur restauration:', error);
  }
}

function resetPublishForm() {
  if (!confirm("⚠️ Voulez-vous vraiment effacer toutes les données du formulaire ?")) {
    return;
  }
  
  // Effacer le localStorage
  localStorage.removeItem("publishFormData");
  currentPlatinumBid = 0;
  
  // Réinitialiser tous les champs
  const fields = [
    "pub-title", "pub-main-category", "pub-address", "pub-address-lat", "pub-address-lng",
    "pub-email", "pub-description", "pub-start", "pub-end", "pub-repeat-frequency",
    "pub-repeat-until", "pub-capacity", "pub-price", "pub-event-type", "pub-ticket-link",
    "pub-audio-links", "pub-social-links", "pub-website", "pub-tags"
  ];
  
  fields.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = "";
  });
  
  // Décocher la répétition
  const repeatCheckbox = document.getElementById("pub-repeat-enabled");
  if (repeatCheckbox) {
    repeatCheckbox.checked = false;
    toggleRepeatOptions();
  }
  
  // Boost standard
  const standardRadio = document.querySelector('input[name="pub-boost"][value="standard"]');
  if (standardRadio) standardRadio.checked = true;
  
  // Réinitialiser le style de la catégorie
  const catInput = document.getElementById("pub-main-category");
  if (catInput) {
    catInput.style.borderColor = '#334155';
  }
  
  updateTotalPrice();
  showNotification("🔄 Formulaire réinitialisé", "info");
  console.log('[FORM] 🔄 Formulaire réinitialisé');
}

// ⚠️⚠️⚠️ VALIDATION ET RECHERCHE D'ADRESSE MONDIALE
let addressSearchTimeout = null;

function debounceAddressSearch() {
  clearTimeout(addressSearchTimeout);
  addressSearchTimeout = setTimeout(() => {
    searchAddress();
  }, 400);
}

async function searchAddress() {
  const input = document.getElementById("pub-address");
  const suggestionsDiv = document.getElementById("pub-address-suggestions");
  
  if (!input || !suggestionsDiv) return;
  
  const query = input.value.trim();
  if (query.length < 3) {
    suggestionsDiv.style.display = "none";
    return;
  }
  
  try {
    // Utiliser Nominatim (OpenStreetMap) pour la recherche mondiale
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5&addressdetails=1`,
      {
        headers: {
          'Accept-Language': 'fr',
          'User-Agent': 'MapEvent/1.0'
        }
      }
    );
    
    if (!response.ok) return;
    
    const results = await response.json();
    
    if (results.length === 0) {
      suggestionsDiv.innerHTML = '<div style="padding:8px;color:var(--ui-text-muted);font-size:11px;">Aucune adresse trouvée</div>';
      suggestionsDiv.style.display = "block";
      return;
    }
    
    // Afficher les suggestions avec data attributes (évite les problèmes d'apostrophes)
    suggestionsDiv.innerHTML = results.map((r, index) => `
      <div class="address-suggestion" data-index="${index}" data-lat="${r.lat}" data-lng="${r.lon}"
           style="padding:8px 10px;cursor:pointer;border-bottom:1px solid rgba(255,255,255,0.1);font-size:12px;color:#fff;transition:background 0.15s;"
           onmouseover="this.style.background='rgba(0,255,195,0.15)'"
           onmouseout="this.style.background='transparent'">
        📍 ${escapeHtml(r.display_name)}
      </div>
    `).join('');
    
    // Stocker les résultats et ajouter les listeners
    window._addressResults = results;
    suggestionsDiv.querySelectorAll('.address-suggestion').forEach(div => {
      div.addEventListener('click', function() {
        const idx = parseInt(this.dataset.index);
        const result = window._addressResults[idx];
        if (result) {
          selectAddress(result.display_name, parseFloat(result.lat), parseFloat(result.lon));
        }
      });
    });
    
    suggestionsDiv.style.display = "block";
    
  } catch (error) {
    console.log('[ADDRESS] Erreur recherche:', error);
  }
}

function selectAddress(displayName, lat, lng) {
  console.log('[ADDRESS] 🔄 selectAddress appelée avec:', displayName, lat, lng);
  
  const input = document.getElementById("pub-address");
  const latInput = document.getElementById("pub-address-lat");
  const lngInput = document.getElementById("pub-address-lng");
  const suggestionsDiv = document.getElementById("pub-address-suggestions");
  const statusDiv = document.getElementById("pub-address-status");
  
  console.log('[ADDRESS] 📦 Éléments trouvés - input:', !!input, 'latInput:', !!latInput, 'lngInput:', !!lngInput);
  
  if (input) {
    input.value = displayName;
    console.log('[ADDRESS] ✅ Adresse écrite dans input:', input.value);
  } else {
    console.error('[ADDRESS] ❌ Element pub-address introuvable!');
  }
  
  if (latInput) latInput.value = lat;
  if (lngInput) lngInput.value = lng;
  if (suggestionsDiv) suggestionsDiv.style.display = "none";
  
  // Afficher le statut de validation
  if (statusDiv) {
    statusDiv.innerHTML = '<span style="color:#00ffc3;">✅ Adresse validée - Coordonnées: ' + lat.toFixed(4) + ', ' + lng.toFixed(4) + '</span>';
    statusDiv.style.display = "block";
  }
  
  // Mettre à jour le style du champ
  if (input) {
    input.style.borderColor = "rgba(0,255,195,0.5)";
    input.style.background = "rgba(0,255,195,0.05)";
  }
  
  console.log('[ADDRESS] ✅ Adresse sélectionnée:', displayName, 'Coords:', lat, lng);
}

async function validateAddress() {
  const input = document.getElementById("pub-address");
  const latInput = document.getElementById("pub-address-lat");
  const lngInput = document.getElementById("pub-address-lng");
  const statusDiv = document.getElementById("pub-address-status");
  const starSpan = document.getElementById("pub-address-star");
  const suggestionsDiv = document.getElementById("pub-address-suggestions");
  
  // Fermer les suggestions
  if (suggestionsDiv) suggestionsDiv.style.display = "none";
  
  if (!input || !input.value.trim()) return false;
  
  const addressValue = input.value.trim();
  
  // Vérifier qu'il y a un numéro de rue (obligatoire)
  const hasStreetNumber = /\d+/.test(addressValue);
  if (!hasStreetNumber) {
    if (statusDiv) {
      statusDiv.innerHTML = '<span style="color:#ff4444;">⚠️ Numéro de rue obligatoire (ex: 15 Rue de la Paix)</span>';
      statusDiv.style.display = "block";
    }
    input.style.borderColor = "#ff4444";
    input.style.background = "rgba(255,68,68,0.1)";
    if (starSpan) starSpan.style.color = "#ff4444";
    return false;
  }
  
  // Si déjà validée (coordonnées présentes), c'est bon
  if (latInput?.value && lngInput?.value) {
    return true;
  }
  
  // Sinon, essayer de géocoder l'adresse
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(input.value)}&limit=1`,
      {
        headers: {
          'Accept-Language': 'fr',
          'User-Agent': 'MapEvent/1.0'
        }
      }
    );
    
    if (!response.ok) throw new Error('Erreur réseau');
    
    const results = await response.json();
    
    if (results.length > 0) {
      const r = results[0];
      if (latInput) latInput.value = r.lat;
      if (lngInput) lngInput.value = r.lon;
      
      if (statusDiv) {
        statusDiv.innerHTML = '<span style="color:#00ffc3;">✅ Adresse validée automatiquement</span>';
        statusDiv.style.display = "block";
      }
      
      input.style.borderColor = "rgba(0,255,195,0.5)";
      input.style.background = "rgba(0,255,195,0.05)";
      if (starSpan) starSpan.style.color = "inherit";
      
      return true;
    } else {
      // Adresse non trouvée
      if (statusDiv) {
        statusDiv.innerHTML = '<span style="color:#ff4444;">⚠️ Adresse non reconnue - Le pointeur ne pourra pas être placé correctement</span>';
        statusDiv.style.display = "block";
      }
      
      input.style.borderColor = "#ff4444";
      input.style.background = "rgba(255,68,68,0.1)";
      if (starSpan) starSpan.style.color = "#ff4444";
      
      return false;
    }
    
  } catch (error) {
    console.log('[ADDRESS] Erreur validation:', error);
    return false;
  }
}

// Fermer les suggestions quand on clique ailleurs
document.addEventListener('click', function(e) {
  const suggestionsDiv = document.getElementById("pub-address-suggestions");
  const input = document.getElementById("pub-address");
  if (suggestionsDiv && input && !input.contains(e.target) && !suggestionsDiv.contains(e.target)) {
    suggestionsDiv.style.display = "none";
  }
});

function toggleAdvancedOptions() {
  const checkbox = document.getElementById("pub-advanced-options");
  const content = document.getElementById("pub-advanced-options-content");
  if (checkbox && content) {
    content.style.display = checkbox.checked ? "block" : "none";
  }
}

function initRepeatHandlers() {
  // Gérer les clics sur les jours de la semaine
  const weekdayLabels = document.querySelectorAll("#pub-repeat-weekdays label");
  weekdayLabels.forEach(label => {
    label.addEventListener("click", function(e) {
      const checkbox = this.querySelector("input[type='checkbox']");
      if (checkbox) {
        checkbox.checked = !checkbox.checked;
        updateRepeatPreview();
        // Mettre à jour le style visuel
        if (checkbox.checked) {
          this.style.background = "rgba(0,255,195,0.2)";
          this.style.borderColor = "rgba(0,255,195,0.5)";
        } else {
          this.style.background = "rgba(15,23,42,0.5)";
          this.style.borderColor = "var(--ui-card-border)";
        }
      }
    });
  });
}

function initMultipleImagesHandler() {
  const input = document.getElementById("pub-images-multiple");
  const preview = document.getElementById("pub-images-preview");
  
  if (input && preview) {
    input.addEventListener("change", function(e) {
      preview.innerHTML = "";
      const files = Array.from(e.target.files);
      files.forEach((file, index) => {
        if (file.type.startsWith("image/")) {
          const reader = new FileReader();
          reader.onload = function(e) {
            const img = document.createElement("img");
            img.src = e.target.result;
            img.style.width = "100%";
            img.style.height = "80px";
            img.style.objectFit = "cover";
            img.style.borderRadius = "6px";
            img.style.border = "1px solid var(--ui-card-border)";
            preview.appendChild(img);
          };
          reader.readAsDataURL(file);
        }
      });
    });
  }
}

// closeAuthModal() est maintenant dans auth.js et exposé via window.closeAuthModal

// Fonction GLOBALE ultra-simple pour le bouton Annuler (accessible depuis onclick inline)
window.fermerModalAuth = function() {
  console.log('[FERMER] fermerModalAuth appelé');
  if (typeof closeAuthModal === 'function') {
    closeAuthModal();
  } else {
    const b = document.getElementById('publish-modal-backdrop');
    const m = document.getElementById('publish-modal-inner');
    const a = document.getElementById('authModal');
    if (b) {
      b.style.display = 'none';
      b.style.visibility = 'hidden';
      b.style.opacity = '0';
    }
    if (m) {
      m.innerHTML = '';
      m.style.display = 'none';
    }
    if (a) {
      a.remove();
    }
    console.log('[FERMER] Modal fermé directement');
  }
};

function closePublishModal(e) {
  console.log('🚪 closePublishModal called', e?.type || 'direct call', e?.target?.id || 'no target');
  
  // ⚠️⚠️⚠️ PROTECTION COORDONNÉES : Vérifier si le clic est dans la zone du panneau gauche
  if (e && e.clientX !== undefined) {
    const leftPanel = document.getElementById("left-panel");
    if (leftPanel && leftPanel.offsetParent !== null) {
      const panelRect = leftPanel.getBoundingClientRect();
      // Si le clic est dans la zone du panneau gauche (avec une marge de 20px)
      if (e.clientX >= panelRect.left - 20 && 
          e.clientX <= panelRect.right + 20 && 
          e.clientY >= panelRect.top - 20 && 
          e.clientY <= panelRect.bottom + 20) {
        console.log('🚪 [GUARD] Clic dans la zone du left-panel (coordonnées) - IGNORÉ (pas de fermeture)', 
          { clickX: e.clientX, clickY: e.clientY, panelRect: { left: panelRect.left, right: panelRect.right, top: panelRect.top, bottom: panelRect.bottom } });
        return;
      }
    }
  }
  
  // ⚠️⚠️⚠️ PROTECTION FILTRE : Ne jamais fermer si le clic vient du left-panel (filtre de catégories)
  if (e && e.target) {
    const isInLeftPanel = e.target.closest('#left-panel') || 
                         e.target.closest('.explorer-col') ||
                         e.target.closest('[onclick*="toggleCategory"]') ||
                         e.target.closest('[onclick*="selectLeafCategory"]') ||
                         e.target.closest('[onclick*="openNextLevel"]') ||
                         e.target.closest('[onchange*="toggleCategory"]');
    if (isInLeftPanel) {
      console.log('🚪 [GUARD] Clic dans le left-panel (filtre) - IGNORÉ (pas de fermeture)');
      return;
    }
    
    // ⚠️⚠️⚠️ PROTECTION FORMULAIRE PUBLICATION : Ne jamais fermer si clic sur éléments du formulaire
    const isPublishFormElement = e.target.closest('#publish-modal') ||
                                  e.target.closest('#publish-modal-inner') ||
                                  e.target.closest('#pub-category-suggestions') ||
                                  e.target.id?.startsWith('pub-') ||
                                  e.target.closest('[id^="pub-"]') ||
                                  e.target.closest('[onclick*="selectCategoryForPublish"]') ||
                                  e.target.tagName === 'INPUT' ||
                                  e.target.tagName === 'TEXTAREA' ||
                                  e.target.tagName === 'SELECT' ||
                                  e.target.tagName === 'LABEL';
    
    // Mais permettre la fermeture si c'est le vrai bouton croix
    const isCloseButton = (e.target.textContent?.trim() === '✕' || e.target.textContent?.trim() === '×') &&
                          (e.target.tagName === 'BUTTON' || e.target.tagName === 'SPAN') &&
                          !e.target.id?.startsWith('pub-');
    
    if (isPublishFormElement && !isCloseButton) {
      console.log('🚪 [GUARD] Clic sur élément du formulaire publication - IGNORÉ (pas de fermeture)', e.target.id || e.target.tagName);
      return;
    }
  }
  
  // ⚠️⚠️⚠️ Si c'est un clic sur le VRAI bouton de fermeture (croix), fermer directement
  if (e && e.target) {
    const isActualCloseButton = (e.target.textContent?.trim() === '✕' || e.target.textContent?.trim() === '×') &&
                                 (e.target.tagName === 'BUTTON' || e.target.tagName === 'SPAN') &&
                                 !e.target.id?.startsWith('pub-');
    
    if (isActualCloseButton) {
      e.stopPropagation();
      // ⚠️ SAUVEGARDER les données avant de fermer
      savePublishFormData();
      const backdrop = document.getElementById("publish-modal-backdrop");
      if (backdrop) {
        backdrop.style.display = "none";
        console.log('🚪 Modal fermé via bouton croix (données sauvegardées)');
        return;
      }
    }
  }
  
  // GUARD: Ne jamais fermer le modal d'auth (register/login) SAUF si c'est explicitement demandé
  // Permettre la fermeture si on clique sur le backdrop ou sur les boutons de fermeture
  const authModal = document.getElementById("authModal");
  const backdrop = document.getElementById("publish-modal-backdrop");
  const modalInner = document.getElementById("publish-modal-inner");
  
  // Vérifier si le modal d'auth est visible (backdrop visible OU modalInner contient du contenu auth)
  const isAuthModalVisible = (backdrop && backdrop.offsetParent !== null && backdrop.style.display !== 'none') ||
                             (modalInner && modalInner.innerHTML.includes('auth-cancel-btn')) ||
                             (authModal && authModal.offsetParent !== null);
  
  if (isAuthModalVisible) {
    // Si c'est un clic sur le backdrop (l'élément backdrop lui-même, pas ses enfants)
    if (e && (e.target?.id === 'publish-modal-backdrop' || e.target === backdrop)) {
      console.log('🚪 [AUTH] Fermeture autorisee via backdrop');
      closeAuthModal();
      return;
    }
    
    // ⚠️⚠️⚠️ IMPORTANT : Ne PAS fermer si on clique sur des éléments du formulaire
    if (e && e.target) {
      const target = e.target;
      
      // Ignorer les clics sur les éléments de photo
      const isPhotoElement = target.closest('.pro-register-photo-upload') ||
                            target.closest('#pro-photo-input') ||
                            target.closest('#pro-photo-preview') ||
                            target.closest('.pro-register-photo-placeholder') ||
                            target.id === 'pro-photo-input' ||
                            target.id === 'pro-photo-preview' ||
                            target.classList?.contains('pro-register-photo-upload') ||
                            target.classList?.contains('pro-register-photo-input');
      
      if (isPhotoElement) {
        console.log('🚪 [GUARD] Clic sur élément de photo - IGNORÉ (pas de fermeture)');
        return;
      }
      
      // ⚠️⚠️⚠️ IMPORTANT : Ignorer TOUS les éléments du formulaire d'inscription
      // Vérifier si on clique sur n'importe quel élément du formulaire
      const isFormElement = target.closest('.pro-register-container') ||
                           target.closest('.pro-register-form') ||
                           target.closest('#publish-modal-inner') ||
                           target.closest('#authModal') ||
                           target.closest('form') ||
                           target.closest('.pro-register-field') ||
                           target.closest('.pro-register-input') ||
                           target.closest('.pro-register-photo-upload') ||
                           target.closest('.pro-register-password-container') ||
                           target.closest('.pro-register-password-toggle') ||
                           target.closest('.pro-register-label') ||
                           target.id === 'pro-photo-input' ||
                           target.id === 'pro-photo-preview' ||
                           target.classList?.contains('pro-register-photo-upload') ||
                           target.classList?.contains('pro-register-photo-input') ||
                           target.classList?.contains('pro-register-password-toggle') ||
                           target.classList?.contains('pro-register-password-container') ||
                           target.classList?.contains('pro-register-field') ||
                           target.classList?.contains('pro-register-input') ||
                           target.classList?.contains('pro-register-form') ||
                           (target.tagName === 'INPUT' && target.closest('.pro-register-form')) ||
                           (target.tagName === 'BUTTON' && target.closest('.pro-register-form')) ||
                           (target.tagName === 'LABEL' && target.closest('.pro-register-form'));
      
      if (isFormElement) {
        console.log('🚪 [GUARD] Clic sur élément du formulaire - IGNORÉ (pas de fermeture)', target.id || target.className || target.tagName);
        return;
      }
      
      // Ignorer les boutons d'affichage/masquage du mot de passe (double vérification)
      const isPasswordToggle = target.classList?.contains('pro-register-password-toggle') ||
                              target.closest('.pro-register-password-toggle') ||
                              target.closest('.pro-register-password-container') ||
                              (target.tagName === 'BUTTON' && target.onclick && target.onclick.toString().includes('toggleProPasswordVisibility'));
      
      if (isPasswordToggle) {
        console.log('🚪 [GUARD] Clic sur bouton toggle mot de passe - IGNORÉ (pas de fermeture)');
        return;
      }
      
      // Ignorer le bouton de soumission du formulaire d'inscription
      const isSubmitButton = target.id === 'pro-submit-btn' ||
                            target.closest('#pro-submit-btn') ||
                            (target.tagName === 'BUTTON' && target.type === 'submit' && target.closest('.pro-register-form')) ||
                            (target.tagName === 'BUTTON' && target.form && target.form.classList.contains('pro-register-form'));
      
      if (isSubmitButton) {
        console.log('🚪 [AUTH] Bouton de soumission detecte - laisser passer');
        // Ne pas bloquer, laisser le formulaire se soumettre normalement
        return;
      }
    }
    
      // Si c'est un bouton de fermeture (X, Annuler, etc.), permettre la fermeture
      // Vérifier par ID, par onclick, ou par classe
      if (e && e.target) {
        const target = e.target;
        const isCancelButton = target.id === 'auth-cancel-btn' ||
                              target.id === 'auth-cancel-btn-pro' ||
                              target.closest('#auth-cancel-btn') ||
                              target.closest('#auth-cancel-btn-pro') ||
                              (target.tagName === 'BUTTON' && target.textContent.trim() === 'Annuler') ||
                              target.closest('button[onclick*="closeAuthModal"]') ||
                              target.closest('button[onclick*="fermerModalAuth"]') ||
                              target.closest('button[onclick*="closePublishModal"]') ||
                              target.closest('button[aria-label*="fermer" i]') ||
                              target.closest('button[aria-label*="close" i]') ||
                              target.closest('button[title*="Fermer" i]') ||
                              target.closest('button[title*="Close" i]');
      
      if (isCancelButton) {
        console.log('🚪 [AUTH] Fermeture autorisee via bouton Annuler/fermeture - ID:', target.id || 'pas d\'ID', 'text:', target.textContent?.trim() || 'pas de texte');
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        closeAuthModal();
        return false;
      }
    }
    
    // Si c'est un appel direct à closeAuthModal (sans event), permettre
    if (!e) {
      console.log('🚪 [AUTH] Fermeture autorisee via appel direct closeAuthModal');
      closeAuthModal();
      return;
    }
    
    // Sinon, bloquer la fermeture automatique
    console.log('🚪 [GUARD] Auth modal visible - closePublishModal bloque');
    return;
  }
  
  // Vérifier aussi si le modal d'onboarding est visible
  const onboardingModal = document.getElementById("onboardingModal");
  if (onboardingModal && onboardingModal.offsetParent !== null) {
    console.log('🚪 [GUARD] Onboarding modal visible - closePublishModal bloque');
    return;
  }
  
  if (e && e.target && e.target.id !== "publish-modal-backdrop") {
    const modal = document.getElementById("publish-modal");
    const modalInner = document.getElementById("publish-modal-inner");
    // Ne ferme pas si on clique sur un élément dans la modal ou le modal inner
    if ((modal && modal.contains(e.target)) || (modalInner && modalInner.contains(e.target))) return;
  }
  
  // Réutiliser la variable backdrop déjà déclarée plus haut
  if (backdrop) {
    backdrop.style.display = "none";
    console.log('🚪 Modal closed - backdrop display set to none');
    
    // ⚠️⚠️⚠️ Réinitialiser le z-index du panneau gauche
    const leftPanel = document.getElementById("left-panel");
    if (leftPanel) {
      leftPanel.style.zIndex = "";
    }
    
    // ⚠️ Nettoyer le mode édition si on ferme le modal
    if (window.editingItem) {
      window.editingItem = null;
      console.log('🚪 Mode édition annulé');
    }
  }
}

async function onSubmitPublishForm(e) {
  e.preventDefault();
  
  // Vérifier que l'utilisateur est connecté
  if (!currentUser || !currentUser.isLoggedIn) {
    showNotification("⚠️ Vous devez être connecté pour publier", "warning");
    openLoginModal();
    return false;
  }
  
  // ⚠️ MODE ÉDITION - Modification d'une annonce existante
  if (window.editingItem) {
    return await handleEditSubmit(e);
  }
  
  // ⚠️⚠️⚠️ VALIDATION DES DATES (pour les events)
  if (currentMode === "event") {
    if (!validateEventDates()) {
      showNotification("⚠️ Les dates de l'événement sont invalides (date passée ou fin avant début)", "error");
      return false;
    }
  }
  
  // ⚠️⚠️⚠️ VALIDATION DE L'ADRESSE
  const addressLat = document.getElementById("pub-address-lat")?.value;
  const addressLng = document.getElementById("pub-address-lng")?.value;
  
  if (!addressLat || !addressLng) {
    // Essayer de valider l'adresse une dernière fois
    const addressValid = await validateAddress();
    if (!addressValid) {
      showNotification("⚠️ L'adresse n'est pas valide. Veuillez sélectionner une adresse dans les suggestions.", "error");
      return false;
    }
  }
  
  // Récupérer les données du formulaire
  const title = document.getElementById("pub-title")?.value.trim();
  const mainCategory = document.getElementById("pub-main-category")?.value.trim();
  const mainCategory2 = document.getElementById("pub-main-category-2")?.value.trim();
  const address = document.getElementById("pub-address")?.value.trim();
  const phone = document.getElementById("pub-phone")?.value.trim();
  const email = document.getElementById("pub-email")?.value.trim();
  const description = document.getElementById("pub-description")?.value.trim();
  const ticketUrl = document.getElementById("pub-ticket")?.value.trim();
  const socialLinks = document.getElementById("pub-social")?.value.trim();
  const videoLinks = document.getElementById("pub-videos")?.value.trim();
  const audioEventLinks = document.getElementById("pub-audio-links")?.value.trim(); // Liens sons pour events
  
  // Pour les events : dates
  const startDate = document.getElementById("pub-start")?.value;
  const endDate = document.getElementById("pub-end")?.value;
  
  // RÉPÉTITIONS (pour les events)
  const repeatEnabled = document.getElementById("pub-repeat-enabled")?.checked || false;
  const repeatFrequency = document.getElementById("pub-repeat-frequency")?.value || "weekly";
  const repeatUntil = document.getElementById("pub-repeat-until")?.value || null;
  const repeatCount = document.getElementById("pub-repeat-count")?.value || null;
  const repeatWeekdays = Array.from(document.querySelectorAll(".repeat-weekday:checked")).map(cb => parseInt(cb.value));
  
  // OPTIONS AVANCÉES (pour les events)
  const capacity = document.getElementById("pub-capacity")?.value || null;
  const price = document.getElementById("pub-price")?.value || null;
  const eventType = document.getElementById("pub-event-type")?.value || "public";
  const wheelchair = document.getElementById("pub-wheelchair")?.checked || false;
  const parking = document.getElementById("pub-parking")?.checked || false;
  const transport = document.getElementById("pub-transport")?.checked || false;
  const languages = Array.from(document.querySelectorAll(".pub-language:checked")).map(cb => cb.value);
  const tags = document.getElementById("pub-tags")?.value?.split(",").map(t => t.trim()).filter(t => t) || [];
  
  // PHOTOS MULTIPLES
  const mainImageFile = document.getElementById("pub-image")?.files[0];
  const additionalImages = Array.from(document.getElementById("pub-images-multiple")?.files || []);
  
  // Convertir l'image principale en base64 pour envoi au backend
  let mainImageBase64 = null;
  if (mainImageFile) {
    try {
      mainImageBase64 = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
          // Redimensionner l'image pour optimiser la taille (max 1200px)
          const img = new window.Image();
          img.onload = () => {
            const canvas = document.createElement('canvas');
            const maxSize = 1200;
            let w = img.width, h = img.height;
            if (w > maxSize || h > maxSize) {
              const ratio = Math.min(maxSize / w, maxSize / h);
              w = Math.round(w * ratio);
              h = Math.round(h * ratio);
            }
            canvas.width = w;
            canvas.height = h;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, w, h);
            resolve(canvas.toDataURL('image/jpeg', 0.82));
          };
          img.onerror = () => resolve(reader.result); // fallback: base64 brut
          img.src = reader.result;
        };
        reader.onerror = reject;
        reader.readAsDataURL(mainImageFile);
      });
      console.log('[PUBLISH] ✅ Image convertie en base64:', mainImageBase64?.substring(0, 50) + '...');
    } catch (imgError) {
      console.warn('[PUBLISH] ⚠️ Erreur conversion image:', imgError);
    }
  }
  
  // Pour les bookings : audio et niveau
  const audioLinks = document.getElementById("pub-audio")?.value.trim();
  const level = document.getElementById("pub-level")?.value.trim();
  const priceEstimate = document.getElementById("pub-price-estimate")?.value.trim();
  
  // Boost sélectionné
  const boostRadio = document.querySelector('input[name="pub-boost"]:checked');
  const boost = boostRadio?.value || 'basic';
  
  // Validation
  if (!title || !mainCategory || !address || !email || !description) {
    showNotification("⚠️ Veuillez remplir tous les champs obligatoires (*)", "warning");
    return false;
  }
  
  if (currentMode === "event" && (!startDate || !endDate)) {
    showNotification("⚠️ Veuillez indiquer les dates de l'événement", "warning");
    return false;
  }
  
  // Utiliser les coordonnées pré-validées si disponibles
  let lat = null, lng = null, city = "";
  const preValidatedLat = document.getElementById("pub-address-lat")?.value;
  const preValidatedLng = document.getElementById("pub-address-lng")?.value;
  
  if (preValidatedLat && preValidatedLng) {
    lat = parseFloat(preValidatedLat);
    lng = parseFloat(preValidatedLng);
    city = address.split(',')[0];
    showNotification("✅ Adresse validée", "success");
  } else {
    // Géocoder l'adresse
    showNotification("🔍 Recherche de l'adresse...", "info");
    
    try {
      const geoResponse = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}&limit=1`, {
        headers: { 'User-Agent': 'MapEventAI/1.0' }
      });
      const geoData = await geoResponse.json();
      
      if (geoData.length > 0) {
        lat = parseFloat(geoData[0].lat);
        lng = parseFloat(geoData[0].lon);
        city = geoData[0].display_name.split(',')[0];
      } else {
        showNotification("⚠️ Adresse introuvable. Vérifiez et réessayez.", "warning");
        return false;
      }
    } catch (error) {
      console.error('Erreur géocodage:', error);
      showNotification("❌ Erreur de géocodage. Réessayez.", "error");
      return false;
    }
  }
  
  // Créer l'objet selon le mode
  const newId = Date.now();
  const now = new Date().toISOString();
  
  const categoriesArr = [mainCategory, mainCategory2].filter(Boolean);
  let newItem = {
    id: newId,
    title: title,
    name: title,
    categories: categoriesArr,
    mainCategory: categoriesArr[0] || mainCategory,
    address: address,
    location: address, // Backend attend "location"
    city: city,
    lat: lat,
    lng: lng,
    latitude: lat,   // Backend attend "latitude"
    longitude: lng,  // Backend attend "longitude"
    description: description,
    imageData: mainImageBase64, // Photo uploadée par l'utilisateur (base64 -> S3)
    email: email,
    phone: phone,
    socialLinks: socialLinks ? socialLinks.split('\n').filter(l => l.trim()) : [],
    videoLinks: videoLinks ? videoLinks.split('\n').filter(l => l.trim()) : [],
    boost: boost,
    verified: false,
    likes: 0,
    comments: 0,
    rating: "4.5",
    createdBy: currentUser.id,
    createdByName: currentUser.name,
    createdAt: now,
    type: currentMode
  };
  
  if (currentMode === "event") {
    newItem.startDate = startDate;
    newItem.endDate = endDate;
    newItem.ticketUrl = ticketUrl;
    newItem.participants = 0;
    newItem.status = "upcoming";
    
    // LIENS AUDIO (SoundCloud, Spotify, etc.)
    if (audioEventLinks) {
      newItem.audioLinks = audioEventLinks.split('\n').filter(l => l.trim());
    }
    
    // RÉPÉTITIONS (hebdomadaire ou mensuel uniquement)
    if (repeatEnabled) {
      const repeatPrice = repeatFrequency === "weekly" ? 15 : 4;
      newItem.repeat = {
        enabled: true,
        frequency: repeatFrequency, // "weekly" ou "monthly"
        until: repeatUntil,
        price: repeatPrice,
        // Pour la logique de réapparition automatique
        nextOccurrence: null, // Sera calculé par le backend
        autoReappear: true
      };
    }
    
    // OPTIONS AVANCÉES
    newItem.advancedOptions = {
      capacity: capacity ? parseInt(capacity) : null,
      price: price ? parseFloat(price) : null,
      eventType: eventType,
      accessibility: {
        wheelchair: wheelchair,
        parking: parking,
        publicTransport: transport
      },
      languages: languages.length > 0 ? languages : ["fr"],
      tags: tags.length > 0 ? tags : []
    };
    
    // PHOTOS MULTIPLES
    if (additionalImages.length > 0) {
      newItem.additionalImages = additionalImages.map((file, index) => ({
        index: index,
        filename: file.name,
        type: file.type,
        size: file.size
        // Note: Les fichiers seront uploadés séparément
      }));
    }
    
    eventsData.push(newItem);
  } else if (currentMode === "booking") {
    newItem.audioLinks = audioLinks ? audioLinks.split('\n').filter(l => l.trim()) : [];
    newItem.level = level;
    newItem.priceEstimate = priceEstimate;
    bookingsData.push(newItem);
  } else if (currentMode === "service") {
    newItem.priceEstimate = priceEstimate;
    servicesData.push(newItem);
  }
  
  // Sauvegarder dans le backend
  try {
    // Préparer les données pour le backend
    const backendData = {
      ...newItem,
      userId: currentUser.id
    };
    
    // ⚠️ CRITIQUE : Convertir startDate/endDate au format backend (date, time, end_date, end_time)
    if (currentMode === "event" && startDate) {
      const [datePart, timePart] = startDate.split('T');
      backendData.date = datePart;
      backendData.time = timePart ? timePart + ':00' : '00:00:00';
    }
    if (currentMode === "event" && endDate) {
      const [endDatePart, endTimePart] = endDate.split('T');
      backendData.end_date = endDatePart;
      backendData.end_time = endTimePart ? endTimePart + ':00' : '23:59:59';
    }
    
    await fetch(`${window.API_BASE_URL}/${currentMode}s`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(backendData)
    });
  } catch (error) {
    console.error('Erreur sauvegarde backend:', error);
    // Continuer même si le backend échoue (sauvegarde locale)
  }
  
  // Calculer le prix final
  const finalPrice = window.currentPublishPrice || 1;
  
  // Stocker les données pour après le paiement
  window.pendingPublishData = {
    newItem: newItem,
    mode: currentMode,
    lat: lat,
    lng: lng,
    boost: boost,
    price: finalPrice
  };
  
  // Ouvrir le modal de paiement Stripe
  openStripePaymentModal(finalPrice, boost);
  
  return false;
}

// ⚠️ GESTION DE LA MODIFICATION D'UNE ANNONCE EXISTANTE
async function handleEditSubmit(e) {
  e.preventDefault();
  
  const editingItem = window.editingItem;
  const itemId = editingItem.id;
  const itemType = editingItem.mode || editingItem.type || 'event';
  
  // Récupérer les données du formulaire
  const title = document.getElementById("pub-title")?.value.trim();
  const mainCategory = document.getElementById("pub-main-category")?.value.trim();
  const mainCategory2 = document.getElementById("pub-main-category-2")?.value.trim();
  const address = document.getElementById("pub-address")?.value.trim();
  const phone = document.getElementById("pub-phone")?.value.trim();
  const email = document.getElementById("pub-email")?.value.trim();
  const description = document.getElementById("pub-description")?.value.trim();
  
  const lat = parseFloat(document.getElementById("pub-address-lat")?.value) || editingItem.lat;
  const lng = parseFloat(document.getElementById("pub-address-lng")?.value) || editingItem.lng;
  
  const startDate = document.getElementById("pub-start")?.value;
  const endDate = document.getElementById("pub-end")?.value;
  
  if (!title || !address) {
    showNotification("⚠️ Veuillez remplir les champs obligatoires", "warning");
    return false;
  }
  
  const categoriesArr = [mainCategory, mainCategory2].filter(Boolean);
  const updateData = {
    title: title,
    description: description,
    location: address,
    address: address,
    latitude: lat,
    longitude: lng,
    email: email,
    phone: phone,
    categories: categoriesArr.length > 0 ? categoriesArr : editingItem.categories
  };
  
  if (itemType === 'event') {
    if (startDate) updateData.date = startDate.split('T')[0];
    if (startDate) updateData.time = startDate.split('T')[1];
    if (endDate) updateData.end_date = endDate.split('T')[0];
    if (endDate) updateData.end_time = endDate.split('T')[1];
  }
  
  // Afficher un loader
  showNotification("⏳ Enregistrement des modifications...", "info");
  
  try {
    const token = typeof getAuthToken === 'function' ? getAuthToken() : localStorage.getItem('accessToken');
    const endpoint = itemType === 'event' ? 'events' : itemType === 'booking' ? 'bookings' : 'services';
    
    const response = await fetch(`${window.API_BASE_URL}/${endpoint}/${itemId}`, {
      method: 'PUT',
      headers: { 
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json' 
      },
      body: JSON.stringify(updateData)
    });
    
    if (response.ok) {
      // Mettre à jour localement
      const dataArray = itemType === 'event' ? eventsData : itemType === 'booking' ? bookingsData : servicesData;
      const index = dataArray.findIndex(i => i.id === itemId);
      if (index !== -1) {
        dataArray[index] = { ...dataArray[index], ...updateData, title: title, name: title };
      }
      
      // Nettoyer
      window.editingItem = null;
      closePublishModal();
      refreshMarkers();
      
      showNotification("✅ Modifications enregistrées !", "success");
      
      // Revenir à Mes Annonces après un court délai
      setTimeout(() => showMesAnnoncesModal(), 500);
    } else {
      const err = await response.json();
      showNotification("❌ Erreur: " + (err.error || "Impossible de modifier"), "error");
    }
  } catch (error) {
    console.error('Erreur modification:', error);
    showNotification("❌ Erreur de connexion", "error");
  }
  
  return false;
}

// ⚠️⚠️⚠️ MODAL PAIEMENT STRIPE (MODE RÉEL)
function openStripePaymentModal(amount, boost) {
  const boostLabels = {
    standard: 'Standard',
    bronze: '🥉 Bronze',
    silver: '🥈 Silver',
    platinum: '💎 Platinum'
  };
  
  const paymentHtml = `
    <div id="stripe-payment-modal" style="position:fixed;inset:0;z-index:10001;background:rgba(0,0,0,0.85);display:flex;align-items:center;justify-content:center;padding:20px;">
      <div style="background:linear-gradient(135deg,#0f172a,#1e293b);border:2px solid #00ffc3;border-radius:16px;max-width:400px;width:100%;box-shadow:0 0 50px rgba(0,255,195,0.2);">
        <div style="padding:24px;">
          <div style="text-align:center;margin-bottom:20px;">
            <div style="font-size:40px;margin-bottom:8px;">💳</div>
            <h2 style="margin:0;font-size:20px;color:#00ffc3;">Paiement sécurisé</h2>
            <p style="font-size:12px;color:#94a3b8;margin-top:4px;">Powered by Stripe</p>
            <div style="margin-top:8px;padding:4px 10px;background:rgba(0,255,195,0.1);border-radius:20px;display:inline-block;">
              <span style="color:#00ffc3;font-size:10px;font-weight:600;">🔒 MODE LIVE - PAIEMENT RÉEL</span>
            </div>
          </div>
          
          <!-- RÉSUMÉ -->
          <div style="background:rgba(0,0,0,0.3);border-radius:10px;padding:12px;margin-bottom:16px;">
            <div style="font-size:11px;color:#94a3b8;margin-bottom:8px;">Récapitulatif</div>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
              <span style="color:#e2e8f0;font-size:13px;">Publication ${currentMode}</span>
              <span style="color:#00ffc3;font-weight:600;">1.- CHF</span>
            </div>
            ${boost !== 'standard' ? `
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
              <span style="color:#e2e8f0;font-size:13px;">Boost ${boostLabels[boost] || boost}</span>
              <span style="color:#a78bfa;font-weight:600;">+${boost === 'platinum' ? currentPlatinumBid : (boost === 'bronze' ? 5 : boost === 'silver' ? 10 : 0)}.- CHF</span>
            </div>
            ` : ''}
            ${document.getElementById("pub-repeat-enabled")?.checked ? `
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
              <span style="color:#e2e8f0;font-size:13px;">Répétition</span>
              <span style="color:#ffc800;font-weight:600;">+${document.getElementById("pub-repeat-frequency")?.value === 'weekly' ? 15 : 4}.- CHF</span>
            </div>
            ` : ''}
            <div style="border-top:1px solid #334155;margin-top:8px;padding-top:8px;display:flex;justify-content:space-between;align-items:center;">
              <span style="color:#fff;font-weight:700;font-size:14px;">TOTAL</span>
              <span style="color:#00ffc3;font-weight:700;font-size:20px;">${amount}.- CHF</span>
            </div>
          </div>
          
          <!-- FORMULAIRE STRIPE -->
          <div id="stripe-card-element" style="background:#1e293b;border:1px solid #334155;border-radius:8px;padding:12px;margin-bottom:16px;">
            <!-- Stripe Elements sera injecté ici -->
            <div style="color:#94a3b8;font-size:12px;text-align:center;">
              Chargement du formulaire de paiement...
            </div>
          </div>
          
          <div id="stripe-card-errors" style="display:none;color:#ff4444;font-size:11px;margin-bottom:12px;"></div>
          
          <button id="stripe-submit-btn" onclick="processStripePayment(${amount})" style="width:100%;padding:14px;border-radius:10px;border:none;background:linear-gradient(135deg,#00ffc3,#00d4a4);color:#0f172a;font-weight:700;cursor:pointer;font-size:14px;transition:transform 0.2s,box-shadow 0.2s;" onmouseover="this.style.transform='scale(1.02)';this.style.boxShadow='0 4px 20px rgba(0,255,195,0.4)'" onmouseout="this.style.transform='scale(1)';this.style.boxShadow='none'">
            💳 Payer ${amount}.- CHF
          </button>
          
          <button onclick="closeStripePaymentModal()" style="width:100%;margin-top:10px;padding:10px;border-radius:8px;border:1px solid #475569;background:transparent;color:#94a3b8;cursor:pointer;font-size:12px;">
            Annuler
          </button>
          
          <div style="text-align:center;margin-top:12px;">
            <img src="https://stripe.com/img/v3/home/social.png" alt="Stripe" style="height:20px;opacity:0.6;">
            <div style="font-size:9px;color:#64748b;margin-top:4px;">Paiement 100% sécurisé • Données chiffrées</div>
          </div>
        </div>
      </div>
    </div>
  `;
  
  document.body.insertAdjacentHTML('beforeend', paymentHtml);
  
  // Initialiser Stripe Elements
  initStripeCardElement();
}

function closeStripePaymentModal() {
  const modal = document.getElementById("stripe-payment-modal");
  if (modal) modal.remove();
}

// Initialiser Stripe Card Element (pas utilisé pour Checkout)
async function initStripeCardElement() {
  const cardElement = document.getElementById("stripe-card-element");
  
  // Afficher un message indiquant la redirection vers Stripe
  if (cardElement) {
    cardElement.innerHTML = `
      <div style="text-align:center;">
        <div style="color:#00ffc3;font-size:13px;font-weight:600;margin-bottom:8px;">💳 Paiement sécurisé Stripe</div>
        <div style="color:#94a3b8;font-size:11px;">Vous serez redirigé vers la page de paiement Stripe</div>
        <div style="color:#e2e8f0;font-size:10px;margin-top:6px;">Carte bancaire • TWINT • Apple Pay • Google Pay</div>
      </div>
    `;
  }
}

// ⚠️⚠️⚠️ VRAI PAIEMENT STRIPE CHECKOUT
async function processStripePayment(amount) {
  const submitBtn = document.getElementById("stripe-submit-btn");
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = '⏳ Redirection vers Stripe...';
  }
  
  try {
    const data = window.pendingPublishData;
    if (!data) {
      throw new Error('Données de publication manquantes');
    }
    
    // Générer un userId si l'utilisateur n'en a pas
    const userId = currentUser?.id || currentUser?.email || `guest_${Date.now()}`;
    
    console.log('[STRIPE] Création session Checkout pour', amount, 'CHF, userId:', userId);
    
    // Appeler le backend pour créer une session Stripe Checkout
    // ⚠️ Champs requis par le backend: userId, paymentType, amount
    const response = await fetch(`${window.API_BASE_URL}/payments/create-checkout-session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': localStorage.getItem('id_token') ? `Bearer ${localStorage.getItem('id_token')}` : ''
      },
      body: JSON.stringify({
        userId: userId,
        paymentType: 'publication',
        amount: amount * 100, // Convertir en centimes pour Stripe
        currency: 'chf',
        email: currentUser?.email || data.newItem?.email || '',
        product_name: `Publication ${data.mode}: ${data.newItem?.title || 'Événement'}`,
        description: `Boost: ${data.boost}${data.newItem?.repeat?.enabled ? ' + Répétition' : ''}`,
        metadata: {
          eventId: String(data.newItem?.id || ''),
          mode: data.mode || 'event',
          boost: data.boost || 'standard',
          repeatEnabled: String(data.newItem?.repeat?.enabled || false),
          title: data.newItem?.title || ''
        }
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `Erreur serveur: ${response.status}`);
    }
    
    const result = await response.json();
    
    if (!result.sessionId && !result.url) {
      throw new Error('Session Stripe non créée');
    }
    
    // Sauvegarder les données en localStorage pour après le paiement
    localStorage.setItem('pendingPublishData', JSON.stringify(data));
    
    // Rediriger vers Stripe Checkout
    if (result.url) {
      // Redirection directe vers l'URL de checkout
      window.location.href = result.url;
    } else if (result.sessionId) {
      // Charger Stripe.js si pas encore chargé
      if (typeof Stripe === 'undefined' && typeof window.loadStripe === 'function') {
        await window.loadStripe();
      }
      // Utiliser Stripe.js pour rediriger
      if (typeof Stripe !== 'undefined') {
        const stripeInstance = Stripe(result.publicKey || 'pk_live_51Sfg8g2YO5zMBO7yRz2yRw9SZMJhYY8bfxLYT7v6VgQ77lFFwaUOGa5WYD1h7SDUgNkyABKnGFu3KN5p4PwT1Eqr00CisIZv67');
        const { error } = await stripeInstance.redirectToCheckout({ sessionId: result.sessionId });
        if (error) {
          throw new Error(error.message);
        }
      } else {
        throw new Error('Stripe.js non chargé');
      }
    }
    
  } catch (error) {
    console.error('[STRIPE] Erreur:', error);
    showNotification(`❌ Erreur: ${error.message}`, "error");
    
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `💳 Payer ${amount}.- CHF`;
    }
  }
}

// Finaliser la publication après paiement
async function finalizePublish() {
  const data = window.pendingPublishData;
  if (!data) {
    console.error('[PUBLISH] ❌ Données de publication perdues - pendingPublishData est null');
    showNotification("❌ Erreur: Données de publication perdues. Veuillez réessayer.", "error");
    return;
  }
  
  console.log('[PUBLISH] 🔄 Tentative de création avec données:', JSON.stringify(data.newItem, null, 2));
  
  // Sauvegarder dans le backend D'ABORD
  let backendSuccess = false;
  try {
    const token = typeof getAuthToken === 'function' ? getAuthToken() : localStorage.getItem('accessToken');
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = 'Bearer ' + token;
    
    // Préparer les données avec les bons noms de champs pour le backend
    const backendData = {
      ...data.newItem,
      // Mapper les champs frontend -> backend
      location: data.newItem.address || data.newItem.location,
      latitude: data.newItem.lat || data.newItem.latitude,
      longitude: data.newItem.lng || data.newItem.longitude,
      userId: currentUser?.id,
      creator_id: currentUser?.id,
      paymentStatus: 'paid',
      paymentAmount: data.price
    };
    
    console.log('[PUBLISH] 📤 Envoi au backend:', window.API_BASE_URL + '/' + data.mode + 's');
    console.log('[PUBLISH] 📤 Données envoyées:', JSON.stringify(backendData, null, 2));
    
    const response = await fetch(`${window.API_BASE_URL}/${data.mode}s`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(backendData)
    });
    
    const responseText = await response.text();
    console.log('[PUBLISH] 📥 Réponse backend:', response.status, responseText);
    
    if (response.ok) {
      backendSuccess = true;
      // Récupérer l'ID généré par le backend
      try {
        const result = JSON.parse(responseText);
        if (result.id) {
          console.log('[PUBLISH] ✅ ID backend reçu:', result.id);
          data.newItem.id = result.id; // Utiliser l'ID du backend !
        }
        if (result.creator_id) {
          console.log('[PUBLISH] ✅ creator_id confirmé:', result.creator_id);
        }
// ===== CODE MOVED TO themes.js (564 lines) =====
// Themes UI & carte (color picker, hsvToRgb, drawSVCanvas, cycleUITheme, cycleMapTheme, applyMapTheme)
// Load via <script src="themes.js"></script> in mapevent.html

function generateRandomDate(daysFromNow, hoursVariation = 0) {
  const date = new Date();
  date.setDate(date.getDate() + daysFromNow);
  date.setHours(20 + Math.floor(Math.random() * 4) + hoursVariation);
  date.setMinutes(Math.random() > 0.5 ? 0 : 30);
  return date.toISOString().slice(0, 16);
}

// Extrait toutes les sous-catégories les plus profondes d'un arbre
function extractDeepestCategories(tree, result = [], visited = new WeakSet(), depth = 0) {
  // Protection contre récursion infinie
  if (depth > 50) {
    console.warn('⚠️ extractDeepestCategories: profondeur maximale atteinte');
    return result;
  }
  
  if (!tree) return result;
  
  // Protection contre références circulaires
  if (typeof tree === 'object' && tree !== null) {
    if (visited.has(tree)) {
      return result; // Déjà visité, éviter la boucle
    }
    visited.add(tree);
  }
  
  if (Array.isArray(tree)) {
    // C'est une liste de feuilles - les plus profondes !
    tree.forEach(item => {
      const name = typeof item === 'string' ? item : (item && item.name ? item.name : '');
      if (name && !result.includes(name)) {
        result.push(name);
      }
    });
    return result;
  }
  
  // Parcourir récursivement seulement si c'est un objet
  if (typeof tree === 'object' && tree !== null) {
    for (const key in tree) {
      if (tree.hasOwnProperty(key)) {
        extractDeepestCategories(tree[key], result, visited, depth + 1);
      }
    }
  }
  
  return result;
}

// Fonction désactivée - les events viennent du backend uniquement
function generateEmergencyEvents() {
  console.log('Events chargés depuis le backend uniquement - pas de génération de faux events');
}

function ensureDemoPoints() {
  // Events et bookings viennent du backend uniquement - PAS de génération de faux data
  console.log(`ensureDemoPoints() - ${eventsData.length} events, ${bookingsData.length} bookings du backend`);
  calculatePlatinumRanks();
}

// Appeler le calcul des rangs Platinum après la génération des données
function finalizeDataGeneration() {
  // Assigner des rangs Platinum aléatoires aux événements platinum (pour la démo)
  eventsData.forEach(ev => {
    if (ev.boost === "platinum" && !ev.platinumBid) {
      // Enchère aléatoire entre 15 et 50 pour la démo
      ev.platinumBid = 15 + Math.floor(Math.random() * 36);
    }
  });
  
  // Calculer les rangs par région
  calculatePlatinumRanks();
}

// ============================================
// BACKEND BRIDGE
// ============================================
window.updateBackendData = function (mode, data) {
  if (!Array.isArray(data)) data = [];
  if (mode === "event") eventsData = data;
  if (mode === "booking") bookingsData = data;
  if (mode === "service") servicesData = data;

  ensureDemoPoints();
  finalizeDataGeneration();
  filteredData = null;
  refreshMarkers();
  refreshListView();
};

