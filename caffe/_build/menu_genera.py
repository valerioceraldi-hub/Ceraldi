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
# tabelle lette con colonne esplicite (ad anon sono concesse solo queste); facoltative: se mancano, il menu si genera senza collegamenti
EXTRA = {'contenuti_collegamenti': 'id,da_tabella,da_id,a_tipo,a_id,url,url_en,titolo,testo,posizione,ordine,attivo',
         'guida_luoghi': 'id,slug,nome,stato', 'guida_racconti': 'id,slug,titolo,stato'}

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
    for t, c in EXTRA.items():
        try: out[t] = rich('%s/rest/v1/%s?select=%s' % (url, t, c))
        except Exception as x: print('collegamenti: %s non letta (%s): il menu si genera senza' % (t, x)); out[t] = []
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

def costruisci(src, lingua, foto_base, esiste=None, lingue=None, guida=None):
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
        if x.get('attiva') is not False: var_di.setdefault(x['voce_id'], []).append({'g': L(x, 'gruppo', 'menu_varianti') if x.get('gruppo') else '', 'n': L(x, 'nome', 'menu_varianti'), 'd': x.get('delta_cent') or 0})  # varianti tradotte come il resto
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
            lu = b.get('link_url')
            if lu and '{guida}' in lu:  # segnaposto: la guida nella stessa lingua del menu (senza guida, niente collegamento)
                lu = lu.replace('{guida}', guida) if guida else None
            bl.append({'id': b['id'], 'tipo': b['tipo'], 'pos': b['posizione'], 'ruolo': ruolo, 'sopra': L(b, 'sopratitolo', 'menu_blocchi'), 'titolo': L(b, 'titolo', 'menu_blocchi'), 'testo': L(b, 'testo', 'menu_blocchi'), 'f': U(b.get('foto_url')),
                       'fa': L(b, 'foto_alt', 'menu_blocchi'), 'lt': L(b, 'link_testo', 'menu_blocchi'), 'lu': lu, 'lp': b.get('link_pagina'), 'voci': vs})
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
    # collegamenti di prodotti e categorie verso il sito (url) e la guida (luoghi, racconti): riferimenti per id, nell'ordine scelto
    gl = {r['id']: r for r in src.get('guida_luoghi', []) if r.get('stato') in ('pubblicato', 'anteprima')}
    gr = {r['id']: r for r in src.get('guida_racconti', []) if r.get('stato') in ('pubblicato', 'anteprima')}
    catid = {c['id'] for s in sezioni for c in s['c']}
    col = {}
    for r in ordina([r for r in src.get('contenuti_collegamenti', []) if r.get('attivo') is not False]):
        chi = ('v%s' % r['da_id']) if r['da_tabella'] == 'menu_voci' and r['da_id'] in ids else ('c%s' % r['da_id']) if r['da_tabella'] == 'menu_categorie' and r['da_id'] in catid else None
        if not chi: continue
        x = L(r, 'testo', 'contenuti_collegamenti')
        if r['a_tipo'] == 'url' and r.get('url'):
            en = lingua != 'it' and r.get('url_en')
            o = {'k': 's', 'u': en or r['url'], 't': L(r, 'titolo', 'contenuti_collegamenti'), 'it': lingua != 'it' and not en}
        elif r['a_tipo'] in ('guida_luogo', 'guida_racconto') and guida:
            g = (gl if r['a_tipo'] == 'guida_luogo' else gr).get(r.get('a_id'))
            if not g: continue
            o = {'k': 'g', 'u': guida + ('#/l/' if r['a_tipo'] == 'guida_luogo' else '#/r/') + g['slug'],
                 't': L(g, 'nome', 'guida_luoghi') if r['a_tipo'] == 'guida_luogo' else L(g, 'titolo', 'guida_racconti')}
        else: continue
        if x: o['x'] = x
        col.setdefault(chi, []).append(o)
    lo = (src.get('locale') or [{}])[0]
    ori = lo.get('orari') or {}
    d = {'testi': testi, 'locale': {'nome': lo.get('nome') or '', 'ind': lo.get('indirizzo') or '', 'tel': lo.get('telefono') or '', 'wifi': wifi_dati(lo), 'orari': (ori.get('testo_' + lingua) if lingua != 'it' else None) or ori.get('testo') or ''},
         'sezioni': sezioni, 'pagine': pagine, 'momenti': momenti, 'abb': {'v': abb, 'c': abbc}, 'consigli': cons, 'lingua': lingua, 'lingue': lingue or [], 'col': col, 'guida': guida or ''}
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

# ── Menu pubblicato sul sito dell'attività (--sito): indirizzo canonico, versioni nelle altre lingue,
#    dati strutturati schema.org «Menu» per i motori di ricerca, link per tornare al sito. Nulla di specifico di un locale.
def url_lingua(sito, cod, codici):
    return sito + ('' if cod == codici[0] and cod == 'it' else cod + '/')

# Etichetta della pagina nella lingua del menu (titolo, H1, anteprime): lingue senza voce → «Menu».
ETICHETTA_MENU = {'it': 'Menu e prezzi', 'en': 'Menu and prices', 'fr': 'Carte et prix', 'de': 'Speisekarte und Preise', 'es': 'Carta y precios', 'pt': 'Menu e preços'}
OG_LOCALE = {'it': 'it_IT', 'en': 'en_GB', 'fr': 'fr_FR', 'de': 'de_DE', 'es': 'es_ES', 'pt': 'pt_PT'}

def pulisci_nome(n): return re.sub(r'\s*⏳.*$', '', str(n or '')).strip()  # come pulisci() del modello

def titolo_sito(cod, d):
    nome = d['locale'].get('nome') or ''
    et = ETICHETTA_MENU.get(cod, 'Menu')
    return (et + ' | ' + nome) if nome else et

def corpo_statico(cod, d):
    """Contenuto leggibile senza JavaScript dentro #app (titolo, sezioni, categorie, prodotti e prezzi):
    è quello che leggono i motori di ricerca; il modello lo sostituisce subito con il menu interattivo."""
    e = lambda s: str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    pz = lambda c: (str(c // 100) if c % 100 == 0 else ('%.2f' % (c / 100)).replace('.', ',')) + ' €'
    h = '<div class="gut" style="padding:24px 20px"><h1>%s</h1>' % e(titolo_sito(cod, d).replace(' | ', ' · '))
    lo = d['locale']
    info = ' · '.join(x for x in (lo.get('ind'), lo.get('orari')) if x)
    if info: h += '<p>%s</p>' % e(info)
    for s in d.get('sezioni', []):
        h += '<h2>%s</h2>' % e(pulisci_nome(s.get('n')))
        for c in s.get('c', []):
            h += '<h3>%s</h3><ul>' % e(pulisci_nome(c.get('n')))
            for v in c.get('v', []):
                p = v.get('p')
                h += '<li>%s%s</li>' % (e(pulisci_nome(v.get('n'))), (' — ' + pz(int(round(p)))) if isinstance(p, (int, float)) and p > 0 else '')
            h += '</ul>'
    return h + '</div>'

def testa_sito(sito, cod, codici, d, valuta):
    ea = lambda s: str(s).replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;')
    can = url_lingua(sito, cod, codici)
    h = '<link rel="canonical" href="%s">' % ea(can)
    if len(codici) > 1:
        h += ''.join('<link rel="alternate" hreflang="%s" href="%s">' % (c, ea(url_lingua(sito, c, codici))) for c in codici)
        h += '<link rel="alternate" hreflang="x-default" href="%s">' % ea(url_lingua(sito, codici[0], codici))
    lo = d['locale']; nome = lo.get('nome') or 'Menu'
    # descrizione diversa per lingua: etichetta e nomi delle sezioni sono già tradotti
    # descrizione diversa per lingua (etichetta e sezioni già tradotte), entro ~160 caratteri: oltre Google la taglia.
    # Si toglie prima l'orario, poi l'indirizzo, poi le ultime sezioni (sempre intere, mai parole tagliate a metà).
    sezioni = [x for x in (pulisci_nome(s.get('n')) for s in d.get('sezioni', [])) if x]
    def componi(n_sez, coda):
        t = '%s — %s' % (nome, ETICHETTA_MENU.get(cod, 'Menu'))
        if n_sez: t += ': ' + ', '.join(sezioni[:n_sez]) + ('…' if n_sez < len(sezioni) else '')
        c = ' · '.join(x for x in coda if x)
        return (t + (' ' if t.endswith('…') else '. ') + c) if c else t
    prove = [componi(n, c) for c in ((lo.get('ind'), lo.get('orari')), (lo.get('ind'),), ()) for n in range(len(sezioni), -1, -1)]
    desc = next((x for x in prove if len(x) <= 160), prove[-1])
    h += '<meta name="description" content="%s">' % ea(desc)
    tit = titolo_sito(cod, d)
    h += '<meta property="og:type" content="website"><meta property="og:url" content="%s"><meta property="og:title" content="%s"><meta property="og:description" content="%s">' % (ea(can), ea(tit), ea(desc))
    if lo.get('nome'): h += '<meta property="og:site_name" content="%s">' % ea(lo['nome'])
    if cod in OG_LOCALE: h += '<meta property="og:locale" content="%s">' % OG_LOCALE[cod]
    def voce(v):
        o = {'@type': 'MenuItem', 'name': v.get('n') or ''}
        if v.get('d'): o['description'] = v['d']
        if isinstance(v.get('p'), (int, float)) and v['p'] > 0: o['offers'] = {'@type': 'Offer', 'price': '%.2f' % (v['p'] / 100), 'priceCurrency': valuta}
        return o
    ld = {'@context': 'https://schema.org', '@type': 'Menu', 'name': nome, 'url': can, 'inLanguage': cod,
          'hasMenuSection': [{'@type': 'MenuSection', 'name': s.get('n') or '',
                              'hasMenuSection': [{'@type': 'MenuSection', 'name': c.get('n') or '', 'hasMenuItem': [voce(v) for v in c.get('v', [])]} for c in s.get('c', [])]}
                             for s in d.get('sezioni', [])]}
    return h + '<script type="application/ld+json">' + json_js(ld) + '</script>'

def ritorno_sito(sito):
    """Barra sottile in cima: «‹ dominio» per tornare alla home del sito (il menu ha la grafica dell'app, non la barra del sito)."""
    p = urllib.parse.urlparse(sito); home = p.scheme + '://' + p.netloc + '/'
    nome = re.sub(r'^www\.', '', p.netloc)
    return ('<a class="ritorno-sito" href="%s" style="display:block;max-width:var(--lw,480px);margin:0 auto;padding:7px max(20px,env(safe-area-inset-left,0px));'
            'background:var(--scuro);color:var(--su-scuro);font:500 .75rem/1.3 var(--f-testo);letter-spacing:.06em;text-decoration:none;opacity:.92">&lsaquo; %s</a>') % (home, nome)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True); ap.add_argument('--lingua', default='it', help='una sola lingua (it, en, ...)'); ap.add_argument('--json'); ap.add_argument('--esporta-json')
    ap.add_argument('--tutte-le-lingue', action='store_true', help="italiano nella cartella e ogni lingua attiva del database in una sottocartella (en/, fr/, ...)")
    ap.add_argument('--copia-foto', action='store_true'); ap.add_argument('--noindex', action='store_true', help='pagina di prova: non indicizzata dai motori di ricerca')
    ap.add_argument('--guida-url', default='../guida-nuova/', help="indirizzo della guida visto dalla cartella del menu (vuoto = nessuna guida); per le altre lingue si aggiunge la loro sottocartella")
    ap.add_argument('--fuso', default='Europe/Rome', help='fuso orario del locale (IANA) per le fasce di disponibilità')
    ap.add_argument('--sito', default='', help="indirizzo pubblico della cartella del menu sul sito dell'attività (es. https://www.esempio.it/menu/): indirizzo canonico, versioni nelle altre lingue, dati strutturati per i motori di ricerca e link per tornare al sito")
    ap.add_argument('--caratteri', default='', help="foglio di stile dei caratteri ospitati dal sito (es. /assets/font.css) al posto di Google Fonts: nessuna chiamata a servizi esterni; deve contenere le famiglie scelte nell'Aspetto")
    ap.add_argument('--valuta', default='EUR', help='valuta dei prezzi nei dati strutturati (codice ISO 4217)')
    ap.add_argument('--statistiche', action='store_true', help='attiva i contatori anonimi di visita (funzione menu_stat_registra; nessun cookie, nessun dato sul telefono)')
    ap.add_argument('--consenti-vuoto', action='store_true', help='genera anche se nessuna voce è pubblicata (altrimenti si ferma per non svuotare il menu)'); ap.add_argument('--modello', default=os.path.join(QUI, 'menu_template.html'))
    a = ap.parse_args()
    if a.sito:
        if not re.match(r'^https://[a-z0-9.-]+\.[a-z]{2,}(/|$)', a.sito, re.I): sys.exit('--sito deve essere un indirizzo https completo, es. https://www.esempio.it/menu/')
        if not a.sito.endswith('/'): a.sito += '/'
        if a.noindex: sys.exit('--sito e --noindex insieme non hanno senso: il menu sul sito è fatto per essere trovato')
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
        radice_ = cod == codici[0] and (cod == 'it' or not a.tutte_le_lingue)
        guida = (('' if radice_ or re.match(r'^(https?:)?/', a.guida_url) else '../') + a.guida_url + ('' if cod == 'it' else cod + '/')) if a.guida_url else None
        d, DEF, cfg = costruisci(src, cod, base, None if a.json else file_esiste, lingue, guida)  # --json = prove senza rete: nessun controllo
        d['fuso'] = a.fuso  # fasce orarie di disponibilità calcolate sull'ora del locale, non su quella del telefono
        if a.statistiche:  # contatori anonimi: solo la funzione pubblica menu_stat_registra, con la chiave anon (già pubblica)
            su, sk = (src.get('_url') or os.environ.get('MENU_SB_URL', '')).rstrip('/'), os.environ.get('MENU_SB_KEY', '')
            if su.startswith('https://') and sk: d['stat'] = {'u': su + '/rest/v1/rpc/menu_stat_registra', 'k': sk}
        if cod == codici[0] and not d['sezioni'] and not a.consenti_vuoto:
            sys.exit('Nessuna voce pubblicata: non genero un menu vuoto (usa --consenti-vuoto se è voluto).')
        pagine.append((cod, d, DEF, cfg))
    n = copia_foto([(d, '' if cod == codici[0] and (cod == 'it' or not a.tutte_le_lingue) else '../') for cod, d, _, _ in pagine], a.out) if a.copia_foto else 0
    t0 = open(a.modello, encoding='utf-8').read()
    os.makedirs(a.out, exist_ok=True)
    for cod, d, DEF, cfg in pagine:
        css, link = tema_css(cfg)
        if a.caratteri and link: link = '<link rel="stylesheet" href="%s">' % a.caratteri.replace('"', '')
        titolo = titolo_sito(cod, d) if a.sito else (d['locale']['nome'] or 'Menu')
        t = t0
        for k, v in (('__LANG__', cod), ('__TITOLO__', titolo.replace('<', '')), ('__FONT_LINK__', link), ('__TEMA_CSS__', css), ('__DATI__', json_js(d)), ('__DEF__', json_js(DEF))):
            t = t.replace('/*' + k + '*/null' if k in ('__DATI__', '__DEF__') else k, v)
        cart = a.out if cod == codici[0] and (cod == 'it' or not a.tutte_le_lingue) else os.path.join(a.out, cod)
        os.makedirs(cart, exist_ok=True)
        if a.noindex: t = t.replace('<meta charset="utf-8">', '<meta charset="utf-8"><meta name="robots" content="noindex,nofollow">', 1)
        if a.sito:
            t = t.replace('<meta charset="utf-8">', '<meta charset="utf-8">' + testa_sito(a.sito, cod, codici, d, a.valuta), 1)
            t = t.replace('<body>', '<body>' + ritorno_sito(a.sito), 1)
            t = t.replace('<div class="app" id="app"></div>', '<div class="app" id="app">' + corpo_statico(cod, d) + '</div>', 1)
        tmp = os.path.join(cart, 'index.html.tmp')
        open(tmp, 'w', encoding='utf-8').write(t); os.replace(tmp, os.path.join(cart, 'index.html'))
        print('ok: %s/index.html  lingua=%s sezioni=%d voci=%d pagine=%d momenti=%d' % (cart, cod, len(d['sezioni']), sum(len(c['v']) for s in d['sezioni'] for c in s['c']), len(d['pagine']), len(d['momenti'])))
    if a.tutte_le_lingue:  # lingue disattivate: via la cartella rimasta
        for nome in os.listdir(a.out):
            if re.fullmatch(r'[a-z]{2,3}(-[A-Za-z]{2,4})?', nome) and nome not in codici and os.path.isfile(os.path.join(a.out, nome, 'index.html')): shutil.rmtree(os.path.join(a.out, nome))
    print('foto copiate=%d' % n)
if __name__ == '__main__': main()
