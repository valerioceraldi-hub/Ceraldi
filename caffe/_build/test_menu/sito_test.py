#!/usr/bin/env python3
"""Prove dell'opzione --sito di menu_genera.py (menu pubblicato sul sito dell'attività), senza rete.
Uso: python3 caffe/_build/test_menu/sito_test.py   → esce con 1 se una prova fallisce."""
import json, os, re, subprocess, sys, tempfile

QUI = os.path.dirname(os.path.abspath(__file__)); GEN = os.path.join(QUI, '..', 'menu_genera.py')
R = []
def ok(n, c): R.append(('OK   ' if c else 'FAIL ') + n)

with tempfile.TemporaryDirectory() as t:
    out = os.path.join(t, 'm')
    subprocess.run([sys.executable, GEN, '--json', os.path.join(QUI, 'fix_ml.json'), '--out', out, '--tutte-le-lingue', '--sito', 'https://www.esempio.it/menu'], check=True, capture_output=True)
    it = open(os.path.join(out, 'index.html'), encoding='utf-8').read()
    en = open(os.path.join(out, 'en', 'index.html'), encoding='utf-8').read()
    ok('canonico italiano', '<link rel="canonical" href="https://www.esempio.it/menu/">' in it)
    ok('canonico inglese nella sua cartella', '<link rel="canonical" href="https://www.esempio.it/menu/en/">' in en)
    ok('versioni nelle lingue + x-default', 'hreflang="en" href="https://www.esempio.it/menu/en/"' in it and 'hreflang="x-default" href="https://www.esempio.it/menu/"' in en)
    ok('indicizzabile (nessun noindex)', 'noindex' not in it)
    ok('descrizione presente', re.search(r'<meta name="description" content="[^"]+">', it) is not None)
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', it, re.S)
    ld = json.loads(m.group(1)) if m else {}
    ok('dati strutturati Menu', ld.get('@type') == 'Menu' and ld.get('url') == 'https://www.esempio.it/menu/')
    voci = [v for s in ld.get('hasMenuSection', []) for c in s.get('hasMenuSection', []) for v in c.get('hasMenuItem', [])]
    ok('prodotti con prezzo in EUR', voci and all(v['offers']['priceCurrency'] == 'EUR' and re.match(r'^\d+\.\d\d$', v['offers']['price']) for v in voci if 'offers' in v))
    ok('link per tornare al sito', 'class="ritorno-sito" href="https://www.esempio.it/"' in it and '&lsaquo; esempio.it' in it)
    tit = lambda h: re.search(r'<title>(.*?)</title>', h).group(1)
    dsc = lambda h: re.search(r'<meta name="description" content="([^"]*)">', h).group(1)
    ok('titolo con etichetta per lingua e diverso tra lingue', tit(it).startswith('Menu e prezzi') and tit(en).startswith('Menu and prices'))
    ok('descrizione diversa tra lingue', dsc(it) != dsc(en))
    ok('descrizione entro 160 caratteri', len(dsc(it)) <= 160 and len(dsc(en)) <= 160)
    ok('anteprime Open Graph', all(('property="og:%s"' % k) in it for k in ('title', 'description', 'url', 'type')))
    body = it[it.find('<div class="app" id="app">'):]
    ok('contenuto leggibile senza JavaScript (H1 + prodotti)', '<h1>' in body[:400] and body.count('<li>') >= len(voci) > 0)
    subprocess.run([sys.executable, GEN, '--json', os.path.join(QUI, 'fix_ml.json'), '--out', os.path.join(t, 'y0'), '--tutte-le-lingue'], check=True, capture_output=True)
    ok('senza --sito #app resta vuoto', '<div class="app" id="app"></div>' in open(os.path.join(t, 'y0', 'index.html'), encoding='utf-8').read())
    r = subprocess.run([sys.executable, GEN, '--json', os.path.join(QUI, 'fix.json'), '--out', os.path.join(t, 'x'), '--sito', 'http://esempio.it/'], capture_output=True, text=True)
    ok('rifiuta indirizzi non https', r.returncode != 0)
    r = subprocess.run([sys.executable, GEN, '--json', os.path.join(QUI, 'fix.json'), '--out', os.path.join(t, 'y')], check=True, capture_output=True)
    subprocess.run([sys.executable, GEN, '--json', os.path.join(QUI, 'fix.json'), '--out', os.path.join(t, 'z'), '--caratteri', '/assets/font.css'], check=True, capture_output=True)
    z = open(os.path.join(t, 'z', 'index.html'), encoding='utf-8').read()
    ok('caratteri del sito al posto di Google Fonts', '<link rel="stylesheet" href="/assets/font.css">' in z and 'fonts.googleapis' not in z)
    ok('senza --sito nulla cambia', 'ritorno-sito' not in open(os.path.join(t, 'y', 'index.html'), encoding='utf-8').read())

print('\n'.join(R)); sys.exit(1 if any(x.startswith('FAIL') for x in R) else 0)
