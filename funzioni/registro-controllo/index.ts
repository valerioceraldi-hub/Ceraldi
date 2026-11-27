// @ts-nocheck
// ════════════════════════════════════════════════════════════════════════
// registro-controllo — CONTROLLO QUOTIDIANO DEL REGISTRO LEGALE (v79, 28/11/2026)
// ────────────────────────────────────────────────────────────────────────
// Ogni mattina (pg_cron) ricontrolla il sigillo della notte come farebbe un
// perito, senza fidarsi di nessun "ok" scritto in precedenza:
//  1. il sigillo di ieri esiste (se manca, prova a crearlo subito);
//  2. il manifesto salvato è quello sigillato (stessa impronta);
//  3. il manifesto è completo: numerazione continua, numero di eventi giusto,
//     attaccato al giorno prima;
//  4. il registro del database coincide evento per evento con il manifesto
//     e la catena delle impronte è integra (ricalcolata qui e dal database);
//  5. le ricevute FreeTSA e DigiCert sono firmate davvero dagli enti, risalgono
//     ai loro certificati radice ufficiali e riguardano proprio quel manifesto;
//     se una manca o non è valida si chiede subito una marca di recupero;
//  6. la prova Bitcoin (OpenTimestamps) viene completata, salvata in versione
//     definitiva e confrontata con il blocco su DUE archivi pubblici;
//  7. le ancore orarie delle ultime 24 ore sono riuscite.
// Ogni esito va in registro_controlli; l'esito definitivo di ogni giorno va
// anche nel registro legale (così il controllo stesso diventa una prova).
// AVVISA SOLO SE QUALCOSA NON VA (Telegram/push admin, come gli altri avvisi).
// Chi può chiamarla: pg_cron (x-sistema-secret) oppure un admin loggato.
// {"prova":true} = esegue tutti i controlli senza scrivere né avvisare.
// ════════════════════════════════════════════════════════════════════════
import * as asn1js from 'npm:asn1js@3.0.6';
import * as pkijs from 'npm:pkijs@3.2.5';
import { verificaMarca } from './tsa.js';
import { leggiOts, scriviOts, completaOts, verificaBitcoin, attestazioni, nuovaOts, ARCHIVI_BITCOIN } from './ots.js';
import { p384 } from 'npm:@noble/curves@1.9.7/p384';
import { p256 } from 'npm:@noble/curves@1.9.7/p256';
import { sha512, sha384 } from 'npm:@noble/hashes@1.8.0/sha512';
import { sha256 as nobleSha256 } from 'npm:@noble/hashes@1.8.0/sha256';

// noble = riserva per le firme ECDSA che il motore del server non implementa (vedi tsa.js)
const LIB = { pkijs, asn1js, crypto: globalThis.crypto, noble: { p384, p256, sha512, sha384, sha256: nobleSha256 } };

const SB_URL = Deno.env.get('SUPABASE_URL');
const SB_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
const H = { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}`, 'Content-Type': 'application/json' };
const BUCKET = 'registro-legale';
const TSA = [
  { nome: 'FreeTSA', url: 'https://freetsa.org/tsr' },
  { nome: 'DigiCert', url: 'http://timestamp.digicert.com' },
];
const PAGINA = 1000;
const ATTESA_BITCOIN_ORE = 72;      // oltre questo tempo una prova Bitcoin non completata è un'anomalia
const GIORNI_RICONTROLLO = 10;      // giorni recenti ricontrollati anche se mai controllati
const ATTESA_VERIFICA_ORE = 72;     // una verifica che resta "in attesa" oltre questo tempo diventa anomalia
const TEMPO_MAX_MS = 80000;         // oltre, i giorni rimasti si controllano alla chiamata successiva
const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type, x-sistema-secret',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
};

const hex = (b) => [...new Uint8Array(b)].map((x) => x.toString(16).padStart(2, '0')).join('');
const sha256 = async (d) => new Uint8Array(await crypto.subtle.digest('SHA-256', typeof d === 'string' ? new TextEncoder().encode(d) : d));
const fmtG = (g) => g.split('-').reverse().join('/');
const fmtOra = (iso) => new Date(iso).toLocaleString('it-IT', { timeZone: 'Europe/Rome', day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });

async function rest(path, init = {}) {
  const r = await fetch(`${SB_URL}/rest/v1/${path}`, { ...init, headers: { ...H, ...(init.headers || {}) } });
  const t = await r.text();
  if (!r.ok) throw new Error(`${path.split('?')[0]}: ${r.status} ${t.slice(0, 200)}`);
  return t ? JSON.parse(t) : null;
}
const rpc = (fn, body) => rest(`rpc/${fn}`, { method: 'POST', body: JSON.stringify(body) });
async function esportaTutto(dal, al) {
  const tutti = [];
  for (let da = 0; ; ) {
    const pag = await rest(`rpc/registro_esporta?order=anello.asc&limit=${PAGINA}&offset=${da}`,
      { method: 'POST', body: JSON.stringify({ p_dal: dal, p_al: al, p_dipendente: null }) });
    if (!pag || !pag.length) break;
    tutti.push(...pag); da += pag.length;
  }
  return tutti;
}
// Scarica un file del registro. Restituisce null SOLO se il file non esiste davvero;
// un errore temporaneo (rete, troppe richieste) si riprova e, se persiste, interrompe il
// controllo di quel giorno con "non verificabile ora" invece di un falso "file assente".
class NonVerificabile extends Error {}
const pausa = (ms) => new Promise((ok) => setTimeout(ok, ms));
async function scarica(percorso) {
  let ultimo = '';
  for (let t = 0; t < 4; t++) {
    if (t) await pausa(800 * t);
    try {
      const r = await fetch(`${SB_URL}/storage/v1/object/${BUCKET}/${percorso}`, { headers: { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}` }, signal: AbortSignal.timeout(20000) });
      if (r.ok) return new Uint8Array(await r.arrayBuffer());
      const testo = await r.text();
      if ((r.status === 400 || r.status === 404) && /not.?found|non.?trovat|does not exist/i.test(testo)) return null;
      ultimo = `HTTP ${r.status}`;
    } catch (e) { ultimo = String((e && e.message) || e).slice(0, 60); }
  }
  throw new NonVerificabile(`spazio file non raggiungibile (${ultimo})`);
}
async function carica(percorso, dati, tipo) {
  const r = await fetch(`${SB_URL}/storage/v1/object/${BUCKET}/${percorso}`, {
    method: 'POST', headers: { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}`, 'Content-Type': tipo, 'x-upsert': 'true' }, body: dati,
  });
  if (!r.ok) throw new Error(`salvataggio ${percorso}: ${r.status}`);
}
function giornoRoma(d) {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Rome', year: 'numeric', month: '2-digit', day: '2-digit' }).format(d);
}
const giornoPrima = (g) => giornoRoma(new Date(new Date(`${g}T12:00:00Z`).getTime() - 86400000));

// richiesta di marca RFC 3161 (identica al sigillo notturno)
function tsqDer(digest) {
  const nonce = crypto.getRandomValues(new Uint8Array(8)); nonce[0] &= 0x7f; if (nonce[0] === 0) nonce[0] = 1;
  const algo = [0x30, 0x0d, 0x06, 0x09, 0x60, 0x86, 0x48, 0x01, 0x65, 0x03, 0x04, 0x02, 0x01, 0x05, 0x00];
  const imprint = [0x30, 0, ...algo, 0x04, 0x20, ...digest]; imprint[1] = imprint.length - 2;
  const body = [0x02, 0x01, 0x01, ...imprint, 0x02, 0x08, ...nonce, 0x01, 0x01, 0xff];
  return new Uint8Array([0x30, body.length, ...body]);
}
async function chiediMarca(url, digest) {
  const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/timestamp-query' }, body: tsqDer(digest), signal: AbortSignal.timeout(20000) });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return new Uint8Array(await r.arrayBuffer());
}

async function autorizzato(req) {
  const segreto = req.headers.get('x-sistema-secret');
  if (segreto) {
    const r = await rest(`app_segreti?chiave=eq.sistema_secret&select=valore`);
    return Array.isArray(r) && r[0] && r[0].valore === segreto ? 'sistema' : null;
  }
  const auth = req.headers.get('authorization') || '';
  if (!auth.startsWith('Bearer ')) return null;
  const u = await fetch(`${SB_URL}/auth/v1/user`, { headers: { apikey: SB_KEY, Authorization: auth } });
  if (!u.ok) return null;
  const user = await u.json();
  const p = await rest(`presenze_profili?id=eq.${user.id}&select=ruolo,eliminato`);
  return Array.isArray(p) && p[0] && p[0].ruolo === 'admin' && !p[0].eliminato ? 'admin' : null;
}

// ── controllo di UN giorno sigillato ────────────────────────────────────
async function controllaGiorno(s, prec, primoGiorno, prova) {
  const C = []; // { voce, ok, nota }
  const add = (voce, ok, nota) => C.push({ voce, ok, nota: nota || null });
  const out = { giorno: s.giorno, controlli: C, marche: [], bitcoin: null, riparazioni: [] };

  // 2. manifesto salvato = manifesto sigillato
  const manB = await scarica(`${s.percorso}.manifesto.json`);
  if (!manB) { add('Manifesto del giorno', false, 'file del manifesto non trovato'); return chiudi(out); }
  const impMan = await sha256(manB);
  if (hex(impMan) !== s.sigillo_sha256) { add('Manifesto del giorno', false, 'il file salvato non ha l\'impronta sigillata'); return chiudi(out); }
  let man; try { man = JSON.parse(new TextDecoder().decode(manB)); } catch { add('Manifesto del giorno', false, 'manifesto illeggibile'); return chiudi(out); }
  add('Manifesto del giorno', true, 'impronta ' + s.sigillo_sha256.slice(0, 16) + '…');

  // 3. manifesto completo e coerente
  const he = man.hash_eventi || [];
  const n = he.length;
  let coerente = man.giorno === s.giorno && man.eventi_del_giorno === n && n === s.n_eventi
    && (n === 0 ? man.primo_anello === null : (man.primo_anello === s.primo_anello && he[0].anello === man.primo_anello && he[n - 1].anello === man.ultimo_anello))
    && man.ultimo_anello === s.ultimo_anello;
  for (let i = 1; coerente && i < n; i++) if (he[i].anello !== he[i - 1].anello + 1) coerente = false;
  if (coerente && n > 0 && he[n - 1].hash !== man.hash_testa_catena) coerente = false;
  add('Numerazione completa nel giorno', coerente, coerente ? `${n} eventi, dal n. ${man.primo_anello ?? '—'} al n. ${man.ultimo_anello}` : 'manifesto incompleto o incoerente');

  // continuità con il giorno prima
  if (s.giorno > primoGiorno) {
    if (!prec) add('Attaccato al giorno precedente', false, 'manca il sigillo del giorno precedente');
    else {
      const okc = n === 0 ? s.ultimo_anello === prec.ultimo_anello : s.primo_anello === prec.ultimo_anello + 1;
      add('Attaccato al giorno precedente', okc, okc ? 'continua dal n. ' + prec.ultimo_anello : 'salto di numerazione tra i due giorni');
    }
  }

  // 4. database = manifesto, catena integra
  const { dal_utc: dal, al_utc: al } = man;
  const righe = await esportaTutto(dal, al);
  let okDb = righe.length === n;
  for (let i = 0; okDb && i < n; i++) if (righe[i].anello !== he[i].anello || righe[i].hash !== he[i].hash) okDb = false;
  let okHash = true;
  for (let i = 0; okHash && i < righe.length; i++) {
    const r = righe[i];
    if (hex(await sha256(r.testo_canonico)) !== r.hash || !r.testo_canonico.startsWith(r.hash_prec + '|' + r.anello + '|')) okHash = false;
    if (i > 0 && r.hash_prec !== righe[i - 1].hash) okHash = false;
  }
  if (okHash && n > 0 && prec && prec.hash_testa && righe[0].hash_prec !== prec.hash_testa) okHash = false;
  let okVer = true;
  if (n > 0) { const v = await rpc('registro_verifica', { p_da: man.primo_anello, p_a: man.ultimo_anello }); okVer = !!(v && v.ok && v.verificati === n); }
  const jsonl = righe.map((r) => JSON.stringify(r)).join('\n') + '\n';
  const okJsonl = hex(await sha256(jsonl)) === s.file_sha256;
  add('Registro identico al sigillo', okDb && okJsonl, okDb && okJsonl ? 'ogni evento coincide con il sigillo' : 'il registro non coincide con il sigillo');
  add('Catena delle impronte integra', okHash && okVer, okHash && okVer ? 'impronte ricalcolate e collegate' : 'collegamento o impronta non validi');

  // 5. marche temporali
  const finegiorno = new Date(al).getTime();
  let marcheValide = 0;
  for (const t of TSA) {
    const base = `${s.percorso}.${t.nome.toLowerCase()}`;
    const cand = [['notturna', `${base}.tsr`], ['recupero', `${base}.recupero.tsr`]];
    let buona = null, motivi = [];
    for (const [tipo, p] of cand) {
      const b = await scarica(p); if (!b) continue;
      const r = await verificaMarca(LIB, t.nome, b, manB);
      if (r.ok && new Date(r.ora).getTime() >= finegiorno - 60000) { buona = { tipo, ...r }; break; }
      motivi.push(tipo + ': ' + (r.ok ? 'ora della marca precedente alla fine del giorno' : r.motivo));
    }
    if (!buona && !prova) {
      try {
        const b = await chiediMarca(t.url, impMan);
        const r = await verificaMarca(LIB, t.nome, b, manB);
        if (r.ok) { await carica(`${base}.recupero.tsr`, b, 'application/timestamp-reply'); buona = { tipo: 'recupero', ...r }; out.riparazioni.push(`marca ${t.nome} mancante o non valida: ottenuta marca di recupero (${fmtOra(r.ora)})`); }
        else motivi.push('recupero: ' + r.motivo);
      } catch (e) { motivi.push('recupero: ente non raggiungibile'); }
    }
    out.marche.push(buona ? { ente: t.nome, ok: true, tipo: buona.tipo, ora: buona.ora, firmatario: buona.firmatario } : { ente: t.nome, ok: false, motivo: motivi.join('; ') || 'ricevuta assente' });
    if (buona) marcheValide++;
  }
  add('Marche temporali FreeTSA e DigiCert', marcheValide === TSA.length,
    out.marche.map((m) => m.ente + (m.ok ? ' ✓ ' + fmtOra(m.ora) + (m.tipo === 'recupero' ? ' (recupero)' : '') : ' ✕ ' + m.motivo)).join(' · '));

  // 6. Bitcoin
  let otsB = await scarica(`${s.percorso}.completo.ots`), giaCompleta = !!otsB, recOts = false;
  if (!otsB) otsB = await scarica(`${s.percorso}.ots`);
  if (!otsB) { otsB = await scarica(`${s.percorso}.recupero.ots`); recOts = !!otsB; }
  if (!otsB) {
    if (!prova) { const o = await nuovaOts(impMan); if (o) { await carica(`${s.percorso}.recupero.ots`, o.bytes, 'application/octet-stream'); out.riparazioni.push('prova Bitcoin assente: inviata ora ai calendari'); } }
    out.bitcoin = { stato: 'in_attesa', motivo: 'prova Bitcoin richiesta solo ora' };
  } else {
    try {
      const p = await leggiOts(otsB, impMan);
      if (!giaCompleta) await completaOts(p);
      const v = await verificaBitcoin(p);
      if (v.ok && !giaCompleta && !prova) await carica(`${s.percorso}.completo.ots`, scriviOts(p), 'application/octet-stream');
      out.bitcoin = v.ok ? { stato: 'ok', blocco: v.blocco, ora_blocco: v.ora_blocco, hash_blocco: v.hash_blocco, archivi: v.archivi, calendari: [...new Set(attestazioni(p).filter((a) => a.tipo === 'in_attesa').map((a) => a.uri))] }
        : { stato: v.stato, motivo: v.motivo };
      if (recOts) out.bitcoin.recupero = true;
    } catch (e) { out.bitcoin = { stato: 'anomalia', motivo: String((e && e.message) || e) }; }
  }
  const oreDaFine = (Date.now() - finegiorno) / 3600000;
  if (out.bitcoin.stato === 'ok') add('Prova su Bitcoin', true, `blocco n. ${out.bitcoin.blocco} del ${fmtOra(out.bitcoin.ora_blocco)}, confermato da ${(out.bitcoin.archivi || []).join(' e ')}`);
  else if (out.bitcoin.stato === 'anomalia') add('Prova su Bitcoin', false, out.bitcoin.motivo);
  else if (out.bitcoin.stato === 'non_verificabile') add('Prova su Bitcoin', null, 'archivi Bitcoin non raggiungibili ora: si riprova al prossimo controllo');
  else if (oreDaFine > ATTESA_BITCOIN_ORE) add('Prova su Bitcoin', false, `non ancora registrata dopo ${Math.round(oreDaFine)} ore (${out.bitcoin.motivo})`);
  else add('Prova su Bitcoin', null, 'in attesa di registrazione (normale nelle prime ore)');
  return chiudi(out);
}
function chiudi(out) {
  const ko = out.controlli.filter((c) => c.ok === false);
  out.esito = ko.length ? 'anomalia' : out.controlli.some((c) => c.ok === null) ? 'in_attesa' : 'ok';
  out.anomalie = ko.map((c) => c.voce + ': ' + c.nota);
  return out;
}

// Diagnostica senza scritture: cosa funziona da questo server (crittografia e archivi Bitcoin)
async function diagnostica() {
  const out = { crittografia: {}, archivi: {} };
  try { const k = await crypto.subtle.generateKey({ name: 'ECDSA', namedCurve: 'P-384' }, true, ['sign', 'verify']);
    const d = new TextEncoder().encode('prova'); const sg = await crypto.subtle.sign({ name: 'ECDSA', hash: 'SHA-384' }, k.privateKey, d);
    out.crittografia.ecdsa_p384_sha384 = await crypto.subtle.verify({ name: 'ECDSA', hash: 'SHA-384' }, k.publicKey, sg, d);
    try { await crypto.subtle.verify({ name: 'ECDSA', hash: 'SHA-512' }, k.publicKey, sg, d); out.crittografia.ecdsa_p384_sha512 = 'supportato'; }
    catch (e) { out.crittografia.ecdsa_p384_sha512 = 'non supportato dal server: si usa la riserva (' + String(e.message || e).slice(0, 40) + ')'; }
  } catch (e) { out.crittografia.errore = String(e.message || e); }
  const s = await rest(`registro_sigilli?select=*&order=giorno.desc&limit=1`);
  if (s && s.length) {
    const man = await scarica(`${s[0].percorso}.manifesto.json`);
    for (const t of TSA) { const b = await scarica(`${s[0].percorso}.${t.nome.toLowerCase()}.tsr`); out.crittografia['marca_' + t.nome + '_' + s[0].giorno] = b && man ? await verificaMarca(LIB, t.nome, b, man) : 'file assente'; }
  }
  const f = (u) => fetch(u, { signal: AbortSignal.timeout(20000), headers: { Accept: 'application/json' } });
  for (const a of ARCHIVI_BITCOIN) { try { const b = await a.blocco(f, 970567); out.archivi[a.nome] = b.merkle ? 'raggiungibile' : 'risposta vuota'; } catch (e) { out.archivi[a.nome] = 'non raggiungibile: ' + String(e.message || e).slice(0, 60); } }
  return out;
}

async function ancoreRecenti() {
  const r = await rest(`registro_ancore?select=ok,creato_il&creato_il=gte.${encodeURIComponent(new Date(Date.now() - 86400000).toISOString())}&order=id.asc`);
  let fila = 0, max = 0, ko = 0;
  for (const a of (r || [])) { if (a.ok) fila = 0; else { fila++; ko++; max = Math.max(max, fila); } }
  return { totale: (r || []).length, fallite: ko, fallite_di_fila: max, ok: max < 3 };
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: CORS });
  const J = (o, st = 200) => new Response(JSON.stringify(o), { status: st, headers: { ...CORS, 'Content-Type': 'application/json' } });
  try {
    const chi = await autorizzato(req);
    if (!chi) return J({ errore: 'Non autorizzato' }, 401);
    let body = {}; try { body = await req.json(); } catch (_) { /* vuoto */ }
    if (body.diagnostica) return J(await diagnostica());
    const inizio = Date.now();
    const prova = !!body.prova;
    const avvisare = chi === 'sistema' && body.avvisa !== false;
    const ieri = giornoRoma(new Date(Date.now() - 86400000));
    const primoSig = await rest(`registro_sigilli?select=giorno&order=giorno.asc&limit=1`);
    const primoGiorno = primoSig && primoSig.length ? primoSig[0].giorno : ieri;

    // quali giorni: richiesti esplicitamente, oppure ieri + i recenti non ancora definitivi
    let giorni = [];
    if (Array.isArray(body.giorni) && body.giorni.length) giorni = body.giorni.map(String).filter((g) => /^\d{4}-\d{2}-\d{2}$/.test(g)).slice(0, 62);
    else {
      giorni = [ieri];
      const da = giornoRoma(new Date(Date.now() - GIORNI_RICONTROLLO * 86400000));
      const sig = await rest(`registro_sigilli?select=giorno&giorno=gte.${da}&giorno=lte.${ieri}&order=giorno.asc`);
      const ctr = await rest(`registro_controlli?select=giorno,esito,eseguito_il&giorno=gte.${da}&order=eseguito_il.desc`);
      const ultimo = {}; for (const c of (ctr || [])) if (!ultimo[c.giorno]) ultimo[c.giorno] = c.esito;
      for (const x of (sig || [])) if (ultimo[x.giorno] !== 'ok' && !giorni.includes(x.giorno)) giorni.push(x.giorno);
      // v79: anche i giorni PIÙ VECCHI rimasti non definitivi (in attesa o anomalia) si ricontrollano
      // finché non tornano a posto: nessun giorno resta "in sospeso" per sempre senza che nessuno lo sappia
      const nonOk = await rest(`registro_controlli?select=giorno&esito=neq.ok&giorno=lt.${da}&order=giorno.asc&limit=1000`);
      const cand = [...new Set((nonOk || []).map((c) => c.giorno))];
      if (cand.length) {
        const ctr2 = await rest(`registro_controlli?select=giorno,esito,eseguito_il&giorno=in.(${cand.join(',')})&order=eseguito_il.desc&limit=5000`);
        const ult2 = {}; for (const c of (ctr2 || [])) if (!ult2[c.giorno]) ult2[c.giorno] = c.esito;
        for (const g of cand) if (ult2[g] !== 'ok' && !giorni.includes(g)) giorni.push(g);
      }
      giorni.sort();
    }

    const avvisi = [], risultati = [];
    // 1. il sigillo di ieri esiste? se no si prova a crearlo subito
    if (giorni.includes(ieri) && !prova) {
      const c = await rest(`registro_sigilli?giorno=eq.${ieri}&select=giorno`);
      if (!c || !c.length) {
        const sec = await rest(`app_segreti?chiave=eq.sistema_secret&select=valore`);
        try {
          await fetch(`${SB_URL}/functions/v1/registro-sigillo`, { method: 'POST', headers: { ...H, 'x-sistema-secret': sec[0].valore }, body: '{}', signal: AbortSignal.timeout(140000) });
        } catch (_e) { /* si controlla sotto */ }
      }
    }
    const rimandati = [];
    for (const g of giorni) {
      if (Date.now() - inizio > TEMPO_MAX_MS) { rimandati.push(g); continue; }
      const s = await rest(`registro_sigilli?giorno=eq.${g}&select=*`);
      if (!s || !s.length) {
        const r = { giorno: g, esito: 'anomalia', controlli: [{ voce: 'Sigillo del giorno', ok: false, nota: 'il sigillo non esiste e non è stato possibile crearlo' }], anomalie: ['Sigillo del giorno: non esiste'] };
        risultati.push(r); continue;
      }
      const p = await rest(`registro_sigilli?giorno=lt.${g}&select=*&order=giorno.desc&limit=1`);
      const prec = p && p.length && p[0].giorno === giornoPrima(g) ? p[0] : null;
      try { risultati.push(await controllaGiorno(s[0], prec, primoGiorno, prova)); }
      catch (e) {
        if (!(e instanceof NonVerificabile)) throw e;
        risultati.push(chiudi({ giorno: g, controlli: [{ voce: 'Controllo eseguibile', ok: null, nota: e.message + ': si riprova al prossimo controllo' }], marche: [], bitcoin: null, riparazioni: [] }));
      }
    }
    const ancore = await ancoreRecenti();

    // v79: una verifica che non riesce a completarsi (ente o archivio irraggiungibile, prova Bitcoin
    // che non arriva) non può restare "in attesa" per sempre: dopo ATTESA_VERIFICA_ORE dal primo
    // controllo di quel giorno diventa un'anomalia e l'admin viene avvisato.
    // (solo in prova, che non scrive niente, la soglia si può abbassare per collaudare questo passaggio)
    const soglia = prova && Number.isFinite(body.attesa_ore) ? body.attesa_ore : ATTESA_VERIFICA_ORE;
    const sospesi = risultati.filter((r) => r.esito === 'in_attesa').map((r) => r.giorno);
    if (sospesi.length) {
      const primi = await rest(`registro_controlli?select=giorno,eseguito_il&giorno=in.(${sospesi.join(',')})&order=eseguito_il.asc&limit=5000`);
      const primo = {}; for (const c of (primi || [])) if (!primo[c.giorno]) primo[c.giorno] = c.eseguito_il;
      for (const r of risultati) {
        if (r.esito !== 'in_attesa' || !primo[r.giorno]) continue;
        const ore = (Date.now() - new Date(primo[r.giorno]).getTime()) / 3600000;
        if (ore <= soglia) continue;
        for (const c of r.controlli) if (c.ok === null) { c.ok = false; c.nota = `${c.nota} — non si completa da ${Math.round(ore)} ore (primo controllo ${fmtOra(primo[r.giorno])})`; }
        chiudi(r);
      }
    }

    if (!prova) {
      for (const r of risultati) {
        await rest('registro_controlli', { method: 'POST', headers: { Prefer: 'return=minimal' },
          body: JSON.stringify({ giorno: r.giorno, esito: r.esito, dettagli: { controlli: r.controlli, marche: r.marche, bitcoin: r.bitcoin, riparazioni: r.riparazioni || [] }, origine: chi }) });
        // l'esito definitivo del giorno entra anche nel registro legale (una volta per esito)
        if (r.esito !== 'in_attesa') {
          const gia = await rest(`registro_controlli?select=id&giorno=eq.${r.giorno}&esito=eq.${r.esito}&nel_registro=eq.true&limit=1`);
          if (!gia || !gia.length) {
            await rpc('registro_evento_sistema', { p_azione: 'controllo_sigillo', p_tabella: 'registro_sigilli', p_rif: r.giorno, p_dip: null,
              p_dati: { giorno: r.giorno, esito: r.esito, controlli: r.controlli.map((c) => ({ voce: c.voce, ok: c.ok, nota: c.nota })), bitcoin: r.bitcoin, riparazioni: r.riparazioni || [] } });
            await rest(`registro_controlli?giorno=eq.${r.giorno}&esito=eq.${r.esito}&nel_registro=eq.false`, { method: 'PATCH', headers: { Prefer: 'return=minimal' }, body: JSON.stringify({ nel_registro: true }) });
          }
        }
        if (r.esito === 'anomalia') avvisi.push('• <b>' + fmtG(r.giorno) + '</b>: ' + r.anomalie.join('; '));
      }
      if (!ancore.ok) avvisi.push(`• Ancore orarie: ${ancore.fallite_di_fila} fallite di fila nelle ultime 24 ore`);
      // AVVISO SOLO SE QUALCOSA NON VA (e solo dal controllo automatico: l'admin che preme "Controlla ora" vede già l'esito)
      if (avvisi.length && avvisare) {
        await rpc('presenze_avvisa', { p_dip: null, p_testo: '⚠️ <b>Registro legale: anomalia nel controllo automatico</b>\n' + avvisi.join('\n').slice(0, 3000)
          + '\n\nApri Registro legale e tocca «Riprova ora».', p_link: '#registro', p_tabella: 'registro_controlli', p_rif: null });
      }
    }
    return J({ esito: risultati.some((r) => r.esito === 'anomalia') || !ancore.ok ? 'anomalia' : risultati.some((r) => r.esito === 'in_attesa') ? 'in_attesa' : 'ok', prova, giorni: risultati, rimandati, ancore, durata_ms: Date.now() - inizio });
  } catch (e) {
    return J({ errore: String((e && e.message) || e) }, 500);
  }
});
