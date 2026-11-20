// Promemoria mensile degli estratti da importare (20/09).
// Guarda l'archivio degli import (estratti_archivio) e avvisa su Telegram
// quando manca l'estratto conto, la carta o gli incassi POS di un mese.
// Cron: il 3 di ogni mese. {prova:true} restituisce solo il testo.
//
// MODIFICA 06/10/2026: prima bastava la chiave pubblica (anon), scritta nelle
// pagine dell'app: chiunque poteva leggere quali estratti mancano o mandare
// messaggi Telegram a ripetizione. Ora risponde solo al pianificatore del
// database (intestazione x-sistema-secret = app_segreti 'sistema_secret') o a
// una persona con permesso di modifica su Fatture (ceraldi_puo('fatture',
// true), controllato col token della persona). In più, protezione
// anti-raffica come nel riepilogo settimanale: se un messaggio è partito
// meno di 10 minuti fa non se ne manda un altro (l'ora dell'ultimo invio sta
// in ceraldi_stato_condiviso, riga 'estratti_promemoria_ultimo').
//
// MODIFICA 21/11/2026 (Fatture v10.47.0):
// - i conti non sono più scritti qui: vengono dall'elenco di Fatture →
//   Impostazioni → Conti e incassi (ceraldi_stato_condiviso, riga
//   'fatture_conti'). I mesi mancanti si contano solo nelle date in cui il
//   conto era in uso (Numia: fino al 14/09/2026) e mai per un conto i cui
//   movimenti arrivano da soli. Stessa regola di _esMancanti nell'app.
// - il token del bot sta in app_segreti ('tg_token_riepilogo'), non più nel codice.
//   Il sorgente è in funzioni/estratti-promemoria/index.ts del repository.
import { createClient } from 'jsr:@supabase/supabase-js@2';
const SB_URL = Deno.env.get('SUPABASE_URL')!;
const SB_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
const ANON = Deno.env.get('SUPABASE_ANON_KEY')!;
const KEY_ULTIMO = 'estratti_promemoria_ultimo';
const CHAT_DEFAULT = '5441779658';
const H = { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}`, 'Content-Type': 'application/json' };
const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
};
type Conto = { archivio: string; nome: string; tipo: string; arrivo: string; dal: string; al: string };
// Usati solo finché in Fatture non è mai stato salvato l'elenco dei conti (come CONTI_BASE nell'app).
const CONTI_BASE: Conto[] = [
  { archivio: 'banca', nome: 'Banco BPM', tipo: 'conto', arrivo: 'estratto', dal: '', al: '' },
  { archivio: 'sumup', nome: 'SumUp', tipo: 'pos', arrivo: 'estratto', dal: '2026-08-01', al: '' },
  { archivio: 'carta', nome: 'Carta Nexi', tipo: 'carta', arrivo: 'estratto', dal: '', al: '' },
  { archivio: 'numia', nome: 'Numia', tipo: 'pos', arrivo: 'estratto', dal: '', al: '2026-09-14' },
];
function nomeEstratto(c: Conto): string {
  if (c.tipo === 'carta') return 'Estratto ' + (/^carta\b/i.test(c.nome) ? 'carta' + c.nome.slice(5) : 'carta ' + c.nome);
  if (c.tipo === 'pos') return 'Incassi ' + c.nome;
  if (c.tipo === 'online') return 'Movimenti ' + c.nome;
  return 'Estratto conto ' + c.nome;
}
const data10 = (s: unknown) => { const x = String(s || '').slice(0, 10); return /^\d{4}-\d{2}-\d{2}$/.test(x) ? x : ''; };
async function leggiConti(): Promise<Conto[]> {
  const r = await fetch(`${SB_URL}/rest/v1/ceraldi_stato_condiviso?id=eq.fatture_conti&select=data`, { headers: H });
  const j = await r.json().catch(() => []);
  const L = Array.isArray(j) && j[0] && j[0].data && Array.isArray(j[0].data.conti) && j[0].data.conti.length ? j[0].data.conti : null;
  if (!L) return CONTI_BASE;
  return L.filter((c: any) => c && c.archivio).map((c: any) => ({
    archivio: String(c.archivio), nome: String(c.nome || c.id || ''), tipo: String(c.tipo || 'conto'),
    arrivo: c.arrivo === 'automatico' ? 'automatico' : 'estratto', dal: data10(c.dal), al: data10(c.al),
  }));
}
// Chi può chiamarla: il pianificatore (chiave di sistema) o una persona che
// può modificare Fatture. Risponde 'ok', 'anonimo' (nessun account) o 'vietato'.
async function autorizzato(req: Request): Promise<'ok' | 'anonimo' | 'vietato'> {
  const db = createClient(SB_URL, SB_KEY);
  const { data } = await db.from('app_segreti').select('valore').eq('chiave', 'sistema_secret').maybeSingle();
  const sis = req.headers.get('x-sistema-secret');
  if (data && data.valore && sis && sis === data.valore) return 'ok';
  const auth = req.headers.get('Authorization') || '';
  const tok = auth.replace(/^Bearer\s+/i, '');
  if (!tok) return 'anonimo';
  const asUser = createClient(SB_URL, ANON, { global: { headers: { Authorization: auth } } });
  const { data: { user } } = await asUser.auth.getUser(tok);
  if (!user) return 'anonimo';
  const { data: ok } = await asUser.rpc('ceraldi_puo', { p_app: 'fatture', p_scrittura: true });
  return ok === true ? 'ok' : 'vietato';
}
// Token del bot: segreto del server TG_TOKEN_RIEPILOGO se c'è, altrimenti app_segreti.
async function tokenBot(): Promise<string> {
  const env = Deno.env.get('TG_TOKEN_RIEPILOGO');
  if (env) return env;
  const db = createClient(SB_URL, SB_KEY);
  const { data } = await db.from('app_segreti').select('valore').eq('chiave', 'tg_token_riepilogo').maybeSingle();
  return (data && data.valore) || '';
}
// Stato dell'ultimo invio (stesso schema di fatture_riepilogo_cfg, riga separata)
async function leggiUltimo(): Promise<any> {
  const r = await fetch(`${SB_URL}/rest/v1/ceraldi_stato_condiviso?id=eq.${KEY_ULTIMO}&select=data`, { headers: H });
  const j = await r.json().catch(() => []);
  return (Array.isArray(j) && j[0] && j[0].data) || {};
}
async function salvaUltimo(stato: any) {
  await fetch(`${SB_URL}/rest/v1/ceraldi_stato_condiviso?on_conflict=id`, {
    method: 'POST', headers: { ...H, Prefer: 'resolution=merge-duplicates,return=minimal' },
    body: JSON.stringify({ id: KEY_ULTIMO, data: stato, updated_at: new Date().toISOString() }),
  });
}
const MESI = ['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre'];
function meseEt(ym: string): string {
  const p = String(ym).split('-');
  return (MESI[parseInt(p[1], 10) - 1] || '') + ' ' + p[0];
}
function mesiTra(da: string, a: string): string[] {
  const out: string[] = [];
  const d = new Date(da + '-01T12:00:00Z'), fine = new Date(a + '-01T12:00:00Z');
  while (d <= fine) { out.push(d.toISOString().slice(0, 7)); d.setUTCMonth(d.getUTCMonth() + 1); }
  return out;
}
function mesePrecedente(): string {
  const d = new Date();
  d.setUTCDate(1); d.setUTCMonth(d.getUTCMonth() - 1);
  return d.toISOString().slice(0, 7);
}
// Mesi mancanti di un conto: dal primo mese in archivio (o dal primo giorno d'uso, se dopo)
// al mese scorso (o all'ultimo giorno d'uso, se prima). Niente per i movimenti automatici.
export function mancantiDi(c: Conto, righe: any[], prec: string): string[] {
  if (c.arrivo === 'automatico') return [];
  const mie = righe.filter((x: any) => x.tipo === c.archivio);
  if (!mie.length) return [];
  const coperti = new Set<string>();
  mie.forEach((x: any) => {
    const da = String(x.periodo_da || x.periodo_a || '').slice(0, 7);
    const a = String(x.periodo_a || x.periodo_da || '').slice(0, 7);
    if (da && a) mesiTra(da, a).forEach((m) => coperti.add(m));
  });
  const ordinati = Array.from(coperti).sort();
  if (!ordinati.length) return [];
  let inizio = ordinati[0], fine = prec;
  if (c.dal && c.dal.slice(0, 7) > inizio) inizio = c.dal.slice(0, 7);
  if (c.al && c.al.slice(0, 7) < fine) fine = c.al.slice(0, 7);
  if (inizio > fine) return [];
  return mesiTra(inizio, fine).filter((m) => !coperti.has(m));
}
async function componi(): Promise<{ testo: string; mancanti: number }> {
  const r = await fetch(`${SB_URL}/rest/v1/estratti_archivio?select=tipo,periodo_da,periodo_a`, { headers: H });
  const righe = await r.json().catch(() => []);
  const conti = await leggiConti();
  const prec = mesePrecedente();
  const blocchi: string[] = [];
  let mancanti = 0;
  for (const c of conti) {
    const manc = mancantiDi(c, Array.isArray(righe) ? righe : [], prec);
    if (manc.length) {
      mancanti += manc.length;
      blocchi.push(`• <b>${nomeEstratto(c)}</b>: ${manc.map(meseEt).join(', ')}`);
    }
  }
  if (!mancanti) {
    return { testo: `\u{1F4DA} <b>Estratti</b>\n\nTutto in regola: non manca nessun estratto fino a ${meseEt(prec)}.`, mancanti: 0 };
  }
  const testo = `\u{1F4DA} <b>Estratti da importare</b>\n\n` + blocchi.join('\n') +
    `\n\nSi caricano in Fatture → Fiscale → Importazioni. Il file originale resta conservato nell'archivio.`;
  return { testo, mancanti };
}
Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: CORS });
  const J = (o: unknown, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { ...CORS, 'Content-Type': 'application/json' } });
  try {
    const acc = await autorizzato(req);
    if (acc === 'anonimo') return J({ errore: 'Accedi con il tuo account' }, 401);
    if (acc === 'vietato') return J({ errore: 'Questo account non ha il permesso di modifica su Fatture' }, 403);
  } catch (e) {
    return J({ errore: 'Controllo accesso non riuscito: ' + String((e as any)?.message || e) }, 500);
  }
  let body: any = {};
  try { body = await req.json(); } catch (_) { /* vuoto */ }
  try {
    const { testo, mancanti } = await componi();
    if (body.prova) return J({ inviato: false, testo, mancanti });
    if (!mancanti && body.auto) return J({ inviato: false, motivo: 'niente da segnalare' });
    // Protezione anti-raffica: al massimo un invio ogni 10 minuti
    const ultimo = await leggiUltimo();
    if (ultimo.ultimo_invio && Date.now() - new Date(ultimo.ultimo_invio).getTime() < 10 * 60 * 1000) {
      return J({ inviato: false, motivo: 'inviato da poco', mancanti, testo });
    }
    const TG_TOKEN = await tokenBot();
    if (!TG_TOKEN) return J({ inviato: false, errore: 'Token del bot mancante in app_segreti (tg_token_riepilogo)' }, 500);
    const cr = await fetch(`${SB_URL}/rest/v1/ceraldi_stato_condiviso?id=eq.fatture_riepilogo_cfg&select=data`, { headers: H });
    const cj = await cr.json().catch(() => []);
    const chat = (Array.isArray(cj) && cj[0] && cj[0].data && cj[0].data.chat_id) || CHAT_DEFAULT;
    const tg = await fetch(`https://api.telegram.org/bot${TG_TOKEN}/sendMessage`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chat, text: testo, parse_mode: 'HTML', disable_web_page_preview: true }),
    });
    const tj = await tg.json().catch(() => ({}));
    await salvaUltimo({ ultimo_invio: new Date().toISOString(), ultimo_esito: tj.ok ? 'ok' : (tj.description || 'errore'), ultimo_auto: !!body.auto });
    return J({ inviato: !!tj.ok, mancanti, testo, errore: tj.ok ? undefined : (tj.description || 'Telegram non ha accettato il messaggio') });
  } catch (e) {
    return J({ errore: String((e as any)?.message || e) }, 500);
  }
});
