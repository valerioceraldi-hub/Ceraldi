#!/usr/bin/env python3
"""Genera la pagina statica del menu per i clienti dai dati del database (o da un export JSON).
Uso:  MENU_SB_URL=https://xxx.supabase.co MENU_SB_KEY=<chiave anon> python3 menu_genera.py --out DIR [--lingua it|en] [--copia-foto] [--esporta-json F]
      python3 menu_genera.py --json F --out DIR           (senza rete, per i test)
Il modello (menu_template.html) non contiene nomi, testi, prodotti o colori di nessuna attività: tutto arriva dai dati."""
import argparse, json, os, re, sys, time, hashlib, datetime, urllib.request, urllib.error, urllib.parse
QUI = os.path.dirname(os.path.abspath(__file__))
TAB = ['menu_sezioni','menu_categorie','menu_voci','menu_varianti','menu_voci_allergeni','allergeni','menu_disponibilita',
       'menu_pagine','menu_blocchi','menu_raccomandazioni','menu_momenti','menu_momenti_voci','locale']
# testi fissi neutri (stessa chiave del pannello: CT_TESTI). Chi non compila nulla ottiene questi.
DEF_IT = dict(aggiungi='Aggiungi', aggiunto='Aggiunto ✓', abbinamento='Abbinamento', consiglio='Consiglio', proposte='Proposte di oggi',
  proposta_etichetta='Proposta', scorri='Scorri', ordinazione='Il mio ordine', ordinazione_intro='Vorrei:', mostra_altre='Mostra altre', cerca='Cerca nel menu',
  allergeni='In caso di allergie o intolleranze chiedi al personale.', menu='Menu', sezione_invito='Scegli una sezione', menu_vuoto='Il menu è in preparazione.',
  voci='voci', tel='Tel.', nota_prezzi='', finito='Finito', chiudi='Chiudi', allergeni_dichiarati='Allergeni dichiarati:', nessun_allergene='Nessun allergene dichiarato.',
  foto_illustrativa='Foto illustrativa', infusione='Infusione', prodotto='prodotto', prodotti='prodotti', vedi='Vedi', promemoria="Un promemoria sul tuo telefono: l'ordine non viene inviato.",
  totale='Totale', mostra_personale='Mostra al personale', ordine_vuoto='Non hai ancora aggiunto nulla.', per_personale='Per il personale', grazie='Grazie!', torna_menu='Torna al menu')
DEF_EN = dict(aggiungi='Add', aggiunto='Added ✓', abbinamento='Pairs well with', consiglio='Suggestion', proposte="Today's picks", proposta_etichetta='Pick', scorri='Swipe',
  ordinazione='My order', ordinazione_intro="I'd like:", mostra_altre='Show more', cerca='Search the menu', allergeni='If you have allergies or intolerances, please ask our staff.',
  menu='Menu', sezione_invito='Choose a section', menu_vuoto='The menu is being prepared.', voci='items', tel='Tel.', nota_prezzi='', finito='Sold out', chiudi='Close',
  allergeni_dichiarati='Declared allergens:', nessun_allergene='No declared allergens.', foto_illustrativa='Illustrative photo', infusione='Brewing', prodotto='item', prodotti='items',
  vedi='View', promemoria='A reminder on your phone: the order is not sent.', totale='Total', mostra_personale='Show to staff', ordine_vuoto='You have not added anything yet.',
  per_personale='For the staff', grazie='Thank you!', torna_menu='Back to menu')

def scarica(url, chiave, rpc=False):
    def rich(u, extra=None, dati=None):
        h = {'apikey': chiave, 'Authorization': 'Bearer ' + chiave}; h.update(extra or {})
        return json.load(urllib.request.urlopen(urllib.request.Request(u, data=dati, headers=h), timeout=60))
    out = {}
    for t in TAB:
        righe, da = [], 0
        while True:
            r = rich('%s/rest/v1/%s?select=*' % (url, t), {'Range-Unit': 'items', 'Range': '%d-%d' % (da, da + 999)})
            righe += r
            if len(r) < 1000: break
            da += 1000
        out[t] = righe
    out['config'] = rich(url + '/rest/v1/rpc/menu_config_pubblica', {'Content-Type': 'application/json'}, b'{}')
    return out

def file_esiste(url, cache={}):
    """Vero solo se l'indirizzo risponde 200: la foto grande (-1200) esiste solo per una parte delle voci."""
    if url in cache: return cache[url]
    for tent in range(4):
        try:
            cache[url] = urllib.request.urlopen(urllib.request.Request(url, method='HEAD'), timeout=30).status == 200
            return cache[url]
        except urllib.error.HTTPError as e:
            if e.code in (400, 403, 404): cache[url] = False; return False   # file assente (Supabase Storage risponde 400 per un oggetto che non esiste)
            err = 'HTTP %s' % e.code
        except Exception as e:
            err = type(e).__name__
        time.sleep(1 + tent)
    sys.exit('Verifica foto non riuscita (%s): %s. Riprova: non genero una pagina con foto scartate per un errore di rete.' % (err, url))

def costruisci(src, lingua, foto_base, esiste=None):
    en = lingua == 'en'
    def L(r, k):  # campo nella lingua scelta, con ripiego sull'italiano
        return ((r.get(k + '_en') if en else None) or r.get(k) or '')
    cfg = src.get('config') or {}
    DEF = DEF_EN if en else DEF_IT
    testi = {k: (v.get('en') if en else v.get('it')) for k, v in (cfg.get('testi') or {}).items() if isinstance(v, dict) and (v.get('en') if en else v.get('it'))}
    def U(p):  # percorso foto del bucket -> indirizzo
        return foto_base + p if p else None
    def grande(p):
        u = U(re.sub(r'-320\.(webp|jpg)$', r'-1200.\1', p)) if p and re.search(r'-320\.(webp|jpg)$', p) else None
        return u if u and (esiste is None or esiste(u)) else None  # senza file grande resta la miniatura
    oggi = datetime.date.today().isoformat()
    pub = lambda r: r.get('stato') == 'pubblicato'
    ordina = lambda l: sorted(l, key=lambda r: (r.get('ordine') or 0, r.get('id') or 0))
    nomi = {a['id']: a for a in src['allergeni']}
    al_di = {}
    for x in src['menu_voci_allergeni']: al_di.setdefault(x['voce_id'], []).append(x['allergene_id'])
    var_di = {}
    for x in ordina(src['menu_varianti']):
        if x.get('attiva') is not False: var_di.setdefault(x['voce_id'], []).append({'g': x.get('gruppo') or '', 'n': x['nome'], 'd': x.get('delta_cent') or 0})
    disp_v, disp_c = {}, {}
    for x in src['menu_disponibilita']:
        r = {k: v for k, v in dict(g=x.get('giorni'), dal=x.get('dal'), al=x.get('al'), da=(x.get('dalle') or '')[:5] or None, a=(x.get('alle') or '')[:5] or None).items() if v}
        (disp_v if x.get('voce_id') else disp_c).setdefault(x.get('voce_id') or x.get('categoria_id'), []).append(r)
    sezioni = []
    for s in ordina([s for s in src['menu_sezioni'] if pub(s)]):
        cats = []
        for c in ordina([c for c in src['menu_categorie'] if pub(c) and c['sezione_id'] == s['id']]):
            voci = []
            for v in ordina([v for v in src['menu_voci'] if pub(v) and v['categoria_id'] == c['id']]):
                es = bool(v.get('esaurito_fino')) and str(v['esaurito_fino'])[:10] >= oggi
                al = None
                if v.get('allergeni_verificati_il'):
                    al = [nomi[i]['nome'] for i in al_di.get(v['id'], []) if i in nomi and nomi[i].get('tipo') == 'allergene']
                o = {'id': v['id'], 'n': L(v, 'nome'), 'd': L(v, 'descrizione'), 'p': v.get('prezzo_cent') or 0, 'f': U(v.get('foto_path')), 'fg': grande(v.get('foto_path')),
                     'fa': v.get('foto_alt') or '', 'ft': v.get('foto_tipo') or '', 'b': v.get('badge') or [], 'es': es, 'al': al, 'var': var_di.get(v['id'], []),
                     'dp': (disp_v.get(v['id'], []) + disp_c.get(c['id'], []))}
                if v.get('proposta_giorno'): o['pr'] = {'pos': v.get('proposta_posizione') or 'home', 'ord': v.get('proposta_ordine') or 0}
                voci.append(o)
            if voci: cats.append({'id': c['id'], 'n': L(c, 'nome'), 'd': L(c, 'descrizione'), 'f': U(c.get('foto_path')), 'v': voci})
        if cats: sezioni.append({'id': s['id'], 'n': L(s, 'nome'), 'f': U(s.get('foto_path')), 'c': cats})
    ids = {v['id'] for s in sezioni for c in s['c'] for v in c['v']}
    pagine = {}
    for p in ordina(src['menu_pagine']):
        if p.get('attiva') is False: continue
        bl = [{'tipo': b['tipo'], 'pos': b['posizione'], 'ruolo': ((b.get('stile') or {}).get('ruolo') if p['codice'] == 'home' and b['posizione'] == 'alto' and (b.get('stile') or {}).get('ruolo') in ('logo', 'sfondo') else None), 'sopra': L(b, 'sopratitolo'), 'titolo': L(b, 'titolo'), 'testo': L(b, 'testo'), 'f': b.get('foto_url'),
               'fa': L(b, 'foto_alt'), 'lt': L(b, 'link_testo'), 'lu': b.get('link_url'), 'lp': b.get('link_pagina')} for b in ordina(src['menu_blocchi']) if b['pagina'] == p['codice'] and b.get('attivo') is not False]
        pagine[p['codice']] = {'titolo': L(p, 'titolo'), 'blocchi': bl}
    for b in pagine.values():
        for x in b['blocchi']:
            if x['lp'] and x['lp'] not in pagine: x['lp'] = None
    momenti = []
    for m in ordina(src['menu_momenti']):
        if m.get('attivo') is False: continue
        vs = [x['voce_id'] for x in sorted(src['menu_momenti_voci'], key=lambda x: (x.get('ordine') or 0, x['id'])) if x['momento_id'] == m['id'] and x['voce_id'] in ids]
        momenti.append({'q': m['quando'], 'da': (m.get('dalle') or '')[:5], 'a': (m.get('alle') or '')[:5], 'saluto': L(m, 'saluto'), 'intro': L(m, 'introduzione'),
                        'sopra': L(m, 'sopratitolo'), 'titolo': L(m, 'titolo'), 'testo': L(m, 'testo'), 'f': m.get('foto_url'), 'fa': L(m, 'foto_alt'),
                        'pulsante': L(m, 'testo_pulsante'), 'voci': vs})
    abb, cons = {}, {}
    for r in ordina(src['menu_raccomandazioni']):
        if r.get('attivo') is False or r['target_voce_id'] not in ids: continue
        if r['tipo'] == 'abbinamento' and r.get('voce_id') in ids: abb.setdefault(r['voce_id'], []).append(r['target_voce_id'])
        elif r['tipo'] == 'consiglio_categoria' and r.get('categoria_id'): cons.setdefault(r['categoria_id'], []).append(r['target_voce_id'])
    lo = (src.get('locale') or [{}])[0]
    ori = lo.get('orari') or {}
    d = {'testi': testi, 'locale': {'nome': lo.get('nome') or '', 'ind': lo.get('indirizzo') or '', 'tel': lo.get('telefono') or '', 'orari': (ori.get('testo_en') if en else None) or ori.get('testo') or ''},
         'sezioni': sezioni, 'pagine': pagine, 'momenti': momenti, 'abb': {'v': abb, 'c': {}}, 'consigli': cons}
    return d, DEF, cfg

HEX = re.compile(r'^#[0-9a-fA-F]{3,8}$')
def blocco_var(o):
    return ''.join('--%s:%s;' % (k, v) for k, v in (o or {}).items() if re.match(r'^[a-z0-9-]+$', k) and HEX.match(str(v)))
def tema_css(cfg):
    a = cfg.get('aspetto') or {}
    car = a.get('caratteri') or {}
    ok = lambda n: n if n and re.match(r'^[A-Za-z0-9 ]+$', n) else None
    ft, fx = ok(car.get('titoli')), ok(car.get('testo'))
    css = ':root{' + blocco_var(a.get('globale'))
    if ft: css += '--f-display:"%s",Georgia,serif;' % ft
    if fx: css += '--f-testo:"%s",system-ui,sans-serif;' % fx
    css += '}'
    try: sc = float(a.get('scala') or 1)
    except Exception: sc = 1
    if sc != 1 and 0.7 <= sc <= 1.6: css += 'html{font-size:%s%%}' % round(100 * sc, 1)
    if blocco_var(a.get('home')): css += '.vh{%s}' % blocco_var(a['home'])
    for i, o in (a.get('sezioni') or {}).items():
        if re.match(r'^\d+$', str(i)) and blocco_var(o): css += '.sezv[data-s="%s"]{%s}' % (i, blocco_var(o))
    for i, o in (a.get('categorie') or {}).items():
        if re.match(r'^\d+$', str(i)) and blocco_var(o): css += '#c%s{%s}' % (i, blocco_var(o))
    fam = ['%s:wght@400;500' % ft.replace(' ', '+')] if ft else []
    if fx and fx != ft: fam.append('%s:wght@400;500;600' % fx.replace(' ', '+'))
    link = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?%s&display=swap">' % '&'.join('family=' + f for f in fam) if fam else ''
    return css, link

def copia_foto(d, out):
    """Scarica le foto usate nella cartella img/ accanto alla pagina e riscrive gli indirizzi (i visitatori non toccano mai il database)."""
    cart = os.path.join(out, 'img'); os.makedirs(cart, exist_ok=True); fatte = {}
    def loc(u):
        if not u or not u.startswith('http'): return u
        if u not in fatte:
            ext = os.path.splitext(urllib.parse.urlparse(u).path)[1] or '.webp'
            n = hashlib.sha1(u.encode()).hexdigest()[:12] + ext
            with open(os.path.join(cart, n), 'wb') as f: f.write(urllib.request.urlopen(u, timeout=60).read())
            fatte[u] = 'img/' + n
        return fatte[u]
    for s in d['sezioni']:
        s['f'] = loc(s['f'])
        for c in s['c']:
            c['f'] = loc(c['f'])
            for v in c['v']: v['f'] = loc(v['f']); v['fg'] = loc(v['fg'])
    for p in d['pagine'].values():
        for b in p['blocchi']: b['f'] = loc(b['f'])
    for m in d['momenti']: m['f'] = loc(m['f'])
    return len(fatte)

def json_js(o): return json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True); ap.add_argument('--lingua', default='it', choices=['it', 'en']); ap.add_argument('--json'); ap.add_argument('--esporta-json')
    ap.add_argument('--copia-foto', action='store_true'); ap.add_argument('--modello', default=os.path.join(QUI, 'menu_template.html'))
    a = ap.parse_args()
    if a.json: src = json.load(open(a.json, encoding='utf-8'))
    else:
        url, k = os.environ.get('MENU_SB_URL'), os.environ.get('MENU_SB_KEY')
        if not url or not k: sys.exit('Imposta MENU_SB_URL e MENU_SB_KEY (chiave anon pubblica) oppure usa --json')
        src = scarica(url.rstrip('/'), k); src['_url'] = url.rstrip('/')
    if a.esporta_json: json.dump(src, open(a.esporta_json, 'w', encoding='utf-8'), ensure_ascii=False)
    base = (src.get('_url') or os.environ.get('MENU_SB_URL', '')).rstrip('/') + '/storage/v1/object/public/menu-foto/'
    d, DEF, cfg = costruisci(src, a.lingua, base, None if a.json else file_esiste)  # --json = prove senza rete: nessun controllo
    n = copia_foto(d, a.out) if a.copia_foto else 0
    css, link = tema_css(cfg)
    t = open(a.modello, encoding='utf-8').read()
    titolo = d['locale']['nome'] or 'Menu'
    for k, v in (('__LANG__', a.lingua), ('__TITOLO__', titolo.replace('<', '')), ('__FONT_LINK__', link), ('__TEMA_CSS__', css), ('__DATI__', json_js(d)), ('__DEF__', json_js(DEF))):
        t = t.replace('/*' + k + '*/null' if k in ('__DATI__', '__DEF__') else k, v)
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, 'index.html'), 'w', encoding='utf-8').write(t)
    print('ok: %s/index.html  sezioni=%d voci=%d pagine=%d momenti=%d foto copiate=%d' % (a.out, len(d['sezioni']), sum(len(c['v']) for s in d['sezioni'] for c in s['c']), len(d['pagine']), len(d['momenti']), n))
if __name__ == '__main__': main()
