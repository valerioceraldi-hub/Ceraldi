/* ════════════════════════════════════════════════════════════════════════
   CERALDI — Leggi bollette da Gmail (Google Apps Script)
   Da installare UNA volta nell'account ceraldigroupsrl@gmail.com.

   Cosa fa:
   · cerca SOLO le email con PDF allegato dei fornitori di luce, gas e acqua
     (e quelle con «bolletta» nell'oggetto, per i fornitori nuovi);
   · manda ogni PDF all'app Ceraldi Fatture, che lo legge e lo archivia;
   · mette all'email l'etichetta «Ceraldi/Bolletta letta» così non la rilegge.
   Non legge nient'altro della casella, non cancella e non sposta nulla.

   Gira da solo una volta al mese (il 20, alle 7) e quando premi
   «Leggi da Gmail» nell'app.
   ════════════════════════════════════════════════════════════════════════ */

const URL_APP = 'https://qaqqptpprmfjlolordaq.supabase.co/functions/v1/utenze-bolletta';
const CHIAVE = 'INCOLLA_QUI_LA_CHIAVE';   // la trovi in app: Utenze → Leggi da Gmail → «Copia la chiave»
const ETICHETTA = 'Ceraldi/Bolletta letta';
const RICERCA = 'has:attachment filename:pdf newer_than:400d -label:"' + ETICHETTA + '" ' +
  '(from:enel.it OR from:enel.com OR from:abc.napoli.it OR from:eniplenitude.com OR subject:bolletta OR subject:"nuova bolletta")';

function leggiBollette() {
  const et = GmailApp.getUserLabelByName(ETICHETTA) || GmailApp.createLabel(ETICHETTA);
  const conti = { email: 0, pdf: 0, archiviate: 0, da_confermare: 0, scartate: 0, gia: 0, errori: 0 };
  const inizio = Date.now();
  const discussioni = GmailApp.search(RICERCA, 0, 40);
  for (const d of discussioni) {
    if (Date.now() - inizio > 4.5 * 60 * 1000) break;          // limite di tempo di Google: il resto al giro dopo
    let tuttoOk = true;
    for (const m of d.getMessages()) {
      const pdf = m.getAttachments({ includeInlineImages: false }).filter(a => /pdf$/i.test(a.getContentType()) || /\.pdf$/i.test(a.getName()));
      if (!pdf.length) continue;
      conti.email++;
      for (const a of pdf) {
        conti.pdf++;
        try {
          const r = UrlFetchApp.fetch(URL_APP, {
            method: 'post', contentType: 'application/json', muteHttpExceptions: true,
            headers: { 'x-utenze-token': CHIAVE },
            payload: JSON.stringify({
              azione: 'ricevi', nome_file: a.getName(), pdf_base64: Utilities.base64Encode(a.getBytes()),
              email: { id: m.getId(), mittente: m.getFrom(), oggetto: m.getSubject(), data: m.getDate().toISOString() }
            })
          });
          const j = JSON.parse(r.getContentText() || '{}');
          if (r.getResponseCode() !== 200 || j.errore) { conti.errori++; tuttoOk = false; continue; }
          if (j.esito === 'archiviata') conti.archiviate++;
          else if (j.esito === 'da confermare') conti.da_confermare++;
          else if (j.esito === 'già presente' || j.esito === 'già ricevuta') conti.gia++;
          else conti.scartate++;
        } catch (e) { conti.errori++; tuttoOk = false; }
      }
    }
    if (tuttoOk) d.addLabel(et);                                // se qualcosa è andato storto la si riprova la volta dopo
  }
  return conti;
}

// «Leggi da Gmail» premuto nell'app: l'app chiama questo indirizzo con la chiave
function doGet(e) {
  if (!e || !e.parameter || e.parameter.chiave !== CHIAVE) return risposta({ errore: 'Non autorizzato' });
  try { return risposta({ ok: true, ...leggiBollette() }); }
  catch (err) { return risposta({ errore: String(err && err.message || err) }); }
}
function risposta(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }

// Da eseguire UNA volta dopo aver incollato la chiave: attiva la lettura mensile e fa subito un primo giro
function installa() {
  ScriptApp.getProjectTriggers().filter(t => t.getHandlerFunction() === 'leggiBollette').forEach(t => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger('leggiBollette').timeBased().onMonthDay(20).atHour(7).create();
  Logger.log(JSON.stringify(leggiBollette()));
}
