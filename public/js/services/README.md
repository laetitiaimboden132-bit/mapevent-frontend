# Services

Services réutilisables pour MapEvent.

## Modules

### `notifications.js`
Service de notifications toast.

**Usage :**
```javascript
import notificationService from './services/notifications.js';

// Méthodes directes
notificationService.success('Opération réussie !');
notificationService.error('Une erreur est survenue');
notificationService.info('Information');
notificationService.warning('Attention');

// Ou méthode générique
notificationService.show('Message', 'success', 5000);
```

**Compatibilité globale :**
```javascript
// Fonction globale (compatibilité avec code existant)
window.showNotification('Message', 'info');
```

### `storage.js`
Service de stockage unifié (IndexedDB + LocalStorage).

**Usage :**
```javascript
import storageService from './services/storage.js';

// IndexedDB (données utilisateur)
await storageService.saveUser('user123', userData);
const user = await storageService.getUser('user123');
await storageService.deleteUser('user123');

// LocalStorage
storageService.setItem('key', value);
const value = storageService.getItem('key');
storageService.removeItem('key');

// SessionStorage
storageService.setItem('key', value, true); // true = sessionStorage
```

**Compatibilité globale :**
```javascript
// Fonctions globales (compatibilité avec code existant)
window.saveUserToIndexedDB(userId, userData);
window.getUserFromIndexedDB(userId);
```
