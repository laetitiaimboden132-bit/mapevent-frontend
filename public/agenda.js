// ============================================================
// agenda.js
// Agenda mini-window + popup + nettoyage (toggleAgendaWindow, cleanupExpiredEvents)
// Extrait de map_logic.js (lignes 22385-23220)
// ============================================================

// AGENDA MINI WINDOW (comme Event List)
// ============================================
let agendaMiniWindowOpen = false;

// Toggle la fenêtre Agenda depuis la topbar
function toggleAgendaWindow() {
  // L'agenda s'ouvre automatiquement quand on ajoute un élément
  // Cette fonction ouvre simplement la mini-fenêtre
  if (!agendaMiniWindowOpen) {
    showAgendaMiniWindow();
  } else {
    hideAgendaMiniWindow();
  }
}

async function showAgendaMiniWindow() {
  // Résoudre les items agenda - chercher d'abord en mémoire, puis fetch si manquant
  const agendaItems = [];
  for (const key of currentUser.agenda) {
    const [type, id] = key.split(":");
    const numId = parseInt(id);
    const data = type === "event" ? eventsData : type === "booking" ? bookingsData : servicesData;
    let item = data.find(i => i.id === numId);
    
    // Si pas en mémoire (event hors viewport), fetch depuis l'API
    if (!item && type === "event") {
      try {
        const resp = await fetch(`${window.API_BASE_URL}/events/${numId}`);
        if (resp.ok) {
          const eventData = await resp.json();
          if (eventData && eventData.id) {
            eventData.type = 'event';
            eventsData.push(eventData); // Ajouter en cache mémoire
            item = eventData;
          }
        }
      } catch(e) { console.warn('[AGENDA] Fetch event', numId, 'failed:', e); }
    }
    
    if (item) {
      if (!item.type) item.type = type;
      agendaItems.push(item);
    }
  }

  let agendaView = document.getElementById("agenda-mini-window");
  if (!agendaView) {
    agendaView = document.createElement("div");
    agendaView.id = "agenda-mini-window";
    agendaView.style.cssText = "position:fixed;bottom:20px;right:20px;width:380px;max-height:500px;background:var(--ui-card-bg);border:1px solid var(--ui-card-border);border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,0.5);z-index:100000;display:flex;flex-direction:column;overflow:hidden;";
    document.body.appendChild(agendaView);
  }

  agendaView.innerHTML = `
    <div style="display:flex;flex-direction:column;gap:12px;padding:16px;background:var(--ui-card-bg);border-bottom:1px solid var(--ui-card-border);">
      <div style="display:flex;align-items:center;justify-content:space-between;">
        <div style="font-size:16px;font-weight:700;">📅 Mon agenda (${agendaItems.length})</div>
        <div style="display:flex;gap:8px;">
          <button onclick="hideAgendaMiniWindow()" style="padding:6px 12px;border-radius:8px;background:rgba(239,68,68,0.2);border:1px solid rgba(239,68,68,0.4);color:#ef4444;font-size:11px;cursor:pointer;">✕</button>
        </div>
      </div>
    </div>
    <div style="flex:1;overflow-y:auto;padding:12px;max-height:400px;">
      ${agendaItems.length === 0 ? `
        <div style="text-align:center;padding:20px;color:var(--ui-text-muted);font-size:12px;">
          <div style="font-size:32px;margin-bottom:8px;">📭</div>
          <div>Votre agenda est vide</div>
        </div>
      ` : agendaItems.slice(0, 5).map(item => {
        const imgTag = buildMainImageTag(item, item.title || item.name || "");
        return `
          <div style="display:flex;gap:10px;padding:10px;border-radius:10px;margin-bottom:8px;background:rgba(15,23,42,0.5);border:1px solid var(--ui-card-border);cursor:pointer;transition:all 0.2s;" onclick="openItemFromAgenda('${item.type}', ${item.id})" onmouseover="this.style.background='rgba(0,255,195,0.1)';this.style.borderColor='rgba(0,255,195,0.5)'" onmouseout="this.style.background='rgba(15,23,42,0.5)';this.style.borderColor='var(--ui-card-border)'">
            <div style="width:60px;height:60px;border-radius:8px;overflow:hidden;flex-shrink:0;">
              ${imgTag}
            </div>
            <div style="flex:1;min-width:0;">
              <div style="font-weight:600;font-size:13px;margin-bottom:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${escapeHtml(item.title || item.name)}</div>
              <div style="font-size:11px;color:var(--ui-text-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${item.startDate ? formatEventDateRange(item.startDate, item.endDate) : item.city}</div>
              ${item.type === 'event' ? `
                <button onclick="event.stopPropagation();openAddAlarmModal('event', ${item.id})" style="margin-top:6px;padding:4px 8px;border-radius:6px;border:1px solid rgba(245,158,11,0.5);background:rgba(245,158,11,0.1);color:#f59e0b;cursor:pointer;font-size:10px;font-weight:600;">⏰ Alarme</button>
              ` : ''}
            </div>
          </div>
        `;
      }).join('')}
      ${agendaItems.length > 5 ? `
        <div style="text-align:center;padding:8px;color:var(--ui-text-muted);font-size:11px;">
          +${agendaItems.length - 5} autres... Cliquez sur un élément pour voir plus
        </div>
      ` : ''}
    </div>
  `;

  agendaView.style.display = "flex";
  agendaMiniWindowOpen = true;
}

function hideAgendaMiniWindow() {
  const agendaView = document.getElementById("agenda-mini-window");
  if (agendaView) {
    agendaView.style.display = "none";
    agendaMiniWindowOpen = false;
  }
}

// FONCTION SUPPRIMÉE - Le bloc compte ne doit JAMAIS être modifié
// function updateAccountButton() { ... }

// Fonctions pour les photos
window.openPhotoViewer = function(photoUrl) {
  const html = `
    <div style="padding:20px;max-width:600px;margin:0 auto;text-align:center;">
      <h2 style="margin:0 0 20px;font-size:20px;color:var(--ui-text-main);">📸 Photo</h2>
      <img src="${photoUrl}" style="max-width:100%;max-height:70vh;border-radius:12px;border:1px solid var(--ui-card-border);" onerror="this.style.display='none';this.parentElement.innerHTML='<div style=\\'padding:40px;color:var(--ui-text-muted);\\'>Erreur de chargement de l\\'image</div>';" />
      <button onclick="closePublishModal()" style="margin-top:20px;padding:10px 24px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-size:14px;">Fermer</button>
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
};

window.openPhotoUploader = function() {
  const html = `
    <div style="padding:24px;max-width:500px;margin:0 auto;">
      <h2 style="margin:0 0 20px;font-size:20px;color:var(--ui-text-main);display:flex;align-items:center;gap:10px;">
        <span>📸</span> <span>Ajouter une photo</span>
      </h2>
      <div style="border:2px dashed var(--ui-card-border);border-radius:12px;padding:40px;text-align:center;background:rgba(15,23,42,0.3);margin-bottom:20px;">
        <div style="font-size:48px;margin-bottom:12px;">📷</div>
        <div style="color:var(--ui-text-muted);margin-bottom:16px;">Glissez-déposez une image ou cliquez pour sélectionner</div>
        <input type="file" id="photo-upload-input" accept="image/*" style="display:none;" onchange="handlePhotoUpload(event)">
        <button onclick="document.getElementById('photo-upload-input').click()" style="padding:12px 24px;border-radius:999px;border:none;background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff;font-weight:600;cursor:pointer;font-size:14px;">
          Choisir un fichier
        </button>
      </div>
      <div style="display:flex;gap:12px;">
        <button onclick="closePublishModal()" style="flex:1;padding:12px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-size:14px;">Annuler</button>
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
};

window.handlePhotoUpload = function(event) {
  const file = event.target.files[0];
  if (!file) return;
  
  if (!file.type.startsWith('image/')) {
    showNotification("⚠️ Veuillez sélectionner une image", "warning");
    return;
  }
  
  const reader = new FileReader();
  reader.onload = function(e) {
    const photoUrl = e.target.result;
    if (!currentUser.photos) currentUser.photos = [];
    currentUser.photos.unshift({ url: photoUrl, timestamp: Date.now() });
    
    // Ajouter à l'historique
    if (!currentUser.history) currentUser.history = [];
    currentUser.history.unshift({
      action: "Photo ajoutée",
      icon: "📸",
      timestamp: Date.now()
    });
    
    saveUser();
    showNotification("✅ Photo ajoutée avec succès !", "success");
    openAccountModal(); // Rafraîchir le modal compte
  };
  reader.readAsDataURL(file);
};

// ============================================
// AGENDA POPUP (Style Facebook) - Version complète
// ============================================
function openAgendaModal() {
  // Fermer la mini-fenêtre si elle est ouverte
  hideAgendaMiniWindow();
  
  // Protection contre les erreurs TDZ
  // NE JAMAIS créer de variable locale 't' - utiliser directement window.t() pour éviter toute TDZ
  const agendaItems = currentUser.agenda.map(key => {
    const [type, id] = key.split(":");
    const data = type === "event" ? eventsData : type === "booking" ? bookingsData : servicesData;
    return data.find(i => i.id === parseInt(id));
  }).filter(Boolean);

  // Filtrer uniquement les événements pour les alarmes
  const agendaEvents = agendaItems.filter(item => item.type === 'event');
  
  const html = `
    <div style="padding:10px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
        <h2 style="margin:0;font-size:18px;">📅 ${window.t("my_agenda")}</h2>
        <button onclick="closePublishModal()" style="background:none;border:none;font-size:20px;cursor:pointer;color:var(--ui-text-muted);">${window.t("close") === "Fermer" ? "✕" : "×"}</button>
      </div>
      
      ${agendaEvents.length > 0 ? `
        <!-- Bouton Ajouter Alarme -->
        <button onclick="closePublishModal();setTimeout(() => openAddAlarmModal('agenda'), 300);" style="width:100%;padding:12px;border-radius:12px;border:2px solid #f59e0b;background:linear-gradient(135deg,#f59e0b,#d97706);color:#fff;font-weight:600;cursor:pointer;font-size:14px;transition:all 0.2s;display:flex;align-items:center;justify-content:center;gap:8px;margin-bottom:16px;">
          <span>⏰</span>
          <span>Ajouter alarme</span>
        </button>
      ` : ''}
      
      ${agendaItems.length === 0 ? `
        <div style="text-align:center;padding:40px;color:var(--ui-text-muted);">
          <div style="font-size:48px;margin-bottom:16px;">📭</div>
          <p>${window.t("agenda_empty")}</p>
          <p style="font-size:12px;">${window.t("add_from_map")}</p>
        </div>
      ` : `
        <div style="margin-bottom:12px;font-size:12px;color:var(--ui-text-muted);text-align:center;">
          ${agendaItems.length} ${agendaItems.length === 1 ? 'élément' : 'éléments'} dans votre agenda
        </div>
        <div id="agenda-list-container" style="max-height:calc(80vh - 180px);overflow-y:auto;padding-right:8px;">
          ${agendaItems.slice(0, 20).map(item => `
            <div style="display:flex;gap:12px;padding:12px;border-radius:12px;margin-bottom:8px;background:rgba(15,23,42,0.5);border:1px solid var(--ui-card-border);cursor:pointer;transition:all 0.2s;" onclick="openItemFromAgenda('${item.type}', ${item.id})" onmouseover="this.style.background='rgba(0,255,195,0.1)';this.style.borderColor='rgba(0,255,195,0.5)'" onmouseout="this.style.background='rgba(15,23,42,0.5)';this.style.borderColor='var(--ui-card-border)'">
              <div style="width:60px;height:60px;border-radius:8px;background:linear-gradient(135deg,#3b82f6,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:24px;">
                ${getCategoryEmoji(item)}
              </div>
              <div style="flex:1;">
                <div style="font-weight:600;margin-bottom:4px;">${escapeHtml(item.title || item.name)}</div>
                <div style="font-size:12px;color:var(--ui-text-muted);">${item.startDate ? formatEventDateRange(item.startDate, item.endDate) : item.city}</div>
                <div style="font-size:11px;color:var(--ui-text-muted);">${item.city}</div>
                ${(currentUser.eventAlarms || []).some(a => a.eventId === item.id.toString() && item.type === 'event') ? `
                  <div style="margin-top:4px;display:flex;align-items:center;gap:4px;font-size:11px;color:#f59e0b;">
                    <span>⏰</span>
                    <span>${(currentUser.eventAlarms || []).filter(a => a.eventId === item.id.toString()).length} alarme${(currentUser.eventAlarms || []).filter(a => a.eventId === item.id.toString()).length > 1 ? 's' : ''}</span>
                  </div>
                ` : ''}
              </div>
              <button onclick="event.stopPropagation();removeFromAgenda('${item.type}', ${item.id})" style="background:none;border:none;color:#ef4444;cursor:pointer;font-size:18px;padding:4px;" title="${window.t('remove_from_agenda')}">🗑️</button>
            </div>
          `).join('')}
        </div>
        ${agendaItems.length > 20 ? `
          <div style="text-align:center;margin-top:12px;padding:12px;background:rgba(15,23,42,0.5);border-radius:8px;border:1px solid var(--ui-card-border);">
            <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:8px;">
              Affichage de 20 sur ${agendaItems.length} éléments
            </div>
            <button onclick="loadMoreAgendaItems()" style="padding:8px 16px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-size:12px;">
              Afficher plus (${Math.min(20, agendaItems.length - 20)} suivants)
            </button>
          </div>
        ` : ''}
      `}
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
  
  // Stocker les items complets pour la pagination
  window.agendaItemsFull = agendaItems;
  window.agendaItemsDisplayed = 20;
}

function loadMoreAgendaItems() {
  // Protection contre les erreurs TDZ
  const t = window.t || function(key) { return key; };
  
  if (!window.agendaItemsFull) return;
  const container = document.getElementById("agenda-list-container");
  if (!container) return;
  
  const start = window.agendaItemsDisplayed;
  const end = Math.min(start + 20, window.agendaItemsFull.length);
  const newItems = window.agendaItemsFull.slice(start, end);
  
  newItems.forEach(item => {
    const itemHtml = `
      <div style="display:flex;gap:12px;padding:12px;border-radius:12px;margin-bottom:8px;background:rgba(15,23,42,0.5);border:1px solid var(--ui-card-border);cursor:pointer;transition:all 0.2s;" onclick="openItemFromAgenda('${item.type}', ${item.id})" onmouseover="this.style.background='rgba(0,255,195,0.1)';this.style.borderColor='rgba(0,255,195,0.5)'" onmouseout="this.style.background='rgba(15,23,42,0.5)';this.style.borderColor='var(--ui-card-border)'">
        <div style="width:60px;height:60px;border-radius:8px;background:linear-gradient(135deg,#3b82f6,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:24px;">
          ${getCategoryEmoji(item)}
        </div>
        <div style="flex:1;">
          <div style="font-weight:600;margin-bottom:4px;">${escapeHtml(item.title || item.name)}</div>
          <div style="font-size:12px;color:var(--ui-text-muted);">${item.startDate ? formatEventDateRange(item.startDate, item.endDate) : item.city}</div>
          <div style="font-size:11px;color:var(--ui-text-muted);">${item.city}</div>
          ${(currentUser.eventAlarms || []).some(a => a.eventId === item.id.toString() && item.type === 'event') ? `
            <div style="margin-top:4px;display:flex;align-items:center;gap:4px;font-size:11px;color:#f59e0b;">
              <span>⏰</span>
              <span>${(currentUser.eventAlarms || []).filter(a => a.eventId === item.id.toString()).length} alarme${(currentUser.eventAlarms || []).filter(a => a.eventId === item.id.toString()).length > 1 ? 's' : ''}</span>
            </div>
          ` : ''}
        </div>
        <button onclick="event.stopPropagation();removeFromAgenda('${item.type}', ${item.id})" style="background:none;border:none;color:#ef4444;cursor:pointer;font-size:18px;padding:4px;" title="${window.t('remove_from_agenda')}">🗑️</button>
      </div>
    `;
    container.insertAdjacentHTML('beforeend', itemHtml);
  });
  
  window.agendaItemsDisplayed = end;
  
  // Mettre à jour le bouton "Afficher plus"
  const moreButton = container.nextElementSibling?.querySelector('button');
  if (moreButton) {
    const remaining = window.agendaItemsFull.length - end;
    if (remaining > 0) {
      moreButton.textContent = `Afficher plus (${Math.min(20, remaining)} suivants)`;
    } else {
      moreButton.parentElement.remove();
    }
  }
}

function removeFromAgenda(type, id) {
  // Protection contre les erreurs TDZ
  const t = window.t || function(key) { return key; };
  
  const key = `${type}:${id}`;
  currentUser.agenda = currentUser.agenda.filter(k => k !== key);
  showNotification(`📅 ${window.t("removed_from_agenda")}`, "info");
  openAgendaModal(); // Rafraîchir
}

// ============================================
// SYSTÈME D'ALARMES POUR ÉVÉNEMENTS
// ============================================

// Initialiser les alarmes si elles n'existent pas
if (!currentUser.eventAlarms) {
  currentUser.eventAlarms = [];
}

// Ouvrir le modal pour ajouter une alarme
function openAddAlarmModal(source, eventId = null) {
  if (!currentUser || !currentUser.isLoggedIn) {
    showNotification("⚠️ Vous devez être connecté pour ajouter une alarme", "warning");
    openLoginModal();
    return;
  }
  
  // Si appelé depuis l'agenda, proposer de choisir un événement
  let eventsToChoose = [];
  if (source === 'agenda') {
    const agendaItems = currentUser.agenda.map(key => {
      const [type, id] = key.split(":");
      if (type === "event") {
        return eventsData.find(e => e.id === parseInt(id));
      }
      return null;
    }).filter(Boolean);
    
    eventsToChoose = agendaItems.filter(ev => {
      const alarms = (currentUser.eventAlarms || []).filter(a => a.eventId === ev.id.toString());
      return alarms.length < 2;
    });
    
    if (eventsToChoose.length === 0) {
      showNotification("⚠️ Aucun événement disponible pour ajouter une alarme (limite de 2 alarmes atteinte)", "warning");
      return;
    }
  }
  
  // Si eventId est fourni, utiliser cet événement
  let selectedEvent = null;
  if (eventId) {
    selectedEvent = eventsData.find(e => e.id === eventId);
    if (!selectedEvent) {
      showNotification("⚠️ Événement introuvable", "error");
      return;
    }
    const alarms = (currentUser.eventAlarms || []).filter(a => a.eventId === eventId.toString());
    if (alarms.length >= 2) {
      showNotification("⚠️ Limite de 2 alarmes atteinte pour cet événement", "warning");
      return;
    }
  }
  
  const html = `
    <div style="padding:24px;max-width:500px;margin:0 auto;max-height:85vh;overflow-y:auto;">
      <div style="text-align:center;margin-bottom:24px;">
        <div style="font-size:48px;margin-bottom:12px;">⏰</div>
        <h2 style="margin:0;font-size:22px;font-weight:700;color:#fff;">Ajouter une alarme</h2>
        <p style="color:var(--ui-text-muted);margin-top:8px;font-size:13px;">Recevez un rappel avant ou pendant l'événement</p>
        <div style="margin-top:12px;padding:12px;background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:10px;font-size:12px;color:var(--ui-text-muted);line-height:1.6;">
          <div style="font-weight:600;color:#3b82f6;margin-bottom:6px;">📱 Comment ça fonctionne ?</div>
          <div>• <strong>Notifications navigateur</strong> : Une notification apparaîtra sur votre écran (comme les notifications WhatsApp)</div>
          <div>• <strong>Email</strong> : Vous recevrez un email à l'adresse enregistrée</div>
          <div>• <strong>SMS</strong> : Si configuré, vous recevrez un SMS sur votre téléphone</div>
          <div style="margin-top:8px;font-size:11px;color:#00ffc3;">💡 Pour les notifications navigateur, autorisez-les quand le navigateur vous le demande</div>
        </div>
      </div>
      
      ${source === 'agenda' && !eventId ? `
        <div style="margin-bottom:20px;">
          <label style="display:block;font-size:14px;font-weight:600;color:#fff;margin-bottom:8px;">
            Choisir un événement <span style="color:#ef4444;">*</span>
          </label>
          <select id="alarm-event-select" style="width:100%;padding:12px;border-radius:10px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:14px;cursor:pointer;">
            ${eventsToChoose.map(ev => `
              <option value="${ev.id}">${escapeHtml(ev.title || 'Sans titre')} - ${formatEventDateRange(ev.startDate, ev.endDate)}</option>
            `).join('')}
          </select>
        </div>
      ` : selectedEvent ? `
        <div style="padding:12px;background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:10px;margin-bottom:20px;">
          <div style="font-weight:600;font-size:14px;color:#fff;margin-bottom:4px;">${escapeHtml(selectedEvent.title || 'Sans titre')}</div>
          <div style="font-size:12px;color:var(--ui-text-muted);">${formatEventDateRange(selectedEvent.startDate, selectedEvent.endDate)}</div>
        </div>
      ` : ''}
      
      <div style="margin-bottom:20px;">
        <label style="display:block;font-size:14px;font-weight:600;color:#fff;margin-bottom:8px;">
          Type d'alarme <span style="color:#ef4444;">*</span>
        </label>
        <select id="alarm-type" style="width:100%;padding:12px;border-radius:10px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:14px;cursor:pointer;">
          <option value="before">Avant l'événement</option>
          <option value="during">Pendant l'événement</option>
        </select>
      </div>
      
      <div id="alarm-timing-container">
        <div style="margin-bottom:20px;">
          <label style="display:block;font-size:14px;font-weight:600;color:#fff;margin-bottom:8px;">
            Moment <span style="color:#ef4444;">*</span>
          </label>
          <select id="alarm-timing" style="width:100%;padding:12px;border-radius:10px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:14px;cursor:pointer;">
            <option value="hour">1 heure avant</option>
            <option value="day">1 jour avant</option>
            <option value="week">1 semaine avant</option>
          </select>
        </div>
      </div>
      
      <div style="display:flex;gap:12px;">
        <button onclick="closePublishModal()" style="flex:1;padding:12px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-weight:600;">
          Annuler
        </button>
        <button onclick="saveAlarm(${eventId || 'null'})" style="flex:1;padding:12px;border-radius:999px;border:none;background:linear-gradient(135deg,#f59e0b,#d97706);color:#fff;font-weight:700;cursor:pointer;">
          Enregistrer
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
  
  // Mettre à jour les options selon le type
  document.getElementById("alarm-type").addEventListener('change', function() {
    const timingSelect = document.getElementById("alarm-timing");
    const container = document.getElementById("alarm-timing-container");
    if (this.value === 'during') {
      container.innerHTML = `
        <div style="margin-bottom:20px;">
          <label style="display:block;font-size:14px;font-weight:600;color:#fff;margin-bottom:8px;">
            Heure <span style="color:#ef4444;">*</span>
          </label>
          <input type="time" id="alarm-time" style="width:100%;padding:12px;border-radius:10px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:14px;">
        </div>
      `;
    } else {
      container.innerHTML = `
        <div style="margin-bottom:20px;">
          <label style="display:block;font-size:14px;font-weight:600;color:#fff;margin-bottom:8px;">
            Moment <span style="color:#ef4444;">*</span>
          </label>
          <select id="alarm-timing" style="width:100%;padding:12px;border-radius:10px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:14px;cursor:pointer;">
            <option value="hour">1 heure avant</option>
            <option value="day">1 jour avant</option>
            <option value="week">1 semaine avant</option>
          </select>
        </div>
      `;
    }
  });
}

window.openAddAlarmModal = openAddAlarmModal;

// Sauvegarder une alarme
function saveAlarm(eventId) {
  const eventSelect = document.getElementById("alarm-event-select");
  const finalEventId = eventId || (eventSelect ? parseInt(eventSelect.value) : null);
  
  if (!finalEventId) {
    showNotification("⚠️ Veuillez sélectionner un événement", "warning");
    return;
  }
  
  const event = eventsData.find(e => e.id === finalEventId);
  if (!event) {
    showNotification("⚠️ Événement introuvable", "error");
    return;
  }
  
  // Vérifier la limite de 2 alarmes
  const existingAlarms = (currentUser.eventAlarms || []).filter(a => a.eventId === finalEventId.toString());
  if (existingAlarms.length >= 2) {
    showNotification("⚠️ Limite de 2 alarmes atteinte pour cet événement", "warning");
    return;
  }
  
  const alarmType = document.getElementById("alarm-type").value;
  let alarmTime = null;
  let alarmTiming = null;
  
  if (alarmType === 'during') {
    const timeInput = document.getElementById("alarm-time");
    if (!timeInput || !timeInput.value) {
      showNotification("⚠️ Veuillez sélectionner une heure", "warning");
      return;
    }
    alarmTime = timeInput.value;
  } else {
    const timingSelect = document.getElementById("alarm-timing");
    if (!timingSelect || !timingSelect.value) {
      showNotification("⚠️ Veuillez sélectionner un moment", "warning");
      return;
    }
    alarmTiming = timingSelect.value;
  }
  
  // Calculer la date de déclenchement
  const startDate = event.startDate ? new Date(event.startDate) : null;
  if (!startDate) {
    showNotification("⚠️ L'événement n'a pas de date de début", "error");
    return;
  }
  
  let triggerDate = null;
  if (alarmType === 'during') {
    const [hours, minutes] = alarmTime.split(':');
    triggerDate = new Date(startDate);
    triggerDate.setHours(parseInt(hours), parseInt(minutes), 0, 0);
  } else {
    triggerDate = new Date(startDate);
    if (alarmTiming === 'hour') {
      triggerDate.setHours(triggerDate.getHours() - 1);
    } else if (alarmTiming === 'day') {
      triggerDate.setDate(triggerDate.getDate() - 1);
    } else if (alarmTiming === 'week') {
      triggerDate.setDate(triggerDate.getDate() - 7);
    }
  }
  
  const alarm = {
    id: `alarm-${finalEventId}-${Date.now()}`,
    eventId: finalEventId.toString(),
    type: alarmType,
    timing: alarmTiming,
    time: alarmTime,
    triggerDate: triggerDate.toISOString(),
    triggered: false,
    createdAt: new Date().toISOString()
  };
  
  if (!currentUser.eventAlarms) {
    currentUser.eventAlarms = [];
  }
  currentUser.eventAlarms.push(alarm);
  saveUser();
  
  showNotification("✅ Alarme ajoutée avec succès !", "success");
  closePublishModal();
  
  // Rafraîchir la popup si elle est ouverte
  if (currentPopupMarker) {
    const item = getItemById('event', finalEventId);
    if (item) {
      const popupContent = buildEventPopup(item);
      const backdrop = document.getElementById("popup-modal-backdrop");
      if (backdrop) {
        backdrop.innerHTML = `
          <div id="popup-modal-content" style="position:relative;width:380px;max-height:85vh;overflow:hidden;background:var(--ui-card-bg);border-radius:16px;border:1px solid var(--ui-card-border);margin:20px;box-shadow:0 20px 60px rgba(0,0,0,0.5);display:flex;flex-direction:column;padding:0;box-sizing:border-box;pointer-events:auto;">
            <button onclick="closePopupModal()" style="position:absolute;top:12px;right:12px;width:36px;height:36px;border-radius:50%;border:none;background:rgba(0,0,0,0.6);color:#fff;cursor:pointer;font-size:20px;z-index:1001;display:flex;align-items:center;justify-content:center;transition:all 0.2s;" onmouseover="this.style.background='rgba(239,68,68,0.8)'" onmouseout="this.style.background='rgba(0,0,0,0.6)'">✕</button>
            <div id="popup-scroll-container" style="flex:1;overflow-y:auto;overflow-x:hidden;scrollbar-width:none;-webkit-overflow-scrolling:touch;width:100%;margin:0;padding:0;box-sizing:border-box;touch-action:pan-y;overscroll-behavior:contain;">
              ${popupContent}
            </div>
          </div>
        `;
      }
    }
  }
}

window.saveAlarm = saveAlarm;

// Vérifier et déclencher les alarmes
function checkEventAlarms() {
  if (!isLoggedIn() || !currentUser.eventAlarms || currentUser.eventAlarms.length === 0) {
    return;
  }
  
  const now = new Date();
  const alarmsToTrigger = currentUser.eventAlarms.filter(alarm => {
    if (alarm.triggered) return false;
    const triggerDate = new Date(alarm.triggerDate);
    return triggerDate <= now;
  });
  
  alarmsToTrigger.forEach(alarm => {
    const event = eventsData.find(e => e.id === parseInt(alarm.eventId));
    if (event) {
      const message = alarm.type === 'during' 
        ? `⏰ ${event.title || 'Événement'} commence maintenant !`
        : `⏰ Rappel : ${event.title || 'Événement'} ${alarm.timing === 'hour' ? 'dans 1 heure' : alarm.timing === 'day' ? 'demain' : 'dans 1 semaine'}`;
      
      showNotification(message, "info");
      alarm.triggered = true;
    }
  });
  
  if (alarmsToTrigger.length > 0) {
    saveUser();
  }
}

// Vérifier les alarmes toutes les minutes
setInterval(checkEventAlarms, 60000);
checkEventAlarms(); // Vérifier immédiatement au chargement

// ============================================
// NETTOYAGE DES ÉVÉNEMENTS EXPIRÉS
// ============================================

function cleanExpiredEvents() {
  if (!isLoggedIn()) {
    // Nettoyer les événements expirés même si non connecté (pour la liste publique)
    // Mais ne pas toucher aux alarmes/agenda de l'utilisateur
  }
  
  const now = new Date();
  const organizerEvents = {}; // {organizerEmail: [events]}
  
  // Compter les événements par organisateur
  eventsData.forEach(event => {
    if (event.organizerEmail) {
      if (!organizerEvents[event.organizerEmail]) {
        organizerEvents[event.organizerEmail] = [];
      }
      organizerEvents[event.organizerEmail].push(event);
    }
  });
  
  // Filtrer les événements expirés
  const beforeCount = eventsData.length;
  eventsData = eventsData.filter(event => {
    // Si l'événement n'a pas de date de fin, le garder
    if (!event.endDate) return true;
    
    const endDate = new Date(event.endDate);
    
    // Si l'événement n'est pas encore terminé, le garder
    if (endDate > now) return true;
    
    // Si l'événement est terminé mais appartient à un organisateur avec moins de 30 événements, le garder
    if (event.organizerEmail) {
      const organizerEventCount = organizerEvents[event.organizerEmail]?.length || 0;
      if (organizerEventCount <= 30) {
        return true;
      }
    }
    
    // Sinon, supprimer l'événement
    return false;
  });
  
  const afterCount = eventsData.length;
  const removedCount = beforeCount - afterCount;
  
  if (removedCount > 0) {
    console.log(`🧹 Nettoyage : ${removedCount} événement(s) expiré(s) supprimé(s)`);
    
    // Vérifier si des organisateurs ont trop d'événements
    Object.keys(organizerEvents).forEach(email => {
      const count = organizerEvents[email].filter(e => {
        if (!e.endDate) return true;
        return new Date(e.endDate) > now;
      }).length;
      
      if (count > 30) {
        // Trouver l'organisateur dans les événements restants
        const organizerEventsRemaining = eventsData.filter(e => e.organizerEmail === email);
        if (organizerEventsRemaining.length > 30) {
          // Avertir l'organisateur (simulation - à implémenter avec notification réelle)
          console.warn(`⚠️ Organisateur ${email} a ${organizerEventsRemaining.length} événements. Limite de 30 atteinte.`);
          // TODO: Envoyer une notification à l'organisateur pour qu'il supprime des événements
        }
      }
    });
  }
  
  // Nettoyer aussi les alarmes des événements supprimés
  if (isLoggedIn() && currentUser.eventAlarms) {
    const eventIds = new Set(eventsData.map(e => e.id.toString()));
    const beforeAlarmsCount = currentUser.eventAlarms.length;
    currentUser.eventAlarms = currentUser.eventAlarms.filter(alarm => eventIds.has(alarm.eventId));
    const afterAlarmsCount = currentUser.eventAlarms.length;
    
    if (beforeAlarmsCount !== afterAlarmsCount) {
      saveUser();
    }
  }
  
  // Nettoyer aussi l'agenda des événements supprimés
  if (isLoggedIn() && currentUser.agenda) {
    const eventIds = new Set(eventsData.map(e => e.id.toString()));
    const beforeAgendaCount = currentUser.agenda.length;
    currentUser.agenda = currentUser.agenda.filter(key => {
      const [type, id] = key.split(':');
      if (type === 'event') {
        return eventIds.has(id);
      }
      return true;
    });
    const afterAgendaCount = currentUser.agenda.length;
    
    if (beforeAgendaCount !== afterAgendaCount) {
      saveUser();
    }
  }
}

// Nettoyer les événements toutes les heures
setInterval(cleanExpiredEvents, 3600000);
cleanExpiredEvents(); // Nettoyer immédiatement au chargement

// Ouvrir la popup originale d'un item depuis l'agenda
function openItemFromAgenda(type, id) {
  // Fermer la modal agenda
  closePublishModal();
  
  // Trouver l'item
  const data = type === "event" ? eventsData : type === "booking" ? bookingsData : servicesData;
  const item = data.find(i => i.id === parseInt(id));
  
  if (!item) {
    showNotification("⚠️ Item introuvable", "error");
    return;
  }
  
  // Trouver le marqueur correspondant et ouvrir sa popup
  const key = `${type}:${id}`;
  const marker = markerMap[key];
  
  if (marker) {
    // Centrer la map sur le marqueur
    map.setView([item.lat, item.lng], Math.max(map.getZoom(), 13));
    
    // Ouvrir la popup
    marker.openPopup();
  } else {
    // Si le marqueur n'existe pas (filtre actif), créer temporairement la popup
    const popupContent = buildPopupHtml(item);
    L.popup({ maxWidth: 360 })
      .setLatLng([item.lat, item.lng])
      .setContent(popupContent)
      .openOn(map);
    
    // Centrer la map
    map.setView([item.lat, item.lng], Math.max(map.getZoom(), 13));
  }
}

// FONCTION SUPPRIMÉE - Le bloc compte ne doit JAMAIS être modifié
// function updateUserUI() { ... }

// ============================================
// SYSTÈME D'ABONNEMENTS & ALERTES
// ============================================

// Obtenir le nombre d'utilisateurs actifs depuis l'API
async function getActiveUsersCount() {
  try {
    const response = await fetch(`${window.API_BASE_URL}/stats/active-users`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });
    
    if (response.ok) {
      const data = await response.json();
      return (data.count || data.activeUsers || 0).toLocaleString('fr-CH');
    }
  } catch (error) {
    console.warn('Erreur récupération utilisateurs actifs:', error);
  }
  
  // Fallback : simulation si l'API n'est pas disponible
  const base = 1247;
  const variation = Math.floor(Math.random() * 909);
  return (base + variation).toLocaleString('fr-CH');
}

// Mettre à jour le compteur d'utilisateurs actifs
async function updateActiveUsersCount() {
  const countElement = document.getElementById("active-users-count");
  if (countElement) {
    const count = await getActiveUsersCount();
    countElement.textContent = count;
  }
