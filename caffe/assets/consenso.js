/* Consenso cookie e Google Analytics 4 per il sito di Ceraldi Caffè.
   - Nessun cookie e nessuna chiamata a Google finché il visitatore non accetta.
   - "Rifiuta" e "Accetta" hanno lo stesso peso; la X chiude e vale come rifiuto.
   - La scelta vale 6 mesi, poi viene richiesta di nuovo; si può cambiare dal link "Preferenze cookie" nel piè di pagina.
   - Eventi misurati: clic su Chiama, Indicazioni, WhatsApp, Menu. */
(function () {
  var s = document.currentScript, ID = s && s.getAttribute('data-ga');
  if (!ID) return;
  var CHIAVE = 'ceraldi_consenso', DURATA = 182 * 24 * 3600 * 1000;
  var en = (document.documentElement.lang || 'it').indexOf('en') === 0;
  var T = en
    ? { testo: 'We use Google Analytics cookies only with your consent, to understand how the site is used. No advertising.', si: 'Accept', no: 'Reject', info: 'Privacy and cookies', chiudi: 'Close and reject' }
    : { testo: 'Usiamo i cookie di Google Analytics solo con il tuo consenso, per capire come viene usato il sito. Nessuna pubblicità.', si: 'Accetta', no: 'Rifiuta', info: 'Privacy e cookie', chiudi: 'Chiudi e rifiuta' };

  function leggi() {
    try { var v = JSON.parse(localStorage.getItem(CHIAVE)); if (v && Date.now() - v.t < DURATA) return v.s; } catch (e) {}
    return null;
  }
  function salva(scelta) { try { localStorage.setItem(CHIAVE, JSON.stringify({ s: scelta, t: Date.now() })); } catch (e) {} }

  var caricato = false;
  function caricaGA() {
    if (caricato) return; caricato = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { dataLayer.push(arguments); };
    gtag('js', new Date());
    gtag('config', ID, { anonymize_ip: true });
    var g = document.createElement('script'); g.async = true;
    g.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(ID);
    document.head.appendChild(g);
  }
  function rimuoviCookieGA() {
    document.cookie.split(';').forEach(function (c) {
      var n = c.split('=')[0].trim();
      if (n === '_ga' || n.indexOf('_ga_') === 0) {
        var d = location.hostname.split('.');
        for (var i = 0; i < d.length - 1; i++) document.cookie = n + '=; Max-Age=0; path=/; domain=.' + d.slice(i).join('.');
        document.cookie = n + '=; Max-Age=0; path=/';
      }
    });
  }

  function banner() {
    if (document.getElementById('consenso')) return;
    var privacy = (document.querySelector('a[href$="privacy/"]') || {}).href || '#';
    var b = document.createElement('div');
    b.id = 'consenso'; b.setAttribute('role', 'dialog'); b.setAttribute('aria-live', 'polite'); b.setAttribute('aria-label', T.info);
    b.innerHTML = '<button type="button" class="consenso-x" aria-label="' + T.chiudi + '">×</button>' +
      '<p>' + T.testo + ' <a href="' + privacy + '">' + T.info + '</a></p>' +
      '<div class="consenso-azioni"><button type="button" data-s="no">' + T.no + '</button><button type="button" data-s="si">' + T.si + '</button></div>';
    b.addEventListener('click', function (ev) {
      var t = ev.target.closest('button'); if (!t) return;
      var scelta = t.getAttribute('data-s') === 'si' ? 'si' : 'no';
      salva(scelta); b.remove();
      if (scelta === 'si') caricaGA(); else { rimuoviCookieGA(); if (caricato) location.reload(); }
    });
    document.body.appendChild(b);
  }

  // Eventi: solo se GA è stato caricato dopo il consenso
  document.addEventListener('click', function (ev) {
    var a = ev.target.closest && ev.target.closest('a'); if (!a) return;
    if (a.hasAttribute('data-preferenze-cookie')) { ev.preventDefault(); banner(); return; }
    if (!caricato) return;
    var h = a.getAttribute('href') || '', nome = null;
    if (h.indexOf('tel:') === 0) nome = 'clic_chiama';
    else if (h.indexOf('query_place_id') > -1) nome = 'clic_recensioni';
    else if (h.indexOf('maps.google') > -1 || h.indexOf('google.com/maps') > -1) nome = 'clic_indicazioni';
    else if (h.indexOf('wa.me') > -1) nome = 'clic_whatsapp';
    else if (/(^|\/)menu\/($|#)/.test(h) || h.indexOf('qromo.it') > -1) nome = 'clic_menu';
    else if (h.indexOf('query_place_id') > -1 || h.indexOf('writereview') > -1 || h.indexOf('tripadvisor') > -1) nome = 'clic_recensioni';
    if (nome) gtag('event', nome, { link_url: a.href, posizione: a.closest('.barra-fissa') ? 'barra_fissa' : (a.closest('footer') ? 'pie_di_pagina' : 'pagina') });
  });

  var v = leggi();
  if (v === 'si') caricaGA();
  else if (v === null) { if (document.body) banner(); else document.addEventListener('DOMContentLoaded', banner); }
})();
