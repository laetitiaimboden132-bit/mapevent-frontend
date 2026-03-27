// ============================================
// ARCHIVE DES FONCTIONNALITÉS SOCIALES
// Sauvegardé le 2026-02-21
// Ces fonctionnalités ont été retirées de map_logic.js
// pour simplifier l'app. Garder ce fichier au cas où
// on voudrait les réactiver plus tard.
// ============================================

// ============================================
// 1. NOTIFICATIONS SOCIALES (friend_request, event_invite, etc.)
// ============================================

async function openNotificationsModal() {
  if (!currentUser || !currentUser.isLoggedIn) { openAuthModal('login'); return; }
  
  const token = typeof getAuthToken === 'function' ? getAuthToken() : null;
  if (!token) return;
  
  let backdrop = document.getElementById('popup-modal-backdrop');
  if (!backdrop) {
    backdrop = document.createElement('div');
    backdrop.id = 'popup-modal-backdrop';
    backdrop.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.75);display:flex;align-items:center;justify-content:center;z-index:99999;backdrop-filter:blur(2px);';
    document.body.appendChild(backdrop);
  }
  backdrop.style.display = 'flex';
  backdrop.onclick = (e) => { if (e.target === backdrop) backdrop.style.display = 'none'; };
  
  backdrop.innerHTML = `
    <div id="popup-modal-content" style="background:#1e293b;border-radius:20px;width:90%;max-width:500px;max-height:85vh;overflow-y:auto;padding:20px;">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;">
        <h2 style="margin:0;font-size:20px;font-weight:700;color:#fff;">🔔 Notifications</h2>
        <div style="display:flex;gap:8px;align-items:center;">
          <button onclick="markAllNotificationsRead()" style="padding:6px 12px;border-radius:8px;border:1px solid rgba(255,255,255,0.1);background:transparent;color:#64748b;font-size:11px;cursor:pointer;">Tout lire</button>
          <button onclick="document.getElementById('popup-modal-backdrop').style.display='none'" style="background:none;border:none;color:#64748b;font-size:22px;cursor:pointer;">✕</button>
        </div>
      </div>
      <div id="notifications-list" style="color:#64748b;">Chargement...</div>
    </div>
  `;
  
  try {
    const resp = await fetch(`${window.API_BASE_URL}/notifications`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!resp.ok) throw new Error();
    const data = await resp.json();
    const listDiv = document.getElementById('notifications-list');
    if (!listDiv) return;
    
    if (!data.notifications || data.notifications.length === 0) {
      listDiv.innerHTML = '<div style="text-align:center;padding:40px;"><div style="font-size:48px;margin-bottom:12px;opacity:0.5;">🔔</div><div style="color:#64748b;">Aucune notification</div></div>';
      return;
    }
    
    const typeIcons = { 'friend_request': '👥', 'friend_accepted': '🤝', 'event_invite': '📅', 'social_like': '❤️', 'social_comment': '💬' };
    const typeLabels = { 'friend_request': 'Demande d\'ami', 'friend_accepted': 'Ami accepte', 'event_invite': 'Invitation event', 'social_like': 'A aime votre post', 'social_comment': 'A commente' };
    
    listDiv.innerHTML = data.notifications.map(n => `
      <div style="display:flex;gap:12px;padding:12px;border-radius:12px;background:${n.isRead ? 'transparent' : 'rgba(59,130,246,0.08)'};border:1px solid ${n.isRead ? 'rgba(255,255,255,0.05)' : 'rgba(59,130,246,0.15)'};margin-bottom:8px;cursor:pointer;" onclick="markNotificationRead(${n.id})">
        <div style="width:40px;height:40px;border-radius:50%;background:rgba(59,130,246,0.15);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">
          ${typeIcons[n.type] || '🔔'}
        </div>
        <div style="flex:1;">
          <div style="font-size:14px;color:#e2e8f0;"><strong>${escapeHtml(n.fromUsername)}</strong> ${typeLabels[n.type] || n.message || ''}</div>
          <div style="font-size:11px;color:#64748b;margin-top:4px;">${n.date ? new Date(n.date).toLocaleDateString('fr-FR', {day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'}) : ''}</div>
        </div>
        ${!n.isRead ? '<div style="width:8px;height:8px;border-radius:50%;background:#3b82f6;flex-shrink:0;align-self:center;"></div>' : ''}
      </div>
    `).join('');
  } catch(e) {
    const listDiv = document.getElementById('notifications-list');
    if (listDiv) listDiv.innerHTML = '<div style="color:#ef4444;">Erreur chargement notifications</div>';
  }
}

window.markNotificationRead = async function(notifId) {
  const token = typeof getAuthToken === 'function' ? getAuthToken() : null;
  if (!token) return;
  try {
    await fetch(`${window.API_BASE_URL}/notifications/read`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ notificationId: notifId })
    });
  } catch(e) {}
};

window.markAllNotificationsRead = async function() {
  const token = typeof getAuthToken === 'function' ? getAuthToken() : null;
  if (!token) return;
  try {
    await fetch(`${window.API_BASE_URL}/notifications/read`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    showNotification('Toutes les notifications marquees comme lues', 'success');
    openNotificationsModal();
  } catch(e) {}
};

window.openNotificationsModal = openNotificationsModal;

// ============================================
// 2. AMIS - getFriendsParticipating
// ============================================

function getFriendsParticipating(eventId) {
  if (!currentUser.isLoggedIn || !currentUser.friends || currentUser.friends.length === 0) {
    return [];
  }
  
  initDemoUsers();
  
  const friendsParticipating = [];
  
  currentUser.friends.forEach(friendId => {
    const hashCode = (str) => {
      let hash = 0;
      for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
      }
      return Math.abs(hash);
    };
    
    const combinedHash = hashCode(`${friendId}:${eventId}`);
    const participates = combinedHash % 5 === 0;
    
    if (participates) {
      const friend = allUsers.find(u => u.id === friendId);
      if (friend) {
        friendsParticipating.push({
          id: friend.id,
          name: friend.name,
          avatar: friend.avatar
        });
      }
    }
  });
  
  return friendsParticipating;
}

// ============================================
// 3. AMIS - acceptFriendRequest / rejectFriendRequest
// ============================================

function acceptFriendRequest(requestId) {
  const request = currentUser.friendRequests?.find(r => r.id === requestId);
  if (!request) return;
  
  if (!currentUser.friends) currentUser.friends = [];
  currentUser.friends.push({
    id: request.fromUserId,
    name: request.fromUserName,
    avatar: request.fromUserAvatar,
    username: request.username
  });
  
  currentUser.friendRequests = currentUser.friendRequests.filter(r => r.id !== requestId);
  localStorage.setItem('currentUser', JSON.stringify(currentUser));
  showNotification(`✅ ${request.fromUserName} ajouté(e) à vos amis !`, 'success');
  showAccountModalTab('amis');
}

function rejectFriendRequest(requestId) {
  currentUser.friendRequests = currentUser.friendRequests.filter(r => r.id !== requestId);
  localStorage.setItem('currentUser', JSON.stringify(currentUser));
  showNotification('Demande d\'ami refusée', 'info');
  showAccountModalTab('amis');
}

window.acceptFriendRequest = acceptFriendRequest;
window.declineFriendRequest = rejectFriendRequest;

// ============================================
// 4. PROFIL UTILISATEUR - Boutons Message / Ajouter comme ami
// ============================================

// Dans openUserProfileView(), section boutons (pour profils non-soi):
/*
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
*/

// Stat "Amis" dans le profil:
/*
  <div style="text-align:center;padding:16px;background:rgba(15,23,42,0.5);border-radius:12px;border:1px solid var(--ui-card-border);">
    <div style="font-size:24px;font-weight:700;color:#00ffc3;">${friendsCount}</div>
    <div style="font-size:12px;color:var(--ui-text-muted);margin-top:4px;">Amis</div>
  </div>
*/

// ============================================
// 5. ONGLETS DU MODAL COMPTE - Groupes, Amis, Map Friend
// ============================================

// Onglet "Groupes" :
/*
  } else if (tab === 'groupes') {
    const groups = currentUser.groups || [];
    tabContent = `
      <div style="padding:16px;">
        <h3 style="margin:0 0 16px;font-size:18px;font-weight:700;">👥 Mes Groupes</h3>
        ... (contenu complet du tab groupes)
      </div>
    `;
*/

// Onglet "Amis" :
/*
  } else if (tab === 'amis') {
    tabContent = `
      <div style="padding:16px;" id="friends-tab-content">
        <h3>Mes Amis</h3>
        <input id="friend-search-input" ... oninput="searchFriendsDebounced(this.value)">
        <div id="friend-requests-section">...</div>
        <div id="friends-list-section">...</div>
      </div>
    `;
    setTimeout(() => loadFriendsTab(), 50);
*/

// Boutons onglets :
/*
  <button onclick="showAccountModalTab('groupes')">👥 Groupes</button>
  <button onclick="showAccountModalTab('amis')">👥 Amis</button>
  <button onclick="showAccountModalTab('mapfriend')">🌍 Map Friend</button>
*/

// ============================================
// 6. PRIVACY - showFriends toggle
// ============================================

/*
  <label>
    <span>👥</span> <span>Mes amis</span>
    <input type="checkbox" onchange="togglePrivacy('showFriends')" />
  </label>
*/

// ============================================
// 7. sendGroupMessage (stub + backend wrapper)
// ============================================

function sendGroupMessage() {
  console.warn('sendGroupMessage appelé mais non implémenté');
  showNotification('Fonctionnalité en cours de développement', 'info');
}

const originalSendGroupMessage = sendGroupMessage;
sendGroupMessage = function(channelId, channelName) {
  const input = document.getElementById(`group-input-${channelId}`);
  if (!input || !input.value.trim()) return;
  const messageText = input.value.trim();
  input.value = '';
  sendGroupMessageBackend(channelId, channelName, messageText);
};

// ============================================
// 8. WEBSOCKET / POLLING pour notifications sociales
// ============================================

let socket = null;
let socketConnected = false;

function initWebSocket() {
  if (!currentUser || !currentUser.isLoggedIn) return;
  try {
    if (window.socketInterval) clearInterval(window.socketInterval);
    window.socketInterval = setInterval(() => {
      checkForNewNotifications();
      checkForNewMessages();
    }, 5000);
    socketConnected = true;
    console.log('✅ WebSocket simulé activé (polling)');
  } catch (error) {
    console.error('Erreur connexion WebSocket:', error);
    socketConnected = false;
  }
}

async function checkForNewNotifications() {
  return; // Route pas encore implémentée
}

// ============================================
// 9. MODÉRATION IMAGE + BACKEND SOCIAL
// ============================================

async function moderateImageBeforeUpload(imageUrl) {
  try {
    const response = await fetch(`${window.API_BASE_URL}/social/moderation/image`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ imageUrl: imageUrl, userId: currentUser.id })
    });
    if (response.ok) {
      const data = await response.json();
      return data.isSafe;
    }
    return true;
  } catch (error) {
    console.error('Erreur modération image:', error);
    return true;
  }
}

// ============================================
// 10. OPEN GROUP CHANNEL (backend integration)
// ============================================

/*
  const originalOpenGroupChannel = openGroupChannel;
  openGroupChannel = async function(channelId, channelName, channelType, channelCategory) {
    ... charge messages depuis /social/groups/{channelId}/messages
    ... appelle originalOpenGroupChannel()
  };
*/

// ============================================
// 11. FRIENDS SECTION IN EVENT POPUP
// ============================================

/*
  // friendsSection template (dans statsRow) :
  ${friendsSection}

  // friendsSection contenait :
  const friendsSection = friendsParticipating.length > 0 ? `
    <div>
      <div style="display:flex;gap:6px;flex-wrap:wrap;">
        ${friendsParticipating.slice(0, 5).map(f => `
          <div>
            <span>${f.avatar}</span>
            <span>${f.name.split('_')[0]}</span>
          </div>
        `).join('')}
      </div>
    </div>
  ` : (currentUser.isLoggedIn && currentUser.friends?.length > 0 ? `
    <div>
      👥 Aucun de vos amis ne participe encore. <span onclick="onAction('share', 'event', ${ev.id})">Invitez-les !</span>
    </div>
  ` : '');
*/

// ============================================
// 12. HELP/ABOUT - lignes sociales
// ============================================

/*
  <li><strong>Safe Social</strong> - Réseau social sécurisé et bienveillant</li>
  <li><strong>Messagerie</strong> - Discutez avec vos amis</li>
  <li><strong>Groupes</strong> - Créez des groupes comme WhatsApp</li>
  <li><strong>Invitations</strong> - Invitez vos amis aux événements</li>
  <li><strong>Localisation live</strong> - Retrouvez vos amis sur place</li>
*/

// ============================================
// 13. BLOCS SOCIAUX DANS LE MODAL COMPTE PRINCIPAL
// ============================================

/*
  // Bloc "Map Friend" dans le header du modal compte:
  <div style="flex:1;text-align:left;">
    <div style="font-weight:700;font-size:16px;color:#fff;">Map Friend</div>
    <div style="font-size:12px;color:#93c5fd;margin-top:3px;">Fil social, partage d'events entre amis et messages</div>
  </div>
  <div style="font-size:18px;color:#60a5fa;flex-shrink:0;">→</div>

  // Bloc "Amis" dans la grille du modal compte:
  <div style="font-weight:600;font-size:13px;color:#fff;">Amis</div>
  <div style="font-size:11px;color:#94a3b8;margin-top:4px;">Ajoutez des amis pour partager vos events</div>
*/

// ============================================
// 14. WINDOW EXPORTS SOCIAUX
// ============================================

/*
  window.initWebSocket = initWebSocket;
  window.toggleReaction = toggleReaction;
  window.showReactionPicker = showReactionPicker;
  window.moderateImageBeforeUpload = moderateImageBeforeUpload;
  window.searchUsers = searchUsers;
  window.acceptFriendRequest = acceptFriendRequest;
  window.declineFriendRequest = declineFriendRequest;
  window.shareToFriend = shareToFriend;
  window.handleSocialAlert = handleSocialAlert;
  window.updateSocialAlertsCount = updateSocialAlertsCount;
*/
