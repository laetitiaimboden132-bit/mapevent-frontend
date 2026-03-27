// ============================================================
// popups.js
// Popups Event/Booking/Service (buildEventPopup, buildBookingPopup, buildServicePopup)
// Extrait de map_logic.js (lignes 6523-7499)
// ============================================================

// POPUPS (Event / Booking / Service)
// ============================================

// Fonction pour masquer le numéro d'adresse (booking/service)
function maskAddressNumber(address) {
  if (!address) return "";
  
  // Enlever le numéro au début mais garder la rue complète
  // Ex: "12 Rue du Centre, Lausanne" → "Rue du Centre, Lausanne"
  // Ex: "45 Avenue de la Gare, Genève" → "Avenue de la Gare, Genève"
  // Patterns: "12 ", "12,", "12-", "No 12", "N°12", etc.
  let masked = address
    .replace(/^\d+[\s,-]+/, '') // Enlève numéro au début suivi d'un espace/virgule/tiret
    .replace(/^[Nn]°?\s*\d+[\s,-]+/, '') // Enlève "N°12 " ou "No 12 " suivi d'un espace
    .replace(/^[Nn]uméro\s+\d+[\s,-]+/i, '') // Enlève "Numéro 12 " suivi d'un espace
    .trim();
  
  // Si le résultat est vide ou ne contient que la ville, essayer de garder au moins la rue
  if (!masked || masked.split(',').length <= 1) {
    // Si l'adresse contient une virgule, essayer de garder la partie avant la virgule (la rue)
    const parts = address.split(',');
    if (parts.length > 1) {
      const streetPart = parts[0].replace(/^\d+[\s,-]+/, '').trim();
      if (streetPart) {
        masked = streetPart + ',' + parts.slice(1).join(',');
      } else {
        masked = address; // Si on ne peut pas extraire la rue, retourner l'adresse originale
      }
    } else {
      masked = address; // Pas de virgule, retourner l'adresse originale
    }
  }
  
  return masked;
}

function isPlaceholderEventDescription(text) {
  if (!text || typeof text !== 'string') return false;
  const d = text.trim().toLowerCase();
  if (!d) return false;
  return (
    d.includes('historique 80k') ||
    d.includes('importe depuis l historique 80k') ||
    d.includes('informations disponibles via la publication originale') ||
    d.includes('details et horaires disponibles via la publication originale') ||
    d.includes('détails et horaires disponibles via la publication originale') ||
    d === 'description non disponible' ||
    d === 'description indisponible'
  );
}

function cleanEventDescriptionText(text) {
  if (!text || typeof text !== 'string') return '';
  return text
    .replace(/https?:\/\/\S+/gi, ' ')
    .replace(/\s+/g, ' ')
    .replace(/[|]{2,}/g, ' ')
    .replace(/[.]{4,}/g, '...')
    .replace(/\(\s*lieu\s*:\s*[^)]+\)/gi, '')
    .trim();
}

function buildEventFallbackSummary(ev) {
  const title = (ev && (ev.title || ev.name)) ? String(ev.title || ev.name).trim() : 'Événement';
  const cat = (ev && (ev.mainCategory || (Array.isArray(ev.categories) ? ev.categories[0] : '')))
    ? String(ev.mainCategory || ev.categories[0]).trim()
    : '';
  if (cat) {
    return `${title} - ${cat}. Résumé disponible via la publication originale.`;
  }
  return `${title} - Résumé disponible via la publication originale.`;
}

function getEventDescriptionForPopup(ev, evTranslated) {
  const translatedRaw = evTranslated && typeof evTranslated.description === 'string' ? evTranslated.description : '';
  const sourceRaw = ev && typeof ev.description === 'string' ? ev.description : '';
  const translated = cleanEventDescriptionText(translatedRaw);
  const raw = cleanEventDescriptionText(sourceRaw);

  if (translated && translated.length >= 24 && !isPlaceholderEventDescription(translated)) return translated;
  if (raw && raw.length >= 24 && !isPlaceholderEventDescription(raw)) return raw;
  return buildEventFallbackSummary(ev);
}

function buildPopupHtml(item) {
  // Protection contre les erreurs TDZ - s'assurer que window.t() est disponible
  // NE PAS logger d'avertissement ici car cela génère des milliers de messages
  if (typeof window.t !== 'function') {
    window.t = function(key) { return key; };
  }
  
  // Protection contre les erreurs - s'assurer que window.translations est disponible
  // NE PAS logger d'avertissement ici car cela génère des milliers de messages
  if (!window.translations || typeof window.translations !== 'object') {
    window.translations = window.translations || { fr: {}, en: {}, es: {}, zh: {}, hi: {} };
  }
  
  try {
    if (item.type === "event") return buildEventPopup(item);
    if (item.type === "booking") return buildBookingPopup(item);
    if (item.type === "service") return buildServicePopup(item);
    return "<div>Type inconnu</div>";
  } catch (err) {
    // Ne pas logger l'erreur complète pour éviter les milliers de messages
    // Retourner un popup minimal au lieu de générer une erreur
    return `<div style="padding:10px;"><strong>${item.title || 'Événement'}</strong><br>Erreur d'affichage</div>`;
  }
}

function buildStatusOverlay(status) {
  // ⚠️ Ne pas afficher de badge pour le statut "active" (c'est le statut par défaut)
  // Seulement afficher les statuts importants : annulé, reporté, complet
  if (!status || status === "OK" || status === "active" || status === "upcoming") {
    return "";
  }

  let label = status;
  let bg = "rgba(239,68,68,0.9)";
  let textColor = "#111827";

  if (status === "COMPLET" || status === "SOLDOUT" || status === "completed") {
    label = "COMPLET";
    bg = "rgba(234,179,8,0.9)";
  } else if (status === "ANNULE" || status === "ANNULÉ" || status === "cancelled") {
    label = "ANNULÉ";
    bg = "rgba(239,68,68,0.9)";
  } else if (status === "REPORTE" || status === "REPORTÉ" || status === "postponed") {
    label = "REPORTÉ";
    bg = "rgba(59,130,246,0.9)";
  }

  return `
    <div style="
      position:absolute;
      top:10px;
      left:10px;
      background:${bg};
      padding:4px 10px;
      border-radius:999px;
      font-size:11px;
      font-weight:700;
      text-transform:uppercase;
      color:${textColor};
    ">
      ${label}
    </div>
  `;
}

// POPUP EVENT - Design Premium 2025
function buildEventPopup(ev) {
  // Protection CRITIQUE contre les erreurs TDZ - DOIT être la première chose dans la fonction
  // S'assurer que window.translations existe AVANT toute utilisation
  if (typeof window === 'undefined') {
    return '<div>Erreur: window non disponible</div>';
  }
  
  // Initialiser window.translations de manière sûre
  if (!window.translations || typeof window.translations !== 'object') {
    window.translations = { fr: {}, en: {}, es: {}, zh: {}, hi: {} };
  }
  
  // S'assurer que toutes les langues existent
  ['fr', 'en', 'es', 'zh', 'hi'].forEach(lang => {
    if (!window.translations[lang] || typeof window.translations[lang] !== 'object') {
      window.translations[lang] = window.translations[lang] || {};
    }
  });
  
  // ⚠️⚠️⚠️ CRITIQUE : S'assurer que currentLanguage est défini
  if (typeof currentLanguage === 'undefined' || !currentLanguage) {
    currentLanguage = 'fr';
  }
  
  // ⚠️⚠️⚠️ CRITIQUE : S'assurer que currentUser est défini et a les propriétés nécessaires
  if (typeof currentUser === 'undefined' || !currentUser) {
    currentUser = {
      isLoggedIn: false,
      favorites: [],
      agenda: [],
      participating: [],
      subscription: 'free'
    };
  }
  
  // S'assurer que les propriétés nécessaires existent
  if (!Array.isArray(currentUser.favorites)) {
    currentUser.favorites = [];
  }
  if (!Array.isArray(currentUser.agenda)) {
    currentUser.agenda = [];
  }
  if (!Array.isArray(currentUser.participating)) {
    currentUser.participating = [];
  }
  if (!Array.isArray(currentUser.likes)) {
    currentUser.likes = [];
  }
  if (!currentUser.subscription) {
    currentUser.subscription = 'free';
  }
  // ⚠️⚠️⚠️ CRITIQUE : S'assurer que reviews est un objet (pas undefined)
  if (!currentUser.reviews || typeof currentUser.reviews !== 'object') {
    currentUser.reviews = {};
  }
  // ⚠️⚠️⚠️ CRITIQUE : S'assurer que reviews est un objet (pas undefined)
  if (!currentUser.reviews || typeof currentUser.reviews !== 'object') {
    currentUser.reviews = {};
  }
  
  // NE PAS redéfinir window.t ici pour éviter les erreurs TDZ
  // Utiliser directement du texte en dur au lieu d'appeler window.t()
  
  // TRADUCTION AUTOMATIQUE du contenu de l'événement
  const evTranslated = getTranslatedItemSync(ev, currentLanguage);
  
  const statusOverlay = buildStatusOverlay(ev.status);
  const borderColor = getBoostColor(ev.boost);
  const cats = (evTranslated.categories || ev.categories || []).join(" • ");
  const popupAddress = ev.address || ev.location || ev.city || "";
  const popupDescription = getEventDescriptionForPopup(ev, evTranslated);
  
  // ⚠️ CRITIQUE : Utiliser l'image de statut si le statut n'est pas "active"
  // Les images de statut remplacent complètement l'image de l'événement
  const statusImages = {
    'cancelled': '/assets/event_overlays/Event canceled.jpeg',
    'postponed': '/assets/event_overlays/postponed.jpeg',
    'completed': '/assets/event_overlays/completed.jpeg',
    'ANNULE': '/assets/event_overlays/Event canceled.jpeg',
    'ANNULÉ': '/assets/event_overlays/Event canceled.jpeg',
    'REPORTE': '/assets/event_overlays/postponed.jpeg',
    'REPORTÉ': '/assets/event_overlays/postponed.jpeg',
    'COMPLET': '/assets/event_overlays/completed.jpeg',
    'SOLDOUT': '/assets/event_overlays/completed.jpeg'
  };
  
  let imgTag;
  const statusImage = statusImages[ev.status];
  if (statusImage) {
    // Si statut spécial : utiliser l'image de statut en plein écran
    imgTag = `
      <img 
        src="${statusImage}"
        alt="${escapeHtml(evTranslated.title || ev.title || '')}"
        style="width:100%;min-height:280px;max-height:400px;object-fit:cover;display:block;margin:0;padding:0;border:none;box-sizing:border-box;background:linear-gradient(135deg,#3b82f6,#8b5cf6);vertical-align:top;"
        onerror="this.src='/assets/event_overlays/eventdefault.jpg';"
        loading="eager"
      >
    `;
    console.log('[POPUP] Image de statut utilisée:', ev.status, statusImage);
  } else {
    // Statut normal (active) : utiliser l'image de l'événement
    imgTag = buildMainImageTag(ev, evTranslated.title || ev.title || "");
  }
  
  const emoji = getCategoryEmoji(ev);
  
  // Calcul du temps restant
  const now = new Date();
  // ⚠️ Support des deux formats : startDate/endDate (frontend) ou date+time/end_date+end_time (backend)
  let startDate = null;
  let endDate = null;
  
  if (ev.startDate) {
    startDate = new Date(ev.startDate);
  } else if (ev.date) {
    // Format backend : date (2026-02-05) + time (14:00:00)
    const dateStr = ev.date + (ev.time ? 'T' + ev.time : 'T00:00:00');
    startDate = new Date(dateStr);
  }
  
  if (ev.endDate) {
    endDate = new Date(ev.endDate);
  } else if (ev.end_date) {
    // Format backend : end_date + end_time
    const endDateStr = ev.end_date + (ev.end_time ? 'T' + ev.end_time : 'T23:59:59');
    endDate = new Date(endDateStr);
  }
  
  const daysUntil = (startDate && !isNaN(startDate.getTime())) ? Math.ceil((startDate - now) / (1000 * 60 * 60 * 24)) : null;
  const timeLabel = daysUntil !== null ? (
    daysUntil < 0 ? "Terminé" :
    daysUntil === 0 ? "Aujourd'hui !" :
    daysUntil === 1 ? "Demain" :
    daysUntil <= 7 ? `Dans ${daysUntil} jours` :
    daysUntil <= 30 ? `Dans ${Math.ceil(daysUntil/7)} sem.` :
    `Dans ${Math.ceil(daysUntil/30)} mois`
  ) : "";
  const timeLabelColor = daysUntil !== null ? (
    daysUntil < 0 ? "#6b7280" :
    daysUntil === 0 ? "#ef4444" :
    daysUntil <= 3 ? "#f59e0b" :
    "#22c55e"
  ) : "#22c55e";
  
  // Badge boost avec animation et système Top 10 Platinum
  const platinumRank = ev.platinumRank || 10;
  let boostBadge = "";
  
  if (ev.boost && ev.boost !== "basic") {
    let badgeStyle = "";
    let badgeText = "";
    
    if (ev.boost === "platinum") {
      // Système Top 10 avec enchères
      if (platinumRank === 1) {
        badgeStyle = "background:linear-gradient(135deg,#ffd700,#ff8c00);color:#1f2937;box-shadow:0 0 25px rgba(255,215,0,0.7);";
        badgeText = "👑 TOP 1";
      } else if (platinumRank === 2) {
        badgeStyle = "background:linear-gradient(135deg,#ef4444,#dc2626);color:#fff;box-shadow:0 0 20px rgba(239,68,68,0.6);";
        badgeText = "🔥 TOP 2";
      } else if (platinumRank === 3) {
        badgeStyle = "background:linear-gradient(135deg,#f97316,#ea580c);color:#fff;box-shadow:0 0 15px rgba(249,115,22,0.5);";
        badgeText = "⚡ TOP 3";
      } else {
        badgeStyle = "background:linear-gradient(135deg,#ef4444,#b91c1c);color:#fff;box-shadow:0 0 10px rgba(239,68,68,0.4);";
        badgeText = `🏆 TOP ${platinumRank}`;
      }
    } else if (ev.boost === "gold") {
      badgeStyle = "background:linear-gradient(135deg,rgba(255,215,0,0.9),rgba(218,165,32,0.9));color:#1f2937;";
      badgeText = "🥇 Gold";
    } else if (ev.boost === "silver") {
      badgeStyle = "background:linear-gradient(135deg,rgba(192,192,192,0.9),rgba(169,169,169,0.9));color:#1f2937;";
      badgeText = "🥈 Silver";
    } else {
      badgeStyle = "background:linear-gradient(135deg,rgba(205,127,50,0.9),rgba(184,115,51,0.9));color:#fff;";
      badgeText = "🥉 Bronze";
    }
    
    boostBadge = `
      <div style="position:absolute;top:12px;right:12px;padding:6px 12px;border-radius:999px;font-size:11px;font-weight:700;display:flex;align-items:center;gap:4px;backdrop-filter:blur(8px);${badgeStyle}">
        ${badgeText}
      </div>
    `;
  }

  // Badge vérifié amélioré
  const verifiedBadge = ev.verified ? `
    <span style="display:inline-flex;align-items:center;gap:4px;padding:4px 10px;border-radius:999px;background:linear-gradient(135deg,#3b82f6,#8b5cf6);color:#fff;font-size:10px;font-weight:600;box-shadow:0 2px 8px rgba(59,130,246,0.4);">
      ✓ Vérifié
    </span>
  ` : "";
  
  // Badge de validation organisateur (pour événements scrapés)
  let validationBadge = "";
  if (ev.validation_status === 'validated' || ev.validation_status === 'auto_validated') {
    validationBadge = `
      <div style="margin:8px 0;padding:8px 14px;background:linear-gradient(135deg,rgba(34,197,94,0.12),rgba(22,163,74,0.08));border:1px solid rgba(34,197,94,0.4);border-radius:10px;display:flex;align-items:center;gap:8px;">
        <span style="font-size:16px;">✅</span>
        <span style="font-size:11px;font-weight:700;color:#22c55e;line-height:1.3;">Validé</span>
      </div>
    `;
  }
  
  // Lien vers la source originale (pour événements scrapés)
  const evSourceUrl = ev.source_url || ev.sourceUrl;
  const sourceLink = evSourceUrl ? `
    <a href="${escapeHtml(evSourceUrl)}" target="_blank" rel="noopener noreferrer" style="display:inline-flex;align-items:center;gap:4px;padding:4px 10px;border-radius:999px;background:rgba(148,163,184,0.1);border:1px solid rgba(148,163,184,0.3);color:#94a3b8;font-size:10px;font-weight:500;text-decoration:none;transition:all 0.2s;" onmouseover="this.style.background='rgba(148,163,184,0.2)'" onmouseout="this.style.background='rgba(148,163,184,0.1)'">
      🔗 Source
    </a>
  ` : "";
  
  // Indicateur source (sans mention "Publié par MapEvent")
  const aiIndicator = ev.isAI ? `
    <div style="margin-top:8px;padding:8px 12px;background:linear-gradient(135deg,rgba(59,130,246,0.1),rgba(139,92,246,0.1));border:1px solid rgba(59,130,246,0.3);border-radius:10px;font-size:11px;color:#94a3b8;display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
      <span style="font-size:14px;">📢</span>
      <span>Source originale : <a href="${escapeHtml(evSourceUrl || '#')}" target="_blank" style="color:#60a5fa;text-decoration:underline;font-weight:600;">vérifier la source</a></span>
    </div>
  ` : "";

  // Stats avec icônes animées
  const isLiked = currentUser.likes.includes('event:'+ev.id);
  const isFavorite = currentUser.favorites.some(f => f.id === ev.id.toString() && f.mode === 'event');
  const isParticipating = currentUser.participating.includes('event:'+ev.id);
  const inAgenda = currentUser.agenda.includes('event:'+ev.id);
  
  // Trouver les amis qui participent à cet événement
  const friendsParticipating = getFriendsParticipatingToEvent(ev.id);
  const friendsSection = friendsParticipating.length > 0 ? `
    <div style="padding:10px 12px;background:linear-gradient(135deg,rgba(0,255,195,0.1),rgba(59,130,246,0.1));border:1px solid rgba(0,255,195,0.3);border-radius:10px;margin-bottom:10px;">
      <div style="font-size:11px;font-weight:600;color:#00ffc3;margin-bottom:8px;display:flex;align-items:center;gap:6px;">
        <span>👥</span> ${friendsParticipating.length} ami${friendsParticipating.length > 1 ? 's' : ''} y ${friendsParticipating.length > 1 ? 'vont' : 'va'} !
      </div>
      <div style="display:flex;gap:6px;flex-wrap:wrap;">
        ${friendsParticipating.slice(0, 5).map(f => `
          <div style="display:flex;align-items:center;gap:4px;padding:4px 8px;background:rgba(0,0,0,0.3);border-radius:999px;">
            <span style="font-size:14px;">${f.avatar}</span>
            <span style="font-size:11px;color:#fff;font-weight:500;">${f.name.split('_')[0]}</span>
          </div>
        `).join('')}
        ${friendsParticipating.length > 5 ? `<span style="font-size:11px;color:var(--ui-text-muted);">+${friendsParticipating.length - 5} autres</span>` : ''}
      </div>
    </div>
  ` : (currentUser.isLoggedIn && currentUser.friends?.length > 0 ? `
    <div style="padding:8px 12px;background:rgba(148,163,184,0.1);border-radius:10px;margin-bottom:10px;font-size:11px;color:var(--ui-text-muted);text-align:center;">
      👥 Aucun de vos amis ne participe encore. <span style="color:#00ffc3;cursor:pointer;" onclick="onAction('share', 'event', ${ev.id})">Invitez-les !</span>
    </div>
  ` : '');
  
  const statsRow = `
    <div style="display:flex;gap:16px;padding:10px 0;border-top:1px solid rgba(148,163,184,0.2);border-bottom:1px solid rgba(148,163,184,0.2);margin:10px 0;">
      <div style="display:flex;align-items:center;gap:6px;cursor:pointer;transition:transform 0.2s;" onclick="onAction('like', 'event', ${ev.id})">
        <span style="font-size:18px;${isLiked ? 'animation:bounce-in 0.3s;' : ''}">${isLiked ? '❤️' : '🤍'}</span>
        <span style="font-size:13px;font-weight:600;color:${isLiked ? '#ef4444' : 'var(--ui-text-muted)'};">${ev.likes || 0}</span>
      </div>
      <div style="display:flex;align-items:center;gap:6px;">
        <span style="font-size:18px;">💬</span>
        <span style="font-size:13px;font-weight:600;color:var(--ui-text-muted);">${ev.comments || 0}</span>
      </div>
      <div style="display:flex;align-items:center;gap:6px;">
        <span style="font-size:18px;">👥</span>
        <span style="font-size:13px;font-weight:600;color:var(--ui-text-muted);">${ev.participants || 0}</span>
      </div>
      <div style="margin-left:auto;display:flex;align-items:center;gap:6px;cursor:pointer;" onclick="onAction('favorite', 'event', ${ev.id})">
        <span style="font-size:18px;${isFavorite ? 'animation:bounce-in 0.3s;' : ''}">${isFavorite ? '⭐' : '☆'}</span>
      </div>
    </div>
    ${friendsSection}
  `;

  // Vérifier les alarmes existantes pour cet événement
  const eventAlarms = (currentUser.eventAlarms || []).filter(a => a.eventId === ev.id.toString());
  const hasAlarms = eventAlarms.length > 0;
  const canAddAlarm = eventAlarms.length < 2 && inAgenda;
  
  // Actions avec design moderne (barre fixe en bas au scroll)
  const actionsRow = `
    <div class="popup-actions-sticky" style="position:sticky;bottom:0;background:var(--ui-card-bg);z-index:10;padding:12px 0 8px;margin-top:12px;border-top:1px solid var(--ui-card-border);">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:0;">
      <button onclick="onAction('participate', 'event', ${ev.id})" style="padding:12px;border-radius:12px;border:none;font-weight:700;font-size:13px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;transition:all 0.2s;
        ${isParticipating ? 
          'background:linear-gradient(135deg,#22c55e,#16a34a);color:#fff;box-shadow:0 4px 12px rgba(34,197,94,0.4);' : 
          'background:linear-gradient(135deg,#00ffc3,#10b981);color:#022c22;box-shadow:0 4px 12px rgba(0,255,195,0.4);'}">
        ${isParticipating ? '✅ Inscrit' : '🎟️ Participer'}
      </button>
      <button onclick="onAction('agenda', 'event', ${ev.id})" style="padding:12px;border-radius:12px;border:1px solid rgba(59,130,246,0.5);background:${inAgenda ? 'rgba(59,130,246,0.2)' : 'transparent'};color:${inAgenda ? '#3b82f6' : 'var(--ui-text-main)'};font-weight:600;font-size:13px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;transition:all 0.2s;">
        ${inAgenda ? '📅 Dans agenda' : '📅 Ajouter'}
      </button>
    </div>
    ${inAgenda && currentUser.isLoggedIn ? `
      <div style="margin-top:8px;">
        ${canAddAlarm ? `
          <button onclick="openAddAlarmModal('event', ${ev.id})" style="width:100%;padding:10px;border-radius:10px;border:1px solid rgba(245,158,11,0.5);background:rgba(245,158,11,0.1);color:#f59e0b;font-weight:600;font-size:12px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px;transition:all 0.2s;">
            ⏰ Ajouter alarme (${eventAlarms.length}/2)
          </button>
        ` : hasAlarms ? `
          <div style="padding:10px;border-radius:10px;border:1px solid rgba(245,158,11,0.3);background:rgba(245,158,11,0.1);color:#f59e0b;font-size:12px;text-align:center;">
            ⏰ ${eventAlarms.length} alarme${eventAlarms.length > 1 ? 's' : ''} configurée${eventAlarms.length > 1 ? 's' : ''}
          </div>
        ` : ''}
      </div>
    ` : ''}
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-top:8px;">
      ${currentUser.isLoggedIn ? `
        <button onclick="(function(){try{if(window.openEventDiscussion){window.openEventDiscussion('event',${ev.id});}else if(window.openDiscussionModal){window.openDiscussionModal('event',${ev.id});}else{console.warn('Discussion non disponible');}}catch(e){console.error('Erreur ouverture discussion:',e);}})();" style="padding:10px;border-radius:10px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);font-size:12px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px;transition:all 0.2s;" title="Canal de discussion">
          💬 Discussion
        </button>
        <button onclick="window.viewEventAttendees && window.viewEventAttendees('event', ${ev.id})" style="padding:10px;border-radius:10px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);font-size:12px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px;transition:all 0.2s;" title="Voir qui participe">
          👥 Participants
        </button>
        <button onclick="inviteFriendsToEvent('event', ${ev.id})" style="padding:10px;border-radius:10px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);font-size:12px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px;transition:all 0.2s;" title="Inviter des amis">
          ➕ Inviter
        </button>
      ` : ''}
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;margin-top:8px;">
      ${currentUser.isLoggedIn ? `
        <button onclick="onAction('route', 'event', ${ev.id})" style="padding:10px;border-radius:10px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);font-size:12px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px;transition:all 0.2s;">
          🗺️ Y aller
        </button>
      ` : `
        <button onclick="onAction('route', 'event', ${ev.id})" style="padding:10px;border-radius:10px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);font-size:12px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px;transition:all 0.2s;">
          🗺️ Y aller
        </button>
      `}
      <button onclick="window.sharePopup('event', ${ev.id})" style="padding:10px;border-radius:10px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);font-size:12px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px;transition:all 0.2s;" title="Partager le lien">
        🔗 Partager
      </button>
      <button onclick="onAction('avis', 'event', ${ev.id})" style="padding:10px;border-radius:10px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);font-size:12px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px;transition:all 0.2s;">
        ⭐ Avis
      </button>
      <button onclick="onAction('report', 'event', ${ev.id})" style="padding:10px;border-radius:10px;border:1px solid rgba(239,68,68,0.3);background:rgba(239,68,68,0.1);color:#ef4444;font-size:12px;cursor:pointer;transition:all 0.2s;" title="Signaler">
        🚨
      </button>
    </div>
    </div>
  `;

  // Reviews compactes
  const reviewsSection = (() => {
    // ⚠️⚠️⚠️ CRITIQUE : S'assurer que currentUser.reviews existe
    if (!currentUser.reviews || typeof currentUser.reviews !== 'object') {
      currentUser.reviews = {};
    }
    const key = `event:${ev.id}`;
    const reviews = currentUser.reviews[key] || [];
    if (reviews.length === 0 && !ev.rating) return '';
    
    const ratingStars = ev.rating ? `
      <div style="display:flex;align-items:center;gap:6px;margin-bottom:8px;">
        <div style="display:flex;gap:2px;">
          ${[1,2,3,4,5].map(i => `<span style="font-size:14px;${i <= Math.floor(parseFloat(ev.rating)) ? '' : 'opacity:0.3;'}"}>⭐</span>`).join('')}
        </div>
        <span style="font-size:14px;font-weight:700;color:#fbbf24;">${ev.rating}</span>
        <span style="font-size:11px;color:var(--ui-text-muted);">(${reviews.length} avis)</span>
      </div>
    ` : '';
    
    const latestReview = reviews.length > 0 ? `
      <div style="padding:10px;background:rgba(15,23,42,0.5);border-radius:10px;border:1px solid var(--ui-card-border);">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
          <div style="width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,${reviews[0].avatarColor || '#00ffc3'},${reviews[0].avatarColor2 || '#3b82f6'});display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#fff;">
            ${reviews[0].avatar || reviews[0].userName.charAt(0).toUpperCase()}
          </div>
          <div style="flex:1;">
            <div style="font-weight:600;font-size:12px;color:var(--ui-text-main);">${escapeHtml(reviews[0].userName)}</div>
            ${reviews[0].rating ? `<div style="font-size:10px;color:#fbbf24;">${'⭐'.repeat(reviews[0].rating)}</div>` : ''}
          </div>
        </div>
        <div style="font-size:12px;color:var(--ui-text-main);line-height:1.4;">"${escapeHtml(reviews[0].text.length > 100 ? reviews[0].text.substring(0, 100) + '...' : reviews[0].text)}"</div>
        ${reviews.length > 1 ? `
          <button onclick="onAction('avis', 'event', ${ev.id})" style="margin-top:8px;padding:6px 12px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-muted);font-size:11px;cursor:pointer;width:100%;">
            Voir les ${reviews.length} avis →
          </button>
        ` : ''}
      </div>
    ` : '';
    
    return ratingStars + latestReview;
  })();

  return `
    <div style="width:100%;max-height:none;overflow:visible;font-family:system-ui,sans-serif;color:var(--ui-text-main);margin:0;padding:0;box-sizing:border-box;">
      <!-- Image principale avec overlay - ALIGNÉE PARFAITEMENT avec la bordure de la modal -->
      <div style="position:relative;border-radius:16px 16px 0 0;overflow:hidden;margin:0;padding:0;width:100%;left:0;right:0;box-sizing:border-box;min-height:280px;background:linear-gradient(135deg,#3b82f6,#8b5cf6);">
        <div style="position:relative;width:100%;margin:0;padding:0;box-sizing:border-box;min-height:280px;display:flex;align-items:stretch;">
          ${imgTag}
          ${statusOverlay}
          ${boostBadge}
          <!-- Gradient overlay -->
          <div style="position:absolute;bottom:0;left:0;right:0;height:80px;background:linear-gradient(to top,rgba(15,23,42,0.95),transparent);pointer-events:none;"></div>
          <!-- Time badge -->
          ${timeLabel ? `
            <div style="position:absolute;bottom:12px;left:12px;padding:6px 12px;border-radius:999px;background:${timeLabelColor};color:#fff;font-size:11px;font-weight:700;box-shadow:0 2px 8px rgba(0,0,0,0.3);">
              ${daysUntil === 0 ? '🔥' : daysUntil === 1 ? '⏰' : '📅'} ${timeLabel}
            </div>
          ` : ''}
        </div>
      </div>
      
      <!-- Content - ALIGNÉ AVEC L'IMAGE -->
      <div style="padding:16px 12px 12px;margin:0;width:100%;box-sizing:border-box;">
        <!-- Category & Verified -->
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap;">
          <span style="font-size:28px;filter:drop-shadow(0 2px 4px rgba(0,0,0,0.2));">${emoji}</span>
          <span style="font-size:12px;color:var(--ui-text-muted);padding:4px 10px;background:rgba(148,163,184,0.1);border-radius:999px;">${cats}</span>
          ${verifiedBadge}
          ${sourceLink}
        </div>
        
        <!-- Title -->
        <h3 style="margin:0 0 10px;font-size:20px;font-weight:800;line-height:1.3;color:var(--ui-text-main);">${escapeHtml(evTranslated.title || ev.title || "")}</h3>
        
        <!-- Validation organisateur (bloc visible sous le titre) -->
        ${validationBadge}
        
        <!-- Date & Location Cards -->
        <div style="display:flex;flex-direction:column;gap:8px;margin-bottom:12px;">
          <div style="display:flex;align-items:center;gap:10px;padding:10px 12px;background:linear-gradient(135deg,rgba(0,255,195,0.1),rgba(16,185,129,0.05));border:1px solid rgba(0,255,195,0.2);border-radius:10px;">
            <span style="font-size:20px;">📅</span>
            <div>
              <div style="font-size:13px;font-weight:600;color:#00ffc3;">${formatEventDateRange(startDate, endDate, !!ev.source_url)}</div>
              ${ev.source_url ? `<div style="font-size:11px;color:#f59e0b;margin-top:4px;">⚠️ Pour l'heure exacte, voir la publication originale</div>` : ''}
            </div>
          </div>
          <div style="display:flex;align-items:center;gap:10px;padding:10px 12px;background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.2);border-radius:10px;">
            <span style="font-size:20px;">📍</span>
            <div style="font-size:13px;font-weight:500;color:var(--ui-text-main);flex:1;">${escapeHtml(popupAddress)}</div>
          </div>
          ${(ev.source_url || ev.sourceUrl) ? `
            <a href="${escapeHtml(ev.source_url || ev.sourceUrl || '#')}" target="_blank" rel="noopener noreferrer" style="display:flex;align-items:center;gap:10px;padding:12px;background:linear-gradient(135deg,rgba(245,158,11,0.15),rgba(234,88,12,0.1));border:2px solid rgba(245,158,11,0.5);border-radius:10px;text-decoration:none;transition:all 0.2s;" onmouseover="this.style.background='linear-gradient(135deg,rgba(245,158,11,0.25),rgba(234,88,12,0.2))';this.style.transform='scale(1.01)'" onmouseout="this.style.background='linear-gradient(135deg,rgba(245,158,11,0.15),rgba(234,88,12,0.1))';this.style.transform='scale(1)'">
              <span style="font-size:24px;">🔗</span>
              <div style="flex:1;">
                <div style="font-size:13px;font-weight:700;color:#f59e0b;">VOIR LA PUBLICATION ORIGINALE</div>
                <div style="font-size:11px;color:#94a3b8;margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml((ev.source_url || ev.sourceUrl || '').substring(0, 50))}...</div>
              </div>
              <span style="font-size:18px;color:#f59e0b;">→</span>
            </a>
          ` : ''}
        </div>
        
        <!-- Description -->
        ${popupDescription ? `
          <div style="font-size:14px;color:#ffffff;line-height:1.7;margin-bottom:12px;padding:12px;background:transparent;border-radius:8px;">
            ${escapeHtml(popupDescription)}
          </div>
        ` : ""}
        
        <!-- Audio Player (si liens audio disponibles) -->
        ${(ev.audioLinks && ev.audioLinks.length > 0) || (ev.soundLinks && ev.soundLinks.length > 0) ? (() => {
          const evAudioLinks = [...(ev.soundLinks || []), ...(ev.audioLinks || [])].filter(Boolean);
          const evTitle = (ev.title || ev.name || '').replace(/"/g, '&quot;');
          return `
          <div style="margin:8px 0 12px;padding:12px;background:linear-gradient(135deg,rgba(139,92,246,0.15),rgba(59,130,246,0.1));border-radius:12px;border:1px solid rgba(139,92,246,0.3);">
            <div style="font-size:12px;color:#a78bfa;margin-bottom:10px;font-weight:600;">🎵 Écouter directement</div>
            <div style="display:flex;flex-direction:column;gap:8px;">
              ${evAudioLinks.slice(0, 5).map((link, i) => {
                const safeUrl = (link || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
                const trackLabel = 'Piste ' + (i + 1) + (link.includes('audius') ? ' • Audius' : link.includes('soundcloud') ? ' • SoundCloud' : link.includes('spotify') ? ' • Spotify' : '');
                return `
                <div data-audio-track data-item-title="${evTitle}" data-track-label="${trackLabel}" style="display:flex;flex-direction:column;gap:6px;padding:10px 12px;background:rgba(0,0,0,0.3);border-radius:10px;">
                  <audio id="event-audio-${ev.id}-${i}" src="${safeUrl}" data-original-src="${safeUrl}" preload="metadata" style="display:none;"></audio>
                  <div style="display:flex;align-items:center;gap:10px;">
                    <button onclick="event.stopPropagation();toggleEventAudio('${ev.id}',${i})" id="btn-event-${ev.id}-${i}" style="width:36px;height:36px;border-radius:50%;border:none;background:linear-gradient(135deg,#a78bfa,#8b5cf6);color:white;cursor:pointer;font-size:14px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">▶</button>
                    <div style="flex:1;min-width:0;">
                      <div style="font-size:12px;color:#e5e7eb;font-weight:500;">Piste ${i + 1}</div>
                      <div style="font-size:10px;color:var(--ui-text-muted);">${link.includes('audius') ? '🎵 Audius' : link.includes('soundcloud') ? '☁️ SoundCloud' : link.includes('spotify') ? '🟢 Spotify' : link.includes('youtube') ? '▶️ YouTube' : '🎵 Audio'}</div>
                    </div>
                    <button onclick="event.stopPropagation();seekAudioOffset('event','${ev.id}',${i},-15)" style="width:32px;height:32px;border-radius:50%;border:1px solid rgba(167,139,250,0.5);background:transparent;color:#a78bfa;cursor:pointer;font-size:12px;flex-shrink:0;display:flex;align-items:center;justify-content:center;">⏪</button>
                    <button onclick="event.stopPropagation();seekAudioOffset('event','${ev.id}',${i},15)" style="width:32px;height:32px;border-radius:50%;border:1px solid rgba(167,139,250,0.5);background:transparent;color:#a78bfa;cursor:pointer;font-size:12px;flex-shrink:0;display:flex;align-items:center;justify-content:center;">⏩</button>
                    <span id="time-event-${ev.id}-${i}" style="font-size:10px;color:#a78bfa;font-variant-numeric:tabular-nums;min-width:70px;text-align:right;flex-shrink:0;">0:00</span>
                  </div>
                  <div id="seekbar-event-${ev.id}-${i}" onmousedown="event.stopPropagation();startAudioDrag('event','${ev.id}',${i},event)" ontouchstart="event.stopPropagation();event.preventDefault();startAudioDrag('event','${ev.id}',${i},event)" onclick="event.stopPropagation();seekEventAudio('${ev.id}',${i},event)" style="width:100%;height:14px;padding:12px 0;margin:-12px 0;cursor:pointer;position:relative;touch-action:none;-webkit-user-select:none;user-select:none;-webkit-tap-highlight-color:transparent;" title="Cliquer pour aller à la position dans le son">
                    <div style="height:14px;background:rgba(255,255,255,0.15);border-radius:7px;overflow:hidden;position:relative;">
                      <div id="progress-event-${ev.id}-${i}" style="width:0%;height:100%;background:linear-gradient(90deg,#a78bfa,#8b5cf6);border-radius:7px;transition:width 0.05s;pointer-events:none;"></div>
                    </div>
                  </div>
                </div>`;
              }).join('')}
            </div>
          </div>`;
        })() : ''}
        
        <!-- Stats -->
        ${statsRow}
        
        <!-- Reviews -->
        ${reviewsSection}
        
        <!-- AI Indicator -->
        ${aiIndicator}
        
        <!-- Actions - barre fixe en bas quand scroll -->
        <div class="popup-actions-sticky" style="position:sticky;bottom:0;background:var(--ui-card-bg);margin:12px -12px -12px -12px;padding:12px 12px 12px 12px;z-index:10;border-top:1px solid rgba(148,163,184,0.2);">
          ${actionsRow}
        </div>
      </div>
    </div>
  `;
}

// POPUP BOOKING
function buildBookingPopup(b) {
  // Protection contre les erreurs TDZ
  if (typeof window.t !== 'function') {
    window.t = function(key) { return key; };
  }
  if (!window.translations || typeof window.translations !== 'object') {
    window.translations = window.translations || { fr: {}, en: {}, es: {}, zh: {}, hi: {} };
  }
  
  // ⚠️⚠️⚠️ CRITIQUE : S'assurer que currentUser est défini et a les propriétés nécessaires
  if (typeof currentUser === 'undefined' || !currentUser) {
    currentUser = {
      isLoggedIn: false,
      favorites: [],
      agenda: [],
      participating: [],
      subscription: 'free'
    };
  }
  
  // S'assurer que les propriétés nécessaires existent
  if (!Array.isArray(currentUser.favorites)) {
    currentUser.favorites = [];
  }
  if (!Array.isArray(currentUser.agenda)) {
    currentUser.agenda = [];
  }
  if (!currentUser.subscription) {
    currentUser.subscription = 'free';
  }
  // ⚠️⚠️⚠️ CRITIQUE : S'assurer que reviews est un objet (pas undefined)
  if (!currentUser.reviews || typeof currentUser.reviews !== 'object') {
    currentUser.reviews = {};
  }
  
  // ⚠️⚠️⚠️ CRITIQUE : S'assurer que paidContacts est défini
  if (typeof paidContacts === 'undefined' || !Array.isArray(paidContacts)) {
    paidContacts = [];
  }
  
  const borderColor = getBoostColor(b.boost);
  const imgTag = buildMainImageTag(b, b.name || "");
  const cats = (b.categories || []).join(" • ");
  const emoji = getCategoryEmoji(b);

  // Badge niveau
  const levelColors = {
    "Débutant": "#9ca3af",
    "Semi-pro": "#3b82f6",
    "Pro": "#8b5cf6",
    "Headliner": "#f59e0b",
    "International": "#ef4444",
    "Non détecté": "#6b7280"
  };
  const levelBadge = b.level ? `
    <span style="display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:999px;font-size:10px;font-weight:600;background:${levelColors[b.level] || '#6b7280'};color:white;">
      ${b.level === "Headliner" ? "🌟" : b.level === "International" ? "🌍" : "🎵"} ${b.level}
    </span>
  ` : "";

  // Badge vérifié
  const verifiedBadge = b.verified ? `<span class="verified-badge">✓ Vérifié</span>` : "";

  // Liens sons - Player intégré sans accès au site
  // ⚠️ GRATUIT : Coordonnées toujours affichées (plus de paiement requis)
  const hasPaidContact = true;
  
  // Fusionner soundLinks (scraping) et audioLinks (publication utilisateur)
  const allSoundLinks = [...(b.soundLinks || []), ...(b.audioLinks || [])].filter(Boolean);
  
  const soundsSection = allSoundLinks.length > 0 ? `
    <div style="margin:8px 0;padding:12px;background:linear-gradient(135deg,rgba(139,92,246,0.15),rgba(59,130,246,0.1));border-radius:12px;border:1px solid rgba(139,92,246,0.3);">
      <div style="font-size:12px;color:#a78bfa;margin-bottom:10px;font-weight:600;">🎵 Écouter directement</div>
      
      <div style="display:flex;flex-direction:column;gap:8px;">
        ${allSoundLinks.slice(0, 12).map((link, i) => {
          const safeUrl = (link || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
          const safeTitle = (b.name || '').replace(/"/g, '&quot;');
          const trackLabel = 'Piste ' + (i + 1) + (link.includes('audius') ? ' • Audius' : link.includes('soundcloud') ? ' • SoundCloud' : link.includes('spotify') ? ' • Spotify' : '');
          return `
          <div data-audio-track data-item-title="${safeTitle}" data-track-label="${trackLabel}" style="display:flex;flex-direction:column;gap:6px;padding:10px 12px;background:rgba(0,0,0,0.3);border-radius:10px;">
            <audio id="booking-audio-${b.id}-${i}" src="${safeUrl}" data-original-src="${safeUrl}" preload="metadata" style="display:none;"></audio>
            <div style="display:flex;align-items:center;gap:10px;">
              <button onclick="event.stopPropagation();toggleBookingAudio('${b.id}',${i})" id="btn-booking-${b.id}-${i}" style="width:36px;height:36px;border-radius:50%;border:none;background:linear-gradient(135deg,#a78bfa,#8b5cf6);color:white;cursor:pointer;font-size:14px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">▶</button>
              <div style="flex:1;min-width:0;">
                <div style="font-size:12px;color:#e5e7eb;font-weight:500;">Piste ${i + 1}</div>
                <div style="font-size:10px;color:var(--ui-text-muted);">${link.includes('audius') ? '🎵 Audius' : link.includes('soundcloud') ? '☁️ SoundCloud' : link.includes('spotify') ? '🟢 Spotify' : link.includes('youtube') ? '▶️ YouTube' : '🎵 Audio'}</div>
              </div>
              <button onclick="event.stopPropagation();seekAudioOffset('booking','${b.id}',${i},-15)" style="width:32px;height:32px;border-radius:50%;border:1px solid rgba(167,139,250,0.5);background:transparent;color:#a78bfa;cursor:pointer;font-size:12px;flex-shrink:0;display:flex;align-items:center;justify-content:center;">⏪</button>
              <button onclick="event.stopPropagation();seekAudioOffset('booking','${b.id}',${i},15)" style="width:32px;height:32px;border-radius:50%;border:1px solid rgba(167,139,250,0.5);background:transparent;color:#a78bfa;cursor:pointer;font-size:12px;flex-shrink:0;display:flex;align-items:center;justify-content:center;">⏩</button>
              <span id="time-booking-${b.id}-${i}" style="font-size:10px;color:#a78bfa;font-variant-numeric:tabular-nums;min-width:70px;text-align:right;flex-shrink:0;">0:00</span>
            </div>
            <div id="seekbar-booking-${b.id}-${i}" onmousedown="event.stopPropagation();startAudioDrag('booking','${b.id}',${i},event)" ontouchstart="event.stopPropagation();event.preventDefault();startAudioDrag('booking','${b.id}',${i},event)" onclick="event.stopPropagation();seekBookingAudio('${b.id}',${i},event)"  style="width:100%;height:14px;padding:12px 0;margin:-12px 0;cursor:pointer;position:relative;touch-action:none;-webkit-user-select:none;user-select:none;-webkit-tap-highlight-color:transparent;" title="Cliquer pour aller à la position dans le son">
              <div style="height:14px;background:rgba(255,255,255,0.15);border-radius:7px;overflow:hidden;position:relative;">
                <div id="progress-booking-${b.id}-${i}" style="width:0%;height:100%;background:linear-gradient(90deg,#a78bfa,#8b5cf6);border-radius:7px;transition:width 0.05s;pointer-events:none;"></div>
              </div>
            </div>
          </div>`;
        }).join('')}
      </div>
    </div>
  ` : '';

  // Rating
  const ratingStars = b.rating ? `
    <div style="display:flex;align-items:center;gap:4px;margin-bottom:6px;">
      ${'⭐'.repeat(Math.floor(parseFloat(b.rating)))}
      <span style="font-size:12px;color:var(--ui-text-muted);">${b.rating}/5</span>
      <span style="font-size:11px;color:var(--ui-text-muted);">(${b.likes || 0} avis)</span>
    </div>
  ` : "";

  // Lien publication originale (si disponible)
  const sourceUrl = b.sourceUrl || b.source_url;
  const sourceLinkBlock = sourceUrl ? `
    <a href="${escapeHtml(sourceUrl)}" target="_blank" rel="noopener noreferrer" style="display:flex;align-items:center;gap:10px;padding:10px 12px;margin:8px 0;background:linear-gradient(135deg,rgba(245,158,11,0.15),rgba(234,88,12,0.1));border:2px solid rgba(245,158,11,0.5);border-radius:10px;text-decoration:none;transition:all 0.2s;" onmouseover="this.style.background='linear-gradient(135deg,rgba(245,158,11,0.25),rgba(234,88,12,0.2))';this.style.transform='scale(1.01)'" onmouseout="this.style.background='linear-gradient(135deg,rgba(245,158,11,0.15),rgba(234,88,12,0.1))';this.style.transform='scale(1)'">
      <span style="font-size:20px;">🔗</span>
      <div style="flex:1;">
        <div style="font-size:12px;font-weight:700;color:#f59e0b;">VOIR LA PUBLICATION ORIGINALE</div>
        <div style="font-size:10px;color:#94a3b8;margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(sourceUrl.substring(0, 45))}...</div>
      </div>
      <span style="font-size:16px;color:#f59e0b;">→</span>
    </a>
  ` : "";

  // Indicateur source (sans mention "Publié par MapEvent")
  const aiIndicator = b.isAI ? `
    <div style="margin:6px 0;padding:6px 10px;background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:8px;font-size:11px;color:#94a3b8;">
      📢 Source originale : <a href="${sourceUrl || '#'}" target="_blank" style="color:#60a5fa;text-decoration:underline;">vérifier la source</a>
    </div>
  ` : "";

  const actionsRow = `
    <div class="popup-actions-sticky" style="position:sticky;bottom:0;background:var(--ui-card-bg);z-index:10;padding:12px 0 8px;margin-top:12px;border-top:1px solid var(--ui-card-border);">
    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:0;">
      <button onclick="onAction('like', 'booking', ${b.id})" class="pill small" style="flex:1;">
        ${currentUser.likes.includes('booking:'+b.id) ? '👍' : '👍'} Like
      </button>
      <button onclick="onAction('favorite', 'booking', ${b.id})" class="pill small" style="flex:1;">
        ${currentUser.favorites.some(f => f.id === b.id.toString() && f.mode === 'booking') ? '⭐' : '☆'} Favoris
      </button>
      <button onclick="window.sharePopup('booking', ${b.id})" class="pill small" style="flex:1;">📤 Partager</button>
      ${currentUser.isLoggedIn ? `
        <button onclick="inviteFriendsToEvent('booking', ${b.id})" class="pill small" style="flex:1;">➕ Inviter</button>
      ` : ''}
    </div>
    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:6px;">
      <button onclick="onAction('agenda', 'booking', ${b.id})" class="pill small" style="flex:1;">
        ${currentUser.agenda.includes('booking:'+b.id) ? '📅 ' + ((typeof window.t === 'function' ? window.t("in_agenda") : null) || "Dans agenda") : '📅 ' + (typeof window.t === 'function' ? window.t("agenda") : "Agenda")}
      </button>
    </div>
    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:6px;">
      <button onclick="onAction('avis', 'booking', ${b.id})" class="pill small" style="flex:1;">⭐ Avis</button>
      <button onclick="onAction('discussion', 'booking', ${b.id})" class="pill small" style="flex:1;">💬 Contact</button>
      <button onclick="onAction('report', 'booking', ${b.id})" class="pill small" style="color:#ef4444;">🚨</button>
    </div>
    </div>
  `;

  return `
    <div style="width:100%;max-height:none;overflow:visible;font-family:system-ui,sans-serif;color:var(--ui-text-main);margin:0;padding:0;box-sizing:border-box;">
      <!-- Image principale avec overlay - ALIGNÉE PARFAITEMENT avec la bordure de la modal -->
      <div style="position:relative;border-radius:16px 16px 0 0;overflow:hidden;margin:0;padding:0;width:100%;left:0;right:0;box-sizing:border-box;min-height:280px;background:linear-gradient(135deg,#3b82f6,#8b5cf6);">
        <div style="position:relative;width:100%;margin:0;padding:0;box-sizing:border-box;min-height:280px;display:flex;align-items:stretch;">
          ${imgTag}
        </div>
      </div>
      
      <!-- Content - ALIGNÉ AVEC L'IMAGE -->
      <div style="padding:16px 12px 12px;margin:0;width:100%;box-sizing:border-box;">
        <!-- Category & Verified -->
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap;">
          <span style="font-size:28px;filter:drop-shadow(0 2px 4px rgba(0,0,0,0.2));">${emoji}</span>
          <span style="font-size:12px;color:var(--ui-text-muted);padding:4px 10px;background:rgba(148,163,184,0.1);border-radius:999px;">${cats}</span>
          ${levelBadge}
          ${verifiedBadge}
        </div>
        
        <!-- Title -->
        <h3 style="margin:0 0 10px;font-size:20px;font-weight:800;line-height:1.3;color:var(--ui-text-main);">${escapeHtml(b.name || "")}</h3>
        ${ratingStars ? `
          <div style="display:flex;align-items:center;gap:4px;margin-bottom:6px;">
            ${'⭐'.repeat(Math.floor(parseFloat(b.rating)))}
            <span style="font-size:13px;color:#facc15;font-weight:600;">${b.rating}/5</span>
            <span style="font-size:11px;color:var(--ui-text-muted);">(${b.likes || 0} avis)</span>
        </div>
        ` : ''}
        <div style="font-size:13px;color:#1f2937;background:rgba(255,255,255,0.95);padding:6px 8px;border-radius:8px;margin-bottom:6px;font-weight:500;">
          📍 ${hasPaidContact ? escapeHtml(b.address || b.city || "") : escapeHtml(maskAddressNumber(b.address || b.city || ""))}
        </div>
        ${b.description ? `<div style="font-size:14px;color:#ffffff;margin-bottom:12px;line-height:1.7;padding:12px;background:transparent;border-radius:8px;">${escapeHtml(stripPhoneNumbers(b.description))}</div>` : ""}
        ${soundsSection}
        ${sourceLinkBlock}
        ${aiIndicator}
        ${hasPaidContact ? `
          <div style="margin:8px 0;padding:12px;background:linear-gradient(135deg,rgba(0,255,195,0.15),rgba(34,197,94,0.1));border:1px solid rgba(0,255,195,0.3);border-radius:10px;">
            <div style="font-size:12px;color:#00ffc3;font-weight:600;margin-bottom:8px;">✅ Contact</div>
            <div style="font-size:13px;color:#e5e7eb;">📧 ${b.email || 'contact@artiste.ch'}</div>
            <div style="font-size:10px;color:var(--ui-text-muted);margin-top:6px;">📅 Ajouté à votre agenda permanent</div>
        </div>
        ` : `
          <div style="font-size:11px;color:#6b7280;margin:8px 0;padding:8px;background:rgba(107,114,128,0.1);border-radius:8px;">
            🔒 Coordonnées masquées • Email disponible après paiement
          </div>
        `}
        <div class="popup-actions-sticky" style="position:sticky;bottom:0;background:var(--ui-card-bg);margin:12px -12px -12px -12px;padding:12px;z-index:10;border-top:1px solid rgba(148,163,184,0.2);">
          ${actionsRow}
        </div>
        ${!hasPaidContact ? `
          <button onclick="onBuyContact('booking', ${b.id})" style="margin-top:10px;width:100%;padding:12px;border-radius:999px;border:none;cursor:pointer;font-size:14px;font-weight:700;background:var(--btn-main-bg);color:var(--btn-main-text);box-shadow:var(--btn-main-shadow);">
            💳 Débloquer contact + sons – CHF 1.–
        </button>
        ` : ''}
      </div>
    </div>
  `;
}

// POPUP SERVICE
function buildServicePopup(s) {
  // Protection contre les erreurs TDZ
  if (typeof window.t !== 'function') {
    window.t = function(key) { return key; };
  }
  if (!window.translations || typeof window.translations !== 'object') {
    window.translations = window.translations || { fr: {}, en: {}, es: {}, zh: {}, hi: {} };
  }
  
  // ⚠️⚠️⚠️ CRITIQUE : S'assurer que currentUser est défini et a les propriétés nécessaires
  if (typeof currentUser === 'undefined' || !currentUser) {
    currentUser = {
      isLoggedIn: false,
      favorites: [],
      agenda: [],
      participating: [],
      subscription: 'free'
    };
  }
  
  // S'assurer que les propriétés nécessaires existent
  if (!currentUser.subscription) {
    currentUser.subscription = 'free';
  }
  // ⚠️⚠️⚠️ CRITIQUE : S'assurer que reviews est un objet (pas undefined)
  if (!currentUser.reviews || typeof currentUser.reviews !== 'object') {
    currentUser.reviews = {};
  }
  
  // ⚠️⚠️⚠️ CRITIQUE : S'assurer que paidContacts est défini
  if (typeof paidContacts === 'undefined' || !Array.isArray(paidContacts)) {
    paidContacts = [];
  }
  
  const borderColor = getBoostColor(s.boost);
  const imgTag = buildMainImageTag(s, s.name || "");
  const cats = (s.categories || []).join(" • ");
  const emoji = getCategoryEmoji(s);
  // ⚠️ GRATUIT : Coordonnées toujours affichées (plus de paiement requis)
  const hasPaidContact = true;

  // Badge vérifié
  const verifiedBadge = s.verified ? `<span class="verified-badge">✓ Vérifié</span>` : "";

  // Rating
  const ratingStars = s.rating ? `
    <div style="display:flex;align-items:center;gap:4px;margin-bottom:6px;">
      ${'⭐'.repeat(Math.floor(parseFloat(s.rating)))}
      <span style="font-size:12px;color:var(--ui-text-muted);">${s.rating}/5</span>
      <span style="font-size:11px;color:var(--ui-text-muted);">(${s.likes || 0} avis)</span>
    </div>
  ` : "";

  // Indicateur source (sans mention "Publié par MapEvent")
  const aiIndicator = s.isAI ? `
    <div style="margin:6px 0;padding:6px 10px;background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:8px;font-size:11px;color:#94a3b8;">
      📢 Source originale : <a href="${s.sourceUrl || '#'}" target="_blank" style="color:#60a5fa;text-decoration:underline;">vérifier la source</a>
    </div>
  ` : "";

  const actionsRow = `
    <div class="popup-actions-sticky" style="position:sticky;bottom:0;background:var(--ui-card-bg);z-index:10;padding:12px 0 8px;margin-top:12px;border-top:1px solid var(--ui-card-border);">
    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:0;">
      <button onclick="onAction('like', 'service', ${s.id})" class="pill small" style="flex:1;">
        ${currentUser.likes.includes('service:'+s.id) ? '👍' : '👍'} Like
      </button>
      <button onclick="onAction('favorite', 'service', ${s.id})" class="pill small" style="flex:1;">
        ${currentUser.favorites.some(f => f.id === s.id.toString() && f.mode === 'service') ? '⭐' : '☆'} Favoris
      </button>
      <button onclick="window.sharePopup('service', ${s.id})" class="pill small" style="flex:1;">📤 Partager</button>
      ${currentUser.isLoggedIn ? `
        <button onclick="inviteFriendsToEvent('service', ${s.id})" class="pill small" style="flex:1;">➕ Inviter</button>
      ` : ''}
    </div>
    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:6px;">
      <button onclick="onAction('agenda', 'service', ${s.id})" class="pill small" style="flex:1;">
        ${currentUser.agenda.includes('service:'+s.id) ? '📅 ' + ((typeof window.t === 'function' ? window.t("in_agenda") : null) || "Dans agenda") : '📅 ' + (typeof window.t === 'function' ? window.t("agenda") : "Agenda")}
      </button>
      <button onclick="onAction('route', 'service', ${s.id})" class="pill small" style="flex:1;">🗺️ ${(typeof window.t === 'function' ? window.t("route") : null) || "Itinéraire"}</button>
    </div>
    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:6px;">
      <button onclick="onAction('avis', 'service', ${s.id})" class="pill small" style="flex:1;">⭐ Avis</button>
      <button onclick="onAction('discussion', 'service', ${s.id})" class="pill small" style="flex:1;">💬 Contact</button>
      <button onclick="onAction('report', 'service', ${s.id})" class="pill small" style="color:#ef4444;">🚨</button>
    </div>
    </div>
  `;

  return `
    <div style="width:100%;max-height:none;overflow:visible;font-family:system-ui,sans-serif;color:var(--ui-text-main);margin:0;padding:0;box-sizing:border-box;">
      <!-- Image principale avec overlay - ALIGNÉE PARFAITEMENT avec la bordure de la modal -->
      <div style="position:relative;border-radius:16px 16px 0 0;overflow:hidden;margin:0;padding:0;width:100%;left:0;right:0;box-sizing:border-box;min-height:280px;background:linear-gradient(135deg,#3b82f6,#8b5cf6);">
        <div style="position:relative;width:100%;margin:0;padding:0;box-sizing:border-box;min-height:280px;display:flex;align-items:stretch;">
          ${imgTag}
        </div>
      </div>
      
      <!-- Content - ALIGNÉ AVEC L'IMAGE -->
      <div style="padding:16px 12px 12px;margin:0;width:100%;box-sizing:border-box;">
        <!-- Category & Verified -->
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap;">
          <span style="font-size:28px;filter:drop-shadow(0 2px 4px rgba(0,0,0,0.2));">${emoji}</span>
          <span style="font-size:12px;color:var(--ui-text-muted);padding:4px 10px;background:rgba(148,163,184,0.1);border-radius:999px;">${cats}</span>
          ${verifiedBadge}
        </div>
        
        <!-- Title -->
        <h3 style="margin:0 0 10px;font-size:20px;font-weight:800;line-height:1.3;color:var(--ui-text-main);">${escapeHtml(s.name || "")}</h3>
        ${ratingStars ? `
          <div style="display:flex;align-items:center;gap:4px;margin-bottom:6px;">
            ${'⭐'.repeat(Math.floor(parseFloat(s.rating)))}
            <span style="font-size:13px;color:#facc15;font-weight:600;">${s.rating}/5</span>
            <span style="font-size:11px;color:var(--ui-text-muted);">(${s.likes || 0} avis)</span>
        </div>
        ` : ''}
        <div style="font-size:13px;color:#1f2937;background:rgba(255,255,255,0.95);padding:6px 8px;border-radius:8px;margin-bottom:6px;font-weight:500;">
          📍 ${escapeHtml(s.address || s.city || "")}, Suisse
        </div>
        ${s.description ? `<div style="font-size:14px;color:#ffffff;margin-bottom:12px;line-height:1.7;padding:12px;background:transparent;border-radius:8px;">${escapeHtml(stripPhoneNumbers(s.description))}</div>` : ""}
        ${aiIndicator}
        ${hasPaidContact ? `
          <div style="margin:8px 0;padding:12px;background:linear-gradient(135deg,rgba(0,255,195,0.15),rgba(34,197,94,0.1));border:1px solid rgba(0,255,195,0.3);border-radius:10px;">
            <div style="font-size:12px;color:#00ffc3;font-weight:600;margin-bottom:8px;">✅ Contact</div>
            <div style="font-size:13px;color:#e5e7eb;">📧 ${s.email || 'contact@service.ch'}</div>
            ${s.website ? `<a href="${s.website}" target="_blank" style="display:inline-flex;align-items:center;gap:4px;font-size:12px;color:#3b82f6;margin-top:4px;">🌐 ${s.website}</a>` : ''}
            <div style="font-size:10px;color:var(--ui-text-muted);margin-top:6px;">📅 Ajouté à votre agenda permanent</div>
        </div>
        ` : `
          <div style="font-size:11px;color:#6b7280;margin:8px 0;padding:10px;background:rgba(107,114,128,0.1);border-radius:8px;">
            🔒 <strong>Masqué :</strong> Email, site web<br>
            <span style="font-size:10px;">Débloquez pour accéder aux coordonnées complètes</span>
          </div>
        `}
        <div class="popup-actions-sticky" style="position:sticky;bottom:0;background:var(--ui-card-bg);margin:12px -12px -12px -12px;padding:12px;z-index:10;border-top:1px solid rgba(148,163,184,0.2);">
          ${actionsRow}
        </div>
        ${!hasPaidContact ? `
          <button onclick="onBuyContact('service', ${s.id})" style="margin-top:10px;width:100%;padding:12px;border-radius:999px;border:none;cursor:pointer;font-size:14px;font-weight:700;background:var(--btn-main-bg);color:var(--btn-main-text);box-shadow:var(--btn-main-shadow);">
            💳 Débloquer contact + site – CHF 1.–
        </button>
        ` : ''}
      </div>
    </div>
  `;
}

// ============================================
