// Service worker: deja la app instalable y abrirse sin conexión tras la primera visita.
// Nunca guarda las llamadas al servidor (/.netlify/), que llevan datos de la cuenta.
const CACHE = 'ceci-v1';

self.addEventListener('install', () => self.skipWaiting());

self.addEventListener('activate', evento => {
  evento.waitUntil(
    caches.keys()
      .then(claves => Promise.all(claves.filter(c => c !== CACHE).map(c => caches.delete(c))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', evento => {
  const pedido = evento.request;
  const url = new URL(pedido.url);
  if (pedido.method !== 'GET' || url.origin !== self.location.origin || url.pathname.startsWith('/.netlify/')) return;

  if (pedido.mode === 'navigate') {
    // Páginas: red primero (para recibir versiones nuevas) y, sin conexión, la última guardada.
    evento.respondWith(
      fetch(pedido)
        .then(resp => {
          const copia = resp.clone();
          caches.open(CACHE).then(c => c.put('/index.html', copia));
          return resp;
        })
        .catch(() => caches.match('/index.html'))
    );
    return;
  }

  // Archivos (js, css, iconos): los de la caché al instante y se actualizan en segundo plano.
  evento.respondWith(
    caches.open(CACHE).then(async cache => {
      const guardado = await cache.match(pedido);
      const red = fetch(pedido)
        .then(resp => {
          if (resp.ok) cache.put(pedido, resp.clone());
          return resp;
        })
        .catch(() => guardado);
      return guardado || red;
    })
  );
});
