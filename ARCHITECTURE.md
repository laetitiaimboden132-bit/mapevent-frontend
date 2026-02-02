# 🏗️ Architecture MapEvent - Documentation Complète

## Vue d'ensemble

MapEvent est une application web modulaire organisée selon les principes de séparation des responsabilités et de réutilisabilité.

## Structure des dossiers

```
public/
├── js/
│   ├── core/                    # Modules de base
│   │   ├── config.js           # Configuration centralisée
│   │   ├── constants.js        # Constantes
│   │   ├── utils.js            # Utilitaires
│   │   ├── error-handler.js    # Gestion d'erreurs
│   │   └── README.md
│   ├── services/                # Services réutilisables
│   │   ├── notifications.js    # Service de notifications
│   │   ├── storage.js          # Service de stockage
│   │   └── README.md
│   ├── modules/                 # Modules fonctionnels
│   │   └── publish-manager.js
│   ├── api.js                   # Client API
│   └── index.js                 # Point d'entrée centralisé
├── tests/                       # Fichiers de test/diagnostic
│   └── diagnostic/
├── map_logic.js                 # Logique principale (orchestrateur)
├── auth.js                      # Authentification
└── mapevent.html                # Page principale
```

## Architecture des modules

### 1. Core Modules (`/js/core/`)

Modules fondamentaux utilisés par toute l'application.

#### `config.js`
- **Rôle** : Configuration centralisée
- **Contenu** : URLs API, limites, abonnements, langues
- **Usage** : `Config.API.BASE_URL`, `Config.LIMITS.MAX_AGENDA`

#### `constants.js`
- **Rôle** : Constantes de l'application
- **Contenu** : Types, statuts, codes d'erreur, messages
- **Usage** : `Constants.EVENT_STATUS.COMPLETED`

#### `utils.js`
- **Rôle** : Fonctions utilitaires

#### `profile-validator.js`
- **Rôle** : Validation du profil utilisateur
- **Contenu** : Validation des champs obligatoires (username, photo), vérification de complétude
- **Usage** : `validateRequiredFields()`, `canAllowConnection()`, `getValidUsername()`
- **Fonctions** : `escapeHtml()`, `formatEventDateRange()`, `debounce()`, etc.
- **Usage** : Import direct des fonctions nécessaires

#### `error-handler.js`
- **Rôle** : Gestion centralisée des erreurs
- **Fonctionnalités** : Parsing, logging, notifications automatiques
- **Usage** : `errorHandler.handle(error, context)`

### 2. Services (`/js/services/`)

Services réutilisables avec état et logique métier.

#### `notifications.js`
- **Rôle** : Affichage de notifications toast
- **Classe** : `NotificationService`
- **Méthodes** : `success()`, `error()`, `info()`, `warning()`

#### `storage.js`
- **Rôle** : Gestion du stockage (IndexedDB + LocalStorage)
- **Classe** : `StorageService`
- **Méthodes** : `saveUser()`, `getUser()`, `setItem()`, `getItem()`

### 3. Modules fonctionnels (`/js/modules/`)

Modules spécifiques à une fonctionnalité.

#### `publish-manager.js`
- **Rôle** : Gestion de la publication d'événements
- **Usage** : Importé dans `map_logic.js`

## Flux de données

```
mapevent.html
  ├── auth.js (chargé en premier)
  ├── map_logic.js (orchestrateur principal)
  │   ├── Importe: Config, Constants, Utils
  │   ├── Utilise: NotificationService, StorageService
  │   └── Appelle: API via api.js
  └── Modules fonctionnels (chargés à la demande)
```

## Principes de conception

### 1. Séparation des responsabilités
- **Core** : Configuration et utilitaires
- **Services** : Logique métier réutilisable
- **Modules** : Fonctionnalités spécifiques

### 2. Singleton Pattern
- Tous les services sont des singletons
- Accès via instance unique exportée

### 3. Compatibilité globale
- Tous les modules s'exportent aussi sur `window.*`
- Compatibilité avec le code existant

### 4. Documentation JSDoc
- Toutes les fonctions publiques documentées
- Types et paramètres explicites

## Migration depuis l'ancien code

### Avant
```javascript
// Code dispersé dans map_logic.js
function showNotification(message, type) {
  // 30 lignes de code...
}
function escapeHtml(str) {
  // ...
}
```

### Après
```javascript
// Import depuis modules
import notificationService from './js/services/notifications.js';
import { escapeHtml } from './js/core/utils.js';

// Utilisation
notificationService.success('Message');
const safe = escapeHtml(userInput);
```

## Bonnes pratiques

1. **Toujours utiliser les modules** au lieu de dupliquer le code
2. **Config centralisée** : Modifier `config.js` plutôt que hardcoder
3. **Gestion d'erreurs** : Utiliser `ErrorHandler` pour toutes les erreurs
4. **Notifications** : Utiliser `NotificationService` au lieu de `showNotification()`
5. **Stockage** : Utiliser `StorageService` au lieu d'accès direct à localStorage

## Prochaines étapes

- [ ] Migration complète de `map_logic.js` vers les modules
- [ ] Tests unitaires pour chaque module
- [ ] Documentation API complète
- [ ] Optimisation des imports (tree-shaking)
