#!/usr/bin/env python3
"""Genera la Guida di Napoli (pagine statiche) dai dati del database o da un export JSON. Stesso modello di menu_genera.py.
Uso:  MENU_SB_URL=https://xxx.supabase.co MENU_SB_KEY=<chiave anon> python3 guida_genera.py --out guida-nuova [--anteprima] [--noindex] [--tutte-le-lingue]
      python3 guida_genera.py --json F --out DIR        (senza rete, per le prove)
- Legge solo cio' che il pubblico puo' leggere (chiave anon, colonne pubbliche): pubblicato, e con --anteprima anche lo stato «anteprima».
- Il visitatore non chiama mai il database ne' servizi esterni: dati, foto e mappa stanno nella cartella generata.
- Una pagina per lingua (italiano nella cartella, le altre in en/ fr/ de/ es/); schermate interne con indirizzi #/... ."""
import argparse, json, os, re, sys, hashlib, datetime, shutil, urllib.request, urllib.parse
QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
from menu_genera import blocco_var, json_js  # stessi colori del menu (dal database), stessa serializzazione sicura

COL = {  # solo colonne pubbliche (anon non legge note_interne, aggiornato_da, verificata_da, risposte)
    'guida_luoghi': 'id,slug,nome,tipo,zona,indirizzo,lat,lon,minuti_a_piedi,metri_a_piedi,durata_visita_min,gratuito,sempre_accessibile,sito_ufficiale,pagina_orari,sommario,racconto,consiglio,accessibilita,accessibilita_verificata_il,foto_path,foto_alt,foto_autore,foto_licenza,foto_fonte_url,stato,orari_stato,orari_verificati_il,ordine,leggende,foto_consentite',
    'guida_orari': 'id,luogo_id,giorni,dalle,alle,ultimo_ingresso,dal,al,chiuso,nota,ordine',
    'guida_itinerari': 'id,slug,nome,sottotitolo,descrizione,durata_min,distanza_m,etichette,foto_path,foto_alt,foto_autore,foto_licenza,foto_fonte_url,stato,ordine',
    'guida_tappe': 'id,itinerario_id,luogo_id,ordine,minuti_dal_precedente,metri_dal_precedente,sosta_min,nota,alternativa_luogo_id,percorso,svolte',
    'guida_racconti': 'id,slug,titolo,sommario,testo,foto_path,foto_alt,foto_autore,foto_licenza,foto_fonte_url,stato,ordine',
    'guida_affermazioni_fonti': 'tabella,riga_id,fonte_titolo,fonte_url',
    'guida_dettagli': 'id,luogo_id,ordine,titolo,testo,dove,foto_path,foto_alt,foto_autore,foto_licenza,foto_fonte_url,foto_permesso,stato',
    'guida_foto': 'id,luogo_id,ordine,foto_path,foto_alt,foto_autore,foto_licenza,foto_fonte_url,foto_permesso,stato',
    'menu_lingue': '*',
    'scioperi_napoli_trasporti': 'data,linea,dettaglio',
}
_BASE = json.load(open(os.path.join(QUI, 'guida_testi_base.json'), encoding='utf-8'))
ITALIANO = {'c': 'it', 'n': 'Italiano', 'b': '🇮🇹'}
AL_COPERTO = {'museo', 'chiesa', 'sotterraneo', 'palazzo', 'teatro', 'castello'}  # «Piove?»: tipi di luogo al chiuso (regola fissa)

def scarica(url, chiave):
    def rich(u, extra=None, dati=None):
        h = {'apikey': chiave, 'Authorization': 'Bearer ' + chiave}; h.update(extra or {})
        return json.load(urllib.request.urlopen(urllib.request.Request(u, data=dati, headers=h), timeout=60))
    out = {}
    ieri = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    for t, c in COL.items():
        q = 'select=' + c
        if t == 'scioperi_napoli_trasporti': q += '&data=gte.' + ieri
        out[t] = rich('%s/rest/v1/%s?%s' % (url, t, q))
    out['menu_traduzioni'] = rich(url + '/rest/v1/menu_traduzioni?select=tabella,riga_id,campo,lingua,testo&tabella=like.guida_*')
    out['config'] = rich(url + '/rest/v1/rpc/menu_config_pubblica', {'Content-Type': 'application/json'}, b'{}')
    return out

def semplifica(svolte):
    """Svolte grezze OSM -> indicazioni da dare a chi cammina (regole fisse, uguali per tutte le lingue):
    - «stessa strada» (new name/continue dritto) non si annuncia: i metri si sommano all'indicazione precedente;
    - una svolta seguita da meno di 20 m prima della successiva si accorpa (i «gradini» di 5 m nei vicoli);
    - restano: partenza, svolte vere (con direzione e nome della strada), arrivo. a = metri dall'inizio del tratto."""
    out, pos, sv = [], 0, svolte or []
    for i, x in enumerate(sv):
        inizio, pos = pos, pos + (x.get('d') or 0)
        t, m, n, d = x.get('t'), x.get('m') or '', x.get('n') or '', x.get('d') or 0
        if t == 'depart': out.append({'k': 'parti', 'n': n, 'd': d, 'a': 0}); continue
        if t == 'arrive': out.append({'k': 'arrivo', 'a': inizio}); continue
        dritto = m in ('', 'straight')
        if (t in ('new name', 'continue') and dritto) or (d < 20 and i < len(sv) - 2):
            if out: out[-1]['d'] = out[-1].get('d', 0) + d
            continue
        out.append({'k': 'gira', 'm': m, 'n': n, 'd': d, 'a': inizio})
    return out

def costruisci(src, lingua, foto_base, anteprima):
    visibile = ('pubblicato', 'anteprima') if anteprima else ('pubblicato',)
    TR = {(t['tabella'], str(t['riga_id']), t['campo']): t['testo'] for t in src.get('menu_traduzioni', []) if t.get('lingua') == lingua and t.get('testo')}
    def L(r, k, tab):  # campo nella lingua scelta, con ripiego sull'italiano
        if lingua == 'it': return r.get(k) or ''
        return TR.get((tab, str(r.get('id')), k)) or r.get(k) or ''
    def U(p):
        if not p: return None
        return p if re.match(r'^https://', p) else foto_base + p
    def foto(r, tab):
        if not r.get('foto_path'): return None
        return {'u': U(r['foto_path']), 'alt': L(r, 'foto_alt', tab), 'aut': r.get('foto_autore') or '', 'lic': r.get('foto_licenza') or '', 'src': r.get('foto_fonte_url') or ''}
    ordina = lambda l: sorted(l, key=lambda r: (r.get('ordine') or 0, r.get('id') or 0))
    fonti = {}
    for f in src.get('guida_affermazioni_fonti', []):
        k = (f['tabella'], f['riga_id']); v = {'t': f['fonte_titolo'], 'u': f['fonte_url']}
        if v not in fonti.setdefault(k, []): fonti[k].append(v)
    orari = {}
    for o in ordina(src.get('guida_orari', [])):
        orari.setdefault(o['luogo_id'], []).append({k: v for k, v in dict(g=o.get('giorni'), da=(o.get('dalle') or '')[:5] or None, a=(o.get('alle') or '')[:5] or None,
            ui=(o.get('ultimo_ingresso') or '')[:5] or None, dal=o.get('dal'), al=o.get('al'), x=bool(o.get('chiuso')), n=L(o, 'nota', 'guida_orari')).items() if v not in (None, '', False)})
    dettagli, galleria = {}, {}
    for x in ordina(src.get('guida_dettagli', [])):
        if x.get('stato') not in visibile: continue
        f = foto(x, 'guida_dettagli') if x.get('foto_permesso') else None   # mai una foto senza permesso d'uso registrato
        dettagli.setdefault(x['luogo_id'], []).append({'t': L(x, 'titolo', 'guida_dettagli'), 'x': L(x, 'testo', 'guida_dettagli'), 'd': L(x, 'dove', 'guida_dettagli'), 'foto': f})
        for v in fonti.get(('guida_dettagli', x['id']), []): fonti.setdefault(('guida_luoghi', x['luogo_id']), []).append(v) if v not in fonti.get(('guida_luoghi', x['luogo_id']), []) else None
    for x in ordina(src.get('guida_foto', [])):
        if x.get('stato') not in visibile or not x.get('foto_permesso'): continue
        galleria.setdefault(x['luogo_id'], []).append(foto(x, 'guida_foto'))
    luoghi = {}
    for l in ordina(src.get('guida_luoghi', [])):
        if l.get('stato') not in visibile: continue
        luoghi[l['id']] = {'id': l['id'], 's': l['slug'], 'n': L(l, 'nome', 'guida_luoghi'), 'tipo': l.get('tipo'), 'zona': l.get('zona'), 'ind': l.get('indirizzo') or '',
            'lat': float(l['lat']) if l.get('lat') is not None else None, 'lon': float(l['lon']) if l.get('lon') is not None else None,
            'mp': l.get('minuti_a_piedi'), 'dv': l.get('durata_visita_min'), 'gr': l.get('gratuito'), 'sa': bool(l.get('sempre_accessibile')),
            'sito': l.get('sito_ufficiale') or '', 'po': l.get('pagina_orari') or '', 'som': L(l, 'sommario', 'guida_luoghi'), 'rac': L(l, 'racconto', 'guida_luoghi'),
            'con': L(l, 'consiglio', 'guida_luoghi'), 'acc': L(l, 'accessibilita', 'guida_luoghi'), 'foto': foto(l, 'guida_luoghi'),
            'ov': l.get('orari_stato') == 'verificati', 'ovi': (l.get('orari_verificati_il') or '')[:10] or None, 'or': orari.get(l['id'], []),
            'fonti': fonti.get(('guida_luoghi', l['id']), []), 'ant': l.get('stato') == 'anteprima',
            'dett': dettagli.get(l['id'], []), 'gal': galleria.get(l['id'], []), 'leg': L(l, 'leggende', 'guida_luoghi'), 'fc': l.get('foto_consentite')}
    itinerari = []
    for i in ordina(src.get('guida_itinerari', [])):
        if i.get('stato') not in visibile: continue
        tappe = []
        for t in ordina([t for t in src.get('guida_tappe', []) if t['itinerario_id'] == i['id']]):
            if t['luogo_id'] not in luoghi: continue  # tappa su un luogo non visibile: si salta (mai un buco con dati nascosti)
            alt = t.get('alternativa_luogo_id')
            geo = (t.get('percorso') or {}).get('coordinates')
            tappe.append({'l': t['luogo_id'], 'm': t.get('minuti_dal_precedente') or 0, 'mt': t.get('metri_dal_precedente') or 0, 'so': t.get('sosta_min') or 0,
                          'nota': L(t, 'nota', 'guida_tappe'), 'alt': alt if alt in luoghi else None,
                          'geo': [[round(x, 5), round(y, 5)] for x, y in geo] if geo else None, 'sv': semplifica(t.get('svolte')) if t.get('svolte') else None})
        if not tappe: continue
        itinerari.append({'id': i['id'], 's': i['slug'], 'n': L(i, 'nome', 'guida_itinerari'), 'sub': L(i, 'sottotitolo', 'guida_itinerari'), 'desc': L(i, 'descrizione', 'guida_itinerari'),
                          'dur': i.get('durata_min'), 'dist': i.get('distanza_m'), 'et': i.get('etichette') or [], 'foto': foto(i, 'guida_itinerari'), 'tappe': tappe,
                          'fonti': fonti.get(('guida_itinerari', i['id']), []), 'ant': i.get('stato') == 'anteprima'})
    racconti = [{'id': r['id'], 's': r['slug'], 't': L(r, 'titolo', 'guida_racconti'), 'som': L(r, 'sommario', 'guida_racconti'), 'txt': L(r, 'testo', 'guida_racconti'),
                 'foto': foto(r, 'guida_racconti'), 'fonti': fonti.get(('guida_racconti', r['id']), []), 'ant': r.get('stato') == 'anteprima'}
                for r in ordina(src.get('guida_racconti', [])) if r.get('stato') in visibile]
    scioperi = [{'d': s['data'], 'l': s.get('linea') or '', 'x': s.get('dettaglio') or ''} for s in src.get('scioperi_napoli_trasporti', []) if s.get('data')]
    return {'lingua': lingua, 'luoghi': list(luoghi.values()), 'itinerari': itinerari, 'racconti': racconti, 'scioperi': scioperi, 'coperto': sorted(AL_COPERTO),
            'generata': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')}

def tema_css(cfg):  # colori del menu; caratteri di sistema (nessuna richiesta a Google Fonts)
    return ':root{' + blocco_var((cfg.get('aspetto') or {}).get('globale')) + '}'

def copia_foto(pagine, out):
    cart = os.path.join(out, 'img'); os.makedirs(cart, exist_ok=True); nomi = {}
    def loc(f, pre):
        if not f or not f.get('u', '').startswith('http'): return
        u = f['u']
        if u not in nomi:
            n = hashlib.sha1(u.encode()).hexdigest()[:12] + (os.path.splitext(urllib.parse.urlparse(u).path)[1] or '.webp')
            dest = os.path.join(cart, n)
            if not os.path.exists(dest):
                dati = urllib.request.urlopen(u, timeout=60).read()
                open(dest + '.tmp', 'wb').write(dati); os.replace(dest + '.tmp', dest)
            nomi[u] = n
        f['u'] = pre + 'img/' + nomi[u]
    for d, pre in pagine:
        for x in d['luoghi'] + d['itinerari'] + d['racconti']: loc(x.get('foto'), pre)
        for x in d['luoghi']:
            for g in x.get('gal', []): loc(g, pre)
            for g in x.get('dett', []): loc(g.get('foto'), pre)
    for f in os.listdir(cart):
        if f not in set(nomi.values()): os.remove(os.path.join(cart, f))
    return len(nomi)

def file_mappa(out):
    """Elenco dei file della mappa da salvare per l'uso senza rete (relativi alla cartella della guida). I caratteri sono in caratteri/."""
    r = []
    for radice, _, files in os.walk(os.path.join(out, 'mappa')):
        for f in files:
            if f.endswith('.md'): continue
            r.append(os.path.relpath(os.path.join(radice, f), out).replace(os.sep, '/'))
    return sorted(r)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True); ap.add_argument('--json'); ap.add_argument('--esporta-json')
    ap.add_argument('--tutte-le-lingue', action='store_true'); ap.add_argument('--lingua', default='it')
    ap.add_argument('--anteprima', action='store_true', help='include i contenuti in stato «anteprima» (solo per la prova non indicizzata)')
    ap.add_argument('--noindex', action='store_true'); ap.add_argument('--copia-foto', action='store_true')
    ap.add_argument('--menu-url', default='../menu-nuovo/', help='indirizzo del menu clienti visto dalla cartella della guida')
    ap.add_argument('--modello', default=os.path.join(QUI, 'guida_template.html'))
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
        codici = ['it'] + [l['codice'] for l in att if l['codice'] in _BASE]  # solo lingue con i testi fissi della guida
        info = {'it': ITALIANO}; info.update({l['codice']: {'c': l['codice'], 'n': l.get('nome_nativo') or l['codice'], 'b': l.get('bandiera') or ''} for l in att})
    else:
        codici = [a.lingua]; info = {a.lingua: {'c': a.lingua, 'n': a.lingua, 'b': ''}}
    radice = lambda c: c == codici[0] and (c == 'it' or not a.tutte_le_lingue)
    vai = lambda da, x: '' if da == x else ('../' if da != 'it' else '') + ('' if x == 'it' else x + '/')
    pagine = []
    for cod in codici:
        d = costruisci(src, cod, base, a.anteprima)
        d['lingue'] = [dict(info[x], u=vai(cod, x)) for x in codici] if len(codici) > 1 else []
        d['pre'] = '' if radice(cod) else '../'
        d['menu'] = d['pre'] + a.menu_url
        pagine.append((cod, d))
    d0 = pagine[0][1]
    if not d0['luoghi'] and not d0['itinerari'] and not d0['racconti']:
        print('Nessun contenuto visibile: non genero una guida vuota (le pagine esistenti restano).'); sys.exit(3)
    n = copia_foto([(d, d['pre']) for _, d in pagine], a.out) if a.copia_foto else 0
    t0 = open(a.modello, encoding='utf-8').read()
    css = tema_css(src.get('config') or {})
    os.makedirs(a.out, exist_ok=True)
    nomi_pagine = []
    for cod, d in pagine:
        T = _BASE.get(cod) or _BASE['en']
        t = t0
        for k, v in (('__LANG__', cod), ('__TITOLO__', T['titolo'] + ' · Ceraldi'), ('__TEMA_CSS__', css), ('__DATI__', json_js(d)), ('__TESTI__', json_js(T)), ('__PRE__', d['pre'])):
            t = t.replace('/*' + k + '*/null' if k in ('__DATI__', '__TESTI__') else k, v)
        if a.noindex: t = t.replace('<meta charset="utf-8">', '<meta charset="utf-8"><meta name="robots" content="noindex,nofollow">', 1)
        cart = a.out if radice(cod) else os.path.join(a.out, cod)
        os.makedirs(cart, exist_ok=True)
        tmp = os.path.join(cart, 'index.html.tmp'); open(tmp, 'w', encoding='utf-8').write(t); os.replace(tmp, os.path.join(cart, 'index.html'))
        nomi_pagine.append('' if radice(cod) else cod + '/')
        print('ok: %s/index.html lingua=%s luoghi=%d itinerari=%d racconti=%d' % (cart, cod, len(d['luoghi']), len(d['itinerari']), len(d['racconti'])))
    if a.tutte_le_lingue:
        for nome in os.listdir(a.out):
            if re.fullmatch(r'[a-z]{2,3}', nome) and nome not in codici and os.path.isfile(os.path.join(a.out, nome, 'index.html')): shutil.rmtree(os.path.join(a.out, nome))
    # service worker: salva pagine, foto e mappa per l'uso senza rete. La versione cambia con i contenuti: il telefono scarica solo se serve.
    elenco = nomi_pagine + ['img/' + f for f in sorted(os.listdir(os.path.join(a.out, 'img')))] if os.path.isdir(os.path.join(a.out, 'img')) else list(nomi_pagine)
    elenco += file_mappa(a.out) + ['caratteri/' + f for f in sorted(os.listdir(os.path.join(a.out, 'caratteri'))) if f.endswith(('.css', '.woff2'))] if os.path.isdir(os.path.join(a.out, 'caratteri')) else file_mappa(a.out)
    h = hashlib.sha1()
    for p in elenco:
        f = os.path.join(a.out, p, 'index.html') if p.endswith('/') or p == '' else os.path.join(a.out, p)
        if os.path.isfile(f): h.update(open(f, 'rb').read())
    sw = open(os.path.join(QUI, 'guida_sw.js'), encoding='utf-8').read().replace('__VERSIONE__', h.hexdigest()[:12]).replace('/*__FILE__*/[]', json.dumps(['./' + p for p in elenco]))
    open(os.path.join(a.out, 'sw.js'), 'w', encoding='utf-8').write(sw)
    print('foto copiate=%d file per l\'uso senza rete=%d' % (n, len(elenco)))

if __name__ == '__main__': main()
