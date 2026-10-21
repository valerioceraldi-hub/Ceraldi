# -*- coding: utf-8 -*-
"""Genera le pagine del sito di Ceraldi Caffè.
Uso:  python3 caffe/_build/build.py   (dalla radice del repository)
La cartella _build non viene pubblicata da GitHub Pages (Jekyll ignora le cartelle con _)."""
import json, os, html, hashlib, datetime, urllib.parse
from contenuti import *
from pagine import *
from pagine_en import *

QUI = os.path.dirname(os.path.abspath(__file__))
SITO = os.path.dirname(QUI)
e = html.escape

# Font ospitati sul sito (nessuna chiamata a server esterni: niente dati dei visitatori a terzi)
def font(rr):
    return (f'<link rel="preload" href="{rr}assets/font/BodoniModa-normal-400_600-latin.woff2" as="font" type="font/woff2" crossorigin>'
            f'<link rel="preload" href="{rr}assets/font/Jost-normal-400-latin.woff2" as="font" type="font/woff2" crossorigin>'
            f'<link rel="preload" href="{rr}assets/font/Jost-normal-500-latin.woff2" as="font" type="font/woff2" crossorigin>'
            f'<link rel="stylesheet" href="{rr}assets/font.css">')
FOTO.update({
    "aspritz": {"alt": "Aspritz di Ceraldi Caffè al bancone, con fetta d'arancia", "w": [1024, 640], "r": (4, 3)},
    "caffe-ceraldi": {"alt": "Il Caffè Ceraldi con cioccolata, crema di caffè e panna sul bancone in marmo", "w": [1024, 640], "r": (3, 2)},
    "saltimbocca": {"alt": "Saltimbocca con porchetta e provola di Ceraldi Caffè", "w": [768, 480], "r": (3, 4)},
    "frittatina": {"alt": "Frittatina napoletana di bucatini aperta a metà", "w": [800, 480], "r": (4, 5)},
})
GIORNI = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Pagine indicizzabili scritte in questo build: alimentano la sitemap in automatico
PAGINE_SITEMAP = []

def scrivi(rel, testo):
    p = os.path.join(SITO, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(testo)
    indicizzabile = (rel.endswith("index.html") and not rel.startswith("..") and 'name="robots" content="noindex' not in testo
                     and 'http-equiv="refresh"' not in testo)
    if indicizzabile:
        PAGINE_SITEMAP.append((BASE + rel[:-len("index.html")], hashlib.sha256(testo.encode()).hexdigest()))

# ── Pezzi comuni ──────────────────────────────────────────────────────
def testa(lang, titolo, descr, url, rr, og_img="img/og.jpg", ld=None, alternates=None, tipo="website", preload=None):
    alt = ''.join(f'<link rel="alternate" hreflang="{h}" href="{u}">' for h, u in (alternates or []))
    lds = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (ld or []))
    # preload: un indirizzo, oppure (indirizzo, srcset, sizes) per far scaricare al telefono la versione piccola
    if isinstance(preload, tuple):
        pre = f'<link rel="preload" as="image" href="{preload[0]}" imagesrcset="{preload[1]}" imagesizes="{preload[2]}" fetchpriority="high">'
    else:
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
{f'<script src="{rr}assets/consenso.js" data-ga="{GA_ID}" defer></script>' if GA_ID else ''}
{lds}
</head>
<body>
<a class="salta" href="#contenuto">{'Vai al contenuto' if lang == 'it' else 'Skip to content'}</a>
'''

# Navigazione principale: sei voci. Specialità, rosticceria e Aspritz restano pagine autonome,
# raggiungibili dalle pagine madri (blocco «Da vedere anche»), dalla home e dal piè di pagina.
VOCI_NAV = [("bar/", "Il bar"), ("pasticceria/", "Pasticceria"), ("menu/", "Menu"), ("storia/", "Storia"), ("storie/", "Storie"), ("contatti/", "Contatti")]
# Pagine che esistono in entrambe le lingue: percorso italiano -> percorso inglese
EN_PATH = {"": "en/", "storia/": "en/storia/", "bar/": "en/bar/", "pasticceria/": "en/pasticceria/", "rosticceria/": "en/rosticceria/",
           "aspritz/": "en/aspritz/", "specialita/": "en/specialita/", "menu/": "en/menu/", "contatti/": "en/contatti/", "privacy/": "en/privacy/"}
VOCI_NAV_EN = [("en/bar/", "Coffee & breakfast"), ("en/pasticceria/", "Pastries"), ("en/menu/", "Menu"), ("en/storia/", "Our story"), ("en/contatti/", "Contact")]

def alt_coppia(it_path):
    return [("it", BASE + it_path), ("en", BASE + EN_PATH[it_path]), ("x-default", BASE + it_path)]

def barra(rr, lang='it', it_path=None):
    """Barra di navigazione uguale su tutte le pagine: marchio, sei voci, lingua; su telefono un pulsante a icona
    (così non si confonde con «Il menu» della barra fissa in basso)."""
    logo = f'<img src="{rr}img/logo-ceraldi-chiaro.svg" width="150" height="52" alt="Ceraldi Caffè">'
    attuale = (EN_PATH.get(it_path, "") if lang == 'en' else it_path) or ""
    if lang == 'en':
        voci = VOCI_NAV_EN
        lingua = (f'{rr}{it_path or ""}', "IT", "Italiano", "it")
        home = f"{rr}en/"
    else:
        voci = VOCI_NAV
        lingua = (f'{rr}{EN_PATH.get(it_path, "en/") if it_path is not None else "en/"}', "EN", "English", "en")
        home = rr or "./"
    def link(h, t):
        cur = ' aria-current="page"' if attuale and (h == attuale or (h == "storie/" and attuale.startswith("storie/"))) else ''
        return f'<a href="{rr}{h}"{cur}>{t}</a>'
    links = ''.join(link(h, t) for h, t in voci)
    nav_l = 'Main' if lang == 'en' else 'Principale'
    apri = 'Open the site sections' if lang == 'en' else 'Apri le sezioni del sito'
    return f'''<div class="p-barra"><a class="p-marchio" href="{home}">{logo}</a>
<nav class="p-nav" aria-label="{nav_l}">{links}<a class="p-lingua" href="{lingua[0]}" hreflang="{lingua[3]}" lang="{lingua[3]}" title="{lingua[2]}">{lingua[1]}</a></nav>
<details class="p-nav-mobile"><summary aria-label="{apri}"><span class="p-burger" aria-hidden="true"></span></summary><nav aria-label="{nav_l}">{links}<a href="{lingua[0]}" hreflang="{lingua[3]}" lang="{lingua[3]}">{lingua[2]}</a></nav></details></div>'''

def piede(rr, lang='it'):
    it = lang == 'it'
    L = '' if it else 'en/'
    col_pagine = (f'<p><a href="{rr}{L}bar/">{"Il bar e la colazione" if it else "Coffee and breakfast"}</a></p>'
                  f'<p><a href="{rr}{L}pasticceria/">{"La pasticceria" if it else "Pastries"}</a></p>'
                  f'<p><a href="{rr}{L}specialita/">{"Specialità della casa" if it else "House specialities"}</a></p>'
                  f'<p><a href="{rr}{L}rosticceria/">{"Rosticceria" if it else "Street food"}</a></p>'
                  f'<p><a href="{rr}{L}aspritz/">{"Aspritz e aperitivi" if it else "Aspritz and aperitivo"}</a></p>'
                  f'<p><a href="{rr}{L}menu/">{"Il menu" if it else "Menu"}</a></p>')
    return f'''<footer class="piede"><div class="contenitore">
<div><img src="{rr}img/logo-ceraldi-chiaro.svg" width="180" height="62" alt="Ceraldi Caffè, artigiani per passione dal 1973" loading="lazy">
<p style="margin-top:14px">{e(BAR['indirizzo'])}, {e(BAR['cap_citta'])}</p><p>{e(BAR['orari'] if it else BAR['orari_en'])}</p>
<p><a href="tel:{BAR['tel_link']}">{'Tel.' if it else 'Phone'} {BAR['telefono'] if it else '+39 081 552 3488'}</a></p><p><a href="{BAR['whatsapp']}" rel="noopener">WhatsApp {BAR['cellulare'] if it else '+39 328 438 8404'}</a></p></div>
<div>{col_pagine}</div>
<div><p><a href="{rr}{L}storia/">{'La nostra storia' if it else 'Our story'}</a></p><p><a href="{rr}storie/"{'' if it else ' hreflang="it"'}>{'Storie dal caffè' if it else 'Stories (in Italian)'}</a></p><p><a href="{rr}{L}contatti/">{'Orari e contatti' if it else 'Hours and contact'}</a></p></div>
<div><p><a href="{BAR['google_recensioni']}" rel="noopener">{'Recensioni Google' if it else 'Google reviews'}</a></p><p><a href="{BAR['tripadvisor']}" rel="noopener">Tripadvisor</a></p><p><a href="{BAR['instagram']}" rel="noopener">Instagram</a></p><p><a href="{BAR['facebook']}" rel="noopener">Facebook</a></p></div>
<p class="legale">© {RAGIONE_SOCIALE}, Piazza Carità 14, 80134 Napoli. {'P. IVA' if it else 'VAT no.'} {PIVA}. <a href="{rr}{L}privacy/">{'Privacy e cookie' if it else 'Privacy and cookies'}</a>{f' <a href="#" data-preferenze-cookie>{"Preferenze cookie" if it else "Cookie preferences"}</a>' if GA_ID else ''}</p>
</div></footer>
<nav class="barra-fissa" aria-label="{'Contatti rapidi' if it else 'Quick contacts'}"><a href="tel:{BAR['tel_link']}">{'Chiama' if it else 'Call'}</a><a href="{BAR['mappa']}" rel="noopener">{'Indicazioni' if it else 'Directions'}</a><a href="{rr}{L}menu/">{'Il menu' if it else 'Menu'}</a></nav>
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
        "image": [BASE + "img/sfogliatella-riccia-1024.webp", BASE + "img/baba-1024.webp", BASE + "img/squadra-1600.webp", BASE + "img/sala-1024.webp"],
        "description": ("Bar e pasticceria napoletana della famiglia Ceraldi, attiva dal 1973 (prima in Piazza Garibaldi, dal 2002 in Piazza Carità, Napoli). Pasticceria di produzione propria con ricette di famiglia tramandate di generazione in generazione: sfogliatelle, babà, pastiera, zeppole. Colazione all'italiana con croissant e brioche, caffè della casa, aperitivo con l'Aspritz fatto in casa."
                        if lang == 'it' else "Neapolitan café and pastry shop run by the Ceraldi family since 1973 (first in Piazza Garibaldi, in Piazza Carità, Naples, since 2002). In-house pastries from family recipes handed down through the generations: sfogliatella, babà, pastiera, zeppole. Italian breakfast with croissants and brioche, house coffees, aperitivo with our homemade Aspritz."),
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
        "sameAs": [BAR["instagram"], BAR["facebook"], BAR["tripadvisor"], BAR["mappa"], BAR["gambero_rosso"]],
        "award": "Guida Bar d'Italia del Gambero Rosso" if lang == 'it' else "Gambero Rosso Bar d'Italia guide",
    }

def ld_sito():
    return {"@context": "https://schema.org", "@type": "WebSite", "@id": BASE + "#sito", "name": "Ceraldi Caffè", "url": BASE,
            "inLanguage": ["it-IT", "en"], "publisher": {"@id": BASE + "#bar"}}

def ld_faq(faq):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a, h in faq]}

# ── Home (italiano e inglese da un'unica funzione) ───────────────────
# Otto sezioni: sala, informazioni pratiche, tre firme, la giornata, la storia, riconoscimenti, storie, visita.
# Ogni foto compare una sola volta nella pagina (controllato da controlla.py).
HOME_FOTO_HERO = "sala-ingresso-piazza-carita"
HOME_FIRME = [  # foto, nome, descrizione IT, descrizione EN, link IT, link EN, etichetta IT, etichetta EN
    ("sfogliatella-riccia", "Sfogliatella riccia", "Sfogliatella riccia",
     "Ricotta, semola, canditi e cannella dentro mille sfoglie croccanti. Riccia, frolla o Santa Rosa.",
     "Ricotta, semolina, candied peel and cinnamon inside a thousand crisp layers. Riccia, frolla or Santa Rosa.",
     "storie/sfogliatella/", "storie/sfogliatella/", "La sua storia", "Its story (in Italian)"),
    ("baba-al-rum-classico", "Babà al rum", "Rum babà",
     "Soffice e bagnato al punto giusto: classico, con crema e amarena oppure con panna e fragole.",
     "Soft and soaked just right: classic, with custard and black cherry, or with cream and strawberries.",
     "storie/baba/", "storie/baba/", "La sua storia", "Its story (in Italian)"),
    ("caffe-ceraldi", "Caffè Ceraldi", "Caffè Ceraldi",
     "La nostra firma al bancone: cioccolata calda sul fondo, crema di caffè e panna montata fresca.",
     "Our signature at the counter: hot chocolate at the bottom, coffee cream and fresh whipped cream.",
     "specialita/", "en/specialita/", "I caffè della casa", "House coffees"),
]
HOME_GIORNATA = [  # foto, momento IT/EN, titolo IT/EN, testo IT/EN, link IT/EN, etichetta IT/EN
    ("cornetti-caffe-bancone", "Mattina", "Morning", "Colazione al bancone", "Breakfast at the counter",
     "Cornetto e cappuccino, sfogliatella o graffa appena fatta. E per chi viene da lontano, la Full English Breakfast tutte le mattine.",
     "Croissant and cappuccino, a sfogliatella or a fresh graffa. And for guests from abroad, a Full English Breakfast every morning.",
     "bar/", "en/bar/", "Il bar e la colazione", "Coffee and breakfast"),
    ("latte-macchiato-dolci", "Pomeriggio", "Afternoon", "Una pausa in sala", "A break in the hall",
     "Un caffè della casa e un dolce della vetrina, seduti tra gli specchi e le poltroncine rosse.",
     "A house coffee and a pastry from the display case, among the mirrors and red leather armchairs.",
     "pasticceria/", "en/pasticceria/", "La pasticceria", "Our pastries"),
    ("cocktail-barman", "Sera", "Evening", "L'aperitivo", "Aperitivo",
     "L'Aspritz fatto in casa con agrumi della Costiera e Asprinio di Aversa, spritz e cocktail preparati al banco.",
     "Our homemade Aspritz with Amalfi Coast citrus and Asprinio di Aversa, spritz and cocktails made at the bar.",
     "aspritz/", "en/aspritz/", "L'Aspritz", "The Aspritz"),
]
HOME_STORIE = [("caffe-sospeso", "squadra"), ("pastiera", "pastiera"), ("piazza-carita-via-toledo", "sala-bianca")]
HOME_TESTI = {
    "it": dict(
        titolo="Ceraldi Caffè | Bar e pasticceria a Napoli, Piazza Carità",
        descr="Bar e pasticceria di produzione propria in Piazza Carità 14, Napoli, dal 1973: sfogliatelle, babà, colazione e aperitivo. Tutti i giorni 6:30–20:30.",
        alt_hero="La sala di Ceraldi Caffè in Piazza Carità: specchi, soffitto Liberty e poltroncine in pelle rossa",
        occhiello="Bar e pasticceria · Piazza Carità 14, Napoli", h1="Artigiani per passione, dal&nbsp;1973",
        lead="Caffè napoletano, sfogliatelle e babà di produzione propria. Dalla prima tazzina delle 6:30 all'aperitivo della sera, lungo via Toledo.",
        btn_menu="Guarda il menu", btn_mappa="Come arrivare",
        info=[("Orari", "Tutti i giorni, 6:30 – 20:30"), ("Indirizzo", "Piazza Carità 14 · metro Toledo e Dante"), ("Telefono", None), ("Gambero Rosso", None)],
        firme_occ="Produzione propria", firme_h2="Tre firme della casa",
        firme_p="Nascono nei nostri laboratori, ogni giorno, con ricette di famiglia tramandate nel tempo.",
        firme_piu=[("specialita/", "Tutte le specialità della casa"), ("menu/", "Il menu completo"), ("rosticceria/", "Rosticceria e pranzo veloce")],
        giorno_occ="Dalle 6:30 alle 20:30", giorno_h2="Una giornata da Ceraldi",
        storia_occ="La nostra storia", storia_h2="Tre date, una famiglia",
        tappe=[("1973", "Piazza Garibaldi", "Michele Ceraldi apre il suo primo bar davanti alla stazione, tra chi parte e chi arriva."),
               ("2002", "Piazza Carità", "L'arrivo al numero 14, lungo via Toledo: un angolo vuoto che sembrava aspettarci."),
               ("Oggi", "Padre e figli", "Michele porta avanti il bar con Vincenzo e Valerio, dal laboratorio al bancone.")],
        storia_btn="Leggi la storia", storia_cap="Michele Ceraldi, il fondatore, con la famiglia nella sala di Piazza Carità.",
        voci_occ="Riconoscimenti e recensioni", voci_h2="Cosa dicono di noi",
        gambero="Nella guida <strong>Bar d'Italia</strong> dal {dal}, presenti anche nell'edizione 2026.", gambero_link="Leggi la scheda",
        google="Valutazione media su Google, su {n} recensioni. Dato rilevato il {data}.", su5="su 5",
        link_rec=("Recensioni su Google", "Tripadvisor", "Lascia una recensione"),
        storie_occ="Storie dal caffè", storie_h2="Napoli raccontata dal bancone", storie_tutte="Tutte le storie",
        visita_occ="Vieni a trovarci", visita_h2="Piazza Carità 14, nel cuore di Napoli",
        visita_p="Lungo via Toledo, tra piazza Dante e piazza del Plebiscito, all'ingresso della Pignasecca e dei Quartieri Spagnoli. A pochi minuti a piedi dalle fermate Toledo e Dante della metro Linea 1.",
        btn_maps="Apri in Google Maps", btn_chiama="Chiama",
        scheda=[("Orari", "Tutti i giorni, domenica compresa<br>dalle 6:30 alle 20:30"), ("Indirizzo", None), ("Telefono", None), ("Cellulare e WhatsApp", None)]),
    "en": dict(
        titolo="Ceraldi Caffè | Café and pastry shop in Naples, Piazza Carità",
        descr="Café and in-house pastry shop in Piazza Carità 14, Naples, since 1973: sfogliatella, babà, breakfast and aperitivo. Open daily 6:30 am – 8:30 pm.",
        alt_hero="The hall of Ceraldi Caffè in Piazza Carità: mirrors, Liberty-style ceiling and red leather armchairs",
        occhiello="Café and pastry shop · Piazza Carità 14, Naples", h1="Craftspeople by passion, since&nbsp;1973",
        lead="Neapolitan coffee, sfogliatelle and babà made in-house. From the first espresso at 6:30 am to the evening aperitivo, on Via Toledo.",
        btn_menu="See the menu", btn_mappa="Get directions",
        info=[("Opening hours", "Every day, 6:30 am – 8:30 pm"), ("Address", "Piazza Carità 14 · Toledo and Dante metro"), ("Phone", None), ("Gambero Rosso", None)],
        firme_occ="Made in-house", firme_h2="Three house signatures",
        firme_p="Made every day in our own kitchens, from family recipes handed down over time.",
        firme_piu=[("en/specialita/", "All our house specialities"), ("en/menu/", "The full menu"), ("en/rosticceria/", "Street food and quick lunch")],
        giorno_occ="From 6:30 am to 8:30 pm", giorno_h2="A day at Ceraldi",
        storia_occ="Our story", storia_h2="Three dates, one family",
        tappe=[("1973", "Piazza Garibaldi", "Michele Ceraldi opens his first café in front of the railway station, among travellers coming and going."),
               ("2002", "Piazza Carità", "We move to number 14, on Via Toledo: an empty corner that seemed to be waiting for us."),
               ("Today", "Father and sons", "Michele runs the café with Vincenzo and Valerio, from the pastry kitchen to the counter.")],
        storia_btn="Read our story", storia_cap="Michele Ceraldi, the founder, with his family in the hall in Piazza Carità.",
        voci_occ="Recognition and reviews", voci_h2="What people say",
        gambero="Listed in the <strong>Bar d'Italia</strong> guide since {dal}, including the 2026 edition.", gambero_link="Read the listing",
        google="Average Google rating from {n} reviews, as of {data}.", su5="out of 5",
        link_rec=("Reviews on Google", "Tripadvisor", "Write a review"),
        storie_occ="Stories from the café (in Italian)", storie_h2="Naples, told from the counter", storie_tutte="All stories",
        visita_occ="Visit us", visita_h2="Piazza Carità 14, in the heart of Naples",
        visita_p="On Via Toledo, between Piazza Dante and Piazza del Plebiscito, at the entrance to the Pignasecca market and the Spanish Quarter. A few minutes' walk from Toledo and Dante stations on Metro Line 1.",
        btn_maps="Open in Google Maps", btn_chiama="Call",
        scheda=[("Opening hours", "Every day, Sundays included<br>6:30 am – 8:30 pm"), ("Address", None), ("Phone", None), ("Mobile and WhatsApp", None)]),
}


def home(lang='it'):
    it = lang == 'it'
    T = HOME_TESTI[lang]
    rr = "" if it else "../"
    rl = rr + ("" if it else "en/")  # radice delle pagine nella stessa lingua
    k = HOME_FOTO_HERO
    larghezze = (640, 1024, 1280, 1890, 2362)
    alt = [("it", BASE), ("en", BASE + "en/"), ("x-default", BASE)]
    h = testa(lang, T["titolo"], T["descr"], BASE + ("" if it else "en/"), rr, og_img=f"img/{k}-1280.webp",
              ld=[ld_bar(lang)] + ([ld_sito()] if it else []), alternates=alt,
              preload=(f"{rr}img/{k}-1890.webp", ", ".join(f"{rr}img/{k}-{w}.webp {w}w" for w in larghezze), "100vw"))
    srcset = ", ".join(f"{rr}img/{k}-{w}.webp {w}w" for w in larghezze)
    tel = BAR["telefono"] if it else "+39 081 552 3488"
    cell = BAR["cellulare"] if it else "+39 328 438 8404"
    info_val = {2: f'<a href="tel:{BAR["tel_link"]}">{tel}</a> · <a href="{BAR["whatsapp"]}" rel="noopener">WhatsApp</a>',
                3: f'<a href="{BAR["gambero_rosso"]}" rel="noopener">Bar d\'Italia, {"dal" if it else "since"} {BAR["gambero_dal"]}</a>'}
    info = ''.join(f'<div><span>{e(t)}</span><b>{info_val.get(i) or e(v)}</b></div>' for i, (t, v) in enumerate(T["info"]))
    firme = ''.join(
        f'<article class="p-firma"><a href="{rr}{(l_it if it else l_en)}"{"" if it or l_en.startswith("en/") else " hreflang=" + chr(34) + "it" + chr(34)}>'
        f'<figure class="p-arco">{immagine(f, rr, "(max-width: 760px) 86vw, 340px")}</figure>'
        f'<h3>{e(n_it if it else n_en)}</h3><p>{e(d_it if it else d_en)}</p><span class="p-link">{e(c_it if it else c_en)}</span></a></article>'
        for f, n_it, n_en, d_it, d_en, l_it, l_en, c_it, c_en in HOME_FIRME)
    piu = ''.join(f'<a href="{rr}{h_}">{e(t)}</a>' for h_, t in T["firme_piu"])
    giornata = ''.join(
        f'<article class="p-momento"><figure>{immagine(f, rr, "(max-width: 760px) 92vw, 560px")}</figure>'
        f'<div><p class="p-ora">{e(m_it if it else m_en)}</p><h3>{e(t_it if it else t_en)}</h3><p>{e(x_it if it else x_en)}</p>'
        f'<a class="p-link" href="{rr}{l_it if it else l_en}">{e(c_it if it else c_en)}</a></div></article>'
        for f, m_it, m_en, t_it, t_en, x_it, x_en, l_it, l_en, c_it, c_en in HOME_GIORNATA)
    tappe = ''.join(f'<li><span class="p-anno">{a}</span><b>{e(l)}</b><p>{e(t)}</p></li>' for a, l, t in T["tappe"])
    PER = {a["slug"]: a for a in ARTICOLI}
    storie = ''.join(
        f'<article class="p-storia-card"><a href="{rr}storie/{s}/"{"" if it else " hreflang=" + chr(34) + "it" + chr(34)}>'
        f'<figure>{immagine(f, rr, "(max-width: 760px) 92vw, 360px")}</figure>'
        f'<p class="p-ora">{e(CATEGORIA_DI[s]["nome"])}</p><h3{"" if it else " lang=" + chr(34) + "it" + chr(34)}>{e(PER[s]["titolo"])}</h3>'
        f'<p{"" if it else " lang=" + chr(34) + "it" + chr(34)}>{e(PER[s]["dek"])}</p></a></article>' for s, f in HOME_STORIE)
    scheda_val = {1: f'{e(BAR["indirizzo"])}<br>{e(BAR["cap_citta"]) if it else "80134 Naples, Italy"}',
                  2: f'<a href="tel:{BAR["tel_link"]}">{tel}</a>',
                  3: f'<a href="tel:{BAR["cell_link"]}">{cell}</a> · <a href="{BAR["whatsapp"]}" rel="noopener">WhatsApp</a>'}
    scheda = ''.join(f'<div><dt>{e(t)}</dt><dd>{scheda_val.get(i) or v}</dd></div>' for i, (t, v) in enumerate(T["scheda"]))
    l_rec = T["link_rec"]
    return h + f'''<header class="p-hero">
<img class="p-hero-foto" src="{rr}img/{k}-1890.webp" srcset="{srcset}" sizes="100vw" width="1890" height="1260" alt="{e(T["alt_hero"])}" fetchpriority="high" decoding="async">
<div class="p-velo"></div>
{barra(rr, lang, "")}
<div class="p-hero-testo">
<p class="p-occhiello">{e(T["occhiello"])}</p>
<h1>{T["h1"]}</h1>
<p class="p-lead">{e(T["lead"])}</p>
<div class="p-azioni"><a class="p-btn pieno" href="{rl}menu/">{e(T["btn_menu"])}</a><a class="p-btn" href="{BAR["mappa"]}" rel="noopener">{e(T["btn_mappa"])}</a></div>
</div>
</header>
<main id="contenuto">
<section class="p-info" aria-label="{'Informazioni pratiche' if it else 'Practical information'}"><div class="p-wrap p-info-griglia">{info}</div></section>

<section class="p-sez p-firme"><div class="p-wrap">
<div class="p-testa"><p class="p-occhiello scuro">{e(T["firme_occ"])}</p><h2>{e(T["firme_h2"])}</h2><p>{e(T["firme_p"])}</p></div>
<div class="p-firme-griglia">{firme}</div>
<p class="p-piu">{piu}</p>
</div></section>

<section class="p-sez p-giornata"><div class="p-wrap">
<div class="p-testa"><p class="p-occhiello scuro">{e(T["giorno_occ"])}</p><h2>{e(T["giorno_h2"])}</h2></div>
{giornata}
</div></section>

<section class="p-sez p-storia"><div class="p-wrap p-storia-griglia">
<div><p class="p-occhiello">{e(T["storia_occ"])}</p><h2>{e(T["storia_h2"])}</h2>
<ol class="p-tappe">{tappe}</ol>
<a class="p-btn" href="{rl}storia/">{e(T["storia_btn"])}</a></div>
<figure class="p-arco grande"><img src="{rr}img/famiglia-1024.webp" srcset="{rr}img/famiglia-640.webp 640w, {rr}img/famiglia-1024.webp 1024w, {rr}img/famiglia-1600.webp 1600w"
 sizes="(max-width: 760px) 92vw, 500px" width="1600" height="1064" alt="{e(FOTO["famiglia"]["alt"])}" loading="lazy" decoding="async">
<figcaption>{e(T["storia_cap"])}</figcaption></figure>
</div></section>

<section class="p-sez p-voci"><div class="p-wrap p-voci-griglia">
<div class="p-testa"><p class="p-occhiello scuro">{e(T["voci_occ"])}</p><h2>{e(T["voci_h2"])}</h2></div>
<div class="p-voce"><p class="p-grande">Gambero Rosso</p><p>{T["gambero"].format(dal=BAR["gambero_dal"])}</p>
<a class="p-link" href="{BAR["gambero_rosso"]}" rel="noopener"{"" if it else ' hreflang="it"'}>{e(T["gambero_link"])}</a></div>
<div class="p-voce"><p class="p-grande">{BAR["google_voto"] if it else BAR["google_voto_en"]} <small>{e(T["su5"])}</small></p>
<p>{e(T["google"].format(n=BAR["google_n"] if it else BAR["google_n_en"], data=BAR["google_data"]))}</p>
<p class="p-link-riga"><a class="p-link" href="{BAR["google_recensioni"]}" rel="noopener">{e(l_rec[0])}</a><a class="p-link" href="{BAR["tripadvisor"]}" rel="noopener">{e(l_rec[1])}</a><a class="p-link" href="{BAR["google_scrivi"]}" rel="noopener">{e(l_rec[2])}</a></p></div>
</div></section>

<section class="p-sez p-storie"><div class="p-wrap">
<div class="p-testa riga"><div><p class="p-occhiello scuro">{e(T["storie_occ"])}</p><h2>{e(T["storie_h2"])}</h2></div>
<a class="p-link" href="{rr}storie/"{"" if it else ' hreflang="it"'}>{e(T["storie_tutte"])}</a></div>
<div class="p-storie-griglia">{storie}</div>
</div></section>

<section class="p-sez p-visita" id="{'visita' if it else 'visit'}"><div class="p-wrap p-visita-griglia">
<div><p class="p-occhiello">{e(T["visita_occ"])}</p><h2>{e(T["visita_h2"])}</h2>
<p>{e(T["visita_p"])}</p>
<div class="p-azioni"><a class="p-btn pieno" href="{BAR["mappa"]}" rel="noopener">{e(T["btn_maps"])}</a><a class="p-btn" href="tel:{BAR["tel_link"]}">{e(T["btn_chiama"])} {tel}</a></div></div>
<dl class="p-scheda">{scheda}</dl>
</div></section>
</main>
''' + piede(rr, lang)


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
    return h + f'''<header class="testata-scura">{barra("../../", "it", "storie/")}</header>
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
    return h + f'''<header class="testata-scura">{barra("../", "it", "storie/")}</header>
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
    return h + f'''<header class="testata-scura">{barra("../../", "it", "storie/")}</header>
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

# Nomi delle sezioni del menu come appaiono sul sito (su qromo restano quelli interni).
# L'ancora (#bar-dolci, ...) resta ricavata dal nome qromo, così i collegamenti esistenti non cambiano.
NOMI_MENU = {
    "Bar & Dolci": ("Bar e dolci", "Coffee bar and pastries"),
    "Food": ("Rosticceria e pranzo", "Street food and lunch"),
    "Cocktails, Birre & Alcolici": ("Cocktail, birre e alcolici", "Cocktails, beers and spirits"),
    "Tè & Tisane Damman": ("Tè e tisane Dammann", "Dammann teas and infusions"),
    "Oriental latte": ("Matcha, chai e golden milk", "Matcha, chai and golden milk"),
    "Senza Glutine": ("Senza glutine", "Gluten-free"),
    "Gelati": ("Gelati", "Ice cream"),
}

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
            n = _pulisci(m['name'])
            it_, en_ = NOMI_MENU.get(n, (n, n))
            out.append({"nome": it_, "nome_en": en_, "id": _slug(n), "categorie": cats})
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

def _voce_html(v, rr="../", it=True):
    extra = []
    if v['allergeni']:
        extra.append(('Allergeni: ' if it else 'Allergens: ') + ', '.join(v['allergeni']))
    if v['etichette']:
        extra.append(', '.join(v['etichette']).capitalize())
    ex = '<small>' + e('. '.join(extra)) + '</small>' if extra else ''
    de = '<span>' + e(v['desc']) + '</span>' if v['desc'] else ''
    ap = MENU_APPROFONDIMENTI.get(v.get('id'))
    if ap and not it:
        ap = ap if ap.startswith("storie/") else "en/" + ap
    lk = (f'<a class="approfondisci" href="{rr}{ap}"' + ('' if it or not ap.startswith("storie/") else ' hreflang="it" lang="en"') + '>'
          + ("La sua storia" if it and ap.startswith("storie/") else "Scopri di più" if it else "Its story (in Italian)" if ap.startswith("storie/") else next(x["nav"] for x in PAGINE_EN if "en/" + x["slug"] + "/" == ap))
          + '</a>') if ap else ''
    return '<li><div class="voce-testa"><b>' + e(v['nome']) + '</b><i>' + _prezzo(v['prezzo']) + '</i></div>' + de + ex + lk + '</li>'

def pagina_menu(lang='it'):
    it = lang == 'it'
    rr = "../" if it else "../../"
    url = BASE + ("" if it else "en/") + "menu/"
    M = dati_menu()
    n_voci = sum(len(c['voci']) for m in M for c in m['categorie'])
    ld = {"@context": "https://schema.org", "@type": "Menu", "name": "Menu di Ceraldi Caffè" if it else "Ceraldi Caffè menu", "url": url, "inLanguage": "it-IT",
          "hasMenuSection": [{"@type": "MenuSection", "name": m['nome'],
                              "hasMenuSection": [{"@type": "MenuSection", "name": c['nome'], "hasMenuItem": [_voce_ld(v) for v in c['voci']]}
                                                 for c in m['categorie']]} for m in M]}
    if it:
        h = testa("it", "Menu e prezzi | Ceraldi Caffè, Napoli",
                  f"Il menu completo di Ceraldi Caffè, Napoli: {n_voci} proposte, dal caffè ai dolci, dalla rosticceria ai cocktail, con prezzi e allergeni.",
                  url, rr, ld=[ld, ld_breadcrumb([("Menu", url)])], alternates=alt_coppia("menu/"))
    else:
        h = testa("en", "Menu and prices | Ceraldi Caffè, Naples",
                  f"The full menu of Ceraldi Caffè, Naples: {n_voci} items, from coffee and pastries to street food and cocktails, with prices and allergens.",
                  url, rr, ld=[ld, ld_breadcrumb([("Menu", url)])], alternates=alt_coppia("menu/"))
    chips = ''.join('<a href="#' + m['id'] + '">' + e(m['nome'] if it else m['nome_en']) + '</a>' for m in M)
    sezioni = ''
    for m in M:
        sezioni += '<section class="menu-sezione" id="' + m['id'] + '"><h2>' + e(m['nome'] if it else m['nome_en']) + '</h2>'
        for c in m['categorie']:
            sezioni += '<h3>' + e(c['nome']) + '</h3><ul class="menu-voci"' + ('' if it else ' lang="it"') + '>' + ''.join(_voce_html(v, rr, it) for v in c['voci']) + '</ul>'
        sezioni += '</section>'
    scaricato = json.load(open(os.path.join(QUI, 'menu_grezzo.json'), encoding='utf-8')).get('_scaricato', MENU_SCARICATO)
    data = scaricato[8:10] + '/' + scaricato[5:7] + '/' + scaricato[:4]
    if it:
        testo = f"""<h1>Il menu</h1>
<p class="dek">Caffetteria, colazione, pasticceria di produzione propria, rosticceria napoletana, freselle, spritz e cocktail. Prezzi aggiornati al {data}.</p>
<nav class="chips" aria-label="Sezioni del menu">{chips}</nav>
<p class="avviso">Le informazioni sugli allergeni vengono dal nostro menu digitale. In caso di allergie o intolleranze chiedi sempre al personale prima di ordinare. Puoi anche consultare il <a href="{BAR['menu']}" rel="noopener">menu interattivo</a>, con filtro allergeni e versione inglese.</p>"""
    else:
        testo = f"""<h1>Our menu</h1>
<p class="dek">Coffee, breakfast, pastries made in-house, Neapolitan street food, freselle, spritz and cocktails. Prices updated on {data}.</p>
<nav class="chips" aria-label="Menu sections" lang="it">{chips}</nav>
<p class="avviso">Dish names and descriptions are in Italian, as on our counter: your browser can translate them, and our staff will be happy to help. Allergen information comes from our digital menu; if you have allergies or intolerances, always ask the staff before ordering. You can also use our <a href="{BAR['menu']}" rel="noopener">interactive menu</a>, with an allergen filter and an English version.</p>"""
    return h + f"""<header class="testata-scura">{barra(rr, lang, "menu/")}</header>
<main id="contenuto" class="articolo pagina-menu"><div class="contenitore">
<p class="briciole"><a href="{rr}{'' if it else 'en/'}">Ceraldi Caffè</a></p>
{testo}
{sezioni}
</div></main>
""" + piede(rr, lang)

CTA_LINK = {"mappa": (BAR["mappa"], True), "menu_interno": ("../menu/", False), "menu_bar": ("../menu/#bar-dolci", False),
            "menu_dolci": ("../menu/#bar-dolci", False), "menu_food": ("../menu/#food", False),
            "menu_drink": ("../menu/#cocktails-birre-alcolici", False)}

# «Da vedere anche»: collega le pagine autonome (specialità, rosticceria, Aspritz) alle pagine madri,
# così restano raggiungibili anche con la navigazione a sei voci. (percorso IT, titolo IT, testo IT, titolo EN, testo EN)
CORRELATI = {
    "bar": [("specialita/", "Specialità della casa", "Caffè Ceraldi, Caffè Babà, Michelino e i dolci nati da noi", "House specialities", "Caffè Ceraldi, Caffè Babà and our own pastries"),
            ("rosticceria/", "Rosticceria e pranzo veloce", "Frittatine, crocchè, pizza fritta, saltimbocca e freselle", "Street food and quick lunch", "Frittatine, croquettes, fried pizza and freselle"),
            ("aspritz/", "Aspritz e aperitivi", "Il nostro spritz fatto in casa", "Aspritz and aperitivo", "Our homemade spritz")],
    "pasticceria": [("specialita/", "Specialità della casa", "Cestino, Segreto amalfitano, Babàmisù, Pellecchiella", "House specialities", "Cestino, Segreto amalfitano, Babàmisù, Pellecchiella"),
                    ("storie/pasticceria-napoletana/", "Storie della pasticceria napoletana", "Sfogliatella, babà, pastiera, zeppole e i dolci dei conventi", "Neapolitan pastry stories", "In Italian: sfogliatella, babà, pastiera, zeppole"),
                    ("bar/", "Il bar e la colazione", "Il caffè al bancone e la colazione napoletana", "Coffee and breakfast", "Espresso at the counter and Neapolitan breakfast")],
    "rosticceria": [("bar/", "Il bar e la colazione", "Dalla colazione all'English breakfast", "Coffee and breakfast", "From espresso to Full English Breakfast"),
                    ("aspritz/", "Aspritz e aperitivi", "La sera, al tavolo, con il nostro spritz", "Aspritz and aperitivo", "In the evening, with our homemade spritz"),
                    ("menu/", "Il menu completo", "Prezzi e allergeni di tutta la rosticceria", "The full menu", "Prices and allergens")],
    "aspritz": [("bar/", "Il bar e la colazione", "La giornata comincia alle 6:30", "Coffee and breakfast", "The day starts at 6:30 am"),
                ("specialita/", "Specialità della casa", "Caffè e dolci nati da Ceraldi", "House specialities", "Coffees and pastries created at Ceraldi"),
                ("menu/", "Cocktail, birre e alcolici", "Tutta la carta del bar, con i prezzi", "Cocktails, beers and spirits", "The full drinks list, with prices")],
    "storia": [("storie/", "Storie dal caffè", "Il caffè, i dolci e le tradizioni di Napoli", "Stories from the café", "In Italian: coffee, pastries and Neapolitan traditions"),
               ("pasticceria/", "La pasticceria", "Produzione propria, dal laboratorio alla vetrina", "Our pastries", "Made in-house, from our kitchens to the display case"),
               ("contatti/", "Orari e contatti", "Piazza Carità 14, tutti i giorni dalle 6:30 alle 20:30", "Hours and contact", "Piazza Carità 14, every day 6:30 am – 8:30 pm")],
}

def correlati(slug, rr, it=True):
    voci = CORRELATI.get(slug)
    if not voci:
        return ''
    li = ''
    for path, t_it, d_it, t_en, d_en in voci:
        solo_it = path.startswith("storie/")
        href = rr + (path if it or solo_it else "en/" + path)
        li += f'<li><a href="{href}"{"" if it or not solo_it else " hreflang=" + chr(34) + "it" + chr(34)}><b>{e(t_it if it else t_en)}</b><span>{e(d_it if it else d_en)}</span></a></li>'
    return f'<nav class="correlati" aria-label="{"Da vedere anche" if it else "See also"}"><h2>{"Da vedere anche" if it else "See also"}</h2><ul>{li}</ul></nav>'

def pagina(p, lang='it'):
    it = lang == 'it'
    rr = "../" if it else "../../"
    url = BASE + ("" if it else "en/") + p["slug"] + "/"
    k = p["foto"]
    og = f"img/{k}-{FOTO[k]['w'][0]}.webp"
    ld = [ld_breadcrumb([(p["nav"], url)]),
          {"@context": "https://schema.org", "@type": "WebPage", "name": p["titolo"], "description": p["descrizione"], "url": url,
           "isPartOf": {"@id": BASE + "#sito"}, "about": {"@id": BASE + "#bar"}, "primaryImageOfPage": BASE + og, "inLanguage": "it-IT" if it else "en"}]
    h = testa(lang, p["titolo_seo"] + " | Ceraldi Caffè", p["descrizione"], url, rr, og_img=og, ld=ld, alternates=alt_coppia(p["slug"] + "/"))
    gal = p.get("galleria") or []
    galleria = ''
    if gal:
        galleria = '<div class="galleria">' + ''.join('<figure>' + immagine(g, rr, "(max-width: 640px) 50vw, 360px") + '</figure>' for g in gal) + '</div>'
    cta = ''
    for i, (t, c) in enumerate(p.get("cta", [])):
        href, est = CTA_LINK[c]
        cta += '<a class="btn' + (' pieno' if i == 0 else '') + '" href="' + href + '"' + (' rel="noopener"' if est else '') + '>' + e(t) + '</a>'
    return h + f"""<header class="hero hero-pagina">{barra(rr, lang, p["slug"] + "/")}
<div class="contenitore hero-griglia">
<div class="hero-testo"><p class="dal"><a href="{'../' if it else '../'}">Ceraldi Caffè</a> / {e(p["nav"])}</p>
<h1>{e(p["titolo"])}</h1>
<p class="tag">{e(p["dek"])}</p>
<div class="azioni sinistra">{cta}</div></div>
<figure class="specchio">{immagine(k, rr, "(max-width: 900px) 92vw, 480px", eager=True)}</figure>
</div></header>
<main id="contenuto" class="articolo"><div class="contenitore">
<div class="corpo">{p["corpo"]}</div>
{galleria}
{correlati(p["slug"], rr, it)}
<aside class="cartellino"><h2>{'Vieni a trovarci' if it else 'Visit us'}</h2><p>{'Piazza Carità 14, Napoli, lungo via Toledo. Tutti i giorni dalle 6:30 alle 20:30.' if it else 'Piazza Carità 14, Naples, on via Toledo. Open every day from 6:30 am to 8:30 pm.'}</p>
<div class="azioni sinistra"><a class="btn" href="{BAR["mappa"]}" rel="noopener">{'Come arrivare' if it else 'Get directions'}</a><a class="btn" href="tel:{BAR["tel_link"]}">{'Chiama' if it else 'Call'} {BAR["telefono"] if it else '+39 081 552 3488'}</a></div></aside>
</div></main>
""" + piede(rr, lang)

def pagina_contatti():
    url = BASE + "contatti/"
    h = testa("it", "Orari e contatti | Ceraldi Caffè, Piazza Carità 14",
              "Ceraldi Caffè, Piazza Carità 14, Napoli: aperto tutti i giorni 6:30–20:30. Telefono 081 552 3488, WhatsApp 328 438 8404 e come arrivare in metro.",
              url, "../", ld=[ld_bar('it'), ld_breadcrumb([("Contatti", url)]), ld_faq(FAQ)], alternates=alt_coppia("contatti/"))
    return h + f"""<header class="testata-scura">{barra("../", "it", "contatti/")}</header>
<main id="contenuto" class="articolo"><div class="contenitore">
<p class="briciole"><a href="../">Ceraldi Caffè</a></p>
<h1>Contatti e orari</h1>
<p class="dek">Siamo in Piazza Carità, nel centro di Napoli, lungo via Toledo. Aperti tutti i giorni, domenica compresa.</p>
<dl class="scheda contatti">
<div><dt>Indirizzo</dt><dd>Piazza Carità 14<br>80134 Napoli (NA)</dd></div>
<div><dt>Orari</dt><dd>Tutti i giorni<br>dalle 6:30 alle 20:30</dd></div>
<div><dt>Telefono</dt><dd><a href="tel:{BAR["tel_link"]}">081 552 3488</a></dd></div>
<div><dt>Cellulare e WhatsApp</dt><dd><a href="tel:{BAR["cell_link"]}">328 438 8404</a><br>scrivici su <a href="{BAR["whatsapp"]}" rel="noopener">WhatsApp</a></dd></div>
</dl>
<div class="azioni sinistra"><a class="btn scuro" href="{BAR["mappa"]}" rel="noopener">Apri in Google Maps</a><a class="btn scuro-vuoto" href="tel:{BAR["tel_link"]}">Chiama</a><a class="btn scuro-vuoto" href="{BAR["whatsapp"]}" rel="noopener">Scrivi su WhatsApp</a></div>
<figure>{immagine("sala-ingresso-piazza-carita", "../", "(max-width: 800px) 100vw, 760px")}</figure>
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
<h2>Domande frequenti</h2>
<div class="domande">{faq_html(FAQ)}</div>
<h2>Dati aziendali</h2>
<p>{RAGIONE_SOCIALE}<br>Piazza Carità 14, 80134 Napoli (NA)<br>P. IVA {PIVA}</p>
</div>
</div></main>
""" + piede("../")

PRIVACY_NESSUN_COOKIE = """<p>Questo sito è una vetrina informativa. <strong>Non usa cookie, non usa strumenti di statistica o di profilazione e non contiene moduli</strong> che raccolgono dati personali. Anche i caratteri tipografici sono ospitati sul sito stesso, senza chiamate a servizi esterni.</p>"""
PRIVACY_STATISTICHE = """<p>Questo sito è una vetrina informativa e <strong>non contiene moduli</strong> che raccolgono dati personali. I caratteri tipografici sono ospitati sul sito stesso.</p>
<h2>Statistiche (Google Analytics 4), solo con il tuo consenso</h2>
<p>Se accetti nel banner, il sito usa Google Analytics 4, servizio di Google Ireland Limited, per contare le visite e i clic su Chiama, Indicazioni, WhatsApp e Menu. Servono a capire quali informazioni sono utili, non a fare pubblicità: non attiviamo funzioni pubblicitarie né la condivisione dei dati per la pubblicità.</p>
<p>Cookie usati: <strong>_ga</strong> e <strong>_ga_&lt;ID&gt;</strong>, che distinguono le visite; durata fino a 2 anni. Senza il tuo consenso Google Analytics non viene caricato e non viene installato alcun cookie. La scelta resta salvata nel tuo browser per 6 mesi e puoi cambiarla in qualsiasi momento dal link <em>Preferenze cookie</em> in fondo a ogni pagina.</p>
<p>Base giuridica: il tuo consenso (art. 6.1.a GDPR). I dati possono essere trattati da Google anche fuori dall'Unione europea, secondo le garanzie previste dalla sua informativa: <a href="https://policies.google.com/privacy" rel="noopener">policies.google.com/privacy</a>.</p>"""

def pagina_privacy():
    url = BASE + "privacy/"
    data = OGGI[8:10] + '/' + OGGI[5:7] + '/' + OGGI[:4]
    h = testa("it", "Privacy e cookie | Ceraldi Caffè", "Informativa sulla privacy e sui cookie del sito di Ceraldi Caffè, Piazza Carità 14, Napoli.", url, "../", alternates=alt_coppia("privacy/"))
    return h + f"""<header class="testata-scura">{barra("../", "it", "privacy/")}</header>
<main id="contenuto" class="articolo"><div class="contenitore">
<p class="briciole"><a href="../">Ceraldi Caffè</a></p>
<h1>Privacy e cookie</h1>
<p class="meta">Ultimo aggiornamento: {data}</p>
<div class="corpo">
<h2>Titolare</h2>
<p>{RAGIONE_SOCIALE}, Piazza Carità 14, 80134 Napoli (NA), P. IVA {PIVA}. Per qualsiasi richiesta sui dati personali puoi contattarci al numero <a href="tel:{BAR["tel_link"]}">081 552 3488</a> o presso la sede.</p>
<h2>Cosa raccoglie questo sito</h2>
{PRIVACY_STATISTICHE if GA_ID else PRIVACY_NESSUN_COOKIE}
<h2>Hosting</h2>
<p>Il sito è ospitato su GitHub Pages (GitHub, Inc.). Come ogni server web, il fornitore di hosting può registrare dati tecnici delle visite, come l'indirizzo IP, per motivi di sicurezza e di funzionamento del servizio, secondo la propria informativa.</p>
<h2>Link esterni</h2>
<p>Alcuni link portano a servizi di terzi: Google Maps e Google (recensioni), Tripadvisor, Instagram, Facebook, WhatsApp e il nostro menu interattivo su qromo. Quando li apri si applicano le informative privacy e cookie di quei servizi.</p>
<h2>I tuoi diritti</h2>
<p>In base al Regolamento UE 2016/679 (GDPR) puoi chiedere l'accesso, la rettifica o la cancellazione dei dati che ti riguardano e proporre reclamo al Garante per la protezione dei dati personali.</p>
</div>
</div></main>
""" + piede("../")


def pagina_contatti_en():
    url = BASE + "en/contatti/"
    h = testa("en", "Opening hours and contact | Ceraldi Caffè, Naples",
              "Ceraldi Caffè, Piazza Carità 14, Naples: open daily 6:30 am – 8:30 pm. Phone +39 081 552 3488, WhatsApp +39 328 438 8404 and how to get here by metro.",
              url, "../../", ld=[ld_bar('en'), ld_breadcrumb([("Contact", url)]), ld_faq(FAQ_EN)], alternates=alt_coppia("contatti/"))
    return h + f"""<header class="testata-scura">{barra("../../", "en", "contatti/")}</header>
<main id="contenuto" class="articolo"><div class="contenitore">
<p class="briciole"><a href="../">Ceraldi Caffè</a></p>
<h1>Opening hours and contact</h1>
<p class="dek">We are in Piazza Carità, in the centre of Naples, on via Toledo. Open every day, Sundays included.</p>
<dl class="scheda contatti">
<div><dt>Address</dt><dd>Piazza Carità 14<br>80134 Naples, Italy</dd></div>
<div><dt>Opening hours</dt><dd>Every day<br>6:30 am – 8:30 pm</dd></div>
<div><dt>Phone</dt><dd><a href="tel:{BAR["tel_link"]}">+39 081 552 3488</a></dd></div>
<div><dt>Mobile and WhatsApp</dt><dd><a href="tel:{BAR["cell_link"]}">+39 328 438 8404</a><br>message us on <a href="{BAR["whatsapp"]}" rel="noopener">WhatsApp</a></dd></div>
</dl>
<div class="azioni sinistra"><a class="btn scuro" href="{BAR["mappa"]}" rel="noopener">Open in Google Maps</a><a class="btn scuro-vuoto" href="tel:{BAR["tel_link"]}">Call</a><a class="btn scuro-vuoto" href="{BAR["whatsapp"]}" rel="noopener">Message us on WhatsApp</a></div>
<figure>{immagine("sala-ingresso-piazza-carita", "../../", "(max-width: 800px) 100vw, 760px")}</figure>
<div class="corpo">
<h2>How to get here</h2>
<ul>
<li><strong>By metro</strong>: Line 1, <strong>Toledo</strong> or <strong>Dante</strong> stations, a few minutes' walk away.</li>
<li><strong>On foot</strong>: we are on via Toledo, between piazza Dante and piazza del Plebiscito, at the entrance to the Pignasecca market and the Quartieri Spagnoli.</li>
<li><strong>By car</strong>: much of the city centre is a limited traffic zone (ZTL); it is best to leave your car in a car park and continue on foot or by metro.</li>
</ul>
<h2>Reviews</h2>
<p>Read what people say about us on <a href="{BAR["google_recensioni"]}" rel="noopener">Google</a> and <a href="{BAR["tripadvisor"]}" rel="noopener">Tripadvisor</a>. If you have visited us, please <a href="{BAR["google_scrivi"]}" rel="noopener">leave a review</a>: it helps us improve.</p>
<h2>Social media</h2>
<p>Follow us on <a href="{BAR["instagram"]}" rel="noopener">Instagram</a> and <a href="{BAR["facebook"]}" rel="noopener">Facebook</a>.</p>
<h2>Frequently asked questions</h2>
<div class="domande">{faq_html(FAQ_EN)}</div>
<h2>Company details</h2>
<p>{RAGIONE_SOCIALE}<br>Piazza Carità 14, 80134 Napoli (NA), Italy<br>VAT no. {PIVA}</p>
</div>
</div></main>
""" + piede("../../", "en")

PRIVACY_EN_NESSUN_COOKIE = """<p>This website is for information only. <strong>It uses no cookies, no analytics or profiling tools, and no forms</strong> that collect personal data. Fonts are hosted on the site itself, with no calls to external services.</p>"""
PRIVACY_EN_STATISTICHE = """<p>This website is for information only and <strong>contains no forms</strong> that collect personal data. Fonts are hosted on the site itself.</p>
<h2>Analytics (Google Analytics 4), only with your consent</h2>
<p>If you accept in the banner, the site uses Google Analytics 4, a service of Google Ireland Limited, to count visits and clicks on Call, Directions, WhatsApp and Menu. This helps us understand which information is useful; it is not used for advertising, and advertising features and data sharing for advertising are not enabled.</p>
<p>Cookies used: <strong>_ga</strong> and <strong>_ga_&lt;ID&gt;</strong>, which distinguish visits; they last up to 2 years. Without your consent Google Analytics is not loaded and no cookies are set. Your choice is stored in your browser for 6 months and you can change it at any time from the <em>Cookie preferences</em> link at the bottom of every page.</p>
<p>Legal basis: your consent (Art. 6(1)(a) GDPR). Data may be processed by Google outside the European Union, with the safeguards described in its privacy policy: <a href="https://policies.google.com/privacy" rel="noopener">policies.google.com/privacy</a>.</p>"""

def pagina_privacy_en():
    url = BASE + "en/privacy/"
    data = OGGI
    h = testa("en", "Privacy and cookies | Ceraldi Caffè", "Privacy and cookie policy of the Ceraldi Caffè website, Piazza Carità 14, Naples.", url, "../../", alternates=alt_coppia("privacy/"))
    return h + f"""<header class="testata-scura">{barra("../../", "en", "privacy/")}</header>
<main id="contenuto" class="articolo"><div class="contenitore">
<p class="briciole"><a href="../">Ceraldi Caffè</a></p>
<h1>Privacy and cookies</h1>
<p class="meta">Last updated: <time datetime="{data}">{data}</time>. The Italian version is the reference text.</p>
<div class="corpo">
<h2>Data controller</h2>
<p>{RAGIONE_SOCIALE}, Piazza Carità 14, 80134 Napoli (NA), Italy, VAT no. {PIVA}. For any request about personal data you can call us on <a href="tel:{BAR["tel_link"]}">+39 081 552 3488</a> or visit us.</p>
<h2>What this website collects</h2>
{PRIVACY_EN_STATISTICHE if GA_ID else PRIVACY_EN_NESSUN_COOKIE}
<h2>Hosting</h2>
<p>The site is hosted on GitHub Pages (GitHub, Inc.). Like any web server, the hosting provider may log technical data about visits, such as the IP address, for security and operational purposes, under its own privacy policy.</p>
<h2>External links</h2>
<p>Some links lead to third-party services: Google Maps and Google (reviews), Tripadvisor, Instagram, Facebook, WhatsApp and our interactive menu on qromo. When you open them, their own privacy and cookie policies apply.</p>
<h2>Your rights</h2>
<p>Under Regulation (EU) 2016/679 (GDPR) you can request access to, correction or deletion of your data, and lodge a complaint with the Italian Data Protection Authority (Garante per la protezione dei dati personali).</p>
</div>
</div></main>
""" + piede("../../", "en")


def pagina_specialita(lang='it'):
    it = lang == 'it'
    rr = "../" if it else "../../"
    url = BASE + ("" if it else "en/") + "specialita/"
    d = json.load(open(os.path.join(QUI, 'menu_grezzo.json'), encoding='utf-8'))
    PROD = {i['menu_item_id']: i for i in d['menusItems'] if i['available']}
    ALL = {}
    for a in d['menusItemsAllergens']:
        ALL.setdefault(a['menu_item_id'], []).append(a['allergen_id'])
    sezioni = ''; voci_ld = []
    for g in SPECIALITA:
        schede = ''
        for pid, foto, d_it, d_en in g["voci"]:
            if pid not in PROD:
                continue  # non più nel menu: non si mostra
            nome = _pulisci(PROD[pid]['name']).replace('Babámisú', 'Babàmisù').replace('Sfogliata Santa Rosa', 'Santa Rosa')
            ancora = _slug(nome)
            al = [ALLERGENI[x] for x in ALL.get(pid, []) if x in ALLERGENI]
            fig = f'<figure>{immagine(foto, rr, "(max-width: 640px) 100vw, 360px")}</figure>' if foto else ''
            al_txt = (('Allergeni: ' if it else 'Allergens (in Italian): ') + ', '.join(al) + '.') if al else ('Allergeni: chiedi al personale.' if it else 'Allergens: please ask our staff.')
            schede += (f'<article class="spec" id="{ancora}">{fig}<div><h3>{e(nome)}</h3><p>{e(d_it if it else d_en)}</p>'
                       f'<p class="spec-al">{e(al_txt)}</p><a class="approfondisci" href="{rr}{"" if it else "en/"}menu/#{g["menu"]}">{"Nel menu, con il prezzo" if it else "On the menu, with price"}</a></div></article>')
            voci_ld.append({"@type": "MenuItem", "name": nome, "description": d_it if it else d_en, "url": url + "#" + ancora,
                            **({"image": BASE + f"img/{foto}-{FOTO[foto]['w'][0]}.webp"} if foto else {})})
        if schede:
            sezioni += f'<section class="spec-gruppo"><h2>{e(g["nome"] if it else g["nome_en"])}</h2><div class="spec-griglia">{schede}</div></section>'
    titolo = "Specialità della casa" if it else "House specialities"
    descr = ("Caffè Ceraldi, Caffè Babà, Cestino, Segreto amalfitano, Babàmisù, Aspritz: le specialità nate da Ceraldi Caffè in Piazza Carità, Napoli."
             if it else "Caffè Ceraldi, Caffè Babà, Cestino, Segreto amalfitano, Babàmisù, Aspritz: the specialities created at Ceraldi Caffè in Piazza Carità, Naples.")
    ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": titolo, "url": url, "itemListElement":
           [{"@type": "ListItem", "position": i + 1, "item": v} for i, v in enumerate(voci_ld)]},
          ld_breadcrumb([(titolo, url)])]
    h = testa(lang, f"{titolo} | Ceraldi Caffè, Napoli" if it else f"{titolo} | Ceraldi Caffè, Naples", descr, url, rr, og_img="img/cestino-768.webp", ld=ld, alternates=alt_coppia("specialita/"))
    intro = ("Oltre all'espresso e ai classici napoletani, al bancone e in vetrina ci sono prodotti che trovi solo da noi. Descrizioni, ingredienti e allergeni vengono dal nostro menu e si aggiornano con lui; in caso di allergie chiedi sempre al personale."
             if it else "Besides espresso and the Neapolitan classics, our counter and display case hold products you will only find here. Descriptions, ingredients and allergens come from our menu and are updated with it; if you have allergies, always ask our staff.")
    return h + f"""<header class="testata-scura">{barra(rr, lang, "specialita/")}</header>
<main id="contenuto" class="articolo pagina-larga"><div class="contenitore">
<p class="briciole"><a href="{rr}{'' if it else 'en/'}">Ceraldi Caffè</a></p>
<h1>{titolo}</h1>
<p class="dek">{e(intro)}</p>
{sezioni}
<aside class="cartellino"><h2>{'Vieni ad assaggiarle' if it else 'Come and taste them'}</h2><p>{'Piazza Carità 14, Napoli, lungo via Toledo. Tutti i giorni dalle 6:30 alle 20:30.' if it else 'Piazza Carità 14, Naples, on via Toledo. Open every day from 6:30 am to 8:30 pm.'}</p>
<div class="azioni sinistra"><a class="btn" href="{BAR["mappa"]}" rel="noopener">{'Come arrivare' if it else 'Get directions'}</a><a class="btn" href="{rr}{'' if it else 'en/'}menu/">{'Il menu completo' if it else 'Full menu'}</a></div></aside>
</div></main>
""" + piede(rr, lang)


def sitemap():
    """Sitemap generata dalle pagine indicizzabili effettivamente scritte.
    lastmod = data dell'ultima modifica reale del contenuto: il registro lastmod.json conserva l'impronta di ogni
    pagina e la data cambia solo se cambia il contenuto (non a ogni pubblicazione)."""
    reg_path = os.path.join(QUI, "lastmod.json")
    reg = json.load(open(reg_path, encoding="utf-8")) if os.path.exists(reg_path) else {}
    oggi = datetime.date.today().isoformat()
    righe = ''
    for url, impronta in sorted(set(PAGINE_SITEMAP)):
        voce = reg.get(url)
        if not voce or voce[0] != impronta:
            reg[url] = [impronta, oggi]
        righe += f'<url><loc>{url}</loc><lastmod>{reg[url][1]}</lastmod></url>'
    json.dump(reg, open(reg_path, "w", encoding="utf-8"), indent=1, sort_keys=True)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{righe}</urlset>\n'

def llms():
    righe = '\n'.join(f'- [{a["titolo"]}]({BASE}storie/{a["slug"]}/): {a["descrizione"]}' for a in ARTICOLI)
    return f'''# Ceraldi Caffè

> Bar e pasticceria napoletana in Piazza Carità 14, Napoli (80134). Attività della famiglia Ceraldi, fondata da Michele Ceraldi nel 1973 in Piazza Garibaldi, in Piazza Carità dal 2002. Motto: "Artigiani per passione dal 1973". Pasticceria di produzione propria con ricette di famiglia tramandate di generazione in generazione.

## Informazioni essenziali
- Indirizzo: Piazza Carità 14, 80134 Napoli, Italia (lungo via Toledo, vicino alle stazioni metro Toledo e Dante, Linea 1)
- Orari: tutti i giorni, domenica compresa, 6:30 – 20:30
- Telefono: +39 081 552 3488; cellulare e WhatsApp: +39 328 438 8404
- Menu completo con prezzi: {BASE}menu/ (menu interattivo con allergeni: {BAR["menu"]})
- Ragione sociale: {RAGIONE_SOCIALE}, P. IVA {PIVA}
- Recensioni: Google ({BAR["google_recensioni"]}), Tripadvisor ({BAR["tripadvisor"]}); valutazione {BAR['google_voto']}/5 su Google con {BAR['google_n']} recensioni (dato rilevato il {BAR['google_data']})
- Riconoscimenti: nella guida Bar d'Italia del Gambero Rosso dal {BAR['gambero_dal']}, presenti nell'edizione 2026 (scheda: {BAR["gambero_rosso"]})
- Instagram: {BAR["instagram"]}
- Mappa: {BAR["mappa"]}

## Cosa offre
- Colazione all'italiana: croissant (vuoti, crema, crema e amarena, cioccolato, albicocca, integrali, vegani), brioche, kranz, pain au chocolat, maritozzo, graffa napoletana
- Pasticceria napoletana di produzione propria: sfogliatella riccia e frolla, sfogliata Santa Rosa, babà al rum, pastiera napoletana, zeppola di San Giuseppe, codina di aragosta
- Dolci della casa: Cestino, Segreto amalfitano, Babàmisù, Pellecchiella (torta con albicocche Pellecchielle del Vesuvio), torta di mele Annurca IGP
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
# Vecchi indirizzi -> nuova pagina. Comprende gli articoli 2019 del vecchio WordPress (permalink /anno/mese/giorno/nome/)
# e gli articoli del sito nuovo assorbiti da una pagina principale.
RIMANDI = {
    "1973-2": "storia",
    "gastronomia": "rosticceria",
    "2019/02/26/artigiani-per-passione": "storia",
    "2019/02/26/caffe-napoletano": "storie/caffe-napoletano",
    "2019/04/01/a-napoli-e-sempre-dolce-la-primavera": "storie/pastiera",
    "2019/04/15/aspritz-aperitivo-ceraldi-caffe": "aspritz",
    "2019/05/09/festa-della-mamma-ceraldi-caffe": "storie/festa-della-mamma",
    "storie/pasticceria-artigianale": "pasticceria",
}
def rimando(dest):
    u = BASE + dest + "/"
    return f'''<!DOCTYPE html>
<html lang="it"><head><meta charset="utf-8"><title>Pagina spostata | Ceraldi Caffè</title>
<link rel="canonical" href="{u}">
<meta http-equiv="refresh" content="0; url={u}"></head>
<body><p>Questa pagina si è spostata: <a href="{u}">vai alla nuova pagina</a>.</p></body></html>
'''

def robots():
    return f"User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n"

if __name__ == "__main__":
    scrivi("index.html", home("it"))
    scrivi("en/index.html", home("en"))
    scrivi("storie/index.html", indice_storie())
    for a in ARTICOLI:
        scrivi(f"storie/{a['slug']}/index.html", articolo(a))
    for c in CATEGORIE:
        scrivi(f"storie/{c['slug']}/index.html", pagina_categoria(c))
    for p in PAGINE:
        scrivi(f"{p['slug']}/index.html", pagina(p))
    for p in PAGINE_EN:
        scrivi(f"en/{p['slug']}/index.html", pagina(p, "en"))
    scrivi("en/menu/index.html", pagina_menu("en"))
    scrivi("specialita/index.html", pagina_specialita("it"))
    scrivi("en/specialita/index.html", pagina_specialita("en"))
    scrivi("en/contatti/index.html", pagina_contatti_en())
    scrivi("en/privacy/index.html", pagina_privacy_en())
    scrivi("menu/index.html", pagina_menu())
    scrivi("contatti/index.html", pagina_contatti())
    scrivi("privacy/index.html", pagina_privacy())
    scrivi("llms.txt", llms())
    scrivi("404.html", pagina_404(BASE))
    # GitHub Pages usa solo il 404.html alla radice del repository: per gli indirizzi fuori da /caffe/ (le app) mostra un messaggio neutro
    percorso = urllib.parse.urlparse(BASE).path
    neutro = (f"<script>if(location.pathname.indexOf('{percorso}')!==0){{document.title='Pagina non trovata';"
              "document.body.innerHTML='<main style=\"font-family:system-ui,sans-serif;padding:48px 24px;text-align:center\"><h1>Pagina non trovata</h1><p>Controlla l\\'indirizzo.</p></main>';}}</script>")
    scrivi("../404.html", pagina_404(BASE).replace("</body>", neutro + "</body>", 1))
    for vecchio, nuovo in RIMANDI.items():
        scrivi(f"{vecchio}/index.html", rimando(nuovo))
    scrivi("robots.txt", robots())
    scrivi("sitemap.xml", sitemap())
    print("Pagine generate:", 6 + len(ARTICOLI) + len(PAGINE) + len(CATEGORIE) + len(PAGINE_EN) + 5)
