// Prove del Passaporto del centro storico (G5). Uso: node tp.js <cartella-con-export.json> <porta>
// Parte dall'export dei dati reali, attiva il Passaporto con dati finti, rigenera in una cartella di prova e prova il telefono.
const { chromium } = require('playwright'); const { execFileSync } = require('child_process'); const fs = require('fs'); const path = require('path'); const crypto = require('crypto');
const DIR = process.argv[2], PORTA = process.argv[3] || '8765', BASE = 'http://127.0.0.1:' + PORTA + '/guida_pass/';
const src = JSON.parse(fs.readFileSync(path.join(DIR, 'export.json')));
const norm = s => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]/g, '');
const hash = s => crypto.createHash('sha256').update(norm(s)).digest('hex');
const it = src.guida_itinerari.find(i => i.slug === 'napoli-sacra'), tp = src.guida_tappe.filter(t => t.itinerario_id === it.id).sort((a, b) => a.ordine - b.ordine);
const t1 = tp[1], l1 = src.guida_luoghi.find(l => l.id === t1.luogo_id);
t1.domanda = 'Di che secolo è la chiesa?';
src.guida_passaporto = [{ id: 1, attivo: true, titolo: 'Passaporto di prova', testo: 'Rispondi e timbra.', premio_titolo: 'Un caffè', premio_testo: 'Mostralo al banco.', minimo: 1 }];
src.passaporto_dati = { minimo: 1, domande: [{ t: t1.id, l: t1.luogo_id, i: t1.itinerario_id, h: [hash('Zibaldone'), hash('zib')] }] };
fs.writeFileSync(path.join(DIR, 'export_pass.json'), JSON.stringify(src));
fs.rmSync(path.join(DIR, 'guida_pass'), { recursive: true, force: true }); fs.cpSync(path.join(DIR, 'guida_out'), path.join(DIR, 'guida_pass'), { recursive: true });
execFileSync('python3', [path.resolve(__dirname, '../guida_genera.py'), '--json', path.join(DIR, 'export_pass.json'), '--out', path.join(DIR, 'guida_pass'), '--tutte-le-lingue', '--anteprima', '--noindex'], { stdio: 'pipe' });
const html = fs.readFileSync(path.join(DIR, 'guida_pass/index.html'), 'utf8');
const R = []; const ok = (n, c, x) => R.push((c ? 'OK   ' : 'FAIL ') + n + (c || x === undefined ? '' : '  → ' + x));
ok('pagina: nessuna risposta in chiaro (solo impronte)', !/Zibaldone/.test(html) && html.includes(hash('Zibaldone')));
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, serviceWorkers: 'block' }); const p = await ctx.newPage(); const err = [];
  p.on('pageerror', e => err.push(e.message)); p.on('console', m => m.type() === 'error' && !/404/.test(m.text()) && err.push(m.text()));
  await p.clock.setFixedTime(new Date('2026-11-03T09:00:00Z'));
  await p.goto(BASE); await p.waitForTimeout(400);
  ok('home: scheda Passaporto con 0 timbri', /Passaporto di prova/.test(await p.locator('#app').innerText()) && /0 di 1 timbri/.test(await p.locator('#app').innerText()));
  await p.goto(BASE + '#/p'); await p.waitForTimeout(300);
  let t = await p.locator('#app').innerText();
  ok('passaporto: elenco luoghi con cerchietto e «mancano timbri»', t.includes('○ ' + l1.nome) && /Mancano 1 timbri/.test(t) && !/Un caffè/.test(t));
  // arrivo alla tappa dal «giro in corso»
  await p.evaluate(({ s, k }) => { localStorage.setItem('guida_giro', JSON.stringify({ s, k, t: Date.now() })); }, { s: it.slug, k: 1 });
  await p.goto(BASE + '#/c/' + it.slug); await p.waitForTimeout(800);
  await p.evaluate(() => { G.arrivato = true; aggiornaCammino(); }); await p.waitForTimeout(200);
  ok('arrivo: domanda mostrata', /Di che secolo è la chiesa/.test(await p.locator('#c-pannello').innerText()));
  await p.fill('#pas-r', 'sbagliata'); await p.click('#c-pannello button:has-text("Timbra")'); await p.waitForTimeout(300);
  ok('risposta sbagliata: messaggio e nessun timbro', /Non è questa/.test(await p.locator('#pas-m').innerText()) && !(await p.evaluate(() => localStorage.getItem('guida_passaporto'))));
  await p.fill('#pas-r', '  ZIBALDONE! '); await p.click('#c-pannello button:has-text("Timbra")'); await p.waitForTimeout(300);
  ok('risposta giusta (maiuscole e punteggiatura ignorate): timbro', /Timbro ottenuto/.test(await p.locator('#c-pannello').innerText()) && (await p.evaluate(() => localStorage.getItem('guida_passaporto'))).includes('"' + t1.luogo_id + '":1'));
  await p.goto(BASE + '#/p'); await p.waitForTimeout(300); t = await p.locator('#app').innerText();
  ok('passaporto: timbro segnato e premio mostrato', t.includes('✓ ' + l1.nome) && /1 di 1 timbri/.test(t) && /Un caffè/.test(t) && /Mostralo al banco/.test(t));
  const sc = await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1); ok('nessuno scorrimento orizzontale (390)', sc);
  await p.goto('http://127.0.0.1:' + PORTA + '/guida_pass/en/#/p'); await p.waitForTimeout(300);
  ok('inglese: testi fissi tradotti', /1 of 1 stamps/.test(await p.locator('#app').innerText()));
  // senza Passaporto attivo non compare nulla
  const sp = JSON.parse(JSON.stringify(src)); sp.guida_passaporto = []; fs.writeFileSync(path.join(DIR, 'export_nopass.json'), JSON.stringify(sp));
  execFileSync('python3', [path.resolve(__dirname, '../guida_genera.py'), '--json', path.join(DIR, 'export_nopass.json'), '--out', path.join(DIR, 'guida_pass'), '--tutte-le-lingue', '--anteprima', '--noindex'], { stdio: 'pipe' });
  await p.goto(BASE); await p.waitForTimeout(400); ok('Passaporto spento: nessuna traccia nella home', !/Passaporto/.test(await p.locator('#app').innerText()));
  ok('nessun errore JS', err.length === 0, err.join(' | '));
  console.log(R.join('\n')); console.log(R.filter(x => x.startsWith('OK')).length + '/' + R.length + ' superate'); await b.close();
})();
