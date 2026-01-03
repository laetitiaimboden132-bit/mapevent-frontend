// ===============================
// COGNITO AUTH (Google) - PKCE SPA
// ===============================
const COGNITO = {
  domain: "https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com",
  clientId: "63rm6h0m26q41lotbho6704dod",
  redirectUri: "https://mapevent.world/",
  scopes: ["openid", "email", "profile"],
};

function base64UrlEncode(arrayBuffer) {
  const bytes = new Uint8Array(arrayBuffer);
  let binary = "";
  bytes.forEach((b) => (binary += String.fromCharCode(b)));
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function randomString(len = 64) {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~";
  const rnd = new Uint8Array(len);
  crypto.getRandomValues(rnd);
  return Array.from(rnd).map((x) => chars[x % chars.length]).join("");
}

async function sha256(str) {
  const data = new TextEncoder().encode(str);
  return crypto.subtle.digest("SHA-256", data);
}

async function pkceChallengeFromVerifier(verifier) {
  const digest = await sha256(verifier);
  return base64UrlEncode(digest);
}

function authSave(key, val) {
  sessionStorage.setItem(key, val);
}
function authLoad(key) {
  return sessionStorage.getItem(key);
}
function authClearTemp() {
  ["pkce_verifier", "oauth_state"].forEach((k) => sessionStorage.removeItem(k));
}

// Fonction utilitaire pour sauvegarder avec gestion de quota localStorage
function safeSetItem(key, value) {
  try {
    localStorage.setItem(key, value);
    return true;
  } catch (e) {
    if (e.name === 'QuotaExceededError' || e.message.includes('quota')) {
      console.warn(`⚠️ localStorage plein, nettoyage ULTRA-AGRESSIF pour ${key}...`);
      
      // ÉTAPE 1: Sauvegarder les données critiques AVANT tout nettoyage
      const criticalData = {
        tokens: localStorage.getItem('cognito_tokens'),
        existingUser: key === 'currentUser' ? null : localStorage.getItem('currentUser')
      };
      
      // ÉTAPE 2: Nettoyage ULTRA-AGRESSIF - Supprimer TOUT sauf les données critiques
      try {
        // Supprimer toutes les clés sauf celles qu'on veut garder
        const keysToKeep = ['cognito_tokens']; // On va tout supprimer sauf ça
        const allKeys = [];
        for (let i = 0; i < localStorage.length; i++) {
          const k = localStorage.key(i);
          if (k && !keysToKeep.includes(k)) {
            allKeys.push(k);
          }
        }
        
        // Supprimer toutes les clés non critiques
        allKeys.forEach(k => {
          try {
            localStorage.removeItem(k);
          } catch (err) {
            // Ignorer les erreurs de suppression individuelle
          }
        });
        
        // ÉTAPE 3: Si c'est currentUser, créer une version MINIMALE
        if (key === 'currentUser') {
          try {
            const userObj = JSON.parse(value);
            // GARDER UNIQUEMENT les champs absolument essentiels
            const minimalUser = {
              id: userObj.id || null,
              email: userObj.email || '',
              username: userObj.username || '',
              name: userObj.name || '',
              firstName: userObj.firstName || '',
              lastName: userObj.lastName || '',
              avatar: userObj.avatar || '👤',
              profilePhoto: userObj.profilePhoto || null,
              avatarDescription: userObj.avatarDescription || '',
              isLoggedIn: userObj.isLoggedIn || false,
              profileComplete: userObj.profileComplete || false,
              subscription: userObj.subscription || 'free',
              role: userObj.role || 'user',
              postalAddress: userObj.postalAddress || '',
              provider: userObj.provider || null,
              googleValidated: userObj.googleValidated || false,
              // Initialiser les tableaux vides (pas de données)
              agenda: [],
              favorites: [],
              likes: [],
              participating: [],
              alerts: [],
              statusAlerts: [],
              proximityAlerts: [],
              eventAlarms: [],
              reviews: {},
              addresses: [],
              friends: [],
              friendRequests: [],
              sentRequests: [],
              blockedUsers: [],
              conversations: [],
              groups: [],
              profileLinks: [],
              history: [],
              photos: [],
              profilePhotos: [],
              eventStatusHistory: {},
              smsNotifications: 0,
              smsLimit: 0,
              emailNotifications: 0,
              notificationPreferences: { email: true, sms: false },
              privacySettings: {
                showName: true,
                showAvatar: true,
                showBio: true,
                showEmail: false,
                showAddresses: false,
                showFavorites: true,
                showAgenda: true,
                showParticipating: true,
                showFriends: true,
                showActivity: true
              },
              lastSeen: new Date().toISOString()
            };
            value = JSON.stringify(minimalUser);
            console.log(`✅ currentUser réduit à la version minimale (${value.length} caractères)`);
          } catch (parseError) {
            console.warn('⚠️ Impossible de parser currentUser, utilisation de la valeur originale réduite');
            // Créer un objet minimal même si le parsing échoue
            value = JSON.stringify({
              id: null,
              email: '',
              username: '',
              name: '',
              isLoggedIn: false,
              profileComplete: false,
              subscription: 'free',
              role: 'user'
            });
          }
        }
        
        // ÉTAPE 4: Restaurer les tokens si nécessaire
        if (criticalData.tokens && !localStorage.getItem('cognito_tokens')) {
          try {
            localStorage.setItem('cognito_tokens', criticalData.tokens);
          } catch (tokenError) {
            console.warn('⚠️ Impossible de restaurer les tokens:', tokenError);
          }
        }
        
        // ÉTAPE 5: Essayer de sauvegarder la nouvelle valeur
        try {
          localStorage.setItem(key, value);
          console.log(`✅ ${key} sauvegardé après nettoyage ultra-agressif`);
          
          // Restaurer l'ancien currentUser si on vient de sauvegarder autre chose
          if (key !== 'currentUser' && criticalData.existingUser) {
            try {
              // Essayer de restaurer l'ancien currentUser après avoir sauvegardé la nouvelle clé
              const existingUserObj = JSON.parse(criticalData.existingUser);
              const minimalExistingUser = {
                id: existingUserObj.id || null,
                email: existingUserObj.email || '',
                username: existingUserObj.username || '',
                name: existingUserObj.name || '',
                firstName: existingUserObj.firstName || '',
                lastName: existingUserObj.lastName || '',
                avatar: existingUserObj.avatar || '👤',
                profilePhoto: existingUserObj.profilePhoto || null,
                isLoggedIn: existingUserObj.isLoggedIn || false,
                profileComplete: existingUserObj.profileComplete || false,
                subscription: existingUserObj.subscription || 'free',
                role: existingUserObj.role || 'user',
                postalAddress: existingUserObj.postalAddress || '',
                provider: existingUserObj.provider || null
              };
              localStorage.setItem('currentUser', JSON.stringify(minimalExistingUser));
            } catch (restoreError) {
              console.warn('⚠️ Impossible de restaurer currentUser:', restoreError);
            }
          }
          
          if (typeof showNotification === 'function') {
            showNotification('✅ Stockage nettoyé. Vos données essentielles sont conservées.', 'success');
          }
          return true;
        } catch (e2) {
          console.error(`❌ Impossible de sauvegarder ${key} même après nettoyage ultra-agressif:`, e2);
          
          // DERNIÈRE TENTATIVE : Vider complètement et ne garder QUE les tokens
          try {
            const tokens = criticalData.tokens;
            localStorage.clear();
            if (tokens) {
              localStorage.setItem('cognito_tokens', tokens);
            }
            
            // Essayer de sauvegarder la version minimale
            if (key === 'currentUser') {
              localStorage.setItem(key, value);
              console.log(`✅ localStorage vidé complètement, ${key} sauvegardé (version minimale)`);
            } else {
              // Pour les autres clés, essayer quand même
              localStorage.setItem(key, value);
            }
            
            if (typeof showNotification === 'function') {
              showNotification('⚠️ Stockage local vidé. Vos données sont sauvegardées sur le serveur.', 'warning');
            }
            return true;
          } catch (e3) {
            console.error(`❌ ÉCHEC TOTAL pour ${key}:`, e3);
            if (typeof showNotification === 'function') {
              showNotification('⚠️ Impossible de sauvegarder localement. Vos données sont sur le serveur.', 'warning');
            }
            return false;
          }
        }
      } catch (cleanupError) {
        console.error(`❌ Erreur lors du nettoyage:`, cleanupError);
        return false;
      }
    } else {
      // Erreur non liée au quota
      console.error(`❌ Erreur lors de la sauvegarde de ${key}:`, e);
      return false;
    }
  }
}

function saveSession(tokens) {
  safeSetItem("cognito_tokens", JSON.stringify(tokens));
}
function loadSession() {
  const raw = localStorage.getItem("cognito_tokens");
  return raw ? JSON.parse(raw) : null;
}
function clearSession() {
  localStorage.removeItem("cognito_tokens");
}

function decodeJwtPayload(token) {
  const payload = token.split(".")[1];
  const pad = payload.length % 4 === 0 ? "" : "=".repeat(4 - (payload.length % 4));
  const b64 = (payload + pad).replace(/-/g, "+").replace(/_/g, "/");
  const json = atob(b64);
  return JSON.parse(json);
}

// 1) Lance login Google (Hosted UI Cognito)
async function startGoogleLogin() {
  const verifier = randomString(80);
  const challenge = await pkceChallengeFromVerifier(verifier);
  const state = randomString(24);

  authSave("pkce_verifier", verifier);
  authSave("oauth_state", state);

  const authorizeUrl =
    `${COGNITO.domain}/oauth2/authorize` +
    `?client_id=${encodeURIComponent(COGNITO.clientId)}` +
    `&response_type=code` +
    `&scope=${encodeURIComponent(COGNITO.scopes.join(" "))}` +
    `&redirect_uri=${encodeURIComponent(COGNITO.redirectUri)}` +
    `&state=${encodeURIComponent(state)}` +
    `&code_challenge=${encodeURIComponent(challenge)}` +
    `&code_challenge_method=S256` +
    `&identity_provider=Google`;

  window.location.assign(authorizeUrl);
}

// 2) Traite le retour Cognito: https://mapevent.world/?code=...&state=...
async function handleCognitoCallbackIfPresent() {
  console.log('🔍 handleCognitoCallbackIfPresent appelé', {
    url: window.location.href,
    hasCode: !!new URL(window.location.href).searchParams.get("code"),
    hasState: !!new URL(window.location.href).searchParams.get("state"),
    hasError: !!new URL(window.location.href).searchParams.get("error")
  });
  
  const url = new URL(window.location.href);
  const code = url.searchParams.get("code");
  const state = url.searchParams.get("state");
  const error = url.searchParams.get("error");

  console.log('📋 Paramètres OAuth:', { code: !!code, state: !!state, error });

  if (error) {
    console.error('❌ Erreur OAuth:', error);
    showNotification("❌ Erreur login: " + error, "error");
    return;
  }
  if (!code) {
    console.log('ℹ️ Pas de code OAuth dans l\'URL - pas un callback');
    return; // pas un callback
  }
  
  console.log('✅ Code OAuth détecté - Traitement du callback...');

  const expectedState = authLoad("oauth_state");
  if (!state || state !== expectedState) {
    showNotification("❌ State OAuth invalide (sécurité).", "error");
    return;
  }

  const verifier = authLoad("pkce_verifier");
  if (!verifier) {
    showNotification("❌ PKCE verifier manquant.", "error");
    return;
  }

  const body = new URLSearchParams({
    grant_type: "authorization_code",
    client_id: COGNITO.clientId,
    code,
    redirect_uri: COGNITO.redirectUri,
    code_verifier: verifier,
  });

  const tokenRes = await fetch(`${COGNITO.domain}/oauth2/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });

  if (!tokenRes.ok) {
    const txt = await tokenRes.text();
    console.warn("Token error:", txt);
    showNotification("❌ Impossible d’échanger le code (token).", "error");
    return;
  }

  const tokens = await tokenRes.json();
  saveSession(tokens);
  authClearTemp();

  // Nettoyer l’URL (enlever ?code=...&state=...)
  url.searchParams.delete("code");
  url.searchParams.delete("state");
  url.searchParams.delete("session_state");
  window.history.replaceState({}, document.title, url.toString());

  // Construire un user "MapEvent"
  try {
    const payload = decodeJwtPayload(tokens.id_token);
    
    // Initialiser currentUser avec toutes les propriétés nécessaires
    currentUser = {
      isLoggedIn: true,
      provider: "google",
      email: payload.email || "",
      name: payload.name || payload.email || "Utilisateur",
      avatar: payload.picture || "👤",
      lastLoginAt: new Date().toISOString(),
      sub: payload.sub,
      // Propriétés nécessaires pour éviter les erreurs undefined
      likes: [],
      agenda: [],
      participating: [],
      favorites: [],
      friendRequests: [],
      eventStatusHistory: {},
      profileComplete: false, // Flag pour savoir si le profil est complet
      username: null,
      profilePhoto: payload.picture || null,
      postalAddress: null,
      password: null
    };
    
    localStorage.setItem("currentUser", JSON.stringify(currentUser));
    updateUserUI();
    updateAccountButton();
    
    // Essayer de synchroniser avec le backend
    console.log('🔐 Cognito callback - Synchronisation avec backend...', {
      email: currentUser.email,
      name: currentUser.name,
      sub: currentUser.sub
    });
    
    try {
      const API_BASE_URL = 'https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default';
      const syncResponse = await fetch(`${API_BASE_URL}/api/user/oauth/google`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tokens.id_token}`
        },
        body: JSON.stringify({
          email: currentUser.email,
          name: currentUser.name,
          sub: currentUser.sub,
          picture: payload.picture || null
        })
      });
      
      if (syncResponse.ok) {
        const syncData = await syncResponse.json();
        console.log('✅ Synchronisation backend réussie:', syncData);
        
        // LOGIQUE PROFESSIONNELLE MAPEVENT :
        // 1. Après validation Google → Vérifier si nouvel utilisateur OU profil incomplet
        // 2. Si NOUVEL utilisateur OU profil incomplet → Afficher formulaire d'inscription MapEvent
        // 3. Si utilisateur EXISTANT avec profil complet → Connexion directe, pas de formulaire
        const isNewUser = syncData.isNewUser === true;
        const profileComplete = syncData.profileComplete === true;
        
        // Vérifier les données utilisateur essentielles
        const user = syncData.user || {};
        const hasUsername = user.username && user.username.trim().length > 0;
        const hasPostalAddress = user.postal_address || user.postalAddress;
        const hasProfilePhoto = user.profile_photo_url || user.profilePhoto;
        
        // Le backend calcule déjà profileComplete en fonction de password_hash et username personnalisé
        // MAIS on vérifie aussi les données essentielles côté frontend pour plus de sécurité
        console.log('📊 État utilisateur après validation Google:', {
          isNewUser: isNewUser,
          profileComplete: profileComplete,
          userEmail: user.email,
          userId: user.id,
          username: user.username,
          hasUsername: hasUsername,
          hasPostalAddress: !!hasPostalAddress,
          hasProfilePhoto: !!hasProfilePhoto,
          userObject: user
        });
        
        // VÉRIFICATION CRITIQUE : Vérifier d'abord si le profil est déjà complet dans localStorage
        // Si oui, NE JAMAIS afficher le formulaire même si le backend dit autre chose
        const savedUser = localStorage.getItem('currentUser');
        let savedUserObj = null;
        try {
          if (savedUser) {
            savedUserObj = JSON.parse(savedUser);
          }
        } catch (e) {
          console.warn('⚠️ Impossible de parser currentUser depuis localStorage:', e);
        }
        
        const isProfileAlreadyComplete = (savedUserObj && savedUserObj.profileComplete === true) ||
                                         (currentUser && currentUser.profileComplete === true);
        
        // Afficher le formulaire si :
        // - Profil PAS déjà complet dans localStorage ET
        // - (Nouvel utilisateur OU Profil incomplet selon backend OU Données essentielles manquantes)
        const shouldShowForm = !isProfileAlreadyComplete && (isNewUser || !profileComplete || !hasUsername || !hasPostalAddress || !hasProfilePhoto);
        
        if (shouldShowForm) {
          // Afficher le formulaire IMMÉDIATEMENT
          console.log('📝 Affichage formulaire d\'inscription', {
            isNewUser,
            profileComplete,
            hasUsername,
            hasPostalAddress,
            hasProfilePhoto,
            isProfileAlreadyComplete,
            userEmail: user.email,
            reason: isNewUser ? 'nouvel utilisateur' : !profileComplete ? 'profil incomplet (backend)' : !hasUsername ? 'pas de username' : !hasPostalAddress ? 'pas d\'adresse' : 'pas de photo'
          });
          
          // FORCER isLoggedIn à false pour forcer l'affichage du formulaire
          currentUser.isLoggedIn = false;
          currentUser.profileComplete = false;
          
          // Appeler la fonction d'affichage du formulaire avec les données utilisateur
          displayRegistrationFormAfterGoogleAuth(user);
          
          // Attendre un peu et vérifier que le formulaire s'est bien affiché
          setTimeout(() => {
            const modal = document.getElementById('publish-modal-backdrop');
            if (!modal || modal.style.display === 'none') {
              console.warn('⚠️ Le formulaire ne s\'est pas affiché, nouvelle tentative...');
              displayRegistrationFormAfterGoogleAuth(syncData.user);
            } else {
              console.log('✅ Formulaire d\'inscription affiché avec succès');
            }
          }, 500);
          
          return; // Sortir ici pour éviter le code suivant
        } else {
          // CAS 2: Utilisateur EXISTANT avec profil complet → Connexion directe à MapEvent
          // IMPORTANT: Ne JAMAIS afficher le formulaire si profileComplete === true
          console.log('✅ Utilisateur existant avec profil complet - Connexion directe à MapEvent (PAS de formulaire)', {
            profileComplete: profileComplete,
            hasUsername: hasUsername,
            hasPostalAddress: !!hasPostalAddress,
            hasProfilePhoto: !!hasProfilePhoto,
            userEmail: user.email
          });
          
          if (syncData.user) {
            currentUser = {
              ...currentUser,
              ...syncData.user,
              // Mapper les champs du backend vers le format frontend
              profilePhoto: syncData.user.profile_photo_url || syncData.user.avatar || syncData.user.profilePhoto || null,
              avatar: syncData.user.avatar || syncData.user.profile_photo_url || syncData.user.profilePhoto || '👤',
              isLoggedIn: true,
              provider: 'google',
              profileComplete: true, // GARANTIR que profileComplete est true
              googleValidated: true,
              // Conserver les données essentielles
              username: syncData.user.username || currentUser.username,
              postalAddress: syncData.user.postal_address || syncData.user.postalAddress || currentUser.postalAddress
            };
            // Sauvegarder dans localStorage avec profileComplete: true
            safeSetItem("currentUser", JSON.stringify(currentUser));
            updateAccountButton();
            updateUserUI();
            
            console.log('✅ Profil utilisateur sauvegardé avec profileComplete: true', {
              email: currentUser.email,
              username: currentUser.username,
              profileComplete: currentUser.profileComplete
            });
          }
          
          showNotification(`✅ Connexion réussie ! Bienvenue ${currentUser.username || currentUser.name || currentUser.email}`, "success");
          
          // Nettoyer l'URL des paramètres OAuth
          if (window.history && window.history.replaceState) {
            window.history.replaceState({}, document.title, window.location.pathname);
          }
          
          // FERMER le formulaire s'il était ouvert (sécurité supplémentaire)
          closePublishModal();
        }
      } else {
        throw new Error(`Backend sync failed: ${syncResponse.status}`);
      }
    } catch (apiError) {
      console.warn('⚠️ Erreur lors de l\'appel API backend:', apiError);
      
      // VÉRIFIER SI LE PROFIL EST DÉJÀ COMPLET AVANT D'AFFICHER LE FORMULAIRE
      // Si currentUser.profileComplete === true dans localStorage, ne JAMAIS afficher le formulaire
      const savedUser = localStorage.getItem('currentUser');
      let savedUserObj = null;
      try {
        if (savedUser) {
          savedUserObj = JSON.parse(savedUser);
        }
      } catch (e) {
        console.warn('⚠️ Impossible de parser currentUser depuis localStorage:', e);
      }
      
      // Vérifier aussi dans currentUser actuel (peut être défini plus haut)
      const isProfileComplete = (savedUserObj && savedUserObj.profileComplete === true) || 
                                 (currentUser && currentUser.profileComplete === true);
      
      if (isProfileComplete) {
        console.log('✅ Profil déjà complet - Connexion directe sans formulaire (fallback)');
        // Restaurer l'utilisateur depuis localStorage ou utiliser currentUser
        if (savedUserObj) {
          currentUser = {
            ...currentUser,
            ...savedUserObj,
            isLoggedIn: true,
            profileComplete: true // GARANTIR que profileComplete est true
          };
        } else {
          currentUser.profileComplete = true;
          currentUser.isLoggedIn = true;
        }
        safeSetItem("currentUser", JSON.stringify(currentUser));
        updateAccountButton();
        updateUserUI();
        showNotification(`✅ Connexion réussie ! Bienvenue ${currentUser.name || currentUser.email}`, "success");
        
        // Nettoyer l'URL des paramètres OAuth
        if (window.history && window.history.replaceState) {
          window.history.replaceState({}, document.title, window.location.pathname);
        }
        
        // FERMER le formulaire s'il était ouvert (sécurité supplémentaire)
        closePublishModal();
        return; // Ne JAMAIS afficher le formulaire si le profil est complet
      }
      
      console.log('🔄 Erreur API détectée - Affichage formulaire d\'inscription (fallback)');
      
      // En cas d'erreur (CORS ou réseau), on assume que c'est un nouvel utilisateur
      // et on affiche le formulaire pour qu'il puisse compléter son profil
      
      // Sauvegarder les données Google dans currentUser (pas encore connecté à MapEvent)
      currentUser = {
        ...currentUser,
        isLoggedIn: false, // Pas encore connecté à MapEvent
        provider: 'google',
        profileComplete: false,
        googleValidated: true, // Google validé mais pas encore inscrit à MapEvent
        likes: currentUser.likes || [],
        agenda: currentUser.agenda || [],
        participating: currentUser.participating || [],
        favorites: currentUser.favorites || [],
        friendRequests: currentUser.friendRequests || [],
        eventStatusHistory: currentUser.eventStatusHistory || {}
      };
      localStorage.setItem("currentUser", JSON.stringify(currentUser));
      
      // Pré-remplir registerData avec les données Google disponibles
      const nameParts = (currentUser.name || '').split(' ');
      registerData = {
        email: currentUser.email || '',
        username: '',
        password: '',
        passwordConfirm: '',
        firstName: nameParts[0] || '',
        lastName: nameParts.slice(1).join(' ') || '',
        profilePhoto: (currentUser.avatar && currentUser.avatar.startsWith('http')) ? currentUser.avatar : (currentUser.profilePhoto || ''),
        postalAddress: '',
        avatarId: 1,
        avatarDescription: '',
        addresses: [],
        emailVerificationCode: null,
        emailVerified: true, // Google email déjà vérifié
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
      
      // Nettoyer l'URL des paramètres OAuth AVANT d'afficher le formulaire
      if (window.history && window.history.replaceState) {
        window.history.replaceState({}, document.title, window.location.pathname);
      }
      
      // Afficher le formulaire avec plusieurs tentatives
      const showFormWithRetry = (attempt = 1, maxAttempts = 5) => {
        console.log(`🔍 Tentative ${attempt}/${maxAttempts} d'affichage du formulaire (fallback erreur API)...`);
        
        if (typeof window.showProRegisterForm === 'function') {
          console.log('✅ Affichage formulaire d\'inscription MapEvent (fallback)');
          try {
            window.showProRegisterForm();
            return;
          } catch (e) {
            console.error('❌ Erreur lors de l\'appel showProRegisterForm:', e);
          }
        } else if (typeof showProRegisterForm === 'function') {
          console.log('✅ Affichage formulaire d\'inscription MapEvent (fallback)');
          try {
            showProRegisterForm();
            return;
          } catch (e) {
            console.error('❌ Erreur lors de l\'appel showProRegisterForm:', e);
          }
        }
        
        if (attempt < maxAttempts) {
          console.log(`⏳ Réessai dans ${attempt * 200}ms...`);
          setTimeout(() => showFormWithRetry(attempt + 1, maxAttempts), attempt * 200);
        } else {
          console.error('❌ showProRegisterForm toujours non disponible après ' + maxAttempts + ' tentatives');
          // Dernière tentative : afficher le modal manuellement
          const backdrop = document.getElementById('publish-modal-backdrop');
          const modal = document.getElementById('publish-modal-inner');
          if (backdrop && modal) {
            console.log('🔄 Affichage modal manuel...');
            backdrop.style.display = 'flex';
            backdrop.style.visibility = 'visible';
            backdrop.style.opacity = '1';
            backdrop.style.zIndex = '99999';
            // Appeler showProRegisterForm une dernière fois
            setTimeout(() => {
              if (typeof window.showProRegisterForm === 'function') {
                window.showProRegisterForm();
              } else if (typeof showProRegisterForm === 'function') {
                showProRegisterForm();
              }
            }, 100);
          }
        }
      };
      
      // Démarrer les tentatives après un court délai
      setTimeout(() => showFormWithRetry(), 300);
    }
  } catch (e) {
    console.warn(e);
    showNotification("✅ Connecté (token reçu).", "success");
  }
}

// Fonction centralisée pour afficher le formulaire d'inscription après validation Google
function displayRegistrationFormAfterGoogleAuth(backendUser) {
  console.log('🎯 displayRegistrationFormAfterGoogleAuth appelé', { backendUser: !!backendUser });
  
  // VÉRIFICATION CRITIQUE : Ne JAMAIS afficher le formulaire si le profil est déjà complet
  // Même si isLoggedIn est false, si profileComplete est true, c'est que l'utilisateur a déjà rempli le formulaire
  if (currentUser && currentUser.profileComplete === true) {
    console.log('⚠️ Tentative d\'affichage formulaire alors que profileComplete === true - Bloqué (profil déjà complet)');
    return; // Ne JAMAIS afficher le formulaire si le profil est déjà complet
  }
  
  // Vérifier aussi dans localStorage au cas où
  const savedUser = localStorage.getItem('currentUser');
  if (savedUser) {
    try {
      const savedUserObj = JSON.parse(savedUser);
      if (savedUserObj && savedUserObj.profileComplete === true) {
        console.log('⚠️ Tentative d\'affichage formulaire alors que profileComplete === true dans localStorage - Bloqué');
        return; // Ne JAMAIS afficher le formulaire si le profil est déjà complet
      }
    } catch (e) {
      console.warn('⚠️ Impossible de parser currentUser depuis localStorage:', e);
    }
  }
  
  // Mettre à jour currentUser avec les données du backend ou Google
  if (backendUser) {
    const googleAvatar = backendUser.profile_photo_url || backendUser.avatar || backendUser.profilePhoto || null;
    currentUser = {
      ...currentUser,
      ...backendUser,
      profilePhoto: googleAvatar,
      avatar: googleAvatar || backendUser.avatar || '👤',
      isLoggedIn: false,
      provider: 'google',
      profileComplete: false, // Pas encore complet, formulaire nécessaire
      googleValidated: true
    };
  } else {
    // Pas de données backend, utiliser les données Google du token
    currentUser = {
      ...currentUser,
      isLoggedIn: false,
      provider: 'google',
      profileComplete: false,
      googleValidated: true
    };
  }
  
  // NE PAS SAUVEGARDER DANS localStorage SI PLEIN - CONTINUER DIRECTEMENT
  // Les données seront sauvegardées sur le serveur après l'inscription
  try {
    // Essayer une seule fois, si ça échoue, on continue quand même
    localStorage.setItem("currentUser", JSON.stringify(currentUser));
  } catch (e) {
    if (e.name === 'QuotaExceededError' || e.message.includes('quota')) {
      console.warn('⚠️ localStorage plein - CONTINUATION SANS SAUVEGARDE');
      // VIDER COMPLÈTEMENT localStorage et réessayer UNE SEULE FOIS
      try {
        const tokens = localStorage.getItem('cognito_tokens');
        localStorage.clear();
        if (tokens) {
          localStorage.setItem('cognito_tokens', tokens);
        }
        // Réessayer avec version minimale
        const minimalUser = {
          id: currentUser.id || null,
          email: currentUser.email || '',
          username: currentUser.username || '',
          name: currentUser.name || '',
          firstName: currentUser.firstName || '',
          lastName: currentUser.lastName || '',
          avatar: currentUser.avatar || '👤',
          profilePhoto: currentUser.profilePhoto || null,
          isLoggedIn: false,
          provider: 'google',
          profileComplete: false,
          googleValidated: true
        };
        localStorage.setItem("currentUser", JSON.stringify(minimalUser));
      } catch (e2) {
        console.warn('⚠️ localStorage toujours plein après nettoyage - CONTINUATION SANS SAUVEGARDE');
        // CONTINUER QUAND MÊME - Le formulaire doit s'afficher
      }
    }
  }
  
  // Pré-remplir registerData avec les données Google
  const nameParts = (currentUser.name || '').split(' ');
  registerData = {
    email: currentUser.email || '',
    username: currentUser.username || '',
    password: '',
    passwordConfirm: '',
    firstName: nameParts[0] || currentUser.firstName || '',
    lastName: nameParts.slice(1).join(' ') || currentUser.lastName || '',
    profilePhoto: (currentUser.avatar && currentUser.avatar.startsWith('http')) ? currentUser.avatar : (currentUser.profilePhoto || ''),
    postalAddress: '',
    avatarId: 1,
    avatarDescription: currentUser.avatarDescription || '',
    addresses: [],
    emailVerificationCode: null,
    emailVerified: true,
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
  
  // Nettoyer l'URL des paramètres OAuth
  if (window.history && window.history.replaceState) {
    window.history.replaceState({}, document.title, window.location.pathname);
  }
  
  // Afficher un message de succès
  showNotification('✅ Connexion Google validée ! Veuillez compléter votre profil.', 'success');
  
  // FORCER l'affichage du formulaire - SOLUTION ULTIME ABSOLUE
  console.log('🚀 DÉMARRAGE FORÇAGE FORMULAIRE...');
  
  // APPEL DIRECT IMMÉDIAT de showProRegisterForm
  if (typeof window.showProRegisterForm === 'function') {
    console.log('✅ APPEL DIRECT showProRegisterForm');
    try {
      window.showProRegisterForm();
    } catch (e) {
      console.error('❌ Erreur appel direct showProRegisterForm:', e);
    }
  } else if (typeof showProRegisterForm === 'function') {
    console.log('✅ APPEL DIRECT showProRegisterForm (sans window)');
    try {
      showProRegisterForm();
    } catch (e) {
      console.error('❌ Erreur appel direct showProRegisterForm:', e);
    }
  } else {
    console.warn('⚠️ showProRegisterForm non disponible immédiatement, utilisation du mécanisme de retry...');
  }
  
  const forceShowForm = (attempt = 1) => {
    console.log(`🔄 Tentative ${attempt} d'affichage du formulaire...`);
    
    let backdrop = document.getElementById('publish-modal-backdrop');
    let modal = document.getElementById('publish-modal-inner');
    
    // Créer les éléments s'ils n'existent pas
    if (!backdrop) {
      console.log('📦 Création backdrop...');
      backdrop = document.createElement('div');
      backdrop.id = 'publish-modal-backdrop';
      backdrop.style.cssText = 'position:fixed!important;top:0!important;left:0!important;width:100%!important;height:100%!important;background:rgba(0,0,0,0.8)!important;z-index:99999!important;display:flex!important;align-items:center!important;justify-content:center!important;visibility:visible!important;opacity:1!important;';
      document.body.appendChild(backdrop);
    }
    
    if (!modal) {
      console.log('📦 Création modal...');
      modal = document.createElement('div');
      modal.id = 'publish-modal-inner';
      modal.style.cssText = 'background:#1e293b!important;border-radius:20px!important;padding:0!important;max-width:600px!important;width:90%!important;max-height:90vh!important;overflow-y:auto!important;';
      backdrop.appendChild(modal);
    }
    
    // FORCER l'affichage avec tous les styles nécessaires
    backdrop.style.display = 'flex';
    backdrop.style.visibility = 'visible';
    backdrop.style.opacity = '1';
    backdrop.style.zIndex = '99999';
    backdrop.style.position = 'fixed';
    backdrop.style.top = '0';
    backdrop.style.left = '0';
    backdrop.style.width = '100%';
    backdrop.style.height = '100%';
    backdrop.style.background = 'rgba(0,0,0,0.8)';
    
    // Essayer d'appeler showProRegisterForm
    if (typeof window.showProRegisterForm === 'function') {
      console.log('✅ Appel showProRegisterForm via window');
      try {
        window.showProRegisterForm();
        console.log('✅ showProRegisterForm appelé avec succès');
        return true;
      } catch (e) {
        console.error('❌ Erreur showProRegisterForm:', e);
      }
    } else if (typeof showProRegisterForm === 'function') {
      console.log('✅ Appel showProRegisterForm direct');
      try {
        showProRegisterForm();
        console.log('✅ showProRegisterForm appelé avec succès');
        return true;
      } catch (e) {
        console.error('❌ Erreur showProRegisterForm:', e);
      }
    } else {
      console.warn('⚠️ showProRegisterForm non disponible, recherche dans le DOM...');
      // Chercher la fonction dans le scope global
      const func = eval('showProRegisterForm');
      if (typeof func === 'function') {
        try {
          func();
          return true;
        } catch (e) {
          console.error('❌ Erreur showProRegisterForm via eval:', e);
        }
      }
    }
    
    // Si showProRegisterForm n'est toujours pas disponible, créer le HTML directement
    if (attempt >= 3) {
      console.log('🔄 Création HTML directe du formulaire...');
      const formHTML = `
        <div style="padding:40px;color:#fff;">
          <h2 style="color:#fff;margin-bottom:20px;">Inscription MapEvent</h2>
          <p style="color:#94a3b8;">Le formulaire d'inscription se charge...</p>
          <p style="color:#94a3b8;font-size:14px;margin-top:20px;">Si le formulaire complet ne s'affiche pas dans quelques secondes, rechargez la page.</p>
        </div>
      `;
      modal.innerHTML = formHTML;
      
      // Réessayer après 1 seconde
      setTimeout(() => {
        if (typeof window.showProRegisterForm === 'function') {
          window.showProRegisterForm();
        }
      }, 1000);
    }
    
    return false;
  };
  
  // Essayer IMMÉDIATEMENT et plusieurs fois
  let success = false;
  success = forceShowForm(1) || success;
  setTimeout(() => { success = forceShowForm(2) || success; }, 100);
  setTimeout(() => { success = forceShowForm(3) || success; }, 300);
  setTimeout(() => { success = forceShowForm(4) || success; }, 600);
  setTimeout(() => { success = forceShowForm(5) || success; }, 1000);
  setTimeout(() => { success = forceShowForm(6) || success; }, 2000);
  
  if (!success) {
    console.error('❌ Impossible d\'afficher le formulaire après toutes les tentatives');
    showNotification('⚠️ Erreur d\'affichage. Rechargez la page et réessayez.', 'error');
  }
}

// 3) Logout (Hosted UI)
function startCognitoLogout() {
  clearSession();
  localStorage.removeItem("currentUser");
  const logoutUrl =
    `${COGNITO.domain}/logout` +
    `?client_id=${encodeURIComponent(COGNITO.clientId)}` +
    `&logout_uri=${encodeURIComponent(COGNITO.redirectUri)}`;
  window.location.assign(logoutUrl);
}

// ============================================
// MAPEVENT – LOGIQUE FRONTEND (VERSION PRO)
// Avec :
//  - MAP + POPUPS + DEMO
//  - Event List fullscreen
//  - Filtre EXPLORATEUR multi-colonnes (Leader One Neon Pro)
//  - Filtres dates pour le mode EVENT
//  - Chargement arbres depuis /trees/*.json
//
// STRATÉGIE COMMERCIALE FUTURE (à implémenter côté backend) :
//  - Events : Envoyer un mail de confirmation à l'organisateur
//    → Rotation : 1 event par organisateur, puis passer au suivant
//    → Faire le tour complet avant de revenir vers le même organisateur
//    → L'organisateur doit publier lui-même ses prochains events
//  - Booking/Service : Publier tous les points automatiquement
//    → Enlever seulement si un utilisateur paie pour publier son propre point
//    → Si l'IA détecte un doublon/rapport, enlever le point automatique
//  - Logique IA : Détection de doublons et conflits lors des paiements
// ============================================

// --- CONFIG PATHS ---
// Les assets sont dans assets/ à la racine du bucket S3
// Depuis la racine CloudFront, on accède à assets/
const ASSETS_BASE = "assets";
const CAT_IMG_DIR = "category_images";
const EVENT_OVERLAYS_DIR = "event_overlays";

const MODE_IMAGE_FOLDERS = {
  event: "event",
  booking: "booking",
  service: "service"
};

const OVERLAY_IMAGES = {
  DEFAULT: `${ASSETS_BASE}/${EVENT_OVERLAYS_DIR}/eventdefault.jpg`,
  CANCELED: `${ASSETS_BASE}/${EVENT_OVERLAYS_DIR}/canceled.jpg`,
  COMPLETED: `${ASSETS_BASE}/${EVENT_OVERLAYS_DIR}/completed.jpg`,
  REPORTED: `${ASSETS_BASE}/${EVENT_OVERLAYS_DIR}/reported.jpg`,
  POSTPONED: `${ASSETS_BASE}/${EVENT_OVERLAYS_DIR}/postponed.jpg`
};

const DEFAULT_EVENT_IMAGE = OVERLAY_IMAGES.DEFAULT;

// --- ÉTAT GLOBAL ---
let map;
let tileLayer;
let markersLayer;
let markerMap = {};

let currentMode = "event"; // "event" | "booking" | "service"
let currentLanguage = "fr"; // "fr" | "en" | "es" | "zh" | "hi"

// CRITIQUE: Initialiser window.translations IMMÉDIATEMENT avec un objet vide
// pour éviter toute erreur TDZ avant que les traductions complètes ne soient chargées
// Cette initialisation doit être SYNCHRONE et IMMÉDIATE
// NE JAMAIS utiliser const/let/var translations car cela crée une TDZ
(function() {
  if (typeof window !== 'undefined') {
    // S'assurer que window.translations existe AVANT toute utilisation
    if (!window.translations || typeof window.translations !== 'object') {
      window.translations = { fr: {}, en: {}, es: {}, zh: {}, hi: {} };
    }
    // S'assurer que toutes les langues existent
    ['fr', 'en', 'es', 'zh', 'hi'].forEach(lang => {
      if (!window.translations[lang] || typeof window.translations[lang] !== 'object') {
        window.translations[lang] = {};
      }
    });
  }
})();

// CRITIQUE: window.translations sera défini juste après, mais on initialise window.t() d'abord
// pour éviter les erreurs de référence
// CRITIQUE: window.t() DOIT être défini AVANT window.translations pour éviter les erreurs TDZ
// Mais window.t() doit utiliser window.translations, donc on initialise window.translations d'abord
// FONCTION window.t - VERSION SÉCURISÉE SANS TDZ
window.t = function(k) {
  if (!k) return '';
  try {
    var w = window;
    if (!w || !w.translations) return k;
    var l = (typeof currentLanguage !== 'undefined' && currentLanguage) ? currentLanguage : 'fr';
    if (w.translations[l] && w.translations[l][k]) return w.translations[l][k];
    if (w.translations.fr && w.translations.fr[k]) return w.translations.fr[k];
    return k;
  } catch(e) {
    return k;
  }
};

// Définir les fonctions critiques IMMÉDIATEMENT pour éviter les erreurs de référence
// Ces fonctions seront redéfinies plus tard avec leurs implémentations complètes
// Stub pour openEventDiscussion - ouvre la discussion d'un événement
window.openEventDiscussion = function(type, id) {
  try {
    // Vérifier si l'utilisateur est connecté
    if (typeof currentUser === 'undefined' || !currentUser || !currentUser.isLoggedIn) {
      if (typeof window.openLoginModal === 'function') {
        window.openLoginModal();
      } else if (typeof openLoginModal === 'function') {
        openLoginModal();
      }
      return;
    }
    // Afficher une notification
    showNotification("💬 Discussion ouverte", "info");
    // Si openDiscussionModal est disponible, l'utiliser
    if (typeof window.openDiscussionModal === 'function') {
      window.openDiscussionModal(type, id);
    } else if (typeof openDiscussionModal === 'function') {
      openDiscussionModal(type, id);
    } else {
      // Attendre un peu et réessayer
      setTimeout(() => {
        if (typeof window.openDiscussionModal === 'function') {
          window.openDiscussionModal(type, id);
        } else if (typeof openDiscussionModal === 'function') {
          openDiscussionModal(type, id);
        }
      }, 100);
    }
  } catch (e) {
    console.warn('openEventDiscussion error:', e);
  }
};

// Stub pour openGroupsModal - sera remplacé par l'implémentation complète plus tard
// CRITIQUE: Cette fonction DOIT être disponible immédiatement pour éviter les erreurs
window.openGroupsModal = function() {
  try {
    // Vérifier si currentUser est disponible et si l'utilisateur est connecté
    if (typeof currentUser !== 'undefined' && currentUser && currentUser.isLoggedIn) {
      // Si l'implémentation complète est déjà disponible (assignée plus tard), elle sera utilisée
      // Sinon, attendre un peu et réessayer
      setTimeout(() => {
        try {
          const currentImpl = window.openGroupsModal;
          // Si la fonction a été remplacée par l'implémentation complète (plus de 500 caractères)
          if (currentImpl && currentImpl.toString().length > 500) {
            currentImpl();
          } else if (typeof window.openLoginModal === 'function') {
            window.openLoginModal();
          } else if (typeof openLoginModal === 'function') {
            openLoginModal();
          }
        } catch (e) {
          console.warn('openGroupsModal error:', e);
        }
      }, 50);
    } else {
      // Utilisateur non connecté - ouvrir le modal de connexion
      if (typeof window.openLoginModal === 'function') {
        window.openLoginModal();
      } else if (typeof openLoginModal === 'function') {
        openLoginModal();
      } else {
        // Attendre que openLoginModal soit disponible
        setTimeout(() => {
          if (typeof window.openLoginModal === 'function') {
            window.openLoginModal();
          } else if (typeof openLoginModal === 'function') {
            openLoginModal();
          }
        }, 100);
      }
    }
  } catch (e) {
    console.warn('openGroupsModal stub error:', e);
  }
};

// Stub pour sharePopup - sera remplacé par l'implémentation complète plus tard
window.sharePopup = function(type, id) {
  try {
    if (!type || !id) {
      console.warn('sharePopup: type and id are required');
      return;
    }
    
    // Vérifier si shareItem est disponible
    if (typeof shareItem === 'function') {
      shareItem(type, id);
    } else if (typeof window.shareItem === 'function') {
      window.shareItem(type, id);
    } else {
      // Attendre que shareItem soit disponible
      setTimeout(() => {
        try {
          if (typeof shareItem === 'function') {
            shareItem(type, id);
          } else if (typeof window.shareItem === 'function') {
            window.shareItem(type, id);
          } else {
            console.warn('sharePopup: shareItem not available yet');
          }
        } catch (e) {
          console.warn('sharePopup timeout error:', e);
        }
      }, 100);
    }
  } catch (e) {
    console.warn('sharePopup stub error:', e);
  }
};

// DICTIONNAIRE DE TRADUCTIONS COMPLET (déplacé ici pour être disponible avant initLanguage)
// ============================================
// CRITIQUE: Ne JAMAIS réassigner window.translations complètement car cela crée une TDZ
// Au lieu de cela, remplir progressivement les objets existants
// Initialiser d'abord avec un objet vide pour éviter les erreurs TDZ
if (!window.translations) {
  window.translations = { fr: {}, en: {}, es: {}, zh: {}, hi: {} };
}
// S'assurer que toutes les langues existent AVANT de les remplir
['fr', 'en', 'es', 'zh', 'hi'].forEach(lang => {
  if (!window.translations[lang] || typeof window.translations[lang] !== 'object') {
    window.translations[lang] = {};
  }
});

// CRITIQUE: Remplir progressivement au lieu de réassigner complètement
// Cela évite toute TDZ car on modifie les objets existants au lieu de les remplacer
// CRITIQUE: Ne JAMAIS utiliser 'const translations' - utiliser un nom différent
const translationsDataObject = {
  fr: {
    // UI Topbar
    "filter": "Filtrer", "list": "Liste", "events": "Events", "booking": "Booking", "services": "Services",
    "agenda": "Agenda", "alerts": "ABOS", "account": "Compte", "cart": "Panier",
    "search_city": "Rechercher une ville...", "publish": "Publier",
    
    // Popups Events
    "event_title": "Événement", "date": "Date", "address": "Adresse", "description": "Description",
    "category": "Catégorie", "organizer": "Organisateur", "price": "Prix", "free": "Gratuit",
    "add_to_agenda": "Ajouter à mon agenda", "like": "J'aime", "favorite": "Favoris", "participate": "Participer",
    "leave_review": "Laisser un avis", "contact_ai": "Contact IA", "report": "Signaler",
    "participants": "participants", "registered": "Inscrit", "in_agenda": "Dans agenda",
    "share": "Partager", "route": "Itinéraire", "review": "Avis", "contact": "Contact", "reviews": "avis",
    "ai_detected": "Publié par MapEvent", "check_source": "vérifier la source",
    "booking_link": "Lien de réservation", "rating": "Note",
    
    // Popups Booking
    "booking_title": "Réservation", "artist": "Artiste", "level": "Niveau", "sound_preview": "Aperçu sonore",
    "get_contact": "Obtenir contact", "pay": "Payer", "view_subs": "Voir les abos", "add_to_cart": "Ajouter au panier",
    "verified": "Vérifié", "website": "Site web", "email": "Email", "phone": "Téléphone",
    
    // Popups Service
    "service_title": "Service", "company": "Entreprise", "contact_info": "Informations de contact",
    
    // Agenda
    "my_agenda": "Mon agenda", "my_favorites": "Mes favoris", "my_subscriptions": "Mes abonnements",
    "agenda_empty": "Votre agenda est vide", "add_from_map": "Ajoutez des événements depuis la carte !",
    "remove_from_agenda": "Retirer de l'agenda",
    
    // Messages
    "city_found": "trouvée !", "city_not_found": "non trouvée", "searching": "Recherche de",
    "language_changed": "Langue changée", "removed_from_agenda": "Retiré de l'agenda",
    
    // Filtres
    "filter_by_date": "Filtrer par date", "today": "Aujourd'hui", "tomorrow": "Demain",
    "weekend": "Ce week-end", "week": "Cette semaine", "month": "Ce mois",
    "select_period": "Ou sélectionner une période", "from": "Du", "to": "Au",
    "reset_all": "Réinitialiser tout", "selected_categories": "Catégories sélectionnées",
    "cumulative": "cumulable",
    
    // Formulaire de publication
    "publish_mode": "Publier – Mode", "main_category": "Catégorie principale", "choose_category": "Choisir catégorie…",
    "start": "Début", "end": "Fin", "title_name": "Titre / Nom", "full_address": "Adresse complète",
    "phone": "Téléphone", "email": "Email", "full_description": "Description complète",
    "main_photo": "Photo principale", "ticketing": "Billetterie", "ticket_link": "Lien billetterie",
    "social_links": "Liens réseaux", "video_links": "Liens vidéos", "sound_links": "Liens sons (SoundCloud, YouTube, Spotify…)",
    "paste_sound_links": "Coller vos liens sons", "level": "Niveau (Débutant, Pro, Headliner…)",
    "price_estimate": "Estimation de prix à négocier", "price_example": "ex: 500.– la soirée (à négocier)",
    "price_not_detected": "Si l'IA ne détecte pas de prix ou a un doute : \"Estimation de prix non détectée\".",
    "visibility_choice": "Choix de visibilité (paiement à l'étape suivante) :",
    "standard_point": "1.– : Point standard sur la map + Event List.",
    "bronze_boost": "5.– Boost Bronze : Pointeur bronze, priorité dans la liste.",
    "silver_boost": "10.– Boost Silver : Pointeur argent, forte priorité.",
    "platinum_boost": "TOP 10 – Boost Platinum : enchères, pointeur platine ultra visible.",
    "subscription_recommended": "💎 Abonnement recommandé",
    "save_on_events": "Économisez sur vos publications events",
    "unlimited_contacts": "Contacts illimités + réductions",
    "view_subs": "Voir les abos",
    "publish_and_pay": "Publier et payer",
    
    // Autres
    "close": "Fermer", "save": "Enregistrer", "cancel": "Annuler", "confirm": "Confirmer",
    "loading": "Chargement...", "error": "Erreur", "success": "Succès", "info": "Information",
    "translate": "Traduire", "hide_translation": "Masquer traduction", "translation_error": "Erreur de traduction",
    "try_again": "Réessayez"
  },
  en: {
    "filter": "Filter", "list": "List", "events": "Events", "booking": "Booking", "services": "Services",
    "agenda": "Agenda", "alerts": "Alerts", "account": "Account", "cart": "Cart",
    "search_city": "Search for a city...", "publish": "Publish",
    "event_title": "Event", "date": "Date", "address": "Address", "description": "Description",
    "category": "Category", "organizer": "Organizer", "price": "Price", "free": "Free",
    "add_to_agenda": "Add to my agenda", "like": "Like", "favorite": "Favorites", "participate": "Participate",
    "leave_review": "Leave a review", "contact_ai": "AI Contact", "report": "Report",
    "participants": "participants", "registered": "Registered", "in_agenda": "In agenda",
    "share": "Share", "route": "Route", "review": "Review", "contact": "Contact", "reviews": "reviews",
    "ai_detected": "Detected by AI", "check_source": "Check source",
    "booking_link": "Booking link", "rating": "Rating",
    "booking_title": "Booking", "artist": "Artist", "level": "Level", "sound_preview": "Sound preview",
    "get_contact": "Get contact", "pay": "Pay", "view_subs": "View subscriptions", "add_to_cart": "Add to cart",
    "verified": "Verified", "website": "Website", "email": "Email", "phone": "Phone",
    "service_title": "Service", "company": "Company", "contact_info": "Contact information",
    "my_agenda": "My agenda", "my_favorites": "My favorites", "my_subscriptions": "My subscriptions",
    "agenda_empty": "Your agenda is empty", "add_from_map": "Add events from the map!",
    "remove_from_agenda": "Remove from agenda",
    "city_found": "found !", "city_not_found": "not found", "searching": "Searching for",
    "language_changed": "Language changed", "removed_from_agenda": "Removed from agenda",
    "filter_by_date": "Filter by date", "today": "Today", "tomorrow": "Tomorrow",
    "weekend": "This weekend", "week": "This week", "month": "This month",
    "select_period": "Or select a period", "from": "From", "to": "To",
    "reset_all": "Reset all", "selected_categories": "Selected categories",
    "cumulative": "cumulative",
    "publish_mode": "Publish – Mode", "main_category": "Main category", "choose_category": "Choose category…",
    "start": "Start", "end": "End", "title_name": "Title / Name", "full_address": "Full address",
    "phone": "Phone", "email": "Email", "full_description": "Full description",
    "main_photo": "Main photo", "ticketing": "Ticketing", "ticket_link": "Ticket link",
    "social_links": "Social links", "video_links": "Video links", "sound_links": "Sound links (SoundCloud, YouTube, Spotify…)",
    "paste_sound_links": "Paste your sound links", "level": "Level (Beginner, Pro, Headliner…)",
    "price_estimate": "Price estimate to negotiate", "price_example": "e.g.: 500.– per evening (to negotiate)",
    "price_not_detected": "If AI doesn't detect a price or has doubts: \"Price estimate not detected\".",
    "visibility_choice": "Visibility choice (payment at next step):",
    "standard_point": "1.– : Standard point on map + Event List.",
    "bronze_boost": "5.– Bronze Boost : Bronze pointer, priority in list.",
    "silver_boost": "10.– Silver Boost : Silver pointer, high priority.",
    "platinum_boost": "TOP 10 – Platinum Boost : auctions, ultra-visible platinum pointer.",
    "subscription_recommended": "💎 Recommended subscription",
    "save_on_events": "Save on your event publications",
    "unlimited_contacts": "Unlimited contacts + discounts",
    "view_subs": "View subscriptions",
    "publish_and_pay": "Publish and pay",
    "close": "Close", "save": "Save", "cancel": "Cancel", "confirm": "Confirm",
    "loading": "Loading...", "error": "Error", "success": "Success", "info": "Information",
    "translate": "Translate", "hide_translation": "Hide translation", "translation_error": "Translation error",
    "try_again": "Try again"
  },
  es: {
    "filter": "Filtrar", "list": "Lista", "events": "Eventos", "booking": "Reservas", "services": "Servicios",
    "agenda": "Agenda", "alerts": "Alertas", "account": "Cuenta", "cart": "Carrito",
    "search_city": "Buscar una ciudad...", "publish": "Publicar",
    "event_title": "Evento", "date": "Fecha", "address": "Dirección", "description": "Descripción",
    "category": "Categoría", "organizer": "Organizador", "price": "Precio", "free": "Gratis",
    "add_to_agenda": "Añadir a mi agenda", "like": "Me gusta", "favorite": "Favoritos", "participate": "Participar",
    "leave_review": "Dejar una reseña", "contact_ai": "Contacto IA", "report": "Reportar",
    "participants": "participantes", "registered": "Inscrito", "in_agenda": "En agenda",
    "share": "Compartir", "route": "Ruta", "review": "Reseña", "contact": "Contacto", "reviews": "reseñas",
    "ai_detected": "Detectado por IA", "check_source": "Verificar fuente",
    "booking_link": "Enlace de reserva", "rating": "Calificación",
    "booking_title": "Reserva", "artist": "Artista", "level": "Nivel", "sound_preview": "Vista previa de sonido",
    "get_contact": "Obtener contacto", "pay": "Pagar", "view_subs": "Ver suscripciones", "add_to_cart": "Añadir al carrito",
    "verified": "Verificado", "website": "Sitio web", "email": "Email", "phone": "Teléfono",
    "service_title": "Servicio", "company": "Empresa", "contact_info": "Información de contacto",
    "my_agenda": "Mi agenda", "my_favorites": "Mis favoritos", "my_subscriptions": "Mis suscripciones",
    "agenda_empty": "Tu agenda está vacía", "add_from_map": "¡Añade eventos desde el mapa!",
    "remove_from_agenda": "Quitar de la agenda",
    "city_found": "encontrada !", "city_not_found": "no encontrada", "searching": "Buscando",
    "language_changed": "Idioma cambiado", "removed_from_agenda": "Eliminado de la agenda",
    "filter_by_date": "Filtrar por fecha", "today": "Hoy", "tomorrow": "Mañana",
    "weekend": "Este fin de semana", "week": "Esta semana", "month": "Este mes",
    "select_period": "O seleccionar un período", "from": "Desde", "to": "Hasta",
    "reset_all": "Restablecer todo", "selected_categories": "Categorías seleccionadas",
    "cumulative": "acumulable",
    "close": "Cerrar", "save": "Guardar", "cancel": "Cancelar", "confirm": "Confirmar",
    "loading": "Cargando...", "error": "Error", "success": "Éxito", "info": "Información",
    "translate": "Traducir", "hide_translation": "Ocultar traducción", "translation_error": "Error de traducción",
    "try_again": "Intentar de nuevo"
  },
  zh: {
    "filter": "筛选", "list": "列表", "events": "活动", "booking": "预订", "services": "服务",
    "agenda": "日程", "alerts": "提醒", "account": "账户", "cart": "购物车",
    "search_city": "搜索城市...", "publish": "发布",
    "event_title": "活动", "date": "日期", "address": "地址", "description": "描述",
    "category": "类别", "organizer": "组织者", "price": "价格", "free": "免费",
    "add_to_agenda": "添加到我的日程", "like": "喜欢", "favorite": "收藏", "participate": "参与",
    "leave_review": "留下评论", "contact_ai": "AI联系", "report": "举报",
    "participants": "参与者", "registered": "已注册", "in_agenda": "在日程中",
    "share": "分享", "route": "路线", "review": "评论", "contact": "联系", "reviews": "评论",
    "ai_detected": "AI检测", "check_source": "检查来源",
    "booking_link": "预订链接", "rating": "评分",
    "booking_title": "预订", "artist": "艺术家", "level": "级别", "sound_preview": "声音预览",
    "get_contact": "获取联系方式", "pay": "支付", "view_subs": "查看订阅", "add_to_cart": "添加到购物车",
    "verified": "已验证", "website": "网站", "email": "电子邮件", "phone": "电话",
    "service_title": "服务", "company": "公司", "contact_info": "联系信息",
    "my_agenda": "我的日程", "my_favorites": "我的收藏", "my_subscriptions": "我的订阅",
    "agenda_empty": "您的日程为空", "add_from_map": "从地图添加活动！",
    "remove_from_agenda": "从日程中移除",
    "city_found": "已找到！", "city_not_found": "未找到", "searching": "正在搜索",
    "language_changed": "语言已更改", "removed_from_agenda": "已从日程中移除",
    "filter_by_date": "按日期筛选", "today": "今天", "tomorrow": "明天",
    "weekend": "本周末", "week": "本周", "month": "本月",
    "select_period": "或选择时间段", "from": "从", "to": "到",
    "reset_all": "重置全部", "selected_categories": "已选类别",
    "cumulative": "累积",
    "close": "关闭", "save": "保存", "cancel": "取消", "confirm": "确认",
    "loading": "加载中...", "error": "错误", "success": "成功", "info": "信息",
    "translate": "翻译", "hide_translation": "隐藏翻译", "translation_error": "翻译错误",
    "try_again": "重试"
  },
  hi: {
    "filter": "फ़िल्टर", "list": "सूची", "events": "इवेंट्स", "booking": "बुकिंग", "services": "सेवाएं",
    "agenda": "एजेंडा", "alerts": "अलर्ट", "account": "खाता", "cart": "कार्ट",
    "search_city": "शहर खोजें...", "publish": "प्रकाशित करें",
    "event_title": "इवेंट", "date": "तारीख", "address": "पता", "description": "विवरण",
    "category": "श्रेणी", "organizer": "आयोजक", "price": "मूल्य", "free": "मुफ्त",
    "add_to_agenda": "मेरे एजेंडा में जोड़ें", "like": "पसंद", "favorite": "पसंदीदा", "participate": "भाग लें",
    "leave_review": "समीक्षा छोड़ें", "contact_ai": "AI संपर्क", "report": "रिपोर्ट",
    "participants": "प्रतिभागी", "registered": "पंजीकृत", "in_agenda": "एजेंडा में",
    "share": "साझा करें", "route": "मार्ग", "review": "समीक्षा", "contact": "संपर्क", "reviews": "समीक्षाएं",
    "ai_detected": "AI द्वारा पता लगाया गया", "check_source": "स्रोत जांचें",
    "booking_link": "बुकिंग लिंक", "rating": "रेटिंग",
    "booking_title": "बुकिंग", "artist": "कलाकार", "level": "स्तर", "sound_preview": "ध्वनि पूर्वावलोकन",
    "get_contact": "संपर्क प्राप्त करें", "pay": "भुगतान", "view_subs": "सदस्यता देखें", "add_to_cart": "कार्ट में जोड़ें",
    "verified": "सत्यापित", "website": "वेबसाइट", "email": "ईमेल", "phone": "फ़ोन",
    "service_title": "सेवा", "company": "कंपनी", "contact_info": "संपर्क जानकारी",
    "my_agenda": "मेरा एजेंडा", "my_favorites": "मेरे पसंदीदा", "my_subscriptions": "मेरी सदस्यताएं",
    "agenda_empty": "आपका एजेंडा खाली है", "add_from_map": "मानचित्र से इवेंट जोड़ें!",
    "remove_from_agenda": "एजेंडा से हटाएं",
    "city_found": "मिल गया !", "city_not_found": "नहीं मिला", "searching": "खोज रहे हैं",
    "language_changed": "भाषा बदली", "removed_from_agenda": "एजेंडा से हटाया गया",
    "filter_by_date": "तारीख से फ़िल्टर करें", "today": "आज", "tomorrow": "कल",
    "weekend": "इस सप्ताहांत", "week": "इस सप्ताह", "month": "इस महीने",
    "select_period": "या एक अवधि चुनें", "from": "से", "to": "तक",
    "reset_all": "सभी रीसेट करें", "selected_categories": "चयनित श्रेणियां",
    "cumulative": "संचयी",
    "close": "बंद करें", "save": "सहेजें", "cancel": "रद्द करें", "confirm": "पुष्टि करें",
    "loading": "लोड हो रहा है...", "error": "त्रुटि", "success": "सफलता", "info": "जानकारी",
    "translate": "अनुवाद करें", "hide_translation": "अनुवाद छुपाएं", "translation_error": "अनुवाद त्रुटि",
    "try_again": "पुनः प्रयास करें"
  }
};

// CRITIQUE: Remplir progressivement window.translations au lieu de le réassigner
// Cela évite toute TDZ car on modifie les objets existants
Object.keys(translationsDataObject).forEach(lang => {
  if (window.translations[lang] && typeof window.translations[lang] === 'object') {
    Object.assign(window.translations[lang], translationsDataObject[lang]);
  } else {
    window.translations[lang] = translationsDataObject[lang];
  }
});

// S'assurer que window.translations est toujours un objet valide après assignation
if (!window.translations || typeof window.translations !== 'object') {
  window.translations = { fr: {}, en: {}, es: {}, zh: {}, hi: {} };
}
// S'assurer que toutes les langues existent
['fr', 'en', 'es', 'zh', 'hi'].forEach(lang => {
  if (!window.translations[lang] || typeof window.translations[lang] !== 'object') {
    window.translations[lang] = window.translations[lang] || {};
  }
});

// CRITIQUE: window.translations est maintenant rempli directement ci-dessus (ligne 160)
// Pas besoin d'Object.assign car nous assignons directement à window.translations
// La fonction window.t() est déjà définie plus haut (ligne 65) et utilise window.translations
// Elle fonctionnera automatiquement maintenant que window.translations est rempli

// Les fonctions sharePopup et openGroupsModal sont déjà définies plus haut (lignes 87-156)
// Elles seront remplacées par les implémentations complètes plus tard dans le fichier

let eventsData = [];
let bookingsData = [];
let servicesData = [];

// Exposer les données globalement pour le script de métadonnées
window.eventsData = eventsData;
window.bookingsData = bookingsData;
window.servicesData = servicesData;

let filteredData = null;
let leftPanelOpen = false;
let listViewOpen = false;
let selectedCityForSorting = null; // Ville sélectionnée pour le tri par distance

let uiThemeIndex = 0;
let mapThemeIndex = 0;

// Arbres pour logique image
let EVENTS_TREE = null;
let BOOKING_TREE = null;
let SERVICE_TREE = null;

// --- CONFIGURATION CONTACT ---
const MAPEVENT_CONTACT_EMAIL = "mapevent777@gmail.com";

// --- 30+ AVATARS DISPONIBLES ---
const AVAILABLE_AVATARS = [
  // Personnages
  { id: 1, emoji: "🦊", name: "Renard", category: "animaux" },
  { id: 2, emoji: "🐺", name: "Loup", category: "animaux" },
  { id: 3, emoji: "🦁", name: "Lion", category: "animaux" },
  { id: 4, emoji: "🐯", name: "Tigre", category: "animaux" },
  { id: 5, emoji: "🐻", name: "Ours", category: "animaux" },
  { id: 6, emoji: "🐼", name: "Panda", category: "animaux" },
  { id: 7, emoji: "🐨", name: "Koala", category: "animaux" },
  { id: 8, emoji: "🦄", name: "Licorne", category: "fantaisie" },
  { id: 9, emoji: "🐉", name: "Dragon", category: "fantaisie" },
  { id: 10, emoji: "🦅", name: "Aigle", category: "animaux" },
  { id: 11, emoji: "🦋", name: "Papillon", category: "animaux" },
  { id: 12, emoji: "🐬", name: "Dauphin", category: "animaux" },
  { id: 13, emoji: "🦈", name: "Requin", category: "animaux" },
  { id: 14, emoji: "🐙", name: "Pieuvre", category: "animaux" },
  { id: 15, emoji: "🦜", name: "Perroquet", category: "animaux" },
  // Musique & Fête
  { id: 16, emoji: "🎧", name: "DJ", category: "musique" },
  { id: 17, emoji: "🎸", name: "Rockeur", category: "musique" },
  { id: 18, emoji: "🎤", name: "Chanteur", category: "musique" },
  { id: 19, emoji: "🎹", name: "Pianiste", category: "musique" },
  { id: 20, emoji: "🥁", name: "Batteur", category: "musique" },
  { id: 21, emoji: "🎷", name: "Saxophoniste", category: "musique" },
  { id: 22, emoji: "🎺", name: "Trompettiste", category: "musique" },
  // Personnages humains stylisés
  { id: 23, emoji: "🧙", name: "Mage", category: "fantaisie" },
  { id: 24, emoji: "🧚", name: "Fée", category: "fantaisie" },
  { id: 25, emoji: "🧛", name: "Vampire", category: "fantaisie" },
  { id: 26, emoji: "🧟", name: "Zombie", category: "fantaisie" },
  { id: 27, emoji: "👻", name: "Fantôme", category: "fantaisie" },
  { id: 28, emoji: "👽", name: "Alien", category: "fantaisie" },
  { id: 29, emoji: "🤖", name: "Robot", category: "tech" },
  { id: 30, emoji: "🦸", name: "Super-héros", category: "fantaisie" },
  // Sport & Loisirs
  { id: 31, emoji: "⚽", name: "Footballeur", category: "sport" },
  { id: 32, emoji: "🏀", name: "Basketteur", category: "sport" },
  { id: 33, emoji: "🎿", name: "Skieur", category: "sport" },
  { id: 34, emoji: "🏄", name: "Surfeur", category: "sport" },
  { id: 35, emoji: "🚴", name: "Cycliste", category: "sport" },
  // Nature & Cosmos
  { id: 36, emoji: "🌟", name: "Étoile", category: "cosmos" },
  { id: 37, emoji: "🌙", name: "Lune", category: "cosmos" },
  { id: 38, emoji: "☀️", name: "Soleil", category: "cosmos" },
  { id: 39, emoji: "🌈", name: "Arc-en-ciel", category: "nature" },
  { id: 40, emoji: "🔥", name: "Flamme", category: "éléments" },
  // Plus d'avatars pour atteindre 30+
  { id: 41, emoji: "🎭", name: "Masque", category: "art" },
  { id: 42, emoji: "🎨", name: "Artiste", category: "art" },
  { id: 43, emoji: "🎪", name: "Cirque", category: "art" },
  { id: 44, emoji: "🎬", name: "Cinéma", category: "art" },
  { id: 45, emoji: "🎮", name: "Gamer", category: "tech" },
  { id: 46, emoji: "💻", name: "Tech", category: "tech" },
  { id: 47, emoji: "🚀", name: "Rocket", category: "cosmos" },
  { id: 48, emoji: "🛸", name: "OVNI", category: "cosmos" },
  { id: 49, emoji: "🌍", name: "Terre", category: "nature" },
  { id: 50, emoji: "🌊", name: "Vague", category: "nature" },
  { id: 51, emoji: "⛰️", name: "Montagne", category: "nature" },
  { id: 52, emoji: "🌲", name: "Arbre", category: "nature" },
  { id: 53, emoji: "🌺", name: "Fleur", category: "nature" },
  { id: 54, emoji: "🍕", name: "Pizza", category: "food" },
  { id: 55, emoji: "🍔", name: "Burger", category: "food" },
  { id: 56, emoji: "☕", name: "Café", category: "food" },
  { id: 57, emoji: "🍺", name: "Bière", category: "food" },
  { id: 58, emoji: "🍷", name: "Vin", category: "food" },
  { id: 59, emoji: "🎯", name: "Cible", category: "sport" },
  { id: 60, emoji: "🏆", name: "Trophée", category: "sport" },
  { id: 61, emoji: "💎", name: "Diamant", category: "luxe" },
  { id: 62, emoji: "👑", name: "Couronne", category: "luxe" },
  { id: 63, emoji: "🎁", name: "Cadeau", category: "divers" },
  { id: 64, emoji: "🎈", name: "Ballon", category: "divers" },
  { id: 65, emoji: "🎊", name: "Confetti", category: "divers" },
  { id: 66, emoji: "🎉", name: "Fête", category: "divers" },
  { id: 67, emoji: "✨", name: "Étincelle", category: "divers" },
  { id: 68, emoji: "💫", name: "Étoile filante", category: "cosmos" },
  { id: 69, emoji: "🌠", name: "Météore", category: "cosmos" },
  { id: 70, emoji: "🦉", name: "Hibou", category: "animaux" }
];

// --- DONNÉES UTILISATEUR ---
let currentUser = {
  id: null,
  name: "",
  email: "",
  avatar: "👤",
  avatarId: null,
  avatarDescription: "", // Description optionnelle de l'avatar
  bio: "", // Bio de l'utilisateur
  isLoggedIn: false, // Par défaut non connecté
  favorites: [],      // IDs des favoris
  agenda: [],         // IDs dans l'agenda (permanent si payé)
  likes: [],          // IDs likés
  participating: [],  // IDs événements participation
  alerts: [],         // Alertes personnalisées
  statusAlerts: [],   // Alertes de statut (GRATUITES et ILLIMITÉES)
  pendingStatusNotifications: [], // Notifications de changement de statut à afficher au login
  proximityAlerts: [], // Alertes de proximité (items likés dans un rayon de 70km)
  eventAlarms: [],    // Alarmes pour les événements dans l'agenda [{eventId, type, value, time, triggered}]
  reviews: {},        // Reviews par item
  subscription: "free",
  agendaLimit: 20,
  alertLimit: 0,
  eventStatusHistory: {},
  addresses: [],
  smsNotifications: 0,
  smsLimit: 0,
  emailNotifications: 0,
  notificationPreferences: {
    email: true,
    sms: false
  },
  // ============================================
  // OPTIONS DE CONFIDENTIALITÉ - Choisir ce qui est public
  // ============================================
  privacySettings: {
    showName: true,        // Toujours visible (minimum requis)
    showAvatar: true,      // Toujours visible (minimum requis)
    showBio: true,         // Visible par défaut, peut être masqué
    showEmail: false,      // Masqué par défaut
    showAddresses: false,  // Masqué par défaut
    showFavorites: true,   // Visible par défaut
    showAgenda: true,      // Visible par défaut
    showParticipating: true, // Visible par défaut
    showFriends: true,     // Visible par défaut
    showActivity: true     // Statistiques visibles par défaut
  },
  // --- NOUVELLES FONCTIONNALITÉS SOCIALES ---
  friends: [],           // Liste des IDs d'amis
  friendRequests: [],    // Demandes d'amis reçues: [{fromUserId, fromUserName, fromUserAvatar, date}]
  sentRequests: [],      // Demandes d'amis envoyées
  blockedUsers: [],      // Utilisateurs bloqués
  conversations: [],     // IDs des conversations
  groups: [],            // Groupes créés/rejoints: [{id, name, type, category, country, members: [], messages: []}]
  socialAlerts: [],      // Alertes sociales: [{type, fromUserId, message, date, read}]
  registeredCountry: 'CH', // Pays d'enregistrement (détecté depuis l'adresse)
  lastSeen: null,        // Dernière connexion
  profileLinks: [],      // Liens vers réseaux sociaux: [{platform, url}]
  profilePhotos: [],     // Photos du profil (URLs)
  profileVideos: [],     // Vidéos du profil (URLs)
  bio: '',               // Description du profil
  createdAt: null,       // Date de création du compte
  lastLoginAt: null      // Dernière connexion
};

// Contacts payés (permanent, ne disparaît jamais)
let paidContacts = [];

// Panier (contacts à acheter)
let cart = [];

// Simuler lecture audio
function playPreview(bookingId, trackIndex) {
  showNotification("🎵 Lecture de la piste " + (trackIndex + 1) + "...", "info");
  
  // Animation de la barre de progression
  const progressBar = document.getElementById(`progress-${bookingId}-${trackIndex}`);
  if (progressBar) {
    let progress = 0;
    const interval = setInterval(() => {
      progress += 2;
      progressBar.style.width = progress + "%";
      if (progress >= 100) {
        clearInterval(interval);
        progressBar.style.width = "0%";
      }
    }, 100);
    
    // Arrêter après 15 secondes (démo généreuse)
    setTimeout(() => {
      clearInterval(interval);
      progressBar.style.width = "0%";
      showNotification("⏹️ Fin de l'aperçu 15s – Débloquez pour écouter en entier !", "info");
    }, 15000);
  }
}

// --- SYSTÈME DE MODÉRATION IA ---
let moderationQueue = [];
let moderationHistory = [];

// --- VILLES SUISSES AVEC COORDONNÉES ---
const SWISS_CITIES = [
  { name: "Zürich", lat: 47.3769, lng: 8.5417, canton: "ZH", region: "Zurich" },
  { name: "Genève", lat: 46.2044, lng: 6.1432, canton: "GE", region: "Genève" },
  { name: "Bâle", lat: 47.5596, lng: 7.5886, canton: "BS", region: "Bâle" },
  { name: "Lausanne", lat: 46.5197, lng: 6.6323, canton: "VD", region: "Vaud" },
  { name: "Berne", lat: 46.9480, lng: 7.4474, canton: "BE", region: "Berne" },
  { name: "Winterthur", lat: 47.5001, lng: 8.7240, canton: "ZH", region: "Zurich" },
  { name: "Lucerne", lat: 47.0502, lng: 8.3093, canton: "LU", region: "Lucerne" },
  { name: "St-Gall", lat: 47.4245, lng: 9.3767, canton: "SG", region: "St-Gall" },
  { name: "Lugano", lat: 46.0037, lng: 8.9511, canton: "TI", region: "Tessin" },
  { name: "Bienne", lat: 47.1368, lng: 7.2467, canton: "BE", region: "Berne" },
  { name: "Thoune", lat: 46.7580, lng: 7.6280, canton: "BE", region: "Berne" },
  { name: "Köniz", lat: 46.9244, lng: 7.4128, canton: "BE", region: "Berne" },
  { name: "La Chaux-de-Fonds", lat: 47.1035, lng: 6.8296, canton: "NE", region: "Neuchâtel" },
  { name: "Fribourg", lat: 46.8065, lng: 7.1620, canton: "FR", region: "Fribourg" },
  { name: "Schaffhouse", lat: 47.6959, lng: 8.6350, canton: "SH", region: "Schaffhouse" },
  { name: "Coire", lat: 46.8508, lng: 9.5320, canton: "GR", region: "Grisons" },
  { name: "Neuchâtel", lat: 46.9920, lng: 6.9311, canton: "NE", region: "Neuchâtel" },
  // VALAIS - Toutes les villes principales
  { name: "Sion", lat: 46.2331, lng: 7.3606, canton: "VS", region: "Valais" },
  { name: "Sierre", lat: 46.2920, lng: 7.5350, canton: "VS", region: "Valais" },
  { name: "Visp", lat: 46.2936, lng: 7.8817, canton: "VS", region: "Valais" },
  { name: "Brig", lat: 46.3167, lng: 7.9875, canton: "VS", region: "Valais" },
  { name: "Monthey", lat: 46.2547, lng: 6.9542, canton: "VS", region: "Valais" },
  { name: "Crans-Montana", lat: 46.3108, lng: 7.4797, canton: "VS", region: "Valais" },
  { name: "Verbier", lat: 46.0967, lng: 7.2286, canton: "VS", region: "Valais" },
  { name: "Zermatt", lat: 46.0207, lng: 7.7491, canton: "VS", region: "Valais" },
  { name: "Leukerbad", lat: 46.3792, lng: 7.6283, canton: "VS", region: "Valais" },
  { name: "Saas-Fee", lat: 46.1081, lng: 7.9272, canton: "VS", region: "Valais" },
  // Autres villes
  { name: "Montreux", lat: 46.4312, lng: 6.9107, canton: "VD", region: "Vaud" },
  { name: "Yverdon", lat: 46.7785, lng: 6.6410, canton: "VD", region: "Vaud" },
  { name: "Aarau", lat: 47.3925, lng: 8.0444, canton: "AG", region: "Argovie" },
  { name: "Bellinzone", lat: 46.1955, lng: 9.0240, canton: "TI", region: "Tessin" },
  { name: "Zoug", lat: 47.1724, lng: 8.5177, canton: "ZG", region: "Zoug" },
  { name: "Nyon", lat: 46.3833, lng: 6.2396, canton: "VD", region: "Vaud" },
  { name: "Martigny", lat: 46.1028, lng: 7.0722, canton: "VS", region: "Valais" },
  { name: "Bulle", lat: 46.6198, lng: 7.0579, canton: "FR", region: "Fribourg" },
  { name: "Morges", lat: 46.5118, lng: 6.4981, canton: "VD", region: "Vaud" },
  { name: "Vevey", lat: 46.4628, lng: 6.8431, canton: "VD", region: "Vaud" },
  { name: "Locarno", lat: 46.1708, lng: 8.7994, canton: "TI", region: "Tessin" },
  { name: "Soleure", lat: 47.2088, lng: 7.5372, canton: "SO", region: "Soleure" },
  { name: "Aigle", lat: 46.3186, lng: 6.9706, canton: "VD", region: "Vaud" },
  { name: "Delémont", lat: 47.3656, lng: 7.3436, canton: "JU", region: "Jura" },
  { name: "Davos", lat: 46.8027, lng: 9.8360, canton: "GR", region: "Grisons" },
  { name: "Interlaken", lat: 46.6863, lng: 7.8632, canton: "BE", region: "Berne" },
  { name: "Grindelwald", lat: 46.6244, lng: 8.0413, canton: "BE", region: "Berne" },
  { name: "Ascona", lat: 46.1569, lng: 8.7700, canton: "TI", region: "Tessin" }
];

// --- VILLES FRANÇAISES AVEC COORDONNÉES ---
const FRENCH_CITIES = [
  { name: "Paris", lat: 48.8566, lng: 2.3522, region: "IDF" },
  { name: "Lyon", lat: 45.7640, lng: 4.8357, region: "ARA" },
  { name: "Marseille", lat: 43.2965, lng: 5.3698, region: "PACA" },
  { name: "Toulouse", lat: 43.6047, lng: 1.4442, region: "OCC" },
  { name: "Nice", lat: 43.7102, lng: 7.2620, region: "PACA" },
  { name: "Nantes", lat: 47.2184, lng: -1.5536, region: "PDL" },
  { name: "Montpellier", lat: 43.6108, lng: 3.8767, region: "OCC" },
  { name: "Strasbourg", lat: 48.5734, lng: 7.7521, region: "GE" },
  { name: "Bordeaux", lat: 44.8378, lng: -0.5792, region: "NAQ" },
  { name: "Lille", lat: 50.6292, lng: 3.0573, region: "HDF" },
  { name: "Rennes", lat: 48.1173, lng: -1.6778, region: "BRE" },
  { name: "Reims", lat: 49.2583, lng: 4.0317, region: "GE" },
  { name: "Toulon", lat: 43.1242, lng: 5.9280, region: "PACA" },
  { name: "Saint-Étienne", lat: 45.4397, lng: 4.3872, region: "ARA" },
  { name: "Le Havre", lat: 49.4944, lng: 0.1079, region: "NOR" },
  { name: "Grenoble", lat: 45.1885, lng: 5.7245, region: "ARA" },
  { name: "Dijon", lat: 47.3220, lng: 5.0415, region: "BFC" },
  { name: "Angers", lat: 47.4784, lng: -0.5632, region: "PDL" },
  { name: "Nîmes", lat: 43.8367, lng: 4.3601, region: "OCC" },
  { name: "Clermont-Ferrand", lat: 45.7772, lng: 3.0870, region: "ARA" },
  { name: "Aix-en-Provence", lat: 43.5297, lng: 5.4474, region: "PACA" },
  { name: "Brest", lat: 48.3904, lng: -4.4861, region: "BRE" },
  { name: "Tours", lat: 47.3941, lng: 0.6848, region: "CVL" },
  { name: "Amiens", lat: 49.8941, lng: 2.2958, region: "HDF" },
  { name: "Limoges", lat: 45.8336, lng: 1.2611, region: "NAQ" },
  { name: "Annecy", lat: 45.8992, lng: 6.1294, region: "ARA" },
  { name: "Perpignan", lat: 42.6887, lng: 2.8948, region: "OCC" },
  { name: "Besançon", lat: 47.2378, lng: 6.0241, region: "BFC" },
  { name: "Orléans", lat: 47.9029, lng: 1.9039, region: "CVL" },
  { name: "Rouen", lat: 49.4432, lng: 1.0993, region: "NOR" },
  { name: "Mulhouse", lat: 47.7508, lng: 7.3359, region: "GE" },
  { name: "Caen", lat: 49.1829, lng: -0.3707, region: "NOR" },
  { name: "Nancy", lat: 48.6921, lng: 6.1844, region: "GE" },
  { name: "Avignon", lat: 43.9493, lng: 4.8055, region: "PACA" },
  { name: "Cannes", lat: 43.5528, lng: 7.0174, region: "PACA" }
];

// Liste combinée pour la génération d'événements
const ALL_CITIES = [...SWISS_CITIES, ...FRENCH_CITIES];

// --- CATÉGORIES AVEC EMOJIS ---
const CATEGORY_EMOJIS = {
  // Music Electronic
  "techno": "🎧", "house": "🏠", "trance": "🌀", "drum & bass": "🥁", "dnb": "🥁",
  "dubstep": "💥", "hardstyle": "⚡", "ambient": "🌙", "electronic": "🔊",
  // Music Urban
  "rap": "🎤", "hip-hop": "🎤", "trap": "🔥", "rnb": "💜", "drill": "🔫",
  "afrobeats": "🌍", "dancehall": "🇯🇲", "reggaeton": "💃",
  // Music Other
  "rock": "🎸", "metal": "🤘", "jazz": "🎷", "blues": "🎺", "folk": "🪕",
  "pop": "⭐", "classique": "🎻", "reggae": "🟢",
  // Culture
  "cinéma": "🎬", "théâtre": "🎭", "exposition": "🖼️", "conférence": "🎓",
  "workshop": "🔧", "danse": "💃",
  // Food
  "brunch": "🥐", "bbq": "🍖", "dégustation": "🍷", "food truck": "🚚",
  "marché": "🛒", "gastronomie": "👨‍🍳",
  // Sport
  "course": "🏃", "trail": "🏔️", "cyclisme": "🚴", "natation": "🏊",
  "ski": "⛷️", "fitness": "💪", "yoga": "🧘",
  // Festivals
  "festival": "🎪", "open air": "🌲", "carnaval": "🎭", "fête": "🎉",
  // Services
  "son": "🔊", "lumière": "💡", "sécurité": "🛡️", "décoration": "🎨",
  "traiteur": "🍽️", "transport": "🚐", "photo": "📸", "vidéo": "🎥"
};

// ============================================
// THÈMES UI
// ============================================
const UI_THEMES = [
  {
    name: "Dark Neon",
    bodyBg: "#020617",
    topbarBg: "#020617",
    cardBg: "#020617",
    cardBorder: "rgba(148,163,184,0.6)",
    textMain: "#e5e7eb",
    textMuted: "#9ca3af",
    btnMainBg: "linear-gradient(135deg,#22c55e,#4ade80)",
    btnMainText: "#022c22",
    btnMainShadow: "0 8px 22px rgba(34,197,94,0.75)",
    btnAltBg: "rgba(15,23,42,0.9)",
    btnAltText: "#e5e7eb",
    pillBorder: "rgba(148,163,184,0.6)",
    logoColor: "#ffffff",
    taglineColor: "#e5e7eb"
  },
  {
    name: "Light Pro",
    bodyBg: "#f4f4f5",
    topbarBg: "#ffffff",
    cardBg: "#ffffff",
    cardBorder: "rgba(148,163,184,0.6)",
    textMain: "#020617",
    textMuted: "#6b7280",
    btnMainBg: "linear-gradient(135deg,#22c55e,#16a34a)",
    btnMainText: "#022c22",
    btnMainShadow: "0 8px 22px rgba(22,163,74,0.6)",
    btnAltBg: "#f9fafb",
    btnAltText: "#111827",
    pillBorder: "rgba(148,163,184,0.7)",
    logoColor: "#020617",
    taglineColor: "#4b5563"
  },
  {
    name: "Purple Cyberpunk",
    bodyBg: "#020617",
    topbarBg: "#020617",
    cardBg: "radial-gradient(circle at 0 0,#4c1d95,#020617)",
    cardBorder: "rgba(192,132,252,0.8)",
    textMain: "#f9fafb",
    textMuted: "#a5b4fc",
    btnMainBg: "linear-gradient(135deg,#a855f7,#ec4899)",
    btnMainText: "#fdf2ff",
    btnMainShadow: "0 10px 24px rgba(168,85,247,0.8)",
    btnAltBg: "rgba(15,23,42,0.9)",
    btnAltText: "#e5e7eb",
    pillBorder: "rgba(192,132,252,0.7)",
    logoColor: "#ffffff",
    taglineColor: "#e5e7eb"
  },
  {
    name: "Miami Sunset",
    bodyBg: "radial-gradient(circle at top,#f97316,#1d1b67)",
    topbarBg: "rgba(15,23,42,0.9)",
    cardBg: "rgba(15,23,42,0.9)",
    cardBorder: "rgba(251,146,60,0.7)",
    textMain: "#fefce8",
    textMuted: "#fed7aa",
    btnMainBg: "linear-gradient(135deg,#fb923c,#ec4899)",
    btnMainText: "#111827",
    btnMainShadow: "0 10px 24px rgba(248,113,113,0.7)",
    btnAltBg: "rgba(15,23,42,0.9)",
    btnAltText: "#fefce8",
    pillBorder: "rgba(250,204,21,0.7)",
    logoColor: "#fefce8",
    taglineColor: "#fed7aa"
  },
  {
    name: "Blue Ice",
    bodyBg: "#020617",
    topbarBg: "#020617",
    cardBg: "linear-gradient(135deg,#0f172a,#0b1120)",
    cardBorder: "rgba(148,163,184,0.8)",
    textMain: "#e5e7eb",
    textMuted: "#94a3b8",
    btnMainBg: "linear-gradient(135deg,#0ea5e9,#22c55e)",
    btnMainText: "#022c22",
    btnMainShadow: "0 10px 24px rgba(56,189,248,0.7)",
    btnAltBg: "rgba(15,23,42,0.9)",
    btnAltText: "#e5e7eb",
    pillBorder: "rgba(148,163,184,0.7)",
    logoColor: "#d1fae5",
    taglineColor: "#bbf7d0"
  }
];

// ===============================
// THÈMES MAP
// ===============================
const MAP_THEMES = [
  {
    name: "OSM Clair",
    url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    maxZoom: 19,
    attribution: "© OpenStreetMap"
  },
  {
    name: "Carto Dark Matter",
    url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    maxZoom: 19,
    attribution: "© Carto"
  },
  {
    name: "Carto Light",
    url: "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
    maxZoom: 19,
    attribution: "© Carto"
  }
];

// ============================================
// DONNÉES DE DÉMO
// ============================================
const demoEventBase = [
  {
    id: 1,
    type: "event",
    title: "Soirée Techno Test",
    description:
      "Événement de test local pour valider l’affichage avec un descriptif un peu plus long pour tester la hauteur de la fenêtre.",
    status: "OK",
    startDate: "2025-12-01T22:00:00",
    endDate: "2025-12-02T06:00:00",
    city: "Lausanne",
    address: "Centre-ville, Lausanne",
    lat: 46.5197,
    lng: 6.6323,
    categories: ["Techno"],
    mainCategory: "Techno",
    categoryImage: null,
    boost: "gold",
    imageUrl: null,
    sourceUrl: "https://example.com",
    isAI: false,
    pricingMode: "Entrée payante"
  }
];

const demoBookingBase = [
  {
    id: 101,
    type: "booking",
    name: "DJ Test Booking",
    description: "Artiste de test, profil booking.",
    city: "Genève",
    address: "Genève centre",
    lat: 46.2044,
    lng: 6.1432,
    categories: ["Techno"],
    mainCategory: "Techno",
    categoryImage: null,
    boost: "silver",
    imageUrl: null,
    soundLinks: [],
    email: "booking@example.com",
    phone: "+41 79 111 11 11",
    isAI: false
  }
];

const demoServiceBase = [
  {
    id: 201,
    type: "service",
    name: "Lumières Pro Suisse",
    description: "Prestataire lumière pour clubs, open airs et festivals.",
    city: "Zurich",
    address: "Lichtstrasse 9, 8000 Zürich",
    lat: 47.3769,
    lng: 8.5417,
    categories: ["Lumière"],
    mainCategory: "Lumière",
    categoryImage: null,
    boost: "bronze",
    imageUrl: null,
    email: "contact@lumieres-pro.ch",
    phone: "+41 78 123 45 67",
    isAI: false,
    pricingMode: "Devis"
  }
];

// ============================================
// INIT
// ============================================
// Gérer le retour de Stripe après paiement
async function handleStripeReturn() {
  const urlParams = new URLSearchParams(window.location.search);
  const paymentStatus = urlParams.get('payment');
  const sessionId = urlParams.get('session_id');
  
  if (paymentStatus === 'success' && sessionId) {
    try {
      // Vérifier le statut du paiement
      const response = await fetch(`${API_BASE_URL}/payments/verify-session?session_id=${sessionId}`);
      const data = await response.json();
      
      if (data.success) {
        const paymentType = data.paymentType;
        const items = data.items || [];
        
        if (paymentType === 'contact' || paymentType === 'cart') {
          // Débloquer les contacts
          items.forEach(item => {
            const key = `${item.type}:${item.id}`;
            if (!paidContacts.includes(key)) {
              paidContacts.push(key);
            }
            if (!currentUser.agenda.includes(key)) {
              currentUser.agenda.push(key);
            }
          });
          
          playPaymentSound();
          showNotification(`✅ Paiement réussi ! ${items.length} contact(s) débloqué(s).`, "success");
          
          // Rafraîchir l'affichage
          refreshMarkers();
        } else if (paymentType === 'subscription') {
          // Charger le nouvel abonnement
          await loadUserSubscription();
          playPaymentSound();
          showNotification("✅ Abonnement activé !", "success");
        }
        
        // Nettoyer l'URL
        window.history.replaceState({}, document.title, window.location.pathname);
      } else {
        showNotification("⚠️ Paiement en attente...", "warning");
      }
    } catch (error) {
      console.error('Erreur vérification paiement:', error);
      showNotification("⚠️ Erreur lors de la vérification du paiement", "error");
    }
  } else if (paymentStatus === 'canceled') {
    showNotification("❌ Paiement annulé", "info");
    // Nettoyer l'URL
    window.history.replaceState({}, document.title, window.location.pathname);
  }
}

// Charger le statut de l'abonnement depuis le backend
async function loadUserSubscription() {
  if (!currentUser.isLoggedIn) return;
  
  try {
    const response = await fetch(`${API_BASE_URL}/payments/subscription-status?userId=${currentUser.id}`);
    if (response.ok) {
      const data = await response.json();
      if (data.subscription) {
        currentUser.subscription = data.subscription.plan;
        currentUser.agendaLimit = getAgendaLimit();
        currentUser.alertLimit = getAlertLimit();
        updateSubscriptionBadge();
      }
    }
  } catch (error) {
    console.error('Erreur chargement abonnement:', error);
  }
}

// ============================================
// DEEP LINKING - Ouvrir un event/booking/service depuis l'URL
// ============================================
function handleDeepLink() {
  const urlParams = new URLSearchParams(window.location.search);
  
  // Vérifier si on a un paramètre event, booking ou service
  const eventId = urlParams.get('event');
  const bookingId = urlParams.get('booking');
  const serviceId = urlParams.get('service');
  
  // Fonction pour nettoyer l'URL après l'ouverture (mais garder les paramètres pour les métadonnées)
  function cleanUrl() {
    // NE PAS nettoyer l'URL immédiatement - garder les paramètres pour que les métadonnées restent visibles
    // On nettoiera seulement après que la popup soit ouverte et que les métadonnées soient mises à jour
    // Les paramètres restent dans l'URL pour que les scrapers des réseaux sociaux puissent les lire
  }
  
  // Fonction pour ouvrir la popup après que les données soient chargées
  function tryOpenPopup(type, id, maxAttempts = 10) {
    let attempts = 0;
    const checkInterval = setInterval(() => {
      attempts++;
      let item = null;
      
      if (type === 'event') {
        item = eventsData.find(e => e.id === parseInt(id) || e.id === id);
      } else if (type === 'booking') {
        item = bookingsData.find(b => b.id === parseInt(id) || b.id === id);
      } else if (type === 'service') {
        item = servicesData.find(s => s.id === parseInt(id) || s.id === id);
      }
      
      if (item) {
        clearInterval(checkInterval);
        
        // Mettre à jour les métadonnées Open Graph AVANT d'ouvrir la popup
        updateOpenGraphMetadata(type, parseInt(id), item);
        
        // Attendre un peu pour que les métadonnées soient mises à jour
        setTimeout(() => {
          if (type === 'event') {
            openEventPopupFromDeepLink(item);
          } else if (type === 'booking') {
            currentMode = "booking";
            refreshMarkers();
            openBookingPopupFromDeepLink(item);
          } else if (type === 'service') {
            currentMode = "service";
            refreshMarkers();
            openServicePopupFromDeepLink(item);
          }
        }, 500);
      } else if (attempts >= maxAttempts) {
        clearInterval(checkInterval);
        console.warn(`⚠️ ${type} ${id} non trouvé après ${maxAttempts} tentatives`);
        showNotification(`L'élément demandé n'a pas été trouvé`, "warning");
      }
    }, 500); // Vérifier toutes les 500ms
  }
  
  if (eventId) {
    console.log(`🔗 Deep link détecté: event=${eventId}`);
    // Mettre à jour les métadonnées immédiatement si possible
    const event = eventsData.find(e => e.id === parseInt(eventId) || e.id === eventId);
    if (event) {
      updateOpenGraphMetadata('event', parseInt(eventId), event);
    }
    // Essayer d'ouvrir la popup
    tryOpenPopup('event', eventId);
    return true;
  }
  
  if (bookingId) {
    console.log(`🔗 Deep link détecté: booking=${bookingId}`);
    const booking = bookingsData.find(b => b.id === parseInt(bookingId) || b.id === bookingId);
    if (booking) {
      updateOpenGraphMetadata('booking', parseInt(bookingId), booking);
    }
    tryOpenPopup('booking', bookingId);
    return true;
  }
  
  if (serviceId) {
    console.log(`🔗 Deep link détecté: service=${serviceId}`);
    const service = servicesData.find(s => s.id === parseInt(serviceId) || s.id === serviceId);
    if (service) {
      updateOpenGraphMetadata('service', parseInt(serviceId), service);
    }
    tryOpenPopup('service', serviceId);
    return true;
  }
  
  return false;
}

function openEventPopupFromDeepLink(event) {
  // Centrer la map sur l'event
  if (map && event.lat && event.lng) {
    map.setView([event.lat, event.lng], 14);
  }
  
  // Ouvrir la popup dans un modal
  const popupContent = buildEventPopup(event);
  openPopupModal(popupContent, event);
}

function openBookingPopupFromDeepLink(booking) {
  if (map && booking.lat && booking.lng) {
    map.setView([booking.lat, booking.lng], 14);
  }
  const popupContent = buildBookingPopup(booking);
  openPopupModal(popupContent, booking);
}

function openServicePopupFromDeepLink(service) {
  if (map && service.lat && service.lng) {
    map.setView([service.lat, service.lng], 14);
  }
  const popupContent = buildServicePopup(service);
  openPopupModal(popupContent, service);
}

// Variable pour stocker le marqueur actuel
let currentPopupMarker = null;

function openPopupModal(content, item) {
  // Supprimer un modal existant
  const existingModal = document.getElementById("popup-modal");
  if (existingModal) existingModal.remove();
  
  // Trouver et stocker le marqueur correspondant à cet item
  if (item && item.lat && item.lng) {
    const key = `${item.type}:${item.id}`;
    currentPopupMarker = markerMap[key] || null;
  }
  
  // Utiliser EXACTEMENT la même structure que le mode liste qui fonctionne
  const modalHtml = `
    <div id="popup-modal-content" style="position:relative;width:380px;max-height:85vh;overflow:hidden;background:var(--ui-card-bg);border-radius:16px;border:1px solid var(--ui-card-border);margin:20px;box-shadow:0 20px 60px rgba(0,0,0,0.5);display:flex;flex-direction:column;padding:0;box-sizing:border-box;">
      <button onclick="closePopupModal()" style="position:absolute;top:12px;right:12px;width:36px;height:36px;border-radius:50%;border:none;background:rgba(0,0,0,0.6);color:#fff;cursor:pointer;font-size:20px;z-index:1001;display:flex;align-items:center;justify-content:center;transition:all 0.2s;" onmouseover="this.style.background='rgba(239,68,68,0.8)'" onmouseout="this.style.background='rgba(0,0,0,0.6)'">✕</button>
      <div id="popup-scroll-container" style="flex:1;overflow-y:auto;overflow-x:hidden;scrollbar-width:none;-webkit-overflow-scrolling:touch;width:100%;margin:0;padding:0;box-sizing:border-box;touch-action:pan-y;overscroll-behavior:contain;pointer-events:auto;position:relative;">
        ${content}
      </div>
    </div>
  `;
  
  // Créer ou réutiliser le backdrop - MÊME STRUCTURE QUE MODE LISTE
  let backdrop = document.getElementById("popup-modal-backdrop");
  if (!backdrop) {
    backdrop = document.createElement("div");
    backdrop.id = "popup-modal-backdrop";
    // z-index très élevé pour être devant tout + pointer-events pour bloquer Leaflet
    backdrop.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,0.75);display:flex;align-items:center;justify-content:center;z-index:99999;backdrop-filter:blur(2px);pointer-events:auto;";
    backdrop.onclick = (e) => {
      if (e.target === backdrop) closePopupModal();
    };
    document.body.appendChild(backdrop);
  }
  
  backdrop.innerHTML = modalHtml;
  backdrop.style.display = "flex";
  
  // Empêcher le scroll du body quand la popup est ouverte
  document.body.style.overflow = 'hidden';
  
  // Désactiver COMPLÈTEMENT Leaflet - approche plus agressive
  if (map) {
    try {
      map.scrollWheelZoom.disable();
      map.dragging.disable();
      map.touchZoom.disable();
      map.doubleClickZoom.disable();
      // Bloquer les événements au niveau du conteneur de la map
      const mapContainer = map.getContainer();
      if (mapContainer) {
        mapContainer.style.pointerEvents = 'none';
      }
    } catch(e) {
      console.warn('Erreur désactivation Leaflet:', e);
    }
  }
  
  // FORCER LE SCROLL - Ajouter un gestionnaire wheel explicite après un court délai
  setTimeout(() => {
    const scrollContainer = document.getElementById('popup-scroll-container');
    const modalContent = document.getElementById('popup-modal-content');
    
    if (scrollContainer) {
      // Empêcher Leaflet de capturer les événements
      const stopPropagation = (e) => {
        e.stopPropagation();
        e.stopImmediatePropagation();
      };
      
      // Empêcher tous les événements de toucher Leaflet
      ['wheel', 'touchstart', 'touchmove', 'touchend', 'mousedown', 'mousemove', 'mouseup'].forEach(eventType => {
        scrollContainer.addEventListener(eventType, stopPropagation, { capture: true, passive: false });
        if (modalContent) {
          modalContent.addEventListener(eventType, stopPropagation, { capture: true, passive: false });
        }
      });
      
      // Gestionnaire wheel qui force le scroll
      const handleWheel = (e) => {
        e.stopPropagation();
        e.stopImmediatePropagation();
        
        const scrollHeight = scrollContainer.scrollHeight;
        const clientHeight = scrollContainer.clientHeight;
        const maxScroll = scrollHeight - clientHeight;
        
        if (maxScroll > 0) {
          const delta = e.deltaY || e.detail || (e.wheelDelta ? -e.wheelDelta / 3 : 0);
          // Multiplier par 12 pour un scroll ultra rapide
          const scrollSpeed = delta * 12;
          const currentScroll = scrollContainer.scrollTop;
          const newScroll = Math.max(0, Math.min(maxScroll, currentScroll + scrollSpeed));
          
          scrollContainer.scrollTop = newScroll;
          e.preventDefault();
          return false;
        }
      };
      
      scrollContainer.addEventListener('wheel', handleWheel, { passive: false, capture: true });
      scrollContainer.addEventListener('mousewheel', handleWheel, { passive: false, capture: true });
      scrollContainer.addEventListener('DOMMouseScroll', handleWheel, { passive: false, capture: true });
    }
  }, 100);
}

document.addEventListener("DOMContentLoaded", () => {
  console.log('🏗️ DOM Content Loaded - REGISTER MODAL FIX VERSION - TEST DEPLOYMENT');
  console.log('🚀 REGISTER MODAL FIX DEPLOYED SUCCESSFULLY - VERSION 2024-12-31');

  // Afficher le message de test du site
  setTimeout(() => {
    alert('⚠️ Attention : site encore en test mais vous pouvez voir les avancées just for fun :) popopopopo');
  }, 1000);
  // FORCER "ABOS" IMMÉDIATEMENT au chargement (avant tout autre code)
  const forceABOS = () => {
    const label = document.getElementById("subscription-label");
    if (label && label.textContent !== "ABOS") {
      label.textContent = "ABOS";
      label.innerHTML = "ABOS";
    }
  };
  forceABOS();
  
  // Observer pour maintenir "ABOS" même si quelque chose essaie de le changer
  const label = document.getElementById("subscription-label");
  if (label) {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList' || mutation.type === 'characterData') {
          if (label.textContent !== "ABOS" && label.textContent.trim() !== "ABOS") {
            label.textContent = "ABOS";
            label.innerHTML = "ABOS";
          }
        }
      });
    });
    observer.observe(label, { childList: true, characterData: true, subtree: true });
  }
  
  // Supprimer le bloc "alertes" entre panier et liste dans la topbar
  const removeAlertsButton = () => {
    const topbarCenter = document.querySelector('.topbar-center');
    if (topbarCenter) {
      // Chercher tous les boutons dans topbar-center
      const buttons = topbarCenter.querySelectorAll('button');
      buttons.forEach(btn => {
        const text = btn.textContent || btn.innerText || '';
        // Supprimer si le bouton contient "alertes" ou "🔔" et est entre les modes et Liste
        if ((text.toLowerCase().includes('alertes') || text.includes('🔔')) && 
            btn.onclick && btn.onclick.toString().includes('openAlerts')) {
          btn.remove();
        }
      });
    }
  };
  
  // Supprimer immédiatement et périodiquement
  removeAlertsButton();
  setTimeout(removeAlertsButton, 100);
  setTimeout(removeAlertsButton, 500);
  setInterval(removeAlertsButton, 2000);
  
  // Observer les changements dans le topbar-center
  const topbarCenter = document.querySelector('.topbar-center');
  if (topbarCenter) {
    const topbarObserver = new MutationObserver(() => {
      removeAlertsButton();
    });
    topbarObserver.observe(topbarCenter, { childList: true, subtree: true });
  }
  
  // Charger l'utilisateur sauvegardé
  loadSavedUser();
  
  // Attacher l'event listener au bouton compte
  const accountBtn = document.getElementById("account-topbar-btn");
  if (accountBtn) {
    accountBtn.addEventListener('click', openAccountModal);
  }
  
  // Mettre à jour le bouton compte après chargement
  setTimeout(() => {
    updateAccountButton();
  }, 100);
  
  // Détecter les paramètres URL pour mettre à jour les métadonnées Open Graph IMMÉDIATEMENT
  // Cela doit être fait AVANT que les scrapers des réseaux sociaux ne lisent la page
  const urlParams = new URLSearchParams(window.location.search);
  const eventId = urlParams.get('event');
  const bookingId = urlParams.get('booking');
  const serviceId = urlParams.get('service');
  
  if (eventId || bookingId || serviceId) {
    // Mettre à jour les métadonnées dès que possible
    checkUrlParamsAndUpdateMetadata();
  }
  
  // CRITIQUE : Gérer le callback OAuth Google IMMÉDIATEMENT au chargement
  console.log('🔍 Vérification callback OAuth Google...');
  const oauthCode = urlParams.get('code');
  const oauthState = urlParams.get('state');
  
  if (oauthCode && oauthState) {
    console.log('✅ Callback OAuth détecté dans l\'URL - Traitement...');
    console.log('🔍 Code:', oauthCode.substring(0, 20) + '...');
    console.log('🔍 State:', oauthState);
    
    // Appeler la fonction de gestion du callback
    handleCognitoCallbackIfPresent().catch(error => {
      console.error('❌ Erreur lors du traitement du callback OAuth:', error);
      showNotification('❌ Erreur lors de la connexion Google', 'error');
    });
  } else {
    console.log('ℹ️ Pas de callback OAuth dans l\'URL');
  }
  
  initMap();
  initUI();
  applyUITheme(0);
  applyMapTheme(0);
  
  // Initialiser les alertes de proximité
  if (currentUser.isLoggedIn) {
    checkProximityAlerts();
    updateProximityAlertsBadge();
    // Vérifier les alertes toutes les 30 secondes
    setInterval(checkProximityAlerts, 30000);
  }

  // ============================================
  // INITIALISATION MODE EVENT PAR DÉFAUT
  // ============================================
  // FORCER le mode EVENT dès le chargement (sans clic nécessaire)
  currentMode = "event";
  
  // Initialiser les données de base - GÉNÉRATION IMMÉDIATE
  eventsData = [];
  bookingsData = [...demoBookingBase];
  servicesData = [...demoServiceBase];
  
  // Mettre à jour les références globales
  window.eventsData = eventsData;
  window.bookingsData = bookingsData;
  window.servicesData = servicesData;
  
  // Génération de données IMMÉDIATE (pas d'attente)
  ensureDemoPoints();
  
  // Si toujours vide, génération d'urgence
  if (eventsData.length === 0) {
    console.warn(`⚠️ Génération d'urgence immédiate...`);
    generateEmergencyEvents();
  }

  // FORCER l'affichage de TOUS les points IMMÉDIATEMENT
  filteredData = null;
  selectedCategories = [];
  timeFilter = null;
  dateRangeStart = null;
  dateRangeEnd = null;
  selectedDates = [];
  
  // CRITIQUE: Initialiser la langue AVANT tout le reste pour que window.translations soit disponible
  // S'assurer que window.translations est complètement initialisé AVANT initLanguage()
  if (typeof window !== 'undefined') {
    if (!window.translations || typeof window.translations !== 'object') {
      window.translations = { fr: {}, en: {}, es: {}, zh: {}, hi: {} };
    }
    // S'assurer que toutes les langues existent
    ['fr', 'en', 'es', 'zh', 'hi'].forEach(lang => {
      if (!window.translations[lang] || typeof window.translations[lang] !== 'object') {
        window.translations[lang] = window.translations[lang] || {};
      }
    });
  }
  initLanguage();
  
  // Gérer le deep linking (ouvrir un event depuis l'URL)
  const hasDeepLink = handleDeepLink();
  
  // NOTE: La vérification du profil Google se fait UNIQUEMENT dans handleCognitoCallbackIfPresent()
  // après le callback OAuth. On ne vérifie PAS automatiquement au chargement de la page.
  
  // NOTE: La vérification du profil Google se fait UNIQUEMENT dans handleCognitoCallbackIfPresent()
  // après le callback OAuth. On ne vérifie PAS automatiquement au chargement de la page.
  
  // Mettre à jour l'UI pour refléter le mode event actif IMMÉDIATEMENT
  setTimeout(() => {
    document.querySelectorAll(".mode-btn").forEach(btn => {
      const txt = btn.textContent.trim().toLowerCase();
      const key =
        txt.includes("event") ? "event" :
        txt.includes("booking") ? "booking" :
        txt.includes("service") ? "service" : "";
      btn.classList.toggle("active", key === "event");
    });
    
    // FORCER l'affichage de TOUS les points - CRITIQUE !
    filteredData = null; // null = afficher TOUS les points
    selectedCategories = []; // Aucune catégorie sélectionnée
    timeFilter = null;
    dateRangeStart = null;
    dateRangeEnd = null;
    selectedDates = [];
    
    // Générer les points de base AVANT d'afficher
    ensureDemoPoints();
    
    // S'assurer qu'on a au moins quelques données
    if (eventsData.length === 0) {
      console.warn(`⚠️ eventsData vide après ensureDemoPoints(), génération d'urgence...`);
      generateEmergencyEvents();
    }
    
    // Attendre un peu pour que les données soient prêtes
    setTimeout(() => {
      const data = getActiveData();
      console.log(`🚀 Affichage initial - Mode: ${currentMode}, ${data.length} points disponibles (eventsData: ${eventsData.length})`);
      
      if (data.length > 0) {
        // Un seul appel à refreshMarkers() ici
        refreshMarkers();
        refreshListView();
        console.log(`✅ Mode EVENT activé par défaut - ${data.length} points affichés automatiquement`);
      }
    }, 100);
  }, 300); // Délai pour laisser le temps à la map de s'initialiser

  // Charger les arbres et générer les points avec les bonnes catégories
  loadCategoryTrees().then(() => {
    // S'assurer que les points sont générés pour tous les modes
    ensureDemoPoints();
    
    // S'assurer qu'on a au moins quelques données
    if (eventsData.length === 0) {
      console.warn(`⚠️ eventsData vide après loadCategoryTrees(), génération d'urgence...`);
      generateEmergencyEvents();
    }
    
    // FORCER l'affichage de TOUS les points - CRITIQUE !
    filteredData = null; // null = afficher TOUS les points
    selectedCategories = []; // Aucune catégorie sélectionnée
    timeFilter = null;
    dateRangeStart = null;
    dateRangeEnd = null;
    selectedDates = [];
    
    // Attendre un peu pour que les données soient prêtes
    // UN SEUL appel à refreshMarkers() ici, pas plusieurs
    setTimeout(() => {
      const data = getActiveData();
      if (data.length > 0 && !isRefreshingMarkers) {
        refreshMarkers();
        refreshListView();
      }
    }, 500); // Délai plus long pour éviter les conflits
    
    // Initialiser l'historique des statuts pour les alertes
    initEventStatusHistory();
    
    // Vérifier les changements d'événements toutes les 30 secondes
    setInterval(checkEventChanges, 30000);
    
    // Mettre à jour le badge abonnement et le panier
    setTimeout(() => {
      updateSubscriptionBadge();
      updateCartCount();
    }, 100);
  });
  
  // left panel fermé par défaut
});

// ============================================
// CHARGEMENT DES ARBRES (pour IMAGES uniquement)
// ============================================
function loadCategoryTrees() {
  // Essayer plusieurs chemins possibles selon la configuration du déploiement
  const tryLoadTree = (filename, setter) => {
    const paths = [
      "trees/" + filename,
      "/trees/" + filename
    ];
    
    return Promise.race(
      paths.map(path => 
        fetch(path)
          .then(r => {
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            return r.json();
          })
          .then(j => {
            console.log(`✅ Chargé: ${path}`);
            setter(j);
            return true;
          })
          .catch(() => null)
      )
    ).catch(() => {
      console.warn(`⚠️ Impossible de charger ${filename}`);
      return null;
    });
  };
  
  return Promise.all([
    tryLoadTree("events_tree.json", (j) => {
      EVENTS_TREE = j.Events || j;
    }),
    tryLoadTree("booking_tree.json", (j) => {
      BOOKING_TREE = j.Booking || j;
    }),
    tryLoadTree("service_tree.json", (j) => {
      SERVICE_TREE = j.Service || j;
    })
  ]).then(() => {
    // Une fois tous les arbres chargés, régénérer les points avec les bonnes catégories
    ensureDemoPoints();
    
    // FORCER l'affichage de TOUS les points (pas de filtre par défaut)
    filteredData = null;
    selectedCategories = [];
    timeFilter = null;
    dateRangeStart = null;
    dateRangeEnd = null;
    selectedDates = [];
    
    refreshMarkers();
    refreshListView();
    
    console.log(`🗺️ Tous les points affichés : ${getCurrentData().length} ${currentMode}(s)`);
  });
}

// ============================================
// MAP
// ============================================
function initMap() {
  map = L.map("map").setView([46.8182, 8.2275], 8);

  const theme = MAP_THEMES[mapThemeIndex];
  tileLayer = L.tileLayer(theme.url, {
    maxZoom: theme.maxZoom,
    attribution: theme.attribution
  });
  tileLayer.addTo(map);

  markersLayer = L.layerGroup().addTo(map);
}

function getCurrentData() {
  let data = [];
  if (currentMode === "event") {
    data = eventsData.filter(item => item && item.type === "event");
  } else if (currentMode === "booking") {
    data = bookingsData.filter(item => item && item.type === "booking");
  } else if (currentMode === "service") {
    data = servicesData.filter(item => item && item.type === "service");
  }
  console.log(`📊 getCurrentData() - Mode: ${currentMode}, ${data.length} items (eventsData: ${eventsData.length}, bookingsData: ${bookingsData.length}, servicesData: ${servicesData.length})`);
  return data;
}

function getActiveData() {
  // Si filteredData est null, retourner TOUS les points (pas de filtre actif)
  // Si filteredData est un tableau, retourner les points filtrés
  if (filteredData === null) {
    return getCurrentData(); // TOUS les points
  }
  return filteredData; // Points filtrés
}

// Protection contre les appels récursifs multiples
let isRefreshingMarkers = false;
let lastRefreshTime = 0;
const REFRESH_COOLDOWN = 1000; // 1 seconde entre chaque refresh

function refreshMarkers() {
  // Protection contre les appels multiples trop rapides
  const now = Date.now();
  if (now - lastRefreshTime < REFRESH_COOLDOWN && isRefreshingMarkers) {
    // Ignorer silencieusement pour éviter les milliers de messages
    return;
  }
  
  // Protection contre les appels récursifs multiples
  if (isRefreshingMarkers) {
    return; // Ignorer silencieusement
  }
  
  lastRefreshTime = now;
  
  if (!markersLayer) {
    console.warn("⚠️ markersLayer n'est pas initialisé");
    return;
  }
  
  if (!map) {
    console.warn("⚠️ map n'est pas initialisé");
    return;
  }
  
  // S'assurer que window.t() est disponible avant de continuer
  if (typeof window.t !== 'function') {
    console.warn("⚠️ window.t() n'est pas disponible, attente...");
    // Protection contre les boucles infinies - limiter à 10 tentatives
    if (!window._refreshMarkersAttempts) {
      window._refreshMarkersAttempts = 0;
    }
    if (window._refreshMarkersAttempts < 10) {
      window._refreshMarkersAttempts++;
      setTimeout(() => {
        isRefreshingMarkers = false; // Réinitialiser le flag avant la nouvelle tentative
        refreshMarkers();
      }, 100);
    } else {
      console.error("❌ Trop de tentatives pour refreshMarkers(), arrêt");
      window._refreshMarkersAttempts = 0;
      isRefreshingMarkers = false;
    }
    return;
  }
  
  // Réinitialiser le compteur si window.t() est disponible
  window._refreshMarkersAttempts = 0;
  
  isRefreshingMarkers = true;
  
  // SUPPRIMER TOUS LES MARQUEURS AVANT D'AJOUTER LES NOUVEAUX
  markersLayer.clearLayers();
  markerMap = {};
  console.log(`🗑️ Tous les marqueurs supprimés avant rafraîchissement`);

  // FORCER l'affichage de TOUS les points si aucun filtre actif
  const data = getActiveData();
  
  console.log(`📊 Données pour mode ${currentMode}: ${data.length} items (eventsData: ${eventsData.length}, bookingsData: ${bookingsData.length}, servicesData: ${servicesData.length})`);
  
  if (!data || data.length === 0) {
    console.warn(`⚠️ Aucune donnée disponible pour le mode ${currentMode}`);
    console.log(`💡 Tentative de régénération des points...`);
    
    // Forcer la génération de données
    ensureDemoPoints();
    
    // Attendre un peu pour que les données soient générées
    setTimeout(() => {
      const dataAfter = getActiveData();
      console.log(`📊 Après ensureDemoPoints() - Mode: ${currentMode}, ${dataAfter.length} items (eventsData: ${eventsData.length}, bookingsData: ${bookingsData.length}, servicesData: ${servicesData.length})`);
      
      if (dataAfter && dataAfter.length > 0) {
        console.log(`✅ ${dataAfter.length} points générés après ensureDemoPoints()`);
        // Réessayer avec les nouvelles données (seulement si pas déjà en cours)
        if (!isRefreshingMarkers) {
          isRefreshingMarkers = false; // Réinitialiser le flag avant l'appel récursif
          refreshMarkers();
          refreshListView();
        }
      } else {
        console.error(`❌ Toujours aucune donnée après ensureDemoPoints() pour le mode ${currentMode}`);
        // Générer au moins quelques points de base en urgence
        if (currentMode === "event" && eventsData.length === 0) {
          console.log(`🚨 Génération d'urgence de points de base...`);
          generateEmergencyEvents();
          if (!isRefreshingMarkers) {
            isRefreshingMarkers = false; // Réinitialiser le flag avant l'appel récursif
            refreshMarkers();
            refreshListView();
          }
        }
      }
      // Réinitialiser le flag après la tentative
      isRefreshingMarkers = false;
    }, 50);
    return;
  }
  
  // Ne pas logger à chaque refresh pour éviter les milliers de messages
  // console.log(`🔄 Refresh markers: ${data.length} points (filteredData: ${filteredData ? 'filtré' : 'null = tous les points'}) - Mode: ${currentMode}`);
  
  let added = 0;
  let skipped = 0;
  let errors = 0;
  
  data.forEach(item => {
    if (!item) {
      skipped++;
      return;
    }
    
    // Vérifier que l'item correspond au mode actuel
    if (item.type !== currentMode) {
      skipped++;
      return;
    }
    
    if (typeof item.lat !== "number" || typeof item.lng !== "number" || isNaN(item.lat) || isNaN(item.lng)) {
      console.warn(`⚠️ Point invalide: ${item.id} (lat: ${item.lat}, lng: ${item.lng})`);
      skipped++;
      return;
    }
    
    try {
    const icon = buildMarkerIcon(item);
    const marker = L.marker([item.lat, item.lng], { icon });
    marker.bindPopup(buildPopupHtml(item), { maxWidth: 360 });
    
    // Intercepter l'ouverture de la popup Leaflet et la remplacer par notre modal avec scroll
    marker.on('popupopen', function() {
      // Fermer la popup Leaflet immédiatement
      marker.closePopup();
      
      // Stocker le marqueur pour le recentrage à la fermeture
      currentPopupMarker = marker;
      
      // Ouvrir notre modal avec scroll
      const popupContent = buildPopupHtml(item);
      openPopupModal(popupContent, item);
    });
    
    markersLayer.addLayer(marker);

    const key = `${item.type}:${item.id}`;
    markerMap[key] = marker;
      added++;
    } catch (err) {
      // Ne pas logger toutes les erreurs pour éviter les milliers de messages
      errors++;
      skipped++;
      // Logger seulement la première erreur pour diagnostiquer
      if (errors === 1) {
        console.error(`❌ Première erreur lors de l'ajout d'un marqueur:`, err.message || err);
      }
    }
  });
  
  // Logger seulement si des erreurs ou si c'est le premier chargement
  if (errors > 0 || added === 0) {
    console.log(`✅ ${added} marqueurs affichés (mode: ${currentMode})${skipped > 0 ? `, ${skipped} ignorés` : ''}${errors > 0 ? `, ${errors} erreurs` : ''}`);
  }
  
  // Vérifier les alertes de proximité après le rafraîchissement des marqueurs
  if (currentUser.isLoggedIn) {
    checkProximityAlerts();
  }
  
  // Nettoyer les événements passés (sauf organisateurs)
  cleanExpiredEvents();
  
  // Ajuster la vue pour voir tous les marqueurs si c'est le premier chargement
  if (added > 0 && markersLayer && typeof markersLayer.getBounds === 'function') {
    try {
      const bounds = markersLayer.getBounds();
      if (bounds && bounds.isValid && bounds.isValid()) {
        map.fitBounds(bounds.pad(0.1));
      }
    } catch (e) {
      // Ne pas logger pour éviter les milliers de messages
    }
  }
  
  // Réinitialiser le flag après un court délai pour permettre les appels légitimes
  setTimeout(() => {
    isRefreshingMarkers = false;
  }, 100);
}

// ============================================
// LOGIQUE IMAGES – AUCUN ÉCRAN NOIR
// ============================================

// Liste complète des fichiers images disponibles par mode
const AVAILABLE_IMAGES = {
  event: [
    "afro", "afrobeats", "arts vivants", "atelier", "auto", "balkan", "BassMusic", "blind test",
    "brocante", "buiseness & communauté", "Carnaval", "Chillambient", "cinéma", "cirque", "Conduite",
    "conférence", "conte", "course à pied", "culture générale", "danse", "débat", "défilé", 
    "dégustation bière", "dégustation gastronomie", "dégustation spiritueux", "dégustation vin",
    "Drum&Bass", "Dub", "electronic", "eventdefault", "exposition", "festival & grandes fêtes", "foire",
    "folk", "foodanddrink", "HardMusic", "hardrock", "hiphop", "house", "indie",
    "jazzsoulfunk", "jeux-lottos", "karaoke", "latin", "live musique", "loisirs & animations",
    "lotto", "marché", "marrionnette", "metal", "music", "networking", "open air", "opéra",
    "oriental", "parade", "peinture", "photographie", "PopVariété", "Pride", "punkrock",
    "quiz", "rallye", "rap", "reggae", "rencontre associative", "rencontre célibaire", "RnB",
    "rock", "salon", "sculpture", "ska", "Soirée jeux", "sportaquatique", "sportdeglisse",
    "sports", "sportsaériens", "Sportsterrestre", "street artjpg", "streetparade",
    "techno", "théâtre", "tournoi", "Trance", "trap", "urban", "vidéo art", "world"
  ],
  booking: ["artistesDJs", "bookingdefault", "LiveActs", "performers", "VJ"],
  service: ["décorationart", "location de matériel", "performers", "sécuritéetlogistique", "servicedefault", "technique", "VJ"]
};

// Extensions possibles
const IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "webp"];

// Trouve le meilleur fichier image correspondant à une catégorie
function findBestImageMatch(categoryName, mode) {
  if (!categoryName || !mode) return null;
  
  const availableImages = AVAILABLE_IMAGES[mode] || [];
  const searchName = categoryName.toLowerCase()
    .normalize("NFD").replace(/[\u0300-\u036f]/g, ""); // Sans accents pour la recherche
  
  // 1. Recherche exacte (insensible à la casse)
  for (const img of availableImages) {
    const imgLower = img.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    if (imgLower === searchName) {
      return img;
    }
  }
  
  // 2. Recherche par inclusion
  for (const img of availableImages) {
    const imgLower = img.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    if (imgLower.includes(searchName) || searchName.includes(imgLower)) {
      return img;
    }
  }
  
  // 3. Mappings personnalisés catégorie → image
  const categoryMappings = {
    // Electronic
    "techno": "techno", "acid techno": "techno", "minimal techno": "techno",
    "hard techno": "techno", "industrial techno": "techno", "melodic techno": "techno",
    "house": "house", "deep house": "house", "tech house": "house", "progressive house": "house",
    "trance": "Trance", "psytrance": "Trance", "goa": "Trance", "uplifting trance": "Trance",
    "progressive psy": "Trance", "dark psy": "Trance", "full on": "Trance", "forest": "Trance",
    "hi-tech": "Trance", "fullon": "Trance", "darkpsy": "Trance", "progressivepsy": "Trance",
    "drum & bass": "Drum&Bass", "dnb": "Drum&Bass", "neurofunk": "Drum&Bass", "jungle": "Drum&Bass",
    "liquid dnb": "Drum&Bass", "jump up": "Drum&Bass", "liquiddnb": "Drum&Bass", "jumpup": "Drum&Bass",
    "dubstep": "BassMusic", "bass music": "BassMusic", "riddim": "BassMusic",
    "hardstyle": "HardMusic", "hardcore": "HardMusic", "gabber": "HardMusic",
    "ambient": "Chillambient", "chillout": "Chillambient", "lofi": "Chillambient",
    "electronic": "electronic",
    
    // Urban
    "rap": "rap", "hip-hop": "hiphop", "hiphop": "hiphop", "trap": "trap",
    "rnb": "RnB", "r&b": "RnB", "afrobeats": "afrobeats", "afro": "afro",
    "dancehall": "reggae", "reggaeton": "latin",
    
    // Rock/Metal
    "rock": "rock", "indie rock": "indie", "punk": "punkrock", "punk rock": "punkrock",
    "punkrock": "punkrock", "metal": "metal", "hard rock": "hardrock",
    "alternative rock": "rock", "indie": "indie", "thrash metal": "metal", "metalcore": "metal",
    
    // Jazz/Soul
    "jazz": "jazzsoulfunk", "soul": "jazzsoulfunk", "funk": "jazzsoulfunk",
    "blues": "jazzsoulfunk", "swing": "jazzsoulfunk",
    
    // World
    "reggae": "reggae", "dub": "Dub", "ska": "ska", "latin": "latin",
    "balkan": "balkan", "oriental": "oriental", "world": "world", "folk": "folk",
    
    // Pop
    "pop": "PopVariété", "variété": "PopVariété", "chanson française": "PopVariété",
    
    // Culture
    "cinéma": "cinéma", "cinema": "cinéma", "film": "cinéma",
    "théâtre": "théâtre", "theatre": "théâtre", "stand-up": "théâtre",
    "exposition": "exposition", "expo": "exposition", "galerie": "exposition",
    "conférence": "conférence", "débat": "débat", "workshop": "atelier", "atelier": "atelier",
    "danse": "danse",
    
    // Food
    "brunch": "dégustation gastronomie", "bbq": "dégustation gastronomie",
    "dégustation": "dégustation vin", "food": "dégustation gastronomie",
    "gastronomie": "dégustation gastronomie",
    
    // Loisirs
    "marché": "marché", "brocante": "brocante", "foire": "foire",
    "quiz": "quiz", "blind test": "blind test", "karaoke": "karaoke",
    "jeux": "Soirée jeux", "festival": "festival & grandes fêtes", "open air": "open air",
    "festival musique": "festival & grandes fêtes", "festivalmusique": "festival & grandes fêtes",
    "carnaval": "Carnaval", "parade": "parade", "pride": "Pride",
    
    // Sport
    "sport": "sports", "course": "Sportsterrestre", "course à pied": "Sportsterrestre",
    "trail": "Sportsterrestre", "cyclisme": "Sportsterrestre", "fitness": "Sportsterrestre",
    "drill": "hiphop",
    "natation": "sportaquatique", "ski": "sportdeglisse", "snowboard": "sportdeglisse",
    
    // Booking
    "dj": "artistesDJs", "djs": "artistesDJs", "producteur": "artistesDJs",
    "live": "LiveActs", "live act": "LiveActs", "performer": "performers",
    "vj": "VJ", "mapping": "VJ",
    
    // Service
    "son": "technique", "lumière": "technique", "technique": "technique",
    "décoration": "décorationart", "sécurité": "sécuritéetlogistique",
    "location": "location de matériel"
  };
  
  const mapping = categoryMappings[searchName];
  if (mapping) {
    return mapping;
  }
  
  // 4. Recherche par mots-clés
  const words = searchName.split(/[\s\-\/&]+/).filter(Boolean);
  for (const word of words) {
    if (word.length < 3) continue;
    for (const img of availableImages) {
      const imgLower = img.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
      if (imgLower.includes(word)) {
        return img;
      }
    }
  }
  
  return null;
}

// Génère différentes variantes possibles d'un nom de catégorie
function generateCategoryNameVariants(name) {
  if (!name) return [];

  const original = String(name);
  const variants = new Set();
  
  // Utiliser le système de matching intelligent
  const mode = currentMode || "event";
  const bestMatch = findBestImageMatch(original, mode);
  
  if (bestMatch) {
    variants.add(bestMatch);
  }
  
  // Ajouter aussi les variantes classiques au cas où
  const base = original.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  variants.add(original);
  variants.add(original.toLowerCase());
  variants.add(base);
  variants.add(base.replace(/\s+/g, ""));
  variants.add(base.charAt(0).toUpperCase() + base.slice(1));

  return Array.from(variants);
}

function getModeFolderForItem(item) {
  if (!item || !item.type) return null;
  const key = item.type.toLowerCase();
  return MODE_IMAGE_FOLDERS[key] || null;
}

// Retourne une liste de noms de catégories de la plus spécifique à la plus générale
// PRIORITÉ : Sous-catégories les plus profondes d'abord, puis remonte
function getCategoryLineageForItem(item) {
  const result = [];
  
  // 1. TOUTES les catégories spécifiques (sous-catégories) - PRIORITÉ MAXIMALE
  if (item.categories && Array.isArray(item.categories)) {
    // Les catégories dans l'array sont généralement les plus spécifiques
    item.categories.forEach(cat => {
      if (cat && !result.includes(cat)) {
        result.push(cat);
      }
    });
  }
  
  // 2. MainCategory (catégorie principale) - si pas déjà inclus
  if (item.mainCategory && !result.includes(item.mainCategory)) {
    result.push(item.mainCategory);
  }
  
  // 3. Si aucune catégorie trouvée, essayer d'autres champs
  if (result.length === 0) {
    const fallback = item.category || item.type || "";
    if (fallback) result.push(fallback);
  }
  
  // Retourner dans l'ordre : plus spécifique → plus général
  // (déjà dans le bon ordre : categories d'abord, puis mainCategory)
  return result;
}

// Construit la liste complète des chemins d’images possibles pour un item
function getImageCandidatesForItem(item) {
  const modeFolder = getModeFolderForItem(item);
  const candidates = [];

  if (!modeFolder) {
    candidates.push(OVERLAY_IMAGES.DEFAULT);
    return candidates;
  }

  // 1) si le back-end / IA fournit déjà un nom de fichier
  if (item.categoryImage) {
    const forcedName = String(item.categoryImage);
    if (/\.(jpg|jpeg|png|webp)$/i.test(forcedName)) {
      candidates.push(
        `${ASSETS_BASE}/${CAT_IMG_DIR}/${modeFolder}/${forcedName}`
      );
    } else {
      ["jpg", "jpeg", "png", "webp"].forEach(ext => {
        candidates.push(
          `${ASSETS_BASE}/${CAT_IMG_DIR}/${modeFolder}/${forcedName}.${ext}`
        );
      });
    }
  }

  // 2) à partir des noms de catégories (catégorie + parents)
  const lineage = getCategoryLineageForItem(item);
  const exts = ["jpg", "jpeg", "png", "webp"];

  lineage.forEach(name => {
    const variants = generateCategoryNameVariants(name);
    variants.forEach(v => {
      exts.forEach(ext => {
        candidates.push(
          `${ASSETS_BASE}/${CAT_IMG_DIR}/${modeFolder}/${v}.${ext}`
        );
      });
    });
  });

  // 3) fallback générique par mode (noms de fichiers réels)
  if (item.type === "booking") {
    candidates.push(
      `${ASSETS_BASE}/${CAT_IMG_DIR}/${modeFolder}/bookingdefault.jpg`
    );
  } else if (item.type === "service") {
    candidates.push(
      `${ASSETS_BASE}/${CAT_IMG_DIR}/${modeFolder}/servicedefault.jpg`
    );
  } else if (item.type === "event") {
    candidates.push(
      `${ASSETS_BASE}/${CAT_IMG_DIR}/${modeFolder}/eventdefault.jpg`
    );
  }

  // 4) fallback overlay global
  candidates.push(OVERLAY_IMAGES.DEFAULT);

  const unique = Array.from(new Set(candidates));
  return unique;
}

// Handler global image fallback
window.__mapEventImageFallback = function (img) {
  if (!img || !img.dataset) {
    // Si pas de fallback, afficher le gradient
    if (img) {
      img.style.display = "block";
      img.style.background = "linear-gradient(135deg,#3b82f6,#8b5cf6)";
      img.style.width = "100%";
      img.style.height = "200px";
    }
    return;
  }
  const list = (img.dataset.fallback || "").split("|").filter(Boolean);
  if (!list.length) {
    img.onerror = null;
    // Afficher le gradient si pas d'image par défaut
    img.style.display = "block";
    img.style.background = "linear-gradient(135deg,#3b82f6,#8b5cf6)";
    img.style.width = "100%";
    img.style.height = "200px";
    img.src = OVERLAY_IMAGES.DEFAULT;
    return;
  }
  const next = list.shift();
  img.dataset.fallback = list.join("|");
  img.src = next;
};

// Renvoie la balise <img> complète
function buildMainImageTag(item, altText) {
  const candidates = getImageCandidatesForItem(item);
  const primary = candidates[0] || OVERLAY_IMAGES.DEFAULT;
  const fallbacks = candidates.slice(1).join("|");
  const altSafe = escapeHtml(altText || "");

  return `
    <img 
      src="${primary}"
      alt="${altSafe}"
      style="width:100%;min-height:280px;max-height:400px;object-fit:cover;display:block;margin:0;padding:0;border:none;box-sizing:border-box;background:linear-gradient(135deg,#3b82f6,#8b5cf6);vertical-align:top;"
      data-fallback="${escapeHtml(fallbacks)}"
      onerror="(function(img){try{if(window.__mapEventImageFallback){window.__mapEventImageFallback(img);}else{img.style.display='block';img.style.background='linear-gradient(135deg,#3b82f6,#8b5cf6)';img.style.width='100%';img.style.minHeight='280px';img.style.maxHeight='400px';img.style.objectFit='cover';img.style.verticalAlign='top';}}catch(e){console.warn('Image fallback error:',e);}})(this)"
      onload="this.style.background='transparent';this.style.display='block';"
      loading="eager"
    >
  `;
}

// ============================================
// ICONES & POPUPS – BOOST & CAT
// ============================================
function getBoostColor(boost) {
  const colors = {
    bronze: "#cd7f32",
    silver: "#c0c0c0",
    gold: "#ffd700",
    platinum: "#ef4444" // Rouge pour platinum
  };
  if (!boost || boost === "basic") return "var(--ui-card-border)";
  return colors[boost] || "#a855f7";
}

// ============================================
// SYSTÈME D'ENCHÈRES PLATINUM TOP 10 PAR RÉGION
// ============================================

// Définir les régions (par canton en Suisse, par département en France, etc.)
function getRegionFromCoords(lat, lng) {
  // Suisse - par canton approximatif
  if (lat >= 45.8 && lat <= 47.9 && lng >= 5.9 && lng <= 10.5) {
    if (lng < 7.0) return "region_geneve";
    if (lng < 7.5 && lat < 46.8) return "region_lausanne";
    if (lng < 8.0) return "region_berne_ouest";
    if (lng < 8.6) return "region_berne_zurich";
    if (lat > 47.2) return "region_zurich_nord";
    return "region_zurich_sud";
  }
  // France
  if (lat >= 41.0 && lat <= 51.5 && lng >= -5.5 && lng <= 10.0) {
    if (lat > 48.5 && lng > 1.5 && lng < 3.5) return "region_paris";
    if (lat > 43.0 && lat < 44.5 && lng > 3.0 && lng < 8.0) return "region_sud_est";
    if (lat < 44.0 && lng < 0.5) return "region_sud_ouest";
    return "region_france_autre";
  }
  return "region_internationale";
}

// Calculer les rangs Platinum pour tous les événements
function calculatePlatinumRanks() {
  // Grouper les événements platinum par région
  const platinumByRegion = {};
  
  eventsData.forEach(ev => {
    if (ev.boost === "platinum") {
      const region = getRegionFromCoords(ev.lat, ev.lng);
      if (!platinumByRegion[region]) {
        platinumByRegion[region] = [];
      }
      platinumByRegion[region].push(ev);
    }
  });
  
  // Pour chaque région, trier par montant d'enchère et assigner les rangs
  Object.keys(platinumByRegion).forEach(region => {
    const events = platinumByRegion[region];
    
    // Trier par platinumBid décroissant (plus on paie, plus on est haut)
    events.sort((a, b) => (b.platinumBid || 15) - (a.platinumBid || 15));
    
    // Assigner les rangs (1 = Top 1, 10 = Top 10)
    events.forEach((ev, index) => {
      // Maximum Top 10, les autres restent à 10
      ev.platinumRank = Math.min(index + 1, 10);
      ev.platinumRegion = region;
    });
  });
  
  // Aussi pour bookings et services
  bookingsData.forEach(b => {
    if (b.boost === "platinum") {
      const region = getRegionFromCoords(b.lat, b.lng);
      b.platinumRank = b.platinumRank || Math.floor(Math.random() * 10) + 1;
      b.platinumRegion = region;
    }
  });
  
  servicesData.forEach(s => {
    if (s.boost === "platinum") {
      const region = getRegionFromCoords(s.lat, s.lng);
      s.platinumRank = s.platinumRank || Math.floor(Math.random() * 10) + 1;
      s.platinumRegion = region;
    }
  });
}

// Obtenir le prix minimum pour atteindre un rang dans une région
function getMinBidForRank(region, targetRank) {
  const platinumInRegion = eventsData.filter(ev => 
    ev.boost === "platinum" && getRegionFromCoords(ev.lat, ev.lng) === region
  );
  
  if (platinumInRegion.length === 0) {
    // Personne dans la région = 15.- pour être Top 1
    return 15;
  }
  
  // Trier par enchère décroissante
  platinumInRegion.sort((a, b) => (b.platinumBid || 15) - (a.platinumBid || 15));
  
  if (targetRank > platinumInRegion.length) {
    // Pas assez de personnes pour ce rang = 15.- minimum
    return 15;
  }
  
  // Pour être à ce rang, il faut payer plus que celui qui est actuellement à ce rang
  const currentAtRank = platinumInRegion[targetRank - 1];
  return (currentAtRank?.platinumBid || 15) + 1;
}

// Mapping des catégories vers leurs IMAGES
// Utilise les vraies images de catégories au lieu des emojis
const CATEGORY_IMAGE_MAP = {
  // === MUSIQUE ÉLECTRONIQUE ===
  "techno": "techno.jpg",
  "acid techno": "techno.jpg",
  "tech house": "house.jpg",
  "deep house": "house.jpg",
  "house": "house.jpg",
  "minimal": "electronic.jpg",
  "progressive house": "house.jpg",
  "trance": "Trance.jpeg",
  "psytrance": "Trance.jpeg",
  "progressive psy": "Trance.jpeg",
  "goa": "Trance.jpeg",
  "hardstyle": "HardMusic.jpg",
  "hardcore": "HardMusic.jpg",
  "gabber": "HardMusic.jpg",
  "drum and bass": "Drum&Bass.jpg",
  "dnb": "Drum&Bass.jpg",
  "jungle": "Drum&Bass.jpg",
  "dubstep": "BassMusic.jpg",
  "bass music": "BassMusic.jpg",
  "breakbeat": "electronic.jpg",
  "electro": "electronic.jpg",
  "electronic": "electronic.jpg",
  "edm": "electronic.jpg",
  "ambient": "Chillambient.jpg",
  "chill": "Chillambient.jpg",
  "downtempo": "Chillambient.jpg",
  "lounge": "Chillambient.jpg",
  "dub": "Dub.jpg",
  
  // === MUSIQUE URBAINE ===
  "rap": "rap.jpg",
  "hip hop": "hiphop.jpg",
  "hip-hop": "hiphop.jpg",
  "hiphop": "hiphop.jpg",
  "trap": "trap.jpg",
  "drill": "trap.jpg",
  "r&b": "RnB.jpg",
  "rnb": "RnB.jpg",
  "urban": "urban.jpg",
  
  // === MUSIQUE TRADITIONNELLE ===
  "rock": "rock.jpg",
  "rock alternatif": "rock.jpg",
  "indie rock": "indie.jpg",
  "indie": "indie.jpg",
  "punk": "punkrock.jpg",
  "punk rock": "punkrock.jpg",
  "metal": "metal.jpg",
  "heavy metal": "metal.jpg",
  "hard rock": "hardrock.jpg",
  "folk": "folk.jpg",
  "country": "folk.jpg",
  "jazz": "jazzsoulfunk.jpg",
  "soul": "jazzsoulfunk.jpg",
  "funk": "jazzsoulfunk.jpg",
  "blues": "jazzsoulfunk.jpg",
  "pop": "PopVariété.jpg",
  "variété": "PopVariété.jpg",
  "chanson française": "PopVariété.jpg",
  "ska": "ska.jpg",
  "reggae": "reggae.jpg",
  "afro": "afro.jpg",
  "afrobeat": "afrobeats.jpg",
  "afrobeats": "afrobeats.jpg",
  "latin": "latin.jpg",
  "latino": "latin.jpg",
  "salsa": "latin.jpg",
  "bachata": "latin.jpg",
  "reggaeton": "latin.jpg",
  "balkan": "balkan.jpg",
  "oriental": "oriental.jpg",
  "world": "world.jpg",
  "opéra": "opéra.jpg",
  "classique": "opéra.jpg",
  "live": "live musique.jpg",
  "live musique": "live musique.jpg",
  "concert": "live musique.jpg",
  "music": "music.jpg",
  "musique": "music.jpg",
  
  // === ÉVÉNEMENTS CULTURELS ===
  "festival": "festival & grandes fêtes.jpg",
  "open air": "open air.jpg",
  "théâtre": "théâtre.jpg",
  "spectacle": "arts vivants.jpg",
  "arts vivants": "arts vivants.jpg",
  "danse": "danse.jpg",
  "ballet": "danse.jpg",
  "cirque": "cirque.jpg",
  "magie": "cirque.jpg",
  "cabaret": "arts vivants.jpg",
  "conte": "conte.jpg",
  "marionnette": "marrionnette.jpg",
  
  // === CINÉMA & ART ===
  "cinéma": "cinéma.jpg",
  "film": "cinéma.jpg",
  "projection": "cinéma.jpg",
  "exposition": "exposition.jpg",
  "expo": "exposition.jpg",
  "musée": "exposition.jpg",
  "galerie": "exposition.jpg",
  "photographie": "photographie.jpg",
  "photo": "photographie.jpg",
  "peinture": "peinture.jpg",
  "sculpture": "sculpture.jpg",
  "street art": "street artjpg.jpg",
  "vidéo art": "vidéo art.jpg",
  
  // === SPORTS ===
  "sport": "sports.jpg",
  "sports": "sports.jpg",
  "football": "Sportsterrestre.jpg",
  "tennis": "Sportsterrestre.jpg",
  "basketball": "Sportsterrestre.jpg",
  "course à pied": "course à pied.jpg",
  "running": "course à pied.jpg",
  "marathon": "course à pied.jpg",
  "trail": "course à pied.jpg",
  "randonnée": "course à pied.jpg",
  "ski": "sportdeglisse.jpg",
  "snowboard": "sportdeglisse.jpg",
  "glisse": "sportdeglisse.jpg",
  "natation": "sportaquatique.png",
  "piscine": "sportaquatique.png",
  "aquatique": "sportaquatique.png",
  "aérien": "sportsaériens.jpg",
  "parachute": "sportsaériens.jpg",
  "parapente": "sportsaériens.jpg",
  "auto": "auto.jpg",
  "rallye": "rallye.jpg",
  "conduite": "Conduite.jpg",
  "tournoi": "tournoi.jpg",
  
  // === GASTRONOMIE ===
  "food": "foodanddrink.jpg",
  "gastronomie": "dégustation gastronomie.jpg",
  "brunch": "foodanddrink.jpg",
  "dégustation vin": "dégustation vin.jpg",
  "vin": "dégustation vin.jpg",
  "dégustation bière": "dégustation bière.jpg",
  "bière": "dégustation bière.jpg",
  "dégustation spiritueux": "dégustation spiritueux.jpg",
  "cocktail": "dégustation spiritueux.jpg",
  
  // === MARCHÉS & FOIRES ===
  "marché": "marché.jpg",
  "brocante": "brocante.jpg",
  "vide-grenier": "brocante.jpg",
  "foire": "foire.jpg",
  "salon": "salon.jpg",
  "carnaval": "Carnaval.jpg",
  "parade": "parade.jpg",
  "street parade": "streetparade.jpg",
  "pride": "Pride.jpg",
  "défilé": "défilé.jpg",
  
  // === JEUX & ANIMATIONS ===
  "quiz": "quiz.jpg",
  "blind test": "blind test.jpg",
  "karaoke": "karaoke.jpg",
  "karaoké": "karaoke.jpg",
  "jeux": "jeux-lottos.jpg",
  "soirée jeux": "Soirée jeux.jpg",
  "lotto": "lotto.jpg",
  "loterie": "lotto.jpg",
  "loisirs": "loisirs & animations.jpg",
  "animation": "loisirs & animations.jpg",
  
  // === BUSINESS & COMMUNAUTÉ ===
  "conférence": "conférence.jpg",
  "séminaire": "conférence.jpg",
  "networking": "networking.jpg",
  "business": "buiseness & communauté.jpg",
  "atelier": "atelier.jpg",
  "workshop": "atelier.jpg",
  "débat": "débat.jpg",
  "rencontre": "rencontre associative.jpg",
  "associatif": "rencontre associative.jpg",
  "célibataire": "rencontre célibaire.jpg"
};

// Mapping pour les SERVICES (mode service)
const SERVICE_IMAGE_MAP = {
  "dj": "booking/artistesDJs.jpg",
  "artiste": "booking/artistesDJs.jpg",
  "live": "booking/LiveActs.jpg",
  "live act": "booking/LiveActs.jpg",
  "décoration": "service/décorationart.jpg",
  "décor": "service/décorationart.jpg",
  "art": "service/décorationart.jpg",
  "location": "service/location de matériel.jpg",
  "matériel": "service/location de matériel.jpg",
  "performer": "service/performers.jpg",
  "danseur": "service/performers.jpg",
  "sécurité": "service/sécuritéetlogistique.jpg",
  "logistique": "service/sécuritéetlogistique.jpg",
  "technique": "service/technique.jpg",
  "son": "service/technique.jpg",
  "lumière": "service/technique.jpg",
  "vj": "service/VJ.jpg",
  "vidéo": "service/VJ.jpg"
};

// Fonction pour obtenir l'image de catégorie
function getCategoryImage(item) {
  const categories = item.categories || [];
  const type = item.type || "event";
  
  // Chercher du plus spécifique au plus général
  for (let i = categories.length - 1; i >= 0; i--) {
    const cat = categories[i].toString().toLowerCase().trim();
    
    if (type === "service" && SERVICE_IMAGE_MAP[cat]) {
      return `assets/category_images/${SERVICE_IMAGE_MAP[cat]}`;
    }
    
    if (CATEGORY_IMAGE_MAP[cat]) {
      return `assets/category_images/event/${CATEGORY_IMAGE_MAP[cat]}`;
    }
    
    // Recherche partielle
    for (const [key, img] of Object.entries(CATEGORY_IMAGE_MAP)) {
      if (cat.includes(key) || key.includes(cat)) {
        return `assets/category_images/event/${img}`;
      }
    }
  }
  
  // Essayer avec mainCategory
  if (item.mainCategory) {
    const mainCat = item.mainCategory.toString().toLowerCase().trim();
    if (CATEGORY_IMAGE_MAP[mainCat]) {
      return `assets/category_images/event/${CATEGORY_IMAGE_MAP[mainCat]}`;
    }
  }
  
  // Image par défaut selon le type
  if (type === "booking") return "assets/category_images/booking/bookingdefault.jpg";
  if (type === "service") return "assets/category_images/service/servicedefault.jpg";
  return "assets/category_images/event/eventdefault.jpg";
}

function getCategoryEmoji(item) {
  const cat = (
    item.mainCategory ||
    (item.categories && item.categories[0]) ||
    ""
  )
    .toString()
    .toLowerCase();

  if (
    cat.includes("techno") ||
    cat.includes("house") ||
    cat.includes("trance") ||
    cat.includes("electro")
  )
    return "🎧";
  if (cat.includes("rap") || cat.includes("hip") || cat.includes("trap"))
    return "🎤";
  if (cat.includes("rock") || cat.includes("metal")) return "🎸";
  if (cat.includes("jazz") || cat.includes("soul") || cat.includes("funk"))
    return "🎷";
  if (cat.includes("ciné") || cat.includes("film")) return "🎬";
  if (cat.includes("festival") || cat.includes("open air")) return "🎪";
  if (cat.includes("marché") || cat.includes("brocante")) return "🛒";
  if (cat.includes("sport") || cat.includes("trail") || cat.includes("ski"))
    return "🏅";
  if (
    cat.includes("food") ||
    cat.includes("brunch") ||
    cat.includes("bbq") ||
    cat.includes("truck")
  )
    return "🍽️";
  if (cat.includes("lumière")) return "💡";
  if (cat.includes("son") || cat.includes("dj")) return "🔊";
  if (cat.includes("sécurité")) return "🛡️";

  return "📍";
}

function getCategoryColor(item) {
  const cat = (
    item.mainCategory ||
    (item.categories && item.categories[0]) ||
    ""
  )
    .toString()
    .toLowerCase();

  if (
    cat.includes("techno") ||
    cat.includes("electro") ||
    cat.includes("trance")
  )
    return "#0f172a";
  if (cat.includes("rap") || cat.includes("trap")) return "#111827";
  if (cat.includes("rock") || cat.includes("metal")) return "#1f2937";
  if (cat.includes("festival") || cat.includes("open air")) return "#7c2d12";
  if (cat.includes("marché") || cat.includes("food")) return "#78350f";
  if (cat.includes("sport")) return "#14532d";
  if (cat.includes("lumière") || cat.includes("visuel")) return "#312e81";

  return "#020617";
}

function buildMarkerIcon(item) {
  const boost = item.boost || "basic";
  const platinumRank = item.platinumRank || 10; // Rang dans le Top 10 (1 = Top 1, 10 = Top 10)
  const isAI = item.isAI || item.aiGenerated || false;
  const emoji = getCategoryEmoji(item);
  
  // Effets selon le niveau de boost
  let markerClass = "";
  let extraStyles = "";
  let size = { w: 38, h: 48 };
  
  // Bordure par défaut
  let borderColor;
  if (isAI) {
    borderColor = "#000000";
  } else if (boost === "basic" || boost === "1.-") {
    borderColor = "var(--ui-card-border)";
  } else {
    borderColor = getBoostColor(boost);
  }
  
  // Couleurs de bordure selon le boost
  const boostBorderColors = {
    platinum: "#ef4444", // Rouge pour platine
    gold: "#ffd700",
    silver: "#b8b8b8",
    bronze: "#cd853f",
    basic: borderColor
  };
  
  const borderColorBoost = boostBorderColors[boost] || borderColor;
  
  // Variables pour le système Platinum Top 10
  let showHalo = false;
  let showCrown = false;
  let borderWidth = 2;
  let fontSize = 18;
  
  switch(boost) {
    case "platinum":
      // Système Top 10 par région avec enchères
      markerClass = `marker-platinum marker-platinum-rank-${platinumRank}`;
      
      // Plus le rang est haut, plus le marqueur est visible
      if (platinumRank === 1) {
        // TOP 1 : Le plus grand, avec couronne et double halo
        size = { w: 52, h: 62 };
        borderWidth = 4;
        fontSize = 24;
        showHalo = true;
        showCrown = true;
      } else if (platinumRank === 2) {
        // TOP 2 : Grand avec halo
        size = { w: 48, h: 58 };
        borderWidth = 3.5;
        fontSize = 22;
        showHalo = true;
      } else if (platinumRank === 3) {
        // TOP 3 : Moyen-grand avec halo léger
        size = { w: 46, h: 56 };
        borderWidth = 3;
        fontSize = 21;
        showHalo = true;
      } else if (platinumRank <= 5) {
        // TOP 4-5 : Moyen
        size = { w: 44, h: 54 };
        borderWidth = 2.5;
        fontSize = 20;
      } else {
        // TOP 6-10 : Standard platinum
        size = { w: 42, h: 52 };
        borderWidth = 2;
        fontSize = 19;
      }
      
      extraStyles = `
        background: linear-gradient(145deg, #1a1a1a, #2d2d2d);
        border: ${borderWidth}px solid ${borderColorBoost};
        box-shadow: 0 4px 12px rgba(239,68,68,0.4);
      `;
      break;
      
    case "gold":
      markerClass = "marker-gold";
      extraStyles = `
        background: linear-gradient(145deg, #1a1a1a, #252525);
        border: 2.5px solid ${borderColorBoost};
        box-shadow: 0 3px 10px rgba(255,215,0,0.3);
      `;
      size = { w: 40, h: 50 };
      fontSize = 19;
      break;
      
    case "silver":
      markerClass = "marker-silver";
      extraStyles = `
        background: #1a1a1a;
        border: 2px solid ${borderColorBoost};
        box-shadow: 0 2px 8px rgba(184,184,184,0.25);
      `;
      size = { w: 38, h: 48 };
      break;
      
    case "bronze":
      // Bronze : bordure un peu plus épaisse (élargie)
      markerClass = "marker-bronze";
      extraStyles = `
        background: #1a1a1a;
        border: 2.5px solid ${borderColorBoost};
        box-shadow: 0 2px 8px rgba(205,133,63,0.3);
      `;
      size = { w: 39, h: 49 };
      break;
      
    default:
      extraStyles = `
        background: #1a1a1a;
        border: 2px solid ${borderColor};
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
      `;
  }

  // Halo décoratif uniquement pour Top 1, 2, 3
  let haloHtml = "";
  if (boost === "platinum" && showHalo) {
    const haloSize1 = size.w + (platinumRank === 1 ? 24 : platinumRank === 2 ? 18 : 14);
    const haloSize2 = size.w + (platinumRank === 1 ? 32 : platinumRank === 2 ? 24 : 18);
    const haloOpacity1 = platinumRank === 1 ? 0.9 : platinumRank === 2 ? 0.7 : 0.5;
    const haloOpacity2 = platinumRank === 1 ? 0.6 : platinumRank === 2 ? 0.4 : 0.3;
    
    haloHtml = `
      <div class="halo-ring-platinum" style="
        position:absolute;
        top:50%;
        left:50%;
        transform:translate(-50%,-50%);
        width:${haloSize1}px;
        height:${haloSize1}px;
        border:${platinumRank === 1 ? 3 : 2}px solid rgba(239,68,68,${haloOpacity1});
        border-radius:50%;
        pointer-events:none;
        animation: pulse-halo-${platinumRank} 2s ease-in-out infinite;
      "></div>
      ${platinumRank <= 2 ? `
        <div class="halo-ring-platinum-2" style="
          position:absolute;
          top:50%;
          left:50%;
          transform:translate(-50%,-50%);
          width:${haloSize2}px;
          height:${haloSize2}px;
          border:2px solid rgba(239,68,68,${haloOpacity2});
          border-radius:50%;
          pointer-events:none;
          animation: pulse-halo-${platinumRank} 2.5s ease-in-out infinite 0.3s;
        "></div>
      ` : ''}
    `;
  }

  // Couronne pour Top 1 (sur le pointeur lui-même)
  const crownHtml = showCrown ? `
    <div style="
      position:absolute;
      top:-18px;
      left:50%;
      transform:translateX(-50%);
      font-size:20px;
      filter:drop-shadow(0 2px 4px rgba(0,0,0,0.5));
      z-index:10;
    ">👑</div>
  ` : "";

  const html = `
    <div class="${markerClass}" style="position:relative;">
      ${haloHtml}
      ${crownHtml}
      <div style="
        ${extraStyles}
        border-radius:16px;
        padding:${boost === "platinum" ? "6px 14px" : boost === "gold" ? "5px 12px" : "4px 10px"};
        color:#fff;
        font-size:${fontSize}px;
        display:flex;
        align-items:center;
        justify-content:center;
        gap:4px;
        position:relative;
        z-index:2;
      ">
        <span>${emoji}</span>
      </div>
      <div style="
        width:0;height:0;
        border-left:${boost === "platinum" && platinumRank <= 3 ? 10 : 8}px solid transparent;
        border-right:${boost === "platinum" && platinumRank <= 3 ? 10 : 8}px solid transparent;
        border-top:${boost === "platinum" && platinumRank <= 3 ? 14 : 12}px solid ${borderColorBoost};
        margin:0 auto;
        position:relative;
        z-index:2;
      "></div>
    </div>
  `;

  const iconAnchorX = size.w / 2;
  const iconAnchorY = size.h + (showCrown ? 18 : 0);

  return L.divIcon({
    html,
    className: markerClass,
    iconSize: [size.w, size.h + (showCrown ? 18 : 0)],
    iconAnchor: [iconAnchorX, iconAnchorY],
    popupAnchor: [0, -size.h + 6],
    tooltipAnchor: [iconAnchorX, 0]
  });
}

// ============================================
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
  if (!status || status === "OK") return "";

  let label = status;
  let bg = "rgba(239,68,68,0.9)";

  if (status === "COMPLET" || status === "SOLDOUT") {
    label = "COMPLET";
    bg = "rgba(234,179,8,0.9)";
  } else if (status === "ANNULE" || status === "ANNULÉ") {
    label = "ANNULÉ";
    bg = "rgba(239,68,68,0.9)";
  } else if (status === "REPORTE" || status === "REPORTÉ") {
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
      color:#111827;
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
  
  // NE PAS redéfinir window.t ici pour éviter les erreurs TDZ
  // Utiliser directement du texte en dur au lieu d'appeler window.t()
  
  // TRADUCTION AUTOMATIQUE du contenu de l'événement
  const evTranslated = getTranslatedItemSync(ev, currentLanguage);
  
  const statusOverlay = buildStatusOverlay(ev.status);
  const borderColor = getBoostColor(ev.boost);
  const cats = (evTranslated.categories || ev.categories || []).join(" • ");
  const imgTag = buildMainImageTag(ev, evTranslated.title || ev.title || "");
  const emoji = getCategoryEmoji(ev);
  
  // Calcul du temps restant
  const now = new Date();
  const startDate = ev.startDate ? new Date(ev.startDate) : null;
  const daysUntil = startDate ? Math.ceil((startDate - now) / (1000 * 60 * 60 * 24)) : null;
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
  
  // Indicateur publication MapEvent
  const aiIndicator = ev.isAI ? `
    <div style="margin-top:8px;padding:8px 12px;background:linear-gradient(135deg,rgba(59,130,246,0.1),rgba(139,92,246,0.1));border:1px solid rgba(59,130,246,0.3);border-radius:10px;font-size:11px;color:#94a3b8;display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
      <span style="font-size:14px;">📢</span>
      <span>Publié par <strong style="color:#60a5fa;">MapEvent</strong> : il peut y avoir des erreurs, merci de <a href="${ev.sourceUrl || '#'}" target="_blank" style="color:#60a5fa;text-decoration:underline;font-weight:600;">vérifier la source</a></span>
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
  
  // Actions avec design moderne
  const actionsRow = `
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px;">
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
  `;

  // Reviews compactes
  const reviewsSection = (() => {
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
        </div>
        
        <!-- Title -->
        <h3 style="margin:0 0 10px;font-size:20px;font-weight:800;line-height:1.3;color:var(--ui-text-main);">${escapeHtml(evTranslated.title || ev.title || "")}</h3>
        
        <!-- Date & Location Cards -->
        <div style="display:flex;flex-direction:column;gap:8px;margin-bottom:12px;">
          <div style="display:flex;align-items:center;gap:10px;padding:10px 12px;background:linear-gradient(135deg,rgba(0,255,195,0.1),rgba(16,185,129,0.05));border:1px solid rgba(0,255,195,0.2);border-radius:10px;">
            <span style="font-size:20px;">📅</span>
            <div>
              <div style="font-size:13px;font-weight:600;color:#00ffc3;">${formatEventDateRange(ev.startDate, ev.endDate)}</div>
            </div>
          </div>
          <div style="display:flex;align-items:center;gap:10px;padding:10px 12px;background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.2);border-radius:10px;">
            <span style="font-size:20px;">📍</span>
            <div style="font-size:13px;font-weight:500;color:var(--ui-text-main);flex:1;">${escapeHtml(ev.address || ev.city || "")}</div>
          </div>
        </div>
        
        <!-- Description -->
        ${ev.description ? `
          <div style="font-size:14px;color:#ffffff;line-height:1.7;margin-bottom:12px;padding:12px;background:transparent;border-radius:8px;">
            ${escapeHtml(evTranslated.description || ev.description)}
          </div>
        ` : ""}
        
        <!-- Stats -->
        ${statsRow}
        
        <!-- Reviews -->
        ${reviewsSection}
        
        <!-- AI Indicator -->
        ${aiIndicator}
        
        <!-- Actions -->
        ${actionsRow}
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

  // Liens sons - Player intégré sans accès au site, paiement débloque tout
  const hasPaidContact = currentUser.subscription === 'premium' || paidContacts.includes(`booking:${b.id}`);
  
  const soundsSection = b.soundLinks && b.soundLinks.length > 0 ? `
    <div style="margin:8px 0;padding:12px;background:linear-gradient(135deg,rgba(139,92,246,0.15),rgba(59,130,246,0.1));border-radius:12px;border:1px solid rgba(139,92,246,0.3);">
      <div style="font-size:12px;color:#a78bfa;margin-bottom:10px;font-weight:600;">🎵 ${b.soundLinks.length} piste(s) disponible(s)</div>
      
      <!-- Mini Player Intégré -->
      <div style="display:flex;flex-direction:column;gap:8px;">
        ${b.soundLinks.slice(0, 3).map((link, i) => `
          <div style="display:flex;align-items:center;gap:10px;padding:8px 12px;background:rgba(0,0,0,0.3);border-radius:10px;">
            <button onclick="event.stopPropagation();playPreview('${b.id}', ${i})" style="width:36px;height:36px;border-radius:50%;border:none;background:linear-gradient(135deg,#a78bfa,#8b5cf6);color:white;cursor:pointer;font-size:14px;display:flex;align-items:center;justify-content:center;">
              ▶
            </button>
            <div style="flex:1;">
              <div style="font-size:12px;color:#e5e7eb;font-weight:500;">Piste ${i + 1}</div>
              <div style="font-size:10px;color:var(--ui-text-muted);">
                ${link.includes('soundcloud') ? '☁️ SoundCloud' : link.includes('spotify') ? '🟢 Spotify' : link.includes('youtube') ? '▶️ YouTube' : '🎵 Audio'}
              </div>
            </div>
            <div style="width:60px;height:4px;background:rgba(255,255,255,0.2);border-radius:2px;overflow:hidden;">
              <div id="progress-${b.id}-${i}" style="width:0%;height:100%;background:#a78bfa;transition:width 0.1s;"></div>
            </div>
          </div>
        `).join('')}
      </div>
      
      ${!hasPaidContact ? `
        <div style="margin-top:10px;padding-top:10px;border-top:1px solid rgba(139,92,246,0.2);text-align:center;">
          <div style="font-size:10px;color:var(--ui-text-muted);margin-bottom:6px;">🔒 Contact & liens complets masqués</div>
        </div>
      ` : `
        <div style="margin-top:10px;padding-top:10px;border-top:1px solid rgba(139,92,246,0.2);">
          <div style="font-size:10px;color:#00ffc3;margin-bottom:6px;">✅ Accès complet débloqué</div>
          <div style="display:flex;gap:6px;flex-wrap:wrap;">
            ${b.soundLinks.map((link, i) => `
              <a href="${link}" target="_blank" style="padding:4px 10px;background:rgba(0,255,195,0.2);border-radius:999px;font-size:11px;color:#00ffc3;text-decoration:none;">
                ${link.includes('soundcloud') ? '☁️ SoundCloud' : link.includes('spotify') ? '🟢 Spotify' : link.includes('youtube') ? '▶️ YouTube' : '🔗 Lien '+(i+1)}
              </a>
            `).join('')}
          </div>
        </div>
      `}
    </div>
  ` : `
    <div style="margin:8px 0;padding:10px;background:rgba(239,68,68,0.1);border:1px dashed rgba(239,68,68,0.3);border-radius:8px;font-size:12px;color:#ef4444;text-align:center;">
      ⚠️ Aucun lien audio fourni<br>
      <span style="font-size:10px;color:var(--ui-text-muted);">Contactez l'artiste pour des démos</span>
    </div>
  `;

  // Rating
  const ratingStars = b.rating ? `
    <div style="display:flex;align-items:center;gap:4px;margin-bottom:6px;">
      ${'⭐'.repeat(Math.floor(parseFloat(b.rating)))}
      <span style="font-size:12px;color:var(--ui-text-muted);">${b.rating}/5</span>
      <span style="font-size:11px;color:var(--ui-text-muted);">(${b.likes || 0} avis)</span>
    </div>
  ` : "";

  // Indicateur publication MapEvent
  const aiIndicator = b.isAI ? `
    <div style="margin:6px 0;padding:6px 10px;background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:8px;font-size:11px;color:#94a3b8;">
      📢 Publié par <strong style="color:#60a5fa;">MapEvent</strong> : il peut y avoir des erreurs, merci de <a href="${b.sourceUrl || '#'}" target="_blank" style="color:#60a5fa;text-decoration:underline;">vérifier la source</a>
    </div>
  ` : "";

  const actionsRow = `
    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;">
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
      <button onclick="onAction('route', 'booking', ${b.id})" class="pill small" style="flex:1;">🗺️ ${(typeof window.t === 'function' ? window.t("route") : null) || "Itinéraire"}</button>
    </div>
    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:6px;">
      <button onclick="onAction('avis', 'booking', ${b.id})" class="pill small" style="flex:1;">⭐ Avis</button>
      <button onclick="onAction('discussion', 'booking', ${b.id})" class="pill small" style="flex:1;">💬 Contact</button>
      <button onclick="onAction('report', 'booking', ${b.id})" class="pill small" style="color:#ef4444;">🚨</button>
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
        ${b.description ? `<div style="font-size:14px;color:#ffffff;margin-bottom:12px;line-height:1.7;padding:12px;background:transparent;border-radius:8px;">${escapeHtml(b.description)}</div>` : ""}
        ${soundsSection}
        ${aiIndicator}
        ${hasPaidContact ? `
          <div style="margin:8px 0;padding:12px;background:linear-gradient(135deg,rgba(0,255,195,0.15),rgba(34,197,94,0.1));border:1px solid rgba(0,255,195,0.3);border-radius:10px;">
            <div style="font-size:12px;color:#00ffc3;font-weight:600;margin-bottom:8px;">✅ Contact débloqué</div>
            <div style="font-size:13px;color:#e5e7eb;margin-bottom:4px;">📧 ${b.email || 'contact@artiste.ch'}</div>
            <div style="font-size:13px;color:#e5e7eb;margin-bottom:4px;">📞 ${b.phone || '+41 79 123 45 67'}</div>
            <div style="font-size:10px;color:var(--ui-text-muted);margin-top:6px;">📅 Ajouté à votre agenda permanent</div>
        </div>
        ` : `
          <div style="font-size:11px;color:#6b7280;margin:8px 0;padding:8px;background:rgba(107,114,128,0.1);border-radius:8px;">
            🔒 Coordonnées masquées • Email & téléphone disponibles après paiement
          </div>
        `}
        ${actionsRow}
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
  const borderColor = getBoostColor(s.boost);
  const imgTag = buildMainImageTag(s, s.name || "");
  const cats = (s.categories || []).join(" • ");
  const emoji = getCategoryEmoji(s);
  const hasPaidContact = currentUser.subscription === 'premium' || paidContacts.includes(`service:${s.id}`);

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

  // Indicateur publication MapEvent
  const aiIndicator = s.isAI ? `
    <div style="margin:6px 0;padding:6px 10px;background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:8px;font-size:11px;color:#94a3b8;">
      📢 Publié par <strong style="color:#60a5fa;">MapEvent</strong> : il peut y avoir des erreurs, merci de <a href="${s.sourceUrl || '#'}" target="_blank" style="color:#60a5fa;text-decoration:underline;">vérifier la source</a>
    </div>
  ` : "";

  const actionsRow = `
    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;">
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
        ${s.description ? `<div style="font-size:14px;color:#ffffff;margin-bottom:12px;line-height:1.7;padding:12px;background:transparent;border-radius:8px;">${escapeHtml(s.description)}</div>` : ""}
        ${aiIndicator}
        ${hasPaidContact ? `
          <div style="margin:8px 0;padding:12px;background:linear-gradient(135deg,rgba(0,255,195,0.15),rgba(34,197,94,0.1));border:1px solid rgba(0,255,195,0.3);border-radius:10px;">
            <div style="font-size:12px;color:#00ffc3;font-weight:600;margin-bottom:8px;">✅ Contact débloqué</div>
            <div style="font-size:13px;color:#e5e7eb;margin-bottom:4px;">📧 ${s.email || 'contact@service.ch'}</div>
            <div style="font-size:13px;color:#e5e7eb;margin-bottom:4px;">📞 ${s.phone || '+41 79 123 45 67'}</div>
            ${s.website ? `<a href="${s.website}" target="_blank" style="display:inline-flex;align-items:center;gap:4px;font-size:12px;color:#3b82f6;margin-top:4px;">🌐 ${s.website}</a>` : ''}
            <div style="font-size:10px;color:var(--ui-text-muted);margin-top:6px;">📅 Ajouté à votre agenda permanent</div>
        </div>
        ` : `
          <div style="font-size:11px;color:#6b7280;margin:8px 0;padding:10px;background:rgba(107,114,128,0.1);border-radius:8px;">
            🔒 <strong>Masqué :</strong> Email, téléphone, site web<br>
            <span style="font-size:10px;">Débloquez pour accéder aux coordonnées complètes</span>
          </div>
        `}
        ${actionsRow}
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
// CALCUL DE DISTANCE (formule de Haversine)
// ============================================
function calculateDistance(lat1, lng1, lat2, lng2) {
  // Formule de Haversine pour calculer la distance entre deux points GPS
  const R = 6371; // Rayon de la Terre en km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLng = (lng2 - lng1) * Math.PI / 180;
  const a = 
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLng / 2) * Math.sin(dLng / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distance = R * c; // Distance en km
  
  // Vérification de sécurité
  if (isNaN(distance) || !isFinite(distance) || distance < 0) {
    console.warn(`Distance invalide calculée: ${distance} pour (${lat1},${lng1}) -> (${lat2},${lng2})`);
    return Infinity; // Retourner Infinity plutôt que null pour le tri
  }
  
  return distance;
}

// ============================================
// VUE LISTE (fullscreen) – tri
// ============================================
function refreshListView() {
  const listView = document.getElementById("list-view");
  if (!listView) return;

  if (!listViewOpen) {
    listView.style.display = "none";
    return;
  }

  const base = getActiveData();
  
  // ============================================
  // LOGIQUE DE TRI SIMPLE ET CLAIRE
  // ============================================
  
  let data;
  
  // Vérifier que selectedCityForSorting existe et a des coordonnées valides
  const hasValidCity = selectedCityForSorting && 
                       selectedCityForSorting.lat !== null && 
                       selectedCityForSorting.lat !== undefined &&
                       selectedCityForSorting.lng !== null && 
                       selectedCityForSorting.lng !== undefined &&
                       !isNaN(parseFloat(selectedCityForSorting.lat)) &&
                       !isNaN(parseFloat(selectedCityForSorting.lng));
  
  // LOG TRÈS VISIBLE POUR DÉBOGUER
  console.log(`\n\n\n========================================`);
  console.log(`🚀 REFRESH LIST VIEW - TRI PAR DISTANCE`);
  console.log(`========================================`);
  console.log(`Ville sélectionnée: ${selectedCityForSorting ? selectedCityForSorting.name : 'AUCUNE'}`);
  console.log(`hasValidCity: ${hasValidCity}`);
  console.log(`Nombre d'items à trier: ${base.length}`);
  console.log(`========================================\n\n\n`);
  
  if (hasValidCity) {
    // ============================================
    // MODE 1 : VILLE SÉLECTIONNÉE → TRIER PAR DISTANCE + CATÉGORIES + BOOSTS
    // Ordre de priorité : 1) DISTANCE (priorité absolue), 2) Catégories, 3) Boost, 4) Platinum rank
    // ============================================
    
    console.log(`\n🎯 ===== TRI PAR DISTANCE (PRIORITÉ ABSOLUE) + CATÉGORIES + BOOSTS =====`);
    console.log(`Ville: ${selectedCityForSorting.name}`);
    console.log(`Coordonnées: lat=${selectedCityForSorting.lat}, lng=${selectedCityForSorting.lng}`);
    console.log(`Total items à trier: ${base.length}`);
    
    const boostOrder = { platinum: 1, gold: 2, silver: 3, bronze: 4, basic: 5 };
    
    // ÉTAPE 1 : Calculer la distance pour CHAQUE item
    const cityLat = parseFloat(selectedCityForSorting.lat);
    const cityLng = parseFloat(selectedCityForSorting.lng);
    
    console.log(`🔍 Vérification coordonnées: lat=${cityLat}, lng=${cityLng}, isNaN(lat)=${isNaN(cityLat)}, isNaN(lng)=${isNaN(cityLng)}`);
    console.log(`🔍 Type de lat: ${typeof selectedCityForSorting.lat}, Type de lng: ${typeof selectedCityForSorting.lng}`);
    
    if (isNaN(cityLat) || isNaN(cityLng)) {
      console.error(`❌ Coordonnées ville invalides ! selectedCityForSorting:`, selectedCityForSorting);
      console.error(`❌ Valeurs brutes: lat="${selectedCityForSorting.lat}", lng="${selectedCityForSorting.lng}"`);
      data = base.slice(0, 200);
    } else {
      // Calculer la distance pour tous les items
      // IMPORTANT: S'assurer que chaque item a un champ 'type' pour l'affichage
      const itemsWithDistance = base.map((item) => {
        let distance = Infinity;
        
        if (item.lat && item.lng) {
          const itemLat = parseFloat(item.lat);
          const itemLng = parseFloat(item.lng);
          
          if (!isNaN(itemLat) && !isNaN(itemLng)) {
            const calculatedDistance = calculateDistance(cityLat, cityLng, itemLat, itemLng);
            if (!isNaN(calculatedDistance) && isFinite(calculatedDistance) && calculatedDistance >= 0) {
              distance = calculatedDistance;
            }
          }
        }
        
        // S'assurer que l'item a un champ 'type' pour l'affichage
        // Déterminer le type basé sur les propriétés de l'item
        let itemType = item.type;
        if (!itemType) {
          if (item.title && item.date) {
            itemType = 'event';
          } else if (item.name && (item.soundLinks || item.audioLinks)) {
            itemType = 'booking';
          } else if (item.name) {
            itemType = 'service';
          }
        }
        
        return { ...item, _distance: distance, type: itemType || item.type || 'event' };
      });
      
      // ÉTAPE 2 : Séparer les items avec distance valide de ceux sans distance
      // PRIORITÉ ABSOLUE : 1) DISTANCE, 2) Catégories, 3) Boost, 4) Platinum rank
      console.log(`🔄 Début du tri de ${itemsWithDistance.length} items...`);
      
      // Vérifier quelques distances calculées
      const sampleDistances = itemsWithDistance.slice(0, 5).map(item => ({
        city: item.city || item.title || item.name || 'N/A',
        distance: item._distance !== undefined && isFinite(item._distance) ? item._distance.toFixed(2) : 'Infinity',
        lat: item.lat,
        lng: item.lng
      }));
      console.log(`📊 EXEMPLE DE DISTANCES CALCULÉES (5 premiers):`, sampleDistances);
      
      // SÉPARER : Items avec distance valide vs items sans distance
      const itemsWithValidDistance = itemsWithDistance.filter(item => isFinite(item._distance));
      const itemsWithoutDistance = itemsWithDistance.filter(item => !isFinite(item._distance));
      
      console.log(`✅ ${itemsWithValidDistance.length} items avec distance valide`);
      console.log(`⚠️ ${itemsWithoutDistance.length} items sans distance`);
      
      // Vérifier que les items avec distance valide ont bien des distances différentes
      if (itemsWithValidDistance.length >= 2) {
        const distances = itemsWithValidDistance.map(item => item._distance).sort((a, b) => a - b);
        console.log(`📊 DISTANCES MIN/MAX: ${distances[0].toFixed(2)}km (min) à ${distances[distances.length - 1].toFixed(2)}km (max)`);
      }
      
      // Vérifier quelques distances avant le tri
      const sampleDistancesBeforeSort = itemsWithValidDistance.slice(0, 5).map(item => ({
        city: item.city || 'N/A',
        distance: item._distance.toFixed(2),
        boost: item.boost || 'basic'
      }));
      console.log(`📊 AVANT TRI - 5 premiers avec distance:`, sampleDistancesBeforeSort);
      
      // VÉRIFICATION SPÉCIFIQUE : Monthey vs Genève pour Sierre
      const monthey = itemsWithValidDistance.find(item => item.city && item.city.toLowerCase().includes('monthey'));
      const geneve = itemsWithValidDistance.find(item => item.city && item.city.toLowerCase().includes('genève'));
      if (monthey && geneve) {
        console.log(`\n🔍 VÉRIFICATION DISTANCES:`);
        console.log(`   Monthey: ${monthey._distance.toFixed(2)}km (lat:${monthey.lat}, lng:${monthey.lng})`);
        console.log(`   Genève: ${geneve._distance.toFixed(2)}km (lat:${geneve.lat}, lng:${geneve.lng})`);
        console.log(`   Ville sélectionnée: ${selectedCityForSorting.name} (lat:${cityLat}, lng:${cityLng})`);
        if (monthey._distance > geneve._distance) {
          console.error(`   ❌ PROBLÈME: Monthey (${monthey._distance.toFixed(2)}km) est PLUS LOIN que Genève (${geneve._distance.toFixed(2)}km) !`);
        } else {
          console.log(`   ✅ CORRECT: Monthey (${monthey._distance.toFixed(2)}km) est plus proche que Genève (${geneve._distance.toFixed(2)}km)`);
        }
      }
      
      // VÉRIFICATION SPÉCIFIQUE : Sion vs Zurich pour Sierre
      const sion = itemsWithValidDistance.find(item => item.city && item.city.toLowerCase().includes('sion'));
      const zurich = itemsWithValidDistance.find(item => item.city && item.city.toLowerCase().includes('zurich'));
      if (sion && zurich) {
        console.log(`\n🔍 VÉRIFICATION DISTANCES SION vs ZURICH:`);
        console.log(`   Sion: ${sion._distance.toFixed(2)}km (lat:${sion.lat}, lng:${sion.lng})`);
        console.log(`   Zurich: ${zurich._distance.toFixed(2)}km (lat:${zurich.lat}, lng:${zurich.lng})`);
        console.log(`   Ville sélectionnée: ${selectedCityForSorting.name} (lat:${cityLat}, lng:${cityLng})`);
        if (sion._distance > zurich._distance) {
          console.error(`   ❌ PROBLÈME CRITIQUE: Sion (${sion._distance.toFixed(2)}km) est PLUS LOIN que Zurich (${zurich._distance.toFixed(2)}km) !`);
          console.error(`   Cela ne devrait JAMAIS arriver car Sion est à ~10km de Sierre et Zurich à ~200km !`);
        } else {
          console.log(`   ✅ CORRECT: Sion (${sion._distance.toFixed(2)}km) est plus proche que Zurich (${zurich._distance.toFixed(2)}km)`);
        }
      }
      
      // TRIER UNIQUEMENT les items avec distance valide
      // PRIORITÉ ABSOLUE : DISTANCE d'abord, puis catégories, puis boost
      console.log(`🔍 ORDRE DE PRIORITÉ: 1) DISTANCE (absolue), 2) CATÉGORIES, 3) BOOST`);
      
      // TRI SIMPLIFIÉ : DISTANCE UNIQUEMENT - PRIORITÉ ABSOLUE
      // La distance est TOUJOURS le premier critère, sans aucune exception
      itemsWithValidDistance.sort((a, b) => {
        const distA = a._distance !== undefined && isFinite(a._distance) ? a._distance : Infinity;
        const distB = b._distance !== undefined && isFinite(b._distance) ? b._distance : Infinity;
        
        // PRIORITÉ ABSOLUE : Distance uniquement
        // Si les distances sont différentes, trier par distance SEULEMENT
        if (distA !== distB) {
          return distA - distB;
        }
        
        // Seulement si les distances sont EXACTEMENT identiques (très rare), utiliser les autres critères
        // 2. Catégories sélectionnées (si filtre actif)
        if (selectedCategories.length > 0) {
          const catA = a.categories || [];
          const catB = b.categories || [];
          const matchA = catA.some(c => selectedCategories.some(sc => 
            c.toLowerCase().includes(sc.toLowerCase()) || sc.toLowerCase().includes(c.toLowerCase())
          ));
          const matchB = catB.some(c => selectedCategories.some(sc => 
            c.toLowerCase().includes(sc.toLowerCase()) || sc.toLowerCase().includes(c.toLowerCase())
          ));
          if (matchA && !matchB) return -1;
          if (!matchA && matchB) return 1;
        }
        
        // 3. Boost (platinum > gold > silver > bronze > basic)
        const boostA = boostOrder[a.boost || "basic"] || 99;
        const boostB = boostOrder[b.boost || "basic"] || 99;
        if (boostA !== boostB) return boostA - boostB;
        
        // 4. Platinum rank
        if (a.boost === "platinum" && b.boost === "platinum") {
          const rankA = a.platinumRank || 10;
          const rankB = b.platinumRank || 10;
          if (rankA !== rankB) return rankA - rankB;
        }
        
        return 0;
      });
      
      // RECONSTITUER : Items avec distance triés + items sans distance à la fin
      const sortedItems = [...itemsWithValidDistance, ...itemsWithoutDistance];
      
      // Vérifier quelques distances après le tri
      const sampleDistancesAfterSort = sortedItems.slice(0, 5).map(item => ({
        city: item.city || 'N/A',
        distance: isFinite(item._distance) ? item._distance.toFixed(2) : 'Infinity',
        boost: item.boost || 'basic'
      }));
      console.log(`📊 APRÈS TRI - 5 premiers:`, sampleDistancesAfterSort);
      
      // VÉRIFICATION SPÉCIFIQUE APRÈS TRI : Monthey vs Genève
      const montheyAfter = sortedItems.find(item => item.city && item.city.toLowerCase().includes('monthey'));
      const geneveAfter = sortedItems.find(item => item.city && item.city.toLowerCase().includes('genève'));
      if (montheyAfter && geneveAfter) {
        const montheyIndex = sortedItems.indexOf(montheyAfter);
        const geneveIndex = sortedItems.indexOf(geneveAfter);
        console.log(`\n🔍 VÉRIFICATION APRÈS TRI:`);
        console.log(`   Monthey: position ${montheyIndex + 1}, distance ${montheyAfter._distance.toFixed(2)}km`);
        console.log(`   Genève: position ${geneveIndex + 1}, distance ${geneveAfter._distance.toFixed(2)}km`);
        if (montheyIndex > geneveIndex && montheyAfter._distance < geneveAfter._distance) {
          console.error(`   ❌ ERREUR DE TRI: Monthey (${montheyAfter._distance.toFixed(2)}km) est APRÈS Genève (${geneveAfter._distance.toFixed(2)}km) alors qu'il devrait être AVANT !`);
        } else if (montheyIndex < geneveIndex) {
          console.log(`   ✅ CORRECT: Monthey est AVANT Genève dans le tri`);
        }
      }
      
      // VÉRIFICATION SPÉCIFIQUE APRÈS TRI : Sion vs Zurich
      const sionAfter = sortedItems.find(item => item.city && item.city.toLowerCase().includes('sion'));
      const zurichAfter = sortedItems.find(item => item.city && item.city.toLowerCase().includes('zurich'));
      if (sionAfter && zurichAfter) {
        const sionIndex = sortedItems.indexOf(sionAfter);
        const zurichIndex = sortedItems.indexOf(zurichAfter);
        console.log(`\n🔍 VÉRIFICATION APRÈS TRI SION vs ZURICH:`);
        console.log(`   Sion: position ${sionIndex + 1}, distance ${sionAfter._distance.toFixed(2)}km`);
        console.log(`   Zurich: position ${zurichIndex + 1}, distance ${zurichAfter._distance.toFixed(2)}km`);
        if (sionIndex > zurichIndex && sionAfter._distance < zurichAfter._distance) {
          console.error(`   ❌ ERREUR CRITIQUE DE TRI: Sion (${sionAfter._distance.toFixed(2)}km) est APRÈS Zurich (${zurichAfter._distance.toFixed(2)}km) alors qu'il devrait être AVANT !`);
          console.error(`   Le tri ne fonctionne PAS correctement !`);
        } else if (sionIndex < zurichIndex) {
          console.log(`   ✅ CORRECT: Sion est AVANT Zurich dans le tri`);
        }
      }
      
      console.log(`✅ Tri terminé - ${sortedItems.length} items triés`);
      
      // VÉRIFICATION : S'assurer que le tri par distance est correct dans itemsWithValidDistance
      if (itemsWithValidDistance.length >= 2) {
        let triCorrect = true;
        for (let i = 0; i < itemsWithValidDistance.length - 1; i++) {
          const current = itemsWithValidDistance[i];
          const next = itemsWithValidDistance[i + 1];
          if (current._distance > next._distance) {
            triCorrect = false;
            console.error(`❌ ERREUR DE TRI: Item ${i} (${current._distance.toFixed(2)}km) est APRÈS item ${i+1} (${next._distance.toFixed(2)}km) !`);
            console.error(`   Item ${i}: ${current.city || current.title} - ${current._distance.toFixed(2)}km`);
            console.error(`   Item ${i+1}: ${next.city || next.title} - ${next._distance.toFixed(2)}km`);
            break;
          }
        }
        if (triCorrect) {
          console.log(`✅ VÉRIFICATION: Le tri par distance est CORRECT - tous les items sont triés par distance croissante`);
        }
      }
      
      // UTILISER DIRECTEMENT sortedItems (qui contient itemsWithValidDistance trié + itemsWithoutDistance)
      // FORCER LE TRI PAR DISTANCE UNIQUEMENT - PRIORITÉ ABSOLUE
      data = sortedItems.slice(0, 200);
      
      // FORCER LE TRI PAR DISTANCE - PRIORITÉ ABSOLUE (aucune exception)
      console.log(`\n🔧 FORCER TRI PAR DISTANCE (PRIORITÉ ABSOLUE) sur data - ${data.length} items`);
      data.sort((a, b) => {
        const distA = a._distance !== undefined && isFinite(a._distance) ? a._distance : Infinity;
        const distB = b._distance !== undefined && isFinite(b._distance) ? b._distance : Infinity;
        // DISTANCE UNIQUEMENT - AUCUN AUTRE CRITÈRE
        return distA - distB;
      });
      
      // VÉRIFICATION CRITIQUE : S'assurer que data est bien trié AVANT l'affichage
      console.log(`\n🎯 VÉRIFICATION APRÈS TRI FORCÉ - data contient ${data.length} items`);
      if (data.length >= 5) {
        console.log(`🔍 5 PREMIERS ITEMS DANS data APRÈS TRI FORCÉ:`);
        for (let i = 0; i < 5; i++) {
          const item = data[i];
          const dist = item._distance !== undefined && isFinite(item._distance) ? item._distance.toFixed(2) : 'Infinity';
          console.log(`   ${i + 1}. ${item.city || item.title || item.name || 'N/A'} - ${dist}km`);
        }
        
        // Vérifier que le tri est correct
        let triCorrect = true;
        for (let i = 0; i < Math.min(10, data.length - 1); i++) {
          const current = data[i];
          const next = data[i + 1];
          const distCurrent = current._distance !== undefined && isFinite(current._distance) ? current._distance : Infinity;
          const distNext = next._distance !== undefined && isFinite(next._distance) ? next._distance : Infinity;
          if (distCurrent > distNext) {
            triCorrect = false;
            console.error(`   ❌ ERREUR: Item ${i} (${distCurrent.toFixed(2)}km) est APRÈS item ${i+1} (${distNext.toFixed(2)}km) !`);
            break;
          }
        }
        if (triCorrect) {
          console.log(`   ✅ data est correctement trié par distance (PRIORITÉ ABSOLUE)`);
        } else {
          console.error(`   ❌ ERREUR CRITIQUE: Le tri ne fonctionne PAS !`);
        }
      }
      
      // VÉRIFICATION FINALE : Vérifier que data contient bien les données triées
      console.log(`\n🎯 VÉRIFICATION FINALE - data contient ${data.length} items`);
      const montheyInData = data.find(item => item.city && item.city.toLowerCase().includes('monthey'));
      const geneveInData = data.find(item => item.city && item.city.toLowerCase().includes('genève'));
      if (montheyInData && geneveInData) {
        const montheyPosInData = data.indexOf(montheyInData) + 1;
        const genevePosInData = data.indexOf(geneveInData) + 1;
        console.log(`   Monthey dans data: position ${montheyPosInData}, distance ${montheyInData._distance.toFixed(2)}km`);
        console.log(`   Genève dans data: position ${genevePosInData}, distance ${geneveInData._distance.toFixed(2)}km`);
        if (montheyPosInData > genevePosInData && montheyInData._distance < geneveInData._distance) {
          console.error(`   ❌ ERREUR CRITIQUE: Monthey est APRÈS Genève dans data alors qu'il devrait être AVANT !`);
        } else {
          console.log(`   ✅ data est correctement trié`);
        }
      }
      
      // VÉRIFICATION FINALE : Sion vs Zurich dans data
      const sionInData = data.find(item => item.city && item.city.toLowerCase().includes('sion'));
      const zurichInData = data.find(item => item.city && item.city.toLowerCase().includes('zurich'));
      if (sionInData && zurichInData) {
        const sionPosInData = data.indexOf(sionInData) + 1;
        const zurichPosInData = data.indexOf(zurichInData) + 1;
        console.log(`\n🎯 VÉRIFICATION FINALE SION vs ZURICH dans data:`);
        const sionDist = sionInData._distance !== undefined && isFinite(sionInData._distance) ? sionInData._distance : Infinity;
        const zurichDist = zurichInData._distance !== undefined && isFinite(zurichInData._distance) ? zurichInData._distance : Infinity;
        console.log(`   Sion dans data: position ${sionPosInData}, distance ${sionDist.toFixed(2)}km`);
        console.log(`   Zurich dans data: position ${zurichPosInData}, distance ${zurichDist.toFixed(2)}km`);
        if (sionPosInData > zurichPosInData && sionDist < zurichDist) {
          console.error(`   ❌ ERREUR CRITIQUE: Sion est APRÈS Zurich dans data alors qu'il devrait être AVANT !`);
          console.error(`   Le problème est dans la variable data utilisée pour l'affichage !`);
          console.error(`   FORCER LE TRI MANUEL IMMÉDIATEMENT`);
          // FORCER le tri manuel
          data.sort((a, b) => {
            const distA = a._distance !== undefined && isFinite(a._distance) ? a._distance : Infinity;
            const distB = b._distance !== undefined && isFinite(b._distance) ? b._distance : Infinity;
            return distA - distB;
          });
          console.log(`   ✅ Tri manuel appliqué - ${data.length} items triés`);
        } else if (sionPosInData < zurichPosInData) {
          console.log(`   ✅ CORRECT: Sion est AVANT Zurich dans data`);
        }
      }
      
      // VÉRIFICATION CRITIQUE FINALE : Vérifier que les 5 premiers items sont bien triés par distance
      if (data.length >= 5) {
        console.log(`\n🔍 VÉRIFICATION FINALE DES 5 PREMIERS ITEMS:`);
        let triCorrect = true;
        for (let i = 0; i < Math.min(5, data.length); i++) {
          const item = data[i];
          const dist = item._distance !== undefined && isFinite(item._distance) ? item._distance : Infinity;
          console.log(`   ${i + 1}. ${item.city || item.title || item.name || 'N/A'} - ${dist !== Infinity ? dist.toFixed(2) + 'km' : 'Infinity'}`);
          
          // Vérifier que l'item suivant n'est pas plus proche
          if (i < data.length - 1) {
            const next = data[i + 1];
            const nextDist = next._distance !== undefined && isFinite(next._distance) ? next._distance : Infinity;
            if (dist > nextDist) {
              triCorrect = false;
              console.error(`   ❌ ERREUR: Item ${i} (${dist.toFixed(2)}km) est APRÈS item ${i+1} (${nextDist.toFixed(2)}km) !`);
            }
          }
        }
        
        if (!triCorrect) {
          console.error(`   ❌ LE TRI EST INCORRECT - FORCER LE TRI MANUEL AVANT AFFICHAGE`);
          data.sort((a, b) => {
            const distA = a._distance !== undefined && isFinite(a._distance) ? a._distance : Infinity;
            const distB = b._distance !== undefined && isFinite(b._distance) ? b._distance : Infinity;
            return distA - distB;
          });
          console.log(`   ✅ Tri manuel appliqué AVANT AFFICHAGE - ${data.length} items triés`);
          
          // Réafficher les 5 premiers après le tri
          console.log(`\n🔍 APRÈS TRI MANUEL - 5 PREMIERS:`);
          for (let i = 0; i < Math.min(5, data.length); i++) {
            const item = data[i];
            const dist = item._distance !== undefined && isFinite(item._distance) ? item._distance : Infinity;
            console.log(`   ${i + 1}. ${item.city || item.title || item.name || 'N/A'} - ${dist !== Infinity ? dist.toFixed(2) + 'km' : 'Infinity'}`);
          }
        } else {
          console.log(`   ✅ Le tri est CORRECT - tous les items sont triés par distance croissante`);
        }
      }
    
      // Logs détaillés
      console.log(`✅ ${itemsWithValidDistance.length} items avec distance calculée`);
      console.log(`⚠️ ${itemsWithDistance.length - itemsWithValidDistance.length} items sans distance`);
      
      if (itemsWithValidDistance.length > 0) {
        console.log(`\n📋 TOP 20 (tri: DISTANCE → CATÉGORIES → BOOSTS) :`);
        data.slice(0, 20).forEach((item, index) => {
          const cityName = (item.city || 'N/A').padEnd(20);
          const distance = isFinite(item._distance) ? item._distance.toFixed(2).padStart(8) : 'N/A'.padStart(8);
          const boost = (item.boost || 'basic').padEnd(10);
          const title = (item.title || item.name || 'N/A').substring(0, 30);
          console.log(`   ${(index + 1).toString().padStart(2)}. ${cityName} ${distance}km  ${boost}  "${title}"`);
        });
        
        // Vérification spécifique pour Sion et Zurich si on cherche Sierre
        if (selectedCityForSorting.name.toLowerCase().includes('sierre') || selectedCityForSorting.name.toLowerCase().includes('sion')) {
          const sion = itemsWithDistance.find(d => d.city && d.city.toLowerCase().includes('sion'));
          const zurich = itemsWithDistance.find(d => d.city && d.city.toLowerCase().includes('zurich'));
          
          console.log(`\n🔍 VÉRIFICATION SPÉCIFIQUE:`);
          if (sion) {
            const sionPos = itemsWithDistance.indexOf(sion) + 1;
            console.log(`   ✅ SION: ${sion._distance.toFixed(2)}km (position ${sionPos})`);
          }
          if (zurich) {
            const zurichPos = itemsWithDistance.indexOf(zurich) + 1;
            console.log(`   ✅ ZURICH: ${zurich._distance.toFixed(2)}km (position ${zurichPos})`);
          }
          
          if (sion && zurich) {
            if (sion._distance < zurich._distance) {
              console.log(`   ✅ TRI CORRECT: Sion (${sion._distance.toFixed(2)}km) est AVANT Zurich (${zurich._distance.toFixed(2)}km)`);
            } else {
              console.error(`   ❌ ERREUR: Sion (${sion._distance.toFixed(2)}km) est APRÈS Zurich (${zurich._distance.toFixed(2)}km) !`);
            }
          }
        }
      }
      
      console.log(`\n📊 Liste finale: ${data.length} items`);
      
      // Vérification finale : Afficher les 5 premiers avec leurs distances
      console.log(`\n🔍 VÉRIFICATION FINALE - 5 PREMIERS ITEMS:`);
      data.slice(0, 5).forEach((item, index) => {
        const dist = isFinite(item._distance) ? item._distance.toFixed(2) : 'Infinity';
        console.log(`   ${index + 1}. ${item.city || 'N/A'} - ${dist}km - boost:${item.boost || 'basic'}`);
      });
    }
  } else {
    // ============================================
    // MODE 2 : AUCUNE VILLE SÉLECTIONNÉE → TRIER PAR BOOST ET CATÉGORIES
    // ============================================
    
    const boostOrder = { platinum: 1, gold: 2, silver: 3, bronze: 4, basic: 5 };
    
    data = base
      .slice()
      .sort((a, b) => {
        // 1. Catégories sélectionnées (si filtre actif)
        if (selectedCategories.length > 0) {
          const catA = a.categories || [];
          const catB = b.categories || [];
          const matchA = catA.some(c => selectedCategories.some(sc => 
            c.toLowerCase().includes(sc.toLowerCase()) || sc.toLowerCase().includes(c.toLowerCase())
          ));
          const matchB = catB.some(c => selectedCategories.some(sc => 
            c.toLowerCase().includes(sc.toLowerCase()) || sc.toLowerCase().includes(c.toLowerCase())
          ));
          if (matchA && !matchB) return -1;
          if (!matchA && matchB) return 1;
        }
        
        // 2. Boost (platinum > gold > silver > bronze > basic)
        const boostA = boostOrder[a.boost || "basic"] || 99;
        const boostB = boostOrder[b.boost || "basic"] || 99;
        if (boostA !== boostB) return boostA - boostB;
        
        // 3. Platinum rank (si les deux sont platinum)
        if (a.boost === "platinum" && b.boost === "platinum") {
          const rankA = a.platinumRank || 10;
          const rankB = b.platinumRank || 10;
          if (rankA !== rankB) return rankA - rankB;
        }
        
        return 0;
      })
      .slice(0, 200);
  }

  // Le tri est déjà fait dans le bloc ci-dessus, pas besoin de vérification supplémentaire

  // Valeur actuelle de la recherche
  const currentSearchValue = listSearchCity || "";

  listView.style.display = "block";
  listView.innerHTML = `
    <div class="list-header" style="display:flex;flex-direction:column;gap:12px;padding:16px;background:var(--ui-card-bg);border-bottom:1px solid var(--ui-card-border);">
      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
        <div style="flex:1;">
          <div style="font-size:16px;font-weight:700;margin-bottom:4px;">📋 Résultats (${data.length}/${Math.min(base.length, 200)}${base.length > 200 ? ' (limite: 200 max)' : ''}) – ${currentMode.toUpperCase()}</div>
          <div style="font-size:12px;color:var(--ui-text-muted);">Cliquer sur un élément pour ouvrir la popup complète.${base.length > 200 ? ' Affichage limité à 200 résultats maximum.' : ''}</div>
        </div>
        <button onclick="toggleListView()" style="padding:8px 12px;border-radius:8px;background:rgba(239,68,68,0.2);border:1px solid rgba(239,68,68,0.4);color:#ef4444;font-size:12px;cursor:pointer;">✕ Fermer</button>
      </div>
      
      <!-- Barre de recherche ville/région -->
      <div style="position:relative;">
        <div style="display:flex;align-items:center;gap:8px;">
          <div style="flex:1;position:relative;">
            <input type="text" 
                   id="city-search-input"
                   placeholder="🔍 Rechercher une ville ou région..."
                   value="${escapeHtml(currentSearchValue)}"
                   oninput="onCitySearchInput(this.value)"
                   onfocus="showCitySuggestions()"
                   style="width:100%;padding:12px 16px;padding-right:40px;border-radius:12px;border:2px solid var(--ui-card-border);background:rgba(0,0,0,0.3);color:var(--ui-text-main);font-size:14px;outline:none;transition:all 0.2s;"
                   onfocus="this.style.borderColor='#00ffc3'"
                   onblur="setTimeout(() => { this.style.borderColor='var(--ui-card-border)'; hideCitySuggestions(); }, 200)">
            ${currentSearchValue ? `
              <button onclick="clearCitySearch()" 
                      style="position:absolute;right:12px;top:50%;transform:translateY(-50%);background:none;border:none;color:var(--ui-text-muted);font-size:18px;cursor:pointer;padding:4px;"
                      title="Effacer">✕</button>
            ` : ''}
          </div>
        </div>
        <div id="city-suggestions" style="display:none;position:absolute;top:100%;left:0;right:0;background:var(--ui-card-bg);border:1px solid var(--ui-card-border);border-radius:12px;margin-top:4px;max-height:250px;overflow-y:auto;z-index:100;box-shadow:0 10px 30px rgba(0,0,0,0.4);"></div>
      </div>
      
      ${selectedCityForSorting ? `
        <div style="display:flex;align-items:center;gap:10px;padding:12px 16px;background:linear-gradient(135deg,rgba(0,255,195,0.2),rgba(34,197,94,0.15));border:2px solid rgba(0,255,195,0.4);border-radius:10px;">
          <span style="font-size:18px;">📍</span>
          <div style="flex:1;">
            <div style="font-size:13px;color:var(--ui-text-muted);margin-bottom:2px;">Tri par proximité activé</div>
            <div style="font-size:15px;font-weight:700;color:#00ffc3;">
              ${escapeHtml(selectedCityForSorting.fullName || selectedCityForSorting.name)}
              ${selectedCityForSorting.countryCode ? getFlagEmoji(selectedCityForSorting.countryCode) : ''}
            </div>
          </div>
          <button onclick="clearCitySearch()" style="padding:6px 12px;background:rgba(239,68,68,0.2);border:1px solid rgba(239,68,68,0.4);border-radius:6px;color:#ef4444;font-size:12px;font-weight:600;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.background='rgba(239,68,68,0.3)'" onmouseout="this.style.background='rgba(239,68,68,0.2)'">✕ Réinitialiser</button>
        </div>
      ` : ''}
    </div>

    <div class="list-grid" style="display:grid;grid-template-columns: repeat(auto-fill,minmax(280px,1fr));gap:12px;padding:16px;max-height:calc(100vh - 200px);overflow-y:auto;">
      ${
        (() => {
          // FORCER LE TRI PAR DISTANCE AVANT L'AFFICHAGE si une ville est sélectionnée
          // PRIORITÉ ABSOLUE : Distance uniquement - AUCUNE EXCEPTION
          if (selectedCityForSorting && selectedCityForSorting.lat && selectedCityForSorting.lng) {
            console.log(`\n\n\n========================================`);
            console.log(`🔧 FORCER TRI PAR DISTANCE (PRIORITÉ ABSOLUE)`);
            console.log(`========================================`);
            console.log(`Nombre d'items: ${data.length}`);
            console.log(`Ville sélectionnée: ${selectedCityForSorting.name}`);
            console.log(`Coordonnées: lat=${selectedCityForSorting.lat}, lng=${selectedCityForSorting.lng}`);
            
            // Vérifier que les items ont bien des distances calculées
            const itemsWithDist = data.filter(item => item._distance !== undefined && isFinite(item._distance));
            const itemsWithoutDist = data.filter(item => !item._distance || !isFinite(item._distance));
            console.log(`   Items avec distance: ${itemsWithDist.length}, sans distance: ${itemsWithoutDist.length}`);
            
            // Créer une copie et trier UNIQUEMENT par distance
            const sortedData = [...data].sort((a, b) => {
              const distA = a._distance !== undefined && isFinite(a._distance) ? a._distance : Infinity;
              const distB = b._distance !== undefined && isFinite(b._distance) ? b._distance : Infinity;
              // Distance est la PRIORITÉ ABSOLUE - pas d'autre critère
              const result = distA - distB;
              return result;
            });
            
            // Vérifier les 10 premiers pour confirmer le tri
            console.log(`\n🔍 10 PREMIERS APRÈS TRI PAR DISTANCE (PRIORITÉ ABSOLUE):`);
            for (let i = 0; i < Math.min(10, sortedData.length); i++) {
              const item = sortedData[i];
              const dist = item._distance !== undefined && isFinite(item._distance) ? item._distance.toFixed(2) : 'Infinity';
              const city = item.city || item.title || item.name || 'N/A';
              console.log(`   ${i + 1}. ${city} - ${dist}km`);
            }
            
            // Vérification finale : s'assurer que le tri est correct
            let triCorrect = true;
            for (let i = 0; i < Math.min(10, sortedData.length - 1); i++) {
              const current = sortedData[i];
              const next = sortedData[i + 1];
              const distCurrent = current._distance !== undefined && isFinite(current._distance) ? current._distance : Infinity;
              const distNext = next._distance !== undefined && isFinite(next._distance) ? next._distance : Infinity;
              if (distCurrent > distNext) {
                triCorrect = false;
                console.error(`\n❌ ERREUR CRITIQUE: Item ${i} (${distCurrent.toFixed(2)}km) est APRÈS item ${i+1} (${distNext.toFixed(2)}km) !`);
                console.error(`   Item ${i}: ${current.city || current.title || current.name}`);
                console.error(`   Item ${i+1}: ${next.city || next.title || next.name}`);
              }
            }
            if (triCorrect) {
              console.log(`\n✅ TRI CORRECT - Les items sont triés par distance croissante`);
              console.log(`========================================\n\n\n`);
            } else {
              console.error(`\n❌ ERREUR CRITIQUE: Le tri ne fonctionne PAS !`);
              console.error(`========================================\n\n\n`);
            }
            
            return sortedData;
          }
          return data;
        })().map(item => {
            if (item.type === "event") {
              return buildEventCard(item, item._distance);
            }
            if (item.type === "booking") {
              return buildBookingCard(item, item._distance);
            }
            if (item.type === "service") {
              return buildServiceCard(item, item._distance);
            }
            return "";
          })
          .join("") ||
        "<div style='color:var(--ui-text-muted);padding:20px;text-align:center;'>Aucun résultat</div>"
      }
    </div>
  `;

  listView.querySelectorAll("[data-type][data-id]").forEach(card => {
    card.addEventListener("click", () => {
      const type = card.dataset.type;
      const id = card.dataset.id;
      openPopupFromList(type, id);
    });
  });
  
  // Vérifier les alertes de proximité après le rafraîchissement de la liste
  if (currentUser.isLoggedIn) {
    checkProximityAlerts();
  }
  
  // Nettoyer les événements passés (sauf organisateurs)
  cleanExpiredEvents();
}

// Cartes style Airbnb pour la liste
function buildEventCard(ev, distance = null) {
  const imgTag = buildMainImageTag(ev, ev.title || "");
  const borderColor = getBoostColor(ev.boost);
  const emoji = getCategoryEmoji(ev);
  const isLiked = currentUser.likes.includes(`event:${ev.id}`);
  
  // Badge boost
  const boostBadge = ev.boost && ev.boost !== "basic" ? `
    <div style="position:absolute;top:8px;right:8px;padding:4px 8px;border-radius:999px;font-size:10px;font-weight:700;z-index:6;
      ${ev.boost === 'platinum' ? 'background:linear-gradient(135deg,#e5e4e2,#fff);color:#1f2937;' : ''}
      ${ev.boost === 'gold' ? 'background:linear-gradient(135deg,#ffd700,#ffed4a);color:#1f2937;' : ''}
      ${ev.boost === 'silver' ? 'background:linear-gradient(135deg,#c0c0c0,#e5e5e5);color:#1f2937;' : ''}
      ${ev.boost === 'bronze' ? 'background:linear-gradient(135deg,#cd7f32,#daa06d);color:#fff;' : ''}
    ">
      ${ev.boost === 'platinum' ? '👑 TOP' : ev.boost === 'gold' ? '🥇' : ev.boost === 'silver' ? '🥈' : '🥉'}
    </div>
  ` : '';
  
  // Badge distance (afficher seulement si distance valide)
  const distanceBadge = (distance !== null && distance !== undefined && isFinite(distance) && distance !== Infinity) ? `
    <div style="position:absolute;top:8px;left:8px;padding:4px 8px;border-radius:999px;font-size:10px;font-weight:600;background:rgba(0,0,0,0.7);color:#fff;backdrop-filter:blur(4px);z-index:5;">
      📍 ${distance < 1 ? Math.round(distance * 1000) + 'm' : distance.toFixed(1) + 'km'}
    </div>
  ` : '';

  return `
    <div data-type="event" data-id="${ev.id}" class="event-card" onclick="openPopupFromList('event', ${ev.id})" style="
      border:3px solid ${borderColor};
      border-radius:16px;
      background:var(--ui-card-bg);
      overflow:hidden;
      cursor:pointer;
      transition:all 0.2s ease;
      box-shadow:0 4px 20px rgba(0,0,0,0.2);
      position:relative;
    ">
      <div style="position:relative;height:160px;overflow:hidden;">
        ${imgTag}
        ${distanceBadge}
        ${boostBadge}
        <button onclick="event.stopPropagation();onAction('like','event',${ev.id})" style="position:absolute;top:8px;${distanceBadge ? 'left:50px;' : 'left:8px;'}width:32px;height:32px;border-radius:50%;border:none;background:rgba(0,0,0,0.5);color:${isLiked ? '#ef4444' : '#fff'};cursor:pointer;font-size:16px;z-index:7;">
          ${isLiked ? '❤️' : '🤍'}
        </button>
        ${ev.status && ev.status !== 'OK' ? `<div style="position:absolute;bottom:0;left:0;right:0;padding:6px;background:${ev.status === 'COMPLET' ? 'rgba(234,179,8,0.9)' : 'rgba(239,68,68,0.9)'};color:#fff;font-size:11px;font-weight:700;text-align:center;">${ev.status}</div>` : ''}
      </div>
      <div style="padding:12px;">
        <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;">
          <span style="font-size:18px;">${emoji}</span>
          <span style="font-size:11px;color:var(--ui-text-muted);">${(ev.categories || []).join(" • ")}</span>
          ${ev.verified ? '<span style="font-size:10px;color:#3b82f6;">✓</span>' : ''}
        </div>
        <div style="font-size:15px;font-weight:700;margin-bottom:4px;line-height:1.3;">${escapeHtml(ev.title || "")}</div>
        <div style="font-size:12px;color:#00ffc3;margin-bottom:4px;">
          📅 ${formatEventDateRange(ev.startDate, ev.endDate)}
        </div>
        <div style="font-size:11px;color:var(--ui-text-muted);margin-bottom:8px;">
          📍 ${escapeHtml(ev.city || "")}
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;color:var(--ui-text-muted);">
          <span>❤️ ${ev.likes || 0} • 👥 ${ev.participants || 0}</span>
          ${ev.isAI ? '<span style="color:#facc15;">🤖 IA</span>' : ''}
        </div>
      </div>
    </div>
  `;
}

function buildBookingCard(b, distance = null) {
  const imgTag = buildMainImageTag(b, b.name || "");
  const borderColor = getBoostColor(b.boost);
  const emoji = getCategoryEmoji(b);
  const isLiked = currentUser.likes.includes(`booking:${b.id}`);
  
  // Badge distance (afficher seulement si distance valide)
  const distanceBadge = (distance !== null && distance !== undefined && isFinite(distance) && distance !== Infinity) ? `
    <div style="position:absolute;top:8px;left:8px;padding:4px 8px;border-radius:999px;font-size:10px;font-weight:600;background:rgba(0,0,0,0.7);color:#fff;backdrop-filter:blur(4px);z-index:5;">
      📍 ${distance < 1 ? Math.round(distance * 1000) + 'm' : distance.toFixed(1) + 'km'}
    </div>
  ` : '';

  return `
    <div data-type="booking" data-id="${b.id}" class="event-card" onclick="openPopupFromList('booking', ${b.id})" style="
      border:3px solid ${borderColor};
      border-radius:16px;
      background:var(--ui-card-bg);
      overflow:hidden;
      cursor:pointer;
      transition:all 0.2s ease;
      box-shadow:0 4px 20px rgba(0,0,0,0.2);
      position:relative;
    ">
      <div style="position:relative;height:160px;overflow:hidden;">
        ${imgTag}
        ${distanceBadge}
        <button onclick="event.stopPropagation();onAction('like','booking',${b.id})" style="position:absolute;top:8px;${distanceBadge ? 'left:50px;' : 'left:8px;'}width:32px;height:32px;border-radius:50%;border:none;background:rgba(0,0,0,0.5);color:${isLiked ? '#ef4444' : '#fff'};cursor:pointer;font-size:16px;z-index:7;">
          ${isLiked ? '❤️' : '🤍'}
        </button>
        ${b.level && b.level !== 'Non détecté' ? `<div style="position:absolute;bottom:8px;right:8px;padding:4px 10px;border-radius:999px;font-size:10px;font-weight:600;background:rgba(139,92,246,0.9);color:#fff;">${b.level}</div>` : ''}
      </div>
      <div style="padding:12px;">
        <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;">
          <span style="font-size:18px;">${emoji}</span>
          <span style="font-size:11px;color:var(--ui-text-muted);">${(b.categories || []).join(" • ")}</span>
          ${b.verified ? '<span style="font-size:10px;color:#3b82f6;">✓</span>' : ''}
        </div>
        <div style="font-size:15px;font-weight:700;margin-bottom:4px;">${escapeHtml(b.name || "")}</div>
        <div style="font-size:11px;color:var(--ui-text-muted);margin-bottom:4px;">
          📍 ${escapeHtml(b.city || "")}
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;">
          <span style="color:var(--ui-text-muted);">⭐ ${b.rating || '—'}/5</span>
          ${b.soundLinks && b.soundLinks.length > 0 ? '<span style="color:#a78bfa;">🎵 Audio</span>' : '<span style="color:#ef4444;">⚠️ Pas d\'audio</span>'}
        </div>
      </div>
    </div>
  `;
}

function buildServiceCard(s, distance = null) {
  const imgTag = buildMainImageTag(s, s.name || "");
  const borderColor = getBoostColor(s.boost);
  const emoji = getCategoryEmoji(s);
  const isLiked = currentUser.likes.includes(`service:${s.id}`);
  
  // Badge distance (afficher seulement si distance valide)
  const distanceBadge = (distance !== null && distance !== undefined && isFinite(distance) && distance !== Infinity) ? `
    <div style="position:absolute;top:8px;left:8px;padding:4px 8px;border-radius:999px;font-size:10px;font-weight:600;background:rgba(0,0,0,0.7);color:#fff;backdrop-filter:blur(4px);z-index:5;">
      📍 ${distance < 1 ? Math.round(distance * 1000) + 'm' : distance.toFixed(1) + 'km'}
    </div>
  ` : '';

  return `
    <div data-type="service" data-id="${s.id}" class="event-card" onclick="openPopupFromList('service', ${s.id})" style="
      border:3px solid ${borderColor};
      border-radius:16px;
      background:var(--ui-card-bg);
      overflow:hidden;
      cursor:pointer;
      transition:all 0.2s ease;
      box-shadow:0 4px 20px rgba(0,0,0,0.2);
      position:relative;
    ">
      <div style="position:relative;height:160px;overflow:hidden;">
        ${imgTag}
        ${distanceBadge}
        <button onclick="event.stopPropagation();onAction('like','service',${s.id})" style="position:absolute;top:8px;${distanceBadge ? 'left:50px;' : 'left:8px;'}width:32px;height:32px;border-radius:50%;border:none;background:rgba(0,0,0,0.5);color:${isLiked ? '#ef4444' : '#fff'};cursor:pointer;font-size:16px;z-index:7;">
          ${isLiked ? '❤️' : '🤍'}
        </button>
      </div>
      <div style="padding:12px;">
        <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;">
          <span style="font-size:18px;">${emoji}</span>
          <span style="font-size:11px;color:var(--ui-text-muted);">${(s.categories || []).join(" • ")}</span>
          ${s.verified ? '<span style="font-size:10px;color:#3b82f6;">✓</span>' : ''}
        </div>
        <div style="font-size:15px;font-weight:700;margin-bottom:4px;">${escapeHtml(s.name || "")}</div>
        <div style="font-size:11px;color:var(--ui-text-muted);margin-bottom:4px;">
          📍 ${escapeHtml(s.city || "")}, Suisse
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;">
          <span style="color:var(--ui-text-muted);">⭐ ${s.rating || '—'}/5</span>
          <span style="color:var(--ui-text-muted);">❤️ ${s.likes || 0}</span>
        </div>
      </div>
    </div>
  `;
}

function openPopupFromList(type, id) {
  const item = getItemById(type, id);
  if (!item) {
    showNotification("⚠️ Item introuvable", "error");
    return;
  }
  
  // Construire le HTML de la popup
  let popupHtml = "";
  if (type === "event") {
    popupHtml = buildEventPopup(item);
  } else if (type === "booking") {
    popupHtml = buildBookingPopup(item);
  } else if (type === "service") {
    popupHtml = buildServicePopup(item);
  }
  
  // Afficher dans une modal avec overlay - EN MODE LISTE, même taille que sur la map (380px exactement)
  // La popup doit être exactement la même que sur la map, avec toutes les actions
  // IMPORTANT: La bordure doit s'aligner PARFAITEMENT avec l'image - PAS DE PADDING, PAS DE MARGIN
  const modalHtml = `
    <div style="position:relative;width:380px;max-height:85vh;overflow:hidden;background:var(--ui-card-bg);border-radius:16px;border:1px solid var(--ui-card-border);margin:20px;box-shadow:0 20px 60px rgba(0,0,0,0.5);display:flex;flex-direction:column;padding:0;box-sizing:border-box;">
      <button onclick="closePopupModal()" style="position:absolute;top:12px;right:12px;width:36px;height:36px;border-radius:50%;border:none;background:rgba(0,0,0,0.6);color:#fff;cursor:pointer;font-size:20px;z-index:1001;display:flex;align-items:center;justify-content:center;transition:all 0.2s;" onmouseover="this.style.background='rgba(239,68,68,0.8)'" onmouseout="this.style.background='rgba(0,0,0,0.6)'">✕</button>
      <div style="flex:1;overflow-y:auto;scrollbar-width:none;width:100%;margin:0;padding:0;box-sizing:border-box;">
        ${popupHtml}
      </div>
    </div>
  `;
  
  // Créer ou réutiliser le backdrop - EN MODE LISTE, devant la liste (z-index élevé)
  let backdrop = document.getElementById("popup-modal-backdrop");
  if (!backdrop) {
    backdrop = document.createElement("div");
    backdrop.id = "popup-modal-backdrop";
    // z-index très élevé pour être devant la liste (qui est à z-index normal)
    backdrop.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,0.75);display:flex;align-items:center;justify-content:center;z-index:99999;backdrop-filter:blur(2px);";
    backdrop.onclick = (e) => {
      if (e.target === backdrop) closePopupModal();
    };
    document.body.appendChild(backdrop);
  }
  
  backdrop.innerHTML = modalHtml;
  backdrop.style.display = "flex";
  
  // Marquer qu'on est en mode liste pour le retour
  backdrop.dataset.fromList = "true";
  
  // Centrer la map sur l'item si possible
  if (map && item.lat && item.lng) {
    map.setView([item.lat, item.lng], Math.max(map.getZoom(), 13));
  }
}

function closePopupModal() {
  const modal = document.getElementById("popup-modal");
  if (modal) {
    modal.remove();
  }
  const backdrop = document.getElementById("popup-modal-backdrop");
  if (backdrop) {
    backdrop.style.display = "none";
    // Si on était en mode liste, s'assurer que la liste reste ouverte
    if (backdrop.dataset.fromList === "true" && listViewOpen) {
      // La liste reste ouverte automatiquement car listViewOpen est toujours true
      backdrop.dataset.fromList = "false";
    }
  }
  // Restaurer le scroll du body
  document.body.style.overflow = '';
  
  // Recentrer la map sur le marqueur qu'on venait de consulter
  if (currentPopupMarker && map) {
    try {
      const latlng = currentPopupMarker.getLatLng();
      // Zoomer assez proche pour voir le point immédiatement
      map.setView(latlng, Math.max(map.getZoom(), 16), { animate: true, duration: 0.3 });
    } catch(e) {
      console.warn('Erreur recentrage map:', e);
    }
    currentPopupMarker = null;
  }
  
  // Réactiver COMPLÈTEMENT les événements Leaflet
  if (map) {
    try {
      map.scrollWheelZoom.enable();
      map.dragging.enable();
      map.touchZoom.enable();
      map.doubleClickZoom.enable();
      // Réactiver les événements au niveau du conteneur de la map
      const mapContainer = map.getContainer();
      if (mapContainer) {
        mapContainer.style.pointerEvents = 'auto';
      }
    } catch(e) {
      console.warn('Erreur réactivation Leaflet:', e);
    }
  }
}

// Variable pour stocker la recherche de ville
let listSearchCity = "";

// Sélectionner une ville pour le tri par distance
function selectCityForSorting(cityName) {
  if (!cityName || cityName === "") {
    selectedCityForSorting = null;
    listSearchCity = "";
  } else {
    const allCities = [...SWISS_CITIES, ...FRENCH_CITIES];
    selectedCityForSorting = allCities.find(c => c.name === cityName) || null;
    if (selectedCityForSorting) {
      listSearchCity = selectedCityForSorting.name;
    }
  }
  
  // Rafraîchir la liste avec le nouveau tri
  if (listViewOpen) {
    refreshListView();
  }
  
  // Rafraîchir aussi les marqueurs sur la map
  refreshMarkers();
}

// Recherche de ville avec autocomplétion - MONDIALE via Nominatim API
let searchTimeout = null;

function onCitySearchInput(value) {
  listSearchCity = value;
  
  const suggestionsDiv = document.getElementById("city-suggestions");
  if (!suggestionsDiv) return;
  
  if (!value || value.length < 2) {
    suggestionsDiv.style.display = "none";
    if (!value) {
      selectedCityForSorting = null;
      refreshListView();
    }
    return;
  }
  
  // Annuler la recherche précédente
  if (searchTimeout) clearTimeout(searchTimeout);
  
  // Afficher un loading
  suggestionsDiv.innerHTML = `
    <div style="padding:16px;text-align:center;color:var(--ui-text-muted);">
      <span style="animation:pulse-subtle 1s infinite;">🔍 Recherche...</span>
    </div>
  `;
  suggestionsDiv.style.display = "block";
  
  // Attendre 300ms avant de lancer la recherche (debounce)
  searchTimeout = setTimeout(() => {
    searchCityGlobal(value);
  }, 300);
}

// Recherche mondiale via Nominatim (OpenStreetMap)
async function searchCityGlobal(query) {
  const suggestionsDiv = document.getElementById("city-suggestions");
  if (!suggestionsDiv) return;
  
  // D'abord chercher dans les villes locales (Suisse/France)
  const allLocalCities = [...SWISS_CITIES, ...FRENCH_CITIES];
  const searchLower = query.toLowerCase();
  const localMatches = allLocalCities.filter(city => 
    city.name.toLowerCase().includes(searchLower) ||
    (city.region && city.region.toLowerCase().includes(searchLower))
  ).slice(0, 5);
  
  // Ensuite chercher via API Nominatim pour le reste du monde
  let globalMatches = [];
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=8&addressdetails=1&featuretype=city`,
      { headers: { 'Accept-Language': 'fr' } }
    );
    const results = await response.json();
    
    globalMatches = results
      .filter(r => r.type === 'city' || r.type === 'town' || r.type === 'village' || r.class === 'place')
      .map(r => ({
        name: r.address?.city || r.address?.town || r.address?.village || r.name,
        lat: parseFloat(r.lat),
        lng: parseFloat(r.lon),
        region: r.address?.state || r.address?.county || '',
        country: r.address?.country || '',
        countryCode: r.address?.country_code?.toUpperCase() || ''
      }))
      .filter(c => c.name); // Filtrer les résultats sans nom
  } catch (error) {
    console.warn('Erreur recherche Nominatim:', error);
  }
  
  // Combiner les résultats (locaux en premier)
  // Marquer les villes locales pour les distinguer
  const localMatchesMarked = localMatches.map(c => ({ ...c, isLocal: true, country: c.country || 'Suisse', countryCode: c.countryCode || 'CH' }));
  const globalMatchesMarked = globalMatches.map(c => ({ ...c, isLocal: false }));
  const allMatches = [...localMatchesMarked, ...globalMatchesMarked].slice(0, 10);
  
  if (allMatches.length === 0) {
    suggestionsDiv.innerHTML = `
      <div style="padding:16px;color:var(--ui-text-muted);text-align:center;">
        <div style="font-size:24px;margin-bottom:8px;">🌍</div>
        <div style="font-size:13px;">Aucune ville trouvée pour "<strong>${escapeHtml(query)}</strong>"</div>
        <div style="font-size:11px;margin-top:4px;">Essayez un autre nom ou une orthographe différente</div>
      </div>
    `;
    suggestionsDiv.style.display = "block";
    return;
  }
  
  // Afficher les suggestions avec pays/région bien visible
  suggestionsDiv.innerHTML = allMatches.map((city, index) => {
    const locationText = city.isLocal 
      ? `${city.region || city.canton || ''}${city.region && city.canton ? ' (' + city.canton + ')' : city.canton ? ' (' + city.canton + ')' : ''}, ${city.country || 'Suisse'}`
      : `${city.region ? escapeHtml(city.region) + ', ' : ''}${escapeHtml(city.country || '')}`;
    
    return `
    <div onclick="selectCityFromSearch(${index})" 
         data-city-index="${index}"
         style="padding:14px 16px;cursor:pointer;display:flex;align-items:center;gap:12px;transition:all 0.15s;border-bottom:1px solid var(--ui-card-border);"
         onmouseover="this.style.background='rgba(0,255,195,0.15)';this.style.borderLeft='3px solid #00ffc3'"
         onmouseout="this.style.background='transparent';this.style.borderLeft='none'">
      <span style="font-size:20px;">📍</span>
      <div style="flex:1;min-width:0;">
        <div style="font-weight:700;color:var(--ui-text-main);font-size:15px;margin-bottom:4px;">${escapeHtml(city.name)}</div>
        <div style="font-size:12px;color:var(--ui-text-muted);display:flex;align-items:center;gap:6px;">
          <span>${locationText}</span>
          ${city.isLocal ? '<span style="padding:2px 6px;background:rgba(0,255,195,0.2);border-radius:4px;font-size:10px;color:#00ffc3;">Local</span>' : ''}
        </div>
      </div>
      <span style="font-size:20px;flex-shrink:0;">${getFlagEmoji(city.countryCode || (city.isLocal ? 'CH' : ''))}</span>
    </div>
  `;
  }).join('');
  
  // Stocker les résultats pour la sélection
  window._citySearchResults = allMatches;
  suggestionsDiv.style.display = "block";
}

// Obtenir le drapeau emoji d'un pays
function getFlagEmoji(countryCode) {
  if (!countryCode || countryCode.length !== 2) return '🌍';
  const codePoints = countryCode
    .toUpperCase()
    .split('')
    .map(char => 127397 + char.charCodeAt(0));
  return String.fromCodePoint(...codePoints);
}

window.getFlagEmoji = getFlagEmoji;

// Sélectionner une ville depuis les résultats de recherche
function selectCityFromSearch(index) {
  const city = window._citySearchResults?.[index];
  if (!city) {
    console.warn('Aucune ville trouvée à l\'index', index);
    return;
  }
  
  // Construire le nom complet avec pays/région pour l'affichage
  const fullName = city.isLocal 
    ? `${city.name}, ${city.region || city.canton || ''}, ${city.country || 'Suisse'}`
    : `${city.name}, ${city.region ? city.region + ', ' : ''}${city.country || ''}`;
  
  // Vérifier que la ville a bien des coordonnées
  if (!city.lat || !city.lng || isNaN(city.lat) || isNaN(city.lng)) {
    console.error(`❌ ERREUR: La ville "${city.name}" n'a pas de coordonnées valides!`, city);
    showNotification(`❌ Erreur: Coordonnées manquantes pour ${city.name}`, 'error');
    return;
  }
  
  // Stocker la ville sélectionnée avec toutes ses infos
  selectedCityForSorting = {
    name: city.name,
    lat: parseFloat(city.lat),
    lng: parseFloat(city.lng),
    region: city.region || city.canton || '',
    country: city.country || (city.isLocal ? 'Suisse' : ''),
    countryCode: city.countryCode || (city.isLocal ? 'CH' : ''),
    fullName: fullName
  };
  
  // Vérifier que les coordonnées sont valides après conversion
  if (isNaN(selectedCityForSorting.lat) || isNaN(selectedCityForSorting.lng)) {
    console.error(`❌ ERREUR: Coordonnées invalides après conversion!`, selectedCityForSorting);
    showNotification(`❌ Erreur: Coordonnées invalides pour ${city.name}`, 'error');
    return;
  }
  
  // Mettre à jour le texte de recherche avec le nom complet
  listSearchCity = fullName;
  
  // Cacher les suggestions
  const suggestionsDiv = document.getElementById("city-suggestions");
  if (suggestionsDiv) suggestionsDiv.style.display = "none";
  
  // Mettre à jour l'input avec le nom complet
  const input = document.getElementById("city-search-input");
  if (input) input.value = fullName;
  
  console.log(`✅ Ville sélectionnée pour tri: ${city.name}`);
  console.log(`   Coordonnées: lat=${selectedCityForSorting.lat}, lng=${selectedCityForSorting.lng}`);
  console.log(`   Objet complet:`, selectedCityForSorting);
  
  console.log(`✅ Ville sélectionnée pour tri: ${city.name}`);
  console.log(`   Coordonnées: lat=${selectedCityForSorting.lat}, lng=${selectedCityForSorting.lng}`);
  console.log(`   Objet complet:`, selectedCityForSorting);
  console.log(`   listViewOpen: ${listViewOpen}`);
  
  // FORCER le rafraîchissement de la liste avec le nouveau tri (même si la liste n'est pas encore ouverte)
  // La liste sera triée correctement quand elle s'ouvrira
  if (listViewOpen) {
    console.log(`🔄 Rafraîchissement de la liste avec tri par distance...`);
    refreshListView();
  } else {
    console.log(`ℹ️ Liste non ouverte, le tri sera appliqué à l'ouverture`);
  }
  
  // Rafraîchir aussi les marqueurs sur la map
  refreshMarkers();
  
  // Centrer la map sur la ville sélectionnée
  if (map && selectedCityForSorting.lat && selectedCityForSorting.lng) {
    map.setView([selectedCityForSorting.lat, selectedCityForSorting.lng], 10);
    showNotification(`📍 Tri par proximité: ${city.name}`, 'success');
  }
}

window.selectCityFromSearch = selectCityFromSearch;

window.searchCityGlobal = searchCityGlobal;
window.selectCityFromSearch = selectCityFromSearch;

function selectCityFromSuggestion(cityName) {
  const allCities = [...SWISS_CITIES, ...FRENCH_CITIES];
  const city = allCities.find(c => c.name === cityName);
  
  if (city) {
    selectedCityForSorting = city;
    listSearchCity = city.name;
    
    // Cacher les suggestions
    const suggestionsDiv = document.getElementById("city-suggestions");
    if (suggestionsDiv) suggestionsDiv.style.display = "none";
    
    // Mettre à jour l'input
    const input = document.getElementById("city-search-input");
    if (input) input.value = city.name;
    
    // Rafraîchir la liste
    refreshListView();
  }
}

function showCitySuggestions() {
  const input = document.getElementById("city-search-input");
  if (input && input.value.length >= 2) {
    onCitySearchInput(input.value);
  }
}

function hideCitySuggestions() {
  const suggestionsDiv = document.getElementById("city-suggestions");
  if (suggestionsDiv) {
    setTimeout(() => { suggestionsDiv.style.display = "none"; }, 200);
  }
}

function clearCitySearch() {
  listSearchCity = "";
  selectedCityForSorting = null;
  
  const input = document.getElementById("city-search-input");
  if (input) input.value = "";
  
  const suggestionsDiv = document.getElementById("city-suggestions");
  if (suggestionsDiv) suggestionsDiv.style.display = "none";
  
  refreshListView();
}

// Exposer les nouvelles fonctions
window.onCitySearchInput = onCitySearchInput;
window.selectCityFromSuggestion = selectCityFromSuggestion;
window.showCitySuggestions = showCitySuggestions;
window.hideCitySuggestions = hideCitySuggestions;
window.clearCitySearch = clearCitySearch;

// ============================================
// FILTRE EXPLORATEUR "LEADER ONE" – MULTI-COLONNES + DATES
// ============================================
let explorerOpen = false;
let explorerPath = [];
let selectedCategories = [];
let explorerTree = null;

// filtres dates (mode event)
let timeFilter = null; // null | 'range' (les boutons rapides ajoutent maintenant à selectedDates)
let dateRangeStart = null;
let dateRangeEnd = null;
let selectedDates = []; // Pour cumuler : ['today', 'tomorrow', 'weekend', etc.]

// surcharge toggleLeftPanel
function toggleLeftPanel() {
  explorerOpen = !explorerOpen;
  const panel = document.getElementById("left-panel");
  if (!explorerOpen) {
    panel.style.display = "none";
    return;
  }
  // Ouvrir le panneau et charger l'arbre correspondant au mode actuel
  panel.style.display = "block";
  console.log(`🔍 Ouverture du filtre pour le mode: ${currentMode}`);
  loadExplorerTree(); // Charge automatiquement le bon arbre selon currentMode
}

// charger l'arbre depuis /trees/*.json
function loadExplorerTree() {
  let file = "";
  if (currentMode === "event") file = "trees/events_tree.json";
  if (currentMode === "booking") file = "trees/booking_tree.json";
  if (currentMode === "service") file = "trees/service_tree.json";

  console.log(`🔍 Chargement de l'arbre depuis : ${file}`);
  fetch(file)
    .then(r => {
      console.log(`📡 Réponse fetch : ${r.status} ${r.statusText} pour ${file}`);
      if (!r.ok) {
        throw new Error(`HTTP ${r.status} - ${r.statusText}`);
      }
      return r.json();
    })
    .then(json => {
      console.log(`✅ Arbre chargé avec succès :`, Object.keys(json));
      // Normaliser la structure selon le mode
      if (json.Events) {
        // events_tree.json : { "Events": { "Music": {...}, ... } }
        explorerTree = json.Events;
      } else if (json.categories && json.categories.children) {
        // booking_tree.json / service_tree.json : { "categories": { "name": "...", "children": [...] } }
        // Convertir en structure compatible { "NomCategorie": {...}, ... }
        explorerTree = normalizeTreeFromChildren(json.categories.children);
      } else if (json.categories) {
        explorerTree = json.categories;
      } else {
        explorerTree = json;
      }

      explorerPath = [];
      renderExplorer();
    })
    .catch(err => {
      console.error("❌ Erreur chargement arbre :", err);
      console.error("   Fichier tenté :", file);
      const panel = document.getElementById("left-panel");
      panel.innerHTML = `
        <div style='padding:20px;font-size:13px;color:#f87171;text-align:center;'>
          <div style='font-size:48px;margin-bottom:12px;'>⚠️</div>
          <div style='font-weight:600;margin-bottom:8px;'>Impossible de charger les catégories</div>
          <div style='font-size:11px;color:var(--ui-text-muted);margin-bottom:12px;'>
            Fichier : ${file}<br>
            Erreur : ${err.message}
          </div>
          <button onclick="loadExplorerTree()" style='padding:8px 16px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-size:12px;'>
            🔄 Réessayer
          </button>
        </div>
      `;
    });
}

// Convertit un tableau de { name, children } en objet { name: children_ou_liste }
function normalizeTreeFromChildren(children) {
  if (!Array.isArray(children)) return children;
  
  const result = {};
  children.forEach(item => {
    if (typeof item === "string") {
      // C'est une feuille
      return;
    }
    if (item.name) {
      if (item.children && item.children.length > 0) {
        // Vérifier si les enfants sont des objets ou des strings
        const firstChild = item.children[0];
        if (typeof firstChild === "string" || (firstChild && !firstChild.children)) {
          // Les enfants sont des feuilles (strings ou objets sans children)
          result[item.name] = item.children.map(c => typeof c === "string" ? c : c.name);
        } else {
          // Les enfants ont eux-mêmes des enfants
          result[item.name] = normalizeTreeFromChildren(item.children);
        }
      } else {
        // Pas d'enfants, c'est une catégorie finale
        result[item.name] = [];
      }
    }
  });
  return result;
}

function renderExplorer() {
  const panel = document.getElementById("left-panel");
  panel.style.width = "480px";
  panel.style.maxHeight = "calc(100vh - 100px)";
  panel.style.overflow = "hidden";
  panel.style.display = "block";

  const dateControls =
    currentMode === "event"
      ? `
      <div style="margin-bottom:10px;font-size:11px;color:var(--ui-text-muted);">
        📅 Filtrer par date (cumulable) :
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px;">
        <label class="date-checkbox-label ${selectedDates.includes('today') ? 'active' : ''}">
          <input type="checkbox" ${selectedDates.includes('today') ? 'checked' : ''} onchange="toggleDateFilter('today')">
          Aujourd'hui
        </label>
        <label class="date-checkbox-label ${selectedDates.includes('tomorrow') ? 'active' : ''}">
          <input type="checkbox" ${selectedDates.includes('tomorrow') ? 'checked' : ''} onchange="toggleDateFilter('tomorrow')">
          Demain
        </label>
        <label class="date-checkbox-label ${selectedDates.includes('weekend') ? 'active' : ''}">
          <input type="checkbox" ${selectedDates.includes('weekend') ? 'checked' : ''} onchange="toggleDateFilter('weekend')">
          Ce week-end
        </label>
        <label class="date-checkbox-label ${selectedDates.includes('week') ? 'active' : ''}">
          <input type="checkbox" ${selectedDates.includes('week') ? 'checked' : ''} onchange="toggleDateFilter('week')">
          Cette semaine
        </label>
        <label class="date-checkbox-label ${selectedDates.includes('month') ? 'active' : ''}">
          <input type="checkbox" ${selectedDates.includes('month') ? 'checked' : ''} onchange="toggleDateFilter('month')">
          Ce mois
        </label>
      </div>
      
      <div style="margin-bottom:12px;padding:10px;background:rgba(0,255,195,0.03);border-radius:10px;">
        <div style="font-size:11px;color:var(--ui-text-muted);margin-bottom:8px;">📆 Ou sélectionner une période :</div>
        <div style="display:flex;gap:10px;align-items:center;">
          <div style="flex:1;">
            <label style="font-size:10px;color:var(--ui-text-muted);">Du</label>
            <input type="date" id="date-range-start" style="width:100%;padding:8px;border-radius:8px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:12px;cursor:pointer;">
          </div>
          <div style="color:var(--ui-text-muted);font-size:16px;">→</div>
          <div style="flex:1;">
            <label style="font-size:10px;color:var(--ui-text-muted);">Au</label>
            <input type="date" id="date-range-end" style="width:100%;padding:8px;border-radius:8px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:12px;cursor:pointer;">
          </div>
        </div>
        <div id="date-range-display" style="font-size:11px;color:#00ffc3;text-align:center;min-height:16px;margin-top:6px;"></div>
      </div>
    `
      : "";

  panel.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
      <div style="font-size:15px;font-weight:700;">Filtrer – ${currentMode}</div>
      <button onclick="closeLeftPanel()" style="background:none;border:none;color:var(--ui-text-muted);font-size:20px;cursor:pointer;padding:4px 8px;border-radius:6px;transition:all 0.15s;" onmouseover="this.style.background='rgba(255,255,255,0.1)';this.style.color='#fff'" onmouseout="this.style.background='none';this.style.color='var(--ui-text-muted)'">✕</button>
    </div>
    <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:10px;">Cochez les catégories souhaitées.</div>

    ${dateControls}

    <div id="explorer-selected" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;"></div>

    <div id="explorer-columns"
      style="
        display:flex;
        gap:12px;
        overflow-x:auto;
        padding-bottom:6px;
        margin-bottom:8px;
        max-height:300px;
      ">
    </div>

    <button onclick="resetExplorerFilter()" class="pill small" style="margin-top:6px;">
      🔄 Réinitialiser tout
    </button>
  `;

  renderSelectedTags();
  buildExplorerColumns();

  if (currentMode === "event") {
    setupDateRangePicker();
  }
}

// Fermer le panneau filtre
function closeLeftPanel() {
  explorerOpen = false;
  const panel = document.getElementById("left-panel");
  if (panel) panel.style.display = "none";
}

// Toggle un filtre de date (cumulable)
function toggleDateFilter(dateType) {
  if (selectedDates.includes(dateType)) {
    selectedDates = selectedDates.filter(d => d !== dateType);
        } else {
    selectedDates.push(dateType);
  }
  // Rafraîchir l'affichage des checkboxes
  renderExplorer();
  applyExplorerFilter();
}

// Gestion du sélecteur de plage de dates
function setupDateRangePicker() {
  const startInput = document.getElementById("date-range-start");
  const endInput = document.getElementById("date-range-end");
  const display = document.getElementById("date-range-display");
  
  if (!startInput || !endInput) return;
  
  // Initialiser avec les valeurs existantes
  if (dateRangeStart) startInput.value = dateRangeStart;
  if (dateRangeEnd) endInput.value = dateRangeEnd;
  
  updateDateRangeDisplay();
  
  startInput.addEventListener("change", () => {
    dateRangeStart = startInput.value || null;
    // Si pas de date de fin, mettre la même que le début
    if (dateRangeStart && !dateRangeEnd) {
      dateRangeEnd = dateRangeStart;
      endInput.value = dateRangeEnd;
    }
    // Si date début > date fin, ajuster
    if (dateRangeStart && dateRangeEnd && dateRangeStart > dateRangeEnd) {
      dateRangeEnd = dateRangeStart;
      endInput.value = dateRangeEnd;
    }
    timeFilter = (dateRangeStart || dateRangeEnd) ? "range" : null;
    updateDateRangeDisplay();
        applyExplorerFilter();
      });
  
  endInput.addEventListener("change", () => {
    dateRangeEnd = endInput.value || null;
    // Si pas de date de début, mettre la même que la fin
    if (dateRangeEnd && !dateRangeStart) {
      dateRangeStart = dateRangeEnd;
      startInput.value = dateRangeStart;
    }
    // Si date fin < date début, ajuster
    if (dateRangeStart && dateRangeEnd && dateRangeEnd < dateRangeStart) {
      dateRangeStart = dateRangeEnd;
      startInput.value = dateRangeStart;
    }
    timeFilter = (dateRangeStart || dateRangeEnd) ? "range" : null;
    updateDateRangeDisplay();
    applyExplorerFilter();
  });
}

function updateDateRangeDisplay() {
  const display = document.getElementById("date-range-display");
  if (!display) return;
  
  if (dateRangeStart && dateRangeEnd) {
    const start = new Date(dateRangeStart);
    const end = new Date(dateRangeEnd);
    const days = Math.round((end - start) / (1000 * 60 * 60 * 24)) + 1;
    
    const formatDate = (d) => d.toLocaleDateString("fr-CH", { day: "2-digit", month: "short" });
    
    if (dateRangeStart === dateRangeEnd) {
      display.textContent = `📍 ${formatDate(start)} (1 jour)`;
    } else {
      display.textContent = `📍 ${formatDate(start)} → ${formatDate(end)} (${days} jours)`;
    }
  } else {
    display.textContent = "";
  }
}

function renderSelectedTags() {
  const box = document.getElementById("explorer-selected");
  if (!box) return;
  box.innerHTML = "";

  selectedCategories.forEach(cat => {
    const safe = escapeHtml(cat);
    box.innerHTML += `
      <div style="
        background:#00ffc3;
        color:#000;
        padding:4px 10px;
        border-radius:999px;
        font-size:12px;
        display:flex;
        align-items:center;
        gap:6px;
      ">
        ${safe}
        <span style="cursor:pointer;font-weight:700;" onclick="removeSelectedCategory('${safe}')">×</span>
      </div>
    `;
  });
}

function removeSelectedCategory(cat) {
  selectedCategories = selectedCategories.filter(c => c !== cat);
  
  // Synchroniser avec les checkboxes dans l'explorateur
  renderExplorer(); // Re-render pour décocher les cases
  renderSelectedTags(); // Mettre à jour les tags
  
  applyExplorerFilter();
}

function resetExplorerFilter() {
  selectedCategories = [];
  explorerPath = [];
  timeFilter = null;
  dateRangeStart = null;
  dateRangeEnd = null;
  selectedDates = [];
  filteredData = null; // null = afficher TOUS les points
  renderExplorer();
  // IMPORTANT : refreshMarkers et refreshListView utilisent getActiveData() qui retourne filteredData || getCurrentData()
  // Donc si filteredData est null, tous les points sont affichés
  refreshMarkers();
  refreshListView();
  showNotification("🔄 Filtres réinitialisés - Tous les points affichés", "info");
}

function buildExplorerColumns() {
  const colBox = document.getElementById("explorer-columns");
  if (!colBox || !explorerTree) return;
  colBox.innerHTML = "";

  let node = explorerTree;
  buildColumn(colBox, node, 0);

  explorerPath.forEach((step, i) => {
    node = findNode(node, step);
    if (node) buildColumn(colBox, node, i + 1);
  });
}

function findNode(obj, name) {
  if (!obj) return null;
  if (Array.isArray(obj)) return null;

  for (const key in obj) {
    if (key === name) return obj[key];
  }
  return null;
}

function buildColumn(colBox, node, level) {
  const div = document.createElement("div");
  div.style.minWidth = "200px";
  div.style.maxWidth = "200px";
  div.style.background = "rgba(2,6,23,0.85)";
  div.style.border = "1px solid rgba(0,255,195,0.25)";
  div.style.borderRadius = "10px";
  div.style.padding = "8px";
  div.style.color = "var(--ui-text-main)";
  div.style.fontSize = "13px";
  div.style.maxHeight = "280px";
  div.style.overflowY = "auto";

  let html = "";

  if (Array.isArray(node)) {
    // Feuilles (catégories finales)
    node.forEach(item => {
      const safe = escapeHtml(item);
      const isChecked = selectedCategories.includes(item);
      html += `
        <label style="display:flex;align-items:center;gap:8px;padding:6px;cursor:pointer;border-radius:6px;transition:background 0.15s;"
             onmouseover="this.style.background='rgba(0,255,195,0.12)'"
               onmouseout="this.style.background='transparent'">
          <input type="checkbox" 
                 ${isChecked ? 'checked' : ''} 
                 onchange="toggleCategory('${safe}')"
                 style="width:16px;height:16px;accent-color:#00ffc3;cursor:pointer;">
          <span style="flex:1;font-size:12px;">${safe}</span>
        </label>
      `;
    });
  } else {
    // Dossiers (catégories avec sous-catégories)
    for (const key in node) {
      const safeKey = escapeHtml(key);
      const isChecked = selectedCategories.includes(key);
      const hasChildren = node[key] && (Array.isArray(node[key]) ? node[key].length > 0 : Object.keys(node[key]).length > 0);
      
      html += `
        <div style="display:flex;align-items:center;gap:6px;padding:6px;border-radius:6px;transition:background 0.15s;"
             onmouseover="this.style.background='rgba(0,255,195,0.12)'"
             onmouseout="this.style.background='transparent'">
          <input type="checkbox" 
                 ${isChecked ? 'checked' : ''} 
                 onchange="toggleCategory('${safeKey}')"
                 onclick="event.stopPropagation()"
                 style="width:16px;height:16px;accent-color:#00ffc3;cursor:pointer;">
          <div style="flex:1;display:flex;align-items:center;justify-content:space-between;cursor:pointer;"
             onclick="openNextLevel('${safeKey}', ${level})">
            <span style="font-size:12px;font-weight:500;">📁 ${safeKey}</span>
            ${hasChildren ? '<span style="color:#00ffc3;font-size:14px;">›</span>' : ''}
          </div>
        </div>
      `;
    }
  }

  div.innerHTML = html;
  colBox.appendChild(div);
}

// Toggle une catégorie (cocher/décocher)
function toggleCategory(cat) {
  if (selectedCategories.includes(cat)) {
    selectedCategories = selectedCategories.filter(c => c !== cat);
  } else {
    selectedCategories.push(cat);
  }
  renderSelectedTags();
  applyExplorerFilter();
}

function openNextLevel(key, level) {
  explorerPath = explorerPath.slice(0, level);
  explorerPath.push(key);
  renderExplorer();
  
  // Scroll automatique vers la droite pour suivre la navigation
  setTimeout(() => {
    const colBox = document.getElementById("explorer-columns");
    if (colBox) {
      colBox.scrollTo({
        left: colBox.scrollWidth,
        behavior: 'smooth'
      });
    }
  }, 100);
}

function selectLeafCategory(cat) {
  if (!selectedCategories.includes(cat)) {
    selectedCategories.push(cat);
  }
  applyExplorerFilter();
}

function setTimeFilter(mode) {
  // Cette fonction est gardée pour compatibilité mais on utilise maintenant toggleDateFilter
  timeFilter = mode;
  applyExplorerFilter();
}

function applyExplorerFilter() {
  renderSelectedTags();

  const base = getCurrentData();
  const lowerCats = selectedCategories.map(c => c.toLowerCase());

  // Si aucun filtre actif, afficher tout
  if (lowerCats.length === 0 && !timeFilter && !dateRangeStart && !dateRangeEnd && selectedDates.length === 0) {
    filteredData = null;
    refreshMarkers();
    refreshListView();
    return;
  }

  // Construire la liste complète des catégories autorisées (incluant descendants)
  let allowedCategories = new Set();
  
  if (lowerCats.length > 0 && explorerTree) {
    lowerCats.forEach(selectedCat => {
      // Ajouter la catégorie sélectionnée elle-même
      allowedCategories.add(selectedCat);
      
      // Ajouter tous les descendants de cette catégorie
      const descendants = findCategoryDescendants(selectedCat, explorerTree);
      descendants.forEach(d => allowedCategories.add(d));
    });
  }

  filteredData = base.filter(item => {
    // filtre catégories
    let catOk = true;
    if (lowerCats.length > 0) {
      const itemCats = (item.categories || []).map(c => c.toLowerCase());
      const itemMainCat = (item.mainCategory || "").toLowerCase();
      
      // Vérifier si la catégorie de l'item est dans les catégories autorisées
      catOk = itemCats.some(cat => allowedCategories.has(cat)) || 
              allowedCategories.has(itemMainCat);
    }

    // filtre dates (events uniquement)
    let dateOk = true;
    if (item.type === "event") {
      dateOk = eventMatchesTimeFilter(item);
    }

    return catOk && dateOk;
  });

  console.log(`Filtre: ${selectedCategories.join(', ')} → ${filteredData.length} résultats`);
  console.log('Catégories autorisées:', Array.from(allowedCategories));

  refreshMarkers();
  refreshListView();
}

// Trouve tous les descendants d'une catégorie dans l'arbre
function findCategoryDescendants(targetCat, tree) {
  const results = new Set();
  
  function searchNode(node, found = false) {
    if (!node) return;
    
    if (Array.isArray(node)) {
      // C'est une liste de feuilles
      if (found) {
        node.forEach(item => {
          const name = (typeof item === 'string' ? item : item.name || '').toLowerCase();
          if (name) results.add(name);
        });
      }
      return;
    }
    
    for (const key in node) {
      const keyLower = key.toLowerCase();
      
      if (keyLower === targetCat || found) {
        // On a trouvé la catégorie cible ou on est déjà dans ses descendants
        results.add(keyLower);
        searchNode(node[key], true);
      } else {
        // Continuer la recherche
        searchNode(node[key], false);
      }
    }
  }
  
  searchNode(tree);
  return results;
}

function eventMatchesTimeFilter(ev) {
  // Si aucun filtre de date actif, tout passe
  if (selectedDates.length === 0 && !dateRangeStart && !dateRangeEnd) return true;
  if (!ev.startDate) return true;

  const evStart = new Date(ev.startDate);
  if (isNaN(evStart.getTime())) return true;

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // Filtre par plage de dates personnalisée
  if (dateRangeStart || dateRangeEnd) {
    const evDate = new Date(ev.startDate);
    evDate.setHours(0, 0, 0, 0);
    
    if (dateRangeStart && dateRangeEnd) {
      const rangeStart = new Date(dateRangeStart + "T00:00:00");
      const rangeEnd = new Date(dateRangeEnd + "T23:59:59");
      if (evDate >= rangeStart && evDate <= rangeEnd) return true;
    } else if (dateRangeStart) {
      const rangeStart = new Date(dateRangeStart + "T00:00:00");
      if (evDate >= rangeStart) return true;
    } else if (dateRangeEnd) {
      const rangeEnd = new Date(dateRangeEnd + "T23:59:59");
      if (evDate <= rangeEnd) return true;
    }
    // Si seulement plage active et pas de match, retourner false
    if (selectedDates.length === 0) return false;
  }

  // Vérifier les filtres de dates cumulés (OR entre eux)
  if (selectedDates.length > 0) {
    return selectedDates.some(filter => matchesDateFilter(evStart, filter, today));
  }

  return true;
}

// Vérifie si une date correspond à un filtre spécifique
function matchesDateFilter(evStart, filter, today) {
  if (filter === "today") {
    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);
    return evStart >= today && evStart < tomorrow;
  }

  if (filter === "tomorrow") {
    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);
    const after = new Date(tomorrow);
    after.setDate(tomorrow.getDate() + 1);
    return evStart >= tomorrow && evStart < after;
  }

  if (filter === "weekend") {
    const wd = today.getDay();
    const sat = new Date(today);
    sat.setDate(today.getDate() + ((6 - wd + 7) % 7));
    sat.setHours(0, 0, 0, 0);
    const mon = new Date(sat);
    mon.setDate(sat.getDate() + 2);
    mon.setHours(0, 0, 0, 0);
    return evStart >= sat && evStart < mon;
  }

  if (filter === "week") {
    const js = today.getDay() || 7;
    const monday = new Date(today);
    monday.setDate(today.getDate() - (js - 1));
    monday.setHours(0, 0, 0, 0);
    const nextMonday = new Date(monday);
    nextMonday.setDate(monday.getDate() + 7);
    return evStart >= monday && evStart < nextMonday;
  }

  if (filter === "month") {
    const m0 = new Date(today.getFullYear(), today.getMonth(), 1);
    const m1 = new Date(today.getFullYear(), today.getMonth() + 1, 1);
    return evStart >= m0 && evStart < m1;
  }

  return false;
}

// ============================================
// UI : Recherche ville, changement mode, thème
// ============================================

// Variables pour l'autocomplétion
let autocompleteTimeout = null;
let currentSuggestions = [];
let selectedSuggestionIndex = -1;

// Fonction pour créer le dropdown d'autocomplétion
function createAutocompleteDropdown() {
  const container = document.getElementById("map-search-container");
  if (!container) return null;
  
  let dropdown = document.getElementById("city-autocomplete-dropdown");
  if (!dropdown) {
    dropdown = document.createElement("div");
    dropdown.id = "city-autocomplete-dropdown";
    dropdown.style.cssText = `
      position: absolute;
      top: 100%;
      left: 0;
      right: 0;
      margin-top: 4px;
      background: rgba(15, 23, 42, 0.98);
      border: 1px solid var(--ui-card-border);
      border-radius: 12px;
      max-height: 300px;
      overflow-y: auto;
      z-index: 1000;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
      display: none;
    `;
    container.style.position = "relative";
    container.appendChild(dropdown);
  }
  return dropdown;
}

// Fonction pour rechercher des suggestions de villes
async function searchCitySuggestions(query) {
  if (!query || query.length < 2) {
    const dropdown = document.getElementById("city-autocomplete-dropdown");
    if (dropdown) dropdown.style.display = "none";
    return;
  }
  
  try {
    const encodedQuery = encodeURIComponent(query);
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?q=${encodedQuery}&format=json&limit=8&addressdetails=1&accept-language=${currentLanguage}`,
      {
        headers: {
          'User-Agent': 'MapEventAI/1.0'
        }
      }
    );
    
    if (!response.ok) throw new Error("Erreur API");
    
    const data = await response.json();
    currentSuggestions = data;
    displaySuggestions(data);
  } catch (error) {
    console.error("Erreur autocomplétion:", error);
    const dropdown = document.getElementById("city-autocomplete-dropdown");
    if (dropdown) dropdown.style.display = "none";
  }
}

// Fonction pour afficher les suggestions
function displaySuggestions(suggestions) {
  const dropdown = createAutocompleteDropdown();
  if (!dropdown) return;
  
  if (suggestions.length === 0) {
    dropdown.style.display = "none";
    return;
  }
  
  dropdown.innerHTML = suggestions.map((suggestion, index) => {
    const displayName = suggestion.display_name.split(',').slice(0, 3).join(','); // Limiter à 3 parties
    return `
      <div 
        class="suggestion-item" 
        data-index="${index}"
        onclick="selectSuggestion(${index})"
        onmouseover="highlightSuggestion(${index})"
        style="
          padding: 12px 16px;
          cursor: pointer;
          border-bottom: 1px solid rgba(255,255,255,0.05);
          transition: all 0.2s;
          ${index === selectedSuggestionIndex ? 'background: rgba(0,255,195,0.15);' : ''}
        "
        onmouseenter="this.style.background='rgba(0,255,195,0.1)'"
        onmouseleave="this.style.background='${index === selectedSuggestionIndex ? 'rgba(0,255,195,0.15)' : 'transparent'}'"
      >
        <div style="font-size: 14px; color: #fff; font-weight: 500; margin-bottom: 4px;">
          ${escapeHtml(displayName)}
        </div>
        <div style="font-size: 11px; color: var(--ui-text-muted);">
          ${suggestion.address?.country || ''} ${suggestion.address?.state ? '• ' + suggestion.address.state : ''}
        </div>
      </div>
    `;
  }).join('');
  
  dropdown.style.display = "block";
  selectedSuggestionIndex = -1;
}

// Fonction pour sélectionner une suggestion
function selectSuggestion(index) {
  if (index < 0 || index >= currentSuggestions.length) return;
  
  const suggestion = currentSuggestions[index];
  const searchInput = document.getElementById("map-search-input");
  
  if (searchInput) {
    searchInput.value = suggestion.display_name.split(',')[0]; // Nom de la ville
  }
  
  // Fermer le dropdown
  const dropdown = document.getElementById("city-autocomplete-dropdown");
  if (dropdown) dropdown.style.display = "none";
  
  // Rechercher la ville
  onSearchCity(suggestion.display_name.split(',')[0]);
}

// Fonction pour mettre en surbrillance une suggestion (navigation clavier)
function highlightSuggestion(index) {
  selectedSuggestionIndex = index;
  const items = document.querySelectorAll('.suggestion-item');
  items.forEach((item, i) => {
    item.style.background = i === index ? 'rgba(0,255,195,0.15)' : 'transparent';
  });
}

function initUI() {
  const search = document.getElementById("map-search-input");
  if (search) {
    // Autocomplétion lors de la saisie
    search.addEventListener("input", e => {
      const query = e.target.value.trim();
      
      // Annuler le timeout précédent
      if (autocompleteTimeout) {
        clearTimeout(autocompleteTimeout);
      }
      
      // Attendre 300ms avant de rechercher (debounce)
      autocompleteTimeout = setTimeout(() => {
        searchCitySuggestions(query);
      }, 300);
    });
    
    // Navigation clavier dans les suggestions
    search.addEventListener("keydown", e => {
      const dropdown = document.getElementById("city-autocomplete-dropdown");
      const isVisible = dropdown && dropdown.style.display !== "none";
      
      if (e.key === "ArrowDown" && isVisible) {
        e.preventDefault();
        selectedSuggestionIndex = Math.min(selectedSuggestionIndex + 1, currentSuggestions.length - 1);
        highlightSuggestion(selectedSuggestionIndex);
        const items = dropdown.querySelectorAll('.suggestion-item');
        if (items[selectedSuggestionIndex]) {
          items[selectedSuggestionIndex].scrollIntoView({ block: 'nearest' });
        }
      } else if (e.key === "ArrowUp" && isVisible) {
        e.preventDefault();
        selectedSuggestionIndex = Math.max(selectedSuggestionIndex - 1, -1);
        if (selectedSuggestionIndex >= 0) {
          highlightSuggestion(selectedSuggestionIndex);
          const items = dropdown.querySelectorAll('.suggestion-item');
          if (items[selectedSuggestionIndex]) {
            items[selectedSuggestionIndex].scrollIntoView({ block: 'nearest' });
          }
        }
      } else if (e.key === "Enter") {
        if (isVisible && selectedSuggestionIndex >= 0) {
          e.preventDefault();
          selectSuggestion(selectedSuggestionIndex);
        } else {
          onSearchCity(search.value);
        }
      } else if (e.key === "Escape") {
        if (dropdown) dropdown.style.display = "none";
      }
    });
    
    // Fermer le dropdown si on clique ailleurs
    document.addEventListener("click", (e) => {
      const dropdown = document.getElementById("city-autocomplete-dropdown");
      const container = document.getElementById("map-search-container");
      if (dropdown && container && !container.contains(e.target)) {
        dropdown.style.display = "none";
      }
    });
  }
}

function switchMode(mode) {
  if (!["event", "booking", "service"].includes(mode)) return;
  
  console.log(`🔄 Changement de mode : ${currentMode} → ${mode}`);
  
  // FERMER LE FILTRE SI OUVERT (l'utilisateur devra le rouvrir)
  const panel = document.getElementById("left-panel");
  if (panel && panel.style.display === "block") {
    panel.style.display = "none";
    explorerOpen = false;
    console.log(`🔒 Filtre fermé automatiquement lors du changement de mode`);
  }
  
  // SUPPRIMER TOUS LES MARQUEURS AVANT DE CHANGER DE MODE
  if (markersLayer) {
    markersLayer.clearLayers();
    markerMap = {};
    console.log(`🗑️ Tous les marqueurs supprimés`);
  }
  
  currentMode = mode;
  
  // FORCER l'affichage de TOUS les points (pas de filtre) - CRITIQUE !
  filteredData = null;
  selectedCategories = [];
  timeFilter = null;
  exactDateStr = null;
  dateRangeStart = null;
  dateRangeEnd = null;
  selectedDates = [];

  document.querySelectorAll(".mode-btn").forEach(btn => {
    const txt = btn.textContent.trim().toLowerCase();
    const key =
      txt.includes("event") ? "event" :
      txt.includes("booking") ? "booking" :
      txt.includes("service") ? "service" : "";
    btn.classList.toggle("active", key === mode);
  });

  // S'assurer que les points sont générés pour le nouveau mode
  ensureDemoPoints();
  
  // FORCER l'affichage immédiat - PAS DE FILTRE
  filteredData = null; // S'assurer qu'on affiche TOUS les points
  selectedCategories = []; // Réinitialiser les catégories
  
  // Rafraîchir les marqueurs et la liste IMMÉDIATEMENT
  const data = getActiveData();
  console.log(`📊 Données disponibles pour mode ${mode}: ${data.length} items (filteredData: ${filteredData}, eventsData: ${eventsData.length}, bookingsData: ${bookingsData.length}, servicesData: ${servicesData.length})`);
  
  // Afficher immédiatement
  refreshMarkers();
  refreshListView();

  // Vérifier après un court délai si les points sont bien affichés
  setTimeout(() => {
    const dataAfter = getActiveData();
    if (dataAfter && dataAfter.length > 0) {
      console.log(`✅ Mode changé : ${mode} - ${dataAfter.length} points affichés`);
    } else {
      console.warn(`⚠️ Aucun point affiché pour le mode ${mode}, nouvelle tentative...`);
      ensureDemoPoints();
      filteredData = null;
      selectedCategories = [];
      refreshMarkers();
      refreshListView();
    }
  }, 100);
}

function toggleListView() {
  listViewOpen = !listViewOpen;
  console.log(`📋 Liste ${listViewOpen ? 'ouverte' : 'fermée'}`);
  if (selectedCityForSorting) {
    console.log(`📍 Ville sélectionnée pour tri: ${selectedCityForSorting.name} (lat:${selectedCityForSorting.lat}, lng:${selectedCityForSorting.lng})`);
  }
  refreshListView();
}

async function onSearchCity(query) {
  if (!query) return;
  const queryLower = query.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim();
  
  showNotification(`${window.t("searching")} "${query}"...`, "info");
  
  // 1. Chercher dans SWISS_CITIES (base de données locale)
  const cityMatch = SWISS_CITIES.find(city => {
    const cityName = city.name.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    return cityName.includes(queryLower) || queryLower.includes(cityName);
  });
  
  if (cityMatch) {
    map.setView([cityMatch.lat, cityMatch.lng], 12);
    showNotification(`📍 ${cityMatch.name} ${window.t("city_found")}`, "success");
    return;
  }
  
  // 2. Chercher dans les données actuelles
  const all = [...eventsData, ...bookingsData, ...servicesData];
  const found = all.find(it => {
    const cityName = (it.city || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    return cityName.includes(queryLower) || queryLower.includes(cityName);
  });
  
  if (found) {
    map.setView([found.lat, found.lng], 12);
    showNotification(`📍 ${found.city} ${window.t("city_found")}`, "success");
    return;
  }
  
  // 3. Recherche mondiale via Nominatim (OpenStreetMap) - GRATUIT et mondial
  try {
    const encodedQuery = encodeURIComponent(query);
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?q=${encodedQuery}&format=json&limit=1&addressdetails=1`,
      {
        headers: {
          'User-Agent': 'MapEventAI/1.0' // Requis par Nominatim
        }
      }
    );
    
    if (!response.ok) throw new Error("Erreur API");
    
    const data = await response.json();
    
    if (data && data.length > 0) {
      const result = data[0];
      const lat = parseFloat(result.lat);
      const lng = parseFloat(result.lon);
      const displayName = result.display_name.split(',')[0]; // Nom de la ville
      
      map.setView([lat, lng], 12);
      showNotification(`📍 ${displayName} ${window.t("city_found")}`, "success");
    } else {
      showNotification(`⚠️ ${window.t("city_not_found")} "${query}". ${window.t("try_again")}`, "warning");
    }
  } catch (error) {
    console.error("Erreur recherche ville:", error);
    showNotification(`⚠️ ${window.t("error")} ${window.t("try_again")}`, "error");
  }
}

// ============================================
// FORMULAIRE PUBLIER (inchangé)
// ============================================
function buildPublishFormHtml() {
  // Utiliser window.t() pour éviter les erreurs TDZ
  // NE JAMAIS créer de variable locale 't' - utiliser directement window.t() pour éviter toute TDZ
  const modeLabel = currentMode.charAt(0).toUpperCase() + currentMode.slice(1);
  const hasDates = currentMode === "event";

  const categoriesBlock = `
    <div style="margin-bottom:10px;">
      <label style="font-size:12px;font-weight:600;">${window.t("main_category")} *</label>
      <input id="pub-main-category" placeholder="${window.t("choose_category")}"
               style="width:100%;padding:6px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);font-size:13px;">
    </div>
  `;

  const datesBlock = hasDates
    ? `
      <div style="display:flex;gap:8px;margin-bottom:10px;">
        <div style="flex:1;">
          <label style="font-size:12px;font-weight:600;">${window.t("start")} *</label>
          <input type="datetime-local" id="pub-start" required style="width:100%;padding:6px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);">
        </div>
        <div style="flex:1;">
          <label style="font-size:12px;font-weight:600;">${window.t("end")} *</label>
          <input type="datetime-local" id="pub-end" required style="width:100%;padding:6px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);">
        </div>
      </div>
      
      <!-- RÉPÉTITIONS D'ÉVÉNEMENTS -->
      <div style="margin-bottom:12px;padding:10px;background:rgba(0,255,195,0.05);border:1px solid rgba(0,255,195,0.2);border-radius:10px;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
          <input type="checkbox" id="pub-repeat-enabled" onchange="toggleRepeatOptions()" style="width:18px;height:18px;accent-color:#00ffc3;cursor:pointer;">
          <label for="pub-repeat-enabled" style="font-size:12px;font-weight:600;color:#00ffc3;cursor:pointer;">🔄 Répéter cet événement</label>
        </div>
        
        <div id="pub-repeat-options" style="display:none;margin-top:10px;">
          <div style="margin-bottom:8px;">
            <label style="font-size:11px;font-weight:600;color:var(--ui-text-muted);margin-bottom:4px;display:block;">Fréquence</label>
            <select id="pub-repeat-frequency" onchange="updateRepeatPreview()" style="width:100%;padding:6px;border-radius:8px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:12px;cursor:pointer;">
              <option value="daily">Quotidien</option>
              <option value="weekly" selected>Hebdomadaire</option>
              <option value="biweekly">Bi-hebdomadaire</option>
              <option value="monthly">Mensuel</option>
              <option value="yearly">Annuel</option>
              <option value="custom">Personnalisé</option>
            </select>
          </div>
          
          <div id="pub-repeat-weekdays" style="margin-bottom:8px;">
            <label style="font-size:11px;font-weight:600;color:var(--ui-text-muted);margin-bottom:4px;display:block;">Jours de la semaine</label>
            <div style="display:flex;gap:4px;flex-wrap:wrap;">
              <label style="flex:1;min-width:40px;padding:6px;border-radius:6px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.5);text-align:center;font-size:11px;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.background='rgba(0,255,195,0.1)'" onmouseout="this.style.background='rgba(15,23,42,0.5)'">
                <input type="checkbox" value="0" class="repeat-weekday" onchange="updateRepeatPreview()" style="display:none;">
                <span>Lun</span>
              </label>
              <label style="flex:1;min-width:40px;padding:6px;border-radius:6px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.5);text-align:center;font-size:11px;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.background='rgba(0,255,195,0.1)'" onmouseout="this.style.background='rgba(15,23,42,0.5)'">
                <input type="checkbox" value="1" class="repeat-weekday" onchange="updateRepeatPreview()" style="display:none;">
                <span>Mar</span>
              </label>
              <label style="flex:1;min-width:40px;padding:6px;border-radius:6px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.5);text-align:center;font-size:11px;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.background='rgba(0,255,195,0.1)'" onmouseout="this.style.background='rgba(15,23,42,0.5)'">
                <input type="checkbox" value="2" class="repeat-weekday" onchange="updateRepeatPreview()" style="display:none;">
                <span>Mer</span>
              </label>
              <label style="flex:1;min-width:40px;padding:6px;border-radius:6px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.5);text-align:center;font-size:11px;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.background='rgba(0,255,195,0.1)'" onmouseout="this.style.background='rgba(15,23,42,0.5)'">
                <input type="checkbox" value="3" class="repeat-weekday" onchange="updateRepeatPreview()" style="display:none;">
                <span>Jeu</span>
              </label>
              <label style="flex:1;min-width:40px;padding:6px;border-radius:6px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.5);text-align:center;font-size:11px;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.background='rgba(0,255,195,0.1)'" onmouseout="this.style.background='rgba(15,23,42,0.5)'">
                <input type="checkbox" value="4" class="repeat-weekday" onchange="updateRepeatPreview()" style="display:none;">
                <span>Ven</span>
              </label>
              <label style="flex:1;min-width:40px;padding:6px;border-radius:6px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.5);text-align:center;font-size:11px;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.background='rgba(0,255,195,0.1)'" onmouseout="this.style.background='rgba(15,23,42,0.5)'">
                <input type="checkbox" value="5" class="repeat-weekday" onchange="updateRepeatPreview()" style="display:none;">
                <span>Sam</span>
              </label>
              <label style="flex:1;min-width:40px;padding:6px;border-radius:6px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.5);text-align:center;font-size:11px;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.background='rgba(0,255,195,0.1)'" onmouseout="this.style.background='rgba(15,23,42,0.5)'">
                <input type="checkbox" value="6" class="repeat-weekday" onchange="updateRepeatPreview()" style="display:none;">
                <span>Dim</span>
              </label>
            </div>
          </div>
          
          <div style="display:flex;gap:8px;margin-bottom:8px;">
            <div style="flex:1;">
              <label style="font-size:11px;font-weight:600;color:var(--ui-text-muted);margin-bottom:4px;display:block;">Répéter jusqu'au</label>
              <input type="date" id="pub-repeat-until" onchange="updateRepeatPreview()" style="width:100%;padding:6px;border-radius:8px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:12px;">
            </div>
            <div style="flex:1;">
              <label style="font-size:11px;font-weight:600;color:var(--ui-text-muted);margin-bottom:4px;display:block;">Ou nombre d'occurrences</label>
              <input type="number" id="pub-repeat-count" min="1" max="365" placeholder="Ex: 10" onchange="updateRepeatPreview()" style="width:100%;padding:6px;border-radius:8px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:12px;">
            </div>
          </div>
          
          <div id="pub-repeat-preview" style="padding:8px;background:rgba(0,255,195,0.1);border-radius:6px;font-size:11px;color:#00ffc3;min-height:20px;">
            <span style="opacity:0.6;">Aperçu des répétitions...</span>
          </div>
        </div>
      </div>
    `
    : "";

  const audioBlock =
    currentMode === "booking"
      ? `
      <div style="margin-bottom:10px;">
        <label style="font-size:12px;font-weight:600;">${window.t("sound_links")}</label>
        <textarea id="pub-audio" rows="2" placeholder="${window.t("paste_sound_links")}"
                  style="width:100%;padding:6px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);"></textarea>
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
    <div style="margin-top:6px;padding:8px;border-radius:10px;border:1px dashed var(--ui-card-border);font-size:12px;color:var(--ui-text-muted);">
      <div style="font-weight:600;margin-bottom:4px;">${window.t("visibility_choice")}</div>
      <ul style="padding-left:18px;margin:0;">
        <li><b>${window.t("standard_point")}</b></li>
        <li><b>${window.t("bronze_boost")}</b></li>
        <li><b>${window.t("silver_boost")}</b></li>
        <li><b>${window.t("platinum_boost")}</b></li>
      </ul>
    </div>
  `;

  return `
    <form onsubmit="return onSubmitPublishForm(event)">
      <h2 style="margin:0 0 10px;font-size:16px;">${window.t("publish_mode")} ${modeLabel}</h2>

      <div style="margin-bottom:10px;">
        <label style="font-size:12px;font-weight:600;">${window.t("title_name")} *</label>
        <input id="pub-title" required
               style="width:100%;padding:6px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);font-size:13px;">
      </div>

      ${categoriesBlock}
      ${datesBlock}

      <div style="margin-bottom:10px;">
        <label style="font-size:12px;font-weight:600;">${window.t("full_address")} *</label>
        <input id="pub-address" required
               style="width:100%;padding:6px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);font-size:13px;">
      </div>

      <div style="display:flex;gap:8px;margin-bottom:10px;">
        <div style="flex:1;">
          <label style="font-size:12px;font-weight:600;">${window.t("phone")}</label>
          <input id="pub-phone"
                 style="width:100%;padding:6px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);font-size:13px;">
        </div>
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
                 style="width:100%;padding:6px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);">
        </div>
      `
          : ""
      }

      <div style="margin-bottom:10px;">
        <label style="font-size:12px;font-weight:600;">${window.t("social_links")}</label>
        <textarea id="pub-social" rows="2" placeholder="Facebook, Instagram…"
                  style="width:100%;padding:6px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);"></textarea>
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

      <div style="margin-top:14px;text-align:right;">
        <button type="button" onclick="closePublishModal()" style="
          padding:6px 14px;border-radius:999px;background:transparent;border:1px solid var(--ui-card-border);color:var(--ui-text-main);cursor:pointer;">
          ${window.t("cancel")}
        </button>

        <button type="submit" style="
          padding:6px 14px;border-radius:999px;border:none;
          background:var(--btn-main-bg);color:var(--btn-main-text);font-weight:700;cursor:pointer;">
          ${window.t("publish_and_pay")}
        </button>
      </div>
    </form>
  `;
}

function openPublishModal() {
  const backdrop = document.getElementById("publish-modal-backdrop");
  const inner = document.getElementById("publish-modal-inner");
  inner.innerHTML = buildPublishFormHtml();
  backdrop.style.display = "flex";
  
  // Initialiser les gestionnaires d'événements pour les répétitions
  if (currentMode === "event") {
    setTimeout(() => {
      initRepeatHandlers();
      initMultipleImagesHandler();
    }, 100);
  }
}

// Fonction pour gérer les répétitions
function toggleRepeatOptions() {
  const checkbox = document.getElementById("pub-repeat-enabled");
  const options = document.getElementById("pub-repeat-options");
  if (checkbox && options) {
    options.style.display = checkbox.checked ? "block" : "none";
    if (checkbox.checked) {
      updateRepeatPreview();
    }
  }
}

function updateRepeatPreview() {
  const preview = document.getElementById("pub-repeat-preview");
  if (!preview) return;
  
  const frequency = document.getElementById("pub-repeat-frequency")?.value || "weekly";
  const until = document.getElementById("pub-repeat-until")?.value;
  const count = document.getElementById("pub-repeat-count")?.value;
  const weekdays = Array.from(document.querySelectorAll(".repeat-weekday:checked")).map(cb => parseInt(cb.value));
  
  let previewText = "";
  
  if (frequency === "weekly" && weekdays.length > 0) {
    const dayNames = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"];
    previewText = `Répétition hebdomadaire le${weekdays.length > 1 ? "s" : ""} ${weekdays.map(d => dayNames[d]).join(", ")}`;
  } else {
    const freqNames = {
      daily: "Quotidien",
      weekly: "Hebdomadaire",
      biweekly: "Bi-hebdomadaire",
      monthly: "Mensuel",
      yearly: "Annuel",
      custom: "Personnalisé"
    };
    previewText = `Répétition ${freqNames[frequency] || frequency}`;
  }
  
  if (until) {
    const untilDate = new Date(until);
    previewText += ` jusqu'au ${untilDate.toLocaleDateString("fr-FR")}`;
  } else if (count) {
    previewText += ` (${count} occurrence${count > 1 ? "s" : ""})`;
  }
  
  preview.innerHTML = `<span style="color:#00ffc3;">📅 ${previewText}</span>`;
}

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

function closePublishModal(e) {
  console.log('🚪 closePublishModal called', e?.type || 'direct call', e?.target?.id || 'no target');
  if (e && e.target && e.target.id !== "publish-modal-backdrop") {
    const modal = document.getElementById("publish-modal");
    const modalInner = document.getElementById("publish-modal-inner");
    // Ne ferme pas si on clique sur un élément dans la modal ou le modal inner
    if ((modal && modal.contains(e.target)) || (modalInner && modalInner.contains(e.target))) return;
  }
  document.getElementById("publish-modal-backdrop").style.display = "none";
  console.log('🚪 Modal closed - backdrop display set to none');
}

async function onSubmitPublishForm(e) {
  e.preventDefault();
  
  // Vérifier que l'utilisateur est connecté
  if (!currentUser.isLoggedIn) {
    showNotification("⚠️ Vous devez être connecté pour publier", "warning");
    openLoginModal();
    return false;
  }
  
  // Récupérer les données du formulaire
  const title = document.getElementById("pub-title")?.value.trim();
  const mainCategory = document.getElementById("pub-main-category")?.value.trim();
  const address = document.getElementById("pub-address")?.value.trim();
  const phone = document.getElementById("pub-phone")?.value.trim();
  const email = document.getElementById("pub-email")?.value.trim();
  const description = document.getElementById("pub-description")?.value.trim();
  const ticketUrl = document.getElementById("pub-ticket")?.value.trim();
  const socialLinks = document.getElementById("pub-social")?.value.trim();
  const videoLinks = document.getElementById("pub-videos")?.value.trim();
  
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
  
  // Géocoder l'adresse
  showNotification("🔍 Recherche de l'adresse...", "info");
  
  let lat = null, lng = null, city = "";
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
  
  // Créer l'objet selon le mode
  const newId = Date.now();
  const now = new Date().toISOString();
  
  let newItem = {
    id: newId,
    title: title,
    name: title,
    categories: [mainCategory],
    mainCategory: mainCategory,
    address: address,
    city: city,
    lat: lat,
    lng: lng,
    description: description,
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
    
    // RÉPÉTITIONS
    if (repeatEnabled) {
      newItem.repeat = {
        enabled: true,
        frequency: repeatFrequency,
        until: repeatUntil,
        count: repeatCount ? parseInt(repeatCount) : null,
        weekdays: repeatWeekdays.length > 0 ? repeatWeekdays : null
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
    await fetch(`${API_BASE_URL}/${currentMode}s`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...newItem,
        userId: currentUser.id
      })
    });
  } catch (error) {
    console.error('Erreur sauvegarde backend:', error);
    // Continuer même si le backend échoue (sauvegarde locale)
  }
  
  // Fermer le modal et rafraîchir
  closePublishModal();
  refreshMarkers();
  refreshListView();
  
  // Centrer la carte sur le nouveau point
  if (map && lat && lng) {
    map.setView([lat, lng], 14);
  }
  
  // Message de succès
  if (boost !== 'basic') {
    showNotification(`✅ ${currentMode === 'event' ? 'Événement' : currentMode === 'booking' ? 'Booking' : 'Service'} publié avec boost ${boost} ! Redirection vers le paiement...`, "success");
    // Ici, vous pourriez rediriger vers Stripe pour le paiement du boost
    setTimeout(() => {
      openSubscriptionModal();
    }, 2000);
  } else {
    showNotification(`✅ ${currentMode === 'event' ? 'Événement' : currentMode === 'booking' ? 'Booking' : 'Service'} publié avec succès !`, "success");
  }
  
  return false;
}

// ============================================
// THÈMES UI + MAP
// ============================================
function cycleUITheme() {
  uiThemeIndex = (uiThemeIndex + 1) % UI_THEMES.length;
  applyUITheme(uiThemeIndex);
}

function applyUITheme(i) {
  const t = UI_THEMES[i];
  const root = document.documentElement;

  root.style.setProperty("--ui-body-bg", t.bodyBg);
  root.style.setProperty("--ui-topbar-bg", t.topbarBg);
  root.style.setProperty("--ui-card-bg", t.cardBg);
  root.style.setProperty("--ui-card-border", t.cardBorder);
  root.style.setProperty("--ui-text-main", t.textMain);
  root.style.setProperty("--ui-text-muted", t.textMuted);
  root.style.setProperty("--btn-main-bg", t.btnMainBg);
  root.style.setProperty("--btn-main-text", t.btnMainText);
  root.style.setProperty("--btn-main-shadow", t.btnMainShadow);
  root.style.setProperty("--btn-alt-bg", t.btnAltBg);
  root.style.setProperty("--btn-alt-text", t.btnAltText);
  root.style.setProperty("--pill-border", t.pillBorder);

  const logoMain = document.querySelector("#logo-main .text");
  const logoIcon = document.querySelector("#logo-main .icon");
  const tagline = document.querySelector("#logo-tagline");

  if (logoMain) logoMain.style.color = t.logoColor;
  if (logoIcon) logoIcon.style.color = t.logoColor;
  if (tagline) tagline.style.color = t.taglineColor;
  
  // NE PAS modifier les couleurs des textes dans les blocs de titre (comme demandé)
  // Les textes dans les blocs de droite gardent leur couleur originale
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

// Générer des événements d'urgence si aucune donnée n'est disponible
function generateEmergencyEvents() {
  console.log(`🚨 Génération d'urgence d'événements de base...`);
  const emergencyCities = SWISS_CITIES && SWISS_CITIES.length > 0 ? [SWISS_CITIES[0]] : 
                         FRENCH_CITIES && FRENCH_CITIES.length > 0 ? [FRENCH_CITIES[0]] : 
                         [{ name: "Lausanne", lat: 46.5197, lng: 6.6323, canton: "VD" }];
  
  if (emergencyCities.length === 0) {
    console.error("❌ Impossible de générer des événements d'urgence : aucune ville disponible");
    return;
  }
  
  const emergencyCategories = ["Techno", "House", "Festival", "Rock", "Jazz"];
  const emergencyTitles = ["Événement Test", "Soirée Musicale", "Festival Local", "Concert", "Rave Party"];
  
  for (let i = 0; i < 10; i++) {
    const city = emergencyCities[i % emergencyCities.length];
    const category = emergencyCategories[i % emergencyCategories.length];
    const title = `${emergencyTitles[i % emergencyTitles.length]} @ ${city.name}`;
    const daysFromNow = i * 2;
    const startDate = generateRandomDate(daysFromNow);
    const endDate = generateRandomDate(daysFromNow, 4);
    
    eventsData.push({
      id: 10000 + i,
      type: "event",
      title: title,
      description: "Événement généré automatiquement pour assurer le fonctionnement du site.",
      status: "OK",
      startDate: startDate,
      endDate: endDate,
      city: city.name,
      canton: city.canton || city.region,
      country: city.canton ? "CH" : "FR",
      address: `Centre-ville, ${city.name}`,
      lat: city.lat + (Math.random() - 0.5) * 0.05,
      lng: city.lng + (Math.random() - 0.5) * 0.05,
      categories: [category],
      mainCategory: category,
      categoryImage: null,
      boost: "basic",
      imageUrl: null,
      sourceUrl: "https://example.com",
      isAI: true,
      pricingMode: "Gratuit",
      likes: Math.floor(Math.random() * 50),
      comments: Math.floor(Math.random() * 10),
      participants: Math.floor(Math.random() * 100),
      verified: false,
      rating: (3.5 + Math.random() * 1.5).toFixed(1)
    });
  }
  
  console.log(`✅ ${eventsData.length} événements d'urgence générés`);
}

function ensureDemoPoints() {
  // Nettoyer les événements passés MAIS garder au moins quelques événements futurs
  const now = new Date();
  const beforeCount = eventsData.length;
  const futureEvents = eventsData.filter(ev => {
    if (!ev.endDate) return true;
    return new Date(ev.endDate) > now;
  });
  
  // Si on a moins de 10 événements futurs, ne pas filtrer pour éviter de tout supprimer
  if (futureEvents.length < 10 && eventsData.length > 0) {
    console.log(`⚠️ Seulement ${futureEvents.length} événements futurs, conservation de tous les événements`);
    // Ne pas filtrer si on a trop peu d'événements
  } else {
    eventsData = futureEvents;
  }
  
  const afterFilterCount = eventsData.length;
  console.log(`🔍 ensureDemoPoints() - Avant: ${beforeCount}, Après filtrage: ${afterFilterCount}, Cible: 600`);

  // Extraire TOUTES les sous-catégories les plus profondes de l'arbre Events
  let deepestEventCategories = [];
  if (EVENTS_TREE) {
    deepestEventCategories = extractDeepestCategories(EVENTS_TREE);
  }
  
  // Si l'arbre n'est pas encore chargé ou vide, utiliser des catégories de base
  if (deepestEventCategories.length === 0) {
    deepestEventCategories = [
      "Acid Techno", "Minimal Techno", "Hard Techno", "Melodic Techno",
      "Deep House", "Tech House", "Progressive House", "Afro House",
      "Psytrance", "Full On", "Goa", "Progressive Psy", "Dark Psy", "Forest", "Hi-Tech", "Uplifting Trance",
      "Neurofunk", "Jungle", "Liquid DnB", "Jump Up",
      "Dubstep", "Riddim", "Future Bass",
      "Hardstyle", "Hardcore", "Gabber",
      "Ambient", "Chillout", "Lofi",
      "Rap", "Trap", "Drill", "Hip-Hop", "RnB", "Afrobeats",
      "Indie Rock", "Alternative Rock", "Punk Rock",
      "Heavy Metal", "Thrash Metal", "Metalcore",
      "Jazz", "Soul", "Funk", "Blues",
      "Reggae", "Dub", "Ska", "Latin", "Balkan",
      "Pop", "Indie Pop", "Electro Pop",
      "Festival musique", "Open Air", "Street Parade",
      "Marché", "Brocante", "Foire",
      "Cinéma", "Théâtre", "Exposition",
      "Sport", "Course à pied", "Cyclisme"
    ];
  }
  
  const boosts = ["basic", "basic", "basic", "basic", "bronze", "bronze", "silver", "gold", "platinum"];
  const statuses = ["OK", "OK", "OK", "OK", "OK", "OK", "OK", "COMPLET", "REPORTÉ"];

  // Utiliser ALL_CITIES ou créer depuis SWISS_CITIES et FRENCH_CITIES
  const citiesToUse = ALL_CITIES && ALL_CITIES.length > 0 ? ALL_CITIES : [...(SWISS_CITIES || []), ...(FRENCH_CITIES || [])];
  if (!citiesToUse || citiesToUse.length === 0) {
    console.error("❌ Aucune ville disponible ! Impossible de générer des événements.");
    // Générer des événements d'urgence avec une ville par défaut
    generateEmergencyEvents();
    return;
  }
  
  // Générer au moins 1 point par pays (CH et FR)
  const swissCities = SWISS_CITIES || [];
  const frenchCities = FRENCH_CITIES || [];
  const countries = [
    { code: "CH", cities: swissCities },
    { code: "FR", cities: frenchCities }
  ];
  
  // S'assurer qu'on a au moins 1 point par pays
  countries.forEach(({ code, cities }) => {
    if (cities && cities.length > 0) {
      const city = cities[0]; // Prendre la première ville de chaque pays
      const id = 1000 + eventsData.length;
      const deepCat = deepestEventCategories[id % deepestEventCategories.length];
      const boost = boosts[Math.floor(Math.random() * boosts.length)];
      const status = statuses[Math.floor(Math.random() * statuses.length)];
      
      // Mapping amélioré des titres
      let parentCat = "Festival";
      let titlePrefix = "";
      if (deepCat.includes("Techno")) parentCat = "Techno";
      else if (deepCat.includes("House")) parentCat = "House";
      else if (deepCat.includes("Trance") || deepCat.includes("Psy")) parentCat = "Trance";
      else if (deepCat.includes("DnB") || deepCat.includes("Drum")) parentCat = "DnB";
      else if (deepCat.includes("Rap") || deepCat.includes("Hip")) parentCat = "Rap";
      else if (deepCat.includes("Rock")) parentCat = "Rock";
      else if (deepCat.includes("Metal")) parentCat = "Metal";
      else if (deepCat.includes("Jazz") || deepCat.includes("Soul")) parentCat = "Jazz";
      else if (deepCat.includes("Festival") || deepCat.includes("Open")) parentCat = "Festival";
      else if (deepCat.includes("Marché") || deepCat.includes("Brocante")) parentCat = "Marché";
      else if (deepCat.includes("Cinéma")) parentCat = "Cinéma";
      else if (deepCat.includes("Théâtre")) parentCat = "Théâtre";
      else if (deepCat.includes("Sport")) parentCat = "Sport";
      
      const titles = EVENT_TITLES[parentCat] || EVENT_TITLES["Festival"];
      const baseTitle = titles[Math.floor(Math.random() * titles.length)];
      const title = titlePrefix ? `${titlePrefix}${baseTitle}` : baseTitle;
      const venue = VENUES[Math.floor(Math.random() * VENUES.length)];
      const desc = DESCRIPTIONS[Math.floor(Math.random() * DESCRIPTIONS.length)];
      
      const daysFromNow = Math.floor(Math.random() * 60);
      const startDate = generateRandomDate(daysFromNow);
      const endDate = generateRandomDate(daysFromNow, 4 + Math.floor(Math.random() * 4));
      
      const latOffset = (Math.random() - 0.5) * 0.05;
      const lngOffset = (Math.random() - 0.5) * 0.05;
      
      eventsData.push({
        id,
        type: "event",
        title: `${title} @ ${city.name}`,
        description: desc,
        status,
        startDate,
        endDate,
        city: city.name,
        canton: city.canton || city.region,
        country: code,
        address: `${venue}, ${Math.floor(Math.random() * 100) + 1} Rue du Centre, ${city.name}`,
        lat: city.lat + latOffset,
        lng: city.lng + lngOffset,
        categories: [deepCat],
        mainCategory: parentCat,
        categoryImage: null,
        boost,
        imageUrl: null,
        sourceUrl: "https://example.com",
        isAI: Math.random() > 0.7,
        pricingMode: Math.random() > 0.3 ? "Entrée payante" : "Gratuit",
        likes: Math.floor(Math.random() * 150),
        comments: Math.floor(Math.random() * 30),
        participants: Math.floor(Math.random() * 200),
        verified: Math.random() > 0.6,
        rating: (3.5 + Math.random() * 1.5).toFixed(1)
      });
    }
  });
  
  // S'assurer qu'on génère au moins quelques événements même si les conditions ne sont pas optimales
  const minEvents = 50; // Minimum d'événements à générer
  
  // Générer 600 événements avec sous-catégories profondes (Suisse + France)
  const targetCount = Math.max(600, minEvents);
  while (eventsData.length < targetCount) {
    const id = 1000 + eventsData.length;
    const city = citiesToUse[id % citiesToUse.length];
    
    // Vérifier que la ville est valide
    if (!city || !city.name || typeof city.lat !== 'number' || typeof city.lng !== 'number') {
      console.error(`❌ Ville invalide à l'index ${id % citiesToUse.length}:`, city);
      break;
    }
    // Utiliser une sous-catégorie profonde au lieu d'une catégorie générale
    const deepCat = deepestEventCategories[id % deepestEventCategories.length];
    const boost = boosts[Math.floor(Math.random() * boosts.length)];
    const status = statuses[Math.floor(Math.random() * statuses.length)];
    
    // Trouver une catégorie parente pour les titres - MAPPING AMÉLIORÉ
    let parentCat = "Festival";
    let titlePrefix = "";
    
    if (deepCat.includes("Acid Techno") || deepCat.includes("Minimal Techno") || deepCat.includes("Hard Techno") || deepCat.includes("Melodic Techno")) {
      parentCat = "Techno";
      titlePrefix = deepCat.includes("Acid") ? "Acid " : deepCat.includes("Minimal") ? "Minimal " : deepCat.includes("Hard") ? "Hard " : "Melodic ";
    } else if (deepCat.includes("Deep House") || deepCat.includes("Tech House") || deepCat.includes("Progressive House") || deepCat.includes("Afro House")) {
      parentCat = "House";
      titlePrefix = deepCat.includes("Deep") ? "Deep " : deepCat.includes("Tech") ? "Tech " : deepCat.includes("Progressive") ? "Progressive " : "Afro ";
    } else if (deepCat.includes("Psytrance") || deepCat.includes("Full On") || deepCat.includes("Goa") || deepCat.includes("Progressive Psy") || deepCat.includes("Dark Psy") || deepCat.includes("Forest") || deepCat.includes("Hi-Tech") || deepCat.includes("Uplifting Trance")) {
      parentCat = "Trance";
      titlePrefix = deepCat.includes("Psytrance") ? "Psytrance " : deepCat.includes("Full On") ? "Full On " : deepCat.includes("Goa") ? "Goa " : deepCat.includes("Progressive Psy") ? "Progressive Psy " : deepCat.includes("Dark Psy") ? "Dark Psy " : deepCat.includes("Forest") ? "Forest " : deepCat.includes("Hi-Tech") ? "Hi-Tech " : "Uplifting ";
    } else if (deepCat.includes("Neurofunk") || deepCat.includes("Jungle") || deepCat.includes("Liquid DnB") || deepCat.includes("Jump Up") || deepCat.includes("Drum & Bass")) {
      parentCat = "DnB";
      titlePrefix = deepCat.includes("Neurofunk") ? "Neurofunk " : deepCat.includes("Jungle") ? "Jungle " : deepCat.includes("Liquid") ? "Liquid " : deepCat.includes("Jump Up") ? "Jump Up " : "";
    } else if (deepCat.includes("Rap") || deepCat.includes("Trap") || deepCat.includes("Drill") || deepCat.includes("Hip-Hop") || deepCat.includes("RnB") || deepCat.includes("Afrobeats")) {
      parentCat = "Rap";
      titlePrefix = deepCat.includes("Trap") ? "Trap " : deepCat.includes("Drill") ? "Drill " : deepCat.includes("Hip-Hop") ? "Hip-Hop " : deepCat.includes("RnB") ? "RnB " : deepCat.includes("Afrobeats") ? "Afrobeats " : "";
    } else if (deepCat.includes("Rock") || deepCat.includes("Punk") || deepCat.includes("Indie Rock") || deepCat.includes("Alternative Rock")) {
      parentCat = "Rock";
      titlePrefix = deepCat.includes("Punk") ? "Punk " : deepCat.includes("Indie") ? "Indie " : deepCat.includes("Alternative") ? "Alternative " : "";
    } else if (deepCat.includes("Metal") || deepCat.includes("Heavy Metal") || deepCat.includes("Thrash Metal") || deepCat.includes("Metalcore")) {
      parentCat = "Metal";
      titlePrefix = deepCat.includes("Heavy") ? "Heavy " : deepCat.includes("Thrash") ? "Thrash " : deepCat.includes("Metalcore") ? "Metalcore " : "";
    } else if (deepCat.includes("Jazz") || deepCat.includes("Soul") || deepCat.includes("Funk") || deepCat.includes("Blues")) {
      parentCat = "Jazz";
      titlePrefix = deepCat.includes("Soul") ? "Soul " : deepCat.includes("Funk") ? "Funk " : deepCat.includes("Blues") ? "Blues " : "";
    } else if (deepCat.includes("Festival") || deepCat.includes("Open Air") || deepCat.includes("Street Parade")) {
      parentCat = "Festival";
    } else if (deepCat.includes("Marché") || deepCat.includes("Brocante") || deepCat.includes("Foire")) {
      parentCat = "Marché";
    } else if (deepCat.includes("Cinéma")) {
      parentCat = "Cinéma";
    } else if (deepCat.includes("Théâtre")) {
      parentCat = "Théâtre";
    } else if (deepCat.includes("Sport") || deepCat.includes("Course à pied") || deepCat.includes("Cyclisme")) {
      parentCat = "Sport";
      titlePrefix = deepCat.includes("Course") ? "Course " : deepCat.includes("Cyclisme") ? "Cyclisme " : "";
    }
    
    const titles = EVENT_TITLES[parentCat] || EVENT_TITLES["Festival"];
    const baseTitle = titles[Math.floor(Math.random() * titles.length)];
    // Ajouter le préfixe de sous-catégorie si disponible
    const title = titlePrefix ? `${titlePrefix}${baseTitle}` : baseTitle;
    const venue = VENUES[Math.floor(Math.random() * VENUES.length)];
    const desc = DESCRIPTIONS[Math.floor(Math.random() * DESCRIPTIONS.length)];
    
    // Dates variées : de aujourd'hui à +60 jours
    const daysFromNow = Math.floor(Math.random() * 60);
    const startDate = generateRandomDate(daysFromNow);
    const endDate = generateRandomDate(daysFromNow, 4 + Math.floor(Math.random() * 4));
    
    // Position avec variation aléatoire
    const latOffset = (Math.random() - 0.5) * 0.15;
    const lngOffset = (Math.random() - 0.5) * 0.15;

    eventsData.push({
      id,
      type: "event",
      title: `${title} @ ${city.name}`,
      description: desc,
      status,
      startDate,
      endDate,
      city: city.name,
      canton: city.canton || city.region, // Suisse = canton, France = region
      country: city.canton ? "CH" : "FR",
      address: `${venue}, ${Math.floor(Math.random() * 100) + 1} Rue du Centre, ${city.name}`,
      lat: city.lat + latOffset,
      lng: city.lng + lngOffset,
      categories: [deepCat], // SOUS-CATÉGORIE PROFONDE !
      mainCategory: parentCat, // Catégorie parente pour référence
      categoryImage: null,
      boost,
      imageUrl: null,
      sourceUrl: "https://example.com",
      isAI: Math.random() > 0.7,
      pricingMode: Math.random() > 0.3 ? "Entrée payante" : "Gratuit",
      likes: Math.floor(Math.random() * 150),
      comments: Math.floor(Math.random() * 30),
      participants: Math.floor(Math.random() * 200),
      verified: Math.random() > 0.6,
      rating: (3.5 + Math.random() * 1.5).toFixed(1) // Rating entre 3.5 et 5.0
    });
  }
  
  console.log(`✅ ensureDemoPoints() terminé - ${eventsData.length} événements générés`);
  
  // Attribuer des enchères Platinum aléatoires pour la démo
  eventsData.forEach(ev => {
    if (ev.boost === "platinum" && !ev.platinumBid) {
      ev.platinumBid = 15 + Math.floor(Math.random() * 40); // 15 à 55.-
    }
  });
  
  // Calculer les rangs Platinum par région
  calculatePlatinumRanks();

  // Générer 80 bookings avec sous-catégories profondes
  let deepestBookingCategories = [];
  if (BOOKING_TREE) {
    // BOOKING_TREE peut être l'objet complet avec "categories" ou directement l'arbre
    const treeToExtract = BOOKING_TREE.categories || BOOKING_TREE;
    deepestBookingCategories = extractDeepestCategories(treeToExtract);
  }
  
  // Si l'arbre n'est pas encore chargé, utiliser des catégories de base
  if (deepestBookingCategories.length === 0) {
    deepestBookingCategories = [
      "Acid Techno", "Minimal Techno", "Hard Techno", "Melodic Techno",
      "Deep House", "Tech House", "Progressive House", "Afro House",
      "Psytrance", "Full On", "Goa", "Progressive Psy", "Dark Psy", "Forest", "Hi-Tech", "Uplifting Trance",
      "Drum & Bass", "Neurofunk", "Jungle", "Liquid DnB",
      "Dubstep", "Riddim", "Future Bass",
      "Hardstyle", "Hardcore", "Gabber",
      "Ambient", "Chillout", "Lofi",
      "Rap", "Trap", "Drill", "Hip-Hop", "RnB", "Afrobeats",
      "Rock", "Indie Rock", "Punk Rock",
      "Metal", "Heavy Metal", "Metalcore",
      "Jazz", "Soul", "Funk", "Blues",
      "Reggae", "Dub", "Ska", "Latin", "Balkan",
      "Pop", "Indie Pop", "Electro Pop",
      "Synth Live", "Modular", "Chant / Vocal", "Guitare", "Percussions",
      "Danseurs", "Jongleurs", "Fire Show", "LED Show", "Acrobates",
      "VJ Software", "Mapping 3D", "Projections", "Laser Artist",
      "MC", "Animateur", "Speaker"
    ];
  }
  
  const bookingLevels = ["Débutant", "Semi-pro", "Pro", "Headliner", "International", "Non détecté"];
  const djNames = ["DJ ", "MC ", "The ", "", "DJ ", ""];
  const djSuffixes = ["Sound", "Beats", "Music", "Vibes", "Flow", "Mix", "Bass", "Groove", "Wave", "Pulse"];
  
  // Générer 200 bookings avec adresses précises à 1km
  const streetNames = ["Rue du Centre", "Avenue de la Gare", "Rue de la Poste", "Chemin des Vignes", "Route de la Plage", "Place du Marché", "Rue des Artisans", "Avenue des Sports", "Rue de la Musique", "Chemin des Artistes"];
  
  while (bookingsData.length < 200) {
    const id = 2000 + bookingsData.length;
    const city = SWISS_CITIES[id % SWISS_CITIES.length];
    // Utiliser une sous-catégorie profonde
    const deepCat = deepestBookingCategories[id % deepestBookingCategories.length];
    const boost = boosts[Math.floor(Math.random() * boosts.length)];
    const level = bookingLevels[Math.floor(Math.random() * bookingLevels.length)];
    const prefix = djNames[Math.floor(Math.random() * djNames.length)];
    const suffix = djSuffixes[Math.floor(Math.random() * djSuffixes.length)];
    const name = `${prefix}${["Alex", "Max", "Sam", "Leo", "Nico", "Marco", "Chris", "David", "Nina", "Sarah", "Lisa", "Emma", "Tom", "Lucas", "Noah", "Mia", "Sofia", "Luna"][id % 18]} ${suffix}`;
    
    // Trouver la catégorie parente
    const parentCat = deepCat.includes("Techno") ? "Techno" :
                     deepCat.includes("House") ? "House" :
                     deepCat.includes("Trance") || deepCat.includes("Psy") ? "Trance" :
                     deepCat.includes("DnB") || deepCat.includes("Drum") ? "DnB" :
                     deepCat.includes("Rap") || deepCat.includes("Hip") ? "Rap" :
                     deepCat.includes("Rock") ? "Rock" :
                     deepCat.includes("Metal") ? "Metal" :
                     deepCat.includes("Jazz") || deepCat.includes("Soul") ? "Jazz" :
                     deepCat.includes("Live") || deepCat.includes("Modular") ? "Live Acts" :
                     deepCat.includes("Danse") || deepCat.includes("Jongleur") || deepCat.includes("Fire") ? "Performers" :
                     deepCat.includes("VJ") || deepCat.includes("Mapping") || deepCat.includes("Laser") ? "VJ & Visuels" :
                     deepCat.includes("MC") || deepCat.includes("Animateur") ? "MCs & Animateurs" :
                     deepCat;
    
    // Adresse précise à 1km (variation de ~0.01 degré = ~1km)
    const latOffset = (Math.random() - 0.5) * 0.02; // ~1km
    const lngOffset = (Math.random() - 0.5) * 0.015; // ~1km
    const streetName = streetNames[Math.floor(Math.random() * streetNames.length)];
    const streetNumber = Math.floor(Math.random() * 150) + 1;
    const preciseAddress = `${streetNumber} ${streetName}, ${city.name}`;

    bookingsData.push({
      id,
      type: "booking",
      name,
      description: `Artiste ${deepCat} basé à ${city.name}. ${level === "Headliner" || level === "International" ? "Artiste reconnu avec de nombreuses performances." : "Passionné de musique, disponible pour vos événements."}`,
      city: city.name,
      canton: city.canton,
      address: preciseAddress, // Adresse précise à 1km
      lat: city.lat + latOffset,
      lng: city.lng + lngOffset,
      categories: [deepCat], // SOUS-CATÉGORIE PROFONDE !
      mainCategory: parentCat, // Catégorie parente
      categoryImage: null,
      boost,
      level,
      soundLinks: [
        `https://soundcloud.com/${name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')}`,
        `https://youtube.com/watch?v=${Math.random().toString(36).substring(2, 11)}`,
        `https://soundcloud.com/${name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')}-${deepCat.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')}`
      ],
      imageUrl: null,
      email: "contact@example.com",
      phone: "+41 79 000 00 00",
      isAI: Math.random() > 0.5,
      verified: Math.random() > 0.7,
      likes: Math.floor(Math.random() * 100),
      rating: (3 + Math.random() * 2).toFixed(1)
    });
  }

  // Générer 50 services
  const serviceCats = ["Son", "Lumière", "Sécurité", "Décoration", "Traiteur", "Transport", "Photo", "Vidéo", "Scène", "Bar"];
  const serviceNames = {
    "Son": ["SoundPro", "AudioMax", "Bass System", "MegaSound"],
    "Lumière": ["LightShow", "LumiPro", "LED Masters", "Laser Art"],
    "Sécurité": ["SecuEvent", "SafeGuard", "Protection Plus"],
    "Décoration": ["DecoPro", "ArtEvent", "Design Studio"],
    "Traiteur": ["GourmetEvent", "CateringPro", "Délices Suisses"],
    "Transport": ["EventTransport", "NavettePro", "MobilEvent"],
    "Photo": ["PhotoEvent", "Capture Pro", "Souvenirs HD"],
    "Vidéo": ["VideoLive", "FilmEvent", "Stream Pro"],
    "Scène": ["StageBuilder", "ScenePro", "Podium Event"],
    "Bar": ["BarMobile", "Cocktail Pro", "DrinkEvent"]
  };

  while (servicesData.length < 50) {
    const id = 3000 + servicesData.length;
    const city = SWISS_CITIES[id % SWISS_CITIES.length];
    const cat = serviceCats[id % serviceCats.length];
    const boost = boosts[Math.floor(Math.random() * boosts.length)];
    const names = serviceNames[cat] || ["Service Pro"];
    const name = `${names[Math.floor(Math.random() * names.length)]} ${city.name}`;

    servicesData.push({
      id,
      type: "service",
      name,
      description: `Service de ${cat.toLowerCase()} professionnel pour vos événements. Basé à ${city.name}, intervention dans toute la Suisse.`,
      city: city.name,
      canton: city.canton,
      address: `Zone industrielle, ${city.name}`,
      lat: city.lat + (Math.random() - 0.5) * 0.1,
      lng: city.lng + (Math.random() - 0.5) * 0.1,
      categories: [cat],
      mainCategory: cat,
      categoryImage: null,
      boost,
      imageUrl: null,
      email: "contact@service.ch",
      phone: "+41 79 000 00 00",
      website: "https://example.ch",
      isAI: Math.random() > 0.6,
      verified: Math.random() > 0.5,
      likes: Math.floor(Math.random() * 50),
      rating: (3.5 + Math.random() * 1.5).toFixed(1)
    });
  }
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

// ============================================
// ACTIONS UTILISATEUR - LIKE / PARTAGER / AGENDA
// ============================================
function onBuyContact(type, id) {
  if (!currentUser.isLoggedIn) {
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
  const key = `${type}:${id}`;
  const index = currentUser.likes.indexOf(key);
  
  const action = index > -1 ? 'remove' : 'add';
  
  // Appeler le backend
  try {
    const response = await fetch(`${API_BASE_URL}/user/likes`, {
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
    const response = await fetch(`${API_BASE_URL}/user/favorites`, {
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
  if (!currentUser.isLoggedIn) {
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

// Toggle Agenda avec limite selon abonnement
function toggleAgenda(type, id) {
  // Vérifier si l'utilisateur est connecté
  if (!currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  
  const key = `${type}:${id}`;
  const index = currentUser.agenda.indexOf(key);
  
  if (index > -1) {
    currentUser.agenda.splice(index, 1);
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
    // Vérifier la limite selon l'abonnement
    const maxAgenda = getAgendaLimit();
    if (currentUser.agenda.length >= maxAgenda) {
      showNotification(`⚠️ Limite d'agenda atteinte (${maxAgenda} places). Retirez un événement ou passez à un abonnement supérieur pour plus de places !`, "warning");
      openSubscriptionModal();
      return;
    }
    
    currentUser.agenda.push(key);
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
        if (currentUser.isLoggedIn) {
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
  if (!currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  
  const item = getItemById(type, id);
  if (!item) return;
  
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
  document.getElementById("publish-modal-backdrop").style.display = "flex";

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
        <div style="width:120px;height:120px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:60px;margin:0 auto 16px;border:4px solid rgba(0,255,195,0.3);">
          ${targetUser.avatar}
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
  document.getElementById("publish-modal-backdrop").style.display = "flex";
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

// Sauvegarder le profil
function saveProfile() {
  const bio = document.getElementById("edit-profile-bio")?.value.trim() || '';
  const photosText = document.getElementById("edit-profile-photos")?.value.trim() || '';
  const photos = photosText.split('\\n').filter(url => url.trim() && url.startsWith('http'));
  
  // Vérifier l'âge des photos (simulation - en production, utiliser une API de modération)
  const photosFiltered = photos.filter(photo => {
    // TODO: Vérifier avec une API de modération d'images
    return true; // Pour l'instant, on accepte tout
  });
  
  currentUser.bio = bio;
  currentUser.profilePhotos = photosFiltered;
  
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
  
  const url = `${window.location.origin}${window.location.pathname}?${type}=${id}`;
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

// ============================================
// NOTIFICATIONS
// ============================================
function showNotification(message, type = "info") {
  const existing = document.getElementById("notification-toast");
  if (existing) existing.remove();

  const colors = {
    success: "#22c55e",
    error: "#ef4444",
    info: "#3b82f6",
    warning: "#f59e0b"
  };

  const toast = document.createElement("div");
  toast.id = "notification-toast";
  toast.innerHTML = message;
  toast.style.cssText = `
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: ${colors[type] || colors.info};
    color: white;
    padding: 12px 24px;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 500;
    z-index: 100000;
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    animation: slideUp 0.3s ease;
    pointer-events: none;
  `;

  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = "slideDown 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// ============================================
// MODALS - LOGIN / REVIEW / DISCUSSION / REPORT
// ============================================
function openLoginModal() {
  const backdrop = document.getElementById('publish-modal-backdrop');
  const modal = document.getElementById('publish-modal-inner');

  if (!backdrop || !modal) {
    console.error('Modal elements not found');
    return;
  }

  const html = `
    <div style="padding:40px;max-width:450px;margin:0 auto;text-align:center;">
      <!-- Logo et titre -->
      <div style="margin-bottom:32px;">
        <div style="font-size:64px;margin-bottom:16px;">🌍</div>
        <h2 style="margin:0 0 8px;font-size:28px;font-weight:800;color:#fff;background:linear-gradient(135deg,#00ffc3,#3b82f6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">MAP EVENT</h2>
        <p style="margin:0;font-size:14px;color:var(--ui-text-muted);">Connectez-vous pour accéder à toutes les fonctionnalités</p>
      </div>
      
      <!-- Boutons de connexion sociale - DESIGN PROFESSIONNEL -->
      <div style="display:flex;flex-direction:column;gap:12px;margin-bottom:24px;">
        <button onclick="startGoogleLogin()" style="width:100%;padding:14px 20px;border-radius:12px;border:2px solid rgba(255,255,255,0.1);background:linear-gradient(135deg,rgba(255,255,255,0.1),rgba(255,255,255,0.05));color:#fff;display:flex;align-items:center;justify-content:center;gap:12px;font-weight:600;font-size:15px;cursor:pointer;transition:all 0.3s;backdrop-filter:blur(10px);" onmouseover="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='linear-gradient(135deg,rgba(0,255,195,0.2),rgba(59,130,246,0.2))';" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)';this.style.background='linear-gradient(135deg,rgba(255,255,255,0.1),rgba(255,255,255,0.05))';">
          <svg width="20" height="20" viewBox="0 0 24 24" style="fill:currentColor;">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
          </svg>
          <span>Connexion avec Google</span>
        </button>
        
        <button disabled style="width:100%;padding:14px 20px;border-radius:12px;border:2px solid rgba(255,255,255,0.05);background:rgba(255,255,255,0.03);color:rgba(255,255,255,0.4);display:flex;align-items:center;justify-content:center;gap:12px;font-weight:600;font-size:15px;cursor:not-allowed;opacity:0.5;">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
          </svg>
          <span>Connexion avec Facebook</span>
          <span style="font-size:11px;margin-left:auto;">(Bientôt)</span>
        </button>
      </div>
      
      <div style="display:flex;align-items:center;gap:12px;margin:24px 0;">
        <div style="flex:1;height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.1),transparent);"></div>
        <span style="font-size:12px;color:var(--ui-text-muted);font-weight:500;">ou</span>
        <div style="flex:1;height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.1),transparent);"></div>
      </div>
      
      <!-- Connexion par email -->
      <div style="margin-bottom:16px;text-align:left;">
        <label style="display:block;font-size:13px;font-weight:600;color:var(--ui-text-main);margin-bottom:8px;">📧 Email</label>
        <input type="email" id="login-email" placeholder="votre@email.com" style="width:100%;padding:12px 16px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:var(--ui-text-main);font-size:14px;transition:all 0.3s;" onfocus="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(15,23,42,0.8)';" onblur="this.style.borderColor='rgba(255,255,255,0.1)';this.style.background='rgba(15,23,42,0.5)';">
      </div>
      <div style="margin-bottom:24px;text-align:left;">
        <label style="display:block;font-size:13px;font-weight:600;color:var(--ui-text-main);margin-bottom:8px;">🔒 Mot de passe</label>
        <input type="password" id="login-password" placeholder="Votre mot de passe" 
               onkeypress="if(event.key==='Enter')performLogin()" style="width:100%;padding:12px 16px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:var(--ui-text-main);font-size:14px;transition:all 0.3s;" onfocus="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(15,23,42,0.8)';" onblur="this.style.borderColor='rgba(255,255,255,0.1)';this.style.background='rgba(15,23,42,0.5)';">
      </div>
      
      <button onclick="performLogin()" style="width:100%;padding:14px;border-radius:12px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:700;font-size:15px;cursor:pointer;margin-bottom:12px;transition:all 0.3s;" onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 8px 20px rgba(0,255,195,0.3)';" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='none';">
        Se connecter
      </button>
      
      <button onclick="closePublishModal()" style="width:100%;padding:12px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:transparent;color:var(--ui-text-muted);font-weight:600;font-size:14px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(255,255,255,0.3)';this.style.color='var(--ui-text-main)';" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)';this.style.color='var(--ui-text-muted)';">
        Annuler
      </button>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
  document.getElementById("publish-modal-backdrop").style.display = "flex";
  
  // Focus sur l'email
  setTimeout(() => {
    const emailInput = document.getElementById("login-email");
    if (emailInput) emailInput.focus();
  }, 100);
}

async function performLogin() {
  const email = document.getElementById("login-email")?.value.trim();
  const password = document.getElementById("login-password")?.value;
  
  if (!email || !password) {
    showNotification("⚠️ Veuillez remplir tous les champs", "warning");
    return;
  }
  
  // Tenter de récupérer l'utilisateur depuis localStorage (pour la démo)
  try {
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
      const parsedUser = JSON.parse(savedUser);
      if (parsedUser.email === email) {
        // Connexion réussie depuis localStorage
        currentUser = {
          ...parsedUser,
          isLoggedIn: true,
          lastLoginAt: new Date().toISOString()
        };
        safeSetItem('currentUser', JSON.stringify(currentUser));
        showNotification(`✅ Bienvenue ${currentUser.name} !`, "success");
        closePublishModal();
        updateUserUI();
        updateAccountButton();
        await loadUserDataOnLogin();
        // Afficher les notifications de changement de statut si l'utilisateur a participé à des événements
        showStatusChangeNotifications();
        return;
      }
    }
  } catch (e) {
    console.error('Erreur lecture localStorage:', e);
  }
  
  // Tenter connexion via le backend
  try {
    const response = await fetch(`${API_BASE_URL}/user/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    if (response.ok) {
      const data = await response.json();
      if (data.user) {
        currentUser = {
          ...data.user,
          isLoggedIn: true,
          lastLoginAt: new Date().toISOString()
        };
        // Initialiser pendingStatusNotifications si nécessaire
        if (!currentUser.pendingStatusNotifications) {
          currentUser.pendingStatusNotifications = [];
        }
        safeSetItem('currentUser', JSON.stringify(currentUser));
        showNotification(`✅ Bienvenue ${currentUser.name} !`, "success");
        closePublishModal();
        updateUserUI();
        updateAccountButton();
        await loadUserDataOnLogin();
        // Afficher les notifications de changement de statut si l'utilisateur a participé à des événements
        setTimeout(() => {
          showStatusChangeNotifications();
        }, 500);
        return;
      }
    }
  } catch (error) {
    console.error('Erreur connexion backend:', error);
  }
  
  // Fallback: créer un compte temporaire pour la démo
  showNotification("ℹ️ Compte non trouvé. Créez un nouveau compte.", "info");
  openRegisterModal();
}

// Ancien alias pour compatibilité
async function simulateLogin() {
  await performLogin();
}

// ============================================
// FORMULAIRE D'INSCRIPTION 3 ÉTAPES
// ============================================

let registerStep = 1;
let registerData = {
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

function openRegisterModal() {
  console.log('🎯 openRegisterModal called - Ouverture fenêtre de connexion');
  
  // Réinitialiser les données d'inscription
  registerStep = 1;
  registerData = {
    email: '',
    username: '',
    password: '',
    passwordConfirm: '',
    firstName: '',
    lastName: '',
    profilePhoto: '',
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
  
  // Ouvrir la fenêtre de connexion (pas le formulaire d'inscription directement)
  openLoginModal();
}

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
  
  // Forcer l'affichage du modal
  backdrop.style.display = 'flex';
  backdrop.style.visibility = 'visible';
  backdrop.style.opacity = '1';
  backdrop.style.zIndex = '9999';
  modal.style.display = 'block';
  modal.style.visibility = 'visible';
  modal.style.opacity = '1';

  const html = `
    <div class="pro-register-container">
      <div class="pro-register-header">
        <div class="pro-register-logo">🌍</div>
        <h1 class="pro-register-title">Créer un compte</h1>
        <p class="pro-register-subtitle">Rejoignez MapEvent et découvrez les événements près de chez vous</p>
      </div>

      <form class="pro-register-form" onsubmit="handleProRegisterSubmit(event)">
        <!-- Prénom et Nom -->
        <div class="pro-register-row">
          <div class="pro-register-field">
            <label class="pro-register-label">
              Prénom <span class="required">*</span>
            </label>
            <input 
              type="text" 
              id="pro-firstname" 
              class="pro-register-input" 
              placeholder="Prénom"
              required
              value="${registerData.firstName || ''}"
              oninput="registerData.firstName = this.value; validateProField('firstname', this.value)"
            >
            <div id="pro-firstname-error" class="pro-register-error"></div>
          </div>
          <div class="pro-register-field">
            <label class="pro-register-label">
              Nom <span class="required">*</span>
            </label>
            <input 
              type="text" 
              id="pro-lastname" 
              class="pro-register-input" 
              placeholder="Nom"
              required
              value="${registerData.lastName || ''}"
              oninput="registerData.lastName = this.value; validateProField('lastname', this.value)"
            >
            <div id="pro-lastname-error" class="pro-register-error"></div>
          </div>
        </div>

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
            value="${registerData.email || ''}"
            oninput="registerData.email = this.value; validateProField('email', this.value)"
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
            value="${registerData.username || ''}"
            oninput="registerData.username = this.value; validateProField('username', this.value)"
          >
          <div id="pro-username-error" class="pro-register-error"></div>
          <div id="pro-username-success" class="pro-register-success"></div>
        </div>

        <!-- Photo de profil -->
        <div class="pro-register-field">
          <label class="pro-register-label">
            Photo de profil <span class="required">*</span>
          </label>
          <div class="pro-register-photo-upload" onclick="document.getElementById('pro-photo-input').click()">
            <img id="pro-photo-preview" class="pro-register-photo-preview" src="${registerData.profilePhoto || ''}" alt="Preview">
            <div class="pro-register-photo-placeholder" id="pro-photo-placeholder" style="${registerData.profilePhoto ? 'display:none' : 'display:flex'}">
              📷
            </div>
            <div class="pro-register-photo-text">
              ${registerData.profilePhoto ? 'Cliquez pour changer la photo' : 'Cliquez pour ajouter une photo'}
            </div>
            <input 
              type="file" 
              id="pro-photo-input" 
              class="pro-register-photo-input" 
              accept="image/*"
              onchange="handleProPhotoUpload(event)"
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
              value="${registerData.password || ''}"
              oninput="registerData.password = this.value; validateProPassword(this.value)"
            >
            <button type="button" class="pro-register-password-toggle" onclick="toggleProPasswordVisibility('pro-password')">👁️</button>
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
              value="${registerData.passwordConfirm || ''}"
              oninput="registerData.passwordConfirm = this.value; validateProPasswordMatch()"
            >
            <button type="button" class="pro-register-password-toggle" onclick="toggleProPasswordVisibility('pro-password-confirm')">👁️</button>
          </div>
          <div id="pro-password-confirm-error" class="pro-register-error"></div>
          <div id="pro-password-confirm-success" class="pro-register-success"></div>
        </div>

        <!-- Adresse postale pour les alertes -->
        <div class="pro-register-field">
          <label class="pro-register-label">
            Adresse postale <span class="required">*</span>
            <span style="font-weight: normal; color: var(--ui-text-muted); font-size: 12px;">(pour recevoir les alertes)</span>
          </label>
          <input 
            type="text" 
            id="pro-postal-address" 
            class="pro-register-input" 
            placeholder="Rue, Code postal, Ville"
            required
            value="${registerData.postalAddress || ''}"
            oninput="registerData.postalAddress = this.value; validateProField('postalAddress', this.value)"
          >
          <div id="pro-postal-address-error" class="pro-register-error"></div>
        </div>

        <!-- Bouton de soumission -->
        <div class="pro-register-actions">
          <button type="submit" class="pro-register-btn-primary" id="pro-submit-btn">
            Créer le compte
          </button>
          <button type="button" class="pro-register-btn-secondary" onclick="closePublishModal()">
            Annuler
          </button>
        </div>

        <!-- Mentions légales -->
        <p class="pro-register-legal">
          En créant un compte, vous acceptez nos 
          <a href="#" onclick="showTermsModal(); return false;">Conditions d'utilisation</a> 
          et notre 
          <a href="#" onclick="showPrivacyModal(); return false;">Politique de confidentialité</a>.
        </p>
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

  // Focus sur le premier champ
  setTimeout(() => {
    const firstInput = document.getElementById("pro-firstname");
    if (firstInput) {
      firstInput.focus();
      console.log('✅ Focus sur le premier champ');
    } else {
      console.warn('⚠️ Premier champ non trouvé');
    }
  }, 100);
}

// Gestion de l'upload de photo
function handleProPhotoUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  // Vérifier la taille (max 5MB)
  if (file.size > 5 * 1024 * 1024) {
    showError('pro-photo-error', 'La photo est trop grande (max 5MB)');
    return;
  }

  // Vérifier le type
  if (!file.type.startsWith('image/')) {
    showError('pro-photo-error', 'Veuillez sélectionner une image');
    return;
  }

  // Lire et convertir en Base64
  const reader = new FileReader();
  reader.onload = function(e) {
    const base64 = e.target.result;
    registerData.profilePhoto = base64;
    
    // Afficher la preview
    const preview = document.getElementById('pro-photo-preview');
    const placeholder = document.getElementById('pro-photo-placeholder');
    if (preview) {
      preview.src = base64;
      preview.classList.add('show');
    }
    if (placeholder) {
      placeholder.style.display = 'none';
    }
    
    // Cacher l'erreur
    showError('pro-photo-error', '');
  };
  reader.readAsDataURL(file);
}

// Validation des champs
function validateProField(fieldName, value) {
  const errorEl = document.getElementById(`pro-${fieldName}-error`);
  const successEl = document.getElementById(`pro-${fieldName}-success`);
  
  if (!errorEl) return true;

  let isValid = true;
  let errorMsg = '';

  switch(fieldName) {
    case 'firstname':
    case 'lastname':
      if (!value || value.trim().length < 2) {
        isValid = false;
        errorMsg = 'Minimum 2 caractères';
      } else if (value.length > 50) {
        isValid = false;
        errorMsg = 'Maximum 50 caractères';
      }
      break;
    
    case 'email':
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!value) {
        isValid = false;
        errorMsg = 'Email requis';
      } else if (!emailRegex.test(value)) {
        isValid = false;
        errorMsg = 'Format email invalide';
      } else {
        if (successEl) successEl.textContent = '✓ Email valide';
      }
      break;
    
    case 'username':
      if (!value) {
        isValid = false;
        errorMsg = 'Nom d\'utilisateur requis';
      } else if (value.length < 3) {
        isValid = false;
        errorMsg = 'Minimum 3 caractères';
      } else if (value.length > 20) {
        isValid = false;
        errorMsg = 'Maximum 20 caractères';
      } else if (!/^[a-zA-Z0-9_-]+$/.test(value)) {
        isValid = false;
        errorMsg = 'Caractères autorisés: lettres, chiffres, _ et -';
      } else {
        if (successEl) successEl.textContent = '✓ Disponible';
      }
      break;
    
    case 'postalAddress':
      if (!value || value.trim().length < 5) {
        isValid = false;
        errorMsg = 'Adresse complète requise';
      }
      break;
  }

  showError(`pro-${fieldName}-error`, errorMsg);
  return isValid;
}

// Validation du mot de passe
function validateProPassword(password) {
  const errorEl = document.getElementById('pro-password-error');
  const strengthEl = document.getElementById('pro-password-strength-fill');
  
  if (!password) {
    if (strengthEl) {
      strengthEl.className = 'pro-register-password-strength-fill';
      strengthEl.style.width = '0%';
    }
    return false;
  }

  let strength = 0;
  let errorMsg = '';

  // Vérifier les critères
  const hasLength = password.length >= 8;
  const hasUpper = /[A-Z]/.test(password);
  const hasLower = /[a-z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);

  if (hasLength) strength++;
  if (hasUpper) strength++;
  if (hasLower) strength++;
  if (hasNumber) strength++;
  if (hasSpecial) strength++;

  // Mettre à jour la barre de force
  if (strengthEl) {
    if (strength <= 2) {
      strengthEl.className = 'pro-register-password-strength-fill weak';
    } else if (strength <= 4) {
      strengthEl.className = 'pro-register-password-strength-fill medium';
    } else {
      strengthEl.className = 'pro-register-password-strength-fill strong';
    }
  }

  // Messages d'erreur
  if (!hasLength) {
    errorMsg = 'Minimum 8 caractères';
  } else if (strength < 3) {
    errorMsg = 'Mot de passe trop faible';
  }

  showError('pro-password-error', errorMsg);
  
  // Vérifier aussi la correspondance si la confirmation est remplie
  const confirmValue = document.getElementById('pro-password-confirm')?.value;
  if (confirmValue) {
    validateProPasswordMatch();
  }

  return strength >= 3;
}

// Validation de la correspondance des mots de passe
function validateProPasswordMatch() {
  const password = registerData.password;
  const confirm = registerData.passwordConfirm;
  const errorEl = document.getElementById('pro-password-confirm-error');
  const successEl = document.getElementById('pro-password-confirm-success');

  if (!confirm) {
    showError('pro-password-confirm-error', '');
    return false;
  }

  if (password !== confirm) {
    showError('pro-password-confirm-error', 'Les mots de passe ne correspondent pas');
    if (successEl) successEl.textContent = '';
    return false;
  } else {
    showError('pro-password-confirm-error', '');
    if (successEl) successEl.textContent = '✓ Les mots de passe correspondent';
    return true;
  }
}

// Toggle visibilité mot de passe
function toggleProPasswordVisibility(inputId) {
  const input = document.getElementById(inputId);
  if (!input) return;
  
  if (input.type === 'password') {
    input.type = 'text';
  } else {
    input.type = 'password';
  }
}

// Helper pour afficher les erreurs
function showError(elementId, message) {
  const el = document.getElementById(elementId);
  if (el) {
    el.textContent = message;
  }
}

// Soumission du formulaire
async function handleProRegisterSubmit(event) {
  event.preventDefault();
  
  // VÉRIFICATION CRITIQUE : Si le profil est déjà complet, ne pas permettre la soumission
  if (currentUser && currentUser.profileComplete === true && currentUser.isLoggedIn === true) {
    console.warn('⚠️ Tentative de soumission formulaire alors que le profil est déjà complet');
    showNotification('✅ Votre compte est déjà créé et complet. Vous êtes connecté !', 'success');
    closePublishModal();
    return;
  }
  
  // Récupérer toutes les valeurs
  registerData.firstName = document.getElementById('pro-firstname')?.value.trim() || '';
  registerData.lastName = document.getElementById('pro-lastname')?.value.trim() || '';
  registerData.email = document.getElementById('pro-email')?.value.trim() || '';
  registerData.username = document.getElementById('pro-username')?.value.trim() || '';
  registerData.password = document.getElementById('pro-password')?.value || '';
  registerData.passwordConfirm = document.getElementById('pro-password-confirm')?.value || '';
  registerData.postalAddress = document.getElementById('pro-postal-address')?.value.trim() || '';

  // Validation complète
  let isValid = true;
  isValid = validateProField('firstname', registerData.firstName) && isValid;
  isValid = validateProField('lastname', registerData.lastName) && isValid;
  isValid = validateProField('email', registerData.email) && isValid;
  isValid = validateProField('username', registerData.username) && isValid;
  isValid = validateProPassword(registerData.password) && isValid;
  isValid = validateProPasswordMatch() && isValid;
  isValid = validateProField('postalAddress', registerData.postalAddress) && isValid;

  // Vérifier la photo
  if (!registerData.profilePhoto) {
    showError('pro-photo-error', 'Veuillez ajouter une photo de profil');
    isValid = false;
  }

  if (!isValid) {
    showNotification('⚠️ Veuillez corriger les erreurs dans le formulaire', 'warning');
    return;
  }

  // Désactiver le bouton
  const submitBtn = document.getElementById('pro-submit-btn');
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.textContent = 'Création du compte...';
  }

  try {
    // Détecter si c'est un utilisateur Google (connexion OAuth)
    // Vérifier plusieurs indicateurs : provider, googleValidated, sub, ou email correspondant
    const isGoogleUser = currentUser && (
      currentUser.provider === 'google' || 
      currentUser.googleValidated === true ||
      (currentUser.sub && currentUser.email === registerData.email) ||
      (currentUser.email === registerData.email && registerData.email.includes('@gmail.com'))
    );
    
    console.log('🔍 Détection type utilisateur:', {
      isGoogleUser: isGoogleUser,
      provider: currentUser?.provider,
      googleValidated: currentUser?.googleValidated,
      hasSub: !!currentUser?.sub,
      emailMatch: currentUser?.email === registerData.email
    });
    
    // API_BASE_URL contient déjà '/api', donc pas besoin de l'ajouter à nouveau
    const endpoint = isGoogleUser ? `${API_BASE_URL}/user/oauth/google/complete` : `${API_BASE_URL}/user/register`;
    
    // Préparer le payload selon le type d'utilisateur
    // Pour Google OAuth, utiliser l'email comme identifiant si pas d'ID disponible
    const payload = isGoogleUser ? {
      userId: currentUser?.id || currentUser?.sub || null, // Peut être null si localStorage plein
      email: registerData.email,
      username: registerData.username,
      password: registerData.password,
      firstName: registerData.firstName,
      lastName: registerData.lastName,
      profilePhoto: registerData.profilePhoto,
      postalAddress: registerData.postalAddress
    } : {
      email: registerData.email,
      username: registerData.username,
      password: registerData.password,
      firstName: registerData.firstName,
      lastName: registerData.lastName,
      profilePhoto: registerData.profilePhoto,
      postalAddress: registerData.postalAddress,
      avatarId: registerData.avatarId || 1
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
      
      // Mettre à jour currentUser avec les données du backend
      if (data.user) {
        // Mapper les champs du backend vers le format frontend
        const profilePhoto = data.user.profile_photo_url || data.user.avatar || data.user.profilePhoto || registerData.profilePhoto || null;
        const avatar = data.user.avatar || data.user.profile_photo_url || data.user.profilePhoto || registerData.profilePhoto || '👤';
        
        currentUser = {
          ...currentUser,
          ...data.user,
          // PRIORITÉ ABSOLUE : username du backend OU du formulaire (GARANTIR qu'il est présent)
          username: data.user.username || registerData.username || currentUser.username,
          // S'assurer que profilePhoto et avatar sont correctement mappés
          profilePhoto: profilePhoto,
          avatar: avatar,
          isLoggedIn: true,
          profileComplete: true, // Profil maintenant complet après inscription - IMPORTANT !
          googleValidated: false, // Plus besoin du marqueur
          likes: currentUser.likes || [],
          favorites: currentUser.favorites || [],
          agenda: currentUser.agenda || [],
          participating: currentUser.participating || [],
          alerts: currentUser.alerts || [],
          statusAlerts: currentUser.statusAlerts || [],
          pendingStatusNotifications: currentUser.pendingStatusNotifications || [],
          proximityAlerts: currentUser.proximityAlerts || [],
          eventAlarms: currentUser.eventAlarms || [],
          reviews: currentUser.reviews || {},
          friends: currentUser.friends || [],
          friendRequests: currentUser.friendRequests || [],
          sentRequests: currentUser.sentRequests || [],
          blockedUsers: currentUser.blockedUsers || [],
          conversations: currentUser.conversations || [],
          groups: currentUser.groups || [],
          profilePhotos: currentUser.profilePhotos || (profilePhoto ? [profilePhoto] : []),
          profileLinks: currentUser.profileLinks || [],
          history: currentUser.history || [],
          photos: currentUser.photos || [],
          eventStatusHistory: currentUser.eventStatusHistory || {}
        };
      } else {
        // Fallback si pas de data.user (inscription standard)
        currentUser = {
          id: data.user?.id || Date.now(),
          email: registerData.email,
          username: registerData.username,
          name: `${registerData.firstName} ${registerData.lastName}`,
          firstName: registerData.firstName,
          lastName: registerData.lastName,
          profilePhoto: registerData.profilePhoto,
          postalAddress: registerData.postalAddress,
          isLoggedIn: true,
          profileComplete: true,
          likes: [],
          favorites: [],
          agenda: [],
          participating: [],
          alerts: [],
          statusAlerts: [],
          pendingStatusNotifications: [],
          proximityAlerts: [],
          eventAlarms: [],
          reviews: {},
          friends: [],
          friendRequests: [],
          sentRequests: [],
          blockedUsers: [],
          conversations: [],
          groups: [],
          profilePhotos: [registerData.profilePhoto],
          profileLinks: [],
          history: [],
          photos: [],
          eventStatusHistory: {}
        };
      }

      // Sauvegarder dans localStorage avec gestion d'erreur de quota
      try {
        safeSetItem('currentUser', JSON.stringify(currentUser));
      } catch (e) {
        if (e.name === 'QuotaExceededError' || e.message.includes('quota')) {
          console.warn('⚠️ localStorage plein, nettoyage...');
          // Nettoyer les anciennes données
          try {
            // Supprimer les données non essentielles
            localStorage.removeItem('eventsData');
            localStorage.removeItem('bookingsData');
            localStorage.removeItem('servicesData');
            // Réessayer
            safeSetItem('currentUser', JSON.stringify(currentUser));
            showNotification('⚠️ Espace de stockage limité - Certaines données ont été nettoyées', 'warning');
          } catch (e2) {
            console.error('❌ Impossible de sauvegarder dans localStorage:', e2);
            showNotification('⚠️ Impossible de sauvegarder localement. Vos données sont sauvegardées sur le serveur.', 'warning');
          }
        } else {
          throw e;
        }
      }
      
      // Afficher le message de bienvenue avec le username choisi (priorité absolue)
      const welcomeName = currentUser.username || currentUser.name || currentUser.email?.split('@')[0] || 'Utilisateur';
      showNotification(`✅ Bienvenue ${welcomeName} ! Votre compte a été créé avec succès.`, 'success');
      
      // Log pour vérifier que le username est bien présent
      console.log('✅ Compte créé - username:', currentUser.username, 'name:', currentUser.name);
      
      closePublishModal();
      updateUserUI();
      updateAccountButton(); // Mettre à jour le bouton compte avec le username
      
      // Forcer une nouvelle mise à jour après un court délai pour être sûr
      setTimeout(() => {
        updateAccountButton();
        console.log('🔄 Mise à jour forcée du bouton compte - username:', currentUser.username);
      }, 100);
      
      await loadUserDataOnLogin();
    } else {
      // Gérer les erreurs HTTP
      let errorMessage = 'Impossible de créer le compte';
      
      try {
        const errorText = await response.text();
        console.error(`❌ Erreur serveur ${response.status}:`, errorText);
        
        try {
          const errorData = JSON.parse(errorText);
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
      
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Créer le compte';
      }
    }
  } catch (error) {
    console.error('❌ Erreur création compte:', error);
    console.error('Détails erreur:', error.message, error.stack);
    
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
}

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
  registerStep = 2;
  
  // Générer la grille d'avatars
  const avatarGrid = AVAILABLE_AVATARS.map(av => `
    <div data-avatar-id="${av.id}"
         id="avatar-option-${av.id}"
         class="register-avatar-option ${registerData.avatarId === av.id ? 'selected' : ''}"
         title="${av.name}">
      ${av.emoji}
    </div>
  `).join('');
  
  const selectedAvatar = AVAILABLE_AVATARS.find(av => av.id === registerData.avatarId) || AVAILABLE_AVATARS[0];
  
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
                 value="${registerData.firstName}"
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
                 value="${registerData.lastName}"
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
               value="${registerData.email}"
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
               value="${registerData.username}"
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
                 value="${registerData.password}"
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
                  class="register-textarea">${registerData.avatarDescription || ''}</textarea>
        <div class="register-textarea-counter">
          <span id="avatar-desc-count">${(registerData.avatarDescription || '').length}/150</span>
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
  document.getElementById("publish-modal-backdrop").style.display = "flex";
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

  if (firstnameInput) firstnameInput.addEventListener('input', (e) => registerData.firstName = e.target.value);
  if (lastnameInput) lastnameInput.addEventListener('input', (e) => registerData.lastName = e.target.value);
  if (emailInput) {
    emailInput.addEventListener('input', (e) => registerData.email = e.target.value);
  }
  if (usernameInput) usernameInput.addEventListener('input', (e) => registerData.username = e.target.value);
  if (passwordInput) passwordInput.addEventListener('input', (e) => registerData.password = e.target.value);
  if (avatarDescInput) avatarDescInput.addEventListener('input', (e) => registerData.avatarDescription = e.target.value);
  
  // Initialiser les validations
  if (registerData.firstName) validateNameRealTime('firstname', registerData.firstName);
  if (registerData.lastName) validateNameRealTime('lastname', registerData.lastName);
  if (registerData.email) validateEmailRealTime(registerData.email);
  if (registerData.username) validateUsernameRealTime(registerData.username);
  if (registerData.password) checkPasswordStrength(registerData.password);

  console.log('✅ showRegisterStep2 completed successfully');
}

// Sélectionner un avatar
function selectAvatar(avatarId) {
  // IMPORTANT: Sauvegarder les valeurs actuelles du formulaire AVANT de régénérer
  const currentFormValues = {
    firstName: document.getElementById('register-firstname')?.value || registerData.firstName || '',
    lastName: document.getElementById('register-lastname')?.value || registerData.lastName || '',
    email: document.getElementById('register-email')?.value || registerData.email || '',
    username: document.getElementById('register-username')?.value || registerData.username || '',
    password: document.getElementById('register-password')?.value || registerData.password || '',
    avatarDescription: document.getElementById('register-avatar-desc')?.value || registerData.avatarDescription || ''
  };

  // Mettre à jour registerData avec les valeurs actuelles du formulaire
  registerData.firstName = currentFormValues.firstName;
  registerData.lastName = currentFormValues.lastName;
  registerData.email = currentFormValues.email;
  registerData.username = currentFormValues.username;
  registerData.password = currentFormValues.password;
  registerData.avatarDescription = currentFormValues.avatarDescription;

  // Mettre à jour l'avatarId
  registerData.avatarId = avatarId;

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
  if (!registerData.avatarId) {
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
  if (registerData.lastRegistrationAttempt && (now - registerData.lastRegistrationAttempt) < 60000) {
    const remainingSeconds = Math.ceil((60000 - (now - registerData.lastRegistrationAttempt)) / 1000);
    showNotification(`⏱️ Veuillez patienter ${remainingSeconds} secondes avant de réessayer`, "warning");
    return;
  }
  
  registerData.firstName = firstName;
  registerData.lastName = lastName;
  registerData.email = email;
  registerData.username = username;
  registerData.password = password;
  registerData.avatarDescription = avatarDesc;
  registerData.lastRegistrationAttempt = now;
  registerData.registrationAttempts++;
  
  // Vérifier si l'email existe déjà
  try {
    const checkResponse = await fetch(`${API_BASE_URL}/user/check-email`, {
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
  registerStep = 2.5;
  
  // Générer et envoyer le code si pas déjà fait
  if (!registerData.emailVerificationCode) {
    sendVerificationCode();
  }
  
  const maskedEmail = registerData.email.replace(/(.{2})(.*)(@.*)/, '$1***$3');
  let countdown = registerData.resendCountdown || 0;
  
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
  
  registerData.captchaAnswer = answer;
  
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
    registerData.emailVerificationCode = code;
    registerData.codeSentAt = Date.now();
    registerData.codeExpiresAt = Date.now() + (15 * 60 * 1000); // 15 minutes
    
    // Envoyer via le backend
    const response = await fetch(`${API_BASE_URL}/user/send-verification-code`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: registerData.email,
        code: code,
        username: registerData.username
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
    registerData.emailVerificationCode = code;
    registerData.codeSentAt = Date.now();
    registerData.codeExpiresAt = Date.now() + (15 * 60 * 1000);
    showNotification("✅ Code généré ! (Mode développement - vérifiez la console)", "info");
    console.log(`🔐 CODE DE VÉRIFICATION (DEV ONLY): ${code}`);
  }
}

// Renvoyer le code
async function resendVerificationCode() {
  const now = Date.now();
  const lastResend = registerData.lastResendAttempt || 0;
  
  // Rate limiting : 60 secondes entre chaque renvoi
  if (now - lastResend < 60000) {
    const remaining = Math.ceil((60000 - (now - lastResend)) / 1000);
    showNotification(`⏱️ Veuillez patienter ${remaining} secondes avant de renvoyer`, "warning");
    return;
  }
  
  registerData.lastResendAttempt = now;
  registerData.emailVerificationCode = null; // Réinitialiser
  
  await sendVerificationCode();
  
  // Démarrer le countdown
  registerData.resendCountdown = 60;
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
    registerData.resendCountdown = remaining;
    
    if (countdownEl) {
      countdownEl.textContent = `Vous pourrez renvoyer dans ${remaining} secondes`;
    }
    
    if (remaining <= 0) {
      clearInterval(interval);
      resendButton.disabled = false;
      resendButton.style.opacity = '1';
      resendButton.style.cursor = 'pointer';
      if (countdownEl) countdownEl.textContent = '';
      registerData.resendCountdown = 0;
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
  if (captchaAnswer !== registerData.captchaAnswer) {
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
  if (registerData.lastVerificationAttempt) {
    const timeSinceLastAttempt = now - registerData.lastVerificationAttempt;
    if (timeSinceLastAttempt < 2000) { // 2 secondes entre chaque tentative
      showNotification("⏱️ Veuillez patienter avant de réessayer", "warning");
      return;
    }
  }
  
  registerData.lastVerificationAttempt = now;
  registerData.verificationAttempts++;
  
  // Vérifier si le code a expiré
  if (registerData.codeExpiresAt && now > registerData.codeExpiresAt) {
    showNotification("⏰ Le code a expiré. Veuillez en demander un nouveau.", "warning");
    registerData.emailVerificationCode = null;
    return;
  }
  
  // Vérifier le code
  if (providedCode === registerData.emailVerificationCode) {
    registerData.emailVerified = true;
    
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
    registerData.verificationAttempts++;
    
    // Bloquer après 5 tentatives
    if (registerData.verificationAttempts >= 5) {
      showNotification("🚫 Trop de tentatives échouées. Veuillez renvoyer un nouveau code.", "error");
      registerData.emailVerificationCode = null;
      registerData.verificationAttempts = 0;
      showRegisterStep2_5();
      return;
    }
    
    // Afficher l'erreur
    const feedbackEl = document.getElementById("code-feedback");
    if (feedbackEl) {
      feedbackEl.textContent = `❌ Code incorrect (${registerData.verificationAttempts}/5 tentatives)`;
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
  if (attemptsEl && registerData.verificationAttempts > 0) {
    attemptsEl.textContent = `${registerData.verificationAttempts}/5 tentatives utilisées`;
    attemptsEl.style.color = registerData.verificationAttempts >= 3 ? "#ef4444" : "var(--ui-text-muted)";
  }
}

function showRegisterStep3() {
  registerStep = 3;
  const addressCount = registerData.addresses.length || 1;
  
  // S'assurer qu'il y a au moins un champ d'adresse
  if (registerData.addresses.length === 0) {
    registerData.addresses = [{ address: '', city: '', lat: null, lng: null, isPrimary: true }];
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
        ${registerData.addresses.map((addr, index) => `
          <div id="address-field-${index}" style="background:rgba(15,23,42,0.5);border:1px solid var(--ui-card-border);border-radius:12px;padding:16px;margin-bottom:12px;">
            ${index === 0 ? '<div style="font-size:11px;color:#00ffc3;margin-bottom:8px;font-weight:600;">📍 Adresse principale</div>' : ''}
            <div style="margin-bottom:12px;">
              <label style="display:block;font-size:12px;font-weight:600;color:#fff;margin-bottom:6px;">Adresse complète *</label>
              <input type="text" id="address-${index}" placeholder="Rue, numéro, ville" required
                     value="${addr.address}"
                     onchange="registerData.addresses[${index}].address = this.value"
                     style="width:100%;padding:10px;border-radius:8px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:14px;">
            </div>
            <div style="display:flex;gap:8px;align-items:end;">
              <div style="flex:1;">
                <label style="display:block;font-size:12px;font-weight:600;color:#fff;margin-bottom:6px;">Ville *</label>
                <input type="text" id="city-${index}" placeholder="Ville" required
                       value="${addr.city}"
                       onchange="registerData.addresses[${index}].city = this.value"
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
      
      ${registerData.addresses.length < 2 ? `
        <button onclick="addAddressField()" style="width:100%;padding:10px;border-radius:8px;border:1px dashed var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-size:13px;margin-bottom:20px;">
          + Ajouter une adresse (${registerData.addresses.length}/2)
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
}

function addAddressField() {
  if (registerData.addresses.length >= 2) {
    showNotification("⚠️ Maximum 2 adresses autorisées", "warning");
    return;
  }
  
  registerData.addresses.push({ address: '', city: '', lat: null, lng: null, isPrimary: false });
  showRegisterStep3();
}

function removeAddressField(index) {
  if (registerData.addresses.length <= 1) {
    showNotification("⚠️ Au moins une adresse est requise", "warning");
    return;
  }
  
  registerData.addresses.splice(index, 1);
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
    const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(fullAddress)}&limit=5&addressdetails=1&extratags=1`, {
      headers: {
        'User-Agent': 'MapEventAI/1.0'
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
    registerData.addresses[addressIndex].lat = lat;
    registerData.addresses[addressIndex].lng = lng;
    registerData.addresses[addressIndex].address = address;
    registerData.addresses[addressIndex].city = city;
    registerData.addresses[addressIndex].verified = true;
    registerData.addresses[addressIndex].addressDetails = {
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
  if (!registerData.emailVerified) {
    showNotification("⚠️ Veuillez vérifier votre email avant de créer le compte", "warning");
    showRegisterStep2_5();
    return;
  }
  
  // Vérifier qu'au moins une adresse a des coordonnées
  const validAddresses = registerData.addresses.filter(addr => 
    addr.address && addr.city && addr.lat && addr.lng
  );
  
  if (validAddresses.length === 0) {
    showNotification("⚠️ Veuillez géocoder au moins une adresse", "warning");
    return;
  }
  
  // Vérifier le rate limiting final
  const now = Date.now();
  if (registerData.lastRegistrationAttempt && (now - registerData.lastRegistrationAttempt) < 30000) {
    const remainingSeconds = Math.ceil((30000 - (now - registerData.lastRegistrationAttempt)) / 1000);
    showNotification(`⏱️ Veuillez patienter ${remainingSeconds} secondes avant de créer le compte`, "warning");
    return;
  }
  
  // Récupérer l'avatar sélectionné
  const selectedAvatar = AVAILABLE_AVATARS.find(av => av.id === registerData.avatarId) || AVAILABLE_AVATARS[0];
  
  // Créer l'utilisateur
  const userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  const createdAt = new Date().toISOString();
  
  currentUser = {
    id: userId,
    name: registerData.username,
    firstName: registerData.firstName,
    lastName: registerData.lastName,
    email: registerData.email,
    avatar: selectedAvatar.emoji,
    avatarId: selectedAvatar.id,
    avatarName: selectedAvatar.name,
    avatarDescription: registerData.avatarDescription || '',
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
  
  // Mettre à jour l'avatar dans la barre des titres
  updateAccountButton();
  
  // Sauvegarder dans le backend (OBLIGATOIRE - vérification côté serveur)
  try {
    const response = await fetch(`${API_BASE_URL}/user/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: registerData.email,
        username: registerData.username,
        password: registerData.password, // Le backend hash le mot de passe
        firstName: registerData.firstName,
        lastName: registerData.lastName,
        avatarId: selectedAvatar.id,
        avatarEmoji: selectedAvatar.emoji,
        avatarDescription: registerData.avatarDescription || '',
        addresses: currentUser.addresses.map(addr => ({
          ...addr,
          addressDetails: registerData.addresses.find(a => a.address === addr.address && a.city === addr.city)?.addressDetails || {}
        })),
        verificationCode: registerData.emailVerificationCode // Envoyer le code pour double vérification
      })
    });
    
    const result = await response.json();
    
    if (!response.ok) {
      // Erreur côté backend
      if (result.code === 'EMAIL_NOT_VERIFIED') {
        showNotification("⚠️ Email non vérifié. Veuillez vérifier votre email d'abord.", "warning");
        showRegisterStep2_5();
        return;
      } else if (result.code === 'EMAIL_ALREADY_EXISTS') {
        showNotification("⚠️ Cet email est déjà utilisé. Veuillez vous connecter.", "warning");
        return;
      } else if (result.code === 'USERNAME_ALREADY_EXISTS') {
        showNotification("⚠️ Ce nom d'utilisateur est déjà pris. Choisissez-en un autre.", "warning");
        showRegisterStep2();
        return;
      } else {
        showNotification(`❌ Erreur lors de la création du compte: ${result.error || 'Erreur inconnue'}`, "error");
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
    showNotification("❌ Erreur de connexion au serveur. Veuillez réessayer.", "error");
    return; // Ne pas continuer si le backend échoue
  }
  
  showNotification("✅ Compte créé avec succès !", "success");
  closePublishModal();
  updateUserUI();
  updateAccountButton();
  
  // Charger les données utilisateur
  await loadUserDataOnLogin();
}

// Alias pour compatibilité
function showRegisterForm() {
  openRegisterModal();
}

// Modales CGU/RGPD
function showTermsModal() {
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
      <button onclick="closePublishModal()" style="width:100%;padding:14px;border-radius:999px;border:none;background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff;font-weight:700;cursor:pointer;margin-top:24px;">
        Fermer
      </button>
    </div>
  `;
  document.getElementById("publish-modal-inner").innerHTML = html;
}

function showPrivacyModal() {
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
      <button onclick="closePublishModal()" style="width:100%;padding:14px;border-radius:999px;border:none;background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff;font-weight:700;cursor:pointer;margin-top:24px;">
        Fermer
      </button>
    </div>
  `;
  document.getElementById("publish-modal-inner").innerHTML = html;
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
  document.getElementById("publish-modal-backdrop").style.display = "flex";
  
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
  
  if (!currentUser.isLoggedIn) {
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
  
  if (!currentUser.isLoggedIn) {
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

function openDiscussionModal(type, id) {
  // Récupérer l'item (event, booking, service)
  let item = null;
  if (type === 'event') {
    item = eventsData.find(e => e.id === id);
  } else if (type === 'booking') {
    item = bookingsData.find(b => b.id === id);
  } else if (type === 'service') {
    item = servicesData.find(s => s.id === id);
  }
  
  const itemTitle = item?.title || item?.name || 'Événement';
  const itemImage = item?.image || item?.photo || '';
  
  // Récupérer les posts existants (stockés localement pour l'instant)
  const postsKey = `discussion_${type}_${id}`;
  let posts = JSON.parse(localStorage.getItem(postsKey) || '[]');
  
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
      <div style="margin-bottom:4px;">
        <div style="display:flex;gap:8px;">
          <div style="width:${avatarSize}px;height:${avatarSize}px;border-radius:50%;background:linear-gradient(135deg,#1877f2,#42a5f5);display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;font-weight:700;color:#fff;">
            ${reply.avatar || '👤'}
          </div>
          <div style="flex:1;min-width:0;">
            <div style="background:#3a3b3c;border-radius:18px;padding:8px 12px;display:inline-block;max-width:100%;">
              <span style="font-weight:600;font-size:13px;color:#e4e6eb;margin-right:4px;">${escapeHtml(reply.author || 'Utilisateur')}</span>
              <span style="font-size:13px;color:#e4e6eb;line-height:1.33;white-space:pre-wrap;word-wrap:break-word;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">${escapeHtml(reply.text)}</span>
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
              <textarea id="reply-input-${postId}-${replyPath}" placeholder="Répondre à ${escapeHtml(reply.author || 'Utilisateur')}..." style="width:100%;min-height:36px;max-height:100px;padding:8px 12px;border-radius:20px;border:none;background:rgba(58,59,60,0.8);color:#e4e6eb;font-size:14px;resize:none;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;line-height:1.33;" onkeydown="if(event.key==='Enter' && !event.shiftKey) { event.preventDefault(); submitReply('${type}', '${id}', '${postId}', '${replyPath}'); }" oninput="this.style.height='auto';this.style.height=Math.min(this.scrollHeight,100)+'px';"></textarea>
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
      <div style="background:#242526;border-radius:8px;padding:12px;margin-bottom:12px;">
        <!-- En-tête du post -->
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
          <div style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#1877f2,#42a5f5);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;font-weight:700;color:#fff;">
            ${post.avatar || '👤'}
          </div>
          <div style="flex:1;">
            <div style="font-weight:600;font-size:15px;color:#e4e6eb;line-height:1.2;">${escapeHtml(post.author || 'Utilisateur')}</div>
            <div style="font-size:13px;color:#b0b3b8;line-height:1.2;">${formatTime(post.timestamp || Date.now())}</div>
          </div>
        </div>
        
        <!-- Contenu du post -->
        <div style="font-size:15px;color:#e4e6eb;line-height:1.33;margin-bottom:8px;white-space:pre-wrap;word-wrap:break-word;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
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
              <textarea id="reply-input-${post.id}" placeholder="Écrivez un commentaire..." style="width:100%;min-height:36px;max-height:100px;padding:8px 12px;border-radius:20px;border:none;background:rgba(58,59,60,0.8);color:#e4e6eb;font-size:14px;resize:none;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;line-height:1.33;" onkeydown="if(event.key==='Enter' && !event.shiftKey) { event.preventDefault(); submitReply('${type}', '${id}', '${post.id}'); }" oninput="this.style.height='auto';this.style.height=Math.min(this.scrollHeight,100)+'px';"></textarea>
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
      <div style="display:flex;align-items:center;gap:12px;padding:16px 20px;border-bottom:1px solid rgba(255,255,255,0.1);background:var(--ui-card-bg);flex-shrink:0;">
        <button onclick="closeDiscussionAndReturnToPopup()" style="background:none;border:none;color:var(--ui-text-muted);font-size:20px;cursor:pointer;padding:4px;border-radius:50%;width:36px;height:36px;display:flex;align-items:center;justify-content:center;transition:all 0.15s;" onmouseover="this.style.background='rgba(255,255,255,0.1)';this.style.color='#fff'" onmouseout="this.style.background='none';this.style.color='var(--ui-text-muted)'">←</button>
        <div style="flex:1;">
          <div style="font-weight:600;font-size:16px;color:var(--ui-text-main);">Discussion</div>
          <div style="font-size:13px;color:var(--ui-text-muted);">${escapeHtml(itemTitle)}</div>
        </div>
        <button onclick="closePublishModal()" style="background:none;border:none;color:var(--ui-text-muted);font-size:20px;cursor:pointer;padding:4px;border-radius:50%;width:36px;height:36px;display:flex;align-items:center;justify-content:center;transition:all 0.15s;" onmouseover="this.style.background='rgba(239,68,68,0.2)';this.style.color='#ef4444'" onmouseout="this.style.background='none';this.style.color='var(--ui-text-muted)'">✕</button>
      </div>
      
      <!-- Zone de scroll avec posts -->
      <div id="discussion-posts-container" style="flex:1;overflow-y:auto;overflow-x:hidden;padding:16px 20px;background:#18191a;">
        ${posts.length > 0 ? posts.map(p => renderPost(p)).join('') : `
          <div style="text-align:center;padding:80px 20px;color:var(--ui-text-muted);font-size:14px;">
            <div style="font-size:64px;margin-bottom:16px;opacity:0.5;">💬</div>
            <div style="font-weight:600;margin-bottom:8px;color:var(--ui-text-main);font-size:16px;">Aucune publication</div>
            <div style="font-size:13px;">Soyez le premier à partager quelque chose !</div>
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
            <textarea id="discussion-input" placeholder="Écrivez un commentaire..." style="width:100%;min-height:38px;max-height:120px;padding:8px 12px;border-radius:20px;border:none;background:rgba(58,59,60,0.8);color:#e4e6eb;font-size:15px;resize:none;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;line-height:1.33;" onkeydown="if(event.key==='Enter' && !event.shiftKey) { event.preventDefault(); submitDiscussionComment('${type}', '${id}'); }" oninput="this.style.height='auto';this.style.height=Math.min(this.scrollHeight,120)+'px';"></textarea>
          </div>
          <button onclick="submitDiscussionComment('${type}', '${id}')" style="padding:8px 16px;border-radius:18px;border:none;background:#1877f2;color:#fff;cursor:pointer;font-size:14px;font-weight:600;transition:all 0.2s;flex-shrink:0;" onmouseover="this.style.background='#166fe5'" onmouseout="this.style.background='#1877f2'">
            Publier
          </button>
        </div>
      </div>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
  document.getElementById("publish-modal-backdrop").style.display = "flex";
  
  // Focus sur le textarea
  setTimeout(() => {
    const input = document.getElementById("discussion-input");
    if (input) input.focus();
  }, 100);
}

// Fermer la discussion et retourner à la popup de l'événement
function closeDiscussionAndReturnToPopup() {
  const type = window.currentDiscussionType;
  const id = window.currentDiscussionId;
  
  if (type && id) {
    const item = getItemById(type, id);
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
        // Réouvrir la popup de l'événement
        openPopupModal(popupHtml, item);
      }
    }
  }
  
  // Fermer la modal de discussion
  closePublishModal();
}

window.closeDiscussionAndReturnToPopup = closeDiscussionAndReturnToPopup;

// Fonction pour soumettre un post (style Facebook) - reste dans la discussion
window.submitDiscussionComment = function(type, id) {
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
  
  const postsKey = `discussion_${type}_${id}`;
  let posts = JSON.parse(localStorage.getItem(postsKey) || '[]');
  posts.unshift(post); // Ajouter au début pour afficher les plus récents en premier
  localStorage.setItem(postsKey, JSON.stringify(posts));
  
  // Vider le champ de saisie et réinitialiser la hauteur
  input.value = '';
  input.style.height = 'auto';
  
  // Rafraîchir uniquement la liste des posts sans fermer la modal
  const postsContainer = document.getElementById("discussion-posts-container");
  if (postsContainer) {
    // Recharger les posts depuis localStorage
    const updatedPosts = JSON.parse(localStorage.getItem(postsKey) || '[]');
    
    // Reconstruire le HTML des posts
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
    
    // Fonction renderReply (doit être redéfinie ici pour le contexte)
    const renderReply = (reply, postId, parentPath = '', depth = 0) => {
      const replyPath = parentPath ? `${parentPath}-${reply.id}` : reply.id;
      const avatarSize = depth === 0 ? 32 : 28;
      
      return `
        <div style="margin-bottom:${reply.replies && reply.replies.length > 0 ? '8px' : '12px'};">
          <div style="display:flex;gap:8px;">
            <div style="width:${avatarSize}px;height:${avatarSize}px;border-radius:50%;background:linear-gradient(135deg,#1877f2,#42a5f5);display:flex;align-items:center;justify-content:center;font-size:${avatarSize === 32 ? '14px' : '12px'};flex-shrink:0;font-weight:700;color:#fff;">
              ${reply.avatar || '👤'}
            </div>
            <div style="flex:1;">
              <div style="background:#3a3b3c;border-radius:12px;padding:8px 12px;margin-bottom:4px;">
                <div style="display:flex;align-items:center;gap:6px;margin-bottom:2px;">
                  <span style="font-weight:600;font-size:13px;color:#e4e6eb;">${escapeHtml(reply.author || 'Utilisateur')}</span>
                  <span style="font-size:12px;color:#b0b3b8;">${formatTime(reply.timestamp || Date.now())}</span>
                </div>
                <div style="font-size:14px;color:#e4e6eb;line-height:1.33;white-space:pre-wrap;word-wrap:break-word;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">${escapeHtml(reply.text)}</div>
              </div>
              <button onclick="showReplyForm('${postId}', '${replyPath}')" style="display:flex;align-items:center;gap:4px;background:none;border:none;color:#b0b3b8;font-size:12px;font-weight:600;cursor:pointer;padding:4px 8px;border-radius:4px;transition:all 0.15s;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='none'">
                <span>Répondre</span>
              </button>
            </div>
          </div>
          <div id="reply-form-${postId}-${replyPath}" style="display:none;margin-left:${avatarSize + 8}px;margin-top:8px;">
            <div style="display:flex;gap:8px;align-items:flex-start;">
              <div style="width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#1877f2,#42a5f5);display:flex;align-items:center;justify-content:center;font-size:12px;flex-shrink:0;font-weight:700;color:#fff;">
                ${currentUser?.avatar || '👤'}
              </div>
              <div style="flex:1;position:relative;">
                <textarea id="reply-input-${postId}-${replyPath}" placeholder="Répondre à ${escapeHtml(reply.author || 'Utilisateur')}..." style="width:100%;min-height:36px;max-height:100px;padding:8px 12px;border-radius:20px;border:none;background:rgba(58,59,60,0.8);color:#e4e6eb;font-size:14px;resize:none;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;line-height:1.33;" onkeydown="if(event.key==='Enter' && !event.shiftKey) { event.preventDefault(); submitReply('${type}', '${id}', '${postId}', '${replyPath}'); }" oninput="this.style.height='auto';this.style.height=Math.min(this.scrollHeight,100)+'px';"></textarea>
              </div>
            </div>
          </div>
          ${reply.replies && reply.replies.length > 0 ? `
            <div style="margin-left:${avatarSize + 8}px;margin-top:8px;">
              ${reply.replies.map(nestedReply => renderReply(nestedReply, postId, replyPath, depth + 1)).join('')}
            </div>
          ` : ''}
        </div>
      `;
    };
    
    const renderPost = (post) => {
      const isLiked = (post.likes || []).includes(currentUser?.id || currentUser?.username);
      const likesCount = post.likes ? post.likes.length : 0;
      const repliesCount = post.replies ? post.replies.length : 0;
      
      return `
        <div style="background:#242526;border-radius:8px;padding:12px;margin-bottom:12px;">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            <div style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#1877f2,#42a5f5);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;font-weight:700;color:#fff;">
              ${post.avatar || '👤'}
            </div>
            <div style="flex:1;">
              <div style="font-weight:600;font-size:15px;color:#e4e6eb;line-height:1.2;">${escapeHtml(post.author || 'Utilisateur')}</div>
              <div style="font-size:13px;color:#b0b3b8;line-height:1.2;">${formatTime(post.timestamp || Date.now())}</div>
            </div>
          </div>
          <div style="font-size:15px;color:#e4e6eb;line-height:1.33;margin-bottom:8px;white-space:pre-wrap;word-wrap:break-word;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">${escapeHtml(post.text)}</div>
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
          <div style="display:flex;align-items:center;gap:4px;padding:4px 0;border-top:1px solid rgba(255,255,255,0.1);">
            <button onclick="togglePostLike('${type}', '${id}', '${post.id}')" style="flex:1;display:flex;align-items:center;justify-content:center;gap:6px;background:none;border:none;color:${isLiked ? '#1877f2' : '#b0b3b8'};font-size:14px;font-weight:600;cursor:pointer;padding:6px;border-radius:4px;transition:all 0.15s;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='none'">
              <span style="font-size:18px;">👍</span>
              <span>J'aime</span>
            </button>
            <button onclick="showReplyForm('${post.id}')" style="flex:1;display:flex;align-items:center;justify-content:center;gap:6px;background:none;border:none;color:#b0b3b8;font-size:14px;font-weight:600;cursor:pointer;padding:6px;border-radius:4px;transition:all 0.15s;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='none'">
              <span style="font-size:18px;">💬</span>
              <span>Commenter</span>
            </button>
          </div>
          <div id="reply-form-${post.id}" style="display:none;margin-top:8px;padding-top:8px;">
            <div style="display:flex;gap:8px;align-items:flex-start;">
              <div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#1877f2,#42a5f5);display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;font-weight:700;color:#fff;">
                ${currentUser?.avatar || '👤'}
              </div>
              <div style="flex:1;position:relative;">
                <textarea id="reply-input-${post.id}" placeholder="Écrivez un commentaire..." style="width:100%;min-height:36px;max-height:100px;padding:8px 12px;border-radius:20px;border:none;background:rgba(58,59,60,0.8);color:#e4e6eb;font-size:14px;resize:none;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;line-height:1.33;" onkeydown="if(event.key==='Enter' && !event.shiftKey) { event.preventDefault(); submitReply('${type}', '${id}', '${post.id}'); }" oninput="this.style.height='auto';this.style.height=Math.min(this.scrollHeight,100)+'px';"></textarea>
              </div>
            </div>
          </div>
          ${post.replies && post.replies.length > 0 ? `
            <div style="margin-top:8px;padding-left:48px;">
              ${post.replies.map(reply => renderReply(reply, post.id, '', 0)).join('')}
            </div>
          ` : ''}
        </div>
      `;
    };
    
    postsContainer.innerHTML = updatedPosts.length > 0 
      ? updatedPosts.map(p => renderPost(p)).join('')
      : `
        <div style="text-align:center;padding:80px 20px;color:var(--ui-text-muted);font-size:14px;">
          <div style="font-size:64px;margin-bottom:16px;opacity:0.5;">💬</div>
          <div style="font-weight:600;margin-bottom:8px;color:var(--ui-text-main);font-size:16px;">Aucune publication</div>
          <div style="font-size:13px;">Soyez le premier à partager quelque chose !</div>
        </div>
      `;
    
    // Scroll vers le haut pour voir le nouveau post
    postsContainer.scrollTop = 0;
    
    // Remettre le focus sur le textarea
    setTimeout(() => {
      if (input) input.focus();
    }, 100);
  } else {
    // Si le container n'existe pas, réouvrir la modal
    openDiscussionModal(type, id);
  }
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
window.submitReply = function(type, id, postId, replyPath = null) {
  const inputId = replyPath ? `reply-input-${postId}-${replyPath}` : `reply-input-${postId}`;
  const input = document.getElementById(inputId);
  if (!input || !input.value.trim()) return;
  
  const reply = {
    id: Date.now().toString(),
    author: currentUser?.name || currentUser?.username || 'Utilisateur',
    avatar: currentUser?.avatar || '👤',
    text: input.value.trim(),
    timestamp: Date.now(),
    replies: [] // Permet les réponses imbriquées illimitées
  };
  
  const postsKey = `discussion_${type}_${id}`;
  let posts = JSON.parse(localStorage.getItem(postsKey) || '[]');
  const post = posts.find(p => p.id === postId);
  
  if (post) {
    if (replyPath) {
      // Répondre à une réponse existante (peut être à n'importe quel niveau)
      const pathArray = replyPath.split('-');
      const parentReply = findReplyByPath(post.replies || [], pathArray);
      
      if (parentReply) {
        if (!parentReply.replies) parentReply.replies = [];
        parentReply.replies.push(reply);
      }
    } else {
      // Répondre directement au post
      if (!post.replies) post.replies = [];
      post.replies.push(reply);
    }
    
    localStorage.setItem(postsKey, JSON.stringify(posts));
    
    // Masquer le formulaire et vider le champ
    hideReplyForm(postId, replyPath);
    
    // Rafraîchir uniquement la liste des posts sans fermer la modal
    const postsContainer = document.getElementById("discussion-posts-container");
    if (postsContainer) {
      // Recharger les posts depuis localStorage
      const updatedPosts = JSON.parse(localStorage.getItem(postsKey) || '[]');
      
      // Reconstruire le HTML (même logique que dans submitDiscussionComment)
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
      
      const renderReply = (reply, postId, parentPath = '', depth = 0) => {
        const replyPath = parentPath ? `${parentPath}-${reply.id}` : reply.id;
        const avatarSize = depth === 0 ? 32 : 28;
        
        return `
          <div style="margin-bottom:${reply.replies && reply.replies.length > 0 ? '8px' : '12px'};">
            <div style="display:flex;gap:8px;">
              <div style="width:${avatarSize}px;height:${avatarSize}px;border-radius:50%;background:linear-gradient(135deg,#1877f2,#42a5f5);display:flex;align-items:center;justify-content:center;font-size:${avatarSize === 32 ? '14px' : '12px'};flex-shrink:0;font-weight:700;color:#fff;">
                ${reply.avatar || '👤'}
              </div>
              <div style="flex:1;">
                <div style="background:#3a3b3c;border-radius:12px;padding:8px 12px;margin-bottom:4px;">
                  <div style="display:flex;align-items:center;gap:6px;margin-bottom:2px;">
                    <span style="font-weight:600;font-size:13px;color:#e4e6eb;">${escapeHtml(reply.author || 'Utilisateur')}</span>
                    <span style="font-size:12px;color:#b0b3b8;">${formatTime(reply.timestamp || Date.now())}</span>
                  </div>
                  <div style="font-size:14px;color:#e4e6eb;line-height:1.33;white-space:pre-wrap;word-wrap:break-word;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">${escapeHtml(reply.text)}</div>
                </div>
                <button onclick="showReplyForm('${postId}', '${replyPath}')" style="display:flex;align-items:center;gap:4px;background:none;border:none;color:#b0b3b8;font-size:12px;font-weight:600;cursor:pointer;padding:4px 8px;border-radius:4px;transition:all 0.15s;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='none'">
                  <span>Répondre</span>
                </button>
              </div>
            </div>
            <div id="reply-form-${postId}-${replyPath}" style="display:none;margin-left:${avatarSize + 8}px;margin-top:8px;">
              <div style="display:flex;gap:8px;align-items:flex-start;">
                <div style="width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#1877f2,#42a5f5);display:flex;align-items:center;justify-content:center;font-size:12px;flex-shrink:0;font-weight:700;color:#fff;">
                  ${currentUser?.avatar || '👤'}
                </div>
                <div style="flex:1;position:relative;">
                  <textarea id="reply-input-${postId}-${replyPath}" placeholder="Répondre à ${escapeHtml(reply.author || 'Utilisateur')}..." style="width:100%;min-height:36px;max-height:100px;padding:8px 12px;border-radius:20px;border:none;background:rgba(58,59,60,0.8);color:#e4e6eb;font-size:14px;resize:none;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;line-height:1.33;" onkeydown="if(event.key==='Enter' && !event.shiftKey) { event.preventDefault(); submitReply('${type}', '${id}', '${postId}', '${replyPath}'); }" oninput="this.style.height='auto';this.style.height=Math.min(this.scrollHeight,100)+'px';"></textarea>
                </div>
              </div>
            </div>
            ${reply.replies && reply.replies.length > 0 ? `
              <div style="margin-left:${avatarSize + 8}px;margin-top:8px;">
                ${reply.replies.map(nestedReply => renderReply(nestedReply, postId, replyPath, depth + 1)).join('')}
              </div>
            ` : ''}
          </div>
        `;
      };
      
      const renderPost = (post) => {
        const isLiked = (post.likes || []).includes(currentUser?.id || currentUser?.username);
        const likesCount = post.likes ? post.likes.length : 0;
        const repliesCount = post.replies ? post.replies.length : 0;
        
        return `
          <div style="background:#242526;border-radius:8px;padding:12px;margin-bottom:12px;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
              <div style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#1877f2,#42a5f5);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;font-weight:700;color:#fff;">
                ${post.avatar || '👤'}
              </div>
              <div style="flex:1;">
                <div style="font-weight:600;font-size:15px;color:#e4e6eb;line-height:1.2;">${escapeHtml(post.author || 'Utilisateur')}</div>
                <div style="font-size:13px;color:#b0b3b8;line-height:1.2;">${formatTime(post.timestamp || Date.now())}</div>
              </div>
            </div>
            <div style="font-size:15px;color:#e4e6eb;line-height:1.33;margin-bottom:8px;white-space:pre-wrap;word-wrap:break-word;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">${escapeHtml(post.text)}</div>
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
            <div style="display:flex;align-items:center;gap:4px;padding:4px 0;border-top:1px solid rgba(255,255,255,0.1);">
              <button onclick="togglePostLike('${type}', '${id}', '${post.id}')" style="flex:1;display:flex;align-items:center;justify-content:center;gap:6px;background:none;border:none;color:${isLiked ? '#1877f2' : '#b0b3b8'};font-size:14px;font-weight:600;cursor:pointer;padding:6px;border-radius:4px;transition:all 0.15s;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='none'">
                <span style="font-size:18px;">👍</span>
                <span>J'aime</span>
              </button>
              <button onclick="showReplyForm('${post.id}')" style="flex:1;display:flex;align-items:center;justify-content:center;gap:6px;background:none;border:none;color:#b0b3b8;font-size:14px;font-weight:600;cursor:pointer;padding:6px;border-radius:4px;transition:all 0.15s;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='none'">
                <span style="font-size:18px;">💬</span>
                <span>Commenter</span>
              </button>
            </div>
            <div id="reply-form-${post.id}" style="display:none;margin-top:8px;padding-top:8px;">
              <div style="display:flex;gap:8px;align-items:flex-start;">
                <div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#1877f2,#42a5f5);display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;font-weight:700;color:#fff;">
                  ${currentUser?.avatar || '👤'}
                </div>
                <div style="flex:1;position:relative;">
                  <textarea id="reply-input-${post.id}" placeholder="Écrivez un commentaire..." style="width:100%;min-height:36px;max-height:100px;padding:8px 12px;border-radius:20px;border:none;background:rgba(58,59,60,0.8);color:#e4e6eb;font-size:14px;resize:none;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;line-height:1.33;" onkeydown="if(event.key==='Enter' && !event.shiftKey) { event.preventDefault(); submitReply('${type}', '${id}', '${post.id}'); }" oninput="this.style.height='auto';this.style.height=Math.min(this.scrollHeight,100)+'px';"></textarea>
                </div>
              </div>
            </div>
            ${post.replies && post.replies.length > 0 ? `
              <div style="margin-top:8px;padding-left:48px;">
                ${post.replies.map(reply => renderReply(reply, post.id, '', 0)).join('')}
              </div>
            ` : ''}
          </div>
        `;
      };
      
      postsContainer.innerHTML = updatedPosts.length > 0 
        ? updatedPosts.map(p => renderPost(p)).join('')
        : `
          <div style="text-align:center;padding:80px 20px;color:var(--ui-text-muted);font-size:14px;">
            <div style="font-size:64px;margin-bottom:16px;opacity:0.5;">💬</div>
            <div style="font-weight:600;margin-bottom:8px;color:var(--ui-text-main);font-size:16px;">Aucune publication</div>
            <div style="font-size:13px;">Soyez le premier à partager quelque chose !</div>
          </div>
        `;
    } else {
      // Si le container n'existe pas, réouvrir la modal
      openDiscussionModal(type, id);
    }
  }
};

// Fonction pour liker/unliker un post
window.togglePostLike = function(type, id, postId) {
  const postsKey = `discussion_${type}_${id}`;
  let posts = JSON.parse(localStorage.getItem(postsKey) || '[]');
  const post = posts.find(p => p.id === postId);
  
  if (post) {
    if (!post.likes) post.likes = [];
    const userId = currentUser?.id || currentUser?.username;
    const index = post.likes.indexOf(userId);
    
    if (index > -1) {
      // Retirer le like
      post.likes.splice(index, 1);
    } else {
      // Ajouter le like
      post.likes.push(userId);
    }
    
    localStorage.setItem(postsKey, JSON.stringify(posts));
    
    // Réouvrir le modal pour afficher le changement
    openDiscussionModal(type, id);
  }
};

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
  document.getElementById("publish-modal-backdrop").style.display = "flex";
}

async function submitReport(type, id, parentType = null, parentId = null) {
  if (!currentUser.isLoggedIn) {
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
    const response = await fetch(`${API_BASE_URL}/user/reports`, {
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
  document.getElementById("publish-modal-backdrop").style.display = "flex";
}

// Son de paiement
function playPaymentSound() {
  try {
    const audio = new Audio('./assets/popopo.m4a');
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
    document.getElementById("publish-modal-backdrop").style.display = "flex";
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
  document.getElementById("publish-modal-backdrop").style.display = "flex";
}

async function processCartCheckout() {
  if (cart.length === 0) return;
  
  if (!currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  
  const total = cart.reduce((sum, item) => sum + item.price, 0);
  const count = cart.length;
  
  try {
    showNotification("💳 Redirection vers le paiement...", "info");
    
    // Créer une session Stripe Checkout
    const response = await fetch(`${API_BASE_URL}/payments/create-checkout-session`, {
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
  if (!currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  
  try {
    showNotification("💳 Redirection vers le paiement...", "info");
    
    // Créer une session Stripe Checkout
    const response = await fetch(`${API_BASE_URL}/payments/create-checkout-session`, {
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

function showAgendaMiniWindow() {
  const agendaItems = currentUser.agenda.map(key => {
    const [type, id] = key.split(":");
    const data = type === "event" ? eventsData : type === "booking" ? bookingsData : servicesData;
    return data.find(i => i.id === parseInt(id));
  }).filter(Boolean);

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

// Mettre à jour le bouton Compte avec l'avatar et le nom de l'utilisateur
function updateAccountButton() {
  const accountBtn = document.getElementById("account-topbar-btn");
  const avatarEl = document.getElementById("account-avatar");
  const nameEl = document.getElementById("account-name");
  
  if (accountBtn && avatarEl && nameEl) {
    // Afficher le nom d'utilisateur si connecté, sinon "Compte"
    if (currentUser.isLoggedIn) {
      // PRIORITÉ: username > name > email > "Compte"
      const displayName = currentUser.username || currentUser.name || currentUser.email?.split('@')[0] || "Compte";
      nameEl.textContent = displayName.length > 14 ? displayName.substring(0, 14) + "..." : displayName;
    } else {
      nameEl.textContent = "Compte";
    }
    
    // Mettre à jour l'avatar si connecté
    if (currentUser.isLoggedIn) {
      // Utiliser la photo de profil si disponible, sinon l'avatar emoji
      // PRIORITÉ: profilePhoto > profile_photo_url > avatar (qui peut être une URL Google)
      let avatarUrl = currentUser.profilePhoto || currentUser.profile_photo_url || currentUser.avatar;
      
      // Si avatar est une URL (Google picture), l'utiliser si pas de profilePhoto
      if (!currentUser.profilePhoto && !currentUser.profile_photo_url && currentUser.avatar && 
          (currentUser.avatar.startsWith('http') || currentUser.avatar.startsWith('data:image'))) {
        avatarUrl = currentUser.avatar;
      }
      
      // Réduire la taille de l'avatar pour correspondre aux blocs booking/service
      // Les blocs ont une hauteur d'image de 160px, mais l'avatar doit être plus petit
      avatarEl.style.width = '32px';
      avatarEl.style.height = '32px';
      avatarEl.style.borderRadius = '50%';
      avatarEl.style.display = 'flex';
      avatarEl.style.alignItems = 'center';
      avatarEl.style.justifyContent = 'center';
      avatarEl.style.fontSize = '16px';
      avatarEl.style.overflow = 'hidden';
      avatarEl.style.flexShrink = '0';
      
      if (avatarUrl && (avatarUrl.startsWith('http') || avatarUrl.startsWith('data:image'))) {
        // C'est une URL d'image (http ou base64)
        const existingImg = avatarEl.querySelector('img');
        if (!existingImg) {
          const img = document.createElement('img');
          img.src = avatarUrl;
          img.style.width = '100%';
          img.style.height = '100%';
          img.style.borderRadius = '50%';
          img.style.objectFit = 'cover';
          img.onerror = function() {
            // Si l'image ne charge pas, afficher l'emoji
            avatarEl.innerHTML = currentUser.avatar || "👤";
            avatarEl.style.fontSize = '16px';
          };
          avatarEl.innerHTML = '';
          avatarEl.appendChild(img);
        } else {
          // Mettre à jour l'image existante seulement si l'URL a changé
          if (existingImg.src !== avatarUrl) {
            existingImg.src = avatarUrl;
            existingImg.onerror = function() {
              // Si l'image ne charge pas, afficher l'emoji
              avatarEl.innerHTML = currentUser.avatar || "👤";
              avatarEl.style.fontSize = '16px';
            };
          }
        }
      } else {
        // C'est un emoji ou texte
        avatarEl.innerHTML = '';
        avatarEl.textContent = avatarUrl || currentUser.avatar || "👤";
      }
    } else {
      avatarEl.innerHTML = '';
      avatarEl.textContent = "👤";
    }
  }
  
  // Mettre à jour aussi l'avatar dans le modal compte si ouvert
  const modalInner = document.getElementById("publish-modal-inner");
  if (modalInner && currentUser.isLoggedIn) {
    // Chercher l'avatar dans le header du modal compte
    const headerAvatar = modalInner.querySelector('[data-account-avatar="true"]');
    if (headerAvatar) {
      if (currentUser.profilePhoto) {
        headerAvatar.style.backgroundImage = `url(${currentUser.profilePhoto})`;
        headerAvatar.style.backgroundSize = 'cover';
        headerAvatar.style.backgroundPosition = 'center';
        headerAvatar.innerHTML = '';
      } else {
        headerAvatar.style.backgroundImage = 'none';
        headerAvatar.innerHTML = currentUser.avatar || "👤";
      }
    }
  }
}

// Exposer la fonction globalement
window.updateAccountButton = updateAccountButton;

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
  document.getElementById("publish-modal-backdrop").style.display = "flex";
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
  document.getElementById("publish-modal-backdrop").style.display = "flex";
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
  document.getElementById("publish-modal-backdrop").style.display = "flex";
  
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
  if (!currentUser.isLoggedIn) {
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
  document.getElementById("publish-modal-backdrop").style.display = "flex";
  
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
  if (!currentUser.isLoggedIn || !currentUser.eventAlarms || currentUser.eventAlarms.length === 0) {
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
  if (currentUser.isLoggedIn && currentUser.eventAlarms) {
    const eventIds = new Set(eventsData.map(e => e.id.toString()));
    const beforeAlarmsCount = currentUser.eventAlarms.length;
    currentUser.eventAlarms = currentUser.eventAlarms.filter(alarm => eventIds.has(alarm.eventId));
    const afterAlarmsCount = currentUser.eventAlarms.length;
    
    if (beforeAlarmsCount !== afterAlarmsCount) {
      saveUser();
    }
  }
  
  // Nettoyer aussi l'agenda des événements supprimés
  if (currentUser.isLoggedIn && currentUser.agenda) {
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

// Mise à jour de l'UI utilisateur
function updateUserUI() {
  // Mettre à jour le bouton Compte avec avatar et nom
  const accountAvatar = document.getElementById("account-avatar");
  const accountName = document.getElementById("account-name");
  
  if (currentUser.isLoggedIn && currentUser.avatar) {
    if (accountAvatar) accountAvatar.textContent = currentUser.avatar;
    if (accountName) {
      // PRIORITÉ: username > name > "Compte"
      const displayName = currentUser.username || currentUser.name || "Compte";
      accountName.textContent = displayName.length > 14 ? displayName.substring(0, 14) + "..." : displayName;
    }
  } else {
    if (accountAvatar) accountAvatar.textContent = "👤";
    if (accountName) accountName.textContent = "Compte";
  }
}

// ============================================
// SYSTÈME D'ABONNEMENTS & ALERTES
// ============================================

// Obtenir le nombre d'utilisateurs actifs depuis l'API
async function getActiveUsersCount() {
  try {
    const response = await fetch(`${API_BASE_URL}/stats/active-users`, {
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
}

function openSubscriptionModal() {
  const currentSub = currentUser.subscription || "free";
  const maxAgenda = getAgendaLimit();
  const maxAlerts = getAlertLimit();
  const alertText = maxAlerts === Infinity ? "∞" : maxAlerts;
  
  const html = `
    <div style="padding:10px;max-height:90vh;overflow-y:auto;">
      <h2 style="margin:0 0 16px;font-size:18px;text-align:center;">💎 Abonnements</h2>
      <p style="text-align:center;color:var(--ui-text-muted);margin-bottom:20px;font-size:12px;">
        Choisissez votre formule selon vos besoins !
      </p>
      
      <div style="margin-bottom:16px;">
        <div style="font-size:13px;font-weight:600;color:#00ffc3;margin-bottom:8px;text-align:center;">🎉 Pour les utilisateurs d'événements</div>
        <div style="display:grid;gap:10px;margin-bottom:16px;">
          <div style="padding:14px;border-radius:12px;border:2px solid ${currentSub === 'events-explorer' ? '#22c55e' : '#22c55e'};background:rgba(34,197,94,0.05);cursor:pointer;position:relative;overflow:hidden;${currentSub === 'events-explorer' ? 'box-shadow:0 0 15px rgba(34,197,94,0.3);' : ''}" onclick="selectPlan('events-explorer')">
            ${currentSub === 'events-explorer' ? '<div style="position:absolute;top:0;right:0;background:#22c55e;color:#fff;padding:2px 10px;font-size:9px;font-weight:700;border-bottom-left-radius:8px;">ACTIF</div>' : '<div style="position:absolute;top:0;right:0;background:#22c55e;color:#fff;padding:2px 10px;font-size:9px;font-weight:700;border-bottom-left-radius:8px;">POPULAIRE</div>'}
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
              <span style="font-weight:700;font-size:14px;">🌱 Events Explorer</span>
              <span style="color:#22c55e;font-weight:700;font-size:14px;">CHF 5.–/mois</span>
            </div>
            <ul style="margin:0;padding-left:18px;font-size:11px;color:var(--ui-text-muted);line-height:1.6;">
              <li><strong>10 alertes personnalisées/mois</strong></li>
              <li><strong>10 alarmes</strong></li>
              <li>Notifications instantanées</li>
              <li><strong>Agenda 50 places</strong> (vs 20 gratuit)</li>
              <li>Écoute des sons booking illimités</li>
            </ul>
          </div>
          
          <div style="padding:14px;border-radius:12px;border:2px solid ${currentSub === 'events-alerts-pro' ? '#3b82f6' : '#3b82f6'};background:rgba(59,130,246,0.05);cursor:pointer;position:relative;overflow:hidden;${currentSub === 'events-alerts-pro' ? 'box-shadow:0 0 15px rgba(59,130,246,0.3);' : ''}" onclick="selectPlan('events-alerts-pro')">
            ${currentSub === 'events-alerts-pro' ? '<div style="position:absolute;top:0;right:0;background:#3b82f6;color:#fff;padding:2px 10px;font-size:9px;font-weight:700;border-bottom-left-radius:8px;">ACTIF</div>' : '<div style="position:absolute;top:0;right:0;background:#3b82f6;color:#fff;padding:2px 10px;font-size:9px;font-weight:700;border-bottom-left-radius:8px;">ALERTES</div>'}
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
              <span style="font-weight:700;font-size:14px;">🔔 Events Alertes Pro</span>
              <span style="color:#3b82f6;font-weight:700;font-size:14px;">CHF 10.–/mois</span>
            </div>
            <ul style="margin:0;padding-left:18px;font-size:11px;color:var(--ui-text-muted);line-height:1.6;">
              <li><strong>Tout de Events Explorer +</strong></li>
              <li><strong>Alertes jusqu'à 200</strong> avec notifications push + email</li>
              <li><strong>Agenda jusqu'à 200 places</strong></li>
            </ul>
          </div>
        </div>
      </div>
      
      <div style="margin-bottom:16px;">
        <div style="font-size:13px;font-weight:600;color:#a78bfa;margin-bottom:8px;text-align:center;">🎤 Pour les professionnels</div>
        <div style="display:grid;gap:10px;margin-bottom:16px;">
          <div style="padding:14px;border-radius:12px;border:2px solid ${currentSub === 'service-pro' ? '#8b5cf6' : '#8b5cf6'};background:rgba(139,92,246,0.05);cursor:pointer;position:relative;overflow:hidden;${currentSub === 'service-pro' ? 'box-shadow:0 0 15px rgba(139,92,246,0.3);' : ''}" onclick="selectPlan('service-pro')">
            ${currentSub === 'service-pro' ? '<div style="position:absolute;top:0;right:0;background:#8b5cf6;color:#fff;padding:2px 10px;font-size:9px;font-weight:700;border-bottom-left-radius:8px;">ACTIF</div>' : ''}
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
              <span style="font-weight:700;font-size:14px;">💼 Service Pro</span>
              <span style="color:#8b5cf6;font-weight:700;font-size:14px;">CHF 10.–/mois</span>
            </div>
            <ul style="margin:0;padding-left:18px;font-size:11px;color:var(--ui-text-muted);line-height:1.6;">
              <li><strong>Tout de Events Explorer</strong></li>
              <li><strong>Contacts illimités</strong> - voit toutes les infos directement</li>
              <li><strong>Badge Pro</strong> visible sur avatar</li>
              <li>Support prioritaire</li>
            </ul>
          </div>
          
          <div style="padding:14px;border-radius:12px;border:2px solid ${currentSub === 'service-ultra' ? '#a78bfa' : '#a78bfa'};background:rgba(167,139,250,0.05);cursor:pointer;position:relative;overflow:hidden;${currentSub === 'service-ultra' ? 'box-shadow:0 0 15px rgba(167,139,250,0.3);' : ''}" onclick="selectPlan('service-ultra')">
            ${currentSub === 'service-ultra' ? '<div style="position:absolute;top:0;right:0;background:#a78bfa;color:#fff;padding:2px 10px;font-size:9px;font-weight:700;border-bottom-left-radius:8px;">ACTIF</div>' : '<div style="position:absolute;top:0;right:0;background:#a78bfa;color:#fff;padding:2px 10px;font-size:9px;font-weight:700;border-bottom-left-radius:8px;">ULTRA</div>'}
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
              <span style="font-weight:700;font-size:14px;">🚀 Service Ultra</span>
              <span style="color:#a78bfa;font-weight:700;font-size:14px;">CHF 18.–/mois</span>
            </div>
            <ul style="margin:0;padding-left:18px;font-size:11px;color:var(--ui-text-muted);line-height:1.6;">
              <li>Tout de Pro +</li>
              <li><strong>Accès API</strong> pour développeurs</li>
              <li><strong>Ajout automatique d'events</strong> pour organisateurs</li>
              <li>Contacts infos illimités</li>
              <li><strong>Statistiques avancées</strong></li>
              <li><strong>5 events gratuits / mois placés OR</strong></li>
              <li>Support 24/7</li>
            </ul>
          </div>
        </div>
      </div>
      
      <div style="margin-bottom:20px;">
        <div style="font-size:13px;font-weight:600;color:#ffd700;margin-bottom:8px;text-align:center;">⭐ Tout compris</div>
        <div style="padding:16px;border-radius:12px;border:2px solid ${currentSub === 'full-premium' ? '#ffd700' : '#ffd700'};background:linear-gradient(135deg,rgba(255,215,0,0.15),rgba(255,215,0,0.05));cursor:pointer;position:relative;overflow:hidden;${currentSub === 'full-premium' ? 'box-shadow:0 0 20px rgba(255,215,0,0.4);' : ''}" onclick="selectPlan('full-premium')">
          ${currentSub === 'full-premium' ? '<div style="position:absolute;top:0;right:0;background:#ffd700;color:#000;padding:2px 12px;font-size:10px;font-weight:700;border-bottom-left-radius:8px;">ACTIF</div>' : '<div style="position:absolute;top:0;right:0;background:#ffd700;color:#000;padding:2px 12px;font-size:10px;font-weight:700;border-bottom-left-radius:8px;">TOP</div>'}
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span style="font-weight:700;font-size:16px;">👑 Full Premium</span>
            <span style="color:#ffd700;font-weight:700;font-size:16px;">CHF 25.–/mois</span>
          </div>
          <ul style="margin:0;padding-left:20px;font-size:12px;color:var(--ui-text-muted);line-height:1.8;">
            <li><strong>Tout de Events Alertes Pro, Tout de Service Ultra</strong></li>
            <li><strong>Agenda 250 places</strong></li>
            <li><strong>Alertes 250</strong> avec notifications push + email</li>
            <li><strong>Alarmes 250 places</strong></li>
            <li><strong>Contacts illimités</strong> partout</li>
            <li><strong>Accès API complet</strong> et facilité pour poser tous les events</li>
            <li><strong>Statistiques ultras avancées</strong></li>
            <li>Support 24/7 prioritaire</li>
          </ul>
        </div>
      </div>
      
      <div style="background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.3);border-radius:12px;padding:12px;margin-bottom:20px;">
        <div style="font-size:12px;font-weight:600;color:#22c55e;margin-bottom:6px;">🌍 70% de vos paiements vont à la Mission Planète</div>
        <div style="font-size:11px;color:var(--ui-text-muted);">Achat de forêts, filtres CO2, protection des océans...</div>
      </div>
      
      
      
      <button onclick="closePublishModal()" style="width:100%;padding:10px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;margin-top:16px;">
        Fermer
      </button>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
  document.getElementById("publish-modal-backdrop").style.display = "flex";
}

function createAlert() {
  const category = document.getElementById("alert-category").value;
  const city = document.getElementById("alert-city").value;
  
  if (!category) {
    showNotification("⚠️ Veuillez sélectionner une catégorie", "warning");
    return;
  }
  
  // Vérifier la limite selon l'abonnement
  const maxAlerts = getAlertLimit();
  if (maxAlerts === 0) {
    showNotification("⚠️ Les alertes nécessitent un abonnement Events Explorer ou supérieur", "warning");
    openSubscriptionModal();
    return;
  }
  
  if (maxAlerts !== Infinity && currentUser.alerts.length >= maxAlerts) {
    showNotification(`⚠️ Limite atteinte (${maxAlerts} alertes) ! Passez à Events Alertes Pro pour des alertes illimitées.`, "warning");
    openSubscriptionModal();
    return;
  }
  
  currentUser.alerts.push({ category, city, createdAt: new Date().toISOString() });
  showNotification("🔔 Alerte créée ! Vous serez notifié des nouveaux événements et changements.", "success");
  openSubscriptionModal(); // Rafraîchir
}

function removeAlert(index) {
  currentUser.alerts.splice(index, 1);
  showNotification("🔕 Alerte supprimée", "info");
  openSubscriptionModal(); // Rafraîchir
}

function selectPlan(plan) {
  if (plan === 'free') {
    currentUser.subscription = "free";
    showNotification("✅ Plan gratuit actif", "info");
    updateSubscriptionBadge();
    openSubscriptionModal();
  } else if (plan === 'events-explorer') {
    openPremiumPaymentModal('events-explorer', 5);
  } else if (plan === 'events-alerts-pro') {
    openPremiumPaymentModal('events-alerts-pro', 10);
  } else if (plan === 'service-pro') {
    openPremiumPaymentModal('service-pro', 10);
  } else if (plan === 'service-ultra') {
    openPremiumPaymentModal('service-ultra', 18);
  } else if (plan === 'full-premium') {
    openPremiumPaymentModal('full-premium', 25);
  }
}

function openPremiumPaymentModal(plan = 'full-premium', price = 25) {
  const planInfo = {
    'events-explorer': { emoji: '🌱', name: 'Events Explorer', color: '#22c55e', bg: 'rgba(34,197,94,0.2)' },
    'events-alerts-pro': { emoji: '🔔', name: 'Events Alertes Pro', color: '#3b82f6', bg: 'rgba(59,130,246,0.2)' },
    'service-pro': { emoji: '💼', name: 'Service Pro', color: '#8b5cf6', bg: 'rgba(139,92,246,0.2)' },
    'service-ultra': { emoji: '🚀', name: 'Service Ultra', color: '#a78bfa', bg: 'rgba(167,139,250,0.2)' },
    'full-premium': { emoji: '👑', name: 'Full Premium', color: '#ffd700', bg: 'rgba(255,215,0,0.2)' },
    // Anciens noms pour compatibilité
    'events-alerts': { emoji: '🔔', name: 'Events Alertes Pro', color: '#3b82f6', bg: 'rgba(59,130,246,0.2)' },
    'booking-pro': { emoji: '💼', name: 'Service Pro', color: '#8b5cf6', bg: 'rgba(139,92,246,0.2)' },
    'booking-ultra': { emoji: '🚀', name: 'Service Ultra', color: '#a78bfa', bg: 'rgba(167,139,250,0.2)' },
    'full': { emoji: '👑', name: 'Full Premium', color: '#ffd700', bg: 'rgba(255,215,0,0.2)' },
    explorer: { emoji: '🌱', name: 'Explorer', color: '#22c55e', bg: 'rgba(34,197,94,0.2)' },
    pro: { emoji: '💼', name: 'Pro', color: '#8b5cf6', bg: 'rgba(139,92,246,0.2)' },
    premium: { emoji: '⭐', name: 'Premium', color: '#ffd700', bg: 'rgba(255,215,0,0.2)' }
  };
  
  const info = planInfo[plan] || planInfo.full;
  
  const html = `
    <div style="padding:10px;text-align:center;">
      <div style="font-size:48px;margin-bottom:16px;">${info.emoji}</div>
      <h2 style="margin:0 0 10px;font-size:20px;">Passer en ${info.name}</h2>
      <p style="color:var(--ui-text-muted);margin-bottom:20px;">
        Débloquez toutes les fonctionnalités ${info.name} !
      </p>
      
      <div style="background:linear-gradient(135deg,${info.bg},transparent);border:2px solid ${info.color};border-radius:16px;padding:20px;margin-bottom:20px;">
        <div style="font-size:32px;font-weight:800;color:${info.color};">CHF ${price.toFixed(2)}</div>
        <div style="font-size:12px;color:var(--ui-text-muted);">par mois • Sans engagement</div>
      </div>
      
      <div style="background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.3);border-radius:12px;padding:12px;margin-bottom:20px;">
        <div style="font-size:12px;font-weight:600;color:#22c55e;margin-bottom:4px;">🌍 70% → Mission Planète</div>
        <div style="font-size:11px;color:var(--ui-text-muted);">Votre contribution sauve la Terre</div>
      </div>
      
        <button onclick="processSubscriptionPayment('${plan}', ${price})" style="width:100%;padding:14px;border-radius:999px;border:none;background:linear-gradient(135deg,${info.color},${info.color}dd);color:${plan === 'premium' ? '#1f2937' : '#fff'};font-weight:700;cursor:pointer;font-size:16px;box-shadow:0 8px 24px ${info.color}66;">
          💳 Payer CHF ${price.toFixed(2)}/mois
        </button>
      
      <button onclick="openSubscriptionModal()" style="width:100%;margin-top:10px;padding:10px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;">
        Retour
      </button>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
  document.getElementById("publish-modal-backdrop").style.display = "flex";
}

async function processSubscriptionPayment(plan = 'full-premium', price = 25) {
  if (!currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  
  try {
    showNotification("💳 Redirection vers le paiement...", "info");
    
    // Créer une session Stripe Checkout pour abonnement
    const response = await fetch(`${API_BASE_URL}/payments/create-checkout-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId: currentUser.id.toString(),
        paymentType: 'subscription',
        plan: plan,
        amount: price,
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
    console.error('Erreur abonnement:', error);
    showNotification(`❌ Erreur lors de l'abonnement : ${error.message}`, "error");
  }
}

// Fonction de compatibilité (fallback si Stripe échoue)
function simulatePremiumPayment(plan = 'full-premium', price = 25) {
  processSubscriptionPayment(plan, price).catch(() => {
    // Fallback : simulation locale si l'API échoue
    currentUser.subscription = plan;
    currentUser.agendaLimit = getAgendaLimit();
    currentUser.alertLimit = getAlertLimit();
    updateSubscriptionBadge();
    
    const planNames = {
      'events-explorer': '🌱 Events Explorer',
      'events-alerts-pro': '🔔 Events Alertes Pro',
      'service-pro': '💼 Service Pro',
      'service-ultra': '🚀 Service Ultra',
      'full-premium': '👑 Full Premium',
      'events-alerts': '🔔 Events Alertes Pro',
      'booking-pro': '💼 Service Pro',
      'booking-ultra': '🚀 Service Ultra',
      'full': '👑 Full Premium',
      explorer: '🌱 Explorer',
      pro: '💼 Pro',
      premium: '⭐ Premium'
    };
    
    const planName = planNames[plan] || 'Premium';
    playPaymentSound();
    showNotification(`💎 Abonnement simulé (mode démo) : ${planName}`, "info");
    closePublishModal();
    openSubscriptionModal();
  });
}

// ============================================
// MODAL "À PROPOS" - CLIC SUR LOGO MAPEVENT
// ============================================
function openAboutModal() {
  // Récupérer la date de dernière connexion
  const lastLogin = currentUser.lastLoginAt ? new Date(currentUser.lastLoginAt).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }) : 'Première visite';
  
  const html = `
    <div style="padding:24px;max-width:600px;margin:0 auto;max-height:85vh;overflow-y:auto;">
      <!-- Header avec logo -->
      <div style="text-align:center;margin-bottom:24px;">
        <div style="font-size:48px;margin-bottom:12px;">🗺️</div>
        <h2 style="margin:0;font-size:28px;font-weight:800;background:linear-gradient(90deg,#00ffc3,#3b82f6);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;">MAP EVENT</h2>
        <p style="color:var(--ui-text-muted);margin-top:8px;font-size:14px;">La plateforme événementielle mondiale</p>
      </div>
      
      <!-- Contact -->
      <div style="background:linear-gradient(135deg,rgba(0,255,195,0.1),rgba(59,130,246,0.1));border:1px solid rgba(0,255,195,0.3);border-radius:16px;padding:16px;margin-bottom:20px;text-align:center;">
        <div style="font-size:14px;font-weight:600;color:#00ffc3;margin-bottom:8px;">📧 Contact</div>
        <a href="mailto:${MAPEVENT_CONTACT_EMAIL}" style="color:#3b82f6;font-size:16px;font-weight:600;text-decoration:none;">${MAPEVENT_CONTACT_EMAIL}</a>
      </div>
      
      <!-- État actuel -->
      <div style="background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.3);border-radius:16px;padding:16px;margin-bottom:20px;">
        <div style="font-size:14px;font-weight:700;color:#22c55e;margin-bottom:12px;display:flex;align-items:center;gap:8px;">
          <span>✅</span> Fonctionnalités disponibles
        </div>
        <ul style="margin:0;padding-left:20px;color:var(--ui-text-main);font-size:13px;line-height:1.8;">
          <li><strong>Carte interactive</strong> - 3 modes : Events, Booking, Services</li>
          <li><strong>Filtres avancés</strong> - Par catégorie, date, distance</li>
          <li><strong>Popups détaillées</strong> - Infos complètes sur chaque point</li>
          <li><strong>Comptes utilisateurs</strong> - Inscription, connexion, profil avec avatar</li>
          <li><strong>Favoris & Agenda</strong> - Sauvegardez vos événements préférés</li>
          <li><strong>Likes & Commentaires</strong> - Interagissez avec la communauté</li>
          <li><strong>Signalements</strong> - Signalez les contenus inappropriés</li>
          <li><strong>Paiements Stripe</strong> - Abonnements et boosts sécurisés</li>
          <li><strong>Multi-langues</strong> - FR, EN, ES, ZH, HI</li>
          <li><strong>Mode sombre</strong> - Design premium adaptatif</li>
        </ul>
      </div>
      
      <!-- Prochaines fonctionnalités -->
      <div style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:16px;padding:16px;margin-bottom:20px;">
        <div style="font-size:14px;font-weight:700;color:#3b82f6;margin-bottom:12px;display:flex;align-items:center;gap:8px;">
          <span>🚀</span> Prochaines étapes
        </div>
        <ul style="margin:0;padding-left:20px;color:var(--ui-text-main);font-size:13px;line-height:1.8;">
          <li><strong>Messagerie</strong> - Discutez avec vos amis</li>
          <li><strong>Groupes</strong> - Créez des groupes comme WhatsApp</li>
          <li><strong>Invitations</strong> - Invitez vos amis aux événements</li>
          <li><strong>Localisation live</strong> - Retrouvez vos amis sur place</li>
          <li><strong>Last Minute Tickets</strong> - Revente de billets sécurisée</li>
          <li><strong>Transport partagé</strong> - Covoiturage vers les events</li>
          <li><strong>Quêtes & Gamification</strong> - Gagnez des récompenses</li>
          <li><strong>Scraping 200+ events/pays</strong> - Données automatiques</li>
        </ul>
      </div>
      
      <!-- Dernière connexion -->
      ${currentUser.isLoggedIn ? `
        <div style="background:rgba(148,163,184,0.1);border:1px solid rgba(148,163,184,0.3);border-radius:16px;padding:16px;margin-bottom:20px;text-align:center;">
          <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:4px;">Dernière connexion</div>
          <div style="font-size:14px;font-weight:600;color:var(--ui-text-main);">${lastLogin}</div>
        </div>
      ` : `
        <div style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);border-radius:16px;padding:16px;margin-bottom:20px;text-align:center;">
          <div style="font-size:14px;color:#f59e0b;margin-bottom:8px;">👋 Bienvenue !</div>
          <button style="padding:10px 24px;border-radius:999px;border:none;background:linear-gradient(135deg,#22c55e,#16a34a);color:#fff;font-weight:600;cursor:pointer;" id="register-modal-btn">
            Créer un compte gratuit
          </button>
        </div>
      `}
      
      <!-- Version -->
      <div style="text-align:center;color:var(--ui-text-muted);font-size:11px;margin-bottom:16px;">
        Version 1.0.0 • Décembre 2024 • Made with ❤️ in Switzerland
      </div>
      
      <!-- Bouton fermer -->
      <button onclick="closePublishModal()" style="width:100%;padding:14px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-weight:600;font-size:14px;">
        Fermer
      </button>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
  document.getElementById("publish-modal-backdrop").style.display = "flex";
}

// ============================================
// SYSTÈME D'AMIS ET MESSAGERIE
// ============================================

// Données des utilisateurs simulés (pour la démo)
let allUsers = [];

// Initialiser des utilisateurs de démo
function initDemoUsers() {
  if (allUsers.length > 0) return;
  
  const demoNames = [
    "Alex_DJ", "Sophie_Techno", "Marco_Festivals", "Julie_Dance", "Thomas_Music",
    "Emma_Events", "Lucas_Party", "Léa_Vibes", "Hugo_Sound", "Camille_Beat",
    "Nathan_Bass", "Chloé_Electro", "Arthur_Rave", "Manon_House", "Théo_Groove"
  ];
  
  allUsers = demoNames.map((name, i) => {
    const avatar = AVAILABLE_AVATARS[i % AVAILABLE_AVATARS.length];
    return {
      id: `demo_user_${i + 1}`,
      name: name,
      avatar: avatar.emoji,
      avatarId: avatar.id,
      avatarDescription: `Fan de ${['techno', 'house', 'festivals', 'concerts', 'musique'][i % 5]}`,
      isOnline: Math.random() > 0.5,
      lastSeen: new Date(Date.now() - Math.random() * 86400000 * 7).toISOString()
    };
  });
}

// Ouvrir le modal des amis
function openFriendsModal() {
  if (!currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  
  initDemoUsers();
  
  const friendsList = currentUser.friends || [];
  const friendRequests = currentUser.friendRequests || [];
  
  // Trouver les infos des amis
  const friendsInfo = friendsList.map(friendId => {
    return allUsers.find(u => u.id === friendId) || { id: friendId, name: 'Utilisateur', avatar: '👤' };
  });
  
  const html = `
    <div style="padding:20px;max-width:550px;margin:0 auto;max-height:85vh;overflow-y:auto;">
      <div style="text-align:center;margin-bottom:20px;">
        <div style="font-size:40px;margin-bottom:8px;">👥</div>
        <h2 style="margin:0;font-size:22px;font-weight:700;color:#fff;">Mes Amis</h2>
        <p style="color:var(--ui-text-muted);margin-top:6px;font-size:13px;">${friendsList.length} ami(s)</p>
      </div>
      
      <!-- Demandes d'amis en attente -->
      ${friendRequests.length > 0 ? `
        <div style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);border-radius:12px;padding:14px;margin-bottom:16px;">
          <div style="font-size:13px;font-weight:600;color:#f59e0b;margin-bottom:10px;">📬 Demandes en attente (${friendRequests.length})</div>
          ${friendRequests.map(req => `
            <div style="display:flex;align-items:center;gap:10px;padding:10px;background:rgba(15,23,42,0.5);border-radius:10px;margin-bottom:8px;">
              <div style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:20px;">${req.fromUserAvatar || '👤'}</div>
              <div style="flex:1;">
                <div style="font-weight:600;font-size:14px;color:#fff;">${escapeHtml(req.fromUserName)}</div>
                <div style="font-size:11px;color:var(--ui-text-muted);">${new Date(req.date).toLocaleDateString('fr-FR')}</div>
              </div>
              <button onclick="acceptFriendRequest('${req.fromUserId}')" style="padding:6px 12px;border-radius:8px;border:none;background:#22c55e;color:#fff;font-size:12px;font-weight:600;cursor:pointer;">✓</button>
              <button onclick="declineFriendRequest('${req.fromUserId}')" style="padding:6px 12px;border-radius:8px;border:none;background:#ef4444;color:#fff;font-size:12px;font-weight:600;cursor:pointer;">✗</button>
            </div>
          `).join('')}
        </div>
      ` : ''}
      
      <!-- Rechercher des amis -->
      <div style="margin-bottom:16px;">
        <label style="display:block;font-size:13px;font-weight:600;color:#fff;margin-bottom:8px;">🔍 Rechercher des utilisateurs</label>
        <input type="text" id="search-friends-input" placeholder="Nom d'utilisateur..." 
               onkeyup="searchUsers(this.value)"
               style="width:100%;padding:12px;border-radius:10px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:14px;">
        <div id="search-friends-results" style="margin-top:10px;"></div>
      </div>
      
      <!-- Liste des amis -->
      <div style="margin-bottom:20px;">
        <div style="font-size:13px;font-weight:600;color:#fff;margin-bottom:10px;">👫 Mes amis</div>
        ${friendsInfo.length > 0 ? friendsInfo.map(friend => `
          <div style="display:flex;align-items:center;gap:12px;padding:12px;background:rgba(15,23,42,0.5);border-radius:12px;margin-bottom:8px;border:1px solid var(--ui-card-border);">
            <div style="position:relative;">
              <div style="width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:24px;">${friend.avatar}</div>
              <div style="position:absolute;bottom:2px;right:2px;width:12px;height:12px;border-radius:50%;background:${friend.isOnline ? '#22c55e' : '#6b7280'};border:2px solid var(--ui-card-bg);"></div>
            </div>
            <div style="flex:1;">
              <div style="font-weight:600;font-size:14px;color:#fff;">${escapeHtml(friend.name)}</div>
              <div style="font-size:11px;color:var(--ui-text-muted);">${friend.avatarDescription || ''}</div>
            </div>
            <button onclick="openChatWith('${friend.id}')" style="padding:8px 14px;border-radius:8px;border:none;background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff;font-size:12px;font-weight:600;cursor:pointer;">💬 Chat</button>
            <button onclick="removeFriend('${friend.id}')" style="padding:8px 10px;border-radius:8px;border:1px solid rgba(239,68,68,0.5);background:transparent;color:#ef4444;font-size:12px;cursor:pointer;">🗑️</button>
          </div>
        `).join('') : `
          <div style="text-align:center;padding:30px;color:var(--ui-text-muted);">
            <div style="font-size:32px;margin-bottom:8px;">🔍</div>
            <p>Vous n'avez pas encore d'amis.<br>Recherchez des utilisateurs ci-dessus !</p>
          </div>
        `}
      </div>
      
      <button onclick="closePublishModal()" style="width:100%;padding:12px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-weight:600;">
        Fermer
      </button>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
  document.getElementById("publish-modal-backdrop").style.display = "flex";
}

// Ouvrir le modal des groupes
function openGroupsModal() {
  if (!currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  
  // Récupérer les groupes de l'utilisateur (simulation)
  const userGroups = currentUser.groups || [];
  const registeredCountry = currentUser.registeredCountry || "CH";
  
  const html = `
    <div style="padding:20px;max-width:600px;margin:0 auto;max-height:85vh;overflow-y:auto;">
      <div style="text-align:center;margin-bottom:20px;">
        <div style="font-size:40px;margin-bottom:8px;">👥</div>
        <h2 style="margin:0;font-size:22px;font-weight:700;color:#fff;">Groupes</h2>
      </div>
      
      <!-- Sections principales -->
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px;">
        <!-- Canaux par pays -->
        <div onclick="changeGroupCountry()" style="padding:20px;background:rgba(0,255,195,0.1);border:2px solid rgba(0,255,195,0.3);border-radius:12px;cursor:pointer;text-align:center;">
          <div style="font-size:32px;margin-bottom:8px;">🌍</div>
          <div style="font-weight:600;color:#00ffc3;margin-bottom:4px;">Par Pays</div>
          <div style="font-size:12px;color:var(--ui-text-muted);">${registeredCountry}</div>
        </div>
        
        <!-- Catégories MapEvent -->
        <div onclick="openGroupChannel('category', 'events')" style="padding:20px;background:rgba(59,130,246,0.1);border:2px solid rgba(59,130,246,0.3);border-radius:12px;cursor:pointer;text-align:center;">
          <div style="font-size:32px;margin-bottom:8px;">📅</div>
          <div style="font-weight:600;color:#3b82f6;margin-bottom:4px;">Events</div>
          <div style="font-size:12px;color:var(--ui-text-muted);">Discussion</div>
        </div>
      </div>
      
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px;">
        <div onclick="openGroupChannel('category', 'booking')" style="padding:20px;background:rgba(139,92,246,0.1);border:2px solid rgba(139,92,246,0.3);border-radius:12px;cursor:pointer;text-align:center;">
          <div style="font-size:32px;margin-bottom:8px;">🎵</div>
          <div style="font-weight:600;color:#8b5cf6;margin-bottom:4px;">Booking</div>
          <div style="font-size:12px;color:var(--ui-text-muted);">Discussion</div>
        </div>
        
        <div onclick="openGroupChannel('category', 'services')" style="padding:20px;background:rgba(245,158,11,0.1);border:2px solid rgba(245,158,11,0.3);border-radius:12px;cursor:pointer;text-align:center;">
          <div style="font-size:32px;margin-bottom:8px;">💼</div>
          <div style="font-weight:600;color:#f59e0b;margin-bottom:4px;">Services</div>
          <div style="font-size:12px;color:var(--ui-text-muted);">Discussion</div>
        </div>
      </div>
      
      <!-- Vos groupes -->
        <div style="margin-bottom:20px;">
        <div style="font-size:13px;font-weight:600;color:#fff;margin-bottom:10px;">👥 Vos groupes</div>
        ${userGroups.length > 0 ? userGroups.map(group => `
          <div onclick="openGroupChannel('custom', '${group.id}')" style="display:flex;align-items:center;gap:12px;padding:12px;background:rgba(15,23,42,0.5);border-radius:12px;margin-bottom:8px;border:1px solid var(--ui-card-border);cursor:pointer;">
              <div style="width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:24px;">${group.emoji || '👥'}</div>
              <div style="flex:1;">
                <div style="font-weight:600;font-size:14px;color:#fff;">${escapeHtml(group.name)}</div>
                <div style="font-size:11px;color:var(--ui-text-muted);">${group.memberCount || 0} membres</div>
              </div>
            </div>
        `).join('') : `
          <div style="text-align:center;padding:30px;color:var(--ui-text-muted);">
            <div style="font-size:32px;margin-bottom:8px;">🔍</div>
            <p>Vous n'avez pas encore de groupes.<br>Créez-en un ci-dessous !</p>
        </div>
        `}
      </div>
      
      <!-- Créer un groupe -->
      <div onclick="createGroup()" style="padding:20px;background:linear-gradient(135deg,rgba(0,255,195,0.2),rgba(59,130,246,0.2));border:2px dashed rgba(0,255,195,0.5);border-radius:12px;cursor:pointer;text-align:center;margin-bottom:20px;">
        <div style="font-size:40px;margin-bottom:8px;">➕</div>
        <div style="font-weight:700;color:#00ffc3;font-size:16px;">Créer un groupe</div>
      </div>
      
      <button onclick="closePublishModal()" style="width:100%;padding:12px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-weight:600;">
        Fermer
      </button>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
  document.getElementById("publish-modal-backdrop").style.display = "flex";
}

// Mettre à jour la fonction globale avec l'implémentation complète
// Cette assignation remplace le stub défini plus tôt
window.openGroupsModal = openGroupsModal;

// Rechercher des utilisateurs
function searchUsers(query) {
  const resultsContainer = document.getElementById("search-friends-results");
  if (!resultsContainer) return;
  
  if (!query || query.length < 2) {
    resultsContainer.innerHTML = '';
    return;
  }
  
  initDemoUsers();
  
  const results = allUsers.filter(u => 
    u.name.toLowerCase().includes(query.toLowerCase()) && 
    u.id !== currentUser.id &&
    !currentUser.friends.includes(u.id)
  ).slice(0, 5);
  
  if (results.length === 0) {
    resultsContainer.innerHTML = '<div style="color:var(--ui-text-muted);font-size:12px;padding:10px;">Aucun utilisateur trouvé</div>';
    return;
  }
  
  resultsContainer.innerHTML = results.map(user => `
    <div style="display:flex;align-items:center;gap:10px;padding:10px;background:rgba(0,255,195,0.05);border-radius:10px;margin-bottom:6px;border:1px solid rgba(0,255,195,0.2);">
      <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:18px;">${user.avatar}</div>
      <div style="flex:1;">
        <div style="font-weight:600;font-size:13px;color:#fff;">${escapeHtml(user.name)}</div>
        <div style="font-size:10px;color:var(--ui-text-muted);">${user.isOnline ? '🟢 En ligne' : '⚫ Hors ligne'}</div>
      </div>
      <button onclick="sendFriendRequest('${user.id}', '${escapeHtml(user.name)}', '${user.avatar}')" style="padding:6px 12px;border-radius:8px;border:none;background:#00ffc3;color:#000;font-size:11px;font-weight:600;cursor:pointer;">+ Ajouter</button>
    </div>
  `).join('');
}

// Envoyer une demande d'ami
function sendFriendRequest(userId, userName, userAvatar) {
  if (!currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  
  if (!currentUser.sentRequests) currentUser.sentRequests = [];
  
  if (currentUser.sentRequests.includes(userId)) {
    showNotification("⏳ Demande déjà envoyée", "info");
    return;
  }
  
  if (currentUser.friends.includes(userId)) {
    showNotification("✅ Déjà ami avec cet utilisateur", "info");
    return;
  }
  
  currentUser.sentRequests.push(userId);
  
  // Simuler l'ajout d'une demande côté destinataire (pour la démo, on accepte automatiquement)
  setTimeout(() => {
    if (!currentUser.friends.includes(userId)) {
      currentUser.friends.push(userId);
      currentUser.sentRequests = currentUser.sentRequests.filter(id => id !== userId);
      showNotification(`🎉 ${userName} a accepté votre demande d'ami !`, "success");
      saveUserData();
    }
  }, 2000);
  
  showNotification(`📤 Demande envoyée à ${userName}`, "success");
  saveUserData();
  openFriendsModal(); // Rafraîchir
}

// Accepter une demande d'ami
function acceptFriendRequest(fromUserId) {
  if (!currentUser.friendRequests) return;
  
  const request = currentUser.friendRequests.find(r => r.fromUserId === fromUserId);
  if (!request) return;
  
  // Ajouter comme ami
  if (!currentUser.friends.includes(fromUserId)) {
    currentUser.friends.push(fromUserId);
  }
  
  // Retirer de la liste des demandes
  currentUser.friendRequests = currentUser.friendRequests.filter(r => r.fromUserId !== fromUserId);
  
  showNotification(`🎉 Vous êtes maintenant ami avec ${request.fromUserName} !`, "success");
  saveUserData();
  openFriendsModal(); // Rafraîchir
}

// Refuser une demande d'ami
function declineFriendRequest(fromUserId) {
  if (!currentUser.friendRequests) return;
  
  currentUser.friendRequests = currentUser.friendRequests.filter(r => r.fromUserId !== fromUserId);
  
  showNotification("❌ Demande refusée", "info");
  saveUserData();
  openFriendsModal(); // Rafraîchir
}

// Retirer un ami
function removeFriend(friendId) {
  if (!confirm("Voulez-vous vraiment retirer cet ami ?")) return;
  
  currentUser.friends = currentUser.friends.filter(id => id !== friendId);
  
  showNotification("👋 Ami retiré", "info");
  saveUserData();
  openFriendsModal(); // Rafraîchir
}

// Ouvrir le chat avec un ami
function openChatWith(friendId) {
  initDemoUsers();
  const friend = allUsers.find(u => u.id === friendId) || { id: friendId, name: 'Utilisateur', avatar: '👤' };
  
  // Récupérer les messages existants
  const conversationKey = [currentUser.id, friendId].sort().join(':');
  if (!window.conversations) window.conversations = {};
  if (!window.conversations[conversationKey]) {
    window.conversations[conversationKey] = [
      { from: friendId, text: "Salut ! 👋", time: new Date(Date.now() - 3600000).toISOString() },
      { from: currentUser.id, text: "Hey ! Comment ça va ?", time: new Date(Date.now() - 3500000).toISOString() },
      { from: friendId, text: "Super bien, tu vas à la soirée ce weekend ?", time: new Date(Date.now() - 3400000).toISOString() }
    ];
  }
  
  const messages = window.conversations[conversationKey] || [];
  
  const html = `
    <div style="display:flex;flex-direction:column;height:70vh;max-width:500px;margin:0 auto;">
      <!-- Header -->
      <div style="display:flex;align-items:center;gap:12px;padding:16px;border-bottom:1px solid var(--ui-card-border);">
        <button onclick="openFriendsModal()" style="width:36px;height:36px;border-radius:50%;border:none;background:rgba(15,23,42,0.9);color:#fff;cursor:pointer;font-size:16px;">←</button>
        <div style="width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:22px;">${friend.avatar}</div>
        <div style="flex:1;">
          <div style="font-weight:600;font-size:16px;color:#fff;">${escapeHtml(friend.name)}</div>
          <div style="font-size:11px;color:${friend.isOnline ? '#22c55e' : 'var(--ui-text-muted)'};">${friend.isOnline ? '🟢 En ligne' : 'Hors ligne'}</div>
        </div>
        <button onclick="openReportModal('user', '${friendId}')" style="padding:8px;border-radius:8px;border:1px solid rgba(239,68,68,0.3);background:transparent;color:#ef4444;font-size:12px;cursor:pointer;">🚨</button>
      </div>
      
      <!-- Messages -->
      <div id="chat-messages" style="flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px;">
        ${messages.map(msg => `
          <div style="display:flex;${msg.from === currentUser.id ? 'justify-content:flex-end;' : 'justify-content:flex-start;'}">
            <div style="max-width:75%;padding:10px 14px;border-radius:16px;${msg.from === currentUser.id ? 'background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;border-bottom-right-radius:4px;' : 'background:rgba(15,23,42,0.9);color:#fff;border-bottom-left-radius:4px;'}">
              <div style="font-size:14px;">${escapeHtml(msg.text)}</div>
              <div style="font-size:10px;opacity:0.7;margin-top:4px;text-align:right;">${new Date(msg.time).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}</div>
            </div>
          </div>
        `).join('')}
      </div>
      
      <!-- Input -->
      <div style="padding:16px;border-top:1px solid var(--ui-card-border);display:flex;gap:10px;">
        <input type="text" id="chat-input" placeholder="Votre message..." 
               onkeypress="if(event.key==='Enter')sendChatMessage('${friendId}')"
               style="flex:1;padding:12px;border-radius:999px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.9);color:var(--ui-text-main);font-size:14px;">
        <button onclick="sendChatMessage('${friendId}')" style="width:48px;height:48px;border-radius:50%;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;cursor:pointer;font-size:20px;">➤</button>
      </div>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
  
  // Scroll to bottom
  setTimeout(() => {
    const chatMessages = document.getElementById("chat-messages");
    if (chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight;
  }, 100);
}

// Envoyer un message
function sendChatMessage(friendId) {
  const input = document.getElementById("chat-input");
  if (!input || !input.value.trim()) return;
  
  const conversationKey = [currentUser.id, friendId].sort().join(':');
  if (!window.conversations) window.conversations = {};
  if (!window.conversations[conversationKey]) window.conversations[conversationKey] = [];
  
  window.conversations[conversationKey].push({
    from: currentUser.id,
    text: input.value.trim(),
    time: new Date().toISOString()
  });
  
  // Simuler une réponse automatique (pour la démo)
  setTimeout(() => {
    const autoResponses = [
      "Super ! 🎉",
      "Ah cool !",
      "On se retrouve là-bas ?",
      "J'ai hâte !",
      "Trop bien 👍",
      "À bientôt !"
    ];
    window.conversations[conversationKey].push({
      from: friendId,
      text: autoResponses[Math.floor(Math.random() * autoResponses.length)],
      time: new Date().toISOString()
    });
    openChatWith(friendId); // Rafraîchir
  }, 1500);
  
  openChatWith(friendId); // Rafraîchir immédiatement pour montrer notre message
}

// Sauvegarder les données utilisateur
function saveUserData() {
  try {
    localStorage.setItem('currentUser', JSON.stringify(currentUser));
  } catch (e) {
    console.error('Erreur sauvegarde:', e);
  }
}

// Exposer saveUser globalement pour compatibilité
window.saveUser = saveUserData;

// Récupérer les amis qui participent à un événement
function getFriendsParticipatingToEvent(eventId) {
  if (!currentUser.isLoggedIn || !currentUser.friends || currentUser.friends.length === 0) {
    return [];
  }
  
  initDemoUsers();
  
  // Simuler que certains amis participent à des événements (pour la démo)
  // Dans la vraie implémentation, cela viendrait du backend
  const friendsParticipating = [];
  
  currentUser.friends.forEach(friendId => {
    // Simuler une participation aléatoire basée sur l'ID de l'événement
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
    const participates = combinedHash % 5 === 0; // ~20% de chance de participer
    
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

// Charger l'utilisateur sauvegardé au démarrage
function loadSavedUser() {
  try {
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
      const parsedUser = JSON.parse(savedUser);
      
      // Vérifier que l'utilisateur a des tokens Cognito valides avant de restaurer la session
      const tokensRaw = localStorage.getItem("cognito_tokens");
      let hasValidTokens = false;
      
      if (tokensRaw) {
        try {
          const tokens = JSON.parse(tokensRaw);
          // Vérifier que les tokens existent et ne sont pas expirés
          if (tokens && tokens.id_token && tokens.access_token) {
            // Vérifier l'expiration du token (optionnel mais recommandé)
            try {
              const payload = decodeJwtPayload(tokens.id_token);
              const now = Math.floor(Date.now() / 1000);
              if (payload.exp && payload.exp > now) {
                hasValidTokens = true;
              }
            } catch (e) {
              // Si on ne peut pas décoder, on considère que les tokens sont valides
              // (ils seront vérifiés côté serveur)
              hasValidTokens = true;
            }
          }
        } catch (e) {
          console.warn('⚠️ Tokens Cognito invalides:', e);
        }
      }
      
      // IMPORTANT: Ne PAS restaurer automatiquement la session
      // L'utilisateur doit TOUJOURS passer par la modal de connexion
      // On charge juste les données mais on garde isLoggedIn: false
      if (parsedUser) {
        // Si pas de tokens valides, nettoyer complètement
        if (!hasValidTokens) {
          console.log('⚠️ Pas de tokens Cognito valides - Nettoyage de la session');
          currentUser.isLoggedIn = false;
          // NE PAS forcer profileComplete à false si le profil est déjà complet
          // On garde la valeur existante pour éviter de réafficher le formulaire
          const existingProfileComplete = parsedUser.profileComplete === true;
          localStorage.removeItem('cognito_tokens');
          localStorage.setItem('currentUser', JSON.stringify({ 
            ...parsedUser, 
            isLoggedIn: false, 
            profileComplete: existingProfileComplete // Conserver la valeur existante
          }));
          updateAccountButton();
          return;
        }
        
        // Même avec des tokens valides, on ne restaure PAS automatiquement la session
        // L'utilisateur doit cliquer sur "Compte" et se reconnecter
        // On charge juste les données de base pour référence
        // IMPORTANT: Respecter profileComplete si le profil est déjà complet
        console.log('ℹ️ Données utilisateur trouvées mais session non restaurée automatiquement', {
          profileComplete: parsedUser.profileComplete,
          email: parsedUser.email
        });
        
        // CONSERVER profileComplete si le profil est déjà complet
        const existingProfileComplete = parsedUser.profileComplete === true;
        
        // Fusionner avec les valeurs par défaut pour éviter les propriétés manquantes
        currentUser = {
          id: null,
          name: "",
          email: "",
          avatar: "👤",
          avatarId: null,
          avatarDescription: "",
          bio: "",
          isLoggedIn: false, // TOUJOURS false au chargement - doit passer par la modal de connexion
          favorites: [],
          agenda: [],
          likes: [],
          participating: [],
          alerts: [],
          statusAlerts: [],
          pendingStatusNotifications: [],
          proximityAlerts: [],
          eventAlarms: [],
          reviews: {},
          subscription: "free",
          agendaLimit: 20,
          alertLimit: 0,
          eventStatusHistory: {},
          addresses: [],
          smsNotifications: 0,
          smsLimit: 0,
          emailNotifications: 0,
          notificationPreferences: { email: true, sms: false },
          privacySettings: {
            showName: true,
            showAvatar: true,
            showBio: true,
            showEmail: false,
            showAddresses: false,
            showFavorites: true,
            showAgenda: true,
            showParticipating: true,
            showFriends: true,
            showActivity: true
          },
          friends: [],
          friendRequests: [],
          sentRequests: [],
          blockedUsers: [],
          conversations: [],
          groups: [],
          profilePhotos: [],
          profileLinks: [],
          history: [],
          photos: [],
          ...parsedUser, // Écraser avec les valeurs sauvegardées
          lastSeen: new Date().toISOString(),
          isLoggedIn: false, // TOUJOURS false au chargement - l'utilisateur doit passer par la modal de connexion
          profileComplete: existingProfileComplete // CONSERVER la valeur existante si le profil est complet
        };
        console.log(`ℹ️ Données utilisateur chargées depuis localStorage mais session non restaurée (doit passer par modal de connexion)`, {
          profileComplete: currentUser.profileComplete,
          email: currentUser.email
        });
        // Sauvegarder en conservant profileComplete
        try {
          localStorage.setItem('currentUser', JSON.stringify({ 
            ...currentUser, 
            profileComplete: existingProfileComplete // Conserver la valeur existante
          }));
        } catch (e) {
          console.warn('⚠️ Impossible de sauvegarder currentUser:', e);
        }
        updateUserUI();
        updateAccountButton();
      }
    }
  } catch (e) {
    console.error('Erreur chargement utilisateur:', e);
  }
}

// Fonctions helper pour le modal compte
function acceptFriendRequest(requestId) {
  const request = currentUser.friendRequests?.find(r => r.id === requestId);
  if (!request) return;
  
  // Ajouter aux amis
  if (!currentUser.friends) currentUser.friends = [];
  currentUser.friends.push({
    id: request.fromUserId,
    name: request.fromUserName,
    avatar: request.fromUserAvatar,
    username: request.username
  });
  
  // Retirer de la liste des demandes
  currentUser.friendRequests = currentUser.friendRequests.filter(r => r.id !== requestId);
  
  // Sauvegarder
  localStorage.setItem('currentUser', JSON.stringify(currentUser));
  showNotification(`✅ ${request.fromUserName} ajouté(e) à vos amis !`, 'success');
  
  // Rafraîchir le modal
  showAccountModalTab('amis');
}

function rejectFriendRequest(requestId) {
  currentUser.friendRequests = currentUser.friendRequests.filter(r => r.id !== requestId);
  localStorage.setItem('currentUser', JSON.stringify(currentUser));
  showNotification('Demande d\'ami refusée', 'info');
  showAccountModalTab('amis');
}

function openUserProfile(userId) {
  showNotification('Profil utilisateur à venir', 'info');
  // TODO: Implémenter l'ouverture du profil utilisateur
}

function openGroupDetails(groupId) {
  showNotification('Détails du groupe à venir', 'info');
  // TODO: Implémenter l'ouverture des détails du groupe
}

// ============================================
// COMPTE UTILISATEUR COMPLET - DESIGN PREMIUM
// ============================================
// Variable pour gérer l'onglet actif du modal Compte
let accountModalActiveTab = 'agenda';

function openAccountModal() {
  if (!currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  
  // Réinitialiser l'onglet actif
  accountModalActiveTab = 'agenda';
  showAccountModalTab('agenda');
}

function showAccountModalTab(tab) {
  accountModalActiveTab = tab;
  
  // Calculer les statistiques
  const memberSince = currentUser.createdAt ? new Date(currentUser.createdAt).toLocaleDateString('fr-FR', { month: 'short', year: 'numeric' }) : 'Déc. 2024';
  const totalEvents = eventsData.length;
  const alertsCount = currentUser.alerts?.length || 0;
  const notificationsCount = (currentUser.friendRequests?.length || 0) + (currentUser.pendingStatusNotifications?.length || 0);
  
  // Initialiser les propriétés si elles sont undefined
  if (!currentUser.likes) currentUser.likes = [];
  if (!currentUser.agenda) currentUser.agenda = [];
  if (!currentUser.participating) currentUser.participating = [];
  if (!currentUser.favorites) currentUser.favorites = [];
  if (!currentUser.friendRequests) currentUser.friendRequests = [];
  
  // Déterminer le niveau et les badges
  const activityScore = (currentUser.likes.length || 0) + (currentUser.agenda.length || 0) * 2 + (currentUser.participating.length || 0) * 3;
  const level = activityScore > 50 ? 'Expert' : activityScore > 20 ? 'Actif' : activityScore > 5 ? 'Découvreur' : 'Nouveau';
  const levelColor = activityScore > 50 ? '#ffd700' : activityScore > 20 ? '#8b5cf6' : activityScore > 5 ? '#3b82f6' : '#6b7280';
  const levelEmoji = activityScore > 50 ? '🏆' : activityScore > 20 ? '⭐' : activityScore > 5 ? '🌱' : '👋';
  
  // Badges gagnés
  const badges = [];
  if ((currentUser.likes?.length || 0) >= 1) badges.push({ emoji: '❤️', name: 'Premier like' });
  if ((currentUser.agenda?.length || 0) >= 5) badges.push({ emoji: '📅', name: '5 événements' });
  if ((currentUser.participating?.length || 0) >= 1) badges.push({ emoji: '🎉', name: 'Participant' });
  if (currentUser.subscription !== 'free') badges.push({ emoji: '💎', name: 'Premium' });
  if (alertsCount >= 3) badges.push({ emoji: '🔔', name: 'Alerté' });
  
  // Plan d'abonnement actuel
  const planNames = {
    'free': { name: 'Gratuit', color: '#6b7280', emoji: '🆓' },
    'events-explorer': { name: 'Events Explorer', color: '#22c55e', emoji: '🌱' },
    'events-alerts-pro': { name: 'Events Alerts Pro', color: '#3b82f6', emoji: '🔔' },
    'service-pro': { name: 'Service Pro', color: '#8b5cf6', emoji: '💼' },
    'service-ultra': { name: 'Service Ultra', color: '#a78bfa', emoji: '🚀' },
    'full-premium': { name: 'Full Premium', color: '#ffd700', emoji: '👑' }
  };
  const currentPlan = planNames[currentUser.subscription] || planNames.free;
  
  // Avatar à afficher (photo de profil ou emoji)
  // PRIORITÉ: profilePhoto > profile_photo_url > avatar (qui peut être une URL Google)
  const avatarUrl = currentUser.profilePhoto || currentUser.profile_photo_url || currentUser.avatar;
  const avatarDisplay = (avatarUrl && (avatarUrl.startsWith('http') || avatarUrl.startsWith('data:image')))
    ? `<img src="${avatarUrl}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;" onerror="this.parentElement.innerHTML='${currentUser.avatar || '👤'}';" />`
    : (avatarUrl || currentUser.avatar || "👤");
  
  // Contenu des onglets
  let tabContent = '';
  
  if (tab === 'agenda') {
    const agendaItems = (currentUser.agenda || []).map(key => {
      const [type, id] = key.split(":");
      const data = type === "event" ? eventsData : type === "booking" ? bookingsData : servicesData;
      return data.find(i => i.id === parseInt(id));
    }).filter(Boolean);
    
    tabContent = `
      <div style="padding:16px;">
        <h3 style="margin:0 0 16px;font-size:18px;font-weight:700;">📅 Mon Agenda</h3>
        ${agendaItems.length === 0 ? `
          <div style="text-align:center;padding:40px;color:var(--ui-text-muted);">
            <div style="font-size:48px;margin-bottom:16px;">📭</div>
            <p>Votre agenda est vide</p>
            <p style="font-size:12px;margin-top:8px;">Ajoutez des événements depuis la carte !</p>
          </div>
        ` : `
          <div style="display:flex;flex-direction:column;gap:12px;">
            ${agendaItems.slice(0, 10).map(item => {
              const imgTag = buildMainImageTag(item, item.title || item.name || "");
              return `
                <div onclick="openPopupFromList('${item.type}', ${item.id}); closePublishModal();" style="display:flex;gap:12px;padding:12px;border-radius:12px;background:rgba(15,23,42,0.5);border:1px solid var(--ui-card-border);cursor:pointer;transition:all 0.2s;" onmouseover="this.style.background='rgba(0,255,195,0.1)';this.style.borderColor='rgba(0,255,195,0.5)'" onmouseout="this.style.background='rgba(15,23,42,0.5)';this.style.borderColor='var(--ui-card-border)'">
                  <div style="width:80px;height:80px;border-radius:8px;overflow:hidden;flex-shrink:0;">
                    ${imgTag}
                  </div>
                  <div style="flex:1;min-width:0;">
                    <div style="font-weight:600;font-size:14px;margin-bottom:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${escapeHtml(item.title || item.name || 'Sans titre')}</div>
                    <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:4px;">${getCategoryEmoji(item)} ${item.category || 'Autre'}</div>
                    ${item.startDate ? `<div style="font-size:11px;color:var(--ui-text-muted);">📅 ${formatDate(item.startDate)}</div>` : ''}
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        `}
      </div>
    `;
  } else if (tab === 'groupes') {
    const groups = currentUser.groups || [];
    tabContent = `
      <div style="padding:16px;">
        <h3 style="margin:0 0 16px;font-size:18px;font-weight:700;">👥 Mes Groupes</h3>
        ${groups.length === 0 ? `
          <div style="text-align:center;padding:40px;color:var(--ui-text-muted);">
            <div style="font-size:48px;margin-bottom:16px;">👥</div>
            <p>Vous n'êtes dans aucun groupe</p>
            <button onclick="openGroupsModal()" style="margin-top:16px;padding:12px 24px;border-radius:999px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:700;cursor:pointer;">Créer un groupe</button>
          </div>
        ` : `
          <div style="display:flex;flex-direction:column;gap:12px;">
            ${groups.map(group => `
              <div onclick="openGroupDetails(${group.id})" style="display:flex;gap:12px;padding:12px;border-radius:12px;background:rgba(15,23,42,0.5);border:1px solid var(--ui-card-border);cursor:pointer;">
                <div style="width:60px;height:60px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:24px;">${group.emoji || '👥'}</div>
                <div style="flex:1;">
                  <div style="font-weight:600;font-size:14px;">${escapeHtml(group.name || 'Groupe sans nom')}</div>
                  <div style="font-size:12px;color:var(--ui-text-muted);">${group.members?.length || 0} membres</div>
                </div>
              </div>
            `).join('')}
          </div>
        `}
      </div>
    `;
  } else if (tab === 'amis') {
    const friends = currentUser.friends || [];
    const friendRequests = currentUser.friendRequests || [];
    tabContent = `
      <div style="padding:16px;">
        <h3 style="margin:0 0 16px;font-size:18px;font-weight:700;">👥 Mes Amis</h3>
        ${friendRequests.length > 0 ? `
          <div style="margin-bottom:20px;">
            <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:12px;font-weight:600;">🔔 Demandes en attente (${friendRequests.length})</div>
            <div style="display:flex;flex-direction:column;gap:8px;">
              ${friendRequests.slice(0, 5).map(req => `
                <div style="display:flex;align-items:center;gap:12px;padding:12px;border-radius:12px;background:rgba(15,23,42,0.5);border:1px solid var(--ui-card-border);">
                  <div style="width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:20px;">${req.avatar || '👤'}</div>
                  <div style="flex:1;">
                    <div style="font-weight:600;font-size:14px;">${escapeHtml(req.name || 'Utilisateur')}</div>
                    <div style="font-size:11px;color:var(--ui-text-muted);">${req.username || ''}</div>
                  </div>
                  <div style="display:flex;gap:8px;">
                    <button onclick="acceptFriendRequest(${req.id})" style="padding:6px 12px;border-radius:8px;border:none;background:#22c55e;color:#fff;font-size:12px;font-weight:600;cursor:pointer;">✓</button>
                    <button onclick="rejectFriendRequest(${req.id})" style="padding:6px 12px;border-radius:8px;border:none;background:#ef4444;color:#fff;font-size:12px;font-weight:600;cursor:pointer;">✕</button>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}
        ${friends.length === 0 ? `
          <div style="text-align:center;padding:40px;color:var(--ui-text-muted);">
            <div style="font-size:48px;margin-bottom:16px;">👥</div>
            <p>Vous n'avez pas encore d'amis</p>
            <p style="font-size:12px;margin-top:8px;">Ajoutez des amis pour partager vos événements !</p>
          </div>
        ` : `
          <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px;">
            ${friends.map(friend => `
              <div onclick="openUserProfile(${friend.id})" style="display:flex;flex-direction:column;align-items:center;gap:8px;padding:16px;border-radius:12px;background:rgba(15,23,42,0.5);border:1px solid var(--ui-card-border);cursor:pointer;">
                <div style="width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:28px;">${friend.avatar || '👤'}</div>
                <div style="font-weight:600;font-size:13px;text-align:center;">${escapeHtml(friend.name || 'Ami')}</div>
              </div>
            `).join('')}
          </div>
        `}
      </div>
    `;
  } else if (tab === 'notifications') {
    const notifications = [
      ...(currentUser.pendingStatusNotifications || []).map(n => ({...n, type: 'status'})),
      ...(currentUser.friendRequests || []).map(n => ({...n, type: 'friend'})),
    ].sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));
    
    tabContent = `
      <div style="padding:16px;">
        <h3 style="margin:0 0 16px;font-size:18px;font-weight:700;">🔔 Notifications</h3>
        ${notifications.length === 0 ? `
          <div style="text-align:center;padding:40px;color:var(--ui-text-muted);">
            <div style="font-size:48px;margin-bottom:16px;">🔔</div>
            <p>Aucune notification</p>
          </div>
        ` : `
          <div style="display:flex;flex-direction:column;gap:8px;">
            ${notifications.slice(0, 20).map(notif => `
              <div style="display:flex;gap:12px;padding:12px;border-radius:12px;background:rgba(15,23,42,0.5);border:1px solid var(--ui-card-border);">
                <div style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">
                  ${notif.type === 'status' ? '📊' : notif.type === 'friend' ? '👥' : '🔔'}
                </div>
                <div style="flex:1;">
                  <div style="font-size:13px;color:var(--ui-text-main);line-height:1.4;">${escapeHtml(notif.message || 'Nouvelle notification')}</div>
                  <div style="font-size:11px;color:var(--ui-text-muted);margin-top:4px;">${formatTime(notif.timestamp || Date.now())}</div>
                </div>
              </div>
            `).join('')}
          </div>
        `}
      </div>
    `;
  }
  
  const html = `
    <div style="padding:0;max-width:500px;margin:0 auto;">
      <!-- Header avec avatar et infos -->
      <div style="background:linear-gradient(135deg,#0f172a 0%,#1e293b 50%,#0f172a 100%);padding:20px;border-radius:16px 16px 0 0;position:relative;">
        <div style="display:flex;align-items:center;gap:16px;">
          <div style="position:relative;">
            <div style="width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#00ffc3,#3b82f6);display:flex;align-items:center;justify-content:center;font-size:24px;border:2px solid rgba(255,255,255,0.2);overflow:hidden;" data-account-avatar="true">
              ${avatarDisplay}
            </div>
            <div style="position:absolute;bottom:-2px;right:-2px;width:20px;height:20px;background:${levelColor};border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10px;border:2px solid #0f172a;">
              ${levelEmoji}
            </div>
          </div>
          <div style="flex:1;">
            <div style="font-size:18px;font-weight:800;color:#fff;margin-bottom:2px;">${currentUser.username || currentUser.name || 'Utilisateur'}</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.6);margin-bottom:4px;">${currentUser.email || ''}</div>
            ${currentUser.postalAddress ? `
              <div style="font-size:11px;color:rgba(255,255,255,0.5);display:flex;align-items:center;gap:4px;">
                <span>📍</span>
                <span>${typeof currentUser.postalAddress === 'object' 
                  ? `${currentUser.postalAddress.address || ''}${currentUser.postalAddress.city ? ', ' + currentUser.postalAddress.city : ''}${currentUser.postalAddress.zip ? ' ' + currentUser.postalAddress.zip : ''}${currentUser.postalAddress.country ? ' (' + currentUser.postalAddress.country + ')' : ''}`.trim()
                  : currentUser.postalAddress}</span>
              </div>
            ` : ''}
          </div>
        </div>
      </div>
      
      <!-- Onglets style Facebook -->
      <div style="display:flex;background:var(--ui-card-bg);border-top:1px solid var(--ui-card-border);border-bottom:1px solid var(--ui-card-border);">
        <button onclick="showAccountModalTab('agenda')" style="flex:1;padding:14px;border:none;background:${tab === 'agenda' ? 'rgba(0,255,195,0.1)' : 'transparent'};color:${tab === 'agenda' ? '#00ffc3' : 'var(--ui-text-main)'};font-weight:${tab === 'agenda' ? '700' : '600'};font-size:13px;cursor:pointer;border-bottom:${tab === 'agenda' ? '3px solid #00ffc3' : 'none'};transition:all 0.2s;">
          📅 Agenda
        </button>
        <button onclick="showAccountModalTab('groupes')" style="flex:1;padding:14px;border:none;background:${tab === 'groupes' ? 'rgba(0,255,195,0.1)' : 'transparent'};color:${tab === 'groupes' ? '#00ffc3' : 'var(--ui-text-main)'};font-weight:${tab === 'groupes' ? '700' : '600'};font-size:13px;cursor:pointer;border-bottom:${tab === 'groupes' ? '3px solid #00ffc3' : 'none'};transition:all 0.2s;">
          👥 Groupes
        </button>
        <button onclick="showAccountModalTab('amis')" style="flex:1;padding:14px;border:none;background:${tab === 'amis' ? 'rgba(0,255,195,0.1)' : 'transparent'};color:${tab === 'amis' ? '#00ffc3' : 'var(--ui-text-main)'};font-weight:${tab === 'amis' ? '700' : '600'};font-size:13px;cursor:pointer;border-bottom:${tab === 'amis' ? '3px solid #00ffc3' : 'none'};transition:all 0.2s;position:relative;">
          👥 Amis
          ${(currentUser.friendRequests?.length || 0) > 0 ? `<span style="position:absolute;top:8px;right:8px;width:16px;height:16px;background:#ef4444;border-radius:50%;font-size:9px;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;">${currentUser.friendRequests.length}</span>` : ''}
        </button>
        <button onclick="showAccountModalTab('notifications')" style="flex:1;padding:14px;border:none;background:${tab === 'notifications' ? 'rgba(0,255,195,0.1)' : 'transparent'};color:${tab === 'notifications' ? '#00ffc3' : 'var(--ui-text-main)'};font-weight:${tab === 'notifications' ? '700' : '600'};font-size:13px;cursor:pointer;border-bottom:${tab === 'notifications' ? '3px solid #00ffc3' : 'none'};transition:all 0.2s;position:relative;">
          🔔 Notifs
          ${notificationsCount > 0 ? `<span style="position:absolute;top:8px;right:8px;width:16px;height:16px;background:#ef4444;border-radius:50%;font-size:9px;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;">${notificationsCount}</span>` : ''}
        </button>
      </div>
      
      <!-- Contenu de l'onglet -->
      <div style="max-height:calc(80vh - 200px);overflow-y:auto;">
        ${tabContent}
      </div>
      
      <!-- Footer avec actions -->
      <div style="padding:12px 16px;background:var(--ui-card-bg);border-top:1px solid var(--ui-card-border);border-radius:0 0 16px 16px;display:flex;flex-direction:column;gap:8px;">
        <div style="display:flex;gap:8px;">
          <button onclick="openEditProfileModal()" style="flex:1;padding:10px;border-radius:8px;border:1px solid rgba(0,255,195,0.3);background:rgba(0,255,195,0.1);color:#00ffc3;cursor:pointer;font-size:12px;font-weight:600;">✏️ Modifier profil</button>
          <button onclick="openSettingsModal()" style="flex:1;padding:10px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-size:12px;">⚙️ Paramètres</button>
        </div>
        <div style="display:flex;gap:8px;">
          <button onclick="logout()" style="flex:1;padding:10px;border-radius:8px;border:1px solid rgba(239,68,68,0.3);background:rgba(239,68,68,0.1);color:#ef4444;cursor:pointer;font-size:12px;">🚪 Déconnexion</button>
          <button onclick="closePublishModal()" style="flex:1;padding:10px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-muted);cursor:pointer;font-size:12px;">Fermer</button>
        </div>
      </div>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
  document.getElementById("publish-modal-backdrop").style.display = "flex";
}

// Modal Paramètres
function openSettingsModal() {
  const html = `
    <div style="padding:20px;max-width:400px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
        <h2 style="margin:0;font-size:20px;display:flex;align-items:center;gap:10px;">⚙️ Paramètres</h2>
        <button onclick="closePublishModal()" style="background:none;border:none;font-size:24px;cursor:pointer;color:var(--ui-text-muted);">✕</button>
      </div>
      
      <!-- Notifications -->
      <div style="margin-bottom:20px;">
        <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:12px;font-weight:600;">🔔 NOTIFICATIONS</div>
        <div style="display:flex;flex-direction:column;gap:10px;">
          <label style="display:flex;align-items:center;justify-content:space-between;padding:12px;background:rgba(15,23,42,0.5);border-radius:10px;cursor:pointer;">
            <div style="display:flex;align-items:center;gap:10px;">
              <span>📧</span>
              <span style="font-size:14px;">Notifications par email</span>
            </div>
            <input type="checkbox" ${currentUser.notificationPreferences?.email ? 'checked' : ''} onchange="toggleNotification('email')" style="width:20px;height:20px;">
          </label>
          <label style="display:flex;align-items:center;justify-content:space-between;padding:12px;background:rgba(15,23,42,0.5);border-radius:10px;cursor:pointer;">
            <div style="display:flex;align-items:center;gap:10px;">
              <span>📱</span>
              <span style="font-size:14px;">Notifications SMS</span>
            </div>
            <input type="checkbox" ${currentUser.notificationPreferences?.sms ? 'checked' : ''} onchange="toggleNotification('sms')" style="width:20px;height:20px;">
          </label>
        </div>
      </div>
      
      <!-- Thème -->
      <div style="margin-bottom:20px;">
        <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:12px;font-weight:600;">🎨 APPARENCE</div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;">
          <button onclick="cycleUITheme()" style="padding:16px;border-radius:12px;border:1px solid var(--ui-card-border);background:linear-gradient(135deg,#1e293b,#0f172a);color:var(--ui-text-main);cursor:pointer;font-size:12px;">
            <div style="font-size:20px;margin-bottom:4px;">🌙</div>
            Thème UI
          </button>
          <button onclick="cycleMapTheme()" style="padding:16px;border-radius:12px;border:1px solid var(--ui-card-border);background:linear-gradient(135deg,#1e293b,#0f172a);color:var(--ui-text-main);cursor:pointer;font-size:12px;">
            <div style="font-size:20px;margin-bottom:4px;">🗺️</div>
            Thème carte
          </button>
          <button onclick="showNotification('🌍 Langue à venir', 'info')" style="padding:16px;border-radius:12px;border:1px solid var(--ui-card-border);background:linear-gradient(135deg,#1e293b,#0f172a);color:var(--ui-text-main);cursor:pointer;font-size:12px;">
            <div style="font-size:20px;margin-bottom:4px;">🌍</div>
            Langue
          </button>
        </div>
      </div>
      
      <!-- Confidentialité - Ce qui est visible publiquement -->
      <div style="margin-bottom:20px;">
        <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:8px;font-weight:600;">🔒 CONFIDENTIALITÉ</div>
        <div style="font-size:11px;color:var(--ui-text-muted);margin-bottom:12px;">Choisissez ce qui est visible par les autres utilisateurs</div>
        <div style="display:flex;flex-direction:column;gap:8px;">
          <!-- Toujours visibles (non modifiables) -->
          <div style="padding:10px 12px;background:rgba(0,255,195,0.1);border:1px solid rgba(0,255,195,0.2);border-radius:8px;display:flex;align-items:center;justify-content:space-between;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span>👤</span>
              <span style="font-size:13px;">Nom + Avatar</span>
            </div>
            <span style="font-size:11px;color:#00ffc3;font-weight:600;">Toujours visible</span>
          </div>
          
          <!-- Options modifiables -->
          <label style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:rgba(15,23,42,0.5);border-radius:8px;cursor:pointer;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span>📝</span>
              <span style="font-size:13px;">Ma bio / description</span>
            </div>
            <input type="checkbox" ${currentUser.privacySettings?.showBio !== false ? 'checked' : ''} onchange="togglePrivacy('showBio')" style="width:18px;height:18px;accent-color:#00ffc3;">
          </label>
          
          <label style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:rgba(15,23,42,0.5);border-radius:8px;cursor:pointer;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span>📧</span>
              <span style="font-size:13px;">Mon email</span>
            </div>
            <input type="checkbox" ${currentUser.privacySettings?.showEmail ? 'checked' : ''} onchange="togglePrivacy('showEmail')" style="width:18px;height:18px;accent-color:#00ffc3;">
          </label>
          
          <label style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:rgba(15,23,42,0.5);border-radius:8px;cursor:pointer;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span>📍</span>
              <span style="font-size:13px;">Mes adresses</span>
            </div>
            <input type="checkbox" ${currentUser.privacySettings?.showAddresses ? 'checked' : ''} onchange="togglePrivacy('showAddresses')" style="width:18px;height:18px;accent-color:#00ffc3;">
          </label>
          
          <label style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:rgba(15,23,42,0.5);border-radius:8px;cursor:pointer;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span>❤️</span>
              <span style="font-size:13px;">Mes favoris</span>
            </div>
            <input type="checkbox" ${currentUser.privacySettings?.showFavorites !== false ? 'checked' : ''} onchange="togglePrivacy('showFavorites')" style="width:18px;height:18px;accent-color:#00ffc3;">
          </label>
          
          <label style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:rgba(15,23,42,0.5);border-radius:8px;cursor:pointer;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span>📅</span>
              <span style="font-size:13px;">Mon agenda</span>
            </div>
            <input type="checkbox" ${currentUser.privacySettings?.showAgenda !== false ? 'checked' : ''} onchange="togglePrivacy('showAgenda')" style="width:18px;height:18px;accent-color:#00ffc3;">
          </label>
          
          <label style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:rgba(15,23,42,0.5);border-radius:8px;cursor:pointer;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span>🎉</span>
              <span style="font-size:13px;">Mes participations</span>
            </div>
            <input type="checkbox" ${currentUser.privacySettings?.showParticipating !== false ? 'checked' : ''} onchange="togglePrivacy('showParticipating')" style="width:18px;height:18px;accent-color:#00ffc3;">
          </label>
          
          <label style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:rgba(15,23,42,0.5);border-radius:8px;cursor:pointer;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span>👥</span>
              <span style="font-size:13px;">Mes amis</span>
            </div>
            <input type="checkbox" ${currentUser.privacySettings?.showFriends !== false ? 'checked' : ''} onchange="togglePrivacy('showFriends')" style="width:18px;height:18px;accent-color:#00ffc3;">
          </label>
          
          <label style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:rgba(15,23,42,0.5);border-radius:8px;cursor:pointer;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span>📊</span>
              <span style="font-size:13px;">Mes statistiques</span>
            </div>
            <input type="checkbox" ${currentUser.privacySettings?.showActivity !== false ? 'checked' : ''} onchange="togglePrivacy('showActivity')" style="width:18px;height:18px;accent-color:#00ffc3;">
          </label>
        </div>
      </div>
      
      <!-- Compte -->
      <div style="margin-bottom:20px;">
        <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:12px;font-weight:600;">👤 COMPTE</div>
        <div style="display:flex;flex-direction:column;gap:10px;">
          <button onclick="showNotification('📧 Modification email à venir', 'info')" style="padding:12px;border-radius:10px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;text-align:left;display:flex;align-items:center;gap:10px;font-size:14px;">
            <span>📧</span> Modifier mon email
          </button>
          <button onclick="showNotification('🔒 Modification mot de passe à venir', 'info')" style="padding:12px;border-radius:10px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;text-align:left;display:flex;align-items:center;gap:10px;font-size:14px;">
            <span>🔒</span> Modifier mon mot de passe
          </button>
          <button onclick="showNotification('🗑️ Suppression compte à venir', 'info')" style="padding:12px;border-radius:10px;border:1px solid rgba(239,68,68,0.3);background:rgba(239,68,68,0.05);color:#ef4444;cursor:pointer;text-align:left;display:flex;align-items:center;gap:10px;font-size:14px;">
            <span>🗑️</span> Supprimer mon compte
          </button>
        </div>
      </div>
      
      <button onclick="openAccountModal()" style="width:100%;padding:12px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;">
        ← Retour au compte
      </button>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
}

function toggleNotification(type) {
  if (!currentUser.notificationPreferences) {
    currentUser.notificationPreferences = { email: true, sms: false };
  }
  currentUser.notificationPreferences[type] = !currentUser.notificationPreferences[type];
  saveUserData();
  showNotification(`${type === 'email' ? '📧' : '📱'} Notifications ${type} ${currentUser.notificationPreferences[type] ? 'activées' : 'désactivées'}`, 'success');
}

// Basculer une option de confidentialité
// Modal Modifier le profil - Affiche le formulaire d'inscription complet
function openEditProfileModal() {
  console.log('✏️ openEditProfileModal appelé - Affichage formulaire d\'inscription complet pour modification');
  
  // Pré-remplir registerData avec les données actuelles de l'utilisateur
  const nameParts = (currentUser.name || '').split(' ');
  const addressValue = currentUser.postalAddress && typeof currentUser.postalAddress === 'object' 
    ? ((currentUser.postalAddress.address || '') + (currentUser.postalAddress.city ? ', ' + currentUser.postalAddress.city : '') + (currentUser.postalAddress.zip ? ' ' + currentUser.postalAddress.zip : '')).trim()
    : (currentUser.postalAddress || '');
  
  registerData = {
    email: currentUser.email || '',
    username: currentUser.username || '',
    password: '', // Ne pas pré-remplir le mot de passe pour la sécurité
    passwordConfirm: '',
    firstName: currentUser.firstName || nameParts[0] || '',
    lastName: currentUser.lastName || nameParts.slice(1).join(' ') || '',
    profilePhoto: currentUser.profilePhoto || (currentUser.avatar && currentUser.avatar.startsWith('http') ? currentUser.avatar : ''),
    postalAddress: addressValue,
    avatarId: currentUser.avatarId || 1,
    avatarDescription: currentUser.avatarDescription || '',
    addresses: currentUser.addresses || [],
    emailVerificationCode: null,
    emailVerified: true, // L'email est déjà vérifié
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
  
  // Marquer que c'est une modification (pas une nouvelle inscription)
  window.isEditingProfile = true;
  
  // Afficher le formulaire d'inscription complet
  if (typeof window.showProRegisterForm === 'function') {
    window.showProRegisterForm();
  } else if (typeof showProRegisterForm === 'function') {
    showProRegisterForm();
  } else {
    console.error('❌ showProRegisterForm non disponible');
    showNotification('⚠️ Erreur: formulaire non disponible', 'error');
  }
}

// Gérer le changement de photo de profil
function handleEditProfilePhoto(event) {
  const file = event.target.files[0];
  if (!file) return;
  
  if (!file.type.startsWith('image/')) {
    showNotification("⚠️ Veuillez sélectionner une image", "warning");
    return;
  }
  
  const reader = new FileReader();
  reader.onload = function(e) {
    const photoUrl = e.target.result;
    const preview = document.getElementById('edit-profile-photo-preview');
    if (preview) {
      preview.innerHTML = `<img src="${photoUrl}" style="width:100%;height:100%;object-fit:cover;" />`;
    }
    // Stocker temporairement pour la sauvegarde
    window.tempProfilePhoto = photoUrl;
  };
  reader.readAsDataURL(file);
}

// Sauvegarder les modifications du profil
async function saveProfileChanges() {
  const username = document.getElementById('edit-profile-username')?.value.trim();
  const address = document.getElementById('edit-profile-address')?.value.trim();
  const photo = window.tempProfilePhoto || currentUser.profilePhoto;
  
  if (!username || username.length < 3) {
    showNotification("⚠️ Le nom d'utilisateur doit contenir au moins 3 caractères", "warning");
    return;
  }
  
  // Mettre à jour currentUser
  currentUser.username = username;
  currentUser.postalAddress = address;
  if (photo) {
    currentUser.profilePhoto = photo;
  }
  
  // Sauvegarder dans localStorage
  safeSetItem('currentUser', JSON.stringify(currentUser));
  
  // Mettre à jour le backend si connecté
  if (currentUser.isLoggedIn && currentUser.id) {
    try {
      const response = await fetch(`${API_BASE_URL}/user/profile`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: currentUser.id,
          username: username,
          postalAddress: address,
          profilePhoto: photo
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.user) {
          currentUser = { ...currentUser, ...data.user };
          safeSetItem('currentUser', JSON.stringify(currentUser));
        }
      }
    } catch (error) {
      console.warn('Erreur sauvegarde profil backend:', error);
    }
  }
  
  // Mettre à jour l'UI
  updateAccountButton();
  updateUserUI();
  
  showNotification("✅ Profil modifié avec succès !", "success");
  openAccountModal();
}

// Exposer les fonctions globalement pour les onclick
// Exposer les fonctions globalement pour les onclick
window.openEditProfileModal = openEditProfileModal;
window.handleEditProfilePhoto = handleEditProfilePhoto;
window.saveProfileChanges = saveProfileChanges;

// Vérifier que les fonctions sont bien exposées
console.log('✅ Fonctions profil exposées:', {
  openEditProfileModal: typeof window.openEditProfileModal,
  handleEditProfilePhoto: typeof window.handleEditProfilePhoto,
  saveProfileChanges: typeof window.saveProfileChanges
});

function togglePrivacy(setting) {
  if (!currentUser.privacySettings) {
    currentUser.privacySettings = {
      showName: true,
      showAvatar: true,
      showBio: true,
      showEmail: false,
      showAddresses: false,
      showFavorites: true,
      showAgenda: true,
      showParticipating: true,
      showFriends: true,
      showActivity: true
    };
  }
  
  currentUser.privacySettings[setting] = !currentUser.privacySettings[setting];
  saveUserData();
  
  const labels = {
    showBio: 'Bio',
    showEmail: 'Email',
    showAddresses: 'Adresses',
    showFavorites: 'Favoris',
    showAgenda: 'Agenda',
    showParticipating: 'Participations',
    showFriends: 'Amis',
    showActivity: 'Statistiques'
  };
  
  showNotification(
    `${currentUser.privacySettings[setting] ? '👁️ Visible' : '🔒 Masqué'}: ${labels[setting] || setting}`, 
    'success'
  );
}

window.togglePrivacy = togglePrivacy;

function openFavoritesModal() {
  // Utiliser currentUser.favorites au lieu de currentUser.likes
  const favorites = currentUser.favorites.map(fav => {
    const type = fav.mode || fav.type;
    const id = parseInt(fav.id);
    const data = type === "event" ? eventsData : type === "booking" ? bookingsData : servicesData;
    const item = data.find(i => i.id === id);
    if (item) {
      return { ...item, favoriteId: fav.id };
    }
    return null;
  }).filter(Boolean);

  const html = `
    <div style="padding:10px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
        <h2 style="margin:0;font-size:18px;">❤️ Mes Favoris</h2>
        <button onclick="closePublishModal()" style="background:none;border:none;font-size:20px;cursor:pointer;color:var(--ui-text-muted);">✕</button>
      </div>
      
      ${favorites.length === 0 ? `
        <div style="text-align:center;padding:40px;color:var(--ui-text-muted);">
          <div style="font-size:48px;margin-bottom:16px;">💔</div>
          <p>Aucun favori pour le moment</p>
        </div>
      ` : `
        <div style="margin-bottom:12px;font-size:12px;color:var(--ui-text-muted);text-align:center;">
          ${favorites.length} ${favorites.length === 1 ? 'favori' : 'favoris'}
        </div>
        <div id="favorites-list-container" style="max-height:calc(80vh - 180px);overflow-y:auto;">
          ${favorites.slice(0, 20).map(item => `
            <div style="display:flex;gap:12px;padding:12px;border-radius:12px;margin-bottom:8px;background:rgba(15,23,42,0.5);border:1px solid var(--ui-card-border);cursor:pointer;" onclick="focusOnItem('${item.type}', ${item.id})">
              <div style="width:60px;height:60px;border-radius:8px;background:linear-gradient(135deg,#ef4444,#f97316);display:flex;align-items:center;justify-content:center;font-size:24px;">
                ${getCategoryEmoji(item)}
              </div>
              <div style="flex:1;">
                <div style="font-weight:600;margin-bottom:4px;">${escapeHtml(item.title || item.name)}</div>
                <div style="font-size:12px;color:var(--ui-text-muted);">${item.city}</div>
              </div>
            </div>
          `).join('')}
        </div>
        ${favorites.length > 20 ? `
          <div style="text-align:center;margin-top:12px;padding:12px;background:rgba(15,23,42,0.5);border-radius:8px;border:1px solid var(--ui-card-border);">
            <div style="font-size:12px;color:var(--ui-text-muted);margin-bottom:8px;">
              Affichage de 20 sur ${favorites.length} favoris
            </div>
            <button onclick="loadMoreFavorites()" style="padding:8px 16px;border-radius:8px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-size:12px;">
              Afficher plus (${Math.min(20, favorites.length - 20)} suivants)
            </button>
          </div>
        ` : ''}
      `}
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
  document.getElementById("publish-modal-backdrop").style.display = "flex";
  
  // Stocker les favoris complets pour la pagination
  window.favoritesFull = favorites;
  window.favoritesDisplayed = 20;
}

function loadMoreFavorites() {
  if (!window.favoritesFull) return;
  const container = document.getElementById("favorites-list-container");
  if (!container) return;
  
  const start = window.favoritesDisplayed;
  const end = Math.min(start + 20, window.favoritesFull.length);
  const newItems = window.favoritesFull.slice(start, end);
  
  newItems.forEach(item => {
    const itemHtml = `
      <div style="display:flex;gap:12px;padding:12px;border-radius:12px;margin-bottom:8px;background:rgba(15,23,42,0.5);border:1px solid var(--ui-card-border);cursor:pointer;" onclick="focusOnItem('${item.type}', ${item.id})">
        <div style="width:60px;height:60px;border-radius:8px;background:linear-gradient(135deg,#ef4444,#f97316);display:flex;align-items:center;justify-content:center;font-size:24px;">
          ${getCategoryEmoji(item)}
        </div>
        <div style="flex:1;">
          <div style="font-weight:600;margin-bottom:4px;">${escapeHtml(item.title || item.name)}</div>
          <div style="font-size:12px;color:var(--ui-text-muted);">${item.city}</div>
        </div>
      </div>
    `;
    container.insertAdjacentHTML('beforeend', itemHtml);
  });
  
  window.favoritesDisplayed = end;
  
  // Mettre à jour le bouton "Afficher plus"
  const moreButton = container.nextElementSibling?.querySelector('button');
  if (moreButton) {
    const remaining = window.favoritesFull.length - end;
    if (remaining > 0) {
      moreButton.textContent = `Afficher plus (${Math.min(20, remaining)} suivants)`;
    } else {
      moreButton.parentElement.remove();
    }
  }
}

function focusOnItem(type, id) {
  closePublishModal();
  const key = `${type}:${id}`;
  const marker = markerMap[key];
  if (marker && map) {
    map.setView(marker.getLatLng(), 14);
    setTimeout(() => marker.openPopup(), 300);
  }
}

function logout() {
    currentUser.isLoggedIn = false;
  showNotification("👋 À bientôt !", "info");
    closePublishModal();
}

// ============================================
// UTILITAIRES
// ============================================
function formatEventDateRange(startIso, endIso) {
  if (!startIso || !endIso) return "";
  const s = new Date(startIso);
  const e = new Date(endIso);

  const optD = { day: "2-digit", month: "2-digit" };
  const optT = { hour: "2-digit", minute: "2-digit" };

  const sd = s.toLocaleDateString("fr-CH", optD);
  const ed = e.toLocaleDateString("fr-CH", optD);
  const st = s.toLocaleTimeString("fr-CH", optT);
  const et = e.toLocaleTimeString("fr-CH", optT);

  if (sd === ed) return `${sd} ${st}–${et}`;
  return `${sd} ${st} – ${ed} ${et}`;
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// ============================================
// DRAG & DROP PANNEAU FILTRE
// ============================================
function initDragDropPanel() {
  const panel = document.getElementById("left-panel");
  if (!panel) return;
  
  let isDragging = false;
  let startX, startY, startLeft, startTop;
  
  panel.addEventListener("mousedown", (e) => {
    // Ne drag que si on clique sur l'en-tête
    if (e.target.closest("#explorer-columns") || e.target.closest("input") || e.target.closest("button")) {
      return;
    }
    
    isDragging = true;
    panel.classList.add("dragging");
    
    startX = e.clientX;
    startY = e.clientY;
    startLeft = panel.offsetLeft;
    startTop = panel.offsetTop;
    
    e.preventDefault();
  });
  
  document.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    
    const dx = e.clientX - startX;
    const dy = e.clientY - startY;
    
    panel.style.left = (startLeft + dx) + "px";
    panel.style.top = (startTop + dy) + "px";
  });
  
  document.addEventListener("mouseup", () => {
    isDragging = false;
    panel.classList.remove("dragging");
  });
}

// Initialiser après le chargement
document.addEventListener("DOMContentLoaded", () => {
  setTimeout(initDragDropPanel, 500);
});

// ============================================
// PLUS DE THÈMES
// ============================================
const EXTRA_THEMES = [
  {
    name: "Ocean Deep",
    bodyBg: "#0a192f",
    topbarBg: "#0a192f",
    cardBg: "linear-gradient(135deg,#0a192f,#112240)",
    cardBorder: "rgba(100,255,218,0.3)",
    textMain: "#ccd6f6",
    textMuted: "#8892b0",
    btnMainBg: "linear-gradient(135deg,#64ffda,#00bcd4)",
    btnMainText: "#0a192f",
    btnMainShadow: "0 8px 22px rgba(100,255,218,0.5)",
    btnAltBg: "rgba(17,34,64,0.9)",
    btnAltText: "#ccd6f6",
    pillBorder: "rgba(100,255,218,0.3)",
    logoColor: "#64ffda",
    taglineColor: "#8892b0"
  },
  {
    name: "Sunset Vibes",
    bodyBg: "linear-gradient(180deg,#1a1a2e,#16213e)",
    topbarBg: "rgba(26,26,46,0.95)",
    cardBg: "rgba(26,26,46,0.9)",
    cardBorder: "rgba(233,69,96,0.4)",
    textMain: "#edf2f4",
    textMuted: "#8d99ae",
    btnMainBg: "linear-gradient(135deg,#e94560,#ff6b6b)",
    btnMainText: "#1a1a2e",
    btnMainShadow: "0 8px 22px rgba(233,69,96,0.6)",
    btnAltBg: "rgba(22,33,62,0.9)",
    btnAltText: "#edf2f4",
    pillBorder: "rgba(233,69,96,0.4)",
    logoColor: "#e94560",
    taglineColor: "#8d99ae"
  },
  {
    name: "Forest Night",
    bodyBg: "#1b2d1b",
    topbarBg: "#1b2d1b",
    cardBg: "linear-gradient(135deg,#1b2d1b,#2d4a2d)",
    cardBorder: "rgba(144,238,144,0.4)",
    textMain: "#e8f5e9",
    textMuted: "#a5d6a7",
    btnMainBg: "linear-gradient(135deg,#66bb6a,#81c784)",
    btnMainText: "#1b2d1b",
    btnMainShadow: "0 8px 22px rgba(102,187,106,0.6)",
    btnAltBg: "rgba(45,74,45,0.9)",
    btnAltText: "#e8f5e9",
    pillBorder: "rgba(144,238,144,0.4)",
    logoColor: "#81c784",
    taglineColor: "#a5d6a7"
  }
];

// Ajouter les nouveaux thèmes
UI_THEMES.push(...EXTRA_THEMES);

// ============================================
// EXPOSE FUNCTIONS
// ============================================
window.switchMode = switchMode;
window.toggleLeftPanel = toggleLeftPanel;
window.toggleListView = toggleListView;
window.openPublishModal = openPublishModal;
window.closePublishModal = closePublishModal;
window.openRegisterModal = openRegisterModal;
window.showProRegisterForm = showProRegisterForm;
window.cycleUITheme = cycleUITheme;
window.cycleMapTheme = cycleMapTheme;
window.onSearchCity = onSearchCity;

// Exposer les fonctions du formulaire de publication
window.toggleRepeatOptions = toggleRepeatOptions;
window.updateRepeatPreview = updateRepeatPreview;
window.toggleAdvancedOptions = toggleAdvancedOptions;
window.initRepeatHandlers = initRepeatHandlers;
window.initMultipleImagesHandler = initMultipleImagesHandler;
window.onAction = onAction;
window.onBuyContact = onBuyContact;
window.toggleCategory = toggleCategory;
window.setTimeFilter = setTimeFilter;
window.openNextLevel = openNextLevel;
window.removeSelectedCategory = removeSelectedCategory;
window.closePopupModal = closePopupModal;
window.openPopupFromList = openPopupFromList;
window.closePopupModal = closePopupModal;
window.selectCityForSorting = selectCityForSorting;
window.resetExplorerFilter = resetExplorerFilter;
window.closeLeftPanel = closeLeftPanel;
window.toggleDateFilter = toggleDateFilter;
window.openAgendaModal = openAgendaModal;
window.toggleAgendaWindow = toggleAgendaWindow;
window.showAgendaMiniWindow = showAgendaMiniWindow;
window.hideAgendaMiniWindow = hideAgendaMiniWindow;
window.openLoginModal = openLoginModal;
window.simulateLogin = simulateLogin;
window.performLogin = performLogin;
window.openReviewModal = openReviewModal;
window.setRating = setRating;
window.submitReview = submitReview;
window.openDiscussionModal = openDiscussionModal;
window.openEventDiscussion = window.openEventDiscussion || function(type, id) {
  if (typeof window.openDiscussionModal === 'function') {
    window.openDiscussionModal(type, id);
  }
};
window.submitDiscussionComment = window.submitDiscussionComment || function(type, id) {
  // Déjà défini plus haut dans le code
};
window.showReplyForm = window.showReplyForm || function(commentId) {
  // Déjà défini plus haut dans le code
};
window.submitReply = window.submitReply || function(type, id, commentId) {
  // Déjà défini plus haut dans le code
};
window.loadReviewPage = loadReviewPage;
window.validateStep2 = validateStep2;
window.showRegisterStep1 = showRegisterStep1;
window.showRegisterStep2 = showRegisterStep2;
window.showRegisterStep3 = showRegisterStep3;
window.completeRegistration = completeRegistration;
window.openSubscriptionModal = openSubscriptionModal;
window.openCartModal = openCartModal;
window.openAccountModal = openAccountModal;

// Fonction formatDate globale
function formatDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString("fr-CH", { day: "2-digit", month: "short", year: date.getFullYear() !== new Date().getFullYear() ? "numeric" : undefined });
}
window.formatDate = formatDate;
window.openReportModal = openReportModal;
window.submitReport = submitReport;
window.openPaymentModal = openPaymentModal;
window.simulatePayment = simulatePayment; // Fallback
window.processContactPayment = processContactPayment;
window.processSubscriptionPayment = processSubscriptionPayment;
window.processCartCheckout = processCartCheckout;
window.loadUserSubscription = loadUserSubscription;
window.removeFromAgenda = removeFromAgenda;
window.showRegisterForm = showRegisterForm;
window.addAddressField = addAddressField;
window.removeAddressField = removeAddressField;
window.geocodeAddress = geocodeAddress;
window.showRegisterStep1 = showRegisterStep1;
window.showRegisterStep2 = showRegisterStep2;
window.showRegisterStep2_5 = showRegisterStep2_5;
window.showRegisterStep3 = showRegisterStep3;
window.validateEmailRealTime = validateEmailRealTime;
window.validateUsernameRealTime = validateUsernameRealTime;
window.validateNameRealTime = validateNameRealTime;
window.checkPasswordStrength = checkPasswordStrength;
window.togglePasswordVisibility = togglePasswordVisibility;
window.socialLogin = socialLogin;
window.showTermsModal = showTermsModal;
window.showPrivacyModal = showPrivacyModal;
window.sendVerificationCode = sendVerificationCode;
window.resendVerificationCode = resendVerificationCode;
window.verifyEmailCode = verifyEmailCode;
window.handleCodeInput = handleCodeInput;
window.handleCodeKeydown = handleCodeKeydown;
window.generateCaptcha = generateCaptcha;
window.completeRegistration = completeRegistration;
window.deleteAlertWithWarning = deleteAlertWithWarning;
window.openSubscriptionModal = openSubscriptionModal;
window.createAlert = createAlert;
window.removeAlert = removeAlert;
window.addEventAlert = addEventAlert;
window.selectPlan = selectPlan;
window.openPremiumPaymentModal = openPremiumPaymentModal;
window.simulatePremiumPayment = simulatePremiumPayment;
window.openAccountModal = openAccountModal;
window.openAboutModal = openAboutModal;
window.selectAvatar = selectAvatar;
window.openFavoritesModal = openFavoritesModal;
window.openFriendsModal = openFriendsModal;
// openGroupsModal est déjà exposé immédiatement après sa définition (ligne 10436)
// window.openGroupsModal = openGroupsModal; // DÉJÀ EXPOSÉ
// openSocialAlertsModal sera exposé après sa définition
// Fonction stub pour openGroupChannel (à implémenter si nécessaire)
function openGroupChannel(groupId) {
  console.warn('openGroupChannel appelé mais non implémenté:', groupId);
  showNotification('Fonctionnalité en cours de développement', 'info');
}
window.openGroupChannel = openGroupChannel;
// Fonction stub pour createGroup (à implémenter si nécessaire)
function createGroup() {
  console.warn('createGroup appelé mais non implémenté');
  showNotification('Fonctionnalité en cours de développement', 'info');
}
window.createGroup = createGroup;
// Fonction stub pour confirmCreateGroup (à implémenter si nécessaire)
function confirmCreateGroup() {
  console.warn('confirmCreateGroup appelé mais non implémenté');
  showNotification('Fonctionnalité en cours de développement', 'info');
}
window.confirmCreateGroup = confirmCreateGroup;
// Fonction stub pour changeGroupCountry (à implémenter si nécessaire)
function changeGroupCountry() {
  console.warn('changeGroupCountry appelé mais non implémenté');
  showNotification('Fonctionnalité en cours de développement', 'info');
}
window.changeGroupCountry = changeGroupCountry;
// Fonction stub pour sendGroupMessage (à implémenter si nécessaire)
function sendGroupMessage() {
  console.warn('sendGroupMessage appelé mais non implémenté');
  showNotification('Fonctionnalité en cours de développement', 'info');
}
window.sendGroupMessage = sendGroupMessage;
// Fonction stub pour inviteFriendFromPopup (à implémenter si nécessaire)
function inviteFriendFromPopup() {
  console.warn('inviteFriendFromPopup appelé mais non implémenté');
  showNotification('Fonctionnalité en cours de développement', 'info');
}
window.inviteFriendFromPopup = inviteFriendFromPopup;
window.inviteFriendsToEvent = inviteFriendsToEvent;
// sharePopup est déjà exposé après sa définition (ligne 7060)
// window.sharePopup = sharePopup; // DÉJÀ EXPOSÉ
// Fonction stub pour viewEventAttendees (à implémenter si nécessaire)
function viewEventAttendees(type, id) {
  console.warn('viewEventAttendees appelé mais non implémenté:', type, id);
  showNotification('Fonctionnalité en cours de développement', 'info');
}
window.viewEventAttendees = viewEventAttendees;
// Fonction stub pour shareToGroup (à implémenter si nécessaire)
function shareToGroup() {
  console.warn('shareToGroup appelé mais non implémenté');
  showNotification('Fonctionnalité en cours de développement', 'info');
}
window.shareToGroup = shareToGroup;
// Fonction stub pour shareToFriend (à implémenter si nécessaire)
function shareToFriend() {
  console.warn('shareToFriend appelé mais non implémenté');
  showNotification('Fonctionnalité en cours de développement', 'info');
}
window.shareToFriend = shareToFriend;
// copyShareLink est déjà défini ailleurs (ligne 7375)
// window.copyShareLink = copyShareLink;
// Fonction stub pour shareEventToChannel (à implémenter si nécessaire)
function shareEventToChannel() {
  console.warn('shareEventToChannel appelé mais non implémenté');
  showNotification('Fonctionnalité en cours de développement', 'info');
}
window.shareEventToChannel = shareEventToChannel;
// Fonction stub pour addToAgendaFromChannel (à implémenter si nécessaire)
function addToAgendaFromChannel(type, id) {
  console.warn('addToAgendaFromChannel appelé mais non implémenté:', type, id);
  // Utiliser la fonction existante toggleAgenda si disponible
  if (typeof toggleAgenda === 'function') {
    toggleAgenda(type, id);
  } else {
    showNotification('Fonctionnalité en cours de développement', 'info');
  }
}
window.addToAgendaFromChannel = addToAgendaFromChannel;
// Fonction stub pour reportMessage (à implémenter si nécessaire)
function reportMessage() {
  console.warn('reportMessage appelé mais non implémenté');
  showNotification('Fonctionnalité en cours de développement', 'info');
}
window.reportMessage = reportMessage;
// Fonction stub pour shareGroupChannel (à implémenter si nécessaire)
function shareGroupChannel() {
  console.warn('shareGroupChannel appelé mais non implémenté');
  showNotification('Fonctionnalité en cours de développement', 'info');
}
window.shareGroupChannel = shareGroupChannel;
// Fonction stub pour handleSocialAlert (à implémenter si nécessaire)
function handleSocialAlert() {
  console.warn('handleSocialAlert appelé mais non implémenté');
  showNotification('Fonctionnalité en cours de développement', 'info');
}
window.handleSocialAlert = handleSocialAlert;
// Fonction stub pour updateSocialAlertsCount (à implémenter si nécessaire)
function updateSocialAlertsCount() {
  console.warn('updateSocialAlertsCount appelé mais non implémenté');
  // Ne rien faire pour l'instant
}
window.updateSocialAlertsCount = updateSocialAlertsCount;
window.inviteFriendsToEvent = inviteFriendsToEvent;
window.filterInviteFriends = filterInviteFriends;
window.sendInvitationToFriend = sendInvitationToFriend;
window.openUserProfile = openUserProfile;
window.editProfile = editProfile;
window.saveProfile = saveProfile;
window.viewPhoto = viewPhoto;
window.viewVideo = viewVideo;

// ============================================
// INTÉGRATION BACKEND ET WEBSOCKET
// ============================================

// Connexion WebSocket pour notifications temps réel
let socket = null;
let socketConnected = false;

function initWebSocket() {
  if (!currentUser.isLoggedIn) return;
  
  try {
    // Pour Lambda/API Gateway, WebSocket nécessite un endpoint séparé
    // Pour l'instant, on simule avec polling
    // En production, utiliser: const wsUrl = 'wss://your-websocket-api.execute-api.region.amazonaws.com/production';
    
    // Simulation avec polling toutes les 5 secondes
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

// Vérifier les nouvelles notifications
async function checkForNewNotifications() {
  if (!currentUser.isLoggedIn) return;
  
  try {
    const response = await fetch(`${API_BASE_URL}/social/alerts?userId=${currentUser.id}&unreadOnly=true`);
    if (response.ok) {
      const data = await response.json();
      if (data.alerts && data.alerts.length > 0) {
        // Ajouter les nouvelles alertes
        data.alerts.forEach(alert => {
          if (!currentUser.socialAlerts.find(a => a.id === alert.id)) {
            currentUser.socialAlerts.push(alert);
          }
        });
        saveUserData();
        updateSocialAlertsCount();
      }
    }
  } catch (error) {
    console.error('Erreur vérification notifications:', error);
  }
}

// Vérifier les nouveaux messages dans les groupes actifs
async function checkForNewMessages() {
  if (!currentUser.isLoggedIn || !window.activeGroupChannels) return;
  
  for (const groupId of window.activeGroupChannels) {
    try {
      const response = await fetch(`${API_BASE_URL}/social/groups/${groupId}/messages?userId=${currentUser.id}&limit=1`);
      if (response.ok) {
        const data = await response.json();
        if (data.messages && data.messages.length > 0) {
          const latestMessage = data.messages[0];
          // Vérifier si c'est un nouveau message
          if (!window.groupChannels[groupId] || 
              !window.groupChannels[groupId].find(m => m.id === latestMessage.id)) {
            // Ajouter le nouveau message
            if (!window.groupChannels[groupId]) window.groupChannels[groupId] = [];
            window.groupChannels[groupId].unshift({
              id: latestMessage.id,
              from: latestMessage.userId,
              fromName: latestMessage.username,
              fromAvatar: currentUser.avatar,
              text: latestMessage.message,
              attachments: latestMessage.attachments || [],
              reactions: latestMessage.reactions || {},
              time: latestMessage.createdAt,
              status: latestMessage.status,
              type: 'user'
            });
            
            // Rafraîchir la vue si le canal est ouvert
            if (document.getElementById(`group-messages-${groupId}`)) {
              openGroupChannel(groupId, '', '', '');
            }
          }
        }
      }
    } catch (error) {
      console.error(`Erreur vérification messages groupe ${groupId}:`, error);
    }
  }
}

// Modérer une image avant upload
async function moderateImageBeforeUpload(imageUrl) {
  try {
    const response = await fetch(`${API_BASE_URL}/social/moderation/image`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        imageUrl: imageUrl,
        userId: currentUser.id
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      return data.isSafe;
    }
    return true; // En cas d'erreur, on accepte (sera modéré manuellement)
  } catch (error) {
    console.error('Erreur modération image:', error);
    return true; // En cas d'erreur, on accepte
  }
}

// Envoyer un message avec intégration backend
async function sendGroupMessageBackend(channelId, channelName, messageText) {
  if (!currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}/social/groups/${channelId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId: currentUser.id,
        message: messageText,
        attachments: []
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      
      // Ajouter le message localement
      if (!window.groupChannels) window.groupChannels = {};
      if (!window.groupChannels[channelId]) window.groupChannels[channelId] = [];
      
      window.groupChannels[channelId].push({
        id: data.messageId,
        from: currentUser.id,
        fromName: currentUser.name,
        fromAvatar: currentUser.avatar,
        text: messageText,
        time: data.createdAt,
        status: data.status,
        type: 'user'
      });
      
      // Si en attente de modération, afficher un message
      if (data.status === 'pending_moderation') {
        showNotification("⚠️ Votre message est en attente de modération", "warning");
      }
      
      // Rafraîchir la vue
      openGroupChannel(channelId, channelName, '', '');
      
      // Simuler l'envoi via WebSocket
      if (socketConnected) {
        // En production, utiliser socket.emit('send_message', {...})
        console.log('Message envoyé via backend');
      }
    } else {
      const error = await response.json();
      showNotification(`Erreur: ${error.error}`, "error");
    }
  } catch (error) {
    console.error('Erreur envoi message:', error);
    showNotification("Erreur lors de l'envoi du message", "error");
  }
}

// Ajouter une réaction à un message
async function addMessageReaction(messageId, emoji) {
  if (!currentUser.isLoggedIn) return;
  
  try {
    const response = await fetch(`${API_BASE_URL}/social/messages/${messageId}/reaction`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId: currentUser.id,
        emoji: emoji
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      return data.reactions;
    }
  } catch (error) {
    console.error('Erreur ajout réaction:', error);
  }
  return null;
}

// Mettre à jour la fonction sendGroupMessage pour utiliser le backend
const originalSendGroupMessage = sendGroupMessage;
sendGroupMessage = function(channelId, channelName) {
  const input = document.getElementById(`group-input-${channelId}`);
  if (!input || !input.value.trim()) return;
  
  const messageText = input.value.trim();
  input.value = '';
  
  // Utiliser le backend
  sendGroupMessageBackend(channelId, channelName, messageText);
};

// Mettre à jour saveProfile pour modérer les images
const originalSaveProfile = saveProfile;
saveProfile = async function() {
  const bio = document.getElementById("edit-profile-bio")?.value.trim() || '';
  const photosText = document.getElementById("edit-profile-photos")?.value.trim() || '';
  const photos = photosText.split('\n').filter(url => url.trim() && url.startsWith('http'));
  
  // Modérer chaque photo
  const photosFiltered = [];
  for (const photo of photos) {
    const isSafe = await moderateImageBeforeUpload(photo);
    if (isSafe) {
      photosFiltered.push(photo);
    } else {
      showNotification(`⚠️ Photo rejetée (contenu inapproprié): ${photo.substring(0, 50)}...`, "warning");
    }
  }
  
  // Sauvegarder via backend
  try {
    const response = await fetch(`${API_BASE_URL}/social/profile`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId: currentUser.id,
        bio: bio,
        profilePhotos: photosFiltered,
        profileVideos: currentUser.profileVideos || [],
        profileLinks: currentUser.profileLinks || []
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      currentUser.bio = bio;
      currentUser.profilePhotos = photosFiltered;
      
      saveUserData();
      showNotification(`✅ Profil mis à jour ! ${data.photosAccepted} photos acceptées, ${data.photosRejected} rejetées`, "success");
      openUserProfile();
    } else {
      const error = await response.json();
      showNotification(`Erreur: ${error.error}`, "error");
    }
  } catch (error) {
    console.error('Erreur sauvegarde profil:', error);
    showNotification("Erreur lors de la sauvegarde", "error");
  }
};

// Initialiser WebSocket au login - wrapper autour de performLogin existante
(function() {
  const originalPerformLogin = window.performLogin;
  window.performLogin = async function() {
    await originalPerformLogin();
    if (currentUser.isLoggedIn) {
      initWebSocket();
    }
  };
})();

// Mettre à jour openGroupChannel pour charger les messages depuis le backend
const originalOpenGroupChannel = openGroupChannel;
openGroupChannel = async function(channelId, channelName, channelType, channelCategory) {
  if (!currentUser.isLoggedIn) {
    openLoginModal();
    return;
  }
  
  // Marquer le canal comme actif
  if (!window.activeGroupChannels) window.activeGroupChannels = [];
  if (!window.activeGroupChannels.includes(channelId)) {
    window.activeGroupChannels.push(channelId);
  }
  
  // Charger les messages depuis le backend
  try {
    const response = await fetch(`${API_BASE_URL}/social/groups/${channelId}/messages?userId=${currentUser.id}&limit=50`);
    if (response.ok) {
      const data = await response.json();
      
      // Convertir les messages du backend au format local
      if (!window.groupChannels) window.groupChannels = {};
      window.groupChannels[channelId] = data.messages.map(msg => ({
        id: msg.id,
        from: msg.userId,
        fromName: msg.username,
        fromAvatar: currentUser.avatar,
        text: msg.message,
        attachments: msg.attachments || [],
        reactions: msg.reactions || {},
        time: msg.createdAt,
        status: msg.status,
        type: 'user'
      })).reverse(); // Inverser pour avoir les plus anciens en premier
      
      // Ajouter un message système si vide
      if (window.groupChannels[channelId].length === 0) {
        window.groupChannels[channelId] = [{
          from: 'system',
          fromName: 'Système',
          text: `Bienvenue dans le canal "${channelName}" ! 👋`,
          time: new Date().toISOString(),
          type: 'system'
        }];
      }
    }
  } catch (error) {
    console.error('Erreur chargement messages:', error);
    // Utiliser les messages locaux en fallback
    if (!window.groupChannels) window.groupChannels = {};
    if (!window.groupChannels[channelId]) {
      window.groupChannels[channelId] = [{
        from: 'system',
        fromName: 'Système',
        text: `Bienvenue dans le canal "${channelName}" ! 👋`,
        time: new Date().toISOString(),
        type: 'system'
      }];
    }
  }
  
  // Appeler la fonction originale
  originalOpenGroupChannel(channelId, channelName, channelType, channelCategory);
};

// Améliorer l'affichage des messages avec réactions
function renderMessageWithReactions(msg, idx, channelId) {
  if (msg.type === 'system') return '';
  
  const reactions = msg.reactions || {};
  const hasReactions = Object.keys(reactions).length > 0;
  const userReacted = hasReactions && Object.values(reactions).some(userIds => 
    Array.isArray(userIds) && userIds.includes(currentUser.id)
  );
  
  const reactionsHtml = hasReactions ? `
    <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:8px;">
      ${Object.entries(reactions).map(([emoji, userIds]) => {
        const count = Array.isArray(userIds) ? userIds.length : (typeof userIds === 'number' ? userIds : 0);
        const userHasReacted = Array.isArray(userIds) && userIds.includes(currentUser.id);
        return `
          <button onclick="toggleReaction('${channelId}', ${idx}, '${emoji}')" 
                  style="display:flex;align-items:center;gap:4px;padding:4px 8px;border-radius:999px;border:1px solid ${userHasReacted ? 'rgba(0,255,195,0.5)' : 'var(--ui-card-border)'};background:${userHasReacted ? 'rgba(0,255,195,0.2)' : 'rgba(15,23,42,0.5)'};color:${userHasReacted ? '#00ffc3' : 'var(--ui-text-muted)'};font-size:12px;cursor:pointer;transition:all 0.2s;"
                  onmouseover="this.style.background='rgba(0,255,195,0.3)'"
                  onmouseout="this.style.background='${userHasReacted ? 'rgba(0,255,195,0.2)' : 'rgba(15,23,42,0.5)'}'">
            <span>${emoji}</span>
            <span>${count}</span>
          </button>
        `;
      }).join('')}
      <button onclick="showReactionPicker('${channelId}', ${idx})" 
              style="padding:4px 8px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-muted);font-size:12px;cursor:pointer;transition:all 0.2s;"
              onmouseover="this.style.background='rgba(0,255,195,0.1)'"
              onmouseout="this.style.background='transparent'">
        ➕
      </button>
    </div>
  ` : `
    <button onclick="showReactionPicker('${channelId}', ${idx})" 
            style="margin-top:8px;padding:4px 8px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-muted);font-size:12px;cursor:pointer;transition:all 0.2s;"
            onmouseover="this.style.background='rgba(0,255,195,0.1)'"
            onmouseout="this.style.background='transparent'">
      ➕ Réagir
    </button>
  `;
  
  return reactionsHtml;
}

// Afficher le sélecteur de réactions
function showReactionPicker(channelId, messageIndex) {
  const emojis = ['👍', '❤️', '😂', '😮', '😢', '🔥', '🎉', '👏'];
  
  const html = `
    <div style="padding:16px;max-width:300px;margin:0 auto;">
      <h3 style="margin:0 0 16px 0;font-size:18px;font-weight:600;color:#fff;">Réagir</h3>
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;">
        ${emojis.map(emoji => `
          <button onclick="addReactionToMessage('${channelId}', ${messageIndex}, '${emoji}');closePublishModal();" 
                  style="padding:12px;border-radius:12px;border:1px solid var(--ui-card-border);background:rgba(15,23,42,0.5);font-size:24px;cursor:pointer;transition:all 0.2s;"
                  onmouseover="this.style.background='rgba(0,255,195,0.2)';this.style.transform='scale(1.1)'"
                  onmouseout="this.style.background='rgba(15,23,42,0.5)';this.style.transform='scale(1)'">
            ${emoji}
          </button>
        `).join('')}
      </div>
      <button onclick="closePublishModal()" style="width:100%;margin-top:16px;padding:10px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);cursor:pointer;font-weight:600;">
        Annuler
      </button>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
  document.getElementById("publish-modal-backdrop").style.display = "flex";
}

// Ajouter une réaction à un message
async function addReactionToMessage(channelId, messageIndex, emoji) {
  const messages = window.groupChannels[channelId];
  if (!messages || messageIndex >= messages.length) return;
  
  const message = messages[messageIndex];
  if (!message.id) {
    showNotification("⚠️ Impossible de réagir à ce message", "warning");
    return;
  }
  
  const reactions = await addMessageReaction(message.id, emoji);
  if (reactions) {
    message.reactions = reactions;
    // Rafraîchir uniquement la vue sans recharger depuis le backend
    const messagesDiv = document.getElementById(`group-messages-${channelId}`);
    if (messagesDiv) {
      // Trouver le message dans le DOM et mettre à jour les réactions
      const messageElement = messagesDiv.children[messageIndex];
      if (messageElement) {
        const reactionsContainer = messageElement.querySelector('.message-reactions');
        if (reactionsContainer) {
          reactionsContainer.outerHTML = renderMessageWithReactions(message, messageIndex, channelId);
        }
      }
    }
  }
}

// Toggle une réaction
async function toggleReaction(channelId, messageIndex, emoji) {
  await addReactionToMessage(channelId, messageIndex, emoji);
}

window.initWebSocket = initWebSocket;
window.addReactionToMessage = addReactionToMessage;
window.toggleReaction = toggleReaction;
window.showReactionPicker = showReactionPicker;
window.moderateImageBeforeUpload = moderateImageBeforeUpload;
window.searchUsers = searchUsers;
window.sendFriendRequest = sendFriendRequest;
window.acceptFriendRequest = acceptFriendRequest;
window.declineFriendRequest = declineFriendRequest;
window.removeFriend = removeFriend;
window.openChatWith = openChatWith;
window.sendChatMessage = sendChatMessage;
window.focusOnItem = focusOnItem;
window.logout = logout;
window.playPreview = playPreview;
window.openEcoMissionModal = openEcoMissionModal;
window.makeDonation = makeDonation;
window.openCartModal = openCartModal;
window.addToCart = addToCart;
window.removeFromCart = removeFromCart;
window.checkoutCart = checkoutCart;
window.openAlertsView = openAlertsView;
window.openProximityAlertsView = openProximityAlertsView;
window.closeProximityAlertsView = closeProximityAlertsView;
window.removeProximityAlert = removeProximityAlert;
window.openItemFromProximityAlert = openItemFromProximityAlert;
// Compatibilité : rediriger openAlertsModal vers openSubscriptionModal
window.openAlertsModal = function() {
  console.warn("openAlertsModal() est obsolète, redirection vers openSubscriptionModal()");
  openSubscriptionModal();
};
window.closeAlertsView = closeAlertsView;
window.openAddAlarmModal = openAddAlarmModal;
window.toggleAlarmItemSelection = toggleAlarmItemSelection;
window.saveAlarm = saveAlarm;
window.closeAddAlarmModal = closeAddAlarmModal;
window.closeAlertsLoginPopup = closeAlertsLoginPopup;
window.closeAlertsLoginPopupAndOpenAlerts = closeAlertsLoginPopupAndOpenAlerts;
window.closeStatusChangeNotification = closeStatusChangeNotification;
window.addEventToAlertsFromNotification = addEventToAlertsFromNotification;
window.openEventFromAlert = openEventFromAlert;

// ============================================
// GESTION DES LANGUES - STRATÉGIE MONDIALE #1
// ============================================
//
// 🎯 OBJECTIF : ÊTRE LA PLATEFORME ÉVÉNEMENTIELLE LA PLUS MULTILINGUE AU MONDE
//
// 📋 STRATÉGIE COMPLÈTE POUR DEVENIR #1 MONDIAL :
//
// 1. COUVERTURE LINGUISTIQUE MAXIMALE
//    ✅ Phase 1 (ACTUELLE) : 5 langues principales (FR, EN, ES, ZH, HI)
//       → Couvre ~70% de la population mondiale
//    🔄 Phase 2 : Ajouter 10 langues supplémentaires
//       → Arabe (AR), Portugais (PT), Russe (RU), Japonais (JA), 
//         Allemand (DE), Italien (IT), Coréen (KO), Turc (TR), 
//         Polonais (PL), Néerlandais (NL)
//       → Couvre ~85% de la population mondiale
//    🚀 Phase 3 : Support de 50+ langues (via compte utilisateur)
//       → Toutes les langues majeures + langues régionales
//       → Couvre ~95% de la population mondiale
//
// 2. SYSTÈME DE TRADUCTION HYBRIDE (QUALITÉ MAXIMALE)
//    A. TRADUCTIONS MANUELLES (Priorité #1 - Meilleure qualité)
//       → Lors de la publication, l'utilisateur peut ajouter des traductions
//       → Système de validation par la communauté
//       → Traductions certifiées par des traducteurs professionnels
//       → Stockage : item.translations = { en: "...", es: "...", etc. }
//
//    B. TRADUCTION AUTOMATIQUE (Fallback - Qualité acceptable)
//       → API Google Translate (meilleure qualité, payant)
//       → API DeepL (excellente qualité, payant)
//       → API LibreTranslate (gratuit, qualité moyenne)
//       → Cache agressif pour éviter les coûts
//
//    C. DÉTECTION AUTOMATIQUE DE LA LANGUE
//       → Détecter la langue du contenu source (titre, description)
//       → Utiliser la bonne traduction selon la langue de l'utilisateur
//
// 3. TRADUCTION EN TEMPS RÉEL
//    ✅ Interface utilisateur : Traduite instantanément (dictionnaire)
//    ✅ Contenu événements : Traduit à la volée (cache + API)
//    ✅ Commentaires : Traduction à la demande (bouton "Traduire")
//    ✅ Catégories : Dictionnaire multilingue complet
//    ✅ Messages système : Tous traduits
//
// 4. EXPÉRIENCE UTILISATEUR OPTIMALE
//    ✅ Détection automatique de la langue du navigateur
//    ✅ Changement de langue en 1 clic (sans rechargement)
//    ✅ Sauvegarde de la préférence (localStorage + compte)
//    ✅ Traduction contextuelle (selon le contenu)
//    ✅ Support RTL (arabe, hébreu) pour l'interface
//
// 5. OPTIMISATIONS PERFORMANCE
//    ✅ Cache local (localStorage) pour les traductions fréquentes
//    ✅ Cache serveur (base de données) pour éviter les appels API
//    ✅ Lazy loading : Traduire seulement ce qui est visible
//    ✅ Préchargement : Traductions des événements populaires
//    ✅ CDN : Servir les traductions depuis un CDN
//
// 6. QUALITÉ DES TRADUCTIONS
//    ✅ Système de notation des traductions (utilisateurs)
//    ✅ Suggestions d'amélioration (crowdsourcing)
//    ✅ Traductions professionnelles pour les événements premium
//    ✅ Vérification par IA (détecter les erreurs)
//
// 7. MONÉTISATION
//    ✅ Traductions gratuites pour les utilisateurs
//    ✅ Traductions premium pour les organisateurs (meilleure visibilité)
//    ✅ Service de traduction professionnelle (option payante)
//    ✅ API de traduction pour les partenaires
//
// 8. AVANTAGE CONCURRENTIEL
//    ✅ Aucune plateforme événementielle n'offre un multilinguisme aussi complet
//    ✅ Accessible à 95% de la population mondiale
//    ✅ Expérience native dans la langue de l'utilisateur
//    ✅ Communauté mondiale unie
//
// 📊 MÉTRIQUES DE SUCCÈS :
//    - Nombre de langues supportées : 50+
//    - % de contenu traduit : 90%+
//    - Temps de traduction : <100ms
//    - Satisfaction utilisateurs : 95%+
//    - Couverture mondiale : 95%+
//
// 🔧 IMPLÉMENTATION TECHNIQUE :
//
// 1. INTERFACE UTILISATEUR (UI) :
//    - Tous les textes de l'interface (boutons, labels, messages)
//    - Géré par le dictionnaire `translations` ci-dessous
//    - Fonction `t(key)` pour obtenir la traduction
//    - Fonction `updateUITranslations()` met à jour l'UI dynamiquement
//
// 2. CONTENU DES ÉVÉNEMENTS (Events/Booking/Service) :
//    - Titres, descriptions, catégories, adresses
//    - Solution A : API de traduction (Google Translate, DeepL, etc.)
//      → Traduction automatique à la volée lors de l'affichage
//      → Cache des traductions pour éviter les appels répétés
//    - Solution B : Base de données multilingue
//      → Chaque événement stocke ses traductions dans plusieurs langues
//      → Lors de la publication, l'utilisateur peut ajouter des traductions
//    - Solution C : Hybrid (recommandé)
//      → Traductions manuelles prioritaires (meilleure qualité)
//      → Fallback sur traduction automatique si manquant
//
// 3. IMPLÉMENTATION TECHNIQUE :
//    - Frontend : Fonction `translateContent(item, lang)` qui :
//      a) Cherche une traduction manuelle dans item.translations[lang]
//      b) Si absente, appelle l'API de traduction
//      c) Cache le résultat dans localStorage/sessionStorage
//    - Backend : Endpoint `/api/translate` qui :
//      a) Reçoit le texte source + langue cible
//      b) Vérifie le cache en base de données
//      c) Si absent, appelle l'API externe et sauvegarde
//      d) Retourne la traduction
//
// 4. EXEMPLE D'UTILISATION :
//    - Utilisateur sélectionne "English"
//    - Tous les popups affichent les événements en anglais
//    - Les descriptions sont traduites automatiquement
//    - Les catégories sont traduites (via dictionnaire)
//    - L'interface est traduite (via `translations`)
//
// 5. OPTIMISATIONS :
//    - Cache agressif des traductions (éviter les appels répétés)
//    - Traduction lazy (seulement ce qui est visible)
//    - Préchargement des traductions courantes
//    - Support des langues RTL (arabe, hébreu)
//
// ============================================
// DICTIONNAIRE DE TRADUCTIONS COMPLET (déplacé au début du fichier)
// ============================================
// Ce dictionnaire a été déplacé après la déclaration de currentLanguage pour éviter les erreurs d'initialisation
// L'ancienne déclaration a été supprimée - voir ligne 55 pour la nouvelle déclaration

// ============================================
// API DE TRADUCTION - INTÉGRATION
// ============================================
//
// 🎯 MEILLEURES APIs DE TRADUCTION (avec liens) :
//

// Initialisation du dictionnaire de traductions complet
// NOTE: Cette section a été supprimée car les traductions sont déjà définies ailleurs dans le fichier
// (voir lignes 219-431 pour la structure complète et correcte)
if (typeof window !== 'undefined') {
  window.translations = window.translations || { fr: {}, en: {}, es: {}, zh: {}, hi: {} };
}

// NOTE: Section de traductions mal formée supprimée (lignes 12663-12860)
// Les traductions sont déjà définies correctement ailleurs dans le fichier (lignes 219-431)

// ============================================
// API DE TRADUCTION - INTÉGRATION
// ============================================
//
// 🎯 MEILLEURES APIs DE TRADUCTION (avec liens) :
//
// 1. GOOGLE CLOUD TRANSLATE API (RECOMMANDÉ - Meilleure qualité)
//    📍 Lien : https://cloud.google.com/translate/docs/setup
//    💰 Prix : 20$/million de caractères (gratuit jusqu'à 500k/mois)
//    ✅ Avantages : Meilleure qualité, support 100+ langues, très rapide
//    ✅ Paiement : Carte bancaire, Twint via Stripe
//    📝 Documentation : https://cloud.google.com/translate/docs/reference/rest/v2/translate
//
// 2. DEEPL API (EXCELLENTE QUALITÉ - Spécialisé européen)
// ============================================
// API DE TRADUCTION - INTÉGRATION
// ============================================
//
// 🎯 MEILLEURES APIs DE TRADUCTION (avec liens) :
//
// 1. GOOGLE CLOUD TRANSLATE API (RECOMMANDÉ - Meilleure qualité)
//    📍 Lien : https://cloud.google.com/translate/docs/setup
//    💰 Prix : 20$/million de caractères (gratuit jusqu'à 500k/mois)
//    ✅ Avantages : Meilleure qualité, support 100+ langues, très rapide
//    ✅ Paiement : Carte bancaire, Twint via Stripe
//    📝 Documentation : https://cloud.google.com/translate/docs/reference/rest/v2/translate
//
// 2. DEEPL API (EXCELLENTE QUALITÉ - Spécialisé européen)
//    📍 Lien : https://www.deepl.com/fr/pro-api
//    💰 Prix : 25€/million de caractères (gratuit jusqu'à 500k/mois)
//    ✅ Avantages : Meilleure qualité pour langues européennes, très naturel
//    ✅ Paiement : Carte bancaire, PayPal, Twint via Stripe
//    📝 Documentation : https://www.deepl.com/fr/docs-api
//
// 3. AZURE TRANSLATOR (Microsoft - Bon compromis)
//    📍 Lien : https://azure.microsoft.com/fr-fr/services/cognitive-services/translator/
//    💰 Prix : 10$/million de caractères (gratuit jusqu'à 2M/mois)
//    ✅ Avantages : Bon prix, bonne qualité, intégration facile
//    ✅ Paiement : Carte bancaire, Twint via Stripe
//    📝 Documentation : https://docs.microsoft.com/fr-fr/azure/cognitive-services/translator/
//
// 4. LIBRETRANSLATE (GRATUIT - Open Source)
//    📍 Lien : https://libretranslate.com/
//    💰 Prix : GRATUIT (ou self-hosted)
//    ⚠️ Avantages : Gratuit, open source
//    ⚠️ Inconvénients : Qualité moindre, limité en langues
//    📝 Documentation : https://github.com/LibreTranslate/LibreTranslate
//
// 💡 RECOMMANDATION : Utiliser GOOGLE CLOUD TRANSLATE pour la production
//    → Meilleure qualité mondiale
//    → Support de toutes les langues
//    → Très fiable et rapide
//    → Paiement flexible (Twint via Stripe)
//
// 🔧 CONFIGURATION :
//    1. Créer un compte Google Cloud : https://console.cloud.google.com/
//    2. Activer l'API Translate : https://console.cloud.google.com/apis/library/translate.googleapis.com
//    3. Créer une clé API : https://console.cloud.google.com/apis/credentials
//    4. Configurer le paiement (Twint via Stripe accepté)
//    5. Mettre la clé dans les variables d'environnement (NE JAMAIS la commiter!)
//
// Cache pour les traductions de contenu (évite les appels répétés)
const contentTranslationCache = {};

// ============================================
// SYSTÈME INTELLIGENT MULTI-PROVIDER DE TRADUCTION
// ============================================
// Stratégie #1 Mondial : Utiliser plusieurs providers selon la région/langue
// pour optimiser qualité, coûts et vitesse

// Configuration des providers de traduction
const TRANSLATION_PROVIDERS = {
  google: {
    name: "Google Cloud Translate",
    apiKey: "", // À configurer
    endpoint: "https://translation.googleapis.com/language/translate/v2",
    regions: ["global"], // Toutes les régions
    languages: ["all"], // Toutes les langues
    quality: "excellent",
    speed: "very_fast",
    cost: "medium",
    priority: 1 // Priorité pour l'Europe et langues principales
  },
  deepl: {
    name: "DeepL API",
    apiKey: "", // À configurer
    endpoint: "https://api-free.deepl.com/v2/translate",
    regions: ["europe", "americas"], // Spécialisé Europe/Amériques
    languages: ["en", "fr", "de", "es", "it", "pt", "ru", "pl", "nl", "ja", "zh"],
    quality: "excellent", // Meilleure qualité pour langues européennes
    speed: "fast",
    cost: "medium",
    priority: 2 // Priorité pour langues européennes
  },
  azure: {
    name: "Azure Translator",
    apiKey: "", // À configurer
    endpoint: "https://api.cognitive.microsofttranslator.com/translate",
    regions: ["global"],
    languages: ["all"],
    quality: "very_good",
    speed: "fast",
    cost: "low", // Meilleur rapport qualité/prix
    priority: 3 // Fallback économique
  },
  libretranslate: {
    name: "LibreTranslate",
    apiKey: "", // Optionnel (gratuit)
    endpoint: "https://libretranslate.com/translate",
    regions: ["global"],
    languages: ["en", "fr", "es", "de", "it", "pt", "ru", "zh", "ja"],
    quality: "good",
    speed: "medium",
    cost: "free",
    priority: 4 // Fallback gratuit
  }
};

// Mapping intelligent région/langue → provider optimal
const INTELLIGENT_PROVIDER_MAPPING = {
  // Europe → DeepL (meilleure qualité) ou Google (fallback)
  "europe": {
    primary: "deepl",
    fallback: "google",
    languages: ["fr", "en", "de", "es", "it", "pt", "ru", "pl", "nl", "cs", "sk", "hu", "ro", "bg", "hr", "sl", "et", "lv", "lt", "fi", "sv", "da", "no", "is", "ga", "mt", "el"]
  },
  // Amériques → Google (meilleure couverture) ou DeepL
  "americas": {
    primary: "google",
    fallback: "deepl",
    languages: ["en", "es", "pt", "fr"]
  },
  // Asie → Google (meilleure couverture langues asiatiques)
  "asia": {
    primary: "google",
    fallback: "azure",
    languages: ["zh", "ja", "ko", "hi", "th", "vi", "id", "ms", "tl", "my", "km", "lo"]
  },
  // Afrique → Google (meilleure couverture)
  "africa": {
    primary: "google",
    fallback: "azure",
    languages: ["ar", "sw", "am", "zu", "xh", "af", "yo", "ig", "ha", "fr", "en", "pt"]
  },
  // Moyen-Orient → Google (meilleure couverture arabe)
  "middle_east": {
    primary: "google",
    fallback: "azure",
    languages: ["ar", "he", "fa", "tr", "ku"]
  },
  // Océanie → Google ou DeepL
  "oceania": {
    primary: "google",
    fallback: "deepl",
    languages: ["en", "fr", "mi", "haw"]
  }
};

// Fonction intelligente pour sélectionner le meilleur provider
function getBestProviderForTranslation(sourceLang, targetLang, region = null) {
  // Si région spécifiée, utiliser le mapping intelligent
  if (region && INTELLIGENT_PROVIDER_MAPPING[region]) {
    const mapping = INTELLIGENT_PROVIDER_MAPPING[region];
    const provider = TRANSLATION_PROVIDERS[mapping.primary];
    
    // Vérifier si le provider supporte la langue
    if (provider && (provider.languages.includes(targetLang) || provider.languages.includes("all"))) {
      if (provider.apiKey) return mapping.primary;
    }
    
    // Fallback
    const fallbackProvider = TRANSLATION_PROVIDERS[mapping.fallback];
    if (fallbackProvider && fallbackProvider.apiKey) {
      return mapping.fallback;
    }
  }
  
  // Détection automatique de la région selon la langue
  let detectedRegion = "global";
  
  // Langues européennes → Europe
  if (["fr", "de", "es", "it", "pt", "ru", "pl", "nl", "cs", "sk", "hu", "ro", "bg", "hr", "sl", "et", "lv", "lt", "fi", "sv", "da", "no"].includes(targetLang)) {
    detectedRegion = "europe";
  }
  // Langues asiatiques → Asie
  else if (["zh", "ja", "ko", "hi", "th", "vi", "id", "ms", "tl", "my", "km", "lo"].includes(targetLang)) {
    detectedRegion = "asia";
  }
  // Langues arabes → Moyen-Orient
  else if (["ar", "he", "fa"].includes(targetLang)) {
    detectedRegion = "middle_east";
  }
  
  // Utiliser le mapping détecté
  if (INTELLIGENT_PROVIDER_MAPPING[detectedRegion]) {
    const mapping = INTELLIGENT_PROVIDER_MAPPING[detectedRegion];
    const provider = TRANSLATION_PROVIDERS[mapping.primary];
    
    if (provider && provider.apiKey && (provider.languages.includes(targetLang) || provider.languages.includes("all"))) {
      return mapping.primary;
    }
    
    const fallbackProvider = TRANSLATION_PROVIDERS[mapping.fallback];
    if (fallbackProvider && fallbackProvider.apiKey) {
      return mapping.fallback;
    }
  }
  
  // Fallback final : Google (si disponible) ou Azure ou LibreTranslate
  if (TRANSLATION_PROVIDERS.google.apiKey) return "google";
  if (TRANSLATION_PROVIDERS.azure.apiKey) return "azure";
  if (TRANSLATION_PROVIDERS.libretranslate.apiKey) return "libretranslate";
  
  return null; // Aucun provider disponible
}

// Configuration globale (pour compatibilité)
const TRANSLATION_API_CONFIG = {
  provider: "auto", // "auto" = sélection intelligente
  apiKey: "", // Déprécié, utiliser TRANSLATION_PROVIDERS
  cacheEnabled: true,
  cacheMaxSize: 10000
};

// ============================================
// TRADUCTION AUTOMATIQUE COMPLÈTE - IA
// ============================================
// Fonction pour traduire automatiquement TOUT le contenu d'un item
// (titre, description, catégories, etc.) - Utilisée par l'IA
async function translateItemContentAuto(item, targetLang = currentLanguage) {
  if (!item || targetLang === "fr") return item; // Pas besoin de traduire si déjà en français
  
  const translated = { ...item };
  
  // Traduire le titre
  if (item.title) {
    translated.title = await translateContent(item.title, "auto", targetLang);
  }
  if (item.name) {
    translated.name = await translateContent(item.name, "auto", targetLang);
  }
  
  // Traduire la description
  if (item.description) {
    translated.description = await translateContent(item.description, "auto", targetLang);
  }
  
  // Traduire les catégories (si ce sont des strings)
  if (item.categories && Array.isArray(item.categories)) {
    translated.categories = await Promise.all(
      item.categories.map(cat => translateContent(cat, "auto", targetLang))
    );
  }
  
  // Traduire le nom de l'organisateur/artiste/entreprise
  if (item.organizer) {
    translated.organizer = await translateContent(item.organizer, "auto", targetLang);
  }
  if (item.artist) {
    translated.artist = await translateContent(item.artist, "auto", targetLang);
  }
  if (item.company) {
    translated.company = await translateContent(item.company, "auto", targetLang);
  }
  
  // Mettre en cache les traductions
  const cacheKey = `item_${item.id}_${targetLang}`;
  localStorage.setItem(cacheKey, JSON.stringify(translated));
  
  return translated;
}

// Version synchrone qui utilise le cache (pour affichage immédiat)
function getTranslatedItemSync(item, targetLang = currentLanguage) {
  if (!item || targetLang === "fr") return item;
  
  // Vérifier le cache
  const cacheKey = `item_${item.id}_${targetLang}`;
  const cached = localStorage.getItem(cacheKey);
  if (cached) {
    try {
      return JSON.parse(cached);
    } catch (e) {
      console.warn("Erreur parsing cache traduction", e);
    }
  }
  
  // Si pas en cache, retourner l'original et lancer la traduction en arrière-plan
  translateItemContentAuto(item, targetLang).then(translated => {
    // Mettre à jour les popups si elles sont ouvertes
    refreshMarkers();
  });
  
  return item; // Retourner l'original en attendant
}

// Fonction pour traduire le contenu d'un événement (titre, description)
// Utilise le système intelligent multi-provider avec fallback automatique
async function translateContent(text, sourceLang = "auto", targetLang = currentLanguage, region = null) {
  if (!text || targetLang === sourceLang) return text;
  
  // Vérifier le cache
  const cacheKey = `${text}|${sourceLang}|${targetLang}`;
  if (TRANSLATION_API_CONFIG.cacheEnabled && contentTranslationCache[cacheKey]) {
    return contentTranslationCache[cacheKey];
  }
  
  // Sélectionner le meilleur provider intelligemment
  const provider = getBestProviderForTranslation(sourceLang, targetLang, region);
  
  if (!provider) {
    console.warn("⚠️ Aucun provider de traduction disponible. Retour du texte original.");
    return text;
  }
  
  try {
    let translated = text;
    let lastError = null;
    
    // Essayer le provider principal
    try {
      switch (provider) {
        case "google":
          translated = await translateWithGoogle(text, sourceLang, targetLang);
          break;
        case "deepl":
          translated = await translateWithDeepL(text, sourceLang, targetLang);
          break;
        case "azure":
          translated = await translateWithAzure(text, sourceLang, targetLang);
          break;
        case "libretranslate":
          translated = await translateWithLibreTranslate(text, sourceLang, targetLang);
          break;
        default:
          throw new Error("Provider inconnu");
      }
    } catch (error) {
      lastError = error;
      console.warn(`⚠️ Erreur avec ${provider}, tentative fallback...`, error);
      
      // Fallback automatique : essayer les autres providers
      const fallbackProviders = ["google", "azure", "libretranslate"].filter(p => p !== provider);
      
      for (const fallbackProvider of fallbackProviders) {
        const fallback = TRANSLATION_PROVIDERS[fallbackProvider];
        if (!fallback || !fallback.apiKey) continue;
        
        try {
          switch (fallbackProvider) {
            case "google":
              translated = await translateWithGoogle(text, sourceLang, targetLang);
              break;
            case "azure":
              translated = await translateWithAzure(text, sourceLang, targetLang);
              break;
            case "libretranslate":
              translated = await translateWithLibreTranslate(text, sourceLang, targetLang);
              break;
          }
          
          console.log(`✅ Traduction réussie avec fallback ${fallbackProvider}`);
          break; // Succès avec le fallback
        } catch (fallbackError) {
          console.warn(`❌ Fallback ${fallbackProvider} échoué`, fallbackError);
          continue; // Essayer le suivant
        }
      }
      
      // Si tous les fallbacks ont échoué
      if (translated === text && lastError) {
        throw lastError;
      }
    }
    
    // Mettre en cache
    if (TRANSLATION_API_CONFIG.cacheEnabled && translated !== text) {
      // Limiter la taille du cache
      const keys = Object.keys(contentTranslationCache);
      if (keys.length >= TRANSLATION_API_CONFIG.cacheMaxSize) {
        delete contentTranslationCache[keys[0]]; // Supprimer la plus ancienne
      }
      contentTranslationCache[cacheKey] = translated;
    }
    
    return translated;
  } catch (error) {
    console.error("❌ Erreur traduction finale:", error);
    return text; // Retourner le texte original en cas d'erreur
  }
}

// Fonction pour traduire avec Google Cloud Translate
async function translateWithGoogle(text, sourceLang, targetLang) {
  const apiKey = TRANSLATION_PROVIDERS.google.apiKey;
  if (!apiKey) throw new Error("Clé API Google non configurée");
  
  const response = await fetch(
    `${TRANSLATION_PROVIDERS.google.endpoint}?key=${apiKey}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        q: text,
        source: sourceLang === "auto" ? "" : sourceLang,
        target: targetLang,
        format: "text"
      })
    }
  );
  
  if (!response.ok) throw new Error("Erreur Google Translate API");
  
  const data = await response.json();
  return data.data.translations[0].translatedText;
}

// Fonction pour traduire avec DeepL
async function translateWithDeepL(text, sourceLang, targetLang) {
  const apiKey = TRANSLATION_PROVIDERS.deepl.apiKey;
  if (!apiKey) throw new Error("Clé API DeepL non configurée");
  
  const response = await fetch(
    TRANSLATION_PROVIDERS.deepl.endpoint,
    {
      method: "POST",
      headers: {
        "Authorization": `DeepL-Auth-Key ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text: [text],
        source_lang: sourceLang === "auto" ? null : sourceLang.toUpperCase(),
        target_lang: targetLang.toUpperCase()
      })
    }
  );
  
  if (!response.ok) throw new Error("Erreur DeepL API");
  
  const data = await response.json();
  return data.translations[0].text;
}

// Fonction pour traduire avec Azure Translator
async function translateWithAzure(text, sourceLang, targetLang) {
  const apiKey = TRANSLATION_PROVIDERS.azure.apiKey;
  if (!apiKey) throw new Error("Clé API Azure non configurée");
  
  const endpoint = TRANSLATION_PROVIDERS.azure.endpoint;
  const location = "global"; // ou la région de ta ressource Azure
  
  const response = await fetch(
    `${endpoint}?api-version=3.0&from=${sourceLang === "auto" ? "" : sourceLang}&to=${targetLang}`,
    {
      method: "POST",
      headers: {
        "Ocp-Apim-Subscription-Key": apiKey,
        "Ocp-Apim-Subscription-Region": location,
        "Content-Type": "application/json",
      },
      body: JSON.stringify([{ text }])
    }
  );
  
  if (!response.ok) throw new Error("Erreur Azure Translator API");
  
  const data = await response.json();
  return data[0].translations[0].text;
}

// Fonction pour traduire avec LibreTranslate (gratuit)
async function translateWithLibreTranslate(text, sourceLang, targetLang) {
  const response = await fetch(
    `https://libretranslate.com/translate`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        q: text,
        source: sourceLang === "auto" ? "auto" : sourceLang,
        target: targetLang,
        format: "text"
      })
    }
  );
  
  if (!response.ok) throw new Error("Erreur LibreTranslate API");
  
  const data = await response.json();
  return data.translatedText;
}

// ============================================
// FONCTION POUR L'IA : TRADUIRE AUTOMATIQUEMENT LES POINTS
// ============================================
//
// Cette fonction permet à l'IA de traduire automatiquement les événements
// qu'elle insère depuis le bout du monde dans toutes les langues supportées
//
async function translateItemForAI(item, targetLanguages = ["fr", "en", "es", "zh", "hi"]) {
  if (!item || !TRANSLATION_API_CONFIG.apiKey) {
    console.warn("⚠️ Impossible de traduire : clé API manquante");
    return item;
  }
  
  // Détecter la langue source du contenu
  const sourceLang = detectLanguage(item.title || item.description || "");
  
  // Créer un objet de traductions
  if (!item.translations) item.translations = {};
  
  // Traduire dans chaque langue cible
  for (const targetLang of targetLanguages) {
    if (targetLang === sourceLang) continue; // Pas besoin de traduire dans la même langue
    
    try {
      // Traduire le titre
      if (item.title) {
        const titleKey = `title_${targetLang}`;
        if (!item.translations[titleKey]) {
          item.translations[titleKey] = await translateContent(item.title, sourceLang, targetLang);
        }
      }
      
      // Traduire la description
      if (item.description) {
        const descKey = `description_${targetLang}`;
        if (!item.translations[descKey]) {
          item.translations[descKey] = await translateContent(item.description, sourceLang, targetLang);
        }
      }
      
      // Traduire les catégories (via dictionnaire si possible, sinon API)
      if (item.categories && item.categories.length > 0) {
        const catKey = `categories_${targetLang}`;
        if (!item.translations[catKey]) {
          item.translations[catKey] = await Promise.all(
            item.categories.map(cat => translateContent(cat, sourceLang, targetLang))
          );
        }
      }
      
      console.log(`✅ Traduit en ${targetLang.toUpperCase()}: ${item.title || item.name}`);
    } catch (error) {
      console.error(`❌ Erreur traduction en ${targetLang}:`, error);
    }
  }
  
  return item;
}

// Fonction simple de détection de langue (basique)
function detectLanguage(text) {
  if (!text) return "en";
  
  // Détection basique par patterns
  const patterns = {
    fr: /[àâäéèêëïîôùûüÿç]/i,
    es: /[ñáéíóúü¿¡]/i,
    zh: /[\u4e00-\u9fff]/,
    hi: /[\u0900-\u097f]/,
    ar: /[\u0600-\u06ff]/,
    ja: /[\u3040-\u309f\u30a0-\u30ff]/,
    ko: /[\uac00-\ud7a3]/
  };
  
  for (const [lang, pattern] of Object.entries(patterns)) {
    if (pattern.test(text)) return lang;
  }
  
  return "en"; // Par défaut anglais
}

// Fonction pour obtenir le contenu traduit d'un item
function getTranslatedContent(item, field, lang = currentLanguage) {
  if (!item.translations) return item[field] || "";
  
  const key = `${field}_${lang}`;
  return item.translations[key] || item[field] || "";
}

// Fonction pour traduire un commentaire (avec bouton de traduction si différent de la langue actuelle)
function translateComment(comment, commentLang = "auto") {
  if (!comment) return "";
  
  // Protection contre les erreurs TDZ - utiliser directement window.t()
  // Si le commentaire est déjà dans la langue actuelle, pas besoin de traduire
  if (commentLang === currentLanguage || commentLang === "auto") {
    return comment;
  }
  
  // Sinon, afficher le commentaire original + bouton de traduction
  return `
    <div class="comment-translation-wrapper" data-original="${escapeHtml(comment)}" data-lang="${commentLang}">
      <div class="comment-original" style="margin-bottom:4px;">${escapeHtml(comment)}</div>
      <button onclick="translateThisComment(this)" style="background:rgba(0,255,195,0.1);border:1px solid rgba(0,255,195,0.3);color:#00ffc3;padding:2px 8px;border-radius:4px;font-size:10px;cursor:pointer;">
        🌍 ${window.t("translate")}
      </button>
      <div class="comment-translated" style="display:none;margin-top:4px;padding:4px;background:rgba(0,255,195,0.05);border-left:2px solid #00ffc3;font-size:11px;"></div>
    </div>
  `;
}

// Fonction pour traduire un commentaire spécifique
async function translateThisComment(button) {
  // Protection contre les erreurs TDZ - utiliser directement window.t()
  
  const wrapper = button.closest(".comment-translation-wrapper");
  if (!wrapper) return;
  
  const original = wrapper.dataset.original;
  const sourceLang = wrapper.dataset.lang || "auto";
  const translatedDiv = wrapper.querySelector(".comment-translated");
  
  if (translatedDiv.style.display === "block") {
    translatedDiv.style.display = "none";
    button.textContent = `🌍 ${window.t("translate")}`;
    return;
  }
  
  button.textContent = `${window.t("loading")}...`;
  
  try {
    const translated = await translateContent(original, sourceLang, currentLanguage);
    translatedDiv.innerHTML = escapeHtml(translated);
    translatedDiv.style.display = "block";
    button.textContent = `🌍 ${window.t("hide_translation")}`;
  } catch (error) {
    console.error("Erreur traduction:", error);
    button.textContent = `🌍 ${window.t("translate")}`;
    showNotification(window.t("translation_error"), "error");
  }
}

// Fonction pour changer de langue
function setLanguage(lang) {
  if (!["fr", "en", "es", "zh", "hi"].includes(lang)) return;
  
  currentLanguage = lang;
  localStorage.setItem("mapEventLanguage", lang);
  
  // Mettre à jour l'UI
  const flagMap = { fr: "🇫🇷", en: "🇬🇧", es: "🇪🇸", zh: "🇨🇳", hi: "🇮🇳" };
  const codeMap = { fr: "FR", en: "EN", es: "ES", zh: "ZH", hi: "HI" };
  
  const flagEl = document.getElementById("current-lang-flag");
  const codeEl = document.getElementById("current-lang-code");
  
  if (flagEl) flagEl.textContent = flagMap[lang];
  if (codeEl) codeEl.textContent = codeMap[lang];
  
  // Mettre à jour les checkmarks
  ["fr", "en", "es", "zh", "hi"].forEach(l => {
    const check = document.getElementById(`lang-check-${l}`);
    if (check) check.style.display = l === lang ? "block" : "none";
  });
  
  // Fermer le menu
  const menu = document.getElementById("language-menu");
  if (menu) menu.style.display = "none";
  
  // Re-traduire l'interface (à implémenter complètement plus tard)
  updateUITranslations();
  
  showNotification(`🌍 Langue changée : ${flagMap[lang]} ${codeMap[lang]}`, "success");
}

// Fonction pour mettre à jour les traductions de l'UI (TOUT LE SITE)
function updateUITranslations() {
  // CRITIQUE: S'assurer que window.translations est complètement initialisé AVANT d'utiliser t()
  if (typeof window === 'undefined' || !window.translations || typeof window.translations !== 'object') {
    window.translations = { fr: {}, en: {}, es: {}, zh: {}, hi: {} };
  }
  // S'assurer que toutes les langues existent
  ['fr', 'en', 'es', 'zh', 'hi'].forEach(lang => {
    if (!window.translations[lang] || typeof window.translations[lang] !== 'object') {
      window.translations[lang] = window.translations[lang] || {};
    }
  });
  // NE JAMAIS redéfinir window.t ici - utiliser la version globale sécurisée
  // window.t est déjà défini au début du fichier et ne doit jamais être redéfini
  
  // 1. Topbar - Boutons principaux
  const filterBtn = document.querySelector('button[onclick="toggleLeftPanel()"]');
  if (filterBtn) filterBtn.textContent = `🔍 ${window.t("filter")}`;
  
  const listBtn = document.querySelector('button[onclick="toggleListView()"]');
  if (listBtn) listBtn.textContent = `📋 ${window.t("list")}`;
  
  // 2. Boutons de navigation
  const agendaBtn = document.querySelector('button[onclick="openAgendaModal()"]');
  if (agendaBtn) agendaBtn.textContent = `📅 ${window.t("agenda")}`;
  
  const alertsBtn = document.querySelector('button[onclick="openSubscriptionModal()"]');
  const alertsLabel = document.getElementById("subscription-label");
  if (alertsLabel) {
    alertsLabel.textContent = "ABOS";
    alertsLabel.innerHTML = "ABOS"; // Double vérification avec innerHTML
  }
  
  const accountBtn = document.querySelector('button[onclick="openAccountModal()"]');
  if (accountBtn) accountBtn.textContent = `👤 ${window.t("account")}`;
  
  const cartBtn = document.getElementById("cart-btn");
  if (cartBtn) {
    const count = cartBtn.querySelector("#cart-count");
    cartBtn.innerHTML = `🛒 ${window.t("cart")}`;
    if (count) cartBtn.appendChild(count);
  }
  
  // 3. Champ de recherche de ville (IMPORTANT!)
  const searchInput = document.getElementById("map-search-input");
  if (searchInput) {
    searchInput.placeholder = window.t("search_city");
  }
  
  // 4. Bouton Publier
  const publishBtn = document.getElementById("map-publish-btn");
  if (publishBtn) publishBtn.textContent = window.t("publish");
  
  // 5. FILTRES - Traduire les labels de dates dans l'explorer
  setTimeout(() => {
    const explorerPanel = document.getElementById("left-panel");
    if (explorerPanel) {
      // Traduire "Filtrer par date"
      const dateFilterText = Array.from(explorerPanel.querySelectorAll('div')).find(d => 
        d.textContent.includes("Filtrer par date") || d.textContent.includes("Filter by date")
      );
      if (dateFilterText) {
        dateFilterText.textContent = `📅 ${window.t("filter_by_date")} (${window.t("cumulative") || "cumulable"})`;
      }
      
      // Traduire "Ou sélectionner une période"
      const periodText = Array.from(explorerPanel.querySelectorAll('div')).find(d => 
        d.textContent.includes("Ou sélectionner") || d.textContent.includes("Or select")
      );
      if (periodText) {
        periodText.textContent = `📆 ${window.t("select_period")}`;
      }
    }
  }, 100);
  
  // 6. Rafraîchir les marqueurs pour mettre à jour les popups
  // CRITIQUE: Ne pas appeler refreshMarkers() immédiatement car cela peut créer une boucle infinie
  // Attendre que tout soit initialisé avant de rafraîchir
  // DÉSACTIVÉ temporairement pour éviter les boucles infinies
  // setTimeout(() => {
  //   try {
  //     refreshMarkers();
  //     refreshListView();
  //   } catch (e) {
  //     // Ne pas logger pour éviter les milliers de messages
  //   }
  // }, 500);
  
  // 8. Rafraîchir les modals si ouvertes
  if (document.getElementById("publish-modal-backdrop")?.style.display === "flex") {
    const modalInner = document.getElementById("publish-modal-inner");
    if (modalInner) {
      const content = modalInner.innerHTML;
      if (content.includes("Mon Agenda") || content.includes("My agenda") || content.includes("Mi agenda")) {
        openAgendaModal();
      } else if (content.includes("Abonnements") || content.includes("Subscriptions")) {
        openSubscriptionModal();
      } else if (content.includes("Mon compte") || content.includes("My account")) {
        openAccountModal();
      }
    }
  }
  
  console.log(`✅ Traduction complète terminée en ${currentLanguage.toUpperCase()}`);
}

// Fonction pour ouvrir/fermer le menu de langue
function toggleLanguageMenu() {
  const menu = document.getElementById("language-menu");
  if (!menu) return;
  
  const isOpen = menu.style.display === "block";
  menu.style.display = isOpen ? "none" : "block";
  
  // Fermer si on clique ailleurs
  if (!isOpen) {
    setTimeout(() => {
      document.addEventListener("click", function closeMenu(e) {
        if (!menu.contains(e.target) && !e.target.closest("#language-selector")) {
          menu.style.display = "none";
          document.removeEventListener("click", closeMenu);
        }
      });
    }, 100);
  }
}

// Charger la langue sauvegardée au démarrage
function initLanguage() {
  // CRITIQUE: S'assurer que window.translations est complètement initialisé AVANT updateUITranslations()
  if (typeof window === 'undefined' || !window.translations || typeof window.translations !== 'object') {
    window.translations = { fr: {}, en: {}, es: {}, zh: {}, hi: {} };
  }
  // S'assurer que toutes les langues existent
  ['fr', 'en', 'es', 'zh', 'hi'].forEach(lang => {
    if (!window.translations[lang] || typeof window.translations[lang] !== 'object') {
      window.translations[lang] = window.translations[lang] || {};
    }
  });
  
  // FORCER LE FRANÇAIS PAR DÉFAUT
  currentLanguage = "fr";
  localStorage.setItem("mapEventLanguage", "fr");
  updateUITranslations();
  console.log("🇫🇷 Langue définie en français par défaut");
}

// Exports
window.toggleLanguageMenu = toggleLanguageMenu;
window.setLanguage = setLanguage;
window.translateThisComment = translateThisComment;
window.openItemFromAgenda = openItemFromAgenda;
window.selectSuggestion = selectSuggestion;
window.highlightSuggestion = highlightSuggestion;

// Mettre à jour le badge abonnement dans la topbar
function updateSubscriptionBadge() {
  const badge = document.getElementById("subscription-badge");
  const label = document.getElementById("subscription-label");
  if (!badge || !label) return;
  
  const sub = currentUser.subscription || "free";
  
  // TOUJOURS afficher "ABOS" peu importe l'abonnement - FORCER IMMÉDIATEMENT
  label.textContent = "ABOS";
  label.innerHTML = "ABOS"; // Double vérification avec innerHTML
  
  // Plans Full Premium
  if (sub === "full-premium" || sub === "full") {
    badge.style.background = "linear-gradient(135deg,rgba(255,215,0,0.3),rgba(255,215,0,0.1))";
    badge.style.borderColor = "rgba(255,215,0,0.6)";
    label.style.color = "#ffd700";
  }
  // Plans Service Ultra
  else if (sub === "service-ultra" || sub === "booking-ultra") {
    badge.style.background = "linear-gradient(135deg,rgba(167,139,250,0.3),rgba(139,92,246,0.2))";
    badge.style.borderColor = "rgba(167,139,250,0.6)";
    label.style.color = "#a78bfa";
  }
  // Plans Service Pro
  else if (sub === "service-pro" || sub === "booking-pro" || sub === "pro") {
    badge.style.background = "linear-gradient(135deg,rgba(139,92,246,0.3),rgba(59,130,246,0.2))";
    badge.style.borderColor = "rgba(139,92,246,0.6)";
    label.style.color = "#a78bfa";
  }
  // Plans Events Alertes Pro
  else if (sub === "events-alerts-pro" || sub === "events-alerts") {
    badge.style.background = "linear-gradient(135deg,rgba(59,130,246,0.3),rgba(37,99,235,0.2))";
    badge.style.borderColor = "rgba(59,130,246,0.6)";
    label.style.color = "#3b82f6";
  }
  // Plans Events Explorer
  else if (sub === "events-explorer" || sub === "explorer") {
    badge.style.background = "linear-gradient(135deg,rgba(34,197,94,0.3),rgba(16,185,129,0.2))";
    badge.style.borderColor = "rgba(34,197,94,0.6)";
    label.style.color = "#22c55e";
  }
  // Ancien premium (compatibilité)
  else if (sub === "premium") {
    badge.style.background = "linear-gradient(135deg,rgba(255,215,0,0.3),rgba(255,215,0,0.1))";
    badge.style.borderColor = "rgba(255,215,0,0.6)";
    label.style.color = "#ffd700";
  }
  // Gratuit
  else {
    badge.style.background = "linear-gradient(135deg,rgba(139,92,246,0.2),rgba(59,130,246,0.1))";
    badge.style.borderColor = "rgba(139,92,246,0.4)";
    label.style.color = "#a78bfa";
  }
}

// ============================================
// MISSION ÉCOLOGIQUE - SAUVER LA TERRE 🌍
// ============================================
function openEcoMissionModal() {
  const html = `
    <div style="padding:16px;text-align:center;">
      <div style="font-size:60px;margin-bottom:16px;">🌍</div>
      <h2 style="margin:0 0 12px;font-size:22px;background:linear-gradient(90deg,#22c55e,#10b981);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;">
        Notre Mission : Sauver la Planète
      </h2>
      
      <p style="font-size:14px;color:var(--ui-text-main);line-height:1.6;margin-bottom:20px;">
        <strong>Map Event</strong> n'est pas qu'une plateforme d'événements.<br>
        C'est un projet engagé pour l'environnement.
      </p>
      
      <div style="background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.3);border-radius:12px;padding:16px;margin-bottom:20px;text-align:left;">
        <div style="font-size:14px;font-weight:600;color:#22c55e;margin-bottom:12px;">💚 Où vont vos contributions ?</div>
        <ul style="margin:0;padding-left:20px;font-size:13px;color:var(--ui-text-main);line-height:1.8;">
          <li><strong>🌳 Achat de terrains forestiers</strong> – Protection des écosystèmes</li>
          <li><strong>🏭 Filtres CO2 pour entreprises</strong> – Offerts aux plus gros pollueurs</li>
          <li><strong>🌊 Nettoyage des océans</strong> – Partenariats avec Ocean Cleanup</li>
          <li><strong>☀️ Énergie renouvelable</strong> – Financement de projets solaires</li>
          <li><strong>🐝 Protection de la biodiversité</strong> – Ruches urbaines & réserves</li>
          <li><strong>🎓 Éducation environnementale</strong> – Sensibilisation des jeunes</li>
        </ul>
      </div>
      
      <div style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:12px;padding:16px;margin-bottom:20px;">
        <div style="font-size:14px;font-weight:600;color:#3b82f6;margin-bottom:8px;">📊 Répartition de nos revenus</div>
        <div style="display:flex;justify-content:center;gap:20px;font-size:12px;color:var(--ui-text-main);">
          <div><strong style="color:#22c55e;font-size:24px;">70%</strong><br>Mission Planète</div>
          <div><strong style="color:#f59e0b;font-size:24px;">20%</strong><br>Développement</div>
          <div><strong style="color:#8b5cf6;font-size:24px;">10%</strong><br>Équipe</div>
        </div>
      </div>
      
      <div style="font-size:13px;color:var(--ui-text-muted);margin-bottom:16px;">
        Chaque paiement sur Map Event contribue directement à ces actions.<br>
        <strong>Ensemble, on peut faire la différence.</strong> 🌱
      </div>
      
      <div style="display:flex;gap:8px;margin-bottom:12px;">
        <button onclick="makeDonation(5)" style="flex:1;padding:12px;border-radius:12px;border:none;cursor:pointer;font-weight:600;background:rgba(34,197,94,0.2);color:#22c55e;font-size:14px;">
          🌱 5 CHF
        </button>
        <button onclick="makeDonation(10)" style="flex:1;padding:12px;border-radius:12px;border:none;cursor:pointer;font-weight:600;background:rgba(34,197,94,0.3);color:#22c55e;font-size:14px;">
          🌳 10 CHF
        </button>
        <button onclick="makeDonation(25)" style="flex:1;padding:12px;border-radius:12px;border:none;cursor:pointer;font-weight:600;background:rgba(34,197,94,0.4);color:#22c55e;font-size:14px;">
          🌲 25 CHF
        </button>
      </div>
      
      <button onclick="makeDonation(0)" style="width:100%;padding:14px;border-radius:999px;border:none;cursor:pointer;font-weight:700;font-size:15px;background:linear-gradient(135deg,#22c55e,#10b981);color:white;box-shadow:0 8px 24px rgba(34,197,94,0.4);">
        💚 Faire un don personnalisé
      </button>
      
      <button onclick="closePublishModal()" style="width:100%;margin-top:12px;padding:10px;border-radius:999px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-muted);cursor:pointer;font-size:12px;">
        Fermer
      </button>
    </div>
  `;
  
  document.getElementById("publish-modal-inner").innerHTML = html;
  document.getElementById("publish-modal-backdrop").style.display = "flex";
}

function makeDonation(amount) {
  if (amount === 0) {
    const customAmount = prompt("Montant de votre don (CHF) :");
    if (customAmount && !isNaN(customAmount) && parseFloat(customAmount) > 0) {
      amount = parseFloat(customAmount);
    } else {
      return;
    }
  }
  
  showNotification(`🌍 Merci pour votre don de ${amount} CHF ! La Terre vous remercie 💚`, "success");
  closePublishModal();
  
  // Afficher un message de remerciement après
  setTimeout(() => {
    showNotification("🌳 Votre contribution sera utilisée pour protéger notre planète.", "info");
  }, 2000);
}

// ============================================
// SYSTÈME D'ALERTES ET D'ALARMES - LEADER MONDIAL
// ============================================

// Configuration API
const API_BASE_URL = "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api";

// --- CONFIGURATION STRIPE ---
// Note: La clé publique sera récupérée depuis le backend lors de la création de la session
let stripe = null;
let stripePublicKey = null;

// Initialiser Stripe (sera fait après récupération de la clé publique)
function initStripe(publicKey) {
  if (!publicKey) {
    console.warn('⚠️ Clé publique Stripe manquante');
    return;
  }
  
  // Attendre que Stripe.js soit chargé
  if (typeof Stripe === 'undefined') {
    console.warn('⚠️ Stripe.js non chargé, attente...');
    // Réessayer après un court délai
    setTimeout(() => {
      if (typeof Stripe !== 'undefined') {
        stripe = Stripe(publicKey);
        stripePublicKey = publicKey;
        console.log('✅ Stripe initialisé (retardé)');
      } else {
        console.error('❌ Stripe.js toujours non disponible');
      }
    }, 500);
    return;
  }
  
  try {
    stripe = Stripe(publicKey);
    stripePublicKey = publicKey;
    console.log('✅ Stripe initialisé avec succès');
  } catch (error) {
    console.error('❌ Erreur initialisation Stripe:', error);
  }
}

// Vérifier que Stripe.js est chargé au démarrage
document.addEventListener("DOMContentLoaded", () => {
  // Vérifier après un court délai pour laisser le temps au script de charger
  setTimeout(() => {
    if (typeof Stripe !== 'undefined') {
      console.log('✅ Stripe.js chargé et prêt');
    } else {
      console.warn('⚠️ Stripe.js non détecté - vérifiez que le script est chargé dans le HTML');
    }
  }, 1000);
});

// État des alertes
let alertsViewOpen = false;
let alertsScrollPosition = 0;
let selectedAlertId = null;
let alarmsViewOpen = false;

// Variables pour les alarmes
let currentUserAlarms = []; // [{alertId, eventId, favoriteId, favoriteName, favoriteMode, timeBefore: {value, unit}, createdAt}]
let alarmsForAgenda = []; // Même structure pour l'agenda

// ============================================
// DÉTECTION AUTOMATIQUE DES FAVORIS DANS LES ÉVÉNEMENTS
// ============================================

// Vérifier si des favoris apparaissent dans de nouveaux événements
async function checkFavoritesInNewEvents(newEvents) {
  if (!currentUser.isLoggedIn || !currentUser.favorites || currentUser.favorites.length === 0) {
    return;
  }

  const maxAlerts = getAlertLimit();
  if (maxAlerts === 0) return; // Pas d'alertes pour les utilisateurs gratuits

  const newAlerts = [];

  // Pour chaque nouvel événement
  newEvents.forEach(event => {
    if (!event || !event.title) return;

    const eventTitle = (event.title || '').toLowerCase();
    const eventDescription = (event.description || '').toLowerCase();
    const eventLocation = (event.location || event.city || '').toLowerCase();

    // Pour chaque favori de l'utilisateur
    currentUser.favorites.forEach(favorite => {
      if (!favorite || !favorite.name) return;

      const favoriteName = favorite.name.toLowerCase();
      
      // Vérifier si le nom du favori apparaît dans le titre, description ou location
      const foundInTitle = eventTitle.includes(favoriteName);
      const foundInDescription = eventDescription.includes(favoriteName);
      const foundInLocation = eventLocation.includes(favoriteName);

      if (foundInTitle || foundInDescription || foundInLocation) {
        // Vérifier si l'alerte existe déjà
        const alertExists = currentUser.alerts.some(a => 
          a.eventId === event.id.toString() && 
          a.favoriteId === favorite.id &&
          a.status !== 'deleted'
        );

        if (!alertExists) {
          // ✅ NOUVEAU : Vérifier la distance entre l'utilisateur et l'événement
          // L'alerte n'est créée que si l'événement est à moins de 75 km d'au moins une adresse de l'utilisateur
          if (!event.lat || !event.lng) {
            // Si l'événement n'a pas de coordonnées, on ne peut pas calculer la distance
            // On ne crée pas l'alerte
            return;
          }

          // Vérifier si l'utilisateur a au moins une adresse définie
          if (!currentUser.addresses || currentUser.addresses.length === 0) {
            // Si l'utilisateur n'a pas d'adresse, on ne crée pas l'alerte
            console.log('⚠️ Aucune adresse utilisateur définie - alerte non créée');
            return;
          }

          // Vérifier la distance pour chaque adresse de l'utilisateur
          let distanceToUser = null;
          let closestAddress = null;
          
          for (const address of currentUser.addresses) {
            if (address.lat && address.lng) {
              const distance = calculateDistance(
                address.lat, address.lng,
                event.lat, event.lng
              );
              
              // Si l'événement est à moins de 75 km de cette adresse
              if (distance <= 75) {
                if (!distanceToUser || distance < distanceToUser) {
                  distanceToUser = distance;
                  closestAddress = address;
                }
              }
            }
          }

          // ✅ Condition : L'alerte n'est créée que si l'événement est à moins de 75 km d'au moins une adresse
          if (distanceToUser === null || distanceToUser > 75) {
            console.log(`⚠️ Événement trop loin (${distanceToUser ? distanceToUser + ' km' : 'distance inconnue'} > 75 km) - alerte non créée`);
            return;
          }

          // Calculer la distance entre le favori et l'événement (pour affichage)
          let distanceToFavorite = null;
          if (favorite.lat && favorite.lng) {
            distanceToFavorite = calculateDistance(
              event.lat, event.lng,
              favorite.lat, favorite.lng
            );
          }

          // Vérifier la limite d'alertes pour déterminer si elle doit être floutée
          const alertLimit = getAlertLimit();
          const activeAlerts = currentUser.alerts.filter(a => a.status !== 'deleted' && !a.isBlurred);
          const isBlurred = alertLimit !== Infinity && activeAlerts.length >= alertLimit;

          const alert = {
            id: `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            eventId: event.id.toString(),
            favoriteId: favorite.id,
            favoriteName: favorite.name,
            favoriteMode: favorite.mode || favorite.type || 'event',
            distance: distanceToFavorite, // Distance entre favori et événement
            distanceToUser: distanceToUser, // Distance entre utilisateur et événement
            closestAddress: closestAddress ? (closestAddress.address || closestAddress.city) : null,
            status: 'new',
            isBlurred: isBlurred, // ✅ Alerte floutée si limite atteinte
            creationDate: new Date().toISOString(),
            eventTitle: event.title,
            eventDate: event.startDate || event.date
          };

          newAlerts.push(alert);
          
          // Si l'alerte est floutée, supprimer les alarmes correspondantes (elles n'existent pas encore, mais on prépare)
          // Les alarmes seront supprimées automatiquement quand elles seront créées pour une alerte floutée
        }
      }
    });
  });

  // Ajouter les nouvelles alertes
  if (newAlerts.length > 0) {
    // Sauvegarder dans le backend
    for (const alert of newAlerts) {
      try {
        const response = await fetch(`${API_BASE_URL}/user/alerts`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            userId: currentUser.id.toString(),
            alert: alert
          })
        });

        if (response.ok) {
          currentUser.alerts.push(alert);
        }
      } catch (error) {
        console.error('Erreur création alerte:', error);
      }
    }

    // Afficher la fenêtre popup au login si l'utilisateur vient de se connecter
    if (currentUser.isLoggedIn) {
      showAlertsLoginPopup(newAlerts);
    }
  }
}

// Calculer la distance entre deux points (formule de Haversine)
// Fonction calculateDistance déjà définie plus haut (ligne 2753)
// Cette fonction utilise la signature: calculateDistance(lat1, lng1, lat2, lng2)

// ============================================
// FENÊTRE POPUP D'ALERTES AU LOGIN
// ============================================

function showAlertsLoginPopup(newAlerts) {
  if (!newAlerts || newAlerts.length === 0) return;

  const html = `
    <div style="position:relative;width:100%;max-width:500px;background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:20px;border:2px solid #3b82f6;box-shadow:0 20px 60px rgba(59,130,246,0.3);overflow:hidden;">
      <div style="background:linear-gradient(135deg,#3b82f6,#2563eb);padding:20px;text-align:center;">
        <div style="font-size:32px;margin-bottom:8px;">🔔</div>
        <h2 style="margin:0;font-size:22px;font-weight:700;color:#fff;">Nouvelles Alertes</h2>
        <p style="margin:8px 0 0;font-size:14px;color:rgba(255,255,255,0.9);">Vos favoris apparaissent dans de nouveaux événements !</p>
      </div>
      
      <div style="padding:20px;max-height:400px;overflow-y:auto;">
        ${newAlerts.map(alert => `
          <div style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:12px;padding:16px;margin-bottom:12px;">
            <div style="display:flex;align-items:start;gap:12px;">
              <div style="width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#2563eb);display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0;">
                ${getFavoriteEmoji(alert.favoriteMode)}
              </div>
              <div style="flex:1;">
                <div style="font-weight:700;font-size:16px;margin-bottom:4px;color:#fff;">
                  ${escapeHtml(alert.favoriteName)}
                </div>
                <div style="font-size:13px;color:rgba(255,255,255,0.7);margin-bottom:6px;">
                  apparaît dans l'événement
                </div>
                <div style="font-weight:600;font-size:14px;color:#00ffc3;margin-bottom:4px;">
                  ${escapeHtml(alert.eventTitle)}
                </div>
                ${alert.distanceToUser ? `<div style="font-size:12px;color:rgba(255,255,255,0.6);">📍 À ${alert.distanceToUser} km de chez vous</div>` : alert.distance ? `<div style="font-size:12px;color:rgba(255,255,255,0.6);">📍 À ${alert.distance} km</div>` : ''}
              </div>
            </div>
          </div>
        `).join('')}
        
        <div style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:12px;padding:16px;margin-top:16px;text-align:center;">
          <div style="font-size:14px;color:rgba(255,255,255,0.8);">
            💡 Toutes vos alertes sont disponibles dans le bloc <strong style="color:#3b82f6;">Alertes</strong>
          </div>
        </div>
      </div>
      
      <div style="padding:20px;border-top:1px solid rgba(255,255,255,0.1);display:flex;gap:12px;">
        <button onclick="closeAlertsLoginPopup()" style="flex:1;padding:14px;border-radius:12px;border:none;background:rgba(255,255,255,0.1);color:#fff;font-weight:600;cursor:pointer;transition:all 0.2s;">
          Fermer
        </button>
        <button onclick="closeAlertsLoginPopupAndOpenAlerts()" style="flex:1;padding:14px;border-radius:12px;border:none;background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff;font-weight:600;cursor:pointer;transition:all 0.2s;">
          OK, j'ai compris
        </button>
      </div>
    </div>
  `;

  // Créer ou réutiliser le backdrop
  let backdrop = document.getElementById("alerts-login-popup-backdrop");
  if (!backdrop) {
    backdrop = document.createElement("div");
    backdrop.id = "alerts-login-popup-backdrop";
    backdrop.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,0.95);display:flex;align-items:center;justify-content:center;z-index:2000;backdrop-filter:blur(10px);";
    backdrop.onclick = (e) => {
      if (e.target === backdrop) closeAlertsLoginPopup();
    };
    document.body.appendChild(backdrop);
  }
  
  backdrop.innerHTML = html;
  backdrop.style.display = "flex";
}

function closeAlertsLoginPopup() {
  const backdrop = document.getElementById("alerts-login-popup-backdrop");
  if (backdrop) {
    backdrop.style.display = "none";
  }
}

function closeAlertsLoginPopupAndOpenAlerts() {
  closeAlertsLoginPopup();
  setTimeout(() => {
    openAlertsView();
  }, 300);
}

// Afficher les notifications de changement de statut pour les événements où l'utilisateur a participé
function showStatusChangeNotifications() {
  if (!currentUser.isLoggedIn || !currentUser.pendingStatusNotifications || currentUser.pendingStatusNotifications.length === 0) {
    return;
  }
  
  // Filtrer les notifications qui concernent des événements toujours dans participating
  const validNotifications = currentUser.pendingStatusNotifications.filter(notif => {
    const key = `event:${notif.eventId}`;
    return currentUser.participating.includes(key);
  });
  
  if (validNotifications.length === 0) {
    // Nettoyer les notifications obsolètes
    currentUser.pendingStatusNotifications = [];
    saveUser();
    return;
  }
  
  // Afficher la première notification
  const notification = validNotifications[0];
  const event = eventsData.find(e => e.id === notification.eventId);
  if (!event) {
    // Supprimer la notification si l'événement n'existe plus
    currentUser.pendingStatusNotifications = currentUser.pendingStatusNotifications.filter(n => n.eventId !== notification.eventId);
    saveUser();
    return;
  }
  
  // Créer la fenêtre de notification
  let backdrop = document.getElementById("status-change-notification-backdrop");
  if (!backdrop) {
    backdrop = document.createElement("div");
    backdrop.id = "status-change-notification-backdrop";
    backdrop.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,0.75);display:flex;align-items:center;justify-content:center;z-index:99999;backdrop-filter:blur(2px);";
    document.body.appendChild(backdrop);
  }
  
  const statusEmoji = notification.status === 'REPORTÉ' || notification.status === 'REPORTE' ? '📅' :
                     notification.status === 'ANNULE' || notification.status === 'ANNULÉ' ? '❌' :
                     notification.status === 'COMPLET' || notification.status === 'SOLDOUT' ? '🔒' : '⚠️';
  
  const statusColor = notification.status === 'REPORTÉ' || notification.status === 'REPORTE' ? '#3b82f6' :
                      notification.status === 'ANNULE' || notification.status === 'ANNULÉ' ? '#ef4444' :
                      notification.status === 'COMPLET' || notification.status === 'SOLDOUT' ? '#f59e0b' : '#ef4444';
  
  backdrop.innerHTML = `
    <div style="position:relative;width:100%;max-width:500px;background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:20px;border:2px solid ${statusColor};box-shadow:0 20px 60px rgba(0,0,0,0.5);overflow:hidden;">
      <button onclick="closeStatusChangeNotification(${notification.eventId})" style="position:absolute;top:12px;right:12px;width:36px;height:36px;border-radius:50%;border:none;background:rgba(255,255,255,0.1);color:#fff;cursor:pointer;font-size:20px;z-index:1001;display:flex;align-items:center;justify-content:center;transition:all 0.2s;" onmouseover="this.style.background='rgba(239,68,68,0.8)'" onmouseout="this.style.background='rgba(255,255,255,0.1)'">✕</button>
      
      <div style="background:linear-gradient(135deg,${statusColor},${statusColor}dd);padding:20px;text-align:center;">
        <div style="font-size:48px;margin-bottom:8px;">${statusEmoji}</div>
        <h2 style="margin:0;font-size:22px;font-weight:700;color:#fff;">Changement d'événement</h2>
        <p style="margin:8px 0 0;font-size:14px;color:rgba(255,255,255,0.9);">L'événement auquel vous participez a changé</p>
      </div>
      
      <div style="padding:24px;">
        <div style="background:rgba(255,255,255,0.05);border-radius:12px;padding:16px;margin-bottom:20px;">
          <div style="font-size:18px;font-weight:700;color:#fff;margin-bottom:8px;">${escapeHtml(event.title)}</div>
          <div style="font-size:14px;color:var(--ui-text-muted);margin-bottom:12px;">${escapeHtml(event.address || '')}</div>
          <div style="padding:8px 12px;background:rgba(239,68,68,0.2);border-radius:8px;display:inline-block;">
            <span style="font-size:13px;font-weight:600;color:#ef4444;">⚠️ Événement ${notification.statusText}</span>
          </div>
        </div>
        
        <div style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:12px;padding:16px;margin-bottom:20px;">
          <div style="font-size:13px;font-weight:600;color:#3b82f6;margin-bottom:8px;">💡 Que souhaitez-vous faire ?</div>
          <div style="font-size:12px;color:var(--ui-text-muted);line-height:1.6;">
            Vous pouvez ajouter cette annonce dans le bloc <strong style="color:#3b82f6;">ABOS</strong> pour recevoir des alertes sur les changements futurs.
          </div>
        </div>
        
        <div style="display:flex;gap:10px;">
          <button onclick="closeStatusChangeNotification(${notification.eventId})" style="flex:1;padding:12px;border-radius:12px;border:1px solid var(--ui-card-border);background:transparent;color:var(--ui-text-main);font-weight:600;cursor:pointer;transition:all 0.2s;">
            Fermer
          </button>
          <button onclick="addEventToAlertsFromNotification(${notification.eventId})" style="flex:1;padding:12px;border-radius:12px;border:none;background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff;font-weight:600;cursor:pointer;transition:all 0.2s;">
            Ajouter aux alertes
          </button>
        </div>
      </div>
    </div>
  `;
  
  backdrop.style.display = "flex";
}

function closeStatusChangeNotification(eventId) {
  // Supprimer la notification de la liste
  currentUser.pendingStatusNotifications = currentUser.pendingStatusNotifications.filter(n => n.eventId !== eventId);
  saveUser();
  
  // Fermer la fenêtre
  const backdrop = document.getElementById("status-change-notification-backdrop");
  if (backdrop) {
    backdrop.style.display = "none";
  }
  
  // Afficher la notification suivante s'il y en a
  setTimeout(() => {
    showStatusChangeNotifications();
  }, 300);
}

// Ajouter une alerte pour un événement depuis l'agenda
function addEventAlert(eventId) {
  const event = eventsData.find(e => e.id === eventId);
  if (!event) {
    showNotification("⚠️ Événement introuvable", "warning");
    return;
  }
  
  if (!currentUser.isLoggedIn) {
    showNotification("⚠️ Vous devez être connecté pour ajouter des alertes", "warning");
    openLoginModal();
    return;
  }
  
  // Vérifier la limite d'alertes
  const maxAlerts = getAlertLimit();
  if (maxAlerts === 0) {
    showNotification("⚠️ Les alertes nécessitent un abonnement Events Explorer ou supérieur", "warning");
    openSubscriptionModal();
    return;
  }
  
  if (currentUser.alerts && currentUser.alerts.length >= maxAlerts) {
    showNotification(`⚠️ Limite atteinte (${maxAlerts} alertes) ! Passez à Events Alertes Pro pour des alertes illimitées.`, "warning");
    openSubscriptionModal();
    return;
  }
  
  // Vérifier si l'alerte existe déjà
  const existingAlert = currentUser.alerts?.find(a => a.eventId === eventId && a.status !== 'deleted');
  if (existingAlert) {
    showNotification("ℹ️ Cet événement est déjà dans vos alertes", "info");
    return;
  }
  
  // Créer l'alerte
  if (!currentUser.alerts) currentUser.alerts = [];
  currentUser.alerts.push({
    id: Date.now(),
    eventId: eventId,
    type: 'event',
    category: event.category,
    city: event.city,
    createdAt: new Date().toISOString(),
    status: 'active'
  });
  
  saveUser();
  showNotification(`✅ Alerte ajoutée pour "${event.title}"`, "success");
  
  // Rafraîchir la vue agenda si elle est ouverte
  if (agendaMiniWindowOpen) {
    showAgendaMiniWindow();
  }
}

function addEventToAlertsFromNotification(eventId) {
  const event = eventsData.find(e => e.id === eventId);
  if (!event) return;
  
  // Utiliser la fonction addEventAlert
  addEventAlert(eventId);
  closeStatusChangeNotification(eventId);
  setTimeout(() => {
    openSubscriptionModal();
    showNotification("💡 Vous pouvez créer une alerte dans le bloc ABOS pour cet événement", "info");
  }, 300);
}

function getFavoriteEmoji(mode) {
  const emojis = {
    'event': '🎉',
    'booking': '🎤',
    'service': '⚙️',
    'avatar': '👤'
  };
  return emojis[mode] || '⭐';
}

// ============================================
// ============================================
// SYSTÈME D'ALERTES DE PROXIMITÉ (rayon 70km)
// ============================================

let proximityAlertsViewOpen = false;

// Vérifier les alertes de proximité basées sur les likes et les adresses
function checkProximityAlerts() {
  if (!currentUser.isLoggedIn || !currentUser.addresses || currentUser.addresses.length === 0) {
    currentUser.proximityAlerts = [];
    updateProximityAlertsBadge();
    return;
  }
  
  const alerts = [];
  const likedItems = currentUser.likes || [];
  
  // Parcourir tous les items likés
  likedItems.forEach(likeKey => {
    const [type, idStr] = likeKey.split(':');
    const id = parseInt(idStr);
    
    let item = null;
    if (type === 'event') {
      item = eventsData.find(e => e.id === id);
    } else if (type === 'booking') {
      item = bookingsData.find(b => b.id === id);
    } else if (type === 'service') {
      item = servicesData.find(s => s.id === id);
    }
    
    if (!item) return;
    
    // CAS 1: Item liké directement (event, booking, service)
    if (item.lat && item.lng) {
      currentUser.addresses.forEach((address, addrIndex) => {
        if (!address.lat || !address.lng) return;
        
        const distance = calculateDistance(address.lat, address.lng, item.lat, item.lng);
        
        if (distance <= 70) {
          const existingAlert = alerts.find(a => 
            a.itemId === id && a.itemType === type && a.addressIndex === addrIndex && a.alertType === 'direct'
          );
          
          if (!existingAlert) {
            const typeEmoji = type === 'event' ? '🎉' : type === 'booking' ? '🎤' : '🔧';
            const typeName = type === 'event' ? 'Événement' : type === 'booking' ? 'Booking' : 'Service';
            
            alerts.push({
              id: `proximity-${type}-${id}-${addrIndex}-direct-${Date.now()}`,
              itemId: id,
              itemType: type,
              itemTitle: item.title || item.name || 'Sans titre',
              itemCity: item.city || '',
              itemLat: item.lat,
              itemLng: item.lng,
              addressIndex: addrIndex,
              address: address.address || address.city || 'Adresse inconnue',
              distance: Math.round(distance * 10) / 10,
              emoji: typeEmoji,
              typeName: typeName,
              alertType: 'direct', // Item liké directement
              timestamp: new Date().toISOString()
            });
          }
        }
      });
    }
    
    // CAS 2: Booking (artiste) liké apparaît dans un événement
    if (type === 'booking' && item.lat && item.lng) {
      eventsData.forEach(event => {
        if (!event.lat || !event.lng) return;
        
        // Vérifier si l'événement référence ce booking (par ID, nom, ou organisateur)
        const eventReferencesBooking = 
          event.bookingIds?.includes(id) ||
          event.bookings?.some(b => b.id === id || b.name === item.name) ||
          event.organizerId === id ||
          (event.organizer && event.organizer.toLowerCase().includes((item.name || '').toLowerCase()));
        
        if (eventReferencesBooking) {
          currentUser.addresses.forEach((address, addrIndex) => {
            if (!address.lat || !address.lng) return;
            
            const distance = calculateDistance(address.lat, address.lng, event.lat, event.lng);
            
            if (distance <= 70) {
              const existingAlert = alerts.find(a => 
                a.eventId === event.id && a.likedItemId === id && a.likedItemType === 'booking' && a.addressIndex === addrIndex && a.alertType === 'artist_in_event'
              );
              
              if (!existingAlert) {
                alerts.push({
                  id: `proximity-event-${event.id}-booking-${id}-${addrIndex}-${Date.now()}`,
                  eventId: event.id,
                  eventTitle: event.title || 'Sans titre',
                  eventCity: event.city || '',
                  eventLat: event.lat,
                  eventLng: event.lng,
                  likedItemId: id,
                  likedItemType: 'booking',
                  likedItemTitle: item.name || 'Artiste',
                  addressIndex: addrIndex,
                  address: address.address || address.city || 'Adresse inconnue',
                  distance: Math.round(distance * 10) / 10,
                  emoji: '🎤',
                  typeName: 'Artiste dans événement',
                  alertType: 'artist_in_event',
                  message: `${item.name || 'Artiste'} se produit dans "${event.title || 'Événement'}"`,
                  timestamp: new Date().toISOString()
                });
              }
            }
          });
        }
      });
    }
    
    // CAS 3: Service liké apparaît dans un événement
    if (type === 'service' && item.lat && item.lng) {
      eventsData.forEach(event => {
        if (!event.lat || !event.lng) return;
        
        const eventReferencesService = 
          event.serviceIds?.includes(id) ||
          event.services?.some(s => s.id === id || s.name === item.name) ||
          (event.description && event.description.toLowerCase().includes((item.name || '').toLowerCase()));
        
        if (eventReferencesService) {
          currentUser.addresses.forEach((address, addrIndex) => {
            if (!address.lat || !address.lng) return;
            
            const distance = calculateDistance(address.lat, address.lng, event.lat, event.lng);
            
            if (distance <= 70) {
              const existingAlert = alerts.find(a => 
                a.eventId === event.id && a.likedItemId === id && a.likedItemType === 'service' && a.addressIndex === addrIndex && a.alertType === 'service_in_event'
              );
              
              if (!existingAlert) {
                alerts.push({
                  id: `proximity-event-${event.id}-service-${id}-${addrIndex}-${Date.now()}`,
                  eventId: event.id,
                  eventTitle: event.title || 'Sans titre',
                  eventCity: event.city || '',
                  eventLat: event.lat,
                  eventLng: event.lng,
                  likedItemId: id,
                  likedItemType: 'service',
                  likedItemTitle: item.name || 'Service',
                  addressIndex: addrIndex,
                  address: address.address || address.city || 'Adresse inconnue',
                  distance: Math.round(distance * 10) / 10,
                  emoji: '🔧',
                  typeName: 'Service dans événement',
                  alertType: 'service_in_event',
                  message: `${item.name || 'Service'} est utilisé dans "${event.title || 'Événement'}"`,
                  timestamp: new Date().toISOString()
                });
              }
            }
          });
        }
      });
    }
  });
  
  // Trier par distance (plus proche en premier)
  alerts.sort((a, b) => a.distance - b.distance);
  
  currentUser.proximityAlerts = alerts;
  updateProximityAlertsBadge();
  saveUser();
}

// Mettre à jour le badge de notifications
function updateProximityAlertsBadge() {
  const alertsCount = currentUser.proximityAlerts?.length || 0;
  const badge = document.getElementById("alerts-count");
  if (badge) {
    if (alertsCount > 0) {
      badge.textContent = alertsCount > 99 ? '99+' : alertsCount;
      badge.style.display = 'flex';
    } else {
      badge.style.display = 'none';
    }
  }
}

// Fonction pour ouvrir les alertes sociales (alertes de proximité)
function openSocialAlertsModal() {
  if (!currentUser.isLoggedIn) {
    showNotification("⚠️ Vous devez être connecté pour voir vos alertes", "warning");
    openLoginModal();
    return;
  }
  // Ouvrir la vue des alertes de proximité (qui inclut les alertes sociales)
  openProximityAlertsView();
}
window.openSocialAlertsModal = openSocialAlertsModal;

// Ouvrir la vue des alertes de proximité
function openProximityAlertsView() {
  proximityAlertsViewOpen = true;
  refreshProximityAlertsView();
  
  // Si pas d'alertes, expliquer comment ça marche
  if (!currentUser.isLoggedIn) {
    showNotification("⚠️ Vous devez être connecté pour recevoir des alertes", "warning");
    openLoginModal();
    proximityAlertsViewOpen = false;
    return;
  }
}

// Fermer la vue des alertes de proximité
function closeProximityAlertsView() {
  proximityAlertsViewOpen = false;
  const alertsView = document.getElementById("proximity-alerts-view");
  if (alertsView) {
    alertsView.style.display = "none";
  }
}

// Rafraîchir la vue des alertes de proximité
function refreshProximityAlertsView() {
  let alertsView = document.getElementById("proximity-alerts-view");
  if (!alertsView) {
    alertsView = document.createElement("div");
    alertsView.id = "proximity-alerts-view";
    alertsView.style.cssText = "position:fixed;inset:0;z-index:1500;display:none;background:rgba(0,0,0,0.8);backdrop-filter:blur(4px);";
    document.body.appendChild(alertsView);
  }
  
  if (!proximityAlertsViewOpen) {
    alertsView.style.display = "none";
    return;
  }
  
  const alerts = currentUser.proximityAlerts || [];
  
  alertsView.innerHTML = `
    <div style="position:relative;width:100%;max-width:800px;height:100%;background:var(--ui-card-bg);border-radius:16px;overflow:hidden;display:flex;flex-direction:column;margin:20px auto;">
      <!-- Header -->
      <div style="padding:20px;border-bottom:1px solid var(--ui-card-border);background:linear-gradient(135deg,#0f172a,#1e293b);">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
          <div>
            <h2 style="margin:0;font-size:24px;font-weight:700;color:#fff;">🔔 Alertes de proximité</h2>
            <p style="margin:4px 0 0;font-size:13px;color:rgba(255,255,255,0.7);">${alerts.length} alerte${alerts.length > 1 ? 's' : ''} dans un rayon de 70 km</p>
          </div>
          <button onclick="closeProximityAlertsView()" style="width:40px;height:40px;border-radius:50%;border:none;background:rgba(255,255,255,0.1);color:#fff;cursor:pointer;font-size:20px;display:flex;align-items:center;justify-content:center;">✕</button>
        </div>
        
        <div style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:10px;padding:12px;">
          <div style="font-size:12px;color:#3b82f6;line-height:1.6;">
            💡 Vous recevez des alertes quand un <strong>booking, service, organisateur ou événement</strong> que vous avez <strong>liké</strong> se trouve à moins de <strong>70 km</strong> de l'une de vos adresses.
          </div>
        </div>
      </div>
      
      <!-- Liste des alertes -->
      <div style="flex:1;overflow-y:auto;padding:20px;">
        ${alerts.length === 0 ? `
          <div style="text-align:center;padding:40px 20px;color:var(--ui-text-muted);">
            <div style="font-size:64px;margin-bottom:16px;">🔔</div>
            <h3 style="font-size:18px;font-weight:700;color:#fff;margin-bottom:12px;">Comment fonctionnent les alertes ?</h3>
            <div style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:12px;padding:16px;margin:20px 0;text-align:left;">
              <p style="font-size:14px;color:#fff;margin:0 0 12px 0;line-height:1.6;">
                <strong style="color:#3b82f6;">1. Ajoutez des favoris</strong><br>
                Likez des événements, bookings, services ou organisateurs qui vous intéressent.
              </p>
              <p style="font-size:14px;color:#fff;margin:0 0 12px 0;line-height:1.6;">
                <strong style="color:#3b82f6;">2. Configurez vos adresses</strong><br>
                Ajoutez jusqu'à 2 adresses dans votre profil pour définir votre zone de proximité.
              </p>
              <p style="font-size:14px;color:#fff;margin:0;line-height:1.6;">
                <strong style="color:#3b82f6;">3. Recevez des alertes</strong><br>
                Quand un favori se trouve à moins de 70 km d'une de vos adresses, vous recevez une alerte ici !
              </p>
            </div>
            <p style="font-size:13px;margin:16px 0 0;color:var(--ui-text-muted);">Les alertes apparaîtront ici quand vos favoris seront à proximité</p>
          </div>
        ` : `
          <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px;">
            ${alerts.map(alert => `
              <div onclick="openItemFromProximityAlert('${alert.itemType}', ${alert.itemId})" style="background:rgba(15,23,42,0.5);border:1px solid var(--ui-card-border);border-radius:12px;padding:16px;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.borderColor='#3b82f6';this.style.transform='translateY(-2px)'" onmouseout="this.style.borderColor='var(--ui-card-border)';this.style.transform='translateY(0)'">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                  <span style="font-size:24px;">${alert.emoji}</span>
                  <div style="flex:1;">
                    <div style="font-size:14px;font-weight:600;color:#fff;margin-bottom:4px;">${escapeHtml(alert.itemTitle)}</div>
                    <div style="font-size:12px;color:var(--ui-text-muted);">${alert.typeName}</div>
                  </div>
                </div>
                <div style="background:rgba(59,130,246,0.1);border-radius:8px;padding:8px;margin-bottom:8px;">
                  <div style="font-size:12px;color:#3b82f6;font-weight:600;">📍 À ${alert.distance} km</div>
                  <div style="font-size:11px;color:var(--ui-text-muted);margin-top:4px;">de ${escapeHtml(alert.address)}</div>
                </div>
                <div style="font-size:11px;color:var(--ui-text-muted);">
                  📍 ${escapeHtml(alert.itemCity)}
                </div>
                <button onclick="event.stopPropagation();removeProximityAlert('${alert.id}')" style="margin-top:12px;width:100%;padding:8px;border-radius:8px;border:1px solid rgba(239,68,68,0.5);background:rgba(239,68,68,0.1);color:#ef4444;cursor:pointer;font-size:12px;font-weight:600;">
                  ✕ Marquer comme lue
                </button>
              </div>
            `).join('')}
          </div>
        `}
      </div>
    </div>
  `;
  
  alertsView.style.display = "flex";
}

// Ouvrir un item depuis une alerte de proximité
function openItemFromProximityAlert(type, id) {
  closeProximityAlertsView();
  setTimeout(() => {
    openPopupFromList(type, id);
  }, 300);
}

// Supprimer une alerte de proximité
function removeProximityAlert(alertId) {
  currentUser.proximityAlerts = currentUser.proximityAlerts.filter(a => a.id !== alertId);
  saveUser();
  updateProximityAlertsBadge();
  refreshProximityAlertsView();
}

// BLOC ALERTES - INTERFACE SIMILAIRE À EVENT LIST
// ============================================

function openAlertsView() {
  alertsViewOpen = true;
  refreshAlertsView();
}

function closeAlertsView() {
  alertsViewOpen = false;
  const alertsView = document.getElementById("alerts-view");
  if (alertsView) {
    alertsView.style.display = "none";
  }
}

function refreshAlertsView() {
  const alertsView = document.getElementById("alerts-view");
  if (!alertsView) {
    // Créer le bloc Alertes s'il n'existe pas
    createAlertsViewElement();
    return;
  }

  if (!alertsViewOpen) {
    alertsView.style.display = "none";
    return;
  }

  // Filtrer les alertes actives (non supprimées)
  const activeAlerts = currentUser.alerts.filter(a => a.status !== 'deleted');
  const visibleAlerts = activeAlerts.filter(a => !a.isBlurred);
  const blurredAlerts = activeAlerts.filter(a => a.isBlurred);
  const alertLimit = getAlertLimit();
  
  // Trier par date de création (plus récentes en premier)
  activeAlerts.sort((a, b) => new Date(b.creationDate) - new Date(a.creationDate));
  
  // Afficher un message si limite atteinte
  const limitMessage = alertLimit !== Infinity && visibleAlerts.length >= alertLimit
    ? `<div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:12px;padding:12px;margin-bottom:16px;text-align:center;">
         <div style="font-weight:700;font-size:14px;color:#ef4444;margin-bottom:4px;">⚠️ Limite atteinte (${visibleAlerts.length}/${alertLimit})</div>
         <div style="font-size:12px;color:rgba(255,255,255,0.7);">Les nouvelles alertes seront floutées. Effacez une alerte pour en afficher une nouvelle.</div>
       </div>`
    : '';

  alertsView.style.display = "block";
  alertsView.innerHTML = `
    <div style="position:relative;width:100%;height:100%;background:var(--ui-card-bg);border-radius:16px;overflow:hidden;display:flex;flex-direction:column;">
      <!-- Header -->
      <div style="padding:20px;border-bottom:1px solid var(--ui-card-border);background:linear-gradient(135deg,#0f172a,#1e293b);">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
          <div>
            <h2 style="margin:0;font-size:24px;font-weight:700;color:#fff;">🔔 Mes Alertes</h2>
            <p style="margin:4px 0 0;font-size:13px;color:rgba(255,255,255,0.7);">${visibleAlerts.length} visible${visibleAlerts.length > 1 ? 's' : ''}${blurredAlerts.length > 0 ? ` • ${blurredAlerts.length} floutée${blurredAlerts.length > 1 ? 's' : ''}` : ''}</p>
          </div>
          <button onclick="closeAlertsView()" style="width:40px;height:40px;border-radius:50%;border:none;background:rgba(255,255,255,0.1);color:#fff;cursor:pointer;font-size:20px;display:flex;align-items:center;justify-content:center;">✕</button>
        </div>
        
        <!-- Bouton Ajouter Alarme -->
        <button onclick="openAddAlarmModal('alerts')" style="width:100%;padding:12px;border-radius:12px;border:2px solid #3b82f6;background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff;font-weight:600;cursor:pointer;font-size:14px;transition:all 0.2s;display:flex;align-items:center;justify-content:center;gap:8px;margin-bottom:12px;">
          <span>⏰</span>
          <span>Ajouter alarme</span>
        </button>
        
        ${limitMessage}
      </div>
      
      <!-- Info alertes gratuites -->
      <div style="margin:12px 20px 0;padding:12px 16px;background:linear-gradient(135deg,rgba(0,255,195,0.1),rgba(34,197,94,0.1));border:1px solid rgba(0,255,195,0.3);border-radius:10px;">
        <div style="display:flex;align-items:center;gap:10px;">
          <span style="font-size:20px;">🆓</span>
          <div>
            <div style="font-size:13px;font-weight:600;color:#00ffc3;">Alertes de statut : GRATUITES & ILLIMITÉES</div>
            <div style="font-size:11px;color:var(--ui-text-muted);">Annulation, complet, reporté... Vous serez toujours informé gratuitement pour vos événements en agenda.</div>
          </div>
        </div>
      </div>
      
      <!-- Liste des alertes -->
      <div id="alerts-list-container" style="flex:1;overflow-y:auto;padding:20px;">
        ${activeAlerts.length === 0 ? `
          <div style="text-align:center;padding:40px 20px;color:var(--ui-text-muted);">
            <div style="font-size:64px;margin-bottom:16px;">🔔</div>
            <p style="font-size:16px;margin:0;">Les alertes arriveront ici</p>
            <p style="font-size:13px;margin:8px 0 0;color:var(--ui-text-muted);">selon vos likes et votre agenda</p>
            <p style="font-size:12px;margin:16px 0 0;padding:10px;background:rgba(0,255,195,0.1);border-radius:8px;color:#00ffc3;">
              💚 Si un event de votre agenda est annulé, complet ou reporté,<br>vous recevrez une alerte <strong>gratuite et illimitée</strong> !
            </p>
          </div>
        ` : `
          <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px;">
            ${activeAlerts.map((alert, index) => buildAlertCard(alert, index)).join('')}
          </div>
        `}
      </div>
    </div>
  `;

  // Restaurer la position de scroll
  const container = document.getElementById("alerts-list-container");
  if (container && alertsScrollPosition > 0) {
    container.scrollTop = alertsScrollPosition;
  }

  // Restaurer la sélection
  if (selectedAlertId) {
    const selectedCard = alertsView.querySelector(`[data-alert-id="${selectedAlertId}"]`);
    if (selectedCard) {
      selectedCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }
}

function createAlertsViewElement() {
  let alertsView = document.getElementById("alerts-view");
  if (!alertsView) {
    alertsView = document.createElement("div");
    alertsView.id = "alerts-view";
    alertsView.style.cssText = "position:fixed;inset:0;z-index:1500;display:none;";
    document.body.appendChild(alertsView);
  }
  refreshAlertsView();
}

function buildAlertCard(alert, index) {
  const event = eventsData.find(e => e.id.toString() === alert.eventId);
  const isNew = alert.status === 'new';
  const isBlurred = alert.isBlurred || false;
  const hasAlarm = currentUserAlarms.some(a => a.alertId === alert.id && !isBlurred);
  const alertLimit = getAlertLimit();
  const activeAlerts = currentUser.alerts.filter(a => a.status !== 'deleted' && !a.isBlurred);
  const canDelete = isBlurred || (alertLimit !== Infinity && activeAlerts.length > alertLimit);
  
  return `
    <div data-alert-id="${alert.id}" class="alert-card" style="
      border:2px solid ${isBlurred ? '#ef4444' : isNew ? '#3b82f6' : 'var(--ui-card-border)'};
      border-radius:16px;
      background:${isBlurred ? 'rgba(239,68,68,0.1)' : isNew ? 'rgba(59,130,246,0.1)' : 'var(--ui-card-bg)'};
      overflow:hidden;
      cursor:${isBlurred ? 'default' : 'pointer'};
      transition:all 0.2s ease;
      box-shadow:0 4px 20px rgba(0,0,0,0.2);
      position:relative;
      filter:${isBlurred ? 'blur(3px)' : 'none'};
      opacity:${isBlurred ? '0.6' : '1'};
    " ${!isBlurred ? `onclick="openEventFromAlert('${alert.eventId}', '${alert.id}')"` : ''}>
      ${isNew && !isBlurred ? '<div style="position:absolute;top:8px;right:8px;width:12px;height:12px;border-radius:50%;background:#3b82f6;box-shadow:0 0 8px rgba(59,130,246,0.8);"></div>' : ''}
      ${isBlurred ? '<div style="position:absolute;top:8px;right:8px;width:32px;height:32px;border-radius:50%;background:rgba(239,68,68,0.9);display:flex;align-items:center;justify-content:center;font-size:16px;color:#fff;box-shadow:0 2px 8px rgba(239,68,68,0.4);">🔒</div>' : ''}
      ${hasAlarm && !isBlurred ? '<div style="position:absolute;top:8px;left:8px;width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#f59e0b,#d97706);display:flex;align-items:center;justify-content:center;font-size:16px;box-shadow:0 2px 8px rgba(245,158,11,0.4);">⏰</div>' : ''}
      
      <div style="padding:16px;position:relative;">
        ${isBlurred ? `
          <div style="position:absolute;inset:0;background:rgba(0,0,0,0.3);border-radius:12px;display:flex;align-items:center;justify-content:center;z-index:10;">
            <div style="text-align:center;padding:20px;">
              <div style="font-size:32px;margin-bottom:8px;">🔒</div>
              <div style="font-weight:700;font-size:14px;color:#fff;margin-bottom:4px;">Alerte floutée</div>
              <div style="font-size:12px;color:rgba(255,255,255,0.8);">Limite atteinte (${activeAlerts.length}/${alertLimit})</div>
              <div style="font-size:11px;color:rgba(255,255,255,0.6);margin-top:8px;">Effacez une alerte pour afficher celle-ci</div>
            </div>
          </div>
        ` : ''}
        
        <div style="display:flex;align-items:start;gap:12px;margin-bottom:12px;">
          <div style="width:48px;height:48px;border-radius:12px;background:linear-gradient(135deg,#3b82f6,#2563eb);display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0;">
            ${getFavoriteEmoji(alert.favoriteMode)}
          </div>
          <div style="flex:1;">
            <div style="font-weight:700;font-size:15px;margin-bottom:4px;color:#fff;">
              ${escapeHtml(alert.favoriteName)}
            </div>
            <div style="font-size:12px;color:rgba(255,255,255,0.6);">
              ${alert.favoriteMode === 'event' ? 'Événement' : alert.favoriteMode === 'booking' ? 'Booking' : alert.favoriteMode === 'service' ? 'Service' : 'Avatar'}
            </div>
          </div>
          ${canDelete ? `
            <button onclick="event.stopPropagation();deleteAlertWithWarning('${alert.id}')" style="width:32px;height:32px;border-radius:50%;border:none;background:rgba(239,68,68,0.2);color:#ef4444;cursor:pointer;font-size:16px;display:flex;align-items:center;justify-content:center;flex-shrink:0;" title="Supprimer l'alerte">
              🗑️
            </button>
          ` : ''}
        </div>
        
        <div style="background:rgba(0,255,195,0.1);border:1px solid rgba(0,255,195,0.3);border-radius:8px;padding:12px;margin-bottom:12px;">
          <div style="font-size:11px;color:rgba(0,255,195,0.8);margin-bottom:4px;text-transform:uppercase;font-weight:600;">Apparaît dans</div>
          <div style="font-weight:600;font-size:14px;color:#00ffc3;margin-bottom:4px;">
            ${escapeHtml(alert.eventTitle || 'Événement')}
          </div>
          ${alert.eventDate ? `<div style="font-size:12px;color:rgba(0,255,195,0.7);">📅 ${formatEventDateRange(alert.eventDate, alert.eventDate)}</div>` : ''}
        </div>
        
        <div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;color:var(--ui-text-muted);">
          ${alert.distanceToUser ? `<span>📍 ${alert.distanceToUser} km de chez vous</span>` : alert.distance ? `<span>📍 ${alert.distance} km</span>` : '<span></span>'}
          <span>${new Date(alert.creationDate).toLocaleDateString('fr-CH', {day:'2-digit', month:'2-digit'})}</span>
        </div>
      </div>
    </div>
  `;
}

function openEventFromAlert(eventId, alertId) {
  selectedAlertId = alertId;
  
  // Sauvegarder la position de scroll
  const container = document.getElementById("alerts-list-container");
  if (container) {
    alertsScrollPosition = container.scrollTop;
  }
  
  // Trouver l'événement
  const event = eventsData.find(e => e.id.toString() === eventId);
  if (!event) {
    showNotification("⚠️ Événement introuvable", "error");
    return;
  }
  
  // Marquer l'alerte comme vue
  markAlertAsSeen(alertId);
  
  // Ouvrir la popup de l'événement
  openPopupFromList('event', parseInt(eventId));
  
  // Quand on ferme la popup, revenir aux alertes
  setTimeout(() => {
    const backdrop = document.getElementById("popup-modal-backdrop");
    if (backdrop) {
      const originalClose = backdrop.onclick;
      backdrop.onclick = (e) => {
        if (e.target === backdrop) {
          closePopupModal();
          setTimeout(() => {
            refreshAlertsView();
          }, 300);
        }
      };
    }
  }, 100);
}

function markAlertAsSeen(alertId) {
  const alert = currentUser.alerts.find(a => a.id === alertId);
  if (alert && alert.status === 'new') {
    alert.status = 'seen';
    alert.seenAt = new Date().toISOString();
    
    // Sauvegarder dans le backend
    fetch(`${API_BASE_URL}/user/alerts/seen`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId: currentUser.id.toString(),
        alertId: alertId
      })
    }).catch(err => console.error('Erreur marquage alerte vue:', err));
  }
}

function deleteAlertWithWarning(alertId) {
  const alert = currentUser.alerts.find(a => a.id === alertId);
  if (!alert) return;
  
  const isBlurred = alert.isBlurred || false;
  const alertLimit = getAlertLimit();
  const activeAlerts = currentUser.alerts.filter(a => a.status !== 'deleted' && !a.isBlurred);
  
  // Avertissement si alerte floutée
  if (isBlurred) {
    const confirmMessage = `⚠️ Attention : Cette alerte est floutée.\n\n` +
      `Limite atteinte (${activeAlerts.length}/${alertLimit}).\n\n` +
      `Notez bien les informations avant d'effacer, car vous ne pourrez plus les voir !\n\n` +
      `Voulez-vous vraiment supprimer cette alerte ?`;
    
    if (!confirm(confirmMessage)) {
      return;
    }
  }
  
  // Supprimer l'alerte
  alert.status = 'deleted';
  
  // Supprimer les alarmes associées
  currentUserAlarms = currentUserAlarms.filter(a => a.alertId !== alertId);
  
  // Sauvegarder dans le backend
  fetch(`${API_BASE_URL}/user/alerts`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      userId: currentUser.id.toString(),
      alertId: alertId
    })
  }).catch(err => console.error('Erreur suppression alerte:', err));
  
  // Si l'alerte était floutée, vérifier s'il faut déflouter d'autres alertes
  if (isBlurred && alertLimit !== Infinity) {
    const remainingBlurred = currentUser.alerts.filter(a => a.status !== 'deleted' && a.isBlurred);
    if (remainingBlurred.length > 0 && activeAlerts.length < alertLimit) {
      // Déflouter la première alerte floutée
      const toUnblur = remainingBlurred[0];
      toUnblur.isBlurred = false;
      showNotification(`✅ Alerte "${toUnblur.eventTitle}" est maintenant visible !`, "success");
    }
  }
  
  refreshAlertsView();
  showNotification("✅ Alerte supprimée", "success");
}

// ============================================
// SYSTÈME D'ALARMES
// ============================================

function openAddAlarmModal(context) {
  // context = 'alerts' ou 'agenda'
  const items = context === 'alerts' 
    ? currentUser.alerts.filter(a => a.status !== 'deleted')
    : currentUser.agenda.map(key => {
        const [type, id] = key.split(':');
        const data = type === 'event' ? eventsData : type === 'booking' ? bookingsData : servicesData;
        const item = data.find(i => i.id === parseInt(id));
        if (item && type === 'event') {
          return {
            id: `agenda-${key}`,
            eventId: id,
            eventTitle: item.title,
            eventDate: item.startDate || item.date,
            type: 'agenda'
          };
        }
        return null;
      }).filter(Boolean);

  if (items.length === 0) {
    showNotification("⚠️ Aucun élément disponible pour ajouter une alarme", "warning");
    return;
  }

  const selectedItems = [];
  const maxSelections = 3;

  const html = `
    <div style="position:relative;width:100%;max-width:600px;background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:20px;border:2px solid #f59e0b;box-shadow:0 20px 60px rgba(245,158,11,0.3);overflow:hidden;">
      <div style="background:linear-gradient(135deg,#f59e0b,#d97706);padding:20px;text-align:center;">
        <div style="font-size:32px;margin-bottom:8px;">⏰</div>
        <h2 style="margin:0;font-size:22px;font-weight:700;color:#fff;">Ajouter une alarme</h2>
        <p style="margin:8px 0 0;font-size:14px;color:rgba(255,255,255,0.9);">Sélectionnez jusqu'à ${maxSelections} élément${maxSelections > 1 ? 's' : ''}</p>
      </div>
      
      <div style="padding:20px;max-height:400px;overflow-y:auto;">
        <div style="font-size:14px;font-weight:600;color:#fff;margin-bottom:12px;">Sélectionner des éléments :</div>
        <div style="display:grid;gap:8px;">
          ${items.map(item => {
            const itemId = item.id || `item-${item.eventId}`;
            const isSelected = selectedItems.includes(itemId);
            return `
              <div data-item-id="${itemId}" onclick="toggleAlarmItemSelection('${itemId}', '${context}')" style="
                padding:12px;
                border-radius:12px;
                border:2px solid ${isSelected ? '#f59e0b' : 'rgba(255,255,255,0.1)'};
                background:${isSelected ? 'rgba(245,158,11,0.2)' : 'rgba(255,255,255,0.05)'};
                cursor:pointer;
                transition:all 0.2s;
                display:flex;
                align-items:center;
                gap:12px;
              ">
                <div style="width:24px;height:24px;border-radius:50%;border:2px solid ${isSelected ? '#f59e0b' : 'rgba(255,255,255,0.3)'};background:${isSelected ? '#f59e0b' : 'transparent'};display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                  ${isSelected ? '✓' : ''}
                </div>
                <div style="flex:1;">
                  <div style="font-weight:600;font-size:14px;color:#fff;">
                    ${escapeHtml(item.eventTitle || item.favoriteName || 'Élément')}
                  </div>
                  ${item.eventDate ? `<div style="font-size:12px;color:rgba(255,255,255,0.6);">📅 ${formatEventDateRange(item.eventDate, item.eventDate)}</div>` : ''}
                </div>
              </div>
            `;
          }).join('')}
        </div>
        
        <div style="margin-top:20px;padding:16px;background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);border-radius:12px;">
          <div style="font-size:14px;font-weight:600;color:#f59e0b;margin-bottom:12px;">Configuration de l'alarme :</div>
          
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;">
            <div>
              <label style="display:block;font-size:12px;color:rgba(255,255,255,0.7);margin-bottom:6px;">Temps avant</label>
              <input type="number" id="alarm-time-value" min="1" value="1" style="width:100%;padding:10px;border-radius:8px;border:1px solid rgba(255,255,255,0.2);background:rgba(255,255,255,0.05);color:#fff;font-size:14px;">
            </div>
            <div>
              <label style="display:block;font-size:12px;color:rgba(255,255,255,0.7);margin-bottom:6px;">Unité</label>
              <select id="alarm-time-unit" style="width:100%;padding:10px;border-radius:8px;border:1px solid rgba(255,255,255,0.2);background:rgba(255,255,255,0.05);color:#fff;font-size:14px;">
                <option value="hours">Heures</option>
                <option value="days" selected>Jours</option>
                <option value="weeks">Semaines</option>
              </select>
            </div>
          </div>
          
          <div style="font-size:12px;color:rgba(255,255,255,0.6);">
            Exemple : 1 jour avant = l'alarme sonnera 1 jour avant l'événement
          </div>
        </div>
      </div>
      
      <div style="padding:20px;border-top:1px solid rgba(255,255,255,0.1);display:flex;gap:12px;">
        <button onclick="closeAddAlarmModal()" style="flex:1;padding:14px;border-radius:12px;border:none;background:rgba(255,255,255,0.1);color:#fff;font-weight:600;cursor:pointer;">Annuler</button>
        <button onclick="saveAlarm('${context}')" style="flex:1;padding:14px;border-radius:12px;border:none;background:linear-gradient(135deg,#f59e0b,#d97706);color:#fff;font-weight:600;cursor:pointer;">
          Enregistrer (${selectedItems.length}/${maxSelections})
        </button>
      </div>
    </div>
  `;

  // Créer ou réutiliser le backdrop
  let backdrop = document.getElementById("add-alarm-modal-backdrop");
  if (!backdrop) {
    backdrop = document.createElement("div");
    backdrop.id = "add-alarm-modal-backdrop";
    backdrop.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,0.95);display:flex;align-items:center;justify-content:center;z-index:2000;backdrop-filter:blur(10px);";
    backdrop.onclick = (e) => {
      if (e.target === backdrop) closeAddAlarmModal();
    };
    document.body.appendChild(backdrop);
  }
  
  backdrop.innerHTML = html;
  backdrop.style.display = "flex";
  
  // Stocker le contexte et les items sélectionnés
  backdrop.dataset.context = context;
  backdrop.dataset.selectedItems = JSON.stringify([]);
}

function toggleAlarmItemSelection(itemId, context) {
  const backdrop = document.getElementById("add-alarm-modal-backdrop");
  if (!backdrop) return;
  
  const selectedItems = JSON.parse(backdrop.dataset.selectedItems || '[]');
  const maxSelections = 3;
  
  const index = selectedItems.indexOf(itemId);
  if (index > -1) {
    selectedItems.splice(index, 1);
  } else {
    if (selectedItems.length >= maxSelections) {
      showNotification(`⚠️ Maximum ${maxSelections} sélections autorisées`, "warning");
      return;
    }
    selectedItems.push(itemId);
  }
  
  backdrop.dataset.selectedItems = JSON.stringify(selectedItems);
  
  // Mettre à jour l'affichage
  const item = backdrop.querySelector(`[data-item-id="${itemId}"]`);
  if (item) {
    const isSelected = selectedItems.includes(itemId);
    item.style.border = `2px solid ${isSelected ? '#f59e0b' : 'rgba(255,255,255,0.1)'}`;
    item.style.background = isSelected ? 'rgba(245,158,11,0.2)' : 'rgba(255,255,255,0.05)';
    const checkbox = item.querySelector('div:first-child');
    if (checkbox) {
      checkbox.style.border = `2px solid ${isSelected ? '#f59e0b' : 'rgba(255,255,255,0.3)'}`;
      checkbox.style.background = isSelected ? '#f59e0b' : 'transparent';
      checkbox.innerHTML = isSelected ? '✓' : '';
    }
  }
  
  // Mettre à jour le bouton
  const saveBtn = backdrop.querySelector('button:last-child');
  if (saveBtn) {
    saveBtn.innerHTML = `Enregistrer (${selectedItems.length}/${maxSelections})`;
    saveBtn.disabled = selectedItems.length === 0;
    saveBtn.style.opacity = selectedItems.length === 0 ? '0.5' : '1';
  }
}

function saveAlarm(context) {
  const backdrop = document.getElementById("add-alarm-modal-backdrop");
  if (!backdrop) return;
  
  const selectedItems = JSON.parse(backdrop.dataset.selectedItems || '[]');
  if (selectedItems.length === 0) {
    showNotification("⚠️ Veuillez sélectionner au moins un élément", "warning");
    return;
  }
  
  const timeValue = parseInt(document.getElementById("alarm-time-value").value) || 1;
  const timeUnit = document.getElementById("alarm-time-unit").value;
  
  // Créer les alarmes
  const items = context === 'alerts' 
    ? currentUser.alerts.filter(a => a.status !== 'deleted')
    : currentUser.agenda.map(key => {
        const [type, id] = key.split(':');
        const data = type === 'event' ? eventsData : type === 'booking' ? bookingsData : servicesData;
        const item = data.find(i => i.id === parseInt(id));
        if (item && type === 'event') {
          return {
            id: `agenda-${key}`,
            alertId: `agenda-${key}`,
            eventId: id,
            eventTitle: item.title,
            eventDate: item.startDate || item.date,
            type: 'agenda'
          };
        }
        return null;
      }).filter(Boolean);
  
  selectedItems.forEach(itemId => {
    const item = items.find(i => (i.id || `item-${i.eventId}`) === itemId);
    if (item) {
      // ✅ Vérifier si l'alerte correspondante est floutée (pour les alertes)
      if (context === 'alerts') {
        const alert = currentUser.alerts.find(a => a.id === (item.id || item.alertId));
        if (alert && alert.isBlurred) {
          showNotification("⚠️ Impossible d'ajouter une alarme à une alerte floutée. Effacez une alerte pour la rendre visible.", "warning");
          return;
        }
      }
      
      const alarm = {
        id: `alarm-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        alertId: item.id || item.alertId || `agenda-${item.eventId}`,
        eventId: item.eventId || item.id,
        favoriteId: item.favoriteId,
        favoriteName: item.favoriteName || item.eventTitle,
        favoriteMode: item.favoriteMode || 'event',
        timeBefore: {
          value: timeValue,
          unit: timeUnit
        },
        notificationMethod: currentUser.notificationPreferences.email && currentUser.notificationPreferences.sms ? 'both' : 
                           currentUser.notificationPreferences.email ? 'email' : 
                           currentUser.notificationPreferences.sms ? 'sms' : 'email',
        createdAt: new Date().toISOString()
      };
      
      if (context === 'alerts') {
        currentUserAlarms.push(alarm);
      } else {
        alarmsForAgenda.push(alarm);
      }
    }
  });
  
  showNotification(`✅ ${selectedItems.length} alarme${selectedItems.length > 1 ? 's' : ''} ajoutée${selectedItems.length > 1 ? 's' : ''} !`, "success");
  closeAddAlarmModal();
  
  if (context === 'alerts') {
    refreshAlertsView();
  } else {
    // Rafraîchir la vue agenda si elle existe
    if (typeof refreshAgendaView === 'function') {
      refreshAgendaView();
    }
  }
}

function closeAddAlarmModal() {
  const backdrop = document.getElementById("add-alarm-modal-backdrop");
  if (backdrop) {
    backdrop.style.display = "none";
  }
}

// ============================================
// VÉRIFICATION ET DÉCLENCHEMENT DES ALARMES
// ============================================

// Stocker les alarmes déjà déclenchées pour éviter les doublons
let triggeredAlarms = new Set();

function checkAndTriggerAlarms() {
  if (!currentUser.isLoggedIn) return;
  
  const now = new Date();
  const allAlarms = [...currentUserAlarms, ...alarmsForAgenda];
  
  allAlarms.forEach(alarm => {
    // Vérifier si l'alarme a déjà été déclenchée
    if (triggeredAlarms.has(alarm.id)) return;
    
    // Trouver l'événement associé
    const event = eventsData.find(e => e.id.toString() === alarm.eventId);
    if (!event) return;
    
    // Obtenir la date de l'événement
    const eventDate = new Date(event.startDate || event.date);
    if (isNaN(eventDate.getTime())) return; // Date invalide
    
    // Calculer le temps avant l'événement
    const timeDiff = eventDate.getTime() - now.getTime();
    const timeDiffMs = timeDiff;
    
    // Convertir le timeBefore en millisecondes
    let timeBeforeMs = 0;
    const { value, unit } = alarm.timeBefore || { value: 1, unit: 'days' };
    
    switch(unit) {
      case 'hours':
        timeBeforeMs = value * 60 * 60 * 1000;
        break;
      case 'days':
        timeBeforeMs = value * 24 * 60 * 60 * 1000;
        break;
      case 'weeks':
        timeBeforeMs = value * 7 * 24 * 60 * 60 * 1000;
        break;
      default:
        timeBeforeMs = value * 24 * 60 * 60 * 1000; // Par défaut en jours
    }
    
    // Vérifier si on est dans la fenêtre de déclenchement (entre timeBefore et timeBefore - 1h)
    // Cela permet d'éviter de déclencher plusieurs fois la même alarme
    const oneHourMs = 60 * 60 * 1000;
    const isInWindow = timeDiffMs <= timeBeforeMs && timeDiffMs > (timeBeforeMs - oneHourMs);
    
    if (isInWindow) {
      triggerAlarm(alarm, event);
      triggeredAlarms.add(alarm.id);
    }
  });
}

function triggerAlarm(alarm, event) {
  const { notificationMethod } = alarm;
  
  // Préparer le message
  const eventTitle = event.title || 'Événement';
  const eventDate = new Date(event.startDate || event.date);
  const dateStr = eventDate.toLocaleDateString('fr-CH', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
  
  const favoriteName = alarm.favoriteName || 'Votre favori';
  const { value, unit } = alarm.timeBefore || { value: 1, unit: 'days' };
  const unitText = unit === 'hours' ? 'heure(s)' : unit === 'days' ? 'jour(s)' : 'semaine(s)';
  
  const message = `⏰ Alarme : ${favoriteName} apparaît dans "${eventTitle}"\n\n` +
    `📅 Date : ${dateStr}\n` +
    `📍 Lieu : ${event.location || event.city || 'Lieu à confirmer'}\n\n` +
    `Cette alarme a été configurée pour ${value} ${unitText} avant l'événement.`;
  
  // Envoyer les notifications selon les préférences
  if (notificationMethod === 'email' || notificationMethod === 'both') {
    sendEmailNotification(currentUser.email, `Alarme MapEventAI : ${eventTitle}`, message);
    currentUser.emailNotifications++;
  }
  
  if (notificationMethod === 'sms' || notificationMethod === 'both') {
    if (canSendSMS()) {
      sendSMSNotification(currentUser.phone || '', message);
      updateSmsCount();
      currentUser.smsNotifications++;
    } else {
      // Si limite SMS atteinte, envoyer par email à la place
      if (!currentUser.notificationPreferences.email) {
        showNotification(`⚠️ Limite SMS atteinte. Alarme envoyée par email.`, "warning");
      }
      sendEmailNotification(currentUser.email, `Alarme MapEventAI : ${eventTitle}`, message);
      currentUser.emailNotifications++;
    }
  }
  
  // Afficher une notification dans l'interface
  showNotification(`⏰ Alarme : ${eventTitle} dans ${value} ${unitText} !`, "info");
  
  // Notification push pour smartphone (si l'utilisateur a autorisé)
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification(`⏰ Alarme MapEvent`, {
      body: `${favoriteName} apparaît dans "${eventTitle}"\n${dateStr}\n📍 ${event.location || event.city || 'Lieu à confirmer'}`,
      icon: '/favicon.ico',
      badge: '/favicon.ico',
      tag: `alarm-${alarm.id}`,
      requireInteraction: false,
      silent: false
    });
  } else if ('Notification' in window && Notification.permission === 'default') {
    // Demander la permission pour les notifications push
    Notification.requestPermission().then(permission => {
      if (permission === 'granted') {
        new Notification(`⏰ Alarme MapEvent`, {
          body: `${favoriteName} apparaît dans "${eventTitle}"\n${dateStr}\n📍 ${event.location || event.city || 'Lieu à confirmer'}`,
          icon: '/favicon.ico',
          badge: '/favicon.ico',
          tag: `alarm-${alarm.id}`,
          requireInteraction: false,
          silent: false
        });
      }
    });
  }
  
  // Sauvegarder les préférences mises à jour
  try {
    localStorage.setItem('currentUser', JSON.stringify(currentUser));
  } catch (e) {
    console.error('Erreur sauvegarde utilisateur:', e);
  }
}

// Simuler l'envoi d'email (à remplacer par un vrai service d'email)
function sendEmailNotification(email, subject, message) {
  console.log(`📧 Email envoyé à ${email}`);
  console.log(`Sujet: ${subject}`);
  console.log(`Message: ${message}`);
  
  // TODO: Intégrer un service d'email (SendGrid, AWS SES, etc.)
  // Pour l'instant, on simule juste
}

// Simuler l'envoi de SMS (à remplacer par un vrai service SMS)
function sendSMSNotification(phone, message) {
  console.log(`📱 SMS envoyé à ${phone}`);
  console.log(`Message: ${message}`);
  
  // TODO: Intégrer un service SMS (Twilio, AWS SNS, etc.)
  // Pour l'instant, on simule juste
}

function updateSmsCount() {
  const limit = getSMSLimit();
  
  // Réinitialiser le compteur au début du mois
  const now = new Date();
  const lastReset = new Date(currentUser.smsResetDate || 0);
  const isNewMonth = now.getMonth() !== lastReset.getMonth() || now.getFullYear() !== lastReset.getFullYear();
  
  if (isNewMonth) {
    currentUser.smsNotifications = 0;
    currentUser.smsResetDate = now.toISOString();
  }
  
  // Vérifier si la limite est atteinte
  if (limit !== Infinity && currentUser.smsNotifications >= limit) {
    // Désactiver les notifications SMS si la limite est atteinte
    if (currentUser.notificationPreferences.sms) {
      currentUser.notificationPreferences.sms = false;
      showNotification(`⚠️ Limite SMS mensuelle atteinte (${limit}). Les alarmes seront envoyées par email uniquement.`, "warning");
    }
  }
  
  // Sauvegarder
  try {
    localStorage.setItem('currentUser', JSON.stringify(currentUser));
  } catch (e) {
    console.error('Erreur sauvegarde compteur SMS:', e);
  }
}

// Vérifier les alarmes périodiquement (toutes les heures)
function startAlarmChecker() {
  // Vérifier immédiatement
  checkAndTriggerAlarms();
  
  // Puis toutes les heures
  setInterval(() => {
    checkAndTriggerAlarms();
  }, 60 * 60 * 1000); // 1 heure
}

// Démarrer le vérificateur d'alarmes au chargement
if (typeof window !== 'undefined') {
  window.addEventListener('load', () => {
    setTimeout(() => {
      startAlarmChecker();
    }, 5000); // Attendre 5 secondes après le chargement
  });
}

// ============================================
// INTÉGRATION DANS LE CHARGEMENT DES ÉVÉNEMENTS
// ============================================

// Modifier la fonction de chargement des événements pour appeler checkFavoritesInNewEvents
// Cette fonction doit être appelée après chaque chargement d'événements depuis le backend

// ============================================
// CHARGEMENT DES DONNÉES DEPUIS LE BACKEND
// ============================================

// Charger les favoris depuis le backend
async function loadFavoritesFromBackend() {
  if (!currentUser.isLoggedIn) return;
  
  try {
    const response = await fetch(`${API_BASE_URL}/user/favorites?userId=${currentUser.id}`);
    if (response.ok) {
      const data = await response.json();
      if (data.success && data.favorites) {
        currentUser.favorites = data.favorites;
      }
    }
  } catch (error) {
    console.error('Erreur chargement favoris:', error);
  }
}

// Charger les alertes depuis le backend
async function loadAlertsFromBackend() {
  if (!currentUser.isLoggedIn) return;
  
  try {
    const response = await fetch(`${API_BASE_URL}/user/alerts?userId=${currentUser.id}`);
    if (response.ok) {
      const data = await response.json();
      if (data.success && data.alerts) {
        currentUser.alerts = data.alerts;
      }
    }
  } catch (error) {
    console.error('Erreur chargement alertes:', error);
  }
}

// Charger les événements depuis le backend et vérifier les favoris
async function loadEventsFromBackend() {
  try {
    // ✅ Charger les événements de France ET du backend en parallèle
    const [franceResponse, backendResponse] = await Promise.allSettled([
      fetch('/public/events_france_final.geojson'),
      fetch(`${API_BASE_URL}/events`)
    ]);
    
    let allNewEvents = [];
    
    // Traiter les événements de France
    if (franceResponse.status === 'fulfilled' && franceResponse.value.ok) {
      try {
        const geojson = await franceResponse.value.json();
        const franceEvents = geojson.features.map((feature, index) => {
          const props = feature.properties;
          const coords = feature.geometry.coordinates;
          const startDate = parseFrenchDate(props['Date Début'], props['Heure Début']);
          const endDate = parseFrenchDate(props['Date Fin'], props['Heure Fin']);
          
          return {
            id: index + 1000,
            type: 'event',
            title: props.Titre || 'Événement sans titre',
            description: `${props.Catégorie || ''} - ${props.Adresse || ''}`,
            city: props.city || 'France',
            lat: coords[1],
            lng: coords[0],
            startDate: startDate,
            endDate: endDate,
            category: props.Catégorie || 'Autre',
            link: props.Lien || '',
            email: props.Email || '',
            address: props.Adresse || '',
            boost: '1.-',
            likes: 0,
            favorites: 0,
            participations: 0
          };
        });
        allNewEvents.push(...franceEvents);
        console.log(`✅ ${franceEvents.length} événements de France chargés`);
      } catch (e) {
        console.warn('Erreur parsing France GeoJSON:', e);
      }
    }
    
    // Traiter les événements du backend
    if (backendResponse.status === 'fulfilled' && backendResponse.value.ok) {
      try {
        const backendEvents = await backendResponse.value.json();
        allNewEvents.push(...backendEvents);
        console.log(`✅ ${backendEvents.length} événements du backend chargés`);
      } catch (e) {
        console.warn('Erreur parsing backend:', e);
      }
    }
    
    // Filtrer les doublons et ajouter
    const existingIds = new Set(eventsData.map(e => e.id));
    const trulyNewEvents = allNewEvents.filter(e => !existingIds.has(e.id));
    
    if (trulyNewEvents.length > 0) {
      eventsData.push(...trulyNewEvents);
      window.eventsData = eventsData; // Mettre à jour la référence globale
      await checkFavoritesInNewEvents(trulyNewEvents);
      refreshMarkers();
      refreshListView();
      
      // Vérifier si on doit mettre à jour les métadonnées Open Graph
      const urlParams = new URLSearchParams(window.location.search);
      const eventId = urlParams.get('event');
      if (eventId) {
        const item = eventsData.find(e => e.id === parseInt(eventId));
        if (item) {
          updateOpenGraphMetadata('event', parseInt(eventId), item);
        }
      }
    }
  } catch (error) {
    console.error('Erreur chargement événements:', error);
  }
}

// Parser une date française (ex: "5 Avr. 2026" + "08:30:00")
function parseFrenchDate(dateStr, timeStr) {
  if (!dateStr) return null;
  
  const months = {
    'janv.': '01', 'févr.': '02', 'mars': '03', 'avr.': '04',
    'mai': '05', 'juin': '06', 'juil.': '07', 'août': '08',
    'sept.': '09', 'oct.': '10', 'nov.': '11', 'déc.': '12'
  };
  
  // Parser "5 Avr. 2026"
  const parts = dateStr.trim().split(' ');
  if (parts.length !== 3) return null;
  
  const day = parts[0].padStart(2, '0');
  const month = months[parts[1].toLowerCase()] || '01';
  const year = parts[2];
  
  // Parser l'heure "08:30:00"
  const time = timeStr ? timeStr.substring(0, 5) : '00:00';
  
  return `${year}-${month}-${day}T${time}:00`;
}

// Charger toutes les données utilisateur au login
async function loadUserDataOnLogin() {
  // Charger la position depuis le stockage local
  loadUserLocationFromStorage();
  
  // Charger les adresses depuis localStorage si elles existent
  try {
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
      const parsed = JSON.parse(savedUser);
      if (parsed.addresses && parsed.addresses.length > 0) {
        currentUser.addresses = parsed.addresses;
      }
    }
  } catch (e) {
    console.error('Erreur chargement adresses:', e);
  }
  
  // Si pas de position, demander la géolocalisation
  if (!currentUser.location || !currentUser.location.lat || !currentUser.location.lng) {
    // Demander la géolocalisation (non bloquant)
    requestUserLocation().catch(() => {
      // Si l'utilisateur refuse, on continue sans position
      console.log('Géolocalisation refusée ou indisponible');
    });
  }
  
  await loadFavoritesFromBackend();
  await loadAlertsFromBackend();
  await loadEventsFromBackend();
  
  // Afficher la popup d'alertes si il y en a de nouvelles
  const newAlerts = currentUser.alerts.filter(a => a.status === 'new');
  if (newAlerts.length > 0) {
    setTimeout(() => {
      showAlertsLoginPopup(newAlerts);
    }, 1000);
  }
}

// ============================================
// GÉOLOCALISATION UTILISATEUR
// ============================================

// Obtenir la position de l'utilisateur (géolocalisation)
function getUserLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Géolocalisation non supportée'));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const location = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
          city: null // Peut être rempli avec une API de géocodage inverse
        };
        
        // Sauvegarder dans currentUser
        if (currentUser) {
          currentUser.location = location;
        }
        
        // Sauvegarder dans localStorage
        try {
          localStorage.setItem('userLocation', JSON.stringify(location));
        } catch (e) {
          console.error('Erreur sauvegarde position:', e);
        }
        
        resolve(location);
      },
      (error) => {
        console.error('Erreur géolocalisation:', error);
        reject(error);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000 // Cache de 5 minutes
      }
    );
  });
}

// Définir manuellement la position de l'utilisateur (par ville ou coordonnées)
function setUserLocation(lat, lng, city = null) {
  if (currentUser) {
    currentUser.location = {
      lat: lat,
      lng: lng,
      city: city
    };
    
    // Sauvegarder dans localStorage
    try {
      localStorage.setItem('userLocation', JSON.stringify(currentUser.location));
    } catch (e) {
      console.error('Erreur sauvegarde position:', e);
    }
    
    showNotification('📍 Position mise à jour', 'success');
  }
}

// Charger la position depuis localStorage
function loadUserLocationFromStorage() {
  try {
    const saved = localStorage.getItem('userLocation');
    if (saved) {
      const location = JSON.parse(saved);
      if (currentUser) {
        currentUser.location = location;
      }
      return location;
    }
  } catch (e) {
    console.error('Erreur chargement position:', e);
  }
  return null;
}

// Demander la géolocalisation à l'utilisateur
async function requestUserLocation() {
  try {
    const location = await getUserLocation();
    showNotification('📍 Position obtenue avec succès', 'success');
    return location;
  } catch (error) {
    showNotification('⚠️ Impossible d\'obtenir votre position. Vous pouvez la définir manuellement dans les paramètres.', 'warning');
    return null;
  }
}

// ============================================
// INTÉGRATION DANS L'AGENDA
// ============================================

// Modifier openAgendaModal pour ajouter le bouton "Ajouter alarme"
// Cette fonction doit être modifiée pour inclure le système d'alarmes
