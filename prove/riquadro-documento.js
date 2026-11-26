#!/usr/bin/env node
// Prova: ogni schermata di Ceraldi Fatture in cui si SCEGLIE o si CONFERMA un documento
// deve usare il riquadro unico ricvEstremi (tipo, importo col segno, fornitore, numero,
// data, XML e Dettagli). Uso:  node prove/riquadro-documento.js [Primanota.html]
const fs = require('fs'), path = require('path');
const file = process.argv[2] || path.join(__dirname, '..', 'Primanota.html');
const righe = fs.readFileSync(file, 'utf8').split('\n');
const F = {}; let nome = null;
for (const r of righe) {
  const m = r.match(/^(?:async\s+)?function\s+([\w$]+)\s*\(/);
  if (m) { nome = m[1]; F[nome] = ''; } else if (/^<\/script>/.test(r)) nome = null;
  if (nome) F[nome] += r + '\n';
}
const usaRiquadro = s => /\bricvEstremi\(|\b_cfRigaFattura\(|\bdocsBox\(/.test(s);

// 1) le schermate note: se una smette di usare il riquadro, la prova fallisce
const SCHERMATE = [
  'ricvScegliDisegna', 'ricvDaFatturaDisegna', 'ricvRiga', 'ricvApri', 'ricvGuidaDisegna', 'ricvHtmlDoppia', 'ricvSceltaDoc',
  'apriCollegaNC', 'pncDisegna', '_cfRender', '_cfRigaFattura', '_cfMultiplo', '_cfMostraCombinazioni', '_cfMostraCombinazioniDueVersanti',
  '_apriPickerCambioAbbinamento', '_apriPickerAbbinamentoCarta', '_apriPickerAbbinamentoPaypal', '_apriRiconciliaGruppoDaBanca',
  '_quickPayConfirmDialog', 'pnRegistraPagamento', '_apriListaAggancio', '_apriCercaRateFattura', '_renderDedupModale',
  '_bonRender', '_bfRender', 'ricControlloDisegna', 'ricMovSchedaHtml', '_pnDisegnaSchedaVero', 'docDettagliHtml',
  'renderRiconciliazione', 'renderRiconciliazionePaypal', 'pnSchedaNc', '_anHtmlVoce'
];

// 2) le schermate nuove: elenchi con documenti e un comando per collegarli, senza riquadro.
//    Qui dentro c'è chi è stato controllato a mano e non fa scegliere un documento (col motivo).
const ESENTI = {
  renderRiconciliazioneCarta: 'scheda «Carta» nascosta: nessun comando la apre (la carta si riconcilia da «Riconciliazione»)',
  _rfRender: 'non si apre: apriRiconciliaDaFattura non ha più chiamanti',
  _apriCercaDdtFattura: 'non ha più chiamanti',
  apriAggancioXml: 'non ha più chiamanti',
  _sfRender: 'scheda fornitore: elenco da consultare, il tocco apre la scheda della fattura',
  _utMostraLettura: 'conferma di una bolletta: la fattura abbinata usa _anRigaFattura (estremi, XML, apre la scheda)'
};

const errori = [];
for (const n of SCHERMATE) {
  if (!F[n]) errori.push(n + ': non esiste più (aggiorna l\'elenco)');
  else if (n !== '_cfRigaFattura' && n !== 'ricvRiga' ? !usaRiquadro(F[n]) : !usaRiquadro(F[n].replace(/^.*\n/, ''))) errori.push(n + ': non usa il riquadro unico');
}
for (const [n, s] of Object.entries(F)) {
  if (SCHERMATE.includes(n) || ESENTI[n] || usaRiquadro(s)) continue;
  const documento = /\.numero\b/.test(s) && /\.fornitore\b/.test(s);
  const disegna = /<(div|label|button)[\s>]/.test(s) && /(\.forEach\(|\.map\()/.test(s);
  const sceglie = /(onclick|onchange|\.onclick)/.test(s) && />[^<>]{0,40}\b(Abbina|Collega|Aggancia|Conferma|Usa|Scegli|Aggiungi)\b|type="checkbox"/.test(s);
  if (documento && disegna && sceglie) errori.push(n + ': sembra far scegliere un documento senza il riquadro');
}
for (const n of Object.keys(ESENTI)) if (!F[n]) errori.push(n + ': esente ma non esiste più');
// il riquadro stesso deve avere tutto
for (const [che, re] of [['tipo', /pnTipo\(f\)/], ['importo col segno', /nc \? '−' : ''/], ['fornitore', /f\.fornitore/], ['numero', /f\.numero/], ['data', /ricGg\(f\.data\)/], ['XML', /_btnXml\(f/], ['Dettagli', /docDettagli\(/], ['uso della nota', /docUsiNc\(f\)/]])
  if (!re.test(F.ricvEstremi || '')) errori.push('ricvEstremi: manca ' + che);

if (errori.length) { console.log('✗ ' + errori.length + ' problemi:\n  ' + errori.join('\n  ')); process.exit(1); }
console.log('✓ riquadro unico in tutte le ' + SCHERMATE.length + ' schermate; nessun elenco nuovo senza riquadro');
