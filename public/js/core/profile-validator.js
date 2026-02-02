/**
 * @fileoverview Module de validation du profil utilisateur
 * @module core/profile-validator
 */

/**
 * Champs obligatoires pour un profil complet
 */
const REQUIRED_FIELDS = ['username', 'photo'];

/**
 * Champs optionnels (peuvent être complétés plus tard)
 */
const OPTIONAL_FIELDS = ['postalAddress', 'address'];

/**
 * Valide si un username est valide
 * @param {string} username - Le username à valider
 * @returns {boolean} True si valide
 */
export function isValidUsername(username) {
  if (!username) return false;
  if (username === '' || username === 'null' || username === 'undefined') return false;
  if (username.includes('@')) return false; // Ne doit pas être un email
  return true;
}

/**
 * Valide si une photo est présente
 * @param {string|null|undefined} photoData - Les données de la photo (base64)
 * @param {string|null|undefined} profilePhotoUrl - L'URL de la photo de profil
 * @returns {boolean} True si une photo est présente
 */
export function hasPhoto(photoData, profilePhotoUrl) {
  const hasPhotoData = photoData && 
    photoData !== '' && 
    photoData !== 'null' && 
    photoData !== 'undefined';
  const hasPhotoUrl = profilePhotoUrl && 
    profilePhotoUrl !== '' && 
    profilePhotoUrl !== 'null';
  return hasPhotoData || hasPhotoUrl;
}

/**
 * Vérifie si toutes les données obligatoires sont présentes
 * @param {Object} userData - Les données de l'utilisateur
 * @param {Object} pendingData - Les données en attente du formulaire
 * @returns {Object} { isValid: boolean, missingFields: string[] }
 */
export function validateRequiredFields(userData = {}, pendingData = {}) {
  const missingFields = [];
  
  // Vérifier username (priorité au formulaire, puis backend)
  const username = pendingData?.username || userData?.username;
  if (!isValidUsername(username)) {
    missingFields.push('username');
  }
  
  // Vérifier photo (priorité au formulaire, puis backend)
  const photoData = pendingData?.photoData || userData?.photoData;
  const profilePhotoUrl = userData?.profile_photo_url || userData?.profilePhotoUrl;
  if (!hasPhoto(photoData, profilePhotoUrl)) {
    missingFields.push('photo');
  }
  
  return {
    isValid: missingFields.length === 0,
    missingFields
  };
}

/**
 * Vérifie si le profil est complet (données obligatoires + optionnelles)
 * @param {Object} userData - Les données de l'utilisateur
 * @param {Object} pendingData - Les données en attente du formulaire
 * @returns {Object} { isComplete: boolean, missingRequired: string[], missingOptional: string[] }
 */
export function validateProfileCompleteness(userData = {}, pendingData = {}) {
  const required = validateRequiredFields(userData, pendingData);
  
  const missingOptional = [];
  
  // Vérifier adresse postale (optionnelle)
  const postalAddress = pendingData?.postalAddress || 
                       userData?.postalAddress || 
                       userData?.postal_address;
  if (!postalAddress || postalAddress === '' || postalAddress === 'null') {
    missingOptional.push('postalAddress');
  }
  
  return {
    isComplete: required.isValid && missingOptional.length === 0,
    missingRequired: required.missingFields,
    missingOptional
  };
}

/**
 * Détermine si la connexion doit être autorisée
 * @param {Object} userData - Les données de l'utilisateur
 * @param {Object} pendingData - Les données en attente du formulaire
 * @returns {boolean} True si la connexion peut être autorisée
 */
export function canAllowConnection(userData = {}, pendingData = {}) {
  const validation = validateRequiredFields(userData, pendingData);
  return validation.isValid;
}

/**
 * Récupère le username valide (priorité au formulaire)
 * @param {Object} userData - Les données de l'utilisateur
 * @param {Object} pendingData - Les données en attente du formulaire
 * @param {Object} payload - Les données Google OAuth
 * @returns {string} Le username valide
 */
export function getValidUsername(userData = {}, pendingData = {}, payload = {}) {
  // Priorité 1 : Username du formulaire
  if (isValidUsername(pendingData?.username)) {
    return pendingData.username;
  }
  
  // Priorité 2 : Username du backend
  if (isValidUsername(userData?.username)) {
    return userData.username;
  }
  
  // Priorité 3 : Prénom Google
  const googleName = payload?.name || payload?.given_name || payload?.family_name;
  if (googleName) {
    return googleName.split(' ')[0];
  }
  
  // Priorité 4 : Email sans @ (fallback)
  if (payload?.email || userData?.email) {
    const email = payload.email || userData.email;
    return email.split('@')[0];
  }
  
  // Dernier recours
  return 'Utilisateur';
}
