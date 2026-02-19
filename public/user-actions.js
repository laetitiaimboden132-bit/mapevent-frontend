// ============================================================
// user-actions.js
// Actions utilisateur (toggleLike, toggleFavorite, toggleAgenda, shareItem, inviteFriends)
// Extrait de map_logic.js (lignes 12466-14120)
// ============================================================

// ACTIONS UTILISATEUR - LIKE / PARTAGER / AGENDA
// ============================================
function onBuyContact(type, id) {
  if (!currentUser || !currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  openPaymentModal(type, id, "contact");
}

function onAction(action, type, id) {
  if (!currentUser.isLoggedIn && action !== "share") {
    openLoginModal();
    return;
  }

  switch(action) {
    case "like":
      toggleLike(type, id);
      break;
    case "favorite":
      toggleFavorite(type, id);
      break;
    case "participate":
      toggleParticipation(type, id);
      break;
    case "agenda":
      toggleAgenda(type, id);
      break;
    case "route":
      openRoute(type, id);
      break;
    case "avis":
      openReviewModal(type, id);
      break;
    case "share":
      shareItem(type, id);
      break;
    case "discussion":
      openDiscussionModal(type, id);
      break;
    case "report":
      openReportModal(type, id);
      break;
    default:
      console.log("Action non gérée:", action);
  }
}

// Toggle Like (juste le compteur, pas de sauvegarde)
async function toggleLike(type, id) {
  if (navigator.vibrate) navigator.vibrate(10);
  const key = `${type}:${id}`;
  const index = currentUser.likes.indexOf(key);
  
  const action = index > -1 ? 'remove' : 'add';
  
  // Appeler le backend
  try {
    const response = await fetch(`${window.API_BASE_URL}/user/likes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId: currentUser.id.toString(),
        itemId: id,
        itemMode: type,
        action: action
      })
    });
    
    if (response.ok) {
      if (action === 'add') {
        currentUser.likes.push(key);
        showNotification("👍 Like ajouté", "success");
      } else {
        currentUser.likes.splice(index, 1);
        showNotification("👎 Like retiré", "info");
      }
    }
  } catch (error) {
    console.error('Erreur toggleLike:', error);
    // Fallback local
    if (index > -1) {
      currentUser.likes.splice(index, 1);
      showNotification("👎 Like retiré", "info");
    } else {
      currentUser.likes.push(key);
      showNotification("👍 Like ajouté", "success");
    }
  }
  
  // Mettre à jour l'affichage
  updateItemLikes(type, id, action === 'add' ? 1 : -1);
  refreshMarkers();
  
  // Rafraîchir la popup si elle est ouverte
  const backdrop = document.getElementById("popup-modal-backdrop");
  if (backdrop && backdrop.style.display !== "none") {
    const data = type === "event" ? eventsData : type === "booking" ? bookingsData : servicesData;
    const item = data.find(i => i.id === parseInt(id));
    if (item) {
      let popupHtml = "";
      if (type === "event") {
        popupHtml = buildEventPopup(item);
      } else if (type === "booking") {
        popupHtml = buildBookingPopup(item);
      } else if (type === "service") {
        popupHtml = buildServicePopup(item);
      }
      if (popupHtml) {
        const scrollContainer = document.getElementById("popup-scroll-container");
        if (scrollContainer) {
          const scrollTop = scrollContainer.scrollTop; // Sauvegarder la position
          scrollContainer.innerHTML = popupHtml;
          scrollContainer.scrollTop = scrollTop; // Restaurer la position
        }
      }
    }
  }
}

// Toggle Favorite (sauvegarde dans "Mes favoris", pas dans l'agenda)
async function toggleFavorite(type, id) {
  if (navigator.vibrate) navigator.vibrate(10);
  const key = `${type}:${id}`;
  
  // Trouver l'item pour obtenir son nom
  const data = type === 'event' ? eventsData : type === 'booking' ? bookingsData : servicesData;
  const item = data.find(i => i.id === id);
  if (!item) return;
  
  const favoriteName = item.title || item.name;
  const favoriteMode = type;
  
  // Vérifier si déjà en favoris
  const existingFavorite = currentUser.favorites.find(f => 
    f.id === id.toString() && f.mode === type
  );
  
  const action = existingFavorite ? 'remove' : 'add';
  
  // Appeler le backend
  try {
    const response = await fetch(`${window.API_BASE_URL}/user/favorites`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId: currentUser.id.toString(),
        itemId: id,
        itemMode: type,
        action: action
      })
    });
    
    if (response.ok) {
      if (action === 'add') {
        // Ajouter aux favoris avec les infos nécessaires pour les alertes
        const favorite = {
          id: id.toString(),
          name: favoriteName,
          mode: favoriteMode,
          type: favoriteMode,
          lat: item.lat,
          lng: item.lng
        };
        currentUser.favorites.push(favorite);
        showNotification("⭐ Ajouté aux favoris !", "success");
      } else {
        // Retirer des favoris
        const index = currentUser.favorites.findIndex(f => 
          f.id === id.toString() && f.mode === type
        );
        if (index > -1) {
          currentUser.favorites.splice(index, 1);
        }
        showNotification("💔 Retiré des favoris", "info");
      }
      
      // Sauvegarder dans localStorage
      try {
        safeSetItem('currentUser', JSON.stringify(currentUser));
      } catch (e) {
        console.error('Erreur sauvegarde favoris:', e);
      }
    }
  } catch (error) {
    console.error('Erreur toggleFavorite:', error);
    // Fallback local
    if (existingFavorite) {
      const index = currentUser.favorites.findIndex(f => 
        f.id === id.toString() && f.mode === type
      );
      if (index > -1) {
        currentUser.favorites.splice(index, 1);
      }
      showNotification("💔 Retiré des favoris", "info");
    } else {
      const favorite = {
        id: id.toString(),
        name: favoriteName,
        mode: favoriteMode,
        type: favoriteMode,
        lat: item.lat,
        lng: item.lng
      };
      currentUser.favorites.push(favorite);
      showNotification("⭐ Ajouté aux favoris !", "success");
    }
  }
  
  refreshMarkers();
  
  // Rafraîchir la popup si elle est ouverte
  const backdrop = document.getElementById("popup-modal-backdrop");
  if (backdrop && backdrop.style.display !== "none") {
    if (item) {
      let popupHtml = "";
      if (type === "event") {
        popupHtml = buildEventPopup(item);
      } else if (type === "booking") {
        popupHtml = buildBookingPopup(item);
      } else if (type === "service") {
        popupHtml = buildServicePopup(item);
      }
      if (popupHtml) {
        const scrollContainer = document.getElementById("popup-scroll-container");
        if (scrollContainer) {
          const scrollTop = scrollContainer.scrollTop;
          scrollContainer.innerHTML = popupHtml;
          scrollContainer.scrollTop = scrollTop;
        }
      }
    }
  }
}

// Toggle Participation
function toggleParticipation(type, id) {
  // Vérifier si l'utilisateur est connecté
  if (!currentUser || !currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  
  const key = `${type}:${id}`;
  const index = currentUser.participating.indexOf(key);
  
  // Trouver l'item pour mettre à jour le compteur
  const data = type === "event" ? eventsData : type === "booking" ? bookingsData : servicesData;
  const item = data.find(i => i.id === parseInt(id));
  
  if (index > -1) {
    currentUser.participating.splice(index, 1);
    if (item) item.participants = Math.max(0, (item.participants || 0) - 1);
    showNotification("🚫 Participation annulée", "info");
  } else {
    currentUser.participating.push(key);
    if (item) item.participants = (item.participants || 0) + 1;
    // Ajouter aussi à l'agenda automatiquement
    if (!currentUser.agenda.includes(key)) {
      currentUser.agenda.push(key);
    }
    showNotification("✅ Participation confirmée ! Ajouté à votre agenda.", "success");
  }
  
  refreshMarkers();
  
  // Rafraîchir la popup si elle est ouverte
  const backdrop = document.getElementById("popup-modal-backdrop");
  if (backdrop && backdrop.style.display !== "none") {
    if (item) {
      let popupHtml = "";
      if (type === "event") {
        popupHtml = buildEventPopup(item);
      } else if (type === "booking") {
        popupHtml = buildBookingPopup(item);
      } else if (type === "service") {
        popupHtml = buildServicePopup(item);
      }
      if (popupHtml) {
        const scrollContainer = document.getElementById("popup-scroll-container");
        if (scrollContainer) {
          const scrollTop = scrollContainer.scrollTop; // Sauvegarder la position
          scrollContainer.innerHTML = popupHtml;
          scrollContainer.scrollTop = scrollTop; // Restaurer la position
        }
      }
    }
  }
  
  // Reconstruire la popup pour mettre à jour le compteur
  if (item) {
    const marker = markersLayer.getLayers().find(m => m.options.itemId === id && m.options.itemType === type);
    if (marker) {
      marker.bindPopup(buildPopupHtml(item), { maxWidth: 400 });
      // Réajouter le gestionnaire pour intercepter l'ouverture
      marker.off('popupopen'); // Retirer l'ancien gestionnaire s'il existe
      marker.on('popupopen', function() {
        marker.closePopup();
        // Stocker le marqueur pour le recentrage à la fermeture
        currentPopupMarker = marker;
        const popupContent = buildPopupHtml(item);
        openPopupModal(popupContent, item);
      });
    }
  }
}

// Toggle Agenda avec limite selon abonnement - PERSISTANT EN BASE DE DONNÉES
async function toggleAgenda(type, id) {
  // Vérifier si l'utilisateur est connecté
  if (!currentUser || !currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  
  const key = `${type}:${id}`;
  const index = currentUser.agenda.indexOf(key);
  const action = index > -1 ? 'remove' : 'add';
  
  // Vérifier limite AVANT d'appeler l'API (pour add)
  if (action === 'add') {
    const maxAgenda = getAgendaLimit();
    if (currentUser.agenda.length >= maxAgenda) {
      showNotification(`⚠️ Limite d'agenda atteinte (${maxAgenda} places). Retirez un événement ou passez à un abonnement supérieur pour plus de places !`, "warning");
      openSubscriptionModal();
      return;
    }
  }
  
  // Appeler l'API pour persister en base
  try {
    const response = await fetch(`${window.API_BASE_URL}/user/agenda`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId: currentUser.id.toString(),
        itemId: id,
        itemMode: type,
        action: action
      })
    });
    
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.error || 'Erreur API');
    }
  } catch (error) {
    console.error('[AGENDA] Erreur persistance:', error);
    showNotification("❌ Impossible de sauvegarder l'agenda. Réessayez.", "error");
    return;
  }
  
  if (index > -1) {
    currentUser.agenda.splice(index, 1);
    if (typeof saveUserData === 'function') saveUserData();
    try { localStorage.setItem('user_agenda_backup', JSON.stringify(currentUser.agenda)); } catch(e) {}
    showNotification("📅 Retiré de l'agenda", "info");
    refreshMarkers();
    refreshListView();
    // Rafraîchir la mini-fenêtre si elle est ouverte
    if (agendaMiniWindowOpen) {
      showAgendaMiniWindow();
    }
    
    // Rafraîchir la popup si elle est ouverte
    const backdrop = document.getElementById("popup-modal-backdrop");
    if (backdrop && backdrop.style.display !== "none") {
      const data = type === "event" ? eventsData : type === "booking" ? bookingsData : servicesData;
      const item = data.find(i => i.id === parseInt(id));
      if (item) {
        let popupHtml = "";
        if (type === "event") {
          popupHtml = buildEventPopup(item);
        } else if (type === "booking") {
          popupHtml = buildBookingPopup(item);
        } else if (type === "service") {
          popupHtml = buildServicePopup(item);
        }
        if (popupHtml) {
          const scrollContainer = document.getElementById("popup-scroll-container");
          if (scrollContainer) {
            const scrollTop = scrollContainer.scrollTop;
            scrollContainer.innerHTML = popupHtml;
            scrollContainer.scrollTop = scrollTop;
          }
        }
      }
    }
  } else {
    currentUser.agenda.push(key);
    if (typeof saveUserData === 'function') saveUserData();
    try { localStorage.setItem('user_agenda_backup', JSON.stringify(currentUser.agenda)); } catch(e) {}
    showNotification(`📅 Ajouté à votre agenda ! (${currentUser.agenda.length}/${maxAgenda})`, "success");
    refreshMarkers();
    refreshListView();
    // Afficher la mini-fenêtre agenda
    showAgendaMiniWindow();
    
    // Rafraîchir la popup si elle est ouverte
    const backdrop = document.getElementById("popup-modal-backdrop");
    if (backdrop && backdrop.style.display !== "none") {
      const data = type === "event" ? eventsData : type === "booking" ? bookingsData : servicesData;
      const item = data.find(i => i.id === parseInt(id));
      if (item) {
        let popupHtml = "";
        if (type === "event") {
          popupHtml = buildEventPopup(item);
        } else if (type === "booking") {
          popupHtml = buildBookingPopup(item);
        } else if (type === "service") {
          popupHtml = buildServicePopup(item);
        }
        if (popupHtml) {
          const scrollContainer = document.getElementById("popup-scroll-container");
          if (scrollContainer) {
            const scrollTop = scrollContainer.scrollTop;
            scrollContainer.innerHTML = popupHtml;
            scrollContainer.scrollTop = scrollTop;
          }
        }
      }
    }
  }
}

// Obtenir la limite d'agenda selon l'abonnement
function getAgendaLimit() {
  const sub = currentUser.subscription || "free";
  switch(sub) {
    case "events-explorer": return 50;
    case "events-alerts-pro": return 200;
    case "service-pro": return 100;
    case "service-ultra": return 200;
    case "full-premium": return 250;
    default: return 20; // Gratuit
  }
}

// Obtenir la limite d'alertes selon l'abonnement
function getAlertLimit() {
  const sub = currentUser.subscription || "free";
  switch(sub) {
    case "events-explorer": return Infinity; // Illimité avec abo
    case "events-alerts-pro": return 200; // Jusqu'à 200 alertes
    case "service-pro": return 0; // Pas d'alertes
    case "service-ultra": return 0; // Pas d'alertes
    case "full-premium": return Infinity; // Illimité
    default: return 2; // Gratuit = 2 alertes max
  }
}

// Obtenir la limite de SMS selon l'abonnement
function getSMSLimit() {
  const sub = currentUser.subscription || "free";
  switch(sub) {
    case "full-premium": return Infinity; // Illimité pour premium 25.-
    case "events-alerts-pro": return 10; // 10 SMS/mois
    case "events-explorer": return 10; // 10 SMS/mois
    default: return 0; // Gratuit = pas de SMS
  }
}

// Vérifier si l'utilisateur peut recevoir des SMS
function canSendSMS() {
  const limit = getSMSLimit();
  if (limit === 0) return false;
  if (limit === Infinity) return true;
  return currentUser.smsNotifications < limit;
}

// Vérifier les changements d'événements et envoyer des alertes
// ⚠️ LES ALERTES DE STATUT (annulé, complet, reporté) SONT TOUJOURS GRATUITES ET ILLIMITÉES
function checkEventChanges() {
  if (!isLoggedIn()) return;
  
  // Les alertes de statut sont GRATUITES pour TOUS - pas de limite !
  // C'est vital pour l'utilisateur de savoir si un event est annulé/complet/reporté
  
  // Initialiser les propriétés si elles sont undefined
  if (!currentUser.agenda) currentUser.agenda = [];
  if (!currentUser.participating) currentUser.participating = [];
  if (!currentUser.eventStatusHistory) currentUser.eventStatusHistory = {};
  
  // Vérifier tous les événements dans l'agenda ET dans participating de l'utilisateur
  const eventKeys = [...new Set([...currentUser.agenda, ...currentUser.participating])];
  
  eventKeys.forEach(key => {
    if (!key.startsWith('event:')) return;
    
    const eventId = parseInt(key.split(':')[1]);
    const event = eventsData.find(e => e.id === eventId);
    if (!event) return;
    
    const previousStatus = currentUser.eventStatusHistory[eventId] || event.status || 'OK';
    const currentStatus = event.status || 'OK';
    
    // Détecter un changement de statut
    if (previousStatus !== currentStatus) {
      // Mettre à jour l'historique
      currentUser.eventStatusHistory[eventId] = currentStatus;
      
      // Vérifier si c'est un changement important (reporté, annulé, etc.)
      const importantStatuses = ['REPORTÉ', 'REPORTE', 'ANNULE', 'ANNULÉ', 'COMPLET', 'SOLDOUT'];
      if (importantStatuses.includes(currentStatus)) {
        const statusText = currentStatus === 'REPORTÉ' || currentStatus === 'REPORTE' ? 'reporté' :
                          currentStatus === 'ANNULE' || currentStatus === 'ANNULÉ' ? 'annulé' :
                          currentStatus === 'COMPLET' || currentStatus === 'SOLDOUT' ? 'complet' : currentStatus;
        
        // Si l'utilisateur a participé à cet événement, stocker la notification pour l'afficher au login
        const hasParticipated = currentUser.participating.includes(key);
        if (hasParticipated) {
          // Vérifier si cette notification n'existe pas déjà
          const existingNotification = currentUser.pendingStatusNotifications.find(n => n.eventId === eventId);
          if (!existingNotification) {
            currentUser.pendingStatusNotifications.push({
              eventId: eventId,
              eventTitle: event.title,
              status: currentStatus,
              statusText: statusText,
              timestamp: new Date().toISOString()
            });
            saveUser();
          }
        }
        
        // Afficher une notification immédiate si l'utilisateur est connecté
        if (currentUser && currentUser.isLoggedIn) {
          showNotification(`🔔 Changement d'événement : "${event.title}" a été ${statusText}`, "warning");
        }
        
        // Si l'utilisateur a un abonnement avec notifications push/email, on pourrait aussi envoyer une notification push/email ici
        if (currentUser.subscription === 'events-alerts-pro' || currentUser.subscription === 'full-premium') {
          // Logique pour notifications push/email (à implémenter avec le backend)
          console.log(`📧 Notification push/email pour changement d'événement: ${event.title} - ${statusText}`);
        }
      }
    } else {
      // Initialiser l'historique si c'est la première fois qu'on vérifie cet événement
      if (!currentUser.eventStatusHistory[eventId]) {
        currentUser.eventStatusHistory[eventId] = currentStatus;
      }
    }
  });
}

// Initialiser l'historique des statuts au chargement
function initEventStatusHistory() {
  eventsData.forEach(ev => {
    if (!currentUser.eventStatusHistory[ev.id]) {
      currentUser.eventStatusHistory[ev.id] = ev.status || 'OK';
    }
  });
}

// Mettre à jour les likes d'un item
function updateItemLikes(type, id, delta) {
  let data = type === "event" ? eventsData : type === "booking" ? bookingsData : servicesData;
  const item = data.find(i => i.id === parseInt(id));
  if (item) {
    item.likes = (item.likes || 0) + delta;
  }
}

// Récupérer un item par son type et ID
function getItemById(type, id) {
  if (type === "event") {
    return eventsData.find(e => e.id === id);
  } else if (type === "booking") {
    return bookingsData.find(b => b.id === id);
  } else if (type === "service") {
    return servicesData.find(s => s.id === id);
  }
  return null;
}

// Inviter des amis à un événement/booking/service
function inviteFriendsToEvent(type, id) {
  if (!currentUser || !currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  
  const item = getItemById(type, id);
  if (!item) return;
  
  // Utiliser le nouveau système d'invitation par API
  openInviteFriendsModal(type, id, item.title || item.name || 'Événement');
  return;
  
  // --- Ancien code local ci-dessous (désactivé) ---
  const friendsList = currentUser.friends || [];
  if (friendsList.length === 0) {
    showNotification("👥 Vous n'avez pas encore d'amis. Ajoutez-en depuis le menu Amis !", "info");
    openFriendsModal();
    return;
  }
  
  initDemoUsers();
  const friendsInfo = friendsList.map(friendId => {
    return allUsers.find(u => u.id === friendId) || { id: friendId, name: 'Ami', avatar: '👤' };
  });
  
  const itemTitle = item.title || item.name || 'Élément';
  const itemTypeLabel = type === 'event' ? 'événement' : type === 'booking' ? 'artiste' : 'service';
  
  const html = `
    <div style="padding:20px;max-width:550px;margin:0 auto;max-height:85vh;overflow-y:auto;">
      <div style="text-align:center;margin-bottom:20px;">
        <div style="font-size:40px;margin-bottom:8px;">➕</div>
        <h2 style="margin:0;font-size:22px;font-weight:700;color:#fff;">Inviter des amis</h2>
        <p style="color:var(--ui-text-muted);margin-top:6px;font-size:13px;">${escapeHtml(itemTitle)}</p>
      </div>
      
      <div style="margin-bottom:16px;">
        <label style="display:block;font-size:13px;font-weight:600;color:#fff;margin-bottom:8px;">🔍 Rechercher un ami</label>
        <input type="text" id="invite-search-friends" placeholder="Nom d'ami..." 
               onkeyup="filterInviteFriends(this.value)"
               style="width:100%;padding:12px;border-radius:10px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:14px;">
      </div>
      
      <div id="invite-friends-list" style="display:flex;flex-direction:column;gap:8px;margin-bottom:20px;">
        ${friendsInfo.map(friend => `
          <div id="invite-friend-${friend.id}" style="display:flex;align-items:center;gap:12px;padding:12px;background:rgba(15,23,42,0.5);border-radius:12px;border:1px solid var(--ui-card-border);">
            <div style="width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:24px;">${friend.avatar}</div>
            <div style="flex:1;">
              <div style="font-weight:600;font-size:14px;color:#fff;">${escapeHtml(friend.name)}</div>
              <div style="font-size:11px;color:var(--ui-text-muted);">${friend.isOnline ? '🟢 En ligne' : '⚫ Hors ligne'}</div>
            </div>
            <button onclick="sendInvitationToFriend('${friend.id}', '${escapeHtml(friend.name)}', '${friend.avatar}', '${type}', ${id})" 
                    style="padding:8px 14px;border-radius:8px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-size:12px;font-weight:600;cursor:pointer;">
              Inviter
            </button>
          </div>
        `).join('')}
      </div>
      
      <button onclick="closePublishModal()" style="width:100%;padding:12px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-weight:600;">
        Fermer
      </button>
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

  // L'event listener pour le bouton d'inscription est maintenant attaché dans openLoginModal après la création du HTML
}

// Filtrer les amis lors de l'invitation
function filterInviteFriends(query) {
  const friendsList = currentUser.friends || [];
  initDemoUsers();
  
  const filtered = friendsList
    .map(friendId => allUsers.find(u => u.id === friendId))
    .filter(friend => {
      if (!friend) return false;
      if (!query || query.trim() === '') return true;
      return friend.name.toLowerCase().includes(query.toLowerCase());
    });
  
  const container = document.getElementById("invite-friends-list");
  if (!container) return;
  
  container.innerHTML = filtered.map(friend => `
    <div id="invite-friend-${friend.id}" style="display:flex;align-items:center;gap:12px;padding:12px;background:rgba(15,23,42,0.5);border-radius:12px;border:1px solid var(--ui-card-border);">
      <div style="width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:24px;">${friend.avatar}</div>
      <div style="flex:1;">
        <div style="font-weight:600;font-size:14px;color:#fff;">${escapeHtml(friend.name)}</div>
        <div style="font-size:11px;color:var(--ui-text-muted);">${friend.isOnline ? '🟢 En ligne' : '⚫ Hors ligne'}</div>
      </div>
      <button onclick="sendInvitationToFriend('${friend.id}', '${escapeHtml(friend.name)}', '${friend.avatar}', 'event', 0)" 
              style="padding:8px 14px;border-radius:8px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-size:12px;font-weight:600;cursor:pointer;">
        Inviter
      </button>
    </div>
  `).join('');
}

// Envoyer une invitation à un ami
function sendInvitationToFriend(friendId, friendName, friendAvatar, type, id) {
  const item = getItemById(type, id);
  if (!item) return;
  
  const itemTitle = item.title || item.name || 'Élément';
  const itemTypeLabel = type === 'event' ? 'événement' : type === 'booking' ? 'artiste' : 'service';
  
  // Créer une alerte sociale pour l'ami
  if (!window.userAlerts) window.userAlerts = {};
  if (!window.userAlerts[friendId]) window.userAlerts[friendId] = [];
  
  window.userAlerts[friendId].push({
    type: 'event_invitation',
    fromUserId: currentUser.id,
    fromUserName: currentUser.name,
    fromUserAvatar: currentUser.avatar,
    eventType: type,
    eventId: id,
    eventTitle: itemTitle,
    message: `${currentUser.name} vous invite à découvrir cet ${itemTypeLabel}`,
    date: new Date().toISOString(),
    read: false,
    icon: '🎉'
  });
  
  showNotification(`✅ Invitation envoyée à ${friendName} !`, "success");
  
  // Mettre à jour le bouton
  const button = document.querySelector(`#invite-friend-${friendId} button`);
  if (button) {
    button.textContent = '✅ Invité';
    button.style.background = '#22c55e';
    button.disabled = true;
  }
}

// Ouvrir le profil utilisateur complet
function openUserProfile(userId = null) {
  if (!currentUser.isLoggedIn && !userId) {
    openLoginModal();
    return;
  }
  
  const targetUserId = userId || currentUser.id;
  const isOwnProfile = targetUserId === currentUser.id;
  
  initDemoUsers();
  const targetUser = allUsers.find(u => u.id === targetUserId) || currentUser;
  
  const profilePhotos = targetUser.profilePhotos || [];
  const profileVideos = targetUser.profileVideos || [];
  const bio = targetUser.bio || '';
  const friendsCount = targetUser.friends?.length || 0;
  const eventsCount = targetUser.participating?.filter(p => p.startsWith('event:')).length || 0;
  
  const html = `
    <div style="padding:20px;max-width:700px;margin:0 auto;max-height:85vh;overflow-y:auto;">
      <!-- Header du profil -->
      <div style="text-align:center;margin-bottom:24px;padding-bottom:20px;border-bottom:1px solid var(--ui-card-border);">
        <div style="width:120px;height:120px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:60px;margin:0 auto 16px;border:4px solid rgba(0,255,195,0.3);overflow:hidden;position:relative;">
          ${(() => {
            const avatarUrl = targetUser.profile_photo_url || targetUser.profilePhoto || targetUser.avatarUrl || targetUser.avatar;
            if (avatarUrl && (avatarUrl.startsWith('http') || avatarUrl.startsWith('data:image'))) {
              return `<img src="${avatarUrl}" style="width:100%;height:100%;object-fit:cover;position:absolute;top:0;left:0;" onerror="this.style.display='none';this.parentElement.innerHTML='${targetUser.avatar || '👤'}';this.parentElement.style.fontSize='60px';" />`;
            }
            return targetUser.avatar || '👤';
          })()}
        </div>
        <h2 style="margin:0 0 8px;font-size:28px;font-weight:700;color:#fff;">${escapeHtml(targetUser.name)}</h2>
        ${targetUser.firstName && targetUser.lastName ? `
          <div style="font-size:14px;color:var(--ui-text-muted);margin-bottom:12px;">
            ${escapeHtml(targetUser.firstName)} ${escapeHtml(targetUser.lastName)}
          </div>
        ` : ''}
        ${bio ? `<div style="font-size:14px;color:var(--ui-text-main);line-height:1.6;max-width:500px;margin:0 auto;">${escapeHtml(bio)}</div>` : ''}
        
        ${isOwnProfile ? `
          <button onclick="editProfile()" style="margin-top:16px;padding:10px 20px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);font-weight:600;cursor:pointer;">
            ✏️ Modifier le profil
          </button>
        ` : `
          <div style="display:flex;gap:8px;justify-content:center;margin-top:16px;">
            ${currentUser.friends?.includes(targetUserId) ? `
              <button onclick="openChatWith('${targetUserId}')" style="padding:10px 20px;border-radius:999px;border:none;background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff;font-weight:600;cursor:pointer;">
                💬 Message
              </button>
            ` : `
              <button onclick="sendFriendRequest('${targetUserId}', '${escapeHtml(targetUser.name)}', '${targetUser.avatar}')" style="padding:10px 20px;border-radius:999px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:600;cursor:pointer;">
                ➕ Ajouter comme ami
              </button>
            `}
          </div>
        `}
      </div>
      
      <!-- Stats -->
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:24px;">
        <div style="text-align:center;padding:16px;background:rgba(15,23,42,0.5);border-radius:12px;border:1px solid var(--ui-card-border);">
          <div style="font-size:24px;font-weight:700;color:#00ffc3;">${friendsCount}</div>
          <div style="font-size:12px;color:var(--ui-text-muted);margin-top:4px;">Amis</div>
        </div>
        <div style="text-align:center;padding:16px;background:rgba(15,23,42,0.5);border-radius:12px;border:1px solid var(--ui-card-border);">
          <div style="font-size:24px;font-weight:700;color:#3b82f6;">${eventsCount}</div>
          <div style="font-size:12px;color:var(--ui-text-muted);margin-top:4px;">Événements</div>
        </div>
        <div style="text-align:center;padding:16px;background:rgba(15,23,42,0.5);border-radius:12px;border:1px solid var(--ui-card-border);">
          <div style="font-size:24px;font-weight:700;color:#f59e0b;">${(targetUser.likes || []).length}</div>
          <div style="font-size:12px;color:var(--ui-text-muted);margin-top:4px;">Likes</div>
        </div>
      </div>
      
      <!-- Photos -->
      ${profilePhotos.length > 0 ? `
        <div style="margin-bottom:24px;">
          <h3 style="margin:0 0 12px 0;font-size:18px;font-weight:600;color:#fff;">📸 Photos</h3>
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;">
            ${profilePhotos.slice(0, 9).map(photo => `
              <div style="aspect-ratio:1;border-radius:12px;overflow:hidden;background:rgba(15,23,42,0.5);border:1px solid var(--ui-card-border);cursor:pointer;"
                   onclick="viewPhoto('${photo}')">
                <img src="${photo}" style="width:100%;height:100%;object-fit:cover;" onerror="this.style.display='none'">
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}
      
      <!-- Vidéos -->
      ${profileVideos.length > 0 ? `
        <div style="margin-bottom:24px;">
          <h3 style="margin:0 0 12px 0;font-size:18px;font-weight:600;color:#fff;">🎥 Vidéos</h3>
          <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:8px;">
            ${profileVideos.slice(0, 4).map(video => `
              <div style="aspect-ratio:16/9;border-radius:12px;overflow:hidden;background:rgba(15,23,42,0.5);border:1px solid var(--ui-card-border);cursor:pointer;position:relative;"
                   onclick="viewVideo('${video}')">
                <img src="${video.thumbnail || ''}" style="width:100%;height:100%;object-fit:cover;" onerror="this.style.display='none'">
                <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:48px;height:48px;border-radius:50%;background:rgba(0,0,0,0.7);display:flex;align-items:center;justify-content:center;font-size:24px;">▶️</div>
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}
      
      <button onclick="closePublishModal()" style="width:100%;padding:12px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-weight:600;">
        Fermer
      </button>
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
}

// Modifier le profil
function editProfile() {
  const html = `
    <div style="padding:24px;max-width:500px;margin:0 auto;max-height:85vh;overflow-y:auto;">
      <h2 style="margin:0 0 20px 0;font-size:22px;font-weight:700;color:#fff;">Modifier le profil</h2>
      
      <div style="margin-bottom:16px;">
        <label style="display:block;font-size:14px;font-weight:600;color:#fff;margin-bottom:8px;">Bio</label>
        <textarea id="edit-profile-bio" placeholder="Décrivez-vous..." rows="4"
                  style="width:100%;padding:12px;border-radius:10px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:14px;resize:none;">${currentUser.bio || ''}</textarea>
      </div>
      
      <div style="margin-bottom:20px;">
        <label style="display:block;font-size:14px;font-weight:600;color:#fff;margin-bottom:8px;">Photos (URLs, une par ligne)</label>
        <textarea id="edit-profile-photos" placeholder="https://exemple.com/photo1.jpg&#10;https://exemple.com/photo2.jpg" rows="3"
                  style="width:100%;padding:12px;border-radius:10px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:14px;resize:none;">${(currentUser.profilePhotos || []).join('\\n')}</textarea>
      </div>
      
      <div style="display:flex;gap:12px;">
        <button onclick="openUserProfile()" style="flex:1;padding:12px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-weight:600;">
          Annuler
        </button>
        <button onclick="saveProfile()" style="flex:1;padding:12px;border-radius:999px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:700;cursor:pointer;">
          Enregistrer
        </button>
      </div>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
}

// Gérer l'upload de photo dans le formulaire de modification
window.handleEditProfilePhotoUpload = function(event) {
  const file = event.target.files[0];
  if (!file) return;
  
  if (file.size > 5 * 1024 * 1024) {
    showNotification('⚠️ La photo doit faire moins de 5MB', 'warning');
    return;
  }
  
  const reader = new FileReader();
  reader.onload = function(e) {
    const previewContainer = document.getElementById('edit-profile-photo-preview-container');
    const previewImg = document.getElementById('edit-profile-photo-preview');
    
    if (previewImg) {
      previewImg.src = e.target.result;
    }
    if (previewContainer) {
      previewContainer.style.display = 'block';
    }
    
    // Stocker temporairement la photo pour l'upload
    window.editProfilePhotoFile = file;
  };
  reader.readAsDataURL(file);
};

// Configurer l'autocomplete d'adresse pour le formulaire de modification
function setupEditProfileAddressAutocomplete(inputElement) {
  let timeout;
  const suggestionsContainer = document.getElementById('edit-profile-address-suggestions');
  const selectedDisplay = document.getElementById('edit-profile-selected-address-display');
  const selectedLabel = document.getElementById('edit-profile-selected-address-label');
  const selectedDetails = document.getElementById('edit-profile-selected-address-details');
  
  inputElement.addEventListener('input', function(e) {
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
            <div class="edit-profile-address-suggestion" style="padding:12px;cursor:pointer;border-bottom:1px solid rgba(255,255,255,0.1);transition:background 0.2s;" 
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
          
          suggestionsContainer.querySelectorAll('.edit-profile-address-suggestion').forEach(suggestion => {
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
              
              window.editProfileSelectedAddress = addressData;
              
              if (inputElement) {
                inputElement.value = addressData.label;
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
                selectedDetails.textContent = `${addressData.city || ''} ${addressData.postcode || ''} ${addressData.country_code || ''}`.trim();
              }
            });
          });
        } else if (suggestionsContainer) {
          suggestionsContainer.style.display = 'none';
        }
      } catch (error) {
        console.error('[EDIT PROFILE] Erreur autocomplete adresse:', error);
      }
    }, 300);
  });
}

// Sauvegarder le profil
async function saveProfile() {
  const username = document.getElementById("edit-profile-username")?.value.trim() || '';
  const bio = document.getElementById("edit-profile-bio")?.value.trim() || '';
  const photosText = document.getElementById("edit-profile-photos")?.value.trim() || '';
  const photos = photosText.split('\n').filter(url => url.trim() && url.startsWith('http'));
  
  // Upload de la nouvelle photo si présente
  if (window.editProfilePhotoFile) {
    try {
      await uploadProfilePhoto(window.editProfilePhotoFile);
      showNotification("✅ Photo de profil mise à jour !", "success");
    } catch (error) {
      console.error('[EDIT PROFILE] Erreur upload photo:', error);
      showNotification("⚠️ Erreur lors de l'upload de la photo", "error");
    }
  }
  
  // Sauvegarder l'adresse si modifiée
  if (window.editProfileSelectedAddress) {
    try {
      await saveUserAddress(window.editProfileSelectedAddress);
    } catch (error) {
      console.error('[EDIT PROFILE] Erreur sauvegarde adresse:', error);
      showNotification("⚠️ Erreur lors de la sauvegarde de l'adresse", "error");
    }
  }
  
  // Mettre à jour le nom d'utilisateur si modifié
  if (username && username !== currentUser.username) {
    try {
      const response = await fetch(`${window.API_BASE_URL}/user/profile-settings`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify({ username })
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.user) {
          currentUser.username = data.user.username;
        }
      } else {
        const errorData = await response.json();
        if (errorData.error && errorData.error.includes('déjà pris')) {
          showNotification("⚠️ Ce nom d'utilisateur est déjà pris", "error");
          return;
        }
      }
    } catch (error) {
      console.error('[EDIT PROFILE] Erreur mise à jour username:', error);
    }
  }
  
  // Vérifier l'âge des photos (simulation - en production, utiliser une API de modération)
  const photosFiltered = photos.filter(photo => {
    return true; // Pour l'instant, on accepte tout
  });
  
  currentUser.bio = bio;
  currentUser.profilePhotos = photosFiltered;
  
  // Recharger les données utilisateur depuis l'API
  await loadCurrentUserFromAPI();
  
  saveUserData();
  showNotification("✅ Profil mis à jour !", "success");
  openUserProfile();
}

// Voir une photo en grand
function viewPhoto(photoUrl) {
  const html = `
    <div style="padding:20px;text-align:center;">
      <img src="${photoUrl}" style="max-width:100%;max-height:70vh;border-radius:12px;box-shadow:0 20px 60px rgba(0,0,0,0.5);">
      <button onclick="closePublishModal()" style="margin-top:20px;padding:12px 24px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-weight:600;">
        Fermer
      </button>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
}

// Voir une vidéo
function viewVideo(videoUrl) {
  const html = `
    <div style="padding:20px;text-align:center;">
      <video controls style="max-width:100%;max-height:70vh;border-radius:12px;box-shadow:0 20px 60px rgba(0,0,0,0.5);">
        <source src="${videoUrl}" type="video/mp4">
        Votre navigateur ne supporte pas la lecture de vidéos.
      </video>
      <button onclick="closePublishModal()" style="margin-top:20px;padding:12px 24px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-weight:600;">
        Fermer
      </button>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
}

// Itinéraire direct
function openRoute(type, id) {
  const item = getItemById(type, id);
  if (!item) return;
  
  const address = item.address || `${item.lat},${item.lng}`;
  const encodedAddress = encodeURIComponent(address);
  
  // Ouvrir Google Maps avec l'itinéraire
  const url = `https://www.google.com/maps/dir/?api=1&destination=${encodedAddress}`;
  window.open(url, '_blank');
  
  showNotification("🗺️ Itinéraire ouvert dans Google Maps", "success");
}

// Partager
function shareItem(type, id) {
  // Récupérer les infos de l'item
  // Cette fonction fonctionne pour TOUS les types d'événements :
  // - Événements de test
  // - Événements réels
  // - Événements générés par IA
  // - Bookings
  // - Services
  let item = null;
  let title = "Découvrez cet événement sur MapEvent !";
  
  if (type === "event") {
    item = eventsData.find(e => e.id === id);
    if (item) {
      // Utiliser le titre de l'événement (fonctionne pour test, réel, AI)
      title = item.title || item.name || title;
    }
  } else if (type === "booking") {
    item = bookingsData.find(b => b.id === id);
    if (item) title = item.title || item.name || title;
  } else if (type === "service") {
    item = servicesData.find(s => s.id === id);
    if (item) title = item.title || item.name || title;
  }
  
  // Mettre à jour les métadonnées Open Graph pour le partage
  // Ces métadonnées seront utilisées par Facebook, Twitter, LinkedIn, etc.
  if (item) {
    updateOpenGraphMetadata(type, id, item);
    console.log(`✅ Partage de ${type} ${id}: "${title}"`);
  } else {
    console.warn(`⚠️ ${type} ${id} non trouvé pour le partage`);
  }
  
  shareItemModal(type, id, item, title);
}

// Mettre à jour les métadonnées Open Graph pour le partage social
function updateOpenGraphMetadata(type, id, item) {
  const baseUrl = window.location.origin + window.location.pathname;
  const shareUrl = `${baseUrl}?${type}=${id}`;
  
  // Obtenir l'image de l'événement
  const imageCandidates = getImageCandidatesForItem(item);
  let imageUrl = imageCandidates[0] || OVERLAY_IMAGES.DEFAULT;
  
  // S'assurer que l'URL de l'image est absolue et complète
  if (!imageUrl.startsWith('http')) {
    // Si l'URL est relative, la rendre absolue
    if (imageUrl.startsWith('/')) {
      imageUrl = window.location.origin + imageUrl;
    } else {
      imageUrl = window.location.origin + '/' + imageUrl;
    }
  }
  
  // Obtenir la description optimisée pour les réseaux sociaux
  let description = '';
  if (item.description) {
    description = item.description.length > 200 
      ? item.description.substring(0, 197) + '...' 
      : item.description;
  } else {
    const dateStr = item.startDate 
      ? new Date(item.startDate).toLocaleDateString('fr-FR', { 
          weekday: 'long', 
          day: 'numeric', 
          month: 'long',
          year: 'numeric'
        })
      : '';
    const locationStr = item.city || item.address || 'Suisse';
    description = `${dateStr ? dateStr + ' - ' : ''}${locationStr} | Découvrez cet événement sur MapEvent`;
  }
  
  // Créer un titre optimisé avec le titre de l'événement en premier
  // Fonctionne pour TOUS les types d'événements : test, réel, AI, etc.
  const eventTitle = item.title || item.name || 'Événement';
  // Le titre doit être le titre de l'événement uniquement (sans suffixe)
  // Cela fonctionne pour les événements de test ET les vrais événements
  const title = eventTitle.trim(); // Titre principal = titre de l'événement uniquement
  
  // Description enrichie avec date et lieu pour plus de contexte
  let enrichedDescription = description;
  if (item.startDate) {
    const dateStr = new Date(item.startDate).toLocaleDateString('fr-FR', { 
      weekday: 'long', 
      day: 'numeric', 
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
    const locationStr = item.city || item.address || '';
    if (locationStr) {
      enrichedDescription = `${dateStr} - ${locationStr}${description ? ' | ' + description : ''}`;
    } else {
      enrichedDescription = `${dateStr}${description ? ' | ' + description : ''}`;
    }
  }
  
  // Mettre à jour les métadonnées Open Graph (Facebook, LinkedIn, etc.)
  // IMPORTANT: Ces métadonnées fonctionnent pour TOUS les types d'événements
  // (test, réel, AI, etc.) car elles utilisent les propriétés standard (title, description, etc.)
  updateMetaTag('og:url', shareUrl);
  updateMetaTag('og:title', title);
  updateMetaTag('og:description', enrichedDescription);
  updateMetaTag('og:image', imageUrl);
  updateMetaTag('og:image:width', '1200');
  updateMetaTag('og:image:height', '630');
  updateMetaTag('og:image:type', 'image/jpeg');
  updateMetaTag('og:type', 'website');
  updateMetaTag('og:site_name', 'MapEvent');
  updateMetaTag('og:locale', 'fr_FR');
  
  // Log pour debug (peut être retiré en production)
  console.log(`📱 Métadonnées Open Graph mises à jour:`, {
    title: title,
    description: enrichedDescription.substring(0, 50) + '...',
    image: imageUrl.substring(0, 50) + '...',
    url: shareUrl
  });
  
  // Mettre à jour les métadonnées Twitter Card
  updateMetaTag('twitter:url', shareUrl);
  updateMetaTag('twitter:title', title);
  updateMetaTag('twitter:description', enrichedDescription);
  updateMetaTag('twitter:image', imageUrl);
  updateMetaTag('twitter:card', 'summary_large_image');
  updateMetaTag('twitter:site', '@mapevent');
  
  // Mettre à jour la meta description standard
  updateMetaTag('description', enrichedDescription, 'name');
  
  // Mettre à jour le titre de la page avec le titre de l'événement
  document.title = title;
  
  // Ajouter aussi un meta title pour certains réseaux sociaux
  updateMetaTag('title', title, 'name');
  
  // Ajouter un lien canonique pour éviter les doublons
  let canonical = document.querySelector('link[rel="canonical"]');
  if (!canonical) {
    canonical = document.createElement('link');
    canonical.setAttribute('rel', 'canonical');
    document.head.appendChild(canonical);
  }
  canonical.setAttribute('href', shareUrl);
}

// Fonction utilitaire pour mettre à jour les métadonnées
function updateMetaTag(property, content, attribute = 'property') {
  let meta = document.querySelector(`meta[${attribute}="${property}"]`);
  if (!meta) {
    meta = document.createElement('meta');
    meta.setAttribute(attribute, property);
    document.head.appendChild(meta);
  }
  meta.setAttribute('content', content);
}

// Vérifier les paramètres URL et mettre à jour les métadonnées Open Graph
function checkUrlParamsAndUpdateMetadata() {
  const urlParams = new URLSearchParams(window.location.search);
  const eventId = urlParams.get('event');
  const bookingId = urlParams.get('booking');
  const serviceId = urlParams.get('service');
  
  // Fonction pour essayer de mettre à jour les métadonnées
  function tryUpdateMetadata(maxAttempts = 15) {
    let attempts = 0;
    const checkInterval = setInterval(() => {
      attempts++;
      let item = null;
      let type = null;
      let id = null;
      
      if (eventId && eventsData && eventsData.length > 0) {
        item = eventsData.find(e => e.id === parseInt(eventId));
        type = 'event';
        id = parseInt(eventId);
      } else if (bookingId && bookingsData && bookingsData.length > 0) {
        item = bookingsData.find(b => b.id === parseInt(bookingId));
        type = 'booking';
        id = parseInt(bookingId);
      } else if (serviceId && servicesData && servicesData.length > 0) {
        item = servicesData.find(s => s.id === parseInt(serviceId));
        type = 'service';
        id = parseInt(serviceId);
      }
      
      if (item && type && id) {
        clearInterval(checkInterval);
        console.log(`✅ Mise à jour des métadonnées Open Graph pour ${type} ${id}`);
        updateOpenGraphMetadata(type, id, item);
      } else if (attempts >= maxAttempts) {
        clearInterval(checkInterval);
        console.warn(`⚠️ Impossible de mettre à jour les métadonnées après ${maxAttempts} tentatives`);
      }
    }, 300); // Vérifier toutes les 300ms
  }
  
  // Commencer immédiatement
  tryUpdateMetadata();
}

window.checkUrlParamsAndUpdateMetadata = checkUrlParamsAndUpdateMetadata;
window.updateOpenGraphMetadata = updateOpenGraphMetadata;
window.updateMetaTag = updateMetaTag;

// Fonction pour créer le modal de partage (séparée pour réutilisation)
function shareItemModal(type, id, item, title) {
  
  // URL de partage via l'API pour que les crawlers sociaux (Facebook, Twitter) voient les bonnes meta OG
  const shareUrl = `${window.API_BASE_URL}/share/${type}/${id}`;
  // URL directe pour le clipboard et le navigateur
  const url = shareUrl;

  // Sur mobile, essayer l'API Web Share native (menu système du téléphone)
  const isMobile = window.innerWidth <= 768 || /Mobi|Android|iPhone|iPad/i.test(navigator.userAgent);
  if (isMobile && navigator.share) {
    navigator.share({
      title: title || 'MapEvent',
      text: title + ' — sur MapEvent',
      url: url
    }).catch(function() { /* utilisateur a annulé, pas d'erreur */ });
    return;
  }

  const text = encodeURIComponent(title);
  const encodedUrl = encodeURIComponent(url);
  
  // Mettre à jour les métadonnées Open Graph avant le partage
  // IMPORTANT: Les métadonnées doivent être mises à jour AVANT que l'utilisateur clique sur le bouton de partage
  // pour que les scrapers des réseaux sociaux les détectent correctement
  if (item) {
    updateOpenGraphMetadata(type, id, item);
    
    // Afficher une notification pour informer l'utilisateur
    showNotification("📱 Métadonnées mises à jour pour le partage social", "info");
  }
  
  // Créer le modal de partage professionnel
  const shareModal = document.createElement('div');
  shareModal.id = 'share-modal';
  shareModal.dataset.type = type;
  shareModal.dataset.id = String(id);
  shareModal.innerHTML = `
    <div style="position:fixed;inset:0;background:rgba(0,0,0,0.8);backdrop-filter:blur(8px);z-index:99999;display:flex;align-items:center;justify-content:center;" onclick="closeShareModal(event)">
      <div style="background:var(--ui-card-bg, #1a1a2e);border-radius:20px;padding:24px;max-width:400px;width:90%;box-shadow:0 25px 50px rgba(0,0,0,0.5);border:1px solid var(--ui-card-border, rgba(255,255,255,0.1));" onclick="event.stopPropagation()">
        
        <div style="text-align:center;margin-bottom:20px;">
          <h3 style="margin:0 0 8px 0;font-size:20px;font-weight:700;color:var(--ui-text-main, #fff);">🔗 Partager</h3>
          <p style="margin:0;font-size:13px;color:var(--ui-text-muted, #94a3b8);max-width:280px;margin:0 auto;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(title)}</p>
        </div>
        
        <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:12px;margin-bottom:20px;">
          
          <!-- Facebook -->
          <a href="https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}" target="_blank" rel="noopener" 
             style="display:flex;flex-direction:column;align-items:center;gap:8px;padding:16px 12px;border-radius:12px;background:rgba(24,119,242,0.15);border:1px solid rgba(24,119,242,0.3);text-decoration:none;transition:all 0.2s;"
             onmouseover="this.style.background='rgba(24,119,242,0.25)';this.style.transform='scale(1.05)'"
             onmouseout="this.style.background='rgba(24,119,242,0.15)';this.style.transform='scale(1)'">
            <span style="font-size:28px;">📘</span>
            <span style="font-size:11px;font-weight:600;color:#1877f2;">Facebook</span>
          </a>
          
          <!-- WhatsApp -->
          <a href="https://api.whatsapp.com/send?text=${text}%20${encodedUrl}" target="_blank" rel="noopener"
             style="display:flex;flex-direction:column;align-items:center;gap:8px;padding:16px 12px;border-radius:12px;background:rgba(37,211,102,0.15);border:1px solid rgba(37,211,102,0.3);text-decoration:none;transition:all 0.2s;"
             onmouseover="this.style.background='rgba(37,211,102,0.25)';this.style.transform='scale(1.05)'"
             onmouseout="this.style.background='rgba(37,211,102,0.15)';this.style.transform='scale(1)'">
            <span style="font-size:28px;">💬</span>
            <span style="font-size:11px;font-weight:600;color:#25d366;">WhatsApp</span>
          </a>
          
          <!-- Twitter/X -->
          <a href="https://twitter.com/intent/tweet?text=${text}&url=${encodedUrl}" target="_blank" rel="noopener"
             style="display:flex;flex-direction:column;align-items:center;gap:8px;padding:16px 12px;border-radius:12px;background:rgba(29,155,240,0.15);border:1px solid rgba(29,155,240,0.3);text-decoration:none;transition:all 0.2s;"
             onmouseover="this.style.background='rgba(29,155,240,0.25)';this.style.transform='scale(1.05)'"
             onmouseout="this.style.background='rgba(29,155,240,0.15)';this.style.transform='scale(1)'">
            <span style="font-size:28px;">🐦</span>
            <span style="font-size:11px;font-weight:600;color:#1d9bf0;">Twitter</span>
          </a>
          
          <!-- Telegram -->
          <a href="https://t.me/share/url?url=${encodedUrl}&text=${text}" target="_blank" rel="noopener"
             style="display:flex;flex-direction:column;align-items:center;gap:8px;padding:16px 12px;border-radius:12px;background:rgba(0,136,204,0.15);border:1px solid rgba(0,136,204,0.3);text-decoration:none;transition:all 0.2s;"
             onmouseover="this.style.background='rgba(0,136,204,0.25)';this.style.transform='scale(1.05)'"
             onmouseout="this.style.background='rgba(0,136,204,0.15)';this.style.transform='scale(1)'">
            <span style="font-size:28px;">✈️</span>
            <span style="font-size:11px;font-weight:600;color:#0088cc;">Telegram</span>
          </a>
          
          <!-- LinkedIn -->
          <a href="https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}" target="_blank" rel="noopener"
             style="display:flex;flex-direction:column;align-items:center;gap:8px;padding:16px 12px;border-radius:12px;background:rgba(10,102,194,0.15);border:1px solid rgba(10,102,194,0.3);text-decoration:none;transition:all 0.2s;"
             onmouseover="this.style.background='rgba(10,102,194,0.25)';this.style.transform='scale(1.05)'"
             onmouseout="this.style.background='rgba(10,102,194,0.15)';this.style.transform='scale(1)'">
            <span style="font-size:28px;">💼</span>
            <span style="font-size:11px;font-weight:600;color:#0a66c2;">LinkedIn</span>
          </a>
          
          <!-- Email -->
          <a href="mailto:?subject=${text}&body=${text}%20-%20${encodedUrl}" 
             style="display:flex;flex-direction:column;align-items:center;gap:8px;padding:16px 12px;border-radius:12px;background:rgba(234,88,12,0.15);border:1px solid rgba(234,88,12,0.3);text-decoration:none;transition:all 0.2s;"
             onmouseover="this.style.background='rgba(234,88,12,0.25)';this.style.transform='scale(1.05)'"
             onmouseout="this.style.background='rgba(234,88,12,0.15)';this.style.transform='scale(1)'">
            <span style="font-size:28px;">📧</span>
            <span style="font-size:11px;font-weight:600;color:#ea580c;">Email</span>
          </a>
          
        </div>
        
        <!-- Partager en Story (image 1080x1920) -->
        <button onclick="closeShareModal();generateShareStory(this.closest('#share-modal').dataset.type, this.closest('#share-modal').dataset.id);" 
                style="display:flex;align-items:center;justify-content:center;gap:8px;width:100%;padding:14px;border-radius:12px;background:linear-gradient(135deg,rgba(0,255,195,0.2),rgba(59,130,246,0.2));border:1px solid rgba(0,255,195,0.4);color:#00ffc3;font-weight:600;font-size:14px;cursor:pointer;margin-bottom:12px;transition:all 0.2s;"
                onmouseover="this.style.transform='scale(1.02)'"
                onmouseout="this.style.transform='scale(1)'">
          📱 Partager en Story (image 1080×1920)
        </button>
        
        <!-- Copier le lien -->
        <div style="display:flex;gap:8px;align-items:center;background:rgba(0,0,0,0.3);border-radius:12px;padding:12px;border:1px solid var(--ui-card-border, rgba(255,255,255,0.1));">
          <input type="text" value="${url}" readonly 
                 style="flex:1;background:transparent;border:none;color:var(--ui-text-main, #fff);font-size:12px;outline:none;min-width:0;">
          <button onclick="copyShareLink('${url}')" 
                  style="padding:8px 16px;border-radius:8px;background:#00ffc3;border:none;color:#000;font-weight:600;font-size:12px;cursor:pointer;white-space:nowrap;transition:all 0.2s;"
                  onmouseover="this.style.transform='scale(1.05)'"
                  onmouseout="this.style.transform='scale(1)'">
            📋 Copier
          </button>
        </div>
        
        <!-- Fermer -->
        <button onclick="closeShareModal()" 
                style="width:100%;margin-top:16px;padding:12px;border-radius:12px;background:transparent;border:1px solid var(--ui-card-border, rgba(255,255,255,0.2));color:var(--ui-text-muted, #94a3b8);font-size:13px;cursor:pointer;transition:all 0.2s;"
                onmouseover="this.style.background='rgba(255,255,255,0.05)'"
                onmouseout="this.style.background='transparent'">
          Fermer
        </button>
        
      </div>
    </div>
  `;
  
  document.body.appendChild(shareModal);
}

// Génère une image Story 1080×1920 pour partage Instagram/Stories
async function generateShareStory(type, id) {
  const idNum = typeof id === 'string' ? parseInt(id, 10) : id;
  let item = null;
  let title = "Découvrez sur MapEvent !";
  if (type === "event") {
    item = eventsData.find(e => e.id === idNum);
    if (item) title = item.title || item.name || title;
  } else if (type === "booking") {
    item = bookingsData.find(b => b.id === idNum);
    if (item) title = item.title || item.name || title;
  } else if (type === "service") {
    item = servicesData.find(s => s.id === idNum);
    if (item) title = item.title || item.name || title;
  }
  const url = `${window.location.origin}${window.location.pathname}?${type}=${idNum}`;
  const W = 1080, H = 1920;
  const canvas = document.createElement('canvas');
  canvas.width = W;
  canvas.height = H;
  const ctx = canvas.getContext('2d');
  
  // Fond gradient
  const grad = ctx.createLinearGradient(0, 0, W, H);
  grad.addColorStop(0, '#0f172a');
  grad.addColorStop(0.5, '#1e293b');
  grad.addColorStop(1, '#020617');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, W, H);
  
  // Image de l'item (si disponible)
  let imgUrl = item && typeof getImageCandidatesForItem === 'function' 
    ? (getImageCandidatesForItem(item)[0] || '') 
    : '';
  if (imgUrl && !imgUrl.startsWith('http')) {
    imgUrl = (imgUrl.startsWith('/') ? window.location.origin : '') + imgUrl;
  }
  if (imgUrl) {
    try {
      const img = await new Promise((resolve, reject) => {
        const i = new Image();
        i.crossOrigin = 'anonymous';
        i.onload = () => resolve(i);
        i.onerror = reject;
        i.src = imgUrl;
      });
      const maxH = H * 0.45;
      const ratio = img.naturalWidth / img.naturalHeight;
      const drawH = Math.min(maxH, img.naturalHeight);
      const drawW = ratio * drawH;
      const sx = (W - drawW) / 2;
      ctx.drawImage(img, 0, 0, img.naturalWidth, img.naturalHeight, sx, 0, drawW, drawH);
    } catch (_) {}
  }
  
  // Overlay sombre
  ctx.fillStyle = 'rgba(0,0,0,0.4)';
  ctx.fillRect(0, 0, W, H);
  
  // Zone contenu
  const pad = 60;
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 52px system-ui, sans-serif';
  ctx.textAlign = 'center';
  const lines = (title || '').match(/.{1,28}/g) || [''];
  lines.slice(0, 3).forEach((line, i) => {
    ctx.fillText(line, W / 2, H * 0.5 + i * 60, W - pad * 2);
  });
  
  // Date/lieu
  if (item) {
    ctx.fillStyle = '#94a3b8';
    ctx.font = 'bold 32px system-ui, sans-serif';
    let sub = '';
    if (item.startDate) sub = new Date(item.startDate).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
    if (item.city || item.address) sub += (sub ? ' • ' : '') + (item.city || item.address || '').substring(0, 40);
    if (sub) ctx.fillText(sub, W / 2, H * 0.62, W - pad * 2);
  }
  
  // QR code (API publique)
  const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(url)}`;
  try {
    const qrImg = await new Promise((resolve, reject) => {
      const i = new Image();
      i.crossOrigin = 'anonymous';
      i.onload = () => resolve(i);
      i.onerror = reject;
      i.src = qrUrl;
    });
    ctx.fillStyle = '#fff';
    ctx.fillRect((W - 240) / 2, H - 320, 240, 240);
    ctx.drawImage(qrImg, (W - 200) / 2, H - 310, 200, 200);
  } catch (_) {}
  
  // Branding MapEvent
  ctx.fillStyle = '#00ffc3';
  ctx.font = 'bold 36px system-ui, sans-serif';
  ctx.fillText('MapEvent', W / 2, H - 50);
  
  // Télécharger ou partager
  canvas.toBlob(blob => {
    const u = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = u;
    a.download = `mapevent-story-${type}-${idNum}.png`;
    a.click();
    URL.revokeObjectURL(u);
    if (typeof showNotification === 'function') showNotification('📱 Image Story téléchargée ! Partagez-la dans vos Stories.', 'success');
  }, 'image/png');
}
window.generateShareStory = generateShareStory;

function closeShareModal(event) {
  if (event && event.target !== event.currentTarget) return;
  const modal = document.getElementById('share-modal');
  if (modal) modal.remove();
}

function copyShareLink(url) {
  navigator.clipboard.writeText(url).then(() => {
    showNotification("🔗 Lien copié dans le presse-papier !", "success");
    closeShareModal();
  }).catch(() => {
    // Fallback pour les navigateurs qui ne supportent pas clipboard
    const input = document.querySelector('#share-modal input');
    if (input) {
      input.select();
      document.execCommand('copy');
      showNotification("🔗 Lien copié !", "success");
      closeShareModal();
    }
  });
}

// Exposer les fonctions
window.closeShareModal = closeShareModal;
window.copyShareLink = copyShareLink;
window.shareItem = shareItem;
// Mettre à jour la fonction globale avec l'implémentation complète
// sharePopup appelle directement shareItem maintenant que shareItem est défini
// Cette assignation remplace le stub défini plus tôt
window.sharePopup = function(type, id) {
  if (typeof shareItem === 'function') {
    shareItem(type, id);
  } else {
    console.warn('sharePopup: shareItem not available');
  }
};

