# -*- coding: utf-8 -*-
"""Scarica il menu pubblico di Ceraldi Caffè da qromo e lo salva in menu.json.
Uso: python3 caffe/_build/aggiorna_menu.py   poi   python3 caffe/_build/build.py
Fonte unica: il menu che il personale aggiorna già su qromo (prezzi, disponibilità, allergeni)."""
import json, os, re, sys, urllib.request

QUI = os.path.dirname(os.path.abspath(__file__))
URL = "https://ceraldicaffe.qromo.it/"

def estrai(js, nome):
    m = re.search(r'const\s+' + nome + r'\s*=\s*', js)
    if not m: raise SystemExit(f"Variabile {nome} non trovata: il formato di qromo è cambiato")
    dec = json.JSONDecoder()
    val, _ = dec.raw_decode(js, m.end())
    return val

def main(percorso=None):
    if percorso: html = open(percorso, encoding='utf-8').read()
    else: html = urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode('utf-8')
    return {k: estrai(html, k) for k in ("menus", "menusCategories", "menusItems", "allergens", "menusItemsAllergens")}

if __name__ == "__main__":
    d = main(sys.argv[1] if len(sys.argv) > 1 else None)
    import datetime
    d["_scaricato"] = datetime.date.today().isoformat()  # data mostrata come "Prezzi aggiornati al"
    json.dump(d, open(os.path.join(QUI, "menu_grezzo.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print({k: len(v) for k, v in d.items()})
