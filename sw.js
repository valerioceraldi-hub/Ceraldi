/* ══════════════════════════════════════════════════════════════════
   Service worker delle app Ceraldi — 20/09/2026 (aggiornato 05/10/2026)
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
  // 05/10/2026: prima, con l'app già aperta, la notifica la portava solo in
  // primo piano e il collegamento (es. #richieste) andava perso: si restava
  // sulla prima pagina. Ora il collegamento viene passato all'app aperta,
  // che apre la sezione giusta. Se l'app non risponde (versione vecchia),
  // per Presenze si ricarica direttamente sul collegamento.
  e.waitUntil(self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function (lista) {
    var file = pagina.split('/').pop().split('#')[0].split('?')[0];
    for (var i = 0; i < lista.length; i++) {
      var c = lista[i];
      if (file && c.url.indexOf(file) >= 0 && 'focus' in c) {
        return c.focus().then(function (cl) {
          cl = cl || c;
          if (!dati.link) return cl;
          return avvisaApp(cl, dati.link).then(function (ok) {
            if (!ok && dati.app === 'presenze' && 'navigate' in cl) return cl.navigate(dati.link).catch(function () {});
            return cl;
          });
        }).catch(function () { return self.clients.openWindow(pagina); });
      }
    }
    return self.clients.openWindow(pagina);
  }));
});

// Manda il collegamento all'app aperta e aspetta (al massimo 1,5 s) che
// risponda "ricevuto". Le app che non lo gestiscono semplicemente non
// rispondono: per loro non cambia nulla.
function avvisaApp(client, link) {
  return new Promise(function (ok) {
    var fatto = false;
    try {
      var canale = new MessageChannel();
      canale.port1.onmessage = function () { if (!fatto) { fatto = true; ok(true); } };
      client.postMessage({ tipo: 'ceraldi-notifica', link: link }, [canale.port2]);
    } catch (err) { ok(false); return; }
    setTimeout(function () { if (!fatto) { fatto = true; ok(false); } }, 1500);
  });
}
