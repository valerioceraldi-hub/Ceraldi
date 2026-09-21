/* ══════════════════════════════════════════════════════════════════
   Service worker delle app Ceraldi — 20/09/2026
   Serve SOLO alle notifiche push: non mette niente in cache, così
   l'app aggiornata su GitHub arriva sempre fresca senza sorprese.
   Vive nella cartella del sito, quindi vale per tutte e quattro le app.
   ══════════════════════════════════════════════════════════════════ */
self.addEventListener('install', function (e) { self.skipWaiting(); });
self.addEventListener('activate', function (e) { e.waitUntil(self.clients.claim()); });

self.addEventListener('push', function (e) {
  var d = {};
  try { d = e.data ? e.data.json() : {}; } catch (err) { d = { titolo: 'Ceraldi', testo: e.data ? e.data.text() : '' }; }
  var titolo = d.titolo || 'Ceraldi';
  var app = d.app || 'fatture';
  e.waitUntil(self.registration.showNotification(titolo, {
    body: d.testo || '',
    icon: 'icon-' + app + '-192.png',
    badge: 'icon-' + app + '-192.png',
    tag: d.tag || ('ceraldi-' + app + '-' + (d.id || Date.now())),
    renotify: false,
    data: { link: d.link || '', app: app, id: d.id || null }
  }));
});

self.addEventListener('notificationclick', function (e) {
  e.notification.close();
  var dati = e.notification.data || {};
  var pagina = dati.link || ({
    fatture: 'Primanota.html', presenze: 'ceraldi_presenze.html',
    ordini: 'ceraldi_ordini.html', richieste: 'ceraldi_richieste.html'
  }[dati.app] || './');
  e.waitUntil(self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function (lista) {
    for (var i = 0; i < lista.length; i++) {
      if (lista[i].url.indexOf(pagina.split('/').pop().split('#')[0]) >= 0 && 'focus' in lista[i]) return lista[i].focus();
    }
    return self.clients.openWindow(pagina);
  }));
});
