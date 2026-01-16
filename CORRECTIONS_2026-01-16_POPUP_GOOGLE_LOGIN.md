# Corrections 2026-01-16 - Popups après connexion Google

## 🎯 Problème résolu
Les popups d'événements affichaient "Erreur d'affichage" après la connexion Google, alors qu'elles fonctionnaient correctement avec "Continuer sans vérifier".

## 🔍 Causes identifiées

### 1. Variables globales non initialisées
- `currentUser` dans `map_logic.js` n'était pas synchronisé avec `window.currentUser` mis à jour par `connectUser`
- Propriétés manquantes : `favorites`, `agenda`, `likes`, `participating`, `subscription`, `reviews`

### 2. Propriété `reviews` undefined
- `currentUser.reviews` n'était pas initialisé comme objet vide
- Erreur : `TypeError: can't access property "event:1463", currentUser.reviews is undefined`

## ✅ Solutions appliquées

### 1. Synchronisation de `currentUser` dans `connectUser` (`auth.js`)
**Fichier** : `public/auth.js` (lignes ~3606-3650)

**Modifications** :
- Ajout de la synchronisation de `window.currentUser` avec toutes les propriétés nécessaires
- Utilisation de `getDefaultUser()` si disponible pour initialiser les propriétés manquantes
- Préservation des propriétés existantes (favorites, agenda, likes, etc.)

**Code ajouté** :
```javascript
// ⚠️⚠️⚠️ CRITIQUE : Synchroniser la variable globale currentUser dans map_logic.js
try {
  if (typeof window !== 'undefined') {
    if (typeof window.getDefaultUser === 'function') {
      const defaultUser = window.getDefaultUser();
      window.currentUser = {
        ...defaultUser, // Propriétés par défaut
        ...window.currentUser, // Propriétés existantes préservées
        ...user, // Nouvelles données utilisateur
        ...slimUser, // Données slim
        isLoggedIn: true,
        username: finalUsername || user.username || window.currentUser.username || 'Utilisateur',
        photoData: normalizedPhotoData || window.currentUser.photoData || null
      };
    } else {
      // Initialisation manuelle des propriétés nécessaires
      if (!Array.isArray(window.currentUser.favorites)) {
        window.currentUser.favorites = [];
      }
      // ... (autres propriétés)
      if (!window.currentUser.reviews || typeof window.currentUser.reviews !== 'object') {
        window.currentUser.reviews = {};
      }
    }
  }
} catch (e) {
  console.warn('[CONNECT] ⚠️ Erreur synchronisation currentUser:', e);
}
```

### 2. Protection dans `updateAuthUI` (`map_logic.js`)
**Fichier** : `public/map_logic.js` (lignes ~133-180)

**Modifications** :
- Vérification et initialisation de toutes les propriétés nécessaires avant la mise à jour
- Préservation des propriétés existantes lors de la fusion avec `slimUser`

**Code ajouté** :
```javascript
// ⚠️⚠️⚠️ CRITIQUE : Préserver toutes les propriétés nécessaires de currentUser
if (!currentUser || typeof currentUser !== 'object') {
  if (typeof getDefaultUser === 'function') {
    currentUser = getDefaultUser();
  } else {
    currentUser = {
      isLoggedIn: false,
      favorites: [],
      agenda: [],
      likes: [],
      participating: [],
      subscription: 'free'
    };
  }
}

// S'assurer que toutes les propriétés nécessaires existent
if (!Array.isArray(currentUser.favorites)) {
  currentUser.favorites = [];
}
// ... (autres propriétés)
if (!currentUser.reviews || typeof currentUser.reviews !== 'object') {
  currentUser.reviews = {};
}

// Mettre à jour en préservant toutes les propriétés existantes
currentUser = {
  ...currentUser, // Préserver toutes les propriétés existantes
  ...slimUser,    // Ajouter les nouvelles données slim
  isLoggedIn: true
};
```

### 3. Protection dans les fonctions de popup (`map_logic.js`)
**Fichiers** : `public/map_logic.js`

**Fonctions modifiées** :
- `buildEventPopup` (lignes ~4976-5010)
- `buildBookingPopup` (lignes ~5335-5370)
- `buildServicePopup` (lignes ~5540-5570)

**Modifications** :
- Ajout de protections pour initialiser toutes les propriétés nécessaires de `currentUser`
- Protection spécifique pour `reviews` dans `buildEventPopup` avant utilisation

**Code ajouté dans chaque fonction** :
```javascript
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
if (!Array.isArray(currentUser.likes)) {
  currentUser.likes = [];
}
if (!Array.isArray(currentUser.participating)) {
  currentUser.participating = [];
}
if (!currentUser.subscription) {
  currentUser.subscription = 'free';
}
// ⚠️⚠️⚠️ CRITIQUE : S'assurer que reviews est un objet (pas undefined)
if (!currentUser.reviews || typeof currentUser.reviews !== 'object') {
  currentUser.reviews = {};
}
```

**Protection spécifique dans `buildEventPopup` pour `reviews`** :
```javascript
// Reviews compactes
const reviewsSection = (() => {
  // ⚠️⚠️⚠️ CRITIQUE : S'assurer que currentUser.reviews existe
  if (!currentUser.reviews || typeof currentUser.reviews !== 'object') {
    currentUser.reviews = {};
  }
  const key = `event:${ev.id}`;
  const reviews = currentUser.reviews[key] || [];
  // ... reste du code
})();
```

### 4. Exposition globale de `getDefaultUser`
**Fichier** : `public/map_logic.js` (après la définition de `getDefaultUser`)

**Modifications** :
- Exposition de `getDefaultUser` sur `window` pour que `connectUser` puisse l'utiliser

**Code ajouté** :
```javascript
// ⚠️⚠️⚠️ CRITIQUE : Exposer getDefaultUser globalement pour que connectUser puisse l'utiliser
if (typeof window !== 'undefined') {
  window.getDefaultUser = getDefaultUser;
}
```

## 📋 Liste des fichiers modifiés

1. **`public/auth.js`**
   - Synchronisation de `currentUser` dans `connectUser`
   - Protection pour `reviews` dans la synchronisation

2. **`public/map_logic.js`**
   - Protection dans `updateAuthUI` pour préserver toutes les propriétés
   - Protection dans `buildEventPopup` pour initialiser toutes les propriétés
   - Protection dans `buildBookingPopup` pour initialiser toutes les propriétés
   - Protection dans `buildServicePopup` pour initialiser toutes les propriétés
   - Protection spécifique pour `reviews` dans `buildEventPopup` avant utilisation
   - Exposition globale de `getDefaultUser`

3. **`public/mapevent.html`**
   - Mise à jour des versions de cache-busting : `20260116-184000-REVIEWS-FIX`

## 🎯 Résultat

### Avant
- ❌ Popups affichaient "Erreur d'affichage" après connexion Google
- ❌ Erreur `TypeError: can't access property "event:1463", currentUser.reviews is undefined`
- ❌ Popups ne s'ouvraient pas depuis la liste

### Après
- ✅ Popups s'affichent correctement après connexion Google
- ✅ Popups s'affichent correctement avec "Continuer sans vérifier"
- ✅ Popups s'ouvrent depuis la liste sans erreur
- ✅ Toutes les propriétés de `currentUser` sont correctement initialisées

## 🔧 Versions de déploiement

- **Version finale** : `20260116-184000-REVIEWS-FIX`
- **CloudFront Invalidation ID** : `I8XWVR0D1B4ZRL5BPEHXTFZYPS`
- **Date de déploiement** : 2026-01-16 18:40:00

## 📝 Notes importantes

1. **Synchronisation** : La variable globale `currentUser` dans `map_logic.js` doit toujours être synchronisée avec `window.currentUser` après `connectUser`

2. **Propriétés critiques** : Les propriétés suivantes doivent toujours être initialisées :
   - `favorites` : Array
   - `agenda` : Array
   - `likes` : Array
   - `participating` : Array
   - `subscription` : String ('free' par défaut)
   - `reviews` : Object ({} par défaut)

3. **Ordre d'exécution** : Les protections doivent être ajoutées dans cet ordre :
   - Vérifier si `currentUser` existe
   - Initialiser les propriétés manquantes
   - Utiliser les propriétés dans le code

4. **Tests recommandés** :
   - Connexion Google → Clic sur événement dans la liste → Popup doit s'afficher
   - Connexion Google → Clic sur marqueur sur la carte → Popup doit s'afficher
   - "Continuer sans vérifier" → Clic sur événement → Popup doit s'afficher
   - Déconnexion → Reconnexion → Popups doivent toujours fonctionner

## 🚀 Prochaines étapes (optionnel)

1. Vérifier que `updateAccountBlockLegitimately` est disponible quand `connectUser` l'appelle
2. Ajouter des tests unitaires pour vérifier l'initialisation de `currentUser`
3. Documenter toutes les propriétés de `currentUser` dans un fichier de référence

---

**Date de création** : 2026-01-16  
**Dernière mise à jour** : 2026-01-16 18:40:00  
**Statut** : ✅ Résolu et déployé
