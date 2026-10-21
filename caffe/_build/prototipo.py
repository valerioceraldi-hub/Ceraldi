# -*- coding: utf-8 -*-
"""Prototipo della homepage «Salotto Liberty» (fase 2). Uso: python3 caffe/_build/prototipo.py
Scrive caffe/prototipo/index.html: pagina NON indicizzata e fuori dalla sitemap, solo per la valutazione.
Riusa dati e funzioni del sito (build.py, contenuti.py): nessun testo commerciale è scritto qui due volte."""
import os, sys
QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import build as B  # noqa: E402
from build import BAR, ARTICOLI, e, immagine  # noqa: E402

RR = "../"
ART = {a["slug"]: a for a in ARTICOLI}

# Ogni foto compare una sola volta nella pagina (controllato anche da controlla.py)
FIRME = [
    ("sfogliatella-riccia", "Sfogliatella riccia", "Ricotta, semola, canditi e cannella dentro mille sfoglie croccanti. Riccia, frolla o Santa Rosa.", "storie/sfogliatella/", "La sua storia"),
    ("baba-al-rum-classico", "Babà al rum", "Soffice e bagnato al punto giusto: classico, con crema e amarena oppure con panna e fragole.", "storie/baba/", "La sua storia"),
    ("caffe-ceraldi", "Caffè Ceraldi", "La nostra firma al bancone: cioccolata calda sul fondo, crema di caffè e panna montata fresca.", "specialita/", "I caffè della casa"),
]
GIORNATA = [
    ("cornetti-caffe-bancone", "Mattina", "Colazione al bancone", "Cornetto e cappuccino, sfogliatella o graffa appena fatta. E per chi viene da lontano, la Full English Breakfast tutte le mattine.", "bar/", "Il bar e la colazione"),
    ("latte-macchiato-dolci", "Pomeriggio", "Una pausa in sala", "Un caffè della casa e un dolce della vetrina, seduti tra gli specchi e le poltroncine rosse.", "pasticceria/", "La pasticceria"),
    ("cocktail-barman", "Sera", "L'aperitivo", "L'Aspritz fatto in casa con agrumi della Costiera e Asprinio di Aversa, spritz e cocktail preparati al banco.", "aspritz/", "L'Aspritz"),
]
STORIE = [("caffe-sospeso", "squadra"), ("pastiera", "pastiera"), ("piazza-carita-via-toledo", "sala-bianca")]
NAV = [("bar/", "Il bar"), ("pasticceria/", "Pasticceria"), ("menu/", "Menu"), ("storia/", "Storia"), ("storie/", "Storie"), ("contatti/", "Contatti")]


def hero():
    k = "sala-ingresso-piazza-carita"
    srcset = ", ".join(f"{RR}img/{k}-{w}.webp {w}w" for w in (640, 1024, 1280, 1890, 2362))
    return f'''<header class="p-hero">
<img class="p-hero-foto" src="{RR}img/{k}-1890.webp" srcset="{srcset}" sizes="100vw" width="1890" height="1260"
 alt="La sala di Ceraldi Caffè in Piazza Carità: specchi, soffitto Liberty e poltroncine in pelle rossa" fetchpriority="high" decoding="async">
<div class="p-velo"></div>
<div class="p-barra">
<a class="p-marchio" href="{RR}"><img src="{RR}img/logo-ceraldi-chiaro.svg" width="150" height="52" alt="Ceraldi Caffè"></a>
<nav class="p-nav" aria-label="Principale">{''.join(f'<a href="{RR}{h}">{t}</a>' for h, t in NAV)}<a href="{RR}en/" hreflang="en" lang="en" class="p-lingua">EN</a></nav>
<details class="p-nav-mobile"><summary aria-label="Apri le sezioni del sito"><span class="p-burger" aria-hidden="true"></span></summary><nav aria-label="Principale">{''.join(f'<a href="{RR}{h}">{t}</a>' for h, t in NAV)}<a href="{RR}en/" hreflang="en" lang="en">English</a></nav></details>
</div>
<div class="p-hero-testo">
<p class="p-occhiello">Bar e pasticceria · Piazza Carità 14, Napoli</p>
<h1>Artigiani per passione, dal&nbsp;1973</h1>
<p class="p-lead">Caffè napoletano, sfogliatelle e babà di produzione propria. Dalla prima tazzina delle 6:30 all'aperitivo della sera, lungo via Toledo.</p>
<div class="p-azioni"><a class="p-btn pieno" href="{RR}menu/">Guarda il menu</a><a class="p-btn" href="{BAR["mappa"]}" rel="noopener">Come arrivare</a></div>
</div>
</header>'''


def info():
    return f'''<section class="p-info" aria-label="Informazioni pratiche"><div class="p-wrap p-info-griglia">
<div><span>Orari</span><b>Tutti i giorni, 6:30 – 20:30</b></div>
<div><span>Indirizzo</span><b><a href="{BAR["mappa"]}" rel="noopener">Piazza Carità 14</a> · metro Toledo e Dante</b></div>
<div><span>Telefono</span><b><a href="tel:{BAR["tel_link"]}">{BAR["telefono"]}</a> · <a href="{BAR["whatsapp"]}" rel="noopener">WhatsApp</a></b></div>
<div><span>Gambero Rosso</span><b><a href="{BAR["gambero_rosso"]}" rel="noopener">Bar d'Italia, dal {BAR["gambero_dal"]}</a></b></div>
</div></section>'''


def firme():
    schede = "".join(f'''<article class="p-firma"><a href="{RR}{link}">
<figure class="p-arco">{immagine(k, RR, "(max-width: 760px) 86vw, 340px")}</figure>
<h3>{e(t)}</h3><p>{e(d)}</p><span class="p-link">{e(cta)}</span></a></article>''' for k, t, d, link, cta in FIRME)
    return f'''<section class="p-sez p-firme"><div class="p-wrap">
<div class="p-testa"><p class="p-occhiello scuro">Produzione propria</p><h2>Tre firme della casa</h2>
<p>Nascono nei nostri laboratori, ogni giorno, con ricette di famiglia tramandate nel tempo.</p></div>
<div class="p-firme-griglia">{schede}</div>
<p class="p-piu"><a href="{RR}specialita/">Tutte le specialità della casa</a><a href="{RR}menu/">Il menu completo</a></p>
</div></section>'''


def giornata():
    righe = "".join(f'''<article class="p-momento">
<figure>{immagine(k, RR, "(max-width: 760px) 92vw, 520px")}</figure>
<div><p class="p-ora">{e(ora)}</p><h3>{e(t)}</h3><p>{e(d)}</p><a class="p-link" href="{RR}{link}">{e(cta)}</a></div>
</article>''' for k, ora, t, d, link, cta in GIORNATA)
    return f'''<section class="p-sez p-giornata"><div class="p-wrap">
<div class="p-testa"><p class="p-occhiello scuro">Dalle 6:30 alle 20:30</p><h2>Una giornata da Ceraldi</h2></div>
{righe}
</div></section>'''


def storia():
    tappe = [("1973", "Piazza Garibaldi", "Michele Ceraldi apre il suo primo bar davanti alla stazione, tra chi parte e chi arriva."),
             ("2002", "Piazza Carità", "L'arrivo al numero 14, lungo via Toledo: un angolo vuoto che sembrava aspettarci."),
             ("Oggi", "Padre e figli", "Michele porta avanti il bar con Vincenzo e Valerio, dal laboratorio al bancone.")]
    li = "".join(f'<li><span class="p-anno">{a}</span><b>{e(l)}</b><p>{e(t)}</p></li>' for a, l, t in tappe)
    return f'''<section class="p-sez p-storia"><div class="p-wrap p-storia-griglia">
<div><p class="p-occhiello">La nostra storia</p><h2>Tre date, una famiglia</h2>
<ol class="p-tappe">{li}</ol>
<a class="p-btn" href="{RR}storia/">Leggi la storia</a></div>
<figure class="p-arco grande"><img src="{RR}img/famiglia-1024.webp" srcset="{RR}img/famiglia-640.webp 640w, {RR}img/famiglia-1024.webp 1024w, {RR}img/famiglia-1600.webp 1600w"
 sizes="(max-width: 760px) 92vw, 460px" width="1600" height="1064" alt="{e(B.FOTO["famiglia"]["alt"])}" loading="lazy" decoding="async">
<figcaption>La famiglia Ceraldi nella sala di Piazza Carità.</figcaption></figure>
</div></section>'''


def reputazione():
    return f'''<section class="p-sez p-voci"><div class="p-wrap p-voci-griglia">
<div class="p-testa"><p class="p-occhiello scuro">Riconoscimenti e recensioni</p><h2>Cosa dicono di noi</h2></div>
<div class="p-voce"><p class="p-grande">Gambero Rosso</p><p>Nella guida <strong>Bar d'Italia</strong> dal {BAR["gambero_dal"]}, presenti anche nell'edizione 2026.</p>
<a class="p-link" href="{BAR["gambero_rosso"]}" rel="noopener">Leggi la scheda</a></div>
<div class="p-voce"><p class="p-grande">{BAR["google_voto"]} <small>su 5</small></p><p>Valutazione media su Google, su {BAR["google_n"]} recensioni. Dato rilevato il {BAR["google_data"]}.</p>
<p class="p-link-riga"><a class="p-link" href="{BAR["google_recensioni"]}" rel="noopener">Recensioni su Google</a><a class="p-link" href="{BAR["tripadvisor"]}" rel="noopener">Tripadvisor</a><a class="p-link" href="{BAR["google_scrivi"]}" rel="noopener">Lascia una recensione</a></p></div>
</div></section>'''


def storie():
    schede = "".join(f'''<article class="p-storia-card"><a href="{RR}storie/{s}/">
<figure>{immagine(k, RR, "(max-width: 760px) 92vw, 340px")}</figure>
<p class="p-ora">{e(B.CATEGORIA_DI[s]["nome"])}</p><h3>{e(ART[s]["titolo"])}</h3><p>{e(ART[s]["dek"])}</p></a></article>''' for s, k in STORIE)
    return f'''<section class="p-sez p-storie"><div class="p-wrap">
<div class="p-testa riga"><div><p class="p-occhiello scuro">Storie dal caffè</p><h2>Napoli raccontata dal bancone</h2></div>
<a class="p-link" href="{RR}storie/">Tutte le storie</a></div>
<div class="p-storie-griglia">{schede}</div>
</div></section>'''


def visita():
    return f'''<section class="p-sez p-visita" id="visita"><div class="p-wrap p-visita-griglia">
<div><p class="p-occhiello">Vieni a trovarci</p><h2>Piazza Carità 14, nel cuore di Napoli</h2>
<p>Lungo via Toledo, tra piazza Dante e piazza del Plebiscito, all'ingresso della Pignasecca e dei Quartieri Spagnoli. A pochi minuti a piedi dalle fermate Toledo e Dante della metro Linea 1.</p>
<div class="p-azioni"><a class="p-btn pieno" href="{BAR["mappa"]}" rel="noopener">Apri in Google Maps</a><a class="p-btn" href="tel:{BAR["tel_link"]}">Chiama {BAR["telefono"]}</a></div></div>
<dl class="p-scheda">
<div><dt>Orari</dt><dd>Tutti i giorni, domenica compresa<br>dalle 6:30 alle 20:30</dd></div>
<div><dt>Indirizzo</dt><dd>{e(BAR["indirizzo"])}<br>{e(BAR["cap_citta"])}</dd></div>
<div><dt>Telefono</dt><dd><a href="tel:{BAR["tel_link"]}">{BAR["telefono"]}</a></dd></div>
<div><dt>Cellulare e WhatsApp</dt><dd><a href="tel:{BAR["cell_link"]}">{BAR["cellulare"]}</a> · <a href="{BAR["whatsapp"]}" rel="noopener">WhatsApp</a></dd></div>
</dl>
</div></section>'''


def pagina():
    h = B.testa("it", "Prototipo homepage | Ceraldi Caffè", "Prototipo della nuova homepage di Ceraldi Caffè, non indicizzato.",
                B.BASE + "prototipo/", RR, preload=f"{RR}img/sala-ingresso-piazza-carita-1890.webp")
    h = h.replace('content="index, follow, max-image-preview:large"', 'content="noindex, nofollow"')
    h = h.replace(f'<link rel="stylesheet" href="{RR}assets/sito.css">', f'<link rel="stylesheet" href="{RR}assets/prototipo.css">')
    h = h.replace(f'{RR}assets/font/WorkSans-normal-400-latin.woff2', f'{RR}assets/font/Jost-normal-400-latin.woff2')
    corpo = hero() + '<main id="contenuto">' + info() + firme() + giornata() + storia() + reputazione() + storie() + visita() + '</main>'
    piede = B.piede(RR).replace('class="piede"', 'class="piede p-piede"').replace(f'<a href="{RR}menu/">Menu</a></nav>', f'<a href="{RR}menu/">Il menu</a></nav>')
    nota = '<p class="p-prototipo" role="note">Prototipo · non indicizzato</p>'
    return h + corpo + piede.replace("</body>", nota + "</body>", 1)


if __name__ == "__main__":
    p = os.path.join(B.SITO, "prototipo", "index.html")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(pagina())
    print("Scritto", os.path.relpath(p, os.path.dirname(B.SITO)))
