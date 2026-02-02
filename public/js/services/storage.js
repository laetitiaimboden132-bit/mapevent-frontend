/**
 * @fileoverview Service de stockage centralisé (IndexedDB + LocalStorage)
 * @module services/storage
 */

/**
 * Service de stockage unifié pour IndexedDB et LocalStorage
 */
class StorageService {
  constructor() {
    this.dbName = 'mapevent_db';
    this.dbVersion = 1;
    this.storeName = 'users';
    this.db = null;
  }

  /**
   * Ouvre la connexion IndexedDB
   * @returns {Promise<IDBDatabase>}
   */
  async openDB() {
    if (this.db) {
      return this.db;
    }

    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);

      request.onerror = () => {
        console.error('❌ Erreur ouverture IndexedDB:', request.error);
        reject(request.error);
      };

      request.onsuccess = () => {
        this.db = request.result;
        console.log('✅ IndexedDB ouvert');
        resolve(this.db);
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        if (!db.objectStoreNames.contains(this.storeName)) {
          db.createObjectStore(this.storeName, { keyPath: 'id' });
          console.log('✅ ObjectStore créé');
        }
      };
    });
  }

  /**
   * Sauvegarde des données utilisateur dans IndexedDB
   * @param {string} userId - ID de l'utilisateur
   * @param {Object} userData - Données utilisateur
   * @returns {Promise<void>}
   */
  async saveUser(userId, userData) {
    try {
      const database = await this.openDB();
      const transaction = database.transaction([this.storeName], 'readwrite');
      const store = transaction.objectStore(this.storeName);
      
      const data = {
        id: userId,
        ...userData,
        updatedAt: new Date().toISOString()
      };
      
      await new Promise((resolve, reject) => {
        const request = store.put(data);
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
      });
      
      console.log('✅ Utilisateur sauvegardé dans IndexedDB');
    } catch (error) {
      console.error('❌ Erreur sauvegarde IndexedDB:', error);
      throw error;
    }
  }

  /**
   * Récupère les données utilisateur depuis IndexedDB
   * @param {string} userId - ID de l'utilisateur
   * @returns {Promise<Object|null>}
   */
  async getUser(userId) {
    try {
      const database = await this.openDB();
      const transaction = database.transaction([this.storeName], 'readonly');
      const store = transaction.objectStore(this.storeName);
      
      return new Promise((resolve, reject) => {
        const request = store.get(userId);
        request.onsuccess = () => resolve(request.result || null);
        request.onerror = () => reject(request.error);
      });
    } catch (error) {
      console.error('❌ Erreur récupération IndexedDB:', error);
      return null;
    }
  }

  /**
   * Supprime les données utilisateur de IndexedDB
   * @param {string} userId - ID de l'utilisateur
   * @returns {Promise<void>}
   */
  async deleteUser(userId) {
    try {
      const database = await this.openDB();
      const transaction = database.transaction([this.storeName], 'readwrite');
      const store = transaction.objectStore(this.storeName);
      
      await new Promise((resolve, reject) => {
        const request = store.delete(userId);
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
      });
      
      console.log('✅ Utilisateur supprimé de IndexedDB');
    } catch (error) {
      console.error('❌ Erreur suppression IndexedDB:', error);
      throw error;
    }
  }

  // ============================================
  // LocalStorage API (compatibilité)
  // ============================================

  /**
   * Sauvegarde dans LocalStorage
   * @param {string} key - Clé
   * @param {*} value - Valeur (sera sérialisée en JSON)
   * @param {boolean} useSession - Utiliser sessionStorage au lieu de localStorage
   */
  setItem(key, value, useSession = false) {
    const storage = useSession ? sessionStorage : localStorage;
    try {
      const serialized = typeof value === 'string' ? value : JSON.stringify(value);
      storage.setItem(key, serialized);
    } catch (error) {
      console.error(`❌ Erreur sauvegarde ${useSession ? 'session' : 'local'}Storage:`, error);
    }
  }

  /**
   * Récupère depuis LocalStorage
   * @param {string} key - Clé
   * @param {boolean} useSession - Utiliser sessionStorage
   * @param {boolean} parseJson - Parser le JSON automatiquement
   * @returns {*} Valeur récupérée
   */
  getItem(key, useSession = false, parseJson = true) {
    const storage = useSession ? sessionStorage : localStorage;
    try {
      const value = storage.getItem(key);
      if (value === null) return null;
      
      if (parseJson) {
        try {
          return JSON.parse(value);
        } catch {
          return value; // Retourner tel quel si pas du JSON
        }
      }
      return value;
    } catch (error) {
      console.error(`❌ Erreur récupération ${useSession ? 'session' : 'local'}Storage:`, error);
      return null;
    }
  }

  /**
   * Supprime de LocalStorage
   * @param {string} key - Clé
   * @param {boolean} useSession - Utiliser sessionStorage
   */
  removeItem(key, useSession = false) {
    const storage = useSession ? sessionStorage : localStorage;
    try {
      storage.removeItem(key);
    } catch (error) {
      console.error(`❌ Erreur suppression ${useSession ? 'session' : 'local'}Storage:`, error);
    }
  }

  /**
   * Vide tout le LocalStorage
   * @param {boolean} useSession - Utiliser sessionStorage
   */
  clear(useSession = false) {
    const storage = useSession ? sessionStorage : localStorage;
    try {
      storage.clear();
    } catch (error) {
      console.error(`❌ Erreur clear ${useSession ? 'session' : 'local'}Storage:`, error);
    }
  }

  /**
   * Récupère toutes les clés du LocalStorage
   * @param {boolean} useSession - Utiliser sessionStorage
   * @returns {string[]} Liste des clés
   */
  getAllKeys(useSession = false) {
    const storage = useSession ? sessionStorage : localStorage;
    const keys = [];
    for (let i = 0; i < storage.length; i++) {
      keys.push(storage.key(i));
    }
    return keys;
  }
}

// Instance singleton
const storageService = new StorageService();

// Export pour compatibilité globale
if (typeof window !== "undefined") {
  window.StorageService = storageService;
  
  // Compatibilité avec l'ancien code
  window.saveUserToIndexedDB = (userId, userData) => storageService.saveUser(userId, userData);
  window.getUserFromIndexedDB = (userId) => storageService.getUser(userId);
  window.deleteUserFromIndexedDB = (userId) => storageService.deleteUser(userId);
}

export default storageService;
export { StorageService };
