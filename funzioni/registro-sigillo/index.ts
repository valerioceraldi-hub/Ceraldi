// @ts-nocheck
// ════════════════════════════════════════════════════════════════════════
// registro-sigillo — SIGILLO NOTTURNO DEL REGISTRO LEGALE (Presenze 2.1/2.2)
// ────────────────────────────────────────────────────────────────────────
// Ogni notte (pg_cron, 01:20 UTC) e su richiesta dell'admin ("Sigilla ora"):
//  1. calcola l'impronta SHA-256 dei documenti caricati quel giorno e la
//     scrive nel registro;
//  2. esporta gli eventi del giorno in un file JSONL con, per ogni riga, la
//     stringa canonica esatta da cui nasce l'impronta;
//  3. fa marcare temporalmente il manifesto del giorno da FreeTSA e DigiCert
//     (RFC 3161) e da OpenTimestamps (ancoraggio su Bitcoin);
//  4. salva file, marche e manifesto nel bucket privato "registro-legale"
//     e scrive la riga del giorno in registro_sigilli (immutabile).
// Chi può chiamarla: pg_cron (intestazione x-sistema-secret) oppure un admin loggato.
// 2.2: con {"modo":"ancora"} (ogni ora) marca solo la testa della catena.
//
// v79 (28/11/2026):
//  - LETTURA PAGINATA degli eventi: prima una sola richiesta, che il server
//    limita a 1.000 righe. Un giorno con più eventi avrebbe prodotto un
//    sigillo incompleto e non più correggibile. Ora si legge a pagine finché
//    non arriva una pagina vuota (vale con qualunque limite del server).
//  - OpenTimestamps: la prova si chiede a DUE calendari (prima uno solo) e le
//    ricevute si uniscono nello stesso file .ots: se un calendario sparisce,
//    l'altro basta a completare la prova su Bitcoin.
//  - {"prova":true,"giorno":"AAAA-MM-GG"}: ricostruisce il manifesto di un
//    giorno già sigillato SENZA scrivere niente e dice se è identico a quello
//    sigillato (prova che la lettura paginata non cambia il risultato).
// ════════════════════════════════════════════════════════════════════════
import { nuovaOts, leggiOts, attestazioni } from './ots.js';

const SB_URL = Deno.env.get('SUPABASE_URL')!;
const SB_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
const H = { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}`, 'Content-Type': 'application/json' };
const BUCKET = 'registro-legale';
const TSA = [
  { nome: 'FreeTSA', url: 'https://freetsa.org/tsr' },
  { nome: 'DigiCert', url: 'http://timestamp.digicert.com' },
];
const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type, x-sistema-secret',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
};
const PAGINA = 1000;

const hex = (b: Uint8Array) => [...b].map((x) => x.toString(16).padStart(2, '0')).join('');
const unhex = (s: string) => new Uint8Array(s.match(/../g)!.map((x) => parseInt(x, 16)));
async function sha256(data: Uint8Array | string): Promise<Uint8Array> {
  const buf = typeof data === 'string' ? new TextEncoder().encode(data) : data;
  return new Uint8Array(await crypto.subtle.digest('SHA-256', buf));
}
async function rest(path: string, init: RequestInit = {}) {
  const r = await fetch(`${SB_URL}/rest/v1/${path}`, { ...init, headers: { ...H, ...(init.headers || {}) } });
  const t = await r.text();
  if (!r.ok) throw new Error(`${path.split('?')[0]}: ${r.status} ${t.slice(0, 200)}`);
  return t ? JSON.parse(t) : null;
}
const rpc = (fn: string, body: unknown) => rest(`rpc/${fn}`, { method: 'POST', body: JSON.stringify(body) });

// v79: export del registro a pagine, in ordine di anello, finché arriva una pagina vuota
async function esportaTutto(dal: string, al: string, dip: string | null) {
  const tutti: any[] = [];
  for (let da = 0; ; ) {
    const pag = await rest(`rpc/registro_esporta?order=anello.asc&limit=${PAGINA}&offset=${da}`,
      { method: 'POST', body: JSON.stringify({ p_dal: dal, p_al: al, p_dipendente: dip }) });
    if (!pag || !pag.length) break;
    for (const r of pag) {
      if (tutti.length && r.anello <= tutti[tutti.length - 1].anello) throw new Error('export del registro non in ordine: interrotto per sicurezza');
      tutti.push(r);
    }
    da += pag.length;
    if (da > 5_000_000) throw new Error('export troppo grande');
  }
  return tutti;
}

// RFC 3161: richiesta DER costruita a mano (nessuna libreria esterna)
function tsqDer(digest: Uint8Array): Uint8Array {
  const nonce = crypto.getRandomValues(new Uint8Array(8)); nonce[0] &= 0x7f; if (nonce[0] === 0) nonce[0] = 1;
  const algo = [0x30, 0x0d, 0x06, 0x09, 0x60, 0x86, 0x48, 0x01, 0x65, 0x03, 0x04, 0x02, 0x01, 0x05, 0x00];
  const imprint = [0x30, 2 + algo.length + 2 + 32 - 2, ...algo, 0x04, 0x20, ...digest];
  imprint[1] = imprint.length - 2;
  const body = [0x02, 0x01, 0x01, ...imprint, 0x02, 0x08, ...nonce, 0x01, 0x01, 0xff];
  return new Uint8Array([0x30, body.length, ...body]);
}
function tsrInfo(r: Uint8Array): { ok: boolean; stato: number; ora: string | null } {
  let i = 1; const lenByte = r[1];
  i = lenByte & 0x80 ? 2 + (lenByte & 0x7f) : 2;
  if (r[i] !== 0x30) return { ok: false, stato: -1, ora: null };
  const j = i + 2;
  const stato = r[j] === 0x02 ? r[j + 2] : -1;
  let ora: string | null = null;
  for (let k = 0; k < r.length - 17; k++) {
    if (r[k] === 0x18 && r[k + 1] >= 15 && r[k + 1] <= 24) {
      const s = new TextDecoder().decode(r.slice(k + 2, k + 2 + r[k + 1]));
      if (/^\d{14}(\.\d+)?Z$/.test(s)) { ora = `${s.slice(0, 4)}-${s.slice(4, 6)}-${s.slice(6, 8)}T${s.slice(8, 10)}:${s.slice(10, 12)}:${s.slice(12)}`; break; }
    }
  }
  return { ok: stato === 0 || stato === 1, stato, ora };
}
async function marcaTemporale(url: string, digest: Uint8Array) {
  const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/timestamp-query' }, body: tsqDer(digest), signal: AbortSignal.timeout(20000) });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  const tsr = new Uint8Array(await r.arrayBuffer());
  return { tsr, ...tsrInfo(tsr) };
}

function giornoRoma(d: Date): string {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Rome', year: 'numeric', month: '2-digit', day: '2-digit' }).format(d);
}
function limitiGiornoRoma(giorno: string): { dal: string; al: string } {
  const inizio = (g: string) => {
    for (const off of ['+02:00', '+01:00']) {
      const d = new Date(`${g}T00:00:00${off}`);
      if (giornoRoma(d) === g && giornoRoma(new Date(d.getTime() - 1000)) !== g) return d;
    }
    return new Date(`${g}T00:00:00+01:00`);
  };
  const dopo = new Date(new Date(`${giorno}T12:00:00Z`).getTime() + 86400000);
  return { dal: inizio(giorno).toISOString(), al: inizio(dopo.toISOString().slice(0, 10)).toISOString() };
}

async function autorizzato(req: Request): Promise<boolean> {
  const segreto = req.headers.get('x-sistema-secret');
  if (segreto) {
    const r = await rest(`app_segreti?chiave=eq.sistema_secret&select=valore`);
    return Array.isArray(r) && r[0] && r[0].valore === segreto;
  }
  const auth = req.headers.get('authorization') || '';
  if (!auth.startsWith('Bearer ')) return false;
  const u = await fetch(`${SB_URL}/auth/v1/user`, { headers: { apikey: SB_KEY, Authorization: auth } });
  if (!u.ok) return false;
  const user = await u.json();
  const p = await rest(`presenze_profili?id=eq.${user.id}&select=ruolo,eliminato`);
  return Array.isArray(p) && p[0] && p[0].ruolo === 'admin' && !p[0].eliminato;
}

async function carica(percorso: string, dati: Uint8Array | string, tipo: string) {
  const r = await fetch(`${SB_URL}/storage/v1/object/${BUCKET}/${percorso}`, {
    method: 'POST', headers: { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}`, 'Content-Type': tipo, 'x-upsert': 'true' },
    body: typeof dati === 'string' ? new TextEncoder().encode(dati) : dati,
  });
  if (!r.ok) throw new Error(`upload ${percorso}: ${r.status} ${(await r.text()).slice(0, 150)}`);
}
async function scarica(percorso: string): Promise<Uint8Array | null> {
  const r = await fetch(`${SB_URL}/storage/v1/object/${BUCKET}/${percorso}`, { headers: { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}` } });
  if (!r.ok) { await r.body?.cancel(); return null; }
  return new Uint8Array(await r.arrayBuffer());
}

async function improntaDocumenti(dal: string, al: string): Promise<number> {
  const docs = await rest(`presenze_documenti?select=id,dipendente_id,url,nome_file,categoria,anno,mese&creato_il=gte.${encodeURIComponent(dal)}&creato_il=lt.${encodeURIComponent(al)}`);
  let n = 0;
  for (const d of (docs || [])) {
    if (!d.url || /^https?:/.test(d.url)) continue;
    try {
      const r = await fetch(`${SB_URL}/storage/v1/object/presenze-allegati/${d.url}`, { headers: { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}` } });
      if (!r.ok) continue;
      const bytes = new Uint8Array(await r.arrayBuffer());
      await rpc('registro_evento_sistema', {
        p_azione: 'impronta_documento', p_tabella: 'presenze_documenti', p_rif: d.id, p_dip: d.dipendente_id,
        p_dati: { sha256: hex(await sha256(bytes)), byte: bytes.length, file: d.nome_file, percorso: d.url, categoria: d.categoria, anno: d.anno, mese: d.mese },
      });
      n++;
    } catch (_) { /* un file illeggibile non ferma il sigillo */ }
  }
  return n;
}

// Costruisce manifesto e file JSONL di un giorno (uguale per il sigillo vero e per la prova)
async function costruisciManifesto(giorno: string, nDoc: number) {
  const { dal, al } = limitiGiornoRoma(giorno);
  const righe = await esportaTutto(dal, al, null);
  const testa = await rest(`registro_eventi?select=anello,hash&creato_il=lt.${encodeURIComponent(al)}&order=anello.desc&limit=1`);
  if (!testa || !testa.length) return null;
  const jsonl = (righe || []).map((r: unknown) => JSON.stringify(r)).join('\n') + '\n';
  const fileSha = hex(await sha256(jsonl));
  const manifesto = {
    tipo: 'Sigillo giornaliero del registro legale — Presenze',
    giorno, fuso: 'Europe/Rome', dal_utc: dal, al_utc: al,
    eventi_del_giorno: (righe || []).length,
    primo_anello: righe && righe.length ? righe[0].anello : null,
    ultimo_anello: testa[0].anello, hash_testa_catena: testa[0].hash,
    file: `${giorno}.jsonl`, file_sha256: fileSha, impronte_documenti: nDoc,
    hash_eventi: (righe || []).map((r: any) => ({ anello: r.anello, hash: r.hash })),
    algoritmo: 'hash = SHA-256(testo_canonico); testo_canonico inizia con hash della riga precedente e numero di anello',
  };
  const manifestoTxt = JSON.stringify(manifesto, null, 2);
  return { manifesto, manifestoTxt, jsonl, fileSha, sigillo: await sha256(manifestoTxt) };
}

async function sigillaGiorno(giorno: string) {
  const { dal, al } = limitiGiornoRoma(giorno);
  const nDoc = await improntaDocumenti(dal, al);
  const m = await costruisciManifesto(giorno, nDoc);
  if (!m) return { giorno, saltato: 'registro vuoto' };
  const { manifesto, manifestoTxt, jsonl, fileSha, sigillo } = m;
  const cartella = `${giorno.slice(0, 4)}/${giorno.slice(5, 7)}/${giorno}`;
  const marche: Record<string, unknown>[] = [];
  for (const t of TSA) {
    try {
      const mt = await marcaTemporale(t.url, sigillo);
      await carica(`${cartella}.${t.nome.toLowerCase()}.tsr`, mt.tsr, 'application/timestamp-reply');
      marche.push({ tsa: t.nome, ok: mt.ok, ora: mt.ora, file: `${cartella}.${t.nome.toLowerCase()}.tsr` });
    } catch (e) { marche.push({ tsa: t.nome, ok: false, errore: String((e as Error)?.message || e) }); }
  }
  const ots = await nuovaOts(sigillo);
  if (ots) await carica(`${cartella}.ots`, ots.bytes, 'application/octet-stream');
  await carica(`${cartella}.jsonl`, jsonl, 'application/x-ndjson');
  await carica(`${cartella}.manifesto.json`, manifestoTxt, 'application/json');
  const ok = marche.some((x) => x.ok);
  await rpc('registro_sigillo_salva', { p: {
    giorno, primo_anello: manifesto.primo_anello, ultimo_anello: manifesto.ultimo_anello, n_eventi: manifesto.eventi_del_giorno,
    hash_testa: manifesto.hash_testa_catena, file_sha256: fileSha, sigillo_sha256: hex(sigillo), marche, ots: !!ots,
    percorso: cartella, esito: ok ? 'sigillato' : 'senza marca (riprovare)',
  } });
  return { giorno, eventi: manifesto.eventi_del_giorno, documenti: nDoc, marche, ots: !!ots, calendari: ots ? ots.calendari : [], sigillo: hex(sigillo) };
}

// v79: PROVA senza scritture — ricostruisce un giorno già sigillato e lo confronta
async function provaGiorno(giorno: string, provaOts: boolean) {
  const s = await rest(`registro_sigilli?giorno=eq.${giorno}&select=*`);
  if (!s || !s.length) return { giorno, errore: 'giorno non sigillato' };
  const salvato = await scarica(`${s[0].percorso}.manifesto.json`);
  const nDoc = salvato ? JSON.parse(new TextDecoder().decode(salvato)).impronte_documenti : 0;
  const m = await costruisciManifesto(giorno, nDoc);
  if (!m) return { giorno, errore: 'registro vuoto' };
  const out: any = {
    giorno, eventi: m.manifesto.eventi_del_giorno,
    manifesto_identico_al_sigillato: hex(m.sigillo) === s[0].sigillo_sha256,
    jsonl_identico_al_sigillato: m.fileSha === s[0].file_sha256,
    manifesto_salvato_identico: !!salvato && hex(await sha256(salvato)) === s[0].sigillo_sha256,
  };
  if (provaOts) {
    // impronta di prova (non del registro): verifica che l'invio a due calendari funzioni da qui
    const d = await sha256('prova invio OpenTimestamps Ceraldi ' + new Date().toISOString());
    const o = await nuovaOts(d);
    out.ots_prova = o ? { calendari: o.calendari, in_attesa: attestazioni(await leggiOts(o.bytes, d)).filter((a) => a.tipo === 'in_attesa').map((a) => a.uri) } : null;
  }
  return out;
}
async function provaPaginazione(dal: string, al: string) {
  const r = await fetch(`${SB_URL}/rest/v1/rpc/registro_esporta`, { method: 'POST', headers: H, body: JSON.stringify({ p_dal: dal, p_al: al, p_dipendente: null }) });
  const vecchio = r.ok ? (await r.json()).length : null;
  const nuovo = (await esportaTutto(dal, al, null)).length;
  const conta = await fetch(`${SB_URL}/rest/v1/registro_eventi?select=anello&creato_il=gte.${encodeURIComponent(dal)}&creato_il=lt.${encodeURIComponent(al)}`,
    { method: 'HEAD', headers: { ...H, Prefer: 'count=exact' } });
  const tot = Number((conta.headers.get('content-range') || '/').split('/')[1]);
  return { dal, al, eventi_nel_database: tot, lettura_senza_pagine: vecchio, lettura_a_pagine: nuovo };
}

// Presenze 2.2: ANCORAGGIO ORARIO della testa della catena (FreeTSA, poi DigiCert)
async function ancoraOraria() {
  const testa = await rest(`registro_eventi?select=anello,hash&order=anello.desc&limit=1`);
  if (!testa || !testa.length) return { esito: 'registro vuoto' };
  const ultima = await rest(`registro_ancore?select=anello&order=id.desc&limit=1`);
  if (ultima && ultima.length && ultima[0].anello === testa[0].anello) return { esito: 'nessun evento nuovo', anello: testa[0].anello };
  const digest = unhex(testa[0].hash);
  const ora = new Date().toISOString();
  const perc = `ancore/${ora.slice(0, 4)}/${ora.slice(5, 7)}/${ora.slice(8, 10)}/${ora.slice(11, 13)}${ora.slice(14, 16)}-${testa[0].anello}`;
  for (const t of TSA) {
    try {
      const m = await marcaTemporale(t.url, digest);
      await carica(`${perc}.${t.nome.toLowerCase()}.tsr`, m.tsr, 'application/timestamp-reply');
      await rpc('registro_ancora_salva', { p: { anello: testa[0].anello, hash: testa[0].hash, tsa: t.nome, ok: m.ok, ora_marca: m.ora, percorso: `${perc}.${t.nome.toLowerCase()}.tsr` } });
      return { esito: 'ok', anello: testa[0].anello, tsa: t.nome, ora: m.ora };
    } catch (_e) { /* si prova la seconda autorità */ }
  }
  await rpc('registro_ancora_salva', { p: { anello: testa[0].anello, hash: testa[0].hash, tsa: null, ok: false, ora_marca: null, percorso: null } });
  return { esito: 'nessuna autorità raggiungibile', anello: testa[0].anello };
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: CORS });
  const J = (o: unknown, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { ...CORS, 'Content-Type': 'application/json' } });
  try {
    if (!(await autorizzato(req))) return J({ errore: 'Non autorizzato' }, 401);
    let body: any = {}; try { body = await req.json(); } catch (_) { /* vuoto */ }
    if (body.modo === 'ancora') return J(await ancoraOraria());
    if (body.prova) {
      const out: any = { prova: true, giorni: [] };
      for (const g of (Array.isArray(body.giorni) ? body.giorni : [body.giorno]).filter(Boolean).slice(0, 10)) out.giorni.push(await provaGiorno(String(g), !!body.ots));
      if (body.paginazione) out.paginazione = await provaPaginazione(String(body.paginazione.dal), String(body.paginazione.al));
      return J(out);
    }
    const ieri = giornoRoma(new Date(Date.now() - 86400000));
    let giorni: string[] = [];
    if (body.giorno) giorni = [String(body.giorno)];
    else {
      const ult = await rest(`registro_sigilli?select=giorno&order=giorno.desc&limit=1`);
      const primo = await rest(`registro_eventi?select=creato_il&order=anello.asc&limit=1`);
      if (!primo || !primo.length) return J({ esito: 'registro vuoto' });
      let g = ult && ult.length ? ult[0].giorno : giornoRoma(new Date(primo[0].creato_il));
      if (ult && ult.length) g = giornoRoma(new Date(new Date(`${g}T12:00:00Z`).getTime() + 86400000));
      while (g <= ieri && giorni.length < 31) { giorni.push(g); g = giornoRoma(new Date(new Date(`${g}T12:00:00Z`).getTime() + 86400000)); }
    }
    const esiti = [];
    for (const g of giorni) {
      if (g > ieri) { esiti.push({ giorno: g, saltato: 'giorno non ancora concluso' }); continue; }
      const gia = await rest(`registro_sigilli?giorno=eq.${g}&select=giorno`);
      if (gia && gia.length) { esiti.push({ giorno: g, saltato: 'già sigillato' }); continue; }
      esiti.push(await sigillaGiorno(g));
    }
    return J({ esito: 'ok', giorni: esiti });
  } catch (e) {
    return J({ errore: String((e as Error)?.message || e) }, 500);
  }
});
