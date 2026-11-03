import { PMTiles } from 'pmtiles';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
const URL_BUILD = process.argv[2], OUT = process.argv[3];
class CurlSource {
  constructor(u){ this.u = u; }
  getKey(){ return this.u; }
  async getBytes(offset, length){
    const buf = execFileSync('curl', ['-sf', '--max-time', '60', '-r', `${offset}-${offset + length - 1}`, this.u], { maxBuffer: 64 << 20 });
    return { data: buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength) };
  }
}
const p = new PMTiles(new CurlSource(URL_BUILD));
const h = await p.getHeader();
console.log('build maxZoom', h.maxZoom, 'tipo', h.tileType);
const lon2x = (lon, z) => Math.floor((lon + 180) / 360 * 2 ** z);
const lat2y = (lat, z) => { const r = lat * Math.PI / 180; return Math.floor((1 - Math.log(Math.tan(r) + 1 / Math.cos(r)) / Math.PI) / 2 * 2 ** z); };
const AMPIO = [14.15, 40.80, 14.33, 40.90], CENTRO = [14.222, 40.822, 14.272, 40.868];
let n = 0, byte = 0;
for (let z = 10; z <= 15; z++) {
  const b = z <= 12 ? AMPIO : CENTRO;
  for (let x = lon2x(b[0], z); x <= lon2x(b[2], z); x++) for (let y = lat2y(b[3], z); y <= lat2y(b[1], z); y++) {
    const t = await p.getZxy(z, x, y);
    if (!t || !t.data) continue;
    fs.mkdirSync(`${OUT}/${z}/${x}`, { recursive: true });
    fs.writeFileSync(`${OUT}/${z}/${x}/${y}.pbf`, Buffer.from(t.data));
    n++; byte += t.data.byteLength;
  }
}
console.log('tasselli', n, 'byte', byte);
