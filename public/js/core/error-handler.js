/**
 * @fileoverview Gestionnaire d'erreurs centralisé
 * @module core/error-handler
 */

import Constants from './constants.js';
import notificationService from '../services/notifications.js';

/**
 * Gestionnaire d'erreurs centralisé
 */
class ErrorHandler {
  constructor() {
    this.errorLog = [];
    this.maxLogSize = 100;
  }

  /**
   * Traite une erreur et affiche une notification appropriée
   * @param {Error|string} error - Erreur à traiter
   * @param {string} context - Contexte de l'erreur
   * @param {boolean} showNotification - Afficher une notification
   */
  handle(error, context = 'Application', showNotification = true) {
    const errorData = this.parseError(error, context);
    
    // Logger l'erreur
    this.logError(errorData);
    
    // Afficher notification si demandé
    if (showNotification) {
      const message = this.getUserFriendlyMessage(errorData);
      notificationService.error(message);
    }
    
    // Console pour debug
    console.error(`[${context}]`, errorData);
    
    return errorData;
  }

  /**
   * Parse une erreur en objet structuré
   * @param {Error|string} error - Erreur à parser
   * @param {string} context - Contexte
   * @returns {Object} Données d'erreur structurées
   */
  parseError(error, context) {
    if (typeof error === 'string') {
      return {
        message: error,
        context,
        timestamp: new Date().toISOString(),
        type: 'string'
      };
    }

    if (error instanceof Error) {
      return {
        message: error.message,
        stack: error.stack,
        context,
        timestamp: new Date().toISOString(),
        type: 'Error',
        name: error.name
      };
    }

    if (error && typeof error === 'object') {
      return {
        ...error,
        context,
        timestamp: new Date().toISOString(),
        type: 'object'
      };
    }

    return {
      message: 'Erreur inconnue',
      context,
      timestamp: new Date().toISOString(),
      type: 'unknown'
    };
  }

  /**
   * Obtient un message utilisateur-friendly
   * @param {Object} errorData - Données d'erreur
   * @returns {string} Message lisible
   */
  getUserFriendlyMessage(errorData) {
    // Vérifier si c'est un code d'erreur connu
    if (errorData.code && Constants.ERROR_MESSAGES[errorData.code]) {
      return Constants.ERROR_MESSAGES[errorData.code];
    }

    // Vérifier si le message contient des indices
    const message = errorData.message || '';
    
    if (message.includes('network') || message.includes('fetch') || message.includes('NetworkError')) {
      return Constants.ERROR_MESSAGES.NETWORK_ERROR;
    }
    
    if (message.includes('auth') || message.includes('401') || message.includes('403')) {
      return Constants.ERROR_MESSAGES.AUTH_ERROR;
    }
    
    if (message.includes('404') || message.includes('not found')) {
      return Constants.ERROR_MESSAGES.NOT_FOUND;
    }

    // Message par défaut
    return errorData.message || Constants.ERROR_MESSAGES.NETWORK_ERROR;
  }

  /**
   * Log une erreur dans le journal
   * @param {Object} errorData - Données d'erreur
   */
  logError(errorData) {
    this.errorLog.push(errorData);
    
    // Limiter la taille du log
    if (this.errorLog.length > this.maxLogSize) {
      this.errorLog.shift();
    }
  }

  /**
   * Récupère le journal d'erreurs
   * @returns {Array} Journal d'erreurs
   */
  getErrorLog() {
    return [...this.errorLog];
  }

  /**
   * Vide le journal d'erreurs
   */
  clearErrorLog() {
    this.errorLog = [];
  }

  /**
   * Wrapper pour les fonctions async avec gestion d'erreur automatique
   * @param {Function} asyncFn - Fonction async
   * @param {string} context - Contexte
   * @returns {Function} Fonction wrappée
   */
  wrapAsync(asyncFn, context = 'Async') {
    return async (...args) => {
      try {
        return await asyncFn(...args);
      } catch (error) {
        this.handle(error, context);
        throw error;
      }
    };
  }
}

// Instance singleton
const errorHandler = new ErrorHandler();

// Export pour compatibilité globale
if (typeof window !== "undefined") {
  window.ErrorHandler = errorHandler;
  window.handleError = (error, context) => errorHandler.handle(error, context);
}

export default errorHandler;
export { ErrorHandler };
