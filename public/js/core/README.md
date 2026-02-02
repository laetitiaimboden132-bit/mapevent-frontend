# Core Modules

Modules de base pour MapEvent.

## Modules

### `config.js`
Configuration centralisée de l'application :
- URLs API
- Configuration de la carte
- Limites et quotas
- Configuration des abonnements
- Langues supportées

**Usage :**
```javascript
import Config from './core/config.js';
const apiUrl = Config.API.BASE_URL;
const maxAgenda = Config.SUBSCRIPTIONS.FREE.maxAgenda;
```

### `constants.js`
Constantes de l'application :
- Types d'événements
- Statuts
- Codes d'erreur
- Messages d'erreur

**Usage :**
```javascript
import Constants from './core/constants.js';
if (status === Constants.EVENT_STATUS.COMPLETED) {
  // ...
}
```

### `utils.js`
Fonctions utilitaires :
- `escapeHtml()` - Protection XSS
- `formatEventDateRange()` - Formatage dates
- `debounce()` / `throttle()` - Optimisation performance
- `isEmpty()` / `deepClone()` - Utilitaires objets

**Usage :**
```javascript
import { escapeHtml, formatEventDateRange } from './core/utils.js';
const safe = escapeHtml(userInput);
const date = formatEventDateRange(start, end);
```

### `error-handler.js`
Gestionnaire d'erreurs centralisé :
- Traitement automatique des erreurs
- Messages utilisateur-friendly
- Journal d'erreurs
- Wrapper pour fonctions async

**Usage :**
```javascript
import errorHandler from './core/error-handler.js';
try {
  // code
} catch (error) {
  errorHandler.handle(error, 'Mon contexte');
}
```
