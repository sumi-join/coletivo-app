"""
Coletivo Sans — entrelinhamento lateral (kerning).

Geometria pura abre buracos previsíveis: diagonal contra diagonal (AV), haste
contra vazio (Tо), redondo contra ponto (o.). Aqui estão os pares que importam,
por classes, para não escrever quatro mil combinações à mão.
"""

# variantes acentuadas entram junto com a base
ACC = {
    "A": ["Agrave", "Aacute", "Acircumflex", "Atilde", "Adieresis", "Aring"],
    "E": ["Egrave", "Eacute", "Ecircumflex", "Edieresis"],
    "O": ["Ograve", "Oacute", "Ocircumflex", "Otilde", "Odieresis", "Oslash"],
    "U": ["Ugrave", "Uacute", "Ucircumflex", "Udieresis"],
    "Y": ["Yacute", "Ydieresis"],
    "C": ["Ccedilla"],
    "N": ["Ntilde"],
    "S": ["Scaron"],
    "Z": ["Zcaron"],
    "a": ["agrave", "aacute", "acircumflex", "atilde", "adieresis", "aring"],
    "e": ["egrave", "eacute", "ecircumflex", "edieresis"],
    "o": ["ograve", "oacute", "ocircumflex", "otilde", "odieresis", "oslash"],
    "u": ["ugrave", "uacute", "ucircumflex", "udieresis"],
    "c": ["ccedilla"],
    "n": ["ntilde"],
    "s": ["scaron"],
    "y": ["yacute", "ydieresis"],
    "z": ["zcaron"],
}


def _fam(*names):
    out = []
    for n in names:
        out.append(n)
        out += ACC.get(n, [])
    return out


CLASSES = {
    "UC_A": _fam("A"),
    "UC_T": ["T"],
    "UC_VWY": _fam("V", "W", "Y"),
    "UC_ROUND": _fam("O", "C", "G", "Q"),
    "UC_D": ["D", "Eth"],
    "UC_L": ["L"],
    "UC_FP": ["F", "P"],
    "UC_K": ["K", "X"],
    "UC_R": ["R"],
    "LC_ROUND": _fam("o", "c", "e") + ["d", "q", "g"],
    "LC_A": _fam("a"),
    "LC_ASC": ["b", "h", "k", "l", "thorn"],
    "LC_VWY": _fam("v", "w", "y"),
    "LC_S": _fam("s"),
    "LC_N": _fam("n", "u") + ["m", "r", "i", "j", "p"],
    "LC_T": ["t"],
    "PONTO": ["period", "comma", "ellipsis", "quotesinglbase", "quotedblbase"],
    "ASPAS": ["quoteright", "quotedblright", "quoteleft", "quotedblleft",
              "quotesingle", "quotedbl"],
    "TRACO": ["hyphen", "endash", "emdash"],
}

# (classe esquerda, classe direita, ajuste em unidades de 1000)
PAIRS = [
    ("UC_A", "UC_T", -76), ("UC_T", "UC_A", -72),
    ("UC_A", "UC_VWY", -64), ("UC_VWY", "UC_A", -64),
    ("UC_A", "UC_ROUND", -18), ("UC_ROUND", "UC_A", -14),
    ("UC_L", "UC_T", -78), ("UC_L", "UC_VWY", -76), ("UC_L", "ASPAS", -92),
    ("UC_L", "UC_ROUND", -20),
    ("UC_FP", "UC_A", -50), ("UC_R", "UC_VWY", -30), ("UC_R", "UC_T", -26),
    ("UC_K", "UC_ROUND", -22), ("UC_ROUND", "UC_K", -14),
    ("UC_D", "UC_A", -24), ("UC_D", "UC_VWY", -22), ("UC_D", "UC_T", -20),
    ("UC_ROUND", "UC_VWY", -14), ("UC_VWY", "UC_ROUND", -22),

    ("UC_T", "LC_ROUND", -88), ("UC_T", "LC_A", -86), ("UC_T", "LC_N", -66),
    ("UC_T", "LC_S", -70), ("UC_T", "LC_VWY", -52), ("UC_T", "PONTO", -104),
    ("UC_T", "TRACO", -72),
    ("UC_VWY", "LC_ROUND", -50), ("UC_VWY", "LC_A", -50),
    ("UC_VWY", "LC_N", -30), ("UC_VWY", "PONTO", -84), ("UC_VWY", "TRACO", -48),
    ("UC_FP", "LC_ROUND", -14), ("UC_FP", "PONTO", -96),
    ("UC_ROUND", "PONTO", -18),
    ("UC_L", "LC_VWY", -34), ("UC_A", "ASPAS", -70),

    ("LC_ROUND", "LC_VWY", -22), ("LC_VWY", "LC_ROUND", -22),
    ("LC_ROUND", "ASPAS", -22), ("LC_VWY", "PONTO", -62),
    ("LC_ROUND", "PONTO", -22), ("LC_A", "LC_VWY", -20),
    ("LC_ASC", "LC_VWY", -16),
    ("LC_T", "LC_ROUND", -14), ("LC_S", "LC_VWY", -14),
    ("ASPAS", "LC_A", -30), ("ASPAS", "LC_ROUND", -28), ("ASPAS", "UC_A", -60),
    ("PONTO", "ASPAS", -70),
    ("TRACO", "UC_T", -70), ("TRACO", "UC_VWY", -46),
]

# pares soltos que não valem uma classe
SINGLE = [
    ("r", "period", -64), ("r", "comma", -64), ("r", "a", -18), ("r", "s", -12),
    ("f", "quoteright", -46), ("f", "period", -18),
    ("F", "period", -96), ("P", "period", -96), ("V", "period", -84),
    ("one", "period", -20),
    ("L", "quoteright", -92), ("y", "period", -62), ("v", "period", -62),
    ("w", "period", -56), ("k", "o", -16), ("x", "o", -14),
]


def fea(glyph_names):
    """Gera o código .fea de kerning só com os glifos que existem na fonte."""
    have = set(glyph_names)
    out = ["languagesystem DFLT dflt;", "languagesystem latn dflt;",
           "languagesystem latn PTG;", "languagesystem latn BRA;", ""]
    used = {}
    for name, members in CLASSES.items():
        ms = [m for m in members if m in have]
        if ms:
            used[name] = ms
            out.append(f"@{name} = [{' '.join(ms)}];")
    out.append("")
    out.append("feature kern {")
    for a, b, v in PAIRS:
        if a in used and b in used:
            out.append(f"    pos @{a} @{b} {v};")
    for a, b, v in SINGLE:
        if a in have and b in have:
            out.append(f"    pos {a} {b} {v};")
    out.append("} kern;")
    return "\n".join(out) + "\n"


def pair_count(glyph_names):
    """Quantos pares de fato o kerning cobre (para o relatório)."""
    have = set(glyph_names)
    n = 0
    for a, b, v in PAIRS:
        ca = [m for m in CLASSES[a] if m in have]
        cb = [m for m in CLASSES[b] if m in have]
        n += len(ca) * len(cb)
    n += sum(1 for a, b, v in SINGLE if a in have and b in have)
    return n
