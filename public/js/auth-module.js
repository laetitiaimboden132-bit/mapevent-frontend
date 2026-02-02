/**
 * MODULE D'AUTHENTIFICATION
 * Extrait de map_logic.js pour modularité
 * Gère : connexion, compte utilisateur, profil
 */

(function() {
    'use strict';
    
    console.log("🔐 MODULE AUTH - Chargement...");
    
    // ============================================
    // FONCTIONS UTILITAIRES DE STOCKAGE
    // ============================================
    
    function authSave(key, val) {
        try {
            sessionStorage.setItem(key, val);
        } catch (e) {
            console.warn(`[AUTH] Erreur sauvegarde ${key}:`, e);
        }
    }
    
    function authLoad(key) {
        try {
            return sessionStorage.getItem(key);
        } catch (e) {
            return null;
        }
    }
    
    function authClearTemp() {
        ["pkce_verifier", "oauth_state"].forEach((k) => {
            try {
                sessionStorage.removeItem(k);
            } catch (e) {}
        });
    }
    
    // ============================================
    // GESTION UTILISATEUR
    // ============================================
    
    /**
     * Crée un utilisateur par défaut (non connecté)
     */
    function getDefaultUser() {
        return {
            id: null,
            name: "",
            email: "",
            avatar: "👤",
            avatarId: null,
            avatarDescription: "",
            bio: "",
            isLoggedIn: false,
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
            notificationPreferences: {
                email: true,
                sms: false
            },
            profile_public: false,
            show_name: false,
            show_photo: false,
            show_city_country_only: false,
            privacySettings: {
                showName: false,
                showAvatar: false,
                showBio: false,
                showEmail: false,
                showAddresses: false,
                showFavorites: false,
                showAgenda: false,
                showParticipating: false,
                showFriends: false,
                showActivity: false
            },
            profile_photo_url: null,
            address_verified: false,
            address_lat: null,
            address_lng: null,
            address_label: null,
            address_country_code: null,
            address_city: null,
            address_postcode: null,
            address_street: null,
            friends: [],
            friendRequests: [],
            sentRequests: [],
            blockedUsers: [],
            conversations: [],
            groups: [],
            socialAlerts: [],
            registeredCountry: 'CH',
            lastSeen: null,
            profileLinks: [],
            profilePhotos: [],
            profileVideos: [],
            createdAt: null,
            lastLoginAt: null
        };
    }
    
    /**
     * Crée une version "slim" de l'utilisateur pour le stockage
     * Évite de stocker trop de données dans localStorage
     */
    function saveUserSlim(userObj) {
        if (!userObj) return null;
        
        const slimUser = {
            id: userObj.id || null,
            email: userObj.email || '',
            username: userObj.username || '',
            profileComplete: userObj.profileComplete || false,
            profile_photo_url: userObj.profile_photo_url || userObj.profilePhoto || null,
            role: userObj.role || 'user',
            subscription: userObj.subscription || 'free',
            hasPassword: userObj.hasPassword || false,
            hasPostalAddress: userObj.hasPostalAddress || false,
            accessToken: userObj.accessToken || null,
            refreshToken: userObj.refreshToken || null
        };
        
        const slimSize = JSON.stringify(slimUser).length;
        console.log(`[AUTH] Taille user slim: ${(slimSize / 1024).toFixed(2)}KB`);
        
        return slimUser;
    }
    
    /**
     * Met à jour l'UI après connexion
     * Remplace le bouton "Connexion" par "Compte"
     */
    function updateAuthUI(slimUser) {
        if (!slimUser || !slimUser.id) {
            console.warn('[AUTH] updateAuthUI: slimUser invalide');
            return;
        }
        
        console.log('[AUTH] Mise à jour UI avec:', { id: slimUser.id, email: slimUser.email, username: slimUser.username });
        
        // S'assurer que currentUser existe
        if (!window.currentUser || typeof window.currentUser !== 'object') {
            if (typeof window.getDefaultUser === 'function') {
                window.currentUser = window.getDefaultUser();
            } else {
                window.currentUser = getDefaultUser();
            }
        }
        
        // Préserver les propriétés existantes
        if (!Array.isArray(window.currentUser.favorites)) window.currentUser.favorites = [];
        if (!Array.isArray(window.currentUser.agenda)) window.currentUser.agenda = [];
        if (!Array.isArray(window.currentUser.likes)) window.currentUser.likes = [];
        if (!Array.isArray(window.currentUser.participating)) window.currentUser.participating = [];
        if (!window.currentUser.subscription) window.currentUser.subscription = 'free';
        if (!window.currentUser.reviews || typeof window.currentUser.reviews !== 'object') {
            window.currentUser.reviews = {};
        }
        
        // Mettre à jour currentUser
        window.currentUser = {
            ...window.currentUser,
            ...slimUser,
            isLoggedIn: true
        };
        
        // Mettre à jour les boutons UI
        if (typeof window.updateAuthButtons === 'function') {
            window.updateAuthButtons();
        }
        
        if (typeof window.updateAccountBlockLegitimately === 'function') {
            window.updateAccountBlockLegitimately();
        }
        
        console.log('[AUTH] ✅ UI mise à jour - utilisateur connecté');
        
        // Ouvrir automatiquement le modal compte après connexion
        setTimeout(() => {
            if (typeof window.openAccountModal === 'function') {
                console.log('[AUTH] ✅ Ouverture automatique du modal Compte...');
                window.openAccountModal();
            }
        }, 1000);
    }
    
    /**
     * Vérifie si l'utilisateur est connecté
     */
    function isLoggedIn() {
        return window.currentUser && window.currentUser.isLoggedIn === true;
    }
    
    // ============================================
    // EXPOSITION GLOBALE
    // ============================================
    
    // Exposer les fonctions globalement
    window.getDefaultUser = getDefaultUser;
    window.saveUserSlim = saveUserSlim;
    window.updateAuthUI = updateAuthUI;
    window.isLoggedIn = isLoggedIn;
    window.authSave = authSave;
    window.authLoad = authLoad;
    window.authClearTemp = authClearTemp;
    
    // Initialiser currentUser si nécessaire
    if (!window.currentUser) {
        window.currentUser = getDefaultUser();
        console.log('[AUTH] ✅ currentUser initialisé');
    }
    
    // ============================================
    // DÉTECTION AUTOMATIQUE DE CONNEXION
    // ============================================
    
    /**
     * Vérifie et restaure la session utilisateur au chargement
     */
    function restoreUserSession() {
        console.log('[AUTH] 🔍 Vérification de la session...');
        
        // Vérifier localStorage
        try {
            const savedUser = localStorage.getItem('currentUser');
            if (savedUser) {
                const userData = JSON.parse(savedUser);
                if (userData && userData.isLoggedIn && userData.id) {
                    console.log('[AUTH] ✅ Session trouvée dans localStorage');
                    window.currentUser = {
                        ...getDefaultUser(),
                        ...userData,
                        isLoggedIn: true
                    };
                    updateAuthUI(userData);
                    return true;
                }
            }
        } catch (e) {
            console.warn('[AUTH] ⚠️ Erreur lecture localStorage:', e);
        }
        
        // Vérifier sessionStorage
        try {
            const savedUser = sessionStorage.getItem('currentUser');
            if (savedUser) {
                const userData = JSON.parse(savedUser);
                if (userData && userData.isLoggedIn && userData.id) {
                    console.log('[AUTH] ✅ Session trouvée dans sessionStorage');
                    window.currentUser = {
                        ...getDefaultUser(),
                        ...userData,
                        isLoggedIn: true
                    };
                    updateAuthUI(userData);
                    return true;
                }
            }
        } catch (e) {
            console.warn('[AUTH] ⚠️ Erreur lecture sessionStorage:', e);
        }
        
        // Vérifier cognito_session
        try {
            const cognitoSession = localStorage.getItem('cognito_session') || sessionStorage.getItem('cognito_session');
            if (cognitoSession) {
                const sessionData = JSON.parse(cognitoSession);
                if (sessionData && (sessionData.accessToken || sessionData.idToken)) {
                    console.log('[AUTH] ✅ Session Cognito trouvée');
                    // L'utilisateur est connecté mais les données complètes seront chargées par auth.js
                    return true;
                }
            }
        } catch (e) {
            console.warn('[AUTH] ⚠️ Erreur lecture cognito_session:', e);
        }
        
        console.log('[AUTH] ℹ️ Aucune session active trouvée');
        return false;
    }
    
    // Restaurer la session au chargement
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', restoreUserSession);
    } else {
        restoreUserSession();
    }
    
    // Surveiller les changements de connexion
    let lastLoginState = false;
    setInterval(function() {
        const isLoggedIn = window.currentUser && window.currentUser.isLoggedIn === true;
        if (isLoggedIn && !lastLoginState) {
            console.log('[AUTH] ✅ Utilisateur vient de se connecter !');
            lastLoginState = true;
            // Ouvrir automatiquement le compte après connexion
            setTimeout(function() {
                if (typeof window.openAccountModal === 'function') {
                    console.log('[AUTH] 🚀 Ouverture automatique du compte...');
                    window.openAccountModal();
                }
            }, 1500);
        } else if (!isLoggedIn) {
            lastLoginState = false;
        }
    }, 500);
    
    console.log("✅ MODULE AUTH - Prêt");
    console.log("💡 L'utilisateur sera reconnu immédiatement après connexion");
})();
