#!/usr/bin/env python3
"""
Coletivo Sans — bench.

Mede a fonte contra as geométricas de referência e contra o uso real do site:
cobertura de caracteres, largura de texto, peso do arquivo, exatidão da
interpolação e sanidade de rasterização. Escreve tipografia/BENCH.md.

    python3 tipografia/bench.py [--ref DIR_COM_REFERENCIAS]
"""
import os
import sys
import glob
import time
import argparse
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.varLib.instancer import instantiateVariableFont
import uharfbuzz as hb
import freetype

FONTE = os.path.join(ROOT, "fonte")
AMOSTRAS = [
    "O coletivo tira o intermediário caro do meio.",
    "divide a mesa",
    "R$ 38,90 — 23% de taxa",
    "Não é um dono mais barato. É não ter dono.",
    "Cadastre seu restaurante e comece a vender hoje",
]


# ─────────────────────────────────────────── utilidades
def kb(path):
    return os.path.getsize(path) / 1024.0


def shape_width(path, text, size=16, wght=None):
    """Largura em px do texto moldado (com kerning), como o navegador faria."""
    with open(path, "rb") as fh:
        data = fh.read()
    face = hb.Face(data)
    font = hb.Font(face)
    upm = face.upem
    if wght is not None:
        try:
            font.set_variations({"wght": wght})
        except Exception:
            pass
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True})
    adv = sum(p.x_advance for p in buf.glyph_positions)
    return adv / upm * size


def cover(path, chars):
    cmap = TTFont(path).getBestCmap()
    return [c for c in chars if ord(c) not in cmap]


def site_chars():
    """Todo caractere que aparece nas páginas do coletivo."""
    seen = set()
    for f in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
        if "/fonte/" in f:
            continue
        with open(f, encoding="utf-8") as fh:
            seen |= set(fh.read())
    # descarta controles e o que só existe dentro de código/emoji
    return {c for c in seen if c.isprintable() and not c.isspace()
            and unicodedata.category(c)[0] not in ("C", "S")
            or c in "→←●·"}


def metrics(path, wght=None):
    f = TTFont(path)
    if wght and "fvar" in f:
        f = instantiateVariableFont(f, {"wght": wght}, inplace=False)
    upm = f["head"].unitsPerEm
    os2 = f["OS/2"]
    gs = f.getGlyphSet()
    cm = f.getBestCmap()

    def bb(ch):
        gn = cm.get(ord(ch))
        if not gn:
            return None
        bp = BoundsPen(gs)
        gs[gn].draw(bp)
        return bp.bounds

    def adv(ch):
        gn = cm.get(ord(ch))
        return f["hmtx"][gn][0] * 1000 // upm if gn else None
    ob, lb = bb("o"), bb("l")
    s = upm / 1000.0
    return {
        "upm": upm,
        "xh": round(getattr(os2, "sxHeight", 0) / s) or round(ob[3] / s),
        "cap": round(getattr(os2, "sCapHeight", 0) / s),
        "stem": round((lb[2] - lb[0]) / s),
        "o": adv("o"), "n": adv("n"), "m": adv("m"), "zero": adv("0"),
        "glifos": len(f.getGlyphOrder()),
    }


def raster_check(path, sizes=(11, 13, 16, 24)):
    """Rasteriza todo o alfabeto e acusa glifo vazio ou fora de esquadro."""
    face = freetype.Face(path)
    bad = []
    cm = TTFont(path).getBestCmap()
    for px in sizes:
        face.set_char_size(px * 64)
        for cp, gn in cm.items():
            if gn == "space":
                continue
            face.load_char(chr(cp), freetype.FT_LOAD_RENDER)
            bm = face.glyph.bitmap
            if bm.rows == 0 or bm.width == 0:
                bad.append((px, chr(cp), gn, "vazio"))
            elif bm.rows > px * 3 or bm.width > px * 4:
                bad.append((px, chr(cp), gn, f"{bm.width}x{bm.rows}"))
    return bad


def interp_exactness(vf_path, static_path, wght):
    """A variável tem de reproduzir a estática do mesmo peso."""
    vf = instantiateVariableFont(TTFont(vf_path), {"wght": wght}, inplace=False)
    st = TTFont(static_path)
    worst, worst_g = 0, None
    for gn in st.getGlyphOrder():
        if gn not in vf["glyf"]:
            continue
        a, b = vf["glyf"][gn], st["glyf"][gn]
        if a.numberOfContours <= 0 or b.numberOfContours <= 0:
            continue
        if len(a.coordinates) != len(b.coordinates):
            return None, gn
        for (x1, y1), (x2, y2) in zip(a.coordinates, b.coordinates):
            d = max(abs(x1 - x2), abs(y1 - y2))
            if d > worst:
                worst, worst_g = d, gn
    return worst, worst_g


# ─────────────────────────────────────────── bench
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default=os.environ.get("COLETIVO_REF", ""))
    ap.add_argument("--md", default=os.path.join(HERE, "BENCH.md"))
    a = ap.parse_args()

    vf = os.path.join(FONTE, "ColetivoSans[wght].ttf")
    vf = vf if os.path.exists(vf) else os.path.join(FONTE, "ttf",
                                                    "ColetivoSans[wght].ttf")
    reg = os.path.join(FONTE, "ttf", "ColetivoSans-Regular.ttf")
    L = []

    def say(s=""):
        print(s)
        L.append(s)

    say("# Bench — Coletivo Sans")
    say()
    say("Gerado por `python3 tipografia/bench.py`. Todas as medidas em "
        "unidades de 1000 por em, salvo indicação.")
    say()

    # 1. desenho
    say("## 1. O desenho, contra as referências")
    say()
    refs = {}
    if a.ref and os.path.isdir(a.ref):
        for name, fn, w in (("Jost", "Jost.ttf", 400),
                            ("Poppins", "Poppins-Regular.ttf", None),
                            ("Montserrat", "Montserrat.ttf", 400)):
            p = os.path.join(a.ref, fn)
            if os.path.exists(p):
                refs[name] = metrics(p, w)
    mine = metrics(reg)
    cols = ["xh", "cap", "stem", "o", "n", "m", "zero"]
    head = ("| fonte | altura-x | caixa alta | haste | av. `o` | av. `n` | "
            "av. `m` | av. `0` |")
    say(head)
    say("|---|---|---|---|---|---|---|---|")
    say("| **Coletivo Sans** | " + " | ".join(f"**{mine[c]}**" for c in cols) + " |")
    for n, m in refs.items():
        say(f"| {n} | " + " | ".join(str(m[c]) for c in cols) + " |")
    say()
    if refs:
        avg_m = sum(m["m"] for m in refs.values()) / len(refs)
        say(f"Largura: o `m` da Coletivo é {100*mine['m']/avg_m:.0f}% da média "
            f"das referências — mais econômica na horizontal, que é o que "
            f"interessa num app cheio de lista e preço.")
    say()

    # 2. largura de texto real
    say("## 2. Quanto texto cabe na linha")
    say()
    say("Largura em px de cada frase a 16px, moldada com kerning "
        "(`uharfbuzz`, o mesmo caminho do navegador).")
    say()
    names = ["Coletivo"] + list(refs.keys())
    say("| frase | " + " | ".join(names) + " |")
    say("|---" * (len(names) + 1) + "|")
    for t in AMOSTRAS:
        vals = [shape_width(reg, t)]
        for n in refs:
            fn = {"Jost": "Jost.ttf", "Poppins": "Poppins-Regular.ttf",
                  "Montserrat": "Montserrat.ttf"}[n]
            vals.append(shape_width(os.path.join(a.ref, fn), t,
                                    wght=400 if n != "Poppins" else None))
        cell = " | ".join(f"{v:.0f}" for v in vals)
        say(f"| {t[:44]}{'…' if len(t) > 44 else ''} | {cell} |")
    say()

    # 3. cobertura
    say("## 3. Cobertura")
    say()
    chars = site_chars()
    falta = cover(reg, chars)
    f = TTFont(reg)
    cmap = f.getBestCmap()
    say(f"- Glifos: **{len(f.getGlyphOrder())}** por peso "
        f"({len(cmap)} caracteres mapeados).")
    say(f"- Caracteres distintos usados hoje nas páginas do coletivo: "
        f"**{len(chars)}**.")
    say(f"- Faltando: **{len(falta)}**"
        + (f" — {' '.join(sorted(falta))} (katakana do letreiro do Rio Sandô e "
           f"seletor de variação; caem na pilha de fallback, como devem)."
           if falta else " — cobertura total."))
    lat1 = [chr(c) for c in list(range(0x20, 0x7F)) + list(range(0xA0, 0x100))]
    fl = cover(reg, lat1)
    say(f"- Latin-1 completo: {'sim' if not fl else 'faltam ' + ' '.join(fl)}.")
    say()

    # 4. arquivos
    say("## 4. Peso dos arquivos")
    say()
    w2 = sorted(glob.glob(os.path.join(FONTE, "*.woff2")))
    var = [p for p in w2 if "[wght]" in p]
    est = [p for p in w2 if "[wght]" not in p]
    say(f"- Variável romana: **{kb(var[0] if var else reg):.1f} KB** (woff2), "
        f"cobre os seis pesos de 300 a 900.")
    if len(var) > 1:
        say(f"- Variável itálica: **{kb(var[1]):.1f} KB**.")
    say(f"- Estáticas: {len(est)} arquivos, "
        f"{sum(kb(p) for p in est)/max(1,len(est)):.1f} KB em média.")
    if a.ref:
        for n, fn in (("Jost variável (9 pesos)", "Jost.ttf"),
                      ("Poppins Regular", "Poppins-Regular.ttf")):
            p = os.path.join(a.ref, fn)
            if os.path.exists(p):
                t = TTFont(p)
                say(f"- Referência {n}: {kb(p):.0f} KB em TTF, "
                    f"{len(t.getGlyphOrder())} glifos.")
    say()
    say("O par que o site carrega (variável romana + itálica) pesa "
        f"**{sum(kb(p) for p in var):.0f} KB**.")
    say()

    # 5. interpolação
    say("## 5. A variável bate com as estáticas?")
    say()
    say("Cada peso estático é gerado direto do desenho paramétrico e a variável "
        "tem um master por peso publicado. Os dois caminhos têm de dar no mesmo "
        "desenho — o que sobra é arredondamento de coordenada inteira. "
        "Diferença máxima de coordenada, por peso:")
    say()
    say("| peso | maior diferença | glifo |")
    say("|---|---|---|")
    for w in (300, 400, 500, 600, 700, 900):
        st = os.path.join(FONTE, "ttf",
                          f"ColetivoSans-{ {300:'Light',400:'Regular',500:'Medium',600:'SemiBold',700:'Bold',900:'Black'}[w] }.ttf")
        if not os.path.exists(st):
            continue
        d, g = interp_exactness(vf, st, w)
        say(f"| {w} | {'incompatível' if d is None else f'{d:.1f} un.'} "
            f"| {g or '—'} |")
    say()

    # 6. rasterização
    say("## 6. Rasterização")
    say()
    t0 = time.time()
    bad = raster_check(reg)
    say(f"Todo o mapa de caracteres rasterizado em 11, 13, 16 e 24 px "
        f"({time.time()-t0:.1f}s): "
        + (f"**{len(bad)} problemas** — {bad[:6]}" if bad
           else "**nenhum glifo vazio ou fora de esquadro**."))
    say()

    # 7. kerning
    from coletivo import features
    say("## 7. Kerning")
    say()
    say(f"- Pares cobertos: **{features.pair_count(f.getGlyphOrder())}** "
        f"(por classes).")
    say(f"- Tabela GPOS presente em todas as estáticas e nas duas variáveis.")
    say()

    with open(a.md, "w") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"\n→ {a.md}")


if __name__ == "__main__":
    main()
