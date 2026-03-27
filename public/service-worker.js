/**
 * Service Worker pour MapEvent PWA
 * v9 - Force cache refresh 2026-02-21:
 *   1. Cache versionnÃ© pour forcer le re-tÃ©lÃ©chargement
 *   2. Install copie les anciens caches si le rÃ©seau Ã©choue â†’ cache jamais vide
 *   3. Navigation = CACHE-FIRST â†’ affichage instantanÃ©, mise Ã  jour en arriÃ¨re-plan
 *   4. JS = network-first avec timeout 3s â†’ cache fallback rapide
 *   5. Fallback HTML sombre intÃ©grÃ© â†’ jamais de page blanche mÃªme offline
 *   6. Navigation Preload pour accÃ©lÃ©rer le dÃ©marrage Ã  froid du SW
 */

// Cache versionnÃ© - changer la version force un re-install
const CACHE = 'mapevent-app-v24';

// Assets critiques Ã  prÃ©-cacher
const CRITICAL_ASSETS = [
  '/mapevent.html',
  '/map_logic.js',
  '/auth.js',
  '/indexeddb_service.js',
  '/js/load-modules.js',
  '/js/core/profile-validator.js',
  '/js/services/notifications.js',
  '/js/services/storage.js'
];

// Fallback HTML sombre (jamais de page blanche, mÃªme sans cache ni rÃ©seau)
const OFFLINE_HTML = '<!DOCTYPE html><html lang="fr" style="background:#020617"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#020617"><title>MapEvent</title></head><body style="background:#020617;color:white;display:flex;align-items:center;justify-content:center;height:100vh;font-family:-apple-system,BlinkMacSystemFont,sans-serif;margin:0"><div style="text-align:center"><div style="color:#00ffc3;font-size:22px;font-weight:800;margin-bottom:16px">MapEvent</div><div style="width:40px;height:40px;border:3px solid rgba(0,255,195,.2);border-top-color:#00ffc3;border-radius:50%;animation:s .8s linear infinite;margin:0 auto"></div><style>@keyframes s{to{transform:rotate(360deg)}}</style><p style="color:#9ca3af;margin-top:16px;font-size:14px">Chargement...</p><button onclick="location.reload()" style="margin-top:20px;padding:12px 32px;background:linear-gradient(135deg,#22c55e,#4ade80);color:#022c22;border:none;border-radius:12px;font-size:15px;font-weight:700;cursor:pointer">Recharger</button><p style="color:#4b5563;margin-top:12px;font-size:11px">Si le probl\u00e8me persiste, v\u00e9rifiez votre connexion internet</p></div></body></html>';

// ===== INSTALLATION =====
// PrÃ©-cache les assets critiques. Si le rÃ©seau Ã©choue, copie depuis les anciens caches.
// RÃ©sultat: le cache n'est JAMAIS vide aprÃ¨s installation.
self.addEventListener('install', (event) => {
  console.log('[SW v12] Installation...');
  event.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE);

      await Promise.allSettled(
        CRITICAL_ASSETS.map(async (url) => {
          // 1) Essayer le rÃ©seau (derniÃ¨re version)
          try {
            const resp = await fetch(url, { cache: 'no-cache' });
            if (resp.ok) {
              await cache.put(url, resp);
              console.log('[SW v12] PrÃ©-cachÃ© (rÃ©seau):', url);
              return;
            }
          } catch (e) {
            console.warn('[SW v12] Fetch Ã©chouÃ© pour', url, e.message);
          }

          // 2) RÃ©seau Ã©chouÃ© â†’ vÃ©rifier si on a dÃ©jÃ  une version en cache
          const existing = await cache.match(url);
          if (existing) {
            console.log('[SW v12] DÃ©jÃ  en cache:', url);
            return;
          }

          // 3) Pas en cache non plus â†’ chercher dans TOUS les caches (migration v5/v6)
          const fromOld = await caches.match(url, { ignoreSearch: true });
          if (fromOld) {
            await cache.put(url, fromOld.clone());
            console.log('[SW v12] CopiÃ© depuis ancien cache:', url);
          }
        })
      );

      // Aussi copier le HTML depuis les anciens caches dynamiques
      const oldHtml = await caches.match('/mapevent.html');
      if (!await cache.match('/mapevent.html') && oldHtml) {
        await cache.put('/mapevent.html', oldHtml.clone());
      }

      await self.skipWaiting();
      console.log('[SW v12] Installation terminÃ©e');
    })()
  );
});

// ===== ACTIVATION =====
// Active Navigation Preload, supprime les ANCIENS caches versionnÃ©s (v5, v6, etc.)
// Le cache unique 'mapevent-app' n'est JAMAIS supprimÃ©.
self.addEventListener('activate', (event) => {
  console.log('[SW v12] Activation...');
  event.waitUntil(
    (async () => {
      // Activer Navigation Preload (accÃ©lÃ¨re le dÃ©marrage Ã  froid du SW)
      if (self.registration.navigationPreload) {
        try { await self.registration.navigationPreload.enable(); }
        catch (e) { console.warn('[SW v12] NavigationPreload non supportÃ©'); }
      }

      // Supprimer les anciens caches versionnÃ©s (v5, v6, etc.) - pas 'mapevent-app'
      const names = await caches.keys();
      await Promise.all(
        names
          .filter(n => n !== CACHE)
          .map(n => {
            console.log('[SW v12] Suppression ancien cache:', n);
            return caches.delete(n);
          })
      );

      await self.clients.claim();
      console.log('[SW v12] Activation terminÃ©e, clients.claim() OK');
    })()
  );
});

// ===== HELPER: Fetch avec timeout =====
function fetchWithTimeout(request, timeoutMs, fetchOptions = {}) {
  return new Promise((resolve, reject) => {
    const controller = new AbortController();
    const timer = setTimeout(() => {
      controller.abort();
      reject(new Error('Timeout ' + timeoutMs + 'ms'));
    }, timeoutMs);

    fetch(request, { ...fetchOptions, signal: controller.signal })
      .then(resp => { clearTimeout(timer); resolve(resp); })
      .catch(err => { clearTimeout(timer); reject(err); });
  });
}

// ===== INTERCEPTION DES REQUÃŠTES =====
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Ignorer non-GET, API Lambda, CDN externes
  if (request.method !== 'GET') return;
  if (url.hostname.includes('lambda-url') || url.pathname.startsWith('/api/')) return;
  if (url.origin !== self.location.origin) return;

  // ================================================================
  // WIDGET PAGES = NETWORK-FIRST STRICT
  // Evite de servir une ancienne version du widget depuis le cache.
  // ================================================================
  if (url.pathname === '/widget-promo.html' || url.pathname === '/widget.html') {
    event.respondWith(
      (async () => {
        try {
          const resp = await fetch(request, { cache: 'no-cache' });
          if (resp && resp.ok) {
            const cache = await caches.open(CACHE);
            await cache.put(request, resp.clone());
          }
          return resp;
        } catch (e) {
          const cached = await caches.match(request, { ignoreSearch: true });
          if (cached) return cached;
          return new Response('Widget indisponible', { status: 503, statusText: 'Service Unavailable' });
        }
      })()
    );
    return;
  }

  // ================================================================
  // HTML NAVIGATION = NETWORK-FIRST (fallback cache)
  //
  // Priorise la version serveur pour que les correctifs UI apparaissent
  // immÃ©diatement. Si le rÃ©seau Ã©choue, fallback sur cache.
  // ================================================================
  if (request.mode === 'navigate' ||
      url.pathname.endsWith('.html') ||
      url.pathname === '/' ||
      (request.headers.get('accept') || '').indexOf('text/html') !== -1) {

    event.respondWith(
      (async () => {
        try {
          let resp = null;
          if (event.preloadResponse) {
            try { resp = await event.preloadResponse; } catch (e) {}
          }
          if (!resp || !resp.ok) {
            resp = await fetch(request, { cache: 'no-cache' });
          }
          if (resp && resp.ok) {
            const cache = await caches.open(CACHE);
            await cache.put(request, resp.clone());
            await cache.put('/mapevent.html', resp.clone());
            return resp;
          }
        } catch (e) {
          console.warn('[SW] HTML network failed, fallback cache:', e.message);
        }

        let cached = await caches.match(request);
        if (!cached) cached = await caches.match('/mapevent.html');
        if (cached) return cached;

        console.warn('[SW v12] âŒ Fallback offline HTML');
        return new Response(OFFLINE_HTML, {
          status: 200,
          headers: { 'Content-Type': 'text/html; charset=utf-8' }
        });
      })()
    );
    return;
  }

  // ================================================================
  // map_logic.js = NETWORK-FIRST SANS TIMEOUT
  // Evite de rester bloque sur une ancienne version cachee.
  // ================================================================
  if (url.pathname === '/map_logic.js' || url.pathname === '/publish-form.js') {
    event.respondWith(
      (async () => {
        try {
          const resp = await fetch(request, { cache: 'no-cache' });
          if (resp && resp.ok) {
            const cache = await caches.open(CACHE);
            await cache.put(request, resp.clone());
            await cache.put(url.pathname, resp.clone());
          }
          return resp;
        } catch (e) {
          let cached = await caches.match(request);
          if (!cached && url.search) cached = await caches.match(url.pathname);
          if (cached) return cached;
          return new Response('', { status: 503, statusText: 'Service Unavailable' });
        }
      })()
    );
    return;
  }

  // ================================================================
  // JS = NETWORK-FIRST AVEC TIMEOUT 3s + CACHE FALLBACK
  // Essaie le rÃ©seau pour la derniÃ¨re version, mais si c'est lent
  // (> 3s), sert immÃ©diatement depuis le cache.
  // ignoreSearch â†’ map_logic.js?v=xxx matche /map_logic.js en cache
  // ================================================================
  if (url.pathname.endsWith('.js')) {
    event.respondWith(
      (async () => {
        try {
          const resp = await fetchWithTimeout(request, 8000, { cache: 'no-cache' });
          if (resp.ok) {
            const cache = await caches.open(CACHE);
            // Cacher sous l'URL complÃ¨te ET sans query string
            await cache.put(request, resp.clone());
            if (url.search) {
              await cache.put(url.pathname, resp.clone());
            }
          }
          return resp;
        } catch (e) {
          // RÃ©seau lent ou offline â†’ servir depuis le cache
          let cached = await caches.match(request);
          if (!cached && url.search) {
            cached = await caches.match(url.pathname);
          }
          if (cached) {
            console.log('[SW v12] JS depuis cache (timeout/offline):', url.pathname);
            return cached;
          }
          console.warn('[SW v12] JS introuvable:', url.pathname);
          return new Response('', { status: 503, statusText: 'Service Unavailable' });
        }
      })()
    );
    return;
  }

  // ================================================================
  // Images/CSS/fonts = STALE-WHILE-REVALIDATE
  // ================================================================
  event.respondWith(
    caches.match(request, { ignoreSearch: true })
      .then(cached => {
        const fetchP = fetch(request)
          .then(resp => {
            if (resp.ok) {
              caches.open(CACHE).then(c => c.put(request, resp));
            }
            return resp.clone();
          })
          .catch(() => null);

        return cached || fetchP;
      })
  );
});

// ===== MESSAGES =====
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  if (event.data && event.data.type === 'SHOW_NOTIFICATION') {
    const d = event.data.payload || event.data;
    self.registration.showNotification(d.title || 'MapEvent', {
      body: d.body || '',
      icon: '/favicon.ico',
      badge: '/favicon.ico',
      tag: d.tag || 'mapevent-fav',
      data: d.data || {},
      requireInteraction: false
    });
  }
});

// ===== PUSH =====
self.addEventListener('push', (event) => {
  let data = { title: 'MapEvent', body: 'Vous avez une notification' };
  try { if (event.data) data = event.data.json(); } catch (e) {}
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: data.icon || '/icons/icon-192x192.png',
      badge: '/favicon.ico',
      tag: data.tag || 'mapevent-push',
      data: data.data || {},
      requireInteraction: false
    })
  );
});

// ===== NOTIFICATION CLICK =====
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const url = (event.notification.data && event.notification.data.url) || '/mapevent.html';
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(windowClients => {
      for (const client of windowClients) {
        if (client.url.includes('mapevent') && 'focus' in client) return client.focus();
      }
      return clients.openWindow(url);
    })
  );
});

console.log('[SW v16] Service Worker chargÃ© - cache-first, push, notification-click');

