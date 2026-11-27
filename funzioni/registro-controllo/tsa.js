// ════════════════════════════════════════════════════════════════════════
// Verifica crittografica di una ricevuta di marca temporale RFC 3161 (.tsr),
// come farebbe un perito con OpenSSL:
//  1. la risposta è "concessa" (status 0 o 1);
//  2. l'impronta marcata è ESATTAMENTE lo SHA-256 del manifesto;
//  3. la firma dell'ente è valida;
//  4. il certificato che firma è autorizzato alle marche temporali (EKU timeStamping)
//     e risale al certificato radice UFFICIALE dell'ente, fissato nel codice;
//  5. la catena è valida alla data della marca.
// Nessun "ok" viene preso per buono dal contenuto del file.
// Funziona in Deno (Edge Function) e in Node (prove), passando le librerie.
// ════════════════════════════════════════════════════════════════════════
import { RADICI } from './certificati.js';

const OID_SHA256 = '2.16.840.1.101.3.4.2.1';
const OID_EKU_TS = '1.3.6.1.5.5.7.3.8';
const hex = (b) => [...new Uint8Array(b)].map((x) => x.toString(16).padStart(2, '0')).join('');

function pemDer(pem) {
  const b64 = pem.replace(/-----[^-]+-----/g, '').replace(/\s+/g, '');
  const bin = atob(b64); const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}
function certDa(pkijs, asn1js, der) {
  const a = asn1js.fromBER(der instanceof Uint8Array ? der.buffer.slice(der.byteOffset, der.byteOffset + der.byteLength) : der);
  if (a.offset === -1) throw new Error('certificato illeggibile');
  return new pkijs.Certificate({ schema: a.result });
}
function bytesOctet(os) {
  // OctetString semplice o costruita (a pezzi)
  if (os.valueBlock.isConstructed) {
    const parti = os.valueBlock.value.map((p) => new Uint8Array(p.valueBlock.valueHexView));
    const n = parti.reduce((s, p) => s + p.length, 0); const out = new Uint8Array(n); let o = 0;
    for (const p of parti) { out.set(p, o); o += p.length; }
    return out;
  }
  return new Uint8Array(os.valueBlock.valueHexView);
}

/**
 * Motore crittografico "con riserva": identico a quello del sistema, ma se il sistema non
 * implementa la verifica ECDSA richiesta (il server di Supabase non supporta P-384 con
 * SHA-512, usato da FreeTSA) la verifica viene fatta con @noble/curves, libreria pubblica
 * e verificata. Si usa SOLO per verificare firme (mai per firmare) e solo per ECDSA.
 * lib.noble = { p384, p256, sha512, sha384, sha256 }; lib.forzaNoble = true solo nelle prove.
 */
const DATI_SPKI = Symbol('spki');
function bytes(x) { return x instanceof Uint8Array ? x : x && x.buffer ? new Uint8Array(x.buffer, x.byteOffset || 0, x.byteLength) : new Uint8Array(x); }
function motoreConRiserva(lib) {
  const { pkijs, noble: N } = lib;
  const base = new pkijs.CryptoEngine({ name: 'webcrypto', crypto: lib.crypto });
  if (!N) return base;
  const curva = (nc) => (nc === 'P-384' ? N.p384 : nc === 'P-256' ? N.p256 : null);
  const hashFn = (h) => { const n = (h && (h.name || h)) || ''; return n === 'SHA-512' ? N.sha512 : n === 'SHA-384' ? N.sha384 : n === 'SHA-256' ? N.sha256 : null; };
  // punto pubblico non compresso (04||X||Y) dentro la SubjectPublicKeyInfo
  const punto = (spki) => { for (let k = 0; k < spki.length - 3; k++) if (spki[k] === 0x03 && spki[k + 2] === 0x00 && spki[k + 3] === 0x04 && spki.length - (k + 3) === spki[k + 1] - 1) return spki.slice(k + 3); throw new Error('chiave pubblica illeggibile'); };
  const ecSpki = (fmt, alg) => fmt === 'spki' && alg && alg.name === 'ECDSA' && curva(alg.namedCurve);
  const vecchioImport = base.importKey.bind(base), vecchioVerify = base.verify.bind(base);
  base.importKey = async function (fmt, data, alg, ext, uso) {
    if (ecSpki(fmt, alg) && lib.forzaNoble === true) return { type: 'public', algorithm: alg, usages: uso, extractable: false, [DATI_SPKI]: { spki: bytes(data).slice(), curva: alg.namedCurve } };
    try {
      const k = await vecchioImport(fmt, data, alg, ext, uso);
      if (ecSpki(fmt, alg)) { try { k[DATI_SPKI] = { spki: bytes(data).slice(), curva: alg.namedCurve }; } catch (_e) { /* chiave non estendibile */ } }
      return k;
    } catch (e) {
      if (!ecSpki(fmt, alg)) throw e;
      return { type: 'public', algorithm: alg, usages: uso, extractable: false, [DATI_SPKI]: { spki: bytes(data).slice(), curva: alg.namedCurve } };
    }
  };
  base.verify = async function (alg, key, sig, data) {
    const info = key && key[DATI_SPKI];
    const nobleVerifica = () => {
      const c = curva(info.curva), h = hashFn(alg.hash);
      if (!c || !h) throw new Error('algoritmo di firma non supportato');
      return c.verify(bytes(sig), h(bytes(data)), punto(info.spki), { prehash: false, lowS: false, format: 'compact' });
    };
    if (alg && alg.name === 'ECDSA' && info && (lib.forzaNoble === true || !(key instanceof CryptoKey))) return nobleVerifica();
    try { return await vecchioVerify(alg, key, sig, data); }
    catch (e) { if (alg && alg.name === 'ECDSA' && info) return nobleVerifica(); throw e; }
  };
  return base;
}

/**
 * @param {object} lib   { pkijs, asn1js, crypto }
 * @param {string} ente  'FreeTSA' | 'DigiCert'
 * @param {Uint8Array} tsr  contenuto del file .tsr
 * @param {Uint8Array} dati contenuto esatto del file marcato (il manifesto)
 * @returns {Promise<{ok:boolean, motivo?:string, ora?:string, firmatario?:string, seriale?:string}>}
 */
export async function verificaMarca(lib, ente, tsr, dati) {
  const { pkijs, asn1js, crypto } = lib;
  const conf = RADICI[ente];
  if (!conf) return { ok: false, motivo: 'ente sconosciuto: ' + ente };
  try {
    // radice ufficiale: si ricontrolla l'impronta del certificato fissato nel codice
    const radDer = pemDer(conf.radice);
    const impRad = hex(await crypto.subtle.digest('SHA-256', radDer)).toUpperCase();
    if (impRad !== conf.impronta_radice) return { ok: false, motivo: 'certificato radice di ' + ente + ' diverso da quello ufficiale' };
    const radice = certDa(pkijs, asn1js, radDer);

    const a = asn1js.fromBER(tsr.buffer.slice(tsr.byteOffset, tsr.byteOffset + tsr.byteLength));
    if (a.offset === -1) return { ok: false, motivo: 'ricevuta illeggibile' };
    const resp = new pkijs.TimeStampResp({ schema: a.result });
    const st = resp.status.status;
    if (st !== 0 && st !== 1) return { ok: false, motivo: 'marca rifiutata dall\'ente (stato ' + st + ')' };
    if (!resp.timeStampToken) return { ok: false, motivo: 'ricevuta senza marca' };
    const sd = new pkijs.SignedData({ schema: resp.timeStampToken.content });
    const eci = sd.encapContentInfo;
    if (eci.eContentType !== '1.2.840.113549.1.9.16.1.4') return { ok: false, motivo: 'contenuto non è una marca temporale' };
    const tstBytes = bytesOctet(eci.eContent);
    const tst = new pkijs.TSTInfo({ schema: asn1js.fromBER(tstBytes.buffer.slice(tstBytes.byteOffset, tstBytes.byteOffset + tstBytes.byteLength)).result });

    // 2. impronta marcata = SHA-256 del manifesto
    if (tst.messageImprint.hashAlgorithm.algorithmId !== OID_SHA256) return { ok: false, motivo: 'algoritmo di impronta inatteso' };
    const attesa = hex(await crypto.subtle.digest('SHA-256', dati));
    const marcata = hex(tst.messageImprint.hashedMessage.valueBlock.valueHexView);
    if (attesa !== marcata) return { ok: false, motivo: 'la marca non riguarda questo manifesto (impronta diversa)' };

    // 3-5. firma e catena fino alla radice ufficiale, alla data della marca
    // Il token può contenere una copia "incrociata" della radice (stesso nome, firmata da
    // un'altra radice): la si toglie, così la catena termina sulla radice ufficiale fissata.
    const certs = (sd.certificates || []).filter((c) => !(c.subject && c.subject.isEqual(radice.subject)));
    for (const p of conf.intermedi) certs.push(certDa(pkijs, asn1js, pemDer(p)));
    sd.certificates = certs;
    let r;
    try {
      r = await sd.verify({ signer: 0, checkChain: true, trustedCerts: [radice], extendedMode: true, checkDate: tst.genTime,
        data: dati.buffer.slice(dati.byteOffset, dati.byteOffset + dati.byteLength) },
        motoreConRiserva(lib));
    } catch (e) {
      const m = (e && (e.message || e.signatureVerified === false && 'firma non valida')) || String(e);
      return { ok: false, motivo: 'firma o catena dei certificati non valida (' + String(m).slice(0, 120) + ')' };
    }
    if (!r || !r.signatureVerified) return { ok: false, motivo: 'firma dell\'ente non valida' };
    const firm = r.signerCertificate;
    const eku = (firm.extensions || []).find((x) => x.extnID === '2.5.29.37');
    const ekuIds = eku && eku.parsedValue && eku.parsedValue.keyPurposes ? eku.parsedValue.keyPurposes : [];
    if (!ekuIds.includes(OID_EKU_TS)) return { ok: false, motivo: 'il certificato che firma non è autorizzato alle marche temporali' };
    const cn = (firm.subject.typesAndValues.find((t) => t.type === '2.5.4.3') || {}).value;
    return { ok: true, ora: tst.genTime.toISOString(), firmatario: cn ? cn.valueBlock.value : '', seriale: hex(tst.serialNumber.valueBlock.valueHexView) };
  } catch (e) {
    return { ok: false, motivo: 'verifica non riuscita: ' + String((e && e.message) || e).slice(0, 160) };
  }
}
