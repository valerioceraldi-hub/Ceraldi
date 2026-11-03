import { layers, namedFlavor } from '@protomaps/basemaps';
import fs from 'node:fs';
const L = layers('protomaps', namedFlavor('light'), { lang: 'it' });
const fonts = new Set(); L.forEach(l => { const f = l.layout && l.layout['text-font']; if (f) fonts.add(JSON.stringify(f)); });
console.log('layer', L.length, 'font', [...fonts].join(' '));
const stile = { version: 8, name: 'Ceraldi guida',
  glyphs: 'GLYPHS/{fontstack}/{range}.pbf', sprite: 'SPRITE',
  sources: { protomaps: { type: 'vector', tiles: ['TILES/{z}/{x}/{y}.pbf'], minzoom: 10, maxzoom: 15,
    attribution: '<a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">© OpenStreetMap</a> · <a href="https://protomaps.com" target="_blank" rel="noopener">Protomaps</a>' } },
  layers: L };
fs.writeFileSync('out/stile.json', JSON.stringify(stile));
