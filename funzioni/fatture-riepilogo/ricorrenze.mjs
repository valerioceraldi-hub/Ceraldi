/* ENTRATE E USCITE RICORRENTI — motore (v10.31.0, 15/10/2026). Lo STESSO codice dell'app (Primanota.html): quello che vedi e quello che ti arriva sul telefono dicono la stessa cosa. */
var RCO_STOP = /^(srl|srls|sas|snc|spa|sapa|soc|societa|cooperativa|coop|unipersonale|dottoressa|dottore|dott|dr|ragioniere|rag|sig|sigra|signor|avv|geom|ing|italia|italy|it|branch|eu|sarl|et|cie|sca|the|di|de|del|della|dei|e|ed|and|a|r|l|s|p|cons|consortile|onlus|via|corso|c)$/;
function rcoViva(v){ return v && (v.stato === 'attiva' || v.stato === 'conclusa' && !!v.al); }
function rcoR2(n){ return Math.round((+n || 0) * 100) / 100; }
function rcoNorm(s){ return String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, ' ').trim(); }
function rcoTok(s){
  var out = {}; rcoNorm(s).split(' ').forEach(function(w){ if(w.length >= 2 && !RCO_STOP.test(w) && !/^\d+$/.test(w) && !/^[a-z]{0,2}\d/.test(w)) out[w] = 1; });
  return Object.keys(out).sort();
}
function rcoIso(d){ return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); }
function rcoData(iso){ return new Date(String(iso).slice(0, 10) + 'T12:00:00'); }
function rcoPiu(iso, n){ var d = rcoData(iso); d.setDate(d.getDate() + n); return rcoIso(d); }
function rcoGiorni(a, b){ return Math.round((rcoData(b) - rcoData(a)) / 86400000); }
function rcoMeseIdx(mk){ return (+mk.slice(0, 4)) * 12 + (+mk.slice(5, 7)) - 1; }
function rcoMeseDa(idx){ return Math.floor(idx / 12) + '-' + String(idx % 12 + 1).padStart(2, '0'); }
function rcoMed(a){ if(!a.length) return null; var b = a.slice().sort(function(x, y){ return x - y; }), m = b.length >> 1; return b.length % 2 ? b[m] : (b[m - 1] + b[m]) / 2; }
function rcoPasqua(a){
  var b = a % 19, c = Math.floor(a / 100), d = a % 100, e = Math.floor(c / 4), f = c % 4, g = Math.floor((c + 8) / 25), h = Math.floor((c - g + 1) / 3),
      i = (19 * b + c - e - h + 15) % 30, k = Math.floor(d / 4), l = d % 4, m = (32 + 2 * f + 2 * k - i - l) % 7, n = Math.floor((b + 11 * m + 22 * i) / 451),
      mese = Math.floor((i + m - 7 * n + 114) / 31), giorno = ((i + m - 7 * n + 114) % 31) + 1;
  return new Date(a, mese - 1, giorno, 12);
}
function rcoFestivo(d){
  var md = (d.getMonth() + 1) + '-' + d.getDate();
  if(['1-1', '1-6', '4-25', '5-1', '6-2', '8-15', '11-1', '12-8', '12-25', '12-26'].indexOf(md) >= 0) return true;
  var p = rcoPasqua(d.getFullYear()); p.setDate(p.getDate() + 1);
  return d.getMonth() === p.getMonth() && d.getDate() === p.getDate();
}
function rcoLavorativo(iso){ var d = rcoData(iso); while(d.getDay() === 0 || d.getDay() === 6 || rcoFestivo(d)) d.setDate(d.getDate() + 1); return rcoIso(d); }
function rcoControparte(m){
  var d = String(m.descrizione || '').replace(/\s+/g, ' ').trim(), st = String(m.sottotipo || ''), x;
  var iban = ((d.toUpperCase().match(/\bIT\d{2}[A-Z][0-9A-Z]{22}\b/) || [])[0]) || '';
  if((x = d.match(/SDD\s*(?:CORE|B2B)\s*:\s*([A-Z0-9]{6,})\s*(.*)$/i))) return { tipo: 'mandato', valore: x[1].toUpperCase(), nome: x[2] || 'Addebito diretto', tok: rcoTok(x[2]), iban: iban };
  if((x = d.match(/MUTUO\s*N\.?\s*([\d ]{6,})/i))) return { tipo: 'mutuo', valore: x[1].replace(/\D/g, ''), nome: 'Mutuo n° ' + x[1].trim(), tok: [], iban: iban };
  if(/\bI24\s+AGENZIA|\bF24\b/i.test(d) || /^f24$/i.test(st)) return { tipo: 'f24', valore: 'f24', nome: 'F24 (Agenzia delle Entrate)', tok: ['f24'], iban: iban };
  if((x = d.match(/CBILL\s+(.+?)\s+-\s+R\b/i))) return { tipo: 'nome', valore: rcoTok('cbill ' + x[1]).join(' '), nome: 'Bollettino ' + x[1], tok: rcoTok('cbill ' + x[1]), iban: iban };
  if(/assegno/i.test(d) || /assegno/i.test(st)) return { tipo: 'assegno', valore: '', nome: 'Assegno', tok: [], iban: '' };
  var nome = '';
  if((x = d.match(/FAVORE\s+(.+?)(?:\s+NOTPROVIDE\b|\s+-\s+|$)/i))) nome = x[1];
  else if((x = d.match(/BON\.?\s*DA\s+(.+?)(?:\s+-\s+|$)/i))) nome = x[1];
  else if(iban && (x = d.match(/^(.+?)\s+IT\d{2}[A-Z][0-9A-Z]{22}\b/i))) nome = x[1];
  else if((x = d.match(/^pagamento\s+(?:pos|online)\s*[—-]\s*(.+?)(?:\s+[A-Z]{2})?$/i))) nome = x[1];
  if(nome){ var t = rcoTok(nome); if(t.length) return { tipo: 'nome', valore: t.join(' '), nome: nome, tok: t, iban: iban }; }
  var testo = rcoNorm(d.replace(/\d[\d\/.:,-]*/g, ' ')).split(' ').filter(Boolean).slice(0, 4).join(' ');
  return { tipo: 'testo', valore: testo, nome: d.split(' - ')[0].slice(0, 40), tok: rcoTok(testo), iban: iban };
}
function rcoCp(m){ if(!m._rco) m._rco = rcoControparte(m); return m._rco; }
function rcoInterno(m){
  var d = String(m.descrizione || ''), c = m.cat || '';
  if(/^(giroconto|finanziamento_soci|incasso|versamento)$/.test(c)) return true;
  if(/giroconto|ceraldi\s+group/i.test(d)) return true;
  if(m.importo > 0 && /numia|inc\.?\s*pos|incas\.?\s*tramite|payout|pagamento da sumup|vers\.?\s*contanti|versamento\s+contanti/i.test(d)) return true;
  if(m.importo > 0 && String(m.conto) === 'SumUp' && /^pid\b|\bpid\s+sumup|sumup\s+pid/i.test(rcoNorm(d))) return true;
  return false;
}
function rcoPresenzeDi(m, ctx){
  if(!ctx || !ctx.presenze) return '';
  var cp = rcoCp(m); if(!(m.importo < 0)) return '';
  if(/beneficiari\s+vari/i.test(m.descrizione || '')) return 'dipendenti';
  if(!cp.tok || !cp.tok.length) return '';
  var t = {}; cp.tok.forEach(function(w){ t[w] = 1; });
  var gruppi = ['soci', 'dipendenti'];
  for(var g = 0; g < gruppi.length; g++){
    var L = ctx.presenze[gruppi[g]] || [];
    for(var i = 0; i < L.length; i++){ var p = L[i]; if(p.tok.length >= 2 && p.tok.every(function(w){ return t[w]; })) return gruppi[g]; }
  }
  return '';
}
function rcoRiconosce(v, m, ctx){
  var r = v.regola || {}; if(!r.tipo || r.tipo === 'nessuna') return false;
  if((v.dir === 'entrata') !== (m.importo > 0)) return false;
  if(r.conto && String(m.conto) !== r.conto) return false;
  var a = Math.abs(+m.importo || 0);
  if(r.min != null && r.min !== '' && a < +r.min - 0.005) return false;
  if(r.max != null && r.max !== '' && a > +r.max + 0.005) return false;
  var cp = rcoCp(m), val = [].concat(r.valori || (r.valore != null ? [r.valore] : [])).map(String);
  if(r.tipo === 'presenze') return rcoPresenzeDi(m, ctx) === r.gruppo;
  if(r.tipo === 'f24') return cp.tipo === 'f24';
  if(r.tipo === 'mandato') return cp.tipo === 'mandato' && val.indexOf(cp.valore) >= 0;
  if(r.tipo === 'mutuo') return cp.tipo === 'mutuo' && val.some(function(x){ return x.replace(/\D/g, '') === cp.valore; });
  if(r.tipo === 'iban') return !!cp.iban && val.some(function(x){ return x.toUpperCase().replace(/\s/g, '') === cp.iban; });
  if(r.tipo === 'nome'){
    if(!cp.tok || !cp.tok.length) return false;
    var t = {}; cp.tok.forEach(function(w){ t[w] = 1; });
    return val.some(function(x){ var w = rcoTok(x); return w.length && w.every(function(y){ return t[y]; }); });
  }
  if(r.tipo === 'testo'){ var dn = rcoNorm(m.descrizione); return val.some(function(x){ var n = rcoNorm(x); return n && dn.indexOf(n) >= 0; }); }
  return false;
}
function rcoSpecificita(v){ var r = v.regola || {}, b = { mandato: 0, mutuo: 0, iban: 0, presenze: 1, nome: 1, testo: 3, f24: 3 }[r.tipo]; if(b == null) b = 4; if(r.min != null && r.min !== '' || r.max != null && r.max !== '') b -= 1; return b; }
function rcoAtteso(v, mk){
  var a = +mk.slice(0, 4), mm = +mk.slice(5, 7), fine = new Date(a, mm, 0).getDate();
  return rcoLavorativo(mk + '-' + String(Math.min(+v.giorno || 1, fine)).padStart(2, '0'));
}
function rcoPeriodi(v, daMk, aMk){
  var ogni = Math.max(1, +v.ogni || 1), base = v.base || (v.dal ? String(v.dal).slice(0, 7) : daMk), bi = rcoMeseIdx(base), out = [];
  var ini = rcoMeseIdx(daMk), fin = rcoMeseIdx(aMk);
  var primo = v.dal ? rcoMeseIdx(String(v.dal).slice(0, 7)) : -Infinity;
  for(var i = ini; i <= fin; i++){
    if(((i - bi) % ogni + ogni) % ogni) continue;
    if(i < primo) continue;
    var mk = rcoMeseDa(i), d = rcoAtteso(v, mk);
    if(v.rate && v.dal){ var n = Math.floor((i - rcoMeseIdx(String(v.dal).slice(0, 7))) / ogni) + 1; if(n > +v.rate) continue; }
    if(v.al && d > String(v.al).slice(0, 10)) continue;
    out.push({ periodo: mk, data: d });
  }
  return out;
}
function rcoFinestra(v){ var t = v.toll != null ? +v.toll : ((+v.ogni || 1) <= 1 ? 8 : (+v.ogni <= 3 ? 12 : 20)); return { prima: Math.max(3, Math.round(t * 0.8)), dopo: t }; }
function rcoStimaPresenze(gruppo, mkPagamento, ctx){
  var P = ctx && ctx.presenze; if(!P) return null;
  var rif = rcoMeseDa(rcoMeseIdx(mkPagamento) - 1), righe = [];
  (P[gruppo] || []).forEach(function(p){
    if(p.fine && String(p.fine).slice(0, 7) < rif) return;
    var liq = (P.liquidazioni[p.id] || {})[rif], comp = (P.compensi[p.id] || {})[rif];
    var storia = P.bonifici[p.id] || {}, ult = Object.keys(storia).filter(function(k){ return k < rif; }).sort().slice(-3).map(function(k){ return storia[k]; }).filter(function(x){ return x > 0; });
    var v = null, come = '';
    if(liq != null && liq > 0){ v = liq; come = 'liquidazione di Presenze'; }
    else if(gruppo === 'soci' && comp != null && comp > 0){ v = comp; come = 'compenso fissato in Presenze'; }
    else if(p.netto && p.netto > 0){ v = p.netto; come = 'netto fisso in Presenze'; }
    else if(ult.length){ v = rcoMed(ult); come = 'media degli ultimi ' + ult.length + ' mesi'; }
    if(v) righe.push({ id: p.id, nome: p.nome, importo: rcoR2(v), come: come, certo: come.indexOf('liquidazione') === 0 || come.indexOf('compenso') === 0 });
  });
  if(!righe.length) return null;
  return { rif: rif, righe: righe, totale: rcoR2(righe.reduce(function(s, x){ return s + x.importo; }, 0)), certo: righe.every(function(x){ return x.certo; }) };
}
function rcoCalcola(voci, movs, ctx, opz){
  opz = opz || {}; var oggi = opz.oggi || rcoIso(new Date());
  var mi = rcoMeseIdx(oggi.slice(0, 7)), daMk = rcoMeseDa(mi - (opz.mesiIndietro != null ? opz.mesiIndietro : 13)), aMk = rcoMeseDa(mi + (opz.mesiAvanti != null ? opz.mesiAvanti : 3));
  var cop = opz.copertura || {}, copTutti = Object.keys(cop).reduce(function(m, k){ return !m || cop[k] > m ? cop[k] : m; }, '');
  var usati = {}, perId = {}, esiti = opz.esiti || {};
  var mPer = {}; (movs || []).forEach(function(m){ mPer[String(m.id)] = m; });
  var attive = (voci || []).filter(function(v){ return v && v.stato !== 'esclusa' && !v.eliminata; }).slice().sort(function(a, b){ return rcoSpecificita(a) - rcoSpecificita(b); });
  attive.forEach(function(v){ Object.keys(esiti).forEach(function(k){ var e = esiti[k]; if(k.split('|')[0] === String(v.id) && e && e.esito === 'collegato' && e.mov) usati[String(e.mov)] = v.id; }); });
  attive.forEach(function(v){
    var F = rcoFinestra(v), P = rcoPeriodi(v, daMk, aMk), agg = !!v.aggrega || (v.regola || {}).tipo === 'presenze' || (v.regola || {}).tipo === 'f24' && v.regola.min == null && v.regola.max == null;
    var cand = (movs || []).filter(function(m){ return !usati[String(m.id)] && rcoRiconosce(v, m, ctx); }).sort(function(a, b){ return a.data < b.data ? -1 : 1; });
    var out = [], ibanVisti = {};
    P.forEach(function(p){
      var e = esiti[v.id + '|' + p.periodo] || null, ini = rcoPiu(p.data, -F.prima), fin = rcoPiu(p.data, F.dopo), presi = [];
      if(e && e.esito === 'collegato' && e.mov && mPer[String(e.mov)]) presi = [mPer[String(e.mov)]];
      else {
        var nel = cand.filter(function(m){ return !usati[String(m.id)] && m.data >= ini && m.data <= fin; });
        if(agg) presi = nel;
        else if(nel.length){ nel.sort(function(a, b){ return Math.abs(rcoGiorni(p.data, a.data)) - Math.abs(rcoGiorni(p.data, b.data)) || Math.abs(Math.abs(a.importo) - (v.importo || 0)) - Math.abs(Math.abs(b.importo) - (v.importo || 0)); }); presi = [nel[0]]; }
      }
      presi.forEach(function(m){ usati[String(m.id)] = v.id; });
      var stima = (v.regola || {}).tipo === 'presenze' ? rcoStimaPresenze(v.regola.gruppo, p.periodo, ctx) : null;
      var atteso = stima ? stima.totale : (+v.importo || 0);
      var reale = rcoR2(presi.reduce(function(s, m){ return s + Math.abs(+m.importo || 0); }, 0));
      var conto = (v.regola || {}).conto || v.conto || '', copre = (conto && cop[conto]) || copTutti;
      var stato;
      if(e && e.esito === 'saltato') stato = 'saltato';
      else if(v.sospesaFino && p.data <= v.sospesaFino) stato = 'sospeso';
      else if(presi.length){
        stato = 'arrivato';
        if(!(e && e.esito === 'va_bene')){
          var lo = v.min != null ? +v.min : atteso, hi = v.max != null ? +v.max : atteso, t = v.variabile || stima ? 0.25 : 0.03;
          if(stima) { lo = Math.min(lo, atteso); hi = Math.max(hi, atteso); }
          if(lo > 0 && (reale < lo * (1 - t) - 0.5 || reale > hi * (1 + t) + 0.5)) stato = 'diverso';
        }
      }
      else if(!(v.regola && v.regola.tipo && v.regola.tipo !== 'nessuna')) stato = p.data < oggi ? 'da_segnare' : 'previsto';
      else if(copre && fin < copre) stato = 'mancante';
      else if(p.data <= oggi) stato = 'in_attesa';
      else stato = 'previsto';
      var ibanNuovo = '';
      presi.forEach(function(m){
        var cp = rcoCp(m); if(!cp.iban) return;
        var chi = (cp.tok || []).join(' ') || '-', visti = ibanVisti[chi] = ibanVisti[chi] || [];
        if(visti.length && visti.indexOf(cp.iban) < 0 && !(opz.ibanNoti && opz.ibanNoti[cp.iban])) ibanNuovo = cp.iban;
        if(visti.indexOf(cp.iban) < 0) visti.push(cp.iban);
      });
      out.push({ periodo: p.periodo, data: p.data, fino: fin, atteso: rcoR2(atteso), stima: stima, reale: reale, movs: presi, stato: stato, esito: e, ibanNuovo: ibanNuovo });
    });
    perId[v.id] = out;
  });
  return { periodi: perId, usati: usati };
}
function rcoProponi(movs, ctx, opz){
  opz = opz || {}; var oggi = opz.oggi || rcoIso(new Date()), note = opz.chiaviNote || {}, usati = opz.usati || {};
  var cop = opz.copertura || {}, copTutti = Object.keys(cop).reduce(function(m, k){ return !m || cop[k] > m ? cop[k] : m; }, '');
  var gruppi = {}, pres = { dipendenti: [], soci: [] };
  (movs || []).forEach(function(m){
    if(!m || !m.data || usati[String(m.id)] || rcoInterno(m)) return;
    if(Math.abs(+m.importo || 0) < 3) return;
    var g = rcoPresenzeDi(m, ctx); if(g){ pres[g].push(m); return; }
    if(m.cat === 'stipendio') return;
    var cp = rcoCp(m), k, nome = cp.nome;
    if(cp.tipo === 'assegno' || !cp.valore) return;
    else k = cp.tipo + ':' + cp.valore;
    k += m.importo > 0 ? ':e' : ':u';
    (gruppi[k] = gruppi[k] || { k: k, cp: cp, nome: nome, movs: [] }).movs.push(m);
  });
  var out = [];
  var valuta = function(chiave, nome, cp, L, extra){
    L = L.slice().sort(function(a, b){ return a.data < b.data ? -1 : 1; });
    var perMese = {}; L.forEach(function(m){ var mk = m.data.slice(0, 7); (perMese[mk] = perMese[mk] || []).push(m); });
    var mesi = Object.keys(perMese).sort(); if(mesi.length < 2) return null;
    var idx = mesi.map(rcoMeseIdx), gaps = []; for(var i = 1; i < idx.length; i++) gaps.push(idx[i] - idx[i - 1]);
    var cand = [1, 2, 3, 4, 6, 12], best = null;
    cand.forEach(function(g){ var ok = gaps.filter(function(x){ return g >= 3 ? Math.abs(x - g) <= 1 : x === g; }).length / gaps.length; if(!best || ok > best.ok + 0.001 || (Math.abs(ok - best.ok) < 0.001 && g < best.g)) best = { g: g, ok: ok }; });
    var recente = rcoGiorni(L[0].data, oggi) <= 130;
    var minimo = best.g >= 4 ? 3 : (recente ? 2 : 3);
    if(mesi.length < minimo || best.ok < (mesi.length >= 8 ? 0.6 : 0.7)) return null;
    if(mesi.length === 2 && best.g !== 1) return null;
    var somme = mesi.map(function(mk){ return rcoR2(perMese[mk].reduce(function(s, m){ return s + Math.abs(+m.importo || 0); }, 0)); });
    var multi = mesi.filter(function(mk){ return perMese[mk].length > 1; }).length / mesi.length;
    var giorni = mesi.map(function(mk){ return +perMese[mk][0].data.slice(8, 10); }), gMed = Math.round(rcoMed(giorni)), spread = rcoMed(giorni.map(function(x){ return Math.abs(x - gMed); }));
    if(mesi.length === 2 && (spread > 4 || Math.abs(somme[0] - somme[1]) > Math.max(2, somme[1] * 0.1))) return null;
    var ult = somme.slice(-6), med = rcoMed(ult), mn = Math.min.apply(null, ult), mx = Math.max.apply(null, ult);
    var fisso = med > 0 && (mx - mn) / med <= 0.03, duo = false;
    if(!fisso && ult.length >= 3){ var lo = ult.filter(function(x){ return Math.abs(x - mn) <= mn * 0.03; }), hi = ult.filter(function(x){ return Math.abs(x - mx) <= mx * 0.03; }); duo = lo.length + hi.length === ult.length; }
    var variabile = !fisso && !duo;
    var tipico = fisso ? rcoR2(med) : (duo ? rcoR2(rcoMed(ult)) : rcoR2(rcoMed(somme.slice(-3))));
    if(tipico < 5) return null;
    var ultimo = L[L.length - 1], ultMk = mesi[mesi.length - 1], prossMk = rcoMeseDa(rcoMeseIdx(ultMk) + best.g);
    var v0 = { giorno: gMed, ogni: best.g };
    var prossima = rcoAtteso(v0, prossMk), toll = best.g <= 1 ? 8 : (best.g <= 3 ? 12 : 20);
    var conti = {}; L.forEach(function(m){ conti[m.conto || ''] = 1; }); var conto = Object.keys(conti).length === 1 ? Object.keys(conti)[0] : '';
    var copre = (conto && cop[conto]) || copTutti;
    var interrotta = !!copre && rcoPiu(prossima, toll) < copre;
    var forte = /^(mandato|mutuo|nome|presenze)$/.test(cp.tipo);
    var score = (mesi.length >= 6 ? 75 : mesi.length >= 4 ? 65 : mesi.length === 3 ? 55 : 40) + (forte ? 12 : 0) + (best.ok === 1 && spread <= 3 ? 8 : 0) - (variabile && (mx - mn) / (med || 1) > 0.5 ? 12 : 0) - (interrotta ? 15 : 0);
    score = Math.max(10, Math.min(98, score));
    var rate = null, rx;
    L.slice(-3).forEach(function(m){ if((rx = String(m.descrizione || '').match(/\brata\s*(\d{1,3})\s*(?:di|\/|su)\s*(\d{1,3})\b/i))) rate = { n: +rx[1], tot: +rx[2] }; });
    var dir = L[0].importo > 0 ? 'entrata' : 'uscita';
    var regola = extra && extra.regola ? extra.regola : { tipo: cp.tipo === 'testo' ? 'testo' : cp.tipo, valore: cp.valore };
    if(cp.tipo === 'assegno') regola = { tipo: 'nessuna' };
    if(extra && extra.min != null){ regola.min = extra.min; regola.max = extra.max; }
    var ogniTxt = { 1: 'ogni mese', 2: 'ogni 2 mesi', 3: 'ogni 3 mesi', 4: 'ogni 4 mesi', 6: 'ogni 6 mesi', 12: 'ogni anno' }[best.g];
    var eur = function(n){ return n.toLocaleString('it-IT', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €'; };
    var perche = 'Trovato ' + L.length + (L.length === 1 ? ' volta' : ' volte') + ' in ' + mesi.length + ' mesi (dal ' + L[0].data.slice(8, 10) + '/' + L[0].data.slice(5, 7) + '/' + L[0].data.slice(2, 4) + '), ' + ogniTxt + ' intorno al ' + gMed + ', ' + (fisso ? 'sempre ' + eur(tipico) : duo ? 'tra ' + eur(mn) + ' e ' + eur(mx) : 'importo variabile ' + eur(mn) + '–' + eur(mx)) + '.';
    return {
      chiave: chiave, nome: nome, dir: dir, cp: cp, regola: regola, ogni: best.g, base: ultMk, giorno: gMed, toll: toll,
      importo: tipico, min: rcoR2(mn), max: rcoR2(mx), variabile: variabile, conto: conto, aggrega: multi >= 0.3,
      storia: L.map(function(m){ return { id: m.id, data: m.data, importo: rcoR2(Math.abs(m.importo)), conto: m.conto }; }),
      prossima: { data: prossima, importo: tipico }, ultima: ultimo.data, mesi: mesi.length, score: score,
      fiducia: score >= 75 ? 'alta' : score >= 55 ? 'media' : 'bassa', interrotta: interrotta, nuova: rcoGiorni(L[0].data, oggi) <= 130,
      rate: rate, perche: perche, cat: extra && extra.cat || ''
    };
  };
  var valutaCoda = function(chiave, nome, cp, L, extra){
    var p = valuta(chiave, nome, cp, L, extra); if(p) return p;
    L = L.slice().sort(function(a, b){ return a.data < b.data ? -1 : 1; });
    var perMese = {}; L.forEach(function(m){ var mk = m.data.slice(0, 7); (perMese[mk] = perMese[mk] || []).push(m); });
    var mesi = Object.keys(perMese).sort(); if(mesi.length < 3) return null;
    var som = function(mk){ return perMese[mk].reduce(function(s, m){ return s + Math.abs(+m.importo || 0); }, 0); };
    var fine = mesi.length - 1, gap = rcoMeseIdx(mesi[fine]) - rcoMeseIdx(mesi[fine - 1]), rif = som(mesi[fine]), ini = fine;
    if(gap < 1 || gap > 12) return null;
    while(ini > 0 && rcoMeseIdx(mesi[ini]) - rcoMeseIdx(mesi[ini - 1]) === gap && Math.abs(som(mesi[ini - 1]) - rif) <= Math.max(2, rif * 0.1)) ini--;
    if(ini === 0 || fine - ini + 1 < 2) return null;
    var coda = []; mesi.slice(ini).forEach(function(mk){ coda = coda.concat(perMese[mk]); });
    var q = valuta(chiave, nome, cp, coda, extra);
    if(q){ q.cambiata = true; q.perche = 'Da ' + rcoData(coda[0].data).toLocaleDateString('it-IT', { month: 'long', year: 'numeric' }) + ' si ripete: ' + q.perche.charAt(0).toLowerCase() + q.perche.slice(1) + ' Prima c\'erano pagamenti diversi.'; }
    return q;
  };
  Object.keys(gruppi).forEach(function(k){
    if(note[k]) return;
    var G = gruppi[k], L = G.movs;
    if(/^(f24|testo|nome)/.test(k) && L.length >= 6){
      var vals = L.map(function(m){ return Math.abs(m.importo); }), medAll = rcoMed(vals), mnA = Math.min.apply(null, vals), mxA = Math.max.apply(null, vals);
      if((mxA - mnA) / (medAll || 1) > 0.4){
        var cl = {};
        L.forEach(function(m){ var a = Math.abs(m.importo), key = null; Object.keys(cl).forEach(function(c){ if(!key && Math.abs(a - +c) <= +c * 0.03) key = c; }); (cl[key || a] = cl[key || a] || []).push(m); });
        Object.keys(cl).forEach(function(c){
          var S = cl[c]; if(S.length < 3) return;
          var mesiS = {}; S.forEach(function(m){ mesiS[m.data.slice(0, 7)] = 1; }); if(Object.keys(mesiS).length < 3) return;
          var vS = S.map(function(m){ return Math.abs(m.importo); }), lo = Math.min.apply(null, vS), hi = Math.max.apply(null, vS);
          var kS = k + ':' + Math.round(rcoMed(vS));
          if(note[kS]) { L = L.filter(function(m){ return S.indexOf(m) < 0; }); return; }
          var p = valuta(kS, G.nome + ' da ~' + Math.round(rcoMed(vS)) + ' €', G.cp, S, { min: rcoR2(lo * 0.97), max: rcoR2(hi * 1.03) });
          if(p){ p.rata = true; out.push(p); L = L.filter(function(m){ return S.indexOf(m) < 0; }); }
        });
      }
    }
    if(L.length){ var p = valutaCoda(k, G.nome, G.cp, L); if(p) out.push(p); }
  });
  ['dipendenti', 'soci'].forEach(function(g){
    var k = 'presenze:' + g; if(note[k] || pres[g].length < 3) return;
    var p = valuta(k, g === 'dipendenti' ? 'Stipendi dei dipendenti' : 'Compensi dei soci', { tipo: 'presenze', valore: g, tok: [] }, pres[g], { regola: { tipo: 'presenze', gruppo: g }, cat: g === 'dipendenti' ? 'Personale' : 'Soci' });
    if(p){ p.aggrega = true; p.variabile = true; var st = rcoStimaPresenze(g, p.prossima.data.slice(0, 7), ctx); if(st){ p.prossima.importo = st.totale; p.importo = st.totale; p.stima = st; p.perche += ' La cifra del prossimo mese viene da Presenze (' + st.righe.length + ' persone).'; } out.push(p); }
  });
  return out.sort(function(a, b){ return (b.nuova - a.nuova) || (b.score - a.score); });
}
function rcoAvvisi(voci, calc, oggi, cfg){
  cfg = cfg || {}; var out = [];
  (voci || []).forEach(function(v){
    if(!rcoViva(v)) return;
    var ant = v.avviso != null && v.avviso !== '' ? +v.avviso : (v.dir === 'uscita' && (+v.importo || 0) >= (cfg.soglia != null ? cfg.soglia : 300) ? (cfg.giorni != null ? cfg.giorni : 3) : -1);
    (calc.periodi[v.id] || []).forEach(function(p){
      var g = rcoGiorni(oggi, p.data);
      if(ant > 0 && g === ant && (p.stato === 'previsto' || p.stato === 'in_attesa')) out.push({ v: v, p: p, tipo: 'prima', giorni: g, chiave: 'rco|' + v.id + '|' + p.periodo + '|prima' });
      if(p.stato === 'mancante' && rcoGiorni(p.fino, oggi) <= 20) out.push({ v: v, p: p, tipo: 'mancato', chiave: 'rco|' + v.id + '|' + p.periodo + '|mancato' });
      if(p.stato === 'diverso' && rcoGiorni(p.movs[0].data, oggi) <= 20) out.push({ v: v, p: p, tipo: 'diverso', chiave: 'rco|' + v.id + '|' + p.periodo + '|diverso' });
      if(p.ibanNuovo && rcoGiorni(p.movs[0].data, oggi) <= 20) out.push({ v: v, p: p, tipo: 'iban', chiave: 'rco|' + v.id + '|' + p.periodo + '|iban' });
    });
  });
  return out;
}
function rcoFrase(a, eur){
  var v = a.v, p = a.p, e = eur || function(n){ return '€ ' + (+n).toLocaleString('it-IT', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); };
  var gg = p.data.slice(8, 10) + '/' + p.data.slice(5, 7), entra = v.dir === 'entrata';
  if(a.tipo === 'prima') return (a.giorni === 1 ? 'Domani' : 'Tra ' + a.giorni + ' giorni') + ' (' + gg + ') · ' + v.nome + ' — ' + (p.stima && !p.stima.certo ? 'circa ' : '') + e(p.atteso) + (entra ? ' in arrivo' : ': tieni i fondi sul conto');
  if(a.tipo === 'mancato') return v.nome + ' del ' + gg + ' (' + e(p.atteso) + ') non risulta nell\'estratto conto';
  if(a.tipo === 'diverso') return v.nome + ': ' + e(p.reale) + ' invece dei soliti ' + e(p.atteso);
  if(a.tipo === 'iban') return v.nome + ' pagato su un IBAN nuovo (…' + String(p.ibanNuovo).slice(-6) + '): se non l\'hai chiesto tu, controlla';
  return v.nome;
}

export { rcoR2, rcoIso, rcoPiu, rcoTok, rcoCalcola, rcoProponi, rcoAvvisi, rcoFrase, rcoStimaPresenze };
