// Prove della Guida generata (Playwright, 390 px). Uso: node tg.js <cartella-servita-da-http> <porta>
// La cartella deve contenere guida_out/ generata con guida_genera.py --tutte-le-lingue --anteprima.
const { chromium } = require('playwright');
const BASE = 'http://127.0.0.1:' + (process.argv[3] || '8765') + '/guida_out/';
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const R = []; const ok = (n, c, x) => R.push((c ? 'OK   ' : 'FAIL ') + n + (c || x === undefined ? '' : '  → ' + x));
  async function apri(url, quando, fn, opz) {
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, serviceWorkers: (opz && opz.sw) ? 'allow' : 'block' });
    const p = await ctx.newPage(); const err = [], esterne = [];
    p.on('pageerror', e => err.push(e.message));
    p.on('console', m => m.type() === 'error' && err.push(m.text()));
    p.on('request', r => { if (!/^(http:\/\/127\.0\.0\.1|blob:|data:)/.test(r.url())) esterne.push(r.url()); });
    if (quando) await p.clock.setFixedTime(new Date(quando));
    await p.goto(url); await p.waitForTimeout(300);
    await fn(p, ctx);
    ok('[' + url.replace(BASE, '') + '] nessun errore JS', err.length === 0, err.join(' | '));
    ok('[' + url.replace(BASE, '') + '] nessuna richiesta esterna', esterne.length === 0, esterne.slice(0, 3).join(' '));
    await ctx.close();
  }
  const testo = async (p, s) => (await p.locator(s).allTextContents()).join(' ');
  const largo = async p => p.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth);

  // martedi' 03/11/2026 ore 10:00 a Napoli (09:00 UTC): Sansevero chiuso il martedi'
  await apri(BASE, '2026-11-03T09:00:00Z', async p => {
    ok('titolo', (await testo(p, '#t-titolo')) === 'Guida di Napoli');
    ok('avviso anteprima', /Versione di prova/.test(await testo(p, '.avviso.prova')));
    ok('2 itinerari', (await p.locator('a.voce[href^="#/i/"]').count()) === 2);
    ok('5 racconti', (await p.locator('a.voce[href^="#/r/"]').count()) === 5);
    ok('chiusi oggi: Sansevero', /Cappella Sansevero/.test(await testo(p, 'section.scheda')), await testo(p, 'section.scheda'));
    ok('nessuna colonna riservata nella pagina', !/note_interne|aggiornato_da|risposte/.test(await p.content()));
    ok('390 px senza scorrimento orizzontale', await largo(p));
    await p.click('a[href="#/i/il-primo-giro"]'); await p.waitForTimeout(1500);
    ok('itinerario: 7 tappe (partenza e ritorno da Ceraldi)', (await p.locator('.tappa').count()) === 7);
    const sans = p.locator('.tappa', { hasText: 'Cappella Sansevero' });
    ok('Sansevero: chiuso all\'arrivo', /Quando arrivi sarà chiuso/.test(await sans.textContent()));
    ok('Sansevero: alternativa statua del Nilo', /Largo Corpo di Napoli/.test(await sans.textContent()));
    ok('mappa disegnata (MapLibre)', (await p.locator('#m-itin canvas.maplibregl-canvas').count()) === 1);
    ok('mappa: segnaposto delle tappe', (await p.locator('#m-itin .num').count()) === 6, await p.locator('#m-itin .num').count());
    ok('mappa: attribuzione OpenStreetMap', /OpenStreetMap/.test(await testo(p, '#m-itin .maplibregl-ctrl-attrib')));
    ok('itinerario 390 px', await largo(p));
    await p.click('.tappa >> text=Santa Chiara'); await p.waitForTimeout(400);
    ok('scheda luogo: orari della settimana', (await p.locator('table.orari tr').count()) === 7);
    ok('scheda luogo: verificato il', /Orari verificati il 3 novembre 2026/.test(await testo(p, 'section.scheda')));
    ok('scheda luogo: oggi aperto (10:00)', /Aperto ora/.test(await testo(p, 'section.scheda')));
    await p.goto(BASE + '#/l/gesu-nuovo'); await p.waitForTimeout(300);
    ok('luogo senza orari verificati: «in verifica»', /Orari in verifica/.test(await testo(p, 'section.scheda')));
    await p.goto(BASE + '#/piove'); await p.waitForTimeout(300);
    ok('«Piove?»: luoghi al coperto', (await p.locator('a.voce').count()) >= 3);
    await p.goto(BASE + '#/r/san-gennaro'); await p.waitForTimeout(300);
    ok('racconto: testo', (await p.locator('.testo p').count()) >= 2);
  });

  // E1: percorso sulle strade, indicazioni, «tu sei qui», «Portami qui»
  async function apriPos(url, pos, fn) {
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, serviceWorkers: 'block', geolocation: pos, permissions: ['geolocation'] });
    const p = await ctx.newPage(); const err = []; p.on('pageerror', e => err.push(e.message));
    await p.clock.setFixedTime(new Date('2026-11-03T09:00:00Z')); await p.goto(url); await p.waitForTimeout(2500);
    await fn(p); ok('[E1 ' + url.replace(BASE, '') + '] nessun errore JS', err.length === 0, err.join(' | ')); await ctx.close();
  }
  await apriPos(BASE + '#/i/il-primo-giro', { latitude: 40.8466, longitude: 14.2501 }, async p => {
    const linee = await p.evaluate(() => { const m = window.MAPPE && window.MAPPE['m-itin']; const s = m && m.getSource('percorso'); return s ? s._data.features.length : -1; });
    ok('E1: 6 tratti del percorso disegnati sulle strade', linee === 6, linee);
    ok('E1: livello «percorso» sulla mappa', await p.evaluate(() => !!window.MAPPE['m-itin'].getLayer('percorso')));
    ok('E1: «Come arrivarci» in 6 tappe', (await p.locator('.tappa details').count()) === 6, await p.locator('.tappa details').count());
    const gesu = await p.locator('.tappa', { hasText: 'Gesù Nuovo' }).first().locator('details li').allTextContents();
    ok('E1: Carità → Gesù Nuovo in 4 indicazioni (8 svolte grezze)', gesu.length === 4, gesu.join(' / '));
    ok('E1: «Gira a destra · Via Maddaloni»', gesu.some(x => /Gira a destra · Via Maddaloni/.test(x)), gesu.join(' / '));
    ok('E1: «Portami qui a piedi» (mappe del telefono, a piedi)', /travelmode=walking|dirflg=w/.test(await p.locator('.tappa details a').first().getAttribute('href')));
    await p.click('button:has-text("Mostra dove sono")'); await p.waitForTimeout(2500);
    ok('E1: punto «tu sei qui»', (await p.locator('#m-itin .maplibregl-user-location-dot').count()) === 1);
    ok('E1: nessun avviso di posizione', await p.locator('#m-itin-msg').isHidden());
    ok('E1: 390 px', await largo(p));
  });
  await apriPos(BASE + '#/mappa', { latitude: 41.9028, longitude: 12.4964 }, async p => {
    await p.click('button:has-text("Mostra dove sono")'); await p.waitForTimeout(2500);
    ok('E1: a Roma → «fuori dalla zona della mappa»', /fuori dalla zona/.test(await p.locator('#m-tutti-msg').textContent()));
  });
  await apriPos(BASE + 'en/#/i/il-primo-giro', { latitude: 40.8466, longitude: 14.2501 }, async p => {
    const t = (await p.locator('.tappa details li').allTextContents()).join(' / ');
    ok('E1: inglese «Turn right · Via Maddaloni»', /Turn right · Via Maddaloni/.test(t), t.slice(0, 120));
    ok('E1: inglese nome itinerario corretto a mano', /Your first walk/.test(await p.content()));
  });

  // mercoledi' 04/11/2026 ore 10:00: Sansevero aperto, niente alternativa
  await apri(BASE + '#/i/il-primo-giro', '2026-11-04T09:00:00Z', async p => {
    const sans = p.locator('.tappa', { hasText: 'Cappella Sansevero' });
    ok('mercoledì: Sansevero aperto all\'arrivo', /Aperto ora/.test(await sans.textContent()) && !/Quando arrivi/.test(await sans.textContent()), await sans.textContent());
  });
  // 10/12/2026: verifica degli orari scaduta (oltre 30 giorni) -> mai un orario non verificato presentato come certo
  await apri(BASE + '#/l/cappella-sansevero', '2026-12-10T09:00:00Z', async p => {
    ok('verifica scaduta: «in verifica»', /Orari in verifica/.test(await testo(p, 'section.scheda')));
    ok('verifica scaduta: nessuna tabella orari', (await p.locator('table.orari').count()) === 0);
  });
  // lingue: inglese tradotto; la scelta si ricorda (stessa chiave del menu)
  await apri(BASE + 'en/', '2026-11-03T09:00:00Z', async p => {
    ok('inglese: titolo', (await testo(p, '#t-titolo')) === 'Naples Guide');
    ok('inglese: nome luogo protetto', /San Biagio dei Librai|Sansevero/.test(await p.content()));
    await p.click('.lingue summary'); await p.click('a[data-lng="de"]'); await p.waitForURL(/\/de\//);
    ok('cambio lingua → de', /Neapel-Führer/.test(await testo(p, '#t-titolo')));
    await p.goto(BASE); await p.waitForURL(/\/de\//, { timeout: 3000 }).catch(() => {});
    ok('lingua ricordata (torna in de)', /\/de\/$/.test(p.url()), p.url());
  });
  // senza rete: dopo la prima apertura la guida e la mappa restano disponibili
  await apri(BASE, '2026-11-03T09:00:00Z', async (p, ctx) => {
    await p.evaluate(() => navigator.serviceWorker.ready); await p.waitForTimeout(2500);
    await ctx.setOffline(true);
    await p.reload(); await p.waitForTimeout(500);
    ok('senza rete: la pagina si apre', /Guida di Napoli/.test(await testo(p, '#t-titolo')));
    await p.goto(BASE + '#/i/il-primo-giro'); await p.waitForTimeout(2000);
    ok('senza rete: mappa disegnata', (await p.locator('#m-itin canvas.maplibregl-canvas').count()) === 1);
    await ctx.setOffline(false);
  }, { sw: true });

  await b.close();
  console.log(R.join('\n')); const f = R.filter(r => r.startsWith('FAIL')).length;
  console.log('\n' + (R.length - f) + '/' + R.length + ' superate'); process.exit(f ? 1 : 0);
})();
