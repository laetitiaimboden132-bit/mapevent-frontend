/**
 * @fileoverview Service de notifications pour MapEvent
 * @module services/notifications
 */

/**
 * Service de gestion des notifications toast
 */
class NotificationService {
  constructor() {
    this.defaultDuration = 3000;
    this.colors = {
      success: "#22c55e",
      error: "#ef4444",
      info: "#3b82f6",
      warning: "#f59e0b"
    };
  }

  /**
   * Affiche une notification toast
   * @param {string} message - Message à afficher
   * @param {string} type - Type de notification (success, error, info, warning)
   * @param {number} duration - Durée d'affichage en ms (défaut: 3000)
   */
  show(message, type = "info", duration = this.defaultDuration) {
    // Supprimer la notification existante
    const existing = document.getElementById("notification-toast");
    if (existing) existing.remove();

    // Créer le toast
    const toast = document.createElement("div");
    toast.id = "notification-toast";
    toast.innerHTML = message;
    toast.style.cssText = `
      position: fixed;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: ${this.colors[type] || this.colors.info};
      color: white;
      padding: 12px 24px;
      border-radius: 12px;
      font-size: 14px;
      font-weight: 500;
      z-index: 9999;
      box-shadow: 0 8px 24px rgba(0,0,0,0.3);
      animation: slideUp 0.3s ease;
      max-width: 90%;
      word-wrap: break-word;
    `;

    document.body.appendChild(toast);

    // Supprimer après la durée spécifiée
    setTimeout(() => {
      toast.style.animation = "slideDown 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }

  /**
   * Affiche une notification de succès
   * @param {string} message - Message à afficher
   * @param {number} duration - Durée d'affichage
   */
  success(message, duration) {
    this.show(message, "success", duration);
  }

  /**
   * Affiche une notification d'erreur
   * @param {string} message - Message à afficher
   * @param {number} duration - Durée d'affichage
   */
  error(message, duration) {
    this.show(message, "error", duration);
  }

  /**
   * Affiche une notification d'information
   * @param {string} message - Message à afficher
   * @param {number} duration - Durée d'affichage
   */
  info(message, duration) {
    this.show(message, "info", duration);
  }

  /**
   * Affiche une notification d'avertissement
   * @param {string} message - Message à afficher
   * @param {number} duration - Durée d'affichage
   */
  warning(message, duration) {
    this.show(message, "warning", duration);
  }
}

// Instance singleton
const notificationService = new NotificationService();

// Export pour compatibilité globale
if (typeof window !== "undefined") {
  // Fonction globale pour compatibilité avec le code existant
  window.showNotification = (message, type = "info") => {
    notificationService.show(message, type);
  };
  
  // Service complet pour utilisation avancée
  window.NotificationService = notificationService;
}

export default notificationService;
export { NotificationService };
