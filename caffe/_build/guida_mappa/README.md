# Mappa della Guida (ospitata da noi)

Mappa vettoriale di Napoli servita come file statici da `guida-nuova/mappa/`: nessun servizio di terzi, nessun cookie, funziona senza rete una volta salvata.

- **Dati**: OpenStreetMap (ODbL) dalla build pubblica Protomaps del **20261102** (`https://build.protomaps.com/20261102.pmtiles`), solo i tasselli necessari:
  zoom 10–12 su Napoli (14.15–14.33 E, 40.80–40.90 N), zoom 13–15 sul centro (14.222–14.272 E, 40.822–40.868 N). Oltre lo zoom 15 MapLibre ingrandisce.
  71 tasselli, 4,1 MB (2,55 MB compressi).
- **Stile**: `@protomaps/basemaps` 5.7.2, tema *light*, nomi in italiano; nascosti i punti di interesse di bar, ristoranti e negozi (niente concorrenti nella nostra guida).
- **Caratteri e icone**: `protomaps/basemaps-assets` (Noto Sans, licenza SIL OFL; icone v4), copiati qui.
- **Motore**: MapLibre GL JS 5.6.2 (BSD-3).
- **Attribuzione obbligatoria** sulla mappa: «© OpenStreetMap · Protomaps» (già nello stile).

## Rigenerare (es. ogni 6 mesi)
```
cd caffe/_build/guida_mappa && npm install
node estrai.mjs https://build.protomaps.com/AAAAMMGG.pmtiles ../../../guida-nuova/mappa/tiles
node stile.mjs   # scrive out/stile.json: copiarlo in guida-nuova/mappa/ e riapplicare il filtro dei punti di interesse (vedi doc 24)
```
Nello stile, `GLYPHS`, `SPRITE` e `TILES` sono segnaposto: la pagina li sostituisce con gli indirizzi della propria cartella.
