// FATTURE-RIEPILOGO — logica del servizio (riepilogo Telegram del lunedì e avvisi di pagamento del mattino).
// Generato dal sorgente TypeScript della funzione; il punto d'ingresso sul server la importa da un COMMIT FISSATO
// e le passa createClient e il token del bot (che non stanno mai nel repo pubblico).
// 21/10/2026: da pagare e scadute contano solo le fatture dalla data scelta in app (contiDal, di base 01/01/2026).
const G = globalThis.__ceraldiRiepilogo || {};
const createClient = G.createClient;
import { scR2, scScadenze, scPiuGiorni, scAvvisiDelGiorno, scFraseAvviso, scPagabile, scStato } from "./scadenze.mjs";
import { rcoTok, rcoCalcola, rcoProponi, rcoAvvisi, rcoFrase } from "./ricorrenze.mjs";
const SB_URL = Deno.env.get("SUPABASE_URL");
const SB_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
const ANON = Deno.env.get("SUPABASE_ANON_KEY");
const TG_TOKEN = Deno.env.get("TG_TOKEN_RIEPILOGO") ?? G.TG;
const CHAT_DEFAULT = "5441779658";
const KEY = "fatture_riepilogo_cfg";
const LINK_APP = "https://valerioceraldi-hub.github.io/Ceraldi/Primanota.html#scadenze";
const LINK_RIC = "https://valerioceraldi-hub.github.io/Ceraldi/Primanota.html#ricorrenti";
const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS"
};
const H = { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}`, "Content-Type": "application/json" };
async function segretoSistema() {
  const db = createClient(SB_URL, SB_KEY);
  const { data } = await db.from("app_segreti").select("valore").eq("chiave", "sistema_secret").maybeSingle();
  return data && data.valore || "";
}
async function autorizzato(req) {
  const sisDb = await segretoSistema();
  const sis = req.headers.get("x-sistema-secret");
  if (sisDb && sis && sis === sisDb) return "ok";
  const auth = req.headers.get("Authorization") || "";
  const tok = auth.replace(/^Bearer\s+/i, "");
  if (!tok) return "anonimo";
  const asUser = createClient(SB_URL, ANON, { global: { headers: { Authorization: auth } } });
  const { data: { user } } = await asUser.auth.getUser(tok);
  if (!user) return "anonimo";
  const { data: ok } = await asUser.rpc("ceraldi_puo", { p_app: "fatture", p_scrittura: true });
  return ok === true ? "ok" : "vietato";
}
function oggiRoma() {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/Rome" }).format(/* @__PURE__ */ new Date());
}
function eur(n) {
  return "\u20AC " + n.toLocaleString("it-IT", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
function gg(iso) {
  const d = /* @__PURE__ */ new Date(iso + "T12:00:00Z");
  return d.toLocaleDateString("it-IT", { weekday: "short", day: "numeric", month: "short", timeZone: "UTC" });
}
function esc(s) {
  return String(s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
async function leggiCfg() {
  const r = await fetch(`${SB_URL}/rest/v1/ceraldi_stato_condiviso?id=eq.${KEY}&select=data`, { headers: H });
  const j = await r.json().catch(() => []);
  return Array.isArray(j) && j[0] && j[0].data || {};
}
async function salvaCfg(cfg) {
  await fetch(`${SB_URL}/rest/v1/ceraldi_stato_condiviso?on_conflict=id`, {
    method: "POST",
    headers: { ...H, Prefer: "resolution=merge-duplicates,return=minimal" },
    body: JSON.stringify({ id: KEY, data: cfg, updated_at: (/* @__PURE__ */ new Date()).toISOString() })
  });
}
async function caricaAperte() {
  const col = "id,tipo,fornitore,numero,importo,parz_pagato,scadenza,stato,rate,pagamento,assegno,avviso_giorni,note";
  const cfgD = await leggiCfg().catch(() => ({}));
  const dal = /^\d{4}-\d{2}-\d{2}$/.test(cfgD.contiDal || "") ? cfgD.contiDal : "2026-01-01";
  const r1 = await fetch(`${SB_URL}/rest/v1/fatture?select=${col}&deleted_at=is.null&stato=in.(da_pagare,parziale)&tipo=not.in.(nota_credito,ddt)&data=gte.${dal}&limit=3000`, { headers: H });
  const aperte = await r1.json();
  const r2 = await fetch(`${SB_URL}/rest/v1/fatture?select=id,tipo,importo,note&deleted_at=is.null&tipo=eq.nota_credito&note=like.*NC*&limit=3000`, { headers: H });
  const nc = await r2.json();
  if (!Array.isArray(aperte)) throw new Error("lettura fatture non riuscita");
  return aperte.concat(Array.isArray(nc) ? nc : []);
}
function pasqua(a) {
  const b = a % 19, c = Math.floor(a / 100), d = a % 100, e = Math.floor(c / 4), f = c % 4, g = Math.floor((c + 8) / 25), h = Math.floor((c - g + 1) / 3), i = (19 * b + c - e - h + 15) % 30, k = Math.floor(d / 4), l = d % 4, m = (32 + 2 * f + 2 * k - i - l) % 7, n = Math.floor((b + 11 * m + 22 * i) / 451), mese = Math.floor((i + m - 7 * n + 114) / 31), giorno = (i + m - 7 * n + 114) % 31 + 1;
  return new Date(Date.UTC(a, mese - 1, giorno, 12));
}
function festivo(d) {
  const md = d.getUTCMonth() + 1 + "-" + d.getUTCDate();
  if (["1-1", "1-6", "4-25", "5-1", "6-2", "8-15", "11-1", "12-8", "12-25", "12-26"].includes(md)) return true;
  const p = pasqua(d.getUTCFullYear());
  p.setUTCDate(p.getUTCDate() + 1);
  return d.getUTCMonth() === p.getUTCMonth() && d.getUTCDate() === p.getUTCDate();
}
function lavorativo(d) {
  const x = new Date(d);
  while (x.getUTCDay() === 0 || x.getUTCDay() === 6 || festivo(x)) x.setUTCDate(x.getUTCDate() + 1);
  return x;
}
function scadenzeFiscali(oggiIso, giorni) {
  const oggi = /* @__PURE__ */ new Date(oggiIso + "T12:00:00Z"), fine = new Date(oggi);
  fine.setUTCDate(fine.getUTCDate() + giorni);
  const out = [];
  const nomeMese = (a, m) => new Date(Date.UTC(a, m, 15)).toLocaleDateString("it-IT", { month: "long", timeZone: "UTC" });
  for (let a = oggi.getUTCFullYear() - 1; a <= fine.getUTCFullYear(); a++) {
    for (let m = 0; m < 12; m++) {
      const p = new Date(Date.UTC(a, m - 1, 15));
      out.push({ d: lavorativo(new Date(Date.UTC(a, m, m === 7 ? 20 : 16, 12))), t: `F24 (IVA di ${nomeMese(p.getUTCFullYear(), p.getUTCMonth())}, ritenute, contributi)` });
      out.push({ d: new Date(Date.UTC(a, m, 5, 12)), t: `Pacchetto di ${nomeMese(p.getUTCFullYear(), p.getUTCMonth())} al commercialista (promemoria)` });
    }
    out.push({ d: lavorativo(new Date(Date.UTC(a, 4, 31, 12))), t: "LIPE 1\xB0 trimestre" });
    out.push({ d: lavorativo(new Date(Date.UTC(a, 8, 30, 12))), t: "LIPE 2\xB0 trimestre" });
    out.push({ d: lavorativo(new Date(Date.UTC(a, 10, 30, 12))), t: "LIPE 3\xB0 trimestre" });
    out.push({ d: lavorativo(new Date(Date.UTC(a, 2, 0, 12))), t: `LIPE 4\xB0 trimestre ${a - 1}` });
    out.push({ d: lavorativo(new Date(Date.UTC(a, 3, 30, 12))), t: `Dichiarazione IVA ${a - 1}` });
    out.push({ d: lavorativo(new Date(Date.UTC(a, 11, 27, 12))), t: "Acconto IVA" });
  }
  return out.filter((x) => x.d >= oggi && x.d <= fine).sort((x, y) => +x.d - +y.d);
}
function vociAperte(tutte) {
  const out = [];
  tutte.forEach((f) => {
    if (!scPagabile(f) || scStato(f) === "pagata") return;
    scScadenze(f, tutte).forEach((s) => {
      if (!s.pagata) out.push({ f, s });
    });
  });
  return out.sort((a, b) => a.s.data.localeCompare(b.s.data));
}
async function componi() {
  const oggi = oggiRoma();
  const tra7 = scPiuGiorni(oggi, 7), tra14 = scPiuGiorni(oggi, 14), meno30 = scPiuGiorni(oggi, -30);
  const tutte = await caricaAperte();
  const voci = vociAperte(tutte);
  const ra = await fetch(`${SB_URL}/rest/v1/ceraldi_stato_condiviso?id=eq.fatture_bonifica_davvero_aperte&select=data`, { headers: H });
  const ja = await ra.json().catch(() => []);
  const aperteOk = Array.isArray(ja) && ja[0] && ja[0].data && ja[0].data.ids || {};
  const scaduteRecenti = voci.filter((v) => v.s.data < oggi && v.s.data >= meno30);
  const vecchieTutte = voci.filter((v) => v.s.data < meno30);
  const vecchieVere = vecchieTutte.filter((v) => aperteOk[String(v.f.id)]);
  const scaduteVecchie = vecchieTutte.filter((v) => !aperteOk[String(v.f.id)]);
  const settimana = voci.filter((v) => v.s.data >= oggi && v.s.data < tra7);
  const prossima = voci.filter((v) => v.s.data >= tra7 && v.s.data <= tra14);
  const tot = (a) => a.reduce((s, v) => s + v.s.residuo, 0);
  const riga = (v) => `\u2022 ${gg(v.s.data)} \u2014 <b>${esc(v.f.fornitore)}</b> ${eur(v.s.residuo)}` + (v.s.tot > 1 ? v.s.saldo ? " (saldo)" : ` (rata ${v.s.n} di ${v.s.tot})` : v.f.stato === "parziale" ? " (residuo)" : "") + (v.s.metodo === "assegno" ? " \xB7 assegno" + (v.s.assegno ? " n\xB0 " + esc(v.s.assegno) : "") : "");
  let t = `\u2615\uFE0F <b>Fatture Ceraldi \u2014 la settimana</b>
`;
  t += `<i>${(/* @__PURE__ */ new Date(oggi + "T12:00:00Z")).toLocaleDateString("it-IT", { weekday: "long", day: "numeric", month: "long", timeZone: "UTC" })}</i>

`;
  if (settimana.length) {
    t += `\u{1F4C5} <b>Da pagare entro 7 giorni: ${eur(tot(settimana))}</b> (${settimana.length})
`;
    settimana.slice(0, 12).forEach((v) => t += riga(v) + "\n");
    if (settimana.length > 12) t += `\u2026e altre ${settimana.length - 12}
`;
  } else {
    t += `\u{1F4C5} Nessun pagamento in scadenza nei prossimi 7 giorni.
`;
  }
  if (scaduteRecenti.length) {
    t += `
\u26A0\uFE0F <b>Scadute nell'ultimo mese: ${eur(tot(scaduteRecenti))}</b> (${scaduteRecenti.length})
`;
    scaduteRecenti.slice(0, 8).forEach((v) => t += riga(v) + "\n");
    if (scaduteRecenti.length > 8) t += `\u2026e altre ${scaduteRecenti.length - 8}
`;
  }
  if (prossima.length) t += `
\u{1F52D} Settimana dopo: ${eur(tot(prossima))} (${prossima.length} ${prossima.length === 1 ? "pagamento" : "pagamenti"})
`;
  if (vecchieVere.length) t += `
\u23F3 Scadute da tempo e ancora da pagare: ${eur(tot(vecchieVere))} (${vecchieVere.length})
`;
  const fisc = scadenzeFiscali(oggi, 14);
  if (fisc.length) {
    t += `
\u{1F3DB}\uFE0F <b>Scadenze fiscali</b>
`;
    fisc.forEach((x) => t += `\u2022 ${x.d.toLocaleDateString("it-IT", { weekday: "short", day: "numeric", month: "short", timeZone: "UTC" })} \u2014 ${x.t}
`);
  }
  try {
    const R = await statoRicorrenti(oggi);
    if (R) {
      const sett = [];
      R.voci.forEach((v) => {
        if (v.stato !== "attiva" || v.dir !== "uscita") return;
        (R.calc.periodi[v.id] || []).forEach((p) => {
          if (p.data >= oggi && p.data < tra7 && (p.stato === "previsto" || p.stato === "in_attesa")) sett.push({ v, p });
        });
      });
      if (sett.length) {
        sett.sort((a, b) => a.p.data.localeCompare(b.p.data));
        t += `
\u{1F501} <b>Uscite ricorrenti della settimana: ${eur(sett.reduce((s, x) => s + x.p.atteso, 0))}</b>
`;
        sett.slice(0, 10).forEach((x) => t += `\u2022 ${gg(x.p.data)} \u2014 ${esc(x.v.nome)} ${x.v.variabile || x.p.stima && !x.p.stima.certo ? "circa " : ""}${eur(x.p.atteso)}
`);
      }
    }
  } catch (e) {
    console.error("riepilogo, ricorrenti:", e);
  }
  if (scaduteVecchie.length) t += `
\u{1F9F9} ${scaduteVecchie.length} pagamenti risultano scaduti da pi\xF9 di un mese (${eur(tot(scaduteVecchie))}): probabilmente gi\xE0 fatti, controllali con la pulizia guidata nell'app.
`;
  return {
    testo: t,
    numeri: {
      settimana: settimana.length,
      totSettimana: tot(settimana),
      scaduteRecenti: scaduteRecenti.length,
      totScadute: tot(scaduteRecenti),
      prossima: prossima.length,
      vecchieVere: vecchieVere.length,
      scaduteVecchie: scaduteVecchie.length
    }
  };
}
async function leggiTutto(path) {
  const out = [];
  for (let da = 0; da < 5e4; da += 1e3) {
    const r = await fetch(`${SB_URL}/rest/v1/${path}`, { headers: { ...H, Range: `${da}-${da + 999}`, "Range-Unit": "items" } });
    const j = await r.json().catch(() => []);
    if (!Array.isArray(j)) break;
    out.push(...j);
    if (j.length < 1e3) break;
  }
  return out;
}
async function statoRicorrenti(oggi) {
  const rd = await fetch(`${SB_URL}/rest/v1/ceraldi_stato_condiviso?id=eq.fatture_ricorrenze&select=data`, { headers: H });
  const jd = await rd.json().catch(() => []);
  const doc = Object.assign({ voci: [], esiti: {}, viste: {} }, Array.isArray(jd) && jd[0] && jd[0].data || {});
  const da = scPiuGiorni(oggi, -430), anno = +oggi.slice(0, 4) - 1;
  const [banca, carta, profili, bon, liq, comp, iban] = await Promise.all([
    leggiTutto(`movimenti_banca?select=id,data,importo,descrizione,banca,sottotipo,ignorata&data=gte.${da}&order=data.asc`),
    leggiTutto(`movimenti_carta?select=id,data,importo,descrizione&data=gte.${da}&order=data.asc`).catch(() => []),
    leggiTutto("presenze_profili?select=id,nome,cognome,ruolo,attivo,eliminato,data_fine_rapporto,iban,netto_fisso_mensile"),
    leggiTutto(`presenze_bonifici_stipendio?select=dipendente_id,anno_riferimento,mese_riferimento,importo&anno_riferimento=gte.${anno}`),
    leggiTutto(`presenze_liquidazioni?select=dipendente_id,anno,mese,bonifico&anno=gte.${anno}`),
    leggiTutto(`presenze_compensi_soci?select=dipendente_id,anno,mese,netto&anno=gte.${anno}`),
    leggiTutto("fatture?select=bon_iban&bon_iban=not.is.null&deleted_at=is.null")
  ]);
  const movs = [];
  banca.forEach((m) => {
    if (m && m.id && !m.ignorata) movs.push({ id: m.id, data: String(m.data).slice(0, 10), importo: +m.importo || 0, descrizione: m.descrizione || "", conto: m.banca || "BPM", sottotipo: m.sottotipo || "", cat: "" });
  });
  carta.forEach((m) => {
    if (m && m.id) movs.push({ id: m.id, data: String(m.data).slice(0, 10), importo: -Math.abs(+m.importo || 0), descrizione: m.descrizione || "", conto: "Nexi", sottotipo: "Carta", cat: "" });
  });
  if (!movs.length) return null;
  const cop = {};
  movs.forEach((m) => {
    if (!cop[m.conto] || m.data > cop[m.conto]) cop[m.conto] = m.data;
  });
  const ibanNoti = {};
  const norm = (s) => {
    const x = String(s || "").toUpperCase().replace(/\s+/g, "").match(/IT\d{2}[A-Z]\d{10}[0-9A-Z]{12}/);
    return x ? x[0] : "";
  };
  const P = { dipendenti: [], soci: [], bonifici: {}, liquidazioni: {}, compensi: {} };
  profili.forEach((p) => {
    if (p.eliminato || p.attivo === false) return;
    const nome = ((p.nome || "") + " " + (p.cognome || "")).trim(), tok = rcoTok(nome);
    if (!tok.length) return;
    (p.ruolo === "admin" ? P.soci : P.dipendenti).push({ id: p.id, nome, tok, fine: p.data_fine_rapporto || null, netto: +p.netto_fisso_mensile || 0 });
    const ib = norm(p.iban);
    if (ib) ibanNoti[ib] = 1;
  });
  const mk = (y, m) => y + "-" + String(m).padStart(2, "0");
  bon.forEach((b) => {
    const o = P.bonifici[b.dipendente_id] = P.bonifici[b.dipendente_id] || {}, k = mk(b.anno_riferimento, b.mese_riferimento);
    o[k] = Math.round(((o[k] || 0) + (+b.importo || 0)) * 100) / 100;
  });
  liq.forEach((l) => {
    if (+l.bonifico > 0) (P.liquidazioni[l.dipendente_id] = P.liquidazioni[l.dipendente_id] || {})[mk(l.anno, l.mese)] = +l.bonifico;
  });
  comp.forEach((c) => {
    if (+c.netto > 0) (P.compensi[c.dipendente_id] = P.compensi[c.dipendente_id] || {})[mk(c.anno, c.mese)] = +c.netto;
  });
  iban.forEach((f) => {
    const ib = norm(f.bon_iban);
    if (ib) ibanNoti[ib] = 1;
  });
  const ctx = { presenze: P };
  const voci = (doc.voci || []).map((v) => Object.assign({}, v));
  const calc = rcoCalcola(voci, movs, ctx, { oggi, copertura: cop, esiti: doc.esiti || {}, ibanNoti });
  return { doc, voci, calc, movs, cop, ctx };
}
async function avvisiRicorrenti(oggi, cfg) {
  if (cfg.ricorrenti === false) return [];
  const R = await statoRicorrenti(oggi);
  if (!R) return [];
  const out = rcoAvvisi(R.voci, R.calc, oggi, {}).map((a) => ({
    id: "rco:" + a.v.id,
    tipo: a.tipo,
    data: a.p.data,
    residuo: a.tipo === "prima" && a.v.dir === "uscita" ? a.p.atteso : 0,
    frase: rcoFrase(a, eur),
    chiave: a.chiave,
    ricorrente: true
  }));
  const note = {};
  (R.doc.voci || []).forEach((v) => {
    if (v.chiave) note[v.chiave] = 1;
  });
  Object.keys(R.doc.viste || {}).forEach((k) => {
    const x = R.doc.viste[k];
    if (x && x.fino && x.fino > oggi) note[k] = 1;
  });
  const viste = cfg.rco_nuove_viste || {};
  const ogni = { 1: "ogni mese", 2: "ogni 2 mesi", 3: "ogni 3 mesi", 4: "ogni 4 mesi", 6: "ogni 6 mesi", 12: "ogni anno" };
  rcoProponi(R.movs, R.ctx, { oggi, copertura: R.cop, chiaviNote: note, usati: R.calc.usati }).filter((p) => p.nuova && !p.interrotta && p.fiducia !== "bassa" && !viste[p.chiave]).slice(0, 3).forEach((p) => out.push({
    id: "rco:nuova",
    tipo: "nuova",
    data: p.prossima.data,
    residuo: 0,
    chiave: "rco|nuova|" + p.chiave,
    chiaveNuova: p.chiave,
    ricorrente: true,
    frase: `Si ripete: ${p.nome} \xB7 ${ogni[p.ogni] || ""} intorno al ${p.giorno} \xB7 ${p.variabile ? "circa " : ""}${eur(p.importo)}. Vuoi che te lo ricordi? (Fatture \u2192 Ricorrenti)`
  }));
  return out;
}
function cfgAvvisi(cfg) {
  return Object.assign({ attivo: true, giorni: 3, giorno: true, scaduta: true }, cfg.avvisi || {});
}
function chiaveAvviso(a) {
  return a.f.id + "|" + a.s.data + "|" + a.s.n + "|" + a.tipo;
}
async function avvisi(body, cfg) {
  const A = cfgAvvisi(cfg);
  const oggi = body.oggi && /^\d{4}-\d{2}-\d{2}$/.test(body.oggi) && body.prova ? body.oggi : oggiRoma();
  const tutte = await caricaAperte();
  const lista = scAvvisiDelGiorno(tutte, A, oggi);
  const prossimi = [];
  if (body.prova) {
    for (let i = 0; i <= 14; i++) {
      const g = scPiuGiorni(oggi, i), l = scAvvisiDelGiorno(tutte, A, g);
      if (l.length) prossimi.push({ data: g, voci: l.map((a) => ({ id: a.f.id, tipo: a.tipo, frase: scFraseAvviso(a, eur) })) });
    }
  }
  const voci = lista.map((a) => ({ id: a.f.id, tipo: a.tipo, data: a.s.data, residuo: a.s.residuo, frase: scFraseAvviso(a, eur), chiave: chiaveAvviso(a) }));
  try {
    (await avvisiRicorrenti(oggi, cfg)).forEach((x) => voci.push(x));
  } catch (e) {
    console.error("avvisi ricorrenti:", e);
  }
  if (body.prova) return { inviato: false, attivo: A.attivo, oggi, voci, prossimi };
  if (body.auto && A.attivo === false) return { inviato: false, motivo: "avvisi spenti" };
  const log = Object.assign({}, cfg.avvisi_log || {});
  const nuoveViste = Object.assign({}, cfg.rco_nuove_viste || {});
  const nuove = voci.filter((v) => !log[v.chiave]);
  if (!nuove.length) return { inviato: false, motivo: voci.length ? "gi\xE0 avvisato" : "niente da avvisare", voci };
  const tot = scR2(nuove.reduce((s, v) => s + v.residuo, 0));
  const scad = nuove.filter((v) => v.tipo === "scaduta").length;
  const soloRic = nuove.every((v) => v.ricorrente);
  const titolo = nuove.length === 1 ? nuove[0].tipo === "scaduta" ? "\u26A0\uFE0F Pagamento scaduto" : nuove[0].tipo === "mancato" ? "\u26A0\uFE0F Pagamento ricorrente non arrivato" : nuove[0].tipo === "nuova" ? "\u{1F501} Ho trovato un movimento che si ripete" : nuove[0].tipo === "iban" ? "\u26A0\uFE0F IBAN nuovo" : nuove[0].tipo === "diverso" ? "\u{1F501} Importo diverso dal solito" : "\u{1F4B6} Pagamento in arrivo" : `\u{1F4B6} ${nuove.length} cose da ricordare${tot > 0 ? " \xB7 " + eur(tot) : ""}`;
  const testo = nuove.map((v) => "\u2022 " + v.frase).join("\n") + (scad && nuove.length > 1 ? `
(${scad} non ${scad === 1 ? "risulta pagato" : "risultano pagati"})` : "");
  const sis = await segretoSistema();
  const r = await fetch(`${SB_URL}/functions/v1/notifica`, {
    method: "POST",
    headers: { ...H, "x-sistema-secret": sis },
    body: JSON.stringify({ app: "fatture", tipo: "scadenze", titolo, testo, link: soloRic ? LINK_RIC : LINK_APP, a: "admin", telegram: "presenze_admin", dati: { voci: nuove.map((v) => ({ id: v.id, data: v.data, tipo: v.tipo })) } })
  });
  const esito = await r.json().catch(() => ({}));
  const ok = r.ok && esito && esito.ok !== false;
  if (ok) {
    const limite = scPiuGiorni(oggi, -60);
    Object.keys(log).forEach((k) => {
      if (log[k] < limite) delete log[k];
    });
    nuove.forEach((v) => {
      log[v.chiave] = oggi;
      if (v.chiaveNuova) nuoveViste[v.chiaveNuova] = oggi;
    });
  }
  await salvaCfg({ ...cfg, avvisi_log: log, rco_nuove_viste: nuoveViste, avvisi_ultimo: (/* @__PURE__ */ new Date()).toISOString(), avvisi_esito: ok ? "ok" : String(esito && (esito.error || esito.errore) || r.status) });
  return { inviato: ok, voci: nuove, esito };
}
Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  const J = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { ...CORS, "Content-Type": "application/json" } });
  try {
    const acc = await autorizzato(req);
    if (acc === "anonimo") return J({ errore: "Accedi con il tuo account" }, 401);
    if (acc === "vietato") return J({ errore: "Questo account non ha il permesso di modifica su Fatture" }, 403);
  } catch (e) {
    return J({ errore: "Controllo accesso non riuscito: " + String(e?.message || e) }, 500);
  }
  let body = {};
  try {
    body = await req.json();
  } catch (_) {
  }
  try {
    const cfg = await leggiCfg();
    if (body.avvisi) return J(await avvisi(body, cfg));
    if (body.auto && cfg.attivo === false) return J({ inviato: false, motivo: "disattivato" });
    const { testo, numeri } = await componi();
    if (body.prova) return J({ inviato: false, testo, numeri });
    if (!body.auto && !body.invia) return J({ errore: "azione mancante" }, 400);
    if (cfg.ultimo_invio && Date.now() - new Date(cfg.ultimo_invio).getTime() < 10 * 60 * 1e3) {
      return J({ inviato: false, motivo: "inviato da poco", testo });
    }
    const chat = cfg.chat_id || CHAT_DEFAULT;
    const tg = await fetch(`https://api.telegram.org/bot${TG_TOKEN}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id: chat, text: testo, parse_mode: "HTML", disable_web_page_preview: true })
    });
    const tj = await tg.json().catch(() => ({}));
    const ok = !!tj.ok;
    await salvaCfg({ ...cfg, ultimo_invio: (/* @__PURE__ */ new Date()).toISOString(), ultimo_esito: ok ? "ok" : tj.description || "errore", ultimo_auto: !!body.auto });
    return J({ inviato: ok, errore: ok ? void 0 : tj.description || "Telegram non ha accettato il messaggio", testo });
  } catch (e) {
    return J({ errore: String(e?.message || e) }, 500);
  }
});
