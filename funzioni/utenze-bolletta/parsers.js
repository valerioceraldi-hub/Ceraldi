// ══════════════════════════════════════════════════════════════════════
// LETTORE BOLLETTE — Ceraldi (21/10/2026)
// Legge il TESTO di una bolletta PDF (luce, gas, acqua) e restituisce i dati
// in una forma unica. Regole fisse, nessuna intelligenza artificiale:
//  · ogni numero viene da una riga precisa del PDF, e per ogni campo si
//    restituisce anche quella riga (così in app si vede da dove arriva);
//  · se un dato non si trova con certezza resta vuoto: mai stimato;
//  · un lettore per fornitore conosciuto (Enel, ABC, Plenitude) + un lettore
//    generico basato sulle voci obbligatorie ARERA (Bolletta 2.0), usato per
//    i fornitori nuovi; i campi che l'utente corregge diventano il «modello»
//    di quel fornitore (etichetta → campo) e vengono riusati alle bollette
//    successive.
// ══════════════════════════════════════════════════════════════════════

export const PIVA_CERALDI = '04523831214';

// numero italiano «1.234,56» → 1234.56 ; «13.418» (migliaia) → 13418
export function num(s) {
  if (s == null) return null;
  let t = String(s).trim().replace(/[€\s]/g, '');
  if (!t) return null;
  if (/^-?\d{1,3}(\.\d{3})+(,\d+)?$/.test(t)) t = t.replace(/\./g, '').replace(',', '.');
  else if (/^-?\d+,\d+$/.test(t)) t = t.replace(',', '.');
  else if (/^-?\d+\.\d+$/.test(t)) { /* già col punto decimale (grafici) */ }
  else if (/^-?\d+$/.test(t)) { /* intero */ }
  else return null;
  const n = parseFloat(t);
  return isFinite(n) ? n : null;
}
// «30/11/2026», «30.11.2026», «30/11/26» → 2026-11-30
export function data(s) {
  const m = String(s || '').match(/(\d{1,2})[\/.](\d{1,2})[\/.](\d{2,4})/);
  if (!m) return null;
  let a = +m[3]; if (a < 100) a += 2000;
  const g = +m[1], me = +m[2];
  if (me < 1 || me > 12 || g < 1 || g > 31) return null;
  return a + '-' + String(me).padStart(2, '0') + '-' + String(g).padStart(2, '0');
}
const NUM = '(-?\\d{1,3}(?:\\.\\d{3})*(?:,\\d+)?|-?\\d+(?:,\\d+)?)';
const DATA = '(\\d{1,2}[\\/.]\\d{1,2}[\\/.]\\d{2,4})';
const MESI = { gen: 1, feb: 2, mar: 3, apr: 4, mag: 5, giu: 6, lug: 7, ago: 8, set: 9, ott: 10, nov: 11, dic: 12 };

// Raccoglitore dei campi: valore + riga di origine + certezza
function Raccolta(testo) {
  const righe = String(testo || '').split(/\r?\n/).map(r => r.replace(/\s+/g, ' ').trim());
  const piatto = righe.join('\n');
  const campi = {};
  const R = {
    righe, testo: piatto, campi,
    set(chiave, valore, riga, certo = true) {
      if (valore == null || valore === '' || (typeof valore === 'number' && !isFinite(valore))) return;
      if (campi[chiave] && campi[chiave].certo && !certo) return;
      campi[chiave] = { valore, riga: String(riga || '').slice(0, 220), certo };
    },
    // prima riga che corrisponde (regex su riga singola)
    riga(re, da = 0) { for (let i = da; i < righe.length; i++) { const m = righe[i].match(re); if (m) return { i, m, r: righe[i] }; } return null; },
    // regex sul testo intero (può attraversare le righe)
    cerca(re) { const m = piatto.match(re); if (!m) return null; const pos = piatto.indexOf(m[0]); const ini = piatto.lastIndexOf('\n', pos) + 1; const fine = piatto.indexOf('\n', pos + m[0].length); return { m, r: piatto.slice(ini, fine < 0 ? undefined : fine).slice(0, 220) || m[0] }; },
    // valore nella riga successiva a un'etichetta
    dopo(reEtichetta, reValore, salto = 3) {
      const e = R.riga(reEtichetta); if (!e) return null;
      for (let k = 0; k <= salto; k++) { const r = righe[e.i + k]; if (r == null) break; const t = k === 0 ? r.replace(reEtichetta, '') : r; const m = t.match(reValore); if (m) return { m, r: righe[e.i] + (k ? ' … ' + r : '') }; }
      return null;
    }
  };
  return R;
}

// ── Riconosce il fornitore dal testo ──
export function riconosci(testo) {
  const t = String(testo || '');
  const tN = t.replace(/\s+/g, ' ');
  const piva = (re) => re.test(tN);
  let fornitore = null;
  if (/Enel Energia/i.test(tN) && (piva(/15844561009/) || piva(/06655971007/))) fornitore = 'enel';
  else if (/ABC Napoli|ACQUA BENE COMUNE/i.test(tN) && piva(/07679350632/)) fornitore = 'abc';
  else if (/Plenitude/i.test(tN) && piva(/12300020158/)) fornitore = 'plenitude';
  const intestataCeraldi = new RegExp(PIVA_CERALDI).test(tN) || /CERALDI GROUP/i.test(tN);
  let tipo = null;
  if (/\bPOD\b|kWh|ENERGIA ELETTRICA/i.test(tN)) tipo = 'luce';
  if (/\bPDR\b|Smc|gas naturale/i.test(tN) && !/kWh/.test(tN)) tipo = 'gas';
  if (/servizio idrico|acquedotto|fognatura|depurazione/i.test(tN) && !/kWh|Smc/i.test(tN)) tipo = 'acqua';
  return { fornitore, tipo, intestataCeraldi };
}

// ═════════════════════════ ENEL (luce) ═════════════════════════
function leggiEnel(R) {
  R.set('tipo', 'luce', 'Enel Energia — energia elettrica');
  R.set('fornitore_nome', 'Enel Energia S.p.A.', 'Enel Energia S.p.A.'); R.set('fornitore_piva', '15844561009', 'Enel P.I. 15844561009');
  let x;
  if ((x = R.cerca(/POD:?\s*\n?\s*(IT\d{3}E\d{8})/i)) || (x = R.cerca(/\b(IT\d{3}E\d{8})\b/))) R.set('codice_fornitura', x.m[1], x.r);
  if ((x = R.cerca(/fattura elettronica n\.\s*(\d+)\s+del\s+(\d{2}\/\d{2}\/\d{4})/i))) { R.set('numero_fattura', x.m[1], x.r); R.set('data_emissione', data(x.m[2]), x.r); }
  if ((x = R.cerca(/Periodo\s+([A-Z]{3})\.?\s*(\d{4})\s*-\s*spesa/i))) { const me = MESI[x.m[1].toLowerCase()]; if (me) { const a = +x.m[2]; R.set('mese_competenza', a + '-' + String(me).padStart(2, '0'), x.r); } }
  if ((x = R.cerca(/Consumo rilevato \(dal (\d{2}\.\d{2}\.\d{4}) al (\d{2}\.\d{2}\.\d{4})\)/i)) || (x = R.cerca(/Consumo fatturato \(dal (\d{2}\.\d{2}\.\d{4}) al (\d{2}\.\d{2}\.\d{4})\)/i))) { R.set('periodo_dal', data(x.m[1]), x.r); R.set('periodo_al', data(x.m[2]), x.r); }
  if ((x = R.dopo(/^Importo da pagare$/i, new RegExp('^' + NUM + '\\s*€')))) R.set('totale', num(x.m[1]), x.r);
  if ((x = R.cerca(new RegExp('TOTALE BOLLETTA\\s+' + NUM + '\\s*€', 'i')))) R.set('totale', num(x.m[1]), x.r);
  if ((x = R.dopo(/^Scadenza$/i, new RegExp('^' + DATA + '$')))) R.set('scadenza_pagamento', data(x.m[1]), x.r);
  if ((x = R.riga(/^Metodo di pagamento (.+)$/i))) R.set('metodo_pagamento', x.m[1], x.r);
  if ((x = R.dopo(/^Stato dei pagamenti precedenti$/i, /^(.+)$/))) R.set('stato_pagamenti', x.m[1], x.r);
  // consumi del periodo per fascia (Consumo fatturato)
  const iF = R.riga(/^Consumo fatturato \(dal/i);
  if (iF) {
    const fasce = {}; let tot = null;
    for (let k = iF.i + 1; k < Math.min(iF.i + 12, R.righe.length); k++) {
      const f = R.righe[k].match(/^(F[123])$/); if (f) { const v = (R.righe[k + 1] || '').match(new RegExp('^' + NUM + ' kWh$')); if (v) fasce[f[1]] = num(v[1]); }
      if (/^Totale energia$/i.test(R.righe[k])) { const v = (R.righe[k + 1] || '').match(new RegExp('^' + NUM + ' kWh$')); if (v) tot = num(v[1]); break; }
    }
    if (Object.keys(fasce).length) R.set('consumo_fasce', fasce, iF.r);
    if (tot != null) R.set('consumo', tot, iF.r + ' … Totale energia ' + tot + ' kWh');
  }
  if ((x = R.cerca(new RegExp('Quota consumi\\s+' + NUM + '\\s*kWh\\s+' + NUM + '\\s*€/kWh\\s+' + NUM + '\\s*€', 'i')))) {
    R.set('consumo', num(x.m[1]), x.r); R.set('prezzo_medio_consumi', num(x.m[2]), x.r); R.set('costo_consumi', num(x.m[3]), x.r);
  }
  R.set('unita', 'kWh', 'kWh');
  if ((x = R.cerca(/^Consumi (Rilevati|Stimati)/im))) R.set('letture', /stim/i.test(x.m[1]) ? 'stimata' : 'reale', x.r);
  if ((x = R.cerca(new RegExp('di cui spesa per la vendita di energia elettrica\\s+' + NUM + '\\s*€/kWh\\s+' + NUM + '\\s*€', 'i')))) { R.set('prezzo_medio_vendita', num(x.m[1]), x.r); R.set('costo_vendita_consumi', num(x.m[2]), x.r); }
  if ((x = R.cerca(new RegExp('di cui spesa per la rete e gli oneri generali di sistema\\s+' + NUM + '\\s*€/kWh\\s+' + NUM + '\\s*€', 'i')))) { R.set('prezzo_medio_rete', num(x.m[1]), x.r); R.set('costo_rete_consumi', num(x.m[2]), x.r); }
  if ((x = R.cerca(new RegExp('Quota fissa\\s+(\\d+)\\s*mesi\\s+' + NUM + '\\s*€/mese\\s+' + NUM + '\\s*€', 'i')))) { R.set('quota_fissa', num(x.m[3]), x.r); R.set('quota_fissa_mese', num(x.m[2]), x.r); }
  if ((x = R.cerca(new RegExp('Quota potenza\\s+' + NUM + '\\s*kW\\s*x\\s*(\\d+)\\s*mesi\\s+' + NUM + '\\s*€/kW/mese\\s+' + NUM + '\\s*€', 'i')))) { R.set('potenza_fatturata', num(x.m[1]), x.r); R.set('quota_potenza', num(x.m[4]), x.r); R.set('prezzo_potenza', num(x.m[3]), x.r); }
  if ((x = R.cerca(new RegExp('ACCISE E IVA\\s+' + NUM + '\\s*€', 'i')))) R.set('accise_iva', num(x.m[1]), x.r);
  if ((x = R.cerca(new RegExp('Accisa sull.energia elettrica[^\\n]*\\n?[^\\n]*?' + NUM + '\\s*€\\s*$', 'im')))) { /* sotto */ }
  if ((x = R.cerca(new RegExp('IVA (\\d+)% su imponibile di euro ' + NUM + '\\s+(?:€\\s+)?' + NUM, 'i')))) { R.set('imponibile', num(x.m[2]), x.r); R.set('iva', num(x.m[3]), x.r); }
  if ((x = R.dopo(/^POTENZA IMPEGNATA:?$/i, new RegExp('^' + NUM + ' kW$')))) R.set('potenza_impegnata', num(x.m[1]), x.r);
  if ((x = R.riga(new RegExp('^Livello massimo di potenza: ' + NUM + ' kW')))) R.set('potenza_max', num(x.m[1]), x.r);
  // offerta
  if ((x = R.dopo(/^Nome Offerta$/i, /^(.+)$/))) R.set('offerta_nome', x.m[1], x.r);
  if ((x = R.dopo(/^Tipologia di offerta$/i, /^(.+)$/))) R.set('offerta_tipo', x.m[1], x.r);
  if ((x = R.dopo(/^Codice offerta$/i, /^([A-Z0-9]{8,})$/))) R.set('offerta_codice', x.m[1], x.r);
  if ((x = R.dopo(/^Data di decorrenza condizioni economiche$/i, new RegExp('^' + DATA + '$')))) R.set('offerta_decorrenza', data(x.m[1]), x.r);
  if ((x = R.dopo(/^Data di scadenza condizioni economiche$/i, new RegExp('^' + DATA + '$')))) R.set('offerta_scadenza', data(x.m[1]), x.r);
  else if ((x = R.cerca(/La tua offerta: (.+)\nscade il (\d{2}\/\d{2}\/\d{4})/i))) { R.set('offerta_nome', x.m[1], x.r, false); R.set('offerta_scadenza', data(x.m[2]), x.r); }
  if ((x = R.dopo(/^Data di scadenza del contratto$/i, /^(.+)$/))) R.set('contratto_scadenza', /indeterminato/i.test(x.m[1]) ? 'indeterminato' : (data(x.m[1]) || x.m[1]), x.r);
  if ((x = R.dopo(/^Presenza di oneri di recesso anticipato$/i, /^(SI|SÌ|NO)$/i))) R.set('oneri_recesso', /^no$/i.test(x.m[1]) ? 'no' : 'sì', x.r);
  // prezzi per fascia (Box offerta e dettaglio importi)
  const pf = {};
  ['F1', 'F2', 'F3'].forEach(f => {
    const y = R.cerca(new RegExp('^' + f + ' Prezzo fisso = ' + NUM + ' Dispacciamento = ' + NUM + ' Sbilanciamento = ' + NUM, 'm'));
    if (y) pf[f] = { prezzo_fisso: num(y.m[1]), dispacciamento: num(y.m[2]), sbilanciamento: num(y.m[3]) };
    const z = R.cerca(new RegExp('^Energia in ' + f + ' \\S+ dal [^€]+€/kWh ' + NUM + ' (\\d+) ' + NUM + '$', 'm'));
    if (z) { pf[f] = pf[f] || {}; pf[f].energia = num(z.m[1]); }
  });
  if (Object.keys(pf).length) R.set('prezzi_fasce', pf, 'Box dell\'offerta: Valori applicati nel periodo');
  // reattiva
  if ((x = R.cerca(/Reattiva fatturata[\s\S]{0,120}?Totale energia\n(\d[\d.]*) kVarh/i))) R.set('reattiva_fatturata', num(x.m[1]), 'Reattiva fatturata — Totale energia ' + x.m[1] + ' kVarh');
  if ((x = R.dopo(/^COSfi$/i, /^(\d+,\d+)$/))) R.set('cosfi', num(x.m[1]), x.r);
  // spesa annua
  if ((x = R.cerca(new RegExp('Spesa annua: ' + NUM + ' Euro dal (\\d{2}\\/\\d{4}) al (\\d{2}\\/\\d{4})', 'i')))) R.set('spesa_annua', num(x.m[1]), x.r);
  // storico 18 mesi
  const iP = R.riga(/^Periodo$/); const iT = R.riga(/^Tot \d/);
  if (iP && iT && iT.i > iP.i) {
    const mesi = []; for (let k = iP.i + 1; k < iT.i; k += 1) { const a = R.righe[k], b = R.righe[k + 1]; const mm = a && a.match(/^(Gen|Feb|Mar|Apr|Mag|Giu|Lug|Ago|Set|Ott|Nov|Dic)$/i); if (mm && /^\d{4}$/.test(b || '')) { mesi.push(b + '-' + String(MESI[mm[1].toLowerCase()]).padStart(2, '0')); k++; } }
    const rigaNum = re => { const y = R.riga(re, iP.i); return y ? y.r.replace(re, '').trim().split(' ').map(v => +v) : null; };
    const tipi = (R.riga(/^Reale|^Stimat/, iP.i) || { r: '' }).r.split(' ');
    const f1 = rigaNum(/^F1 /), f2 = rigaNum(/^F2 /), f3 = rigaNum(/^F3 /), tt = rigaNum(/^Tot /);
    if (mesi.length && tt && tt.length === mesi.length) {
      R.set('storico', mesi.map((m, i) => ({ mese: m, kwh: tt[i], F1: f1 ? f1[i] : null, F2: f2 ? f2[i] : null, F3: f3 ? f3[i] : null, lettura: tipi[i] ? tipi[i].toLowerCase() : null })), 'Consumi in kWh degli ultimi ' + mesi.length + ' mesi');
    }
  }
  const iK = R.riga(/^kW max$/);
  if (iK) {
    const mesi = [], val = [];
    for (let k = iK.i + 1; k < Math.min(iK.i + 40, R.righe.length); k++) { const r = R.righe[k]; const mm = r.match(/^(GEN|FEB|MAR|APR|MAG|GIU|LUG|AGO|SET|OTT|NOV|DIC) (\d{2})$/); if (mm) mesi.push('20' + mm[2] + '-' + String(MESI[mm[1].toLowerCase()]).padStart(2, '0')); else if (/^\d+(\.\d+)?$/.test(r)) val.push(+r); else if (mesi.length && val.length) break; }
    if (mesi.length && val.length === mesi.length) R.set('picchi_potenza', mesi.map((m, i) => ({ mese: m, kw: val[i] })), 'Potenza mensile prelevata in kW');
  }
}

// ═════════════════════════ ABC (acqua) ═════════════════════════
function leggiAbc(R) {
  R.set('tipo', 'acqua', 'ABC Napoli — servizio idrico');
  R.set('fornitore_nome', 'ABC - Acqua Bene Comune Napoli', 'ABC Napoli azienda speciale'); R.set('fornitore_piva', '07679350632', 'Partita Iva / Codice Fiscale 07679350632');
  let x;
  // numero fornitura: dopo «fornitura (ex codice contratto)» arrivano due codici (soggetto, fornitura) — si prende quello che inizia come il soggetto? no: si prende la riga che segue l'etichetta «fornitura», col numero a 11 cifre
  const iS = R.riga(/^soggetto \(codice cliente web\)$/i), iFo = R.riga(/^fornitura \(ex codice contratto\)$/i);
  if (iS && iFo) {
    const nums = []; for (let k = Math.max(iS.i, iFo.i) + 1; k < Math.max(iS.i, iFo.i) + 4; k++) { const m = (R.righe[k] || '').match(/^(\d{8,12})/); if (m) nums.push(m[1]); }
    // ordine nel PDF: prima il codice soggetto, poi la fornitura
    if (nums.length >= 2) { R.set('codice_cliente', nums[0], R.righe[iS.i] + ' ' + nums[0]); R.set('codice_fornitura', nums[1], R.righe[iFo.i] + ' ' + nums[1]); }
  }
  if ((x = R.cerca(/Fornitura (\d{8,12})/))) R.set('codice_fornitura', x.m[1], x.r, false);
  if ((x = R.dopo(/^FATTURA$/i, /^(\d{4,})$/, 6)) || (x = R.cerca(/Fattura numero:\s*\n?(\d{4,})/i))) R.set('numero_fattura', x.m[1], x.r);
  if ((x = R.dopo(/^Data emissione$/i, new RegExp('^' + DATA)))) R.set('data_emissione', data(x.m[1]), x.r);
  if ((x = R.cerca(/Periodo di fatturazione\s*\n?\s*(\d{2}\/\d{2}\/\d{4})\s*-\s*(\d{2}\/\d{2}\/\d{4})/i))) { R.set('periodo_dal', data(x.m[1]), x.r); R.set('periodo_al', data(x.m[2]), x.r); }
  if ((x = R.dopo(/^Tipologia$/i, /^(Bolletta .+)$/i))) { R.set('tipologia', x.m[1], x.r); R.set('acconto', /acconto/i.test(x.m[1]), x.r); }
  if ((x = R.dopo(/^Tipo tariffa$/i, /^(.+)$/))) R.set('tariffa', x.m[1], x.r);
  if ((x = R.dopo(/^Deposito cauzionale versato$/i, new RegExp('^' + NUM + '$')))) R.set('deposito_cauzionale', num(x.m[1]), x.r);
  if ((x = R.dopo(/^TOTALE DELLA BOLLETTA$|TOTALE DELLA BOLLETTA$/i, new RegExp('^€\\s*' + NUM + '$')))) R.set('totale', num(x.m[1]), x.r);
  if ((x = R.cerca(new RegExp('^TOTALE BOLLETTA ' + NUM + '$', 'mi')))) R.set('totale', num(x.m[1]), x.r);
  if ((x = R.dopo(/^DA PAGARE ENTRO IL GIORNO$/i, new RegExp('^' + DATA + '$')))) R.set('scadenza_pagamento', data(x.m[1]), x.r);
  if ((x = R.cerca(new RegExp('insoluto scaduto di €\\s*' + NUM + '[\\s\\S]{0,120}?per n\\.\\s*(\\d+)\\s*documento[\\s\\S]{0,40}?\\(dalla ([\\d\\/]+) del\\s*(\\d{2}\\/\\d{2}\\/\\d{4}) alla ([\\d\\/]+) del (\\d{2}\\/\\d{2}\\/\\d{4})\\)', 'i')))) {
    R.set('insoluto', { importo: num(x.m[1]), documenti: +x.m[2], primo: { numero: x.m[3], data: data(x.m[4]) }, ultimo: { numero: x.m[5], data: data(x.m[6]) } }, x.m[0].replace(/\s+/g, ' '));
  } else if ((x = R.cerca(new RegExp('insoluto[^\\n]{0,40}?€\\s*' + NUM, 'i')))) R.set('insoluto', { importo: num(x.m[1]) }, x.r, false);
  // letture
  const lett = []; R.righe.forEach(r => { const m = r.match(new RegExp('^' + DATA + ' (\\d[\\d.]*) mc (Stimata|Rilevata|Reale|Autolettura|Effettiva)', 'i')); if (m) lett.push({ data: data(m[1]), lettura: num(m[2]), tipo: m[3].toLowerCase() }); });
  if (lett.length) { R.set('letture_dettaglio', lett, 'Data Lettura Tipo'); R.set('letture', lett.every(l => /stimat/.test(l.tipo)) ? 'stimata' : (lett.some(l => /stimat/.test(l.tipo)) ? 'mista' : 'reale'), lett.map(l => l.data + ' ' + l.lettura + ' mc ' + l.tipo).join(' · ')); }
  if ((x = R.cerca(new RegExp('Totale consumi fatturati:\\s*' + NUM + ' mc', 'i'))) || (x = R.cerca(new RegExp('Consumo effettivo del periodo:\\s*' + NUM + ' mc', 'i')))) R.set('consumo', num(x.m[1]), x.r);
  R.set('unita', 'm³', 'mc');
  if ((x = R.cerca(new RegExp('Consumo medio annuo (\\d{4}) \\(CA\\):\\s*' + NUM + ' mc', 'i')))) R.set('consumo_annuo', num(x.m[2]), x.r);
  if ((x = R.cerca(/Matricola e Tipologia Misuratore\s*\n([^\n]+)/i))) R.set('contatore', x.m[1], x.r);
  [['Acquedotto \\(A\\)', 'costo_acquedotto'], ['Depurazione \\(D\\)', 'costo_depurazione'], ['Fognatura \\(F\\)', 'costo_fognatura'], ['Oneri perequazione \\(A\\+F\\+D\\)', 'costo_oneri'], ['Quota fissa', 'quota_fissa'], ['Totale IVA', 'iva'], ['Totale imponibile', 'imponibile'], ['Addebiti\\/Accrediti diversi', 'altri_addebiti']].forEach(([et, k]) => { const y = R.cerca(new RegExp('^' + et + ' €\\s*' + NUM + '$', 'mi')); if (y) R.set(k, num(y.m[1]), y.r); });
  if ((x = R.cerca(/Si può comunicare la lettura nel periodo:\s*\n?\s*(\d{2}\/\d{2}\/\d{4})\s*-\s*(\d{2}\/\d{2}\/\d{4})/i))) R.set('autolettura', { dal: data(x.m[1]), al: data(x.m[2]) }, x.r);
  // scaglioni acquedotto (stesso periodo, quantità diverse)
  const sc = []; R.righe.forEach(r => { const m = r.match(new RegExp('^COMPONENTE QV\\. ACQUEDOTTO.*?' + NUM + ' MC ' + NUM + ' ' + NUM + ' \\d+%$', 'i')); if (m) sc.push({ mc: num(m[1]), prezzo: num(m[2]), importo: num(m[3]) }); });
  if (sc.length) R.set('scaglioni', sc, 'COMPONENTE QV. ACQUEDOTTO (' + sc.length + ' scaglioni)');
  const unit = {}; [['fognatura', /^COMPONENTE TARIFFA FOGNATURA/i], ['depurazione', /^COMPONENTE TARIFFA DEPURAZIONE/i]].forEach(([k, re]) => { const y = R.riga(re); if (y) { const m = y.r.match(new RegExp(NUM + ' MC ' + NUM + ' ' + NUM + ' \\d+%$')); if (m) unit[k] = num(m[2]); } });
  if (Object.keys(unit).length) R.set('prezzi_unitari', unit, 'Fognatura e depurazione, €/mc');
  // consumi medi giornalieri storici
  const st = []; R.righe.forEach(r => { const m = r.match(new RegExp('^' + DATA + ' ' + DATA + ' (\\d+) ' + NUM + ' ' + NUM + '$')); if (m) st.push({ dal: data(m[1]), al: data(m[2]), giorni: +m[3], mc: num(m[4]), mc_giorno: num(m[5]) }); });
  if (st.length) R.set('storico', st, 'Andamento consumi medi giornalieri (in base a letture rilevate e/o autoletture)');
}

// ═════════════════════════ PLENITUDE (gas) ═════════════════════════
function leggiPlenitude(R) {
  R.set('tipo', 'gas', 'Eni Plenitude — gas');
  R.set('fornitore_nome', 'Eni Plenitude S.p.A. Società Benefit', 'Eni Plenitude SpA Società Benefit'); R.set('fornitore_piva', '12300020158', 'Partita IVA 12300020158');
  let x;
  if ((x = R.cerca(/Indirizzo di fornitura PDR Matricola misuratore\s*\n[^\n]*?(\d{14})\s+([A-Z0-9]+)\s*$/im))) { R.set('codice_fornitura', x.m[1], x.r); R.set('contatore', x.m[2], x.r); }
  else if ((x = R.cerca(/\bPDR[^\d\n]{0,40}(\d{14})/))) R.set('codice_fornitura', x.m[1], x.r);
  if ((x = R.cerca(/Fattura elettronica numero (\d+)[^\n]*Data di emissione (\d{2}\/\d{2}\/\d{4})/i))) { R.set('numero_fattura', x.m[1], x.r); R.set('data_emissione', data(x.m[2]), x.r); }
  if ((x = R.cerca(/Periodo di fatturazione: dal (\d{2}\/\d{2}\/\d{4}) al (\d{2}\/\d{2}\/\d{4})/i))) { R.set('periodo_dal', data(x.m[1]), x.r); R.set('periodo_al', data(x.m[2]), x.r); }
  if ((x = R.cerca(/Totale da pagare entro il (\d{2}\/\d{2}\/\d{4})\s*\n?\s*([\d.,]+)\s*€/i))) { R.set('scadenza_pagamento', data(x.m[1]), x.r); R.set('totale', num(x.m[2]), x.r); }
  if ((x = R.cerca(new RegExp('Totale bolletta ' + NUM + ' €', 'i')))) R.set('totale', num(x.m[1]), x.r);
  if ((x = R.cerca(/I tuoi pagamenti sono (regolari|[^\n.]+)/i))) R.set('stato_pagamenti', x.m[1], x.r);
  if ((x = R.cerca(/Consumo del periodo\s*\n?di fatturazione\s*\n?(\d[\d.]*) Smc/i))) R.set('consumo', num(x.m[1]), x.r);
  if ((x = R.cerca(new RegExp('QUOTA PER CONSUMI ' + NUM + ' Smc ' + NUM + ' €\\s*' + NUM, 'i')))) { R.set('consumo', num(x.m[1]), x.r); R.set('costo_consumi', num(x.m[2]), x.r); R.set('prezzo_medio_consumi', num(x.m[3]), x.r); }
  R.set('unita', 'Smc', 'Smc');
  if ((x = R.cerca(new RegExp('di cui spesa per la vendita di gas\\s*\\n?naturale\\s*\\n?' + NUM + ' €\\s*' + NUM + '\\s*\\n?€\\/Smc', 'i')))) { R.set('costo_vendita_consumi', num(x.m[1]), x.r); R.set('prezzo_medio_vendita', num(x.m[2]), x.r); }
  if ((x = R.cerca(new RegExp('QUOTA PER CONSUMI[\\s\\S]{0,200}?di cui spesa per la rete e gli oneri\\s*\\n?generali di sistema\\s*\\n?' + NUM + ' €\\s*' + NUM, 'i')))) { R.set('costo_rete_consumi', num(x.m[1]), 'di cui spesa per la rete e gli oneri generali di sistema ' + x.m[1] + ' € ' + x.m[2] + ' €/Smc'); R.set('prezzo_medio_rete', num(x.m[2]), 'idem'); }
  if ((x = R.cerca(new RegExp('QUOTA FISSA (\\d+) mesi ' + NUM + ' €\\s*' + NUM, 'i')))) { R.set('quota_fissa', num(x.m[2]), x.r); R.set('quota_fissa_mese', num(x.m[3]), x.r); }
  if ((x = R.cerca(new RegExp('Accise e IVA ' + NUM + ' €', 'i')))) R.set('accise_iva', num(x.m[1]), x.r);
  if ((x = R.cerca(new RegExp('Totale IVA ' + NUM + ' €', 'i')))) R.set('iva', num(x.m[1]), x.r);
  if ((x = R.cerca(/Nome offerta: (.+)/i))) R.set('offerta_nome', x.m[1].trim(), x.r);
  if ((x = R.cerca(/Codice offerta: (\S+)/i))) R.set('offerta_codice', x.m[1].replace(/_+$/, ''), x.r);
  if ((x = R.cerca(/Tipologia offerta: (.+)/i))) R.set('offerta_tipo', x.m[1].trim(), x.r);
  if ((x = R.cerca(/Scadenza condizioni economiche: (.+)/i))) R.set('offerta_scadenza', data(x.m[1]) || (/indetermin/i.test(x.m[1]) ? 'indeterminata' : x.m[1].trim()), x.r);
  if ((x = R.cerca(/Scadenza contratto: (.+)/i))) R.set('contratto_scadenza', data(x.m[1]) || (/indetermin/i.test(x.m[1]) ? 'indeterminato' : x.m[1].trim()), x.r);
  if ((x = R.cerca(/Oneri di recesso: (si|sì|no)/i))) R.set('oneri_recesso', /no/i.test(x.m[1]) ? 'no' : 'sì', x.r);
  if ((x = R.cerca(/In un anno hai consumato (\d[\d.]*) smc/i))) R.set('consumo_annuo', num(x.m[1]), x.r);
  if ((x = R.cerca(/Consumo fatturato\*?\s*(\d[\d.]*)/i))) R.set('consumo_fatturato', num(x.m[1]), x.r);
  if (/Rilevata distributore/i.test(R.testo)) R.set('letture', /Stimat/i.test(R.testo.split('Letture e Consumi')[1] || '') ? 'mista' : 'reale', 'Letture: Rilevata distributore');
  if ((x = R.cerca(/Spesa annua\s*\n?dal (\d{2}\.\d{2}\.\d{4}) al (\d{2}\.\d{2}\.\d{4})\s*\n?([\d.,]+) €/i))) R.set('spesa_annua', num(x.m[3]), x.r);
}

// ═════════════════════════ LETTORE GENERICO (voci ARERA) ═════════════════════════
// Per i fornitori nuovi: cerca le voci che ARERA rende obbligatorie in ogni
// bolletta luce/gas. Ogni valore trovato così è segnato «da confermare».
function leggiGenerico(R) {
  let x;
  if ((x = R.cerca(/\b(IT\d{3}E\d{8})\b/))) { R.set('codice_fornitura', x.m[1], x.r, false); R.set('tipo', 'luce', x.r, false); }
  else if ((x = R.cerca(/\bPDR\b[^\d\n]{0,60}(\d{14})\b/)) || (x = R.cerca(/\b(\d{14})\b(?=[^\n]*\bPDR\b)/))) { R.set('codice_fornitura', x.m[1], x.r, false); R.set('tipo', 'gas', x.r, false); }
  if ((x = R.cerca(new RegExp('(?:Totale (?:bolletta|da pagare|della bolletta))[^\\d\\n]{0,20}' + NUM + '\\s*€?', 'i')))) R.set('totale', num(x.m[1]), x.r, false);
  if ((x = R.cerca(new RegExp('(?:Data di )?scadenza (?:delle )?condizioni economiche:?\\s*\\n?\\s*' + DATA, 'i')))) R.set('offerta_scadenza', data(x.m[1]), x.r, false);
  if ((x = R.cerca(/Nome offerta:?\s*\n?\s*([^\n]+)/i))) R.set('offerta_nome', x.m[1].trim(), x.r, false);
  if ((x = R.cerca(/Tipologia (?:di )?offerta:?\s*\n?\s*([^\n]+)/i))) R.set('offerta_tipo', x.m[1].trim(), x.r, false);
  if ((x = R.cerca(new RegExp('(?:Quota (?:per )?consumi|Consumo(?: del periodo| fatturato)?)[^\\d\\n]{0,40}' + NUM + '\\s*(kWh|Smc|mc|m3|m³)', 'i')))) { R.set('consumo', num(x.m[1]), x.r, false); R.set('unita', /kwh/i.test(x.m[2]) ? 'kWh' : (/smc/i.test(x.m[2]) ? 'Smc' : 'm³'), x.r, false); }
  if ((x = R.cerca(new RegExp('Periodo(?: di fatturazione)?:?\\s*(?:dal\\s*)?' + DATA + '\\s*(?:al|-)\\s*' + DATA, 'i')))) { R.set('periodo_dal', data(x.m[1]), x.r, false); R.set('periodo_al', data(x.m[2]), x.r, false); }
  if ((x = R.cerca(new RegExp('(?:scadenza|pagare entro(?: il)?)\\s*:?\\s*' + DATA, 'i')))) R.set('scadenza_pagamento', data(x.m[1]), x.r, false);
  if ((x = R.cerca(new RegExp('(?:insoluto|morosit|bollette? (?:non pagat|scadut))[^\\n]{0,80}?€\\s*' + NUM, 'i')))) R.set('insoluto', { importo: num(x.m[1]) }, x.r, false);
  // P. IVA del fornitore: la prima a 11 cifre accanto a «Partita IVA / P.IVA» che non sia quella di Ceraldi
  const rePiva = /(?:Partita\s*IVA|P\.\s*IVA|P\.IVA|PI)\b[^\d\n]{0,30}(\d{11})/gi; let mp;
  while ((mp = rePiva.exec(R.testo))) { if (mp[1] !== PIVA_CERALDI) { const ini = R.testo.lastIndexOf('\n', mp.index) + 1; R.set('fornitore_piva', mp[1], R.testo.slice(ini, R.testo.indexOf('\n', mp.index + mp[0].length)), false); break; } }
}

// Applica il «modello» imparato per quel fornitore. Per ogni campo si è
// salvato: il testo che precede il valore (i numeri dentro l'etichetta valgono
// come «un numero qualsiasi», così l'etichetta regge anche alla bolletta dopo),
// il testo che lo segue (es. «kWh», «€») e il genere del valore.
const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
function reEtichetta(m) {
  const et = esc(m.etichetta).replace(/\d+(?:[.,\/]\d+)*/g, '[\\d.,/]+');
  const val = m.genere === 'data' ? DATA : (m.genere === 'codice' ? '([A-Za-z0-9/._-]+)' : (m.genere === 'testo' ? '(.+?)' : NUM));
  const dopo = m.dopo ? '\\s*' + esc(m.dopo) : (m.genere === 'testo' ? '\\s*$' : '');
  return new RegExp(et + '\\s*:?\\s*\\n?\\s*' + val + dopo, 'm');
}
function applicaModello(R, modello) {
  if (!modello || !modello.campi) return;
  Object.keys(modello.campi).forEach(k => {
    const m = modello.campi[k]; if (!m || !m.etichetta) return;
    const x = R.cerca(reEtichetta(m)); if (!x) return;
    const grezzo = x.m[1];
    const v = m.genere === 'data' ? data(grezzo) : ((m.genere === 'codice' || m.genere === 'testo') ? grezzo.trim() : num(grezzo));
    if (v != null && v !== '') R.set(k, v, x.r, true);
  });
}

// Insegna: dato il valore così come è scritto nel PDF, trova la riga che lo
// contiene e ricava etichetta (testo prima) e coda (testo subito dopo).
export function imparaEtichetta(testo, valoreScritto) {
  const R = Raccolta(testo); const v = String(valoreScritto || '').trim(); if (!v) return null;
  const coda = (r, p) => { const t = r.slice(p + v.length).trim().split(' ')[0] || ''; return /^[A-Za-z€%³\/]+$/.test(t) && t.length <= 8 ? t : ''; };
  for (const r of R.righe) {
    let p = r.indexOf(v);
    while (p >= 0) {
      const prima = r.charAt(p - 1), poi = r.charAt(p + v.length);
      if (!/[\d,.]/.test(prima) && !/\d/.test(poi)) { const et = r.slice(0, p).replace(/[:\s€]+$/, '').trim(); if (et.length >= 4) return { etichetta: et, dopo: coda(r, p), riga: r }; }
      p = r.indexOf(v, p + 1);
    }
  }
  for (let i = 1; i < R.righe.length; i++) if (R.righe[i].indexOf(v) === 0 && R.righe[i - 1].length >= 4) return { etichetta: R.righe[i - 1].replace(/[:\s]+$/, ''), dopo: coda(R.righe[i], 0), riga: R.righe[i - 1] + ' … ' + R.righe[i] };
  return null;
}

// Etichette leggibili dei campi (per la schermata di conferma)
export const ETICHETTE = {
  tipo: 'Tipo di utenza', fornitore_nome: 'Fornitore', fornitore_piva: 'P. IVA fornitore', codice_fornitura: 'Codice fornitura (POD / PDR / n° fornitura)', codice_cliente: 'Codice cliente',
  numero_fattura: 'Numero fattura', data_emissione: 'Data emissione', mese_competenza: 'Mese di competenza', periodo_dal: 'Periodo dal', periodo_al: 'Periodo al',
  totale: 'Totale bolletta €', imponibile: 'Imponibile €', iva: 'IVA €', scadenza_pagamento: 'Da pagare entro', metodo_pagamento: 'Metodo di pagamento', stato_pagamenti: 'Stato pagamenti precedenti',
  consumo: 'Consumo del periodo', unita: 'Unità', consumo_fasce: 'Consumo per fascia', letture: 'Letture', letture_dettaglio: 'Letture del contatore', consumo_annuo: 'Consumo annuo', consumo_fatturato: 'Consumo fatturato',
  prezzo_medio_consumi: 'Prezzo medio consumi (tutto compreso)', prezzo_medio_vendita: 'Prezzo medio solo energia/materia', prezzo_medio_rete: 'Prezzo medio rete e oneri', costo_consumi: 'Quota consumi €', costo_vendita_consumi: 'di cui vendita €', costo_rete_consumi: 'di cui rete e oneri €',
  quota_fissa: 'Quota fissa €', quota_fissa_mese: 'Quota fissa €/mese', quota_potenza: 'Quota potenza €', prezzo_potenza: 'Prezzo potenza €/kW/mese', potenza_fatturata: 'Potenza fatturata kW', potenza_impegnata: 'Potenza impegnata kW', potenza_max: 'Potenza massima prelevata kW', picchi_potenza: 'Picchi di potenza mensili',
  accise_iva: 'Accise e IVA €', prezzi_fasce: 'Prezzi per fascia €/kWh', reattiva_fatturata: 'Energia reattiva fatturata kVarh', cosfi: 'Cos φ',
  offerta_nome: 'Offerta', offerta_tipo: 'Tipo offerta', offerta_codice: 'Codice offerta', offerta_decorrenza: 'Condizioni economiche dal', offerta_scadenza: 'Scadenza condizioni economiche', contratto_scadenza: 'Scadenza contratto', oneri_recesso: 'Oneri di recesso',
  spesa_annua: 'Spesa annua dichiarata €', storico: 'Storico consumi', insoluto: 'Arretrati dichiarati dal fornitore', autolettura: 'Periodo per l\'autolettura', deposito_cauzionale: 'Deposito cauzionale €', tipologia: 'Tipologia bolletta', acconto: 'Bolletta di acconto', tariffa: 'Tariffa', contatore: 'Contatore',
  costo_acquedotto: 'Acquedotto €', costo_fognatura: 'Fognatura €', costo_depurazione: 'Depurazione €', costo_oneri: 'Oneri perequazione €', altri_addebiti: 'Altri addebiti €', scaglioni: 'Scaglioni acqua', prezzi_unitari: 'Prezzi €/m³'
};
// campi senza i quali la bolletta non serve ai report
export const ESSENZIALI = ['tipo', 'codice_fornitura', 'numero_fattura', 'data_emissione', 'totale', 'consumo', 'unita', 'periodo_dal', 'periodo_al'];

// ── punto d'ingresso ──
export function leggiBolletta(testo, opz = {}) {
  const ric = riconosci(testo);
  const R = Raccolta(testo);
  const lettore = ric.fornitore || (opz.modello && opz.modello.lettore) || 'generico';
  if (lettore === 'enel') leggiEnel(R);
  else if (lettore === 'abc') leggiAbc(R);
  else if (lettore === 'plenitude') leggiPlenitude(R);
  leggiGenerico(R);                       // riempie solo i buchi, «da confermare»
  if (opz.modello) applicaModello(R, opz.modello);
  if (!R.campi.tipo && ric.tipo) R.set('tipo', ric.tipo, 'riconosciuto dalle parole del testo', false);
  const dati = {}; Object.keys(R.campi).forEach(k => { dati[k] = R.campi[k].valore; });
  const mancanti = ESSENZIALI.filter(k => R.campi[k] == null);
  const daConfermare = Object.keys(R.campi).filter(k => !R.campi[k].certo);
  // controlli di coerenza (somme che devono tornare)
  const controlli = [];
  const c = (cond, ok, ko) => controlli.push({ ok: !!cond, testo: cond ? ok : ko });
  if (dati.consumo_fasce && dati.consumo != null) { const s = Object.values(dati.consumo_fasce).reduce((a, b) => a + (+b || 0), 0); c(Math.abs(s - dati.consumo) < 1, 'F1+F2+F3 = consumo totale (' + s + ' kWh)', 'F1+F2+F3 = ' + s + ' ma il totale letto è ' + dati.consumo); }
  if (dati.scaglioni && dati.consumo != null) { const s = dati.scaglioni.reduce((a, b) => a + b.mc, 0); c(Math.abs(s - dati.consumo) < 0.5, 'Scaglioni = consumo (' + s + ' m³)', 'Scaglioni = ' + s + ' m³ ma il consumo letto è ' + dati.consumo); }
  if (dati.imponibile != null && dati.iva != null && dati.totale != null && dati.tipo !== 'luce') c(Math.abs(dati.imponibile + dati.iva - dati.totale) < 0.05, 'Imponibile + IVA = totale', 'Imponibile + IVA (' + (dati.imponibile + dati.iva).toFixed(2) + ') ≠ totale ' + dati.totale);
  if (dati.tipo === 'luce' && dati.costo_consumi != null && dati.quota_fissa != null && dati.quota_potenza != null && dati.accise_iva != null && dati.totale != null) c(Math.abs(dati.costo_consumi + dati.quota_fissa + dati.quota_potenza + dati.accise_iva - dati.totale) < 0.05, 'Consumi + quota fissa + potenza + accise/IVA = totale', 'Le voci non tornano col totale');
  if (dati.tipo === 'gas' && dati.costo_consumi != null && dati.quota_fissa != null && dati.accise_iva != null && dati.totale != null) c(Math.abs(dati.costo_consumi + dati.quota_fissa + dati.accise_iva - dati.totale) < 0.05, 'Consumi + quota fissa + accise/IVA = totale', 'Le voci non tornano col totale');
  if (dati.costo_vendita_consumi != null && dati.costo_rete_consumi != null && dati.costo_consumi != null) c(Math.abs(dati.costo_vendita_consumi + dati.costo_rete_consumi - dati.costo_consumi) < 0.05, 'Vendita + rete = quota consumi', 'Vendita + rete ≠ quota consumi');
  return { lettore, riconosciuto: ric, dati, campi: R.campi, mancanti, daConfermare, controlli };
}
