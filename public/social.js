// ============================================================
// social.js
// Social: Reviews, Discussion, Friends, Invitations, Report (openReviewModal, openDiscussionModal, openFriendsModal)
// Extrait de map_logic.js (lignes 20852-22384)
// ============================================================

  }
  // Fallback localStorage
  try { localStorage.setItem(`discussion_${type}_${id}`, JSON.stringify(posts)); } catch(e) {}
  return false;
}

// Fonction pour soumettre un post (style Facebook) - reste dans la discussion
window.submitDiscussionComment = async function(type, id) {
  const input = document.getElementById("discussion-input");
  if (!input || !input.value.trim()) return;
  
  const post = {
    id: Date.now().toString(),
    author: currentUser?.name || currentUser?.username || 'Utilisateur',
    avatar: currentUser?.avatar || '👤',
    text: input.value.trim(),
    timestamp: Date.now(),
    likes: [],
    replies: []
  };
  
  // Charger posts actuels depuis API
  let posts = [];
  try {
    const resp = await fetch(`${window.API_BASE_URL}/discussions/${type}/${id}`);
    if (resp.ok) {
      const data = await resp.json();
      posts = data.posts || [];
    }
  } catch(e) {
    posts = JSON.parse(localStorage.getItem(`discussion_${type}_${id}`) || '[]');
  }
  
  posts.unshift(post);
  await saveDiscussionToAPI(type, id, posts);
  
  // Vider le champ de saisie
  input.value = '';
  input.style.height = 'auto';
  
  // Rafraichir l'affichage depuis l'API
    openDiscussionModal(type, id);
};

// Fonction pour afficher/masquer le formulaire de réponse (avec support pour chemins)
window.showReplyForm = function(postId, replyPath = null) {
  const formId = replyPath ? `reply-form-${postId}-${replyPath}` : `reply-form-${postId}`;
  const form = document.getElementById(formId);
  if (form) {
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
    if (form.style.display === 'block') {
      const textareaId = replyPath ? `reply-input-${postId}-${replyPath}` : `reply-input-${postId}`;
      const textarea = document.getElementById(textareaId);
      if (textarea) setTimeout(() => textarea.focus(), 100);
    }
  }
};

// Fonction pour afficher toutes les réponses d'un post (style Facebook)
window.showAllReplies = function(postId, parentPath = '') {
  const type = window.currentDiscussionType;
  const id = window.currentDiscussionId;
  
  if (!type || !id) return;
  
  // Stocker l'état "showAll" dans sessionStorage pour persister après rechargement
  const key = `showAllReplies_${type}_${id}_${postId}_${parentPath}`;
  sessionStorage.setItem(key, 'true');
  
  // Recharger la discussion pour afficher toutes les réponses
  openDiscussionModal(type, id);
};

// Fonction pour afficher toutes les réponses imbriquées
window.showAllNestedReplies = function(postId, parentPath) {
  const type = window.currentDiscussionType;
  const id = window.currentDiscussionId;
  
  if (!type || !id) return;
  
  // Stocker l'état "showAll" dans sessionStorage pour persister après rechargement
  const key = `showAllNestedReplies_${type}_${id}_${postId}_${parentPath}`;
  sessionStorage.setItem(key, 'true');
  
  // Recharger la discussion pour afficher toutes les réponses imbriquées
  openDiscussionModal(type, id);
};

// Fonction pour afficher toutes les réponses imbriquées
window.showAllNestedReplies = function(postId, parentPath) {
  const type = window.currentDiscussionType;
  const id = window.currentDiscussionId;
  
  if (!type || !id) return;
  
  // Trouver le conteneur des réponses imbriquées
  const nestedContainer = document.querySelector(`[data-post-id="${postId}"][data-parent-path="${parentPath}"]`);
  if (!nestedContainer) return;
  
  // Marquer comme "tout affiché"
  nestedContainer.dataset.showAll = 'true';
  
  // Recharger la discussion pour afficher toutes les réponses imbriquées
  openDiscussionModal(type, id);
};

// Fonction pour masquer le formulaire de réponse (avec support pour chemins)
window.hideReplyForm = function(postId, replyPath = null) {
  const formId = replyPath ? `reply-form-${postId}-${replyPath}` : `reply-form-${postId}`;
  const form = document.getElementById(formId);
  if (form) {
    form.style.display = 'none';
    const textareaId = replyPath ? `reply-input-${postId}-${replyPath}` : `reply-input-${postId}`;
    const textarea = document.getElementById(textareaId);
    if (textarea) textarea.value = '';
  }
};

// Fonction récursive pour trouver une réponse par son chemin (ex: "reply1-reply2-reply3")
function findReplyByPath(replies, pathArray, currentIndex = 0) {
  if (!replies || currentIndex >= pathArray.length) return null;
  
  const replyId = pathArray[currentIndex];
  const reply = replies.find(r => r.id === replyId);
  
  if (!reply) return null;
  
  if (currentIndex === pathArray.length - 1) {
    return reply; // On a trouvé la réponse cible
  }
  
  // Continuer la recherche dans les réponses de cette réponse
  return findReplyByPath(reply.replies || [], pathArray, currentIndex + 1);
}

// Fonction pour soumettre une réponse à un post (avec support pour chemins imbriqués)
window.submitReply = async function(type, id, postId, replyPath = null) {
  const inputId = replyPath ? `reply-input-${postId}-${replyPath}` : `reply-input-${postId}`;
  const input = document.getElementById(inputId);
  if (!input || !input.value.trim()) return;
  
  const reply = {
    id: Date.now().toString(),
    author: currentUser?.name || currentUser?.username || 'Utilisateur',
    avatar: currentUser?.avatar || '👤',
    text: input.value.trim(),
    timestamp: Date.now(),
    replies: []
  };
  
  // Charger posts actuels depuis API
  let posts = [];
  try {
    const resp = await fetch(`${window.API_BASE_URL}/discussions/${type}/${id}`);
    if (resp.ok) {
      const data = await resp.json();
      posts = data.posts || [];
    }
  } catch(e) {
    posts = JSON.parse(localStorage.getItem(`discussion_${type}_${id}`) || '[]');
  }
  
  const post = posts.find(p => p.id === postId);
  
  if (post) {
    if (replyPath) {
      const pathArray = replyPath.split('-');
      const parentReply = findReplyByPath(post.replies || [], pathArray);
      
      if (parentReply) {
        if (!parentReply.replies) parentReply.replies = [];
        parentReply.replies.push(reply);
      }
    } else {
      if (!post.replies) post.replies = [];
      post.replies.push(reply);
    }
    
    await saveDiscussionToAPI(type, id, posts);
    
    // Rafraichir l'affichage depuis l'API
    openDiscussionModal(type, id);
  }
};

// Fonction pour liker/unliker un post
window.togglePostLike = async function(type, id, postId) {
  // Charger posts depuis API
  let posts = [];
  try {
    const resp = await fetch(`${window.API_BASE_URL}/discussions/${type}/${id}`);
    if (resp.ok) {
      const data = await resp.json();
      posts = data.posts || [];
    }
  } catch(e) {
    posts = JSON.parse(localStorage.getItem(`discussion_${type}_${id}`) || '[]');
  }
  
  const post = posts.find(p => p.id === postId);
  
  if (post) {
    if (!post.likes) post.likes = [];
    const userId = currentUser?.id || currentUser?.username;
    const index = post.likes.indexOf(userId);
    
    if (index > -1) {
      post.likes.splice(index, 1);
    } else {
      post.likes.push(userId);
    }
    
    await saveDiscussionToAPI(type, id, posts);
    
    // Réouvrir le modal pour afficher le changement
    openDiscussionModal(type, id);
  }
};

// ============================================
// SYSTÈME D'AMIS - UI COMPLÈTE
// ============================================

function openFriendsModal() {
  const esc = (typeof escapeHtml === 'function') ? escapeHtml : (s) => String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  
  if (!currentUser || !currentUser.isLoggedIn) {
    openAuthModal('login');
    return;
  }
  
  const token = typeof getAuthToken === 'function' ? getAuthToken() : null;
  const authHeaders = token ? { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' };
  
  let backdrop = document.getElementById('popup-modal-backdrop');
  if (!backdrop) {
    backdrop = document.createElement('div');
    backdrop.id = 'popup-modal-backdrop';
    backdrop.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.75);display:flex;align-items:center;justify-content:center;z-index:99999;backdrop-filter:blur(2px);';
    document.body.appendChild(backdrop);
  }
  
  backdrop.style.display = 'flex';
  backdrop.innerHTML = `
    <div id="popup-modal-content" style="background:#1e293b;border-radius:20px;width:90%;max-width:500px;max-height:85vh;overflow-y:auto;position:relative;">
      <div style="padding:20px;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;">
          <h2 style="margin:0;font-size:20px;font-weight:700;color:#fff;">👥 Mes Amis</h2>
          <button onclick="document.getElementById('popup-modal-backdrop').style.display='none'" style="background:none;border:none;color:#64748b;font-size:22px;cursor:pointer;">✕</button>
        </div>
        
        <!-- Recherche d'amis -->
        <div style="margin-bottom:20px;">
            <div style="display:flex;gap:8px;">
            <input id="friend-search-input" type="text" placeholder="Rechercher par nom ou email..." 
              style="flex:1;padding:10px 14px;border-radius:12px;border:1px solid rgba(255,255,255,0.1);background:#0f172a;color:#e2e8f0;font-size:14px;"
              oninput="searchFriends(this.value)" />
          </div>
          <div id="friend-search-results" style="margin-top:8px;"></div>
        </div>
        
        <!-- Demandes reçues -->
        <div id="friend-requests-section" style="margin-bottom:20px;">
          <div style="font-size:13px;font-weight:600;color:#94a3b8;margin-bottom:10px;text-transform:uppercase;letter-spacing:0.5px;">Demandes reçues</div>
          <div id="friend-requests-list" style="color:#64748b;font-size:13px;">Chargement...</div>
        </div>
        
        <!-- Liste d'amis -->
        <div>
          <div style="font-size:13px;font-weight:600;color:#94a3b8;margin-bottom:10px;text-transform:uppercase;letter-spacing:0.5px;">Mes amis</div>
          <div id="friends-list" style="color:#64748b;font-size:13px;">Chargement...</div>
        </div>
      </div>
    </div>
  `;
  
  backdrop.onclick = (e) => { if (e.target === backdrop) backdrop.style.display = 'none'; };
  
  // Charger les données
  loadFriendRequests(authHeaders);
  loadFriendsList(authHeaders);
}

window.searchFriends = async function(query) {
  const resultsDiv = document.getElementById('friend-search-results');
  if (!resultsDiv) return;
  if (!query || query.length < 2) { resultsDiv.innerHTML = ''; return; }
  
  const token = typeof getAuthToken === 'function' ? getAuthToken() : null;
  if (!token) { resultsDiv.innerHTML = '<div style="color:#ef4444;font-size:12px;">Connexion requise</div>'; return; }
  
  try {
    const resp = await fetch(`${window.API_BASE_URL}/friends/search?q=${encodeURIComponent(query)}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!resp.ok) throw new Error('Erreur recherche');
    const data = await resp.json();
    
    if (!data.users || data.users.length === 0) {
      resultsDiv.innerHTML = '<div style="padding:8px;color:#64748b;font-size:13px;">Aucun utilisateur trouvé</div>';
      return;
    }
    
    resultsDiv.innerHTML = data.users.map(u => `
      <div style="display:flex;align-items:center;gap:10px;padding:10px;border-radius:10px;background:rgba(15,23,42,0.5);margin-bottom:6px;">
        <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:14px;color:#fff;font-weight:700;flex-shrink:0;">
          ${u.avatar ? `<img src="${u.avatar}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;" onerror="this.outerHTML='👤'">` : (u.username||'U').charAt(0).toUpperCase()}
        </div>
        <div style="flex:1;min-width:0;">
          <div style="font-weight:600;font-size:14px;color:#e2e8f0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(u.username || 'Utilisateur')}</div>
        </div>
        <button onclick="sendFriendRequest('${u.id}')" style="padding:6px 14px;border-radius:8px;border:none;background:#3b82f6;color:#fff;font-size:12px;font-weight:600;cursor:pointer;white-space:nowrap;">+ Ajouter</button>
      </div>
    `).join('');
  } catch(e) {
    resultsDiv.innerHTML = '<div style="color:#ef4444;font-size:12px;">Erreur de recherche</div>';
  }
};

window.sendFriendRequest = async function(toUserId) {
  const token = typeof getAuthToken === 'function' ? getAuthToken() : null;
  if (!token) return;
  
  try {
    const resp = await fetch(`${window.API_BASE_URL}/friends/request`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ toUserId })
    });
    const data = await resp.json();
    
    if (data.status === 'accepted') {
      showNotification('Vous etes maintenant amis !', 'success');
      openFriendsModal(); // Rafraichir
    } else if (data.status === 'pending') {
      showNotification('Demande d\'ami envoyee !', 'success');
    } else if (data.error) {
      showNotification(data.error, 'warning');
    }
  } catch(e) {
    showNotification('Erreur lors de l\'envoi', 'error');
  }
};

async function loadFriendRequests(authHeaders) {
  const div = document.getElementById('friend-requests-list');
  if (!div) return;
  
  try {
    const resp = await fetch(`${window.API_BASE_URL}/friends/requests`, { headers: authHeaders });
    if (!resp.ok) throw new Error();
    const data = await resp.json();
    
    if (!data.requests || data.requests.length === 0) {
      div.innerHTML = '<div style="padding:8px;color:#64748b;font-size:13px;">Aucune demande en attente</div>';
      // Cacher la section
      const section = document.getElementById('friend-requests-section');
      if (section) section.style.display = 'none';
      return;
    }
    
    div.innerHTML = data.requests.map(r => `
      <div style="display:flex;align-items:center;gap:10px;padding:10px;border-radius:10px;background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.2);margin-bottom:6px;">
        <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:14px;color:#fff;font-weight:700;flex-shrink:0;">
          ${(r.username||'U').charAt(0).toUpperCase()}
              </div>
              <div style="flex:1;">
          <div style="font-weight:600;font-size:14px;color:#e2e8f0;">${escapeHtml(r.username)}</div>
          <div style="font-size:11px;color:#64748b;">Demande d'ami</div>
                  </div>
        <button onclick="respondFriendRequest(${r.requestId},'accept')" style="padding:6px 12px;border-radius:8px;border:none;background:#22c55e;color:#fff;font-size:12px;font-weight:600;cursor:pointer;">Accepter</button>
        <button onclick="respondFriendRequest(${r.requestId},'reject')" style="padding:6px 12px;border-radius:8px;border:none;background:#ef4444;color:#fff;font-size:12px;font-weight:600;cursor:pointer;">Refuser</button>
                </div>
    `).join('');
  } catch(e) {
    div.innerHTML = '<div style="color:#ef4444;font-size:12px;">Erreur chargement</div>';
  }
}

window.respondFriendRequest = async function(requestId, action) {
  const token = typeof getAuthToken === 'function' ? getAuthToken() : null;
  if (!token) return;
  
  try {
    await fetch(`${window.API_BASE_URL}/friends/respond`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ requestId, action })
    });
    showNotification(action === 'accept' ? 'Ami accepte !' : 'Demande refusee', action === 'accept' ? 'success' : 'info');
    openFriendsModal(); // Rafraichir
  } catch(e) {
    showNotification('Erreur', 'error');
  }
};

async function loadFriendsList(authHeaders) {
  const div = document.getElementById('friends-list');
  if (!div) return;
  
  try {
    const resp = await fetch(`${window.API_BASE_URL}/friends/list`, { headers: authHeaders });
    if (!resp.ok) throw new Error();
    const data = await resp.json();
    
    if (!data.friends || data.friends.length === 0) {
      div.innerHTML = '<div style="text-align:center;padding:30px;"><div style="font-size:48px;margin-bottom:12px;opacity:0.5;">👥</div><div style="color:#64748b;font-size:14px;">Pas encore d\'amis</div><div style="color:#475569;font-size:12px;margin-top:4px;">Recherchez des utilisateurs ci-dessus !</div></div>';
      return;
    }
    
    // Stocker pour utiliser ailleurs (invitations)
    window._friendsList = data.friends;
    
    div.innerHTML = data.friends.map(f => `
      <div style="display:flex;align-items:center;gap:10px;padding:10px;border-radius:10px;background:rgba(15,23,42,0.5);margin-bottom:6px;">
        <div style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:16px;color:#fff;font-weight:700;flex-shrink:0;">
          ${f.avatar ? `<img src="${f.avatar}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;" onerror="this.outerHTML='${(f.username||'U').charAt(0).toUpperCase()}'">` : (f.username||'U').charAt(0).toUpperCase()}
              </div>
        <div style="flex:1;">
          <div style="font-weight:600;font-size:14px;color:#e2e8f0;">${escapeHtml(f.username)}</div>
          <div style="font-size:11px;color:#64748b;">Ami depuis ${f.since ? new Date(f.since).toLocaleDateString('fr-FR', {day:'numeric',month:'short',year:'numeric'}) : '...'}</div>
            </div>
        <button onclick="openPrivateChat('${f.id}','${escapeHtml(f.username)}')" style="padding:6px 10px;border-radius:8px;border:1px solid rgba(59,130,246,0.3);background:transparent;color:#3b82f6;font-size:12px;cursor:pointer;" title="Discuter">💬</button>
        <button onclick="removeFriend('${f.id}')" style="padding:6px 10px;border-radius:8px;border:1px solid rgba(239,68,68,0.3);background:transparent;color:#ef4444;font-size:12px;cursor:pointer;" title="Retirer">✕</button>
                </div>
    `).join('');
  } catch(e) {
    div.innerHTML = '<div style="color:#ef4444;font-size:12px;">Erreur chargement</div>';
  }
}

window.removeFriend = async function(friendId) {
  if (!confirm('Retirer cet ami ?')) return;
  const token = typeof getAuthToken === 'function' ? getAuthToken() : null;
  if (!token) return;
  
  try {
    await fetch(`${window.API_BASE_URL}/friends/remove`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ friendId })
    });
    showNotification('Ami retire', 'info');
    openFriendsModal();
  } catch(e) {}
};

window.openPrivateChat = function(friendId, friendName) {
  showNotification('Discussion privee avec ' + friendName + ' - bientot disponible !', 'info');
};

// ============================================
// INVITER DES AMIS À UN EVENT
// ============================================

function openInviteFriendsModal(itemType, itemId, itemTitle) {
  if (!currentUser || !currentUser.isLoggedIn) { openAuthModal('login'); return; }
  
  const token = typeof getAuthToken === 'function' ? getAuthToken() : null;
  if (!token) return;
  
  // Créer le modal d'invitation
  let modal = document.getElementById('invite-friends-modal');
  if (modal) modal.remove();
  
  modal = document.createElement('div');
  modal.id = 'invite-friends-modal';
  modal.style.cssText = 'position:fixed;inset:0;z-index:100001;background:rgba(0,0,0,0.8);display:flex;align-items:center;justify-content:center;backdrop-filter:blur(4px);';
  modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
  
  modal.innerHTML = `
    <div style="background:#1e293b;border-radius:18px;width:90%;max-width:420px;max-height:80vh;overflow-y:auto;padding:20px;">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
        <div>
          <div style="font-size:16px;font-weight:700;color:#fff;">Inviter des amis</div>
          <div style="font-size:12px;color:#64748b;margin-top:2px;">${escapeHtml(itemTitle || '')}</div>
                </div>
        <button onclick="this.closest('#invite-friends-modal').remove()" style="background:none;border:none;color:#64748b;font-size:20px;cursor:pointer;">✕</button>
              </div>
      <input id="invite-search-input" type="text" placeholder="Chercher un ami..." 
        style="width:100%;padding:10px 14px;border-radius:10px;border:1px solid rgba(255,255,255,0.1);background:#0f172a;color:#e2e8f0;font-size:14px;margin-bottom:12px;box-sizing:border-box;"
        oninput="filterInviteList(this.value)" />
      <div id="invite-friends-list" style="color:#64748b;">Chargement...</div>
            </div>
  `;
  document.body.appendChild(modal);
  
  // Charger la liste d'amis
  fetch(`${window.API_BASE_URL}/friends/list`, {
    headers: { 'Authorization': `Bearer ${token}` }
  }).then(r => r.json()).then(data => {
    const listDiv = document.getElementById('invite-friends-list');
    if (!listDiv) return;
    
    const friends = data.friends || [];
    if (friends.length === 0) {
      listDiv.innerHTML = '<div style="text-align:center;padding:20px;color:#64748b;">Pas encore d\'amis a inviter</div>';
      return;
    }
    
    window._inviteFriends = friends;
    renderInviteList(friends, itemType, itemId);
  }).catch(() => {
    const listDiv = document.getElementById('invite-friends-list');
    if (listDiv) listDiv.innerHTML = '<div style="color:#ef4444;">Erreur chargement</div>';
  });
}

window.filterInviteList = function(query) {
  if (!window._inviteFriends) return;
  const filtered = query.length < 1 ? window._inviteFriends : window._inviteFriends.filter(f => 
    (f.username||'').toLowerCase().includes(query.toLowerCase()) ||
    (f.email||'').toLowerCase().includes(query.toLowerCase())
  );
  const itemType = window._currentInviteType || 'event';
  const itemId = window._currentInviteId || 0;
  renderInviteList(filtered, itemType, itemId);
};

function renderInviteList(friends, itemType, itemId) {
  window._currentInviteType = itemType;
  window._currentInviteId = itemId;
  const listDiv = document.getElementById('invite-friends-list');
  if (!listDiv) return;
  
  listDiv.innerHTML = friends.map(f => `
    <div style="display:flex;align-items:center;gap:10px;padding:10px;border-radius:10px;background:rgba(15,23,42,0.5);margin-bottom:6px;">
      <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:14px;color:#fff;font-weight:700;flex-shrink:0;">
        ${(f.username||'U').charAt(0).toUpperCase()}
              </div>
      <div style="flex:1;font-weight:600;font-size:14px;color:#e2e8f0;">${escapeHtml(f.username)}</div>
      <button onclick="inviteFriendToEvent('${f.id}','${itemType}',${itemId})" style="padding:6px 14px;border-radius:8px;border:none;background:linear-gradient(135deg,#22c55e,#16a34a);color:#fff;font-size:12px;font-weight:600;cursor:pointer;">Inviter</button>
    </div>
  `).join('');
}

window.inviteFriendToEvent = async function(friendId, itemType, itemId) {
  const token = typeof getAuthToken === 'function' ? getAuthToken() : null;
  if (!token) return;
  
  try {
    const resp = await fetch(`${window.API_BASE_URL}/friends/invite`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ friendId, itemType, itemId })
    });
    if (resp.ok) {
      showNotification('Invitation envoyee !', 'success');
    } else {
      const data = await resp.json();
      showNotification(data.error || 'Erreur', 'error');
    }
  } catch(e) {
    showNotification('Erreur d\'envoi', 'error');
  }
};

window.openInviteFriendsModal = openInviteFriendsModal;
window.openFriendsModal = openFriendsModal;

// ============================================
// NOTIFICATIONS - UI
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
// MAP FRIEND - FIL SOCIAL TYPE FACEBOOK
// ============================================

async function openMapFriendModal() {
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
    <div id="popup-modal-content" style="background:var(--ui-card-bg, #0f172a);border-radius:20px;width:95%;max-width:550px;max-height:90vh;overflow:hidden;display:flex;flex-direction:column;">
      <!-- Header -->
      <div style="padding:16px 20px;border-bottom:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:space-between;flex-shrink:0;">
        <div style="display:flex;align-items:center;gap:10px;">
          <span style="font-size:22px;">🌐</span>
          <span style="font-size:18px;font-weight:700;color:#e4e6eb;">Map Friend</span>
        </div>
        <button onclick="document.getElementById('popup-modal-backdrop').style.display='none'" style="background:none;border:none;color:#b0b3b8;font-size:22px;cursor:pointer;">✕</button>
      </div>
      
      <!-- Zone de creation de post -->
      <div style="padding:16px 20px;border-bottom:1px solid rgba(255,255,255,0.1);flex-shrink:0;">
        <div style="display:flex;gap:10px;align-items:flex-start;">
          <div style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:16px;color:#fff;font-weight:700;flex-shrink:0;">
            ${(currentUser.username||'U').charAt(0).toUpperCase()}
              </div>
              <div style="flex:1;">
            <textarea id="social-post-input" placeholder="Quoi de neuf ? Partagez un event, un lien, un message..." 
              style="width:100%;min-height:60px;max-height:150px;padding:10px 14px;border-radius:14px;border:none;background:#3a3b3c;color:#e4e6eb;font-size:15px;resize:none;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;box-sizing:border-box;"
              oninput="this.style.height='auto';this.style.height=Math.min(this.scrollHeight,150)+'px';"></textarea>
            <div style="display:flex;gap:8px;margin-top:8px;align-items:center;">
              <button onclick="showShareEventPicker()" style="padding:6px 12px;border-radius:8px;border:1px solid rgba(255,255,255,0.1);background:transparent;color:#45bd62;font-size:12px;cursor:pointer;display:flex;align-items:center;gap:4px;">📅 Event</button>
              <button onclick="addLinkToPost()" style="padding:6px 12px;border-radius:8px;border:1px solid rgba(255,255,255,0.1);background:transparent;color:#3b82f6;font-size:12px;cursor:pointer;display:flex;align-items:center;gap:4px;">🔗 Lien</button>
              <div style="flex:1;"></div>
              <button onclick="submitSocialPost()" style="padding:8px 20px;border-radius:10px;border:none;background:#1877f2;color:#fff;font-size:13px;font-weight:600;cursor:pointer;">Publier</button>
              </div>
            </div>
                  </div>
                  </div>
      
      <!-- Fil social -->
      <div id="social-feed" style="flex:1;overflow-y:auto;padding:12px 20px;">
        <div style="text-align:center;padding:20px;color:#b0b3b8;">Chargement du fil...</div>
              </div>
            </div>
  `;
  
  // Charger le fil social
  loadSocialFeed(token);
}

async function loadSocialFeed(token, page = 1) {
  const feedDiv = document.getElementById('social-feed');
  if (!feedDiv) return;
  
  try {
    const resp = await fetch(`${window.API_BASE_URL}/social/feed?page=${page}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!resp.ok) throw new Error();
    const data = await resp.json();
    
    if (!data.posts || data.posts.length === 0) {
      feedDiv.innerHTML = `
        <div style="text-align:center;padding:60px 20px;">
          <div style="font-size:64px;margin-bottom:16px;opacity:0.5;">🌐</div>
          <div style="font-size:18px;font-weight:700;color:#e4e6eb;margin-bottom:8px;">Bienvenue sur Map Friend !</div>
          <div style="font-size:14px;color:#b0b3b8;max-width:300px;margin:0 auto;">Ajoutez des amis et partagez vos evenements, liens et messages. Tout le monde peut voir et repondre !</div>
                </div>
      `;
      return;
    }
    
    const userId = String(currentUser.id || '');
    
    feedDiv.innerHTML = data.posts.map(p => {
      const isLiked = (p.likes || []).includes(userId);
      const likesCount = (p.likes || []).length;
      const isOwn = p.userId === userId;
      const timeStr = p.date ? formatSocialTime(p.date) : '';
      
      // Contenu de l'event partagé si présent
      const eventCard = p.eventId && p.eventTitle ? `
        <div style="margin:8px 0;padding:12px;border-radius:12px;background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.15);cursor:pointer;" onclick="openEventById(${p.eventId})">
          <div style="font-size:14px;font-weight:600;color:#e4e6eb;">📅 ${escapeHtml(p.eventTitle)}</div>
          ${p.eventDate ? `<div style="font-size:12px;color:#b0b3b8;margin-top:4px;">${p.eventDate}${p.eventCity ? ' - ' + escapeHtml(p.eventCity) : ''}</div>` : ''}
                </div>
      ` : '';
      
      const linkCard = p.linkUrl ? `
        <div style="margin:8px 0;padding:12px;border-radius:12px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);">
          <a href="${p.linkUrl}" target="_blank" rel="noopener" style="color:#3b82f6;font-size:13px;word-break:break-all;">${escapeHtml(p.linkTitle || p.linkUrl)}</a>
              </div>
      ` : '';
      
      return `
        <div style="background:rgba(15,23,42,0.6);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:14px;margin-bottom:12px;">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
            <div style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:16px;color:#fff;font-weight:700;flex-shrink:0;">
              ${p.avatar ? `<img src="${p.avatar}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;" onerror="this.outerHTML='${(p.username||'U').charAt(0).toUpperCase()}'">` : (p.username||'U').charAt(0).toUpperCase()}
            </div>
            <div style="flex:1;">
              <div style="font-weight:600;font-size:15px;color:#e4e6eb;">${escapeHtml(p.username)}</div>
              <div style="font-size:12px;color:#b0b3b8;">${timeStr}</div>
              </div>
            ${isOwn ? `<button onclick="deleteSocialPost(${p.id})" style="background:none;border:none;color:#64748b;font-size:16px;cursor:pointer;" title="Supprimer">🗑️</button>` : ''}
          </div>
          ${p.content ? `<div style="font-size:15px;color:#e4e6eb;line-height:1.4;margin-bottom:8px;white-space:pre-wrap;word-break:break-word;">${escapeHtml(p.content)}</div>` : ''}
          ${eventCard}
          ${linkCard}
          
          <!-- Actions -->
          <div style="display:flex;align-items:center;gap:4px;padding:4px 0;margin-top:4px;border-top:1px solid rgba(255,255,255,0.08);">
            <button onclick="toggleSocialLike(${p.id})" style="flex:1;display:flex;align-items:center;justify-content:center;gap:6px;background:none;border:none;color:${isLiked ? '#1877f2' : '#b0b3b8'};font-size:14px;font-weight:600;cursor:pointer;padding:8px;border-radius:6px;" onmouseover="this.style.background='rgba(255,255,255,0.05)'" onmouseout="this.style.background='none'">
              <span>👍</span> <span>J'aime${likesCount > 0 ? ' (' + likesCount + ')' : ''}</span>
            </button>
            <button onclick="openSocialComments(${p.id})" style="flex:1;display:flex;align-items:center;justify-content:center;gap:6px;background:none;border:none;color:#b0b3b8;font-size:14px;font-weight:600;cursor:pointer;padding:8px;border-radius:6px;" onmouseover="this.style.background='rgba(255,255,255,0.05)'" onmouseout="this.style.background='none'">
              <span>💬</span> <span>Commenter${p.commentCount > 0 ? ' (' + p.commentCount + ')' : ''}</span>
            </button>
          </div>
          
          <!-- Zone commentaires (cachée par défaut) -->
          <div id="social-comments-${p.id}" style="display:none;margin-top:8px;padding-top:8px;border-top:1px solid rgba(255,255,255,0.05);"></div>
          </div>
        `;
    }).join('');
  } catch(e) {
    feedDiv.innerHTML = '<div style="text-align:center;padding:20px;color:#ef4444;">Erreur de chargement du fil social</div>';
  }
}

function formatSocialTime(dateStr) {
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now - date;
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'A l\'instant';
  if (mins < 60) return `Il y a ${mins} min`;
  const hours = Math.floor(diff / 3600000);
  if (hours < 24) return `Il y a ${hours}h`;
  const days = Math.floor(diff / 86400000);
  if (days < 7) return `Il y a ${days}j`;
  return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
}

window.submitSocialPost = async function() {
  const input = document.getElementById('social-post-input');
  if (!input || !input.value.trim()) { showNotification('Ecrivez quelque chose !', 'warning'); return; }
  
  const token = typeof getAuthToken === 'function' ? getAuthToken() : null;
  if (!token) return;
  
  const content = input.value.trim();
  const eventId = window._socialPostEventId || null;
  const linkUrl = window._socialPostLinkUrl || null;
  const linkTitle = window._socialPostLinkTitle || null;
  
  try {
    const resp = await fetch(`${window.API_BASE_URL}/social/post`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, eventId, linkUrl, linkTitle, type: eventId ? 'event_share' : linkUrl ? 'link' : 'text' })
    });
    if (resp.ok) {
      input.value = '';
      window._socialPostEventId = null;
      window._socialPostLinkUrl = null;
      window._socialPostLinkTitle = null;
      showNotification('Publication partagee !', 'success');
      loadSocialFeed(token);
    }
  } catch(e) {
    showNotification('Erreur de publication', 'error');
  }
};

window.toggleSocialLike = async function(postId) {
  const token = typeof getAuthToken === 'function' ? getAuthToken() : null;
  if (!token) return;
  
  try {
    await fetch(`${window.API_BASE_URL}/social/post/${postId}/like`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    loadSocialFeed(token);
  } catch(e) {}
};

window.deleteSocialPost = async function(postId) {
  if (!confirm('Supprimer cette publication ?')) return;
  const token = typeof getAuthToken === 'function' ? getAuthToken() : null;
  if (!token) return;
  
  try {
    await fetch(`${window.API_BASE_URL}/social/post/${postId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    showNotification('Publication supprimee', 'info');
    loadSocialFeed(token);
  } catch(e) {}
};

window.openSocialComments = async function(postId) {
  const commentsDiv = document.getElementById(`social-comments-${postId}`);
  if (!commentsDiv) return;
  
  // Toggle visibilité
  if (commentsDiv.style.display === 'block') {
    commentsDiv.style.display = 'none';
    return;
  }
  commentsDiv.style.display = 'block';
  commentsDiv.innerHTML = '<div style="padding:8px;color:#64748b;font-size:13px;">Chargement...</div>';
  
  try {
    const resp = await fetch(`${window.API_BASE_URL}/social/post/${postId}/comments`);
    if (!resp.ok) throw new Error();
    const data = await resp.json();
    
    const comments = data.comments || [];
    const userId = String(currentUser.id || '');
    
    commentsDiv.innerHTML = `
      ${comments.map(c => `
        <div style="display:flex;gap:8px;margin-bottom:8px;">
          <div style="width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:12px;color:#fff;font-weight:700;flex-shrink:0;">
            ${(c.username||'U').charAt(0).toUpperCase()}
          </div>
          <div style="flex:1;">
            <div style="background:#3a3b3c;border-radius:14px;padding:8px 12px;">
              <span style="font-weight:600;font-size:13px;color:#e4e6eb;">${escapeHtml(c.username)}</span>
              <span style="font-size:13px;color:#e4e6eb;"> ${escapeHtml(c.content)}</span>
            </div>
            <div style="font-size:11px;color:#b0b3b8;margin-top:2px;margin-left:12px;">${c.date ? formatSocialTime(c.date) : ''}</div>
          </div>
        </div>
      `).join('')}
      <div style="display:flex;gap:8px;margin-top:8px;">
        <div style="width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:12px;color:#fff;font-weight:700;flex-shrink:0;">
          ${(currentUser.username||'U').charAt(0).toUpperCase()}
        </div>
        <div style="flex:1;">
          <textarea id="social-comment-input-${postId}" placeholder="Ecrire un commentaire..." 
            style="width:100%;min-height:32px;padding:8px 12px;border-radius:18px;border:none;background:#3a3b3c;color:#e4e6eb;font-size:13px;resize:none;box-sizing:border-box;"
            onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();submitSocialComment(${postId});}"></textarea>
        </div>
          </div>
        `;
  } catch(e) {
    commentsDiv.innerHTML = '<div style="color:#ef4444;font-size:12px;">Erreur</div>';
  }
};

window.submitSocialComment = async function(postId) {
  const input = document.getElementById(`social-comment-input-${postId}`);
  if (!input || !input.value.trim()) return;
  
  const token = typeof getAuthToken === 'function' ? getAuthToken() : null;
  if (!token) return;
  
  try {
    const resp = await fetch(`${window.API_BASE_URL}/social/post/${postId}/comment`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: input.value.trim() })
    });
    if (resp.ok) {
      input.value = '';
      openSocialComments(postId); // Rafraichir
    }
  } catch(e) {}
};

window.showShareEventPicker = function() {
  // Afficher un mini-picker d'events de l'agenda
  const agendaItems = (currentUser.agenda || []).map(key => {
    const [type, id] = key.split(':');
    if (type !== 'event') return null;
    const ev = eventsData.find(e => e.id === parseInt(id));
    return ev;
  }).filter(Boolean);
  
  if (agendaItems.length === 0) {
    showNotification('Ajoutez d\'abord des events a votre agenda !', 'info');
    return;
  }
  
  let picker = document.getElementById('event-share-picker');
  if (picker) { picker.remove(); return; }
  
  picker = document.createElement('div');
  picker.id = 'event-share-picker';
  picker.style.cssText = 'position:fixed;bottom:200px;left:50%;transform:translateX(-50%);width:90%;max-width:400px;max-height:250px;overflow-y:auto;background:#2d2d30;border-radius:14px;border:1px solid rgba(255,255,255,0.1);z-index:100002;padding:8px;box-shadow:0 8px 32px rgba(0,0,0,0.5);';
  
  picker.innerHTML = `
    <div style="font-size:12px;color:#94a3b8;padding:8px;font-weight:600;">Choisir un event a partager :</div>
    ${agendaItems.map(ev => `
      <div onclick="selectEventForShare(${ev.id},'${escapeHtml(ev.title||'')}')" style="padding:10px;border-radius:8px;cursor:pointer;color:#e4e6eb;font-size:13px;" onmouseover="this.style.background='rgba(59,130,246,0.1)'" onmouseout="this.style.background='none'">
        📅 ${escapeHtml(ev.title || 'Sans titre')} ${ev.city ? '- ' + escapeHtml(ev.city) : ''}
      </div>
    `).join('')}
  `;
  document.body.appendChild(picker);
};

window.selectEventForShare = function(eventId, title) {
  window._socialPostEventId = eventId;
  const picker = document.getElementById('event-share-picker');
  if (picker) picker.remove();
  const input = document.getElementById('social-post-input');
  if (input && !input.value.includes(title)) {
    input.value = (input.value ? input.value + '\n' : '') + '📅 ' + title;
  }
  showNotification('Event ajoute au post !', 'success');
};

window.addLinkToPost = function() {
  const url = prompt('Collez votre lien :');
  if (!url) return;
  window._socialPostLinkUrl = url;
  window._socialPostLinkTitle = url;
  const input = document.getElementById('social-post-input');
  if (input && !input.value.includes(url)) {
    input.value = (input.value ? input.value + '\n' : '') + '🔗 ' + url;
  }
  showNotification('Lien ajoute !', 'success');
};

window.openEventById = function(eventId) {
  const ev = eventsData.find(e => e.id === eventId);
  if (ev) {
    const html = buildEventPopup(ev);
    openPopupModal(html, ev);
  }
};

window.openMapFriendModal = openMapFriendModal;

function openReportModal(type, id, parentType = null, parentId = null) {
  // Déterminer le type d'affichage
  const typeLabels = {
    'event': 'événement',
    'booking': 'booking',
    'service': 'service',
    'message': 'message',
    'discussion': 'discussion',
    'review': 'avis',
    'user': 'utilisateur',
    'comment': 'commentaire'
  };
  
  const typeLabel = typeLabels[type] || type;
  
  const html = `
    <div style="padding:20px;max-width:500px;margin:0 auto;">
      <div style="text-align:center;margin-bottom:20px;">
        <div style="font-size:48px;margin-bottom:8px;">🚨</div>
        <h2 style="margin:0;font-size:20px;font-weight:700;color:#fff;">Signaler un problème</h2>
        <p style="color:var(--ui-text-muted);margin-top:8px;font-size:13px;">Vous signalez un ${typeLabel}</p>
      </div>
      
      <div style="margin-bottom:20px;">
        <div style="font-size:13px;font-weight:600;color:#fff;margin-bottom:12px;">Raison du signalement *</div>
        <div style="display:flex;flex-direction:column;gap:8px;">
          <label style="display:flex;align-items:center;gap:10px;padding:12px;border-radius:8px;border:1px solid var(--ui-card-border);cursor:pointer;transition:all 0.2s;background:rgba(15,23,42,0.5);" 
                 onmouseover="this.style.background='rgba(239,68,68,0.1)';this.style.borderColor='rgba(239,68,68,0.5)'" 
                 onmouseout="this.style.background='rgba(15,23,42,0.5)';this.style.borderColor='var(--ui-card-border)'">
            <input type="radio" name="report-reason" value="inappropriate" style="cursor:pointer;">
            <span style="flex:1;color:#fff;">Contenu inapproprié</span>
          </label>
          <label style="display:flex;align-items:center;gap:10px;padding:12px;border-radius:8px;border:1px solid var(--ui-card-border);cursor:pointer;transition:all 0.2s;background:rgba(15,23,42,0.5);" 
                 onmouseover="this.style.background='rgba(239,68,68,0.1)';this.style.borderColor='rgba(239,68,68,0.5)'" 
                 onmouseout="this.style.background='rgba(15,23,42,0.5)';this.style.borderColor='var(--ui-card-border)'">
            <input type="radio" name="report-reason" value="fake" style="cursor:pointer;">
            <span style="flex:1;color:#fff;">Information fausse / Arnaque</span>
          </label>
          <label style="display:flex;align-items:center;gap:10px;padding:12px;border-radius:8px;border:1px solid var(--ui-card-border);cursor:pointer;transition:all 0.2s;background:rgba(15,23,42,0.5);" 
                 onmouseover="this.style.background='rgba(239,68,68,0.1)';this.style.borderColor='rgba(239,68,68,0.5)'" 
                 onmouseout="this.style.background='rgba(15,23,42,0.5)';this.style.borderColor='var(--ui-card-border)'">
            <input type="radio" name="report-reason" value="offensive" style="cursor:pointer;">
            <span style="flex:1;color:#fff;">Image offensante / Contenu -16 ans</span>
          </label>
          <label style="display:flex;align-items:center;gap:10px;padding:12px;border-radius:8px;border:1px solid var(--ui-card-border);cursor:pointer;transition:all 0.2s;background:rgba(15,23,42,0.5);" 
                 onmouseover="this.style.background='rgba(239,68,68,0.1)';this.style.borderColor='rgba(239,68,68,0.5)'" 
                 onmouseout="this.style.background='rgba(15,23,42,0.5)';this.style.borderColor='var(--ui-card-border)'">
            <input type="radio" name="report-reason" value="spam" style="cursor:pointer;">
            <span style="flex:1;color:#fff;">Spam / Publicité</span>
          </label>
          <label style="display:flex;align-items:center;gap:10px;padding:12px;border-radius:8px;border:1px solid var(--ui-card-border);cursor:pointer;transition:all 0.2s;background:rgba(15,23,42,0.5);" 
                 onmouseover="this.style.background='rgba(239,68,68,0.1)';this.style.borderColor='rgba(239,68,68,0.5)'" 
                 onmouseout="this.style.background='rgba(15,23,42,0.5)';this.style.borderColor='var(--ui-card-border)'">
            <input type="radio" name="report-reason" value="harassment" style="cursor:pointer;">
            <span style="flex:1;color:#fff;">Harcèlement / Intimidation</span>
          </label>
          <label style="display:flex;align-items:center;gap:10px;padding:12px;border-radius:8px;border:1px solid var(--ui-card-border);cursor:pointer;transition:all 0.2s;background:rgba(15,23,42,0.5);" 
                 onmouseover="this.style.background='rgba(239,68,68,0.1)';this.style.borderColor='rgba(239,68,68,0.5)'" 
                 onmouseout="this.style.background='rgba(15,23,42,0.5)';this.style.borderColor='var(--ui-card-border)'">
            <input type="radio" name="report-reason" value="other" style="cursor:pointer;">
            <span style="flex:1;color:#fff;">Autre</span>
          </label>
        </div>
      </div>
      
      <div style="margin-bottom:20px;">
        <label style="display:block;font-size:13px;font-weight:600;color:#fff;margin-bottom:8px;">Détails supplémentaires (optionnel)</label>
        <textarea id="report-details" placeholder="Décrivez le problème en détail..." rows="4" 
                  style="width:100%;padding:12px;border-radius:8px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);resize:none;font-size:14px;font-family:inherit;"></textarea>
      </div>
      
      <div style="display:flex;gap:12px;">
        <button onclick="closePublishModal()" style="flex:1;padding:12px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-weight:600;">
          Annuler
        </button>
        <button onclick="submitReport('${type}', '${id}', '${parentType || ''}', '${parentId || ''}')" 
                style="flex:1;padding:12px;border-radius:999px;border:none;background:linear-gradient(135deg,#ef4444,#dc2626);color:white;font-weight:700;cursor:pointer;">
          🚨 Signaler
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
}

async function submitReport(type, id, parentType = null, parentId = null) {
  if (!currentUser || !currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  
  const reason = document.querySelector('input[name="report-reason"]:checked');
  if (!reason) {
    showNotification("⚠️ Veuillez sélectionner une raison", "warning");
    return;
  }
  
  const details = document.getElementById('report-details')?.value.trim() || '';
  
  // Récupérer les infos de l'item signalé
  let itemInfo = "";
  if (type === "event") {
    const ev = eventsData.find(e => e.id == id);
    itemInfo = ev ? `${ev.title} (${ev.city || 'N/A'})` : `Event #${id}`;
  } else if (type === "booking") {
    const b = bookingsData.find(b => b.id == id);
    itemInfo = b ? `${b.name} (${b.city || 'N/A'})` : `Booking #${id}`;
  } else if (type === "service") {
    const s = servicesData.find(s => s.id == id);
    itemInfo = s ? `${s.name} (${s.city || 'N/A'})` : `Service #${id}`;
  } else {
    itemInfo = `${type} #${id}`;
  }
  
  const reportData = {
    userId: currentUser.id ? currentUser.id.toString() : 'anonymous',
    userEmail: currentUser.email || 'N/A',
    userName: currentUser.name || 'Anonyme',
    itemType: type,
    itemId: id.toString(),
    itemInfo: itemInfo,
    parentType: parentType || null,
    parentId: parentId || null,
    reason: reason.value,
    details: details,
    reportedAt: new Date().toISOString(),
    notifyEmail: MAPEVENT_CONTACT_EMAIL // Email de destination pour les alertes
  };
  
  try {
    // Sauvegarder dans le backend
    const response = await fetch(`${window.API_BASE_URL}/user/reports`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reportData)
    });
    
    if (response.ok) {
      showNotification("🚨 Signalement envoyé ! Notre équipe va examiner ce contenu rapidement.", "success");
      closePublishModal();
    } else {
      throw new Error('Erreur serveur');
    }
  } catch (error) {
    console.error('Erreur signalement:', error);
    // Fallback : sauvegarder localement ET afficher un message avec l'email
    if (!window.moderationQueue) window.moderationQueue = [];
    window.moderationQueue.push(reportData);
    
    // Sauvegarder dans localStorage aussi
    try {
      const existingReports = JSON.parse(localStorage.getItem('pendingReports') || '[]');
      existingReports.push(reportData);
      localStorage.setItem('pendingReports', JSON.stringify(existingReports));
    } catch (e) {
      console.error('Erreur sauvegarde locale:', e);
    }
    
    showNotification(`🚨 Signalement enregistré. En cas d'urgence, contactez : ${MAPEVENT_CONTACT_EMAIL}`, "success");
    closePublishModal();
  }
}

function openPaymentModal(type, id, action) {
  const item = type === "booking" ? bookingsData.find(b => b.id === id) : servicesData.find(s => s.id === id);
  const itemName = item ? (item.name || item.title || `Contact ${type}`) : "Contact";
  
  const html = `
    <div style="padding:10px;text-align:center;">
      <div style="font-size:48px;margin-bottom:16px;">💳</div>
      <h2 style="margin:0 0 10px;font-size:18px;">Obtenir le contact</h2>
      <p style="color:var(--ui-text-muted);margin-bottom:8px;font-size:13px;">${escapeHtml(itemName)}</p>
      <p style="color:var(--ui-text-muted);margin-bottom:20px;font-size:12px;">Choisissez votre option :</p>
      
      <div style="display:grid;gap:10px;margin-bottom:16px;">
        <button onclick="processContactPayment('${type}', ${id})" style="padding:14px;border-radius:12px;border:2px solid #00ffc3;background:rgba(0,255,195,0.1);color:#00ffc3;font-weight:700;cursor:pointer;text-align:left;display:flex;justify-content:space-between;align-items:center;">
          <span>💳 Payer CHF 1.–</span>
          <span style="font-size:12px;color:var(--ui-text-muted);">Immédiat</span>
        </button>
        
        <button onclick="openSubscriptionModal()" style="padding:14px;border-radius:12px;border:2px solid #8b5cf6;background:rgba(139,92,246,0.1);color:#a78bfa;font-weight:700;cursor:pointer;text-align:left;display:flex;justify-content:space-between;align-items:center;">
          <span>💎 Voir les abonnements</span>
          <span style="font-size:12px;color:var(--ui-text-muted);">À partir de 5.–/mois</span>
        </button>
        
        <button onclick="addToCart('${type}', ${id})" style="padding:14px;border-radius:12px;border:2px solid #f59e0b;background:rgba(245,158,11,0.1);color:#f59e0b;font-weight:700;cursor:pointer;text-align:left;display:flex;justify-content:space-between;align-items:center;">
          <span>🛒 Ajouter au panier</span>
          <span style="font-size:12px;color:var(--ui-text-muted);">Payer plus tard</span>
        </button>
      </div>
      
      <button onclick="closePublishModal()" style="width:100%;padding:10px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;">
        Annuler
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

// Son de paiement
function playPaymentSound() {
  try {
    const audio = new Audio('/assets/popopo.m4a');
    audio.volume = 0.7;
    audio.play().catch(e => {
      console.log("Son de paiement non disponible", e);
    });
  } catch (e) {
    console.log("Son de paiement non disponible", e);
  }
}

function addToCart(type, id) {
  const key = `${type}:${id}`;
  
  // Vérifier si déjà dans le panier
  if (cart.some(item => item.key === key)) {
    showNotification("⚠️ Déjà dans le panier", "warning");
    return;
  }
  
  // Trouver l'item
  const data = type === "booking" ? bookingsData : servicesData;
  const item = data.find(i => i.id === id);
  
  if (item) {
    cart.push({
      key,
      type,
      id,
      name: item.name || item.title || `Contact ${type}`,
      price: 1.0
    });
    
    updateCartCount();
    showNotification(`🛒 ${item.name || item.title} ajouté au panier !`, "success");
    closePublishModal();
  }
}

function removeFromCart(key) {
  cart = cart.filter(item => item.key !== key);
  updateCartCount();
  showNotification("🗑️ Retiré du panier", "info");
  openCartModal(); // Rafraîchir
}

function updateCartCount() {
  const cartCount = document.getElementById("cart-count");
  if (cartCount) {
    if (cart.length > 0) {
      cartCount.textContent = cart.length;
      cartCount.style.display = "flex";
    } else {
      cartCount.style.display = "none";
    }
  }
}

function openCartModal() {
  if (cart.length === 0) {
    const html = `
      <div style="padding:20px;text-align:center;">
        <div style="font-size:64px;margin-bottom:16px;">🛒</div>
        <h2 style="margin:0 0 10px;font-size:18px;">Votre panier est vide</h2>
        <p style="color:var(--ui-text-muted);margin-bottom:20px;">Ajoutez des contacts depuis les popups !</p>
        <button onclick="closePublishModal()" style="padding:10px 20px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;">
          Fermer
        </button>
      </div>
    `;
    document.getElementById("publish-modal-inner").innerHTML = html;
    const backdrop = document.getElementById("publish-modal-backdrop");
  if (backdrop) {
    backdrop.style.display = "flex";
    backdrop.style.paddingTop = "40px";
    backdrop.style.paddingBottom = "40px";
    backdrop.style.boxSizing = "border-box";
  }
    return;
  }
  
  const total = cart.reduce((sum, item) => sum + item.price, 0);
  
  const html = `
    <div style="padding:10px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
        <h2 style="margin:0;font-size:18px;">🛒 Mon Panier</h2>
        <button onclick="closePublishModal()" style="background:none;border:none;font-size:20px;cursor:pointer;color:var(--ui-text-muted);">✕</button>
      </div>
      
      <div style="max-height:300px;overflow-y:auto;margin-bottom:16px;">
        ${cart.map(item => `
          <div style="display:flex;justify-content:space-between;align-items:center;padding:12px;background:rgba(15,23,42,0.5);border-radius:8px;margin-bottom:8px;border:1px solid var(--ui-card-border);">
            <div style="flex:1;">
              <div style="font-weight:600;margin-bottom:4px;">${escapeHtml(item.name)}</div>
              <div style="font-size:11px;color:var(--ui-text-muted);">${item.type === 'booking' ? '🎤 Booking' : '🔧 Service'}</div>
            </div>
            <div style="text-align:right;margin-right:12px;">
              <div style="font-weight:700;color:#00ffc3;">CHF ${item.price.toFixed(2)}</div>
            </div>
            <button onclick="removeFromCart('${item.key}')" style="background:none;border:none;color:#ef4444;cursor:pointer;font-size:18px;padding:4px;">🗑️</button>
          </div>
        `).join('')}
      </div>
      
      <div style="padding:12px;background:rgba(0,255,195,0.1);border:1px solid rgba(0,255,195,0.3);border-radius:12px;margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <span style="font-weight:700;font-size:16px;">Total</span>
          <span style="font-weight:800;font-size:20px;color:#00ffc3;">CHF ${total.toFixed(2)}</span>
        </div>
        <div style="font-size:11px;color:var(--ui-text-muted);text-align:center;">${cart.length} contact(s)</div>
      </div>
      
      <div style="display:grid;gap:10px;margin-bottom:12px;">
        <button onclick="checkoutCart()" style="width:100%;padding:14px;border-radius:999px;border:none;background:var(--btn-main-bg);color:var(--btn-main-text);font-weight:700;cursor:pointer;font-size:16px;">
          💳 Payer ${total.toFixed(2)} CHF
        </button>
        
        <button onclick="openSubscriptionModal()" style="width:100%;padding:12px;border-radius:999px;border:2px solid #8b5cf6;background:rgba(139,92,246,0.1);color:#a78bfa;font-weight:600;cursor:pointer;">
          💎 Voir les abonnements (économisez !)
        </button>
        
        <button onclick="openEcoMissionModal()" style="width:100%;padding:12px;border-radius:999px;border:2px solid #22c55e;background:rgba(34,197,94,0.1);color:#22c55e;font-weight:600;cursor:pointer;">
          🌍 Faire un don pour la planète
        </button>
      </div>
      
      <button onclick="closePublishModal()" style="width:100%;padding:10px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;">
        Continuer mes achats
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

async function processCartCheckout() {
  if (cart.length === 0) return;
  
  if (!currentUser || !currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  
  const total = cart.reduce((sum, item) => sum + item.price, 0);
  const count = cart.length;
  
  try {
    showNotification("💳 Redirection vers le paiement...", "info");
    
    // Créer une session Stripe Checkout
    const response = await fetch(`${window.API_BASE_URL}/payments/create-checkout-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId: currentUser.id.toString(),
        paymentType: 'cart',
        items: cart.map(item => ({
          type: item.type,
          id: item.id,
          price: item.price
        })),
        amount: total,
        currency: 'CHF',
        email: currentUser.email
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Erreur lors de la création de la session');
    }
    
    const { sessionId, publicKey } = await response.json();
    
    // Initialiser Stripe si pas encore fait
    if (!stripe && publicKey) {
      initStripe(publicKey);
    }
    
    if (!stripe) {
      throw new Error('Stripe non disponible');
    }
    
    // Rediriger vers Stripe Checkout
    const result = await stripe.redirectToCheckout({ sessionId });
    
    if (result.error) {
      showNotification(`❌ Erreur : ${result.error.message}`, "error");
    }
  } catch (error) {
    console.error('Erreur checkout:', error);
    showNotification(`❌ Erreur lors du paiement : ${error.message}`, "error");
  }
}

// Fonction de compatibilité (fallback si Stripe échoue)
function checkoutCart() {
  processCartCheckout().catch(() => {
    // Fallback : simulation locale si l'API échoue
    const total = cart.reduce((sum, item) => sum + item.price, 0);
    const count = cart.length;
    cart.forEach(item => {
      if (!paidContacts.includes(item.key)) {
        paidContacts.push(item.key);
      }
      if (!currentUser.agenda.includes(item.key)) {
        currentUser.agenda.push(item.key);
      }
    });
    playPaymentSound();
    cart = [];
    updateCartCount();
    showNotification(`✅ Paiement simulé (mode démo) : ${total.toFixed(2)} CHF`, "info");
    closePublishModal();
    refreshMarkers();
  });
}

async function processContactPayment(type, id) {
  if (!currentUser || !currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  
  try {
    showNotification("💳 Redirection vers le paiement...", "info");
    
    // Créer une session Stripe Checkout
    const response = await fetch(`${window.API_BASE_URL}/payments/create-checkout-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId: currentUser.id.toString(),
        paymentType: 'contact',
        itemType: type,
        itemId: id,
        amount: 1.00, // CHF 1.–
        currency: 'CHF',
        email: currentUser.email
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Erreur lors de la création de la session');
    }
    
    const { sessionId, publicKey } = await response.json();
    
    // Initialiser Stripe si pas encore fait
    if (!stripe && publicKey) {
      initStripe(publicKey);
    }
    
    if (!stripe) {
      throw new Error('Stripe non disponible');
    }
    
    // Rediriger vers Stripe Checkout
    const result = await stripe.redirectToCheckout({ sessionId });
    
    if (result.error) {
      showNotification(`❌ Erreur : ${result.error.message}`, "error");
    }
  } catch (error) {
    console.error('Erreur paiement:', error);
    showNotification(`❌ Erreur lors du paiement : ${error.message}`, "error");
  }
}

// Fonction de compatibilité (fallback si Stripe échoue)
function simulatePayment(type, id) {
  processContactPayment(type, id).catch(() => {
    // Fallback : simulation locale si l'API échoue
    const key = `${type}:${id}`;
    if (!paidContacts.includes(key)) {
      paidContacts.push(key);
    }
    if (!currentUser.agenda.includes(key)) {
      currentUser.agenda.push(key);
    }
    playPaymentSound();
    showNotification("✅ Paiement simulé (mode démo)", "info");
    closePublishModal();
    refreshMarkers();
  });
}

// ============================================
