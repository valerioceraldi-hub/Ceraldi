/* Guida di Napoli — uso senza rete. Generato da guida_genera.py (versione 619ebebff840).
   Pagine: prima la rete (contenuti aggiornati), senza rete la copia salvata. Mappa e foto: copia salvata (non cambiano). */
var CACHE = 'guida-619ebebff840';
var FILE = ["./", "./en/", "./fr/", "./de/", "./es/", "./font/bodonimoda-400-latin-ext.woff2", "./font/bodonimoda-400-latin.woff2", "./font/jost-400-latin-ext.woff2", "./font/jost-400-latin.woff2", "./mappa/glyphs/Noto Sans Italic/0-255.pbf", "./mappa/glyphs/Noto Sans Italic/256-511.pbf", "./mappa/glyphs/Noto Sans Italic/512-767.pbf", "./mappa/glyphs/Noto Sans Italic/768-1023.pbf", "./mappa/glyphs/Noto Sans Italic/7936-8191.pbf", "./mappa/glyphs/Noto Sans Italic/8192-8447.pbf", "./mappa/glyphs/Noto Sans Medium/0-255.pbf", "./mappa/glyphs/Noto Sans Medium/256-511.pbf", "./mappa/glyphs/Noto Sans Medium/512-767.pbf", "./mappa/glyphs/Noto Sans Medium/768-1023.pbf", "./mappa/glyphs/Noto Sans Medium/7936-8191.pbf", "./mappa/glyphs/Noto Sans Medium/8192-8447.pbf", "./mappa/glyphs/Noto Sans Regular/0-255.pbf", "./mappa/glyphs/Noto Sans Regular/256-511.pbf", "./mappa/glyphs/Noto Sans Regular/512-767.pbf", "./mappa/glyphs/Noto Sans Regular/768-1023.pbf", "./mappa/glyphs/Noto Sans Regular/7936-8191.pbf", "./mappa/glyphs/Noto Sans Regular/8192-8447.pbf", "./mappa/maplibre-gl.css", "./mappa/maplibre-gl.js", "./mappa/sprite/light.json", "./mappa/sprite/light.png", "./mappa/sprite/light@2x.json", "./mappa/sprite/light@2x.png", "./mappa/stile.json", "./mappa/tiles/10/552/384.pbf", "./mappa/tiles/11/1104/768.pbf", "./mappa/tiles/11/1104/769.pbf", "./mappa/tiles/11/1105/768.pbf", "./mappa/tiles/11/1105/769.pbf", "./mappa/tiles/12/2208/1537.pbf", "./mappa/tiles/12/2208/1538.pbf", "./mappa/tiles/12/2209/1537.pbf", "./mappa/tiles/12/2209/1538.pbf", "./mappa/tiles/12/2210/1537.pbf", "./mappa/tiles/12/2210/1538.pbf", "./mappa/tiles/12/2211/1537.pbf", "./mappa/tiles/12/2211/1538.pbf", "./mappa/tiles/13/4419/3075.pbf", "./mappa/tiles/13/4419/3076.pbf", "./mappa/tiles/13/4420/3075.pbf", "./mappa/tiles/13/4420/3076.pbf", "./mappa/tiles/14/8839/6150.pbf", "./mappa/tiles/14/8839/6151.pbf", "./mappa/tiles/14/8839/6152.pbf", "./mappa/tiles/14/8839/6153.pbf", "./mappa/tiles/14/8840/6150.pbf", "./mappa/tiles/14/8840/6151.pbf", "./mappa/tiles/14/8840/6152.pbf", "./mappa/tiles/14/8840/6153.pbf", "./mappa/tiles/14/8841/6150.pbf", "./mappa/tiles/14/8841/6151.pbf", "./mappa/tiles/14/8841/6152.pbf", "./mappa/tiles/14/8841/6153.pbf", "./mappa/tiles/15/17678/12301.pbf", "./mappa/tiles/15/17678/12302.pbf", "./mappa/tiles/15/17678/12303.pbf", "./mappa/tiles/15/17678/12304.pbf", "./mappa/tiles/15/17678/12305.pbf", "./mappa/tiles/15/17678/12306.pbf", "./mappa/tiles/15/17678/12307.pbf", "./mappa/tiles/15/17679/12301.pbf", "./mappa/tiles/15/17679/12302.pbf", "./mappa/tiles/15/17679/12303.pbf", "./mappa/tiles/15/17679/12304.pbf", "./mappa/tiles/15/17679/12305.pbf", "./mappa/tiles/15/17679/12306.pbf", "./mappa/tiles/15/17679/12307.pbf", "./mappa/tiles/15/17680/12301.pbf", "./mappa/tiles/15/17680/12302.pbf", "./mappa/tiles/15/17680/12303.pbf", "./mappa/tiles/15/17680/12304.pbf", "./mappa/tiles/15/17680/12305.pbf", "./mappa/tiles/15/17680/12306.pbf", "./mappa/tiles/15/17680/12307.pbf", "./mappa/tiles/15/17681/12301.pbf", "./mappa/tiles/15/17681/12302.pbf", "./mappa/tiles/15/17681/12303.pbf", "./mappa/tiles/15/17681/12304.pbf", "./mappa/tiles/15/17681/12305.pbf", "./mappa/tiles/15/17681/12306.pbf", "./mappa/tiles/15/17681/12307.pbf", "./mappa/tiles/15/17682/12301.pbf", "./mappa/tiles/15/17682/12302.pbf", "./mappa/tiles/15/17682/12303.pbf", "./mappa/tiles/15/17682/12304.pbf", "./mappa/tiles/15/17682/12305.pbf", "./mappa/tiles/15/17682/12306.pbf", "./mappa/tiles/15/17682/12307.pbf", "./mappa/tiles/15/17683/12301.pbf", "./mappa/tiles/15/17683/12302.pbf", "./mappa/tiles/15/17683/12303.pbf", "./mappa/tiles/15/17683/12304.pbf", "./mappa/tiles/15/17683/12305.pbf", "./mappa/tiles/15/17683/12306.pbf", "./mappa/tiles/15/17683/12307.pbf", "./caratteri/bodoni-latin-ext.woff2", "./caratteri/bodoni-latin.woff2", "./caratteri/caratteri.css", "./caratteri/jost-latin-ext.woff2", "./caratteri/jost-latin.woff2"];
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
