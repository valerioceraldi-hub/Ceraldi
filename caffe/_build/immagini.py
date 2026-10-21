# -*- coding: utf-8 -*-
"""Prepara una foto per il sito partendo dall'originale (JPG, PNG o WebP ad alta risoluzione).
Uso:  python3 caffe/_build/immagini.py ORIGINALE nome-descrittivo [larghezze]
Esempio: python3 caffe/_build/immagini.py ~/Scaricati/IMG_1234.jpg sfogliatella-riccia-banco 640,1024,1600,2400
Crea caffe/img/nome-descrittivo-<larghezza>.webp per ogni larghezza non più grande dell'originale
e stampa la riga da incollare in FOTO dentro contenuti.py (il testo alternativo va scritto a mano).
I dati nascosti della fotocamera (modello, GPS) non vengono copiati."""
import os, re, sys
from PIL import Image, ImageOps

QUI = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(os.path.dirname(QUI), "img")

def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    orig, nome = sys.argv[1], sys.argv[2]
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", nome):
        sys.exit("Il nome deve essere in minuscolo, con parole separate da trattini (es. baba-al-rum-classico)")
    larghezze = [int(x) for x in (sys.argv[3] if len(sys.argv) > 3 else "640,1024,1600").split(",")]
    im = ImageOps.exif_transpose(Image.open(orig)).convert("RGB")
    fatte = []
    for w in sorted(set(larghezze), reverse=True):
        if w > im.width:
            print(f"Salto {w} px: l'originale è largo solo {im.width} px")
            continue
        h = round(im.height * w / im.width)
        im.resize((w, h), Image.LANCZOS).save(os.path.join(IMG, f"{nome}-{w}.webp"), "WEBP", quality=80, method=6)
        fatte.append(w)
    if not fatte:
        sys.exit("Nessuna versione creata: l'originale è troppo piccolo")
    from math import gcd
    g = gcd(im.width, im.height)
    rw, rh = im.width // g, im.height // g
    for a, b in ((3, 2), (4, 3), (1, 1), (4, 5), (3, 4), (16, 9)):
        if abs(im.width / im.height - a / b) < 0.02:
            rw, rh = a, b
            break
    print(f'Create: {", ".join(f"{nome}-{w}.webp" for w in fatte)}')
    print(f'Riga per FOTO in contenuti.py:\n    "{nome}": {{"alt": "SCRIVI QUI COSA SI VEDE", "w": {fatte}, "r": ({rw}, {rh})}},')

if __name__ == "__main__":
    main()
