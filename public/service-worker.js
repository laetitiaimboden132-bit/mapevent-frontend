/**
 * Service Worker pour MapEvent PWA
 * v8 - Force refresh après revert split code:
 *   1. Cache UNIQUE (pas de version) → jamais de "trou" entre anciennes et nouvelles versions
 *   2. Install copie les anciens caches si le réseau échoue → cache jamais vide
 *   3. Navigation = CACHE-FIRST → affichage instantané, mise à jour en arrière-plan
 *   4. JS = network-first avec timeout 3s → cache fallback rapide
 *   5. Fallback HTML sombre intégré → jamais de page blanche même offline
 *   6. Navigation Preload pour accélérer le démarrage à froid du SW
 */

// UN SEUL cache, jamais supprimé, mis à jour en place
const CACHE = 'mapevent-app';

// Assets critiques à pré-cacher
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

// Fallback HTML sombre (jamais de page blanche, même sans cache ni réseau)
const OFFLINE_HTML = '<!DOCTYPE html><html lang="fr" style="background:#020617"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#020617"><title>MapEvent</title></head><body style="background:#020617;color:white;display:flex;align-items:center;justify-content:center;height:100vh;font-family:-apple-system,BlinkMacSystemFont,sans-serif;margin:0"><div style="text-align:center"><div style="color:#00ffc3;font-size:22px;font-weight:800;margin-bottom:16px">MapEvent</div><div style="width:40px;height:40px;border:3px solid rgba(0,255,195,.2);border-top-color:#00ffc3;border-radius:50%;animation:s .8s linear infinite;margin:0 auto"></div><style>@keyframes s{to{transform:rotate(360deg)}}</style><p style="color:#9ca3af;margin-top:16px;font-size:14px">Chargement...</p><button onclick="location.reload()" style="margin-top:20px;padding:12px 32px;background:linear-gradient(135deg,#22c55e,#4ade80);color:#022c22;border:none;border-radius:12px;font-size:15px;font-weight:700;cursor:pointer">Recharger</button><p style="color:#4b5563;margin-top:12px;font-size:11px">Si le probl\u00e8me persiste, v\u00e9rifiez votre connexion internet</p></div></body></html>';

// ===== INSTALLATION =====
// Pré-cache les assets critiques. Si le réseau échoue, copie depuis les anciens caches.
// Résultat: le cache n'est JAMAIS vide après installation.
self.addEventListener('install', (event) => {
  console.log('[SW v8] Installation...');
  event.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE);

      await Promise.allSettled(
        CRITICAL_ASSETS.map(async (url) => {
          // 1) Essayer le réseau (dernière version)
          try {
            const resp = await fetch(url, { cache: 'no-cache' });
            if (resp.ok) {
              await cache.put(url, resp);
              console.log('[SW v8] Pré-caché (réseau):', url);
              return;
            }
          } catch (e) {
            console.warn('[SW v8] Fetch échoué pour', url, e.message);
          }

          // 2) Réseau échoué → vérifier si on a déjà une version en cache
          const existing = await cache.match(url);
          if (existing) {
            console.log('[SW v8] Déjà en cache:', url);
            return;
          }

          // 3) Pas en cache non plus → chercher dans TOUS les caches (migration v5/v6)
          const fromOld = await caches.match(url, { ignoreSearch: true });
          if (fromOld) {
            await cache.put(url, fromOld.clone());
            console.log('[SW v8] Copié depuis ancien cache:', url);
          }
        })
      );

      // Aussi copier le HTML depuis les anciens caches dynamiques
      const oldHtml = await caches.match('/mapevent.html');
      if (!await cache.match('/mapevent.html') && oldHtml) {
        await cache.put('/mapevent.html', oldHtml.clone());
      }

      await self.skipWaiting();
      console.log('[SW v8] Installation terminée');
    })()
  );
});

// ===== ACTIVATION =====
// Active Navigation Preload, supprime les ANCIENS caches versionnés (v5, v6, etc.)
// Le cache unique 'mapevent-app' n'est JAMAIS supprimé.
self.addEventListener('activate', (event) => {
  console.log('[SW v8] Activation...');
  event.waitUntil(
    (async () => {
      // Activer Navigation Preload (accélère le démarrage à froid du SW)
      if (self.registration.navigationPreload) {
        try { await self.registration.navigationPreload.enable(); }
        catch (e) { console.warn('[SW v8] NavigationPreload non supporté'); }
      }

      // Supprimer les anciens caches versionnés (v5, v6, etc.) - pas 'mapevent-app'
      const names = await caches.keys();
      await Promise.all(
        names
          .filter(n => n !== CACHE)
          .map(n => {
            console.log('[SW v8] Suppression ancien cache:', n);
            return caches.delete(n);
          })
      );

      await self.clients.claim();
      console.log('[SW v8] Activation terminée, clients.claim() OK');
    })()
  );
});

// ===== HELPER: Fetch avec timeout =====
function fetchWithTimeout(request, timeoutMs) {
  return new Promise((resolve, reject) => {
    const controller = new AbortController();
    const timer = setTimeout(() => {
      controller.abort();
      reject(new Error('Timeout ' + timeoutMs + 'ms'));
    }, timeoutMs);

    fetch(request, { signal: controller.signal })
      .then(resp => { clearTimeout(timer); resolve(resp); })
      .catch(err => { clearTimeout(timer); reject(err); });
  });
}

// ===== INTERCEPTION DES REQUÊTES =====
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Ignorer non-GET, API Lambda, CDN externes
  if (request.method !== 'GET') return;
  if (url.hostname.includes('lambda-url') || url.pathname.startsWith('/api/')) return;
  if (url.origin !== self.location.origin) return;

  // ================================================================
  // HTML NAVIGATION = CACHE-FIRST (stale-while-revalidate)
  //
  // POURQUOI: Quand l'utilisateur ouvre la PWA depuis le raccourci,
  // le SW doit répondre IMMÉDIATEMENT avec le HTML en cache.
  // Le réseau est utilisé en arrière-plan pour mettre à jour le cache.
  // Résultat: 0 écran blanc, affichage instantané.
  // ================================================================
  if (request.mode === 'navigate' ||
      url.pathname.endsWith('.html') ||
      url.pathname === '/' ||
      (request.headers.get('accept') || '').indexOf('text/html') !== -1) {

    event.respondWith(
      (async () => {
        // 1) Chercher dans le cache (ignoreSearch pour matcher les variations d'URL)
        let cached = await caches.match(request, { ignoreSearch: true });
        if (!cached) {
          cached = await caches.match('/mapevent.html');
        }

        // 2) Lancer le fetch réseau en arrière-plan (pour mettre à jour le cache)
        const networkUpdate = (async () => {
          try {
            // Navigation Preload: le réseau a déjà commencé pendant le démarrage du SW
            let resp = null;
            if (event.preloadResponse) {
              try { resp = await event.preloadResponse; } catch (e) {}
            }
            if (!resp || !resp.ok) {
              resp = await fetch(request, { cache: 'no-cache' });
            }

            if (resp && resp.ok) {
              const cache = await caches.open(CACHE);
              // Cacher sous l'URL de la requête ET sous /mapevent.html (pour le fallback)
              await cache.put(request, resp.clone());
              await cache.put('/mapevent.html', resp.clone());
              console.log('[SW v8] HTML mis à jour en cache');
            }
            return resp;
          } catch (e) {
            console.warn('[SW v8] Mise à jour HTML échouée:', e.message);
            return null;
          }
        })();

        // 3) Si on a un cache → servir IMMÉDIATEMENT, mettre à jour en fond
        if (cached) {
          console.log('[SW v8] ✅ Navigation servie depuis le cache (instantané)');
          event.waitUntil(networkUpdate);
          return cached;
        }

        // 4) Pas de cache → attendre le réseau (premier lancement)
        console.log('[SW v8] ⏳ Pas de cache, attente réseau...');
        const networkResp = await networkUpdate;
        if (networkResp && networkResp.ok) {
          return networkResp;
        }

        // 5) Ni cache ni réseau → page offline sombre (JAMAIS de page blanche)
        console.warn('[SW v8] ❌ Fallback offline HTML');
        return new Response(OFFLINE_HTML, {
          status: 200,
          headers: { 'Content-Type': 'text/html; charset=utf-8' }
        });
      })()
    );
    return;
  }

  // ================================================================
  // JS = NETWORK-FIRST AVEC TIMEOUT 3s + CACHE FALLBACK
  // Essaie le réseau pour la dernière version, mais si c'est lent
  // (> 3s), sert immédiatement depuis le cache.
  // ignoreSearch → map_logic.js?v=xxx matche /map_logic.js en cache
  // ================================================================
  if (url.pathname.endsWith('.js')) {
    event.respondWith(
      (async () => {
        try {
          const resp = await fetchWithTimeout(request, 3000);
          if (resp.ok) {
            const cache = await caches.open(CACHE);
            // Cacher sous l'URL complète ET sans query string
            await cache.put(request, resp.clone());
            if (url.search) {
              await cache.put(url.pathname, resp.clone());
            }
          }
          return resp;
        } catch (e) {
          // Réseau lent ou offline → servir depuis le cache
          const cached = await caches.match(request, { ignoreSearch: true });
          if (cached) {
            console.log('[SW v8] JS depuis cache (timeout/offline):', url.pathname);
            return cached;
          }
          console.warn('[SW v8] JS introuvable:', url.pathname);
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
});

console.log('[SW v8] Service Worker chargé - cache-first, single cache, migration-safe');
