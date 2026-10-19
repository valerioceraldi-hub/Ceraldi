# -*- coding: utf-8 -*-
"""Genera le pagine del sito di Ceraldi Caffè.
Uso:  python3 caffe/_build/build.py   (dalla radice del repository)
La cartella _build non viene pubblicata da GitHub Pages (Jekyll ignora le cartelle con _)."""
import json, os, html
from contenuti import *
from pagine import *

QUI = os.path.dirname(os.path.abspath(__file__))
SITO = os.path.dirname(QUI)
e = html.escape

# Font ospitati sul sito (nessuna chiamata a server esterni: niente dati dei visitatori a terzi)
def font(rr):
    return (f'<link rel="preload" href="{rr}assets/font/BodoniModa-normal-400_600-latin.woff2" as="font" type="font/woff2" crossorigin>'
            f'<link rel="preload" href="{rr}assets/font/WorkSans-normal-400-latin.woff2" as="font" type="font/woff2" crossorigin>'
            f'<link rel="stylesheet" href="{rr}assets/font.css">')
FOTO.update({
    "aspritz": {"alt": "Aspritz di Ceraldi Caffè al bancone, con fetta d'arancia", "w": [1024, 640], "r": (4, 3)},
    "caffe-ceraldi": {"alt": "Il Caffè Ceraldi con cioccolata, crema di caffè e panna sul bancone in marmo", "w": [1024, 640], "r": (3, 2)},
    "saltimbocca": {"alt": "Saltimbocca con porchetta e provola di Ceraldi Caffè", "w": [768, 480], "r": (3, 4)},
    "frittatina": {"alt": "Frittatina napoletana di bucatini aperta a metà", "w": [800, 480], "r": (4, 5)},
})
GIORNI = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def scrivi(rel, testo):
    p = os.path.join(SITO, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(testo)

# ── Pezzi comuni ──────────────────────────────────────────────────────
def testa(lang, titolo, descr, url, rr, og_img="img/og.jpg", ld=None, alternates=None, tipo="website", preload=None):
    alt = ''.join(f'<link rel="alternate" hreflang="{h}" href="{u}">' for h, u in (alternates or []))
    lds = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (ld or []))
    pre = f'<link rel="preload" as="image" href="{preload}" fetchpriority="high">' if preload else ''
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titolo)}</title>
<meta name="description" content="{e(descr)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{url}">{alt}
<meta name="theme-color" content="#241610">
<meta property="og:type" content="{tipo}">
<meta property="og:site_name" content="Ceraldi Caffè">
<meta property="og:title" content="{e(titolo)}">
<meta property="og:description" content="{e(descr)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}{og_img}">
<meta property="og:locale" content="{'it_IT' if lang == 'it' else 'en_GB'}">
<meta name="twitter:card" content="summary_large_image">
<meta name="geo.region" content="IT-NA"><meta name="geo.placename" content="Napoli">
<link rel="icon" href="{rr}favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{rr}img/apple-touch-icon.png">
{pre}{font(rr)}
<link rel="stylesheet" href="{rr}assets/sito.css">
{lds}
</head>
<body>
<a class="salta" href="#contenuto">{'Vai al contenuto' if lang == 'it' else 'Skip to content'}</a>
'''

VOCI_NAV = [("bar/", "Il bar"), ("pasticceria/", "Pasticceria"), ("rosticceria/", "Rosticceria"), ("aspritz/", "Aspritz"),
            ("menu/", "Menu"), ("storie/", "Storie"), ("contatti/", "Contatti")]
def barra(rr, lang='it'):
    logo = f'<img src="{rr}img/logo-ceraldi-chiaro.svg" width="150" height="52" alt="Ceraldi Caffè">'
    if lang == 'en':
        voci = [("#breakfast", "Breakfast"), ("#specialities", "Specialities"), (f"{rr}menu/", "Menu"), ("#find-us", "Find us")]
        lingua = f'<a href="{rr}" hreflang="it" lang="it">Italiano</a>'
        home = f"{rr}en/"
    else:
        voci = [(rr + h, t) for h, t in VOCI_NAV]
        lingua = f'<a href="{rr}en/" hreflang="en" lang="en">English</a>'
        home = rr or "./"
    links = ''.join(f'<a href="{h}">{t}</a>' for h, t in voci) + lingua
    return f'''<div class="barra"><a class="marchio" href="{home}">{logo}</a>
<nav class="nav-larga" aria-label="{'Main' if lang == 'en' else 'Principale'}">{links}</nav>
<details class="nav-mobile"><summary>{'Menu' if lang == 'en' else 'Menu'}<span aria-hidden="true"></span></summary><nav aria-label="{'Main' if lang == 'en' else 'Principale'}">{links}</nav></details></div>'''

def piede(rr, lang='it'):
    it = lang == 'it'
    return f'''<footer class="piede"><div class="contenitore">
<div><img src="{rr}img/logo-ceraldi-chiaro.svg" width="180" height="62" alt="Ceraldi Caffè, artigiani per passione dal 1973" loading="lazy">
<p style="margin-top:12px">{e(BAR['indirizzo'])}, {e(BAR['cap_citta'])}</p><p>{e(BAR['orari'] if it else BAR['orari_en'])}</p></div>
<div><p><a href="tel:{BAR['tel_link']}">{'Tel.' if it else 'Phone'} {BAR['telefono']}</a></p><p><a href="tel:{BAR['cell_link']}">{'Cell.' if it else 'Mobile'} {BAR['cellulare']}</a></p>
<p><a href="{BAR['whatsapp']}" rel="noopener">WhatsApp</a></p></div>
<div><p><a href="{rr}menu/">{'Il menu' if it else 'Menu'}</a></p><p><a href="{BAR['google_recensioni']}" rel="noopener">{'Recensioni Google' if it else 'Google reviews'}</a></p><p><a href="{BAR['tripadvisor']}" rel="noopener">Tripadvisor</a></p></div>
<div><p><a href="{BAR['instagram']}" rel="noopener">Instagram</a></p><p><a href="{BAR['facebook']}" rel="noopener">Facebook</a></p><p><a href="{rr}storie/">{'Storie dal caffè' if it else 'Stories (Italian)'}</a></p><p><a href="{rr}contatti/">{'Contatti' if it else 'Contact'}</a></p></div>
<p class="legale">© {RAGIONE_SOCIALE}, Piazza Carità 14, 80134 Napoli. P. IVA {PIVA}. <a href="{rr}privacy/">Privacy e cookie</a></p>
</div></footer>
<nav class="barra-fissa" aria-label="{'Contatti rapidi' if it else 'Quick contacts'}"><a href="tel:{BAR['tel_link']}">{'Chiama' if it else 'Call'}</a><a href="{BAR['mappa']}" rel="noopener">{'Indicazioni' if it else 'Directions'}</a><a href="{rr}menu/">Menu</a></nav>
</body>
</html>
'''

def immagine(k, rr, sizes, eager=False, cls=""):
    f = FOTO[k]; w = f["w"]; rw, rh = f["r"]; big = w[0]
    srcset = ', '.join(f'{rr}img/{k}-{x}.webp {x}w' for x in sorted(w))
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ''
    return (f'<img{c} src="{rr}img/{k}-{big}.webp" srcset="{srcset}" sizes="{sizes}" width="{big}" height="{round(big * rh / rw)}" '
            f'alt="{e(f["alt"])}" {load} decoding="async">')

def carta(titolo1, l1, titolo2, l2):
    li = lambda l: ''.join(f'<li><b>{e(n)}</b><span>{e(d)}</span></li>' for n, d in l)
    return f'<div class="carta"><div><h3>{titolo1}</h3><ul>{li(l1)}</ul></div><div><h3>{titolo2}</h3><ul>{li(l2)}</ul></div></div>'

def lista(l):
    return '<ul class="lista-menu">' + ''.join(f'<li><b>{e(n)}</b><span>{e(d)}</span></li>' for n, d in l) + '</ul>'

def faq_html(faq):
    return ''.join(f'<details><summary>{e(q)}</summary><p>{h if h else e(a)}</p></details>' for q, a, h in faq)

# ── Dati strutturati ──────────────────────────────────────────────────
def ld_bar(lang='it'):
    return {
        "@context": "https://schema.org", "@type": ["CafeOrCoffeeShop", "Bakery"], "@id": BASE + "#bar",
        "name": "Ceraldi Caffè", "alternateName": ["Caffè Ceraldi", "Ceraldi Caffe", "Bar Ceraldi Piazza Carità"],
        "slogan": "Artigiani per passione dal 1973", "url": BASE,
        "logo": BASE + "img/logo-ceraldi.svg",
        "image": [BASE + "img/sala-1024.webp", BASE + "img/squadra-1600.webp", BASE + "img/sfogliatella-riccia-1024.webp", BASE + "img/baba-1024.webp"],
        "description": ("Bar e pasticceria napoletana della famiglia Ceraldi, attiva dal 1973 (prima in Piazza Garibaldi, dal 2002 in Piazza Carità, Napoli). Pasticceria di produzione propria con ricette di famiglia custodite da oltre cento anni: sfogliatelle, babà, pastiera, zeppole. Colazione all'italiana con croissant e brioche, caffè della casa, buffet freddi e aperitivo."
                        if lang == 'it' else "Neapolitan café and pastry shop run by the Ceraldi family since 1973 (first in Piazza Garibaldi, in Piazza Carità, Naples, since 2002). In-house pastries from family recipes kept for over a hundred years: sfogliatella, babà, pastiera, zeppole. Italian breakfast with croissants and brioche, house coffees, cold buffet and aperitivo."),
        "foundingDate": "1973", "telephone": "+39 081 552 3488", "priceRange": "€",
        "contactPoint": [{"@type": "ContactPoint", "telephone": "+39 081 552 3488", "contactType": "customer service", "availableLanguage": ["it", "en"]},
                         {"@type": "ContactPoint", "telephone": "+39 328 438 8404", "contactType": "customer service", "availableLanguage": ["it"]}],
        "address": {"@type": "PostalAddress", "streetAddress": "Piazza Carità, 14", "postalCode": "80134",
                    "addressLocality": "Napoli", "addressRegion": "NA", "addressCountry": "IT"},
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": GIORNI, "opens": "06:30", "closes": "20:30"}],
        "geo": {"@type": "GeoCoordinates", "latitude": GEO[0], "longitude": GEO[1]},
        "hasMap": BAR["mappa"], "hasMenu": BASE + "menu/", "vatID": "IT" + PIVA, "legalName": RAGIONE_SOCIALE,
        "servesCuisine": ["Caffetteria", "Pasticceria napoletana", "Colazione italiana", "Aperitivo"],
        "knowsAbout": ["caffè napoletano", "sfogliatella", "babà", "pastiera napoletana", "zeppole di San Giuseppe", "pasticceria napoletana", "colazione all'italiana"],
        "sameAs": [BAR["instagram"], BAR["facebook"], BAR["tripadvisor"], BAR["mappa"]],
    }

def ld_sito():
    return {"@context": "https://schema.org", "@type": "WebSite", "@id": BASE + "#sito", "name": "Ceraldi Caffè", "url": BASE,
            "inLanguage": ["it-IT", "en"], "publisher": {"@id": BASE + "#bar"}}

def ld_faq(faq):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a, h in faq]}

# ── Home italiana ─────────────────────────────────────────────────────
TRAD = [("sfogliatella", "sfogliatella-riccia", "Sfogliatella", "Riccia o frolla, dal convento di Santa Rosa a via Toledo."),
        ("baba", "baba", "Babà", "Il dolce di un re polacco diventato napoletano."),
        ("pastiera", "pastiera", "Pastiera", "Grano, ricotta e fiori d'arancio: la Pasqua a Napoli."),
        ("zeppole-di-san-giuseppe", "zeppola", "Zeppola", "Crema e amarena per il 19 marzo.")]
TRAD_EN = ["Crisp layers or soft shortcrust, from a convent on the Amalfi Coast.", "A Polish king's cake that became Neapolitan.",
           "Wheat, ricotta and orange blossom: Easter in Naples.", "Custard and black cherry for Saint Joseph's Day."]

def recensioni(lang='it'):
    it = lang == 'it'
    return f'''<section class="sezione recensioni" id="{'recensioni' if it else 'reviews'}"><div class="contenitore recensioni-griglia">
<div><p class="voto"><span class="voto-num">4,3</span><span class="voto-stelle" aria-hidden="true">★★★★<i>★</i></span></p>
<p class="voto-txt">{'Valutazione media su Google, con quasi 2.000 recensioni dei nostri clienti.' if it else 'Average rating on Google, from almost 2,000 customer reviews.'}</p></div>
<div><h2>{'Cosa dicono di noi' if it else 'What our customers say'}</h2>
<p class="intro">{'Leggi le opinioni di chi è passato da Piazza Carità, o lascia la tua dopo la visita.' if it else 'Read what visitors say about us, or leave your own review after your visit.'}</p>
<div class="azioni sinistra"><a class="btn scuro" href="{BAR["google_recensioni"]}" rel="noopener">{'Recensioni su Google' if it else 'Reviews on Google'}</a>
<a class="btn scuro-vuoto" href="{BAR["tripadvisor"]}" rel="noopener">{'Recensioni su Tripadvisor' if it else 'Reviews on Tripadvisor'}</a>
<a class="btn scuro-vuoto" href="{BAR["google_scrivi"]}" rel="noopener">{'Lascia una recensione' if it else 'Write a review'}</a></div></div>
</div></section>'''

ACCESSI = [("bar/", "caffe-ceraldi", "Il bar", "Caffè, colazione ed English breakfast"),
           ("pasticceria/", "baba", "Pasticceria", "Produzione propria, ricette di famiglia"),
           ("rosticceria/", "frittatina", "Rosticceria", "Frittatine, freselle e pranzo veloce"),
           ("aspritz/", "aspritz", "Aspritz", "Lo spritz napoletano fatto in casa"),
           ("storia/", "squadra", "La nostra storia", "Dal 1973, una famiglia di baristi")]

def home_it():
    alt = [("it", BASE), ("en", BASE + "en/"), ("x-default", BASE)]
    h = testa("it", "Ceraldi Caffè | Bar e pasticceria a Napoli, Piazza Carità",
              "Ceraldi Caffè, Piazza Carità 14, Napoli: bar e pasticceria di produzione propria dal 1973. Sfogliatelle, babà, pastiera, colazione con croissant e brioche, aperitivo. Aperti tutti i giorni 6:30–20:30.",
              BASE, "", ld=[ld_bar('it'), ld_sito(), ld_faq(FAQ)], alternates=alt, preload="img/sala-1024.webp")
    storie = ''.join(f'<li><a href="storie/{a["slug"]}/"><b>{e(a["titolo"])}</b><span>{e(a["dek"])}</span><small>{a["lettura"]} min di lettura</small></a></li>' for a in ARTICOLI)
    vetr = ''.join(f'<a href="storie/{s}/"><figure>{immagine(k, "", "(max-width: 900px) 50vw, 25vw")}<h3>{t}</h3><p>{e(d)}</p></figure></a>' for s, k, t, d in TRAD)
    return h + f'''<header class="hero">
{barra("")}
<div class="contenitore hero-griglia">
<div class="hero-testo">
<p class="dal">Artigiani per passione dal 1973</p>
<h1>Bar e pasticceria napoletana in Piazza Carità</h1>
<p class="tag">{e(BAR["tagline"])} Dolci di produzione propria, con ricette di famiglia custodite da oltre cento anni.</p>
<div class="azioni sinistra"><a class="btn pieno" href="{BAR["mappa"]}" rel="noopener">Come arrivare</a><a class="btn" href="menu/">Guarda il menu</a><a class="btn" href="tel:{BAR["tel_link"]}">Chiama</a></div>
<p class="aperto">Aperto tutti i giorni dalle 6:30 alle 20:30<br><a href="#recensioni">Valutazione 4,3 su Google</a></p>
</div>
<figure class="specchio">{immagine("sala", "", "(max-width: 900px) 92vw, 480px", eager=True)}</figure>
</div>
</header>
<main id="contenuto">

<nav class="accessi" aria-label="Cosa trovi da Ceraldi"><div class="contenitore accessi-griglia">
{''.join(f'<a href="{h}"><figure>{immagine(k, "", "(max-width: 640px) 50vw, 220px")}</figure><b>{t}</b><span>{d}</span></a>' for h, k, t, d in ACCESSI)}
</div></nav>

<section class="sezione"><div class="contenitore storia">
<div><h2>Artigiani per passione, dal 1973</h2>
<p>La storia della famiglia Ceraldi nei bar di Napoli comincia nei primi anni Settanta in Piazza Garibaldi. Nel 2002 l'arrivo in Piazza Carità, lungo via Toledo, a due passi dalla Pignasecca e dai Quartieri Spagnoli: da allora è il nostro bar. Si entra la mattina presto per il primo caffè e una sfogliatella calda, si torna a metà giornata per un dolce dalla vetrina, ci si ferma la sera per l'aperitivo.</p>
<p>La nostra pasticceria è di <strong>produzione propria</strong>: sfogliatelle, babà, pastiere e torte nascono da ricette di famiglia custodite da oltre cento anni, insieme alle creazioni della casa. Il locale è quello di un bar napoletano elegante, con specchi, poltroncine in pelle rossa e un bancone sempre affollato.</p>
<p><a class="link-forte" href="storia/">Leggi la nostra storia</a></p></div>
<figure class="foto-larga">{immagine("squadra", "", "(max-width: 900px) 100vw, 560px")}<figcaption>La squadra di Ceraldi Caffè al bancone.</figcaption></figure>
</div></section>

<section class="sezione in-breve" aria-labelledby="breve"><div class="contenitore">
<h2 id="breve">Ceraldi Caffè in breve</h2>
<dl class="scheda">
<div><dt>Che cos'è</dt><dd>Bar, caffetteria e pasticceria napoletana di produzione propria</dd></div>
<div><dt>Storia</dt><dd>Famiglia Ceraldi dal 1973, in Piazza Carità dal 2002</dd></div>
<div><dt>Indirizzo</dt><dd>Piazza Carità 14, 80134 Napoli, vicino a via Toledo e alla metro Toledo</dd></div>
<div><dt>Orari</dt><dd>Tutti i giorni, 6:30 – 20:30</dd></div>
<div><dt>Specialità</dt><dd>Sfogliatella riccia e frolla, babà, pastiera, Caffè Ceraldi, Cestino, Segreto amalfitano</dd></div>
<div><dt>Colazione</dt><dd>Croissant, brioche, graffa napoletana, cappuccino e caffè</dd></div>
<div><dt>Contatti</dt><dd>Telefono <a href="tel:{BAR["tel_link"]}">081 552 3488</a>, cellulare <a href="tel:{BAR["cell_link"]}">328 438 8404</a></dd></div>
<div><dt>Menu</dt><dd><a href="menu/">Menu completo con prezzi</a></dd></div>
</dl>
</div></section>

<section class="sezione" id="colazione"><div class="contenitore due-colonne">
<div><h2>La colazione, all'italiana e alla napoletana</h2>
<p class="intro">Il cornetto caldo con il cappuccino, come in tutta Italia. Oppure la sfogliatella e la graffa, come si fa a Napoli. Al nostro bancone trovi entrambe, dalle 6:30 del mattino.</p>
{lista(COLAZIONE)}
<p class="nota"><a href="storie/colazione-napoletana/">Leggi: la colazione a Napoli, tra cornetto e sfogliatella</a></p></div>
<figure class="foto-alta">{immagine("sfogliatella-riccia", "", "(max-width: 900px) 100vw, 480px")}</figure>
</div></section>

<section class="sezione" id="specialita" style="background:var(--marmo-2)"><div class="contenitore">
<h2>Le specialità della casa</h2>
<p class="intro">Oltre all'espresso e ai classici napoletani, caffè e dolci nati da Ceraldi.</p>
<div class="trittico">{immagine("cestino", "", "(max-width: 640px) 33vw, 300px")}{immagine("babamisu", "", "(max-width: 640px) 33vw, 300px")}{immagine("pellecchiella", "", "(max-width: 640px) 33vw, 300px")}</div>
{carta("Al bancone", CAFFE_CASA, "In vetrina", DOLCI_CASA)}
<p class="nota">Tutti i prodotti, con prezzi e allergeni: <a href="menu/">guarda il menu completo</a>.</p>
</div></section>

<section class="sezione"><div class="contenitore">
<h2>La tradizione napoletana, fatta da noi</h2>
<p class="intro">Sfogliatelle, babà, pastiera e zeppole: i dolci che raccontano Napoli, con la loro storia.</p>
<div class="vetrina">{vetr}</div>
</div></section>

<section class="sezione aperitivo"><div class="contenitore due-colonne inverti">
<figure class="foto-alta">{immagine("aperitivo", "", "(max-width: 900px) 100vw, 520px")}</figure>
<div><h2>E la sera, l'aperitivo</h2>
<p class="intro">Spritz, cocktail, birre e buffet freddi: la giornata in Piazza Carità finisce al tavolo, con gli amici.</p>
<div class="azioni sinistra"><a class="btn scuro" href="aspritz/">Scopri l'Aspritz</a><a class="btn scuro-vuoto" href="menu/#cocktails-birre-alcolici">Cocktail e drink</a></div></div>
</div></section>

{recensioni('it')}

<section class="sezione"><div class="contenitore">
<h2>Storie dal caffè</h2>
<p class="intro">Riti, leggende, ricette e luoghi: la cultura napoletana raccontata dal bancone di Piazza Carità.</p>
<ul class="storie">{storie}</ul>
</div></section>

<section class="sezione dove" id="dove"><div class="contenitore">
<h2>Dove siamo</h2>
<p class="intro">In Piazza Carità, lungo via Toledo, a pochi minuti a piedi dalle stazioni Toledo e Dante della Linea 1.</p>
<dl><div><dt>Indirizzo</dt><dd>{e(BAR["indirizzo"])}<br>{e(BAR["cap_citta"])}</dd></div>
<div><dt>Orari</dt><dd>Tutti i giorni<br>dalle 6:30 alle 20:30</dd></div>
<div><dt>Telefono</dt><dd><a href="tel:{BAR["tel_link"]}">081 552 3488</a> (anche <a href="{BAR["whatsapp"]}" rel="noopener">WhatsApp</a>)<br>Cellulare <a href="tel:{BAR["cell_link"]}">328 438 8404</a></dd></div></dl>
<div class="azioni sinistra" style="margin-top:36px"><a class="btn pieno" href="{BAR["mappa"]}" rel="noopener">Apri in Google Maps</a><a class="btn" href="{BAR["instagram"]}" rel="noopener">Seguici su Instagram</a></div>
</div></section>

<section class="sezione"><div class="contenitore">
<h2>Domande frequenti</h2>
<div class="domande">{faq_html(FAQ)}</div>
</div></section>
</main>
''' + piede("")

# ── Home inglese ──────────────────────────────────────────────────────
def home_en():
    alt = [("it", BASE), ("en", BASE + "en/"), ("x-default", BASE)]
    h = testa("en", "Ceraldi Caffè | Café and pastry shop in Naples, Piazza Carità",
              "Ceraldi Caffè, Piazza Carità 14, Naples: café and in-house pastry shop since 1973. Sfogliatella, babà, pastiera, Italian breakfast with croissants, aperitivo. Open every day 6:30 am – 8:30 pm.",
              BASE + "en/", "../", ld=[ld_bar('en'), ld_faq(FAQ_EN)], alternates=alt, preload="../img/sala-1024.webp")
    vetr = ''.join(f'<a href="../storie/{s}/" hreflang="it"><figure>{immagine(k, "../", "(max-width: 900px) 50vw, 25vw")}<h3>{t}</h3><p>{e(d)}</p></figure></a>'
                   for (s, k, t, _), d in zip(TRAD, TRAD_EN))
    return h + f'''<header class="hero">
{barra("../", "en")}
<div class="contenitore hero-griglia">
<div class="hero-testo">
<p class="dal">Craftspeople by passion since 1973</p>
<h1>Neapolitan café and pastry shop in Piazza Carità</h1>
<p class="tag">From breakfast to aperitivo, in the heart of Naples. Pastries made in-house from family recipes kept for over a hundred years.</p>
<div class="azioni sinistra"><a class="btn pieno" href="{BAR["mappa"]}" rel="noopener">Get directions</a><a class="btn" href="../menu/">See the menu</a><a class="btn" href="tel:{BAR["tel_link"]}">Call</a></div>
<p class="aperto">Open every day from 6:30 am to 8:30 pm<br><a href="#reviews">Rated 4.3 on Google</a></p>
</div>
<figure class="specchio">{immagine("sala", "../", "(max-width: 900px) 92vw, 480px", eager=True)}</figure>
</div>
</header>
<main id="contenuto">
<section class="sezione"><div class="contenitore storia">
<div><h2>Craftspeople by passion, since 1973</h2>
<p>The Ceraldi family's story in Naples cafés began in the early 1970s in Piazza Garibaldi. In 2002 we moved to Piazza Carità, on Via Toledo, steps from the Pignasecca market and the Spanish Quarter. Locals come in early for their first espresso and a warm sfogliatella, stop by during the day for something from the pastry case, and come back in the evening for aperitivo.</p>
<p>Our pastries are <strong>made in-house</strong> from family recipes kept for over a hundred years, alongside our own creations. It is an elegant Neapolitan bar, with mirrors, red leather armchairs and a busy counter.</p></div>
<figure class="foto-larga">{immagine("squadra", "../", "(max-width: 900px) 100vw, 560px")}<figcaption>The Ceraldi Caffè team at the counter.</figcaption></figure>
</div></section>
<section class="sezione" id="breakfast"><div class="contenitore due-colonne">
<div><h2>Breakfast, Italian and Neapolitan style</h2>
<p class="intro">A warm croissant with a cappuccino, as everywhere in Italy, or a sfogliatella and a graffa, the Neapolitan way. Served from 6:30 am.</p>
{lista(COLAZIONE_EN)}</div>
<figure class="foto-alta">{immagine("sfogliatella-riccia", "../", "(max-width: 900px) 100vw, 480px")}</figure>
</div></section>
<section class="sezione" id="specialities" style="background:var(--marmo-2)"><div class="contenitore">
<h2>House specialities</h2>
<p class="intro">Besides espresso and Neapolitan classics, coffees and cakes created at Ceraldi.</p>
<div class="trittico">{immagine("cestino", "../", "(max-width: 640px) 33vw, 300px")}{immagine("babamisu", "../", "(max-width: 640px) 33vw, 300px")}{immagine("pellecchiella", "../", "(max-width: 640px) 33vw, 300px")}</div>
{carta("At the counter", CAFFE_CASA_EN, "From the pastry case", DOLCI_CASA_EN)}
<p class="nota">The full menu with prices (in Italian): <a href="../menu/">see the menu</a>. An English version is available on our <a href="{BAR["menu"]}" rel="noopener">interactive menu</a>.</p>
</div></section>
<section class="sezione"><div class="contenitore">
<h2>Neapolitan tradition, made in-house</h2>
<p class="intro">Sfogliatella, babà, pastiera and zeppola, and the stories behind them (in Italian).</p>
<div class="vetrina">{vetr}</div>
</div></section>
{recensioni('en')}
<section class="sezione dove" id="find-us"><div class="contenitore">
<h2>Find us</h2>
<p class="intro">In Piazza Carità on Via Toledo, a few minutes' walk from Toledo and Dante stations on Metro Line 1.</p>
<dl><div><dt>Address</dt><dd>Piazza Carità, 14<br>80134 Naples, Italy</dd></div>
<div><dt>Opening hours</dt><dd>Every day<br>6:30 am – 8:30 pm</dd></div>
<div><dt>Phone</dt><dd><a href="tel:{BAR["tel_link"]}">+39 081 552 3488</a> (also <a href="{BAR["whatsapp"]}" rel="noopener">WhatsApp</a>)<br>Mobile <a href="tel:{BAR["cell_link"]}">+39 328 438 8404</a></dd></div></dl>
<div class="azioni sinistra" style="margin-top:36px"><a class="btn pieno" href="{BAR["mappa"]}" rel="noopener">Open in Google Maps</a><a class="btn" href="{BAR["instagram"]}" rel="noopener">Follow us on Instagram</a></div>
</div></section>
<section class="sezione"><div class="contenitore">
<h2>Frequently asked questions</h2>
<div class="domande">{faq_html(FAQ_EN)}</div>
</div></section>
</main>
''' + piede("../", "en")

# ── Articoli ──────────────────────────────────────────────────────────
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
def data_it(d):
    return f"{int(d[8:10])} {MESI[int(d[5:7]) - 1]} {d[:4]}"

def meta_articolo(a):
    pub = a.get("pubblicato", PUBBLICATO); agg = a.get("aggiornato")
    riga = f'Di <a href="../../storia/">{e(AUTORE)}</a>. Pubblicato il <time datetime="{pub}">{data_it(pub)}</time>'
    if agg and agg != pub:
        riga += f', aggiornato il <time datetime="{agg}">{data_it(agg)}</time>'
    if a.get("revisore"):
        riga += f'. Rivisto da {e(a["revisore"])}'
    c = CATEGORIA_DI[a["slug"]]
    return riga + f'. {a["lettura"]} minuti di lettura. <a href="../{c["slug"]}/">{e(c["nome"])}</a>'

def articolo(a):
    url = BASE + f"storie/{a['slug']}/"
    k = a['foto']
    img = BASE + (f"img/{k}-{FOTO[k]['w'][0]}.webp" if k else "img/og.jpg")
    ld = [{"@context": "https://schema.org", "@type": "Article", "headline": a["titolo"], "description": a["descrizione"],
           "image": [img], "datePublished": a.get("pubblicato", PUBBLICATO), "dateModified": a.get("aggiornato", a.get("pubblicato", PUBBLICATO)), "inLanguage": "it-IT", "mainEntityOfPage": url,
           "isPartOf": {"@id": BASE + "#sito"}, "articleSection": CATEGORIA_DI[a["slug"]]["nome"],
           "citation": [f[1] for f in a["fonti"]],
           "author": {"@type": "Organization", "name": AUTORE, "url": BASE + "storia/"},
           "publisher": {"@type": "Organization", "name": "Ceraldi Caffè", "logo": {"@type": "ImageObject", "url": BASE + "img/apple-touch-icon.png"}}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Ceraldi Caffè", "item": BASE},
              {"@type": "ListItem", "position": 2, "name": "Storie", "item": BASE + "storie/"},
              {"@type": "ListItem", "position": 3, "name": CATEGORIA_DI[a["slug"]]["nome"], "item": BASE + f"storie/{CATEGORIA_DI[a['slug']]['slug']}/"},
              {"@type": "ListItem", "position": 4, "name": a["titolo"], "item": url}]}]
    og = f"img/{k}-{FOTO[k]['w'][0]}.webp" if k else "img/og.jpg"
    h = testa("it", a["titolo_seo"] + " | Ceraldi Caffè", a["descrizione"], url, "../../", og_img=og, ld=ld, tipo="article")
    fig = f'<figure class="{"verticale" if FOTO[k]["r"][1] > FOTO[k]["r"][0] else ""}">{immagine(k, "../../", "(max-width: 800px) 100vw, 760px", eager=True)}</figure>' if k else ''
    prova = ''.join(f'<li><b>{e(n)}</b><br><span>{e(d)}</span></li>' for n, d in a["provare"])
    fonti = ''.join(f'<li><a href="{e(u)}" rel="noopener">{e(t)}</a></li>' for t, u in a["fonti"])
    altre = ''.join(f'<li><a href="../{b["slug"]}/"><b>{e(b["titolo"])}</b><span>{e(b["dek"])}</span><small>{b["lettura"]} min</small></a></li>' for b in sorted(ARTICOLI, key=lambda b: CATEGORIA_DI[b["slug"]] is not CATEGORIA_DI[a["slug"]]) if b is not a)
    return h + f'''<header class="testata-scura">{barra("../../")}</header>
<main id="contenuto" class="articolo"><div class="contenitore">
<p class="briciole"><a href="../../">Ceraldi Caffè</a> / <a href="../">Storie</a> / <a href="../{CATEGORIA_DI[a["slug"]]["slug"]}/">{e(CATEGORIA_DI[a["slug"]]["nome"])}</a></p>
<article>
<h1>{e(a["titolo"])}</h1>
<p class="dek">{e(a["dek"])}</p>
<p class="meta">{meta_articolo(a)}</p>
{fig}
<div class="corpo">{a["corpo"]}</div>
<aside class="cartellino"><h2>Da provare da Ceraldi</h2><p>Piazza Carità 14, Napoli. Tutti i giorni dalle 6:30 alle 20:30. Dolci di produzione propria.</p><ul>{prova}</ul>
<div class="azioni sinistra"><a class="btn" href="../../menu/">Guarda il menu</a><a class="btn" href="{BAR["mappa"]}" rel="noopener">Come arrivare</a></div></aside>
<aside class="fonti"><h2>Fonti</h2><ul>{fonti}</ul></aside>
</article>
<section class="altre"><h2>Altre storie</h2><ul class="storie">{altre}</ul></section>
</div></main>
''' + piede("../../")

def indice_storie():
    url = BASE + "storie/"
    h = testa("it", "Storie di Napoli: caffè, dolci e tradizioni | Ceraldi Caffè",
              "Caffè napoletano, caffè sospeso, sfogliatella, babà, pastiera, dolci di Natale, Piazza Carità e tradizioni di Napoli: le storie raccontate da Ceraldi Caffè.", url, "../",
              ld=[{"@context": "https://schema.org", "@type": "CollectionPage", "name": "Storie dal caffè", "url": url, "isPartOf": {"@id": BASE + "#sito"},
                   "hasPart": [{"@type": "Article", "headline": a["titolo"], "url": url + a["slug"] + "/"} for a in ARTICOLI]}])
    PER = {a["slug"]: a for a in ARTICOLI}
    chips = ''.join(f'<a href="{c["slug"]}/">{e(c["nome"])}</a>' for c in CATEGORIE)
    lista_s = f'<nav class="chips" aria-label="Categorie">{chips}</nav>' + ''.join(
        f'<section class="categoria"><h2><a href="{c["slug"]}/">{e(c["nome"])}</a></h2><ul class="storie">'
        + ''.join(f'<li><a href="{PER[s]["slug"]}/"><b>{e(PER[s]["titolo"])}</b><span>{e(PER[s]["dek"])}</span><small>{PER[s]["lettura"]} min di lettura</small></a></li>' for s in c["articoli"])
        + '</ul></section>' for c in CATEGORIE)
    return h + f'''<header class="testata-scura">{barra("../")}</header>
<main id="contenuto" class="articolo"><div class="contenitore">
<p class="briciole"><a href="../">Ceraldi Caffè</a></p>
<h1>Storie dal caffè</h1>
<p class="dek">Riti, leggende, dolci e luoghi della cultura napoletana, raccontati dal bancone di Piazza Carità.</p>
<div style="margin-top:28px">{lista_s}</div>
</div></main>
''' + piede("../")


def pagina_categoria(c):
    url = BASE + f"storie/{c['slug']}/"
    PER = {a["slug"]: a for a in ARTICOLI}
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": c["nome"], "description": c["intro"], "url": url, "isPartOf": {"@id": BASE + "#sito"},
           "hasPart": [{"@type": "Article", "headline": PER[s]["titolo"], "url": BASE + f"storie/{s}/"} for s in c["articoli"]]},
          ld_breadcrumb([("Storie", BASE + "storie/"), (c["nome"], url)])]
    h = testa("it", f"{c['nome']}: storie dal caffè | Ceraldi Caffè", c["intro"], url, "../../", ld=ld)
    voci = ''.join(f'<li><a href="../{s}/"><b>{e(PER[s]["titolo"])}</b><span>{e(PER[s]["dek"])}</span><small>{PER[s]["lettura"]} min di lettura</small></a></li>' for s in c["articoli"])
    altre = ''.join(f'<a href="../{x["slug"]}/">{e(x["nome"])}</a>' for x in CATEGORIE if x is not c)
    return h + f'''<header class="testata-scura">{barra("../../")}</header>
<main id="contenuto" class="articolo"><div class="contenitore">
<p class="briciole"><a href="../../">Ceraldi Caffè</a> / <a href="../">Storie</a></p>
<h1>{e(c["nome"])}</h1>
<p class="dek">{e(c["intro"])}</p>
<ul class="storie" style="margin-top:36px">{voci}</ul>
<nav class="chips" aria-label="Altre categorie" style="margin-top:40px">{altre}</nav>
</div></main>
''' + piede("../../")

# ── Menu completo (da menu_grezzo.json, scaricato da qromo con aggiorna_menu.py) ──
ALLERGENI = {1: "sedano", 2: "molluschi", 3: "solfiti", 4: "uova", 5: "pesce", 6: "glutine", 7: "lupini", 8: "latte",
             9: "senape", 10: "arachidi", 11: "sesamo", 12: "crostacei", 13: "soia", 14: "frutta a guscio", 15: "mandorle",
             16: "orzo", 17: "noci del Brasile", 18: "anacardi", 19: "nocciole", 20: "macadamia", 21: "avena", 22: "noci pecan",
             23: "pistacchi", 24: "segale", 25: "farro", 26: "noci", 27: "frumento", 28: "kamut"}
ETICHETTE = {29: "contiene alcol", 32: "vegano", 33: "vegetariano", 35: "senza glutine", 43: "prodotto surgelato", 44: "prodotto abbattuto"}
import re as _re

def _slug(t):
    t = t.lower().replace('&', ' ').replace("'", ' ')
    for a, b in (('à', 'a'), ('á', 'a'), ('è', 'e'), ('é', 'e'), ('ì', 'i'), ('ò', 'o'), ('ù', 'u')):
        t = t.replace(a, b)
    return _re.sub(r'[^a-z0-9]+', '-', t).strip('-')

def _pulisci(t):
    t = (t or '').replace('⏳', ' ').strip()
    t = _re.sub(r'\s*\d+/\d+\s*mi[nm]\b|\s*\d+\s*min\b', '', t)
    return _re.sub(r'\s+', ' ', t).strip()

def _prezzo(c):
    return ('€ ' + f"{c / 100:.2f}".replace('.', ',')) if c else ''

def dati_menu():
    d = json.load(open(os.path.join(QUI, 'menu_grezzo.json'), encoding='utf-8'))
    all_by = {}
    for a in d['menusItemsAllergens']:
        all_by.setdefault(a['menu_item_id'], []).append(a['allergen_id'])
    menus = [m for m in sorted(d['menus'], key=lambda m: m['order_number'] or 0)
             if m['available'] and not m['name'].upper().startswith('BANCO') and m['name'].strip() != 'Comunicazioni']
    out = []
    for m in menus:
        cats = []
        cc = [c for c in d['menusCategories'] if c['menu_id'] == m['menu_id'] and c['active'] in (1, None)]
        for c in sorted(cc, key=lambda c: c['order_number'] or 0):
            ii = [i for i in d['menusItems'] if i['category_id'] == c['menu_category_id'] and i['available']]
            voci = []
            for i in sorted(ii, key=lambda i: i['order_number'] or 0):
                ids = all_by.get(i['menu_item_id'], [])
                voci.append({"id": i['menu_item_id'], "nome": _pulisci(i['name']), "desc": _re.sub(r'\s+', ' ', (i['ingredients'] or '')).strip(),
                             "prezzo": i['price'] or 0,
                             "allergeni": [ALLERGENI[x] for x in ids if x in ALLERGENI],
                             "etichette": [ETICHETTE[x] for x in ids if x in ETICHETTE]})
            if voci:
                cats.append({"nome": _pulisci(c['name']), "voci": voci})
        if cats:
            out.append({"nome": _pulisci(m['name']), "id": _slug(_pulisci(m['name'])), "categorie": cats})
    return out

def ld_breadcrumb(voci):
    lst = [{"@type": "ListItem", "position": 1, "name": "Ceraldi Caffè", "item": BASE}]
    lst += [{"@type": "ListItem", "position": i + 2, "name": n, "item": u} for i, (n, u) in enumerate(voci)]
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": lst}

def _voce_ld(v):
    x = {"@type": "MenuItem", "name": v['nome']}
    if v['desc']:
        x["description"] = v['desc']
    if v['prezzo']:
        x["offers"] = {"@type": "Offer", "price": f"{v['prezzo'] / 100:.2f}", "priceCurrency": "EUR"}
    return x

def _voce_html(v):
    extra = []
    if v['allergeni']:
        extra.append('Allergeni: ' + ', '.join(v['allergeni']))
    if v['etichette']:
        extra.append(', '.join(v['etichette']).capitalize())
    ex = '<small>' + e('. '.join(extra)) + '</small>' if extra else ''
    de = '<span>' + e(v['desc']) + '</span>' if v['desc'] else ''
    ap = MENU_APPROFONDIMENTI.get(v.get('id'))
    lk = f'<a class="approfondisci" href="../{ap}">{"La sua storia" if ap.startswith("storie/") else "Scopri di più"}</a>' if ap else ''
    return '<li><div class="voce-testa"><b>' + e(v['nome']) + '</b><i>' + _prezzo(v['prezzo']) + '</i></div>' + de + ex + lk + '</li>'

def pagina_menu():
    url = BASE + "menu/"
    M = dati_menu()
    n_voci = sum(len(c['voci']) for m in M for c in m['categorie'])
    ld = {"@context": "https://schema.org", "@type": "Menu", "name": "Menu di Ceraldi Caffè", "url": url, "inLanguage": "it-IT",
          "hasMenuSection": [{"@type": "MenuSection", "name": m['nome'],
                              "hasMenuSection": [{"@type": "MenuSection", "name": c['nome'], "hasMenuItem": [_voce_ld(v) for v in c['voci']]}
                                                 for c in m['categorie']]} for m in M]}
    h = testa("it", "Menu e prezzi | Ceraldi Caffè, Napoli",
              f"Il menu completo di Ceraldi Caffè in Piazza Carità, Napoli: {n_voci} proposte tra caffè, colazione, dolci, rosticceria, freselle, spritz e cocktail, con prezzi e allergeni.",
              url, "../", ld=[ld, ld_breadcrumb([("Menu", url)])])
    chips = ''.join('<a href="#' + m['id'] + '">' + e(m['nome']) + '</a>' for m in M)
    sezioni = ''
    for m in M:
        sezioni += '<section class="menu-sezione" id="' + m['id'] + '"><h2>' + e(m['nome']) + '</h2>'
        for c in m['categorie']:
            sezioni += '<h3>' + e(c['nome']) + '</h3><ul class="menu-voci">' + ''.join(_voce_html(v) for v in c['voci']) + '</ul>'
        sezioni += '</section>'
    data = OGGI[8:10] + '/' + OGGI[5:7] + '/' + OGGI[:4]
    return h + f"""<header class="testata-scura">{barra("../")}</header>
<main id="contenuto" class="articolo pagina-menu"><div class="contenitore">
<p class="briciole"><a href="../">Ceraldi Caffè</a></p>
<h1>Il menu</h1>
<p class="dek">Caffetteria, colazione, pasticceria di produzione propria, rosticceria napoletana, freselle, spritz e cocktail. Prezzi aggiornati al {data}.</p>
<nav class="chips" aria-label="Sezioni del menu">{chips}</nav>
<p class="avviso">Le informazioni sugli allergeni vengono dal nostro menu digitale. In caso di allergie o intolleranze chiedi sempre al personale prima di ordinare. Puoi anche consultare il <a href="{BAR['menu']}" rel="noopener">menu interattivo</a>, con filtro allergeni e versione inglese.</p>
{sezioni}
</div></main>
""" + piede("../")

CTA_LINK = {"mappa": (BAR["mappa"], True), "menu_interno": ("../menu/", False), "menu_bar": ("../menu/#bar-dolci", False),
            "menu_dolci": ("../menu/#bar-dolci", False), "menu_food": ("../menu/#food", False),
            "menu_drink": ("../menu/#cocktails-birre-alcolici", False)}

def pagina(p):
    url = BASE + p["slug"] + "/"
    k = p["foto"]
    og = f"img/{k}-{FOTO[k]['w'][0]}.webp"
    ld = [ld_breadcrumb([(p["nav"], url)]),
          {"@context": "https://schema.org", "@type": "WebPage", "name": p["titolo"], "description": p["descrizione"], "url": url,
           "isPartOf": {"@id": BASE + "#sito"}, "about": {"@id": BASE + "#bar"}, "primaryImageOfPage": BASE + og, "inLanguage": "it-IT"}]
    h = testa("it", p["titolo_seo"] + " | Ceraldi Caffè", p["descrizione"], url, "../", og_img=og, ld=ld)
    gal = p.get("galleria") or []
    galleria = ''
    if gal:
        galleria = '<div class="galleria">' + ''.join('<figure>' + immagine(g, "../", "(max-width: 640px) 50vw, 360px") + '</figure>' for g in gal) + '</div>'
    cta = ''
    for i, (t, c) in enumerate(p.get("cta", [])):
        href, est = CTA_LINK[c]
        cta += '<a class="btn' + (' pieno' if i == 0 else '') + '" href="' + href + '"' + (' rel="noopener"' if est else '') + '>' + e(t) + '</a>'
    return h + f"""<header class="hero hero-pagina">{barra("../")}
<div class="contenitore hero-griglia">
<div class="hero-testo"><p class="dal"><a href="../">Ceraldi Caffè</a> / {e(p["nav"])}</p>
<h1>{e(p["titolo"])}</h1>
<p class="tag">{e(p["dek"])}</p>
<div class="azioni sinistra">{cta}</div></div>
<figure class="specchio">{immagine(k, "../", "(max-width: 900px) 92vw, 480px", eager=True)}</figure>
</div></header>
<main id="contenuto" class="articolo"><div class="contenitore">
<div class="corpo">{p["corpo"]}</div>
{galleria}
<aside class="cartellino"><h2>Vieni a trovarci</h2><p>Piazza Carità 14, Napoli, lungo via Toledo. Tutti i giorni dalle 6:30 alle 20:30.</p>
<div class="azioni sinistra"><a class="btn" href="{BAR["mappa"]}" rel="noopener">Come arrivare</a><a class="btn" href="tel:{BAR["tel_link"]}">Chiama {BAR["telefono"]}</a></div></aside>
</div></main>
""" + piede("../")

def pagina_contatti():
    url = BASE + "contatti/"
    h = testa("it", "Orari e contatti | Ceraldi Caffè, Piazza Carità 14",
              "Ceraldi Caffè, Piazza Carità 14, 80134 Napoli. Aperto tutti i giorni dalle 6:30 alle 20:30. Telefono 081 552 3488, cellulare 328 438 8404, WhatsApp. Come arrivare con la metro Linea 1.",
              url, "../", ld=[ld_bar('it'), ld_breadcrumb([("Contatti", url)])])
    return h + f"""<header class="testata-scura">{barra("../")}</header>
<main id="contenuto" class="articolo"><div class="contenitore">
<p class="briciole"><a href="../">Ceraldi Caffè</a></p>
<h1>Contatti e orari</h1>
<p class="dek">Siamo in Piazza Carità, nel centro di Napoli, lungo via Toledo. Aperti tutti i giorni, domenica compresa.</p>
<dl class="scheda contatti">
<div><dt>Indirizzo</dt><dd>Piazza Carità 14<br>80134 Napoli (NA)</dd></div>
<div><dt>Orari</dt><dd>Tutti i giorni<br>dalle 6:30 alle 20:30</dd></div>
<div><dt>Telefono</dt><dd><a href="tel:{BAR["tel_link"]}">081 552 3488</a><br>anche <a href="{BAR["whatsapp"]}" rel="noopener">WhatsApp</a></dd></div>
<div><dt>Cellulare</dt><dd><a href="tel:{BAR["cell_link"]}">328 438 8404</a></dd></div>
</dl>
<div class="azioni sinistra"><a class="btn scuro" href="{BAR["mappa"]}" rel="noopener">Apri in Google Maps</a><a class="btn scuro-vuoto" href="tel:{BAR["tel_link"]}">Chiama</a><a class="btn scuro-vuoto" href="{BAR["whatsapp"]}" rel="noopener">Scrivi su WhatsApp</a></div>
<div class="corpo">
<h2>Come arrivare</h2>
<ul>
<li><strong>In metropolitana</strong>: Linea 1, fermate <strong>Toledo</strong> o <strong>Dante</strong>, a pochi minuti a piedi.</li>
<li><strong>A piedi</strong>: siamo lungo via Toledo, tra piazza Dante e piazza del Plebiscito, all'ingresso della Pignasecca e dei Quartieri Spagnoli.</li>
<li><strong>In auto</strong>: il centro è in gran parte zona a traffico limitato; conviene lasciare l'auto in un parcheggio e proseguire a piedi o con la metro.</li>
</ul>
<h2>Recensioni</h2>
<p>Leggi cosa dicono di noi su <a href="{BAR["google_recensioni"]}" rel="noopener">Google</a> e su <a href="{BAR["tripadvisor"]}" rel="noopener">Tripadvisor</a>. Se sei stato da noi, <a href="{BAR["google_scrivi"]}" rel="noopener">lascia una recensione</a>: ci aiuta a migliorare.</p>
<h2>Social</h2>
<p>Seguici su <a href="{BAR["instagram"]}" rel="noopener">Instagram</a> e <a href="{BAR["facebook"]}" rel="noopener">Facebook</a>.</p>
<h2>Dati aziendali</h2>
<p>{RAGIONE_SOCIALE}<br>Piazza Carità 14, 80134 Napoli (NA)<br>P. IVA {PIVA}</p>
</div>
</div></main>
""" + piede("../")

def pagina_privacy():
    url = BASE + "privacy/"
    data = OGGI[8:10] + '/' + OGGI[5:7] + '/' + OGGI[:4]
    h = testa("it", "Privacy e cookie | Ceraldi Caffè", "Informativa sulla privacy e sui cookie del sito di Ceraldi Caffè, Piazza Carità 14, Napoli.", url, "../")
    return h + f"""<header class="testata-scura">{barra("../")}</header>
<main id="contenuto" class="articolo"><div class="contenitore">
<p class="briciole"><a href="../">Ceraldi Caffè</a></p>
<h1>Privacy e cookie</h1>
<p class="meta">Ultimo aggiornamento: {data}</p>
<div class="corpo">
<h2>Titolare</h2>
<p>{RAGIONE_SOCIALE}, Piazza Carità 14, 80134 Napoli (NA), P. IVA {PIVA}. Per qualsiasi richiesta sui dati personali puoi contattarci al numero <a href="tel:{BAR["tel_link"]}">081 552 3488</a> o presso la sede.</p>
<h2>Cosa raccoglie questo sito</h2>
<p>Questo sito è una vetrina informativa. <strong>Non usa cookie, non usa strumenti di statistica o di profilazione e non contiene moduli</strong> che raccolgono dati personali. Anche i caratteri tipografici sono ospitati sul sito stesso, senza chiamate a servizi esterni.</p>
<h2>Hosting</h2>
<p>Il sito è ospitato su GitHub Pages (GitHub, Inc.). Come ogni server web, il fornitore di hosting può registrare dati tecnici delle visite, come l'indirizzo IP, per motivi di sicurezza e di funzionamento del servizio, secondo la propria informativa.</p>
<h2>Link esterni</h2>
<p>Alcuni link portano a servizi di terzi: Google Maps e Google (recensioni), Tripadvisor, Instagram, Facebook, WhatsApp e il nostro menu interattivo su qromo. Quando li apri si applicano le informative privacy e cookie di quei servizi.</p>
<h2>I tuoi diritti</h2>
<p>In base al Regolamento UE 2016/679 (GDPR) puoi chiedere l'accesso, la rettifica o la cancellazione dei dati che ti riguardano e proporre reclamo al Garante per la protezione dei dati personali.</p>
</div>
</div></main>
""" + piede("../")


def sitemap():
    urls = [(BASE, "1.0"), (BASE + "menu/", "0.9")] + [(BASE + p["slug"] + "/", "0.9") for p in PAGINE] + [(BASE + "contatti/", "0.8"), (BASE + "en/", "0.8"), (BASE + "storie/", "0.7")] + [(BASE + f"storie/{c['slug']}/", "0.6") for c in CATEGORIE] + [(BASE + f"storie/{a['slug']}/", "0.6", a.get("aggiornato", a.get("pubblicato", PUBBLICATO))) for a in ARTICOLI]
    righe = ''.join(f'<url><loc>{x[0]}</loc><lastmod>{x[2] if len(x) > 2 else OGGI}</lastmod><priority>{x[1]}</priority></url>' for x in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{righe}</urlset>\n'

def llms():
    righe = '\n'.join(f'- [{a["titolo"]}]({BASE}storie/{a["slug"]}/): {a["descrizione"]}' for a in ARTICOLI)
    return f'''# Ceraldi Caffè

> Bar e pasticceria napoletana in Piazza Carità 14, Napoli (80134). Attività della famiglia Ceraldi dal 1973 (primi anni a Piazza Garibaldi), in Piazza Carità dal 2002. Motto: "Artigiani per passione dal 1973". Pasticceria di produzione propria con ricette di famiglia custodite da oltre cento anni.

## Informazioni essenziali
- Indirizzo: Piazza Carità 14, 80134 Napoli, Italia (lungo via Toledo, vicino alle stazioni metro Toledo e Dante, Linea 1)
- Orari: tutti i giorni, domenica compresa, 6:30 – 20:30
- Telefono: +39 081 552 3488 (anche WhatsApp); cellulare: +39 328 438 8404
- Menu completo con prezzi: {BASE}menu/ (menu interattivo con allergeni: {BAR["menu"]})
- Ragione sociale: {RAGIONE_SOCIALE}, P. IVA {PIVA}
- Recensioni: Google ({BAR["google_recensioni"]}), Tripadvisor ({BAR["tripadvisor"]}); valutazione 4,3/5 su Google con quasi 2.000 recensioni
- Instagram: {BAR["instagram"]}
- Mappa: {BAR["mappa"]}

## Cosa offre
- Colazione all'italiana: croissant (vuoti, crema, crema e amarena, cioccolato, albicocca, integrali, vegani), brioche, kranz, pain au chocolat, maritozzo, graffa napoletana
- Pasticceria napoletana di produzione propria: sfogliatella riccia e frolla, sfogliata Santa Rosa, babà al rum, pastiera napoletana, zeppola di San Giuseppe, codina di aragosta
- Dolci della casa: Cestino, Segreto amalfitano, Babàmisù, Pellecchiella (albicocche del Vesuvio, presidio Slow Food), torta di mele Annurca IGP
- Caffè della casa: Caffè Ceraldi, Caffè Babà, Michelino, Nocciolato, Pistacchiotto, Caldo freddo
- Rosticceria napoletana: frittatina, crocchè, pizza fritta, pizza di scarole, saltimbocca, zingara ischitana; freselle e insalate
- English breakfast tutte le mattine (uova, bacon, salsicce, fagioli, funghi, pomodori, pane tostato, tè)
- Aperitivo: Aspritz fatto in casa (bitter con agrumi della Costiera Amalfitana, erbe e radici, con spumante Asprinio di Aversa), spritz, negroni, gin tonic, vini campani, birre

## Pagine
- [Home]({BASE})
- [Menu completo con prezzi]({BASE}menu/)
- [La nostra storia]({BASE}storia/)
- [Il bar, la colazione e l'English breakfast]({BASE}bar/)
- [La pasticceria]({BASE}pasticceria/)
- [Rosticceria napoletana, freselle e insalate]({BASE}rosticceria/)
- [Aspritz e aperitivi]({BASE}aspritz/)
- [Contatti e orari]({BASE}contatti/)
- [English]({BASE}en/)
- [Storie dal caffè]({BASE}storie/)
{righe}
'''

# ── Pagina non trovata ────────────────────────────────────────────────
def pagina_404(rr):
    h = testa("it", "Pagina non trovata | Ceraldi Caffè Napoli", "La pagina cercata non esiste. Torna alla home di Ceraldi Caffè, Piazza Carità 14, Napoli.", BASE, rr)
    h = h.replace('<meta name="robots" content="index, follow, max-image-preview:large">', '<meta name="robots" content="noindex">')
    h = _re.sub(r'<link rel="canonical"[^>]*>', '', h)
    return h + f'''<header class="testata-scura">{barra(rr)}</header>
<main id="contenuto" class="articolo"><div class="contenitore">
<h1>Questa pagina non c'è</h1>
<p class="dek">L'indirizzo potrebbe essere cambiato o contenere un errore. Il bancone invece è sempre lì, in Piazza Carità 14, tutti i giorni dalle 6:30 alle 20:30.</p>
<div class="azioni sinistra"><a class="btn scuro" href="{rr}">Vai alla home</a><a class="btn scuro-vuoto" href="{rr}menu/">Guarda il menu</a><a class="btn scuro-vuoto" href="{rr}contatti/">Orari e contatti</a></div>
</div></main>
''' + piede(rr)

# Vecchi indirizzi di ceraldicaffe.it che cambiano nome: pagina di rimando (GitHub Pages non fa redirect 301)
RIMANDI = {"1973-2": "storia", "gastronomia": "rosticceria"}
def rimando(dest):
    u = BASE + dest + "/"
    return f'''<!DOCTYPE html>
<html lang="it"><head><meta charset="utf-8"><title>Ceraldi Caffè</title>
<meta name="robots" content="noindex"><link rel="canonical" href="{u}">
<meta http-equiv="refresh" content="0; url=../{dest}/"></head>
<body><p><a href="../{dest}/">Vai alla pagina</a></p></body></html>
'''

def robots():
    return f"User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n"

if __name__ == "__main__":
    scrivi("index.html", home_it())
    scrivi("en/index.html", home_en())
    scrivi("storie/index.html", indice_storie())
    for a in ARTICOLI:
        scrivi(f"storie/{a['slug']}/index.html", articolo(a))
    for c in CATEGORIE:
        scrivi(f"storie/{c['slug']}/index.html", pagina_categoria(c))
    for p in PAGINE:
        scrivi(f"{p['slug']}/index.html", pagina(p))
    scrivi("menu/index.html", pagina_menu())
    scrivi("contatti/index.html", pagina_contatti())
    scrivi("privacy/index.html", pagina_privacy())
    scrivi("sitemap.xml", sitemap())
    scrivi("llms.txt", llms())
    scrivi("404.html", pagina_404(BASE))
    # GitHub Pages usa solo il 404.html alla radice del repository: per gli indirizzi fuori da /caffe/ (le app) mostra un messaggio neutro
    neutro = ("<script>if(location.pathname.indexOf('/Ceraldi/caffe/')!==0){document.title='Pagina non trovata';"
              "document.body.innerHTML='<main style=\"font-family:system-ui,sans-serif;padding:48px 24px;text-align:center\"><h1>Pagina non trovata</h1><p>Controlla l\\'indirizzo.</p></main>';}</script>")
    scrivi("../404.html", pagina_404(BASE).replace("</body>", neutro + "</body>", 1))
    for vecchio, nuovo in RIMANDI.items():
        scrivi(f"{vecchio}/index.html", rimando(nuovo))
    scrivi("robots.txt", robots())
    print("Pagine generate:", 6 + len(ARTICOLI) + len(PAGINE) + len(CATEGORIE))
