/**
 * @fileoverview Chargeur de modules pour MapEvent
 * Charge tous les modules core et services et les expose globalement
 */

(async function() {
  'use strict';
  
  try {
    // Charger le module de validation du profil
    const { 
      isValidUsername, 
      hasPhoto, 
      validateRequiredFields, 
      validateProfileCompleteness, 
      canAllowConnection, 
      getValidUsername 
    } = await import('./core/profile-validator.js');
    
    // Exposer globalement pour compatibilité avec auth.js
    window.ProfileValidator = {
      isValidUsername,
      hasPhoto,
      validateRequiredFields,
      validateProfileCompleteness,
      canAllowConnection,
      getValidUsername
    };
    
    console.log('✅ [MODULES] ProfileValidator chargé et exposé globalement');
  } catch (error) {
    console.error('❌ [MODULES] Erreur chargement ProfileValidator:', error);
    // Le fallback dans auth.js prendra le relais
  }
  
  // Charger les autres modules si nécessaire
  try {
    const { default: NotificationService } = await import('./services/notifications.js');
    if (!window.NotificationService) {
      window.NotificationService = NotificationService;
    }
    console.log('✅ [MODULES] NotificationService chargé');
  } catch (error) {
    console.warn('⚠️ [MODULES] NotificationService non chargé:', error);
  }
  
  try {
    const { default: StorageService } = await import('./services/storage.js');
    if (!window.StorageService) {
      window.StorageService = StorageService;
    }
    console.log('✅ [MODULES] StorageService chargé');
  } catch (error) {
    console.warn('⚠️ [MODULES] StorageService non chargé:', error);
  }
})();
