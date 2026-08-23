"""
Coletivo Sans — algarismos, pontuação, símbolos, acentos e compostas.

Os algarismos são tabulares de fábrica: todos com o mesmo avanço, para que
preço em coluna (o app inteiro é preço em coluna) alinhe sozinho.
"""
import math
from .core import (XH, CAP, ASC, DESC, FIG, OS, OSC, SUPER, Path, ring, arc,
                   rect, poly, isect, diag, diagv, polystroke, dot, shift,
                   scaled, rot180, bounds, se_pt)
from .glyphs import g, hw_of, REG, ORDER

D = math.radians


def wave(x0, x1, cy, h, t):
    """Onda de um traço só (til).

    Dois arcos encostados sempre deixam beliscão no meio; aqui a onda é uma
    cúbica única e o contorno é ela deslocada meia espessura para cima e para
    baixo — deslocamento vertical em cúbica é exato.
    """
    W = x1 - x0
    def curve(dy):
        p_ = Path((x0, cy - h + dy))
        p_.curve((x0 + W * 0.30, cy + h * 1.75 + dy),
                 (x0 + W * 0.70, cy - h * 1.75 + dy),
                 (x1, cy + h + dy))
        return p_
    up = curve(t / 2)
    lo = curve(-t / 2)
    path = Path(up.start)
    path.segs = list(up.segs)
    path.line((x1, cy + h - t / 2))
    r = lo.reversed()
    path.segs += r.segs
    path.line(up.start)
    return path.oriented(True)


def _fw(p):
    """meia-largura do algarismo (mesma família de larguras do 'o')"""
    return p.fx * 0.82


def fadv(p):
    return round(2 * _fw(p) + 2 * p.sbf)


# ══════════════════════════════════════════════ espaços
@g("space", 0x20, raw=True, adv=lambda p: round(250 + p.stem * 0.30),
   alt_uni=(0xA0,))
def _(p):
    return []


# ══════════════════════════════════════════════ ALGARISMOS
@g("zero", 0x30, adv=fadv)
def _(p):
    rx, ry = _fw(p), FIG / 2 + OSC
    return ring(p, rx, FIG / 2, rx, ry, p.rx_t, p.ry_t)


@g("one", 0x31, adv=fadv)
def _(p):
    st, hs = p.stem, p.hstem
    rx = _fw(p)
    fl = rx * 0.62
    stem = rect(rx - st / 2, 0, rx + st / 2, FIG)
    flag = poly([(rx - st / 2, FIG), (rx - st / 2, FIG - hs * 1.9),
                 (rx - st / 2 - fl, FIG - hs * 1.9 - fl * 0.60),
                 (rx - st / 2 - fl, FIG - fl * 0.60)])
    return [stem, flag]


def _bowls(p, y0, H, wr, a_up0, a_up1, a_lo0, a_lo1, cut0, cut1,
           meet_f=0.507, d=0.0, up_narrow=1.0):
    """Duas barrigas empilhadas com junção tangente (S, s, 3, 8...).

    A barriga de baixo nasce uma espessura acima de onde a de cima morre —
    sem isso o material de cada arco fica de um lado da linha de encontro e
    a letra racha no meio.
    """
    ov = (OSC if H > 600 else OS) * 0.9
    top, bot = y0 + H + ov, y0 - ov
    meet = y0 + H * meet_f
    ty = p.ry_t
    ryu = (top - (meet - ty / 2)) / 2
    ryl = ((meet + ty / 2) - bot) / 2
    rx = wr / 2
    up = arc(p, rx + d, top - ryu, rx * up_narrow - d, ryu, p.rx_t, ty,
             a_up0, a_up1, cut0, "r", seg=3)
    lo = arc(p, rx - d, bot + ryl, rx - d, ryl, p.rx_t, ty,
             a_lo0, a_lo1, "r", cut1, seg=3)
    return [up, lo]


@g("two", 0x32, adv=fadv)
def _(p):
    hs = p.hstem
    rx = _fw(p)
    ry = FIG * 0.30
    cy = FIG - ry
    a = arc(p, rx, cy, rx, ry, p.rx_t, p.ry_t, D(191), D(-14), "h", "r", seg=3)
    end = se_pt(rx, cy, rx, ry, SUPER, D(-14))
    dg = diag((end[0] - p.rx_t * 0.4, end[1]),
              (hw_of((0, 0), (end[0], end[1]), p.stem), hs * 0.7), p.stem)
    return [a, dg, rect(0, 0, 2 * rx, hs)]


@g("three", 0x33, adv=fadv)
def _(p):
    rx = _fw(p)
    return _bowls(p, 0, FIG, 2 * rx, D(172), D(-88), D(88), D(-172),
                  "h", "h", meet_f=0.50, d=0, up_narrow=0.92)


@g("four", 0x34, adv=fadv)
def _(p):
    st, hs = p.stem, p.hstem
    W = 2 * _fw(p) * 0.98
    yb = FIG * 0.235
    xs = W * 0.70
    dg = diag((xs + st / 2, FIG), (hw_of((0, FIG), (0, yb), st) * 0 + st * 0.62,
                                   yb + hs / 2), st)
    return [dg, rect(0, yb, W, yb + hs), rect(xs - st / 2, 0, xs + st / 2, FIG)]


@g("five", 0x35, adv=fadv)
def _(p):
    st, hs = p.stem, p.hstem
    rx = _fw(p)
    ytop = FIG * 0.52
    ry = (ytop + OSC * 0.9) / 2
    a = arc(p, rx, -OSC * 0.9 + ry, rx, ry, p.rx_t, p.ry_t,
            D(100), D(-168), "r", "h", seg=3)
    return [a, rect(0, ytop, st, FIG - hs), rect(0, FIG - hs, 2 * rx * 0.93, FIG)]


def _six(p):
    st = p.stem
    rx = _fw(p)
    ryb = FIG * 0.33
    cyb = ryb - OSC * 0.9
    bowl = ring(p, rx, cyb, rx, ryb, p.rx_t, p.ry_t)
    rya = (FIG + OSC * 0.9 - cyb) / 2
    up = arc(p, rx, cyb + rya, rx * 1.06, rya, p.rx_t, p.ry_t,
             D(180), D(62), "r", "v", seg=2)
    return bowl + [up]


@g("six", 0x36, adv=fadv)
def _(p):
    return _six(p)


@g("seven", 0x37, adv=fadv)
def _(p):
    st, hs = p.stem, p.hstem
    W = 2 * _fw(p) * 0.94
    return [rect(0, FIG - hs, W, FIG),
            diag((W - hw_of((0, FIG), (0, 0), st) - st * 0.1, FIG - hs * 0.3),
                 (W * 0.30, 0), st)]


@g("eight", 0x38, adv=fadv)
def _(p):
    rx = _fw(p)
    ty = p.ry_t
    meet = FIG * 0.515
    top, bot = FIG + OSC * 0.9, -OSC * 0.9
    ryu = (top - (meet - ty / 2)) / 2
    ryl = ((meet + ty / 2) - bot) / 2
    up = ring(p, rx, top - ryu, rx * 0.90, ryu, p.rx_t, ty)
    lo = ring(p, rx, bot + ryl, rx, ryl, p.rx_t, ty)
    return up + lo


@g("nine", 0x39, adv=fadv)
def _(p):
    return rot180(_six(p), _fw(p), FIG / 2)


# ══════════════════════════════════════════════ PONTUAÇÃO
def _dotr(p):
    return p.stem * 0.60 + 12


@g("period", 0x2E)
def _(p):
    r = _dotr(p)
    return [dot(r, r, r)], p.sb - 6, p.sb - 6


@g("comma", 0x2C)
def _(p):
    r = _dotr(p)
    tail = poly([(r * 0.30, r * 0.6), (r * 1.5, r * 0.6),
                 (r * 0.55, -r * 2.15), (-r * 0.15, -r * 1.5)])
    return [dot(r, r, r), tail], p.sb - 6, p.sb - 6


@g("colon", 0x3A)
def _(p):
    r = _dotr(p)
    return [dot(r, r, r), dot(r, XH - r, r)], p.sb - 6, p.sb - 6


@g("semicolon", 0x3B)
def _(p):
    r = _dotr(p)
    tail = poly([(r * 0.30, r * 0.6), (r * 1.5, r * 0.6),
                 (r * 0.55, -r * 2.15), (-r * 0.15, -r * 1.5)])
    return [dot(r, r, r), tail, dot(r, XH - r, r)], p.sb - 6, p.sb - 6


def _bang(p):
    st = p.stem
    r = _dotr(p)
    top, botn = CAP, r * 2.6
    return [poly([(-st * 0.53, top), (st * 0.53, top),
                  (st * 0.38, botn), (-st * 0.38, botn)]),
            dot(0, r, r)]


@g("exclam", 0x21)
def _(p):
    return _bang(p), p.sb + p.stem * 0.53 - 4, p.sb + p.stem * 0.53 - 4


@g("exclamdown", 0xA1)
def _(p):
    return (rot180(_bang(p), 0, (CAP - DESC * 0.0) / 2 - CAP * 0.14),
            p.sb + p.stem * 0.53 - 4, p.sb + p.stem * 0.53 - 4)


def _quest(p):
    st, hs = p.stem, p.hstem
    r = _dotr(p)
    rx = p.rx * 0.74
    ry = (CAP - CAP * 0.40) / 2
    cy = CAP + OSC * 0.5 - ry
    a = arc(p, rx, cy, rx, ry, p.rx_t, p.ry_t, D(196), D(-52), "h", "r", seg=3)
    end = se_pt(rx, cy, rx, ry, SUPER, D(-52))
    stem = rect(rx - st / 2, r * 2.7, rx + st / 2, end[1] + p.ry_t * 0.2)
    return [a, stem, dot(rx, r, r)]


@g("question", 0x3F)
def _(p):
    return _quest(p), p.sbr, p.sbr


@g("questiondown", 0xBF)
def _(p):
    return rot180(_quest(p), p.rx * 0.74, (CAP + DESC) / 2 + 24), p.sbr, p.sbr


@g("quotesingle", 0x27)
def _(p):
    st = p.stem
    h = CAP * 0.30
    return ([poly([(-st * 0.48, CAP), (st * 0.48, CAP),
                   (st * 0.36, CAP - h), (-st * 0.36, CAP - h)])],
            p.sb + p.stem * 0.48 - 10, p.sb + p.stem * 0.48 - 10)


@g("quotedbl", 0x22)
def _(p):
    st = p.stem
    h = CAP * 0.30
    one = poly([(-st * 0.48, CAP), (st * 0.48, CAP),
                (st * 0.36, CAP - h), (-st * 0.36, CAP - h)])
    return ([one] + shift([one], st * 1.55),
            p.sb + p.stem * 0.48 - 10, p.sb + p.stem * 0.48 - 10)


def _cma(p, up):
    r = _dotr(p) * 0.96
    y = CAP - r
    shp = [dot(0, y, r),
           poly([(-r * 0.70, y - r * 0.4), (r * 0.5, y - r * 0.4),
                 (-r * 0.45, y - r * 3.1), (-r * 1.15, y - r * 2.4)])]
    if up:
        shp = rot180(shp, 0, y)
    return shp, r


@g("quoteright", 0x2019)
def _(p):
    s, r = _cma(p, False)
    return s, p.sb + r - 8, p.sb + r - 8


@g("quoteleft", 0x2018)
def _(p):
    s, r = _cma(p, True)
    return s, p.sb + r - 8, p.sb + r - 8


@g("quotedblright", 0x201D)
def _(p):
    s, r = _cma(p, False)
    return s + shift(s, r * 2.3), p.sb + r - 8, p.sb + r - 8


@g("quotedblleft", 0x201C)
def _(p):
    s, r = _cma(p, True)
    return s + shift(s, r * 2.3), p.sb + r - 8, p.sb + r - 8


@g("quotesinglbase", 0x201A)
def _(p):
    s, r = _cma(p, False)
    return shift(s, 0, -CAP + _dotr(p) * 2.0), p.sb + r - 8, p.sb + r - 8


@g("quotedblbase", 0x201E)
def _(p):
    s, r = _cma(p, False)
    s = s + shift(s, r * 2.3)
    return shift(s, 0, -CAP + _dotr(p) * 2.0), p.sb + r - 8, p.sb + r - 8


@g("hyphen", 0x2D, alt_uni=(0xAD,))
def _(p):
    y = XH * 0.47
    return [rect(0, y - p.hstem / 2, p.rx * 0.72, y + p.hstem / 2)], p.sb - 12, p.sb - 12


@g("endash", 0x2013)
def _(p):
    y = XH * 0.47
    return [rect(0, y - p.hstem / 2, 500, y + p.hstem / 2)], p.sb - 16, p.sb - 16


@g("emdash", 0x2014)
def _(p):
    y = XH * 0.47
    return [rect(0, y - p.hstem / 2, 800, y + p.hstem / 2)], p.sb - 16, p.sb - 16


@g("underscore", 0x5F)
def _(p):
    return [rect(0, -180, 560, -180 + p.hstem)], 0, 0


@g("periodcentered", 0xB7)
def _(p):
    r = _dotr(p) * 0.86
    return [dot(r, XH * 0.47, r)], p.sb, p.sb


@g("bullet", 0x2022)
def _(p):
    r = _dotr(p) * 1.42
    return [dot(r, XH * 0.47, r)], p.sb - 4, p.sb - 4


@g("uni25CF", 0x25CF)
def _(p):
    r = XH * 0.36
    return [dot(r, XH * 0.47, r)], p.sb - 4, p.sb - 4


@g("ellipsis", 0x2026)
def _(p):
    r = _dotr(p)
    step = r * 2 + p.sb * 1.5
    return ([dot(r, r, r)] + shift([dot(r, r, r)], step)
            + shift([dot(r, r, r)], 2 * step), p.sb - 6, p.sb - 6)


def _paren(p, left):
    rx = p.rx * 0.62
    ry = (CAP + 250) / 2
    cy = CAP * 0.46
    a = arc(p, rx, cy, rx, ry, p.rx_t * 0.86, p.ry_t, D(118), D(242),
            "r", "r", seg=2)
    if not left:
        a = a.transform(lambda t: (2 * rx - t[0], t[1])).oriented(True)
    return [a]


@g("parenleft", 0x28)
def _(p):
    return _paren(p, True), p.sb - 8, p.sb - 14


@g("parenright", 0x29)
def _(p):
    return _paren(p, False), p.sb - 14, p.sb - 8


def _brack(p, left):
    st, hs = p.stem * 0.92, p.hstem
    w = p.rx * 0.52
    top, bot = CAP + 92, -158
    out = [rect(0, bot, st, top), rect(0, top - hs, w, top), rect(0, bot, w, bot + hs)]
    if not left:
        out = [q.transform(lambda t: (w - t[0], t[1])).oriented(True) for q in out]
    return out


@g("bracketleft", 0x5B)
def _(p):
    return _brack(p, True), p.sb - 6, p.sb - 12


@g("bracketright", 0x5D)
def _(p):
    return _brack(p, False), p.sb - 12, p.sb - 6


def _brace(p, left):
    """Chave: dois ganchos nas pontas, dois quartos de volta no meio.

    Os raios são escolhidos para que a espessura do traço caia no mesmo x nos
    dois sentidos de curvatura — senão o espinho vertical não encaixa.
    """
    t = p.stem * 0.78
    top, bot = CAP + 92, -158
    mid = (top + bot) / 2
    x0 = p.rx * 0.50                      # x do espinho
    r = x0                                # gancho das pontas
    r2 = (top - mid) * 0.46               # curva do meio
    out = []
    for sgn in (1, -1):                   # 1 = metade de cima
        end = top if sgn > 0 else bot
        hook = arc(p, x0 + r, end - sgn * r, r, r, t, t,
                   D(180), D(90) if sgn > 0 else D(270), "r", "v", seg=1)
        turn = arc(p, 0, mid + sgn * r2, x0 + t, r2, t, t,
                   D(0), D(-90 * sgn), "r", "v", seg=1)
        out += [hook, turn,
                rect(x0, min(end - sgn * r, mid + sgn * r2),
                     x0 + t, max(end - sgn * r, mid + sgn * r2))]
    if not left:
        out = [q.transform(lambda t_: (-t_[0], t_[1])).oriented(True) for q in out]
    return out


@g("braceleft", 0x7B)
def _(p):
    return _brace(p, True), p.sb - 6, p.sb - 10


@g("braceright", 0x7D)
def _(p):
    return _brace(p, False), p.sb - 10, p.sb - 6


@g("slash", 0x2F)
def _(p):
    W = p.rx * 1.10
    return [diag((hw_of((0, -140), (W, CAP + 60), p.stem), -140),
                 (W, CAP + 60), p.stem)], p.sbd, p.sbd


@g("backslash", 0x5C)
def _(p):
    W = p.rx * 1.10
    return [diag((hw_of((0, -140), (W, CAP + 60), p.stem), CAP + 60),
                 (W, -140), p.stem)], p.sbd, p.sbd


@g("bar", 0x7C)
def _(p):
    return [rect(0, -180, p.stem * 0.86, CAP + 110)], p.sb, p.sb


@g("brokenbar", 0xA6)
def _(p):
    st = p.stem * 0.86
    return ([rect(0, -180, st, CAP * 0.32), rect(0, CAP * 0.52, st, CAP + 110)],
            p.sb, p.sb)


@g("asterisk", 0x2A)
def _(p):
    r = p.rx * 0.46
    t = p.stem * 0.80
    cy = CAP - r * 1.06
    out = []
    for k in range(3):
        a = D(90 + k * 60)
        dx, dy = r * math.cos(a), r * math.sin(a)
        out.append(diagv((-dx, cy - dy), (dx, cy + dy), t) if abs(math.cos(a)) > 0.5
                   else diag((-dx, cy - dy), (dx, cy + dy), t))
    return out, p.sb + r - 12, p.sb + r - 12


@g("numbersign", 0x23)
def _(p):
    t = p.hstem * 0.94
    W = p.rx * 1.60
    out = []
    for y in (XH * 0.34, XH * 0.80):
        out.append(rect(0, y - t / 2, W, y + t / 2))
    for x in (W * 0.34, W * 0.68):
        out.append(diag((x - 40, 0), (x + 40, CAP * 0.94), t))
    return out, p.sb - 14, p.sb - 14


# ── matemática
def _mathy(p):
    return XH * 0.47


@g("plus", 0x2B)
def _(p):
    t = p.hstem * 0.96
    W = p.rx * 1.10
    cy = _mathy(p)
    return ([rect(0, cy - t / 2, W, cy + t / 2),
             rect(W / 2 - t / 2, cy - W / 2, W / 2 + t / 2, cy + W / 2)],
            p.sb - 8, p.sb - 8)


@g("minus", 0x2212)
def _(p):
    t = p.hstem * 0.96
    W = p.rx * 1.10
    cy = _mathy(p)
    return [rect(0, cy - t / 2, W, cy + t / 2)], p.sb - 8, p.sb - 8


@g("equal", 0x3D)
def _(p):
    t = p.hstem * 0.96
    W = p.rx * 1.10
    cy = _mathy(p)
    d = W * 0.20
    return ([rect(0, cy + d - t / 2, W, cy + d + t / 2),
             rect(0, cy - d - t / 2, W, cy - d + t / 2)], p.sb - 8, p.sb - 8)


@g("plusminus", 0xB1)
def _(p):
    t = p.hstem * 0.96
    W = p.rx * 1.10
    cy = _mathy(p) + W * 0.14
    return ([rect(0, cy - t / 2, W, cy + t / 2),
             rect(W / 2 - t / 2, cy - W / 2, W / 2 + t / 2, cy + W / 2),
             rect(0, cy - W / 2 - t * 1.6, W, cy - W / 2 - t * 0.6)],
            p.sb - 8, p.sb - 8)


@g("multiply", 0xD7)
def _(p):
    t = p.hstem * 0.96
    W = p.rx * 0.92
    cy = _mathy(p)
    hw = hw_of((0, 0), (W, W), t)
    return ([diag((hw, cy - W / 2), (W - hw, cy + W / 2), t),
             diag((hw, cy + W / 2), (W - hw, cy - W / 2), t)], p.sb - 6, p.sb - 6)


@g("divide", 0xF7)
def _(p):
    t = p.hstem * 0.96
    W = p.rx * 1.10
    cy = _mathy(p)
    r = t * 0.78
    return ([rect(0, cy - t / 2, W, cy + t / 2),
             dot(W / 2, cy + W * 0.30, r), dot(W / 2, cy - W * 0.30, r)],
            p.sb - 8, p.sb - 8)


@g("less", 0x3C)
def _(p):
    t = p.stem * 0.90
    W = p.rx * 0.92
    cy = _mathy(p)
    return ([polystroke([(W, cy + W * 0.52), (0, cy), (W, cy - W * 0.52)], t)],
            p.sb - 8, p.sb - 8)


@g("greater", 0x3E)
def _(p):
    t = p.stem * 0.90
    W = p.rx * 0.92
    cy = _mathy(p)
    return ([polystroke([(0, cy + W * 0.52), (W, cy), (0, cy - W * 0.52)], t)],
            p.sb - 8, p.sb - 8)


@g("asciitilde", 0x7E)
def _(p):
    W = p.rx * 1.30
    return ([wave(0, W, XH * 0.49, W * 0.145, p.hstem * 0.90)], p.sb - 8, p.sb - 8)


@g("asciicircum", 0x5E)
def _(p):
    t = p.stem * 0.90
    W = p.rx * 0.98
    return ([polystroke([(0, CAP * 0.52), (W / 2, CAP), (W, CAP * 0.52)], t,
                        fit={1: ("T", W / 2, CAP)})], p.sb - 8, p.sb - 8)


@g("logicalnot", 0xAC)
def _(p):
    t = p.hstem * 0.96
    W = p.rx * 1.10
    cy = _mathy(p) + W * 0.10
    return ([rect(0, cy - t / 2, W, cy + t / 2),
             rect(W - t, cy - W * 0.36, W, cy + t / 2)], p.sb - 8, p.sb - 8)


@g("degree", 0xB0)
def _(p):
    r = p.rx * 0.32
    return [q for q in ring(p, r, CAP - r, r, r, p.rx_t * 0.80, p.ry_t * 0.80)], \
        p.sb - 8, p.sb - 8


# ── moedas
@g("dollar", 0x24)
def _(p):
    st = p.stem
    body = _bowls(p, 0, CAP, p.rx * 1.42, D(26), D(286), D(106), D(-154),
                  "h", "h", d=p.rx * 1.42 / 2 * 0.055, up_narrow=0.955)
    x0, y0, x1, y1 = bounds(body)
    barx = (x0 + x1) / 2
    return body + [rect(barx - st * 0.42, -78, barx + st * 0.42, CAP + 78)], \
        p.sbr, p.sbr


@g("cent", 0xA2)
def _(p):
    st = p.stem
    rx = p.rx * 0.80
    ry = XH * 0.56
    cy = XH * 0.50
    a = arc(p, rx, cy, rx, ry, p.rx_t, p.ry_t, D(62), D(298), "v", "v", seg=3)
    return [a, rect(rx - st * 0.40, cy - ry - 74, rx + st * 0.40, cy + ry + 74)], \
        p.sbr, p.sbr


@g("sterling", 0xA3)
def _(p):
    st, hs = p.stem, p.hstem
    W = p.rx * 1.28
    ry = CAP * 0.30
    cy = CAP + OSC * 0.4 - ry
    a = arc(p, W * 0.62, cy, W * 0.44, ry, p.rx_t, p.ry_t, D(80), D(212),
            "v", "r", seg=2)
    return ([a, rect(W * 0.20, 0, W * 0.20 + st, cy),
             rect(0, 0, W, hs), rect(0, XH * 0.52, W * 0.72, XH * 0.52 + hs * 0.9)],
            p.sb - 6, p.sb - 6)


@g("yen", 0xA5)
def _(p):
    st, hs = p.stem, p.hstem
    W = p.rx * 1.42
    jy = CAP * 0.46
    hw = hw_of((0, CAP), (W / 2, jy), st)
    return ([diag((hw, CAP), (W / 2, jy), st), diag((W - hw, CAP), (W / 2, jy), st),
             rect(W / 2 - st / 2, 0, W / 2 + st / 2, jy),
             rect(0, jy * 0.62, W, jy * 0.62 + hs * 0.85),
             rect(0, jy * 0.30, W, jy * 0.30 + hs * 0.85)], p.sbd, p.sbd)


@g("Euro", 0x20AC)
def _(p):
    hs = p.hstem
    RX, RY = p.RX * 0.90, p.RY * 0.94
    cy = CAP / 2
    a = arc(p, RX, cy, RX, RY, p.rx_t, p.ry_t, D(56), D(304), "v", "v", seg=3)
    return ([a, rect(-RX * 0.20, cy + RY * 0.12, RX * 0.96, cy + RY * 0.12 + hs * 0.9),
             rect(-RX * 0.20, cy - RY * 0.20, RX * 0.96, cy - RY * 0.20 + hs * 0.9)],
            p.sbr - 4, p.sbr)


@g("currency", 0xA4)
def _(p):
    r = p.rx * 0.52
    cy = XH * 0.56
    rr = ring(p, r, cy, r, r, p.rx_t * 0.86, p.ry_t * 0.86)
    t = p.hstem * 0.86
    d = r * 0.92
    out = list(rr)
    for sx, sy in ((-1, 1), (1, 1), (-1, -1), (1, -1)):
        out.append(diag((r + sx * d * 0.62, cy + sy * d * 0.62),
                        (r + sx * d, cy + sy * d), t))
    return out, p.sb - 8, p.sb - 8


@g("percent", 0x25)
def _(p):
    r = p.rx * 0.40
    ry = r * 1.06
    t = p.rx_t * 0.72
    W = p.rx * 1.72
    up = ring(p, r, CAP - ry, r, ry, t, t * 0.88)
    lo = ring(p, W - r, ry, r, ry, t, t * 0.88)
    hw = hw_of((0, 0), (W, CAP), p.stem * 0.92)
    return up + lo + [diag((hw, 0), (W - hw, CAP), p.stem * 0.92)], p.sbr, p.sbr


@g("perthousand", 0x2030)
def _(p):
    r = p.rx * 0.40
    ry = r * 1.06
    t = p.rx_t * 0.72
    W = p.rx * 1.72
    up = ring(p, r, CAP - ry, r, ry, t, t * 0.88)
    lo = ring(p, W - r, ry, r, ry, t, t * 0.88)
    hw = hw_of((0, 0), (W, CAP), p.stem * 0.92)
    lo2 = shift(ring(p, W - r, ry, r, ry, t, t * 0.88), 2 * r + p.sb * 0.7)
    return (up + lo + lo2 + [diag((hw, 0), (W - hw, CAP), p.stem * 0.92)],
            p.sbr, p.sbr)


@g("ampersand", 0x26)
def _(p):
    """Laço em cima, barriga em baixo, diagonal cruzando e perna saindo.

    As duas retas têm de ser íngremes: com o corte na horizontal, uma diagonal
    deitada vira espeto (a meia-largura explode quando dy → 0).
    """
    st = p.stem
    W = p.RX * 1.66
    rt, ryt = W * 0.26, CAP * 0.150          # laço de cima
    cyt = CAP + OSC * 0.4 - ryt
    top = ring(p, rt, cyt, rt, ryt, p.rx_t * 0.92, p.ry_t * 0.92)
    rb, ryb = W * 0.38, CAP * 0.255          # barriga de baixo
    cyb = ryb - OSC * 0.4
    bot = arc(p, rb, cyb, rb, ryb, p.rx_t, p.ry_t, D(58), D(-208),
              "h", "r", seg=3)
    dg = diag((rt * 0.62, cyt - ryt * 0.72), (W * 0.94, cyb * 0.30), st)
    return top + [bot, dg], p.sb - 8, p.sbd


@g("at", 0x40)
def _(p):
    t = p.rx_t * 0.58
    ty = p.ry_t * 0.58
    RX, RY = p.RX * 1.10, p.RY * 1.06
    cy = CAP / 2
    outer = arc(p, RX, cy, RX, RY, t, ty, D(-46), D(268), "h", "v", seg=4)
    r, ry = RX * 0.46, RY * 0.44
    cyi = cy + ry * 0.06
    inner = ring(p, RX - r * 0.12, cyi, r, ry, t, ty)
    stem = rect(RX - r * 0.12 + r - t, cyi - ry * 0.72, RX - r * 0.12 + r,
                cyi + ry * 0.72)
    return [outer] + inner + [stem], p.sbr, p.sbr


@g("section", 0xA7)
def _(p):
    """Dois esses meia-altura, um encaixado no outro."""
    H = CAP * 0.62
    wr = p.rx * 1.06
    up = _bowls(p, CAP - H, H, wr, D(26), D(286), D(106), D(-154),
                "h", "h", d=wr / 2 * 0.055, up_narrow=0.955)
    lo = rot180(up, wr / 2, CAP / 2)
    return up + lo, p.sbr, p.sbr


@g("paragraph", 0xB6)
def _(p):
    st = p.stem
    W = p.rx * 1.12
    ry = (CAP - CAP * 0.40) / 2
    cy = CAP - ry
    # barriga cheia à esquerda da haste
    solid = Path(se_pt(W * 0.56, cy, W * 0.56, ry, SUPER, D(90)))
    from .core import se_arc as _sa
    _sa(solid, W * 0.56, cy, W * 0.56, ry, SUPER, D(90), D(270), 2)
    solid = solid.oriented(True)
    return ([solid, rect(W * 0.56 - st * 0.1, -150, W * 0.56 + st * 0.9, CAP),
             rect(W * 0.56 + st * 1.9, -150, W * 0.56 + st * 2.9, CAP)],
            p.sb - 6, p.sb - 6)


@g("guillemotleft", 0xAB)
def _(p):
    t = p.stem * 0.78
    W = p.rx * 0.44
    cy = XH * 0.48
    one = polystroke([(W, cy + W * 0.80), (0, cy), (W, cy - W * 0.80)], t)
    return [one] + shift([one], W * 1.15), p.sb - 10, p.sb - 10


@g("guillemotright", 0xBB)
def _(p):
    t = p.stem * 0.78
    W = p.rx * 0.44
    cy = XH * 0.48
    one = polystroke([(0, cy + W * 0.80), (W, cy), (0, cy - W * 0.80)], t)
    return [one] + shift([one], W * 1.15), p.sb - 10, p.sb - 10


@g("guilsinglleft", 0x2039)
def _(p):
    t = p.stem * 0.78
    W = p.rx * 0.44
    cy = XH * 0.48
    return ([polystroke([(W, cy + W * 0.80), (0, cy), (W, cy - W * 0.80)], t)],
            p.sb - 10, p.sb - 10)


@g("guilsinglright", 0x203A)
def _(p):
    t = p.stem * 0.78
    W = p.rx * 0.44
    cy = XH * 0.48
    return ([polystroke([(0, cy + W * 0.80), (W, cy), (0, cy - W * 0.80)], t)],
            p.sb - 10, p.sb - 10)


@g("dagger", 0x2020)
def _(p):
    st, hs = p.stem * 0.86, p.hstem * 0.9
    y = CAP * 0.72
    return ([rect(0, -60, st, CAP), rect(-st * 1.3, y, st * 2.3, y + hs)],
            p.sb + st * 1.3 - 6, p.sb + st * 1.3 - 6)


@g("daggerdbl", 0x2021)
def _(p):
    st, hs = p.stem * 0.86, p.hstem * 0.9
    return ([rect(0, -60, st, CAP), rect(-st * 1.3, CAP * 0.74, st * 2.3, CAP * 0.74 + hs),
             rect(-st * 1.3, CAP * 0.10, st * 2.3, CAP * 0.10 + hs)],
            p.sb + st * 1.3 - 6, p.sb + st * 1.3 - 6)


# ── sobrescritos e frações
def _small(paths, k, dy):
    return scaled(paths, k, 0, dy)


def _digit_paths(name, p):
    r = REG[name][0](p)
    return r[0] if isinstance(r, tuple) else r


@g("onesuperior", 0xB9)
def _(p):
    from .glyphs import REG as R
    st, hs = p.stem * 0.86, p.hstem * 0.86
    rx = _fw(p)
    k = 0.58
    stem = rect(rx - st / 2, 0, rx + st / 2, FIG)
    flag = poly([(rx - st / 2, FIG), (rx - st / 2, FIG - hs * 1.9),
                 (rx - st / 2 - rx * 0.62, FIG - hs * 1.9 - rx * 0.37),
                 (rx - st / 2 - rx * 0.62, FIG - rx * 0.37)])
    return _small([stem, flag], k, CAP - FIG * k), p.sb - 10, p.sb - 10


@g("twosuperior", 0xB2)
def _(p):
    return (_small(_digit_paths("two", p), 0.58, CAP - FIG * 0.58),
            p.sb - 10, p.sb - 10)


@g("threesuperior", 0xB3)
def _(p):
    return (_small(_digit_paths("three", p), 0.58, CAP - FIG * 0.58),
            p.sb - 10, p.sb - 10)


@g("ordfeminine", 0xAA)
def _(p):
    k = 0.54
    rx = p.rx * 0.95
    r = ring(p, rx, XH / 2, rx, p.ry, p.rx_t, p.ry_t)
    r = r + [rect(2 * rx - p.stem, 0, 2 * rx, XH)]
    out = _small(r, k, CAP - XH * k)
    x0, _, x1, _ = bounds(out)
    return out + [rect(x0, CAP - XH * k - p.hstem * 1.9, x1,
                       CAP - XH * k - p.hstem * 0.9)], p.sb - 10, p.sb - 10


@g("ordmasculine", 0xBA)
def _(p):
    k = 0.54
    r = ring(p, p.rx, XH / 2, p.rx, p.ry, p.rx_t, p.ry_t)
    out = _small(r, k, CAP - XH * k)
    x0, _, x1, _ = bounds(out)
    return out + [rect(x0, CAP - XH * k - p.hstem * 1.9, x1,
                       CAP - XH * k - p.hstem * 0.9)], p.sb - 10, p.sb - 10


@g("fraction", 0x2044)
def _(p):
    W = p.rx * 0.74
    return [diag((hw_of((0, 0), (W, CAP), p.stem * 0.9), -40),
                 (W, CAP + 20), p.stem * 0.9)], p.sbd - 14, p.sbd - 14


# ── marcas
def _frac(p, num, den):
    """Fração armada: numerador em cima, barra, denominador na linha."""
    k = 0.55
    st = p.stem * 0.86
    W = p.rx * 0.66
    n = scaled(_digit_paths(num, p), k, 0, CAP - FIG * k)
    d = scaled(_digit_paths(den, p), k, 0, 0)
    sl = diag((hw_of((0, -40), (W, CAP + 20), st), -40), (W, CAP + 20), st)
    sb = bounds([sl])
    nb, db = bounds(n), bounds(d)
    n = shift(n, sb[0] - nb[2] - p.stem * 0.15)
    d = shift(d, sb[2] - db[0] + p.stem * 0.15)
    return n + [sl] + d


@g("onehalf", 0xBD)
def _(p):
    return _frac(p, "one", "two"), p.sb - 12, p.sb - 12


@g("onequarter", 0xBC)
def _(p):
    return _frac(p, "one", "four"), p.sb - 12, p.sb - 12


@g("threequarters", 0xBE)
def _(p):
    return _frac(p, "three", "four"), p.sb - 12, p.sb - 12


@g("copyright", 0xA9)
def _(p):
    t = p.rx_t * 0.60
    R = p.RX * 0.72
    Ry = p.RY * 0.72
    cy = CAP / 2
    outer = ring(p, R, cy, R, Ry, t, t * 0.90)
    inner = arc(p, R, cy, R * 0.52, Ry * 0.52, t, t * 0.90, D(58), D(302),
                "v", "v", seg=3)
    return outer + [inner], p.sbr, p.sbr


@g("registered", 0xAE)
def _(p):
    t = p.rx_t * 0.60
    R = p.RX * 0.72
    Ry = p.RY * 0.72
    cy = CAP / 2
    outer = ring(p, R, cy, R, Ry, t, t * 0.90)
    st = t * 1.05
    bw = R * 0.50
    bot = cy - Ry * 0.02
    ry = (cy + Ry * 0.52 - bot) / 2
    bowl = arc(p, R - bw * 0.42, bot + ry, bw, ry, t, t * 0.9, D(90), D(-90),
               "r", "r", seg=2)
    leg = diag((R - bw * 0.42 + bw * 0.30, bot), (R + bw * 0.62, cy - Ry * 0.52), st)
    return (outer + [rect(R - bw * 0.9, cy - Ry * 0.52, R - bw * 0.9 + st,
                          cy + Ry * 0.52), bowl, leg], p.sbr, p.sbr)


@g("trademark", 0x2122)
def _(p):
    t = p.hstem * 0.80
    top = CAP
    h = CAP * 0.36
    W1 = p.rx * 0.56
    out = [rect(0, top - h, W1, top),
           rect(W1 / 2 - t / 2, top - h, W1 / 2 + t / 2, top)]
    x = W1 + p.rx * 0.16
    W2 = p.rx * 0.80
    hw = hw_of((0, top), (W2 / 2, top - h), t)
    out += [rect(x, top - h, x + t, top),
            rect(x + W2 - t, top - h, x + W2, top),
            diag((x + hw, top), (x + W2 / 2, top - h), t),
            diag((x + W2 - hw, top), (x + W2 / 2, top - h), t)]
    return out, p.sb - 10, p.sb - 10


@g("mu", 0xB5)
def _(p):
    rx = p.rx * 0.945
    st = p.stem
    sh = arc(p, rx, -OS + p.ry * 0.93, rx, p.ry * 0.93, p.rx_t, p.ry_t,
              D(180), D(360), "r", "r")
    cy = -OS + p.ry * 0.93
    return ([sh, rect(0, DESC, st, XH), rect(2 * rx - st, 0, 2 * rx, XH)],
            p.sb, p.sb)


# ── setas
def _arrow(p, ang):
    t = p.stem * 0.92
    L = p.rx * 1.78
    cy = XH * 0.47
    head = L * 0.30
    out = [rect(0, cy - t / 2, L, cy + t / 2),
           polystroke([(L - head, cy + head * 0.86), (L, cy),
                       (L - head, cy - head * 0.86)], t,
                      fit={1: ("R", L, cy)})]
    if ang:
        ca, sa = math.cos(D(ang)), math.sin(D(ang))
        cx = L / 2

        def rot(q):
            x, y = q[0] - cx, q[1] - cy
            return (cx + x * ca - y * sa, cy + x * sa + y * ca)
        out = [q.transform(rot).oriented(True) for q in out]
    return out


@g("arrowright", 0x2192)
def _(p):
    return _arrow(p, 0), p.sb - 10, p.sb - 10


@g("arrowleft", 0x2190)
def _(p):
    return _arrow(p, 180), p.sb - 10, p.sb - 10


@g("arrowup", 0x2191)
def _(p):
    return _arrow(p, 90), p.sb - 10, p.sb - 10


@g("arrowdown", 0x2193)
def _(p):
    return _arrow(p, -90), p.sb - 10, p.sb - 10


# ══════════════════════════════════════════════ letras que faltam (Latin-1)
@g("AE", 0xC6)
def _(p):
    st, hs = p.stem, p.hstem
    from .glyphs import cw
    W = cw(p) * 1.24
    xE = W * 0.44
    hw = hw_of((0, 0), (xE, CAP), st)
    left = polystroke([(hw, 0), (xE + hw, CAP), (xE + hw, CAP)][:2] + [(xE, CAP)], st,
                      fit={0: ("L", 0, None)})
    yb = p.bar_uc * 0.62
    k = xE / CAP
    bar = rect(k * (yb - hs / 2), yb - hs / 2, W * 0.86, yb + hs / 2)
    return ([left, rect(xE, 0, xE + st, CAP), rect(xE, CAP - hs, W, CAP),
             bar, rect(xE, 0, W, hs)], p.sbd, p.sb)


@g("ae", 0xE6)
def _(p):
    rx = p.rx * 0.86
    hs = p.hstem
    a_ring = ring(p, rx, XH / 2, rx, p.ry, p.rx_t, p.ry_t)
    a_stem = rect(2 * rx - p.stem, 0, 2 * rx, XH)
    cy = XH / 2
    e = arc(p, 2 * rx + rx * 0.90 - p.stem, cy, rx * 0.90, p.ry, p.rx_t, p.ry_t,
            D(0), D(305), "r", "v", seg=4)
    ebar = rect(2 * rx - p.stem, cy - hs / 2, 2 * rx + 2 * rx * 0.90 - p.stem,
                cy + hs / 2)
    return a_ring + [a_stem, e, ebar], p.sbr, p.sbr - 4


@g("OE", 0x152)
def _(p):
    st, hs = p.stem, p.hstem
    from .glyphs import cw
    RX, RY = p.RX, p.RY
    o = ring(p, RX, CAP / 2, RX, RY, p.rx_t, p.ry_t)
    x = 2 * RX - st
    W = cw(p) * 0.74
    yb = p.bar_uc
    return (o + [rect(x, 0, x + st, CAP), rect(x, CAP - hs, x + W, CAP),
                 rect(x, yb - hs / 2, x + W * 0.885, yb + hs / 2),
                 rect(x, 0, x + W, hs)], p.sbr, p.sb)


@g("oe", 0x153)
def _(p):
    rx = p.rx * 0.92
    hs = p.hstem
    o = ring(p, rx, XH / 2, rx, p.ry, p.rx_t, p.ry_t)
    cy = XH / 2
    x = 2 * rx - p.rx_t
    e = arc(p, x + rx * 0.94, cy, rx * 0.94, p.ry, p.rx_t, p.ry_t,
            D(0), D(305), "r", "v", seg=4)
    ebar = rect(x, cy - hs / 2, x + 2 * rx * 0.94, cy + hs / 2)
    return o + [e, ebar], p.sbr, p.sbr - 4


@g("Oslash", 0xD8)
def _(p):
    RX, RY = p.RX, p.RY
    o = ring(p, RX, CAP / 2, RX, RY, p.rx_t, p.ry_t)
    hw = hw_of((0, 0), (2 * RX, CAP), p.stem * 0.92)
    return o + [diag((hw - 30, -46), (2 * RX - hw + 30, CAP + 46), p.stem * 0.92)], \
        p.sbr, p.sbr


@g("oslash", 0xF8)
def _(p):
    rx, ry = p.rx, p.ry
    o = ring(p, rx, XH / 2, rx, ry, p.rx_t, p.ry_t)
    hw = hw_of((0, 0), (2 * rx, XH), p.stem * 0.92)
    return o + [diag((hw - 26, -40), (2 * rx - hw + 26, XH + 40), p.stem * 0.92)], \
        p.sbr, p.sbr


@g("germandbls", 0xDF)
def _(p):
    st = p.stem
    rx = p.rx * 0.86
    ry = (ASC + OS - XH * 0.42) / 2
    cy = ASC + OS - ry
    up = arc(p, rx * 0.72 + st * 0.5, cy, rx * 0.72, ry, p.rx_t, p.ry_t,
             D(150), D(-88), "r", "r", seg=3)
    ryl = (XH * 0.50 + OS) / 2
    lo = arc(p, rx * 0.86, -OS + ryl, rx * 0.86, ryl, p.rx_t, p.ry_t,
             D(96), D(-120), "r", "v", seg=3)
    return [rect(0, 0, st, cy), up, lo], p.sb, p.sbr


@g("Eth", 0xD0)
def _(p):
    st, hs = p.stem, p.hstem
    from .glyphs import cw
    W = cw(p) * 0.98
    cx = st * 0.5
    ry = CAP / 2 + OSC * 0.35
    bowl = arc(p, cx, CAP / 2, W - cx, ry, p.rx_t, p.ry_t, D(90), D(-90), "r", "r")
    return ([rect(0, 0, st, CAP), bowl,
             rect(-st * 0.55, CAP * 0.48 - hs / 2, st * 1.5, CAP * 0.48 + hs / 2)],
            p.sb - 10, p.sbr)


@g("eth", 0xF0)
def _(p):
    rx = p.rx
    r = ring(p, rx, XH / 2, rx, p.ry, p.rx_t, p.ry_t)
    t = p.hstem * 0.94
    return (r + [diagv((rx * 0.42, XH * 0.90), (2 * rx * 1.02, ASC * 0.99), t)],
            p.sbr, p.sbr)


@g("Thorn", 0xDE)
def _(p):
    st = p.stem
    from .glyphs import cw
    W = cw(p) * 0.82
    cx = st * 0.5
    top, bot = CAP * 0.86, CAP * 0.20
    ry = (top - bot) / 2
    bowl = arc(p, cx, bot + ry, W - cx, ry, p.rx_t, p.ry_t, D(90), D(-90), "r", "r")
    return [rect(0, 0, st, CAP), bowl], p.sb, p.sbr


@g("thorn", 0xFE)
def _(p):
    rx, st = p.rx, p.stem
    r = ring(p, rx, XH / 2, rx, p.ry, p.rx_t, p.ry_t)
    return [rect(0, DESC, st, ASC)] + r, p.sb, p.sbr


# ══════════════════════════════════════════════ ACENTOS
# desenhados centrados em x=0, na altura da caixa baixa
ACC_Y = XH + 58


@g("grave", 0x60, raw=True, adv=lambda p: round(2 * p.rx * 0.52))
def _(p):
    w, h = p.rx * 0.40, 128
    t = p.stem * 0.96
    return [diagv((-w, ACC_Y + h), (w, ACC_Y), t)]


@g("acute", 0xB4, raw=True, adv=lambda p: round(2 * p.rx * 0.52))
def _(p):
    w, h = p.rx * 0.40, 128
    t = p.stem * 0.96
    return [diagv((-w, ACC_Y), (w, ACC_Y + h), t)]


@g("circumflex", 0x2C6, raw=True, adv=lambda p: round(2 * p.rx * 0.62))
def _(p):
    w, h = p.rx * 0.44, 118 + p.stem * 0.42
    t = p.stem * 0.80
    return [polystroke([(-w, ACC_Y), (0, ACC_Y + h), (w, ACC_Y)], t,
                       fit={0: ("L", -w, None), 1: ("T", 0, ACC_Y + h),
                            2: ("R", w, None)})]


@g("caron", 0x2C7, raw=True, adv=lambda p: round(2 * p.rx * 0.62))
def _(p):
    w, h = p.rx * 0.44, 118 + p.stem * 0.42
    t = p.stem * 0.80
    return [polystroke([(-w, ACC_Y + h), (0, ACC_Y), (w, ACC_Y + h)], t,
                       fit={0: ("L", -w, None), 1: ("B", 0, ACC_Y),
                            2: ("R", w, None)})]


@g("tilde", 0x2DC, raw=True, adv=lambda p: round(2 * p.rx * 0.66))
def _(p):
    w = p.rx * 0.52
    return [wave(-w, w, ACC_Y + 68, w * 0.30, p.hstem * 1.02)]


@g("dieresis", 0xA8, raw=True, adv=lambda p: round(2 * p.rx * 0.62))
def _(p):
    r = p.stem * 0.58 + 10
    d = p.rx * 0.30
    y = ACC_Y + 62
    return [dot(-d, y, r), dot(d, y, r)]


@g("dotaccent", 0x2D9, raw=True, adv=lambda p: round(2 * p.rx * 0.40))
def _(p):
    r = p.stem * 0.58 + 10
    return [dot(0, ACC_Y + 62, r)]


@g("ring", 0x2DA, raw=True, adv=lambda p: round(2 * p.rx * 0.52))
def _(p):
    r = 76
    return ring(p, 0, ACC_Y + r + 10, r, r, p.rx_t * 0.74, p.ry_t * 0.74)


@g("macron", 0xAF, raw=True, adv=lambda p: round(2 * p.rx * 0.62))
def _(p):
    w = p.rx * 0.44
    return [rect(-w, ACC_Y + 46, w, ACC_Y + 46 + p.hstem * 0.96)]


@g("breve", 0x2D8, raw=True, adv=lambda p: round(2 * p.rx * 0.62))
def _(p):
    w = p.rx * 0.46
    t = p.hstem * 1.0
    return [arc(p, 0, ACC_Y + 118, w, 96, t, t, D(180), D(360), "r", "r", seg=2)]


@g("cedilla", 0xB8, raw=True, adv=lambda p: round(2 * p.rx * 0.40))
def _(p):
    t = p.stem * 0.72
    r = 62
    a = arc(p, 0, -62 - r, r, r, t, t, D(96), D(-60), "r", "v", seg=2)
    return [rect(-t / 2, -66, t / 2, 8), a]


# ══════════════════════════════════════════════ COMPOSTAS
# base, acento, e se o acento sobe para altura de caixa alta
COMPOSITES = []


def _c(name, uni, base, acc, uc=False):
    COMPOSITES.append((name, uni, base, acc, uc))


for _b, _u in (("A", 0xC0), ("E", 0xC8), ("I", 0xCC), ("O", 0xD2), ("U", 0xD9)):
    _c(_b + "grave", _u, _b, "grave", True)
for _b, _u in (("A", 0xC1), ("E", 0xC9), ("I", 0xCD), ("O", 0xD3), ("U", 0xDA),
               ("Y", 0xDD)):
    _c(_b + "acute", _u, _b, "acute", True)
for _b, _u in (("A", 0xC2), ("E", 0xCA), ("I", 0xCE), ("O", 0xD4), ("U", 0xDB)):
    _c(_b + "circumflex", _u, _b, "circumflex", True)
for _b, _u in (("A", 0xC3), ("N", 0xD1), ("O", 0xD5)):
    _c(_b + "tilde", _u, _b, "tilde", True)
for _b, _u in (("A", 0xC4), ("E", 0xCB), ("I", 0xCF), ("O", 0xD6), ("U", 0xDC)):
    _c(_b + "dieresis", _u, _b, "dieresis", True)
_c("Aring", 0xC5, "A", "ring", True)
_c("Ccedilla", 0xC7, "C", "cedilla", True)
_c("Scaron", 0x160, "S", "caron", True)
_c("Zcaron", 0x17D, "Z", "caron", True)
_c("Ydieresis", 0x178, "Y", "dieresis", True)

for _b, _u in (("a", 0xE0), ("e", 0xE8), ("o", 0xF2), ("u", 0xF9)):
    _c(_b + "grave", _u, _b, "grave")
_c("igrave", 0xEC, "dotlessi", "grave")
for _b, _u in (("a", 0xE1), ("e", 0xE9), ("o", 0xF3), ("u", 0xFA), ("y", 0xFD)):
    _c(_b + "acute", _u, _b, "acute")
_c("iacute", 0xED, "dotlessi", "acute")
for _b, _u in (("a", 0xE2), ("e", 0xEA), ("o", 0xF4), ("u", 0xFB)):
    _c(_b + "circumflex", _u, _b, "circumflex")
_c("icircumflex", 0xEE, "dotlessi", "circumflex")
for _b, _u in (("a", 0xE3), ("n", 0xF1), ("o", 0xF5)):
    _c(_b + "tilde", _u, _b, "tilde")
for _b, _u in (("a", 0xE4), ("e", 0xEB), ("o", 0xF6), ("u", 0xFC), ("y", 0xFF)):
    _c(_b + "dieresis", _u, _b, "dieresis")
_c("idieresis", 0xEF, "dotlessi", "dieresis")
_c("aring", 0xE5, "a", "ring")
_c("ccedilla", 0xE7, "c", "cedilla")
_c("scaron", 0x161, "s", "caron")
_c("zcaron", 0x17E, "z", "caron")


def composites(md, p):
    """Monta as acentuadas como componentes das bases já desenhadas.

    No itálico o acento não pode ser só centralizado na caixa da base: a caixa
    já vem inclinada. Desfaz-se a inclinação na altura do centro da base para
    achar o eixo real, e o acento (que já foi inclinado junto) cai no lugar.
    """
    out = {}
    for name, uni, base, acc, uc in COMPOSITES:
        if base not in md or acc not in md:
            continue
        bpaths, badv = md[base]
        bx0, by0, bx1, by1 = bounds(bpaths)
        dx = (bx0 + bx1) / 2 - p.slant * ((by0 + by1) / 2 - p.pivot)
        dy = (CAP - XH - 16) if (uc and acc != "cedilla") else 0.0
        out[name] = {"parts": [(base, 0, 0), (acc, dx, dy)],
                     "adv": badv, "uni": uni}
    return out
