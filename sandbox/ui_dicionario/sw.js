// Service Worker do Códice Tréppio (V8.5 - Brasão do Conde, Cache Rápido & Zero Bloqueio)
const CACHE_NAME = 'treppio-v8-5-cache-brasao';
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './dados_dicionario_conde.js?v=8.5.0',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  './icon-maskable-512.png',
  './favicon.ico'
];

// Instalação: pré-carrega shell, brasão e léxico sem bloquear ativação
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE).catch((err) => {
        console.warn('[SW] Falha parcial no cache inicial:', err);
      });
    })
  );
});

// Ativação: remove versões antigas e assume imediatamente
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((k) => {
          if (k !== CACHE_NAME) {
            return caches.delete(k);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;

  // APIs dinâmicas do Launcher: sempre Network-Only (sem cache obsoleto)
  if (url.pathname.startsWith('/api/')) return;

  // Dados massivos do léxico: Cache-First com ignoreSearch para leitura instantânea (<5 ms)
  if (url.pathname.endsWith('/dados_dicionario_conde.js') || url.pathname === '/dados_dicionario_conde.js') {
    event.respondWith(
      caches.open(CACHE_NAME).then((cache) => {
        return cache.match(event.request, { ignoreSearch: true }).then((cached) => {
          if (cached) return cached;
          return fetch(event.request).then((networkResponse) => {
            if (networkResponse && networkResponse.status === 200) {
              cache.put(event.request, networkResponse.clone());
            }
            return networkResponse;
          });
        });
      })
    );
    return;
  }

  // Demais assets (shell HTML, ícones do Brasão, manifest): Stale-While-Revalidate
  event.respondWith(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.match(event.request, { ignoreSearch: url.pathname.endsWith('.js') }).then((cached) => {
        const networkPromise = fetch(event.request)
          .then((networkResponse) => {
            if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
              cache.put(event.request, networkResponse.clone());
            }
            return networkResponse;
          })
          .catch(() => null);

        if (cached) {
          event.waitUntil(networkPromise);
          return cached;
        }
        return networkPromise.then((res) => {
          if (res) return res;
          if (event.request.headers.get('accept') && event.request.headers.get('accept').includes('text/html')) {
            return cache.match('./index.html');
          }
          return Response.error();
        });
      });
    })
  );
});
