# 🧹 Nettoyer le localStorage (Quota Exceeded)

## ❌ Problème

Erreur : `DOMException: The quota has been exceeded`

Le localStorage du navigateur est plein (limite généralement de 5-10 MB).

## 🔧 Solution Immédiate

### Option 1 : Nettoyer via la Console du Navigateur

1. **Ouvrez la console** (F12)
2. **Tapez ces commandes** :

```javascript
// Voir la taille actuelle
let total = 0;
for (let key in localStorage) {
  if (localStorage.hasOwnProperty(key)) {
    total += localStorage[key].length + key.length;
  }
}
console.log('Taille totale:', (total / 1024 / 1024).toFixed(2), 'MB');

// Nettoyer les données non essentielles
localStorage.removeItem('eventsData');
localStorage.removeItem('bookingsData');
localStorage.removeItem('servicesData');

// Vider complètement (ATTENTION : vous serez déconnecté)
// localStorage.clear();
```

### Option 2 : Nettoyer via l'Interface

1. **Ouvrez les Outils de Développement** (F12)
2. **Onglet "Application"** (Chrome) ou **"Stockage"** (Firefox)
3. **Local Storage** → `https://mapevent.world`
4. **Supprimez** :
   - `eventsData`
   - `bookingsData`
   - `servicesData`
   - Gardez `currentUser` et `cognito_tokens`

### Option 3 : Vider Complètement

**ATTENTION** : Vous serez déconnecté !

1. **Console** (F12)
2. **Tapez** : `localStorage.clear()`
3. **Rechargez** la page

## 🛠️ Corrections Appliquées

Le code a été modifié pour :
- ✅ Détecter automatiquement les erreurs de quota
- ✅ Nettoyer les données non essentielles automatiquement
- ✅ Afficher un avertissement si le nettoyage est nécessaire
- ✅ Continuer à fonctionner même si localStorage est plein

## 📊 Prévention

Pour éviter que ça se reproduise :

1. **Les données d'événements** sont maintenant nettoyées automatiquement si nécessaire
2. **Seules les données essentielles** sont sauvegardées :
   - `currentUser` (profil utilisateur)
   - `cognito_tokens` (tokens de connexion)
3. **Les données volumineuses** (événements, bookings, services) ne sont plus sauvegardées dans localStorage

## ✅ Après Nettoyage

1. **Rechargez** la page
2. **Reconnectez-vous** avec Google si nécessaire
3. **Le formulaire** devrait s'afficher correctement


