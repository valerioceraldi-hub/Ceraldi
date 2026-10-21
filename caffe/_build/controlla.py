# -*- coding: utf-8 -*-
"""Controlli automatici sul sito generato. Uso: python3 caffe/_build/controlla.py  (dopo build.py)
Esce con codice 1 se trova errori, così si vede subito prima di pubblicare.
Controlla: collegamenti interni, rimandi, titoli e descrizioni (presenza, lunghezza, duplicati),
un solo H1, testo alternativo delle immagini, foto ripetute nella stessa pagina, sitemap,
e le frasi che non devono più comparire perché non verificate."""
import glob, html, os, re, sys

QUI = os.path.dirname(os.path.abspath(__file__))
SITO = os.path.dirname(QUI)
sys.path.insert(0, QUI)
from contenuti import BASE  # noqa: E402

# Frasi tolte perché non verificate: se ricompaiono è un errore
VIETATE = ["cento anni", "hundred years", "buffet", "quasi 2.000", "almost 2,000", "dieci anni", "ten years", "primi anni Settanta", "early 1970"]

errori, avvisi = [], []
pagine = sorted(f for f in glob.glob(os.path.join(SITO, "**", "*.html"), recursive=True) if "/_build/" not in f)
titoli, descrizioni = {}, {}

def esiste(path):
    if os.path.isdir(path):
        path = os.path.join(path, "index.html")
    return os.path.exists(path)

for f in pagine:
    rel = os.path.relpath(f, SITO)
    s = open(f, encoding="utf-8").read()
    if rel.startswith("google") and len(s) < 200:
        continue
    cartella = os.path.dirname(f)
    rimando = 'http-equiv="refresh"' in s
    if rimando:
        m = re.search(r'url=([^"]+)"', s)
        dest = m.group(1) if m else ""
        if not dest.startswith(BASE) or not esiste(os.path.join(SITO, dest[len(BASE):])):
            errori.append(f"{rel}: rimando verso una pagina che non esiste ({dest})")
        continue
    # collegamenti e risorse interne
    for href in re.findall(r'(?:href|src)="([^"#?]+)', s):
        if href.startswith(("mailto:", "tel:", "data:")):
            continue
        if href.startswith(("http://", "https://", "//")):
            if not href.startswith(BASE):
                continue
            dest = os.path.join(SITO, href[len(BASE):])
        else:
            dest = os.path.normpath(os.path.join(cartella, href))
        if not esiste(dest):
            errori.append(f"{rel}: collegamento rotto {href}")
    noindex = 'content="noindex' in s
    t = re.search(r"<title>(.*?)</title>", s, re.S)
    d = re.search(r'<meta name="description" content="([^"]*)"', s)
    if not noindex:
        if not t:
            errori.append(f"{rel}: manca il titolo")
        else:
            tt = html.unescape(t.group(1)); titoli.setdefault(tt, []).append(rel)
            if len(tt) > 70:
                avvisi.append(f"{rel}: titolo lungo ({len(tt)} caratteri)")
        if not d:
            errori.append(f"{rel}: manca la descrizione")
        else:
            dd = html.unescape(d.group(1)); descrizioni.setdefault(dd, []).append(rel)
            if not 70 <= len(dd) <= 165:
                avvisi.append(f"{rel}: descrizione di {len(dd)} caratteri")
        if len(re.findall(r"<h1[ >]", s)) != 1:
            errori.append(f"{rel}: deve avere un solo H1")
    for img in re.findall(r"<img[^>]*>", s):
        if 'alt="' not in img:
            errori.append(f"{rel}: immagine senza testo alternativo")
    foto = [re.sub(r"-\d+\.webp$", "", x) for x in re.findall(r'<img[^>]*\ssrc="[^"]*img/([a-z0-9-]+-\d+\.webp)"', s)]
    ripetute = sorted({x for x in foto if foto.count(x) > 1})
    if ripetute:
        avvisi.append(f"{rel}: foto ripetuta nella pagina: {', '.join(ripetute)}")
    testo = html.unescape(re.sub(r"<[^>]+>", " ", s))
    for v in VIETATE:
        if v.lower() in testo.lower():
            errori.append(f"{rel}: contiene la frase non verificata «{v}»")

for tt, rr in titoli.items():
    if len(rr) > 1:
        errori.append(f"titolo duplicato «{tt}»: {', '.join(rr)}")
for dd, rr in descrizioni.items():
    if len(rr) > 1:
        errori.append(f"descrizione duplicata: {', '.join(rr)}")

llms = os.path.join(SITO, "llms.txt")
if os.path.exists(llms):
    t = open(llms, encoding="utf-8").read().lower()
    for v in VIETATE:
        if v.lower() in t:
            errori.append(f"llms.txt: contiene la frase non verificata «{v}»")

sm = open(os.path.join(SITO, "sitemap.xml"), encoding="utf-8").read()
for loc in re.findall(r"<loc>([^<]+)</loc>", sm):
    if not loc.startswith(BASE) or not esiste(os.path.join(SITO, loc[len(BASE):])):
        errori.append(f"sitemap: indirizzo inesistente {loc}")

print(f"Pagine controllate: {len(pagine)}")
for a in avvisi:
    print("AVVISO ", a)
for e in errori:
    print("ERRORE ", e)
print(f"{len(errori)} errori, {len(avvisi)} avvisi")
sys.exit(1 if errori else 0)
