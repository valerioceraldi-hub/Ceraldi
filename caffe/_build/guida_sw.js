/* Guida di Napoli — uso senza rete. Generato da guida_genera.py (versione __VERSIONE__).
   Pagine: prima la rete (contenuti aggiornati), senza rete la copia salvata. Mappa e foto: copia salvata (non cambiano). */
var CACHE = 'guida-__VERSIONE__';
var FILE = /*__FILE__*/[];
self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) {
    // a gruppi: un file che non risponde non blocca gli altri
    return Promise.all(FILE.map(function (f) { return c.add(new Request(f, { cache: 'reload' })).catch(function () {}); }));
  }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (k) {
    return Promise.all(k.filter(function (n) { return n.indexOf('guida-') === 0 && n !== CACHE; }).map(function (n) { return caches.delete(n); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener('fetch', function (e) {
  var r = e.request;
  if (r.method !== 'GET' || new URL(r.url).origin !== location.origin) return;
  var pagina = r.mode === 'navigate' || /\/$|\.html$/.test(new URL(r.url).pathname);
  if (pagina) {
    e.respondWith(fetch(r).then(function (risp) {
      if (risp.ok) { var copia = risp.clone(); caches.open(CACHE).then(function (c) { c.put(r, copia); }); }
      return risp;
    }).catch(function () { return caches.match(r, { ignoreSearch: true }); }));
  } else {
    e.respondWith(caches.match(r, { ignoreSearch: true }).then(function (x) { return x || fetch(r); }));
  }
});
