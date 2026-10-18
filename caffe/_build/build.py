# -*- coding: utf-8 -*-
"""Genera le pagine del sito di Ceraldi Caffè.
Uso:  python3 caffe/_build/build.py   (dalla radice del repository)
La cartella _build non viene pubblicata da GitHub Pages (Jekyll ignora le cartelle con _)."""
import json, os, html
from contenuti import *

QUI = os.path.dirname(os.path.abspath(__file__))
SITO = os.path.dirname(QUI)
e = html.escape

FONT = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400..600;1,6..96,400&family=Work+Sans:wght@400;600&display=swap" rel="stylesheet">')
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
{pre}{FONT}
<link rel="stylesheet" href="{rr}assets/sito.css">
{lds}
</head>
<body>
<a class="salta" href="#contenuto">{'Vai al contenuto' if lang == 'it' else 'Skip to content'}</a>
'''

def barra(rr, lang='it'):
    logo = f'<img src="{rr}img/logo-ceraldi-chiaro.svg" width="150" height="52" alt="Ceraldi Caffè">'
    if lang == 'en':
        return f'''<div class="barra"><a class="marchio" href="{rr}en/">{logo}</a>
<nav aria-label="Main"><a href="#breakfast">Breakfast</a><a class="nasconde" href="#specialities">Specialities</a><a href="#find-us">Find us</a><a href="{rr}" hreflang="it" lang="it">Italiano</a></nav></div>'''
    return f'''<div class="barra"><a class="marchio" href="{rr}">{logo}</a>
<nav aria-label="Principale"><a class="nasconde" href="{rr}#colazione">Colazione</a><a href="{rr}#specialita">Specialità</a><a href="{rr}storie/">Storie</a><a class="nasconde" href="{rr}#dove">Dove siamo</a><a href="{rr}en/" hreflang="en" lang="en">EN</a></nav></div>'''

def piede(rr, lang='it'):
    it = lang == 'it'
    return f'''<footer class="piede"><div class="contenitore">
<div><img src="{rr}img/logo-ceraldi-chiaro.svg" width="180" height="62" alt="Ceraldi Caffè, artigiani per passione dal 1973" loading="lazy">
<p style="margin-top:12px">{e(BAR['indirizzo'])}, {e(BAR['cap_citta'])}</p><p>{e(BAR['orari'] if it else BAR['orari_en'])}</p></div>
<div><p><a href="tel:{BAR['tel_link']}">{'Tel.' if it else 'Phone'} {BAR['telefono']}</a></p><p><a href="tel:{BAR['cell_link']}">{'Cell.' if it else 'Mobile'} {BAR['cellulare']}</a></p>
<p><a href="{BAR['whatsapp']}" rel="noopener">WhatsApp</a></p></div>
<div><p><a href="{BAR['menu']}" rel="noopener">{'Menu online' if it else 'Online menu'}</a></p><p><a href="{BAR['google_recensioni']}" rel="noopener">{'Recensioni Google' if it else 'Google reviews'}</a></p><p><a href="{BAR['tripadvisor']}" rel="noopener">Tripadvisor</a></p></div>
<div><p><a href="{BAR['instagram']}" rel="noopener">Instagram</a></p><p><a href="{BAR['facebook']}" rel="noopener">Facebook</a></p><p><a href="{rr}storie/">{'Storie dal caffè' if it else 'Stories (Italian)'}</a></p></div>
<p class="legale">© Ceraldi Group S.r.l. <a href="{rr}../privacy.html">Privacy</a></p>
</div></footer>
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
        "hasMap": BAR["mappa"], "hasMenu": BAR["menu"],
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

def home_it():
    alt = [("it", BASE), ("en", BASE + "en/"), ("x-default", BASE)]
    h = testa("it", "Ceraldi Caffè | Bar e pasticceria artigianale a Napoli dal 1973, Piazza Carità",
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
<div class="azioni sinistra"><a class="btn pieno" href="{BAR["mappa"]}" rel="noopener">Come arrivare</a><a class="btn" href="{BAR["menu"]}" rel="noopener">Guarda il menu</a><a class="btn" href="tel:{BAR["tel_link"]}">Chiama</a></div>
<p class="aperto">Aperto tutti i giorni dalle 6:30 alle 20:30<br><a href="#recensioni">Valutazione 4,3 su Google</a></p>
</div>
<figure class="specchio">{immagine("sala", "", "(max-width: 900px) 92vw, 480px", eager=True)}</figure>
</div>
</header>
<main id="contenuto">

<section class="sezione"><div class="contenitore storia">
<div><h2>Artigiani per passione, dal 1973</h2>
<p>La storia della famiglia Ceraldi nei bar di Napoli comincia nei primi anni Settanta in Piazza Garibaldi. Nel 2002 l'arrivo in Piazza Carità, lungo via Toledo, a due passi dalla Pignasecca e dai Quartieri Spagnoli: da allora è il nostro bar. Si entra la mattina presto per il primo caffè e una sfogliatella calda, si torna a metà giornata per un dolce dalla vetrina, ci si ferma la sera per l'aperitivo.</p>
<p>La nostra pasticceria è di <strong>produzione propria</strong>: sfogliatelle, babà, pastiere e torte nascono da ricette di famiglia custodite da oltre cento anni, insieme alle creazioni della casa. Il locale è quello di un bar napoletano elegante, con specchi, poltroncine in pelle rossa e un bancone sempre affollato.</p>
<p><a class="link-forte" href="storie/pasticceria-artigianale/">Scopri la nostra pasticceria</a></p></div>
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
<div><dt>Menu</dt><dd><a href="{BAR["menu"]}" rel="noopener">ceraldicaffe.qromo.it</a></dd></div>
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
<p class="nota">Il menu completo, con prezzi e allergeni: <a href="{BAR["menu"]}" rel="noopener">guarda il menu online</a>.</p>
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
<div class="azioni sinistra"><a class="btn scuro" href="{BAR["menu"]}" rel="noopener">Cocktail e drink nel menu</a></div></div>
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
    h = testa("en", "Ceraldi Caffè | Neapolitan café and pastry shop since 1973, Piazza Carità, Naples",
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
<div class="azioni sinistra"><a class="btn pieno" href="{BAR["mappa"]}" rel="noopener">Get directions</a><a class="btn" href="{BAR["menu"]}" rel="noopener">See the menu</a><a class="btn" href="tel:{BAR["tel_link"]}">Call</a></div>
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
<p class="nota">The full menu, with prices, allergens and an English version: <a href="{BAR["menu"]}" rel="noopener">see the online menu</a>.</p>
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
def articolo(a):
    url = BASE + f"storie/{a['slug']}/"
    k = a['foto']
    img = BASE + (f"img/{k}-{FOTO[k]['w'][0]}.webp" if k else "img/og.jpg")
    ld = [{"@context": "https://schema.org", "@type": "Article", "headline": a["titolo"], "description": a["descrizione"],
           "image": [img], "datePublished": OGGI, "dateModified": OGGI, "inLanguage": "it-IT", "mainEntityOfPage": url,
           "isPartOf": {"@id": BASE + "#sito"},
           "author": {"@type": "Organization", "name": "Ceraldi Caffè", "url": BASE},
           "publisher": {"@type": "Organization", "name": "Ceraldi Caffè", "logo": {"@type": "ImageObject", "url": BASE + "img/apple-touch-icon.png"}}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Ceraldi Caffè", "item": BASE},
              {"@type": "ListItem", "position": 2, "name": "Storie", "item": BASE + "storie/"},
              {"@type": "ListItem", "position": 3, "name": a["titolo"], "item": url}]}]
    og = f"img/{k}-{FOTO[k]['w'][0]}.webp" if k else "img/og.jpg"
    h = testa("it", a["titolo_seo"] + " | Ceraldi Caffè Napoli", a["descrizione"], url, "../../", og_img=og, ld=ld, tipo="article")
    fig = f'<figure class="{"verticale" if FOTO[k]["r"][1] > FOTO[k]["r"][0] else ""}">{immagine(k, "../../", "(max-width: 800px) 100vw, 760px", eager=True)}</figure>' if k else ''
    prova = ''.join(f'<li><b>{e(n)}</b><br><span>{e(d)}</span></li>' for n, d in a["provare"])
    altre = ''.join(f'<li><a href="../{b["slug"]}/"><b>{e(b["titolo"])}</b><span>{e(b["dek"])}</span><small>{b["lettura"]} min</small></a></li>' for b in ARTICOLI if b is not a)
    return h + f'''<header class="testata-scura">{barra("../../")}</header>
<main id="contenuto" class="articolo"><div class="contenitore">
<p class="briciole"><a href="../../">Ceraldi Caffè</a> / <a href="../">Storie</a></p>
<article>
<h1>{e(a["titolo"])}</h1>
<p class="dek">{e(a["dek"])}</p>
<p class="meta">{a["lettura"]} minuti di lettura</p>
{fig}
<div class="corpo">{a["corpo"]}</div>
<aside class="cartellino"><h2>Da provare da Ceraldi</h2><p>Piazza Carità 14, Napoli. Tutti i giorni dalle 6:30 alle 20:30. Dolci di produzione propria.</p><ul>{prova}</ul>
<div class="azioni sinistra"><a class="btn" href="{BAR["menu"]}" rel="noopener">Guarda il menu</a><a class="btn" href="{BAR["mappa"]}" rel="noopener">Come arrivare</a></div></aside>
</article>
<section class="altre"><h2>Altre storie</h2><ul class="storie">{altre}</ul></section>
</div></main>
''' + piede("../../")

def indice_storie():
    url = BASE + "storie/"
    h = testa("it", "Storie dal caffè: tradizioni, dolci e cultura napoletana | Ceraldi Caffè Napoli",
              "Caffè napoletano, caffè sospeso, sfogliatella, babà, pastiera, dolci di Natale, Piazza Carità e tradizioni di Napoli: le storie raccontate da Ceraldi Caffè.", url, "../",
              ld=[{"@context": "https://schema.org", "@type": "CollectionPage", "name": "Storie dal caffè", "url": url, "isPartOf": {"@id": BASE + "#sito"},
                   "hasPart": [{"@type": "Article", "headline": a["titolo"], "url": url + a["slug"] + "/"} for a in ARTICOLI]}])
    lista_s = ''.join(f'<li><a href="{a["slug"]}/"><b>{e(a["titolo"])}</b><span>{e(a["dek"])}</span><small>{a["lettura"]} min di lettura</small></a></li>' for a in ARTICOLI)
    return h + f'''<header class="testata-scura">{barra("../")}</header>
<main id="contenuto" class="articolo"><div class="contenitore">
<p class="briciole"><a href="../">Ceraldi Caffè</a></p>
<h1>Storie dal caffè</h1>
<p class="dek">Riti, leggende, dolci e luoghi della cultura napoletana, raccontati dal bancone di Piazza Carità.</p>
<ul class="storie" style="margin-top:36px">{lista_s}</ul>
</div></main>
''' + piede("../")

def sitemap():
    urls = [(BASE, "1.0"), (BASE + "en/", "0.8"), (BASE + "storie/", "0.7")] + [(BASE + f"storie/{a['slug']}/", "0.6") for a in ARTICOLI]
    righe = ''.join(f'<url><loc>{u}</loc><lastmod>{OGGI}</lastmod><priority>{p}</priority></url>' for u, p in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{righe}</urlset>\n'

def llms():
    righe = '\n'.join(f'- [{a["titolo"]}]({BASE}storie/{a["slug"]}/): {a["descrizione"]}' for a in ARTICOLI)
    return f'''# Ceraldi Caffè

> Bar e pasticceria napoletana in Piazza Carità 14, Napoli (80134). Attività della famiglia Ceraldi dal 1973 (primi anni a Piazza Garibaldi), in Piazza Carità dal 2002. Motto: "Artigiani per passione dal 1973". Pasticceria di produzione propria con ricette di famiglia custodite da oltre cento anni.

## Informazioni essenziali
- Indirizzo: Piazza Carità 14, 80134 Napoli, Italia (lungo via Toledo, vicino alle stazioni metro Toledo e Dante, Linea 1)
- Orari: tutti i giorni, domenica compresa, 6:30 – 20:30
- Telefono: +39 081 552 3488 (anche WhatsApp); cellulare: +39 328 438 8404
- Menu online con prezzi e allergeni: {BAR["menu"]}
- Recensioni: Google ({BAR["google_recensioni"]}), Tripadvisor ({BAR["tripadvisor"]}); valutazione 4,3/5 su Google con quasi 2.000 recensioni
- Instagram: {BAR["instagram"]}
- Mappa: {BAR["mappa"]}

## Cosa offre
- Colazione all'italiana: croissant (vuoti, crema, crema e amarena, cioccolato, albicocca, integrali, vegani), brioche, kranz, pain au chocolat, maritozzo, graffa napoletana
- Pasticceria napoletana di produzione propria: sfogliatella riccia e frolla, sfogliata Santa Rosa, babà al rum, pastiera napoletana, zeppola di San Giuseppe, codina di aragosta
- Dolci della casa: Cestino, Segreto amalfitano, Babàmisù, Pellecchiella (albicocche del Vesuvio, presidio Slow Food), torta di mele Annurca IGP
- Caffè della casa: Caffè Ceraldi, Caffè Babà, Michelino, Nocciolato, Pistacchiotto, Caldo freddo
- Aperitivo: spritz, cocktail, birre, buffet freddi

## Pagine
- [Home]({BASE})
- [English]({BASE}en/)
- [Storie dal caffè]({BASE}storie/)
{righe}
'''

if __name__ == "__main__":
    scrivi("index.html", home_it())
    scrivi("en/index.html", home_en())
    scrivi("storie/index.html", indice_storie())
    for a in ARTICOLI:
        scrivi(f"storie/{a['slug']}/index.html", articolo(a))
    scrivi("sitemap.xml", sitemap())
    scrivi("llms.txt", llms())
    print("Pagine generate:", 3 + len(ARTICOLI))
