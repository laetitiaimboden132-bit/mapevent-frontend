/**
 * MODULE AUTHENTIFICATION - MapEventAI
 * VERSION: 2026-01-16-104800-FIX-NORMALIZED-PHOTODATA
 * 
 * Ce fichier contient toutes les fonctions liées à l'authentification :
 * - Gestion des tokens (getAuthToken, getRefreshToken)
 * - OAuth Google (startGoogleLogin, handleCognitoCallbackIfPresent)
 * - Modals AUTH (openAuthModal, closeAuthModal)
 * - Login/Register (performLogin, performRegister)
 * - User management (loadSavedUser, logout, updateAuthUI)
 * 
 * DEPENDANCES EXTERNES (doivent être définies dans map_logic.js) :
 * - currentUser (variable globale)
 * - showNotification() (fonction globale)
 * - updateAuthButtons() (fonction globale)
 * - updateAccountBlockLegitimately() (fonction globale)
 * - API_BASE_URL (constante)
 * - registerData (objet global pour formulaire)
 * 
 * MODULES INTERNES :
 * - profile-validator.js (validation du profil utilisateur)
 */

// ⚠️⚠️⚠️ IMPORT MODULE DE VALIDATION
// Utilisation dynamique pour compatibilité avec l'environnement actuel
let ProfileValidator = null;
if (typeof window !== 'undefined' && window.ProfileValidator) {
  ProfileValidator = window.ProfileValidator;
} else {
  // Fallback : définir les fonctions localement si le module n'est pas chargé
  // Ces fonctions seront remplacées par le module une fois chargé
  ProfileValidator = {
    validateRequiredFields: (userData, pendingData) => {
      const missingFields = [];
      const username = pendingData?.username || userData?.username;
      if (!username || username === '' || username === 'null' || username.includes('@')) {
        missingFields.push('username');
      }
      const photoData = pendingData?.photoData || userData?.photoData;
      const profilePhotoUrl = userData?.profile_photo_url;
      if ((!photoData || photoData === '' || photoData === 'null') && (!profilePhotoUrl || profilePhotoUrl === '')) {
        missingFields.push('photo');
      }
      return { isValid: missingFields.length === 0, missingFields };
    },
    canAllowConnection: (userData, pendingData) => {
      const validation = ProfileValidator.validateRequiredFields(userData, pendingData);
      return validation.isValid;
    },
    getValidUsername: (userData, pendingData, payload) => {
      const username = pendingData?.username || userData?.username;
      if (username && username !== '' && username !== 'null' && !username.includes('@')) {
        return username;
      }
      const googleName = payload?.name || payload?.given_name;
      if (googleName) {
        return googleName.split(' ')[0];
      }
      const email = payload?.email || userData?.email;
      if (email) {
        return email.split('@')[0];
      }
      return 'Utilisateur';
    }
  };
}
// ⚠️⚠️⚠️ LOG DE VERSION - DOIT APPARAÎTRE IMMÉDIATEMENT AU CHARGEMENT
console.log('🚨🚨🚨 [AUTH] VERSION 2026-01-16 00:05 - askRememberMeAndConnect DÉSACTIVÉE (CODE MODAL SUPPRIMÉ) 🚨🚨🚨');
console.log('🚨🚨🚨 [AUTH] Si vous voyez ce message, la bonne version est chargée 🚨🚨🚨');

// ===============================
// CONFIGURATION
// ===============================
// ⚠️⚠️⚠️ VERSION CORRIGÉE 2026-01-16 00:05 - askRememberMeAndConnect désactivée après inscription/connexion (CODE MODAL SUPPRIMÉ)
console.log('🔥🔥🔥 [AUTH] ✅✅✅ VERSION CORRIGÉE 2026-01-16 00:05 - askRememberMeAndConnect désactivée après inscription/connexion (CODE MODAL SUPPRIMÉ) 🔥🔥🔥');
console.log('🔥🔥🔥 [AUTH] Si vous voyez ce message, la bonne version est chargée 🔥🔥🔥');

const API_BASE_URL = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api";

const COGNITO = {
  domain: "https://eu-west-19o9j6xsdr.auth.eu-west-1.amazoncognito.com",
  clientId: "63rm6h0m26q41lotbho6704dod",
  redirectUri: "https://mapevent.world/",
  scopes: ["openid", "email", "profile"],
};

// Variables globales pour OAuth
let isGoogleLoginInProgress = false;

// ===============================
// UTILITAIRES PKCE
// ===============================
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

// ===============================
// STORAGE HELPERS
// ===============================
function authSave(key, val) {
  sessionStorage.setItem(key, val);
}

function authLoad(key) {
  return sessionStorage.getItem(key);
}

function authClearTemp() {
  ["pkce_verifier", "oauth_state"].forEach((k) => sessionStorage.removeItem(k));
}

function safeSetJSON(key, value) {
  const s = JSON.stringify(value);
  try {
    localStorage.setItem(key, s);
    return "localStorage";
  } catch (e) {
    try {
      sessionStorage.setItem(key, s);
      return "sessionStorage";
    } catch (e2) {
      window.__MEMORY_STORE__ = window.__MEMORY_STORE__ || {};
      window.__MEMORY_STORE__[key] = value;
      return "memory";
    }
  }
}

function safeGetJSON(key) {
  try {
    const v = localStorage.getItem(key);
    if (v) return JSON.parse(v);
  } catch {}
  try {
    const v = sessionStorage.getItem(key);
    if (v) return JSON.parse(v);
  } catch {}
  if (window.__MEMORY_STORE__ && window.__MEMORY_STORE__[key]) return window.__MEMORY_STORE__[key];
  return null;
}

function clearAuthStorage() {
  try { localStorage.removeItem("currentUser"); } catch {}
  try { sessionStorage.removeItem("currentUser"); } catch {}
  try { localStorage.removeItem("accessToken"); } catch {}
  try { sessionStorage.removeItem("accessToken"); } catch {}
  try { localStorage.removeItem("refreshToken"); } catch {}
  try { sessionStorage.removeItem("refreshToken"); } catch {}
  try { localStorage.removeItem("rememberMe"); } catch {}
  if (window.__MEMORY_STORE__) delete window.__MEMORY_STORE__["currentUser"];
}

// ===============================
// USER MANAGEMENT
// ===============================
// ⚠️⚠️⚠️ OPTIMISATION STOCKAGE : Helper pour supprimer photoData avant sauvegarde
function removePhotoDataForStorage(userObj) {
  if (!userObj) return null;
  const copy = { ...userObj };
  delete copy.photoData; // Supprimer photoData (base64) qui peut faire plusieurs MB
  return copy;
}

// Exposer globalement pour utilisation dans map_logic.js
window.removePhotoDataForStorage = removePhotoDataForStorage;

function saveUserSlim(userObj) {
  if (!userObj) return null;
  
  // ⚠️⚠️⚠️ OPTIMISATION STOCKAGE : Ne JAMAIS sauvegarder photoData (base64) dans localStorage
  // photoData peut faire plusieurs MB et remplir rapidement le quota localStorage (5-10 MB)
  // On sauvegarde uniquement profile_photo_url (URL S3) qui est beaucoup plus petit (~100-200 chars)
  // photoData reste disponible en mémoire dans window.currentUser mais n'est jamais persisté
  
  const slimUser = {
    id: userObj.id || null,
    email: userObj.email || '',
    username: userObj.username || '',
    firstName: userObj.firstName || userObj.first_name || '',
    lastName: userObj.lastName || userObj.last_name || '',
    profileComplete: userObj.profileComplete || false,
    profile_photo_url: userObj.profile_photo_url || userObj.profilePhoto || null,
    // photoData EXCLU - trop volumineux pour localStorage, reste uniquement en mémoire
    role: userObj.role || 'user',
    subscription: userObj.subscription || 'free',
    hasPassword: userObj.hasPassword || false,
    hasPostalAddress: userObj.hasPostalAddress || false,
    accessToken: userObj.accessToken || null,
    refreshToken: userObj.refreshToken || null
  };
  
  return slimUser;
}

function updateAuthUI(slimUser) {
  if (!slimUser || !slimUser.id) {
    console.warn('[UPDATE AUTH UI] slimUser invalide');
    return;
  }
  
  console.log('[UPDATE AUTH UI] Mise à jour UI avec slimUser:', { 
    id: slimUser.id, 
    email: slimUser.email, 
    username: slimUser.username,
    firstName: slimUser.firstName,
    lastName: slimUser.lastName
  });
  
  // Normaliser photoData dans slimUser avant de mettre à jour currentUser
  if (slimUser.photoData === 'null' || slimUser.photoData === 'undefined' || slimUser.photoData === '') {
    slimUser.photoData = null;
  }
  
  // Mettre à jour currentUser global (doit être défini dans map_logic.js)
  if (typeof window !== 'undefined' && window.currentUser !== undefined) {
    // ⚠️⚠️⚠️ CRITIQUE : Sauvegarder photoData AVANT de les écraser (mais PAS le username)
    const savedPhotoData = window.currentUser.photoData;
    
    // ⚠️⚠️⚠️ SIMPLIFICATION : Utiliser DIRECTEMENT le username de slimUser (qui contient le username du formulaire)
    // Le username de slimUser a déjà la priorité au formulaire, donc on l'utilise tel quel
    window.currentUser = {
      ...window.currentUser,
      ...slimUser,
      username: slimUser.username, // ⚠️⚠️⚠️ FORCER le username de slimUser (qui vient du formulaire)
      isLoggedIn: true
    };
    
    console.log('[UPDATE AUTH UI] ✅✅✅ Username de slimUser utilisé:', window.currentUser.username);
    
    // ⚠️⚠️⚠️ CRITIQUE : PRIORITÉ au photoData du formulaire (savedPhotoData) si valide
    if (savedPhotoData && savedPhotoData !== 'null' && savedPhotoData !== 'undefined' && savedPhotoData.length > 100) {
      window.currentUser.photoData = savedPhotoData;
      console.log('[UPDATE AUTH UI] ✅✅✅ PhotoData du formulaire préservé');
    }
    
    // S'assurer que photoData est null et non "null" dans currentUser
    if (window.currentUser.photoData === 'null' || window.currentUser.photoData === 'undefined' || window.currentUser.photoData === '') {
      window.currentUser.photoData = null;
    }
  }
  
  // Mettre à jour les boutons auth
  if (typeof updateAuthButtons === 'function') {
    updateAuthButtons();
  }
  
  // ⚠️⚠️⚠️ CRITIQUE : S'assurer que window.currentUser.username contient le bon username avant la mise à jour
  if (window.currentUser && slimUser.username && 
      slimUser.username !== 'null' && 
      !slimUser.username.includes('@')) {
    window.currentUser.username = slimUser.username; // ⚠️ FORCER le username avant mise à jour
    console.log('[UPDATE AUTH UI] ✅✅✅ Username FORCÉ avant updateAccountBlockLegitimately:', window.currentUser.username);
  }
  
  // Mettre à jour le bloc compte - FORCER la mise à jour immédiate
  if (typeof window.updateAccountBlockLegitimately === 'function') {
    window.updateAccountBlockLegitimately();
    // Forcer aussi après un court délai pour s'assurer que le DOM est prêt
    setTimeout(() => {
      if (typeof window.updateAccountBlockLegitimately === 'function') {
        window.updateAccountBlockLegitimately();
      }
    }, 100);
  }
  
  console.log('[UPDATE AUTH UI] UI mise à jour - bouton "Connexion" → "Compte"');
}

function getUserDisplayName(user) {
  if (!user) return 'Compte';
  
  // ⚠️⚠️⚠️ SIMPLIFICATION : Utiliser directement user.username (qui devrait contenir le username du formulaire après connectUser)
  // connectUser récupère déjà le username du formulaire depuis localStorage et le met dans user.username
  if (user.username && 
      user.username !== '' && 
      user.username !== 'null' && 
      !user.username.includes('@')) {
    return user.username;
  }
  
  // Prioriser firstName + lastName
  if (user.firstName && user.lastName) {
    return `${user.firstName} ${user.lastName}`;
  }
  if (user.firstName) {
    return user.firstName;
  }
  if (user.first_name && user.last_name) {
    return `${user.first_name} ${user.last_name}`;
  }
  if (user.first_name) {
    return user.first_name;
  }
  
  // Fallback sur email (dernier recours)
  if (user.email) {
    return user.email.split('@')[0];
  }
  
  return 'Utilisateur';
}

// ===============================
// TOKEN MANAGEMENT
// ===============================
function getAuthToken() {
  const rememberMe = localStorage.getItem('rememberMe') === 'true';
  
  // 1. PRIORITÉ : Chercher dans cognito_tokens (source principale pour OAuth)
  try {
    const cognitoTokensRaw = rememberMe 
      ? localStorage.getItem('cognito_tokens') 
      : sessionStorage.getItem('cognito_tokens') || localStorage.getItem('cognito_tokens');
    
    if (cognitoTokensRaw) {
      const cognitoTokens = JSON.parse(cognitoTokensRaw);
      if (cognitoTokens && cognitoTokens.access_token) {
        console.log('[AUTH] Token récupéré depuis cognito_tokens');
        return cognitoTokens.access_token;
      }
    }
  } catch (e) {
    console.warn('[AUTH] Erreur parsing cognito_tokens:', e);
  }
  
  // 2. Chercher directement dans localStorage/sessionStorage
  let token = rememberMe 
    ? localStorage.getItem('accessToken') 
    : sessionStorage.getItem('accessToken');
  
  if (token) {
    console.log('[AUTH] Token récupéré depuis accessToken direct');
    return token;
  }
  
  // 3. Fallback sur currentUser
  if (window.currentUser) {
    token = window.currentUser.accessToken || window.currentUser.access_token || null;
    if (token) {
      console.log('[AUTH] Token récupéré depuis currentUser');
      return token;
    }
  }
  
  console.warn('[AUTH] Aucun token trouvé');
  return null;
}

function getRefreshToken() {
  const rememberMe = localStorage.getItem('rememberMe') === 'true';
  
  if (rememberMe) {
    return localStorage.getItem('refreshToken') || (window.currentUser?.refreshToken) || null;
  } else {
    return sessionStorage.getItem('refreshToken') || (window.currentUser?.refreshToken) || null;
  }
}

function setAuthTokens(accessToken, refreshToken, rememberMe = false) {
  if (rememberMe) {
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
    localStorage.setItem('rememberMe', 'true');
  } else {
    sessionStorage.setItem('accessToken', accessToken);
    sessionStorage.setItem('refreshToken', refreshToken);
    sessionStorage.setItem('rememberMe', 'false');
    localStorage.removeItem('rememberMe');
  }
}

// ===============================
// OAUTH GOOGLE
// ===============================
async function startGoogleLogin() {
  if (isGoogleLoginInProgress) {
    console.warn('⚠️ Connexion Google déjà en cours - double clic ignoré');
    if (typeof showNotification === 'function') {
      showNotification('⏳ Connexion en cours... Veuillez patienter', 'info');
    }
    return;
  }
  
  isGoogleLoginInProgress = true;
  // Exposer globalement pour que map_logic.js puisse vérifier
  if (typeof window !== 'undefined') {
    window.isGoogleLoginInProgress = true;
  }
  
  // Afficher un overlay de chargement
  showGoogleLoginLoading();
  
  try {
    const verifier = randomString(80);
    const challenge = await pkceChallengeFromVerifier(verifier);
    
    // ⚠️⚠️⚠️ FIX MODE PRIVÉ : Encoder les données du formulaire dans le state OAuth
    let state = randomString(24);
    let pendingDataForState = null;
    
    // Récupérer les données du formulaire si disponibles
    try {
      let savedData = null;
      try {
        savedData = localStorage.getItem('pendingRegisterDataForGoogle');
      } catch (e) {
        try {
          savedData = sessionStorage.getItem('pendingRegisterDataForGoogle');
        } catch (e2) {
          if (window.pendingRegisterData) {
            savedData = JSON.stringify(window.pendingRegisterData);
          }
        }
      }
      
      if (savedData) {
        pendingDataForState = JSON.parse(savedData);
        // Encoder seulement les données essentielles (username, photoData) dans le state
        // Limiter la taille pour éviter les problèmes avec les URLs
        const essentialData = {
          username: pendingDataForState.username || null,
          // photoData est trop gros, on le garde dans sessionStorage
          hasPhotoData: !!pendingDataForState.photoData
        };
        if (essentialData.username) {
          // Encoder en base64 et ajouter au state
          try {
            const encodedData = btoa(JSON.stringify(essentialData));
            state = state + '_' + encodedData.substring(0, 100); // Limiter la taille mais garder assez pour le username
            console.log('[GOOGLE LOGIN] ✅ Données formulaire encodées dans state OAuth:', essentialData);
          } catch (e) {
            console.warn('[GOOGLE LOGIN] ⚠️ Erreur encodage dans state:', e);
          }
        }
      }
    } catch (e) {
      console.warn('[GOOGLE LOGIN] ⚠️ Impossible d\'encoder les données dans state:', e);
    }

    authSave("pkce_verifier", verifier);
    authSave("oauth_state", state);

    // ⚠️⚠️⚠️ CRITIQUE : TOUJOURS forcer la validation Google (même pour les reconnexions)
    // Utiliser 'consent' seul pour forcer Google à demander le consentement à chaque fois
    // 'select_account' peut être ignoré si l'utilisateur n'a qu'un seul compte
    // 'consent' force Google à demander la validation smartphone même si l'utilisateur est déjà connecté
    const promptValue = 'consent';  // ⚠️⚠️⚠️ TOUJOURS forcer consentement = validation smartphone OBLIGATOIRE
    
    console.log('[GOOGLE LOGIN] ⚠️⚠️⚠️ Validation Google FORCÉE - Prompt:', promptValue);

    const authorizeUrl =
      `${COGNITO.domain}/oauth2/authorize` +
      `?client_id=${encodeURIComponent(COGNITO.clientId)}` +
      `&response_type=code` +
      `&scope=${encodeURIComponent(COGNITO.scopes.join(" "))}` +
      `&redirect_uri=${encodeURIComponent(COGNITO.redirectUri)}` +
      `&state=${encodeURIComponent(state)}` +
      `&code_challenge=${encodeURIComponent(challenge)}` +
      `&code_challenge_method=S256` +
      `&identity_provider=Google` +
      `&prompt=${encodeURIComponent(promptValue)}`; // ⚠️⚠️⚠️ CRITIQUE : select_account consent pour première inscription = validation smartphone OBLIGATOIRE

    console.log('[GOOGLE LOGIN] ⚠️⚠️⚠️ URL OAuth générée avec prompt:', promptValue);
    window.location.assign(authorizeUrl);
  } catch (error) {
    console.error('❌ Erreur startGoogleLogin:', error);
    isGoogleLoginInProgress = false;
    if (typeof window !== 'undefined') {
      window.isGoogleLoginInProgress = false;
    }
    hideGoogleLoginLoading();
    if (typeof showNotification === 'function') {
      showNotification('❌ Erreur lors de la connexion Google', 'error');
    }
  }
}

// Fonction pour afficher l'overlay de chargement Google
function showGoogleLoginLoading() {
  // Créer ou réutiliser l'overlay
  let overlay = document.getElementById('google-login-loading-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'google-login-loading-overlay';
    overlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.8);
      backdrop-filter: blur(10px);
      z-index: 99999;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-direction: column;
      pointer-events: all;
      padding-top: 40px;
      padding-bottom: 40px;
      box-sizing: border-box;
    `;
    document.body.appendChild(overlay);
  }
  
  overlay.innerHTML = `
    <div style="text-align:center;color:#fff;max-width:400px;padding:40px;">
      <div style="font-size:64px;margin-bottom:20px;animation:spin 1s linear infinite;">⏳</div>
      <h2 style="margin:0 0 10px;font-size:24px;font-weight:700;background:linear-gradient(135deg,#00ffc3,#3b82f6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">Validation Google en cours...</h2>
      <p style="margin:0;font-size:14px;color:rgba(255,255,255,0.7);">Veuillez valider sur votre smartphone si demandé, puis patientez.</p>
    </div>
    <style>
      @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }
    </style>
  `;
  
  overlay.style.display = 'flex';
}

// Fonction pour masquer l'overlay de chargement Google
function hideGoogleLoginLoading() {
  const overlay = document.getElementById('google-login-loading-overlay');
  if (overlay) {
    overlay.style.display = 'none';
    overlay.remove();
  }
}

// ===============================
// UTILITAIRE CENTRAGE MODAL
// ===============================
function centerModalBackdrop() {
  const backdrop = document.getElementById('publish-modal-backdrop');
  if (backdrop) {
    backdrop.style.paddingTop = '40px';
    backdrop.style.paddingBottom = '40px';
    backdrop.style.boxSizing = 'border-box';
  }
}

// ===============================
// UTILITAIRES JWT & SESSION
// ===============================
function decodeJwtPayload(token) {
  const payload = token.split(".")[1];
  const pad = payload.length % 4 === 0 ? "" : "=".repeat(4 - (payload.length % 4));
  const b64 = (payload + pad).replace(/-/g, "+").replace(/_/g, "/");
  const json = atob(b64);
  return JSON.parse(json);
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

// ===============================
// SAFE SET ITEM (avec gestion quota)
// ===============================
function safeSetItem(key, value) {
  try {
    localStorage.setItem(key, value);
    return true;
  } catch (e) {
    if (e.name === 'QuotaExceededError' || e.message.includes('quota')) {
      console.warn(`⚠️ localStorage plein (quota exceeded) pour ${key}...`);
      
      // PRIORITY HOTFIX: Si c'est currentUser, nettoyer la clé et continuer (ne pas freeze UI)
      if (key === 'currentUser') {
        try {
          // Supprimer l'ancien currentUser pour libérer de l'espace
          localStorage.removeItem('currentUser');
          console.warn('⚠️ currentUser supprimé pour libérer de l\'espace');
          
          // Si value est un objet user, essayer de sauvegarder la version slim
          try {
            const userObj = typeof value === 'string' ? JSON.parse(value) : value;
            const slimUser = saveUserSlim(userObj);
            if (slimUser) {
              // ⚠️ OPTIMISATION : saveUserSlim exclut déjà photoData, mais on double-vérifie
              const userForStorage = removePhotoDataForStorage(slimUser);
              const slimJson = JSON.stringify(userForStorage);
              localStorage.setItem('currentUser', slimJson);
              console.log('✅ Version slim de currentUser sauvegardée (photoData exclu)');
              return true;
            }
          } catch (parseError) {
            console.warn('⚠️ Impossible de parser/sauvegarder version slim:', parseError);
          }
          
          // Continuer le flow même si on ne peut pas sauvegarder
          console.warn('⚠️ Continuation du flow sans sauvegarder currentUser (quota exceeded)');
          return false; // Indiquer que la sauvegarde a échoué mais continuer
        } catch (cleanError) {
          console.error('❌ Erreur lors du nettoyage currentUser:', cleanError);
          // Continuer quand même
          return false;
        }
      }
      
      // Pour les autres clés, nettoyage ULTRA-AGRESSIF
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
        
        // ÉTAPE 4: Essayer de sauvegarder la nouvelle valeur
        try {
          localStorage.setItem(key, value);
          console.log(`✅ ${key} sauvegardé après nettoyage ultra-agressif`);
          
          if (typeof showNotification === 'function') {
            showNotification('✅ Stockage nettoyé. Vos données essentielles sont conservées.', 'success');
          }
          return true;
        } catch (e2) {
          console.error(`❌ Impossible de sauvegarder ${key} même après nettoyage ultra-agressif:`, e2);
          
          // DERNIÈRE TENTATIVE : Vider complètement et ne garder QUE les tokens
          try {
            const tokens = localStorage.getItem('cognito_tokens');
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

// ===============================
// VARIABLES GLOBALES REGISTER
// ===============================
let registerStep = 1;
let registerData = {
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

let isSubmittingProRegister = false;

// ===============================
// MODAL AUTH - FERMETURE
// ===============================
function closeAuthModal() {
  console.log('🚪 closeAuthModal called - Fermeture FORCEE du modal auth');
  
  // FERMETURE AGGRESSIVE : Fermer TOUS les éléments possibles
  const backdrop = document.getElementById("publish-modal-backdrop");
  const modal = document.getElementById("publish-modal-inner");
  const authModal = document.getElementById("authModal");
  const onboardingModal = document.getElementById("onboardingModal");
  
  // Fermer le backdrop avec tous les styles possibles
  if (backdrop) {
    backdrop.style.display = "none";
    backdrop.style.visibility = "hidden";
    backdrop.style.opacity = "0";
    backdrop.style.zIndex = "-1";
    backdrop.classList.remove('active', 'visible', 'shown');
    backdrop.setAttribute('aria-hidden', 'true');
    // Forcer avec !important via style direct
    backdrop.setAttribute('style', 'display: none !important; visibility: hidden !important; opacity: 0 !important; z-index: -1 !important;');
    console.log('🚪 Backdrop fermé FORCE');
  }
  
  // Vider le contenu du modal
  if (modal) {
    modal.innerHTML = '';
    modal.style.display = 'none';
    modal.setAttribute('style', 'display: none !important;');
    console.log('🚪 Modal vidé FORCE');
  }
  
  // Supprimer authModal si présent
  if (authModal) {
    authModal.remove();
    console.log('🚪 authModal supprimé');
  }
  
  // Supprimer onboardingModal si présent
  if (onboardingModal) {
    onboardingModal.remove();
    console.log('🚪 onboardingModal supprimé');
  }
  
  // Nettoyer TOUTES les données temporaires
  window.pendingRegisterPhoto = null;
  window.registerSelectedAddress = null;
  window.registerPhotoData = null;
  window.registerPhotoFile = null;
  window.oauthPhotoFile = null;
  window.oauthPhotoUploadData = null;
  
  // Réinitialiser les données d'inscription
  window.registerStep = 1;
  window.registerData = {
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
  window.isSubmittingProRegister = false;
  
  // Réinitialiser le flag de connexion Google en cours
  if (typeof isGoogleLoginInProgress !== 'undefined') {
    isGoogleLoginInProgress = false;
  }
  
  // Forcer la fermeture de tous les modals via closePublishModal aussi
  if (typeof closePublishModal === 'function') {
    try {
      closePublishModal();
    } catch (e) {
      console.warn('Erreur closePublishModal:', e);
    }
  }
  
  // ⚠️⚠️⚠️ CRITIQUE : Restaurer le scroll du body et réactiver la map pour permettre les popups
  // Sinon, après la connexion Google, les popups ne peuvent pas s'afficher
  document.body.style.overflow = '';
  
  // Réactiver la map si elle existe (pour permettre les popups d'événements)
  if (typeof map !== 'undefined' && map) {
    try {
      map.scrollWheelZoom.enable();
      map.dragging.enable();
      map.touchZoom.enable();
      map.doubleClickZoom.enable();
      const mapContainer = map.getContainer();
      if (mapContainer) {
        mapContainer.style.pointerEvents = 'auto';
      }
      console.log('🚪 Map réactivée après fermeture modal auth');
    } catch (e) {
      console.warn('Erreur réactivation map:', e);
    }
  }
  
  console.log('🚪 Auth modal fermé COMPLÈTEMENT (force)');
}

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

// ===============================
// LOAD SAVED USER
// ===============================
function loadSavedUser() {
  try {
      const savedUser = localStorage.getItem('currentUser');
      if (savedUser) {
        const parsedUser = JSON.parse(savedUser);
        
        // ⚠️⚠️⚠️ CRITIQUE : Normaliser photoData lors du chargement (convertir "null" en null réel)
        if (parsedUser.photoData === 'null' || parsedUser.photoData === 'undefined' || parsedUser.photoData === '') {
          parsedUser.photoData = null;
          // Sauvegarder la version normalisée (sans photoData)
          const userForStorage = removePhotoDataForStorage(parsedUser);
          localStorage.setItem('currentUser', JSON.stringify(userForStorage));
          console.log('[LOAD SAVED USER] ⚠️⚠️⚠️ photoData normalisé de "null" vers null lors du chargement');
        }
        
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
          if (typeof window !== 'undefined' && window.currentUser !== undefined) {
            window.currentUser.isLoggedIn = false;
          }
          // Forcer profileComplete à false pour forcer le formulaire
          parsedUser.profileComplete = false;
          localStorage.removeItem('cognito_tokens');
          // ⚠️ OPTIMISATION : Exclure photoData avant sauvegarde
          const userForStorage = removePhotoDataForStorage({ ...parsedUser, isLoggedIn: false, profileComplete: false });
          localStorage.setItem('currentUser', JSON.stringify(userForStorage));
          return;
        }
        
        // ⚠️⚠️⚠️ CORRECTION : Si "Rester connecté" est activé ET tokens valides → restaurer la session
        const rememberMe = localStorage.getItem('rememberMe') === 'true';
        
        if (rememberMe && hasValidTokens) {
          console.log('✅✅✅ [AUTH] "Rester connecté" activé + tokens valides → RESTAURATION SESSION AUTOMATIQUE');
          
          // Restaurer la session avec isLoggedIn: true
          if (typeof window !== 'undefined') {
            window.currentUser = {
              ...parsedUser,
              isLoggedIn: true,
              profileComplete: parsedUser.profileComplete !== false
            };
            
            console.log('[AUTH] ✅ Session restaurée automatiquement pour:', window.currentUser.email || window.currentUser.username);
            
            // Mettre à jour l'UI
            setTimeout(() => {
              if (typeof window.updateAccountBlockLegitimately === 'function') {
                window.updateAccountBlockLegitimately();
              }
              if (typeof window.updateAuthUI === 'function') {
                window.updateAuthUI(window.currentUser);
              }
            }, 100);
          }
          return;
        }
        
        // Si pas de "Rester connecté" ou tokens invalides → ne pas restaurer
        console.log('ℹ️ Données utilisateur trouvées mais session non restaurée automatiquement');
        parsedUser.profileComplete = false;
        
        // Fusionner avec les valeurs par défaut pour éviter les propriétés manquantes
        if (typeof window !== 'undefined' && window.currentUser !== undefined) {
          window.currentUser = {
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
            profileComplete: false // FORCER à false pour forcer le formulaire d'inscription
          };
        }
        console.log(`ℹ️ Données utilisateur chargées depuis localStorage mais session non restaurée (doit passer par modal de connexion)`);
        // Sauvegarder avec profileComplete: false
        try {
          if (typeof window !== 'undefined' && window.currentUser !== undefined) {
            // ⚠️ OPTIMISATION : Exclure photoData avant sauvegarde
            const userForStorage = removePhotoDataForStorage({ ...window.currentUser, profileComplete: false });
            localStorage.setItem('currentUser', JSON.stringify(userForStorage));
          }
        } catch (e) {
          console.warn('⚠️ Impossible de sauvegarder currentUser:', e);
        }
      }
    }
  } catch (e) {
    console.error('Erreur chargement utilisateur:', e);
  }
}

// ===============================
// LOGOUT AVEC CHOIX "RESTER CONNECTÉ"
// ===============================
// ⚠️⚠️⚠️ CRITIQUE : Demander "rester connecté" UNIQUEMENT à la déconnexion (comme les leaders mondiaux)
function askRememberMeOnLogout() {
  console.log('[LOGOUT] Demande choix "rester connecté" avant déconnexion');
  
  // Chercher le modal
  let modal = document.getElementById('authModal');
  if (!modal) {
    modal = document.getElementById('publish-modal-inner');
  }
  
  if (!modal) {
    console.warn('[LOGOUT] Modal non trouvé, déconnexion directe');
    performLogout(false); // Déconnexion complète par défaut
    return;
  }
  
  // S'assurer que le backdrop est visible
  let backdrop = document.getElementById('publish-modal-backdrop');
  if (!backdrop) {
    backdrop = document.getElementById('auth-modal-backdrop');
  }
  
  if (backdrop) {
    backdrop.style.display = 'flex';
    backdrop.style.visibility = 'visible';
    backdrop.style.opacity = '1';
    backdrop.style.zIndex = '9999';
    backdrop.style.paddingTop = '40px';
    backdrop.style.paddingBottom = '40px';
    backdrop.style.boxSizing = 'border-box';
  }
  
  modal.style.display = 'block';
  modal.style.visibility = 'visible';
  modal.style.opacity = '1';
  
  modal.innerHTML = `
    <div id="authModal" data-mode="logout-choice" style="padding:40px;max-width:500px;margin:0 auto;text-align:center;position:relative;">
      <!-- Bouton X (croix) pour fermer -->
      <button id="logout-close-btn" style="position:absolute;top:16px;right:16px;background:none;border:none;color:var(--ui-text-muted);font-size:24px;cursor:pointer;padding:8px;width:40px;height:40px;display:flex;align-items:center;justify-content:center;border-radius:50%;transition:all 0.2s;z-index:10;" onmouseover="this.style.background='rgba(239,68,68,0.2)';this.style.color='#ef4444';this.style.transform='scale(1.1)';" onmouseout="this.style.background='none';this.style.color='var(--ui-text-muted)';this.style.transform='scale(1)';" title="Fermer">✕</button>
      
      <!-- Logo et titre -->
      <div style="margin-bottom:32px;">
        <div style="font-size:64px;margin-bottom:16px;">🚪</div>
        <h2 style="margin:0 0 8px;font-size:28px;font-weight:800;color:#fff;background:linear-gradient(135deg,#00ffc3,#3b82f6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">Déconnexion</h2>
        <p style="margin:0;font-size:14px;color:var(--ui-text-muted);">Souhaitez-vous rester connecté pour la prochaine fois ?</p>
      </div>
      
      <div style="display:flex;flex-direction:column;gap:12px;">
        <button id="logout-yes-btn" style="width:100%;padding:16px;border-radius:12px;border:2px solid rgba(0,255,195,0.3);background:linear-gradient(135deg,rgba(0,255,195,0.1),rgba(59,130,246,0.1));color:var(--ui-text-main);font-weight:600;font-size:15px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(0,255,195,0.6)';this.style.background='linear-gradient(135deg,rgba(0,255,195,0.2),rgba(59,130,246,0.2))';" onmouseout="this.style.borderColor='rgba(0,255,195,0.3)';this.style.background='linear-gradient(135deg,rgba(0,255,195,0.1),rgba(59,130,246,0.1))';">
          ✅ Oui, rester connecté
        </button>
        <button id="logout-no-btn" style="width:100%;padding:16px;border-radius:12px;border:2px solid rgba(255,255,255,0.2);background:rgba(255,255,255,0.05);color:var(--ui-text-main);font-weight:600;font-size:15px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(255,255,255,0.4)';this.style.background='rgba(255,255,255,0.1)';" onmouseout="this.style.borderColor='rgba(255,255,255,0.2)';this.style.background='rgba(255,255,255,0.05)';">
          ❌ Non, me déconnecter complètement
        </button>
      </div>
    </div>
  `;
  
  // ⚠️⚠️⚠️ CRITIQUE : Attacher les event listeners après injection HTML (CSP)
  // Utiliser setTimeout pour garantir que le DOM est prêt
  setTimeout(() => {
    const yesBtn = document.getElementById('logout-yes-btn');
    const noBtn = document.getElementById('logout-no-btn');
    const closeBtn = document.getElementById('logout-close-btn');
    
    console.log('[LOGOUT] Recherche boutons:', { 
      yesBtn: !!yesBtn, 
      noBtn: !!noBtn, 
      closeBtn: !!closeBtn,
      performLogoutAvailable: typeof window.performLogout === 'function',
      closeAuthModalAvailable: typeof closeAuthModal === 'function',
      closePublishModalAvailable: typeof closePublishModal === 'function'
    });
    
    if (!yesBtn || !noBtn || !closeBtn) {
      console.error('[LOGOUT] ❌ Boutons non trouvés dans le DOM');
      return;
    }
    
    if (yesBtn) {
      yesBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        console.log('[LOGOUT] ✅ Bouton "Oui" cliqué');
        if (typeof window.performLogout === 'function') {
          window.performLogout(true);
        } else {
          console.error('[LOGOUT] ❌ performLogout non trouvé');
          alert('Erreur: fonction de déconnexion non disponible');
        }
      }, { capture: true });
    }
    
    if (noBtn) {
      noBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        console.log('[LOGOUT] ✅ Bouton "Non" cliqué');
        if (typeof window.performLogout === 'function') {
          window.performLogout(false);
        } else {
          console.error('[LOGOUT] ❌ performLogout non trouvé');
          alert('Erreur: fonction de déconnexion non disponible');
        }
      }, { capture: true });
    }
    
    if (closeBtn) {
      closeBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        console.log('[LOGOUT] ✅ Bouton "Fermer" cliqué');
        if (typeof closeAuthModal === 'function') {
          closeAuthModal();
        } else if (typeof closePublishModal === 'function') {
          closePublishModal();
        } else {
          console.error('[LOGOUT] ❌ Aucune fonction de fermeture disponible');
        }
      }, { capture: true });
    }
    
    console.log('[LOGOUT] ✅ Event listeners attachés avec succès');
  }, 100);
  
  console.log('[LOGOUT] Modal de choix "rester connecté" affiché');
}

// Fonction de déconnexion réelle
async function performLogout(rememberMe) {
  console.log('[LOGOUT] Déconnexion avec rememberMe:', rememberMe);
  
  try {
    // Appeler /api/auth/logout si un token existe
    const accessToken = getAuthToken();
    if (accessToken) {
      try {
        console.log('[AUTH] Appel POST /api/auth/logout...');
        const logoutResponse = await fetch(`${API_BASE_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`
          }
        });
        console.log('[AUTH] POST /api/auth/logout - Status:', logoutResponse.status);
      } catch (error) {
        console.log('[AUTH] Erreur lors de la deconnexion cote serveur (ignoree):', error);
      }
    }
  } catch (error) {
    console.error('[AUTH] Erreur lors de la deconnexion:', error);
  }
  
  // ⚠️⚠️⚠️ CRITIQUE : Gérer rememberMe
  if (rememberMe) {
    // Garder les tokens dans localStorage pour la prochaine fois
    localStorage.setItem('rememberMe', 'true');
    console.log('[LOGOUT] ✅ Tokens conservés - reconnexion automatique à la prochaine visite');
  } else {
    // Supprimer COMPLÈTEMENT tous les tokens
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('cognito_tokens');
    localStorage.removeItem('rememberMe');
    sessionStorage.removeItem('accessToken');
    sessionStorage.removeItem('refreshToken');
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    sessionStorage.removeItem('cognito_tokens');
    sessionStorage.removeItem('rememberMe');
    console.log('[LOGOUT] ✅ Tokens supprimés - reconnexion requise à la prochaine visite');
  }
  
  // Toujours supprimer currentUser (sera recréé à la prochaine connexion)
  localStorage.removeItem('currentUser');
  sessionStorage.removeItem('currentUser');
  
  // Réinitialiser window.currentUser et currentUser global
  if (typeof window !== 'undefined') {
    // Utiliser getDefaultUser si disponible pour réinitialiser complètement
    if (typeof window.getDefaultUser === 'function') {
      window.currentUser = window.getDefaultUser();
    } else {
      window.currentUser = {
        isLoggedIn: false,
        username: '',
        email: '',
        profile_photo_url: null,
        favorites: [],
        agenda: [],
        likes: [],
        participating: [],
        reviews: {},
        subscription: 'free'
      };
    }
  }
  
  // ⚠️⚠️⚠️ CRITIQUE : Mettre à jour currentUser global aussi
  if (typeof currentUser !== 'undefined') {
    // Utiliser getDefaultUser si disponible
    if (typeof getDefaultUser === 'function') {
      currentUser = getDefaultUser();
    } else {
      currentUser.isLoggedIn = false;
      currentUser.username = '';
      currentUser.email = '';
      currentUser.profile_photo_url = null;
      if (!Array.isArray(currentUser.favorites)) currentUser.favorites = [];
      if (!Array.isArray(currentUser.agenda)) currentUser.agenda = [];
      if (!Array.isArray(currentUser.likes)) currentUser.likes = [];
      if (!Array.isArray(currentUser.participating)) currentUser.participating = [];
      if (!currentUser.reviews || typeof currentUser.reviews !== 'object') currentUser.reviews = {};
      if (!currentUser.subscription) currentUser.subscription = 'free';
    }
  }
  
  // Fermer les modals
  if (typeof closeAuthModal === 'function') {
    closeAuthModal();
  }
  if (typeof closePublishModal === 'function') {
    closePublishModal();
  }
  
  // ⚠️⚠️⚠️ CRITIQUE : NE PAS appeler updateAuthUI(null) car cela génère une erreur
  // updateAuthUI nécessite un slimUser valide avec un id
  // À la place, on met simplement à jour les boutons et le bloc compte
  
  // Mettre à jour le bloc compte pour le masquer
  if (typeof window !== 'undefined' && typeof window.updateAccountBlockLegitimately === 'function') {
    window.updateAccountBlockLegitimately();
  }
  
  // ⚠️⚠️⚠️ CRITIQUE : Mettre à jour les boutons auth pour afficher "Connexion" au lieu de "Compte"
  if (typeof updateAuthButtons === 'function') {
    updateAuthButtons();
  } else if (typeof window !== 'undefined' && typeof window.updateAuthButtons === 'function') {
    window.updateAuthButtons();
  }
  
  // ⚠️⚠️⚠️ FORCER la mise à jour immédiate de l'UI pour masquer le bouton "Compte"
  setTimeout(() => {
    const authButtons = document.getElementById('auth-buttons');
    const accountBtn = document.getElementById('account-topbar-btn');
    if (authButtons) {
      authButtons.style.display = 'flex';
      authButtons.style.visibility = 'visible';
      authButtons.style.opacity = '1';
      authButtons.style.pointerEvents = 'auto';
    }
    if (accountBtn) {
      accountBtn.style.display = 'none';
      accountBtn.style.visibility = 'hidden';
      accountBtn.style.opacity = '0';
      accountBtn.style.pointerEvents = 'none';
    }
  }, 0);
  
  // ⚠️⚠️⚠️ FORCER la mise à jour de l'UI même si les fonctions ne sont pas disponibles
  setTimeout(() => {
    const authButtons = document.getElementById('auth-buttons');
    const accountBtn = document.getElementById('account-topbar-btn');
    if (authButtons) {
      authButtons.style.display = 'flex';
      authButtons.style.visibility = 'visible';
      authButtons.style.opacity = '1';
      authButtons.style.pointerEvents = 'auto';
      
      // ⚠️⚠️ CRITIQUE : Réattacher les event listeners après déconnexion pour garantir que le bouton fonctionne
      let loginBtn = document.getElementById('login-topbar-btn');
      if (!loginBtn && authButtons) {
        loginBtn = authButtons.querySelector('button');
      }
      
      if (loginBtn) {
        console.log('[LOGOUT] ✅ Bouton Connexion trouvé, réattachement des listeners');
        
        // ⚠️⚠️⚠️ CRITIQUE : Supprimer l'onclick inline qui peut interférer
        loginBtn.removeAttribute('onclick');
        
        // Supprimer l'ancien listener s'il existe en clonant le bouton
        const newLoginBtn = loginBtn.cloneNode(true);
        loginBtn.parentNode.replaceChild(newLoginBtn, loginBtn);
        
        // ⚠️⚠️⚠️ S'assurer que le bouton est cliquable
        newLoginBtn.style.pointerEvents = 'auto';
        newLoginBtn.style.cursor = 'pointer';
        newLoginBtn.style.opacity = '1';
        newLoginBtn.style.display = 'flex';
        newLoginBtn.style.visibility = 'visible';
        
        // Ajouter un nouveau listener avec plusieurs fallbacks
        newLoginBtn.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          e.stopImmediatePropagation();
          console.log('[LOGOUT] ✅✅✅ Bouton Connexion cliqué après déconnexion');
          
          // Essayer plusieurs méthodes pour ouvrir le modal de connexion
          if (typeof window.openLoginModal === 'function') {
            window.openLoginModal();
          } else if (typeof window.openAuthModal === 'function') {
            window.openAuthModal('login');
          } else if (typeof openLoginModal === 'function') {
            openLoginModal();
          } else if (typeof openAuthModal === 'function') {
            openAuthModal('login');
          } else {
            console.warn('[LOGOUT] ⚠️ Aucune fonction de connexion disponible, rafraîchissement de la page...');
            // Dernier recours : rafraîchir la page pour réinitialiser tout
            window.location.reload();
          }
        }, { capture: true });
        
        console.log('[LOGOUT] ✅✅✅ Event listener réattaché au bouton Connexion avec fallbacks', {
          display: window.getComputedStyle(newLoginBtn).display,
          visibility: window.getComputedStyle(newLoginBtn).visibility,
          pointerEvents: window.getComputedStyle(newLoginBtn).pointerEvents,
          cursor: window.getComputedStyle(newLoginBtn).cursor
        });
      } else {
        console.warn('[LOGOUT] ⚠️ Bouton Connexion non trouvé dans auth-buttons');
      }
    }
    if (accountBtn) {
      accountBtn.style.display = 'none';
      accountBtn.style.visibility = 'hidden';
      accountBtn.style.opacity = '0';
      accountBtn.style.pointerEvents = 'none';
    }
  }, 100);
  
  // ⚠️⚠️⚠️ DOUBLE VÉRIFICATION après un délai supplémentaire pour s'assurer que tout est bien mis à jour
  setTimeout(() => {
    if (typeof updateAuthButtons === 'function') {
      updateAuthButtons();
    } else if (typeof window !== 'undefined' && typeof window.updateAuthButtons === 'function') {
      window.updateAuthButtons();
    }
  }, 300);
  
  // Notification
  if (typeof showNotification === 'function') {
    if (rememberMe) {
      showNotification('✅ Vous serez reconnecté automatiquement à la prochaine visite', 'success');
    } else {
      showNotification('👋 Vous êtes déconnecté. À bientôt !', 'info');
    }
  }
  
  console.log('[LOGOUT] ✅ Déconnexion terminée');
  
  // ⚠️⚠️⚠️ CRITIQUE : Si "rester connecté" n'est pas activé, recharger la page pour réinitialiser tout
  if (!rememberMe) {
    console.log('[LOGOUT] Rechargement de la page pour réinitialiser complètement...');
    setTimeout(() => {
      window.location.reload();
    }, 500); // Attendre un peu pour que la notification s'affiche
  }
}

// Fonction logout publique (appelée depuis le bouton déconnexion)
// ⚠️⚠️⚠️ FLUX STANDARD : Déconnexion simple sans demander "rester connecté"
// L'option "rester connecté" est dans les paramètres du compte
async function logout() {
  console.log('[LOGOUT] logout() appelée - déconnexion simple');
  
  // ⚠️⚠️⚠️ Vérifier si "rester connecté" est activé dans les paramètres
  const rememberMe = localStorage.getItem('rememberMe') === 'true';
  
  // Déconnexion directe (sans modal de confirmation)
  await performLogout(rememberMe);
}

// ===============================
// OPEN AUTH MODAL
// ===============================
function openAuthModal(mode = 'login') {
  // Log ASCII obligatoire pour debug
  console.log("openAuthModal mode =", mode);
  console.log('[AUTH] ⚠️⚠️⚠️ DEBUG COMPLET - openAuthModal appelé');
  
  // Si c'est le mode register, utiliser le formulaire complet (showProRegisterForm)
  if (mode === 'register') {
    console.log('[AUTH] Mode register - Utilisation du formulaire complet showProRegisterForm');
    // ⚠️⚠️⚠️ CRITIQUE : Marquer qu'on veut créer un compte (même si l'email existe)
    try {
      sessionStorage.setItem('wantToRegister', 'true');
    } catch (e) {
      console.warn('[AUTH] ⚠️ Impossible de sauvegarder wantToRegister:', e);
    }
    if (typeof showProRegisterForm === 'function') {
      showProRegisterForm();
      return;
    } else if (typeof window.showProRegisterForm === 'function') {
      window.showProRegisterForm();
      return;
    } else {
      console.warn('[AUTH] showProRegisterForm non disponible, utilisation du formulaire simplifié');
    }
  }
  
  const backdrop = document.getElementById('publish-modal-backdrop');
  const modal = document.getElementById('publish-modal-inner');
  const publishModal = document.getElementById('publish-modal');
  
  console.log('[AUTH] ⚠️⚠️⚠️ ÉLÉMENTS TROUVÉS:', {
    backdrop: !!backdrop,
    modal: !!modal,
    publishModal: !!publishModal,
    backdropDisplay: backdrop ? window.getComputedStyle(backdrop).display : 'N/A',
    backdropVisibility: backdrop ? window.getComputedStyle(backdrop).visibility : 'N/A',
    backdropOpacity: backdrop ? window.getComputedStyle(backdrop).opacity : 'N/A',
    backdropZIndex: backdrop ? window.getComputedStyle(backdrop).zIndex : 'N/A'
  });
  
  if (!backdrop || !modal) {
    console.error('[AUTH] ❌❌❌ Modal elements not found');
    console.error('[AUTH] backdrop:', backdrop);
    console.error('[AUTH] modal:', modal);
    console.error('[AUTH] publishModal:', publishModal);
    
    // Essayer de créer les éléments s'ils n'existent pas
    if (!backdrop) {
      console.log('[AUTH] ⚠️ Création du backdrop manquant...');
      const newBackdrop = document.createElement('div');
      newBackdrop.id = 'publish-modal-backdrop';
      document.body.appendChild(newBackdrop);
      console.log('[AUTH] ✅ Backdrop créé');
    }
    if (!modal && backdrop) {
      console.log('[AUTH] ⚠️ Création du modal manquant...');
      if (!publishModal) {
        const newPublishModal = document.createElement('div');
        newPublishModal.id = 'publish-modal';
        backdrop.appendChild(newPublishModal);
      }
      const newModal = document.createElement('div');
      newModal.id = 'publish-modal-inner';
      if (publishModal || document.getElementById('publish-modal')) {
        (publishModal || document.getElementById('publish-modal')).appendChild(newModal);
      } else {
        backdrop.appendChild(newModal);
      }
      console.log('[AUTH] ✅ Modal créé');
    }
    
    // Réessayer après création
    const newBackdrop = document.getElementById('publish-modal-backdrop');
    const newModal = document.getElementById('publish-modal-inner');
    if (!newBackdrop || !newModal) {
      console.error('[AUTH] ❌❌❌ Impossible de créer les éléments du modal');
      return;
    }
  }
  
  // Récupérer les éléments à nouveau après création éventuelle
  let finalBackdrop = document.getElementById('publish-modal-backdrop');
  let finalModal = document.getElementById('publish-modal-inner');
  let finalPublishModal = document.getElementById('publish-modal');
  
  // Si les éléments n'existent toujours pas, les créer
  if (!finalBackdrop) {
    console.log('[AUTH] ⚠️ Création du backdrop...');
    finalBackdrop = document.createElement('div');
    finalBackdrop.id = 'publish-modal-backdrop';
    document.body.appendChild(finalBackdrop);
  }
  
  if (!finalPublishModal && finalBackdrop) {
    console.log('[AUTH] ⚠️ Création du publish-modal...');
    finalPublishModal = document.createElement('div');
    finalPublishModal.id = 'publish-modal';
    finalBackdrop.appendChild(finalPublishModal);
  }
  
  if (!finalModal && (finalPublishModal || finalBackdrop)) {
    console.log('[AUTH] ⚠️ Création du modal-inner...');
    finalModal = document.createElement('div');
    finalModal.id = 'publish-modal-inner';
    if (finalPublishModal) {
      finalPublishModal.appendChild(finalModal);
    } else if (finalBackdrop) {
      finalBackdrop.appendChild(finalModal);
    }
  }
  
  // Vérifier une dernière fois
  if (!finalBackdrop || !finalModal) {
    console.error('[AUTH] ❌❌❌ Impossible de créer ou trouver les éléments du modal');
    alert('Erreur : Impossible d\'afficher le modal de connexion. Veuillez rafraîchir la page.');
    return;
  }
  
  // Vérifier aussi avec l'ID authModal après injection
  console.log('[AUTH] ✅ Modal elements found, backdrop:', !!finalBackdrop, 'modal:', !!finalModal, 'publishModal:', !!finalPublishModal);

  // Valider le mode
  if (mode !== 'register' && mode !== 'login') {
    console.log('[AUTH] Invalid mode, defaulting to login');
    mode = 'login';
  }

  const isRegister = mode === 'register';
  console.log('[AUTH] isRegister:', isRegister);
  const title = isRegister ? 'Créer un compte' : 'Connexion';
  const subtitle = isRegister 
    ? 'Rejoignez MapEvent et découvrez les événements près de chez vous' 
    : 'Connectez-vous pour accéder à toutes les fonctionnalités';
  const primaryButtonText = isRegister ? 'Créer mon compte' : 'Se connecter';
  const primaryButtonAction = isRegister ? 'performRegister()' : 'performLogin()';
  const switchText = isRegister ? 'Déjà un compte ?' : 'Pas de compte ?';
  const switchLinkText = isRegister ? 'Se connecter' : 'Créer un compte';
  const switchAction = isRegister 
    ? 'openAuthModal(\'login\')' 
    : 'openAuthModal(\'register\')';

  const html = `
    <div id="authModal" data-mode="${mode}" style="padding:40px;max-width:450px;margin:0 auto;text-align:center;position:relative;">
      <!-- Bouton X (croix) pour fermer -->
      <button onclick="closeAuthModal()" style="position:absolute;top:16px;right:16px;background:none;border:none;color:var(--ui-text-muted);font-size:24px;cursor:pointer;padding:8px;width:40px;height:40px;display:flex;align-items:center;justify-content:center;border-radius:50%;transition:all 0.2s;z-index:10;" onmouseover="this.style.background='rgba(239,68,68,0.2)';this.style.color='#ef4444';this.style.transform='scale(1.1)';" onmouseout="this.style.background='none';this.style.color='var(--ui-text-muted)';this.style.transform='scale(1)';" title="Fermer">✕</button>
      
      <!-- Logo et titre -->
      <div style="margin-bottom:32px;">
        <div style="font-size:64px;margin-bottom:16px;">🌍</div>
        <h2 style="margin:0 0 8px;font-size:28px;font-weight:800;color:#fff;background:linear-gradient(135deg,#00ffc3,#3b82f6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">${title}</h2>
        <p style="margin:0;font-size:14px;color:var(--ui-text-muted);">${subtitle}</p>
      </div>
      
      ${!isRegister ? `
      <!-- Boutons de connexion sociale - Seulement pour LOGIN -->
      <div style="display:flex;flex-direction:column;gap:12px;margin-bottom:24px;">
        <button onclick="startGoogleLogin()" style="width:100%;padding:14px 20px;border-radius:12px;border:2px solid rgba(255,255,255,0.1);background:linear-gradient(135deg,rgba(255,255,255,0.1),rgba(255,255,255,0.05));color:#fff;display:flex;align-items:center;justify-content:center;gap:12px;font-weight:600;font-size:15px;cursor:pointer;transition:all 0.3s;backdrop-filter:blur(10px);" onmouseover="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='linear-gradient(135deg,rgba(0,255,195,0.2),rgba(59,130,246,0.2))';" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)';this.style.background='linear-gradient(135deg,rgba(255,255,255,0.1),rgba(255,255,255,0.05))';">
          <svg width="20" height="20" viewBox="0 0 24 24" style="fill:currentColor;">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
          </svg>
          <span>Continuer avec Google</span>
        </button>
      </div>
      
      <div style="display:flex;align-items:center;gap:12px;margin:24px 0;">
        <div style="flex:1;height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.1),transparent);"></div>
        <span style="font-size:12px;color:var(--ui-text-muted);font-weight:500;">ou</span>
        <div style="flex:1;height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.1),transparent);"></div>
      </div>
      ` : ''}
      
      ${isRegister ? `
      <!-- Formulaire d'inscription LEADER MONDIAL - avec photo + adresse -->
      <div style="margin-bottom:16px;text-align:left;">
        <label style="display:block;font-size:13px;font-weight:600;color:var(--ui-text-main);margin-bottom:8px;">📧 Email</label>
        <input type="email" id="register-email" placeholder="votre@email.com" readonly style="width:100%;padding:12px 16px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:var(--ui-text-main);font-size:14px;transition:all 0.3s;" onfocus="this.removeAttribute('readonly');this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(15,23,42,0.8)';" onblur="this.style.borderColor='rgba(255,255,255,0.1)';this.style.background='rgba(15,23,42,0.5)';" onclick="this.removeAttribute('readonly');this.focus();">
      </div>
      <div style="margin-bottom:16px;text-align:left;">
        <label style="display:block;font-size:13px;font-weight:600;color:var(--ui-text-main);margin-bottom:8px;">👤 Nom d'utilisateur</label>
        <input type="text" id="register-username" placeholder="Votre nom d'utilisateur" style="width:100%;padding:12px 16px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:var(--ui-text-main);font-size:14px;transition:all 0.3s;" onfocus="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(15,23,42,0.8)';" onblur="this.style.borderColor='rgba(255,255,255,0.1)';this.style.background='rgba(15,23,42,0.5)';">
      </div>
      <div style="margin-bottom:16px;text-align:left;">
        <label style="display:block;font-size:13px;font-weight:600;color:var(--ui-text-main);margin-bottom:8px;">🔒 Mot de passe</label>
        <div style="position:relative;">
          <input type="password" id="register-password" placeholder="Votre mot de passe" style="width:100%;padding:12px 40px 12px 16px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:var(--ui-text-main);font-size:14px;transition:all 0.3s;" onfocus="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(15,23,42,0.8)';" onblur="this.style.borderColor='rgba(255,255,255,0.1)';this.style.background='rgba(15,23,42,0.5)';" oninput="if(typeof validateRegisterPassword==='function')validateRegisterPassword(this.value)">
          <button type="button" onclick="if(typeof toggleRegisterPasswordVisibility==='function')toggleRegisterPasswordVisibility('register-password')" style="position:absolute;right:8px;top:50%;transform:translateY(-50%);background:none;border:none;color:var(--ui-text-muted);font-size:18px;cursor:pointer;padding:4px;width:32px;height:32px;display:flex;align-items:center;justify-content:center;">👁️</button>
        </div>
        <div id="register-password-rules" style="margin-top:8px;font-size:11px;color:var(--ui-text-muted);line-height:1.4;">
          <div id="register-password-match" style="display:none;color:#22c55e;">✓ Les mots de passe correspondent</div>
        </div>
      </div>
      <div style="margin-bottom:16px;text-align:left;">
        <label style="display:block;font-size:13px;font-weight:600;color:var(--ui-text-main);margin-bottom:8px;">🔒 Confirmer le mot de passe</label>
        <div style="position:relative;">
          <input type="password" id="register-password-confirm" placeholder="Confirmez votre mot de passe" style="width:100%;padding:12px 40px 12px 16px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:var(--ui-text-main);font-size:14px;transition:all 0.3s;" onfocus="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(15,23,42,0.8)';" onblur="this.style.borderColor='rgba(255,255,255,0.1)';this.style.background='rgba(15,23,42,0.5)';" oninput="if(typeof validateRegisterPasswordMatch==='function')validateRegisterPasswordMatch()">
          <button type="button" onclick="if(typeof toggleRegisterPasswordVisibility==='function')toggleRegisterPasswordVisibility('register-password-confirm')" style="position:absolute;right:8px;top:50%;transform:translateY(-50%);background:none;border:none;color:var(--ui-text-muted);font-size:18px;cursor:pointer;padding:4px;width:32px;height:32px;display:flex;align-items:center;justify-content:center;">👁️</button>
        </div>
      </div>
      
      <!-- Photo de profil -->
      <div style="margin-bottom:16px;text-align:left;">
        <label style="display:block;font-size:13px;font-weight:600;color:var(--ui-text-main);margin-bottom:8px;">📸 Photo de profil</label>
        <div id="register-photo-upload-zone" style="border:2px dashed rgba(0,255,195,0.5);border-radius:12px;padding:30px;text-align:center;background:rgba(0,255,195,0.05);cursor:pointer;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(0,255,195,0.8)';this.style.background='rgba(0,255,195,0.1)';" onmouseout="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(0,255,195,0.05)';">
          <div style="font-size:32px;margin-bottom:8px;">📷</div>
          <div style="color:var(--ui-text-main);margin-bottom:4px;font-weight:600;font-size:12px;">Cliquez pour sélectionner</div>
          <div style="color:var(--ui-text-muted);font-size:11px;">JPG, PNG ou GIF (max 5MB)</div>
          <input type="file" id="register-photo-input" accept="image/*" style="display:none;" onchange="if(typeof handleRegisterPhotoUpload==='function')handleRegisterPhotoUpload(event)">
        </div>
        <div id="register-photo-preview-container" style="display:none;margin-top:12px;text-align:center;">
          <img id="register-photo-preview" src="" style="width:100px;height:100px;border-radius:50%;object-fit:cover;border:3px solid #00ffc3;display:inline-block;">
        </div>
        <label style="display:flex;align-items:center;gap:8px;cursor:pointer;color:var(--ui-text-muted);font-size:12px;margin-top:8px;">
          <input type="checkbox" id="register-photo-later" style="cursor:pointer;">
          <span>Ajouter ma photo plus tard</span>
        </label>
      </div>
      
      <!-- Adresse postale mondiale -->
      <div style="margin-bottom:16px;text-align:left;">
        <label style="display:block;font-size:13px;font-weight:600;color:var(--ui-text-main);margin-bottom:8px;">📍 Adresse postale mondiale</label>
        <input type="text" id="register-address-input" placeholder="Commencez à taper votre adresse..." style="width:100%;padding:12px 16px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:var(--ui-text-main);font-size:14px;">
        <div id="register-address-suggestions" style="margin-top:8px;display:none;max-height:200px;overflow-y:auto;background:rgba(15,23,42,0.9);border-radius:8px;border:1px solid rgba(255,255,255,0.1);"></div>
        <div id="register-selected-address-display" style="display:none;padding:12px;background:rgba(0,255,195,0.1);border:1px solid rgba(0,255,195,0.3);border-radius:10px;margin-top:8px;">
          <div style="display:flex;align-items:start;gap:8px;">
            <span style="font-size:18px;">✅</span>
            <div style="flex:1;">
              <div style="font-weight:600;color:#00ffc3;margin-bottom:4px;font-size:13px;" id="register-selected-address-label"></div>
              <div style="font-size:11px;color:var(--ui-text-muted);" id="register-selected-address-details"></div>
            </div>
          </div>
        </div>
        <label style="display:flex;align-items:center;gap:8px;cursor:pointer;color:var(--ui-text-muted);font-size:12px;margin-top:8px;">
          <input type="checkbox" id="register-address-later" style="cursor:pointer;">
          <span>Vérifier mon adresse plus tard</span>
        </label>
      </div>
      ` : `
      <!-- Formulaire de connexion -->
      <div style="margin-bottom:16px;text-align:left;">
        <label style="display:block;font-size:13px;font-weight:600;color:var(--ui-text-main);margin-bottom:8px;">📧 Email</label>
        <input type="email" id="login-email" placeholder="votre@email.com" style="width:100%;padding:12px 16px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:var(--ui-text-main);font-size:14px;transition:all 0.3s;" onfocus="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(15,23,42,0.8)';" onblur="this.style.borderColor='rgba(255,255,255,0.1)';this.style.background='rgba(15,23,42,0.5)';">
      </div>
      <div style="margin-bottom:16px;text-align:left;">
        <label style="display:block;font-size:13px;font-weight:600;color:var(--ui-text-main);margin-bottom:8px;">🔒 Mot de passe</label>
        <div style="position:relative;">
          <input type="password" id="login-password" placeholder="Votre mot de passe" onkeypress="if(event.key==='Enter'&&typeof performLogin==='function')performLogin()" style="width:100%;padding:12px 40px 12px 16px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:var(--ui-text-main);font-size:14px;transition:all 0.3s;" onfocus="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(15,23,42,0.8)';" onblur="this.style.borderColor='rgba(255,255,255,0.1)';this.style.background='rgba(15,23,42,0.5)';">
          <button type="button" onclick="const pwd=document.getElementById('login-password');if(pwd.type==='password'){pwd.type='text';this.textContent='🙈';}else{pwd.type='password';this.textContent='👁️';}" style="position:absolute;right:8px;top:50%;transform:translateY(-50%);background:none;border:none;color:var(--ui-text-muted);font-size:18px;cursor:pointer;padding:4px;width:32px;height:32px;display:flex;align-items:center;justify-content:center;">👁️</button>
        </div>
      </div>
      <div style="margin-bottom:24px;text-align:left;">
        <label style="display:flex;align-items:center;gap:8px;cursor:pointer;font-size:13px;color:var(--ui-text-muted);">
          <input type="checkbox" id="login-remember-me" style="cursor:pointer;width:16px;height:16px;">
          <span>Rester connecté pour la prochaine fois</span>
        </label>
      </div>
      `}
      
      <button id="auth-primary-btn" data-action="${primaryButtonAction}" style="width:100%;padding:14px;border-radius:12px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:700;font-size:15px;cursor:pointer;margin-bottom:12px;transition:all 0.3s;" onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 8px 20px rgba(0,255,195,0.3)';" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='none';">
        ${primaryButtonText}
      </button>
      
      <!-- Lien pour switcher entre register/login -->
      <div style="text-align:center;margin-bottom:16px;">
        <span style="font-size:13px;color:var(--ui-text-muted);">${switchText} </span>
        <button id="auth-switch-btn" data-mode="${isRegister ? 'login' : 'register'}" style="background:none;border:none;color:#00ffc3;font-size:13px;font-weight:600;cursor:pointer;text-decoration:underline;padding:0;transition:all 0.3s;" onmouseover="this.style.color='#3b82f6';" onmouseout="this.style.color='#00ffc3';">
          ${switchLinkText}
        </button>
      </div>
      
      <button id="auth-cancel-btn" type="button" onclick="console.log('[ANNULER] Click detecte');const e=event||window.event;if(e){e.preventDefault();e.stopPropagation();e.stopImmediatePropagation();}if(typeof window.fermerModalAuth==='function'){window.fermerModalAuth();}else if(typeof closeAuthModal==='function'){closeAuthModal();}else{const b=document.getElementById('publish-modal-backdrop');const m=document.getElementById('publish-modal-inner');if(b){b.style.display='none';b.style.visibility='hidden';b.style.opacity='0';}if(m){m.innerHTML='';m.style.display='none';}}return false;" style="width:100%;padding:12px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:transparent;color:var(--ui-text-muted);font-weight:600;font-size:14px;cursor:pointer;transition:all 0.3s;z-index:10001;position:relative;pointer-events:auto;" onmouseover="this.style.borderColor='rgba(255,255,255,0.3)';this.style.color='var(--ui-text-main)';" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)';this.style.color='var(--ui-text-muted)';">
        Annuler
      </button>
    </div>
  `;
  
  // Utiliser les éléments finaux trouvés/créés
  const modalInner = finalModal;
  const modalBackdrop = finalBackdrop;
  
  if (!modalInner || !modalBackdrop) {
    console.error('[AUTH] ❌❌❌ ERREUR: Elements modal non trouves apres creation HTML');
    console.error('[AUTH] modalInner:', modalInner);
    console.error('[AUTH] modalBackdrop:', modalBackdrop);
    alert('Erreur : Impossible d\'afficher le modal de connexion. Veuillez rafraîchir la page.');
    return;
  }
  
  // ⚠️⚠️⚠️ CRITIQUE : Supprimer l'onclick du backdrop qui pourrait fermer le modal immédiatement
  modalBackdrop.removeAttribute('onclick');
  console.log('[AUTH] ✅ Attribut onclick supprimé du backdrop');
  
  console.log('[AUTH] ✅✅✅ Injection HTML dans le modal...');
  modalInner.innerHTML = html;
  console.log('[AUTH] ✅ HTML injecte, longueur:', html.length);
  
  // Vérifier que modalBackdrop existe toujours après l'injection
  const verifyBackdrop = document.getElementById("publish-modal-backdrop");
  if (!verifyBackdrop) {
    console.error('[AUTH] ❌❌❌ ERREUR: modalBackdrop est null apres injection HTML !');
    alert('Erreur : Le modal a disparu après injection. Veuillez rafraîchir la page.');
    return;
  }
  console.log('[AUTH] ✅ modalBackdrop existe toujours');
  
  // ⚠️⚠️⚠️ CRITIQUE : FORCER l'affichage IMMÉDIATEMENT APRÈS l'injection HTML - AVANT TOUT LE RESTE
  // ⚠️⚠️⚠️ VERSION 2026-01-17 19:00 - CODE DE FORCAGE MODAL
  console.log('[AUTH] ⚠️⚠️⚠️⚠️⚠️⚠️ FORCAGE IMMÉDIAT DU BACKDROP APRÈS INJECTION HTML - DÉBUT ⚠️⚠️⚠️⚠️⚠️⚠️');
  console.log('[AUTH] ⚠️⚠️⚠️ SI VOUS VOYEZ CE MESSAGE, LA NOUVELLE VERSION EST CHARGÉE ⚠️⚠️⚠️');
  console.log('[AUTH] ⚠️⚠️⚠️ modalBackdrop:', !!modalBackdrop, 'modalInner:', !!modalInner);
  
  // FORCER IMMÉDIATEMENT SANS TRY-CATCH POUR VOIR LES ERREURS
  console.log('[AUTH] ⚠️⚠️⚠️ Application setAttribute au backdrop...');
  // Marquer le backdrop comme modal d'authentification pour le CSS
  modalBackdrop.setAttribute('data-auth-modal', 'true');
  modalBackdrop.setAttribute('style', 'display:flex!important;visibility:visible!important;opacity:1!important;z-index:99999!important;position:fixed!important;top:0!important;left:0!important;width:100%!important;height:100%!important;background:rgba(0,0,0,0.8)!important;align-items:center!important;justify-content:center!important;pointer-events:auto!important;padding-top:40px!important;padding-bottom:40px!important;box-sizing:border-box!important;');
  console.log('[AUTH] ✅✅✅ BACKDROP setAttribute APPLIQUÉ');
  
  // Réutiliser publishModal déjà déclaré plus haut (ligne 1409)
  if (publishModal) {
    publishModal.setAttribute('style', 'display:block!important;visibility:visible!important;opacity:1!important;position:relative!important;max-width:500px!important;width:90%!important;max-height:90vh!important;overflow-y:auto!important;');
    console.log('[AUTH] ✅✅✅ PUBLISH-MODAL setAttribute APPLIQUÉ');
  }
  
  modalInner.setAttribute('style', 'display:block!important;visibility:visible!important;opacity:1!important;');
  console.log('[AUTH] ✅✅✅ MODAL-INNER setAttribute APPLIQUÉ');
  
  const computedBackdropCheck = window.getComputedStyle(modalBackdrop);
  console.log('[AUTH] ✅✅✅ BACKDROP FORCÉ - display:', computedBackdropCheck.display, 'visibility:', computedBackdropCheck.visibility, 'opacity:', computedBackdropCheck.opacity, 'z-index:', computedBackdropCheck.zIndex);
  console.log('[AUTH] ⚠️⚠️⚠️⚠️⚠️⚠️ FORCAGE IMMÉDIAT DU BACKDROP APRÈS INJECTION HTML - FIN ⚠️⚠️⚠️⚠️⚠️⚠️');
  
  // ⚠️⚠️⚠️ FORCER ENCORE UNE FOIS AVEC requestAnimationFrame ET setTimeout pour s'assurer que le navigateur a rendu
  requestAnimationFrame(() => {
    setTimeout(() => {
      const backdropCheck = document.getElementById('publish-modal-backdrop');
      const modalCheck = document.getElementById('publish-modal');
      const innerCheck = document.getElementById('publish-modal-inner');
      
      if (backdropCheck) {
        // Supprimer l'onclick qui pourrait fermer le modal
        backdropCheck.removeAttribute('onclick');
        
        const computed = window.getComputedStyle(backdropCheck);
        console.log('[AUTH] 🔍 VÉRIFICATION RAF - backdrop display:', computed.display, 'visibility:', computed.visibility, 'opacity:', computed.opacity);
        
        if (computed.display === 'none' || computed.visibility === 'hidden' || parseFloat(computed.opacity) < 0.1) {
          console.log('[AUTH] ⚠️⚠️⚠️ BACKDROP TOUJOURS INVISIBLE APRÈS RAF - FORCAGE FINAL AVEC cssText');
          // Utiliser style.cssText pour remplacer complètement le style
          backdropCheck.style.cssText = 'display:flex!important;visibility:visible!important;opacity:1!important;z-index:99999!important;position:fixed!important;top:0!important;left:0!important;width:100%!important;height:100%!important;background:rgba(0,0,0,0.8)!important;align-items:center!important;justify-content:center!important;pointer-events:auto!important;padding-top:40px!important;padding-bottom:40px!important;box-sizing:border-box!important;';
          // Aussi forcer avec setAttribute
          backdropCheck.setAttribute('style', 'display:flex!important;visibility:visible!important;opacity:1!important;z-index:99999!important;position:fixed!important;top:0!important;left:0!important;width:100%!important;height:100%!important;background:rgba(0,0,0,0.8)!important;align-items:center!important;justify-content:center!important;pointer-events:auto!important;padding-top:40px!important;padding-bottom:40px!important;box-sizing:border-box!important;');
        }
      }
      
      if (modalCheck) {
        modalCheck.style.cssText = 'display:block!important;visibility:visible!important;opacity:1!important;position:relative!important;max-width:500px!important;width:90%!important;max-height:90vh!important;overflow-y:auto!important;';
        modalCheck.setAttribute('style', 'display:block!important;visibility:visible!important;opacity:1!important;position:relative!important;max-width:500px!important;width:90%!important;max-height:90vh!important;overflow-y:auto!important;');
      }
      
      if (innerCheck) {
        innerCheck.style.cssText = 'display:block!important;visibility:visible!important;opacity:1!important;';
        innerCheck.setAttribute('style', 'display:block!important;visibility:visible!important;opacity:1!important;');
      }
      
      // Vérification finale
      if (backdropCheck) {
        const finalComputed = window.getComputedStyle(backdropCheck);
        console.log('[AUTH] ✅✅✅ VÉRIFICATION FINALE RAF - backdrop display:', finalComputed.display, 'visibility:', finalComputed.visibility, 'opacity:', finalComputed.opacity);
      }
    }, 50);
  });
  
  // SOLUTION ULTRA-ROBUSTE : Créer une fonction nommée pour pouvoir la supprimer si elle existe déjà
  // Supprimer l'ancien event listener si il existe
  if (window._authModalCancelHandler) {
    console.log('[AUTH] Suppression de l\'ancien event listener...');
    try {
      modalBackdrop.removeEventListener('click', window._authModalCancelHandler, true);
      console.log('[AUTH] ✅ Ancien event listener supprime');
    } catch (err) {
      console.warn('[AUTH] ⚠️ Erreur lors de la suppression de l\'ancien listener:', err);
    }
  }
  
  // Créer la fonction de gestion des clics sur les boutons Annuler
  console.log('[AUTH] Creation de la fonction _authModalCancelHandler...');
  window._authModalCancelHandler = function(e) {
    const target = e.target;
    
    const isCancelButton = target.id === 'auth-cancel-btn' || 
                          target.id === 'auth-cancel-btn-pro' ||
                          target.closest('#auth-cancel-btn') ||
                          target.closest('#auth-cancel-btn-pro') ||
                          (target.tagName === 'BUTTON' && target.textContent?.trim() === 'Annuler') ||
                          (target.closest('button') && target.closest('button').textContent?.trim() === 'Annuler');
    
    if (isCancelButton) {
      console.log('[AUTH] 🔥🔥🔥 BOUTON ANNULER CLIQUE (via event delegation) - FERMETURE IMMEDIATE');
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      e.cancelBubble = true;
      
      // Fermer IMMEDIATEMENT sans passer par aucune autre fonction
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
      
      console.log('[AUTH] ✅ Modal ferme COMPLETEMENT (via event delegation)');
      return false;
    }
    
    // Si on clique directement sur le backdrop (pas sur ses enfants), fermer le modal d'auth
    // ⚠️⚠️⚠️ IMPORTANT : Ignorer TOUS les éléments du formulaire d'inscription
    const isClickOnChild = target.closest('button') || 
                          target.closest('input') || 
                          target.closest('a') || 
                          target.closest('#authModal') || 
                          target.closest('#publish-modal-inner') ||
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
                          target.id === 'verify-skip-btn' || // ⚠️ CRITIQUE : Ignorer le bouton "Continuer sans vérifier"
                          target.classList?.contains('pro-register-photo-upload') ||
                          target.classList?.contains('pro-register-photo-input') ||
                          target.classList?.contains('pro-register-password-toggle') ||
                          target.classList?.contains('pro-register-password-container') ||
                          target.classList?.contains('verify-skip-btn'); // ⚠️ CRITIQUE : Ignorer le bouton "Continuer sans vérifier"
    
    if (target === modalBackdrop && !isClickOnChild) {
      console.log('[AUTH] Backdrop click detecte (direct sur backdrop) - Fermeture via closeAuthModal');
      closeAuthModal();
    } else if (isClickOnChild) {
      console.log('[AUTH] Clic sur élément du formulaire - IGNORÉ (pas de fermeture)');
    }
  };
  
  // ⚠️⚠️⚠️ CRITIQUE : FORCER l'affichage du backdrop et du modal IMMÉDIATEMENT AVANT l'attachement de l'event listener
  // ⚠️⚠️⚠️ EXÉCUTION IMMÉDIATE DU CODE DE FORCAGE AVANT LE LOG PROBLÉMATIQUE
  console.log('[AUTH] ⚠️⚠️⚠️ DÉBUT FORCAGE AFFICHAGE MODAL - IMMÉDIAT (AVANT EVENT LISTENER)');
  console.log('[AUTH] ⚠️⚠️⚠️ EXÉCUTION DU CODE DE FORCAGE MAINTENANT');
  console.log('[AUTH] ⚠️⚠️⚠️ modalBackdrop existe:', !!modalBackdrop, 'modalInner existe:', !!modalInner);
  
  // FORCER IMMÉDIATEMENT AVANT TOUT LE RESTE - UTILISER setAttribute POUR FORCER
  console.log('[AUTH] ⚠️⚠️⚠️ FORCAGE IMMÉDIAT DU BACKDROP AVEC setAttribute');
  if (modalBackdrop) {
    modalBackdrop.setAttribute('style', 'display:flex!important;visibility:visible!important;opacity:1!important;z-index:99999!important;position:fixed!important;top:0!important;left:0!important;width:100%!important;height:100%!important;background:rgba(0,0,0,0.8)!important;align-items:center!important;justify-content:center!important;pointer-events:auto!important;padding-top:40px!important;padding-bottom:40px!important;box-sizing:border-box!important;');
    console.log('[AUTH] ✅✅✅ BACKDROP FORCÉ AVEC setAttribute');
  } else {
    console.error('[AUTH] ❌❌❌ modalBackdrop est NULL !');
  }
  
  const publishModalCheck = document.getElementById('publish-modal');
  console.log('[AUTH] ⚠️⚠️⚠️ publishModal trouvé:', !!publishModalCheck);
  if (publishModalCheck) {
    publishModalCheck.setAttribute('style', 'display:block!important;visibility:visible!important;opacity:1!important;position:relative!important;max-width:500px!important;width:90%!important;max-height:90vh!important;overflow-y:auto!important;');
    console.log('[AUTH] ✅✅✅ PUBLISH-MODAL FORCÉ AVEC setAttribute');
  } else {
    console.error('[AUTH] ❌❌❌ publishModal non trouvé !');
  }
  
  if (modalInner) {
    modalInner.setAttribute('style', 'display:block!important;visibility:visible!important;opacity:1!important;');
    console.log('[AUTH] ✅✅✅ MODAL-INNER FORCÉ AVEC setAttribute');
  } else {
    console.error('[AUTH] ❌❌❌ modalInner est NULL !');
  }
  
  // VÉRIFICATION IMMÉDIATE APRÈS FORCAGE
  const computedBackdropCheckFinal = modalBackdrop ? window.getComputedStyle(modalBackdrop) : null;
  console.log('[AUTH] ⚠️⚠️⚠️ VÉRIFICATION IMMÉDIATE - backdrop display:', computedBackdropCheckFinal ? computedBackdropCheckFinal.display : 'NULL', 'visibility:', computedBackdropCheckFinal ? computedBackdropCheckFinal.visibility : 'NULL', 'opacity:', computedBackdropCheckFinal ? computedBackdropCheckFinal.opacity : 'NULL');
  console.log('[AUTH] ✅✅✅ FIN FORCAGE AFFICHAGE MODAL - Code exécuté sans erreur');
  
  // Attacher l'event listener avec useCapture=true pour s'exécuter AVANT tout le monde
  console.log('[AUTH] Attachement de l\'event listener...');
  try {
    modalBackdrop.addEventListener('click', window._authModalCancelHandler, true);
    console.log('[AUTH] ✅ Event delegation attachee avec useCapture=true');
  } catch (err) {
    console.error('[AUTH] ❌ ERREUR lors de l\'attachement de l\'event listener:', err);
  }
  
  // ⚠️⚠️⚠️ CRITIQUE : FORCER l'affichage du backdrop et du modal IMMÉDIATEMENT APRÈS l'attachement
  console.log('[AUTH] ⚠️⚠️⚠️ DÉBUT FORCAGE AFFICHAGE MODAL - IMMÉDIAT');
  console.log('[AUTH] ⚠️⚠️⚠️ EXÉCUTION DU CODE DE FORCAGE MAINTENANT');
  console.log('[AUTH] ⚠️⚠️⚠️ modalBackdrop existe:', !!modalBackdrop, 'modalInner existe:', !!modalInner);
  
  // FORCER IMMÉDIATEMENT AVANT TOUT LE RESTE - UTILISER setAttribute POUR FORCER
  console.log('[AUTH] ⚠️⚠️⚠️ FORCAGE IMMÉDIAT DU BACKDROP AVEC setAttribute');
  if (modalBackdrop) {
    modalBackdrop.setAttribute('style', 'display:flex!important;visibility:visible!important;opacity:1!important;z-index:99999!important;position:fixed!important;top:0!important;left:0!important;width:100%!important;height:100%!important;background:rgba(0,0,0,0.8)!important;align-items:center!important;justify-content:center!important;pointer-events:auto!important;padding-top:40px!important;padding-bottom:40px!important;box-sizing:border-box!important;');
    console.log('[AUTH] ✅✅✅ BACKDROP FORCÉ AVEC setAttribute');
  } else {
    console.error('[AUTH] ❌❌❌ modalBackdrop est NULL !');
  }
  
  // Réutiliser publishModal déjà déclaré plus haut (ligne 1409)
  const publishModalRef = document.getElementById('publish-modal');
  console.log('[AUTH] ⚠️⚠️⚠️ publishModal trouvé:', !!publishModalRef);
  if (publishModalRef) {
    publishModalRef.setAttribute('style', 'display:block!important;visibility:visible!important;opacity:1!important;position:relative!important;max-width:500px!important;width:90%!important;max-height:90vh!important;overflow-y:auto!important;');
    console.log('[AUTH] ✅✅✅ PUBLISH-MODAL FORCÉ AVEC setAttribute');
  } else {
    console.error('[AUTH] ❌❌❌ publishModal non trouvé !');
  }
  
  if (modalInner) {
    modalInner.setAttribute('style', 'display:block!important;visibility:visible!important;opacity:1!important;');
    console.log('[AUTH] ✅✅✅ MODAL-INNER FORCÉ AVEC setAttribute');
  } else {
    console.error('[AUTH] ❌❌❌ modalInner est NULL !');
  }
  
  // VÉRIFICATION IMMÉDIATE APRÈS FORCAGE (réutiliser computedBackdropCheck déjà déclaré plus haut ligne 1705)
  const computedBackdropCheck2 = modalBackdrop ? window.getComputedStyle(modalBackdrop) : null;
  console.log('[AUTH] ⚠️⚠️⚠️ VÉRIFICATION IMMÉDIATE - backdrop display:', computedBackdropCheck2 ? computedBackdropCheck2.display : 'NULL', 'visibility:', computedBackdropCheck2 ? computedBackdropCheck2.visibility : 'NULL', 'opacity:', computedBackdropCheck2 ? computedBackdropCheck2.opacity : 'NULL');
  
  try {
    // ⚠️⚠️⚠️ CRITIQUE : FORCER l'affichage du backdrop et du modal IMMÉDIATEMENT
    // Le backdrop doit être en flex avec align-items:center et justify-content:center pour centrer le modal
    console.log('[AUTH] ⚠️⚠️⚠️ Application des styles au backdrop...');
    // Marquer comme modal d'authentification pour activer le CSS de centrage
    modalBackdrop.setAttribute('data-auth-modal', 'true');
    modalBackdrop.style.display = "flex";
  modalBackdrop.style.visibility = "visible";
  modalBackdrop.style.opacity = "1";
  modalBackdrop.style.zIndex = "9999";
  modalBackdrop.style.position = "fixed";
  modalBackdrop.style.top = "0";
  modalBackdrop.style.left = "0";
  modalBackdrop.style.width = "100%";
  modalBackdrop.style.height = "100%";
  modalBackdrop.style.background = "rgba(0,0,0,0.8)";
  modalBackdrop.style.alignItems = "center";
  modalBackdrop.style.justifyContent = "center";
  modalBackdrop.style.paddingTop = "40px";
  modalBackdrop.style.paddingBottom = "40px";
  modalBackdrop.style.boxSizing = "border-box";
  modalBackdrop.style.setProperty('display', 'flex', 'important');
  console.log('[AUTH] ✅✅✅ Styles appliqués au backdrop');
  
  // Vérifier que #publish-modal existe et est visible (c'est le conteneur entre backdrop et inner)
  // Réutiliser publishModal déjà déclaré plus haut (ligne 1409) - récupérer à nouveau au cas où
  const publishModalCurrent = document.getElementById('publish-modal');
  if (publishModalCurrent) {
    publishModalCurrent.style.display = "block";
    publishModalCurrent.style.visibility = "visible";
    publishModalCurrent.style.opacity = "1";
    publishModalCurrent.style.position = "relative";
    publishModalCurrent.style.top = "auto";
    publishModalCurrent.style.right = "auto";
    publishModalCurrent.style.maxWidth = "500px";
    publishModalCurrent.style.width = "90%";
    publishModalCurrent.style.maxHeight = "90vh";
    publishModalCurrent.style.overflowY = "auto";
    publishModalCurrent.style.setProperty('display', 'block', 'important');
  } else {
    console.error('[AUTH] ❌ ERREUR: #publish-modal non trouvé !');
  }
  
  modalInner.style.display = "block";
  modalInner.style.visibility = "visible";
  modalInner.style.opacity = "1";
  modalInner.style.zIndex = "10000";
  modalInner.style.setProperty('display', 'block', 'important');
  
  // ⚠️⚠️⚠️ LOG IMMÉDIAT pour vérifier les styles appliqués
  const computedBackdropNow = window.getComputedStyle(modalBackdrop);
  const computedModalNow = publishModal ? window.getComputedStyle(publishModal) : null;
  const computedInnerNow = window.getComputedStyle(modalInner);
  
  console.log('[AUTH] ⚠️⚠️⚠️ STYLES APPLIQUÉS IMMÉDIATEMENT:', {
    backdropDisplay: modalBackdrop.style.display,
    backdropVisibility: modalBackdrop.style.visibility,
    backdropOpacity: modalBackdrop.style.opacity,
    backdropZIndex: modalBackdrop.style.zIndex,
    backdropComputedDisplay: computedBackdropNow.display,
    backdropComputedVisibility: computedBackdropNow.visibility,
    backdropComputedOpacity: computedBackdropNow.opacity,
    backdropComputedZIndex: computedBackdropNow.zIndex,
    backdropComputedPosition: computedBackdropNow.position,
    publishModalExists: !!publishModal,
    publishModalDisplay: publishModal ? publishModal.style.display : 'N/A',
    publishModalComputedDisplay: publishModal ? computedModalNow.display : 'N/A',
    innerDisplay: modalInner.style.display,
    innerComputedDisplay: computedInnerNow.display,
    backdropRect: modalBackdrop.getBoundingClientRect()
  });
  
  // ⚠️⚠️⚠️ FORCER IMMÉDIATEMENT si le backdrop n'est pas visible
  if (computedBackdropNow.display === 'none' || computedBackdropNow.visibility === 'hidden' || computedBackdropNow.opacity === '0') {
    console.error('[AUTH] ❌❌❌ BACKDROP INVISIBLE IMMÉDIATEMENT - FORCAGE ULTIME');
    // Marquer comme modal d'authentification pour activer le CSS de centrage
    modalBackdrop.setAttribute('data-auth-modal', 'true');
    // Supprimer l'onclick qui pourrait fermer le modal
    modalBackdrop.removeAttribute('onclick');
    // Forcer avec style.cssText ET setAttribute pour être sûr
    modalBackdrop.style.cssText = 'display:flex!important;visibility:visible!important;opacity:1!important;z-index:99999!important;position:fixed!important;top:0!important;left:0!important;width:100%!important;height:100%!important;background:rgba(0,0,0,0.8)!important;align-items:center!important;justify-content:center!important;pointer-events:auto!important;padding-top:40px!important;padding-bottom:40px!important;box-sizing:border-box!important;';
    modalBackdrop.setAttribute('style', 'display:flex!important;visibility:visible!important;opacity:1!important;z-index:99999!important;position:fixed!important;top:0!important;left:0!important;width:100%!important;height:100%!important;background:rgba(0,0,0,0.8)!important;align-items:center!important;justify-content:center!important;pointer-events:auto!important;padding-top:40px!important;padding-bottom:40px!important;box-sizing:border-box!important;');
    
    if (publishModal) {
      publishModal.setAttribute('style', 'display:block!important;visibility:visible!important;opacity:1!important;position:relative!important;max-width:500px!important;width:90%!important;max-height:90vh!important;overflow-y:auto!important;');
    }
    
    modalInner.setAttribute('style', 'display:block!important;visibility:visible!important;opacity:1!important;');
    
    // Forcer à nouveau après un court délai avec requestAnimationFrame
    requestAnimationFrame(() => {
      setTimeout(() => {
        modalBackdrop.style.cssText = 'display:flex!important;visibility:visible!important;opacity:1!important;z-index:99999!important;position:fixed!important;top:0!important;left:0!important;width:100%!important;height:100%!important;background:rgba(0,0,0,0.8)!important;align-items:center!important;justify-content:center!important;pointer-events:auto!important;padding-top:40px!important;padding-bottom:40px!important;box-sizing:border-box!important;';
        modalBackdrop.setAttribute('data-auth-modal', 'true');
        modalBackdrop.removeAttribute('onclick');
        const computedBackdropAfter = window.getComputedStyle(modalBackdrop);
        console.log('[AUTH] ✅✅✅ APRÈS RAF+SETTIMEOUT - backdrop display:', computedBackdropAfter.display, 'visibility:', computedBackdropAfter.visibility, 'opacity:', computedBackdropAfter.opacity, 'paddingTop:', computedBackdropAfter.paddingTop);
      }, 50);
    });
    
    // Vérifier à nouveau après forçage immédiat
    const computedBackdropAfter = window.getComputedStyle(modalBackdrop);
    console.log('[AUTH] ✅✅✅ APRÈS FORCAGE IMMÉDIAT - backdrop display:', computedBackdropAfter.display, 'visibility:', computedBackdropAfter.visibility, 'opacity:', computedBackdropAfter.opacity, 'paddingTop:', computedBackdropAfter.paddingTop);
  }
  
  console.log('[AUTH] ✅✅✅ FIN FORCAGE AFFICHAGE MODAL - Code exécuté sans erreur');
  } catch (err) {
    console.error('[AUTH] ❌❌❌ ERREUR lors du forçage de l\'affichage:', err);
    // Essayer quand même de forcer l'affichage avec setAttribute
    try {
      // Marquer comme modal d'authentification pour activer le CSS de centrage
      modalBackdrop.setAttribute('data-auth-modal', 'true');
      modalBackdrop.setAttribute('style', 'display:flex!important;visibility:visible!important;opacity:1!important;z-index:99999!important;position:fixed!important;top:0!important;left:0!important;width:100%!important;height:100%!important;background:rgba(0,0,0,0.8)!important;align-items:center!important;justify-content:center!important;pointer-events:auto!important;padding-top:40px!important;padding-bottom:40px!important;box-sizing:border-box!important;');
      console.log('[AUTH] ✅✅✅ Forçage avec setAttribute réussi');
    } catch (err2) {
      console.error('[AUTH] ❌❌❌ ERREUR même avec setAttribute:', err2);
    }
  }
  
  // ⚠️⚠️⚠️ DOUBLE VÉRIFICATION : Vérifier que tout est bien visible après un court délai
  setTimeout(() => {
    console.log('[AUTH] ⚠️⚠️⚠️ VÉRIFICATION FINALE DÉMARRÉE');
    const computedBackdrop = window.getComputedStyle(modalBackdrop);
    const computedModal = publishModal ? window.getComputedStyle(publishModal) : null;
    const computedInner = window.getComputedStyle(modalInner);
    
    console.log('[AUTH] ✅✅✅ VÉRIFICATION FINALE - Styles calculés:', {
      backdropDisplay: computedBackdrop.display,
      backdropVisibility: computedBackdrop.visibility,
      backdropOpacity: computedBackdrop.opacity,
      backdropZIndex: computedBackdrop.zIndex,
      backdropPosition: computedBackdrop.position,
      backdropTop: computedBackdrop.top,
      backdropLeft: computedBackdrop.left,
      backdropWidth: computedBackdrop.width,
      backdropHeight: computedBackdrop.height,
      modalDisplay: computedModal ? computedModal.display : 'N/A',
      modalVisibility: computedModal ? computedModal.visibility : 'N/A',
      innerDisplay: computedInner.display,
      innerVisibility: computedInner.visibility,
      innerOpacity: computedInner.opacity,
      backdropRect: modalBackdrop.getBoundingClientRect(),
      modalRect: publishModal ? publishModal.getBoundingClientRect() : null,
      innerRect: modalInner.getBoundingClientRect()
    });
    
    // Si le backdrop n'est pas visible, forcer encore plus
    if (computedBackdrop.display === 'none' || computedBackdrop.visibility === 'hidden' || computedBackdrop.opacity === '0') {
      console.error('[AUTH] ❌❌❌ BACKDROP TOUJOURS INVISIBLE - FORCAGE ULTIME');
      // Marquer comme modal d'authentification pour activer le CSS de centrage
      modalBackdrop.setAttribute('data-auth-modal', 'true');
      modalBackdrop.setAttribute('style', 'display:flex!important;visibility:visible!important;opacity:1!important;z-index:99999!important;position:fixed!important;top:0!important;left:0!important;width:100%!important;height:100%!important;background:rgba(0,0,0,0.8)!important;align-items:center!important;justify-content:center!important;pointer-events:auto!important;padding-top:40px!important;padding-bottom:40px!important;box-sizing:border-box!important;');
      
      if (publishModal) {
        publishModal.setAttribute('style', 'display:block!important;visibility:visible!important;opacity:1!important;position:relative!important;max-width:500px!important;width:90%!important;max-height:90vh!important;overflow-y:auto!important;');
      }
      
      modalInner.setAttribute('style', 'display:block!important;visibility:visible!important;opacity:1!important;');
      
      // Afficher une alerte pour confirmer que le modal devrait être visible
      console.log('[AUTH] ⚠️⚠️⚠️ MODAL FORCÉ VISIBLE - Vérifiez visuellement si le modal apparaît maintenant');
    } else {
      console.log('[AUTH] ✅✅✅ BACKDROP VISIBLE - Le modal devrait être affiché');
    }
  }, 100);
  
  console.log('[AUTH] Modal affiche, HTML injecte, event delegation configuree sur backdrop', {
    backdropDisplay: modalBackdrop.style.display,
    backdropVisibility: modalBackdrop.style.visibility,
    backdropOpacity: modalBackdrop.style.opacity,
    backdropZIndex: modalBackdrop.style.zIndex,
    backdropAlignItems: modalBackdrop.style.alignItems,
    backdropJustifyContent: modalBackdrop.style.justifyContent,
    publishModalExists: !!publishModal,
    publishModalDisplay: publishModal ? publishModal.style.display : 'N/A',
    modalDisplay: modalInner.style.display,
    modalVisibility: modalInner.style.visibility,
    modalOpacity: modalInner.style.opacity
  });
  
  // Attacher les event listeners après injection HTML
  setTimeout(() => {
    // ⚠️⚠️⚠️ CRITIQUE : S'assurer que le bouton Google fonctionne
    const googleBtn = document.querySelector('button[onclick*="startGoogleLogin"]');
    if (googleBtn) {
      console.log('[AUTH] ✅ Bouton Google trouvé, vérification de startGoogleLogin...');
      // Supprimer l'onclick inline et utiliser addEventListener pour plus de contrôle
      googleBtn.removeAttribute('onclick');
      googleBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('[AUTH] ✅✅✅ Bouton Google cliqué');
        if (typeof window.startGoogleLogin === 'function') {
          console.log('[AUTH] Appel de window.startGoogleLogin');
          window.startGoogleLogin();
        } else if (typeof startGoogleLogin === 'function') {
          console.log('[AUTH] Appel de startGoogleLogin');
          startGoogleLogin();
        } else {
          console.error('[AUTH] ❌ startGoogleLogin non disponible');
          if (typeof showNotification === 'function') {
            showNotification('⚠️ Erreur : fonction Google non disponible', 'error');
          }
        }
      }, { capture: true });
      console.log('[AUTH] ✅ Event listener attaché au bouton Google');
    } else {
      console.warn('[AUTH] ⚠️ Bouton Google non trouvé');
    }
    
    const switchBtn = document.getElementById('auth-switch-btn');
    if (switchBtn) {
      const targetMode = switchBtn.getAttribute('data-mode');
      console.log('[AUTH] Bouton switch trouve, targetMode:', targetMode);
      
      switchBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const mode = switchBtn.getAttribute('data-mode');
        console.log('[AUTH] CLICK sur bouton switch - mode:', mode);
        
        if (typeof window.openAuthModal === 'function') {
          window.openAuthModal(mode);
        } else if (mode === 'register' && typeof window.openRegisterModal === 'function') {
          window.openRegisterModal();
        } else if (mode === 'login' && typeof window.openLoginModal === 'function') {
          window.openLoginModal();
        }
      }, { once: false });
      
      console.log('[AUTH] Event listener attache au bouton switch avec mode:', targetMode);
    }
  }, 50);
  
  // Attacher l'event listener au bouton principal (Créer mon compte / Se connecter)
  setTimeout(() => {
    const primaryBtn = document.getElementById('auth-primary-btn');
    if (primaryBtn) {
      const action = primaryBtn.getAttribute('data-action');
      primaryBtn.addEventListener('click', function() {
        console.log('[AUTH] CLICK primary button - action:', action);
        if (action === 'performRegister()') {
          if (typeof performRegister === 'function') {
            performRegister();
          } else if (typeof window.performRegister === 'function') {
            window.performRegister();
          } else {
            console.error('[AUTH] performRegister non disponible');
          }
        } else if (action === 'performLogin()') {
          if (typeof performLogin === 'function') {
            performLogin();
          } else if (typeof window.performLogin === 'function') {
            window.performLogin();
          } else {
            console.error('[AUTH] performLogin non disponible');
          }
        }
      });
      console.log('[AUTH] Event listener attache au bouton primary');
    }
  }, 50);
  
  // Hack pour éviter l'autofill au chargement : readonly puis focus au clic
  setTimeout(() => {
    const firstInput = document.getElementById(isRegister ? "register-email" : "login-email");
    if (firstInput) {
      firstInput.setAttribute('readonly', 'readonly');
      firstInput.addEventListener('click', function removeReadonly() {
        firstInput.removeAttribute('readonly');
        firstInput.focus();
        firstInput.removeEventListener('click', removeReadonly);
      }, { once: true });
      firstInput.addEventListener('focus', function removeReadonly() {
        firstInput.removeAttribute('readonly');
        firstInput.removeEventListener('focus', removeReadonly);
      }, { once: true });
      console.log('[AUTH] Champ email configure avec hack readonly pour eviter autofill');
    }
    
    // Attacher les event listeners pour le formulaire d'inscription
    if (isRegister) {
      const photoUploadZone = document.getElementById('register-photo-upload-zone');
      const photoInput = document.getElementById('register-photo-input');
      if (photoUploadZone && photoInput) {
        photoUploadZone.addEventListener('click', () => photoInput.click());
      }
      
      const addressInput = document.getElementById('register-address-input');
      if (addressInput && typeof setupRegisterAddressAutocomplete === 'function') {
        setupRegisterAddressAutocomplete(addressInput);
      }
    }
  }, 100);
}

// ⚠️⚠️⚠️ NOUVEAU FLUX LEADER MONDIAL : Vérifier si l'email existe avant de proposer inscription ou validation
async function checkEmailAndProceed(email) {
  console.log('[AUTH] 🔍 Vérification de l\'email:', email);
  
  if (!email || !email.includes('@')) {
    if (typeof showNotification === 'function') {
      showNotification('⚠️ Veuillez entrer une adresse email valide', 'warning');
    }
    return;
  }
  
  // ⚠️⚠️⚠️ SAUVEGARDER l'email dans sessionStorage pour restauration après F5
  try {
    sessionStorage.setItem('lastLoginEmail', email.trim());
    console.log('[AUTH] ✅ Email sauvegardé dans sessionStorage:', email);
  } catch (e) {
    console.warn('[AUTH] ⚠️ Impossible de sauvegarder l\'email:', e);
  }
  
  try {
    // Vérifier si l'email existe via l'API
    const response = await fetch(`${API_BASE_URL}/user/exists?email=${encodeURIComponent(email)}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const data = await response.json();
    const emailExists = data.exists === true;
    
    console.log('[AUTH] ✅ Email existe:', emailExists);
    
    if (emailExists) {
      // ⚠️⚠️⚠️ COMPTE EXISTANT : Vérifier si l'utilisateur veut créer un compte ou se connecter
      const isCreatingAccount = window.location.hash.includes('register') || 
                                document.getElementById('authModal')?.dataset.mode === 'register' ||
                                sessionStorage.getItem('wantToRegister') === 'true';
      
      if (isCreatingAccount) {
        // ⚠️⚠️⚠️ L'utilisateur essaie de créer un compte avec un email existant
        console.log('[AUTH] ❌ Email existe déjà - Impossible de créer un compte avec cet email');
        
        // Afficher le formulaire d'inscription mais avec un message d'erreur
        if (typeof showProRegisterForm === 'function') {
          showProRegisterForm();
          setTimeout(() => {
            const emailInput = document.getElementById('pro-email');
            if (emailInput) {
              emailInput.value = email;
              // Afficher le message d'erreur
              const emailError = document.getElementById('pro-email-error');
              if (emailError) {
                emailError.textContent = '❌ Ce mail existe déjà. Veuillez utiliser un autre email ou vous connecter.';
                emailError.style.color = '#ef4444';
                emailError.style.display = 'block';
              }
              // Marquer le champ comme invalide
              emailInput.style.borderColor = '#ef4444';
              // Empêcher la soumission du formulaire
              emailInput.setAttribute('data-email-exists', 'true');
              emailInput.setAttribute('aria-invalid', 'true');
              // ⚠️⚠️⚠️ CRITIQUE : Ajouter un listener pour vérifier en temps réel si l'email existe
              // Supprimer les anciens listeners pour éviter les doublons
              const newEmailInput = emailInput.cloneNode(true);
              emailInput.parentNode.replaceChild(newEmailInput, emailInput);
              const emailInputFinal = newEmailInput;
              
              // Vérifier immédiatement si l'email existe déjà
              if (email && email.includes('@')) {
                (async () => {
                  try {
                    const response = await fetch(`${API_BASE_URL}/user/exists?email=${encodeURIComponent(email)}`, {
                      method: 'GET',
                      headers: { 'Content-Type': 'application/json' }
                    });
                    if (response.ok) {
                      const data = await response.json();
                      if (data.exists === true) {
                        emailInputFinal.style.borderColor = '#ef4444';
                        emailInputFinal.setAttribute('data-email-exists', 'true');
                        emailInputFinal.setAttribute('aria-invalid', 'true');
                        const emailErrorFinal = document.getElementById('pro-email-error');
                        if (emailErrorFinal) {
                          emailErrorFinal.textContent = '❌ Ce mail existe déjà. Veuillez utiliser un autre email ou vous connecter.';
                          emailErrorFinal.style.color = '#ef4444';
                          emailErrorFinal.style.display = 'block';
                        }
                      }
                    }
                  } catch (e) {
                    console.error('[AUTH] Erreur vérification email:', e);
                  }
                })();
              }
              
              // Ajouter un listener pour vérifier en temps réel lors de la saisie
              emailInputFinal.addEventListener('input', async function checkEmailExists() {
                const currentEmail = this.value.trim();
                if (currentEmail && currentEmail.includes('@')) {
                  try {
                    const response = await fetch(`${API_BASE_URL}/user/exists?email=${encodeURIComponent(currentEmail)}`, {
                      method: 'GET',
                      headers: { 'Content-Type': 'application/json' }
                    });
                    if (response.ok) {
                      const data = await response.json();
                      const emailErrorFinal = document.getElementById('pro-email-error');
                      if (data.exists === true) {
                        this.style.borderColor = '#ef4444';
                        this.setAttribute('data-email-exists', 'true');
                        this.setAttribute('aria-invalid', 'true');
                        if (emailErrorFinal) {
                          emailErrorFinal.textContent = '❌ Ce mail existe déjà. Veuillez utiliser un autre email ou vous connecter.';
                          emailErrorFinal.style.color = '#ef4444';
                          emailErrorFinal.style.display = 'block';
                        }
                      } else {
                        this.style.borderColor = '';
                        this.removeAttribute('data-email-exists');
                        this.removeAttribute('aria-invalid');
                        if (emailErrorFinal) {
                          emailErrorFinal.textContent = '';
                          emailErrorFinal.style.display = 'none';
                        }
                      }
                    }
                  } catch (e) {
                    console.error('[AUTH] Erreur vérification email:', e);
                  }
                }
              });
              
              emailInputFinal.value = email;
              emailInputFinal.dispatchEvent(new Event('input', { bubbles: true }));
            }
          }, 100);
        } else if (typeof window.showProRegisterForm === 'function') {
          window.showProRegisterForm();
          setTimeout(() => {
            const emailInput = document.getElementById('pro-email');
            if (emailInput) {
              emailInput.value = email;
              const emailError = document.getElementById('pro-email-error');
              if (emailError) {
                emailError.textContent = '❌ Ce mail existe déjà. Veuillez utiliser un autre email ou vous connecter.';
                emailError.style.color = '#ef4444';
                emailError.style.display = 'block';
              }
              emailInput.style.borderColor = '#ef4444';
              emailInput.setAttribute('data-email-exists', 'true');
              emailInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
          }, 100);
        }
        
        // Afficher aussi une notification
        if (typeof showNotification === 'function') {
          showNotification('❌ Ce mail existe déjà. Veuillez utiliser un autre email ou vous connecter.', 'error');
        }
        return; // Ne pas continuer
      } else {
        // ⚠️⚠️⚠️ COMPTE EXISTANT : Proposer directement deux options : Google OU Email/Mot de passe
        console.log('[AUTH] ✅✅✅ Compte existant détecté - Affichage choix reconnexion');
      
      // ⚠️⚠️⚠️ SAUVEGARDER l'email dans sessionStorage pour restauration après F5
      try {
        sessionStorage.setItem('lastLoginEmail', email.toLowerCase().trim());
      } catch (e) {
        console.warn('[AUTH] ⚠️ Impossible de sauvegarder l\'email:', e);
      }
      
      // Afficher le modal avec deux options : Google OU Email/Mot de passe
      const backdrop = document.getElementById('publish-modal-backdrop');
      const modal = document.getElementById('publish-modal-inner');
      
      if (!backdrop || !modal) {
        console.error('[AUTH] Modal elements not found');
        return;
      }
      
      const html = `
        <div id="authModal" data-mode="reconnect" style="padding:40px;max-width:450px;margin:0 auto;text-align:center;position:relative;">
          <!-- Bouton X (croix) pour fermer -->
          <button onclick="closeAuthModal()" style="position:absolute;top:16px;right:16px;background:none;border:none;color:var(--ui-text-muted);font-size:24px;cursor:pointer;padding:8px;width:40px;height:40px;display:flex;align-items:center;justify-content:center;border-radius:50%;transition:all 0.2s;z-index:10;" onmouseover="this.style.background='rgba(239,68,68,0.2)';this.style.color='#ef4444';this.style.transform='scale(1.1)';" onmouseout="this.style.background='none';this.style.color='var(--ui-text-muted)';this.style.transform='scale(1)';" title="Fermer">✕</button>
          
          <!-- Logo et titre -->
          <div style="margin-bottom:32px;">
            <div style="font-size:64px;margin-bottom:16px;">🌍</div>
            <h2 style="margin:0 0 8px;font-size:28px;font-weight:800;color:#fff;background:linear-gradient(135deg,#00ffc3,#3b82f6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">Connexion</h2>
            <p style="margin:0;font-size:14px;color:var(--ui-text-muted);">Compte trouvé : ${email}</p>
          </div>
          
          <!-- Deux options de connexion -->
          <div style="display:flex;flex-direction:column;gap:12px;margin-bottom:24px;">
            <!-- Option 1 : Google (pas besoin d'info) -->
            <button id="reconnect-google-btn" onclick="if(typeof window.startGoogleLogin==='function'){window.startGoogleLogin();}" style="width:100%;padding:16px;border-radius:12px;border:2px solid rgba(0,255,195,0.3);background:linear-gradient(135deg,rgba(0,255,195,0.1),rgba(59,130,246,0.1));color:var(--ui-text-main);font-weight:600;font-size:15px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:12px;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(0,255,195,0.6)';this.style.background='linear-gradient(135deg,rgba(0,255,195,0.2),rgba(59,130,246,0.2))';" onmouseout="this.style.borderColor='rgba(0,255,195,0.3)';this.style.background='linear-gradient(135deg,rgba(0,255,195,0.1),rgba(59,130,246,0.1))';">
              <svg width="20" height="20" viewBox="0 0 24 24" style="fill:currentColor;">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              <span>Continuer avec Google</span>
            </button>
            
            <div style="display:flex;align-items:center;gap:12px;margin:16px 0;">
              <div style="flex:1;height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.1),transparent);"></div>
              <span style="font-size:12px;color:var(--ui-text-muted);font-weight:500;">ou</span>
              <div style="flex:1;height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.1),transparent);"></div>
            </div>
            
            <!-- Option 2 : Email/Mot de passe -->
            <div style="margin-bottom:16px;text-align:left;">
              <label style="display:block;font-size:13px;font-weight:600;color:var(--ui-text-main);margin-bottom:8px;">🔒 Mot de passe</label>
              <input type="password" id="reconnect-password" placeholder="Votre mot de passe" style="width:100%;padding:12px 16px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:var(--ui-text-main);font-size:14px;transition:all 0.3s;" onfocus="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(15,23,42,0.8)';" onblur="this.style.borderColor='rgba(255,255,255,0.1)';this.style.background='rgba(15,23,42,0.5)';" onkeypress="if(event.key==='Enter'){const email='${email}';const password=document.getElementById('reconnect-password').value;if(password&&typeof window.performReconnectLogin==='function'){window.performReconnectLogin(email,password);}}">
            </div>
            
            <button id="reconnect-password-btn" onclick="const email='${email}';const password=document.getElementById('reconnect-password').value.trim();if(password&&typeof window.performReconnectLogin==='function'){window.performReconnectLogin(email,password);}" style="width:100%;padding:14px;border-radius:12px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:700;font-size:15px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 8px 20px rgba(0,255,195,0.3)';" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='none';">
              Se connecter avec mot de passe
            </button>
          </div>
          
          <button onclick="closeAuthModal()" style="width:100%;padding:12px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:transparent;color:var(--ui-text-muted);font-weight:600;font-size:14px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(255,255,255,0.3)';this.style.color='var(--ui-text-main)';" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)';this.style.color='var(--ui-text-muted)';">
            Annuler
          </button>
        </div>
      `;
      
      backdrop.style.display = 'flex';
      backdrop.style.visibility = 'visible';
      backdrop.style.opacity = '1';
      backdrop.style.paddingTop = '40px';
      backdrop.style.paddingBottom = '40px';
      backdrop.style.boxSizing = 'border-box';
      modal.innerHTML = html;
      modal.style.display = 'block';
      
      // Focus sur le champ mot de passe
      setTimeout(() => {
        const passwordInput = document.getElementById('reconnect-password');
        if (passwordInput) {
          passwordInput.focus();
        }
      }, 100);
      return; // Ne pas continuer si on a affiché le modal de reconnexion
      }
    }
    
    // ⚠️⚠️⚠️ NOUVEAU COMPTE OU CRÉATION DEMANDÉE : Proposer le formulaire d'inscription complet
    console.log('[AUTH] ✅✅✅ Nouveau compte détecté ou création demandée - Affichage formulaire d\'inscription');
    
    // ⚠️⚠️⚠️ SAUVEGARDER l'email dans sessionStorage pour restauration après F5
    try {
      sessionStorage.setItem('lastLoginEmail', email.toLowerCase().trim());
    } catch (e) {
      console.warn('[AUTH] ⚠️ Impossible de sauvegarder l\'email:', e);
    }
    
    // ⚠️⚠️⚠️ CRITIQUE : Vérifier si l'email existe AVANT de pré-remplir le formulaire
    try {
      const emailCheckResponse = await fetch(`${API_BASE_URL}/user/exists?email=${encodeURIComponent(email)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (emailCheckResponse.ok) {
        const emailCheckData = await emailCheckResponse.json();
        if (emailCheckData.exists === true) {
          // Email existe déjà - NE PAS pré-remplir et afficher une erreur
          console.log('[AUTH] ❌ Email existe déjà - Ne pas pré-remplir le formulaire');
          if (typeof showNotification === 'function') {
            showNotification('❌ Ce mail existe déjà. Veuillez utiliser un autre email ou vous connecter.', 'error');
          }
          
          // Afficher le formulaire SANS pré-remplir l'email
          if (typeof showProRegisterForm === 'function') {
            showProRegisterForm();
            setTimeout(() => {
              // ⚠️⚠️⚠️ CRITIQUE : Configurer la validation en temps réel sur tous les champs
              if (typeof setupProFormValidation === 'function') {
                setupProFormValidation();
              } else if (typeof window.setupProFormValidation === 'function') {
                window.setupProFormValidation();
              }
            }, 200);
            // Ne pas pré-remplir l'email - laisser l'utilisateur en saisir un nouveau
          } else if (typeof window.showProRegisterForm === 'function') {
            window.showProRegisterForm();
            setTimeout(() => {
              // ⚠️⚠️⚠️ CRITIQUE : Configurer la validation en temps réel sur tous les champs
              if (typeof setupProFormValidation === 'function') {
                setupProFormValidation();
              } else if (typeof window.setupProFormValidation === 'function') {
                window.setupProFormValidation();
              }
            }, 200);
            // Ne pas pré-remplir l'email
          } else {
            openAuthModal('register');
          }
          return; // Ne pas continuer
        }
      }
    } catch (error) {
      console.error('[AUTH] Erreur lors de la vérification de l\'email:', error);
      // En cas d'erreur, continuer quand même mais ne pas pré-remplir
    }
    
    // Email n'existe pas - on peut pré-remplir le formulaire
    if (typeof showProRegisterForm === 'function') {
      showProRegisterForm();
      setTimeout(() => {
        const emailInput = document.getElementById('pro-email');
        if (emailInput) {
          emailInput.value = email;
          // ⚠️⚠️⚠️ CRITIQUE : Configurer la validation en temps réel sur tous les champs
          if (typeof setupProFormValidation === 'function') {
            setupProFormValidation();
          } else if (typeof window.setupProFormValidation === 'function') {
            window.setupProFormValidation();
          }
          // Valider immédiatement l'email après pré-remplissage
          if (typeof validateProEmailField === 'function') {
            validateProEmailField(emailInput);
          } else if (typeof window.validateProEmailField === 'function') {
            window.validateProEmailField(emailInput);
          }
          emailInput.dispatchEvent(new Event('input', { bubbles: true }));
        }
      }, 200);
    } else if (typeof window.showProRegisterForm === 'function') {
      window.showProRegisterForm();
      setTimeout(() => {
        const emailInput = document.getElementById('pro-email');
        if (emailInput) {
          emailInput.value = email;
          // ⚠️⚠️⚠️ CRITIQUE : Configurer la validation en temps réel sur tous les champs
          if (typeof setupProFormValidation === 'function') {
            setupProFormValidation();
          } else if (typeof window.setupProFormValidation === 'function') {
            window.setupProFormValidation();
          }
          // Valider immédiatement l'email après pré-remplissage
          if (typeof validateProEmailField === 'function') {
            validateProEmailField(emailInput);
          } else if (typeof window.validateProEmailField === 'function') {
            window.validateProEmailField(emailInput);
          }
          emailInput.dispatchEvent(new Event('input', { bubbles: true }));
        }
      }, 200);
    } else {
      // Fallback : afficher le formulaire d'inscription simplifié
      openAuthModal('register');
    }
  } catch (error) {
    console.error('[AUTH] ❌ Erreur vérification email:', error);
    // En cas d'erreur, proposer le formulaire d'inscription par défaut
    if (typeof showNotification === 'function') {
      showNotification('⚠️ Impossible de vérifier l\'email. Veuillez continuer avec le formulaire.', 'warning');
    }
    if (typeof showProRegisterForm === 'function') {
      showProRegisterForm();
    } else {
      openAuthModal('register');
    }
  }
}

// ⚠️⚠️⚠️ FLUX STANDARD : Afficher directement deux options (Google OU Email/Mot de passe)
function openLoginModal() {
  console.log('[AUTH] CLICK login - openLoginModal() called');
  console.log('[AUTH] ⚠️⚠️⚠️ FLUX STANDARD : Deux options directes (Google OU Email/Mot de passe)');
  
  const backdrop = document.getElementById('publish-modal-backdrop');
  const modal = document.getElementById('publish-modal-inner');
  
  if (!backdrop || !modal) {
    console.error('[AUTH] Modal elements not found');
    return;
  }
  
  // Centrer le modal avec padding vertical
  backdrop.style.display = 'flex';
  backdrop.style.visibility = 'visible';
  backdrop.style.opacity = '1';
  backdrop.style.paddingTop = '40px';
  backdrop.style.paddingBottom = '40px';
  backdrop.style.boxSizing = 'border-box';
  
  // ⚠️⚠️⚠️ Récupérer l'email depuis sessionStorage si disponible
  let savedEmail = '';
  try {
    const emailFromStorage = sessionStorage.getItem('lastLoginEmail');
    if (emailFromStorage && emailFromStorage.includes('@')) {
      savedEmail = emailFromStorage;
      console.log('[AUTH] ✅ Email récupéré depuis sessionStorage:', savedEmail);
    }
  } catch (e) {
    console.warn('[AUTH] ⚠️ Impossible de récupérer l\'email:', e);
  }
  
  // Afficher le modal avec deux options directes
  const html = `
    <div id="authModal" data-mode="login" style="padding:40px;max-width:450px;margin:0 auto;text-align:center;position:relative;">
      <!-- Bouton X (croix) pour fermer -->
      <button onclick="closeAuthModal()" style="position:absolute;top:16px;right:16px;background:none;border:none;color:var(--ui-text-muted);font-size:24px;cursor:pointer;padding:8px;width:40px;height:40px;display:flex;align-items:center;justify-content:center;border-radius:50%;transition:all 0.2s;z-index:10;" onmouseover="this.style.background='rgba(239,68,68,0.2)';this.style.color='#ef4444';this.style.transform='scale(1.1)';" onmouseout="this.style.background='none';this.style.color='var(--ui-text-muted)';this.style.transform='scale(1)';" title="Fermer">✕</button>
      
      <!-- Logo et titre -->
      <div style="margin-bottom:32px;">
        <div style="font-size:64px;margin-bottom:16px;">🌍</div>
        <h2 style="margin:0 0 8px;font-size:28px;font-weight:800;color:#fff;background:linear-gradient(135deg,#00ffc3,#3b82f6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">Connexion</h2>
        <p style="margin:0;font-size:14px;color:var(--ui-text-muted);">Choisissez votre méthode de connexion</p>
      </div>
      
      <!-- Option 1 : Google (pas besoin d'info) -->
      <div style="display:flex;flex-direction:column;gap:12px;margin-bottom:24px;">
        <button id="login-google-btn" onclick="if(typeof window.startGoogleLogin==='function'){window.startGoogleLogin();}" style="width:100%;padding:16px;border-radius:12px;border:2px solid rgba(0,255,195,0.3);background:linear-gradient(135deg,rgba(0,255,195,0.1),rgba(59,130,246,0.1));color:var(--ui-text-main);font-weight:600;font-size:15px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:12px;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(0,255,195,0.6)';this.style.background='linear-gradient(135deg,rgba(0,255,195,0.2),rgba(59,130,246,0.2))';" onmouseout="this.style.borderColor='rgba(0,255,195,0.3)';this.style.background='linear-gradient(135deg,rgba(0,255,195,0.1),rgba(59,130,246,0.1))';">
          <svg width="20" height="20" viewBox="0 0 24 24" style="fill:currentColor;">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
          </svg>
          <span>Continuer avec Google</span>
        </button>
        
        <div style="display:flex;align-items:center;gap:12px;margin:16px 0;">
          <div style="flex:1;height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.1),transparent);"></div>
          <span style="font-size:12px;color:var(--ui-text-muted);font-weight:500;">ou</span>
          <div style="flex:1;height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.1),transparent);"></div>
        </div>
        
        <!-- Option 2 : Email/Mot de passe -->
        <div style="margin-bottom:16px;text-align:left;">
          <label style="display:block;font-size:13px;font-weight:600;color:var(--ui-text-main);margin-bottom:8px;">📧 Email</label>
          <input type="email" id="login-email-input" placeholder="votre@email.com" value="${savedEmail}" style="width:100%;padding:12px 16px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:var(--ui-text-main);font-size:14px;transition:all 0.3s;" onfocus="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(15,23,42,0.8)';" onblur="this.style.borderColor='rgba(255,255,255,0.1)';this.style.background='rgba(15,23,42,0.5)';" oninput="try{const v=this.value.trim();if(v&&v.includes('@')){sessionStorage.setItem('lastLoginEmail',v);}else{sessionStorage.removeItem('lastLoginEmail');}}catch(e){}">
        </div>
        
        <div style="margin-bottom:16px;text-align:left;">
          <label style="display:block;font-size:13px;font-weight:600;color:var(--ui-text-main);margin-bottom:8px;">🔒 Mot de passe</label>
          <input type="password" id="login-password-input" placeholder="Votre mot de passe" style="width:100%;padding:12px 16px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:var(--ui-text-main);font-size:14px;transition:all 0.3s;" onfocus="this.style.borderColor='rgba(0,255,195,0.5)';this.style.background='rgba(15,23,42,0.8)';" onblur="this.style.borderColor='rgba(255,255,255,0.1)';this.style.background='rgba(15,23,42,0.5)';" onkeypress="if(event.key==='Enter'){const email=document.getElementById('login-email-input').value.trim();const password=document.getElementById('login-password-input').value.trim();if(email&&password&&typeof window.performReconnectLogin==='function'){window.performReconnectLogin(email,password);}}">
        </div>
        
        <button id="login-password-btn" onclick="const email=document.getElementById('login-email-input').value.trim();const password=document.getElementById('login-password-input').value.trim();if(email&&password&&typeof window.performReconnectLogin==='function'){window.performReconnectLogin(email,password);}" style="width:100%;padding:14px;border-radius:12px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:700;font-size:15px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 8px 20px rgba(0,255,195,0.3)';" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='none';">
          Se connecter avec mot de passe
        </button>
      </div>
      
      <button onclick="closeAuthModal()" style="width:100%;padding:12px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:transparent;color:var(--ui-text-muted);font-weight:600;font-size:14px;cursor:pointer;transition:all 0.3s;" onmouseover="this.style.borderColor='rgba(255,255,255,0.3)';this.style.color='var(--ui-text-main)';" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)';this.style.color='var(--ui-text-muted)';">
        Annuler
      </button>
    </div>
  `;
  
  backdrop.setAttribute('data-auth-modal', 'true');
  backdrop.style.display = 'flex';
  backdrop.style.visibility = 'visible';
  backdrop.style.opacity = '1';
  backdrop.style.paddingTop = '40px';
  backdrop.style.paddingBottom = '40px';
  backdrop.style.boxSizing = 'border-box';
  modal.innerHTML = html;
  modal.style.display = 'block';
  
  // Focus sur le champ approprié
  setTimeout(() => {
    const emailInput = document.getElementById('login-email-input');
    const passwordInput = document.getElementById('login-password-input');
    if (savedEmail && emailInput) {
      // Si email pré-rempli, focus sur mot de passe
      if (passwordInput) {
        passwordInput.focus();
      }
    } else if (emailInput) {
      // Sinon, focus sur email
      emailInput.focus();
    }
  }, 100);
}

function openRegisterModal() {
  console.log('[AUTH] CLICK register - openRegisterModal() called');
  console.log('[AUTH] Calling openAuthModal(\'register\')...');
  
  try {
    openAuthModal('register');
    console.log('[AUTH] openAuthModal(\'register\') called successfully');
  } catch (error) {
    console.error('[AUTH] ERREUR dans openAuthModal:', error);
    // Fallback vers showRegisterStep1 si disponible
    if (typeof showRegisterStep1 === 'function') {
      showRegisterStep1();
    }
  }
}

// ===============================
// PERFORM LOGIN
// ===============================
async function performLogin() {
  const email = document.getElementById("login-email")?.value.trim();
  const password = document.getElementById("login-password")?.value;
  const rememberMe = document.getElementById("login-remember-me")?.checked || false;
  
  if (!email || !password) {
    if (typeof showNotification === 'function') {
      showNotification("⚠️ Veuillez remplir tous les champs", "warning");
    }
    return;
  }
  
  // Tenter de récupérer l'utilisateur depuis localStorage (pour la démo)
  try {
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
      const parsedUser = JSON.parse(savedUser);
      if (parsedUser.email === email) {
        // Connexion réussie depuis localStorage
        if (typeof window !== 'undefined' && window.currentUser !== undefined) {
          window.currentUser = {
            ...parsedUser,
            isLoggedIn: true,
            lastLoginAt: new Date().toISOString()
          };
        }
        safeSetItem('currentUser', JSON.stringify(window.currentUser || parsedUser));
        if (typeof showNotification === 'function') {
          showNotification(`✅ Bienvenue ${parsedUser.name || parsedUser.email} !`, "success");
        }
        if (typeof closePublishModal === 'function') {
          closePublishModal();
        }
        if (typeof loadUserDataOnLogin === 'function') {
          await loadUserDataOnLogin();
        }
        if (typeof showStatusChangeNotifications === 'function') {
          showStatusChangeNotifications();
        }
        return;
      }
    }
  } catch (e) {
    console.error('Erreur lecture localStorage:', e);
  }
  
  // Tenter connexion via le backend avec JWT
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    if (response.ok) {
      const data = await response.json();
      if (data.user && data.accessToken && data.refreshToken) {
        // Sauvegarder les tokens JWT
        setAuthTokens(data.accessToken, data.refreshToken, rememberMe);
        
        if (typeof window !== 'undefined' && window.currentUser !== undefined) {
          window.currentUser = {
            ...data.user,
            isLoggedIn: true,
            accessToken: data.accessToken,
            refreshToken: data.refreshToken,
            lastLoginAt: new Date().toISOString(),
            rememberMe: rememberMe
          };
          
          // Initialiser pendingStatusNotifications si nécessaire
          if (!window.currentUser.pendingStatusNotifications) {
            window.currentUser.pendingStatusNotifications = [];
          }
        }
        
        safeSetItem('currentUser', JSON.stringify(window.currentUser || data.user));
        if (typeof showNotification === 'function') {
          showNotification(`✅ Bienvenue ${data.user.name || data.user.email} !`, "success");
        }
        if (typeof closePublishModal === 'function') {
          closePublishModal();
        }
        
        // Mettre à jour les boutons auth après connexion
        if (typeof updateAuthButtons === 'function') {
          updateAuthButtons();
        }
        
        // Mettre à jour le bloc compte
        if (typeof window !== 'undefined' && typeof window.updateAccountBlock === 'function') {
          setTimeout(() => window.updateAccountBlock(), 100);
        }
        
        if (typeof loadUserDataOnLogin === 'function') {
          await loadUserDataOnLogin();
        }
        
        console.log('[AUTH] Connexion reussie - pas d\'onboarding (uniquement a la creation de compte)');
        
        // Afficher les notifications de changement de statut si l'utilisateur a participé à des événements
        if (typeof showStatusChangeNotifications === 'function') {
          setTimeout(() => {
            showStatusChangeNotifications();
          }, 500);
        }
        return;
      } else {
        if (typeof showNotification === 'function') {
          showNotification("⚠️ Réponse invalide du serveur", "error");
        }
        return;
      }
    } else if (response.status === 401) {
      if (typeof showNotification === 'function') {
        showNotification("❌ Email ou mot de passe incorrect", "error");
      }
      return;
    } else {
      const errorData = await response.json().catch(() => ({}));
      if (typeof showNotification === 'function') {
        showNotification(`❌ Erreur de connexion: ${errorData.error || response.statusText}`, "error");
      }
      return;
    }
  } catch (error) {
    console.error('Erreur connexion backend:', error);
    if (typeof showNotification === 'function') {
      showNotification("❌ Erreur de connexion au serveur", "error");
    }
  }
  
  // Fallback: créer un compte temporaire pour la démo
  if (typeof showNotification === 'function') {
    showNotification("ℹ️ Compte non trouvé. Créez un nouveau compte.", "info");
  }
  if (typeof openRegisterModal === 'function') {
    openRegisterModal();
  } else if (typeof window.openRegisterModal === 'function') {
    window.openRegisterModal();
  }
}

// ===============================
// PERFORM REGISTER
// ===============================
async function performRegister() {
  console.log('[REGISTER] Debut inscription');
  
  // ⚠️⚠️⚠️ PRIORITÉ au formulaire professionnel
  const emailInput = document.getElementById("pro-email") || document.getElementById("register-email");
  const email = emailInput?.value.trim();
  const username = document.getElementById("pro-username")?.value.trim() || document.getElementById("register-username")?.value.trim();
  const firstName = document.getElementById("pro-firstname")?.value.trim() || '';
  const lastName = document.getElementById("pro-lastname")?.value.trim() || '';
  const password = document.getElementById("pro-password")?.value || document.getElementById("register-password")?.value;
  const passwordConfirm = document.getElementById("pro-password-confirm")?.value || document.getElementById("register-password-confirm")?.value;
  const photoInput = document.getElementById("pro-photo");
  const photoLater = document.getElementById("register-photo-later")?.checked || document.getElementById("pro-photo-later")?.checked;
  const addressLater = document.getElementById("register-address-later")?.checked || document.getElementById("pro-address-later")?.checked;
  
  // Validation des champs obligatoires
  if (!email || !username || !password || !passwordConfirm) {
    if (typeof showNotification === 'function') {
      showNotification("⚠️ Veuillez remplir tous les champs obligatoires", "warning");
    }
    return;
  }
  
  // Validation prénom et nom (formulaire professionnel)
  if (document.getElementById("pro-firstname") && (!firstName || !lastName)) {
    if (typeof showNotification === 'function') {
      showNotification("⚠️ Veuillez remplir le prénom et le nom", "warning");
    }
    return;
  }
  
  // Validation photo (obligatoire dans le formulaire professionnel)
  if (photoInput && !photoInput.files || (photoInput && photoInput.files.length === 0)) {
    if (typeof showNotification === 'function') {
      showNotification("⚠️ Veuillez sélectionner une photo de profil", "warning");
    }
    const photoError = document.getElementById("pro-photo-error");
    if (photoError) {
      photoError.textContent = '❌ Photo de profil obligatoire';
      photoError.style.color = '#ef4444';
      photoError.style.display = 'block';
    }
    photoInput.focus();
    return;
  }
  
  // ⚠️⚠️⚠️ CRITIQUE : Vérifier si l'email est marqué comme existant (validation en temps réel)
  if (emailInput && emailInput.getAttribute('data-email-exists') === 'true') {
    if (typeof showNotification === 'function') {
      showNotification("❌ Ce mail existe déjà. Veuillez utiliser un autre email ou vous connecter.", "error");
    }
    const emailError = document.getElementById("pro-email-error") || document.getElementById("register-email-error");
    if (emailError) {
      emailError.textContent = '❌ Ce mail existe déjà. Veuillez utiliser un autre email ou vous connecter.';
      emailError.style.color = '#ef4444';
      emailError.style.display = 'block';
    }
    emailInput.focus();
    return; // Empêcher la soumission
  }
  
  // ⚠️⚠️⚠️ CRITIQUE : Vérifier si l'email existe déjà AVANT de permettre la soumission
  try {
    const emailCheckResponse = await fetch(`${API_BASE_URL}/user/exists?email=${encodeURIComponent(email)}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (emailCheckResponse.ok) {
      const emailCheckData = await emailCheckResponse.json();
      if (emailCheckData.exists === true) {
        // Email existe déjà - empêcher la création du compte
        if (typeof showNotification === 'function') {
          showNotification("❌ Ce mail existe déjà. Veuillez utiliser un autre email ou vous connecter.", "error");
        }
        
        // Afficher l'erreur dans le formulaire
        const emailInput = document.getElementById("register-email");
        if (emailInput) {
          emailInput.style.borderColor = '#ef4444';
          const emailError = document.getElementById("register-email-error");
          if (emailError) {
            emailError.textContent = '❌ Ce mail existe déjà. Veuillez utiliser un autre email ou vous connecter.';
            emailError.style.color = '#ef4444';
            emailError.style.display = 'block';
          }
        }
        return; // Empêcher la soumission
      }
    }
  } catch (error) {
    console.error('[REGISTER] Erreur lors de la vérification de l\'email:', error);
    // En cas d'erreur, continuer quand même (ne pas bloquer si le backend est indisponible)
  }
  
  if (password !== passwordConfirm) {
    if (typeof showNotification === 'function') {
      showNotification("⚠️ Les mots de passe ne correspondent pas", "warning");
    }
    return;
  }
  
  if (password.length < 8) {
    if (typeof showNotification === 'function') {
      showNotification("⚠️ Le mot de passe doit contenir au moins 8 caractères", "warning");
    }
    return;
  }
  
  // Vérifier les règles de mot de passe
  if (!/[A-Z]/.test(password)) {
    if (typeof showNotification === 'function') {
      showNotification("⚠️ Le mot de passe doit contenir au moins une majuscule", "warning");
    }
    return;
  }
  
  if (!/[a-z]/.test(password)) {
    if (typeof showNotification === 'function') {
      showNotification("⚠️ Le mot de passe doit contenir au moins une minuscule", "warning");
    }
    return;
  }
  
  if (!/[0-9]/.test(password)) {
    if (typeof showNotification === 'function') {
      showNotification("⚠️ Le mot de passe doit contenir au moins un chiffre", "warning");
    }
    return;
  }
  
  // Vérifier que l'adresse est fournie (sauf si "plus tard")
  const selectedAddress = window.registerSelectedAddress;
  if (!addressLater && !selectedAddress) {
    if (typeof showNotification === 'function') {
      showNotification("⚠️ Veuillez sélectionner une adresse ou cocher 'Vérifier plus tard'", "warning");
    }
    return;
  }
  
  // ⚠️⚠️⚠️ CRITIQUE : Vérifier si l'email existe déjà AVANT d'afficher le choix de vérification
  try {
    const emailCheckResponse = await fetch(`${API_BASE_URL}/user/exists?email=${encodeURIComponent(email)}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (emailCheckResponse.ok) {
      const emailCheckData = await emailCheckResponse.json();
      if (emailCheckData.exists === true) {
        // Email existe déjà - empêcher la création du compte
        if (typeof showNotification === 'function') {
          showNotification("❌ Ce mail existe déjà. Veuillez utiliser un autre email ou vous connecter.", "error");
        }
        
        // Afficher l'erreur dans le formulaire
        const emailInput = document.getElementById("register-email") || document.getElementById("pro-email");
        if (emailInput) {
          emailInput.style.borderColor = '#ef4444';
          const emailError = document.getElementById("register-email-error") || document.getElementById("pro-email-error");
          if (emailError) {
            emailError.textContent = '❌ Ce mail existe déjà. Veuillez utiliser un autre email ou vous connecter.';
            emailError.style.color = '#ef4444';
            emailError.style.display = 'block';
          }
        }
        return; // Empêcher l'affichage du choix de vérification
      }
    }
  } catch (error) {
    console.error('[REGISTER] Erreur lors de la vérification de l\'email:', error);
    // En cas d'erreur, continuer quand même (ne pas bloquer si le backend est indisponible)
  }
  
  // NOUVEAU FLUX: Après validation du formulaire, afficher le choix de vérification
  // Stocker les données du formulaire pour utilisation ultérieure
  window.pendingRegisterData = {
    email: email,
    username: username,
    password: password,
    firstName: username.split(' ')[0] || username,
    lastName: username.split(' ').slice(1).join(' ') || username,
    photoLater: photoLater,
    addressLater: addressLater,
    selectedAddress: selectedAddress,
    photoData: window.registerPhotoData
  };
  
  // Afficher le choix de méthode de vérification
  showVerificationChoice();
  return;
  
  // ============================================
  // ANCIEN CODE DÉSACTIVÉ (ne sera plus exécuté)
  // Le compte sera créé après le choix de vérification (Google ou Email)
  // ============================================
  /*
  try {
    // Préparer les données d'inscription
    const firstName = username.split(' ')[0] || username;
    const lastName = username.split(' ').slice(1).join(' ') || username;
    
    const registerDataObj = {
      email: email,
      username: username,
      password: password,
      firstName: firstName,
      lastName: lastName
    };
    
    // Ajouter la photo si fournie
    if (!photoLater && window.registerPhotoData) {
      window.pendingRegisterPhoto = window.registerPhotoData;
      console.log('[REGISTER] Photo prête pour upload après inscription');
    }
    
    // Ajouter l'adresse si fournie
    if (!addressLater && selectedAddress) {
      registerDataObj.addresses = [{
        label: selectedAddress.label,
        lat: selectedAddress.lat,
        lng: selectedAddress.lng,
        addressDetails: {
          country_code: selectedAddress.country_code,
          city: selectedAddress.city,
          postcode: selectedAddress.postcode,
          street: selectedAddress.street
        }
      }];
      console.log('[REGISTER] Adresse incluse dans la requête:', selectedAddress.label);
    } else if (addressLater) {
      registerDataObj.addresses = [];
      console.log('[REGISTER] Adresse marquée "plus tard"');
    }
    
    console.log('[REGISTER] Appel POST /user/register');
    
    // TIMEOUT: 10 secondes avec AbortController
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);
    
    let registerResponse;
    try {
      registerResponse = await fetch(`${API_BASE_URL}/user/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(registerDataObj),
        signal: controller.signal
      });
      clearTimeout(timeoutId);
    } catch (fetchError) {
      clearTimeout(timeoutId);
      
      // Gérer spécifiquement le timeout
      if (fetchError.name === 'AbortError') {
        console.error('[REGISTER] Timeout après 10 secondes (cold start probable)');
        if (typeof showRegisterTimeoutError === 'function') {
          showRegisterTimeoutError(email, username);
        }
        return;
      }
      
      console.error('[REGISTER] Erreur fetch (réseau/CORS):', fetchError);
      if (typeof showNotification === 'function') {
        showNotification('⚠️ Erreur réseau lors de l\'inscription. Vérifiez votre connexion.', "error");
      }
      return;
    }
    
    // Lire le body même en cas d'erreur pour avoir les détails
    let responseBodyText = '';
    try {
      responseBodyText = await registerResponse.text();
    } catch (readError) {
      console.error('[REGISTER] Erreur lecture body:', readError);
    }
    
    if (!registerResponse.ok) {
      let errorData = { error: 'Erreur inconnue' };
      try {
        errorData = JSON.parse(responseBodyText);
      } catch (parseError) {
        errorData = { error: responseBodyText || 'Erreur inconnue' };
      }
      
      // Gérer spécifiquement le 409 Conflict (email/username déjà utilisé)
      if (registerResponse.status === 409) {
        window.pendingRegisterPhoto = null;
        window.registerSelectedAddress = null;
        
        if (typeof showRegisterConflictError === 'function') {
          showRegisterConflictError(errorData, email);
        }
        return;
      } else {
        window.pendingRegisterPhoto = null;
        window.registerSelectedAddress = null;
        
        if (typeof showNotification === 'function') {
          showNotification(`⚠️ Erreur lors de l'inscription: ${errorData.error || 'Erreur inconnue'}`, "error");
        }
        
        if (registerResponse.status === 400) {
          const emailInput = document.getElementById('register-email');
          const usernameInput = document.getElementById('register-username');
          if (emailInput) emailInput.value = '';
          if (usernameInput) usernameInput.value = '';
        }
      }
      return;
    }
    
    let registerResponseData = {};
    try {
      registerResponseData = JSON.parse(responseBodyText);
    } catch (parseError) {
      console.error('[REGISTER] Erreur parse JSON success:', parseError);
      if (typeof showNotification === 'function') {
        showNotification('⚠️ Réponse invalide du serveur', "error");
      }
      return;
    }
    
    // Stocker les tokens si fournis
    if (registerResponseData.accessToken) {
      setAuthTokens(registerResponseData.accessToken, registerResponseData.refreshToken || '', true);
    }
    
    // Si register renvoie directement les tokens, on peut se connecter
    // Sinon, on doit faire un login après
    let accessToken = registerResponseData.accessToken;
    
    if (!accessToken && registerResponseData.user) {
      // Pas de token dans la réponse, faire un login
      console.log('[REGISTER] Pas de token, appel POST /auth/login');
      const loginResponse = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      });
      
      if (loginResponse.ok) {
        const loginData = await loginResponse.json();
        accessToken = loginData.accessToken;
        if (accessToken) {
          setAuthTokens(accessToken, loginData.refreshToken || '', true);
        }
      }
    }
    
    // Récupérer le profil complet avec GET /user/me
    if (accessToken) {
      console.log('[ME] Appel GET /user/me');
      const meResponse = await fetch(`${API_BASE_URL}/user/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (meResponse.ok) {
        const meData = await meResponse.json();
        const user = meData.user;
        
        // Mettre à jour currentUser avec les données du backend
        const avatarUrl = user.avatarUrl || user.profile_photo_url || user.profilePhoto || null;
        
        if (typeof window !== 'undefined' && window.currentUser !== undefined) {
          window.currentUser = {
            ...window.currentUser,
            ...user,
            isLoggedIn: true,
            avatarUrl: avatarUrl,
            profilePhoto: avatarUrl,
            profile_photo_url: avatarUrl,
            avatar: avatarUrl || '👤',
            profile_public: user.profile_public !== undefined ? user.profile_public : false,
            show_name: user.show_name !== undefined ? user.show_name : false,
            show_photo: user.show_photo !== undefined ? user.show_photo : false,
            show_city_country_only: user.show_city_country_only !== undefined ? user.show_city_country_only : false
          };
        }
        
        safeSetItem('currentUser', JSON.stringify(window.currentUser || user));
        
        // Mettre à jour les boutons auth
        if (typeof updateAuthButtons === 'function') {
          updateAuthButtons();
        }
        
        // Fermer le modal d'inscription
        if (typeof closePublishModal === 'function') {
          closePublishModal();
        }
        
        // IMPORTANT: Upload photo uniquement APRÈS login réussi
        if (window.pendingRegisterPhoto && (window.currentUser?.id || user.id)) {
          console.log('[REGISTER] Upload de la photo en attente après connexion...');
          try {
            let photoFile = window.pendingRegisterPhoto;
            if (typeof photoFile === 'string' && photoFile.startsWith('data:image')) {
              const response = await fetch(photoFile);
              const blob = await response.blob();
              photoFile = new File([blob], 'profile-photo.jpg', { type: 'image/jpeg' });
            }
            
            if (typeof uploadProfilePhoto === 'function') {
              await uploadProfilePhoto(photoFile);
              window.pendingRegisterPhoto = null;
              
              if (typeof loadCurrentUserFromAPI === 'function') {
                await loadCurrentUserFromAPI();
              }
            }
          } catch (photoError) {
            console.error('[REGISTER] Erreur upload photo après inscription:', photoError);
            if (typeof showNotification === 'function') {
              showNotification('⚠️ Photo non uploadée, vous pourrez l\'ajouter plus tard', 'warning');
            }
          }
        }
        
        // Vérification email DÉSACTIVÉE - Comme les leaders mondiaux (Reddit, Twitter, etc.)
        // L'inscription email/mot de passe ne nécessite plus de vérification email.
        // SendGrid reste disponible pour d'autres usages (notifications, réinitialisation mot de passe, etc.)
        console.log('[REGISTER] ✅ Inscription réussie - Compte créé sans vérification email (comme les leaders mondiaux)');
        
        if (typeof showNotification === 'function') {
          showNotification('✅ Compte créé avec succès ! Bienvenue ' + (user.username || user.firstName || '') + ' !', 'success');
        }
        
        // Fermer le modal
        if (typeof closeAuthModal === 'function') {
          closeAuthModal();
        }
        
        // Mettre à jour les boutons
        if (typeof updateAuthButtons === 'function') {
          updateAuthButtons();
        }
        
        // Lancer l'onboarding si nécessaire
        if (typeof checkProfileCompleteness === 'function') {
          const profileCheck = checkProfileCompleteness(window.currentUser || user);
          
          if (!profileCheck.isComplete) {
            setTimeout(() => {
              if (typeof startOnboardingIfNeeded === 'function') {
                startOnboardingIfNeeded(window.currentUser || user);
              }
            }, 1000);
          } else {
            if (typeof showNotification === 'function') {
              showNotification('✅ Compte créé avec succès !', 'success');
            }
          }
        }
      } else {
        console.error('[ME] Erreur lors de la récupération du profil');
        if (typeof showNotification === 'function') {
          showNotification('⚠️ Erreur lors de la récupération du profil', 'error');
        }
      }
    } else {
      console.error('[REGISTER] Pas de token disponible après inscription');
      if (typeof showNotification === 'function') {
        showNotification('⚠️ Inscription réussie mais erreur de connexion', "warning");
      }
    }
  } catch (error) {
    console.error('[REGISTER] Erreur exception:', error);
    if (typeof showNotification === 'function') {
      showNotification(`⚠️ Erreur lors de l'inscription: ${error.message}`, "error");
    }
  }
  */
}

// ===============================
// OAUTH GOOGLE CALLBACK
// ===============================
async function handleCognitoCallbackIfPresent() {
  // GUARD: Éviter double traitement du callback
  if (isGoogleLoginInProgress && window.location.search.includes('code=')) {
    console.warn('⚠️ Callback OAuth déjà en cours de traitement');
    return;
  }
  
  console.log('🔍 handleCognitoCallbackIfPresent appelé', {
    url: window.location.href,
    hasCode: !!new URL(window.location.href).searchParams.get("code"),
    hasState: !!new URL(window.location.href).searchParams.get("state"),
    hasError: !!new URL(window.location.href).searchParams.get("error")
  });
  
  // ⚠️ CRITIQUE : Afficher le sablier d'attente pendant toute la validation Google
  showGoogleLoginLoading();
  
  const url = new URL(window.location.href);
  const code = url.searchParams.get("code");
  const state = url.searchParams.get("state");
  const error = url.searchParams.get("error");

  console.log('📋 Paramètres OAuth:', { code: !!code, state: !!state, error });
  
  // ⚠️⚠️⚠️ FIX MODE PRIVÉ : Décoder les données du formulaire depuis le state OAuth
  let decodedFormData = null;
  if (state && state.includes('_')) {
    try {
      const parts = state.split('_');
      if (parts.length > 1) {
        const encodedData = parts.slice(1).join('_'); // Tout après le premier underscore
        const decoded = JSON.parse(atob(encodedData));
        decodedFormData = decoded;
        console.log('[OAUTH] ✅ Données formulaire décodées depuis state OAuth:', decodedFormData);
      }
    } catch (e) {
      console.warn('[OAUTH] ⚠️ Impossible de décoder les données depuis state:', e);
    }
  }

  if (error) {
    console.error('❌ Erreur OAuth:', error);
    if (typeof showNotification === 'function') {
      showNotification("❌ Erreur login: " + error, "error");
    }
    isGoogleLoginInProgress = false;
    if (typeof window !== 'undefined') {
      window.isGoogleLoginInProgress = false;
    }
    hideGoogleLoginLoading();
    return;
  }
  if (!code) {
    console.log('ℹ️ Pas de code OAuth dans l\'URL - pas un callback');
    isGoogleLoginInProgress = false;
    if (typeof window !== 'undefined') {
      window.isGoogleLoginInProgress = false;
    }
    hideGoogleLoginLoading();
    return;
  }
  
  console.log('✅ Code OAuth détecté - Traitement du callback...');

  const expectedState = authLoad("oauth_state");
  if (!state || state !== expectedState) {
    if (typeof showNotification === 'function') {
      showNotification("❌ State OAuth invalide (sécurité).", "error");
    }
    return;
  }

  const verifier = authLoad("pkce_verifier");
  if (!verifier) {
    if (typeof showNotification === 'function') {
      showNotification("❌ PKCE verifier manquant.", "error");
    }
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
    if (typeof showNotification === 'function') {
      showNotification("❌ Impossible d'échanger le code (token).", "error");
    }
    return;
  }

  const tokens = await tokenRes.json();
  saveSession(tokens);
  authClearTemp();

  // Nettoyer l'URL (enlever ?code=...&state=...)
  url.searchParams.delete("code");
  url.searchParams.delete("state");
  url.searchParams.delete("session_state");
  window.history.replaceState({}, document.title, url.toString());

  // Construire un user "MapEvent"
  try {
    const payload = decodeJwtPayload(tokens.id_token);
    
    console.log('[PHOTO] Payload JWT Cognito:', {
      email: payload.email,
      name: payload.name,
      picture: payload.picture ? payload.picture.substring(0, 100) + '...' : 'ABSENTE',
      sub: payload.sub,
      allKeys: Object.keys(payload)
    });
    
    if (!payload.picture) {
      console.warn('[WARNING] payload.picture est ABSENT du token JWT Cognito!');
    }
    
    // Initialiser currentUser avec toutes les propriétés nécessaires
    if (typeof window !== 'undefined' && window.currentUser !== undefined) {
      window.currentUser = {
        isLoggedIn: true,
        provider: "google",
        email: payload.email || "",
        name: payload.name || payload.email || "Utilisateur",
        avatar: payload.picture || "👤",
        lastLoginAt: new Date().toISOString(),
        sub: payload.sub,
        likes: [],
        agenda: [],
        participating: [],
        favorites: [],
        friendRequests: [],
        eventStatusHistory: {},
        profileComplete: false,
        username: null,
        profilePhoto: payload.picture || null,
        profile_photo_url: payload.picture || null,
        postalAddress: null,
        password: null
      };
    }
    
    // PRIORITY HOTFIX: Ne jamais stocker l'objet user complet
    const slimUser = saveUserSlim(window.currentUser || {
      email: payload.email,
      name: payload.name || payload.email,
      profile_photo_url: payload.picture
    });
    if (slimUser) {
      safeSetItem("currentUser", JSON.stringify(slimUser));
    }
    
    // Mettre à jour le bloc compte temporairement avec la photo Google
    if (typeof window !== 'undefined' && typeof window.updateAccountBlock === 'function') {
      setTimeout(() => {
        window.updateAccountBlock();
      }, 100);
    }
    
    // Essayer de synchroniser avec le backend
    console.log('[OAUTH] Cognito callback - Synchronisation avec backend...', {
      email: window.currentUser?.email || payload.email,
      name: window.currentUser?.name || payload.name,
      sub: window.currentUser?.sub || payload.sub,
      picture: payload.picture ? payload.picture.substring(0, 50) + '...' : 'NULL'
    });
    
    try {
      // ⚠️⚠️⚠️ CRITIQUE : Récupérer pendingRegisterData depuis localStorage si perdu lors de la redirection Google
      // Car window.pendingRegisterData est perdu lors de la redirection vers Google
      let pendingData = window.pendingRegisterData;
      
      // ⚠️⚠️⚠️ FIX MODE PRIVÉ : Si on a décodé des données depuis le state OAuth, les utiliser
      if (!pendingData && decodedFormData && decodedFormData.username) {
        console.log('[OAUTH] ✅✅✅ Données formulaire récupérées depuis state OAuth (mode privé)');
        // Récupérer photoData depuis sessionStorage si disponible
        let photoData = null;
        try {
          const savedData = sessionStorage.getItem('pendingRegisterDataForGoogle');
          if (savedData) {
            const parsed = JSON.parse(savedData);
            photoData = parsed.photoData || null;
          }
        } catch (e) {
          // Ignorer
        }
        pendingData = {
          username: decodedFormData.username,
          photoData: photoData,
          firstName: decodedFormData.firstName || null,
          lastName: decodedFormData.lastName || null
        };
        window.pendingRegisterData = pendingData;
        window.isRegisteringWithGoogle = true;
        console.log('[OAUTH] ✅ pendingData restauré depuis state OAuth:', { username: pendingData.username, hasPhotoData: !!pendingData.photoData });
      }
      
      console.log('[OAUTH] 🔍🔍🔍 ÉTAPE 1 - window.pendingRegisterData:', pendingData ? 'EXISTE' : 'NULL');
      
      // Si pendingRegisterData n'existe pas dans window, le récupérer depuis localStorage
      if (!pendingData) {
        try {
          console.log('[OAUTH] 🔍🔍🔍 ÉTAPE 2 - Tentative récupération depuis storage...');
          // ⚠️⚠️⚠️ FIX MODE PRIVÉ : Essayer localStorage, puis sessionStorage, puis window
          let savedPendingData = null;
          try {
            savedPendingData = localStorage.getItem('pendingRegisterDataForGoogle');
          } catch (e) {
            console.warn('[OAUTH] ⚠️ localStorage bloqué (mode privé?), essai sessionStorage...');
            try {
              savedPendingData = sessionStorage.getItem('pendingRegisterDataForGoogle');
            } catch (e2) {
              console.warn('[OAUTH] ⚠️ sessionStorage aussi bloqué, essai window.pendingRegisterData...');
              if (window.pendingRegisterData) {
                savedPendingData = JSON.stringify(window.pendingRegisterData);
              }
            }
          }
          console.log('[OAUTH] 🔍🔍🔍 ÉTAPE 3 - getItem résultat:', savedPendingData ? `EXISTE (${savedPendingData.length} chars)` : 'NULL');
          
          if (savedPendingData) {
            try {
              pendingData = JSON.parse(savedPendingData);
              console.log('[OAUTH] ✅✅✅ pendingRegisterData récupéré depuis localStorage:', {
                username: pendingData.username,
                hasPhotoData: !!pendingData.photoData,
                photoDataLength: pendingData.photoData ? pendingData.photoData.length : 0,
                email: pendingData.email
              });
              // Restaurer dans window pour utilisation ultérieure
              window.pendingRegisterData = pendingData;
              window.isRegisteringWithGoogle = true;
              // ⚠️⚠️⚠️ NE PAS NETTOYER localStorage ici - on en a besoin pour les comptes existants aussi
              // localStorage.removeItem('pendingRegisterDataForGoogle');
            } catch (parseError) {
              console.error('[OAUTH] ❌ Erreur JSON.parse:', parseError);
            }
          } else {
            console.log('[OAUTH] ⚠️⚠️⚠️ Aucune donnée trouvée dans localStorage avec la clé "pendingRegisterDataForGoogle"');
          }
        } catch (e) {
          console.error('[OAUTH] ❌ Erreur récupération pendingRegisterData depuis localStorage:', e);
        }
      }
      
      // Fallback : utiliser window.pendingRegisterData si disponible
      if (!pendingData && window.isRegisteringWithGoogle && window.pendingRegisterData) {
        pendingData = window.pendingRegisterData;
        console.log('[OAUTH] 🔍🔍🔍 ÉTAPE 4 - Utilisation window.pendingRegisterData comme fallback');
      }
      
      console.log('[OAUTH] 🔍🔍🔍 pendingData final:', pendingData ? {
        username: pendingData.username,
        hasPhotoData: !!pendingData.photoData,
        photoDataLength: pendingData.photoData ? pendingData.photoData.length : 0,
        email: pendingData.email
      } : 'NULL');
      
      const requestBody = {
        email: window.currentUser?.email || payload.email,
        name: window.currentUser?.name || payload.name,
        sub: window.currentUser?.sub || payload.sub,
        picture: payload.picture || null
      };
      
      // Si inscription avec Google, ajouter les données du formulaire
      if (pendingData) {
        console.log('[OAUTH] 📤 Envoi données formulaire au backend:', { username: pendingData.username, hasPhotoData: !!pendingData.photoData });
        requestBody.username = pendingData.username;
        requestBody.firstName = pendingData.firstName;
        requestBody.lastName = pendingData.lastName;
        requestBody.photoData = pendingData.photoData || null; // ⚠️⚠️⚠️ CRITIQUE : Inclure photoData dans la requête
        if (pendingData.selectedAddress && !pendingData.addressLater) {
          requestBody.addresses = [{
            label: pendingData.selectedAddress.label,
            lat: pendingData.selectedAddress.lat,
            lng: pendingData.selectedAddress.lng,
            addressDetails: {
              country_code: pendingData.selectedAddress.country_code,
              city: pendingData.selectedAddress.city,
              postcode: pendingData.selectedAddress.postcode,
              street: pendingData.selectedAddress.street
            }
          }];
        }
                // INCLURE photoData si disponible (photo uploadÃ©e lors de la crÃ©ation du profil)
        if (pendingData.photoData && pendingData.photoData !== 'null' && pendingData.photoData !== null) {
          requestBody.photoData = pendingData.photoData;
          console.log('[OAUTH] âœ… photoData inclus dans la requÃªte OAuth Google:', pendingData.photoData.substring(0, 50) + '...');
        }
        console.log('[OAUTH] Inscription avec Google - Données formulaire incluses');
      }
      
      console.log('[OAUTH] pendingRegisterData photoData:', window.pendingRegisterData?.photoData ? (window.pendingRegisterData.photoData.substring(0, 50) + '...') : 'null');
      console.log('[OAUTH] pendingRegisterData username:', window.pendingRegisterData?.username || 'MANQUANT');
      console.log('[OAUTH] requestBody username:', requestBody.username || 'MANQUANT');
      console.log('[OAUTH] Envoi requete OAuth Google au backend');
      
      let syncResponse;
      try {
        syncResponse = await fetch(`${API_BASE_URL}/user/oauth/google`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${tokens.id_token}`
          },
          body: JSON.stringify(requestBody)
        });
      } catch (fetchError) {
        // Erreur réseau (CORS, timeout, etc.) - backend vraiment indisponible
        console.warn('⚠️ Erreur réseau lors de l\'appel API backend:', fetchError);
        throw fetchError; // Relancer pour être géré par le catch externe
      }
      
      // ⚠️⚠️⚠️ CRITIQUE : Vérifier le status de la réponse
      // Si c'est 401, le backend est disponible mais l'utilisateur n'est pas authentifié
      // Si c'est une erreur réseau (NetworkError), le backend est vraiment indisponible
      if (!syncResponse.ok) {
        const errorText = await syncResponse.text();
        let errorData = null;
        try {
          errorData = JSON.parse(errorText);
        } catch (e) {
          // Pas de JSON, utiliser le texte brut
        }
        
        // Si c'est 401, c'est une erreur d'authentification, pas un backend indisponible
        if (syncResponse.status === 401) {
          console.warn('⚠️ Erreur 401 - Authentification requise:', errorData || errorText);
          // Ne pas basculer en mode "backend indisponible" - le backend est disponible
          // mais l'utilisateur n'est pas authentifié correctement
          throw new Error(`Authentication failed: ${errorData?.error || errorText || 'Unauthorized'}`);
        }
        
        // Autres erreurs (500, 503, etc.) - backend peut être indisponible
        console.warn(`⚠️ Erreur ${syncResponse.status} lors de l'appel API backend:`, errorData || errorText);
        throw new Error(`Backend error: ${syncResponse.status} - ${errorData?.error || errorText || 'Unknown error'}`);
      }
      
      if (syncResponse.ok) {
        const syncData = await syncResponse.json();
        console.log('[OAUTH] RÃ©ponse backend photoData:', syncData.user?.photoData ? (syncData.user.photoData.substring(0, 50) + '...') : 'null');
        console.log('[OAUTH] RÃ©ponse backend username:', syncData.user?.username || 'MANQUANT');
        console.log('[OK] Synchronisation backend reussie:', {
          ok: syncData.ok,
          isNewUser: syncData.isNewUser,
          profileComplete: syncData.profileComplete,
          username: syncData.user?.username || 'MANQUANT'
        });
        
        // FLOW INTELLIGENT : Gérer les différents cas selon les données
        if (syncData.ok && syncData.user) {
          const profileComplete = syncData.profileComplete === true;
          const missingData = syncData.missingData || [];
          const needsEmailVerification = syncData.needsEmailVerification === true;
          const isNewUser = syncData.isNewUser === true;
          
          // RÈGLE 1: NOUVEAU COMPTE - FORCER LE FORMULAIRE SI DONNÉES MANQUANTES
          if (isNewUser) {
            // ⚠️⚠️⚠️ CRITIQUE : Vérifier que toutes les données obligatoires sont présentes
            // Utilisation du module de validation
            const validation = ProfileValidator.validateRequiredFields(
              syncData.user || {}, 
              window.pendingRegisterData || {}
            );
            const hasRequiredData = validation.isValid;
            
            // Si c'est une inscription avec Google ET que toutes les données obligatoires sont présentes
            if (window.isRegisteringWithGoogle && hasRequiredData) {
              console.log('[OAUTH] NOUVEAU COMPTE GOOGLE - Connexion automatique (inscription via formulaire avec données complètes)');
              console.log('[OAUTH] Détails:', { profileComplete, missingData, hasPendingData: !!window.pendingRegisterData, hasRequiredData });
              
              // ⚠️⚠️⚠️ CRITIQUE : SAUVEGARDER username ET photoData AVANT de nettoyer pendingRegisterData
              // Le username du formulaire est la SEULE source de vérité pour les nouveaux comptes
              const savedPhotoData = window.pendingRegisterData?.photoData || syncData.user?.photoData || null;
              let savedUsername = window.pendingRegisterData?.username || null; // ⚠️ PRIORITÉ ABSOLUE
              
              // ⚠️⚠️⚠️ Vérifier aussi dans localStorage/sessionStorage si pas trouvé
              if (!savedUsername || savedUsername === 'null' || savedUsername === '' || savedUsername.includes('@')) {
                try {
                  const storedData = localStorage.getItem('pendingRegisterDataForGoogle') || sessionStorage.getItem('pendingRegisterDataForGoogle');
                  if (storedData) {
                    const parsed = JSON.parse(storedData);
                    if (parsed?.username && parsed.username !== 'null' && !parsed.username.includes('@')) {
                      savedUsername = parsed.username;
                      console.log('[OAUTH] ✅ Username récupéré depuis storage:', savedUsername);
                    }
                  }
                } catch (e) {
                  console.error('[OAUTH] ❌ Erreur récupération username depuis storage:', e);
                }
              }
              
              console.log('[OAUTH] ⚠️⚠️⚠️ USERNAME DU FORMULAIRE (pendingRegisterData):', savedUsername || 'MANQUANT');
              console.log('[OAUTH] Username depuis syncData.user (backend):', syncData.user?.username || 'MANQUANT');
              console.log('[OAUTH] Email (pour comparaison):', syncData.user?.email || 'MANQUANT');
              
              // Nettoyer les flags d'inscription MAIS garder les données sauvegardées
              window.isRegisteringWithGoogle = false;
              const tempPendingData = { username: savedUsername, photoData: savedPhotoData }; // Sauvegarder temporairement
              window.pendingRegisterData = null;
              
              // Normaliser photoData : convertir "null" en null réel
              let normalizedPhotoData = savedPhotoData;
              if (normalizedPhotoData === 'null' || normalizedPhotoData === 'undefined' || normalizedPhotoData === '' || !normalizedPhotoData) {
                normalizedPhotoData = null;
              }
              
              // Connecter automatiquement
              // ⚠️⚠️⚠️ RÈGLE ABSOLUE : Le username du FORMULAIRE est la SEULE source de vérité pour les nouveaux comptes
              // Utilisation du module de validation pour récupérer le username valide
              // ⚠️⚠️⚠️ CRITIQUE : Vérifier d'abord si le username du formulaire est présent
              console.log('[OAUTH] 🔍 DEBUG username - tempPendingData.username:', tempPendingData?.username);
              console.log('[OAUTH] 🔍 DEBUG username - syncData.user.username:', syncData.user?.username);
              console.log('[OAUTH] 🔍 DEBUG username - payload.name:', payload?.name);
              
              let finalUsername = tempPendingData?.username; // ⚠️ PRIORITÉ ABSOLUE au username du formulaire
              
              // Si le username du formulaire est invalide, utiliser le module
              if (!finalUsername || finalUsername === 'null' || finalUsername === '' || finalUsername.includes('@')) {
                console.warn('[OAUTH] ⚠️ Username du formulaire invalide, utilisation du module');
                finalUsername = ProfileValidator.getValidUsername(
                  syncData.user || {},
                  tempPendingData,
                  payload
                );
              }
              
              console.log('[OAUTH] ✅ Username final récupéré:', finalUsername);
              
              console.log('[OAUTH] ✅✅✅ Username FINAL pour slimUser:', finalUsername);
              console.log('[OAUTH] ✅✅✅ PhotoData FINAL pour slimUser:', tempPendingData.photoData ? 'PRÉSENT' : 'NULL');
              
              const slimUser = {
                id: syncData.user.id,
                email: syncData.user.email || window.currentUser?.email,
                username: finalUsername, // ⚠️⚠️⚠️ PRIORITÉ ABSOLUE au username du formulaire (tempPendingData.username)
                firstName: syncData.user.firstName || syncData.user.first_name || '',
                lastName: syncData.user.lastName || syncData.user.last_name || '',
                role: syncData.user.role || 'user',
                subscription: syncData.user.subscription || 'free',
                profile_photo_url: syncData.user.profile_photo_url || payload.picture || null,
                hasPassword: syncData.user.hasPassword || false,
                hasPostalAddress: syncData.user.hasPostalAddress || false,
                profileComplete: true, // Toujours true car on vient du formulaire complet
                isLoggedIn: true,
                provider: 'google',
                // INCLURE TOUTES LES DONNÉES DU FORMULAIRE ET DU BACKEND
                postalAddress: syncData.user.postalAddress || syncData.user.postal_address || null,
                addresses: syncData.user.addresses || syncData.user.postal_addresses || [],
                photoData: tempPendingData.photoData ? (tempPendingData.photoData === 'null' ? null : tempPendingData.photoData) : null, // Utiliser photoData du formulaire
                avatarId: tempPendingData.avatarId || null // Utiliser avatarId du formulaire sauvegardé
              };
              
              console.log('[OAUTH] slimUser créé:', {
                username: slimUser.username,
                photoData: slimUser.photoData ? (slimUser.photoData.substring(0, 50) + '...') : 'null',
                photoDataType: typeof slimUser.photoData,
                profile_photo_url: slimUser.profile_photo_url ? (slimUser.profile_photo_url.substring(0, 50) + '...') : 'null'
              });
              
              if (typeof window !== 'undefined' && window.currentUser !== undefined) {
                window.currentUser = { ...window.currentUser, ...slimUser, isLoggedIn: true };
                
                // S'assurer que photoData est null et non "null" dans currentUser
                if (window.currentUser.photoData === 'null' || window.currentUser.photoData === 'undefined' || window.currentUser.photoData === '') {
                  window.currentUser.photoData = null;
                }
              }
              
              // ⚠️⚠️⚠️ CRITIQUE : Connexion DIRECTE sans demander "rester connecté"
              // La question "rester connecté" sera posée uniquement à la déconnexion
              connectUser(slimUser, tokens, true); // true = rester connecté par défaut
              
              // Fermer le modal
              closeAuthModal();
              return;
            }
            
            // ⚠️⚠️⚠️ CRITIQUE : Si données obligatoires manquantes, FORCER le formulaire
            // Utilisation du module de validation
            const newUserValidation = ProfileValidator.validateRequiredFields(
              syncData.user || {},
              window.pendingRegisterData || {}
            );
            
            if (!newUserValidation.isValid) {
              console.log('[OAUTH] ❌ NOUVEAU COMPTE - Données obligatoires manquantes:', newUserValidation.missingFields);
              console.log('[OAUTH] ❌ FORCAGE DU FORMULAIRE - Connexion refusée jusqu\'à complétion');
              if (typeof showNotification === 'function') {
                showNotification(`⚠️ Veuillez compléter les informations obligatoires : ${newUserValidation.missingFields.join(', ')}. L'adresse postale est optionnelle.`, 'warning');
              }
              if (typeof showProRegisterForm === 'function') {
                showProRegisterForm();
              } else if (typeof window.showProRegisterForm === 'function') {
                window.showProRegisterForm();
              }
              isGoogleLoginInProgress = false;
              if (typeof window !== 'undefined') {
                window.isGoogleLoginInProgress = false;
              }
              return; // ⚠️⚠️⚠️ IMPORTANT : Ne pas connecter si données manquantes
            }
            
            // Sinon, afficher le formulaire de complétion (pour adresse postale optionnelle)
            console.log('[OAUTH] NOUVEAU COMPTE - Affichage formulaire complet (adresse postale optionnelle)');
            if (typeof showNotification === 'function') {
              showNotification('⚠️ Veuillez compléter votre profil pour continuer. L\'adresse postale est optionnelle.', 'info');
            }
            if (typeof showProRegisterForm === 'function') {
              showProRegisterForm();
            } else if (typeof window.showProRegisterForm === 'function') {
              window.showProRegisterForm();
            }
            // Pré-remplir avec les données Google
            if (syncData.user) {
              registerData = {
                email: syncData.user.email || window.currentUser?.email || '',
                username: syncData.user.username || window.currentUser?.email?.split('@')[0]?.substring(0, 20) || '',
                password: '',
                passwordConfirm: '',
                firstName: syncData.user.firstName || syncData.user.first_name || window.currentUser?.name?.split(' ')[0] || '',
                lastName: syncData.user.lastName || syncData.user.last_name || window.currentUser?.name?.split(' ').slice(1).join(' ') || '',
                profilePhoto: syncData.user.profile_photo_url || payload.picture || '',
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
            }
            isGoogleLoginInProgress = false;
            if (typeof window !== 'undefined') {
              window.isGoogleLoginInProgress = false;
            }
            return;
          }
          
          // CAS 1: Profil complet → Vérifier données obligatoires puis connexion directe OU Mise à jour profil
          // ⚠️⚠️⚠️ CRITIQUE : Vérifier que toutes les données obligatoires sont présentes
          // Utilisation du module de validation
          const existingUserValidation = ProfileValidator.validateRequiredFields(
            syncData.user || {},
            savedPendingData || {}
          );
          const hasRequiredDataForExisting = existingUserValidation.isValid;
          
          if (profileComplete === true && missingData.length === 0 && !needsEmailVerification && hasRequiredDataForExisting) {
            // Vérifier si c'est une mise à jour de profil
            if (window.isUpdatingProfile && window.pendingProfileChanges) {
              console.log('[OAUTH] ➡️ CAS: MISE À JOUR PROFIL - Application des modifications');
              // Appliquer les modifications
              if (typeof window.applyProfileChanges === 'function') {
                await window.applyProfileChanges();
              }
              return;
            }
            
            console.log('[OAUTH] ➡️ CAS: COMPTE EXISTANT COMPLET - CONNEXION DIRECTE');
            
            // ⚠️⚠️⚠️ COMPTE EXISTANT : Nettoyer les données d'inscription précédentes pour éviter la pollution
            // Un compte existant utilise les données du BACKEND, pas du formulaire d'inscription
            console.log('[OAUTH] 🧹 COMPTE EXISTANT - Nettoyage des données d\'inscription précédentes...');
            try {
              localStorage.removeItem('pendingRegisterDataForGoogle');
              sessionStorage.removeItem('pendingRegisterDataForGoogle');
              sessionStorage.removeItem('wantToRegister');
              window.pendingRegisterData = null;
              window.isRegisteringWithGoogle = false;
              console.log('[OAUTH] ✅ Données d\'inscription nettoyées pour compte existant');
            } catch (e) {
              console.warn('[OAUTH] ⚠️ Erreur nettoyage données inscription:', e);
            }
            
            // ⚠️⚠️⚠️ CRITIQUE : Pour compte existant, pendingData doit être null
            // On utilise UNIQUEMENT les données du backend (syncData.user)
            console.log('[OAUTH] 🔍🔍🔍 VÉRIFICATION pendingRegisterData AVANT sauvegarde:', window.pendingRegisterData ? 'EXISTE' : 'NULL');
            console.log('[OAUTH] 🔍🔍🔍 VÉRIFICATION pendingData (ligne 2336):', pendingData ? 'EXISTE' : 'NULL');
            console.log('[OAUTH] 🔍🔍🔍 VÉRIFICATION isRegisteringWithGoogle:', window.isRegisteringWithGoogle);
            
            // ⚠️⚠️⚠️ CRITIQUE : Utiliser pendingData (récupéré ligne 2337+) OU window.pendingRegisterData selon ce qui est disponible
            // pendingData devrait déjà contenir les données depuis localStorage si nécessaire
            let savedPendingData = pendingData;
            
            console.log('[OAUTH] 🔍🔍🔍 COMPTE EXISTANT - ÉTAPE 1 - pendingData:', savedPendingData ? 'EXISTE' : 'NULL');
            
            // Si pendingData n'existe toujours pas, essayer window.pendingRegisterData
            if (!savedPendingData && window.pendingRegisterData) {
              savedPendingData = JSON.parse(JSON.stringify(window.pendingRegisterData));
              console.log('[OAUTH] 🔍🔍🔍 COMPTE EXISTANT - ÉTAPE 2 - Utilisation window.pendingRegisterData');
            }
            
            // Si toujours rien, essayer localStorage directement (fallback supplémentaire)
            if (!savedPendingData) {
              try {
                console.log('[OAUTH] 🔍🔍🔍 COMPTE EXISTANT - ÉTAPE 3 - Tentative storage...');
                // ⚠️⚠️⚠️ FIX MODE PRIVÉ : Essayer localStorage, puis sessionStorage, puis window
                let savedFromStorage = null;
                try {
                  savedFromStorage = localStorage.getItem('pendingRegisterDataForGoogle');
                } catch (e) {
                  console.warn('[OAUTH] ⚠️ localStorage bloqué (mode privé?), essai sessionStorage...');
                  try {
                    savedFromStorage = sessionStorage.getItem('pendingRegisterDataForGoogle');
                  } catch (e2) {
                    console.warn('[OAUTH] ⚠️ sessionStorage aussi bloqué, essai window.pendingRegisterData...');
                    if (window.pendingRegisterData) {
                      savedFromStorage = JSON.stringify(window.pendingRegisterData);
                    }
                  }
                }
                console.log('[OAUTH] 🔍🔍🔍 COMPTE EXISTANT - ÉTAPE 4 - getItem:', savedFromStorage ? `EXISTE (${savedFromStorage.length} chars)` : 'NULL');
                
                if (savedFromStorage) {
                  savedPendingData = JSON.parse(savedFromStorage);
                  console.log('[OAUTH] ✅✅✅ savedPendingData récupéré depuis localStorage dans compte existant:', {
                    username: savedPendingData.username,
                    hasPhotoData: !!savedPendingData.photoData,
                    photoDataLength: savedPendingData.photoData ? savedPendingData.photoData.length : 0
                  });
                  // Restaurer dans window pour utilisation ultérieure
                  window.pendingRegisterData = savedPendingData;
                  window.isRegisteringWithGoogle = true;
                  // ⚠️⚠️⚠️ NE PAS NETTOYER localStorage ici - on en a besoin pour connectUser
                } else {
                  console.log('[OAUTH] ⚠️⚠️⚠️ COMPTE EXISTANT - Aucune donnée dans localStorage');
                }
              } catch (e) {
                console.error('[OAUTH] ❌ Erreur récupération depuis localStorage:', e);
              }
            }
            
            console.log('[OAUTH] 🔍🔍🔍 COMPTE EXISTANT - savedPendingData final:', savedPendingData ? {
              username: savedPendingData.username,
              hasPhotoData: !!savedPendingData.photoData,
              photoDataLength: savedPendingData.photoData ? savedPendingData.photoData.length : 0
            } : 'NULL');
            
            // ⚠️⚠️⚠️ CRITIQUE : Si savedPendingData est toujours null, essayer localStorage directement
            if (!savedPendingData) {
              try {
                console.log('[OAUTH] 🔍🔍🔍 COMPTE EXISTANT - Tentative récupération DIRECTE depuis storage...');
                // ⚠️⚠️⚠️ FIX MODE PRIVÉ : Essayer localStorage, puis sessionStorage, puis window
                let savedFromStorage = null;
                try {
                  savedFromStorage = localStorage.getItem('pendingRegisterDataForGoogle');
                } catch (e) {
                  console.warn('[OAUTH] ⚠️ localStorage bloqué (mode privé?), essai sessionStorage...');
                  try {
                    savedFromStorage = sessionStorage.getItem('pendingRegisterDataForGoogle');
                  } catch (e2) {
                    console.warn('[OAUTH] ⚠️ sessionStorage aussi bloqué, essai window.pendingRegisterData...');
                    if (window.pendingRegisterData) {
                      savedFromStorage = JSON.stringify(window.pendingRegisterData);
                    }
                  }
                }
                if (savedFromStorage) {
                  savedPendingData = JSON.parse(savedFromStorage);
                  console.log('[OAUTH] ✅✅✅✅✅ COMPTE EXISTANT - savedPendingData récupéré DIRECTEMENT depuis localStorage:', {
                    username: savedPendingData.username,
                    hasPhotoData: !!savedPendingData.photoData,
                    photoDataLength: savedPendingData.photoData ? savedPendingData.photoData.length : 0
                  });
                  // Restaurer dans window pour utilisation ultérieure
                  window.pendingRegisterData = savedPendingData;
                  window.isRegisteringWithGoogle = true;
                }
              } catch (e) {
                console.error('[OAUTH] ❌ Erreur récupération DIRECTE depuis localStorage:', e);
              }
            }
            
            const savedUsernameFromForm = savedPendingData?.username || null;
            const savedPhotoDataFromForm = savedPendingData?.photoData || null;
            
            console.log('[OAUTH] ⚠️⚠️⚠️ USERNAME DU FORMULAIRE (savedPendingData):', savedUsernameFromForm || 'MANQUANT');
            console.log('[OAUTH] Username du backend (syncData.user):', syncData.user?.username || 'MANQUANT');
            console.log('[OAUTH] PhotoData du formulaire (savedPendingData):', savedPhotoDataFromForm ? `PRÉSENT (${savedPhotoDataFromForm.length} chars)` : 'MANQUANT');
            console.log('[OAUTH] PhotoData du backend (syncData.user):', syncData.user?.photoData ? 'PRÉSENT' : 'MANQUANT');
            
            // ⚠️⚠️⚠️ CRITIQUE : Normaliser photoData : PRIORITÉ ABSOLUE au formulaire, puis backend
            // ⚠️⚠️⚠️ FIX MODE PRIVÉ : Si pas de photo du formulaire, la photo Google sera dans profile_photo_url
            // Exactement comme "Continuer sans vérifier" (ligne 3867)
            let normalizedPhotoData = savedPhotoDataFromForm || syncData.user.photoData || null;
            if (normalizedPhotoData === 'null' || normalizedPhotoData === 'undefined' || normalizedPhotoData === '' || !normalizedPhotoData) {
              normalizedPhotoData = null;
            }
            
            // ⚠️⚠️⚠️ FIX MODE PRIVÉ : Si pas de photoData mais qu'on a une photo Google, on l'utilisera via profile_photo_url
            // La photo Google sera affichée via getUserAvatar qui vérifie profile_photo_url
            
            // ⚠️⚠️⚠️ CRITIQUE : Pour COMPTE EXISTANT : PRIORITÉ ABSOLUE au username du BACKEND
            // Le username du formulaire n'a de sens que pour les NOUVEAUX comptes
            // Pour les comptes existants, on utilise ce qui est déjà enregistré en base de données
            console.log('[OAUTH] 🔍 DEBUG username COMPTE EXISTANT - syncData.user.username:', syncData.user?.username);
            console.log('[OAUTH] 🔍 DEBUG username COMPTE EXISTANT - savedPendingData.username:', savedPendingData?.username);
            console.log('[OAUTH] 🔍 DEBUG username COMPTE EXISTANT - payload.name:', payload?.name);
            
            // ⚠️⚠️⚠️ COMPTE EXISTANT : PRIORITÉ au backend (username déjà enregistré)
            let finalUsername = syncData.user?.username; // ⚠️ PRIORITÉ au username du backend pour compte existant
            
            // Si le username du backend est invalide (email ou vide), essayer savedPendingData comme fallback
            if (!finalUsername || finalUsername === 'null' || finalUsername === '' || finalUsername.includes('@')) {
              console.warn('[OAUTH] ⚠️ Username du backend invalide, essai savedPendingData...');
              finalUsername = savedPendingData?.username;
            }
            
            // Si toujours invalide, utiliser le module
            if (!finalUsername || finalUsername === 'null' || finalUsername === '' || finalUsername.includes('@')) {
              console.warn('[OAUTH] ⚠️ Username du formulaire aussi invalide, utilisation du module');
              finalUsername = ProfileValidator.getValidUsername(
                syncData.user || {},
                savedPendingData || {},
                payload
              );
            }
            
            console.log('[OAUTH] ✅✅✅ Username final COMPTE EXISTANT (PRIORITÉ au backend):', finalUsername);
            
            console.log('[OAUTH] ✅✅✅ Username FINAL pour slimUser:', finalUsername);
            console.log('[OAUTH] ✅✅✅ Vérification: savedUsernameFromForm =', savedUsernameFromForm);
            console.log('[OAUTH] ✅✅✅ Vérification: syncData.user.username =', syncData.user?.username);
            console.log('[OAUTH] ✅✅✅ PhotoData FINAL pour slimUser:', normalizedPhotoData ? `PRÉSENT (${normalizedPhotoData.length} chars)` : 'NULL');
            
            // ⚠️⚠️⚠️ CRITIQUE : Créer slimUser exactement comme "Continuer sans vérifier" (ligne 3860-3869)
            const slimUser = {
              id: syncData.user.id || window.currentUser?.id,
              email: syncData.user.email || window.currentUser?.email,
              username: finalUsername, // ⚠️⚠️⚠️ PRIORITÉ ABSOLUE au username du formulaire (comme ligne 3863)
              firstName: syncData.user.firstName || syncData.user.first_name || savedPendingData?.firstName || '',
              lastName: syncData.user.lastName || syncData.user.last_name || savedPendingData?.lastName || '',
              role: syncData.user.role || 'user',
              subscription: syncData.user.subscription || 'free',
              // ⚠️⚠️⚠️ CRITIQUE : PRIORITÉ à profile_photo_url S3 si disponible (uploadée), sinon picture Google
              // photoData (base64) sera utilisé pour l'affichage via getUserAvatar, pas pour profile_photo_url
              profile_photo_url: syncData.user.profile_photo_url || payload.picture || null,
              hasPassword: syncData.user.hasPassword || false,
              hasPostalAddress: syncData.user.hasPostalAddress || false,
              profileComplete: true,
              isLoggedIn: true,
              provider: 'google',
              // INCLURE TOUTES LES DONNÉES DU FORMULAIRE ET DU BACKEND
              postalAddress: syncData.user.postalAddress || syncData.user.postal_address || savedPendingData?.selectedAddress?.label || null,
              addresses: syncData.user.addresses || syncData.user.postal_addresses || (savedPendingData?.selectedAddress ? [{
                label: savedPendingData.selectedAddress.label,
                lat: savedPendingData.selectedAddress.lat,
                lng: savedPendingData.selectedAddress.lng
              }] : []),
              photoData: normalizedPhotoData, // ⚠️⚠️⚠️ PRIORITÉ ABSOLUE au photoData du formulaire (comme ligne 3867)
              avatarId: savedPendingData?.avatarId || syncData.user.avatarId || null
            };
            
            console.log('[OAUTH] ✅✅✅ slimUser créé avec username du FORMULAIRE:', slimUser.username, 'photoData:', slimUser.photoData ? (slimUser.photoData.substring(0, 50) + '...') : 'null', 'photoDataType:', typeof slimUser.photoData, 'photoDataLength:', slimUser.photoData ? slimUser.photoData.length : 0, 'profile_photo_url:', slimUser.profile_photo_url ? (slimUser.profile_photo_url.substring(0, 50) + '...') : 'null');
            
            // ⚠️⚠️⚠️ CRITIQUE : Mettre à jour currentUser AVANT connectUser avec les bonnes valeurs
            if (typeof window !== 'undefined') {
              if (window.currentUser === undefined) {
                window.currentUser = {};
              }
              
              // ⚠️⚠️⚠️ CRITIQUE : Sauvegarder le username et photoData AVANT de les écraser
              const savedUsernameBefore = window.currentUser.username;
              const savedPhotoDataBefore = window.currentUser.photoData;
              
              // ⚠️⚠️⚠️ CRITIQUE : Mettre à jour avec slimUser ET forcer photoData et username
              window.currentUser = { 
                ...window.currentUser, 
                ...slimUser, 
                isLoggedIn: true,
                // ⚠️⚠️⚠️ FORCER photoData si disponible (priorité au formulaire)
                photoData: normalizedPhotoData || savedPhotoDataBefore || slimUser.photoData || null,
                // ⚠️⚠️⚠️ FORCER username si disponible (priorité au formulaire)
                username: finalUsername || savedUsernameBefore || slimUser.username || 'Utilisateur'
              };
              
              // ⚠️⚠️⚠️ VALIDATION FINALE : S'assurer que le username du formulaire est utilisé
              if (finalUsername && finalUsername !== 'Utilisateur' && !finalUsername.includes('@')) {
                window.currentUser.username = finalUsername;
                console.log('[OAUTH] ✅✅✅✅✅ Username FORCÉ dans window.currentUser:', finalUsername);
              }
              
              // S'assurer que photoData est null et non "null" dans currentUser
              if (window.currentUser.photoData === 'null' || window.currentUser.photoData === 'undefined' || window.currentUser.photoData === '') {
                window.currentUser.photoData = null;
              }
              
              // S'assurer que username n'est pas un email ou invalide
              if (window.currentUser.username && (window.currentUser.username.includes('@') || window.currentUser.username === 'null' || window.currentUser.username === '')) {
                window.currentUser.username = finalUsername || 'Utilisateur';
                console.log('[OAUTH] ⚠️ Username invalide remplacé par finalUsername:', finalUsername);
              }
              
              console.log('[OAUTH] ✅✅✅ window.currentUser mis à jour AVANT connectUser:', {
                username: window.currentUser.username,
                finalUsername: finalUsername,
                savedUsernameBefore: savedUsernameBefore,
                photoData: window.currentUser.photoData ? `PRÉSENT (${window.currentUser.photoData.length} chars)` : 'NULL',
                photoDataType: typeof window.currentUser.photoData,
                profile_photo_url: window.currentUser.profile_photo_url ? window.currentUser.profile_photo_url.substring(0, 50) + '...' : 'null'
              });
            }
            
            // ⚠️⚠️⚠️ CRITIQUE : Mettre à jour aussi currentUser global (map_logic.js)
            if (typeof currentUser !== 'undefined') {
              currentUser = {
                ...currentUser,
                ...slimUser,
                isLoggedIn: true,
                photoData: normalizedPhotoData || slimUser.photoData || currentUser.photoData || null,
                username: finalUsername || slimUser.username || currentUser.username || 'Utilisateur'
              };
              // Normaliser photoData
              if (currentUser.photoData === 'null' || currentUser.photoData === 'undefined' || currentUser.photoData === '') {
                currentUser.photoData = null;
              }
              // Normaliser username
              if (currentUser.username && (currentUser.username.includes('@') || currentUser.username === 'null' || currentUser.username === '')) {
                currentUser.username = finalUsername || 'Utilisateur';
              }
            }
            
            // ⚠️⚠️⚠️ CRITIQUE : Forcer photoData et username dans slimUser AVANT connectUser
            // Pour s'assurer que les données du formulaire sont utilisées
            if (normalizedPhotoData && normalizedPhotoData !== 'null' && normalizedPhotoData.length > 100) {
              slimUser.photoData = normalizedPhotoData;
              console.log('[OAUTH] ✅✅✅ photoData FORCÉ dans slimUser avant connectUser:', normalizedPhotoData.substring(0, 50) + '...');
            }
            if (finalUsername && finalUsername !== 'null' && !finalUsername.includes('@')) {
              slimUser.username = finalUsername;
              console.log('[OAUTH] ✅✅✅ username FORCÉ dans slimUser avant connectUser:', finalUsername);
            }
            
            // ⚠️⚠️⚠️ CRITIQUE : Forcer aussi dans window.currentUser AVANT connectUser
            if (typeof window !== 'undefined') {
              if (normalizedPhotoData && normalizedPhotoData !== 'null' && normalizedPhotoData.length > 100) {
                window.currentUser.photoData = normalizedPhotoData;
                console.log('[OAUTH] ✅✅✅ photoData FORCÉ dans window.currentUser avant connectUser');
              }
              if (finalUsername && finalUsername !== 'null' && !finalUsername.includes('@')) {
                window.currentUser.username = finalUsername;
                console.log('[OAUTH] ✅✅✅ username FORCÉ dans window.currentUser avant connectUser');
              }
            }
            
            // ⚠️⚠️⚠️ CRITIQUE : Forcer username et photoData dans slimUser AVANT connectUser
            // Pour s'assurer que les données du formulaire sont bien utilisées
            if (finalUsername && finalUsername !== 'Utilisateur' && !finalUsername.includes('@')) {
              slimUser.username = finalUsername;
              console.log('[OAUTH] ✅✅✅ Username FORCÉ dans slimUser avant connectUser:', finalUsername);
            }
            if (normalizedPhotoData) {
              slimUser.photoData = normalizedPhotoData;
              console.log('[OAUTH] ✅✅✅ PhotoData FORCÉ dans slimUser avant connectUser');
            }
            
            // Demander si l'utilisateur veut rester connecté
            // ⚠️⚠️⚠️ CRITIQUE : Connexion DIRECTE sans demander "rester connecté"
            // La question "rester connecté" sera posée uniquement à la déconnexion
            connectUser(slimUser, tokens, true); // true = rester connecté par défaut
            closeAuthModal();
            
            // ⚠️⚠️⚠️ CRITIQUE : Nettoyer localStorage APRÈS connectUser pour éviter les fuites
            try {
              localStorage.removeItem('pendingRegisterDataForGoogle');
              console.log('[OAUTH] ✅ localStorage nettoyé après connectUser');
            } catch (e) {
              console.error('[OAUTH] ❌ Erreur nettoyage localStorage:', e);
            }
            
            try {
              // ⚠️ OPTIMISATION : Exclure photoData avant sauvegarde
              const userForStorage = removePhotoDataForStorage(slimUser);
              const slimJson = JSON.stringify(userForStorage);
              localStorage.setItem('currentUser', slimJson);
            } catch (e) {
              try { 
                const userForStorage = removePhotoDataForStorage(slimUser);
                sessionStorage.setItem('currentUser', JSON.stringify(userForStorage)); 
              } catch (e2) {}
            }
            
            closeAuthModal();
            if (typeof closePublishModal === 'function') {
              closePublishModal();
            }
            // ⚠️⚠️⚠️ FIX : Utiliser le username du formulaire (déjà dans slimUser.username)
            // Ne PAS utiliser email.split('@')[0] car le username du formulaire a la priorité
            const displayName = slimUser.username || slimUser.firstName || slimUser.email?.split('@')[0] || 'Utilisateur';
            console.log('[OAUTH] ✅ DisplayName pour notification:', displayName, '| Username:', slimUser.username);
            if (typeof showNotification === 'function') {
              showNotification(`✅ Bienvenue ${displayName} ! Vous êtes connecté.`, 'success');
            }
            isGoogleLoginInProgress = false;
            if (typeof window !== 'undefined') {
              window.isGoogleLoginInProgress = false;
            }
            return;
          }
          
          // CAS 1b: Profil marqué complet mais données obligatoires manquantes → FORCER FORMULAIRE
          if (profileComplete === true && missingData.length === 0 && !needsEmailVerification && !hasRequiredDataForExisting) {
            console.log('[OAUTH] ❌ Profil marqué complet mais données obligatoires manquantes - FORCAGE DU FORMULAIRE');
            const missingRequired = existingUserValidation.missingFields;
            if (typeof showNotification === 'function') {
              showNotification(`⚠️ Veuillez compléter les informations obligatoires : ${missingRequired.join(', ')}. L'adresse postale est optionnelle.`, 'warning');
            }
            if (typeof showProRegisterForm === 'function') {
              showProRegisterForm();
            } else if (typeof window.showProRegisterForm === 'function') {
              window.showProRegisterForm();
            }
            isGoogleLoginInProgress = false;
            if (typeof window !== 'undefined') {
              window.isGoogleLoginInProgress = false;
            }
            return; // ⚠️⚠️⚠️ IMPORTANT : Ne pas connecter si données obligatoires manquantes
          }
          
          // CAS 2: Compte existant avec données manquantes
          if (missingData.length > 0) {
            console.log('[OAUTH] Compte existant - Données manquantes:', missingData);
            
            // ⚠️⚠️⚠️ CRITIQUE : Vérifier si ce sont des données obligatoires
            // Utilisation du module de validation pour identifier les champs obligatoires manquants
            const existingValidation = ProfileValidator.validateRequiredFields(
              syncData.user || {},
              {}
            );
            const requiredMissing = existingValidation.missingFields.filter(field => missingData.includes(field));
            const optionalMissing = missingData.filter(field => !existingValidation.missingFields.includes(field));
            
            // Si des données obligatoires manquent → FORCER FORMULAIRE COMPLET
            if (requiredMissing.length > 0) {
              console.log('[OAUTH] ❌ Données obligatoires manquantes - FORCAGE DU FORMULAIRE COMPLET');
              if (typeof showNotification === 'function') {
                showNotification(`⚠️ Veuillez compléter les informations obligatoires : ${requiredMissing.join(', ')}. L'adresse postale est optionnelle.`, 'warning');
              }
              if (typeof showProRegisterForm === 'function') {
                showProRegisterForm();
              } else if (typeof window.showProRegisterForm === 'function') {
                window.showProRegisterForm();
              }
              isGoogleLoginInProgress = false;
              if (typeof window !== 'undefined') {
                window.isGoogleLoginInProgress = false;
              }
              return; // ⚠️⚠️⚠️ IMPORTANT : Ne pas connecter si données obligatoires manquantes
            }
            
            // Si seulement la photo manque → Formulaire photo uniquement
            if (missingData.length === 1 && missingData[0] === 'photo') {
              console.log('[OAUTH] Photo manquante uniquement - Affichage formulaire photo');
              if (typeof showPhotoUploadForm === 'function') {
                showPhotoUploadForm(syncData.user);
              } else if (typeof window.showPhotoUploadForm === 'function') {
                window.showPhotoUploadForm(syncData.user);
              }
              isGoogleLoginInProgress = false;
              return;
            }
            
            // Si seulement des données optionnelles manquent → Formulaire complet pré-rempli (adresse postale)
            console.log('[OAUTH] Données optionnelles manquantes - Affichage formulaire complet pré-rempli');
            if (typeof showNotification === 'function') {
              showNotification(`⚠️ Veuillez compléter les informations manquantes: ${optionalMissing.join(', ')} (optionnel)`, 'info');
            }
            if (typeof showProRegisterForm === 'function') {
              showProRegisterForm();
            } else if (typeof window.showProRegisterForm === 'function') {
              window.showProRegisterForm();
            }
            // Pré-remplir avec les données existantes
            if (syncData.user) {
              registerData = {
                email: syncData.user.email || window.currentUser?.email || '',
                username: syncData.user.username || window.currentUser?.email?.split('@')[0]?.substring(0, 20) || '',
                password: '',
                passwordConfirm: '',
                firstName: syncData.user.firstName || syncData.user.first_name || window.currentUser?.name?.split(' ')[0] || '',
                lastName: syncData.user.lastName || syncData.user.last_name || window.currentUser?.name?.split(' ').slice(1).join(' ') || '',
                profilePhoto: syncData.user.profile_photo_url || payload.picture || '',
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
            }
            isGoogleLoginInProgress = false;
            return;
          }
          
          // CAS 3: Compte existant, profil complet, besoin confirmation email
          if (needsEmailVerification && profileComplete) {
            console.log('[OAUTH] Compte existant - Confirmation email requise');
            const slimUser = {
              id: syncData.user.id || window.currentUser?.id,
              email: syncData.user.email || window.currentUser?.email,
              username: syncData.user.username || window.currentUser?.email?.split('@')[0]?.substring(0, 20) || 'Utilisateur',
              firstName: syncData.user.firstName || syncData.user.first_name || window.currentUser?.name?.split(' ')[0] || '',
              lastName: syncData.user.lastName || syncData.user.last_name || window.currentUser?.name?.split(' ').slice(1).join(' ') || '',
              role: syncData.user.role || 'user',
              subscription: syncData.user.subscription || 'free',
              profile_photo_url: syncData.user.profile_photo_url || payload.picture || null,
              hasPassword: syncData.user.hasPassword || false,
              hasPostalAddress: syncData.user.hasPostalAddress || false,
              profileComplete: true,
              isLoggedIn: true
            };
            
            if (typeof window !== 'undefined' && window.currentUser !== undefined) {
              window.currentUser = { ...window.currentUser, ...slimUser, isLoggedIn: true };
            }
            updateAuthUI(slimUser);
            
            try {
              // ⚠️ OPTIMISATION : Exclure photoData avant sauvegarde
              const userForStorage = removePhotoDataForStorage(slimUser);
              const slimJson = JSON.stringify(userForStorage);
              localStorage.setItem('currentUser', slimJson);
            } catch (e) {
              try { 
                const userForStorage = removePhotoDataForStorage(slimUser);
                sessionStorage.setItem('currentUser', JSON.stringify(userForStorage)); 
              } catch (e2) {}
            }
            
            // Afficher modal confirmation email
            if (typeof showEmailVerificationModal === 'function') {
              showEmailVerificationModal(syncData.user.email, syncData.user.username || 'Utilisateur');
            } else if (typeof window.showEmailVerificationModal === 'function') {
              window.showEmailVerificationModal(syncData.user.email, syncData.user.username || 'Utilisateur');
            }
            isGoogleLoginInProgress = false;
            return;
          }
          
          // CAS 4: Fallback → Connexion directe
          console.log('[OAUTH] Fallback - Connexion directe');
          const slimUser = {
            id: syncData.user.id || window.currentUser?.id,
            email: syncData.user.email || window.currentUser?.email,
            username: syncData.user.username || window.currentUser?.email?.split('@')[0]?.substring(0, 20) || 'Utilisateur',
            firstName: syncData.user.firstName || syncData.user.first_name || window.currentUser?.name?.split(' ')[0] || '',
            lastName: syncData.user.lastName || syncData.user.last_name || window.currentUser?.name?.split(' ').slice(1).join(' ') || '',
            role: syncData.user.role || 'user',
            subscription: syncData.user.subscription || 'free',
            profile_photo_url: syncData.user.profile_photo_url || payload.picture || null,
            hasPassword: syncData.user.hasPassword || false,
            hasPostalAddress: syncData.user.hasPostalAddress || false,
            profileComplete: profileComplete,
            isLoggedIn: true
          };
          
          if (typeof window !== 'undefined' && window.currentUser !== undefined) {
            window.currentUser = { ...window.currentUser, ...slimUser, isLoggedIn: true };
          }
          updateAuthUI(slimUser);
          
          try {
            const slimJson = JSON.stringify(slimUser);
            localStorage.setItem('currentUser', slimJson);
          } catch (e) {
            try { sessionStorage.setItem('currentUser', slimJson); } catch (e2) {}
          }
          
          closeAuthModal();
          if (typeof closePublishModal === 'function') {
            closePublishModal();
          }
          const displayName = slimUser.username || slimUser.firstName || slimUser.email?.split('@')[0] || 'Utilisateur';
          if (typeof showNotification === 'function') {
            showNotification(`✅ Bienvenue ${displayName} !`, 'success');
          }
          isGoogleLoginInProgress = false;
          return;
        } else {
          // Fallback si syncData.ok est false ou syncData.user est manquant
          console.warn('⚠️ Réponse backend invalide, connexion avec données Google uniquement');
          
          const slimUser = {
            id: window.currentUser?.id || `user_${Date.now()}`,
            email: window.currentUser?.email || payload.email,
            username: window.currentUser?.email?.split('@')[0]?.substring(0, 20) || 'Utilisateur',
            firstName: window.currentUser?.name?.split(' ')[0] || '',
            lastName: window.currentUser?.name?.split(' ').slice(1).join(' ') || '',
            role: 'user',
            subscription: 'free',
            profile_photo_url: payload.picture || null,
            hasPassword: false,
            hasPostalAddress: false,
            profileComplete: false,
            isLoggedIn: true
          };
          
          if (typeof window !== 'undefined' && window.currentUser !== undefined) {
            window.currentUser = { ...window.currentUser, ...slimUser, isLoggedIn: true };
          }
          updateAuthUI(slimUser);
          
          try {
            const slimJson = JSON.stringify(slimUser);
            localStorage.setItem('currentUser', slimJson);
          } catch (e) {
            try {
              sessionStorage.setItem('currentUser', slimJson);
            } catch (e2) {
              console.warn('⚠️ Impossible de sauvegarder user');
            }
          }
          
          closeAuthModal();
          if (typeof closePublishModal === 'function') {
            closePublishModal();
          }
          if (typeof showNotification === 'function') {
            showNotification('✅ Connexion Google réussie !', 'success');
          }
          isGoogleLoginInProgress = false;
        }
      } else {
        throw new Error(`Backend sync failed: ${syncResponse.status}`);
      }
    } catch (apiError) {
      console.warn('⚠️ Erreur lors de l\'appel API backend:', apiError);
      
      // ⚠️⚠️⚠️ CRITIQUE : Ne pas basculer en mode "backend indisponible" si c'est une erreur 401
      // Une erreur 401 signifie que le backend est disponible mais l'utilisateur n'est pas authentifié
      if (apiError.message && apiError.message.includes('Authentication failed')) {
        console.error('❌ Erreur d\'authentification - Le backend est disponible mais l\'utilisateur n\'est pas authentifié');
        if (typeof showNotification === 'function') {
          showNotification('❌ Erreur d\'authentification. Veuillez réessayer.', 'error');
        }
        isGoogleLoginInProgress = false;
        if (typeof window !== 'undefined') {
          window.isGoogleLoginInProgress = false;
        }
        return; // Ne pas basculer en mode "backend indisponible"
      }
      
      // VÉRIFIER SI LE PROFIL EST DÉJÀ COMPLET
      const savedUser = localStorage.getItem('currentUser');
      let savedUserObj = null;
      try {
        if (savedUser) {
          savedUserObj = JSON.parse(savedUser);
        }
      } catch (e) {
        console.warn('⚠️ Impossible de parser currentUser depuis localStorage:', e);
      }
      
      const isProfileComplete = (savedUserObj && savedUserObj.profileComplete === true) || 
                                 (window.currentUser && window.currentUser.profileComplete === true);
      
      if (isProfileComplete) {
        console.log('✅ Profil déjà complet - Connexion directe sans formulaire (fallback)');
        if (savedUserObj) {
          if (typeof window !== 'undefined' && window.currentUser !== undefined) {
            window.currentUser = {
              ...window.currentUser,
              ...savedUserObj,
              isLoggedIn: true,
              profileComplete: true
            };
          }
        } else {
          if (typeof window !== 'undefined' && window.currentUser !== undefined) {
            window.currentUser.profileComplete = true;
            window.currentUser.isLoggedIn = true;
          }
        }
        const slimUser = saveUserSlim(window.currentUser);
        if (slimUser) {
          safeSetItem("currentUser", JSON.stringify(slimUser));
        }
        if (typeof showNotification === 'function') {
          showNotification(`✅ Connexion réussie ! Bienvenue ${window.currentUser?.name || window.currentUser?.email}`, "success");
        }
        
        if (window.history && window.history.replaceState) {
          window.history.replaceState({}, document.title, window.location.pathname);
        }
        
        if (typeof closePublishModal === 'function') {
          closePublishModal();
        }
        return;
      }
      
      // FLOW SIMPLIFIÉ : Se connecter quand même avec les données Google disponibles
      console.log('✅ Connexion avec données Google uniquement (backend indisponible)');
      
      // ⚠️⚠️⚠️ CRITIQUE : Récupérer le username du formulaire s'il existe
      let savedPendingData = null;
      try {
        savedPendingData = localStorage.getItem('pendingRegisterDataForGoogle');
        if (savedPendingData) {
          savedPendingData = JSON.parse(savedPendingData);
        } else {
          savedPendingData = sessionStorage.getItem('pendingRegisterDataForGoogle');
          if (savedPendingData) {
            savedPendingData = JSON.parse(savedPendingData);
          } else if (window.pendingRegisterData) {
            savedPendingData = window.pendingRegisterData;
          }
        }
      } catch (e) {
        console.error('[OAUTH] ❌ Erreur récupération username du formulaire:', e);
      }
      
      console.log('[OAUTH] 🔍 DEBUG username (sans backend) - savedPendingData:', savedPendingData);
      console.log('[OAUTH] 🔍 DEBUG username (sans backend) - window.currentUser.username:', window.currentUser?.username);
      console.log('[OAUTH] 🔍 DEBUG username (sans backend) - payload.name:', payload?.name);
      
      // ⚠️⚠️⚠️ PRIORITÉ ABSOLUE au username du formulaire (savedPendingData, puis window.currentUser, puis module)
      let finalUsername = savedPendingData?.username;
      
      // Si le username du formulaire n'est pas trouvé, vérifier dans window.currentUser
      if (!finalUsername || finalUsername === 'null' || finalUsername === '' || finalUsername.includes('@')) {
        if (window.currentUser?.username && 
            window.currentUser.username !== 'null' && 
            window.currentUser.username !== '' && 
            !window.currentUser.username.includes('@')) {
          finalUsername = window.currentUser.username;
          console.log('[OAUTH] ✅ Username récupéré depuis window.currentUser:', finalUsername);
        } else {
          console.warn('[OAUTH] ⚠️ Username du formulaire invalide, utilisation du module');
          finalUsername = ProfileValidator.getValidUsername(
            window.currentUser || {},
            savedPendingData || {},
            payload
          );
        }
      } else {
        console.log('[OAUTH] ✅ Username récupéré depuis savedPendingData:', finalUsername);
      }
      
      console.log('[OAUTH] ✅✅✅ Username final récupéré (sans backend):', finalUsername);
      
      const slimUser = {
        id: window.currentUser?.id || `user_${Date.now()}`,
        email: window.currentUser?.email || payload.email,
        username: finalUsername, // ⚠️⚠️⚠️ PRIORITÉ ABSOLUE au username du formulaire
        firstName: window.currentUser?.name?.split(' ')[0] || payload.given_name || '',
        lastName: window.currentUser?.name?.split(' ').slice(1).join(' ') || payload.family_name || '',
        role: 'user',
        subscription: 'free',
        profile_photo_url: payload.picture || null,
        hasPassword: false,
        hasPostalAddress: false,
        profileComplete: false,
        isLoggedIn: true
      };
      
      console.log('[OAUTH] ✅✅✅ slimUser créé avec username:', slimUser.username);
      
      // ⚠️⚠️⚠️ CRITIQUE : Forcer le username dans window.currentUser AVANT updateAuthUI
      if (typeof window !== 'undefined') {
        if (window.currentUser === undefined) {
          window.currentUser = {};
        }
        // ⚠️ PRIORITÉ ABSOLUE au username du formulaire
        window.currentUser = { 
          ...window.currentUser, 
          ...slimUser, 
          username: finalUsername, // ⚠️⚠️⚠️ FORCER le username du formulaire
          isLoggedIn: true 
        };
        console.log('[OAUTH] ✅✅✅ window.currentUser.username FORCÉ à:', window.currentUser.username);
      }
      
      // ⚠️⚠️⚠️ CRITIQUE : Forcer le username dans slimUser AVANT updateAuthUI (au cas où)
      slimUser.username = finalUsername;
      console.log('[OAUTH] ✅✅✅ slimUser.username FORCÉ à:', slimUser.username);
      
      updateAuthUI(slimUser);
      
      // ⚠️⚠️⚠️ CRITIQUE : Re-forcer le username APRÈS updateAuthUI et sauvegarder
      // updateAuthUI peut avoir modifié window.currentUser, donc on re-force le username
      if (window.currentUser) {
        const usernameBefore = window.currentUser.username;
        window.currentUser.username = finalUsername; // ⚠️ FORCER à nouveau après updateAuthUI
        console.log('[OAUTH] ✅✅✅ window.currentUser.username RE-FORCÉ:', usernameBefore, '→', window.currentUser.username);
      }
      
      // ⚠️⚠️⚠️ CRITIQUE : Sauvegarder dans localStorage/sessionStorage avec le username du formulaire
      try {
        // Utiliser window.currentUser qui contient maintenant le bon username
        const userToSave = { ...window.currentUser };
        userToSave.username = finalUsername; // ⚠️ FORCER le username du formulaire
        const slimJson = JSON.stringify(saveUserSlim(userToSave));
        localStorage.setItem('currentUser', slimJson);
        console.log('[OAUTH] ✅✅✅ currentUser sauvegardé dans localStorage avec username:', finalUsername);
        console.log('[OAUTH] 🔍 Vérification: localStorage.currentUser.username =', JSON.parse(localStorage.getItem('currentUser')).username);
      } catch (e) {
        try {
          const userToSave = { ...window.currentUser };
          userToSave.username = finalUsername; // ⚠️ FORCER le username du formulaire
          const slimJson = JSON.stringify(saveUserSlim(userToSave));
          sessionStorage.setItem('currentUser', slimJson);
          console.log('[OAUTH] ✅✅✅ currentUser sauvegardé dans sessionStorage avec username:', finalUsername);
        } catch (e2) {
          console.warn('⚠️ Impossible de sauvegarder user');
        }
      }
      
      closeAuthModal();
      if (typeof closePublishModal === 'function') {
        closePublishModal();
      }
      if (typeof showNotification === 'function') {
        const displayName = slimUser.username || slimUser.firstName || slimUser.email?.split('@')[0] || 'Utilisateur';
        console.log('[OAUTH] ✅ DisplayName pour notification (sans backend):', displayName, '| Username:', slimUser.username);
        showNotification(`✅ Bienvenue ${displayName} ! Vous êtes connecté.`, 'success');
      }
      isGoogleLoginInProgress = false;
    }
  } catch (e) {
    console.warn(e);
    if (typeof showNotification === 'function') {
      showNotification("✅ Connecté (token reçu).", "success");
    }
  }
}

// ===============================
// UTILITAIRES REGISTER
// ===============================
function showError(elementId, message) {
  const el = document.getElementById(elementId);
  if (el) {
    el.textContent = message;
  }
}

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
        <button onclick="closeAuthModal(); setTimeout(() => { if(typeof openAuthModal==='function')openAuthModal('register'); const el = document.getElementById('register-email'); if (el && '${email}') el.value = '${email}'; const el2 = document.getElementById('register-username'); if (el2 && '${username}') el2.value = '${username}'; }, 200);" style="width:100%;padding:14px;border-radius:12px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:700;font-size:15px;cursor:pointer;">
          🔄 Réessayer
        </button>
        <button onclick="closeAuthModal(); setTimeout(() => { if(typeof openAuthModal==='function')openAuthModal('login'); }, 200);" style="width:100%;padding:14px;border-radius:12px;border:2px solid rgba(255,255,255,0.2);background:transparent;color:#fff;font-weight:600;font-size:15px;cursor:pointer;">
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
          <button onclick="closeAuthModal(); setTimeout(() => { if(typeof openAuthModal==='function')openAuthModal('login'); setTimeout(() => { const el = document.getElementById('login-email'); if (el && '${email}') el.value = '${email}'; }, 300); }, 200);" style="width:100%;padding:14px;border-radius:12px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:700;font-size:15px;cursor:pointer;">
            🔐 Se connecter
          </button>
          <button onclick="if(typeof showNotification==='function')showNotification('Fonctionnalité à venir', 'info')" style="width:100%;padding:12px;border-radius:12px;border:none;background:transparent;color:var(--ui-text-muted);font-weight:500;font-size:14px;cursor:pointer;">
            🔑 Mot de passe oublié
          </button>
        ` : `
          <button onclick="closeAuthModal(); setTimeout(() => { if(typeof openAuthModal==='function')openAuthModal('register'); }, 200);" style="width:100%;padding:14px;border-radius:12px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:700;font-size:15px;cursor:pointer;">
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

function updatePostalAddressRequired() {
  const skipAddress = document.getElementById('pro-skip-address')?.checked || false;
  const addressInput = document.getElementById('pro-postal-address');
  if (addressInput) {
    if (skipAddress) {
      addressInput.removeAttribute('required');
      addressInput.disabled = true;
      addressInput.style.opacity = '0.5';
      addressInput.style.cursor = 'not-allowed';
      registerData.postalAddress = '';
      showError('pro-postal-address-error', '');
    } else {
      addressInput.setAttribute('required', 'required');
      addressInput.disabled = false;
      addressInput.style.opacity = '1';
      addressInput.style.cursor = 'text';
      if (addressInput.value) {
        if (typeof validateProField === 'function') {
          validateProField('postalAddress', addressInput.value);
        } else if (typeof window.validateProField === 'function') {
          window.validateProField('postalAddress', addressInput.value);
        }
      }
    }
  }
}

// Fonction pour vérifier le code après création de compte
async function verifyEmailCodeAfterRegister(email, code) {
  try {
    const feedbackEl = document.getElementById('email-code-feedback');
    const codeInput = document.getElementById('email-verification-code');
    
    if (!code || code.length !== 6) {
      if (feedbackEl) {
        feedbackEl.textContent = '⚠️ Veuillez entrer les 6 chiffres';
        feedbackEl.style.color = '#ef4444';
      }
      return;
    }
    
    if (feedbackEl) {
      feedbackEl.textContent = '⏳ Vérification en cours...';
      feedbackEl.style.color = 'var(--ui-text-muted)';
    }
    
    // Vérifier le code via le backend
    const response = await fetch(`${API_BASE_URL}/user/verify-email`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, code })
    });
    
    const data = await response.json();
    
    if (response.ok && data.success) {
      if (feedbackEl) {
        feedbackEl.textContent = '✅ Code vérifié avec succès !';
        feedbackEl.style.color = '#22c55e';
      }
      if (codeInput) {
        codeInput.style.borderColor = '#22c55e';
        codeInput.style.background = 'rgba(34,197,94,0.1)';
      }
      
      if (typeof showNotification === 'function') {
        showNotification('✅ Email vérifié ! Connexion en cours...', 'success');
      }
      
      // Connecter l'utilisateur automatiquement après vérification
      setTimeout(async () => {
        const pendingData = window.pendingRegisterData;
        if (pendingData && typeof performLogin === 'function') {
          await performLogin(pendingData.email, pendingData.password, true);
          closeAuthModal();
        }
      }, 1000);
    } else {
      if (feedbackEl) {
        feedbackEl.textContent = data.error || '❌ Code incorrect';
        feedbackEl.style.color = '#ef4444';
      }
      if (codeInput) {
        codeInput.style.borderColor = '#ef4444';
        setTimeout(() => {
          codeInput.value = '';
          codeInput.style.borderColor = 'rgba(255,255,255,0.1)';
        }, 1000);
      }
    }
  } catch (error) {
    console.error('[VERIFY] Erreur vérification code:', error);
    const feedbackEl = document.getElementById('email-code-feedback');
    if (feedbackEl) {
      feedbackEl.textContent = '❌ Erreur lors de la vérification';
      feedbackEl.style.color = '#ef4444';
    }
  }
}

// Exposer globalement
window.startGoogleLogin = startGoogleLogin;
window.closeAuthModal = closeAuthModal;
window.loadSavedUser = loadSavedUser;
window.logout = logout;
window.performLogout = performLogout;
window.askRememberMeOnLogout = askRememberMeOnLogout;
window.openAuthModal = openAuthModal;
window.openLoginModal = openLoginModal;
window.openRegisterModal = openRegisterModal;
window.performLogin = performLogin;
window.performRegister = performRegister;
window.verifyEmailCodeAfterRegister = verifyEmailCodeAfterRegister;
window.handleCognitoCallbackIfPresent = handleCognitoCallbackIfPresent;
window.getAuthToken = getAuthToken;
window.getRefreshToken = getRefreshToken;
window.setAuthTokens = setAuthTokens;
window.decodeJwtPayload = decodeJwtPayload;
window.showError = showError;
window.showRegisterTimeoutError = showRegisterTimeoutError;
// ===============================
// GESTION "RESTER CONNECTÉ"
// ===============================

function askRememberMeAndConnect(user, tokens) {
  // ⚠️⚠️⚠️ PROTECTION : Connexion directe sans modal (cette fonction ne doit pas être appelée après inscription/connexion)
  // VERSION CORRIGÉE 2026-01-16 00:05 - Cette fonction ne doit JAMAIS afficher le modal après inscription/connexion
  // Le modal "rester connecté" ne doit apparaître QUE lors de la déconnexion (via askRememberMeOnLogout)
  console.error('[REMEMBER] ⚠️⚠️⚠️ VERSION CORRIGÉE 2026-01-16 00:05 - askRememberMeAndConnect appelée - Connexion directe sans modal');
  console.error('[REMEMBER] ⚠️ Si vous voyez ce message, la bonne version est chargée');
  console.error('[REMEMBER] ⚠️ Cette fonction ne doit JAMAIS afficher de modal - Connexion directe uniquement');
  connectUser(user, tokens, true);
}

function connectUser(user, tokens, rememberMe) {
  // ⚠️⚠️⚠️ VERSION 2026-01-16 11:26 - normalizedPhotoData défini au début
  console.log('[CONNECT] ✅✅✅ VERSION 2026-01-16 11:26 - connectUser avec normalizedPhotoData corrigé');
  
  // ⚠️ PROTECTION : Vérifier que user existe
  if (!user) {
    console.error('[CONNECT] ❌ ERREUR: user est null ou undefined');
    return;
  }
  
  // ⚠️⚠️⚠️ CRITIQUE : Récupérer le username du formulaire depuis localStorage/sessionStorage (PRIORITÉ ABSOLUE)
  // C'est la source de vérité pour le username du formulaire
  let photoDataFromCurrentUser = null;
  let usernameFromCurrentUser = null;
  
  // 1. Vérifier localStorage d'abord (source de vérité)
  try {
    const pendingData = localStorage.getItem('pendingRegisterDataForGoogle');
    if (pendingData) {
      const parsed = JSON.parse(pendingData);
      if (parsed.username && parsed.username !== 'null' && parsed.username !== '' && !parsed.username.includes('@')) {
        usernameFromCurrentUser = parsed.username;
        console.log('[CONNECT] ✅✅✅ Username du formulaire trouvé dans localStorage:', usernameFromCurrentUser);
      }
      if (parsed.photoData && parsed.photoData !== 'null' && parsed.photoData !== 'undefined' && parsed.photoData.length > 100) {
        photoDataFromCurrentUser = parsed.photoData;
        console.log('[CONNECT] ✅✅✅ photoData trouvé dans localStorage (priorité formulaire)');
      }
    }
  } catch(e) {
    console.error('[CONNECT] ❌ Erreur récupération localStorage:', e);
  }
  
  // 2. Vérifier sessionStorage si pas trouvé
  if (!usernameFromCurrentUser) {
    try {
      const pendingData = sessionStorage.getItem('pendingRegisterDataForGoogle');
      if (pendingData) {
        const parsed = JSON.parse(pendingData);
        if (parsed.username && parsed.username !== 'null' && parsed.username !== '' && !parsed.username.includes('@')) {
          usernameFromCurrentUser = parsed.username;
          console.log('[CONNECT] ✅✅✅ Username du formulaire trouvé dans sessionStorage:', usernameFromCurrentUser);
        }
        if (!photoDataFromCurrentUser && parsed.photoData && parsed.photoData !== 'null' && parsed.photoData !== 'undefined' && parsed.photoData.length > 100) {
          photoDataFromCurrentUser = parsed.photoData;
          console.log('[CONNECT] ✅✅✅ photoData trouvé dans sessionStorage (priorité formulaire)');
        }
      }
    } catch(e) {
      console.error('[CONNECT] ❌ Erreur récupération sessionStorage:', e);
    }
  }
  
  // 3. Vérifier window.currentUser si toujours pas trouvé
  if (!usernameFromCurrentUser && typeof window !== 'undefined' && window.currentUser) {
    if (window.currentUser.photoData && window.currentUser.photoData !== 'null' && window.currentUser.photoData !== 'undefined' && window.currentUser.photoData.length > 100) {
      photoDataFromCurrentUser = window.currentUser.photoData;
      console.log('[CONNECT] ✅✅✅ photoData trouvé dans window.currentUser (priorité formulaire)');
    }
    if (window.currentUser.username && window.currentUser.username !== 'null' && !window.currentUser.username.includes('@')) {
      usernameFromCurrentUser = window.currentUser.username;
      console.log('[CONNECT] ✅✅✅ username trouvé dans window.currentUser (priorité formulaire):', usernameFromCurrentUser);
    }
  }
  
  // 4. ⚠️⚠️⚠️ CRITIQUE : Vérifier localStorage.currentUser (username sauvegardé lors de l'inscription précédente)
  // C'est la source de vérité pour un compte EXISTANT qui se reconnecte
  if (!usernameFromCurrentUser) {
    try {
      const savedCurrentUser = localStorage.getItem('currentUser') || sessionStorage.getItem('currentUser');
      if (savedCurrentUser) {
        const parsed = JSON.parse(savedCurrentUser);
        if (parsed.username && parsed.username !== 'null' && parsed.username !== '' && !parsed.username.includes('@') && parsed.username !== 'Utilisateur') {
          usernameFromCurrentUser = parsed.username;
          console.log('[CONNECT] ✅✅✅ Username récupéré depuis localStorage.currentUser (compte existant):', usernameFromCurrentUser);
        }
      }
    } catch(e) {
      console.error('[CONNECT] ❌ Erreur récupération localStorage.currentUser:', e);
    }
  }
  
  // ⚠️ CRITIQUE : Normaliser photoData AU DÉBUT - PRIORITÉ à window.currentUser (formulaire), puis user
  let normalizedPhotoData = photoDataFromCurrentUser || user.photoData || null;
  if (normalizedPhotoData === 'null' || normalizedPhotoData === 'undefined' || normalizedPhotoData === '' || !normalizedPhotoData) {
    normalizedPhotoData = null;
  }
  
  // ⚠️ CRITIQUE : Normaliser username - PRIORITÉ à window.currentUser (formulaire), puis user
  // ⚠️⚠️⚠️ NE JAMAIS utiliser l'email comme username affiché
  let finalUsername = usernameFromCurrentUser || user.username || null;
  if (!finalUsername || finalUsername === 'null' || finalUsername === '' || finalUsername.includes('@') || finalUsername === 'Utilisateur') {
    // Ne PAS utiliser l'email - garder null pour que getUserDisplayName affiche "Compte"
    console.warn('[CONNECT] ⚠️ Username invalide, on garde la valeur du user.username du backend:', user.username);
    // Si user.username du backend est valide (pas un email), l'utiliser
    if (user.username && user.username !== 'null' && user.username !== '' && !user.username.includes('@')) {
      finalUsername = user.username;
    } else {
      // Sinon, ne PAS fallback sur email - utiliser null (getUserDisplayName affichera "Compte")
      finalUsername = null;
      console.warn('[CONNECT] ⚠️ Aucun username valide trouvé - getUserDisplayName affichera "Compte"');
    }
  }
  
  // ⚠️⚠️⚠️ CRITIQUE : Forcer photoData et username dans user AVANT traitement
  if (normalizedPhotoData && normalizedPhotoData.length > 100) {
    user.photoData = normalizedPhotoData;
    console.log('[CONNECT] ✅✅✅ photoData FORCÉ dans user:', normalizedPhotoData.substring(0, 50) + '...');
  }
  if (finalUsername && !finalUsername.includes('@')) {
    user.username = finalUsername;
    console.log('[CONNECT] ✅✅✅ username FORCÉ dans user:', finalUsername);
  }
  
  console.log('[CONNECT] Connexion utilisateur, rememberMe:', rememberMe);
  console.log('[CONNECT] ✅ normalizedPhotoData défini:', normalizedPhotoData ? `PRÉSENT (${normalizedPhotoData.length} chars)` : 'NULL');
  console.log('[CONNECT] ✅ finalUsername défini:', finalUsername);
  console.log('[CONNECT] Données utilisateur reçues:', { 
    firstName: user.firstName, 
    lastName: user.lastName, 
    username: user.username,
    photoData: user.photoData ? `PRÉSENT (${user.photoData.length} chars)` : 'NULL',
    profile_photo_url: user.profile_photo_url ? user.profile_photo_url.substring(0, 50) + '...' : 'null'
  });
  
  // Sauvegarder les tokens selon le choix
  if (tokens && tokens.access_token) {
    setAuthTokens(tokens.access_token, tokens.refresh_token || '', rememberMe);
  }
  
  // Sauvegarder l'utilisateur - s'assurer que toutes les propriétés sont incluses
  if (typeof window !== 'undefined') {
    if (window.currentUser === undefined) {
      window.currentUser = {};
    }
    
    window.currentUser = { 
      ...window.currentUser, 
      ...user, 
      isLoggedIn: true,
      // S'assurer que TOUTES les données sont incluses
      profile_photo_url: user.profile_photo_url || window.currentUser.profile_photo_url || null,
      firstName: user.firstName || window.currentUser.firstName || null,
      lastName: user.lastName || window.currentUser.lastName || null,
      username: finalUsername || user.username || window.currentUser.username || null, // ⚠️⚠️⚠️ PRIORITÉ au username du formulaire (finalUsername)
      postalAddress: user.postalAddress || window.currentUser.postalAddress || null,
      addresses: user.addresses || window.currentUser.addresses || [],
      photoData: normalizedPhotoData, // ⚠️⚠️⚠️ Utiliser photoData normalisé
      avatarId: user.avatarId || window.currentUser.avatarId || null
    };
    
    console.log('[CONNECT] ⚠️⚠️⚠️ currentUser mis à jour avec username:', window.currentUser.username, 'photoData:', window.currentUser.photoData ? 'PRÉSENT' : 'NULL');
  }
  
  // Sauvegarder dans le storage selon le choix
  // ⚠️⚠️⚠️ OPTIMISATION STOCKAGE : Créer une version sans photoData (base64) pour localStorage
  try {
    // Créer une copie sans photoData pour éviter de remplir localStorage
    const userForStorage = { ...user };
    delete userForStorage.photoData; // Supprimer photoData (base64) avant sauvegarde
    
    const slimJson = JSON.stringify(userForStorage);
    if (rememberMe) {
      localStorage.setItem('currentUser', slimJson);
      localStorage.setItem('rememberMe', 'true');
    } else {
      sessionStorage.setItem('currentUser', slimJson);
      sessionStorage.setItem('rememberMe', 'false');
      localStorage.removeItem('rememberMe');
      localStorage.removeItem('currentUser');
    }
    console.log('[CONNECT] ✅ Utilisateur sauvegardé (photoData exclu pour optimiser stockage)');
  } catch (e) {
    console.warn('[CONNECT] Erreur sauvegarde utilisateur:', e);
  }
  
  // Mettre à jour l'UI - CRÉER UN OBJET SLIM POUR updateAuthUI
  // ⚠️⚠️⚠️ CRITIQUE : Utiliser finalUsername et normalizedPhotoData (priorité formulaire)
  const slimUser = {
    id: user.id,
    email: user.email,
    username: finalUsername || user.username || 'Utilisateur', // ⚠️⚠️⚠️ PRIORITÉ au username du formulaire
    firstName: user.firstName || '',
    lastName: user.lastName || '',
    profile_photo_url: user.profile_photo_url || null,
    photoData: normalizedPhotoData, // ⚠️⚠️⚠️ PRIORITÉ au photoData du formulaire
    isLoggedIn: true
  };
  
  console.log('[CONNECT] ✅✅✅ slimUser créé pour updateAuthUI:', {
    username: slimUser.username,
    photoData: slimUser.photoData ? `PRÉSENT (${slimUser.photoData.length} chars)` : 'NULL'
  });
  
  // ⚠️⚠️⚠️ CRITIQUE : Synchroniser la variable globale currentUser dans map_logic.js
  // Cette variable est utilisée par les popups et doit avoir toutes les propriétés nécessaires
  try {
    // Essayer d'accéder à la variable globale currentUser dans map_logic.js
    // Si elle existe, la mettre à jour en préservant les propriétés existantes
    if (typeof window !== 'undefined') {
      // Vérifier si currentUser existe dans le scope global (via eval ou window)
      // Si getDefaultUser existe, l'utiliser pour initialiser les propriétés manquantes
      if (typeof window.getDefaultUser === 'function') {
        const defaultUser = window.getDefaultUser();
        // Mettre à jour currentUser en préservant les propriétés existantes
        if (typeof window.currentUser === 'undefined' || !window.currentUser) {
          window.currentUser = defaultUser;
        }
        // S'assurer que toutes les propriétés nécessaires existent
        window.currentUser = {
          ...defaultUser, // Propriétés par défaut (favorites, agenda, likes, etc.)
          ...window.currentUser, // Propriétés existantes préservées
          ...user, // Nouvelles données utilisateur
          ...slimUser, // Données slim (username, photoData, etc.)
          isLoggedIn: true,
          username: finalUsername || user.username || window.currentUser.username || 'Utilisateur',
          photoData: normalizedPhotoData || window.currentUser.photoData || null
        };
        console.log('[CONNECT] ✅✅✅ Variable globale currentUser synchronisée avec toutes les propriétés');
      } else {
        // Si getDefaultUser n'existe pas, initialiser manuellement les propriétés nécessaires
        if (typeof window.currentUser === 'undefined' || !window.currentUser) {
          window.currentUser = {
            isLoggedIn: false,
            favorites: [],
            agenda: [],
            likes: [],
            participating: [],
            subscription: 'free'
          };
        }
        // S'assurer que toutes les propriétés nécessaires existent
        if (!Array.isArray(window.currentUser.favorites)) {
          window.currentUser.favorites = [];
        }
        if (!Array.isArray(window.currentUser.agenda)) {
          window.currentUser.agenda = [];
        }
        if (!Array.isArray(window.currentUser.likes)) {
          window.currentUser.likes = [];
        }
        if (!Array.isArray(window.currentUser.participating)) {
          window.currentUser.participating = [];
        }
        if (!window.currentUser.subscription) {
          window.currentUser.subscription = 'free';
        }
        // ⚠️⚠️⚠️ CRITIQUE : S'assurer que reviews est un objet (pas undefined)
        if (!window.currentUser.reviews || typeof window.currentUser.reviews !== 'object') {
          window.currentUser.reviews = {};
        }
        // Mettre à jour avec les nouvelles données
        window.currentUser = {
          ...window.currentUser,
          ...user,
          ...slimUser,
          isLoggedIn: true,
          username: finalUsername || user.username || window.currentUser.username || 'Utilisateur',
          photoData: normalizedPhotoData || window.currentUser.photoData || null
        };
        console.log('[CONNECT] ✅✅✅ Variable globale currentUser synchronisée (sans getDefaultUser)');
      }
      
      // ⚠️⚠️⚠️ CRITIQUE : Essayer de synchroniser aussi la variable globale currentUser dans map_logic.js
      // Si map_logic.js expose une fonction pour mettre à jour currentUser, l'utiliser
      if (typeof window.syncCurrentUser === 'function') {
        window.syncCurrentUser(window.currentUser);
      }
    }
  } catch (e) {
    console.warn('[CONNECT] ⚠️ Erreur synchronisation currentUser:', e);
  }
  
  console.log('[CONNECT] ⚠️⚠️⚠️ Appel updateAuthUI avec slimUser:', slimUser);
  if (typeof updateAuthUI === 'function') {
    updateAuthUI(slimUser);
  } else {
    console.warn('[CONNECT] ⚠️ updateAuthUI non disponible');
  }
  
  // Mettre à jour les boutons
  if (typeof updateAuthButtons === 'function') {
    updateAuthButtons();
  }
  
  // Mettre à jour le bloc compte - FORCER plusieurs fois pour s'assurer
  if (typeof window.updateAccountBlockLegitimately === 'function') {
    window.updateAccountBlockLegitimately();
    setTimeout(() => {
      if (typeof window.updateAccountBlockLegitimately === 'function') {
        window.updateAccountBlockLegitimately();
      }
    }, 100);
    setTimeout(() => {
      if (typeof window.updateAccountBlockLegitimately === 'function') {
        window.updateAccountBlockLegitimately();
      }
    }, 500);
  } else {
    console.warn('[CONNECT] ⚠️ window.updateAccountBlockLegitimately non disponible');
  }
  
  // Fermer les modals
  if (typeof closeAuthModal === 'function') {
    closeAuthModal();
  }
  if (typeof closePublishModal === 'function') {
    closePublishModal();
  }
  
  // Notification - L'utilisateur est connecté, le bloc compte se transforme automatiquement
  const displayName = user.username || user.email?.split('@')[0] || 'Utilisateur';
  if (typeof showNotification === 'function') {
    showNotification(`✅ Bienvenue ${displayName} ! Vous êtes connecté.`, 'success');
  }
  
  console.log('[CONNECT] ✅✅✅ Utilisateur connecté - Le bloc compte va se transformer automatiquement');
  
  console.log('[CONNECT] ✅✅✅ Connexion terminée - UI mise à jour');
  
  // Si pas "rester connecté", marquer pour suppression après F5
  if (!rememberMe) {
    window.isTestAccount = true;
    window.testAccountUserId = user.id;
  } else {
    window.isTestAccount = false;
    window.testAccountUserId = null;
  }
  
  // Nettoyer les flags d'inscription
  window.isRegisteringWithGoogle = false;
  window.pendingRegisterData = null;
  isGoogleLoginInProgress = false;
  if (typeof window !== 'undefined') {
    window.isGoogleLoginInProgress = false;
  }
  hideGoogleLoginLoading();
}

// ===============================
// CHOIX DE VÉRIFICATION APRÈS FORMULAIRE
// ===============================

function showVerificationChoice() {
  console.log('[VERIFY] ⚠️⚠️⚠️ VERSION DU CODE: 20260115-124053 - showVerificationChoice appelée');
  console.log('[VERIFY] Si vous voyez ce message, le bon fichier est chargé');
  
  // Le modal peut être soit authModal (dans publish-modal-inner) soit publish-modal-inner directement
  let modal = document.getElementById('authModal');
  if (!modal) {
    modal = document.getElementById('publish-modal-inner');
  }
  
  if (!modal) {
    console.error('[VERIFY] Modal non trouvé (authModal ou publish-modal-inner)');
    // Essayer de créer le modal si nécessaire
    const backdrop = document.getElementById('publish-modal-backdrop');
    if (backdrop) {
      backdrop.style.display = 'flex';
      backdrop.style.visibility = 'visible';
      backdrop.style.opacity = '1';
    }
    modal = document.getElementById('publish-modal-inner');
    if (!modal) {
      console.error('[VERIFY] Impossible de trouver ou créer le modal');
      return;
    }
  }
  
  console.log('[VERIFY] Modal trouvé:', modal);
  
  // ⚠️⚠️⚠️ FORCER la visibilité du modal - SUPPRIMER l'attribut style qui contient display:none !important
  if (modal) {
    // Supprimer complètement l'attribut style pour éviter les conflits avec !important
    modal.removeAttribute('style');
    // Réappliquer les styles nécessaires
    modal.style.display = 'block';
    modal.style.visibility = 'visible';
    modal.style.opacity = '1';
    modal.style.zIndex = '9999';
    console.log('[VERIFY] ⚠️⚠️⚠️ Modal FORCÉ visible (attribut style supprimé)');
  }
  
  const pendingData = window.pendingRegisterData;
  if (!pendingData) {
    console.error('[VERIFY] Pas de données d\'inscription en attente');
    return;
  }
  console.log('[VERIFY] Données d\'inscription trouvées:', pendingData);
  
  // S'assurer que le backdrop est visible et centré verticalement
  const backdrop = document.getElementById('publish-modal-backdrop');
  if (backdrop) {
    backdrop.setAttribute('data-auth-modal', 'true');
    backdrop.style.display = 'flex';
    backdrop.style.visibility = 'visible';
    backdrop.style.opacity = '1';
    centerModalBackdrop();
  }
  
  // ⚠️⚠️⚠️ CRITIQUE : Vérifier que le modal existe avant injection
  if (!modal) {
    console.error('[VERIFY] ❌❌❌ Modal est NULL - impossible d\'injecter HTML');
    return;
  }
  
  console.log('[VERIFY] ⚠️⚠️⚠️ AVANT injection - modal existe:', !!modal, 'display:', modal.style.display);
  
  // Créer le contenu du modal avec le même style que authModal
  const modalHTML = `
    <div id="authModal" data-mode="verify" style="padding:40px;max-width:500px;margin:0 auto;text-align:center;position:relative;">
      <!-- Bouton X (croix) pour fermer -->
      <button onclick="closeAuthModal()" style="position:absolute;top:16px;right:16px;background:none;border:none;color:var(--ui-text-muted);font-size:24px;cursor:pointer;padding:8px;width:40px;height:40px;display:flex;align-items:center;justify-content:center;border-radius:50%;transition:all 0.2s;z-index:10;" onmouseover="this.style.background='rgba(239,68,68,0.2)';this.style.color='#ef4444';this.style.transform='scale(1.1)';" onmouseout="this.style.background='none';this.style.color='var(--ui-text-muted)';this.style.transform='scale(1)';" title="Fermer">✕</button>
      
      <!-- Progress Indicator - ÉTAPE 2 ACTIVE -->
      <div class="registration-progress" style="display:flex;justify-content:space-between;margin-bottom:24px;padding:0 8px;">
        <div class="progress-step" data-step="1" style="flex:1;text-align:center;padding:8px;border-radius:8px;background:rgba(34,197,94,0.2);color:#22c55e;font-weight:600;font-size:12px;transition:all 0.3s;">
          <div style="width:32px;height:32px;border-radius:50%;background:#22c55e;color:#fff;display:flex;align-items:center;justify-content:center;margin:0 auto 4px;font-weight:bold;font-size:18px;">✓</div>
          Informations
        </div>
        <div class="progress-step" data-step="2" style="flex:1;text-align:center;padding:8px;border-radius:8px;background:rgba(34,197,94,0.2);color:#22c55e;font-weight:600;font-size:12px;margin:0 8px;transition:all 0.3s;border:2px solid rgba(34,197,94,0.5);box-shadow:0 0 20px rgba(34,197,94,0.3);">
          <div style="width:32px;height:32px;border-radius:50%;background:#22c55e;color:#fff;display:flex;align-items:center;justify-content:center;margin:0 auto 4px;font-weight:bold;font-size:16px;box-shadow:0 0 15px rgba(34,197,94,0.5);">2</div>
          Vérification
        </div>
        <div class="progress-step" data-step="3" style="flex:1;text-align:center;padding:8px;border-radius:8px;background:rgba(255,255,255,0.05);color:var(--ui-text-muted);font-size:12px;transition:all 0.3s;">
          <div style="width:32px;height:32px;border-radius:50%;background:rgba(255,255,255,0.1);color:var(--ui-text-muted);display:flex;align-items:center;justify-content:center;margin:0 auto 4px;font-weight:bold;">3</div>
          Confirmation
        </div>
      </div>
      
      <!-- Logo et titre -->
      <div style="margin-bottom:32px;">
        <div style="font-size:64px;margin-bottom:16px;">🌍</div>
        <h2 style="margin:0 0 8px;font-size:28px;font-weight:800;color:#fff;background:linear-gradient(135deg,#00ffc3,#3b82f6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">Choisissez votre méthode de vérification</h2>
        <p style="margin:0;font-size:14px;color:var(--ui-text-muted);">Vérifiez votre compte pour finaliser votre inscription</p>
      </div>
      
      <div style="display:flex;flex-direction:column;gap:12px;margin-bottom:20px;">
        <!-- Google (1er choix, fonctionnel) - Utilise addEventListener pour CSP -->
        <button id="verify-google-btn" style="width: 100%; padding: 16px; border-radius: 12px; border: 2px solid rgba(0, 255, 195, 0.3); background: linear-gradient(135deg, rgba(0, 255, 195, 0.1), rgba(59, 130, 246, 0.1)); color: var(--ui-text-main); font-weight: 600; font-size: 15px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 12px; transition: 0.3s;">
          <span style="font-size:20px;">🔵</span>
          <span>Vérifier avec Google</span>
        </button>
        
        <!-- Facebook (bientôt disponible) -->
        <button disabled style="width:100%;padding:16px;border-radius:12px;border:2px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.05);color:var(--ui-text-muted);font-weight:600;font-size:15px;cursor:not-allowed;display:flex;align-items:center;justify-content:center;gap:12px;opacity:0.5;">
          <span style="font-size:20px;">📘</span>
          <span>Facebook (bientôt disponible)</span>
        </button>
        
        <!-- Email (dernier choix) - Utilise addEventListener pour CSP -->
        <button id="verify-email-btn" style="width: 100%; padding: 16px; border-radius: 12px; border: 2px solid rgba(255, 255, 255, 0.2); background: rgba(255, 255, 255, 0.05); color: var(--ui-text-main); font-weight: 600; font-size: 15px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 12px; transition: 0.3s;">
          <span style="font-size:20px;">📧</span>
          <span>Vérifier par email</span>
        </button>
        
        <!-- Continuer sans vérifier (TEMPORAIRE POUR TESTS) - Même résultat que Google -->
        <button id="verify-skip-btn" style="width:100%;padding:16px;border-radius:12px;border:2px solid rgba(255,193,7,0.5);background:linear-gradient(135deg,rgba(255,193,7,0.2),rgba(255,152,0,0.2));color:var(--ui-text-main);font-weight:700;font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:12px;transition:all 0.3s;margin-top:8px;">
          <span style="font-size:20px;">⚡</span>
          <span>Continuer sans vérifier (test)</span>
        </button>
      </div>
      
      <button onclick="closeAuthModal()" style="width:100%;padding:12px;border-radius:10px;border:none;background:rgba(255,255,255,0.1);color:var(--ui-text-muted);font-size:14px;cursor:pointer;">Annuler</button>
    </div>
  `;
  
  // ⚠️⚠️⚠️ INJECTER le HTML
  console.log('[VERIFY] ⚠️⚠️⚠️ Injection HTML dans modal, longueur:', modalHTML.length);
  console.log('[VERIFY] ⚠️⚠️⚠️ VÉRIFICATION AVANT injection: Le HTML contient "verify-skip-btn"?', modalHTML.includes('verify-skip-btn'));
  console.log('[VERIFY] ⚠️⚠️⚠️ VÉRIFICATION AVANT injection: Le HTML contient "Continuer sans vérifier"?', modalHTML.includes('Continuer sans vérifier'));
  
  try {
    modal.innerHTML = modalHTML;
    console.log('[VERIFY] ✅ HTML injecté avec succès');
  } catch (e) {
    console.error('[VERIFY] ❌ Erreur lors de l\'injection HTML:', e);
    return;
  }
  
  // ⚠️⚠️⚠️ FORCER la visibilité APRÈS injection HTML
  if (modal) {
    const currentStyle = modal.getAttribute('style');
    if (currentStyle && currentStyle.includes('display: none')) {
      modal.removeAttribute('style');
    }
    modal.style.display = 'block';
    modal.style.visibility = 'visible';
    modal.style.opacity = '1';
    modal.style.zIndex = '9999';
  }
  
  // S'assurer que le modal interne est aussi visible
  const innerModal = document.getElementById('authModal');
  if (innerModal) {
    innerModal.style.display = 'block';
    innerModal.style.visibility = 'visible';
    innerModal.style.opacity = '1';
  }
  
  console.log('[VERIFY] Modal HTML injecté avec succès');
  console.log('[VERIFY] ⚠️⚠️⚠️ DÉBUT setTimeout pour ajout bouton skip');
  
  // ⚠️⚠️⚠️ AJOUTER LE BOUTON "Continuer sans vérifier" APRÈS injection HTML
  setTimeout(() => {
    console.log('[VERIFY] ⚠️⚠️⚠️ setTimeout EXÉCUTÉ - Recherche du bouton...');
    
    const authModalDiv = document.getElementById('authModal');
    if (!authModalDiv) {
      console.error('[VERIFY] ❌ authModal non trouvé après injection');
      return;
    }
    
    // Vérifier si le bouton existe déjà
    let skipButton = document.getElementById('verify-skip-btn');
    
    if (!skipButton) {
      console.log('[VERIFY] ⚠️⚠️⚠️ Bouton "Continuer sans vérifier" NON TROUVÉ - AJOUT MANUEL');
      
      // Trouver le conteneur des boutons
      const buttonsContainer = authModalDiv.querySelector('div[style*="flex-direction:column"]');
      if (!buttonsContainer) {
        console.error('[VERIFY] ❌ Conteneur des boutons non trouvé');
        console.log('[VERIFY] Structure du modal:', authModalDiv.innerHTML.substring(0, 500));
        return;
      }
      
      console.log('[VERIFY] ✅ Conteneur des boutons trouvé, création du bouton...');
      
      // Créer le bouton
      skipButton = document.createElement('button');
      skipButton.id = 'verify-skip-btn';
      skipButton.style.cssText = 'width:100%;padding:16px;border-radius:12px;border:2px solid rgba(255,193,7,0.5);background:linear-gradient(135deg,rgba(255,193,7,0.2),rgba(255,152,0,0.2));color:var(--ui-text-main);font-weight:700;font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:12px;transition:all 0.3s;margin-top:8px;';
      skipButton.innerHTML = '<span style="font-size:20px;">⚡</span><span>Continuer sans vérifier (test)</span>';
      
      // Ajouter le bouton au conteneur
      buttonsContainer.appendChild(skipButton);
      console.log('[VERIFY] ✅✅✅ Bouton "Continuer sans vérifier" AJOUTÉ MANUELLEMENT!');
    } else {
      console.log('[VERIFY] ✅✅✅ Bouton "Continuer sans vérifier" TROUVÉ dans le HTML!');
    }
    
    // ⚠️⚠️⚠️ CRITIQUE : Attacher les event listeners pour TOUS les boutons (Google, Email, Skip)
    // Bouton Google
    const googleButton = document.getElementById('verify-google-btn');
    if (googleButton) {
      googleButton.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        if (e.cancelBubble !== undefined) {
          e.cancelBubble = true;
        }
        console.log('[VERIFY] 🔵🔵🔵 CLIC sur bouton "Vérifier avec Google"');
        if (typeof handleVerificationChoice === 'function') {
          handleVerificationChoice('google');
        } else if (typeof window.handleVerificationChoice === 'function') {
          window.handleVerificationChoice('google');
        } else {
          console.error('[VERIFY] ❌ handleVerificationChoice non trouvé!');
        }
        return false;
      }, true);
      
      // Styles hover pour Google
      googleButton.addEventListener('mouseenter', function() {
        this.style.borderColor = 'rgba(0,255,195,0.6)';
        this.style.background = 'linear-gradient(135deg,rgba(0,255,195,0.2),rgba(59,130,246,0.2))';
      });
      googleButton.addEventListener('mouseleave', function() {
        this.style.borderColor = 'rgba(0,255,195,0.3)';
        this.style.background = 'linear-gradient(135deg,rgba(0,255,195,0.1),rgba(59,130,246,0.1))';
      });
      console.log('[VERIFY] ✅ Event listeners attachés au bouton Google');
    }
    
    // Bouton Email
    const emailButton = document.getElementById('verify-email-btn');
    if (emailButton) {
      emailButton.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        if (e.cancelBubble !== undefined) {
          e.cancelBubble = true;
        }
        console.log('[VERIFY] 📧📧📧 CLIC sur bouton "Vérifier par email"');
        if (typeof handleVerificationChoice === 'function') {
          handleVerificationChoice('email');
        } else if (typeof window.handleVerificationChoice === 'function') {
          window.handleVerificationChoice('email');
        } else {
          console.error('[VERIFY] ❌ handleVerificationChoice non trouvé!');
        }
        return false;
      }, true);
      
      // Styles hover pour Email
      emailButton.addEventListener('mouseenter', function() {
        this.style.borderColor = 'rgba(255,255,255,0.4)';
        this.style.background = 'rgba(255,255,255,0.1)';
      });
      emailButton.addEventListener('mouseleave', function() {
        this.style.borderColor = 'rgba(255,255,255,0.2)';
        this.style.background = 'rgba(255,255,255,0.05)';
      });
      console.log('[VERIFY] ✅ Event listeners attachés au bouton Email');
    }
    
    // Bouton Skip (Continuer sans vérifier)
    skipButton.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation(); // ⚠️ CRITIQUE : Empêcher les autres listeners de se déclencher
      if (e.cancelBubble !== undefined) {
        e.cancelBubble = true;
      }
      console.log('[VERIFY] ⚡⚡⚡ CLIC sur bouton "Continuer sans vérifier"');
      console.log('[VERIFY] ⚠️ Propagation stoppée pour éviter fermeture du modal');
      if (typeof handleVerificationChoice === 'function') {
        handleVerificationChoice('skip');
      } else if (typeof window.handleVerificationChoice === 'function') {
        window.handleVerificationChoice('skip');
      } else {
        console.error('[VERIFY] ❌ handleVerificationChoice non trouvé!');
      }
      return false; // Empêcher toute action par défaut
    }, true); // ⚠️ CRITIQUE : useCapture=true pour capturer AVANT les autres listeners
    
    // Styles hover pour Skip
    skipButton.addEventListener('mouseenter', function() {
      this.style.borderColor = 'rgba(255,193,7,0.8)';
      this.style.background = 'linear-gradient(135deg,rgba(255,193,7,0.3),rgba(255,152,0,0.3))';
    });
    skipButton.addEventListener('mouseleave', function() {
      this.style.borderColor = 'rgba(255,193,7,0.5)';
      this.style.background = 'linear-gradient(135deg,rgba(255,193,7,0.2),rgba(255,152,0,0.2))';
    });
    
    console.log('[VERIFY] ✅✅✅ Event listeners attachés à tous les boutons (Google, Email, Skip)');
  }, 100);
  
}

async function handleVerificationChoice(method) {
  const pendingData = window.pendingRegisterData;
  if (!pendingData) {
    console.error('[VERIFY] Pas de données d\'inscription');
    return;
  }
  
  if (method === 'google') {
    // Utiliser OAuth Google pour créer le compte et connecter
    console.log('[VERIFY] Vérification Google choisie');
    // Lancer le flux OAuth Google
    if (typeof startGoogleLogin === 'function') {
      // ⚠️⚠️⚠️ CRITIQUE : Sauvegarder pendingRegisterData dans localStorage AVANT redirection Google
      // Car window.pendingRegisterData sera perdu lors de la redirection
      console.log('[VERIFY] ⚠️⚠️⚠️ Sauvegarde pendingRegisterData dans localStorage avant Google:', {
        username: pendingData.username,
        hasPhotoData: !!pendingData.photoData,
        email: pendingData.email
      });
      try {
        // Créer une copie sans photoData pour éviter de remplir localStorage (photoData sera récupéré depuis registerData)
        const pendingDataForStorage = { ...pendingData };
        // Garder photoData quand même car on en a besoin après le retour de Google
        // ⚠️⚠️⚠️ FIX MODE PRIVÉ : Essayer localStorage, puis sessionStorage
        try {
          localStorage.setItem('pendingRegisterDataForGoogle', JSON.stringify(pendingDataForStorage));
          console.log('[VERIFY] ✅ pendingRegisterData sauvegardé dans localStorage');
        } catch (e) {
          console.warn('[VERIFY] ⚠️ localStorage bloqué (mode privé?), sauvegarde dans sessionStorage...');
          try {
            sessionStorage.setItem('pendingRegisterDataForGoogle', JSON.stringify(pendingDataForStorage));
            console.log('[VERIFY] ✅ pendingRegisterData sauvegardé dans sessionStorage');
          } catch (e2) {
            console.error('[VERIFY] ❌ Erreur sauvegarde pendingRegisterData (localStorage et sessionStorage bloqués):', e2);
            // Fallback : sauvegarder dans window
            window.pendingRegisterData = pendingDataForStorage;
            console.log('[VERIFY] ✅ pendingRegisterData sauvegardé dans window.pendingRegisterData');
          }
        }
      } catch (e) {
        console.error('[VERIFY] ❌ Erreur générale sauvegarde pendingRegisterData:', e);
      }
      
      // Marquer que c'est pour l'inscription
      window.isRegisteringWithGoogle = true;
      window.pendingRegisterData = pendingData;
      startGoogleLogin();
    }
  } else if (method === 'email') {
    // Créer le compte puis envoyer email de vérification
    console.log('[VERIFY] Vérification email choisie');
    await createAccountAndSendVerificationEmail(pendingData);
  } else if (method === 'skip') {
    // ⚠️ TEMPORAIRE : Faire exactement la même chose que Google (pour tests)
    console.log('[VERIFY] ⚠️⚠️⚠️ CONTINUER SANS VÉRIFIER (MODE TEST) - Utilisation du flux Google');
    // Utiliser le même flux que Google pour créer le compte et connecter
    if (typeof startGoogleLogin === 'function') {
      // Marquer que c'est pour l'inscription
      window.isRegisteringWithGoogle = true;
      window.pendingRegisterData = pendingData;
      // Simuler le flux Google mais sans ouvrir la popup
      // Créer directement le compte comme Google le ferait
      await createAccountWithoutVerification(pendingData);
    } else {
      await createAccountWithoutVerification(pendingData);
    }
  }
}

async function createAccountAndSendVerificationEmail(pendingData) {
  try {
    // Chercher le modal dans publish-modal-inner ou authModal
    let modal = document.getElementById('authModal');
    if (!modal) {
      modal = document.getElementById('publish-modal-inner');
    }
    
    // S'assurer que le backdrop est visible
    const backdrop = document.getElementById('publish-modal-backdrop');
    if (backdrop) {
      backdrop.style.display = 'flex';
      backdrop.style.visibility = 'visible';
      backdrop.style.opacity = '1';
    }
    
    if (modal) {
      modal.innerHTML = `
        <div id="authModal" data-mode="creating" style="padding:40px;max-width:500px;margin:0 auto;text-align:center;position:relative;">
          <div style="font-size:64px;margin-bottom:20px;">⏳</div>
          <h2 style="margin:0 0 8px;font-size:28px;font-weight:800;color:#fff;background:linear-gradient(135deg,#00ffc3,#3b82f6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">Création du compte...</h2>
          <p style="margin:0;font-size:14px;color:var(--ui-text-muted);">Veuillez patienter</p>
        </div>
      `;
    }
    
    // Préparer les données d'inscription
    console.log('[VERIFY] ⚠️⚠️⚠️ Création compte avec username:', pendingData.username);
    
    // ⚠️⚠️⚠️ VALIDATION : Vérifier que tous les champs requis sont présents
    if (!pendingData.email || !pendingData.email.trim()) {
      console.error('[VERIFY] ❌ Email manquant dans pendingData');
      if (typeof showNotification === 'function') {
        showNotification('⚠️ Erreur: Email requis', "error");
      }
      showVerificationChoice();
      return;
    }
    
    if (!pendingData.username || !pendingData.username.trim()) {
      console.error('[VERIFY] ❌ Username manquant dans pendingData');
      if (typeof showNotification === 'function') {
        showNotification('⚠️ Erreur: Nom d\'utilisateur requis', "error");
      }
      showVerificationChoice();
      return;
    }
    
    if (!pendingData.password || !pendingData.password.trim()) {
      console.error('[VERIFY] ❌ Password manquant dans pendingData');
      if (typeof showNotification === 'function') {
        showNotification('⚠️ Erreur: Mot de passe requis', "error");
      }
      showVerificationChoice();
      return;
    }
    
    // ⚠️⚠️⚠️ CRITIQUE : Vérifier si l'email existe déjà AVANT de créer le compte
    try {
      const emailCheckResponse = await fetch(`${API_BASE_URL}/user/exists?email=${encodeURIComponent(pendingData.email.trim())}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (emailCheckResponse.ok) {
        const emailCheckData = await emailCheckResponse.json();
        if (emailCheckData.exists === true) {
          // Email existe déjà - empêcher la création du compte
          console.error('[VERIFY] ❌ Email existe déjà:', pendingData.email);
          if (typeof showNotification === 'function') {
            showNotification("❌ Ce mail existe déjà. Veuillez utiliser un autre email ou vous connecter.", "error");
          }
          
          // Afficher l'erreur dans le formulaire si on peut le trouver
          const emailInput = document.getElementById("pro-email") || document.getElementById("register-email");
          if (emailInput) {
            emailInput.style.borderColor = '#ef4444';
            const emailError = document.getElementById("pro-email-error") || document.getElementById("register-email-error");
            if (emailError) {
              emailError.textContent = '❌ Ce mail existe déjà. Veuillez utiliser un autre email ou vous connecter.';
              emailError.style.color = '#ef4444';
              emailError.style.display = 'block';
            }
          }
          
          // Revenir au choix de vérification (ou au formulaire)
          showVerificationChoice();
          return; // Empêcher la création du compte
        }
      }
    } catch (error) {
      console.error('[VERIFY] Erreur lors de la vérification de l\'email:', error);
      // En cas d'erreur, continuer quand même (ne pas bloquer si le backend est indisponible)
    }
    
    const registerDataObj = {
      email: pendingData.email.trim(),
      username: pendingData.username.trim(), // ⚠️⚠️⚠️ CRITIQUE : Utiliser le username du formulaire
      password: pendingData.password, // Ne pas trimmer le password (peut contenir des espaces intentionnels)
      firstName: pendingData.firstName?.trim() || '',
      lastName: pendingData.lastName?.trim() || '',
      photoData: pendingData.photoData || null // ⚠️⚠️⚠️ CRITIQUE : Inclure photoData si disponible
    };
    
    // Ajouter la photo si fournie (pour compatibilité)
    if (!pendingData.photoLater && pendingData.photoData) {
      window.pendingRegisterPhoto = pendingData.photoData;
    }
    
    // Ajouter l'adresse si fournie
    if (pendingData.addresses && pendingData.addresses.length > 0) {
      registerDataObj.addresses = pendingData.addresses;
    } else if (!pendingData.addressLater && pendingData.selectedAddress) {
      registerDataObj.addresses = [{
        label: pendingData.selectedAddress.label || pendingData.selectedAddress.addressDetails?.street || '',
        lat: pendingData.selectedAddress.lat,
        lng: pendingData.selectedAddress.lng,
        addressDetails: {
          country_code: pendingData.selectedAddress.country_code || pendingData.selectedAddress.addressDetails?.country_code || '',
          city: pendingData.selectedAddress.city || pendingData.selectedAddress.addressDetails?.city || '',
          postcode: pendingData.selectedAddress.postcode || pendingData.selectedAddress.addressDetails?.postcode || '',
          street: pendingData.selectedAddress.street || pendingData.selectedAddress.addressDetails?.street || ''
        }
      }];
    } else {
      registerDataObj.addresses = [];
    }
    
    // Ajouter avatarId si fourni
    if (pendingData.avatarId) {
      registerDataObj.avatarId = pendingData.avatarId;
    }
    
    // ⚠️⚠️⚠️ IMPORTANT : Créer le compte AVANT d'envoyer l'email
    // Le backend accepte maintenant les adresses non géocodées (elles seront ignorées)
    // Le compte sera créé mais l'email ne sera pas vérifié (sera vérifié via le lien)
    console.log('[VERIFY] 📤 Envoi requête création compte:', { 
      email: registerDataObj.email, 
      username: registerDataObj.username,
      hasPassword: !!registerDataObj.password,
      hasAddresses: !!registerDataObj.addresses,
      addressesCount: registerDataObj.addresses?.length || 0
    });
    const registerResponse = await fetch(`${API_BASE_URL}/user/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(registerDataObj)
    });
    
    console.log('[VERIFY] 📥 Réponse création compte:', { 
      ok: registerResponse.ok, 
      status: registerResponse.status,
      statusText: registerResponse.statusText
    });
    
    if (!registerResponse.ok) {
      const errorData = await registerResponse.json().catch(() => ({ error: 'Erreur inconnue' }));
      console.error('[VERIFY] ❌ Erreur création compte:', errorData);
      console.error('[VERIFY] ❌ Données envoyées:', registerDataObj);
      if (typeof showNotification === 'function') {
        showNotification(`⚠️ Erreur: ${errorData.error || 'Erreur lors de la création du compte'}`, "error");
      }
      showVerificationChoice(); // Revenir au choix
      return;
    }
    
    const registerResult = await registerResponse.json().catch(() => ({}));
    console.log('[VERIFY] ✅ Compte créé avec succès:', registerResult);
    
    // Sauvegarder les données pour pouvoir renvoyer l'email si nécessaire
    if (!window.pendingRegisterData) {
      window.pendingRegisterData = pendingData;
    }
    
    // Envoyer l'email de vérification avec un lien (pas de code)
    console.log('[VERIFY] 📧 Envoi de l\'email de vérification avec lien...');
    const emailResponse = await fetch(`${API_BASE_URL}/user/send-verification-link`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        email: pendingData.email,
        username: pendingData.username || 'Utilisateur'
      })
    });
    
    const emailData = await emailResponse.json().catch(() => ({ error: 'Erreur lors de la lecture de la réponse' }));
    console.log('[VERIFY] 📧 Réponse envoi email:', emailData);
    
    if (emailResponse.ok && emailData.email_sent === true) {
      // Email envoyé avec succès
      console.log('[VERIFY] ✅ Email envoyé avec succès');
      if (typeof showNotification === 'function') {
        showNotification('✅ Email de vérification envoyé ! Vérifiez votre boîte email.', "success");
      }
      
      // Afficher le message de vérification (SANS lien direct)
      if (modal) {
        modal.innerHTML = `
          <div id="authModal" data-mode="email-sent" style="padding:40px;max-width:500px;margin:0 auto;text-align:center;position:relative;">
            <!-- Bouton X (croix) pour fermer -->
            <button onclick="closeAuthModal()" style="position:absolute;top:16px;right:16px;background:none;border:none;color:var(--ui-text-muted);font-size:24px;cursor:pointer;padding:8px;width:40px;height:40px;display:flex;align-items:center;justify-content:center;border-radius:50%;transition:all 0.2s;z-index:10;" onmouseover="this.style.background='rgba(239,68,68,0.2)';this.style.color='#ef4444';this.style.transform='scale(1.1)';" onmouseout="this.style.background='none';this.style.color='var(--ui-text-muted)';this.style.transform='scale(1)';" title="Fermer">✕</button>
            
            <!-- Logo et titre -->
            <div style="margin-bottom:32px;">
              <div style="font-size:64px;margin-bottom:16px;">📧</div>
              <h2 style="margin:0 0 8px;font-size:28px;font-weight:800;color:#fff;background:linear-gradient(135deg,#00ffc3,#3b82f6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">Email de vérification envoyé</h2>
              <p style="margin:0;font-size:14px;color:var(--ui-text-muted);">Un email a été envoyé à <strong>${pendingData.email}</strong></p>
            </div>
            
            <p style="color:var(--ui-text-muted);font-size:13px;margin-bottom:20px;">Un email de vérification a été envoyé à votre adresse email.</p>
            <p style="color:var(--ui-text-muted);font-size:12px;margin-bottom:20px;font-weight:600;">⚠️ Vérifiez votre boîte email (et les spams) pour récupérer le lien de vérification.</p>
            <p style="color:var(--ui-text-muted);font-size:12px;margin-bottom:20px;">Cliquez sur le lien dans l'email pour vérifier votre compte.</p>
            
            <div style="background:rgba(0,255,195,0.1);border:1px solid rgba(0,255,195,0.3);border-radius:12px;padding:16px;margin-bottom:20px;">
              <p style="color:var(--ui-text-muted);font-size:12px;margin:0;line-height:1.6;">
                <strong style="color:#00ffc3;">💡 Important :</strong> Le lien de vérification est valide pendant 24 heures. Si vous ne recevez pas l'email, vérifiez votre dossier spam.
              </p>
            </div>
            
            <button onclick="if(typeof createAccountAndSendVerificationEmail==='function'){const pendingData=window.pendingRegisterData;if(pendingData){createAccountAndSendVerificationEmail(pendingData);}}" style="width:100%;padding:12px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:transparent;color:var(--ui-text-muted);font-weight:600;font-size:14px;cursor:pointer;margin-bottom:12px;">Renvoyer l'email</button>
            <button onclick="closeAuthModal()" style="width:100%;padding:12px;border-radius:10px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:600;font-size:14px;cursor:pointer;">Fermer</button>
          </div>
        `;
      }
    } else {
      // Email non envoyé ou erreur
      console.error('[VERIFY] ❌ Email non envoyé ou erreur');
      console.error('[VERIFY] Détails:', emailData);
      
      // Email non envoyé ou erreur - afficher un message d'erreur
      const errorMessage = emailData.error || 'Impossible d\'envoyer l\'email. Vérifiez votre configuration SendGrid.';
      console.error('[VERIFY] ❌ Email non envoyé:', errorMessage);
      if (typeof showNotification === 'function') {
        showNotification(`⚠️ Erreur: ${errorMessage}`, "error");
      }
      
      // Afficher un message d'erreur avec possibilité de réessayer
      if (modal) {
        // Si on a un lien de vérification en mode dev, l'afficher de manière visible
        const verificationLinkHtml = emailData.verification_url ? `
          <div style="background:rgba(0,255,195,0.1);border:2px solid rgba(0,255,195,0.5);border-radius:12px;padding:20px;margin-bottom:20px;">
            <p style="color:#00ffc3;font-size:14px;font-weight:700;margin-bottom:12px;">🔗 Lien de vérification (mode développement)</p>
            <a href="${emailData.verification_url}" onclick="event.preventDefault(); window.location.href=this.href; return false;" target="_self" style="display:block;padding:12px;background:rgba(0,255,195,0.2);border-radius:8px;color:#00ffc3;font-size:12px;word-break:break-all;text-decoration:none;font-weight:600;transition:all 0.2s;cursor:pointer;" onmouseover="this.style.background='rgba(0,255,195,0.3)';this.style.transform='scale(1.02)'" onmouseout="this.style.background='rgba(0,255,195,0.2)';this.style.transform='scale(1)'">${emailData.verification_url}</a>
            <p style="color:var(--ui-text-muted);font-size:11px;margin-top:12px;margin-bottom:0;">Cliquez sur ce lien pour vérifier votre compte (valable 24h)</p>
          </div>
        ` : '';
        
        modal.innerHTML = `
          <div id="authModal" data-mode="email-error" style="padding:40px;max-width:500px;margin:0 auto;text-align:center;position:relative;">
            <div style="margin-bottom:32px;">
              <div style="font-size:64px;margin-bottom:16px;">⚠️</div>
              <h2 style="margin:0 0 8px;font-size:28px;font-weight:800;color:#fff;">Erreur envoi email</h2>
              <p style="margin:0;font-size:14px;color:var(--ui-text-muted);">L'email n'a pas pu être envoyé</p>
            </div>
            <p style="color:var(--ui-text-muted);font-size:13px;margin-bottom:20px;">${errorMessage}</p>
            ${verificationLinkHtml}
            <p style="color:var(--ui-text-muted);font-size:12px;margin-bottom:20px;">${emailData.verification_url ? 'Vous pouvez utiliser le lien ci-dessus pour vérifier votre compte, ou réessayer l\'envoi de l\'email.' : 'Veuillez réessayer ou contacter le support si le problème persiste.'}</p>
            <button onclick="if(typeof createAccountAndSendVerificationEmail==='function'){const pendingData=window.pendingRegisterData;if(pendingData){createAccountAndSendVerificationEmail(pendingData);}}" style="width:100%;padding:12px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:transparent;color:var(--ui-text-muted);font-weight:600;font-size:14px;cursor:pointer;margin-bottom:12px;">Réessayer l'envoi</button>
            <button onclick="closeAuthModal()" style="width:100%;padding:12px;border-radius:10px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:600;font-size:14px;cursor:pointer;">Fermer</button>
          </div>
        `;
      }
    }
  } catch (error) {
    console.error('[VERIFY] Erreur:', error);
    if (typeof showNotification === 'function') {
      showNotification('⚠️ Erreur lors de la création du compte', "error");
    }
    showVerificationChoice();
  }
}

// ⚠️ TEMPORAIRE : Créer le compte sans vérification email (pour tests)
async function createAccountWithoutVerification(pendingData) {
  try {
    // ⚠️⚠️⚠️ CRITIQUE : Vérifier si l'email existe déjà AVANT de créer le compte
    if (pendingData && pendingData.email) {
      try {
        const emailCheckResponse = await fetch(`${API_BASE_URL}/user/exists?email=${encodeURIComponent(pendingData.email.trim())}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        if (emailCheckResponse.ok) {
          const emailCheckData = await emailCheckResponse.json();
          if (emailCheckData.exists === true) {
            // Email existe déjà - empêcher la création du compte
            console.error('[VERIFY] ❌ Email existe déjà:', pendingData.email);
            if (typeof showNotification === 'function') {
              showNotification("❌ Ce mail existe déjà. Veuillez utiliser un autre email ou vous connecter.", "error");
            }
            
            // Afficher l'erreur dans le formulaire si on peut le trouver
            const emailInput = document.getElementById("pro-email") || document.getElementById("register-email");
            if (emailInput) {
              emailInput.style.borderColor = '#ef4444';
              const emailError = document.getElementById("pro-email-error") || document.getElementById("register-email-error");
              if (emailError) {
                emailError.textContent = '❌ Ce mail existe déjà. Veuillez utiliser un autre email ou vous connecter.';
                emailError.style.color = '#ef4444';
                emailError.style.display = 'block';
              }
            }
            
            // Revenir au choix de vérification (ou au formulaire)
            showVerificationChoice();
            return; // Empêcher la création du compte
          }
        }
      } catch (error) {
        console.error('[VERIFY] Erreur lors de la vérification de l\'email:', error);
        // En cas d'erreur, continuer quand même (ne pas bloquer si le backend est indisponible)
      }
    }
    
    // Chercher le modal dans publish-modal-inner ou authModal
    let modal = document.getElementById('authModal');
    if (!modal) {
      modal = document.getElementById('publish-modal-inner');
    }
    
    // S'assurer que le backdrop est visible
    const backdrop = document.getElementById('publish-modal-backdrop');
    if (backdrop) {
      backdrop.style.display = 'flex';
      backdrop.style.visibility = 'visible';
      backdrop.style.opacity = '1';
    }
    
    if (modal) {
      modal.innerHTML = `
        <div id="authModal" data-mode="creating" style="padding:40px;max-width:500px;margin:0 auto;text-align:center;position:relative;">
          <div style="font-size:64px;margin-bottom:20px;">⏳</div>
          <h2 style="margin:0 0 8px;font-size:28px;font-weight:800;color:#fff;background:linear-gradient(135deg,#00ffc3,#3b82f6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">Création du compte...</h2>
          <p style="margin:0;font-size:14px;color:var(--ui-text-muted);">Veuillez patienter</p>
        </div>
      `;
    }
    
    // Préparer les données d'inscription
    console.log('[VERIFY] ⚠️⚠️⚠️ Création compte SANS vérification avec username:', pendingData.username);
    const registerDataObj = {
      email: pendingData.email,
      username: pendingData.username, // ⚠️⚠️⚠️ CRITIQUE : Utiliser le username du formulaire
      password: pendingData.password,
      firstName: pendingData.firstName,
      lastName: pendingData.lastName,
      photoData: pendingData.photoData || null // ⚠️⚠️⚠️ CRITIQUE : Inclure photoData si disponible
    };
    
    // Ajouter l'adresse si fournie
    if (pendingData.addresses && pendingData.addresses.length > 0) {
      registerDataObj.addresses = pendingData.addresses;
    } else if (!pendingData.addressLater && pendingData.selectedAddress) {
      registerDataObj.addresses = [{
        label: pendingData.selectedAddress.label || pendingData.selectedAddress.addressDetails?.street || '',
        lat: pendingData.selectedAddress.lat,
        lng: pendingData.selectedAddress.lng,
        addressDetails: {
          country_code: pendingData.selectedAddress.country_code || pendingData.selectedAddress.addressDetails?.country_code || '',
          city: pendingData.selectedAddress.city || pendingData.selectedAddress.addressDetails?.city || '',
          postcode: pendingData.selectedAddress.postcode || pendingData.selectedAddress.addressDetails?.postcode || '',
          street: pendingData.selectedAddress.street || pendingData.selectedAddress.addressDetails?.street || ''
        }
      }];
    } else {
      registerDataObj.addresses = [];
    }
    
    // Ajouter avatarId si fourni
    if (pendingData.avatarId) {
      registerDataObj.avatarId = pendingData.avatarId;
    }
    
    // Créer le compte
    const registerResponse = await fetch(`${API_BASE_URL}/user/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(registerDataObj)
    });
    
    if (!registerResponse.ok) {
      const errorData = await registerResponse.json().catch(() => ({ error: 'Erreur inconnue' }));
      if (typeof showNotification === 'function') {
        showNotification(`⚠️ Erreur: ${errorData.error || 'Erreur lors de la création du compte'}`, "error");
      }
      showVerificationChoice(); // Revenir au choix
      return;
    }
    
    const registerData = await registerResponse.json();
    console.log('[VERIFY] ✅ Compte créé sans vérification:', { username: registerData.username, email: registerData.email });
    
    // ⚠️⚠️⚠️ CRITIQUE : Vérifier ce que le backend retourne
    console.log('[VERIFY] 🔍🔍🔍 RÉPONSE BACKEND COMPLÈTE:', registerData);
    console.log('[VERIFY] 🔍 accessToken présent?', registerData.accessToken ? `✅ ${registerData.accessToken.substring(0, 30)}...` : '❌ Absent');
    console.log('[VERIFY] 🔍 refreshToken présent?', registerData.refreshToken ? `✅ ${registerData.refreshToken.substring(0, 30)}...` : '❌ Absent');
    console.log('[VERIFY] 🔍 userId présent?', registerData.userId ? `✅ ${registerData.userId}` : '❌ Absent');
    console.log('[VERIFY] 🔍 id présent?', registerData.id ? `✅ ${registerData.id}` : '❌ Absent');
    console.log('[VERIFY] 🔍 Toutes les clés:', Object.keys(registerData));
    
    // ⚠️⚠️⚠️ CRITIQUE : Connecter automatiquement l'utilisateur SANS demander "rester connecté"
    // L'utilisateur est connecté directement, le bloc compte se transforme automatiquement
    if (registerData.accessToken && registerData.refreshToken) {
      console.log('[VERIFY] ✅✅✅ TOKENS PRÉSENTS - Connexion automatique activée');
      const user = {
        id: registerData.userId || registerData.id,
        email: registerData.email,
        username: registerData.username || pendingData.username, // ⚠️⚠️⚠️ PRIORITÉ au username du formulaire
        firstName: registerData.firstName || pendingData.firstName || '',
        lastName: registerData.lastName || pendingData.lastName || '',
        profile_photo_url: registerData.profile_photo_url || null,
        photoData: pendingData.photoData || registerData.photoData || null,
        isLoggedIn: true
      };
      
      const tokens = {
        access_token: registerData.accessToken,
        refresh_token: registerData.refreshToken
      };
      
      console.log('[VERIFY] ⚠️⚠️⚠️ Connexion automatique DIRECTE avec username:', user.username);
      console.log('[VERIFY] Le bloc compte va se transformer automatiquement');
      console.log('[VERIFY] ⚠️⚠️⚠️ VERSION CORRIGÉE - Pas d\'appel à askRememberMeAndConnect');
      
      // ⚠️⚠️⚠️ CRITIQUE : Connecter DIRECTEMENT sans demander "rester connecté"
      // L'utilisateur est connecté automatiquement, le bloc compte se met à jour
      // ⚠️⚠️⚠️ NE JAMAIS APPELER askRememberMeAndConnect ICI - Elle ne doit être appelée qu'à la déconnexion
      // ⚠️⚠️⚠️ CRITIQUE : connectUser ferme déjà les modals automatiquement et affiche une notification
      // Ne pas fermer les modals ici pour éviter les erreurs de popup (comme flux Google Login)
      connectUser(user, tokens, true); // true = rester connecté par défaut
      // ⚠️⚠️⚠️ NOTE : connectUser affiche déjà une notification de succès, pas besoin d'en afficher une autre ici
    } else {
      // ⚠️⚠️⚠️ CAS IMPROBABLE : Pas de tokens retournés par le backend
      // Cela ne devrait jamais arriver car le backend génère toujours les tokens maintenant
      console.error('[VERIFY] ⚠️⚠️⚠️ ERREUR CRITIQUE : Pas de tokens retournés par le backend !');
      console.error('[VERIFY] Réponse backend:', registerData);
      if (typeof showNotification === 'function') {
        showNotification('⚠️ Erreur : Le compte a été créé mais la connexion automatique a échoué. Veuillez vous connecter manuellement.', 'error');
      }
      if (typeof closeAuthModal === 'function') {
        closeAuthModal();
      }
      // Afficher le formulaire de connexion pour permettre à l'utilisateur de se connecter
      if (typeof openLoginModal === 'function') {
        setTimeout(() => {
          openLoginModal();
        }, 1000);
      }
    }
  } catch (error) {
    console.error('[VERIFY] Erreur création compte sans vérification:', error);
    if (typeof showNotification === 'function') {
      showNotification('⚠️ Erreur lors de la création du compte', "error");
    }
    showVerificationChoice();
  }
}

window.showRegisterConflictError = showRegisterConflictError;
window.toggleRegisterPasswordVisibility = toggleRegisterPasswordVisibility;
window.validateRegisterPassword = validateRegisterPassword;
window.validateRegisterPasswordMatch = validateRegisterPasswordMatch;
window.updatePostalAddressRequired = updatePostalAddressRequired;
// ===============================
// GESTION CALLBACK VÉRIFICATION EMAIL
// ===============================

async function handleEmailVerificationCallback() {
  const url = new URL(window.location.href);
  const token = url.searchParams.get('token');
  const refresh = url.searchParams.get('refresh');
  const email = url.searchParams.get('email');
  
  // Si on a un token et un email dans l'URL (comme Google OAuth avec code et state)
  if (token && email) {
      console.log('[EMAIL VERIFY] Callback détecté, vérification...');
      console.log('[EMAIL VERIFY] Token brut depuis URL:', token);
      console.log('[EMAIL VERIFY] Token longueur:', token.length);
      console.log('[EMAIL VERIFY] Email:', email);
      
      // ⚠️ CRITIQUE : Détecter si on est dans un nouvel onglet (ouvert par le client email)
      // Si on est dans un nouvel onglet ET qu'on a une fenêtre parente, utiliser la fenêtre parente
      if (window.opener && !window.opener.closed) {
        // Si on est dans une popup, fermer la popup et utiliser la fenêtre parente
        console.log('[EMAIL VERIFY] Détection popup - Redirection vers fenêtre parente');
        window.opener.location.href = window.location.href;
        window.close();
        return;
      }
      
      // Si on est dans un nouvel onglet (ouvert par le client email), on reste ici
      // Le callback sera traité normalement et l'URL sera nettoyée
      console.log('[EMAIL VERIFY] Traitement dans le même onglet (comme Google OAuth)');
      
      try {
        // Vérifier le token avec le backend
        const tokenEncoded = encodeURIComponent(token);
        const emailEncoded = encodeURIComponent(email);
        const verifyUrl = `${API_BASE_URL}/user/verify-email-link?token=${tokenEncoded}&email=${emailEncoded}`;
        console.log('[EMAIL VERIFY] URL de vérification:', verifyUrl.substring(0, 200) + '...');
        console.log('[EMAIL VERIFY] Token encodé:', tokenEncoded.substring(0, 50) + '...');
        const verifyResponse = await fetch(verifyUrl);
        
        if (verifyResponse.ok) {
          const verifyData = await verifyResponse.json();
          
          if (verifyData.accessToken && verifyData.refreshToken) {
            // Email vérifié, demander si l'utilisateur veut rester connecté
            console.log('[EMAIL VERIFY] ⚠️⚠️⚠️ Données reçues du backend:', { username: verifyData.username, email: verifyData.email });
            const user = {
              id: verifyData.userId,
              email: verifyData.email,
              username: verifyData.username || verifyData.email?.split('@')[0] || 'Utilisateur', // ⚠️⚠️⚠️ Utiliser le username du backend
              firstName: verifyData.firstName || verifyData.first_name || '',
              lastName: verifyData.lastName || verifyData.last_name || '',
              profile_photo_url: verifyData.profile_photo_url || null,
              photoData: verifyData.photoData || null,
              isLoggedIn: true
            };
            console.log('[EMAIL VERIFY] ✅✅✅ User créé avec username:', user.username);
            
            const tokens = {
              access_token: verifyData.accessToken,
              refresh_token: verifyData.refreshToken
            };
            
            // ⚠️ CRITIQUE : Sauvegarder les tokens AVANT connectUser (comme Google OAuth)
            // Google OAuth appelle saveSession() avant connectUser, on fait pareil ici
            console.log('[EMAIL VERIFY] Sauvegarde des tokens avant connectUser...');
            setAuthTokens(tokens.access_token, tokens.refresh_token || '', true); // true = rester connecté par défaut
            
            // Nettoyer l'URL IMMÉDIATEMENT pour éviter les problèmes et rester sur la même page (comme Google OAuth)
            const cleanUrl = new URL(window.location.href);
            cleanUrl.searchParams.delete('token');
            cleanUrl.searchParams.delete('email');
            cleanUrl.searchParams.delete('refresh');
            // Nettoyer l'URL comme Google OAuth (reste sur la même page, pas de redirection)
            window.history.replaceState({}, document.title, cleanUrl.pathname + (cleanUrl.search || ''));
            
            // Connexion automatique sans demander "rester connecté" (sera demandé uniquement à la déconnexion)
            console.log('[EMAIL VERIFY] Connexion automatique après vérification email (rememberMe=true)');
            connectUser(user, tokens, true); // true = rester connecté par défaut (comme Google OAuth)
            
            // Afficher un message de succès
            if (typeof showNotification === 'function') {
              showNotification('✅ Email vérifié avec succès ! Vous êtes maintenant connecté.', 'success');
            }
          } else {
            // Pas de tokens, juste message de succès
            if (typeof showNotification === 'function') {
              showNotification('✅ Email vérifié avec succès !', 'success');
            }
            // Nettoyer l'URL et rester sur la même page
            const cleanUrl = new URL(window.location.href);
            cleanUrl.searchParams.delete('token');
            cleanUrl.searchParams.delete('email');
            cleanUrl.searchParams.delete('refresh');
            window.history.replaceState({}, document.title, cleanUrl.pathname + (cleanUrl.search || ''));
          }
        } else {
          const errorData = await verifyResponse.json().catch(() => ({ error: 'Erreur inconnue' }));
          console.error('[EMAIL VERIFY] ❌ Erreur vérification:', errorData);
          console.error('[EMAIL VERIFY] Token utilisé:', token);
          console.error('[EMAIL VERIFY] Email utilisé:', email);
          console.error('[EMAIL VERIFY] Code erreur:', errorData.code);
          
          // Nettoyer l'URL même en cas d'erreur (comme Google OAuth)
          const cleanUrl = new URL(window.location.href);
          cleanUrl.searchParams.delete('token');
          cleanUrl.searchParams.delete('email');
          cleanUrl.searchParams.delete('refresh');
          window.history.replaceState({}, document.title, cleanUrl.pathname + (cleanUrl.search || ''));
          
          // Gérer le cas "Utilisateur non trouvé" (mode test - compte supprimé)
          if (errorData.code === 'USER_NOT_FOUND' || verifyResponse.status === 404) {
            if (typeof showNotification === 'function') {
              showNotification('⚠️ Compte non trouvé. Le compte a peut-être été supprimé en mode test. Veuillez créer un nouveau compte.', 'error');
            }
          } else {
            if (typeof showNotification === 'function') {
              showNotification(`⚠️ Erreur: ${errorData.error || 'Lien invalide ou expiré'}`, 'error');
            }
          }
          // Afficher un message plus détaillé dans le modal
          const modal = document.getElementById('authModal') || document.getElementById('publish-modal-inner');
          if (modal && errorData.code === 'TOKEN_EXPIRED') {
            modal.innerHTML = `
              <div id="authModal" data-mode="email-error" style="padding:40px;max-width:500px;margin:0 auto;text-align:center;position:relative;">
                <div style="margin-bottom:32px;">
                  <div style="font-size:64px;margin-bottom:16px;">⏰</div>
                  <h2 style="margin:0 0 8px;font-size:28px;font-weight:800;color:#fff;">Lien expiré</h2>
                  <p style="margin:0;font-size:14px;color:var(--ui-text-muted);">Ce lien de vérification a expiré</p>
                </div>
                <p style="color:var(--ui-text-muted);font-size:13px;margin-bottom:20px;">Les liens de vérification sont valables pendant 24 heures.</p>
                <p style="color:var(--ui-text-muted);font-size:12px;margin-bottom:20px;">Veuillez créer un nouveau compte ou demander un nouveau lien de vérification.</p>
                <button onclick="closeAuthModal(); window.location.href='/';" style="width:100%;padding:12px;border-radius:10px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:600;font-size:14px;cursor:pointer;">Retour à l'accueil</button>
              </div>
            `;
          } else if (modal && errorData.code === 'INVALID_TOKEN') {
            modal.innerHTML = `
              <div id="authModal" data-mode="email-error" style="padding:40px;max-width:500px;margin:0 auto;text-align:center;position:relative;">
                <div style="margin-bottom:32px;">
                  <div style="font-size:64px;margin-bottom:16px;">⚠️</div>
                  <h2 style="margin:0 0 8px;font-size:28px;font-weight:800;color:#fff;">Lien invalide</h2>
                  <p style="margin:0;font-size:14px;color:var(--ui-text-muted);">Ce lien de vérification n'est pas valide</p>
                </div>
                <p style="color:var(--ui-text-muted);font-size:13px;margin-bottom:20px;">Le token de vérification ne correspond pas à celui stocké.</p>
                <p style="color:var(--ui-text-muted);font-size:12px;margin-bottom:20px;">Veuillez créer un nouveau compte ou demander un nouveau lien de vérification.</p>
                <button onclick="closeAuthModal(); window.location.href='/';" style="width:100%;padding:12px;border-radius:10px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:600;font-size:14px;cursor:pointer;">Retour à l'accueil</button>
              </div>
            `;
          }
        }
      } catch (error) {
        console.error('[EMAIL VERIFY] Erreur:', error);
        if (typeof showNotification === 'function') {
          showNotification('⚠️ Erreur lors de la vérification', 'error');
        }
      }
  }
}

// ===============================
// GESTION SUPPRESSION COMPTE TEST APRÈS F5
// ===============================

function checkAndCleanTestAccount() {
  const rememberMe = localStorage.getItem('rememberMe') === 'true' || sessionStorage.getItem('rememberMe') === 'true';
  
  // Si pas "rester connecté" et qu'on a un compte test, le supprimer
  if (!rememberMe && window.isTestAccount && window.testAccountUserId) {
    console.log('[CLEAN] Suppression compte test après F5 (pas "rester connecté")');
    
    // Supprimer le compte du backend
    const token = getAuthToken();
    if (token) {
      fetch(`${API_BASE_URL}/user/me`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }).catch(err => console.warn('[CLEAN] Erreur suppression compte:', err));
    }
    
    // Nettoyer le storage
    clearAuthStorage();
    window.isTestAccount = false;
    window.testAccountUserId = null;
    
    if (typeof window !== 'undefined' && window.currentUser !== undefined) {
      window.currentUser = {
        isLoggedIn: false,
        email: '',
        name: '',
        avatar: '👤'
      };
    }
    
    // Recharger la page pour réinitialiser
    window.location.reload();
  }
}

// Appeler au chargement de la page
if (typeof window !== 'undefined') {
  // Appeler handleEmailVerificationCallback au chargement si on est sur la page de vérification
  if (window.location.pathname.includes('verify-email') || window.location.search.includes('token=')) {
    handleEmailVerificationCallback();
  }

  window.addEventListener('DOMContentLoaded', () => {
    handleEmailVerificationCallback();
    checkAndCleanTestAccount();
    
    // ⚠️ NOTE: Le callback OAuth Google est géré dans map_logic.js (ligne ~3915)
    // pour éviter un double traitement qui cause l'erreur "invalid_grant"
  });
}

window.showVerificationChoice = showVerificationChoice;
window.handleVerificationChoice = handleVerificationChoice;
window.askRememberMeAndConnect = askRememberMeAndConnect;
window.connectUser = connectUser;
window.handleEmailVerificationCallback = handleEmailVerificationCallback;
window.checkAndCleanTestAccount = checkAndCleanTestAccount;
window.checkEmailAndProceed = checkEmailAndProceed; // ⚠️⚠️⚠️ NOUVEAU FLUX LEADER MONDIAL

// ⚠️⚠️⚠️ Fonction pour reconnexion avec email/mot de passe (compte existant)
async function performReconnectLogin(email, password) {
  console.log('[AUTH] 🔐 Reconnexion avec email/mot de passe:', email);
  
  if (!email || !password) {
    if (typeof showNotification === 'function') {
      showNotification('⚠️ Veuillez remplir tous les champs', 'warning');
    }
    return;
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}/user/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: email.toLowerCase().trim(),
        password: password
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.accessToken && data.refreshToken) {
      // Connexion réussie
      const tokens = {
        access_token: data.accessToken,
        refresh_token: data.refreshToken
      };
      
      // Récupérer les données utilisateur
      const userResponse = await fetch(`${API_BASE_URL}/user/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${tokens.access_token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (userResponse.ok) {
        const userData = await userResponse.json();
        const user = {
          id: userData.id,
          email: userData.email,
          username: userData.username || userData.email?.split('@')[0] || 'Utilisateur',
          profile_photo_url: userData.profile_photo_url || null
        };
        
        // Connecter l'utilisateur
        if (typeof connectUser === 'function') {
          connectUser(user, tokens, true); // true = rester connecté par défaut
        } else if (typeof window.connectUser === 'function') {
          window.connectUser(user, tokens, true);
        }
      } else {
        throw new Error('Impossible de récupérer les données utilisateur');
      }
    } else {
      throw new Error('Tokens non reçus du serveur');
    }
  } catch (error) {
    console.error('[AUTH] ❌ Erreur reconnexion:', error);
    if (typeof showNotification === 'function') {
      showNotification(`❌ ${error.message || 'Erreur lors de la connexion'}`, 'error');
    }
  }
}

window.performReconnectLogin = performReconnectLogin; // ⚠️⚠️⚠️ EXPOSER pour CSP

// Exposer les variables globales
// ⚠️⚠️⚠️ FONCTION DE VALIDATION EN TEMPS RÉEL POUR LE FORMULAIRE PROFESSIONNEL
// Debounce pour éviter trop d'appels API
let emailValidationTimeout = null;
let lastValidatedEmail = '';

async function validateProEmailField(emailInput) {
  if (!emailInput) return false;
  
  const email = emailInput.value.trim();
  const emailError = document.getElementById('pro-email-error');
  
  // Réinitialiser l'état visuel
  emailInput.style.borderColor = '';
  emailInput.removeAttribute('data-email-exists');
  emailInput.removeAttribute('aria-invalid');
  if (emailError) {
    emailError.textContent = '';
    emailError.style.display = 'none';
  }
  
  // Validation basique
  if (!email) {
    return false; // Champ vide - pas d'erreur mais pas validé
  }
  
  if (!email.includes('@') || !email.includes('.')) {
    emailInput.style.borderColor = '#ef4444';
    emailInput.setAttribute('aria-invalid', 'true');
    if (emailError) {
      emailError.textContent = '❌ Format d\'email invalide';
      emailError.style.color = '#ef4444';
      emailError.style.display = 'block';
    }
    return false;
  }
  
  // ⚠️⚠️⚠️ CRITIQUE : Annuler le timeout précédent si l'utilisateur tape encore
  if (emailValidationTimeout) {
    clearTimeout(emailValidationTimeout);
    emailValidationTimeout = null;
  }
  
  // ⚠️⚠️⚠️ CRITIQUE : Si c'est le même email que la dernière validation, ne pas re-vérifier
  if (email === lastValidatedEmail) {
    return true; // Déjà validé
  }
  
  // Afficher un message de chargement
  if (emailError) {
    emailError.textContent = '⏳ Vérification en cours...';
    emailError.style.color = '#3b82f6';
    emailError.style.display = 'block';
  }
  
  // ⚠️⚠️⚠️ CRITIQUE : Debounce de 500ms pour attendre que l'utilisateur ait fini de taper
  return new Promise((resolve) => {
    emailValidationTimeout = setTimeout(async () => {
      try {
        // ⚠️⚠️⚠️ CRITIQUE : Utiliser API_BASE_URL depuis window si disponible
        const apiUrl = (typeof window !== 'undefined' && window.API_BASE_URL) || API_BASE_URL || 'https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default/api';
        
        console.log('[VALIDATE] 🔍 Vérification email:', email, 'API:', apiUrl);
        
        const response = await fetch(`${apiUrl}/user/exists?email=${encodeURIComponent(email)}`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        
        console.log('[VALIDATE] 📡 Réponse API:', response.status, response.ok);
        
        if (response.ok) {
          const data = await response.json();
          console.log('[VALIDATE] 📦 Données reçues:', data);
          
          if (data.exists === true) {
            // Email existe déjà - marquer comme invalide
            emailInput.style.borderColor = '#ef4444';
            emailInput.setAttribute('data-email-exists', 'true');
            emailInput.setAttribute('aria-invalid', 'true');
            if (emailError) {
              emailError.textContent = '❌ Ce mail existe déjà. Veuillez utiliser un autre email ou vous connecter.';
              emailError.style.color = '#ef4444';
              emailError.style.display = 'block';
            }
            lastValidatedEmail = email;
            resolve(false);
          } else {
            // Email valide et disponible - marquer comme validé
            emailInput.style.borderColor = '#22c55e';
            emailInput.removeAttribute('data-email-exists');
            emailInput.removeAttribute('aria-invalid');
            if (emailError) {
              emailError.textContent = '✅ Email disponible';
              emailError.style.color = '#22c55e';
              emailError.style.display = 'block';
            }
            lastValidatedEmail = email;
            resolve(true);
          }
        } else {
          console.error('[VALIDATE] ❌ Erreur HTTP:', response.status);
          // En cas d'erreur HTTP, ne pas bloquer mais ne pas marquer comme validé
          if (emailError) {
            emailError.textContent = '⚠️ Erreur de vérification';
            emailError.style.color = '#f59e0b';
            emailError.style.display = 'block';
          }
          resolve(false);
        }
      } catch (e) {
        console.error('[VALIDATE] ❌ Erreur vérification email:', e);
        // En cas d'erreur réseau, ne pas bloquer mais ne pas marquer comme validé
        if (emailError) {
          emailError.textContent = '⚠️ Erreur de connexion';
          emailError.style.color = '#f59e0b';
          emailError.style.display = 'block';
        }
        resolve(false);
      }
    }, 500); // Attendre 500ms après la dernière frappe
  });
}

// ⚠️⚠️⚠️ FONCTION POUR VALIDER TOUS LES CHAMPS DU FORMULAIRE PROFESSIONNEL
function setupProFormValidation() {
  // Validation email en temps réel
  const emailInput = document.getElementById('pro-email');
  if (emailInput) {
    // Supprimer les anciens listeners
    const newEmailInput = emailInput.cloneNode(true);
    emailInput.parentNode.replaceChild(newEmailInput, emailInput);
    
    // Ajouter le listener de validation
    newEmailInput.addEventListener('input', async function() {
      await validateProEmailField(this);
    });
    
    // Valider immédiatement si l'email est déjà rempli
    if (newEmailInput.value) {
      setTimeout(() => validateProEmailField(newEmailInput), 100);
    }
  }
  
  // Validation username en temps réel
  const usernameInput = document.getElementById('pro-username');
  if (usernameInput) {
    usernameInput.addEventListener('input', function() {
      const username = this.value.trim();
      const usernameError = document.getElementById('pro-username-error');
      
      // Réinitialiser
      this.style.borderColor = '';
      this.removeAttribute('aria-invalid');
      if (usernameError) {
        usernameError.textContent = '';
        usernameError.style.display = 'none';
      }
      
      if (!username) {
        return; // Vide - pas d'erreur mais pas validé
      }
      
      if (username.length < 3) {
        this.style.borderColor = '#ef4444';
        this.setAttribute('aria-invalid', 'true');
        if (usernameError) {
          usernameError.textContent = '❌ Le nom d\'utilisateur doit contenir au moins 3 caractères';
          usernameError.style.color = '#ef4444';
          usernameError.style.display = 'block';
        }
      } else if (username.length > 20) {
        this.style.borderColor = '#ef4444';
        this.setAttribute('aria-invalid', 'true');
        if (usernameError) {
          usernameError.textContent = '❌ Le nom d\'utilisateur ne peut pas dépasser 20 caractères';
          usernameError.style.color = '#ef4444';
          usernameError.style.display = 'block';
        }
      } else {
        // Validé
        this.style.borderColor = '#22c55e';
        if (usernameError) {
          usernameError.textContent = '✅ Nom d\'utilisateur valide';
          usernameError.style.color = '#22c55e';
          usernameError.style.display = 'block';
        }
      }
    });
  }
  
  // Validation mot de passe en temps réel (si nécessaire)
  const passwordInput = document.getElementById('pro-password');
  if (passwordInput) {
    passwordInput.addEventListener('input', function() {
      const password = this.value;
      const passwordError = document.getElementById('pro-password-error');
      
      // Réinitialiser
      this.style.borderColor = '';
      this.removeAttribute('aria-invalid');
      if (passwordError) {
        passwordError.textContent = '';
        passwordError.style.display = 'none';
      }
      
      if (!password) {
        return;
      }
      
      if (password.length < 8) {
        this.style.borderColor = '#ef4444';
        this.setAttribute('aria-invalid', 'true');
        if (passwordError) {
          passwordError.textContent = '❌ Le mot de passe doit contenir au moins 8 caractères';
          passwordError.style.color = '#ef4444';
          passwordError.style.display = 'block';
        }
      } else {
        // Validé
        this.style.borderColor = '#22c55e';
        if (passwordError) {
          passwordError.textContent = '✅ Mot de passe valide';
          passwordError.style.color = '#22c55e';
          passwordError.style.display = 'block';
        }
      }
    });
  }
}

// ⚠️⚠️⚠️ FONCTION PRINCIPALE : Créer et afficher le formulaire professionnel avec validation intégrée
function showProRegisterForm() {
  console.log('[PRO REGISTER] Affichage formulaire professionnel avec validation intégrée');
  
  const backdrop = document.getElementById('publish-modal-backdrop');
  const modal = document.getElementById('publish-modal-inner');
  
  if (!backdrop || !modal) {
    console.error('[PRO REGISTER] Modal elements not found');
    return;
  }
  
  // Récupérer l'email sauvegardé si disponible
  let savedEmail = '';
  try {
    const emailFromStorage = sessionStorage.getItem('lastLoginEmail');
    if (emailFromStorage && emailFromStorage.includes('@')) {
      savedEmail = emailFromStorage;
    }
  } catch (e) {
    console.warn('[PRO REGISTER] Impossible de récupérer l\'email:', e);
  }
  
  // ⚠️⚠️⚠️ CRITIQUE : Vérifier si l'email sauvegardé existe déjà AVANT de pré-remplir
  if (savedEmail) {
    fetch(`${API_BASE_URL}/user/exists?email=${encodeURIComponent(savedEmail)}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
      if (data.exists === true) {
        // Email existe - ne pas pré-remplir
        savedEmail = '';
        if (typeof showNotification === 'function') {
          showNotification('❌ Ce mail existe déjà. Veuillez utiliser un autre email.', 'error');
        }
      }
    })
    .catch(e => console.error('[PRO REGISTER] Erreur vérification email:', e));
  }
  
  const html = `
    <div id="pro-register-container" style="padding:40px;max-width:600px;margin:0 auto;">
      <button onclick="closeAuthModal()" style="position:absolute;top:16px;right:16px;background:none;border:none;color:var(--ui-text-muted);font-size:24px;cursor:pointer;padding:8px;width:40px;height:40px;display:flex;align-items:center;justify-content:center;border-radius:50%;transition:all 0.2s;z-index:10;" onmouseover="this.style.background='rgba(239,68,68,0.2)';this.style.color='#ef4444';" onmouseout="this.style.background='none';this.style.color='var(--ui-text-muted)';" title="Fermer">✕</button>
      
      <div style="text-align:center;margin-bottom:32px;">
        <div style="font-size:64px;margin-bottom:16px;">🌍</div>
        <h2 style="margin:0 0 8px;font-size:28px;font-weight:800;color:#fff;background:linear-gradient(135deg,#00ffc3,#3b82f6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">Créer un compte</h2>
        <p style="margin:0;font-size:14px;color:var(--ui-text-muted);">Remplissez tous les champs obligatoires</p>
      </div>
      
      <form id="pro-register-form" onsubmit="event.preventDefault(); if(typeof performRegister==='function')performRegister();">
        <!-- Email avec validation en temps réel -->
        <div style="margin-bottom:20px;">
          <label style="display:block;font-size:13px;font-weight:600;color:var(--ui-text-main);margin-bottom:8px;">📧 Email <span style="color:#ef4444;">*</span></label>
          <input type="email" id="pro-email" name="email" placeholder="votre@email.com" value="${savedEmail}" required
                 style="width:100%;padding:12px 16px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:var(--ui-text-main);font-size:14px;transition:all 0.3s;box-sizing:border-box;"
                 oninput="if(typeof window.validateProEmailField==='function'){window.validateProEmailField(this).then(()=>{}).catch(e=>console.error('Erreur validation:',e));}"
                 onblur="if(typeof window.validateProEmailField==='function'){window.validateProEmailField(this).then(()=>{}).catch(e=>console.error('Erreur validation:',e));}">
          <div id="pro-email-error" style="display:none;font-size:12px;margin-top:6px;"></div>
        </div>
        
        <!-- Username avec validation en temps réel -->
        <div style="margin-bottom:20px;">
          <label style="display:block;font-size:13px;font-weight:600;color:var(--ui-text-main);margin-bottom:8px;">👤 Nom d'utilisateur <span style="color:#ef4444;">*</span></label>
          <input type="text" id="pro-username" name="username" placeholder="Votre pseudo (3-20 caractères)" required
                 style="width:100%;padding:12px 16px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:var(--ui-text-main);font-size:14px;transition:all 0.3s;box-sizing:border-box;"
                 oninput="const u=this.value.trim();const e=document.getElementById('pro-username-error');this.style.borderColor='';if(e){e.textContent='';e.style.display='none';}if(u.length>=3&&u.length<=20){this.style.borderColor='#22c55e';if(e){e.textContent='✅ Nom d\'utilisateur valide';e.style.color='#22c55e';e.style.display='block';}}else if(u.length>0){this.style.borderColor='#ef4444';if(e){e.textContent=u.length<3?'❌ Minimum 3 caractères':'❌ Maximum 20 caractères';e.style.color='#ef4444';e.style.display='block';}}">
          <div id="pro-username-error" style="display:none;font-size:12px;margin-top:6px;"></div>
        </div>
        
        <!-- Prénom -->
        <div style="margin-bottom:20px;">
          <label style="display:block;font-size:13px;font-weight:600;color:var(--ui-text-main);margin-bottom:8px;">👤 Prénom <span style="color:#ef4444;">*</span></label>
          <input type="text" id="pro-firstname" name="firstname" placeholder="Votre prénom" required
                 style="width:100%;padding:12px 16px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:var(--ui-text-main);font-size:14px;transition:all 0.3s;box-sizing:border-box;"
                 oninput="const f=this.value.trim();if(f.length>0){this.style.borderColor='#22c55e';}else{this.style.borderColor='';}">
        </div>
        
        <!-- Nom -->
        <div style="margin-bottom:20px;">
          <label style="display:block;font-size:13px;font-weight:600;color:var(--ui-text-main);margin-bottom:8px;">👤 Nom <span style="color:#ef4444;">*</span></label>
          <input type="text" id="pro-lastname" name="lastname" placeholder="Votre nom" required
                 style="width:100%;padding:12px 16px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:var(--ui-text-main);font-size:14px;transition:all 0.3s;box-sizing:border-box;"
                 oninput="const l=this.value.trim();if(l.length>0){this.style.borderColor='#22c55e';}else{this.style.borderColor='';}">
        </div>
        
        <!-- Mot de passe avec validation en temps réel -->
        <div style="margin-bottom:20px;">
          <label style="display:block;font-size:13px;font-weight:600;color:var(--ui-text-main);margin-bottom:8px;">🔒 Mot de passe <span style="color:#ef4444;">*</span></label>
          <input type="password" id="pro-password" name="password" placeholder="Minimum 8 caractères" required
                 style="width:100%;padding:12px 16px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:var(--ui-text-main);font-size:14px;transition:all 0.3s;box-sizing:border-box;"
                 oninput="const p=this.value;const e=document.getElementById('pro-password-error');this.style.borderColor='';if(e){e.textContent='';e.style.display='none';}if(p.length>=8){this.style.borderColor='#22c55e';if(e){e.textContent='✅ Mot de passe valide';e.style.color='#22c55e';e.style.display='block';}}else if(p.length>0){this.style.borderColor='#ef4444';if(e){e.textContent='❌ Minimum 8 caractères';e.style.color='#ef4444';e.style.display='block';}}">
          <div id="pro-password-error" style="display:none;font-size:12px;margin-top:6px;"></div>
        </div>
        
        <!-- Confirmation mot de passe -->
        <div style="margin-bottom:20px;">
          <label style="display:block;font-size:13px;font-weight:600;color:var(--ui-text-main);margin-bottom:8px;">✅ Confirmer mot de passe <span style="color:#ef4444;">*</span></label>
          <input type="password" id="pro-password-confirm" name="password-confirm" placeholder="Confirmer votre mot de passe" required
                 style="width:100%;padding:12px 16px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:var(--ui-text-main);font-size:14px;transition:all 0.3s;box-sizing:border-box;"
                 oninput="const p=document.getElementById('pro-password')?.value;const c=this.value;const e=document.getElementById('pro-password-confirm-error');this.style.borderColor='';if(e){e.textContent='';e.style.display='none';}if(c===p&&c.length>0){this.style.borderColor='#22c55e';if(e){e.textContent='✅ Les mots de passe correspondent';e.style.color='#22c55e';e.style.display='block';}}else if(c.length>0){this.style.borderColor='#ef4444';if(e){e.textContent='❌ Les mots de passe ne correspondent pas';e.style.color='#ef4444';e.style.display='block';}}">
          <div id="pro-password-confirm-error" style="display:none;font-size:12px;margin-top:6px;"></div>
        </div>
        
        <!-- Photo de profil (obligatoire) -->
        <div style="margin-bottom:20px;">
          <label style="display:block;font-size:13px;font-weight:600;color:var(--ui-text-main);margin-bottom:8px;">📷 Photo de profil <span style="color:#ef4444;">*</span></label>
          <input type="file" id="pro-photo" name="photo" accept="image/*" required
                 style="width:100%;padding:12px 16px;border-radius:10px;border:2px solid rgba(255,255,255,0.1);background:rgba(15,23,42,0.5);color:var(--ui-text-main);font-size:14px;transition:all 0.3s;box-sizing:border-box;"
                 onchange="const f=this.files[0];if(f){this.style.borderColor='#22c55e';const e=document.getElementById('pro-photo-error');if(e){e.textContent='✅ Photo sélectionnée';e.style.color='#22c55e';e.style.display='block';}}else{this.style.borderColor='';const e=document.getElementById('pro-photo-error');if(e){e.textContent='';e.style.display='none';}}">
          <div id="pro-photo-error" style="display:none;font-size:12px;margin-top:6px;"></div>
        </div>
        
        <!-- Bouton de soumission -->
        <button type="submit" style="width:100%;padding:14px;border-radius:12px;border:none;background:linear-gradient(135deg,#00ffc3,#3b82f6);color:#000;font-weight:700;font-size:15px;cursor:pointer;transition:all 0.3s;margin-top:8px;" onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 8px 20px rgba(0,255,195,0.3)';" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='none';">
          Créer mon compte
        </button>
      </form>
    </div>
  `;
  
  backdrop.style.display = 'flex';
  backdrop.style.visibility = 'visible';
  backdrop.style.opacity = '1';
  backdrop.style.paddingTop = '40px';
  backdrop.style.paddingBottom = '40px';
  backdrop.style.boxSizing = 'border-box';
  modal.innerHTML = html;
  modal.style.display = 'block';
  
  // ⚠️⚠️⚠️ CRITIQUE : Valider immédiatement l'email si pré-rempli
  setTimeout(() => {
    const emailInput = document.getElementById('pro-email');
    if (emailInput && emailInput.value) {
      if (typeof window.validateProEmailField === 'function') {
        window.validateProEmailField(emailInput);
      }
    }
  }, 100);
}

// Exposer la fonction globalement
window.showProRegisterForm = showProRegisterForm;

// ⚠️⚠️⚠️ CRITIQUE : S'assurer que la fonction est disponible immédiatement
if (typeof window !== 'undefined') {
  window.showProRegisterForm = showProRegisterForm;
  console.log('[PRO REGISTER] ✅ Fonction showProRegisterForm exposée globalement');
}

window.validateProEmailField = validateProEmailField;
window.setupProFormValidation = setupProFormValidation;
// ⚠️⚠️⚠️ CRITIQUE : Exposer API_BASE_URL pour que la validation inline puisse l'utiliser
window.API_BASE_URL = API_BASE_URL;

window.isSubmittingProRegister = isSubmittingProRegister;
window.registerStep = registerStep;
window.registerData = registerData;
window.isGoogleLoginInProgress = isGoogleLoginInProgress;
window.API_BASE_URL = API_BASE_URL;
window.COGNITO = COGNITO;
