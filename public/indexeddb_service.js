// ============================================
// INDEXEDDB SERVICE - Stockage utilisateur
// ============================================
// Service simple pour stocker les données utilisateur dans IndexedDB
// IndexedDB a un quota beaucoup plus élevé que localStorage (plusieurs GB vs 5-10MB)

const DB_NAME = 'mapevent_db';
const DB_VERSION = 1;
const STORE_NAME = 'users';

let db = null;

// Ouvrir la base de données IndexedDB
function openDB() {
  return new Promise((resolve, reject) => {
    if (db) {
      resolve(db);
      return;
    }
    
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    
    request.onerror = () => {
      console.error('❌ Erreur ouverture IndexedDB:', request.error);
      reject(request.error);
    };
    
    request.onsuccess = () => {
      db = request.result;
      console.log('✅ IndexedDB ouvert');
      resolve(db);
    };
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'id' });
        console.log('✅ ObjectStore créé');
      }
    };
  });
}

// Sauvegarder les données utilisateur dans IndexedDB
async function saveUserToIndexedDB(userId, userData) {
  try {
    const database = await openDB();
    const transaction = database.transaction([STORE_NAME], 'readwrite');
    const store = transaction.objectStore(STORE_NAME);
    
    // IndexedDB peut gérer de gros volumes, donc on peut sauvegarder _avatarBase64Original
    const userToSave = { ...userData, id: userId };
    
    // Pour avatar et profilePhoto, réduire seulement si c'est pour localStorage
    // Mais garder _avatarBase64Original pour IndexedDB (qui peut gérer de gros volumes)
    // Ne pas exclure _avatarBase64Original - IndexedDB peut le gérer
    
    // Réduire avatar et profilePhoto seulement pour éviter les doublons
    // (on garde _avatarBase64Original pour l'affichage)
    if (userToSave.avatar && userToSave.avatar.startsWith('data:image') && userToSave.avatar.length > 1000) {
      // Garder l'avatar dans _avatarBase64Original mais réduire dans avatar
      if (!userToSave._avatarBase64Original) {
        userToSave._avatarBase64Original = userToSave.avatar;
      }
      userToSave.avatar = '👤';
    }
    if (userToSave.profilePhoto && userToSave.profilePhoto.startsWith('data:image') && userToSave.profilePhoto.length > 1000) {
      // Garder profilePhoto dans _avatarBase64Original mais réduire dans profilePhoto
      if (!userToSave._avatarBase64Original) {
        userToSave._avatarBase64Original = userToSave.profilePhoto;
      }
      userToSave.profilePhoto = null;
    }
    
    await new Promise((resolve, reject) => {
      const request = store.put(userToSave);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
    
    console.log('✅ Données utilisateur sauvegardées dans IndexedDB', {
      hasAvatarBase64Original: !!userToSave._avatarBase64Original,
      avatarBase64OriginalLength: userToSave._avatarBase64Original ? userToSave._avatarBase64Original.length : 0
    });
    return true;
  } catch (error) {
    console.error('❌ Erreur sauvegarde IndexedDB:', error);
    // Fallback vers localStorage
    return saveUserToLocalStorage(userId, userData);
  }
}

// Charger les données utilisateur depuis IndexedDB
async function loadUserFromIndexedDB(userId) {
  try {
    const database = await openDB();
    const transaction = database.transaction([STORE_NAME], 'readonly');
    const store = transaction.objectStore(STORE_NAME);
    
    const userData = await new Promise((resolve, reject) => {
      const request = store.get(userId);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
    
    if (userData) {
      console.log('✅ Données utilisateur chargées depuis IndexedDB');
      return userData;
    } else {
      console.log('ℹ️ Aucune donnée utilisateur dans IndexedDB');
      return null;
    }
  } catch (error) {
    console.error('❌ Erreur chargement IndexedDB:', error);
    // Fallback vers localStorage
    return loadUserFromLocalStorage(userId);
  }
}

// Supprimer les données utilisateur de IndexedDB
async function deleteUserFromIndexedDB(userId) {
  try {
    const database = await openDB();
    const transaction = database.transaction([STORE_NAME], 'readwrite');
    const store = transaction.objectStore(STORE_NAME);
    
    await new Promise((resolve, reject) => {
      const request = store.delete(userId);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
    
    console.log('✅ Données utilisateur supprimées de IndexedDB');
    return true;
  } catch (error) {
    console.error('❌ Erreur suppression IndexedDB:', error);
    return false;
  }
}

// Fallback localStorage (pour compatibilité)
function saveUserToLocalStorage(userId, userData) {
  try {
    const userToSave = { ...userData };
    delete userToSave._avatarBase64Original;
    
    if (userToSave.avatar && userToSave.avatar.startsWith('data:image') && userToSave.avatar.length > 1000) {
      userToSave.avatar = '👤';
    }
    if (userToSave.profilePhoto && userToSave.profilePhoto.startsWith('data:image') && userToSave.profilePhoto.length > 1000) {
      userToSave.profilePhoto = null;
    }
    
    localStorage.setItem('currentUser', JSON.stringify(userToSave));
    return true;
  } catch (error) {
    console.error('❌ Erreur sauvegarde localStorage:', error);
    return false;
  }
}

function loadUserFromLocalStorage(userId) {
  try {
    const userData = localStorage.getItem('currentUser');
    if (userData) {
      return JSON.parse(userData);
    }
    return null;
  } catch (error) {
    console.error('❌ Erreur chargement localStorage:', error);
    return null;
  }
}

// Exporter les fonctions
window.indexedDBService = {
  saveUser: saveUserToIndexedDB,
  loadUser: loadUserFromIndexedDB,
  deleteUser: deleteUserFromIndexedDB,
  openDB: openDB
};

