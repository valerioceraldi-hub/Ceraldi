// Prove della Guida generata (E2: nuova grafica + «In cammino»). Playwright, 390 px, orologio fissato.
// Uso: node tg.js <cartella-servita-da-http> <porta>   (la cartella contiene guida_out/ generata con --tutte-le-lingue --anteprima)
const { chromium } = require('playwright');
const BASE = 'http://127.0.0.1:' + (process.argv[3] || '8765') + '/guida_out/';
const MAR = '2026-11-03T09:00:00Z', CARITA = { latitude: 40.844326, longitude: 14.249114 }, GESU = { latitude: 40.847558, longitude: 14.251874 };
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const R = []; const ok = (n, c, x) => R.push((c ? 'OK   ' : 'FAIL ') + n + (c || x === undefined ? '' : '  → ' + x));
  async function apri(url, opz, fn) {
    opz = opz || {};
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, serviceWorkers: opz.sw ? 'allow' : 'block',
      geolocation: opz.pos, permissions: opz.pos ? ['geolocation'] : [] });
    const p = await ctx.newPage(); const err = [], esterne = [];
    p.on('pageerror', e => err.push(e.message)); p.on('console', m => m.type() === 'error' && err.push(m.text()));
    p.on('request', r => { if (!/^(http:\/\/127\.0\.0\.1|blob:|data:)/.test(r.url())) esterne.push(r.url()); });
    await p.clock.setFixedTime(new Date(opz.quando || MAR));
    await p.goto(url); await p.waitForTimeout(opz.attesa || 400);
    await fn(p, ctx);
    const nome = '[' + (url.replace(BASE, '') || 'home') + ']';
    ok(nome + ' nessun errore JS', err.length === 0, err.join(' | '));
    ok(nome + ' nessuna richiesta esterna', esterne.length === 0, esterne.slice(0, 3).join(' '));
    await ctx.close();
  }
  const testo = async (p, s) => (await p.locator(s).allTextContents()).join(' ');
  const largo = async p => p.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth);
  const linee = (p, id) => p.evaluate(id => { const m = window.MAPPE && window.MAPPE[id]; const s = m && m.getSource('percorso'); return s ? s._data.features.length : -1; }, id);

  // 1. Scegliere (martedì 03/11 ore 10: Sansevero chiusa)
  await apri(BASE, {}, async p => {
    ok('home: titolo', /Napoli a piedi/.test(await testo(p, 'h1')));
    ok('home: avviso anteprima', /Versione di prova/.test(await testo(p, '.avviso.prova')));
    ok('home: 3 schede itinerario con disegno del percorso (prima della mappa)', (await p.locator('article.scheda:not(.apertura)').count()) === 3 && (await p.locator('article.scheda svg polyline').count()) >= 16);
    await p.waitForFunction(() => document.querySelectorAll('.copertina-giro.pronta').length === 3, null, {timeout: 30000}).catch(() => {});
    ok('home: copertine con la mappa vera, il percorso e le foto delle tappe', (await p.locator('.copertina-giro.pronta img.fondo[src^="data:image/jpeg"]').count()) === 3 && (await p.locator('.copertina-giro .pin img').count()) >= 6 && (await p.locator('.copertina-giro .pin').count()) >= 18);
    ok('home: «Vedrai…»', /Vedrai:.*Gesù Nuovo/.test(await testo(p, 'article.scheda')));
    ok('home: storia di Napoli in apertura', (await p.locator('article.apertura a[href="#/r/storia-di-napoli"]').count()) >= 1);
    ok('home: altri 6 racconti', (await p.locator('a.voce[href^="#/r/"]').count()) === 6);
    ok('home: «Chiusi oggi» Sansevero', /Cappella Sansevero/.test(await testo(p, 'section.oggi')));
    ok('home: nessuna colonna riservata', !/note_interne|aggiornato_da|risposte/.test(await p.content()));
    ok('home: 390 px', await largo(p));
    await p.click('button[data-filtro="ora"]');
    ok('filtro «Un\'ora»: nessun giro e messaggio chiaro', /non c'è ancora un giro/.test(await testo(p, '.avviso.info')));
    await p.click('button[data-filtro="piove"]');
    ok('filtro «Piove»: luoghi al coperto', (await p.locator('a.voce[href^="#/l/"]').count()) >= 3);
  });
  // 2. Capire (itinerario) + mappa, percorso, «tu sei qui», indicazioni
  await apri(BASE + '#/i/il-primo-giro', { pos: CARITA, attesa: 2500 }, async p => {
    ok('itinerario: 7 voci nella linea del tempo', (await p.locator('ol.tl > li').count()) === 7);
    const sans = p.locator('ol.tl > li', { hasText: 'Cappella Sansevero' });
    ok('itinerario: Sansevero chiusa all\'arrivo', /Quando arrivi sarà chiuso/.test(await sans.textContent()));
    ok('itinerario: alternativa statua del Nilo', /Largo Corpo di Napoli/.test(await sans.textContent()));
    ok('itinerario: mappa disegnata', (await p.locator('#m-itin canvas.maplibregl-canvas').count()) === 1);
    ok('itinerario: 6 tratti sulle strade', (await linee(p, 'm-itin')) === 6);
    ok('itinerario: 6 segnaposto', (await p.locator('#m-itin .pin').count()) === 6);
    ok('itinerario: attribuzione OpenStreetMap', /OpenStreetMap/.test(await testo(p, '#m-itin .maplibregl-ctrl-attrib')));
    ok('itinerario: «Come arrivarci» in 6 tappe', (await p.locator('details.come').count()) === 6);
    const g = await p.locator('ol.tl > li', { hasText: 'Gesù Nuovo' }).first().locator('details.come li').allTextContents();
    ok('itinerario: Carità → Gesù Nuovo in 4 indicazioni', g.length === 4 && /Gira a destra · Via Maddaloni/.test(g.join('/')), g.join(' / '));
    ok('itinerario: «Portami qui» a piedi', /travelmode=walking|dirflg=w/.test(await p.locator('details.come a').first().getAttribute('href')));
    await p.click('button:has-text("Mostra dove sono")'); await p.waitForTimeout(2500);
    ok('itinerario: punto «tu sei qui»', (await p.locator('#m-itin .maplibregl-user-location-dot').count()) === 1);
    ok('itinerario: pulsante «Inizia il giro» fisso in basso', await p.locator('.fisso a:has-text("Inizia il giro")').isVisible());
    ok('itinerario: 390 px', await largo(p));
    await p.click('ol.tl a.riga:has-text("Santa Chiara")'); await p.waitForTimeout(500);
    ok('luogo: orari della settimana', (await p.locator('table.orari tr').count()) === 7);
    ok('luogo: verificato il 3 novembre 2026', /3 novembre 2026/.test(await testo(p, 'details.apri')));
    ok('luogo: aperto ora', /Aperto ora/.test(await testo(p, '.stack-s span')));
    await p.goto(BASE + '#/l/gesu-nuovo'); await p.waitForTimeout(400);
    ok('luogo senza orari verificati: «in verifica»', /Orari in verifica/.test(await testo(p, '.stack-s')));
    ok('luogo: «Perché è speciale» e «La storia»', /Perché è speciale/.test(await testo(p, 'h3')) && /La storia/.test(await testo(p, 'summary')));
    ok('luogo: «Ascolta la storia»', (await p.locator('button:has-text("Ascolta la storia")').count()) === 1);
    await p.goto(BASE + '#/r/san-gennaro'); await p.waitForTimeout(300);
    ok('racconto: testo', (await p.locator('.testo p').count()) >= 2);
  });
  // E3: «Cosa guardare», leggende, accessibilità, fonti
  await apri(BASE + '#/l/cappella-sansevero', {}, async p => {
    ok('E3: Sansevero 5 schede «Cosa guardare»', (await p.locator('article.guarda').count()) === 5, await p.locator('article.guarda').count());
    ok('E3: schede numerate con «dove trovarlo»', /Nella cavea sotterranea/.test(await testo(p, 'article.guarda .dove')));
    ok('E3: prima scheda «Il Cristo velato»', /Il Cristo velato/.test(await p.locator('article.guarda .tit b').first().textContent()));
    ok('E3: leggende', /Leggende e curiosità/.test(await testo(p, 'summary')));
    ok('E3: accessibilità (scala a chiocciola)', /scala a chiocciola/.test(await testo(p, 'details.apri')));
    ok('E3: fonti comprese quelle delle schede (≥ 7)', parseInt((await testo(p, 'details.fonti summary')).replace(/\D/g, '')) >= 7, await testo(p, 'details.fonti summary'));
    ok('E3: 390 px', await largo(p));
  });
  await apri(BASE + '#/l/santa-chiara', {}, async p => {
    ok('E3: Santa Chiara 4 schede + storia', (await p.locator('article.guarda').count()) === 4 && /La storia/.test(await testo(p, 'summary')));
  });
  await apri(BASE + 'en/#/l/cappella-sansevero', {}, async p => {
    ok('E3: inglese «What to look at» e schede tradotte', /What to look at/.test(await testo(p, 'h3')) && /Veiled Christ|veiled/i.test(await testo(p, 'article.guarda')), (await testo(p, 'article.guarda b')).slice(0, 80));
  });
  // 3. Camminare: indicazione, arrivo dal GPS, prosegui, ripresa, fuori percorso, «Sono già qui»
  await apri(BASE + '#/c/il-primo-giro', { pos: CARITA, attesa: 3000 }, async (p, ctx) => {
    ok('cammino: tratto 1 di 6', /Tratto 1 di 6/.test(await testo(p, '#c-tratto')));
    ok('cammino: prima svolta «Gira a destra · Via Maddaloni»', /Gira a destra · Via Maddaloni/.test(await testo(p, '#c-frase')), await testo(p, '#c-frase'));
    ok('cammino: distanza alla svolta', /Tra \d+ m/.test(await testo(p, '.manovra')));
    ok('cammino: punto blu sulla mappa', (await p.locator('#m-cammino .io').count()) === 1);
    ok('cammino: tratto attuale evidenziato', (await linee(p, 'm-cammino')) === 6);
    await ctx.setGeolocation({ latitude: 40.8462, longitude: 14.2493 }); await p.waitForTimeout(700);
    ok('cammino: avanzamento lungo il tratto', parseFloat(await p.evaluate(() => document.getElementById('c-barra').style.width)) > 2);
    await ctx.setGeolocation(GESU); await p.waitForTimeout(700); await ctx.setGeolocation({ latitude: 40.84756, longitude: 14.25188 }); await p.waitForTimeout(900);
    ok('cammino: arrivo riconosciuto dal GPS (Gesù Nuovo)', /Sei arrivato/.test(await testo(p, '.arrivo')) && /Gesù Nuovo/.test(await testo(p, '.arrivo h2')), await testo(p, '#c-pannello'));
    ok('cammino: «Apri la scheda» e «Ascolta la storia» all\'arrivo', (await p.locator('.arrivo a:has-text("Apri la scheda")').count()) === 1 && (await p.locator('.arrivo button:has-text("Ascolta la storia")').count()) === 1);
    await p.click('.arrivo button:has-text("Prosegui")'); await p.waitForTimeout(800);
    ok('cammino: prosegui → tratto 2 di 6 (Santa Chiara)', /Tratto 2 di 6/.test(await testo(p, '#c-tratto')) && /Santa Chiara/.test(await testo(p, '#c-pannello')));
    await p.reload(); await p.waitForTimeout(2500);
    ok('cammino: riaperta la pagina, il giro riprende dal tratto 2', /Tratto 2 di 6/.test(await testo(p, '#c-tratto')));
    await ctx.setGeolocation({ latitude: 40.8430, longitude: 14.2570 }); await p.waitForTimeout(900);
    ok('cammino: fuori percorso → avviso + «Portami qui»', /fuori dal percorso/.test(await testo(p, '#c-pannello')));
    await p.click('#c-qui'); await p.waitForTimeout(300);
    ok('cammino: «Sono già qui» → arrivo', /Sei arrivato/.test(await testo(p, '.arrivo')));
    ok('cammino: 390 px', await largo(p));
    await p.goto(BASE); await p.waitForTimeout(400);
    ok('home: «Riprendi il giro» dopo l\'uscita dalla pagina', (await p.locator('a.btn:has-text("Riprendi il giro")').count()) === 1);
  });
  // ultimo tratto: «Bentornato da Ceraldi»
  await apri(BASE + '#/c/il-primo-giro', { pos: CARITA, attesa: 2500 }, async p => {
    await p.evaluate(() => { G.k = 6; G.arrivato = true; aggiornaCammino(); });
    ok('cammino: fine giro «Bentornato da Ceraldi» + «Torna al menu»', /Bentornato da Ceraldi/.test(await testo(p, '.arrivo')) && (await p.locator('.arrivo a:has-text("Torna al menu")').count()) === 1);
  });
  // senza permesso di posizione: il giro funziona comunque
  await apri(BASE + '#/c/il-primo-giro', { attesa: 2500 }, async p => {
    ok('cammino senza posizione: messaggio chiaro', /Attiva la posizione|Cerco la tua posizione/.test(await testo(p, '#c-pannello')));
    await p.click('#c-qui'); await p.waitForTimeout(300);
    ok('cammino senza posizione: «Sono già qui» funziona', /Sei arrivato/.test(await testo(p, '.arrivo')));
  });
  // altri giorni e scadenza della verifica
  await apri(BASE + '#/i/il-primo-giro', { quando: '2026-11-04T09:00:00Z' }, async p => {
    const sans = await p.locator('ol.tl > li', { hasText: 'Cappella Sansevero' }).textContent();
    ok('mercoledì: Sansevero aperta, nessuna alternativa', /Aperto ora/.test(sans) && !/Quando arrivi/.test(sans), sans);
  });
  await apri(BASE + '#/l/cappella-sansevero', { quando: '2026-12-10T09:00:00Z' }, async p => {
    ok('verifica scaduta: «in verifica» e nessuna tabella', /Orari in verifica/.test(await testo(p, '.stack-s')) && (await p.locator('table.orari').count()) === 0);
  });
  // lingue
  await apri(BASE + 'en/#/c/il-primo-giro', { pos: CARITA, attesa: 2500 }, async p => {
    ok('inglese: «Turn right · Via Maddaloni»', /Turn right · Via Maddaloni/.test(await testo(p, '#c-frase')));
    ok('inglese: «Leg 1 of 6»', /Leg 1 of 6/.test(await testo(p, '#c-tratto')));
  });
  await apri(BASE + 'en/', {}, async p => {
    ok('inglese: titolo home', /Naples on foot/.test(await testo(p, 'h1')));
    ok('inglese: nome itinerario corretto a mano', /Your first walk/.test(await p.content()));
    await p.click('.lingue summary'); await p.click('a[data-lng="de"]'); await p.waitForURL(/\/de\//);
    ok('cambio lingua → de', /Neapel zu Fuß/.test(await testo(p, 'h1')));
    await p.goto(BASE); await p.waitForURL(/\/de\//, { timeout: 3000 }).catch(() => {});
    ok('lingua ricordata (torna in de)', /\/de\/$/.test(p.url()), p.url());
  });
  // senza rete
  await apri(BASE, { sw: true }, async (p, ctx) => {
    await p.evaluate(() => navigator.serviceWorker.ready); await p.waitForFunction(() => document.querySelectorAll('.copertina-giro.pronta').length === 3, null, {timeout: 30000}).catch(() => {}); await p.waitForTimeout(1500);
    await ctx.setOffline(true); await p.reload(); await p.waitForTimeout(600);
    ok('senza rete: la guida si apre', /Napoli a piedi/.test(await testo(p, 'h1')));
    ok('senza rete: caratteri del menu caricati', await p.evaluate(() => document.fonts.check('16px Jost')));
    await p.goto(BASE + '#/i/il-primo-giro'); await p.waitForTimeout(2200);
    ok('senza rete: mappa con percorso', (await p.locator('#m-itin canvas.maplibregl-canvas').count()) === 1 && (await linee(p, 'm-itin')) === 6);
    await ctx.setOffline(false);
  });

  await b.close();
  console.log(R.join('\n')); const f = R.filter(r => r.startsWith('FAIL')).length;
  console.log('\n' + (R.length - f) + '/' + R.length + ' superate'); process.exit(f ? 1 : 0);
})();
