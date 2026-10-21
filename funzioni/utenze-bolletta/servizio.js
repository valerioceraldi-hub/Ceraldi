// ══════════════════════════════════════════════════════════════════════
// UTENZE-BOLLETTA — logica del servizio (21/10/2026)
// Il punto d'ingresso sul server (index.ts) importa questo file da un commit
// fissato del repo e gli passa le librerie: così il codice che gira è sempre
// quello pubblicato qui, versionato e leggibile da chiunque controlli.
// Azioni: leggi · salva · scan_xml · pdf_url (vedi index.ts)
// ══════════════════════════════════════════════════════════════════════
import { leggiBolletta, imparaEtichetta, ETICHETTE, ESSENZIALI, VERSIONE_LETTORE } from './parsers.js';

// Fornitori di utenze già conosciuti (P.IVA): le loro fatture elettroniche
// vengono controllate per cercare il PDF della bolletta allegato.
export const PIVA_UTENZE = ['15844561009', '06655971007', '07679350632', '12300020158'];

export function crea({ createClient, extractText, getDocumentProxy, URL_SB, SERVICE, ANON }) {
const CORS = { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type, x-sistema-secret, x-utenze-token', 'Access-Control-Allow-Methods': 'POST, OPTIONS' };
const json = (b, s = 200) => new Response(JSON.stringify(b), { status: s, headers: { ...CORS, 'Content-Type': 'application/json' } });
const db = createClient(URL_SB, SERVICE);
const BUCKET = 'bollette';

function b64ToBytes(b64) { const s = atob(b64.replace(/^data:[^,]*,/, '').replace(/\s+/g, '')); const u = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) u[i] = s.charCodeAt(i); return u; }
async function sha(bytes) { const h = await crypto.subtle.digest('SHA-256', bytes); return Array.from(new Uint8Array(h)).map(b => b.toString(16).padStart(2, '0')).join('').slice(0, 32); }
async function testoPdf(bytes) { const pdf = await getDocumentProxy(bytes); const { text } = await extractText(pdf, { mergePages: false }); return (text ).map((t, i) => '=== PAGINA ' + (i + 1) + ' ===\n' + t).join('\n'); }
// che forma ha il valore di un campo (serve per rileggerlo alla bolletta successiva)
const genereCampo = (k) => /^(data_|periodo_|scadenza_|offerta_scadenza|offerta_decorrenza)/.test(k) ? 'data' : (/^(numero_fattura|codice_)/.test(k) ? 'codice' : (/(_nome|_tipo|stato_|metodo_|tariffa|tipologia|contatore)/.test(k) ? 'testo' : 'numero'));
const cifre = (s) => String(s || '').replace(/\D/g, '');
const senzaZeri = (s) => cifre(s).replace(/^0+/, '');

async function autorizza(req) {
  // lo script Gmail (account della società) ha una chiave sua, valida SOLO per consegnare PDF
  const tok = req.headers.get('x-utenze-token');
  if (tok) { const { data } = await db.from('app_segreti').select('valore').eq('chiave', 'utenze_gmail_token').maybeSingle(); return (data && data.valore && tok === data.valore) ? { gmail: true } : null; }
  const seg = req.headers.get('x-sistema-secret');
  if (seg) { const { data } = await db.from('app_segreti').select('valore').eq('chiave', 'sistema_secret').maybeSingle(); if (data && data.valore && seg === data.valore) return { sistema: true }; return null; }
  const auth = req.headers.get('Authorization') || ''; if (!auth) return null;
  const asUser = createClient(URL_SB, ANON, { global: { headers: { Authorization: auth } } });
  const { data: { user } } = await asUser.auth.getUser(); if (!user) return null;
  const { data: puo } = await asUser.rpc('ceraldi_puo', { p_app: 'fatture', p_scrittura: true });
  return puo === true ? { utente: user.id } : null;
}

// Fattura elettronica corrispondente: stessa P.IVA del fornitore e stesso numero (senza zeri davanti)
async function trovaFattura(piva, numero, totale) {
  const n = senzaZeri(numero); if (!n) return null;
  const stesso = (f) => { const fn = senzaZeri(f.numero); return fn === n || (fn.length > n.length && fn.endsWith(n)); };
  if (piva) {
    const { data } = await db.from('fatture').select('id,numero,data,importo,stato,fornitore,piva').eq('piva', piva).is('deleted_at', null).order('data', { ascending: false }).limit(400);
    const c = (data || []).filter(stesso);
    if (c.length === 1) return c[0];
  }
  // fornitore nuovo (P.IVA non ancora nota): stesso numero E stesso totale al centesimo
  if (totale != null) {
    const { data } = await db.from('fatture').select('id,numero,data,importo,stato,fornitore,piva').is('deleted_at', null).ilike('numero', '%' + n.slice(-6) + '%').limit(50);
    const c = (data || []).filter((f) => stesso(f) && Math.abs(Math.abs(+f.importo || 0) - totale) < 0.01);
    if (c.length === 1) return c[0];
  }
  return null;
}

async function modelloPer(piva, testo) {
  // modello del fornitore indicato; altrimenti quello del fornitore di una fornitura il cui codice compare nel testo
  if (piva) { const { data } = await db.from('utenze_modelli').select('*').eq('fornitore_piva', piva).maybeSingle(); if (data) return data; }
  const { data: forn } = await db.from('utenze_forniture').select('codice,fornitore_piva');
  for (const f of forn || []) if (f.codice && testo.includes(f.codice) && f.fornitore_piva) { const { data } = await db.from('utenze_modelli').select('*').eq('fornitore_piva', f.fornitore_piva).maybeSingle(); if (data) return data; }
  // P.IVA di un modello che compare nel testo (fornitore già imparato)
  const { data: mod } = await db.from('utenze_modelli').select('*');
  for (const m of mod || []) if (m.fornitore_piva && testo.includes(m.fornitore_piva)) return m;
  return null;
}

async function analizza(bytes, opz = {}) {
  const testo = await testoPdf(bytes);
  if (testo.replace(/=== PAGINA \d+ ===|\s/g, '').length < 200) return { errore: 'Il PDF non contiene testo leggibile (forse è una scansione o una foto). Serve il PDF originale della bolletta.' };
  let mod = await modelloPer(null, testo);
  let r = leggiBolletta(testo, { modello: mod ? { lettore: mod.lettore, campi: mod.campi } : null });
  if (!r.riconosciuto.intestataCeraldi) return { errore: 'Questa bolletta non è intestata a Ceraldi Group (P.IVA 04523831214): non viene archiviata. Le bollette di casa restano fuori dall\'app.' };
  const d = r.dati;
  if (!mod && d.fornitore_piva) { mod = await modelloPer(d.fornitore_piva, testo); if (mod) r = leggiBolletta(testo, { modello: { lettore: mod.lettore, campi: mod.campi } }); }
  const dd = r.dati;
  let fornitura = null, cambioFornitore = false, giaPresente = null;
  if (dd.codice_fornitura) {
    const { data } = await db.from('utenze_forniture').select('*').eq('codice', dd.codice_fornitura).maybeSingle();
    fornitura = data;
    if (fornitura && dd.fornitore_piva && fornitura.fornitore_piva && fornitura.fornitore_piva !== dd.fornitore_piva) cambioFornitore = true;
    if (fornitura && dd.numero_fattura) { const { data: b } = await db.from('utenze_bollette').select('id,stato').eq('fornitura_id', fornitura.id).eq('numero', String(dd.numero_fattura)).maybeSingle(); giaPresente = b; }
  }
  const fattura = opz.fattura || await trovaFattura(dd.fornitore_piva, dd.numero_fattura, dd.totale);
  // la fattura elettronica dice con certezza chi è il fornitore
  if (fattura && fattura.piva && !r.campi.fornitore_piva?.certo) { dd.fornitore_piva = String(fattura.piva).replace(/\D/g, ''); r.campi.fornitore_piva = { valore: dd.fornitore_piva, riga: 'dalla fattura elettronica ' + fattura.numero, certo: true }; if (!dd.fornitore_nome) { dd.fornitore_nome = fattura.fornitore; r.campi.fornitore_nome = { valore: fattura.fornitore, riga: 'dalla fattura elettronica ' + fattura.numero, certo: true }; } }
  const nuovoFornitore = !mod && r.lettore === 'generico';
  return { testo, r, fornitura, cambioFornitore, giaPresente, fattura, nuovoFornitore, modello: mod };
}

function risposta(a, attesa) {
  const r = a.r;
  return {
    attesa, lettore: r.lettore, dati: r.dati, provenienza: Object.fromEntries(Object.entries(r.campi).map(([k, v]) => [k, { riga: v.riga, certo: v.certo }])),
    etichette: ETICHETTE, essenziali: ESSENZIALI, mancanti: r.mancanti, da_confermare: r.daConfermare, controlli: r.controlli,
    fornitura: a.fornitura, cambio_fornitore: a.cambioFornitore, gia_presente: a.giaPresente, fattura: a.fattura, nuovo_fornitore: a.nuovoFornitore
  };
}

async function archivia(attesa, dati, provenienza, controlli, fonte, fatturaId, stato) {
  const d = dati || {};
  if (!d.codice_fornitura || !d.numero_fattura || !d.tipo) throw new Error('Mancano codice fornitura, numero o tipo: non si può archiviare.');
  // fornitura: si crea alla prima bolletta; col cambio fornitore resta la stessa (il POD/PDR non cambia) e si aggiorna il fornitore
  const { data: f0 } = await db.from('utenze_forniture').select('*').eq('codice', d.codice_fornitura).maybeSingle();
  let forn = f0;
  if (!forn) { const { data, error } = await db.from('utenze_forniture').insert({ tipo: d.tipo, codice: d.codice_fornitura, fornitore_nome: d.fornitore_nome || null, fornitore_piva: d.fornitore_piva || null }).select().single(); if (error) throw error; forn = data; }
  else if (d.fornitore_piva && d.fornitore_piva !== forn.fornitore_piva) {
    // si aggiorna il fornitore attuale solo se questa bolletta è la più recente
    const { data: ult } = await db.from('utenze_bollette').select('data_emissione').eq('fornitura_id', forn.id).order('data_emissione', { ascending: false }).limit(1);
    if (!ult || !ult.length || !ult[0].data_emissione || (d.data_emissione && d.data_emissione >= ult[0].data_emissione)) await db.from('utenze_forniture').update({ fornitore_nome: d.fornitore_nome || null, fornitore_piva: d.fornitore_piva, aggiornato_il: new Date().toISOString() }).eq('id', forn.id);
  }
  let path = null;
  if (attesa) { path = 'forniture/' + forn.id + '/' + String(d.numero_fattura).replace(/[^\w.-]/g, '_') + '.pdf'; const { error } = await db.storage.from(BUCKET).move(attesa, path); if (error && !/exists/i.test(error.message)) { path = attesa; } }
  const riga = {
    fornitura_id: forn.id, fattura_id: fatturaId, fornitore_piva: d.fornitore_piva || null, fornitore_nome: d.fornitore_nome || null, numero: String(d.numero_fattura),
    data_emissione: d.data_emissione || null, periodo_dal: d.periodo_dal || null, periodo_al: d.periodo_al || null, scadenza_pagamento: d.scadenza_pagamento || null,
    totale: d.totale ?? null, consumo: d.consumo ?? null, unita: d.unita || null, dati: d, provenienza: provenienza || {}, controlli: controlli || [], fonte, pdf_path: path, stato,
    confermato_il: stato === 'confermata' ? new Date().toISOString() : null
  };
  const { data: b, error: e2 } = await db.from('utenze_bollette').upsert(riga, { onConflict: 'fornitura_id,numero' }).select().single();
  if (e2) throw e2;
  return { bolletta: b, fornitura: forn };
}

async function gestisci(req) {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: CORS });
  if (req.method !== 'POST') return json({ errore: 'Solo POST' }, 405);
  const chi = await autorizza(req);
  if (!chi) return json({ errore: 'Non autorizzato' }, 401);
  let body = {}; try { body = await req.json(); } catch { /* vuoto */ }
  if (chi.gmail && body.azione !== 'ricevi') return json({ errore: 'Non autorizzato' }, 401);
  try {
    if (body.azione === 'leggi') {
      let bytes, fattura = null;
      if (body.fattura_id) {
        const { data: f } = await db.from('fatture').select('id,numero,data,importo,stato,fornitore,piva,fattura_allegata').eq('id', body.fattura_id).maybeSingle();
        const m = String(f?.fattura_allegata || '').match(/<Attachment>([\s\S]*?)<\/Attachment>/);
        if (!m) return json({ errore: 'Questa fattura non ha un PDF allegato nell\'XML.' }, 400);
        bytes = b64ToBytes(m[1]); fattura = f ? { id: f.id, numero: f.numero, data: f.data, importo: f.importo, stato: f.stato, fornitore: f.fornitore, piva: f.piva } : null;
      } else if (body.pdf_base64) bytes = b64ToBytes(body.pdf_base64);
      else return json({ errore: 'Manca il PDF' }, 400);
      if (bytes.length > 15 * 1024 * 1024) return json({ errore: 'PDF troppo grande (max 15 MB)' }, 400);
      const a = await analizza(bytes, { fattura });
      if (a.errore) return json({ errore: a.errore }, 422);
      const attesa = 'in_attesa/' + (await sha(bytes)) + '.pdf';
      await db.storage.from(BUCKET).upload(attesa, bytes, { contentType: 'application/pdf', upsert: true });
      return json(risposta(a, attesa));
    }

    if (body.azione === 'salva') {
      const d = body.dati || {};
      // le correzioni («il valore giusto è scritto così nel PDF») insegnano il modello del fornitore
      if (body.attesa && body.correzioni && Object.keys(body.correzioni).length && d.fornitore_piva) {
        const { data: file } = await db.storage.from(BUCKET).download(body.attesa);
        if (file) {
          const testo = await testoPdf(new Uint8Array(await file.arrayBuffer()));
          const { data: m0 } = await db.from('utenze_modelli').select('*').eq('fornitore_piva', d.fornitore_piva).maybeSingle();
          const campi = Object.assign({}, m0?.campi || {});
          for (const [k, v] of Object.entries(body.correzioni )) {
            const imp = imparaEtichetta(testo, v.scritto); if (!imp) continue;
            campi[k] = { etichetta: imp.etichetta, dopo: imp.dopo, genere: genereCampo(k), esempio: imp.riga };
          }
          await db.from('utenze_modelli').upsert({ fornitore_piva: d.fornitore_piva, fornitore_nome: d.fornitore_nome || null, lettore: m0?.lettore || body.lettore || 'generico', campi, aggiornato_il: new Date().toISOString() });
        }
      } else if (d.fornitore_piva) {
        // anche senza correzioni il fornitore resta ricordato (alla prossima bolletta lo si riconosce)
        const { data: m0 } = await db.from('utenze_modelli').select('fornitore_piva').eq('fornitore_piva', d.fornitore_piva).maybeSingle();
        if (!m0) await db.from('utenze_modelli').insert({ fornitore_piva: d.fornitore_piva, fornitore_nome: d.fornitore_nome || null, lettore: body.lettore || 'generico' });
      }
      const out = await archivia(body.attesa || null, d, body.provenienza, body.controlli, body.fonte === 'gmail' ? 'gmail' : (body.fonte === 'xml' ? 'xml' : 'pdf'), body.fattura_id || null, 'confermata');
      if (body.arrivo_id) await db.from('utenze_in_arrivo').update({ esito: 'archiviata', bolletta_id: out.bolletta.id, attesa: null }).eq('id', body.arrivo_id);
      return json({ ok: true, ...out });
    }

    if (body.azione === 'scan_xml') {
      // Fatture elettroniche dei fornitori di utenze con il PDF della bolletta
      // dentro l'XML, non ancora lette. Poche per volta (il server ha un limite
      // di tempo per chiamata): l'app richiama finché «rimangono» è 0.
      const { data: mod } = await db.from('utenze_modelli').select('fornitore_piva');
      const piva = Array.from(new Set(PIVA_UTENZE.concat((mod || []).map((m) => m.fornitore_piva).filter(Boolean))));
      const { data: gia } = await db.from('utenze_bollette').select('fattura_id').not('fattura_id', 'is', null);
      const { data: saltate } = await db.from('utenze_xml_controllate').select('fattura_id,esito');
      const versione = 'v' + VERSIONE_LETTORE + ': ';
      const fatte = new Set((gia || []).map((x) => String(x.fattura_id)).concat((saltate || []).filter((x) => String(x.esito || '').startsWith(versione)).map((x) => String(x.fattura_id))));
      const { data: cand } = await db.from('fatture').select('id,numero,data,importo,stato,fornitore,piva').is('deleted_at', null).in('piva', piva).gte('data', body.dal || '2025-01-01').order('data', { ascending: false }).limit(500);
      const daFare = (cand || []).filter((f) => !fatte.has(String(f.id)));
      const esiti = [], senza = [];
      const max = Math.min(+body.quante || 2, 3);
      for (const f of daFare.slice(0, max)) {
        const { data: full } = await db.from('fatture').select('fattura_allegata').eq('id', f.id).single();
        const m = String(full?.fattura_allegata || '').match(/<FormatoAttachment>\s*PDF\s*<\/FormatoAttachment>[\s\S]*?<Attachment>([\s\S]*?)<\/Attachment>|<Attachment>([\s\S]{2000,}?)<\/Attachment>/i);
        const b64 = m ? (m[1] || m[2]) : null;
        if (!b64) { senza.push(String(f.id)); continue; }
        let a; try { a = await analizza(b64ToBytes(b64), { fattura: f }); } catch (e) { senza.push(String(f.id)); continue; }
        if (a.errore || !a.r || !a.r.dati.codice_fornitura || !a.r.dati.tipo) { senza.push(String(f.id)); continue; }
        if (a.giaPresente) { senza.push(String(f.id)); continue; } // già archiviata (magari confermata a mano): non si tocca
        const sicura = a.r.lettore !== 'generico' && !a.r.mancanti.length && a.r.controlli.every((c) => c.ok);
        const bytes = b64ToBytes(b64), attesa = 'in_attesa/' + (await sha(bytes)) + '.pdf';
        await db.storage.from(BUCKET).upload(attesa, bytes, { contentType: 'application/pdf', upsert: true });
        const prov = Object.fromEntries(Object.entries(a.r.campi).map(([k, v]) => [k, { riga: v.riga, certo: v.certo }]));
        const out = await archivia(attesa, a.r.dati, prov, a.r.controlli, 'xml', f.id, sicura ? 'confermata' : 'da_confermare');
        esiti.push({ fattura: f.numero, fornitore: f.fornitore, stato: out.bolletta.stato, bolletta_id: out.bolletta.id });
      }
      // le fatture senza PDF di bolletta si ricordano, per non riaprirle ogni volta
      if (senza.length) await db.from('utenze_xml_controllate').upsert(senza.map((id) => ({ fattura_id: +id, esito: versione + 'nessuna bolletta leggibile nell\'XML', controllata_il: new Date().toISOString() })), { onConflict: 'fattura_id' });
      return json({ ok: true, lette: esiti.length, esiti, rimangono: Math.max(0, daFare.length - max) });
    }

    if (body.azione === 'ricevi') {
      // Un PDF allegato a un'email arrivata nella casella della società.
      // Bolletta riconosciuta e con tutti i conti che tornano → archiviata;
      // altrimenti resta «da confermare» in app. Bollette non intestate a
      // Ceraldi Group: scartate senza conservare il file.
      const em = body.email || {}, nome = String(body.nome_file || 'allegato.pdf').slice(0, 200);
      const base = { origine: 'gmail', email_id: em.id || null, mittente: String(em.mittente || '').slice(0, 200), oggetto: String(em.oggetto || '').slice(0, 300), email_data: em.data || null, nome_file: nome };
      if (em.id) { const { data: g } = await db.from('utenze_in_arrivo').select('id,esito').eq('email_id', em.id).eq('nome_file', nome).maybeSingle(); if (g) return json({ ok: true, esito: 'già ricevuta', id: g.id }); }
      if (!body.pdf_base64) return json({ errore: 'Manca il PDF' }, 400);
      const bytes = b64ToBytes(body.pdf_base64);
      if (bytes.length > 15 * 1024 * 1024) return json({ errore: 'PDF troppo grande' }, 400);
      let a;
      try { a = await analizza(bytes); } catch (e) { await db.from('utenze_in_arrivo').insert({ ...base, esito: 'non letta', messaggio: 'PDF non leggibile: ' + String(e?.message || e).slice(0, 200) }); return json({ ok: true, esito: 'non letta' }); }
      if (a.errore) { await db.from('utenze_in_arrivo').insert({ ...base, esito: 'scartata', messaggio: a.errore }); return json({ ok: true, esito: 'scartata' }); }
      if (!a.r.dati.codice_fornitura && a.r.dati.consumo == null) { await db.from('utenze_in_arrivo').insert({ ...base, esito: 'scartata', messaggio: 'Il PDF non sembra una bolletta di luce, gas o acqua' }); return json({ ok: true, esito: 'scartata' }); }
      if (a.giaPresente) { await db.from('utenze_in_arrivo').insert({ ...base, esito: 'già presente', bolletta_id: a.giaPresente.id, messaggio: 'Bolletta già archiviata' }); return json({ ok: true, esito: 'già presente' }); }
      const attesa = 'in_attesa/' + (await sha(bytes)) + '.pdf';
      await db.storage.from(BUCKET).upload(attesa, bytes, { contentType: 'application/pdf', upsert: true });
      const ris = risposta(a, attesa);
      const sicura = a.r.lettore !== 'generico' && !a.r.mancanti.length && a.r.controlli.every((c) => c.ok);
      if (sicura) {
        const out = await archivia(attesa, a.r.dati, ris.provenienza, a.r.controlli, 'gmail', a.fattura ? a.fattura.id : null, 'confermata');
        await db.from('utenze_in_arrivo').insert({ ...base, esito: 'archiviata', bolletta_id: out.bolletta.id, messaggio: (a.cambioFornitore ? 'Cambio fornitore: ' : '') + (a.r.dati.fornitore_nome || '') + ' n° ' + a.r.dati.numero_fattura });
        return json({ ok: true, esito: 'archiviata', bolletta_id: out.bolletta.id });
      }
      await db.from('utenze_in_arrivo').insert({ ...base, attesa, esito: 'da confermare', risultato: ris, messaggio: a.nuovoFornitore ? 'Fornitore nuovo: alla prima bolletta conferma i dati, poi l\'app la riconosce da sola' : (a.r.mancanti.length ? 'Mancano: ' + a.r.mancanti.join(', ') : 'Un controllo sui totali non torna') });
      return json({ ok: true, esito: 'da confermare' });
    }

    if (body.azione === 'gmail_config') {
      // solo un utente (non il sistema): mostra la chiave da incollare nello script e salva l'indirizzo dello script
      if (!chi.utente) return json({ errore: 'Non autorizzato' }, 401);
      if (body.url_script) {
        if (!/^https:\/\/script\.google\.com\/macros\/s\/[\w-]+\/exec$/.test(String(body.url_script).trim())) return json({ errore: 'L\'indirizzo deve essere quello dell\'app web dello script: https://script.google.com/macros/s/…/exec' }, 400);
        await db.from('app_segreti').upsert({ chiave: 'utenze_gmail_script_url', valore: String(body.url_script).trim(), nota: 'app web dello script Gmail delle bollette', aggiornato_il: new Date().toISOString() }, { onConflict: 'chiave' });
      }
      const { data: t } = await db.from('app_segreti').select('valore').eq('chiave', 'utenze_gmail_token').maybeSingle();
      const { data: u } = await db.from('app_segreti').select('valore').eq('chiave', 'utenze_gmail_script_url').maybeSingle();
      return json({ chiave: t?.valore || null, url_script: u?.valore || null, url_app: URL_SB + '/functions/v1/utenze-bolletta' });
    }

    if (body.azione === 'gmail_avvia') {
      // «Leggi da Gmail» premuto in app: si chiede allo script della casella di controllare adesso
      const { data: u } = await db.from('app_segreti').select('valore').eq('chiave', 'utenze_gmail_script_url').maybeSingle();
      const { data: t } = await db.from('app_segreti').select('valore').eq('chiave', 'utenze_gmail_token').maybeSingle();
      if (!u || !u.valore) return json({ errore: 'Lo script Gmail non è ancora installato: segui le istruzioni in Utenze → Leggi da Gmail.' }, 400);
      const r = await fetch(u.valore + (u.valore.includes('?') ? '&' : '?') + 'chiave=' + encodeURIComponent(t?.valore || ''), { redirect: 'follow' });
      const testo = await r.text(); let esito; try { esito = JSON.parse(testo); } catch { esito = { errore: 'Risposta dello script non valida', dettaglio: testo.slice(0, 200) }; }
      return json(esito);
    }

    if (body.azione === 'pdf_url') {
      const { data: b } = await db.from('utenze_bollette').select('pdf_path').eq('id', body.bolletta_id).maybeSingle();
      if (!b || !b.pdf_path) return json({ errore: 'PDF non disponibile' }, 404);
      const { data, error } = await db.storage.from(BUCKET).createSignedUrl(b.pdf_path, 600);
      if (error) throw error;
      return json({ url: data.signedUrl });
    }

    return json({ errore: 'azione sconosciuta' }, 400);
  } catch (e) {
    console.error(e);
    return json({ errore: String(e?.message || e) }, 500);
  }
}

  return gestisci;
}
