// ════════════════════════════════════════════════════════════════════════
// OpenTimestamps — lettura, completamento e verifica delle prove (.ots)
// Formato ufficiale: https://github.com/opentimestamps/python-opentimestamps
// Solo operazioni deterministiche: si ricalcola ogni passaggio dall'impronta
// del manifesto fino alla radice di Merkle del blocco Bitcoin, e la radice
// si confronta con DUE archivi pubblici indipendenti.
// Funziona in Deno (Edge Function) e in Node.
// ════════════════════════════════════════════════════════════════════════
export const MAGIC = new Uint8Array([0x00, 0x4f, 0x70, 0x65, 0x6e, 0x54, 0x69, 0x6d, 0x65, 0x73, 0x74, 0x61, 0x6d, 0x70, 0x73, 0x00, 0x00, 0x50, 0x72, 0x6f, 0x6f, 0x66, 0x00, 0xbf, 0x89, 0xe2, 0xe8, 0x84, 0xe8, 0x92, 0x94]);
const TAG_PENDING = '83dfe30d2ef90c8e';
const TAG_BITCOIN = '0588960d73d71901';
// Calendari pubblici ammessi (si contatta solo questo elenco, mai un indirizzo scritto nel file)
export const CALENDARI_AMMESSI = [
  'https://alice.btc.calendar.opentimestamps.org', 'https://bob.btc.calendar.opentimestamps.org',
  'https://finney.calendar.eternitywall.com', 'https://btc.calendar.catallaxy.com',
  'https://a.pool.opentimestamps.org', 'https://b.pool.opentimestamps.org',
];
export const CALENDARI_INVIO = ['https://a.pool.opentimestamps.org', 'https://b.pool.opentimestamps.org'];

const hex = (b) => [...b].map((x) => x.toString(16).padStart(2, '0')).join('');
const unhex = (s) => new Uint8Array(s.match(/../g).map((x) => parseInt(x, 16)));
const cat = (...a) => { const n = a.reduce((s, x) => s + x.length, 0); const o = new Uint8Array(n); let i = 0; for (const x of a) { o.set(x, i); i += x.length; } return o; };
const sha256 = async (b) => new Uint8Array(await crypto.subtle.digest('SHA-256', b));
const uguali = (a, b) => a.length === b.length && a.every((x, i) => x === b[i]);

class Lettore {
  constructor(b) { this.b = b; this.i = 0; }
  byte() { if (this.i >= this.b.length) throw new Error('file .ots troncato'); return this.b[this.i++]; }
  bytes(n) { if (this.i + n > this.b.length) throw new Error('file .ots troncato'); const o = this.b.slice(this.i, this.i + n); this.i += n; return o; }
  varuint() { let v = 0, sh = 0, b; do { b = this.byte(); v += (b & 0x7f) * 2 ** sh; sh += 7; } while (b & 0x80); return v; }
  varbytes(max = 8192) { const n = this.varuint(); if (n > max) throw new Error('campo troppo lungo'); return this.bytes(n); }
}
const scriviVaruint = (v) => { const o = []; do { let b = v % 128; v = Math.floor(v / 128); if (v > 0) b |= 0x80; o.push(b); } while (v > 0); return new Uint8Array(o); };
const scriviVarbytes = (b) => cat(scriviVaruint(b.length), b);

// Operazioni: 0xf0 append, 0xf1 prepend (con argomento); 0x08 sha256, 0xf2 reverse (senza)
async function applica(op, arg, msg) {
  if (op === 0xf0) return cat(msg, arg);
  if (op === 0xf1) return cat(arg, msg);
  if (op === 0x08) return sha256(msg);
  if (op === 0xf2) return msg.slice().reverse();
  throw new Error('operazione OTS non supportata: 0x' + op.toString(16));
}
const CON_ARG = new Set([0xf0, 0xf1]);

// Nodo: { msg, att: [{tipo,..}], ops: [{op,arg,figlio}] }
async function leggiNodo(L, msg) {
  const nodo = { msg, att: [], ops: [] };
  const uno = async (tag) => {
    if (tag === 0x00) {
      const t = hex(L.bytes(8)); const payload = L.varbytes();
      if (t === TAG_PENDING) { const P = new Lettore(payload); nodo.att.push({ tipo: 'in_attesa', uri: new TextDecoder().decode(P.varbytes(1000)) }); }
      else if (t === TAG_BITCOIN) { const P = new Lettore(payload); nodo.att.push({ tipo: 'bitcoin', altezza: P.varuint() }); }
      else nodo.att.push({ tipo: 'altro', tag: t, payload });
    } else {
      const arg = CON_ARG.has(tag) ? L.varbytes(4096) : null;
      const m2 = await applica(tag, arg, msg);
      nodo.ops.push({ op: tag, arg, figlio: await leggiNodo(L, m2) });
    }
  };
  let tag = L.byte();
  while (tag === 0xff) { await uno(L.byte()); tag = L.byte(); }
  await uno(tag);
  return nodo;
}
function scriviNodo(n) {
  const pezzi = [];
  for (const a of n.att) {
    let tag, payload;
    if (a.tipo === 'in_attesa') { tag = unhex(TAG_PENDING); payload = scriviVarbytes(new TextEncoder().encode(a.uri)); }
    else if (a.tipo === 'bitcoin') { tag = unhex(TAG_BITCOIN); payload = scriviVaruint(a.altezza); }
    else { tag = unhex(a.tag); payload = a.payload; }
    pezzi.push(cat(new Uint8Array([0x00]), tag, scriviVarbytes(payload)));
  }
  for (const o of n.ops) pezzi.push(cat(new Uint8Array([o.op]), o.arg ? scriviVarbytes(o.arg) : new Uint8Array(0), scriviNodo(o.figlio)));
  if (!pezzi.length) throw new Error('nodo vuoto');
  return cat(...pezzi.map((p, i) => (i < pezzi.length - 1 ? cat(new Uint8Array([0xff]), p) : p)));
}

/** Legge un file .ots. Controlla che riguardi esattamente l'impronta attesa (se data). */
export async function leggiOts(bytes, improntaAttesa) {
  const L = new Lettore(bytes);
  if (!uguali(L.bytes(MAGIC.length), MAGIC)) throw new Error('non è un file OpenTimestamps');
  if (L.varuint() !== 1) throw new Error('versione .ots non supportata');
  if (L.byte() !== 0x08) throw new Error('il file .ots non usa SHA-256');
  const digest = L.bytes(32);
  if (improntaAttesa && !uguali(digest, improntaAttesa)) throw new Error('la prova .ots riguarda un\'altra impronta');
  const radice = await leggiNodo(L, digest);
  if (L.i !== bytes.length) throw new Error('dati in più in fondo al file .ots');
  return { digest, radice };
}
export function scriviOts(p) { return cat(MAGIC, new Uint8Array([0x01, 0x08]), p.digest, scriviNodo(p.radice)); }

function visita(n, f) { f(n); for (const o of n.ops) visita(o.figlio, f); }
export function attestazioni(p) { const out = []; visita(p.radice, (n) => n.att.forEach((a) => out.push({ ...a, msg: n.msg }))); return out; }

/** Chiede ai calendari il completamento delle parti "in attesa". Restituisce quante ne ha completate. */
export async function completaOts(p, fetchFn = fetch) {
  let completate = 0; const nodi = [];
  visita(p.radice, (n) => { if (n.att.some((a) => a.tipo === 'in_attesa')) nodi.push(n); });
  for (const n of nodi) {
    for (const a of n.att.filter((x) => x.tipo === 'in_attesa')) {
      const uri = a.uri.replace(/\/+$/, '');
      if (!CALENDARI_AMMESSI.includes(uri)) continue;
      try {
        const r = await fetchFn(`${uri}/timestamp/${hex(n.msg)}`, { headers: { Accept: 'application/vnd.opentimestamps.v1' }, signal: AbortSignal.timeout(20000) });
        if (r.status !== 200) continue;
        const sub = await leggiNodo(new Lettore(new Uint8Array(await r.arrayBuffer())), n.msg);
        let haBtc = false; visita(sub, (x) => { if (x.att.some((y) => y.tipo === 'bitcoin')) haBtc = true; });
        if (!haBtc) continue;
        n.ops.push(...sub.ops); n.att.push(...sub.att.filter((y) => y.tipo !== 'in_attesa'));
        n.att = n.att.filter((y) => y !== a);
        completate++;
      } catch (_e) { /* calendario non raggiungibile: si riprova al prossimo controllo */ }
    }
  }
  return completate;
}

/** Invia un'impronta a più calendari e unisce le ricevute provvisorie in un solo file .ots */
export async function nuovaOts(digest, fetchFn = fetch, calendari = CALENDARI_INVIO) {
  const radice = { msg: digest, att: [], ops: [] }; const usati = [];
  for (const cal of calendari) {
    try {
      const r = await fetchFn(`${cal}/digest`, { method: 'POST', headers: { Accept: 'application/vnd.opentimestamps.v1', 'Content-Type': 'application/x-www-form-urlencoded' }, body: digest, signal: AbortSignal.timeout(15000) });
      if (!r.ok) continue;
      const sub = await leggiNodo(new Lettore(new Uint8Array(await r.arrayBuffer())), digest);
      radice.ops.push(...sub.ops); radice.att.push(...sub.att); usati.push(cal);
    } catch (_e) { /* calendario non raggiungibile */ }
  }
  if (!usati.length) return null;
  return { bytes: scriviOts({ digest, radice }), calendari: usati };
}

/**
 * Archivi pubblici della blockchain Bitcoin, indipendenti tra loro. Per ogni blocco se ne
 * interrogano in ordine finché DUE concordano (stesso blocco, stessa radice di Merkle);
 * se uno raggiunto dice una cosa diversa è un'anomalia.
 */
export const ARCHIVI_BITCOIN = [
  { nome: 'mempool.space', blocco: async (f, h) => {
      const x = await (await ok(f(`https://mempool.space/api/block-height/${h}`))).text();
      const b = await (await ok(f(`https://mempool.space/api/block/${x.trim()}`))).json();
      return { hash: x.trim(), merkle: b.merkle_root, ora: b.timestamp }; } },
  { nome: 'blockcypher.com', blocco: async (f, h) => {
      const b = await (await ok(f(`https://api.blockcypher.com/v1/btc/main/blocks/${h}?txstart=0&limit=1`))).json();
      return { hash: b.hash, merkle: b.mrkl_root, ora: Math.floor(Date.parse(b.time) / 1000) }; } },
  { nome: 'blockstream.info', blocco: async (f, h) => {
      const x = await (await ok(f(`https://blockstream.info/api/block-height/${h}`))).text();
      const b = await (await ok(f(`https://blockstream.info/api/block/${x.trim()}`))).json();
      return { hash: x.trim(), merkle: b.merkle_root, ora: b.timestamp }; } },
  { nome: 'blockchain.info', blocco: async (f, h) => {
      const j = await (await ok(f(`https://blockchain.info/block-height/${h}?format=json`))).json();
      const b = (j.blocks || []).find((x) => x.main_chain !== false) || (j.blocks || [])[0];
      return { hash: b.hash, merkle: b.mrkl_root, ora: b.time }; } },
];
// blocchi già letti in questa esecuzione (un blocco Bitcoin non cambia: nessun rischio)
const CACHE_BLOCCHI = new Map();
async function ok(p) { const r = await p; if (!r.ok) { await r.body?.cancel(); throw new Error('HTTP ' + r.status); } return r; }

/**
 * Verifica le attestazioni Bitcoin: la radice di Merkle ricalcolata dalla prova deve essere
 * quella del blocco, confermata da almeno DUE archivi pubblici indipendenti e concordi.
 */
export async function verificaBitcoin(p, fetchFn = fetch, archivi = ARCHIVI_BITCOIN) {
  const btc = attestazioni(p).filter((a) => a.tipo === 'bitcoin');
  if (!btc.length) return { ok: false, stato: 'in_attesa', motivo: 'prova non ancora registrata su Bitcoin' };
  const f = (u) => fetchFn(u, { signal: AbortSignal.timeout(8000), headers: { Accept: 'application/json' } });
  const esiti = [];
  for (const a of btc) {
    const attesa = hex(a.msg.slice().reverse());
    const viste = [];
    for (const arc of archivi) {
      if (viste.filter((v) => !v.errore).length >= 2) break;
      // un archivio lento o che limita le richieste si salta: ce ne sono altri (4 in tutto)
      const chiave = arc.nome + ':' + a.altezza;
      let v = CACHE_BLOCCHI.get(chiave);
      if (!v) {
        try { const b = await arc.blocco(f, a.altezza); if (!/^[0-9a-f]{64}$/.test(b.hash || '') || !/^[0-9a-f]{64}$/.test(b.merkle || '')) throw new Error('risposta non valida'); v = { archivio: arc.nome, hash_blocco: b.hash, merkle: b.merkle, ora: new Date(b.ora * 1000).toISOString() }; CACHE_BLOCCHI.set(chiave, v); }
        catch (e) { v = { archivio: arc.nome, errore: String((e && e.message) || e).slice(0, 80) }; }
      }
      viste.push(v);
    }
    const raggiunti = viste.filter((v) => !v.errore);
    if (raggiunti.some((v) => v.merkle !== attesa || v.hash_blocco !== raggiunti[0].hash_blocco)) {
      esiti.push({ altezza: a.altezza, ok: false, motivo: 'la prova non corrisponde al blocco Bitcoin', viste }); continue;
    }
    if (raggiunti.length < 2) { esiti.push({ altezza: a.altezza, ok: null, motivo: 'archivi Bitcoin non raggiungibili', viste }); continue; }
    esiti.push({ altezza: a.altezza, ok: true, ora_blocco: raggiunti[0].ora, hash_blocco: raggiunti[0].hash_blocco, archivi: raggiunti.map((v) => v.archivio) });
  }
  const buoni = esiti.filter((e) => e.ok === true);
  if (esiti.some((e) => e.ok === false)) return { ok: false, stato: 'anomalia', motivo: 'la prova non corrisponde al blocco Bitcoin', esiti };
  if (buoni.length) return { ok: true, stato: 'ok', blocco: buoni[0].altezza, ora_blocco: buoni[0].ora_blocco, hash_blocco: buoni[0].hash_blocco, archivi: buoni[0].archivi, esiti };
  return { ok: false, stato: 'non_verificabile', motivo: 'archivi Bitcoin non raggiungibili', esiti };
}
