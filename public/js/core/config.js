/**
 * @fileoverview Configuration centralisée pour MapEvent
 * @module core/config
 */

/**
 * Configuration de l'application MapEvent
 */
const Config = {
  // URLs API
  API: {
    BASE_URL: process.env.API_URL || "https://your-api-url.com",
    ENDPOINTS: {
      EVENTS: "/api/events",
      BOOKINGS: "/api/bookings",
      SERVICES: "/api/services",
      USERS: "/api/users",
      AUTH: "/api/auth"
    }
  },

  // Configuration de la carte
  MAP: {
    DEFAULT_CENTER: [46.5197, 6.6323], // Lausanne
    DEFAULT_ZOOM: 10,
    MIN_ZOOM: 6,
    MAX_ZOOM: 18,
    TILE_LAYER: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
  },

  // Limites et quotas
  LIMITS: {
    MAX_FAVORITES: 50,
    MAX_AGENDA: 10,
    MAX_ALERTS: 5,
    MAX_CATEGORIES_SELECTED: 5,
    MAX_BID_AMOUNT: 10000,
    MIN_BID_AMOUNT: 10
  },

  // Configuration des notifications
  NOTIFICATIONS: {
    DEFAULT_DURATION: 3000,
    SUCCESS_DURATION: 3000,
    ERROR_DURATION: 5000,
    WARNING_DURATION: 4000
  },

  // Configuration des abonnements
  SUBSCRIPTIONS: {
    FREE: {
      name: "Gratuit",
      maxAgenda: 3,
      maxAlerts: 0,
      features: ["basic"]
    },
    EXPLORER: {
      name: "Events Explorer",
      maxAgenda: 10,
      maxAlerts: 3,
      features: ["basic", "alerts"]
    },
    PRO: {
      name: "Events Pro",
      maxAgenda: 50,
      maxAlerts: 10,
      features: ["basic", "alerts", "premium"]
    }
  },

  // Langues supportées
  LANGUAGES: {
    fr: { code: "fr", name: "Français", flag: "🇫🇷" },
    en: { code: "en", name: "English", flag: "🇬🇧" },
    de: { code: "de", name: "Deutsch", flag: "🇩🇪" },
    it: { code: "it", name: "Italiano", flag: "🇮🇹" }
  },

  // Configuration des catégories
  CATEGORIES: {
    EVENTS: "events",
    BOOKINGS: "bookings",
    SERVICES: "services"
  },

  // Configuration UI
  UI: {
    ANIMATION_DURATION: 300,
    DEBOUNCE_DELAY: 300,
    THROTTLE_DELAY: 100
  }
};

// Export pour compatibilité globale
if (typeof window !== "undefined") {
  window.Config = Config;
}

export default Config;
