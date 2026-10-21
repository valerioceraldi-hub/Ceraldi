// ══════════════════════════════════════════════════════════════════════
// UTENZE-BOLLETTA — punto d'ingresso sul server (21/10/2026)
// Legge le bollette PDF di luce, gas e acqua del bar e le archivia.
// Tutta la logica sta in servizio.js e parsers.js (questa cartella del repo),
// importati da un COMMIT FISSATO: il codice che gira non cambia finché non si
// ripubblica questo file con un commit nuovo.
// Azioni:
//   leggi     {pdf_base64 | fattura_id}  → legge, NON salva (PDF in attesa nel bucket privato)
//   salva     {attesa, dati, correzioni}  → archivia; le correzioni insegnano il modello del fornitore
//   scan_xml  {quante}                    → bollette già allegate agli XML delle utenze (poche per volta)
//   pdf_url   {bolletta_id}               → link temporaneo al PDF
// Accesso: utente con scrittura su Fatture, o il sistema (x-sistema-secret).
// Solo bollette intestate a Ceraldi Group: quelle di casa vengono rifiutate.
// ══════════════════════════════════════════════════════════════════════
import { createClient } from 'jsr:@supabase/supabase-js@2';
import { extractText, getDocumentProxy } from 'npm:unpdf@0.12.1';
import { crea } from 'https://raw.githubusercontent.com/valerioceraldi-hub/Ceraldi/bfab808eab9d8cf9fdef762095f1e98386be3281/funzioni/utenze-bolletta/servizio.js';

const gestisci = crea({
  createClient, extractText, getDocumentProxy,
  URL_SB: Deno.env.get('SUPABASE_URL')!, SERVICE: Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!, ANON: Deno.env.get('SUPABASE_ANON_KEY')!,
});
Deno.serve(gestisci);
