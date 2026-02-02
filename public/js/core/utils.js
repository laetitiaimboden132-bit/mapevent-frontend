/**
 * @fileoverview Utilitaires généraux pour MapEvent
 * @module core/utils
 */

/**
 * Échappe les caractères HTML pour prévenir les injections XSS
 * @param {string} str - Chaîne à échapper
 * @returns {string} Chaîne échappée
 */
export function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

/**
 * Formate une plage de dates d'événement au format français suisse
 * @param {string} startIso - Date de début au format ISO
 * @param {string} endIso - Date de fin au format ISO
 * @returns {string} Date formatée (ex: "15.01 14:00–18:00" ou "15.01 14:00 – 16.01 18:00")
 */
export function formatEventDateRange(startIso, endIso) {
  if (!startIso || !endIso) return "";
  const s = new Date(startIso);
  const e = new Date(endIso);

  const optD = { day: "2-digit", month: "2-digit" };
  const optT = { hour: "2-digit", minute: "2-digit" };

  const sd = s.toLocaleDateString("fr-CH", optD);
  const ed = e.toLocaleDateString("fr-CH", optD);
  const st = s.toLocaleTimeString("fr-CH", optT);
  const et = e.toLocaleTimeString("fr-CH", optT);

  if (sd === ed) return `${sd} ${st}–${et}`;
  return `${sd} ${st} – ${ed} ${et}`;
}

/**
 * Masque le numéro d'une adresse pour la protection des données
 * @param {string} address - Adresse complète
 * @returns {string} Adresse avec numéro masqué
 */
export function maskAddressNumber(address) {
  if (!address) return "";
  // Masque le numéro au début de l'adresse (ex: "12 Rue" -> "Rue")
  return address.replace(/^\d+\s+/, "");
}

/**
 * Débounce une fonction pour limiter les appels fréquents
 * @param {Function} func - Fonction à débouncer
 * @param {number} wait - Délai en millisecondes
 * @returns {Function} Fonction débouncée
 */
export function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Throttle une fonction pour limiter les appels
 * @param {Function} func - Fonction à throttler
 * @param {number} limit - Délai minimum entre les appels en millisecondes
 * @returns {Function} Fonction throttlée
 */
export function throttle(func, limit) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

/**
 * Vérifie si une valeur est vide (null, undefined, "", [], {})
 * @param {*} value - Valeur à vérifier
 * @returns {boolean} True si vide
 */
export function isEmpty(value) {
  if (value == null) return true;
  if (typeof value === "string") return value.trim() === "";
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === "object") return Object.keys(value).length === 0;
  return false;
}

/**
 * Clone profond d'un objet
 * @param {*} obj - Objet à cloner
 * @returns {*} Objet cloné
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== "object") return obj;
  if (obj instanceof Date) return new Date(obj.getTime());
  if (obj instanceof Array) return obj.map(item => deepClone(item));
  if (typeof obj === "object") {
    const cloned = {};
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        cloned[key] = deepClone(obj[key]);
      }
    }
    return cloned;
  }
}

// Export pour compatibilité globale (si nécessaire)
if (typeof window !== "undefined") {
  window.escapeHtml = escapeHtml;
  window.formatEventDateRange = formatEventDateRange;
  window.maskAddressNumber = maskAddressNumber;
}
