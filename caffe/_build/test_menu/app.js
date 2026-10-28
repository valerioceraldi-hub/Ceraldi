(function(){
var D = /*__DATI__*/null, DEF = /*__DEF__*/null;
function T(k){ var t = D.testi && D.testi[k]; return t ? t : (DEF[k] || ''); }
function esc(s){ return String(s == null ? '' : s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function prezzo(c){ if(c == null) return ''; return c % 100 === 0 ? String(c / 100) : (c / 100).toFixed(2).replace('.', ','); }
function pulisci(n){ return String(n || '').replace(/\s*⏳.*$/, '').trim(); }
function nota(n){ var m = String(n || '').match(/⏳\s*(.*)$/); return m ? (T('infusione') + ' ' + m[1].replace(/mim/, 'min').replace('/', '–').trim()).trim() : ''; }
function img(src, alt, cls){ return src ? '<img' + (cls ? ' class="' + cls + '"' : '') + ' src="' + esc(src) + '" alt="' + esc(alt || '') + '" loading="lazy" decoding="async">' : '<span class="vu" aria-hidden="true"></span>'; }
function min(h){ var p = String(h || '0:0').split(':'); return (+p[0]) * 60 + (+p[1] || 0); }
function p2(n){ return (n < 10 ? '0' : '') + n; }
var VOCI = {}, CATDI = {};
D.sezioni.forEach(function(s){ s.c.forEach(function(c){ c.v.forEach(function(v){ VOCI[v.id] = v; CATDI[v.id] = c; }); }); });
function dispOk(v){
  if(!v.dp || !v.dp.length) return true;
  var n = new Date(), m = n.getHours() * 60 + n.getMinutes(), dow = (n.getDay() + 6) % 7 + 1, iso = n.getFullYear() + '-' + p2(n.getMonth() + 1) + '-' + p2(n.getDate());
  return v.dp.some(function(r){
    if(r.g && r.g.length && r.g.indexOf(dow) < 0) return false;
    if(r.dal && iso < r.dal) return false; if(r.al && iso > r.al) return false;
    if(r.da && r.a){ var a = min(r.da), b = min(r.a); if(a <= b ? !(m >= a && m < b) : !(m >= a || m < b)) return false; }
    return true; });
}
var S = { vista: 'home', sez: null, pag: null, ord: {} };
try{ S.ord = JSON.parse(localStorage.getItem('menu_ord') || '{}') || {}; }catch(e){ S.ord = {}; }
function salvaOrd(){ try{ localStorage.setItem('menu_ord', JSON.stringify(S.ord)); }catch(e){} }

/* momento della giornata: la prima fascia che corrisponde all'ora; se nessuna, quello «quando nessuna fascia corrisponde» */
function mom(){
  var n = new Date(), m = n.getHours() * 60 + n.getMinutes(), altro = null;
  for(var i = 0; i < (D.momenti || []).length; i++){
    var x = D.momenti[i];
    if(x.q === 'chiuso'){ if(!altro) altro = x; continue; }
    var a = min(x.da), b = min(x.a); if(a <= b ? (m >= a && m < b) : (m >= a || m < b)) return x;
  }
  return altro;
}

/* blocchi */
function lnk(b){ if(b.lp) return { t: 'button', a: ' type="button" data-pag="' + esc(b.lp) + '"' }; if(b.lu) return { t: 'a', a: ' href="' + esc(b.lu) + '" target="_blank" rel="noopener"' }; return null; }
function corpoBlocco(b){ return (b.sopra ? '<span class="ey">' + esc(b.sopra) + '</span>' : '') + (b.titolo ? '<h3>' + esc(b.titolo) + '</h3>' : '') + (b.testo ? '<p>' + esc(b.testo) + '</p>' : ''); }
function blocco(b){
  var L = lnk(b), btn = L && b.lt ? '<' + L.t + L.a + ' class="btn oro">' + esc(b.lt) + '</' + L.t + '>' : '';
  if(b.tipo === 'banner' || b.tipo === 'link_pagina'){
    var inner = (b.f ? img(b.f, b.fa) : '') + '<span>' + corpoBlocco(b) + (b.lt ? '<span class="go">' + esc(b.lt) + ' ›</span>' : '') + '</span>';
    return L ? '<' + L.t + L.a + ' class="blk b' + (b.f ? '' : ' sf') + '">' + inner + '</' + L.t + '>' : '<div class="blk b' + (b.f ? '' : ' sf') + '">' + inner + '</div>';
  }
  if(b.tipo === 'testo_foto') return '<section class="blk tf">' + (b.f ? img(b.f, b.fa) : '') + '<div class="tx gut">' + corpoBlocco(b) + btn + '</div></section>';
  if(b.tipo === 'foto'){ var im = img(b.f, b.fa); return '<figure class="blk f" style="margin-block:26px 0">' + (L ? '<' + L.t + L.a + '>' + im + '</' + L.t + '>' : im) + '</figure>'; }
  return '<div class="blk t gut">' + corpoBlocco(b) + btn + '</div>';
}
function blocchi(cod, pos){ var p = D.pagine[cod]; return p ? p.blocchi.filter(function(b){ return !pos || b.pos === pos; }).map(blocco).join('') : ''; }

/* home */
function copertina(m){
  var s = m && m.saluto, h = '<header class="cop gut"><div class="in">' + (s && D.locale.nome ? '<div class="nome">' + esc(D.locale.nome) + '</div>' : '');
  h += '<h1>' + esc(s || D.locale.nome || '') + '</h1>' + (m && m.intro ? '<p class="sal">' + esc(m.intro) + '</p>' : '') + blocchi('home', 'alto') + '</div></header>';
  return h;
}
function momentoHtml(m){
  if(!m || (!m.titolo && !m.testo && !(m.voci || []).length && !m.f)) return '';
  var vs = (m.voci || []).map(function(id){ return VOCI[id]; }).filter(function(v){ return v && dispOk(v) && !v.es; });
  var tot = vs.reduce(function(t, v){ return t + (v.p || 0); }, 0);
  return '<section class="mom">' + (m.f ? '<div class="ft">' + img(m.f, m.fa) + '</div>' : '') + '<div class="tx"' + (m.f ? '' : ' style="margin-top:0;padding-top:20px"') + '>' +
    (m.sopra ? '<span class="ey">' + esc(m.sopra) + '</span>' : '') + (m.titolo ? '<h2>' + esc(m.titolo) + '</h2>' : '') + (m.testo ? '<p>' + esc(m.testo) + '</p>' : '') +
    (vs.length ? '<div class="coppia">' + vs.map(function(v){ return '<button type="button" data-voce="' + v.id + '"><span>' + esc(pulisci(v.n)) + '</span><span class="prz">' + prezzo(v.p) + '</span></button>'; }).join('') + '</div>' +
      '<div class="cta"><button type="button" class="btn oro" data-aggiungi="' + vs.map(function(v){ return v.id; }).join(',') + '">' + esc(m.pulsante || T('aggiungi')) + (vs.length > 1 ? ' · ' + prezzo(tot) : '') + '</button></div>' : '') + '</div></section>';
}
function proposteDi(pos, catId){
  var l = [];
  D.sezioni.forEach(function(s){ s.c.forEach(function(c){ if(catId && c.id !== catId) return; c.v.forEach(function(v){ if(v.pr && v.pr.pos === pos && dispOk(v) && !v.es) l.push(v); }); }); });
  return l.sort(function(a, b){ return a.pr.ord - b.pr.ord || a.id - b.id; });
}
function proposte(){
  var l = proposteDi('home'); if(!l.length) return '';
  return '<div class="gut"><div class="tit"><h3>' + esc(T('proposte')) + '</h3><span class="ey">' + esc(T('scorri')) + '</span></div></div><div class="pista" id="pista">' + l.map(function(v){
    return '<button type="button" class="pc" data-voce="' + v.id + '">' + img(v.fg || v.f, pulisci(v.n)) + '<span class="c"><span class="ey">' + esc(T('proposta_etichetta')) + '</span><span class="r"><h4>' + esc(pulisci(v.n)) + '</h4><span class="prz">' + prezzo(v.p) + '</span></span>' + (v.d ? '<span class="d">' + esc(v.d) + '</span>' : '') + '</span></button>'; }).join('') +
    '</div><div class="punti" aria-hidden="true">' + l.map(function(_, i){ return '<i' + (i ? '' : ' class="on"') + '></i>'; }).join('') + '</div>';
}
function tavola(s){
  var n = s.c.reduce(function(t, c){ return t + c.v.length; }, 0), f = s.f;
  if(!f) s.c.some(function(c){ return c.v.some(function(v){ if(v.f){ f = v.f; return true; } }); });
  var nomi = s.c.slice(0, 4).map(function(c){ return pulisci(c.n); }).join(' · ');
  return '<button type="button" class="tav' + (f ? '' : ' senza') + '" data-sez="' + s.id + '">' + (f ? '<img src="' + esc(f) + '" alt="">' : '') + '<span class="t"><small>' + n + ' ' + esc(T('voci')) + '</small><h3>' + esc(pulisci(s.n)) + '</h3><span class="q">' + esc(nomi) + (s.c.length > 4 ? '…' : '') + '</span></span></button>';
}
function piede(){
  var L = D.locale, riga2 = [L.orari, L.tel ? T('tel') + ' ' + L.tel : ''].filter(Boolean).join(' · ');
  return '<footer class="piede gut">' + (L.ind ? '<b>' + esc(L.ind) + '</b>' : '') + (riga2 ? '<span>' + esc(riga2) + '</span>' : '') + (T('nota_prezzi') ? '<span>' + esc(T('nota_prezzi')) + '</span>' : '') + '</footer>';
}
function home(){
  var m = mom(), h = '<div class="vh">' + copertina(m) + momentoHtml(m) + proposte() + blocchi('home', 'dopo_proposte');
  if(D.sezioni.length) h += '<div class="gut"><div class="tit"><h3>' + esc(T('menu')) + '</h3><span class="ey">' + esc(T('sezione_invito')) + '</span></div><div class="tavole">' + D.sezioni.map(tavola).join('') + '</div></div>';
  else h += '<p class="vuoto-menu">' + esc(T('menu_vuoto')) + '</p>';
  return h + blocchi('home', 'dopo_sezioni') + blocchi('home', 'piede') + piede() + '</div>';
}

/* sezione */
var _aperte = {};
function sezione(){
  var s = D.sezioni.find(function(x){ return x.id === S.sez; }); if(!s) return home();
  var h = '<div class="sezv" data-s="' + s.id + '"><div class="bar gut" id="bar"><div class="r"><button type="button" class="ind" data-home>‹ ' + esc(T('menu')) + '</button><h2>' + esc(pulisci(s.n)) + '</h2></div>' +
    '<div class="chips" id="chips">' + s.c.map(function(c, i){ return '<button type="button" data-vai="c' + c.id + '"' + (i ? '' : ' class="on"') + '>' + esc(pulisci(c.n)) + '</button>'; }).join('') + '</div></div><main class="gut" style="padding-bottom:130px">';
  s.c.forEach(function(c){ h += categoria(c); });
  return h + (T('nota_prezzi') ? '<p class="piede" style="padding:26px 0 0">' + esc(T('nota_prezzi')) + '</p>' : '') + '</main></div>';
}
function categoria(c){
  var pc = proposteDi('categoria', c.id), cons = ((D.consigli || {})[c.id] || []).filter(function(id){ return VOCI[id] && dispOk(VOCI[id]) && !VOCI[id].es && pc.indexOf(VOCI[id]) < 0; });
  var mostrati = pc.map(function(v){ return v.id; }).concat(cons);
  var resto = c.v.filter(function(v){ return mostrati.indexOf(v.id) < 0; });
  var lungo = resto.length > 14 && !_aperte[c.id], vis = lungo ? resto.slice(0, 10) : resto;
  var h = '<section class="cat" id="c' + c.id + '"><h3>' + esc(pulisci(c.n)) + '</h3>' + (nota(c.n) ? '<p class="nota">' + esc(nota(c.n)) + '</p>' : '') + (c.d ? '<p class="desc">' + esc(c.d) + '</p>' : '');
  h += pc.map(function(v){ return evidenza(v, T('proposta_etichetta')); }).join('') + cons.map(function(id){ return evidenza(VOCI[id], T('consiglio')); }).join('');
  h += '<ul class="righe">' + vis.filter(dispOk).map(riga).join('') + '</ul>';
  if(lungo) h += '<button type="button" class="altre" data-apri="' + c.id + '">' + esc(T('mostra_altre')) + ' ' + (resto.length - 10) + '</button>';
  return h + '</section>';
}
function tags(v){ var t = (v.b || []).map(function(x){ return '<span class="tag np">' + esc(x) + '</span>'; }); if(v.es) t.push('<span class="tag fin">' + esc(T('finito')) + '</span>'); return t.join(''); }
function evidenza(v, etich){
  if(!v) return '';
  return '<button type="button" class="consiglio" data-voce="' + v.id + '">' + img(v.fg || v.f, pulisci(v.n)) + '<span class="c"><span class="ey">' + esc(etich) + '</span><span class="r"><h4>' + esc(pulisci(v.n)) + '</h4><span class="prz">' + prezzo(v.p) + '</span></span>' + (v.d ? '<span class="d">' + esc(v.d) + '</span>' : '') + (tags(v) ? '<span class="m" style="display:flex;gap:6px;margin-top:2px">' + tags(v) + '</span>' : '') + '</span></button>';
}
function riga(v){
  return '<li><button type="button" class="voce" data-voce="' + v.id + '"><span><h4>' + esc(pulisci(v.n)) + '</h4>' + (v.d ? '<span class="d">' + esc(v.d) + '</span>' : '') +
    '<span class="m"><span class="prz">' + prezzo(v.p) + '</span>' + tags(v) + '</span></span>' + (v.f ? img(v.f, '') : '') + '</button></li>';
}

/* pagine extra */
function pagina(cod){
  var p = D.pagine[cod]; if(!p) return home();
  return '<div class="pag" data-p="' + esc(cod) + '"><div class="bar gut"><div class="r"><button type="button" class="ind" data-home>‹ ' + esc(T('menu')) + '</button><h2>' + esc(p.titolo || '') + '</h2></div></div>' + p.blocchi.map(blocco).join('') + piede() + '</div>';
}

/* scheda prodotto */
function mini(id){ var v = VOCI[id]; if(!v) return ''; return '<button type="button" class="mini" data-voce="' + id + '">' + img(v.f, '') + '<span><b>' + esc(pulisci(v.n)) + '</b><span>' + prezzo(v.p) + '</span></span></button>'; }
function apriVoce(id){
  var v = VOCI[id]; if(!v) return;
  var c = CATDI[id], ab = [], A = D.abb || { v: {}, c: {} };
  (A.v[id] || []).concat(A.c[c.id] || []).forEach(function(x){ if(x !== id && VOCI[x] && dispOk(VOCI[x]) && !VOCI[x].es && ab.indexOf(x) < 0) ab.push(x); });
  ab = ab.slice(0, 4);
  var al = v.al == null ? '' : (v.al.length ? '<b>' + esc(T('allergeni_dichiarati')) + '</b> ' + esc(v.al.join(', ')) + '. ' : esc(T('nessun_allergene')) + ' ');
  var vr = v.var && v.var.length ? '<ul class="vars">' + v.var.map(function(x, i){ var nuovo = i === 0 || v.var[i - 1].g !== x.g; return (nuovo && x.g ? '<li class="g">' + esc(x.g) + '</li>' : '') + '<li><span>' + esc(x.n) + '</span><span class="prz">' + (x.d > 0 ? '+' : '') + (x.d ? prezzo(x.d) : '') + '</span></li>'; }).join('') + '</ul>' : '';
  var fo = v.fg || v.f;
  var html = '<div class="velo" id="velo"><div class="foglio" role="dialog" aria-modal="true" aria-label="' + esc(pulisci(v.n)) + '">' +
    (fo ? '<div class="ft">' + img(fo, v.fa || pulisci(v.n)) + '<button type="button" class="chiudi" data-chiudi aria-label="' + esc(T('chiudi')) + '">×</button></div>' : '<div style="height:52px;position:relative"><button type="button" class="chiudi" data-chiudi aria-label="' + esc(T('chiudi')) + '">×</button></div>') +
    '<div class="c"><span class="ey" style="color:var(--accento)">' + esc(pulisci(c.n)) + '</span><h3>' + esc(pulisci(v.n)) + '</h3>' + (v.d ? '<p class="d">' + esc(v.d) + '</p>' : '') + (tags(v) ? '<span style="display:flex;gap:6px;flex-wrap:wrap">' + tags(v) + '</span>' : '') + vr +
    (fo && v.ft === 'illustrativa' ? '<span class="cap">' + esc(T('foto_illustrativa')) + '</span>' : '') +
    '<div class="all">' + al + esc(T('allergeni')) + '</div>' +
    '<div class="r"><span class="prz">' + prezzo(v.p) + '</span>' + (v.es ? '<button type="button" class="btn scuro" disabled>' + esc(T('finito')) + '</button>' : '<button type="button" class="btn scuro" data-aggiungi="' + id + '">' + esc(T('aggiungi')) + '</button>') + '</div></div>' +
    (ab.length ? '<div class="abb"><h5>' + esc(T('abbinamento')) + '</h5><div class="l">' + ab.map(mini).join('') + '</div></div>' : '') + '</div></div>';
  chiudiVelo(); document.body.insertAdjacentHTML('beforeend', html);
}
function chiudiVelo(){ var x = document.getElementById('velo'); if(x) x.remove(); var y = document.getElementById('mostra'); if(y) y.remove(); }

/* ordinazione (promemoria locale, non inviato) */
function aggiungi(ids){ ids.forEach(function(id){ S.ord[id] = (S.ord[id] || 0) + 1; }); salvaOrd(); pillola(true); }
function conta(){ return Object.keys(S.ord).reduce(function(t, k){ return t + S.ord[k]; }, 0); }
function pillola(lampo){
  var p = document.getElementById('ord'), n = conta();
  if(!n){ if(p) p.remove(); return; }
  var h = '<span class="n">' + esc(T('ordinazione')) + ' · <b>' + n + ' ' + esc(n === 1 ? T('prodotto') : T('prodotti')) + '</b></span><span class="go">' + esc(T('vedi')) + '</span>';
  if(!p){ document.body.insertAdjacentHTML('beforeend', '<button type="button" class="ord" id="ord" data-lista>' + h + '</button>'); p = document.getElementById('ord'); } else p.innerHTML = h;
  if(lampo && p.animate) p.animate([{ transform: 'translateX(-50%) scale(1)' }, { transform: 'translateX(-50%) scale(1.05)' }, { transform: 'translateX(-50%) scale(1)' }], { duration: 320 });
}
function lista(){
  var ids = Object.keys(S.ord).filter(function(k){ return S.ord[k] > 0 && VOCI[k]; });
  var tot = ids.reduce(function(t, k){ return t + VOCI[k].p * S.ord[k]; }, 0);
  var html = '<div class="velo" id="velo"><div class="foglio" role="dialog" aria-modal="true" aria-label="' + esc(T('ordinazione')) + '"><div style="position:relative;height:8px"><button type="button" class="chiudi" data-chiudi aria-label="' + esc(T('chiudi')) + '" style="top:12px">×</button></div><div class="lista">' +
    '<h3>' + esc(T('ordinazione')) + '</h3><p class="s">' + esc(T('promemoria')) + '</p>' +
    (ids.length ? ids.map(function(k){ var v = VOCI[k]; return '<div class="li"><span>' + esc(pulisci(v.n)) + '<br><span class="prz" style="font-size:.9rem">' + prezzo(v.p) + '</span></span><span class="qta"><button type="button" data-meno="' + k + '" aria-label="−">−</button><span>' + S.ord[k] + '</span><button type="button" data-piu="' + k + '" aria-label="+">+</button></span></div>'; }).join('') +
      '<div class="li" style="font-size:.86rem;color:var(--testo-2)"><span>' + esc(T('totale')) + '</span><span class="prz">' + prezzo(tot) + '</span></div>' +
      '<div class="cta"><button type="button" class="btn scuro" data-mostra style="flex:1">' + esc(T('mostra_personale')) + '</button></div>' : '<p class="s">' + esc(T('ordine_vuoto')) + '</p>') + '</div></div></div>';
  chiudiVelo(); document.body.insertAdjacentHTML('beforeend', html);
}
function mostra(){
  var ids = Object.keys(S.ord).filter(function(k){ return S.ord[k] > 0 && VOCI[k]; });
  chiudiVelo();
  document.body.insertAdjacentHTML('beforeend', '<div class="mostra" id="mostra" role="dialog" aria-modal="true" aria-label="' + esc(T('ordinazione')) + '"><span class="ey">' + esc(D.locale.nome || '') + ' · ' + esc(T('per_personale')) + '</span><h3>' + esc(T('ordinazione_intro')) + '</h3><ul>' +
    ids.map(function(k){ return '<li><b>' + S.ord[k] + '×</b><span>' + esc(pulisci(VOCI[k].n)) + '</span></li>'; }).join('') + '</ul><div class="g">' + esc(T('grazie')) + '</div><div class="cta"><button type="button" class="btn vuoto" data-chiudi style="color:var(--accento-chiaro)">' + esc(T('torna_menu')) + '</button></div></div>');
}

/* navigazione */
function daHash(){ var h = location.hash, m; if((m = /^#p-([a-z0-9-]+)$/.exec(h)) && D.pagine[m[1]]){ S.vista = 'pag'; S.pag = m[1]; } else if((m = /^#s-(\d+)$/.exec(h)) && D.sezioni.some(function(s){ return s.id === +m[1]; })){ S.vista = 'sez'; S.sez = +m[1]; } }
function vai(st){ Object.assign(S, st); disegna(true); try{ history.pushState({ vista: S.vista, sez: S.sez, pag: S.pag }, ''); }catch(e){} }
window.addEventListener('popstate', function(e){ var st = e.state || { vista: 'home' }; S.vista = st.vista; S.sez = st.sez; S.pag = st.pag; chiudiVelo(); disegna(true); });
function disegna(inCima){
  document.getElementById('app').innerHTML = S.vista === 'sez' ? sezione() : S.vista === 'pag' ? pagina(S.pag) : home();
  if(inCima) window.scrollTo(0, 0);
  pillola(false); avviaPista(); spia();
}
var _pT = null;
function avviaPista(){
  clearInterval(_pT); var p = document.getElementById('pista'); if(!p) return;
  var punti = document.querySelectorAll('.punti i'), fermo = false;
  function k(){ var w = p.children[0].getBoundingClientRect().width + 12; return Math.round(p.scrollLeft / w); }
  p.addEventListener('scroll', function(){ var i = k(); punti.forEach(function(x, j){ x.className = i === j ? 'on' : ''; }); }, { passive: true });
  ['pointerdown', 'touchstart', 'wheel', 'focusin'].forEach(function(ev){ p.addEventListener(ev, function(){ fermo = true; }, { passive: true }); });
  if(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches || p.children.length < 2) return;
  _pT = setInterval(function(){ if(fermo || !document.body.contains(p)) return; var w = p.children[0].getBoundingClientRect().width + 12, n = (k() + 1) % p.children.length; p.scrollTo({ left: n * w, behavior: 'smooth' }); }, 5000);
}
var _spia = null;
function spia(){
  if(_spia) _spia.disconnect(); var chips = document.getElementById('chips'); if(!chips || !('IntersectionObserver' in window)) return;
  _spia = new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting){ chips.querySelectorAll('button').forEach(function(b){ var on = b.dataset.vai === e.target.id; b.classList.toggle('on', on); if(on){ var x = b.offsetLeft - (chips.clientWidth - b.offsetWidth) / 2; chips.scrollTo({ left: Math.max(0, x), behavior: 'smooth' }); } }); } }); }, { rootMargin: '-140px 0px -60% 0px' });
  document.querySelectorAll('.cat').forEach(function(c){ _spia.observe(c); });
}
document.addEventListener('click', function(e){
  var t;
  if((t = e.target.closest('[data-aggiungi]'))){ aggiungi(t.dataset.aggiungi.split(',').map(Number)); t.textContent = T('aggiunto'); return; }
  if(e.target.closest('[data-chiudi]') || e.target.id === 'velo'){ chiudiVelo(); return; }
  if((t = e.target.closest('[data-piu]'))){ S.ord[t.dataset.piu]++; salvaOrd(); lista(); pillola(false); return; }
  if((t = e.target.closest('[data-meno]'))){ S.ord[t.dataset.meno]--; if(S.ord[t.dataset.meno] <= 0) delete S.ord[t.dataset.meno]; salvaOrd(); lista(); pillola(false); return; }
  if(e.target.closest('[data-mostra]')){ mostra(); return; }
  if(e.target.closest('[data-lista]')){ lista(); return; }
  if((t = e.target.closest('[data-pag]'))){ chiudiVelo(); vai({ vista: 'pag', pag: t.dataset.pag }); return; }
  if(e.target.closest('[data-home]')){ vai({ vista: 'home' }); return; }
  if((t = e.target.closest('[data-sez]'))){ vai({ vista: 'sez', sez: +t.dataset.sez }); return; }
  if((t = e.target.closest('[data-apri]'))){ _aperte[t.dataset.apri] = true; var y = window.scrollY; disegna(false); window.scrollTo(0, y); return; }
  if((t = e.target.closest('[data-vai]'))){ var el = document.getElementById(t.dataset.vai); if(el) el.scrollIntoView({ behavior: 'smooth' }); return; }
  if((t = e.target.closest('[data-voce]'))){ apriVoce(+t.dataset.voce); return; }
});
document.addEventListener('keydown', function(e){ if(e.key === 'Escape') chiudiVelo(); });
window.addEventListener('hashchange', function(){ daHash(); disegna(true); });
daHash(); disegna(false);
})();
