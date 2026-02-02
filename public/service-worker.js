/**
 * Service Worker pour MapEvent PWA
 * Gère le cache et le mode hors-ligne
 */

const CACHE_NAME = 'mapevent-v1';
const STATIC_CACHE = 'mapevent-static-v1';
const DYNAMIC_CACHE = 'mapevent-dynamic-v1';

// Fichiers à mettre en cache (optionnel, ne bloque pas si échec)
const STATIC_FILES = [
  '/mapevent.html',
  '/manifest.json'
];

// Installation du Service Worker - Mode non-bloquant
self.addEventListener('install', (event) => {
  console.log('[SW] Installation...');
  // Skip waiting immédiatement pour ne pas bloquer
  self.skipWaiting();
  
  // Cache optionnel en arrière-plan (ne bloque pas l'installation)
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('[SW] Mise en cache optionnelle...');
        // Utiliser addAll avec catch pour ignorer les erreurs
        return Promise.allSettled(
          STATIC_FILES.map(url => 
            cache.add(url).catch(err => {
              console.warn('[SW] Cache ignoré pour:', url, err.message);
              return null;
            })
          )
        );
      })
      .then(() => {
        console.log('[SW] Installation terminée');
      })
      .catch((error) => {
        console.warn('[SW] Erreur installation (ignorée):', error);
      })
  );
});

// Activation du Service Worker
self.addEventListener('activate', (event) => {
  console.log('[SW] Activation...');
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((name) => name !== STATIC_CACHE && name !== DYNAMIC_CACHE)
            .map((name) => {
              console.log('[SW] Suppression ancien cache:', name);
              return caches.delete(name);
            })
        );
      })
      .then(() => {
        console.log('[SW] Activation terminée');
        return self.clients.claim();
      })
  );
});

// Interception des requêtes - Mode passif (ne bloque jamais)
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Ignorer les requêtes non-GET
  if (request.method !== 'GET') {
    return;
  }

  // Ignorer les requêtes vers des domaines externes
  if (url.origin !== self.location.origin) {
    return;
  }

  // Ignorer les fichiers JS critiques - laisser le réseau les gérer directement
  if (url.pathname.endsWith('.js') || url.pathname.includes('/js/')) {
    return;
  }

  // Pour les API, toujours aller au réseau
  if (url.pathname.startsWith('/api/')) {
    return;
  }

  // Pour les autres fichiers statiques, essayer le cache puis le réseau
  event.respondWith(
    caches.match(request)
      .then(cachedResponse => {
        if (cachedResponse) {
          // Mettre à jour en arrière-plan
          fetch(request).then(response => {
            if (response.ok) {
              caches.open(STATIC_CACHE).then(cache => cache.put(request, response));
            }
          }).catch(() => {});
          return cachedResponse;
        }
        return fetch(request);
      })
      .catch(() => fetch(request))
  );
});

// Stratégie Cache First (pour fichiers statiques)
async function cacheFirst(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    // Mettre à jour en arrière-plan
    fetchAndCache(request);
    return cachedResponse;
  }
  return fetchAndCache(request);
}

// Stratégie Network First (pour API)
async function networkFirst(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    // Retourner une réponse d'erreur hors-ligne pour les API
    return new Response(
      JSON.stringify({ error: 'Hors ligne', offline: true }),
      { 
        status: 503, 
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Fetch et mise en cache
async function fetchAndCache(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    // Retourner page hors-ligne si disponible
    const offlineResponse = await caches.match('/mapevent.html');
    if (offlineResponse) {
      return offlineResponse;
    }
    throw error;
  }
}

// Gestion des messages (pour mise à jour forcée, etc.)
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

console.log('[SW] Service Worker chargé');
