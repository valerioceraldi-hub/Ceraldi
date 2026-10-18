# -*- coding: utf-8 -*-
# Contenuti del sito di Ceraldi Caffè. Modifica qui i testi, poi esegui build.py.
# Fatti sul bar: solo da fonti del bar (Instagram @ceraldicaffe, menu ceraldicaffe.qromo.it,
# scheda Google). Fatti storici negli articoli: verificati sulle fonti elencate in ogni articolo.

BASE = "https://valerioceraldi-hub.github.io/Ceraldi/caffe/"
OGGI = "2026-10-18"

BAR = {
    "nome": "Ceraldi Caffè",
    "dal": "1973",
    "motto": "Artigiani per passione dal 1973",
    "tagline": "Dalla colazione all'aperitivo, nel cuore di Napoli.",
    "indirizzo": "Piazza Carità, 14",
    "cap_citta": "80134 Napoli (NA)",
    "telefono": "081 552 3488",
    "tel_link": "+390815523488",
    "whatsapp": "https://wa.me/390815523488",
    "orari": "Tutti i giorni, 6:30 – 20:30",
    "orari_en": "Every day, 6:30 am – 8:30 pm",
    "mappa": "https://maps.google.com/?cid=3267263170235699466",
    "menu": "https://ceraldicaffe.qromo.it",
    "instagram": "https://www.instagram.com/ceraldicaffe/",
    "facebook": "https://www.facebook.com/ceraldicaffe",
    "descrizione_google": "Pasticcini artigianali, buffet freddi e aperitivi in un elegante bar con specchi e sedie di pelle rossa.",
}

# Specialità prese dal menu online del bar (senza prezzi: cambiano).
CAFFE_CASA = [
    ("Caffè Ceraldi", "Cioccolata calda sul fondo, crema di caffè e panna montata fresca."),
    ("Caffè Babà", "Crema di caffè, crema al babà, un babà mignon e panna fresca."),
    ("Michelino", "Espresso, crema di zucchero e panna sciolta a bagnomaria."),
    ("Nocciolato", "Espresso con crema di zucchero, pasta di nocciola Piemonte IGP e cacao."),
    ("Pistacchiotto", "Espresso con crema di pistacchio e granella tostata."),
    ("Caldo freddo", "Espresso, crema di zucchero e crema di latte montata a freddo."),
]
DOLCI_CASA = [
    ("Segreto amalfitano", "Babà bagnato al limoncello con cuore di chantilly ai limoni di Amalfi."),
    ("Cestino", "Il riccio della sfogliatella farcito con chantilly e frutti di bosco."),
    ("Babàmisù", "Cupola di babà con crema al mascarpone e caffè."),
    ("Pellecchiella", "Torta con albicocche Pellecchielle del Vesuvio, presidio Slow Food."),
    ("Torta di mele", "Con mela Annurca IGP, crema pasticcera e cannella."),
    ("Sfogliata Santa Rosa", "La sfogliatella con crema e amarene, come nella ricetta delle origini."),
]

CAFFE_CASA_EN = [
    ("Caffè Ceraldi", "Hot chocolate at the bottom, coffee cream and fresh whipped cream."),
    ("Caffè Babà", "Coffee cream, babà cream, a mini babà and fresh cream."),
    ("Michelino", "Espresso, sugar cream and gently warmed cream."),
    ("Nocciolato", "Espresso with sugar cream, Piedmont IGP hazelnut paste and cocoa."),
    ("Pistacchiotto", "Espresso with pistachio cream and toasted nuts."),
    ("Caldo freddo", "Espresso, sugar cream and cold-whipped milk cream."),
]
DOLCI_CASA_EN = [
    ("Segreto amalfitano", "Limoncello-soaked babà with an Amalfi lemon chantilly heart."),
    ("Cestino", "Sfogliatella pastry filled with chantilly cream and berries."),
    ("Babàmisù", "A babà dome filled with mascarpone and coffee cream."),
    ("Pellecchiella", "Cake with Vesuvius Pellecchiella apricots, a Slow Food presidium."),
    ("Torta di mele", "Annurca IGP apples, custard and cinnamon."),
    ("Sfogliata Santa Rosa", "Sfogliatella with custard and black cherries, like the original."),
]

# Crediti delle foto (Wikimedia Commons). Obbligatori per le licenze CC.
FOTO = {
    "sfogliatella-riccia": {"alt": "Sfogliatella riccia napoletana tagliata a metà, con il ripieno di ricotta e canditi",
        "autore": "Saggittarius A", "licenza": "CC BY-SA 4.0", "lic_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "fonte": "https://commons.wikimedia.org/wiki/File:Sfogliatella_riccia_napoletana.jpg"},
    "sfogliatella-frolla": {"alt": "Sfogliatella frolla napoletana con il ripieno in vista",
        "autore": "Saggittarius A", "licenza": "CC BY-SA 4.0", "lic_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "fonte": "https://commons.wikimedia.org/wiki/File:Sfogliatella_frolla_napoletana.jpg"},
    "baba": {"alt": "Babà al rum lucidi di sciroppo",
        "autore": "Marica Massaro", "licenza": "CC BY-SA 4.0", "lic_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "fonte": "https://commons.wikimedia.org/wiki/File:Bab%C3%A0_rum.jpg"},
    "pastiera": {"alt": "Pastiera napoletana intera con le strisce di pasta frolla incrociate",
        "autore": "Mattia Luigi Nappi", "licenza": "CC BY-SA 3.0", "lic_url": "https://creativecommons.org/licenses/by-sa/3.0/",
        "fonte": "https://commons.wikimedia.org/wiki/File:Pastiera_Napoletana.JPG"},
    "zeppole": {"alt": "Zeppola di San Giuseppe con crema e amarena",
        "autore": "Salvatore Capalbi", "licenza": "CC BY-SA 2.0", "lic_url": "https://creativecommons.org/licenses/by-sa/2.0/",
        "fonte": "https://commons.wikimedia.org/wiki/File:Zeppole,_popular_pastries_eaten_in_Naples_on_Saint_Joseph%27s_Day.jpg"},
}

# ── Articoli ──────────────────────────────────────────────────────────
# corpo: HTML semplice (p, h2, ul, blockquote). "provare": cosa assaggiare da Ceraldi.
ARTICOLI = [
{
 "slug": "caffe-napoletano",
 "titolo": "Il caffè napoletano: un rito, non una bevanda",
 "titolo_seo": "Il caffè napoletano: storia, rito e la cuccumella",
 "descrizione": "Tazzina calda, bicchiere d'acqua, la cuccumella e il cuppetiello: perché a Napoli il caffè è un rito che si ripete ogni giorno, al bar e a casa.",
 "dek": "Tazzina calda, un sorso d'acqua prima, due parole al bancone. Perché a Napoli il caffè si beve in un modo tutto suo.",
 "foto": None,
 "lettura": 4,
 "corpo": """
<p>A Napoli il caffè non si "prende": si fa una pausa. Dura pochi minuti, si ripete più volte al giorno e ha regole che nessuno ha mai scritto ma che tutti conoscono. Al bancone di un bar napoletano si capisce subito: si chiede il caffè, si scambiano due parole con il barista, si beve in piedi e si riparte.</p>

<h2>La tazzina calda e il bicchiere d'acqua</h2>
<p>La tazzina arriva calda, spesso appena tolta dall'acqua bollente o dalla piastra della macchina, perché il caffè non deve raffreddarsi a contatto con la porcellana. Accanto c'è quasi sempre un bicchiere d'acqua: si beve <em>prima</em>, per pulire il palato e sentire meglio l'aroma. Poi l'espresso, corto e denso, con la sua crema.</p>
<p>Lo zucchero è una scelta personale, ma molti bar lo aggiungono già nella tazzina o preparano la "cremina", lo zucchero montato con le prime gocce di caffè fino a diventare una spuma chiara. È la base di tante varianti che si trovano nei bar della città.</p>

<h2>La cuccumella, la caffettiera nata a Parigi</h2>
<p>Prima della moka, nelle case napoletane c'era la <strong>cuccumella</strong>, la caffettiera napoletana che si capovolge a metà preparazione. Curiosamente non è nata a Napoli: la inventò nel 1819 un lattoniere parigino, Jean-Louis Morize. Napoli però la adottò al punto da darle il proprio nome.</p>
<p>Il caffè della cuccumella scende lentamente, per gravità, e ci vuole pazienza. Per non perdere il profumo durante l'attesa si mette sul beccuccio il <strong>cuppetiello</strong>, un piccolo cono di carta arrotolato a mano: un gesto minimo che racconta quanto conti l'aroma.</p>

<h2>Eduardo e il caffè sul balcone</h2>
<p>Il ritratto più famoso di questo rito lo ha lasciato Eduardo De Filippo in <em>Questi fantasmi!</em>: il protagonista, affacciato al balcone, spiega al dirimpettaio come si prepara il caffè con la napoletana, cuppetiello compreso. È una scena comica e malinconica insieme, e ancora oggi è il modo in cui molti napoletani raccontano il caffè a chi non lo conosce.</p>

<h2>Il bar come piazza</h2>
<p>Il bar napoletano è un luogo di passaggio e di incontro: si entra per un caffè e si esce con una notizia, un saluto, un consiglio. È anche il posto dove nasce un'altra tradizione tutta napoletana, il <a href="../caffe-sospeso/">caffè sospeso</a>.</p>
""",
 "provare": [("Caffè Ceraldi", "cioccolata, crema di caffè e panna fresca"), ("Michelino", "espresso, crema di zucchero e panna"), ("Caldo freddo", "espresso e crema di latte montata a freddo")],
 "fonti": [("Reversible coffee pot (Wikipedia)", "https://en.wikipedia.org/wiki/Reversible_coffee_pot"),
           ("La cuccumella napoletana è nata a Parigi (Linkiesta)", "https://www.linkiesta.it/2020/07/cuccumella-napoletana-caffe-napoli-parigi/"),
           ("La caffettiera napoletana: la storia della cuccumella (Napolike)", "https://www.napolike.it/caffettiera-napoletana-storia-della-cuccumella")],
},
{
 "slug": "caffe-sospeso",
 "titolo": "Il caffè sospeso: un gesto napoletano che ha fatto il giro del mondo",
 "titolo_seo": "Caffè sospeso: cos'è e com'è nata la tradizione napoletana",
 "descrizione": "Pagare un caffè in più per chi verrà dopo: cos'è il caffè sospeso, da dove nasce e perché il 10 dicembre gli è dedicata una giornata.",
 "dek": "Si paga un caffè in più, per chi entrerà dopo e non potrà permetterselo. Un'abitudine piccola, nata nei bar di Napoli.",
 "foto": None,
 "lettura": 3,
 "corpo": """
<p>Il caffè sospeso è semplice: chi entra al bar paga due caffè e ne beve uno. L'altro resta "in sospeso", pagato e in attesa di qualcuno che entrerà più tardi e chiederà se c'è un sospeso. Nessuno sa chi l'ha offerto, nessuno deve ringraziare.</p>

<h2>Da dove nasce</h2>
<p>Le origini precise non sono documentate e i racconti sono diversi. Secondo una versione l'usanza si diffuse nel dopoguerra, quando molti non potevano permettersi nemmeno un caffè. Lo scrittore Riccardo Pazzaglia ne dava una lettura più leggera: amici che al bancone litigavano per pagare, e il caffè in più lasciato per il prossimo cliente.</p>
<p>A renderlo famoso fuori da Napoli è stato Luciano De Crescenzo, che nel libro <em>Il caffè sospeso</em> lo descrive come il gesto di chi è contento e vuole, in qualche modo, offrire un caffè al resto del mondo.</p>

<h2>Il 10 dicembre e il giro del mondo</h2>
<p>Il 10 dicembre si celebra la giornata del caffè sospeso, promossa da una rete di associazioni per diffondere l'usanza nei bar italiani. Nel frattempo l'idea è arrivata lontano: in altre città italiane e in vari paesi del mondo, dove ha preso nomi diversi, come il <em>café pendiente</em> in Argentina.</p>

<h2>Perché resiste</h2>
<p>Il caffè sospeso funziona perché è piccolo: costa poco, non chiede organizzazione e non mette in imbarazzo nessuno. È lo stesso spirito del bar napoletano, dove il caffè è prima di tutto un'occasione per stare in mezzo agli altri. Se vuoi capire meglio questo rito, leggi anche <a href="../caffe-napoletano/">come si beve il caffè a Napoli</a>.</p>
""",
 "provare": [("Espresso al bancone", "il modo più napoletano per cominciare"), ("Caffè Babà", "caffè e babà nella stessa tazza")],
 "fonti": [("Giornata del caffè sospeso (GreenMe)", "https://www.greenme.it/lifestyle/costume-e-societa/giornata-caffe-sospeso-tradiziona-napoletana-solidarieta/"),
           ("Caffè sospeso: la tradizione napoletana (Italy Segreta)", "https://italysegreta.com/it/caffe-sospeso-la-tradizione-napoletana-di-comprare-un-caffe-per-qualcuno-che-non-puo-permetterselo/")],
},
{
 "slug": "sfogliatella",
 "titolo": "Sfogliatella riccia e frolla: dal convento di Santa Rosa a via Toledo",
 "titolo_seo": "Sfogliatella napoletana: storia, riccia e frolla",
 "descrizione": "La storia della sfogliatella, nata in un convento della Costiera Amalfitana e arrivata a Napoli nel 1818: le differenze tra riccia, frolla e Santa Rosa.",
 "dek": "Nata in un convento della Costiera Amalfitana, arrivata a pochi passi da Piazza Carità all'inizio dell'Ottocento. Storia del dolce che scrocchia.",
 "foto": "sfogliatella-riccia",
 "lettura": 4,
 "corpo": """
<p>Basta un morso per riconoscerla: la sfogliatella riccia scrocchia, si sbriciola in mille lamelle dorate e lascia sulle dita lo zucchero a velo. Dentro, un ripieno morbido di ricotta, semola, uova, zucchero, canditi e cannella.</p>

<h2>Il convento di Santa Rosa</h2>
<p>La storia più raccontata porta a Conca dei Marini, sulla Costiera Amalfitana, nel monastero di Santa Rosa. Qui, nel Seicento, una suora avrebbe usato gli avanzi della cucina, semola cotta nel latte, ricotta e frutta secca, per creare un dolce nuovo, chiuso in una sfoglia a forma di cappuccio. Da quel convento prende il nome la <strong>Santa Rosa</strong>, la sfogliatella con crema pasticcera e amarene.</p>

<h2>Pintauro e via Toledo</h2>
<p>A portare la sfogliatella in città fu, intorno al 1818, Pasquale Pintauro, che aveva una bottega su via Toledo, a pochi passi da Piazza Carità. Pintauro la semplificò: tolse crema e amarene e lasciò il ripieno di ricotta che conosciamo oggi. Da lì la sfogliatella è diventata uno dei simboli della colazione napoletana.</p>

<h2>Riccia, frolla e Santa Rosa</h2>
<ul>
<li><strong>Riccia</strong>: la pasta è tirata sottilissima, arrotolata e tagliata a dischi che in forno si aprono in lamelle croccanti.</li>
<li><strong>Frolla</strong>: stesso ripieno, ma dentro un guscio liscio e morbido di pasta frolla. Più delicata, perfetta per chi non vuole briciole.</li>
<li><strong>Santa Rosa</strong>: la riccia con crema pasticcera e amarene, la più vicina alla ricetta del convento.</li>
</ul>

<h2>Come si mangia</h2>
<p>Calda, appena sfornata, con lo zucchero a velo che cade sul piattino. A Napoli si accompagna al caffè, al bancone, a qualsiasi ora del mattino. E chi ama la sfoglia può provare anche la <strong>coda d'aragosta</strong>, una sfogliatella allungata e farcita di crema.</p>
""",
 "provare": [("Sfogliatella riccia e frolla", "con ricotta, semola, canditi e cannella"), ("Sfogliata Santa Rosa", "crema e amarene"), ("Cestino", "il riccio della sfogliatella con chantilly e frutti di bosco"), ("Codina di aragosta", "con chantilly, cioccolato o pistacchio")],
 "fonti": [("Pasticceria Pintauro, la sfogliatella più antica della città (Dissapore)", "https://www.dissapore.com/ristoranti/pasticceria-pintauro-a-napoli-recensione-come-la-sfogliatella-piu-antica-della-citta"),
           ("The history and the origin of the sfogliatella (Gran Caffè Gambrinus)", "https://grancaffegambrinus.com/en/the-history-and-the-origin-of-the-sfogliatella/")],
},
{
 "slug": "baba",
 "titolo": "Il babà: il dolce di un re polacco diventato napoletano",
 "titolo_seo": "Babà napoletano: storia del dolce al rum",
 "descrizione": "Dalla Lorena di re Stanislao Leszczyński a Napoli: la storia del babà al rum, perché si chiama così e come si gusta oggi.",
 "dek": "Un re in esilio, un dolce troppo asciutto, un bagno di liquore. Il babà ha fatto un lungo viaggio prima di diventare napoletano.",
 "foto": "baba",
 "lettura": 4,
 "corpo": """
<p>Lucido, morbido, gonfio di sciroppo al rum. Il babà è uno dei dolci più napoletani che esistano, eppure è nato lontano, alla corte di un re senza regno.</p>

<h2>Il re Stanislao e il dolce troppo asciutto</h2>
<p>Stanislao Leszczyński, re di Polonia in esilio, viveva in Lorena, a Lunéville. La tradizione racconta che trovasse troppo asciutto il kugelhopf, il dolce lievitato tipico della zona, e che lo facesse bagnare nel liquore. Appassionato delle <em>Mille e una notte</em>, lo avrebbe chiamato "Alì Babà".</p>
<p>Il suo pasticcere, Nicolas Stohrer, seguì a Versailles la figlia del re, Maria, sposa di Luigi XV, e portò con sé la ricetta. A Parigi il dolce diventò il <em>baba au rhum</em>, bagnato nel rum.</p>

<h2>L'arrivo a Napoli</h2>
<p>A Napoli il babà arrivò tra la fine del Settecento e l'Ottocento, con i cuochi francesi delle grandi famiglie e della corte borbonica. I pasticceri napoletani gli diedero la forma a fungo che conosciamo, un impasto più soffice e una bagna generosa. Da dolce di corte diventò un dolce di strada, da mangiare in piedi al bar.</p>

<h2>"Sì nu babà"</h2>
<p>A Napoli dire a qualcuno "sì nu babà" è un complimento affettuoso: vuol dire che è dolce, buono, irresistibile. È il segno di quanto questo dolce sia entrato nel modo di parlare della città.</p>

<h2>Come si gusta</h2>
<p>Il babà classico è semplice, solo pasta e bagna. Ma si presta a mille varianti: con crema e amarene, con panna e fragole, con il cioccolato, o al limoncello, per un omaggio alla Costiera.</p>
""",
 "provare": [("Babà al rum", "classico, oppure con crema e amarene, panna e fragole o cioccolato"), ("Segreto amalfitano", "babà al limoncello con chantilly ai limoni di Amalfi"), ("Babàmisù", "cupola di babà con mascarpone e caffè"), ("Caffè Babà", "il babà anche nella tazza")],
 "fonti": [("Babà, storia e leggenda del dolce napoletano nato in Francia (Gambero Rosso)", "https://www.gamberorosso.it/notizie/storie/baba-storia-e-leggenda-del-dolce-napoletano-nato-in-francia"),
           ("Il babà: un dolce polacco diventato simbolo di Napoli (Napolike)", "https://www.napolike.it/il-baba-dolce-polacco-simbolo-di-napoli")],
},
{
 "slug": "pastiera",
 "titolo": "La pastiera napoletana: il profumo della Pasqua",
 "titolo_seo": "Pastiera napoletana: storia, leggende e ingredienti",
 "descrizione": "Grano, ricotta e fiori d'arancio: la storia e le leggende della pastiera napoletana, dalla sirena Partenope al convento di San Gregorio Armeno.",
 "dek": "Grano cotto, ricotta, fiori d'arancio. Nessun dolce racconta la primavera a Napoli come la pastiera, e nessuno ha tante leggende.",
 "foto": "pastiera",
 "lettura": 4,
 "corpo": """
<p>Quando nelle case e nelle pasticcerie di Napoli si sente il profumo dei fiori d'arancio, vuol dire che la Pasqua è vicina. La pastiera è il dolce della festa: pasta frolla, un ripieno di grano cotto, ricotta, uova, zucchero, canditi e spezie, e le strisce di frolla incrociate sopra.</p>

<h2>La leggenda di Partenope</h2>
<p>Si racconta che la sirena Partenope, che dà il nome antico a Napoli, uscisse dal mare ogni primavera per cantare alla gente del golfo. Per ringraziarla, sette fanciulle le portarono in dono farina, ricotta, uova, grano, acqua di fiori d'arancio, spezie e zucchero. La sirena li consegnò agli dei, che li mescolarono in un unico dolce: la pastiera.</p>
<p>Un'altra storia parla delle mogli dei pescatori, che lasciavano sulla spiaggia ceste di ricotta, grano e uova come offerta per il ritorno dei mariti. Al mattino le onde avevano mescolato tutto.</p>

<h2>Il convento di San Gregorio Armeno</h2>
<p>Più vicina alla storia è l'ipotesi che la ricetta moderna sia nata nei conventi del centro antico, in particolare in quello di San Gregorio Armeno, dove le suore preparavano le pastiere per le famiglie nobili nella settimana santa. Gli ingredienti hanno un significato: il grano e le uova per la rinascita, la ricotta per la primavera.</p>

<h2>La regina che non sorrideva</h2>
<p>Un aneddoto molto amato riguarda Maria Teresa d'Austria, moglie di re Ferdinando II di Borbone, chiamata "la regina che non sorride mai". Si dice che, convinta dal re ad assaggiare la pastiera, abbia finalmente sorriso.</p>

<h2>Un consiglio</h2>
<p>La pastiera dà il meglio di sé un giorno o due dopo la cottura, quando i profumi di grano, agrumi e fiori d'arancio si sono amalgamati. Per questo in molte famiglie si prepara qualche giorno prima di Pasqua.</p>
""",
 "provare": [("Pastiera napoletana", "con grano, canditi e fiori d'arancio"), ("Pellecchiella", "torta con albicocche del Vesuvio, presidio Slow Food")],
 "fonti": [("Storia e leggenda della pastiera napoletana (Gambero Rosso)", "https://www.gamberorosso.it/notizie/storie/storia-e-leggenda-della-pastiera-napoletana-con-la-ricetta-di-sal-de-riso/"),
           ("Pastiera napoletana: storia (Eroica Fenice)", "https://www.eroicafenice.com/napoli/food/pastiera-napoletana-storia-e-consigli-per-gli-acquisti/")],
},
{
 "slug": "zeppole-di-san-giuseppe",
 "titolo": "Zeppole di San Giuseppe: il dolce del 19 marzo",
 "titolo_seo": "Zeppole di San Giuseppe: storia e tradizione napoletana",
 "descrizione": "Crema pasticcera, amarena e zucchero a velo: la storia delle zeppole di San Giuseppe, dal ricettario di Ippolito Cavalcanti del 1837 alla festa del papà.",
 "dek": "Una corona di pasta, crema pasticcera e un'amarena al centro. A Napoli il 19 marzo si festeggia così.",
 "foto": "zeppole",
 "lettura": 3,
 "corpo": """
<p>Il 19 marzo è San Giuseppe, ed è anche la festa del papà. A Napoli è soprattutto il giorno delle zeppole: anelli di pasta, crema pasticcera, un'amarena sciroppata e una nuvola di zucchero a velo.</p>

<h2>Una ricetta del 1837</h2>
<p>La prima ricetta scritta della zeppola napoletana si trova nella <em>Cucina teorico-pratica</em> di Ippolito Cavalcanti, duca di Buonvicino, pubblicata nel 1837. All'epoca era un dolce fritto e semplice: farina, acqua, un liquore all'anice, vino e zucchero.</p>
<p>La tradizione attribuisce al pasticcere Pasquale Pintauro, lo stesso della <a href="../sfogliatella/">sfogliatella</a>, l'idea di arricchirla e di friggerla due volte. È un racconto più che un fatto documentato, ma dice molto di come i dolci napoletani siano cresciuti nelle botteghe del centro.</p>

<h2>San Giuseppe frittellaro</h2>
<p>Una leggenda popolare racconta che, durante la fuga in Egitto, San Giuseppe abbia venduto frittelle per mantenere la famiglia. Per questo a Napoli è anche il protettore di chi frigge, e il suo giorno si festeggia con un dolce fritto.</p>

<h2>Fritte o al forno</h2>
<p>La zeppola nasce fritta, ed è quella la versione più fedele alla tradizione. Oggi si trova anche al forno, più leggera. In entrambi i casi l'impasto è quello della pasta choux, che si gonfia e resta vuoto dentro, pronto per la crema.</p>
""",
 "provare": [("Zeppolina di San Giuseppe", "crema pasticcera e amarena"), ("Francesina crema e amarena", "pasta sfoglia, crema e amarene")],
 "fonti": [("Zeppole di San Giuseppe: storia e varianti regionali (Dissapore)", "https://www.dissapore.com/cucina/zeppole-di-san-giuseppe-storia-e-varianti-regionali-di-un-dolce-frittissimo/"),
           ("Festa di San Giuseppe, tempo di zeppole (La Voce di New York)", "https://lavocedinewyork.com/food/cucina-italiana/2019/03/17/festa-di-san-giuseppe-tempo-di-zeppole-storia-e-leggenda-di-una-tradizione-napoletana")],
},
]

FAQ = [
    ("Quali sono gli orari di Ceraldi Caffè?", "Siamo aperti tutti i giorni, domenica compresa, dalle 6:30 alle 20:30."),
    ("Dove si trova il bar?", "In Piazza Carità 14, nel centro di Napoli, tra via Toledo e il quartiere Pignasecca. Le stazioni Toledo e Dante della metropolitana Linea 1 sono a pochi minuti a piedi."),
    ("Posso vedere il menu prima di venire?", "Sì, il menu completo con caffè, dolci, cocktail e allergeni è online su ceraldicaffe.qromo.it."),
    ("Cosa si può mangiare?", "Colazione con la pasticceria napoletana (sfogliatelle, babà, pastiera, zeppole), torte, buffet freddi e, la sera, aperitivo con cocktail, birre e alcolici."),
    ("Come posso contattarvi?", "Al telefono o su WhatsApp allo 081 552 3488, oppure su Instagram @ceraldicaffe."),
]
FAQ_EN = [
    ("What are the opening hours?", "We are open every day, Sundays included, from 6:30 am to 8:30 pm."),
    ("Where is the café?", "At Piazza Carità 14 in central Naples, between Via Toledo and the Pignasecca market. Toledo and Dante stations on Metro Line 1 are a few minutes' walk away."),
    ("Can I see the menu online?", "Yes, the full menu with coffee, pastries, cocktails and allergens is online at ceraldicaffe.qromo.it."),
    ("What can I eat there?", "Breakfast with Neapolitan pastries (sfogliatella, babà, pastiera, zeppole), cakes, a cold buffet and, in the evening, aperitivo with cocktails, beer and spirits."),
]
