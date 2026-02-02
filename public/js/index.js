/**
 * @fileoverview Point d'entrée centralisé pour tous les modules
 * @module index
 * 
 * Ce fichier exporte tous les modules principaux pour faciliter les imports
 */

// Core modules
export { default as Config } from './core/config.js';
export { default as Constants } from './core/constants.js';
export * from './core/utils.js';
export { default as ErrorHandler } from './core/error-handler.js';
export * from './core/profile-validator.js';

// Services
export { default as NotificationService } from './services/notifications.js';
export { default as StorageService } from './services/storage.js';

// API
export * from './api.js';

// Exports globaux pour compatibilité
if (typeof window !== "undefined") {
  // Les modules s'exportent déjà globalement, mais on peut ajouter des helpers ici
  window.MapEventModules = {
    Config: window.Config,
    Constants: window.Constants,
    NotificationService: window.NotificationService,
    StorageService: window.StorageService,
    ErrorHandler: window.ErrorHandler
  };
}
