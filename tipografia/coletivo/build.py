"""
Coletivo Sans — montagem das fontes.

Gera os masters (300/500/700/900), monta as estáticas e compila a variável
com o eixo wght. Como todos os pesos saem do mesmo desenho paramétrico, a
estrutura de pontos é idêntica e a interpolação é exata nos pesos intermediários.
"""
import os
import math
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.cu2qu import curves_to_quadratic
from fontTools.ttLib import TTFont, newTable
from fontTools.misc.timeTools import timestampNow

from .core import (UPM, XH, CAP, ASC, DESC, OS, OSC, TYPO_ASC, TYPO_DESC,
                   TYPO_GAP, P, MASTERS, INSTANCES, STYLE_NAME, STEM, slantify)
from . import glyphs as G
from . import extras            # registra números, pontuação, símbolos, acentos
from . import features

VERSION = "1.000"
FAMILY = "Coletivo Sans"
VENDOR = "CLTV"
COPYRIGHT = ("Copyright 2026 coletivo.app. "
             "Licenciada sob a SIL Open Font License, Version 1.1.")
DESIGNER = "coletivo — divide a mesa"
MAX_ERR = 0.85


# ─────────────────────────────────────────── desenho normalizado
def bbox(paths):
    xs, ys = [], []
    for p in paths:
        for x, y in p.sample(8):
            xs.append(x); ys.append(y)
    if not xs:
        return (0, 0, 0, 0)
    return (min(xs), min(ys), max(xs), max(ys))


def draw(name, p):
    """Devolve (contornos posicionados, avanço) para um glifo."""
    fn, uni, opts = G.REG[name]
    res = fn(p)
    if isinstance(res, tuple) and len(res) == 3:
        paths, sbl, sbr = res
    else:
        paths, sbl, sbr = res, p.sb, p.sb
    paths = [q for q in paths if q is not None]
    if opts.get("raw"):
        adv = opts["adv"](p) if callable(opts.get("adv")) else opts.get("adv", 0)
        return slantify(paths, p), round(adv)
    x0, _, x1, _ = bbox(paths)
    w = x1 - x0
    adv = opts["adv"](p) if callable(opts.get("adv")) else None
    if adv is None:
        adv = w + sbl + sbr
        dx = sbl - x0
    else:
        dx = (adv - w) / 2 - x0          # centralizado no avanço fixo
    paths = [q.transform(lambda t: (t[0] + dx, t[1])) for q in paths]
    return slantify(paths, p), round(adv)


def all_glyphs(p):
    out = {}
    for name in G.ORDER:
        out[name] = draw(name, p)
    return out


# ─────────────────────────────────────────── cúbicas → quadráticas
def compat(masters, name):
    """Confere que todos os masters têm a mesma estrutura de contornos."""
    ref = masters[0][name][0]
    for m in masters[1:]:
        cur = m[name][0]
        if len(cur) != len(ref):
            raise ValueError(f"{name}: nº de contornos difere "
                             f"({len(ref)} x {len(cur)})")
        for a, b in zip(ref, cur):
            if len(a.segs) != len(b.segs) or \
               [s[0] for s in a.segs] != [s[0] for s in b.segs]:
                raise ValueError(f"{name}: estrutura de segmentos difere")


def to_glyphs(masters, name):
    """Converte os contornos de todos os masters de um glifo, mantendo
    o mesmo número de pontos em todos (requisito da interpolação)."""
    compat(masters, name)
    # outputImpliedClosingLine=True: sem isso a caneta descarta o último ponto
    # quando ele coincide com o primeiro — e isso acontece em alguns pesos e
    # não em outros, quebrando a compatibilidade de interpolação.
    pens = [TTGlyphPen(None, outputImpliedClosingLine=True) for _ in masters]
    ref = masters[0][name][0]
    for ci in range(len(ref)):
        conts = [m[name][0][ci] for m in masters]
        for pen, c in zip(pens, conts):
            pen.moveTo(c.start)
        cur = [c.start for c in conts]
        for si in range(len(ref[ci].segs)):
            segs = [c.segs[si] for c in conts]
            if segs[0][0] == "l":
                for pen, s in zip(pens, segs):
                    pen.lineTo(s[1])
                cur = [s[1] for s in segs]
            else:
                curves = [(cur[i], s[1], s[2], s[3]) for i, s in enumerate(segs)]
                splines = curves_to_quadratic(curves, [MAX_ERR] * len(curves))
                for pen, sp in zip(pens, splines):
                    pen.qCurveTo(*sp[1:])
                cur = [s[3] for s in segs]
        for pen in pens:
            pen.closePath()
    return [pen.glyph() for pen in pens]


def notdef_pen(p):
    pen = TTGlyphPen(None)
    w, h, t = 380, CAP, p.hstem * 0.8
    for (x0, y0, x1, y1) in [(0, 0, w, t), (0, h - t, w, h),
                             (0, 0, t, h), (w - t, 0, w, h)]:
        pen.moveTo((x0, y0)); pen.lineTo((x1, y0))
        pen.lineTo((x1, y1)); pen.lineTo((x0, y1)); pen.closePath()
    return pen.glyph()


# ─────────────────────────────────────────── montagem de uma fonte
def build_font(masters_data, idx, wght, italic, style, glyf_cache):
    p = P(wght, italic)
    names = [".notdef"] + list(G.ORDER)
    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(names)

    cmap = {}
    for n in G.ORDER:
        uni = G.REG[n][1]
        if uni is not None:
            cmap[uni] = n
        for extra in G.REG[n][2].get("alt_uni", ()):
            cmap[extra] = n
    fb.setupCharacterMap(cmap)

    glyf = {".notdef": notdef_pen(p)}
    metrics = {".notdef": (500, 0)}
    for n in G.ORDER:
        glyf[n] = glyf_cache[n][idx]
        adv = masters_data[idx][n][1]
        metrics[n] = (adv, 0)
    # componentes (acentuadas)
    for n, comps in extras.composites(masters_data[idx], p).items():
        pen = TTGlyphPen(glyf)
        for base, dx, dy in comps["parts"]:
            pen.addComponent(base, (1, 0, 0, 1, round(dx), round(dy)))
        glyf[n] = pen.glyph()
        metrics[n] = (comps["adv"], 0)
        if comps["uni"]:
            cmap[comps["uni"]] = n
        names.append(n)
    fb.setupGlyphOrder(names)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyf)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=TYPO_ASC, descent=TYPO_DESC, lineGap=TYPO_GAP)
    fb.setupNameTable(name_records(wght, italic, style))
    fb.setupOS2(
        version=4,
        sTypoAscender=TYPO_ASC, sTypoDescender=TYPO_DESC, sTypoLineGap=TYPO_GAP,
        usWinAscent=TYPO_ASC, usWinDescent=-TYPO_DESC,
        sxHeight=XH, sCapHeight=CAP, achVendID=VENDOR,
        usWeightClass=wght, usWidthClass=5,
        fsType=0,
        fsSelection=fs_selection(wght, italic),
        panose=dict(bFamilyType=2, bSerifStyle=11, bWeight=panose_weight(wght),
                    bProportion=4, bContrast=2, bStrokeVariation=2,
                    bArmStyle=2, bLetterForm=8, bMidline=2, bXHeight=4),
        ulCodePageRange1=(1 << 0) | (1 << 1),
    )
    fb.setupPost(italicAngle=-10.0 if italic else 0.0,
                 underlinePosition=-150, underlineThickness=round(p.hstem * 0.9),
                 isFixedPitch=0)
    fb.font["head"].created = fb.font["head"].modified = timestampNow()
    fb.font["head"].macStyle = (1 if wght >= 700 else 0) | (2 if italic else 0)
    fb.addOpenTypeFeatures(features.fea(fb.font.getGlyphOrder()))
    gasp = newTable("gasp")
    gasp.version = 1
    gasp.gaspRange = {65535: 15}
    fb.font["gasp"] = gasp
    return fb.font


def fs_selection(wght, italic):
    v = 1 << 7                     # USE_TYPO_METRICS
    if italic:
        v |= 1 << 0
    if wght == 700:
        v |= 1 << 5
    if wght == 400 and not italic:
        v |= 1 << 6
    return v


def panose_weight(w):
    return {300: 4, 400: 5, 500: 6, 600: 7, 700: 8, 900: 10}.get(w, 5)


def name_records(wght, italic, style):
    sub = STYLE_NAME[wght]
    ribbi = wght in (400, 700)
    if ribbi:
        fam = FAMILY
        sf = ("Bold" if wght == 700 else "Regular")
        if italic:
            sf = "Bold Italic" if wght == 700 else "Italic"
    else:
        fam = f"{FAMILY} {sub}"
        sf = "Italic" if italic else "Regular"
    typo_sub = (sub + (" Italic" if italic else "")) if not (
        wght == 400 and not italic) else "Regular"
    if wght == 400 and italic:
        typo_sub = "Italic"
    full = f"{FAMILY} {sub}" + (" Italic" if italic else "")
    ps = f"ColetivoSans-{sub}" + ("Italic" if italic else "")
    return {
        "copyright": COPYRIGHT,
        "familyName": fam,
        "styleName": sf,
        "uniqueFontIdentifier": f"{VERSION};{VENDOR};{ps}",
        "fullName": full,
        "version": f"Version {VERSION}",
        "psName": ps,
        "designer": DESIGNER,
        "manufacturer": "coletivo.app",
        "vendorURL": "https://coletivo.app",
        "designerURL": "https://coletivo.app",
        "licenseDescription": (
            "Esta fonte é livre sob a SIL Open Font License, Version 1.1. "
            "Pode usar, estudar, modificar e redistribuir. "
            "Não pode vender sozinha. https://openfontlicense.org"),
        "licenseInfoURL": "https://openfontlicense.org",
        "typographicFamily": FAMILY,
        "typographicSubfamily": typo_sub,
        "sampleText": "divide a mesa",
    }


# ─────────────────────────────────────────── atalhos
def build_one(wght, italic=False):
    md = [all_glyphs(P(wght, italic))]
    cache = {n: to_glyphs(md, n) for n in G.ORDER}
    return build_font(md, 0, wght, italic, STYLE_NAME[wght], cache)


# ─────────────────────────────────────────── família inteira
def build_family(outdir, statics=True, variable=True, log=print):
    """Gera os masters, as estáticas e as variáveis (romana e itálica)."""
    import time
    os.makedirs(outdir, exist_ok=True)
    made = []
    for italic in (False, True):
        t0 = time.time()
        weights = list(INSTANCES)
        md = [all_glyphs(P(w, italic)) for w in weights]
        cache = {}
        for n in G.ORDER:
            cache[n] = to_glyphs(md, n)
        log(f"  {'itálica' if italic else 'romana'}: {len(G.ORDER)} glifos "
            f"desenhados em {len(weights)} pesos ({time.time()-t0:.1f}s)")
        fonts = {}
        for i, w in enumerate(weights):
            f = build_font(md, i, w, italic, STYLE_NAME[w], cache)
            fonts[w] = f
            if statics:
                nm = f"ColetivoSans-{STYLE_NAME[w]}" + ("Italic" if italic else "")
                path = os.path.join(outdir, nm + ".ttf")
                f.save(path)
                made.append(path)
        if variable:
            made.append(build_vf(fonts, italic, outdir, log))
    return made


def build_vf(fonts, italic, outdir, log=print):
    from fontTools.designspaceLib import DesignSpaceDocument, SourceDescriptor, \
        AxisDescriptor, InstanceDescriptor
    from fontTools.varLib import build as vbuild
    from fontTools.otlLib.builder import buildStatTable

    ds = DesignSpaceDocument()
    ax = AxisDescriptor()
    ax.minimum, ax.maximum, ax.default = 300, 900, 400
    ax.name, ax.tag, ax.labelNames = "Weight", "wght", {"en": "Weight"}
    ds.addAxis(ax)
    for w in MASTERS:
        s = SourceDescriptor()
        s.font = fonts[w]
        s.location = {"Weight": w}
        s.styleName = STYLE_NAME[w]
        s.familyName = FAMILY
        if w == 400:
            s.copyInfo = True
        ds.addSource(s)
    # o master padrão precisa existir na designspace
    if 400 not in MASTERS:
        ds.sources[0].copyInfo = True
    for w in INSTANCES:
        ins = InstanceDescriptor()
        ins.location = {"Weight": w}
        ins.styleName = STYLE_NAME[w] + (" Italic" if italic else "")
        ins.familyName = FAMILY
        ds.addInstance(ins)
    vf, _, _ = vbuild(ds, optimize=True)
    buildStatTable(vf, [{
        "tag": "wght", "name": "Weight",
        "values": [{"value": w, "name": STYLE_NAME[w],
                    **({"flags": 0, "linkedValue": 700} if w == 400 else {})}
                   for w in INSTANCES],
    }], macNames=False)
    vf["name"].setName("Coletivo Sans", 16, 3, 1, 0x409)
    vf["name"].setName("Italic" if italic else "Regular", 17, 3, 1, 0x409)
    nm = "ColetivoSans-Italic[wght].ttf" if italic else "ColetivoSans[wght].ttf"
    path = os.path.join(outdir, nm)
    vf.save(path)
    log(f"  variável: {nm}")
    return path
