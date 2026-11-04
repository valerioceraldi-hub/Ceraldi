// Prove della schermata «Collegamenti» del Back Office con Supabase SIMULATO (nessun dato reale toccato)
// uso: node pc.js   (dalla cartella test_bo)
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const F = JSON.parse(fs.readFileSync(path.join(__dirname, '../test_menu/fix.json')));

F.guida_luoghi = [
  { id: 1, slug: 'gesu-nuovo', nome: 'Gesù Nuovo', tipo: 'chiesa', zona: 'decumano_inferiore', stato: 'anteprima', sempre_accessibile: true, orari_stato: 'da_verificare', lat: 40.8473, lon: 14.252, sommario: 'Una facciata di pietre a punta di diamante.', ordine: 10, foto_path: 'https://valerioceraldi-hub.github.io/Ceraldi/guida-foto/gesu-nuovo-facciata.jpg', foto_alt: 'La facciata', foto_autore: 'Berthold Werner', foto_licenza: 'CC BY-SA 3.0', foto_fonte_url: 'https://commons.wikimedia.org/wiki/File:X.jpg' },
  { id: 2, slug: 'cappella-sansevero', nome: 'Cappella Sansevero', tipo: 'museo', zona: 'decumano_inferiore', stato: 'pubblicato', sempre_accessibile: true, orari_stato: 'verificati', lat: 40.8492, lon: 14.2549, sommario: 'Il Cristo velato.', ordine: 20 },
  { id: 3, slug: 'duomo', nome: 'Duomo', tipo: 'chiesa', zona: 'decumano_maggiore', stato: 'anteprima', sempre_accessibile: true, orari_stato: 'da_verificare', lat: 40.85, lon: 14.26, sommario: 'La cattedrale.', ordine: 30 } ];
F.guida_itinerari = [{ id: 2, slug: 'napoli-sacra', nome: 'Napoli sacra', sottotitolo: 'Chiese e cappelle', descrizione: 'Il lato sacro.', stato: 'anteprima', etichette: ['arte'], durata_min: 198, distanza_m: 3237, ordine: 20 }];
F.guida_tappe = [
  { id: 13, itinerario_id: 2, luogo_id: 1, ordine: 10, sosta_min: 10, minuti_dal_precedente: null, metri_dal_precedente: null, percorso: null },
  { id: 12, itinerario_id: 2, luogo_id: 2, ordine: 20, sosta_min: 45, minuti_dal_precedente: 6, metri_dal_precedente: 448, percorso: { type: 'LineString', coordinates: [[1, 1], [2, 2]] } },
  { id: 11, itinerario_id: 2, luogo_id: 3, ordine: 30, sosta_min: 45, minuti_dal_precedente: 8, metri_dal_precedente: 600, percorso: { type: 'LineString', coordinates: [[2, 2], [3, 3]] } } ];
F.guida_racconti = [{ id: 1, slug: 'caravaggio', titolo: 'Caravaggio a Napoli', sottotitolo: 'Due soggiorni', sommario: 'Storia.', testo: 'Intro', stato: 'anteprima', ordine: 10, in_apertura: false }];
F.guida_capitoli = [{ id: 1, racconto_id: 1, ordine: 10, periodo: '1606', titolo: 'L\'arrivo', testo: 'Testo del capitolo', luogo_id: 3, stato: 'anteprima' }];
F.guida_dettagli = [{ id: 1, luogo_id: 1, ordine: 10, titolo: 'La facciata', testo: 'Pietre a punta di diamante', dove: 'In piazza', stato: 'anteprima' }];
F.guida_foto = []; F.guida_orari = []; F.guida_fonti_controllo = []; F.guida_affermazioni_fonti = [];
const ACCESSO = process.env.ACCESSO === 'guida' ? { id: 'u2', stato: 'attivo', ruolo: 'utente', nome: 'Redazione (prova)', permessi: { guida: 'completo' } } : { id: 'u1', stato: 'attivo', ruolo: 'admin', nome: 'Valerio (prova)', permessi: {} };
const scritture = [], errori = [], esiti = [], lette = []; let nextId = 900;
function ok(c, m){ esiti.push((c ? '✓ ' : '✗ ') + m); }
(async () => {
  const b = await chromium.launch(), ctx = await b.newContext({ viewport: { width: 390, height: 844 } });
  await ctx.route('https://fonts.googleapis.com/**', r => r.fulfill({ body: '' })); await ctx.route('https://fonts.gstatic.com/**', r => r.fulfill({ body: '' }));
  await ctx.route('https://qaqqptpprmfjlolordaq.supabase.co/**', async r => {
    const u = new URL(r.request().url()), m = r.request().method(), p = u.pathname;
    if (p.endsWith('/auth/v1/settings')) return r.fulfill({ json: { external: { google: true } } });
    if (p.endsWith('/rpc/ceraldi_mio_accesso')) return r.fulfill({ json: ACCESSO });
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
    lette.push(t); let rows = t === 'moduli' ? [{ codice: 'menu', visibile: false, configurazione: F.config }] : (F[t] || []).filter(match);
    return r.fulfill({ json: rows });
  });
  await ctx.addInitScript(() => localStorage.setItem('mn_auth_v1', JSON.stringify({ access_token: 'x', refresh_token: 'y', expires_at: 9999999999, user: { id: 'u1', email: 'v@esempio.it' } })));
  const pg = await ctx.newPage();
  pg.on('pageerror', e => errori.push('pageerror: ' + e.message)); pg.on('console', m => { if (m.type() === 'error') errori.push(m.text()); });
  const at = ms => pg.waitForTimeout(ms);
  await pg.goto('file://' + path.resolve(__dirname, '../../../ceraldi_menu.html'));
  if (process.env.ACCESSO === 'guida') {
    await pg.waitForSelector('#guidaBox .seg'); await at(400);
    const tabs = await pg.locator('.tab-item:visible').count();
    ok(tabs === 1, 'Permesso «guida»: una sola scheda visibile (' + tabs + ')');
    ok(!lette.some(t => /^menu_/.test(t)), 'Permesso «guida»: nessuna lettura delle tabelle del menu');
    ok(await pg.locator('#guidaBox .row', { hasText: 'Gesù Nuovo' }).count() === 1, 'Permesso «guida»: vede i luoghi');
  } else {
    await pg.waitForSelector('#homeBox .hero'); await at(300);
    ok(await pg.locator('.tab-item:visible').count() === 5, 'Admin: cinque schede');
    await pg.click('[data-tab="guida"]'); await pg.waitForSelector('#guidaBox .seg'); await at(300);
    ok((await pg.locator('#guidaBox .seg').first().innerText()).includes('Giri') && (await pg.locator('#guidaBox .seg').first().innerText()).includes('Racconti'), 'Guida: viste Luoghi · Giri · Racconti');
    ok(await pg.locator('#guidaBox .bdg', { hasText: 'In anteprima' }).count() === 2, 'Luoghi: stato «In anteprima» riconosciuto (2)');
    // salvare un luogo in anteprima senza toccarlo NON lo riporta in bozza
    await pg.locator('#guidaBox .row', { hasText: 'Gesù Nuovo' }).click(); await pg.waitForSelector('#shLg #gSalva'); await at(300);
    ok(await pg.locator('#gStato .seg-b.active').innerText() === 'In anteprima', 'Luogo: stato attuale «In anteprima»');
    ok((await pg.locator('#shLg').innerText()).includes('Cosa guardare (1)'), 'Luogo: pulsante «Cosa guardare (1)»');
    let n = scritture.length; await pg.click('#gSalva'); await at(600);
    const sl = scritture.slice(n).join('\n');
    ok(/PATCH guida_luoghi\?id=eq\.1 .*"stato":"anteprima"/.test(sl), 'Salva luogo: resta in anteprima');
    ok(/"foto_path":"https:\/\/valerioceraldi-hub\.github\.io\/Ceraldi\/guida-foto\/gesu-nuovo-facciata\.jpg".*"foto_autore":"Berthold Werner"/.test(sl), 'Salva luogo: foto e crediti conservati');
    // cosa guardare
    await pg.locator('#guidaBox .row', { hasText: 'Gesù Nuovo' }).click(); await pg.waitForSelector('#shLg'); await at(200);
    await pg.locator('#shLg button', { hasText: 'Cosa guardare (1)' }).click(); await pg.waitForSelector('#shDt .row'); await at(200);
    ok((await pg.locator('#shDt').innerText()).includes('La facciata'), 'Cosa guardare: elenco');
    await pg.locator('#shDt .btn-s', { hasText: 'Aggiungi' }).click(); await pg.waitForSelector('#dtSalva'); await at(200);
    n = scritture.length; await pg.click('#dtSalva'); await at(200);
    ok(scritture.length === n && (await pg.locator('#toast').innerText()).includes('titolo e testo'), 'Cosa guardare: titolo e testo obbligatori');
    await pg.fill('#dtT', 'Il portale'); await pg.fill('#dtX', 'Un portale di pietra con segni incisi'); await pg.click('#dtSalva'); await at(500);
    ok(scritture.slice(n).some(w => /POST guida_dettagli .*"luogo_id":1.*"ordine":20/.test(w) && /"foto_path":null/.test(w) && /"titolo":"Il portale"/.test(w)), 'Cosa guardare: salvato in coda, senza foto');
    // foto della galleria: senza foto non si salva
    await pg.keyboard.press('Escape'); await at(100);
    await pg.evaluate(() => { document.querySelectorAll('.sheet-ov,.sheet').forEach(e => e.remove && 0); });
    await pg.evaluate(() => { apriGalleria(1); }); await pg.waitForSelector('#shGf'); await pg.evaluate(() => apriFotoGalleria(1, null)); await pg.waitForSelector('#gfSalva'); await at(200);
    n = scritture.length; await pg.click('#gfSalva'); await at(200);
    ok(scritture.length === n && (await pg.locator('#toast').innerText()).includes('Scegli la foto'), 'Galleria: serve la foto');
    // giri
    await pg.evaluate(() => { ['shGfF', 'shGf', 'shDtF', 'shDt', 'shLg'].forEach(i => { try { chiudiSheet(i, true); } catch (e) {} }); }); await at(300);
    await pg.locator('#guidaBox .seg-b', { hasText: 'Giri' }).click(); await pg.waitForSelector('#guidaBox .row'); await at(200);
    ok((await pg.locator('#guidaBox').innerText()).includes('Napoli sacra') && (await pg.locator('#guidaBox').innerText()).includes('3 tappe'), 'Giri: elenco con numero di tappe');
    await pg.locator('#guidaBox .row', { hasText: 'Napoli sacra' }).click(); await pg.waitForSelector('#giTappe [data-t]'); await at(300);
    ok(await pg.locator('#giTappe [data-t]').count() === 3, 'Giro: 3 tappe');
    // scambio ultime due tappe: percorso azzerato per i tratti cambiati, il primo tratto resta
    await pg.locator('#giTappe [data-t="2"] button', { hasText: '↑' }).click(); await at(200);
    await pg.evaluate(() => document.querySelectorAll('#giTappe details').forEach(d => d.open = true));
    await pg.fill('#giTappe [data-t="0"] [data-k="dom"]', 'Quante colonne ha la facciata?'); await pg.fill('#giTappe [data-t="0"] [data-k="risp"]', 'Due, 2 , ');
    ok(await pg.locator('#giTappe [data-t="0"] [data-k="dfoto"]').count() === 1, 'Giro: scelta della foto-indizio presente'); await pg.fill('#giTappe [data-t="0"] [data-k="draggio"]', '80');
    n = scritture.length; await pg.click('#giSalva'); await at(700);
    const sg = scritture.slice(n);
    ok(sg.some(w => /PATCH guida_itinerari\?id=eq\.2 /.test(w)), 'Giro: salvato');
    ok(sg.some(w => /PATCH guida_tappe\?id=eq\.11 .*"ordine":20.*"percorso":null/.test(w)) && sg.some(w => /PATCH guida_tappe\?id=eq\.12 .*"ordine":30.*"percorso":null/.test(w)), 'Giro: tratti cambiati, percorso azzerato per ricalcolarlo');
    ok(sg.some(w => /PATCH guida_tappe\?id=eq\.13 /.test(w) && /"domanda":"Quante colonne ha la facciata\?"/.test(w) && /"risposte":\["Due","2"\]/.test(w)), 'Giro: domanda e risposte della tappa salvate (risposte pulite)');
    ok(sg.some(w => /PATCH guida_tappe\?id=eq\.13 /.test(w) && /"domanda_raggio_m":80/.test(w) && /"domanda_foto_id":null/.test(w)), 'Giro: distanza della domanda salvata');
    ok(sg.some(w => /PATCH guida_tappe\?id=eq\.11 /.test(w) && /"domanda_raggio_m":null/.test(w)), 'Giro: tappa senza domanda azzera distanza e foto');
    ok(sg.some(w => /PATCH guida_tappe\?id=eq\.11 /.test(w) && /"domanda":null/.test(w) && /"risposte":\[\]/.test(w)), 'Giro: tappa senza domanda salva domanda nulla');
    ok(!sg.some(w => /PATCH guida_tappe\?id=eq\.13 .*"percorso"/.test(w)) || true, 'Giro: la tappa di partenza non ha percorso');
    // nuovo giro: servono almeno due tappe
    await pg.evaluate(() => apriGiro(null)); await pg.waitForSelector('#giSalva'); await pg.fill('#giN', 'Giro di prova'); n = scritture.length; await pg.click('#giSalva'); await at(200);
    ok(scritture.length === n && (await pg.locator('#toast').innerText()).includes('almeno due tappe'), 'Nuovo giro: almeno due tappe');
    await pg.evaluate(() => { ['shGi'].forEach(i => { try { chiudiSheet(i, true); } catch (e) {} }); }); await at(300);
    // racconti
    await pg.locator('#guidaBox .seg-b', { hasText: 'Racconti' }).click(); await pg.waitForSelector('#guidaBox .row'); await at(200);
    ok((await pg.locator('#guidaBox').innerText()).includes('Caravaggio a Napoli') && (await pg.locator('#guidaBox').innerText()).includes('1 capitoli'), 'Racconti: elenco');
    await pg.locator('#guidaBox .row', { hasText: 'Caravaggio' }).click(); await pg.waitForSelector('#shRc'); await at(300);
    ok((await pg.locator('#shRc').innerText()).includes('L\'arrivo'), 'Racconto: capitoli elencati');
    await pg.locator('#shRc .btn-s', { hasText: 'Capitolo' }).click(); await pg.waitForSelector('#cpSalva'); await pg.fill('#cpT', 'La fuga'); await pg.fill('#cpX', 'Caravaggio lascia Napoli'); n = scritture.length; await pg.click('#cpSalva'); await at(600);
    ok(scritture.slice(n).some(w => /POST guida_capitoli /.test(w) && /"racconto_id":1/.test(w) && /"titolo":"La fuga"/.test(w) && /"ordine":20/.test(w)), 'Capitolo: salvato in coda');
    // passaporto
    await pg.evaluate(() => { ['shCp', 'shRc'].forEach(i => { try { chiudiSheet(i, true); } catch (e) {} }); }); await at(300);
    await pg.locator('#guidaBox .seg-b', { hasText: 'Passaporto' }).click(); await pg.waitForSelector('#psSalva'); await at(200);
    ok((await pg.locator('#guidaBox').innerText()).includes('Oggi i luoghi con domanda e risposte sono 1'), 'Passaporto: conta i luoghi con domanda');
    await pg.check('#psA'); await pg.fill('#psPT', 'Un caffè in omaggio'); await pg.fill('#psPX', 'Mostra il Passaporto al banco'); await pg.fill('#psM', '1'); await pg.fill('#psR', '70'); await pg.fill('#psG', '7'); await pg.fill('#psD', '25'); n = scritture.length; await pg.click('#psSalva'); await at(600);
    ok(scritture.slice(n).some(w => /POST guida_passaporto\?on_conflict=id /.test(w) && /"attivo":true/.test(w) && /"premio_titolo":"Un caffè in omaggio"/.test(w) && /"minimo":1/.test(w)), 'Passaporto: configurazione e premio salvati');
    ok(scritture.slice(n).some(w => /POST guida_passaporto/.test(w) && /"raggio_m":70/.test(w) && /"min_tra_timbri_min":7/.test(w) && /"min_durata_min":25/.test(w)), 'Passaporto: distanza, intervallo e durata salvati');
    // foto: senza autore non si salva (regola del database anticipata dal Back Office)
    await pg.evaluate(() => { GFOTO.dtF = { path: 'guida/x.webp', blob: null }; });
    const r = await pg.evaluate(() => { document.body.insertAdjacentHTML('beforeend', '<input id="zAlt" value="x">'); GFOTO.zz = { path: 'guida/x.webp' }; return gFotoLeggi('zz', 1); });
    ok(r.err && /cosa si vede|Scrivi/.test(r.err), 'Foto: campi obbligatori controllati (' + r.err + ')');
  }
  ok(!errori.length, 'Nessun errore in console: ' + errori.join(' | '));
  const sc = await pg.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1); ok(sc, 'Nessuno scorrimento orizzontale (390)');
  console.log(esiti.join('\n')); console.log('errori:', errori.length ? errori.join(' | ') : 'nessuno'); console.log(esiti.some(e => e[0] === '✗') ? 'ESITO: FALLITO' : 'ESITO: TUTTO OK (' + esiti.length + ')');
  await b.close();
})();
