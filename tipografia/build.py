#!/usr/bin/env python3
"""
Coletivo Sans — build.

    python3 tipografia/build.py            # gera tudo em /fonte
    python3 tipografia/build.py --out DIR  # em outro lugar

Sai: 12 estáticas + 2 variáveis, em TTF e WOFF2, mais o CSS.
"""
import os
import sys
import time
import shutil
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fontTools.ttLib import TTFont
from coletivo.build import build_family, FAMILY, VERSION
from coletivo.core import INSTANCES, STYLE_NAME

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = """/* Coletivo Sans %(v)s — SIL Open Font License 1.1 — coletivo.app/fonte
   Uma família geométrica desenhada para o coletivo. Peso variável 300–900. */

@font-face {
  font-family: 'Coletivo Sans';
  src: url('ColetivoSans[wght].woff2') format('woff2-variations'),
       url('ColetivoSans[wght].woff2') format('woff2');
  font-weight: 300 900;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: 'Coletivo Sans';
  src: url('ColetivoSans-Italic[wght].woff2') format('woff2-variations'),
       url('ColetivoSans-Italic[wght].woff2') format('woff2');
  font-weight: 300 900;
  font-style: italic;
  font-display: swap;
}

/* pilha pronta: usa a Coletivo e cai nas geométricas de sempre */
:root {
  --fonte-coletivo: 'Coletivo Sans', Futura, 'Futura PT', 'Century Gothic',
                    'Jost', 'Avenir Next', sans-serif;
}
"""

CSS_STATIC = """/* Coletivo Sans %(v)s — versão com pesos estáticos (sem fonte variável) */
%(faces)s"""

FACE = """@font-face {
  font-family: 'Coletivo Sans';
  src: url('%(file)s.woff2') format('woff2');
  font-weight: %(w)s;
  font-style: %(style)s;
  font-display: swap;
}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "fonte"))
    ap.add_argument("--no-ttf", action="store_true")
    a = ap.parse_args()

    t0 = time.time()
    out = a.out
    tmp = os.path.join(out, "ttf")
    os.makedirs(tmp, exist_ok=True)
    print(f"Coletivo Sans {VERSION} → {out}")
    made = build_family(tmp)

    total_ttf = total_w2 = 0
    for path in made:
        f = TTFont(path)
        f.flavor = "woff2"
        w2 = os.path.join(out, os.path.basename(path).replace(".ttf", ".woff2"))
        f.save(w2)
        total_ttf += os.path.getsize(path)
        total_w2 += os.path.getsize(w2)
        print(f"    {os.path.basename(w2):38s} "
              f"{os.path.getsize(w2)/1024:6.1f} KB "
              f"(ttf {os.path.getsize(path)/1024:.1f})")

    with open(os.path.join(out, "coletivo-sans.css"), "w") as fh:
        fh.write(CSS % {"v": VERSION})
    # na web a família é uma só: o peso é que muda (o desdobramento em
    # "Coletivo Sans Light" etc. serve ao menu de fontes do sistema, não ao CSS)
    faces = []
    for italic in (False, True):
        for w in INSTANCES:
            sub = STYLE_NAME[w]
            faces.append(FACE % {
                "file": f"ColetivoSans-{sub}" + ("Italic" if italic else ""),
                "w": w, "style": "italic" if italic else "normal"})
    with open(os.path.join(out, "coletivo-sans-static.css"), "w") as fh:
        fh.write(CSS_STATIC % {"v": VERSION, "faces": "".join(faces)})

    lic = os.path.join(os.path.dirname(os.path.abspath(__file__)), "OFL.txt")
    if os.path.exists(lic):
        shutil.copy(lic, os.path.join(out, "OFL.txt"))

    print(f"\n  {len(made)} arquivos · woff2 {total_w2/1024:.0f} KB · "
          f"ttf {total_ttf/1024:.0f} KB · {time.time()-t0:.1f}s")
    print(f"  variável: {os.path.getsize(os.path.join(out, 'ColetivoSans[wght].woff2'))/1024:.1f} KB "
          f"cobre os 6 pesos")


if __name__ == "__main__":
    main()
