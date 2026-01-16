# Corrections 2026-01-16 - Bouton Connexion après déconnexion

## 🎯 Problème résolu
Le bouton "Connexion" ne fonctionnait pas après déconnexion, et une erreur `[UPDATE AUTH UI] slimUser invalide` apparaissait dans la console.

## 🔍 Causes identifiées

### 1. Erreur `slimUser invalide`
- `updateAuthUI(null)` était appelé lors de la déconnexion dans `performLogout`
- La fonction `updateAuthUI` nécessite un `slimUser` valide avec un `id`
- Appeler `updateAuthUI(null)` générait une erreur et empêchait la mise à jour correcte de l'UI

### 2. Bouton "Connexion" non fonctionnel
- Les event listeners n'étaient pas correctement réattachés après déconnexion
- Le bouton utilisait un `onclick` inline qui pouvait être perdu lors du clonage du DOM

### 3. Bouton "Compte" toujours visible
- Le bouton "Compte" n'était pas toujours masqué après déconnexion
- `currentUser.isLoggedIn` n'était pas toujours correctement mis à jour

## ✅ Solutions appliquées

### 1. Suppression de `updateAuthUI(null)` dans `performLogout` (`auth.js`)
**Fichier** : `public/auth.js` (lignes ~1198-1205)

**Modifications** :
- Suppression de l'appel à `updateAuthUI(null)` qui causait l'erreur
- Remplacement par un appel direct à `updateAuthButtons()` et masquage manuel du bouton "Compte"

**Code modifié** :
```javascript
// AVANT (causait l'erreur)
if (typeof updateAuthUI === 'function') {
  updateAuthUI(null); // ❌ Erreur : slimUser invalide
}

// APRÈS (corrigé)
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
  }
  if (accountBtn) {
    accountBtn.style.display = 'none';
  }
}, 0);
```

### 2. Réinitialisation complète de `currentUser` (`auth.js`)
**Fichier** : `public/auth.js` (lignes ~1172-1188)

**Modifications** :
- Utilisation de `getDefaultUser()` si disponible pour réinitialiser toutes les propriétés
- Sinon, initialisation manuelle avec toutes les propriétés nécessaires

**Code modifié** :
```javascript
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
```

### 3. Amélioration de `updateAuthButtons()` (`map_logic.js`)
**Fichier** : `public/map_logic.js` (lignes ~2671-2705)

**Modifications** :
- Réattache automatique des event listeners au bouton "Connexion" quand l'utilisateur n'est pas connecté
- Ajout de plusieurs fallbacks pour garantir que le modal s'ouvre
- Rafraîchissement automatique de la page en dernier recours

**Code ajouté** :
```javascript
function updateAuthButtons() {
  const authButtons = document.getElementById("auth-buttons");
  const accountBtn = document.getElementById("account-topbar-btn");
  
  if (!authButtons || !accountBtn) return;
  
  const isLoggedIn = currentUser && currentUser.isLoggedIn;
  
  if (isLoggedIn) {
    // Utilisateur connecté : masquer les boutons auth, afficher le bouton compte
    authButtons.style.display = 'none';
    accountBtn.style.display = 'flex';
  } else {
    // Utilisateur non connecté : afficher les boutons auth, masquer le bouton compte
    authButtons.style.display = 'flex';
    accountBtn.style.display = 'none';
    
    // ⚠️⚠️⚠️ CRITIQUE : Réattacher les event listeners au bouton "Connexion" après déconnexion
    setTimeout(() => {
      const loginBtn = document.getElementById('login-topbar-btn');
      if (loginBtn) {
        // Supprimer tous les anciens listeners en clonant le bouton
        const newLoginBtn = loginBtn.cloneNode(true);
        loginBtn.parentNode.replaceChild(newLoginBtn, loginBtn);
        
        // Réattacher le listener avec plusieurs fallbacks
        newLoginBtn.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          e.stopImmediatePropagation();
          console.log('[AUTH BUTTONS] Bouton Connexion cliqué');
          
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
            console.warn('[AUTH BUTTONS] ⚠️ Aucune fonction de connexion disponible, rafraîchissement de la page...');
            // Dernier recours : rafraîchir la page pour réinitialiser tout
            window.location.reload();
          }
        }, { capture: true });
        
        console.log('[AUTH BUTTONS] ✅ Event listener réattaché au bouton Connexion');
      }
    }, 50);
  }
}
```

### 4. Amélioration de `performLogout` (`auth.js`)
**Fichier** : `public/auth.js` (lignes ~1214-1256)

**Modifications** :
- Amélioration de la réattache des event listeners avec recherche par ID puis par sélecteur
- Ajout de plusieurs fallbacks pour ouvrir le modal de connexion
- Double vérification après 300ms pour s'assurer que tout est bien mis à jour

**Code modifié** :
```javascript
// ⚠️⚠️⚠️ FORCER la mise à jour de l'UI même si les fonctions ne sont pas disponibles
setTimeout(() => {
  const authButtons = document.getElementById('auth-buttons');
  const accountBtn = document.getElementById('account-topbar-btn');
  if (authButtons) {
    authButtons.style.display = 'flex';
    // ⚠️⚠️ CRITIQUE : Réattacher les event listeners après déconnexion pour garantir que le bouton fonctionne
    // Essayer d'abord avec l'ID spécifique, puis avec querySelector
    let loginBtn = document.getElementById('login-topbar-btn');
    if (!loginBtn) {
      loginBtn = authButtons.querySelector('button');
    }
    
    if (loginBtn) {
      // Supprimer l'ancien listener s'il existe en clonant le bouton
      const newLoginBtn = loginBtn.cloneNode(true);
      loginBtn.parentNode.replaceChild(newLoginBtn, loginBtn);
      
      // Ajouter un nouveau listener avec plusieurs fallbacks
      newLoginBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        console.log('[LOGOUT] ✅ Bouton Connexion cliqué après déconnexion');
        
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
      
      console.log('[LOGOUT] ✅✅✅ Event listener réattaché au bouton Connexion avec fallbacks');
    } else {
      console.warn('[LOGOUT] ⚠️ Bouton Connexion non trouvé dans auth-buttons');
    }
  }
  if (accountBtn) accountBtn.style.display = 'none';
}, 100);

// ⚠️⚠️⚠️ DOUBLE VÉRIFICATION après un délai supplémentaire pour s'assurer que tout est bien mis à jour
setTimeout(() => {
  if (typeof updateAuthButtons === 'function') {
    updateAuthButtons();
  } else if (typeof window !== 'undefined' && typeof window.updateAuthButtons === 'function') {
    window.updateAuthButtons();
  }
}, 300);
```

## 📋 Liste des fichiers modifiés

1. **`public/auth.js`**
   - Suppression de `updateAuthUI(null)` dans `performLogout`
   - Réinitialisation complète de `currentUser` avec `getDefaultUser()`
   - Amélioration de la réattache des event listeners avec fallbacks multiples
   - Masquage forcé du bouton "Compte" après déconnexion

2. **`public/map_logic.js`**
   - Amélioration de `updateAuthButtons()` pour réattacher automatiquement les event listeners
   - Ajout de fallbacks multiples pour ouvrir le modal de connexion
   - Rafraîchissement automatique de la page en dernier recours

3. **`public/mapevent.html`**
   - Mise à jour des versions de cache-busting : `20260116-185200-LOGOUT-FIX`

## 🎯 Résultat

### Avant
- ❌ Erreur `[UPDATE AUTH UI] slimUser invalide` après déconnexion
- ❌ Bouton "Connexion" ne fonctionnait pas après déconnexion
- ❌ Bouton "Compte" parfois encore visible après déconnexion

### Après
- ✅ Plus d'erreur `slimUser invalide` après déconnexion
- ✅ Bouton "Connexion" fonctionne correctement après déconnexion
- ✅ Modal de connexion s'ouvre correctement
- ✅ Bouton "Compte" est toujours masqué après déconnexion
- ✅ Fallbacks multiples garantissent que le modal s'ouvre toujours
- ✅ Rafraîchissement automatique de la page en dernier recours si nécessaire

## 🔧 Ordre des fallbacks pour ouvrir le modal de connexion

Le système essaie dans cet ordre :
1. `window.openLoginModal()` - Fonction principale
2. `window.openAuthModal('login')` - Fonction alternative
3. `openLoginModal()` - Fonction globale (fallback)
4. `openAuthModal('login')` - Fonction globale alternative (fallback)
5. Si rien ne fonctionne : rafraîchissement automatique de la page

## 🔧 Versions de déploiement

- **Version finale** : `20260116-185200-LOGOUT-FIX`
- **CloudFront Invalidation ID** : `IBKS11QUAYBPYXGZID5P3F3MG6`
- **Date de déploiement** : 2026-01-16 19:52:00

## 📝 Notes importantes

1. **Ne jamais appeler `updateAuthUI(null)`** : Cette fonction nécessite un `slimUser` valide avec un `id`. Utiliser `updateAuthButtons()` à la place lors de la déconnexion.

2. **Réinitialisation de `currentUser`** : Toujours utiliser `getDefaultUser()` si disponible pour réinitialiser toutes les propriétés correctement.

3. **Réattache des event listeners** : Toujours cloner le bouton pour supprimer les anciens listeners avant d'en ajouter de nouveaux.

4. **Fallbacks multiples** : Toujours prévoir plusieurs méthodes pour ouvrir le modal de connexion, avec un rafraîchissement de page en dernier recours.

5. **Double vérification** : Utiliser des `setTimeout` avec des délais différents pour s'assurer que l'UI est bien mise à jour.

## 🚀 Tests recommandés

1. Se connecter → Se déconnecter → Cliquer sur "Connexion" → Modal doit s'ouvrir ✅
2. Se connecter → Se déconnecter → Vérifier que le bouton "Compte" est masqué ✅
3. Se connecter → Se déconnecter → Vérifier qu'il n'y a pas d'erreur `slimUser invalide` ✅
4. Se connecter → Se déconnecter → Vérifier que le bouton "Connexion" est visible ✅
5. Se connecter → Se déconnecter → Vérifier que `currentUser.isLoggedIn` est `false` ✅

---

**Date de création** : 2026-01-16  
**Dernière mise à jour** : 2026-01-16 19:52:00  
**Statut** : ✅ Résolu et déployé
