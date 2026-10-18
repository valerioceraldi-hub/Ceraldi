# -*- coding: utf-8 -*-
"""Genera le pagine del sito di Ceraldi Caffè dalla cartella caffe/_build.
Uso:  python3 caffe/_build/build.py   (dalla radice del repository)
La cartella _build non viene pubblicata da GitHub Pages."""
import json, os, html
from contenuti import *

QUI = os.path.dirname(os.path.abspath(__file__))
SITO = os.path.dirname(QUI)
e = html.escape

FONT = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400..600;1,6..96,400&family=Work+Sans:wght@400;600&display=swap" rel="stylesheet">')

def scrivi(rel, testo):
    p = os.path.join(SITO, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(testo)

def testa(lang, titolo, descr, url, rel_root, og_img="img/og.jpg", extra="", ld=None, alternates=None):
    alt = ''.join(f'<link rel="alternate" hreflang="{h}" href="{u}">' for h, u in (alternates or []))
    lds = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (ld or []))
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titolo)}</title>
<meta name="description" content="{e(descr)}">
<link rel="canonical" href="{url}">{alt}
<meta name="theme-color" content="#241610">
<meta property="og:type" content="{'article' if '/storie/' in url and not url.endswith('/storie/') else 'website'}">
<meta property="og:site_name" content="Ceraldi Caffè">
<meta property="og:title" content="{e(titolo)}">
<meta property="og:description" content="{e(descr)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}{og_img}">
<meta property="og:locale" content="{'it_IT' if lang == 'it' else 'en_GB'}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{rel_root}favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{rel_root}img/apple-touch-icon.png">
{FONT}
<link rel="stylesheet" href="{rel_root}assets/sito.css">
{lds}{extra}
</head>
<body>
<a class="salta" href="#contenuto">{'Vai al contenuto' if lang == 'it' else 'Skip to content'}</a>
'''

def barra(rel_root, lang='it'):
    if lang == 'en':
        return f'''<div class="barra"><a class="marchio" href="{rel_root}en/">Ceraldi Caffè</a>
<nav aria-label="Main"><a href="#specialities">Specialities</a><a class="nasconde" href="#find-us">Find us</a><a href="{rel_root}" hreflang="it" lang="it">Italiano</a></nav></div>'''
    return f'''<div class="barra"><a class="marchio" href="{rel_root}">Ceraldi Caffè</a>
<nav aria-label="Principale"><a href="{rel_root}#specialita">Specialità</a><a href="{rel_root}storie/">Storie</a><a class="nasconde" href="{rel_root}#dove">Dove siamo</a><a href="{rel_root}en/" hreflang="en" lang="en">English</a></nav></div>'''

def piede(rel_root, lang='it'):
    it = lang == 'it'
    return f'''<footer class="piede"><div class="contenitore">
<div><p><b style="font-family:var(--display);font-size:20px;color:#F3E9DC;font-weight:400">Ceraldi Caffè</b></p>
<p>{e(BAR['indirizzo'])}, {e(BAR['cap_citta'])}</p><p>{e(BAR['orari'] if it else BAR['orari_en'])}</p>
<p><a href="tel:{BAR['tel_link']}">{BAR['telefono']}</a></p></div>
<div><p><a href="{BAR['instagram']}" rel="noopener">Instagram</a></p><p><a href="{BAR['facebook']}" rel="noopener">Facebook</a></p>
<p><a href="{BAR['menu']}" rel="noopener">{'Menu online' if it else 'Online menu'}</a></p></div>
<div><p>Ceraldi Group S.r.l.</p><p><a href="{rel_root}../privacy.html">Privacy</a></p>
<p>{'Foto della tradizione: Wikimedia Commons, crediti sotto ogni immagine.' if it else 'Tradition photos: Wikimedia Commons, credited under each image.'}</p></div>
</div></footer>
</body>
</html>
'''

def credito(k):
    f = FOTO[k]
    return f'<figcaption class="credito">Foto: {e(f["autore"])}, <a href="{f["lic_url"]}" rel="license noopener">{f["licenza"]}</a>, via <a href="{f["fonte"]}" rel="noopener">Wikimedia Commons</a></figcaption>'

def immagine(k, rel_root, sizes, eager=False):
    f = FOTO[k]
    return (f'<img src="{rel_root}img/{k}-1200.webp" srcset="{rel_root}img/{k}-640.webp 640w, {rel_root}img/{k}-1200.webp 1200w" '
            f'sizes="{sizes}" width="1200" height="900" alt="{e(f["alt"])}" {"fetchpriority=\"high\"" if eager else "loading=\"lazy\""} decoding="async">')

def ld_bar(lang='it'):
    return {
        "@context": "https://schema.org", "@type": ["CafeOrCoffeeShop", "Bakery"], "@id": BASE + "#bar",
        "name": "Ceraldi Caffè", "url": BASE, "image": BASE + "img/og.jpg", "logo": BASE + "img/apple-touch-icon.png",
        "description": ("Bar e pasticceria napoletana dal 1973 in Piazza Carità: caffè, sfogliatelle, babà, pastiera, buffet freddi e aperitivo."
                        if lang == 'it' else "Neapolitan café and pastry shop since 1973 in Piazza Carità: coffee, sfogliatella, babà, pastiera, cold buffet and aperitivo."),
        "foundingDate": "1973", "telephone": "+39 081 552 3488", "priceRange": "€",
        "address": {"@type": "PostalAddress", "streetAddress": "Piazza Carità, 14", "postalCode": "80134",
                    "addressLocality": "Napoli", "addressRegion": "NA", "addressCountry": "IT"},
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "06:30", "closes": "20:30"}],
        "hasMap": BAR["mappa"], "hasMenu": BAR["menu"], "servesCuisine": ["Caffetteria", "Pasticceria napoletana"],
        "sameAs": [BAR["instagram"], BAR["facebook"]],
    }

def ld_faq(faq):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}

# ── Home (italiano) ──
TRAD = [("sfogliatella", "sfogliatella-riccia", "Sfogliatella", "Riccia o frolla, dal convento di Santa Rosa a via Toledo."),
        ("baba", "baba", "Babà", "Il dolce di un re polacco diventato napoletano."),
        ("pastiera", "pastiera", "Pastiera", "Grano, ricotta e fiori d'arancio: la Pasqua a Napoli."),
        ("zeppole-di-san-giuseppe", "zeppole", "Zeppole", "Crema e amarena per il 19 marzo.")]
TRAD_EN = [("Sfogliatella", "Crisp layers or soft shortcrust, from a convent on the Amalfi Coast."),
           ("Babà", "A Polish king's cake that became Neapolitan."),
           ("Pastiera", "Wheat, ricotta and orange blossom: Easter in Naples."),
           ("Zeppole", "Custard and black cherry for Saint Joseph's Day.")]

def carta(titolo1, l1, titolo2, l2):
    li = lambda l: ''.join(f'<li><b>{e(n)}</b><span>{e(d)}</span></li>' for n, d in l)
    return f'<div class="carta"><div><h3>{titolo1}</h3><ul>{li(l1)}</ul></div><div><h3>{titolo2}</h3><ul>{li(l2)}</ul></div></div>'

def home_it():
    alt = [("it", BASE), ("en", BASE + "en/"), ("x-default", BASE)]
    h = testa("it", "Ceraldi Caffè — Bar e pasticceria napoletana dal 1973 in Piazza Carità, Napoli",
              "Ceraldi Caffè, Piazza Carità 14, Napoli: caffè, sfogliatelle, babà e pastiera dal 1973. Colazione, buffet freddi e aperitivo, tutti i giorni dalle 6:30 alle 20:30.",
              BASE, "", ld=[ld_bar('it'), ld_faq(FAQ)], alternates=alt)
    storie = ''.join(f'<li><a href="storie/{a["slug"]}/"><b>{e(a["titolo"])}</b><span>{e(a["dek"])}</span><small>{a["lettura"]} min di lettura</small></a></li>' for a in ARTICOLI)
    vetr = ''.join(f'<a href="storie/{s}/"><figure>{immagine(k, "", "(max-width: 900px) 50vw, 25vw")}<h3>{t}</h3><p>{e(d)}</p></figure></a>' for s, k, t, d in TRAD)
    crediti = ' '.join(f'{t}: {e(FOTO[k]["autore"])}, <a href="{FOTO[k]["lic_url"]}" rel="license noopener">{FOTO[k]["licenza"]}</a>.' for s, k, t, d in TRAD)
    faq = ''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in FAQ)
    return h + f'''<header class="hero">
{barra("")}
<div class="specchio"><p class="dal">dal 1973</p><h1>Ceraldi Caffè</h1><p class="luogo">Piazza Carità, Napoli</p></div>
<p class="tag">{e(BAR["tagline"])}</p>
<div class="azioni"><a class="btn pieno" href="{BAR["mappa"]}" rel="noopener">Come arrivare</a><a class="btn" href="{BAR["menu"]}" rel="noopener">Guarda il menu</a><a class="btn" href="tel:{BAR["tel_link"]}">Chiama</a></div>
<p class="aperto">Aperto tutti i giorni dalle 6:30 alle 20:30</p>
</header>
<main id="contenuto">
<section class="sezione"><div class="contenitore storia">
<div><h2>Artigiani per passione, dal 1973</h2>
<p>Da oltre cinquant'anni Ceraldi Caffè è il bar di Piazza Carità, tra via Toledo e la Pignasecca. Si entra la mattina presto per il primo caffè e una sfogliatella calda, si torna a metà giornata per un dolce dalla vetrina, ci si ferma la sera per l'aperitivo.</p>
<p>Il locale è quello di un bar napoletano elegante: specchi, sedute in pelle rossa, il bancone sempre affollato e una vetrina di pasticceria rinnovata ogni giorno. La pasticceria segue la tradizione della città, con qualche dolce della casa che non trovi altrove.</p></div>
<p class="citazione">A Napoli il caffè non è solo un caffè: è il momento in cui la città si ferma, anche solo per un minuto.</p>
</div></section>

<section class="sezione" id="specialita" style="background:var(--marmo-2)"><div class="contenitore">
<h2>Le specialità della casa</h2>
<p class="intro">Oltre all'espresso e ai classici della pasticceria napoletana, al bancone trovi caffè e dolci nati da Ceraldi.</p>
{carta("Al bancone", CAFFE_CASA, "In vetrina", DOLCI_CASA)}
<p class="nota">Il menu completo, con allergeni, è online: <a href="{BAR["menu"]}" rel="noopener">guarda il menu</a>.</p>
</div></section>

<section class="sezione"><div class="contenitore">
<h2>La tradizione napoletana in vetrina</h2>
<p class="intro">Sfogliatelle, babà, pastiera e zeppole: i dolci che raccontano Napoli, con la loro storia.</p>
<div class="vetrina">{vetr}</div>
<p class="credito" style="margin-top:18px">Foto da Wikimedia Commons. {crediti}</p>
</div></section>

<section class="sezione" style="padding-top:0"><div class="contenitore">
<h2>Storie dal caffè</h2>
<p class="intro">Riti, leggende e ricette della caffetteria e della pasticceria napoletana.</p>
<ul class="storie">{storie}</ul>
</div></section>

<section class="sezione dove" id="dove"><div class="contenitore">
<h2>Dove siamo</h2>
<p class="intro">In Piazza Carità, nel centro di Napoli, a pochi minuti a piedi dalle stazioni Toledo e Dante della Linea 1.</p>
<dl><div><dt>Indirizzo</dt><dd>{e(BAR["indirizzo"])}<br>{e(BAR["cap_citta"])}</dd></div>
<div><dt>Orari</dt><dd>Tutti i giorni<br>dalle 6:30 alle 20:30</dd></div>
<div><dt>Telefono e WhatsApp</dt><dd><a href="tel:{BAR["tel_link"]}">{BAR["telefono"]}</a><br><a href="{BAR["whatsapp"]}" rel="noopener">Scrivici su WhatsApp</a></dd></div></dl>
<div class="azioni"><a class="btn pieno" href="{BAR["mappa"]}" rel="noopener">Apri in Google Maps</a><a class="btn" href="{BAR["instagram"]}" rel="noopener">Seguici su Instagram</a></div>
</div></section>

<section class="sezione"><div class="contenitore">
<h2>Domande frequenti</h2>
<div class="domande">{faq}</div>
</div></section>
</main>
''' + piede("")

def home_en():
    alt = [("it", BASE), ("en", BASE + "en/"), ("x-default", BASE)]
    h = testa("en", "Ceraldi Caffè — Neapolitan café and pastry shop since 1973, Piazza Carità, Naples",
              "Ceraldi Caffè, Piazza Carità 14, Naples: espresso, sfogliatella, babà and pastiera since 1973. Breakfast, cold buffet and aperitivo, every day 6:30 am – 8:30 pm.",
              BASE + "en/", "../", ld=[ld_bar('en'), ld_faq(FAQ_EN)], alternates=alt)
    vetr = ''.join(f'<a href="../storie/{s}/" hreflang="it"><figure>{immagine(k, "../", "(max-width: 900px) 50vw, 25vw")}<h3>{t}</h3><p>{e(d)}</p></figure></a>'
                   for (s, k, t, _), (_, d) in zip(TRAD, TRAD_EN))
    crediti = ' '.join(f'{t}: {e(FOTO[k]["autore"])}, <a href="{FOTO[k]["lic_url"]}" rel="license noopener">{FOTO[k]["licenza"]}</a>.' for s, k, t, d in TRAD)
    faq = ''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in FAQ_EN)
    return h + f'''<header class="hero">
{barra("../", "en")}
<div class="specchio"><p class="dal">since 1973</p><h1>Ceraldi Caffè</h1><p class="luogo">Piazza Carità, Naples</p></div>
<p class="tag">From breakfast to aperitivo, in the heart of Naples.</p>
<div class="azioni"><a class="btn pieno" href="{BAR["mappa"]}" rel="noopener">Get directions</a><a class="btn" href="{BAR["menu"]}" rel="noopener">See the menu</a><a class="btn" href="tel:{BAR["tel_link"]}">Call</a></div>
<p class="aperto">Open every day from 6:30 am to 8:30 pm</p>
</header>
<main id="contenuto">
<section class="sezione"><div class="contenitore storia">
<div><h2>Craftspeople by passion, since 1973</h2>
<p>For more than fifty years Ceraldi Caffè has been the café of Piazza Carità, between Via Toledo and the Pignasecca market. Locals come in early for their first espresso and a warm sfogliatella, stop by during the day for something from the pastry counter, and come back in the evening for aperitivo.</p>
<p>It is an elegant Neapolitan bar: mirrors, red leather seats, a busy counter and a pastry display refilled every day, following the city's tradition with a few house creations you won't find anywhere else.</p></div>
<p class="citazione">In Naples coffee is never just coffee: it is the moment the city stops, even for a minute.</p>
</div></section>
<section class="sezione" id="specialities" style="background:var(--marmo-2)"><div class="contenitore">
<h2>House specialities</h2>
<p class="intro">Besides espresso and the classics of Neapolitan pastry, our counter serves coffees and cakes created at Ceraldi.</p>
{carta("At the counter", CAFFE_CASA_EN, "From the pastry case", DOLCI_CASA_EN)}
<p class="nota">The full menu, with allergens and an English version, is online: <a href="{BAR["menu"]}" rel="noopener">see the menu</a>.</p>
</div></section>
<section class="sezione"><div class="contenitore">
<h2>Neapolitan tradition, in the pastry case</h2>
<p class="intro">Sfogliatella, babà, pastiera and zeppole, and the stories behind them (in Italian).</p>
<div class="vetrina">{vetr}</div>
<p class="credito" style="margin-top:18px">Photos from Wikimedia Commons. {crediti}</p>
</div></section>
<section class="sezione dove" id="find-us"><div class="contenitore">
<h2>Find us</h2>
<p class="intro">In Piazza Carità, central Naples, a few minutes' walk from Toledo and Dante stations on Metro Line 1.</p>
<dl><div><dt>Address</dt><dd>Piazza Carità, 14<br>80134 Naples, Italy</dd></div>
<div><dt>Opening hours</dt><dd>Every day<br>6:30 am – 8:30 pm</dd></div>
<div><dt>Phone and WhatsApp</dt><dd><a href="tel:{BAR["tel_link"]}">+39 081 552 3488</a><br><a href="{BAR["whatsapp"]}" rel="noopener">Message us on WhatsApp</a></dd></div></dl>
<div class="azioni"><a class="btn pieno" href="{BAR["mappa"]}" rel="noopener">Open in Google Maps</a><a class="btn" href="{BAR["instagram"]}" rel="noopener">Follow us on Instagram</a></div>
</div></section>
<section class="sezione"><div class="contenitore">
<h2>Frequently asked questions</h2>
<div class="domande">{faq}</div>
</div></section>
</main>
''' + piede("../", "en")

def articolo(a):
    url = BASE + f"storie/{a['slug']}/"
    img = BASE + (f"img/{a['foto']}-1200.webp" if a['foto'] else "img/og.jpg")
    ld = [{"@context": "https://schema.org", "@type": "Article", "headline": a["titolo"], "description": a["descrizione"],
           "image": [img], "datePublished": OGGI, "dateModified": OGGI, "inLanguage": "it-IT", "mainEntityOfPage": url,
           "author": {"@type": "Organization", "name": "Ceraldi Caffè", "url": BASE},
           "publisher": {"@type": "Organization", "name": "Ceraldi Caffè", "logo": {"@type": "ImageObject", "url": BASE + "img/apple-touch-icon.png"}}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Ceraldi Caffè", "item": BASE},
              {"@type": "ListItem", "position": 2, "name": "Storie", "item": BASE + "storie/"},
              {"@type": "ListItem", "position": 3, "name": a["titolo"], "item": url}]}]
    og = f"img/{a['foto']}-1200.webp" if a['foto'] else "img/og.jpg"
    h = testa("it", a["titolo_seo"] + " | Ceraldi Caffè", a["descrizione"], url, "../../", og_img=og, ld=ld)
    fig = f'<figure>{immagine(a["foto"], "../../", "(max-width: 800px) 100vw, 760px", eager=True)}{credito(a["foto"])}</figure>' if a['foto'] else ''
    prova = ''.join(f'<li><b>{e(n)}</b><br><span>{e(d)}</span></li>' for n, d in a["provare"])
    fonti = ''.join(f'<li><a href="{u}" rel="noopener">{e(t)}</a></li>' for t, u in a["fonti"])
    altre = ''.join(f'<li><a href="../{b["slug"]}/"><b>{e(b["titolo"])}</b><span>{e(b["dek"])}</span><small>{b["lettura"]} min</small></a></li>' for b in ARTICOLI if b is not a)[:]
    return h + f'''<header class="testata-scura">{barra("../../")}</header>
<main id="contenuto" class="articolo"><div class="contenitore">
<p class="briciole"><a href="../../">Ceraldi Caffè</a> / <a href="../">Storie</a></p>
<article>
<h1>{e(a["titolo"])}</h1>
<p class="dek">{e(a["dek"])}</p>
<p class="meta">{a["lettura"]} minuti di lettura</p>
{fig}
<div class="corpo">{a["corpo"]}</div>
<aside class="cartellino"><h2>Da provare da Ceraldi</h2><p>In Piazza Carità 14, tutti i giorni dalle 6:30 alle 20:30.</p><ul>{prova}</ul>
<a class="btn" href="{BAR["menu"]}" rel="noopener">Guarda il menu</a></aside>
<section class="fonti"><h2>Fonti</h2><ul>{fonti}</ul></section>
</article>
<section class="altre"><h2>Altre storie</h2><ul class="storie">{altre}</ul></section>
</div></main>
''' + piede("../../")

def indice_storie():
    url = BASE + "storie/"
    h = testa("it", "Storie dal caffè: tradizioni della caffetteria e pasticceria napoletana | Ceraldi Caffè",
              "Caffè napoletano, caffè sospeso, sfogliatella, babà, pastiera e zeppole: storie e leggende della tradizione napoletana raccontate da Ceraldi Caffè.", url, "../",
              ld=[{"@context": "https://schema.org", "@type": "CollectionPage", "name": "Storie dal caffè", "url": url,
                   "hasPart": [{"@type": "Article", "headline": a["titolo"], "url": url + a["slug"] + "/"} for a in ARTICOLI]}])
    lista = ''.join(f'<li><a href="{a["slug"]}/"><b>{e(a["titolo"])}</b><span>{e(a["dek"])}</span><small>{a["lettura"]} min di lettura</small></a></li>' for a in ARTICOLI)
    return h + f'''<header class="testata-scura">{barra("../")}</header>
<main id="contenuto" class="articolo"><div class="contenitore">
<p class="briciole"><a href="../">Ceraldi Caffè</a></p>
<h1>Storie dal caffè</h1>
<p class="dek">Riti, leggende e ricette della caffetteria e della pasticceria napoletana, raccontati dal bancone di Piazza Carità.</p>
<ul class="storie" style="margin-top:36px">{lista}</ul>
</div></main>
''' + piede("../")

def sitemap():
    urls = [(BASE, "1.0"), (BASE + "en/", "0.8"), (BASE + "storie/", "0.7")] + [(BASE + f"storie/{a['slug']}/", "0.6") for a in ARTICOLI]
    righe = ''.join(f'<url><loc>{u}</loc><lastmod>{OGGI}</lastmod><priority>{p}</priority></url>' for u, p in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{righe}</urlset>\n'

FAVICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><circle cx="32" cy="32" r="32" fill="#241610"/><circle cx="32" cy="32" r="28.5" fill="none" stroke="#B48C4A" stroke-width="1.5"/><text x="32" y="44" text-anchor="middle" font-family="Didot, 'Bodoni 72', Georgia, serif" font-size="34" fill="#DCC08A">C</text></svg>'''

if __name__ == "__main__":
    scrivi("index.html", home_it())
    scrivi("en/index.html", home_en())
    scrivi("storie/index.html", indice_storie())
    for a in ARTICOLI:
        scrivi(f"storie/{a['slug']}/index.html", articolo(a))
    scrivi("sitemap.xml", sitemap())
    scrivi("favicon.svg", FAVICON)
    print("Pagine generate:", 3 + len(ARTICOLI))
