# -*- coding: utf-8 -*-
# Contenuti del sito di Ceraldi Caffè. Modifica qui i testi, poi esegui build.py.
# Fatti sul bar: da Ceraldi (logo, menu ceraldicaffe.qromo.it, Instagram, scheda Google).
# Foto: tutte di Ceraldi Caffè, prese dal menu online del bar.

BASE = "https://valerioceraldi-hub.github.io/Ceraldi/caffe/"
OGGI = "2026-10-18"
# Data in cui è stato scaricato l'attuale menu_grezzo.json (i file nuovi la contengono in "_scaricato")
MENU_SCARICATO = "2026-10-18"
# Firma e data di prima pubblicazione degli articoli (un articolo può avere "pubblicato" e "aggiornato" propri)
AUTORE = "Famiglia Ceraldi"
PUBBLICATO = "2026-10-18"
# Coordinate della scheda Google di Ceraldi Caffè (Google Places, place_id ChIJj5ui8loIOxMRCpGd6YqmVy0)
GEO = (40.8445035, 14.2488753)
# ID di misurazione di Google Analytics 4 (G-...). Vuoto = nessuno script di statistica e nessun banner.
GA_ID = ""

BAR = {
    "nome": "Ceraldi Caffè",
    "dal": "1973",
    "motto": "Artigiani per passione dal 1973",
    "tagline": "Dalla colazione all'aperitivo, nel cuore di Napoli.",
    "indirizzo": "Piazza Carità, 14",
    "cap_citta": "80134 Napoli (NA)",
    "telefono": "081 552 3488",
    "tel_link": "+390815523488",
    "cellulare": "328 438 8404",
    "cell_link": "+393284388404",
    "whatsapp": "https://wa.me/393284388404",  # WhatsApp è sul cellulare, non sul fisso
    "orari": "Tutti i giorni, 6:30 – 20:30",
    "orari_en": "Every day, 6:30 am – 8:30 pm",
    "mappa": "https://maps.google.com/?cid=3267263170235699466",
    "menu": "https://ceraldicaffe.qromo.it",
    "instagram": "https://www.instagram.com/ceraldicaffe/",
    "facebook": "https://www.facebook.com/ceraldicaffe",
    # Scheda Google con le recensioni (formato ufficiale Google Maps URLs; il vecchio search.google.com/local/reviews risponde 404)
    "google_recensioni": "https://www.google.com/maps/search/?api=1&query=Ceraldi%20Caff%C3%A8&query_place_id=ChIJj5ui8loIOxMRCpGd6YqmVy0",
    "google_scrivi": "https://search.google.com/local/writereview?placeid=ChIJj5ui8loIOxMRCpGd6YqmVy0",
    # Valutazione Google: dato scritto a mano, va aggiornato insieme alla data di rilevazione
    "google_voto": "4,3", "google_voto_en": "4.3", "google_n": "1.946", "google_n_en": "1,946", "google_data": "20/10/2026",
    # Gambero Rosso: edizione 2026 verificata online; presenza dal 2014 dichiarata dal titolare (21/10/2026)
    "gambero_dal": "2014",
    "gambero_rosso": "https://www.gamberorosso.it/luoghi/locali/caffe-bar/ceraldi-caffe/",
    "tripadvisor": "https://www.tripadvisor.it/Restaurant_Review-g187785-d2695184-Reviews-Ceraldi_Caffe-Naples_Province_of_Naples_Campania.html",
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
    ("Pellecchiella", "Torta con albicocche Pellecchielle del Vesuvio."),
    ("Torta di mele", "Con mela Annurca IGP, crema pasticcera e cannella."),
    ("Sfogliata Santa Rosa", "La sfogliatella con crema e amarene, come nella ricetta delle origini."),
]
COLAZIONE = [
    ("Croissant", "Vuoto, alla crema, crema e amarena, cioccolato, albicocca, lampone, mela e cannella, limone."),
    ("Croissant integrali e vegani", "Integrale vuoto, ai frutti di bosco, al miele; vegano vuoto."),
    ("Croissant ischitano", "Doppio strato di sfoglia e pasta brioche, con crema e amarena."),
    ("Brioche, kranz e pain au chocolat", "I classici della colazione all'italiana."),
    ("Graffa napoletana", "Fritta e zuccherata, morbida come vuole la tradizione."),
    ("Maritozzo e nuvoletta", "Brioche morbide ripiene di panna o di crema al latte."),
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
    ("Pellecchiella", "Cake with Pellecchiella apricots from Vesuvius."),
    ("Torta di mele", "Annurca IGP apples, custard and cinnamon."),
    ("Sfogliata Santa Rosa", "Sfogliatella with custard and black cherries, like the original."),
]
COLAZIONE_EN = [
    ("Croissants", "Plain, custard, custard and black cherry, chocolate, apricot, raspberry, apple and cinnamon, lemon."),
    ("Wholemeal and vegan croissants", "Plain wholemeal, berries, honey; plain vegan."),
    ("Ischia-style croissant", "Puff pastry and brioche dough in one, with custard and black cherry."),
    ("Brioche, kranz and pain au chocolat", "The classics of an Italian breakfast."),
    ("Graffa napoletana", "Neapolitan fried sugar doughnut, soft and fragrant."),
    ("Maritozzo and nuvoletta", "Soft buns filled with whipped cream or milk custard."),
]

# Foto di Ceraldi Caffè (dal menu online). larghezze disponibili, proporzioni.
FOTO = {
    "sfogliatella-riccia": {"alt": "Sfogliatelle ricce di Ceraldi Caffè su un piattino", "w": [1024, 640], "r": (4, 3)},
    "sfogliatella-frolla": {"alt": "Sfogliatella frolla di Ceraldi Caffè aperta, con il ripieno di ricotta", "w": [1024, 640], "r": (4, 3)},
    "baba": {"alt": "Babà al rum di Ceraldi Caffè sul bancone", "w": [1024, 640], "r": (4, 3)},
    "baba-amarena": {"alt": "Babà con crema e amarena di Ceraldi Caffè", "w": [1024, 640], "r": (4, 3)},
    "pastiera": {"alt": "Fetta di pastiera napoletana di Ceraldi Caffè spolverata di zucchero a velo", "w": [1016, 640], "r": (4, 3)},
    "zeppola": {"alt": "Zeppola di San Giuseppe di Ceraldi Caffè con crema e amarena", "w": [1024, 640], "r": (4, 3)},
    "cestino": {"alt": "Il Cestino di Ceraldi Caffè: riccio di sfogliatella con chantilly e frutti di bosco", "w": [768, 480], "r": (3, 4)},
    "babamisu": {"alt": "Babàmisù di Ceraldi Caffè", "w": [800, 480], "r": (1, 1)},
    "pellecchiella": {"alt": "Torta Pellecchiella di Ceraldi Caffè con albicocche del Vesuvio", "w": [800, 480], "r": (1, 1)},
    "squadra": {"alt": "La squadra di Ceraldi Caffè al bancone del bar in Piazza Carità", "w": [1600, 800], "r": (3, 2)},
    "sala": {"alt": "La sala di Ceraldi Caffè con le poltroncine in pelle rossa e una colazione servita al tavolo", "w": [1024, 640], "r": (3, 2)},
    "bar-banco": {"alt": "Il banco del bar di Ceraldi Caffè con il barista al lavoro", "w": [1024, 640], "r": (3, 2)},
    "vetrina": {"alt": "La vetrina della pasticceria e della rosticceria di Ceraldi Caffè", "w": [1024, 640], "r": (3, 2)},
    "sala-bianca": {"alt": "La sala bianca e oro di Ceraldi Caffè con i tavolini e le poltroncine rosse", "w": [1024, 640], "r": (3, 2)},
    "famiglia": {"alt": "La famiglia Ceraldi seduta a un tavolo nella sala del bar", "w": [1024, 640], "r": (3, 2)},
    "crostatina": {"alt": "Crostatina di fragole di Ceraldi Caffè su un piatto", "w": [1024, 640], "r": (3, 2)},
    "caffe-servito-bancone": {"alt": "Il barman di Ceraldi Caffè serve un caffè con panna al bancone", "w": [1024, 640], "r": (3, 2)},
    "cornetti-caffe-bancone": {"alt": "Cornetti e caffè serviti sul bancone di marmo di Ceraldi Caffè", "w": [1024, 640], "r": (3, 2)},
    "latte-macchiato-dolci": {"alt": "Latte macchiato e alzatina di dolci al bancone di Ceraldi Caffè", "w": [1024, 640], "r": (3, 2)},
    "baba-al-rum-classico": {"alt": "Babà al rum classico di Ceraldi Caffè, accanto a una tazzina di caffè", "w": [1024, 640], "r": (3, 2)},
    "zeppolina-san-giuseppe": {"alt": "Zeppolina di San Giuseppe di Ceraldi Caffè con crema e amarena", "w": [1024, 640], "r": (3, 2)},
    "cocktail-menta-cetriolo": {"alt": "Il barman di Ceraldi Caffè versa lo spumante in un cocktail con menta e cetriolo", "w": [1024, 640], "r": (3, 2)},
    "cocktail-frutti-rossi": {"alt": "Cocktail rosso ai frutti di bosco al bancone di Ceraldi Caffè", "w": [1024, 640], "r": (3, 2)},
    "cocktail-barman": {"alt": "Il barman di Ceraldi Caffè guarnisce un cocktail al bancone", "w": [1024, 640], "r": (3, 2)},
    "logo-ceraldi-caffe-carta": {"alt": "Il logo di Ceraldi Caffè, Artigiani per passione dal 1973, stampato su carta", "w": [1024, 640], "r": (3, 2)},
    "sala-ingresso-piazza-carita": {"alt": "L'interno di Ceraldi Caffè in Piazza Carità, con la sala e le poltroncine rosse", "w": [1024, 640], "r": (3, 2)},
    "aperitivo": {"alt": "Aperitivo da Ceraldi Caffè: spritz e cocktail al tavolo", "w": [960, 640], "r": (4, 3)},
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
 "foto": "sala",
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
},
{
 "slug": "caffe-sospeso",
 "titolo": "Il caffè sospeso: un gesto napoletano che ha fatto il giro del mondo",
 "titolo_seo": "Caffè sospeso: cos'è e come è nato",
 "descrizione": "Pagare un caffè in più per chi verrà dopo: cos'è il caffè sospeso, da dove nasce e perché il 10 dicembre gli è dedicata una giornata.",
 "dek": "Si paga un caffè in più, per chi entrerà dopo e non potrà permetterselo. Un'abitudine piccola, nata nei bar di Napoli.",
 "foto": "squadra",
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
},
{
 "slug": "pastiera",
 "titolo": "La pastiera napoletana: il profumo della Pasqua",
 "titolo_seo": "Pastiera napoletana: storia e leggende",
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
 "provare": [("Pastiera napoletana", "con grano, canditi e fiori d'arancio"), ("Pellecchiella", "torta con albicocche Pellecchielle del Vesuvio")],
},
{
 "slug": "zeppole-di-san-giuseppe",
 "titolo": "Zeppole di San Giuseppe: il dolce del 19 marzo",
 "titolo_seo": "Zeppole di San Giuseppe: storia e tradizione",
 "descrizione": "Crema pasticcera, amarena e zucchero a velo: la storia delle zeppole di San Giuseppe, dal ricettario di Ippolito Cavalcanti del 1837 alla festa del papà.",
 "dek": "Una corona di pasta, crema pasticcera e un'amarena al centro. A Napoli il 19 marzo si festeggia così.",
 "foto": "zeppola",
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
},
]

ARTICOLI += [
{
 "slug": "colazione-napoletana",
 "titolo": "La colazione a Napoli: cornetto, sfogliatella o graffa?",
 "titolo_seo": "Colazione a Napoli: cornetto e sfogliatella",
 "descrizione": "Come si fa colazione a Napoli: cornetto e cappuccino al bancone, sfogliatella, graffa e caffè. E le differenze tra cornetto, brioche e croissant.",
 "dek": "In piedi al bancone, in pochi minuti, con il profumo del forno. Guida alla colazione napoletana, tra classici italiani e dolci della città.",
 "foto": "sfogliatella-frolla",
 "lettura": 4,
 "corpo": """
<p>In Italia la colazione al bar è un piccolo rito quotidiano: un cappuccino o un caffè, un cornetto caldo, due parole con il barista. A Napoli questo rito si arricchisce dei dolci della città, e la scelta al bancone diventa più difficile.</p>

<h2>La colazione all'italiana</h2>
<p>La colazione all'italiana è dolce e veloce. Al centro c'è il <strong>cornetto</strong>, vuoto o farcito con crema, cioccolato o marmellata, accompagnato da un cappuccino, un caffè o una spremuta. Accanto ci sono la <strong>brioche</strong>, più soffice e ricca di uova, e i lievitati sfogliati come il pain au chocolat e il kranz.</p>

<h2>Cornetto, brioche o croissant?</h2>
<p>Le parole cambiano da una regione all'altra. Al Nord molti chiamano "brioche" quello che al Centro e al Sud è il cornetto. Cornetto e croissant hanno un antenato comune, il <em>kipferl</em> viennese, ma sono diversi: il croissant francese non ha uova e ha più burro, il cornetto italiano ha un impasto arricchito con uova e burro, più morbido e profumato.</p>
<p>Una leggenda racconta che il kipferl sia nato a Vienna nel 1683, per festeggiare la fine dell'assedio ottomano, con la forma della mezzaluna. È una bella storia, ma il kipferl è documentato già secoli prima.</p>

<h2>La colazione napoletana</h2>
<p>A Napoli al cornetto si affiancano i dolci della tradizione: la <a href="../sfogliatella/">sfogliatella</a> riccia o frolla, appena sfornata; la <strong>graffa</strong>, una ciambella fritta e zuccherata dall'impasto morbido; il <a href="../baba/">babà</a> per chi ama i sapori decisi fin dal mattino. E naturalmente il caffè, corto e denso, servito nella tazzina calda.</p>

<h2>Come ordinare al bancone</h2>
<ul>
<li>Si ordina e si paga, spesso prima alla cassa e poi al banco.</li>
<li>Il cappuccino è una bevanda del mattino: dopo pranzo si passa al caffè.</li>
<li>Se c'è fila, si beve in piedi e si lascia il posto: la colazione al bar è rapida per definizione.</li>
</ul>
""",
 "provare": [("Croissant", "vuoto, crema, crema e amarena, cioccolato, albicocca, integrali e vegani"), ("Graffa napoletana", "fritta e zuccherata"), ("Sfogliatella riccia e frolla", "calda, con il caffè"), ("Maritozzo", "brioche ripiena di panna")],
},
{
 "slug": "dolci-dei-conventi",
 "titolo": "I dolci nati nei conventi di Napoli",
 "titolo_seo": "Dolci dei conventi napoletani: storia e leggende",
 "descrizione": "Sfogliatella, pastiera, roccocò, susamielli, raffioli: molti dolci napoletani sono nati nei conventi della città e della costiera. Ecco la loro storia.",
 "dek": "Dietro molti dolci napoletani ci sono le cucine dei monasteri. Un viaggio tra suore pasticcere, ricette segrete e festività.",
 "foto": "sfogliatella-riccia",
 "lettura": 4,
 "corpo": """
<p>Per secoli i conventi sono stati tra i più grandi laboratori di pasticceria di Napoli. Le monache avevano tempo, ingredienti preziosi come zucchero, mandorle e spezie, e ricette custodite all'interno delle mura. Molti dei dolci che oggi troviamo nelle pasticcerie vengono da lì.</p>

<h2>La sfogliatella di Santa Rosa</h2>
<p>La storia più famosa è quella della <a href="../sfogliatella/">sfogliatella</a>, che la tradizione fa nascere nel Seicento nel monastero di Santa Rosa a Conca dei Marini, sulla Costiera Amalfitana. Da lì arrivò a Napoli all'inizio dell'Ottocento.</p>

<h2>La pastiera di San Gregorio Armeno</h2>
<p>Per la <a href="../pastiera/">pastiera</a> si indica spesso il convento di San Gregorio Armeno, nel centro antico. Le monache la preparavano nella settimana santa per le famiglie nobili. Allo stesso convento si attribuiscono altri dolci, come il <strong>divino amore</strong>, a base di pasta di mandorle e canditi, e i <strong>raffioli</strong>, dischi di pan di Spagna con marmellata di albicocche e glassa bianca.</p>

<h2>I dolci di Natale delle monache</h2>
<p>I <strong>roccocò</strong>, ciambelle dure con mandorle, scorza d'arancia e pisto, sono legati alle monache del Real Convento della Maddalena, e la loro storia viene fatta risalire al Trecento. I <strong>susamielli</strong>, biscotti al miele coperti di sesamo, vengono associati alle clarisse. Sono i dolci che ancora oggi annunciano il <a href="../dolci-di-natale/">Natale a Napoli</a>.</p>

<h2>Perché proprio i conventi</h2>
<p>Lo zucchero e le spezie erano costosi, e i monasteri erano tra i pochi luoghi in grado di permetterseli. I dolci servivano anche come doni per benefattori e famiglie nobili, e a volte come fonte di guadagno. Così le ricette passarono, nel tempo, dalle cucine delle suore alle botteghe dei pasticceri.</p>
""",
 "provare": [("Sfogliatella riccia e frolla", "la più famosa delle ricette conventuali"), ("Pastiera napoletana", "grano, ricotta e fiori d'arancio"), ("Sfogliata Santa Rosa", "crema e amarene")],
},
{
 "slug": "dolci-di-natale",
 "titolo": "I dolci di Natale a Napoli: struffoli, roccocò e mostaccioli",
 "titolo_seo": "Dolci di Natale napoletani: struffoli e roccocò",
 "descrizione": "Struffoli, roccocò, mostaccioli, susamielli, raffioli e divino amore: i dolci del Natale napoletano, i loro ingredienti e la loro storia.",
 "dek": "Miele, mandorle, pisto e diavulilli colorati. A Napoli il Natale si riconosce prima di tutto dai dolci.",
 "foto": None,
 "lettura": 4,
 "corpo": """
<p>Il Natale a Napoli ha un profumo preciso: miele caldo, mandorle tostate, scorza d'arancia e <strong>pisto</strong>, la miscela di spezie (cannella, chiodi di garofano, noce moscata e altre) che entra in quasi tutti i dolci delle feste.</p>

<h2>Struffoli</h2>
<p>Piccole palline di pasta fritte, raccolte con il miele e decorate con canditi e confettini colorati, i <em>diavulilli</em>. Gli struffoli si preparano in grandi quantità, si regalano e restano in tavola per giorni. Somigliano a dolci di altre tradizioni mediterranee, come i <em>loukoumades</em> greci.</p>

<h2>Roccocò</h2>
<p>Ciambelle dure e croccanti con mandorle, scorza d'arancia e pisto. La tradizione li fa risalire al Trecento e alle monache del Real Convento della Maddalena. Sono duri per natura: molti li ammorbidiscono nel vino, come il marsala.</p>

<h2>Mostaccioli</h2>
<p>Biscotti morbidi al miele e spezie, ricoperti di cioccolato. In origine l'impasto conteneva il mosto d'uva, da cui viene il nome.</p>

<h2>Susamielli, raffioli e divino amore</h2>
<ul>
<li><strong>Susamielli</strong>: biscotti a forma di S con miele, mandorle e pisto, coperti di sesamo.</li>
<li><strong>Raffioli</strong>: dischi di pan di Spagna con marmellata di albicocche e glassa bianca.</li>
<li><strong>Divino amore</strong>: pasta di mandorle con canditi e marmellata, sotto una glassa rosa.</li>
</ul>

<h2>Il Natale nei bar</h2>
<p>Durante le feste i dolci natalizi entrano anche nei bar, accanto al caffè. E la <a href="../pastiera/">pastiera</a>, dolce di Pasqua per eccellenza, a Napoli si trova sempre più spesso anche a Natale.</p>
""",
 "provare": [("Pastiera napoletana", "a Napoli ormai si mangia anche a Natale"), ("Biscotto all'amarena", "dolce tradizionale napoletano di pasta frolla")],
},
{
 "slug": "piazza-carita-via-toledo",
 "titolo": "Piazza Carità e via Toledo: una passeggiata nel cuore di Napoli",
 "titolo_seo": "Piazza Carità e via Toledo: storia e cosa vedere",
 "descrizione": "Piazza Carità e via Toledo, aperta nel 1536 dal viceré Pedro de Toledo: storia, il monumento a Salvo D'Acquisto, la Pignasecca e i Quartieri Spagnoli.",
 "dek": "La piazza dove si trova Ceraldi Caffè ha cambiato nome e monumenti più volte. Ecco la sua storia e cosa c'è intorno.",
 "foto": "sala-bianca",
 "lettura": 4,
 "corpo": """
<p>Piazza Carità si apre lungo via Toledo, a metà strada tra piazza Dante e piazza del Plebiscito. È uno snodo della Napoli di tutti i giorni: da qui si sale verso la Pignasecca e i Quartieri Spagnoli, si scende verso il porto, si attraversa il centro a piedi.</p>

<h2>Via Toledo, dal 1536</h2>
<p>Via Toledo fu aperta nel 1536 per volere del viceré spagnolo Pedro de Toledo, da cui prende il nome. È lunga quasi un chilometro e duecento metri ed è una delle strade dello shopping più frequentate d'Italia. Dal 1870 al 1980 si chiamò ufficialmente via Roma, ma per i napoletani è sempre rimasta "Toledo".</p>

<h2>Una piazza dai molti nomi</h2>
<p>La piazza nacque insieme a via Toledo e per secoli ospitò un mercato molto animato. Nel Cinquecento vi fu costruita la chiesa di Santa Maria della Carità, che le ha dato il nome con cui tutti la conoscono. Nel tempo è stata chiamata largo della Carità, piazza Carlo Poerio e piazza Costanzo Ciano.</p>
<p>Anche i monumenti sono cambiati: nel 1887 vi fu collocata la statua di Carlo Poerio, trasferita nel 1939 a piazza San Pasquale a Chiaia. Dal 1971 al centro della piazza c'è il monumento a <strong>Salvo D'Acquisto</strong>, il vicebrigadiere dei carabinieri eroe nazionale.</p>

<h2>Cosa c'è intorno</h2>
<ul>
<li><strong>La Pignasecca</strong>: il mercato storico, con banchi di frutta, pesce e friggitorie.</li>
<li><strong>I Quartieri Spagnoli</strong>: i vicoli nati per alloggiare le truppe spagnole, oggi tra le zone più vive della città.</li>
<li><strong>La stazione Toledo</strong> della metropolitana Linea 1, aperta nel 2012 e famosa per le sue decorazioni.</li>
<li><strong>Piazza Dante</strong> e, verso il mare, la Galleria Umberto I e piazza del Plebiscito.</li>
</ul>
<p>In mezzo a tutto questo, dal 2002, c'è Ceraldi Caffè, la cui storia era cominciata nel 1973 in Piazza Garibaldi: un caffè al bancone è il modo più napoletano per cominciare la passeggiata.</p>
""",
 "provare": [("Espresso al bancone", "prima di partire per via Toledo"), ("Sfogliatella riccia", "da mangiare calda, anche passeggiando")],
},
{
 "slug": "a-tazza-e-cafe",
 "titolo": "'A tazza 'e cafè: il caffè nella canzone e nel teatro napoletano",
 "titolo_seo": "'A tazza 'e cafè: la canzone del 1918 e il caffè",
 "descrizione": "'A tazza 'e cafè, la canzone del 1918 di Capaldo e Fassone, e il caffè nella cultura di Napoli, da Eduardo De Filippo a Luciano De Crescenzo.",
 "dek": "Una cassiera che non sorrideva mai, un poeta innamorato e una canzone del 1918 che paragona l'amore a una tazza di caffè.",
 "foto": "bar-banco",
 "lettura": 3,
 "corpo": """
<p>A Napoli il caffè non è solo una bevanda: è entrato nelle canzoni, nel teatro e nei libri. Ed è uno dei modi in cui la città racconta sé stessa.</p>

<h2>La storia di 'A tazza 'e cafè</h2>
<p><em>'A tazza 'e cafè</em> è una canzone del 1918, con il testo di Giuseppe Capaldo e la musica di Vittorio Fassone. La portò al successo Elvira Donnarumma, una delle voci più amate dell'epoca.</p>
<p>Dietro la canzone c'è una storia vera. Capaldo era innamorato di Brigida, la cassiera di un caffè del centro, che respingeva tutti i corteggiatori, lui compreso. Così le dedicò una canzone in cui la paragona a una tazza di caffè: amara in superficie, ma con lo zucchero sul fondo. Basta girare il cucchiaino, con pazienza, per trovare la dolcezza.</p>
<p>Nel corso del Novecento l'hanno cantata, tra gli altri, Roberto Murolo, Claudio Villa, Milva, Gabriella Ferri e l'Orchestra Italiana di Renzo Arbore.</p>

<h2>Il caffè di Eduardo</h2>
<p>Il teatro napoletano ha regalato al caffè la sua scena più celebre: in <em>Questi fantasmi!</em> di Eduardo De Filippo il protagonista, affacciato al balcone, spiega come si prepara il caffè con la <a href="../caffe-napoletano/">cuccumella</a>, cuppetiello compreso.</p>

<h2>Il caffè di De Crescenzo</h2>
<p>Luciano De Crescenzo ha raccontato il <a href="../caffe-sospeso/">caffè sospeso</a> come il gesto di chi, essendo felice, offre un caffè al resto del mondo. Una frase che ha fatto conoscere l'usanza ben oltre Napoli.</p>
""",
 "provare": [("Caffè Ceraldi", "la nostra tazza più dolce"), ("Michelino", "espresso, crema di zucchero e panna")],
},
{
 "slug": "festa-della-mamma",
 "titolo": "Festa della mamma: fragole, cioccolato e dolci fatti col cuore",
 "titolo_seo": "Festa della mamma: dolci con fragole e cioccolato",
 "descrizione": "Per la festa della mamma, la seconda domenica di maggio, i dolci che non sbagliano mai: fragole e cioccolato, crostata, macarons, biscotti e torta di rose.",
 "dek": "Non esiste un dolce ufficiale per la festa della mamma. Ma qualche abbinamento che non sbaglia mai c'è.",
 "foto": "crostatina",
 "lettura": 3,
 "pubblicato": "2019-05-09",
 "aggiornato": "2026-10-20",
 "corpo": """
<p>La mamma non è una persona come tutte le altre. È pronta a correre in aiuto in ogni momento, telefona sempre (anche quando il figlio è ormai cresciuto), mette da parte l'ultima fetta di torta e prepara in anticipo il piatto preferito. Insomma, sulla mamma si può sempre contare.</p>
<p>Esistono tanti modi per dirle grazie nel giorno della sua festa, che in Italia cade la seconda domenica di maggio. Uno è preparare insieme a lei un dolce speciale, senza dimenticare l'ingrediente più importante: l'amore.</p>

<h2>Il dolce ufficiale non esiste</h2>
<p>A Natale il simbolo è il panettone, a Pasqua la colomba (e a Napoli la <a href="../pastiera/">pastiera</a>). Per la festa della mamma non c'è un dolce prestabilito: contano la cura e il gesto, più della ricetta. Ci sono però alcune preparazioni che per tradizione tornano ogni anno.</p>

<h2>Fragole e cioccolato</h2>
<p>A maggio le fragole sono di stagione, e l'accoppiata con il cioccolato mette d'accordo quasi tutti i palati, anche quelli delle mamme più severe. Bastano due ingredienti per ricette facili e veloci, come un tiramisù veloce o la classica crostata di fragole.</p>
<p>Per personalizzare la crostata si può tagliare la pasta frolla a forma di cuoricini, oppure ricoprire la superficie con delle formine e aggiungere uno strato di crema al cioccolato.</p>

<h2>Piccole dolcezze</h2>
<p>Altri classici da preparare per l'occasione sono i macarons in tutte le loro sfumature: quelli alla nocciola sono perfetti da servire con un tè caldo, chiacchierando. Per dei biscotti più semplici basta una frolla al burro e qualche stampino per decorarli con la forma che si preferisce.</p>

<h2>Rose, rose e rose</h2>
<p>Per la mamma romantica, il dolce giusto è la classica torta di rose oppure un fresco dessert con more e confettura di rose. Con i più piccoli in cucina, si possono fare le eleganti rose di sfoglia.</p>

<p>Se invece vuoi farle trovare qualcosa di già pronto, passa a trovarci: in vetrina ci sono la crostatina di fragole, i babà e le torte della casa, tutti di <a href="../../pasticceria/">produzione propria</a>. Auguri a tutte le mamme!</p>
""",
 "provare": [("Crostatina di fragole", "frolla, crema e fragole fresche"), ("Babà panna e fragole", "il babà con panna e fragole")],
},
{
 "slug": "tradizioni-napoletane",
 "titolo": "Napoli in sette tradizioni: dal panaro al miracolo di San Gennaro",
 "titolo_seo": "Tradizioni napoletane: panaro, smorfia e presepe",
 "descrizione": "Sette tradizioni napoletane: caffè sospeso, panaro, cornicello, smorfia, presepe di San Gregorio Armeno, miracolo di San Gennaro e dolci delle feste.",
 "dek": "Piccoli gesti, credenze e feste che raccontano Napoli meglio di qualsiasi guida.",
 "foto": "zeppolina-san-giuseppe",
 "lettura": 4,
 "corpo": """
<p>Napoli è una città di tradizioni vive, che si vedono per strada ogni giorno. Eccone sette, dalle più quotidiane alle più solenni.</p>

<h2>Il caffè sospeso</h2>
<p>Si paga un caffè in più per chi entrerà dopo e non potrà permetterselo. Un gesto piccolo, nato nei bar della città, che ha fatto il giro del mondo. Ne parliamo nell'articolo sul <a href="../caffe-sospeso/">caffè sospeso</a>.</p>

<h2>Il panaro</h2>
<p>Il <em>panaro</em> è il cesto che si cala dal balcone con una corda, per ricevere la spesa, il pane o un pacco senza scendere le scale. Nei vicoli si vede ancora oggi.</p>

<h2>Il cornicello</h2>
<p>Il corno rosso è il portafortuna napoletano per eccellenza. Secondo la tradizione deve essere regalato, non comprato per sé, per proteggere davvero dalla sfortuna.</p>

<h2>La smorfia</h2>
<p>La smorfia napoletana associa a ogni numero da 1 a 90 un significato: si usa per "tradurre" i sogni e gli avvenimenti in numeri da giocare al lotto e alla tombola.</p>

<h2>Il presepe di San Gregorio Armeno</h2>
<p>Nel centro antico, via San Gregorio Armeno è la strada degli artigiani del presepe. Tutto l'anno, e soprattutto a Natale, le botteghe espongono pastori, case e scene di vita napoletana fatte a mano.</p>

<h2>Il miracolo di San Gennaro</h2>
<p>Tre volte l'anno, a Napoli si attende lo scioglimento del sangue di San Gennaro, il patrono della città: il sabato prima della prima domenica di maggio, il 19 settembre, giorno della festa, e il 16 dicembre, in ricordo dell'eruzione del Vesuvio del 1631.</p>

<h2>I dolci delle feste</h2>
<p>Ogni festa ha il suo dolce: le <a href="../zeppole-di-san-giuseppe/">zeppole</a> il 19 marzo, la <a href="../pastiera/">pastiera</a> a Pasqua, gli <a href="../dolci-di-natale/">struffoli e i roccocò</a> a Natale. Il calendario napoletano si può seguire anche dalla vetrina di una pasticceria.</p>
""",
 "provare": [("Zeppolina di San Giuseppe", "il dolce del 19 marzo"), ("Pastiera napoletana", "il dolce di Pasqua"), ("Un caffè sospeso", "il gesto più napoletano")],
},
]

FAQ = [
    ("Quali sono gli orari di Ceraldi Caffè?", "Siamo aperti tutti i giorni, domenica compresa, dalle 6:30 alle 20:30.", None),
    ("Dove si trova il bar?", "In Piazza Carità 14, nel centro di Napoli, lungo via Toledo e vicino alla Pignasecca. Le stazioni Toledo e Dante della metropolitana Linea 1 sono a pochi minuti a piedi.", None),
    ("Posso vedere il menu prima di venire?", "Sì, il menu completo con prezzi è sul sito: " + BASE + "menu/ e c'è anche il menu interattivo con filtro allergeni: https://ceraldicaffe.qromo.it",
     'Sì, il menu completo con prezzi è qui sul sito: <a href="' + BASE + 'menu/">apri il menu di Ceraldi Caffè</a>. C\'è anche il <a href="https://ceraldicaffe.qromo.it" rel="noopener">menu interattivo</a> con filtro allergeni.'),
    ("I dolci sono fatti da voi?", "Sì. La pasticceria è di produzione propria, con ricette di famiglia tramandate di generazione in generazione: sfogliatelle, babà, pastiera, zeppole e le creazioni della casa.", None),
    ("Cosa posso mangiare a colazione?", "La classica colazione all'italiana con croissant (vuoti, alla crema, al cioccolato, integrali, vegani), brioche, kranz e pain au chocolat, insieme ai dolci napoletani come sfogliatella, graffa e babà.", None),
    ("Fate anche l'aperitivo?", "Sì, fino alle 20:30, con il nostro Aspritz fatto in casa, spritz, negroni, gin tonic, vini campani al calice e birre.", None),
    ("Si può pranzare?", "Sì, con la rosticceria napoletana (frittatine, crocchè, pizza fritta), saltimbocca e panini, freselle e insalate.", None),
    ("Servite la colazione inglese?", "Sì, tutte le mattine serviamo la Full English Breakfast: uova, bacon, salsicce, fagioli, funghi, pomodori, pane tostato e tè.", None),
    ("Come posso contattarvi?", "Al telefono fisso 081 552 3488, al cellulare 328 438 8404 (anche WhatsApp) oppure su Instagram @ceraldicaffe.", None),
    ("Dove posso leggere le recensioni?", "Su Google e su Tripadvisor, dove trovi le recensioni dei nostri clienti.",
     'Su <a href="https://www.google.com/maps/search/?api=1&amp;query=Ceraldi%20Caff%C3%A8&amp;query_place_id=ChIJj5ui8loIOxMRCpGd6YqmVy0" rel="noopener">Google</a> e su <a href="https://www.tripadvisor.it/Restaurant_Review-g187785-d2695184-Reviews-Ceraldi_Caffe-Naples_Province_of_Naples_Campania.html" rel="noopener">Tripadvisor</a>, dove trovi le recensioni dei nostri clienti.'),
]
FAQ_EN = [
    ("What are the opening hours?", "We are open every day, Sundays included, from 6:30 am to 8:30 pm.", None),
    ("Where is the café?", "At Piazza Carità 14 in central Naples, on Via Toledo near the Pignasecca market. Toledo and Dante stations on Metro Line 1 are a few minutes' walk away.", None),
    ("Can I see the menu online?", "Yes, the full menu with prices is on our website: " + BASE + "en/menu/ and there is also an interactive menu with an allergen filter: https://ceraldicaffe.qromo.it",
     'Yes: <a href="' + BASE + 'en/menu/">see the full menu with prices</a>, or the <a href="https://ceraldicaffe.qromo.it" rel="noopener">interactive menu</a>, available in English with an allergen filter.'),
    ("Do you make your own pastries?", "Yes. Our pastries are made in-house from family recipes handed down through the generations.", None),
    ("What can I have for breakfast?", "A classic Italian breakfast with croissants, brioche, kranz and pain au chocolat, plus Neapolitan pastries such as sfogliatella, graffa and babà.", None),
    ("Do you serve an English breakfast?", "Yes, every morning: eggs, bacon, sausages, beans, mushrooms, tomatoes, toast and tea.", None),
    ("How can I contact you?", "Call +39 081 552 3488, or mobile +39 328 438 8404 (also WhatsApp), or find us on Instagram @ceraldicaffe.", None),
]


# ── Fonti degli articoli (solo fonti autorevoli, nessun concorrente) ──
_W = "https://it.wikipedia.org/wiki/"
FONTI = {
 "caffe-napoletano": [("Caffettiera napoletana, Wikipedia", _W + "Caffettiera_napoletana"), ("Questi fantasmi!, Wikipedia", _W + "Questi_fantasmi%21"),
                      ("La cuccumella napoletana è nata a Parigi, Linkiesta", "https://www.linkiesta.it/2020/07/cuccumella-napoletana-caffe-napoli-parigi/")],
 "caffe-sospeso": [("Caffè sospeso, Wikipedia", _W + "Caff%C3%A8_sospeso"),
                   ("Giornata del caffè sospeso, GreenMe", "https://www.greenme.it/lifestyle/costume-e-societa/giornata-caffe-sospeso-tradiziona-napoletana-solidarieta/")],
 "sfogliatella": [("Sfogliatella, Wikipedia", _W + "Sfogliatella"), ("Monastero di Santa Rosa, Wikipedia", _W + "Monastero_di_Santa_Rosa")],
 "baba": [("Babà, Wikipedia", _W + "Bab%C3%A0"),
          ("Babà, storia e leggenda del dolce napoletano nato in Francia, Gambero Rosso", "https://www.gamberorosso.it/notizie/storie/baba-storia-e-leggenda-del-dolce-napoletano-nato-in-francia")],
 "pastiera": [("Pastiera napoletana, Wikipedia", _W + "Pastiera_napoletana"), ("Chiesa di San Gregorio Armeno, Wikipedia", _W + "Chiesa_di_San_Gregorio_Armeno"),
              ("Storia e leggenda della pastiera napoletana, Gambero Rosso", "https://www.gamberorosso.it/notizie/storie/storia-e-leggenda-della-pastiera-napoletana-con-la-ricetta-di-sal-de-riso/")],
 "zeppole-di-san-giuseppe": [("Zeppola di San Giuseppe, Wikipedia", _W + "Zeppola_di_San_Giuseppe"), ("Ippolito Cavalcanti, Wikipedia", _W + "Ippolito_Cavalcanti"),
                             ("Zeppole di San Giuseppe: storia e varianti regionali, Dissapore", "https://www.dissapore.com/cucina/zeppole-di-san-giuseppe-storia-e-varianti-regionali-di-un-dolce-frittissimo/")],
 "colazione-napoletana": [("Croissant, Wikipedia", _W + "Croissant"), ("Kipferl, Wikipedia", _W + "Kipferl"), ("Sfogliatella, Wikipedia", _W + "Sfogliatella")],
 "dolci-dei-conventi": [("Monastero di Santa Rosa, Wikipedia", _W + "Monastero_di_Santa_Rosa"), ("Chiesa di San Gregorio Armeno, Wikipedia", _W + "Chiesa_di_San_Gregorio_Armeno"),
                        ("Roccocò, Wikipedia", _W + "Roccoc%C3%B2"), ("Susamielli, Wikipedia", _W + "Susamielli")],
 "dolci-di-natale": [("Struffoli, Wikipedia", _W + "Struffoli"), ("Roccocò, Wikipedia", _W + "Roccoc%C3%B2"), ("Mustaccioli, Wikipedia", _W + "Mostaccioli"),
                     ("Susamielli, Wikipedia", _W + "Susamielli"), ("Pisto, Wikipedia", _W + "Pisto")],
 "piazza-carita-via-toledo": [("Via Toledo, Wikipedia", _W + "Via_Toledo"), ("Piazza Carità, Wikipedia", _W + "Piazza_Carit%C3%A0"),
                              ("Chiesa di Santa Maria della Carità, Wikipedia", _W + "Chiesa_di_Santa_Maria_della_Carit%C3%A0_(Napoli)"),
                              ("Pignasecca, Wikipedia", _W + "Pignasecca"), ("Quartieri Spagnoli, Wikipedia", _W + "Quartieri_Spagnoli")],
 "a-tazza-e-cafe": [("'A tazza 'e cafè, Wikipedia", _W + "%27A_tazza_%27e_caf%C3%A8"), ("Questi fantasmi!, Wikipedia", _W + "Questi_fantasmi%21"),
                    ("Caffè sospeso, Wikipedia", _W + "Caff%C3%A8_sospeso")],
 "festa-della-mamma": [("Festa della mamma, Wikipedia", _W + "Festa_della_mamma")],
 "tradizioni-napoletane": [("Panaro, Wikipedia", _W + "Panaro"), ("Cornicello, Wikipedia", _W + "Cornicello"), ("Smorfia napoletana, Wikipedia", _W + "Smorfia_napoletana"),
                           ("San Gennaro, Wikipedia", _W + "San_Gennaro")],
}
for _a in ARTICOLI:
    _a["fonti"] = FONTI[_a["slug"]]
    # Revisore: si indica solo dopo una revisione reale (nome di chi ha riletto e data)
    _a.setdefault("revisore", None)

# ── Categorie del magazine ────────────────────────────────────────────
CATEGORIE = [
 {"slug": "caffe-e-colazione", "nome": "Caffè e colazione",
  "intro": "Il rito del caffè a Napoli, il caffè sospeso, le canzoni e la colazione al bar: cornetto, sfogliatella e tazzina.",
  "articoli": ["caffe-napoletano", "caffe-sospeso", "a-tazza-e-cafe", "colazione-napoletana"]},
 {"slug": "pasticceria-napoletana", "nome": "Pasticceria napoletana",
  "intro": "Storie, leggende e ingredienti dei dolci napoletani: sfogliatella, babà, pastiera, zeppole, i dolci dei conventi e quelli di Natale.",
  "articoli": ["sfogliatella", "baba", "pastiera", "zeppole-di-san-giuseppe", "dolci-dei-conventi", "dolci-di-natale", "festa-della-mamma"]},
 {"slug": "napoli", "nome": "Napoli: luoghi e tradizioni",
  "intro": "Piazza Carità, via Toledo e le tradizioni che si vedono ogni giorno per le strade di Napoli.",
  "articoli": ["piazza-carita-via-toledo", "tradizioni-napoletane"]},
]
CATEGORIA_DI = {s: c for c in CATEGORIE for s in c["articoli"]}
assert sorted(CATEGORIA_DI) == sorted(a["slug"] for a in ARTICOLI), "ogni articolo deve avere una categoria"

# ── Collegamenti dal menu agli approfondimenti (per id del prodotto su qromo) ──
MENU_APPROFONDIMENTI = {
 152789: "storie/zeppole-di-san-giuseppe/",
 153840: "storie/sfogliatella/", 153867: "storie/sfogliatella/", 153868: "storie/sfogliatella/",
 153848: "storie/pastiera/",
 153854: "storie/baba/", 153855: "storie/baba/", 153860: "storie/baba/", 153861: "storie/baba/",
 219384: "pasticceria/", 472126: "pasticceria/", 616031: "pasticceria/", 638146: "pasticceria/",
 153960: "aspritz/",
 278576: "bar/", 296968: "bar/",
}

# ── Specialità della casa (pagina /specialita/) ───────────────────────
# Ogni voce è legata al prodotto su qromo tramite il suo id: ingredienti, allergeni e disponibilità
# arrivano dal menu; se un prodotto non è più disponibile su qromo, sparisce da solo dalla pagina.
SPECIALITA = [
 {"id": "caffe", "nome": "I caffè della casa", "nome_en": "House coffees", "menu": "bar-dolci", "voci": [
   (153768, "caffe-ceraldi", "La nostra firma: cioccolata calda sul fondo, crema di caffè e panna montata fresca, in bicchiere.", "Our signature: hot chocolate at the bottom, coffee cream and fresh whipped cream, served in a glass."),
   (153770, None, "Il caffè incontra il dolce più napoletano: crema di caffè, crema al babà, un babà mignon e panna.", "Coffee meets the most Neapolitan of pastries: coffee cream, babà cream, a mini babà and cream."),
   (153769, None, "Espresso con crema di zucchero e panna sciolta a bagnomaria.", "Espresso with whipped sugar cream and cream warmed in a bain-marie."),
   (153771, None, "Espresso con crema di zucchero, pasta di nocciola Piemonte IGP e cacao.", "Espresso with whipped sugar cream, Piedmont PGI hazelnut paste and cocoa."),
   (153789, None, "Espresso con crema di pistacchio e granella tostata.", "Espresso with pistachio cream and toasted chopped pistachios."),
   (153773, None, "Espresso con crema di zucchero e crema di latte montata a freddo.", "Espresso with whipped sugar cream and cold-whipped milk cream."),
 ]},
 {"id": "dolci", "nome": "I dolci della casa", "nome_en": "House pastries", "menu": "bar-dolci", "voci": [
   (616031, "cestino", "Il riccio della sfogliatella diventa un cesto croccante, farcito con crema chantilly e frutti di bosco.", "The crisp layers of the sfogliatella shaped into a basket, filled with chantilly cream and berries."),
   (638146, None, "Monoporzione di babà bagnato al limoncello, con un cuore di chantilly ai limoni di Amalfi.", "A single-serve babà soaked in limoncello, with a heart of Amalfi lemon chantilly."),
   (219384, "babamisu", "Una cupola di babà farcita con crema al mascarpone e caffè: il babà incontra il tiramisù.", "A babà dome filled with mascarpone cream and coffee: babà meets tiramisù."),
   (472126, "pellecchiella", "Torta al forno con albicocche Pellecchielle del Vesuvio.", "A baked cake with Pellecchiella apricots from Vesuvius."),
   (472130, None, "Torta al forno con mela Annurca IGP, crema pasticcera e cannella.", "A baked cake with Annurca PGI apples, custard and cinnamon."),
   (153840, None, "La sfogliatella riccia con crema pasticcera e amarene, la più vicina alla ricetta del convento.", "The sfogliatella riccia with custard and black cherries, the closest to the original convent recipe."),
 ]},
 {"id": "aperitivo", "nome": "L'aperitivo della casa", "nome_en": "House aperitivo", "menu": "cocktails-birre-alcolici", "voci": [
   (153960, "aspritz", "Il nostro spritz napoletano: bitter fatto in casa con agrumi della Costiera Amalfitana, erbe e radici, e Asprinio di Aversa spumante.", "Our Neapolitan spritz: a homemade bitter with Amalfi Coast citrus, herbs and roots, topped with sparkling Asprinio di Aversa."),
 ]},
]
