#!/usr/bin/env python3
"""Genera la pagina statica del menu per i clienti dai dati del database (o da un export JSON).
Uso:  MENU_SB_URL=https://xxx.supabase.co MENU_SB_KEY=<chiave anon> python3 menu_genera.py --out DIR [--lingua it|en] [--copia-foto] [--esporta-json F]
      python3 menu_genera.py --json F --out DIR           (senza rete, per i test)
Il modello (menu_template.html) non contiene nomi, testi, prodotti o colori di nessuna attività: tutto arriva dai dati."""
import argparse, json, os, re, sys, time, hashlib, datetime, shutil, urllib.request, urllib.error, urllib.parse
QUI = os.path.dirname(os.path.abspath(__file__))
RUOLI = ('logo', 'sfondo', 'motivo')  # foto «in alto» che compongono la testata di una pagina
TAB = ['menu_sezioni','menu_categorie','menu_voci','menu_varianti','menu_voci_allergeni','allergeni','menu_disponibilita',
       'menu_pagine','menu_blocchi','menu_raccomandazioni','menu_momenti','menu_momenti_voci','locale','menu_lingue','menu_traduzioni']
# testi fissi neutri (stesse chiavi del pannello: CT_TESTI). Chi non compila nulla ottiene questi. Li legge anche il pannello per l'anteprima.
_BASE = json.load(open(os.path.join(QUI, 'menu_testi_base.json'), encoding='utf-8'))
DEF_IT, DEF_EN = _BASE['it'], _BASE['en']
ITALIANO = {'c': 'it', 'n': 'Italiano', 'b': '🇮🇹'}

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

def wifi_dati(lo):
    """Wi-Fi OSPITI dal locale: solo se acceso e completo. QR standard (WIFI:...) disegnato qui come SVG, se c'è la libreria segno."""
    w = lo.get('wifi') or {}
    rete, pw = (w.get('rete') or '').strip(), (w.get('password') or '').strip()
    if not w.get('mostra') or not rete: return None
    e = lambda x: re.sub(r'([\\;,:"])', r'\\\1', x)
    qr = None
    try:
        import segno, io
        b = io.BytesIO(); segno.make('WIFI:T:%s;S:%s;%s;' % ('WPA' if pw else 'nopass', e(rete), ('P:' + e(pw) + ';') if pw else ''), error='m').save(b, kind='svg', scale=1, border=2, xmldecl=False, svgns=True, omitsize=True, dark='#000', light='#fff')
        qr = b.getvalue().decode('utf-8')
    except Exception as x:
        print('QR Wi-Fi non generato:', x)
    return {'rete': rete, 'pw': pw, 'qr': qr}

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

def costruisci(src, lingua, foto_base, esiste=None, lingue=None):
    nuove = 'menu_traduzioni' in src  # tabella delle traduzioni; senza (vecchi export) valgono le colonne *_en
    TR = {(t['tabella'], str(t['riga_id']), t['campo']): t['testo'] for t in src.get('menu_traduzioni', []) if t.get('lingua') == lingua and t.get('testo')}
    def L(r, k, tab=None):  # campo nella lingua scelta, con ripiego sull'italiano (mai vuoto se l'italiano c'è)
        if lingua == 'it': return r.get(k) or ''
        if nuove:
            x = TR.get((tab, str(r['codice'] if tab == 'menu_pagine' else r.get('id')), k))
            return x or r.get(k) or ''
        return (r.get(k + '_en') if lingua == 'en' else None) or r.get(k) or ''
    def LV(v, k):  # voce: «non tradurre» per prodotto (traduzione = nome_fisso / tutto_fisso)
        m = v.get('traduzione') or 'auto'
        if m == 'tutto_fisso' or (m == 'nome_fisso' and k == 'nome'): return v.get(k) or ''
        return L(v, k, 'menu_voci')
    cfg = src.get('config') or {}
    DEF = _BASE.get(lingua) or DEF_EN
    testi = {k: v.get(lingua) for k, v in (cfg.get('testi') or {}).items() if isinstance(v, dict) and v.get(lingua)}
    def U(p):  # percorso foto del bucket -> indirizzo (un indirizzo https completo resta com'è)
        if not p: return None
        return p if re.match(r'^https://', p) else foto_base + p
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
                o = {'id': v['id'], 'n': LV(v, 'nome'), 'd': LV(v, 'descrizione'), 'p': v.get('prezzo_cent') or 0, 'f': U(v.get('foto_path')), 'fg': grande(v.get('foto_path')),
                     'fa': v.get('foto_alt') or '', 'ft': v.get('foto_tipo') or '', 'b': v.get('badge') or [], 'es': es, 'al': al, 'var': var_di.get(v['id'], []),
                     'dp': (disp_v.get(v['id'], []) + disp_c.get(c['id'], []))}
                if v.get('proposta_giorno'): o['pr'] = {'pos': v.get('proposta_posizione') or 'home', 'ord': v.get('proposta_ordine') or 0}
                voci.append(o)
            if voci: cats.append({'id': c['id'], 'n': L(c, 'nome', 'menu_categorie'), 'd': L(c, 'descrizione', 'menu_categorie'), 'f': U(c.get('foto_path')), 'v': voci})
        if cats: sezioni.append({'id': s['id'], 'n': L(s, 'nome', 'menu_sezioni'), 'f': U(s.get('foto_path')), 'c': cats})
    ids = {v['id'] for s in sezioni for c in s['c'] for v in c['v']}
    pagine = {}
    for p in ordina(src['menu_pagine']):
        if p.get('attiva') is False: continue
        bl = []
        for b in ordina(src['menu_blocchi']):
            if b['pagina'] != p['codice'] or b.get('attivo') is False: continue
            st = b.get('stile') if isinstance(b.get('stile'), dict) else {}
            ruolo = st.get('ruolo') if b['tipo'] == 'foto' and b['posizione'] == 'alto' and st.get('ruolo') in RUOLI else None
            # prodotti collegati al blocco (stile.voci = elenco di id): solo quelli pubblicati e visibili, nell'ordine scelto
            vs = [int(x) for x in (st.get('voci') or []) if str(x).isdigit() and int(x) in ids]
            bl.append({'tipo': b['tipo'], 'pos': b['posizione'], 'ruolo': ruolo, 'sopra': L(b, 'sopratitolo', 'menu_blocchi'), 'titolo': L(b, 'titolo', 'menu_blocchi'), 'testo': L(b, 'testo', 'menu_blocchi'), 'f': U(b.get('foto_url')),
                       'fa': L(b, 'foto_alt', 'menu_blocchi'), 'lt': L(b, 'link_testo', 'menu_blocchi'), 'lu': b.get('link_url'), 'lp': b.get('link_pagina'), 'voci': vs})
        pagine[p['codice']] = {'titolo': L(p, 'titolo', 'menu_pagine'), 'blocchi': bl}
    for b in pagine.values():
        for x in b['blocchi']:
            if x['lp'] and x['lp'] not in pagine: x['lp'] = None
    momenti = []
    for m in ordina(src['menu_momenti']):
        if m.get('attivo') is False: continue
        vs = [x['voce_id'] for x in sorted(src['menu_momenti_voci'], key=lambda x: (x.get('ordine') or 0, x['id'])) if x['momento_id'] == m['id'] and x['voce_id'] in ids]
        momenti.append({'q': m['quando'], 'da': (m.get('dalle') or '')[:5], 'a': (m.get('alle') or '')[:5], 'saluto': L(m, 'saluto', 'menu_momenti'), 'intro': L(m, 'introduzione', 'menu_momenti'),
                        'sopra': L(m, 'sopratitolo', 'menu_momenti'), 'titolo': L(m, 'titolo', 'menu_momenti'), 'testo': L(m, 'testo', 'menu_momenti'), 'f': m.get('foto_url'), 'fa': L(m, 'foto_alt', 'menu_momenti'),
                        'pulsante': L(m, 'testo_pulsante', 'menu_momenti'), 'voci': vs})
    abb, abbc, cons = {}, {}, {}
    for r in ordina(src['menu_raccomandazioni']):
        if r.get('attivo') is False or r['target_voce_id'] not in ids: continue
        if r['tipo'] == 'abbinamento' and r.get('voce_id') in ids: abb.setdefault(r['voce_id'], []).append(r['target_voce_id'])
        elif r['tipo'] == 'abbinamento' and not r.get('voce_id') and r.get('categoria_id'): abbc.setdefault(r['categoria_id'], []).append(r['target_voce_id'])
        elif r['tipo'] == 'consiglio_categoria' and r.get('categoria_id'): cons.setdefault(r['categoria_id'], []).append(r['target_voce_id'])
    lo = (src.get('locale') or [{}])[0]
    ori = lo.get('orari') or {}
    d = {'testi': testi, 'locale': {'nome': lo.get('nome') or '', 'ind': lo.get('indirizzo') or '', 'tel': lo.get('telefono') or '', 'wifi': wifi_dati(lo), 'orari': (ori.get('testo_' + lingua) if lingua != 'it' else None) or ori.get('testo') or ''},
         'sezioni': sezioni, 'pagine': pagine, 'momenti': momenti, 'abb': {'v': abb, 'c': abbc}, 'consigli': cons, 'lingua': lingua, 'lingue': lingue or []}
    return d, DEF, cfg

HEX = re.compile(r'^#[0-9a-fA-F]{3,8}$')
DERIVATI = ('scuro', 'su-scuro', 'accento-chiaro')  # facoltativi: se mancano il modello li ricava da testo, sfondo e accento
def blocco_var(o):
    return ''.join('--%s%s:%s;' % ('c-' if k in DERIVATI else '', k, v) for k, v in (o or {}).items() if re.match(r'^[a-z0-9-]+$', k) and HEX.match(str(v)))
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
    for i, o in (a.get('pagine') or {}).items():  # pagine extra: valgono anche per i banner che portano a quella pagina
        if re.match(r'^[a-z0-9-]{1,40}$', str(i)) and i != 'home' and blocco_var(o): css += '[data-p="%s"]{%s}' % (i, blocco_var(o))
    fam = ['%s:wght@400;500' % ft.replace(' ', '+')] if ft else []
    if fx and fx != ft: fam.append('%s:wght@400;500;600' % fx.replace(' ', '+'))
    link = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?%s&display=swap">' % '&'.join('family=' + f for f in fam) if fam else ''
    return css, link

def copia_foto(pagine, out):
    """Scarica le foto usate nella cartella img/ accanto alla pagina italiana e riscrive gli indirizzi (i visitatori non toccano mai il database).
    pagine = [(dati, prefisso)]: le pagine delle altre lingue stanno in sottocartelle e puntano alla stessa img/ con prefisso '../'."""
    cart = os.path.join(out, 'img'); os.makedirs(cart, exist_ok=True); nomi = {}
    def loc(u, pre):
        if not u or not u.startswith('http'): return u
        if u not in nomi:
            ext = os.path.splitext(urllib.parse.urlparse(u).path)[1] or '.webp'
            n = hashlib.sha1(u.encode()).hexdigest()[:12] + ext
            dest = os.path.join(cart, n)
            if not os.path.exists(dest):  # già scaricata in un giro precedente: stesso indirizzo = stesso nome (risparmia traffico)
                dati = urllib.request.urlopen(u, timeout=60).read()
                with open(dest + '.tmp', 'wb') as f: f.write(dati)
                os.replace(dest + '.tmp', dest)
            nomi[u] = n
        return pre + 'img/' + nomi[u]
    for d, pre in pagine:
        for s in d['sezioni']:
            s['f'] = loc(s['f'], pre)
            for c in s['c']:
                c['f'] = loc(c['f'], pre)
                for v in c['v']: v['f'] = loc(v['f'], pre); v['fg'] = loc(v['fg'], pre)
        for p in d['pagine'].values():
            for b in p['blocchi']: b['f'] = loc(b['f'], pre)
        for m in d['momenti']: m['f'] = loc(m['f'], pre)
    for f in os.listdir(cart):  # foto non più usate nel menu
        if f not in set(nomi.values()): os.remove(os.path.join(cart, f))
    return len(nomi)

def json_js(o): return json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True); ap.add_argument('--lingua', default='it', help='una sola lingua (it, en, ...)'); ap.add_argument('--json'); ap.add_argument('--esporta-json')
    ap.add_argument('--tutte-le-lingue', action='store_true', help="italiano nella cartella e ogni lingua attiva del database in una sottocartella (en/, fr/, ...)")
    ap.add_argument('--copia-foto', action='store_true'); ap.add_argument('--noindex', action='store_true', help='pagina di prova: non indicizzata dai motori di ricerca')
    ap.add_argument('--consenti-vuoto', action='store_true', help='genera anche se nessuna voce è pubblicata (altrimenti si ferma per non svuotare il menu)'); ap.add_argument('--modello', default=os.path.join(QUI, 'menu_template.html'))
    a = ap.parse_args()
    if a.json: src = json.load(open(a.json, encoding='utf-8'))
    else:
        url, k = os.environ.get('MENU_SB_URL'), os.environ.get('MENU_SB_KEY')
        if not url or not k: sys.exit('Imposta MENU_SB_URL e MENU_SB_KEY (chiave anon pubblica) oppure usa --json')
        src = scarica(url.rstrip('/'), k); src['_url'] = url.rstrip('/')
    if a.esporta_json: json.dump(src, open(a.esporta_json, 'w', encoding='utf-8'), ensure_ascii=False)
    base = (src.get('_url') or os.environ.get('MENU_SB_URL', '')).rstrip('/') + '/storage/v1/object/public/menu-foto/'
    if a.tutte_le_lingue:
        att = sorted([l for l in src.get('menu_lingue', []) if l.get('attiva') is not False and l.get('codice') != 'it'], key=lambda l: (l.get('ordine') or 0, l['codice']))
        codici = ['it'] + [l['codice'] for l in att]
        info = {'it': ITALIANO}; info.update({l['codice']: {'c': l['codice'], 'n': l.get('nome_nativo') or l['codice'], 'b': l.get('bandiera') or ''} for l in att})
    else:
        codici = [a.lingua]; info = {a.lingua: {'c': a.lingua, 'n': a.lingua, 'b': ''}}
    def vai(da, a_):  # indirizzo relativo della pagina in lingua a_ visto dalla pagina in lingua da
        if da == a_: return ''
        return ('../' if da != 'it' else '') + ('' if a_ == 'it' else a_ + '/')
    pagine = []
    for cod in codici:
        lingue = [dict(info[x], u=vai(cod, x)) for x in codici] if len(codici) > 1 else []
        d, DEF, cfg = costruisci(src, cod, base, None if a.json else file_esiste, lingue)  # --json = prove senza rete: nessun controllo
        if cod == codici[0] and not d['sezioni'] and not a.consenti_vuoto:
            sys.exit('Nessuna voce pubblicata: non genero un menu vuoto (usa --consenti-vuoto se è voluto).')
        pagine.append((cod, d, DEF, cfg))
    n = copia_foto([(d, '' if cod == codici[0] and (cod == 'it' or not a.tutte_le_lingue) else '../') for cod, d, _, _ in pagine], a.out) if a.copia_foto else 0
    t0 = open(a.modello, encoding='utf-8').read()
    os.makedirs(a.out, exist_ok=True)
    for cod, d, DEF, cfg in pagine:
        css, link = tema_css(cfg)
        titolo = d['locale']['nome'] or 'Menu'
        t = t0
        for k, v in (('__LANG__', cod), ('__TITOLO__', titolo.replace('<', '')), ('__FONT_LINK__', link), ('__TEMA_CSS__', css), ('__DATI__', json_js(d)), ('__DEF__', json_js(DEF))):
            t = t.replace('/*' + k + '*/null' if k in ('__DATI__', '__DEF__') else k, v)
        cart = a.out if cod == codici[0] and (cod == 'it' or not a.tutte_le_lingue) else os.path.join(a.out, cod)
        os.makedirs(cart, exist_ok=True)
        if a.noindex: t = t.replace('<meta charset="utf-8">', '<meta charset="utf-8"><meta name="robots" content="noindex,nofollow">', 1)
        tmp = os.path.join(cart, 'index.html.tmp')
        open(tmp, 'w', encoding='utf-8').write(t); os.replace(tmp, os.path.join(cart, 'index.html'))
        print('ok: %s/index.html  lingua=%s sezioni=%d voci=%d pagine=%d momenti=%d' % (cart, cod, len(d['sezioni']), sum(len(c['v']) for s in d['sezioni'] for c in s['c']), len(d['pagine']), len(d['momenti'])))
    if a.tutte_le_lingue:  # lingue disattivate: via la cartella rimasta
        for nome in os.listdir(a.out):
            if re.fullmatch(r'[a-z]{2,3}(-[A-Za-z]{2,4})?', nome) and nome not in codici and os.path.isfile(os.path.join(a.out, nome, 'index.html')): shutil.rmtree(os.path.join(a.out, nome))
    print('foto copiate=%d' % n)
if __name__ == '__main__': main()
