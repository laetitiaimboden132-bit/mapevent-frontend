# 🔔 Système de Favoris et Alertes - Fonctionnement

## 📋 Vue d'ensemble

Le système permet aux utilisateurs de :
1. **Ajouter des favoris** (bookings, services, events, avatars)
2. **Recevoir des alertes automatiques** quand un favori apparaît dans un nouvel événement sur la map

---

## 🎯 Fonctionnement Prévu

### 1. **Ajout de Favoris**

L'utilisateur peut ajouter en favoris :
- ✅ **Events** (événements)
- ✅ **Bookings** (réservations/contacts)
- ✅ **Services** (services)
- ✅ **Avatars** (organisateurs/artistes)

**Stockage :**
- **Frontend :** `currentUser.favorites[]` (localStorage)
- **Backend :** Table `user_favorites` (PostgreSQL)
- **Format :** `{key: "event:123", id: "123", mode: "event", name: "Nom", addedAt: "..."}`

---

### 2. **Détection Automatique des Favoris dans les Nouveaux Événements**

**Quand un nouvel événement apparaît sur la map :**

1. **Le système vérifie** si le nom/titre de l'événement contient :
   - Le nom d'un **booking favori**
   - Le nom d'un **service favori**
   - Le nom d'un **event favori**
   - Le nom d'un **avatar/organisateur favori**

2. **Si une correspondance est trouvée :**
   - ✅ Créer une **alerte automatique**
   - ✅ Envoyer une **notification** à l'utilisateur
   - ✅ Sauvegarder l'alerte dans `user_alerts` (backend)

---

## 🔍 Logique de Détection (À Implémenter)

### Algorithme de Correspondance

```javascript
// Fonction à appeler quand de nouveaux événements sont chargés
function checkFavoritesInNewEvents(newEvents) {
  // Pour chaque nouvel événement
  newEvents.forEach(event => {
    // Pour chaque favori de l'utilisateur
    currentUser.favorites.forEach(favorite => {
      // Vérifier si le nom du favori apparaît dans le titre/description de l'événement
      const favoriteName = favorite.name.toLowerCase();
      const eventTitle = event.title.toLowerCase();
      const eventDescription = (event.description || '').toLowerCase();
      
      // Correspondance exacte ou partielle
      if (eventTitle.includes(favoriteName) || eventDescription.includes(favoriteName)) {
        // Créer une alerte
        createAlertForFavorite(event, favorite);
      }
    });
  });
}

// Créer une alerte pour un favori trouvé
async function createAlertForFavorite(event, favorite) {
  const alert = {
    id: `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    eventId: event.id,
    favoriteId: favorite.id,
    favoriteName: favorite.name,
    favoriteMode: favorite.mode, // 'event', 'booking', 'service', 'avatar'
    distance: calculateDistance(event, favorite), // Distance en km (si géolocalisé)
    status: 'new', // 'new', 'seen', 'deleted'
    creationDate: new Date().toISOString()
  };
  
  // Sauvegarder dans le backend
  try {
    const response = await fetch(`${API_BASE_URL}/user/alerts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId: currentUser.id,
        alert: alert
      })
    });
    
    if (response.ok) {
      // Ajouter à la liste locale
      currentUser.alerts.push(alert);
      
      // Afficher une notification
      showNotification(
        `🔔 Alerte ! "${favorite.name}" apparaît dans l'événement "${event.title}"`,
        'success'
      );
    }
  } catch (error) {
    console.error('Erreur création alerte:', error);
  }
}
```

---

## 📊 Structure des Données

### Favori (Frontend)
```javascript
{
  key: "booking:123",      // Clé unique
  id: "123",               // ID de l'item
  mode: "booking",         // Type: 'event', 'booking', 'service', 'avatar'
  type: "booking",         // Alias de mode
  name: "Nom du Booking",  // Nom à rechercher
  addedAt: "2025-01-15T10:00:00Z"
}
```

### Alerte (Backend)
```javascript
{
  id: "alert-123",
  eventId: "456",          // ID de l'événement où le favori a été trouvé
  favoriteId: "123",       // ID du favori
  favoriteName: "Nom du Booking",
  favoriteMode: "booking", // Type du favori
  distance: 15,            // Distance en km (si géolocalisé)
  status: "new",           // 'new', 'seen', 'deleted'
  creationDate: "2025-01-15T10:00:00Z",
  seenAt: null             // Date de visualisation (si status = 'seen')
}
```

---

## 🔄 Flux Complet

### 1. **Ajout d'un Favori**
```
Utilisateur clique "Ajouter aux favoris"
  ↓
Frontend: toggleFavorite(type, id)
  ↓
Appel API: POST /api/user/favorites
  ↓
Backend: Sauvegarde dans user_favorites
  ↓
Frontend: Ajoute à currentUser.favorites[]
```

### 2. **Chargement de Nouveaux Événements**
```
Chargement événements depuis API
  ↓
Nouveaux événements ajoutés à eventsData[]
  ↓
Appel: checkFavoritesInNewEvents(newEvents)
  ↓
Pour chaque événement, vérifier si un favori apparaît
  ↓
Si correspondance trouvée → Créer alerte
```

### 3. **Affichage des Alertes**
```
Chargement des alertes: GET /api/user/alerts?userId=123
  ↓
Affichage dans le panneau utilisateur
  ↓
Notification visuelle (badge, popup)
```

---

## 🎨 Interface Utilisateur

### Affichage des Alertes

**Dans le panneau utilisateur :**
- 🔔 Badge avec nombre d'alertes non lues
- Liste des alertes avec :
  - Nom du favori trouvé
  - Titre de l'événement
  - Distance (si géolocalisé)
  - Date de création
  - Bouton "Voir l'événement" → Centre la map sur l'événement

**Notification en temps réel :**
- Popup/Toast quand une nouvelle alerte est créée
- Son optionnel (si abonnement premium)

---

## ⚙️ Configuration Backend

### Endpoints Disponibles

1. **GET /api/user/alerts?userId=123**
   - Récupère toutes les alertes d'un utilisateur
   - Filtre les alertes supprimées (status != 'deleted')

2. **POST /api/user/alerts**
   - Crée une nouvelle alerte
   - Body: `{userId, alert: {...}}`

3. **POST /api/user/alerts/seen**
   - Marque une alerte comme vue
   - Body: `{userId, alertId}`

---

## 🚀 Implémentation

### À Ajouter dans `map_logic.js`

1. **Fonction de détection** : `checkFavoritesInNewEvents(newEvents)`
2. **Fonction de création d'alerte** : `createAlertForFavorite(event, favorite)`
3. **Appel automatique** : Dans `loadDataFromBackend()` après chargement des événements

### Exemple d'Intégration

```javascript
// Dans loadDataFromBackend(), après avoir ajouté les nouveaux événements
async function loadDataFromBackend() {
  try {
    const response = await fetch(`${API_BASE_URL}/events`);
    const newEvents = await response.json();
    
    // Ajouter les nouveaux événements
    eventsData.push(...newEvents);
    
    // ✅ NOUVEAU : Vérifier si des favoris apparaissent dans les nouveaux événements
    checkFavoritesInNewEvents(newEvents);
    
    refreshMarkers();
  } catch (error) {
    console.error('Erreur chargement événements:', error);
  }
}
```

---

## 📝 Notes Importantes

1. **Correspondance de noms** : La recherche est **insensible à la casse** et peut être **partielle**
2. **Performance** : Pour éviter trop d'alertes, on peut :
   - Limiter à 1 alerte par favori/événement
   - Vérifier uniquement les nouveaux événements (pas tous les événements à chaque fois)
3. **Abonnements** : Les alertes peuvent être limitées selon l'abonnement :
   - Gratuit : Pas d'alertes
   - Events Explorer : 10 alertes/mois
   - Events Alerts Pro : Illimité
4. **Géolocalisation** : Si le favori et l'événement ont des coordonnées, calculer la distance

---

## ✅ Prochaines Étapes

1. ✅ Endpoints backend créés (`/api/user/favorites`, `/api/user/alerts`)
2. ⏳ Implémenter `checkFavoritesInNewEvents()` dans le frontend
3. ⏳ Implémenter `createAlertForFavorite()` dans le frontend
4. ⏳ Appeler la détection après chaque chargement d'événements
5. ⏳ Afficher les alertes dans l'interface utilisateur
6. ⏳ Tester avec des favoris réels



