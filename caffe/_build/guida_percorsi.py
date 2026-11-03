#!/usr/bin/env python3
"""Calcola il percorso pedonale reale di ogni tratto di un itinerario (dalla tappa precedente alla tappa) e scrive l'SQL
che lo salva in guida_tappe (percorso, svolte, percorso_calcolato_il). Si usa in redazione, mai dal telefono del visitatore.
Uso:  MENU_SB_URL=... MENU_SB_KEY=<anon> python3 guida_percorsi.py --itinerario il-primo-giro [--itinerario ...] --sql out.sql
Servizio: routing.openstreetmap.de/routed-foot (FOSSGIS, dati OSM). Una richiesta ogni 3 secondi, come chiede chi lo gestisce.
Legge con la chiave anon: vede solo itinerari e luoghi pubblicati o in anteprima."""
import argparse, json, os, sys, time, urllib.request

SERVIZIO = 'https://routing.openstreetmap.de/routed-foot/route/v1/driving/%s,%s;%s,%s?overview=full&geometries=geojson&steps=true'

def rest(url, k, q):
    r = urllib.request.Request('%s/rest/v1/%s' % (url, q), headers={'apikey': k, 'Authorization': 'Bearer ' + k})
    return json.load(urllib.request.urlopen(r, timeout=60))

def tratto(a, b):
    r = urllib.request.Request(SERVIZIO % (a['lon'], a['lat'], b['lon'], b['lat']), headers={'User-Agent': 'CeraldiGuida/1.0 (redazione)'})
    d = json.load(urllib.request.urlopen(r, timeout=60))
    if d.get('code') != 'Ok' or not d.get('routes'): raise SystemExit('percorso non trovato: %s -> %s' % (a['slug'], b['slug']))
    rt = d['routes'][0]
    geo = {'type': 'LineString', 'coordinates': [[round(x, 6), round(y, 6)] for x, y in rt['geometry']['coordinates']]}
    sv = [{'t': s['maneuver']['type'], 'm': s['maneuver'].get('modifier', ''), 'n': s.get('name', ''), 'd': round(s['distance'])} for s in rt['legs'][0]['steps']]
    return geo, sv, round(rt['distance']), round(rt['duration'] / 60)

def q(s): return "'" + s.replace("'", "''") + "'"

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--itinerario', action='append', required=True); ap.add_argument('--sql', required=True)
    a = ap.parse_args()
    url, k = os.environ['MENU_SB_URL'].rstrip('/'), os.environ['MENU_SB_KEY']
    luoghi = {l['id']: l for l in rest(url, k, 'guida_luoghi?select=id,slug,lat,lon')}
    righe = []
    for slug in a.itinerario:
        it = rest(url, k, 'guida_itinerari?select=id&slug=eq.' + slug)
        if not it: sys.exit('itinerario non visibile: ' + slug)
        tappe = rest(url, k, 'guida_tappe?select=id,luogo_id,ordine,metri_dal_precedente,minuti_dal_precedente&itinerario_id=eq.%d&order=ordine' % it[0]['id'])
        for prec, t in zip(tappe, tappe[1:]):
            geo, sv, metri, minuti = tratto(luoghi[prec['luogo_id']], luoghi[t['luogo_id']])
            print('%s tappa %d: %d m (salvati %s), %d min (salvati %s), %d punti, %d svolte' % (slug, t['ordine'], metri, t['metri_dal_precedente'], minuti, t['minuti_dal_precedente'], len(geo['coordinates']), len(sv)))
            righe.append("update guida_tappe set percorso = %s::jsonb, svolte = %s::jsonb, percorso_calcolato_il = now() where id = %d;" % (q(json.dumps(geo, separators=(',', ':'))), q(json.dumps(sv, ensure_ascii=False, separators=(',', ':'))), t['id']))
            time.sleep(3)
    open(a.sql, 'w', encoding='utf-8').write('\n'.join(righe) + '\n')
    print('SQL: %s (%d tratti)' % (a.sql, len(righe)))

if __name__ == '__main__': main()
