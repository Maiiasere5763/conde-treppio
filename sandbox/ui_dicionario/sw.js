// Service Worker do Códice Tréppio (V8.2 - Redesign Editorial Obsidiana & Ouro)
const CACHE_NAME = 'treppio-v8-2-cache-editorial';
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './dados_dicionario_conde.js?v=8.2.0',
  './dicionario_formas_expandidas.json',
  './manifest.json',
  './icon-512.png'
];

// Instalação: baixa os assets e assume o controle sem esperar
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE).catch((err) => {
        console.warn('Falha parcial no cache inicial:', err);
      });
    })
  );
});

// Ativação: expurga agressivamente TODOS os caches anteriores
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((k) => {
          if (k !== CACHE_NAME) {
            console.log('[SW] Purgando cache legado:', k);
            return caches.delete(k);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Estratégia Network-First: sempre prioriza a versão mais recente da rede
// com fallback elegante para o Cache Storage caso o usuário esteja offline
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      })
      .catch(() => {
        // Fallback offline a partir do cache
        return caches.match(event.request).then((cached) => {
          if (cached) return cached;
          if (event.request.headers.get('accept') && event.request.headers.get('accept').includes('text/html')) {
            return caches.match('./index.html');
          }
        });
      })
  );
});
