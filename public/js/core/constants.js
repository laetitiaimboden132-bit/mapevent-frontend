/**
 * @fileoverview Constantes de l'application MapEvent
 * @module core/constants
 */

/**
 * Constantes de l'application
 */
const Constants = {
  // Types d'événements
  ITEM_TYPES: {
    EVENT: 'event',
    BOOKING: 'booking',
    SERVICE: 'service'
  },

  // Statuts d'événements
  EVENT_STATUS: {
    UPCOMING: 'upcoming',
    ONGOING: 'ongoing',
    COMPLETED: 'completed',
    CANCELLED: 'cancelled',
    POSTPONED: 'postponed'
  },

  // Types de notifications
  NOTIFICATION_TYPES: {
    SUCCESS: 'success',
    ERROR: 'error',
    INFO: 'info',
    WARNING: 'warning'
  },

  // Types d'abonnements
  SUBSCRIPTION_TYPES: {
    FREE: 'free',
    EXPLORER: 'explorer',
    PRO: 'pro'
  },

  // Codes de langue
  LANGUAGES: {
    FR: 'fr',
    EN: 'en',
    DE: 'de',
    IT: 'it'
  },

  // Codes de pays
  COUNTRIES: {
    CH: 'CH',
    FR: 'FR',
    DE: 'DE',
    IT: 'IT'
  },

  // Emojis pour les catégories
  CATEGORY_EMOJIS: {
    MUSIC: '🎵',
    SPORTS: '⚽',
    CULTURE: '🎭',
    FOOD: '🍽️',
    BUSINESS: '💼',
    EDUCATION: '📚',
    HEALTH: '🏥',
    TRAVEL: '✈️'
  },

  // Durées par défaut (en millisecondes)
  DURATIONS: {
    NOTIFICATION: 3000,
    ANIMATION: 300,
    DEBOUNCE: 300,
    THROTTLE: 100,
    CACHE: 3600000 // 1 heure
  },

  // Limites de validation
  VALIDATION: {
    MIN_PASSWORD_LENGTH: 8,
    MAX_USERNAME_LENGTH: 50,
    MAX_DESCRIPTION_LENGTH: 1000,
    MAX_TITLE_LENGTH: 200
  },

  // Codes d'erreur
  ERROR_CODES: {
    NETWORK_ERROR: 'NETWORK_ERROR',
    AUTH_ERROR: 'AUTH_ERROR',
    VALIDATION_ERROR: 'VALIDATION_ERROR',
    NOT_FOUND: 'NOT_FOUND',
    PERMISSION_DENIED: 'PERMISSION_DENIED',
    RATE_LIMIT: 'RATE_LIMIT'
  },

  // Messages d'erreur par défaut
  ERROR_MESSAGES: {
    NETWORK_ERROR: 'Erreur de connexion. Vérifiez votre connexion internet.',
    AUTH_ERROR: 'Erreur d\'authentification. Veuillez vous reconnecter.',
    VALIDATION_ERROR: 'Les données saisies ne sont pas valides.',
    NOT_FOUND: 'Élément introuvable.',
    PERMISSION_DENIED: 'Vous n\'avez pas les permissions nécessaires.',
    RATE_LIMIT: 'Trop de requêtes. Veuillez patienter un moment.'
  }
};

// Export pour compatibilité globale
if (typeof window !== "undefined") {
  window.Constants = Constants;
}

export default Constants;
