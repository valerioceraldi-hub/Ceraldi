// Prove della schermata «Collegamenti» del Back Office con Supabase SIMULATO (nessun dato reale toccato)
// uso: node pc.js   (dalla cartella test_bo)
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const F = JSON.parse(fs.readFileSync(path.join(__dirname, '../test_menu/fix.json')));
F.contenuti_collegamenti = [
  { id: 1, da_tabella: 'menu_voci', da_id: 3, a_tipo: 'url', a_id: null, url: 'https://www.ceraldicaffe.it/storie/tiramisu/', url_en: null, titolo: 'La storia del tiramisù', testo: null, posizione: null, ordine: 10, attivo: true },
  { id: 2, da_tabella: 'guida_itinerari', da_id: 1, a_tipo: 'menu_voce', a_id: 1, url: null, url_en: null, titolo: null, testo: 'Prima di partire', posizione: 'inizio', ordine: 10, attivo: true },
  { id: 3, da_tabella: 'menu_voci', da_id: 4, a_tipo: 'guida_luogo', a_id: 2, url: null, url_en: null, titolo: null, testo: null, posizione: null, ordine: 20, attivo: false } ];
F.guida_luoghi = [{ id: 1, nome: 'Gesù Nuovo', stato: 'pubblicato' }, { id: 2, nome: 'Santa Chiara', stato: 'bozza' }];
F.guida_racconti = [{ id: 1, titolo: 'La storia di Napoli', stato: 'pubblicato' }];
F.guida_itinerari = [{ id: 1, nome: 'Il primo giro', stato: 'pubblicato' }];
const scritture = [], errori = [], esiti = []; let nextId = 900;
function ok(c, m){ esiti.push((c ? '✓ ' : '✗ ') + m); }
(async () => {
  const b = await chromium.launch(), ctx = await b.newContext({ viewport: { width: 390, height: 844 } });
  await ctx.route('https://fonts.googleapis.com/**', r => r.fulfill({ body: '' })); await ctx.route('https://fonts.gstatic.com/**', r => r.fulfill({ body: '' }));
  await ctx.route('https://qaqqptpprmfjlolordaq.supabase.co/**', async r => {
    const u = new URL(r.request().url()), m = r.request().method(), p = u.pathname;
    if (p.endsWith('/auth/v1/settings')) return r.fulfill({ json: { external: { google: true } } });
    if (p.endsWith('/rpc/ceraldi_mio_accesso')) return r.fulfill({ json: { id: 'u1', stato: 'attivo', ruolo: 'admin', nome: 'Valerio (prova)', permessi: {} } });
    if (p.endsWith('/app_errori')) return r.fulfill({ status: 201, body: '' });
    const t = p.split('/rest/v1/')[1], q = Object.fromEntries(u.searchParams);
    const filtri = Object.entries(q).filter(([k]) => !['select', 'order', 'limit', 'offset'].includes(k));
    const match = row => filtri.every(([k, v]) => v.startsWith('eq.') ? String(row[k]) === v.slice(3) : true);
    if (m !== 'GET') {
      const body = r.request().postData() ? JSON.parse(r.request().postData()) : null;
      scritture.push(m + ' ' + t + (u.search ? decodeURIComponent(u.search) : '') + ' ' + JSON.stringify(body));
      const rows = F[t] = F[t] || [];
      if (m === 'PATCH') rows.filter(match).forEach(x => Object.assign(x, body));
      if (m === 'DELETE') F[t] = rows.filter(x => !match(x));
      if (m === 'POST') rows.push(Object.assign({ id: nextId++ }, body));
      return r.fulfill({ status: 204, body: '' });
    }
    let rows = t === 'moduli' ? [{ codice: 'menu', visibile: false, configurazione: F.config }] : (F[t] || []).filter(match);
    return r.fulfill({ json: rows });
  });
  await ctx.addInitScript(() => localStorage.setItem('mn_auth_v1', JSON.stringify({ access_token: 'x', refresh_token: 'y', expires_at: 9999999999, user: { id: 'u1', email: 'v@esempio.it' } })));
  const pg = await ctx.newPage();
  pg.on('pageerror', e => errori.push('pageerror: ' + e.message)); pg.on('console', m => { if (m.type() === 'error') errori.push(m.text()); });
  const at = ms => pg.waitForTimeout(ms);
  await pg.goto('file://' + path.resolve(__dirname, '../../../ceraldi_menu.html'));
  await pg.waitForSelector('#homeBox .hero'); await at(400);
  await pg.click('[data-tab="altro"]'); await at(300);
  ok(await pg.locator('#altroBox .row', { hasText: 'Collegamenti' }).count() === 1, 'Altro: c\'è la voce «Collegamenti»');
  ok((await pg.locator('#altroBox .row', { hasText: 'Collegamenti' }).innerText()).includes('3 tra menu'), 'Altro: conta i collegamenti (3)');
  await pg.locator('#altroBox .row', { hasText: 'Collegamenti' }).click(); await pg.waitForSelector('#clLista .row'); await at(300);
  ok(await pg.locator('#clLista .row').count() === 3, 'Elenco: 3 collegamenti');
  ok(await pg.locator('#clLista .sec-title', { hasText: 'Giri della guida' }).count() === 1, 'Elenco: raggruppato per origine');
  const el = await pg.locator('#clLista').innerText();
  ok(el.includes('Tiramisù') && el.includes('La storia del tiramisù') && el.includes('Spaghetti'), 'Elenco: origine e destinazione con i nomi');
  ok(el.includes('prima di partire'), 'Elenco: posizione nel giro');
  ok(el.includes('la destinazione non è pubblicata'), 'Elenco: avviso se la destinazione è in bozza');
  ok(await pg.locator('#clLista .bdg', { hasText: 'Nascosto' }).count() === 1, 'Elenco: segno «Nascosto»');
  await pg.fill('#clQ', 'spaghetti'); await at(200); ok(await pg.locator('#clLista .row').count() === 1, 'Ricerca: trova per nome');
  await pg.fill('#clQ', ''); await at(200);
  // nuovo: prodotto -> pagina del sito
  await pg.locator('#shCl .btn-p').click(); await pg.waitForSelector('#shClF'); await at(200);
  let n = scritture.length; await pg.click('#clSalva'); await at(200);
  ok(scritture.length === n && (await pg.locator('#toast').innerText()).includes('da dove parte'), 'Blocco: serve scegliere l\'origine');
  await pg.locator('#clDaPick button').click(); await pg.waitForSelector('#scQ'); await pg.fill('#scQ', 'penne'); await at(200);
  await pg.locator('#scLista .row').first().click(); await at(200);
  ok((await pg.locator('#clDaPick').innerText()).includes('Penne'), 'Origine scelta: Penne');
  await pg.fill('#clUrl', 'http://sito.it'); await pg.fill('#clTit', 'Titolo'); n = scritture.length; await pg.click('#clSalva'); await at(200);
  ok(scritture.length === n && (await pg.locator('#toast').innerText()).includes('https://'), 'Blocco: indirizzo senza https');
  await pg.fill('#clUrl', 'https://www.ceraldicaffe.it/storie/pasta/'); await pg.fill('#clTit', ''); await pg.click('#clSalva'); await at(200);
  ok(scritture.length === n && (await pg.locator('#toast').innerText()).includes('titolo'), 'Blocco: titolo obbligatorio per le pagine del sito');
  await pg.fill('#clTit', 'La storia della pasta'); await pg.fill('#clTesto', 'Un po\' di storia'); await pg.click('#clSalva'); await at(500);
  const s1 = scritture.slice(n).join('\n');
  ok(/POST contenuti_collegamenti .*"da_tabella":"menu_voci","da_id":2,"a_tipo":"url".*"url":"https:\/\/www.ceraldicaffe.it\/storie\/pasta\/".*"titolo":"La storia della pasta"/.test(s1) && /"a_id":null/.test(s1) && /"ordine":30/.test(s1), 'Salvato: prodotto → pagina del sito (ordine in coda)');
  ok(await pg.locator('#clLista .row').count() === 4, 'Elenco aggiornato (4)');
  // nuovo: giro -> prodotto (solo prodotti ammessi), posizione
  await pg.locator('#shCl .btn-p').click(); await at(200);
  await pg.selectOption('#clDa', 'guida_itinerari'); await at(200);
  ok(await pg.locator('#clAt option').count() === 1 && (await pg.locator('#clAt').innerText()).includes('prodotto'), 'Giro: come destinazione solo un prodotto');
  ok(await pg.locator('#clPosBox').isVisible(), 'Giro: compare «Dove, nel giro»');
  await pg.locator('#clDaPick button').click(); await pg.locator('#scLista .row').first().click(); await at(150);
  await pg.locator('#clAPick button').click(); await pg.fill('#scQ', 'spaghetti'); await at(150); await pg.locator('#scLista .row').first().click(); await at(150);
  await pg.selectOption('#clPos', 'inizio'); n = scritture.length; await pg.click('#clSalva'); await at(400);
  ok((await pg.locator('#toast').innerText()).includes('esiste già') && scritture.length === n, 'Blocco: collegamento doppio');
  await pg.selectOption('#clPos', 'fine'); await pg.click('#clSalva'); await at(500);
  ok(/POST contenuti_collegamenti .*"da_tabella":"guida_itinerari".*"a_tipo":"menu_voce".*"posizione":"fine".*"a_id":1/.test(scritture.slice(n).join('\n')), 'Salvato: giro → prodotto, «al ritorno»');
  // modifica: spegni
  await pg.locator('#clLista .row', { hasText: 'Tiramisù' }).click(); await pg.waitForSelector('#clTit'); await at(200);
  ok(await pg.inputValue('#clTit') === 'La storia del tiramisù' && (await pg.inputValue('#clUrl')).includes('tiramisu'), 'Modifica: campi precompilati');
  await pg.locator('#clAtt + span').click(); n = scritture.length; await pg.click('#clSalva'); await at(500);
  ok(/PATCH contenuti_collegamenti\?id=eq\.1 .*"attivo":false/.test(scritture.slice(n).join('\n')), 'Modifica: collegamento nascosto');
  // cambio origine → destinazioni valide si adattano
  await pg.locator('#clLista .row', { hasText: 'Tiramisù' }).click(); await pg.waitForSelector('#clTit'); await pg.selectOption('#clDa', 'guida_luoghi'); await at(200);
  ok((await pg.locator('#clAt option').allInnerTexts()).join('|').includes('prodotto') && !(await pg.locator('#clAt option').allInnerTexts()).join('|').includes('racconto'), 'Luogo della guida: destinazioni = sito o prodotto');
  await pg.click('#shClF [data-x]').catch(() => {}); await at(200);
  // elimina
  await pg.locator('#clLista .row', { hasText: 'Santa Chiara' }).click(); await pg.waitForSelector('#clTit', { state: 'attached' }); await at(200);
  await pg.locator('#shClF .btn-d').click(); await at(300); n = scritture.length; await pg.locator('.mo [data-si]').last().click(); await at(500);
  ok(/DELETE contenuti_collegamenti\?id=eq\.3/.test(scritture.slice(n).join('\n')), 'Elimina: con conferma');
  const w = await pg.evaluate(() => document.documentElement.scrollWidth); ok(w <= 390, 'Nessuno scorrimento orizzontale (' + w + ')');
  await pg.screenshot({ path: path.join(__dirname, 'collegamenti.png') });
  console.log(esiti.join('\n'));
  const e = errori.filter(x => !/favicon|Failed to load resource/.test(x)); console.log('errori:', e.length ? e : 'nessuno');
  console.log(esiti.filter(x => x[0] === '✗').length ? 'ESITO: CI SONO ERRORI' : 'ESITO: TUTTO OK (' + esiti.length + ')');
  await b.close();
})().catch(e => { console.log(esiti.join('\n')); console.error('INTERROTTO:', e.message); process.exit(1); });
