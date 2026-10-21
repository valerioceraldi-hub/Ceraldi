/* ══════════════════════════════════════════════════════════════════
   SCADENZE, RATE E NOTE DI CREDITO — logica unica (07/10/2026)
   Lo STESSO codice gira nell'app (registro, scheda fattura) e sul server
   (avvisi e riepilogo del lunedì): così quello che vedi e quello che ti
   arriva come avviso dicono sempre la stessa cosa.
   ══════════════════════════════════════════════════════════════════ */
var SC_RE_NC = /\[NC→(\d+)·([\d.]+)·([^\]]*)\]/g;
function scR2(n){ return Math.round((+n || 0) * 100) / 100; }
function scNum(v){ if(typeof v === 'number') return v; var s = String(v == null ? '' : v).trim(); if(/,\d{1,2}$/.test(s)) s = s.replace(/\./g, '').replace(',', '.'); var n = parseFloat(s); return isNaN(n) ? 0 : n; }
function scNcUsi(nc){
  var note = String((nc && nc.note) || ''), out = [], m;
  var vecchioP = /\[NC-P\]/.test(note);
  SC_RE_NC.lastIndex = 0;
  while((m = SC_RE_NC.exec(note))){
    var fid = m[1];
    out.push({ fid: fid, imp: scR2(parseFloat(m[2]) || 0), label: m[3], pagata: vecchioP || note.indexOf('[NC-P:' + fid + ']') >= 0 });
  }
  return out;
}
function scNcUsato(nc){ return scR2(scNcUsi(nc).reduce(function(s, u){ return s + u.imp; }, 0)); }
function scNcCredito(nc){ return scR2(Math.max(0, Math.abs(+(nc && nc.importo) || 0) - scNcUsato(nc))); }
function scNcSuFattura(fid, tutte){
  var out = [];
  (tutte || []).forEach(function(nc){
    if(!nc || nc.tipo !== 'nota_credito') return;
    scNcUsi(nc).forEach(function(u){ if(String(u.fid) === String(fid)) out.push({ nc: nc, imp: u.imp, pagata: u.pagata }); });
  });
  return out;
}
function scPagabile(f){ return !!f && f.tipo !== 'nota_credito' && f.tipo !== 'ddt' && !f.deleted_at && !f.deletedAt; }
function scStato(f){ var s = f && f.stato; return (s && typeof s === 'object') ? s.stato : (s || 'pagata'); }
function scParz(f){ return +(f.parzPagato != null ? f.parzPagato : f.parz_pagato) || 0; }
function scConti(f, tutte){
  var lordo = scR2(Math.abs(+f.importo || 0));
  var nc = scNcSuFattura(f.id, tutte);
  var ncTot = scR2(nc.reduce(function(s, x){ return s + x.imp; }, 0));
  var ncSulDovuto = scR2(nc.filter(function(x){ return !x.pagata; }).reduce(function(s, x){ return s + x.imp; }, 0));
  var dovuto = scR2(Math.max(0, lordo - ncTot));
  var st = scStato(f), pagato;
  if(st === 'pagata') pagato = dovuto;
  else if(st === 'parziale') pagato = scR2(Math.max(0, scParz(f) - ncSulDovuto));
  else pagato = 0;
  var residuo = (st === 'pagata' || st === 'annullata') ? 0 : scR2(Math.max(0, Math.min(lordo - scParz(f), dovuto - pagato)));
  return { lordo: lordo, nc: nc, ncTot: ncTot, dovuto: dovuto, pagato: scR2(Math.min(pagato, dovuto)), residuo: residuo, stato: st };
}
function scScadenze(f, tutte){
  if(!scPagabile(f)) return [];
  var C = scConti(f, tutte), rate = [];
  (f.rate || []).forEach(function(r, i){
    var imp = scR2(Math.abs(scNum(r.importo))), d = String(r.data || r.scadenza || '').slice(0, 10);
    if(imp > 0 && /^\d{4}-\d{2}-\d{2}$/.test(d)) rate.push({ i: i, importo: imp, data: d, metodo: r.pagamento || f.pagamento || '', assegno: r.assegno || '' });
  });
  rate.sort(function(a, b){ return a.data < b.data ? -1 : a.data > b.data ? 1 : a.i - b.i; });
  var scad = String(f.scadenza || '').slice(0, 10), out = [];
  if(rate.length){
    var somma = scR2(rate.reduce(function(s, r){ return s + r.importo; }, 0));
    if(C.dovuto - somma > 0.99) rate.push({ i: -1, importo: scR2(C.dovuto - somma), data: (scad && scad >= rate[rate.length - 1].data) ? scad : rate[rate.length - 1].data, metodo: f.pagamento || '', assegno: '', saldo: true });
    var acc = C.stato === 'pagata' ? Infinity : C.pagato;
    rate.forEach(function(r, k){
      var coperto = Math.min(acc, r.importo); acc -= coperto;
      out.push({ n: k + 1, tot: rate.length, data: r.data, importo: r.importo, residuo: scR2(r.importo - coperto), pagata: r.importo - coperto < 0.01, metodo: r.metodo, assegno: r.assegno, saldo: !!r.saldo, idx: r.i });
    });
  } else if(/^\d{4}-\d{2}-\d{2}$/.test(scad)){
    out.push({ n: 1, tot: 1, data: scad, importo: C.dovuto, residuo: C.residuo, pagata: C.residuo < 0.01, metodo: f.pagamento || '', assegno: f.assegno || '', saldo: false, idx: -1 });
  }
  return out;
}
function scProssima(f, tutte){
  var st = scStato(f); if(!scPagabile(f) || st === 'pagata' || st === 'annullata') return null;
  var l = scScadenze(f, tutte).filter(function(x){ return !x.pagata; });
  return l.length ? l[0] : null;
}
function scGiorni(da, a){ return Math.round((Date.parse(a + 'T12:00:00Z') - Date.parse(da + 'T12:00:00Z')) / 86400000); }
function scPiuGiorni(iso, n){ var d = new Date(iso + 'T12:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); }
function scAnticipo(f, cfg){
  var v = f.avvisoGiorni != null ? f.avvisoGiorni : f.avviso_giorni;
  if(v === null || v === undefined || v === '') v = (cfg && cfg.giorni != null) ? cfg.giorni : 3;
  return parseInt(v, 10);
}
function scAvvisiDelGiorno(fatture, cfg, oggi){
  cfg = cfg || {}; var out = [];
  (fatture || []).forEach(function(f){
    var st = scStato(f); if(!scPagabile(f) || st === 'pagata' || st === 'annullata') return;
    var ant = scAnticipo(f, cfg); if(!(ant >= 0)) return;
    scScadenze(f, fatture).forEach(function(s){
      if(s.pagata) return;
      var g = scGiorni(oggi, s.data);
      if(ant > 0 && g === ant) out.push({ f: f, s: s, tipo: 'prima', giorni: g });
      else if(g === 0 && cfg.giorno !== false) out.push({ f: f, s: s, tipo: 'oggi', giorni: 0 });
      else if(g === -1 && cfg.scaduta !== false) out.push({ f: f, s: s, tipo: 'scaduta', giorni: -1 });
    });
  });
  return out.sort(function(a, b){ return a.giorni - b.giorni || (a.s.data < b.s.data ? -1 : 1); });
}
var SC_METODI = { contanti: 'in contanti', bonifico: 'con bonifico', carta: 'con carta' };
function scFraseAvviso(a, fmtEur){
  var s = a.s, f = a.f, e = fmtEur || function(n){ return '€ ' + (+n).toLocaleString('it-IT', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); };
  var quando = a.tipo === 'scaduta' ? 'Scaduta ieri' : a.tipo === 'oggi' ? 'Oggi' : (a.giorni === 1 ? 'Domani' : 'Tra ' + a.giorni + ' giorni');
  var rata = s.tot > 1 ? (s.saldo ? ', saldo' : ', rata ' + s.n + ' di ' + s.tot) : '';
  var cosa, scad = a.tipo === 'scaduta';
  if(s.metodo === 'assegno') cosa = 'assegno' + (s.assegno ? ' n° ' + s.assegno : '') + ' di ' + e(s.residuo) + (scad ? ': non risulta ancora incassato' : ': tieni i fondi sul conto');
  else if(s.metodo === 'sdd' || s.metodo === 'rid') cosa = 'addebito SDD di ' + e(s.residuo) + (scad ? ': non risulta ancora addebitato' : ' sul conto');
  else cosa = e(s.residuo) + (scad ? ' non risulta ancora pagata' : ' da pagare' + (SC_METODI[s.metodo] ? ' ' + SC_METODI[s.metodo] : ''));
  return quando + ' · ' + (f.fornitore || '—') + ' n° ' + (f.numero || '—') + rata + ' — ' + cosa;
}

export { scR2, scNcUsi, scNcCredito, scNcSuFattura, scConti, scScadenze, scProssima, scGiorni, scPiuGiorni, scAnticipo, scAvvisiDelGiorno, scFraseAvviso, scPagabile, scStato };
