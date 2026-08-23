"""
Coletivo Sans — desenho dos glifos.

Cada letra é uma função do peso. Nada de coordenada solta: tudo sai de p.stem,
p.rx, p.RX etc., o que garante que os seis pesos sejam a mesma letra com outra
espessura — condição para a variável interpolar sem torcer o desenho.
"""
import math
from .core import (UPM, XH, CAP, ASC, DESC, FIG, OS, OSC, SUPER, P, Path,
                   ring, arc, rect, poly, isect, diag, polystroke, dot, shift,
                   mirror, se_pt, se_arc)

TAU = 2 * math.pi
D = math.radians

REG = {}          # nome -> (função, unicode, opções)
ORDER = []        # ordem de gravação


def g(name, uni=None, **opts):
    def deco(fn):
        REG[name] = (fn, uni, opts)
        ORDER.append(name)
        return fn
    return deco


# ══════════════════════════════════════════════ auxiliares de traço
def arm(x_edge, apex_x, y0, y1, t, left=True):
    """x do eixo do braço para que a aresta externa caia em x_edge."""
    hw = t / 2
    for _ in range(5):
        x = x_edge + hw if left else x_edge - hw
        dx, dy = apex_x - x, y1 - y0
        L = math.hypot(dx, dy)
        hw = t * L / (2 * abs(dy)) if dy else t / 2
    return x_edge + hw if left else x_edge - hw


def hw_of(a, b, t):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    return t / 2 if abs(dy) < 1e-6 else t * L / (2 * abs(dy))


def cw(p):     # largura de referência da caixa alta
    return 2 * p.RX


# ══════════════════════════════════════════════ CAIXA ALTA
@g("A", 0x41)
def _(p):
    W = cw(p) * 0.98
    st, hs = p.stem, p.hstem
    hw = hw_of((0, 0), (W / 2, CAP), st)
    body = polystroke([(hw, 0), (W / 2 + hw, CAP), (W - hw, 0)], st,
                      fit={0: ("L", 0, None), 1: ("T", W / 2, CAP),
                           2: ("R", W, None)})
    yb = p.bar_uc * 0.62
    k = W / (2 * CAP)                      # inclinação da aresta externa
    xl = k * (yb + hs / 2)                 # medida no topo da barra: nada sobra
    xr = W - k * (yb + hs / 2)
    bar = rect(xl, yb - hs / 2, xr, yb + hs / 2)
    return [body, bar], p.sbd, p.sbd


@g("B", 0x42)
def _(p):
    st, hs = p.stem, p.hstem
    W = cw(p) * 0.865
    yb = p.bar_uc
    stem = rect(0, 0, st, CAP)
    cx = st * 0.5
    # bojo de cima
    top, bot = CAP + OSC * 0.4, yb - hs / 2
    ryu = (top - bot) / 2
    up = arc(p, cx, bot + ryu, W * 0.905 - cx, ryu, p.rx_t, p.ry_t,
             D(90), D(-90), "r", "r")
    # bojo de baixo
    top2, bot2 = yb + hs / 2, -OSC * 0.4
    ryl = (top2 - bot2) / 2
    lo = arc(p, cx, bot2 + ryl, W - cx, ryl, p.rx_t, p.ry_t,
             D(90), D(-90), "r", "r")
    bar = rect(0, yb - hs / 2, W * 0.80, yb + hs / 2)
    return [stem, up, lo, bar], p.sb, p.sbr


@g("C", 0x43)
def _(p):
    RX, RY = p.RX, p.RY
    a = arc(p, RX, CAP / 2, RX, RY, p.rx_t, p.ry_t, D(60), D(300), "v", "v")
    return [a], p.sbr, p.sbr - 4


@g("D", 0x44)
def _(p):
    st = p.stem
    W = cw(p) * 0.98
    cx = st * 0.5
    ry = CAP / 2 + OSC * 0.35
    stem = rect(0, 0, st, CAP)
    bowl = arc(p, cx, CAP / 2, W - cx, ry, p.rx_t, p.ry_t, D(90), D(-90), "r", "r")
    return [stem, bowl], p.sb, p.sbr


def _EF(p, with_foot):
    st, hs = p.stem, p.hstem
    W = cw(p) * 0.775
    yb = p.bar_uc
    out = [rect(0, 0, st, CAP),
           rect(0, CAP - hs, W, CAP),
           rect(0, yb - hs / 2, W * 0.885, yb + hs / 2)]
    if with_foot:
        out.append(rect(0, 0, W, hs))
    return out


@g("E", 0x45)
def _(p):
    return _EF(p, True), p.sb, p.sb


@g("F", 0x46)
def _(p):
    return _EF(p, False), p.sb, p.sb - 10


@g("G", 0x47)
def _(p):
    RX, RY, hs = p.RX, p.RY, p.hstem
    cy = CAP / 2
    a = arc(p, RX, cy, RX, RY, p.rx_t, p.ry_t, D(60), D(360), "v", "h")
    bar = rect(RX + RX * 0.34, cy - hs, 2 * RX, cy)
    stub = rect(2 * RX - p.rx_t, cy - hs, 2 * RX, cy)
    return [a, bar, stub], p.sbr, p.sb


@g("H", 0x48)
def _(p):
    st, hs = p.stem, p.hstem
    W = cw(p) * 0.90
    yb = p.bar_uc
    return ([rect(0, 0, st, CAP), rect(W - st, 0, W, CAP),
             rect(0, yb - hs / 2, W, yb + hs / 2)], p.sb, p.sb)


@g("I", 0x49)
def _(p):
    return [rect(0, 0, p.stem, CAP)], p.sb + 12, p.sb + 12


@g("J", 0x4A)
def _(p):
    st = p.stem
    W = cw(p) * 0.66
    rx = W / 2
    ry = rx * 1.02
    cy = ry - OSC
    a = arc(p, rx, cy, rx, ry, p.rx_t, p.ry_t, D(0), D(-172), "r", "h")
    stem = rect(W - st, cy, W, CAP)
    return [a, stem], p.sbr, p.sb


@g("K", 0x4B)
def _(p):
    st = p.stem
    W = cw(p) * 0.885
    jy = CAP * 0.455
    up = diag((st * 0.72, jy), (W - hw_of((0, jy), (W, CAP), st), CAP), st)
    lo = diag((st * 0.62, jy), (W - hw_of((0, jy), (W, 0), st * 1.06), 0), st * 1.06)
    return [rect(0, 0, st, CAP), up, lo], p.sb, p.sbd


@g("L", 0x4C)
def _(p):
    W = cw(p) * 0.72
    return [rect(0, 0, p.stem, CAP), rect(0, 0, W, p.hstem)], p.sb, p.sb - 6


@g("M", 0x4D)
def _(p):
    st = p.stem
    W = cw(p) * 1.185
    hw = hw_of((0, CAP), (W / 2, 0), st)
    v = polystroke([(hw, CAP), (W / 2 - hw, 0), (W - hw, CAP)], st,
                   fit={0: ("L", 0, None), 1: ("B", W / 2, 0),
                        2: ("R", W, None)})
    return ([rect(0, 0, st, CAP), rect(W - st, 0, W, CAP), v], p.sb, p.sb)


@g("N", 0x4E)
def _(p):
    st = p.stem
    W = cw(p) * 0.905
    hw = hw_of((0, CAP), (W, 0), st)
    dg = diag((hw, CAP), (W - hw, 0), st)
    return ([rect(0, 0, st, CAP), rect(W - st, 0, W, CAP), dg], p.sb, p.sb)


@g("O", 0x4F)
def _(p):
    return ring(p, p.RX, CAP / 2, p.RX, p.RY, p.rx_t, p.ry_t), p.sbr, p.sbr


@g("P", 0x50)
def _(p):
    st = p.stem
    W = cw(p) * 0.845
    cx = st * 0.5
    bot = CAP * 0.435
    ry = (CAP + OSC * 0.4 - bot) / 2
    bowl = arc(p, cx, bot + ry, W - cx, ry, p.rx_t, p.ry_t, D(90), D(-90), "r", "r")
    return [rect(0, 0, st, CAP), bowl], p.sb, p.sbr


@g("Q", 0x51)
def _(p):
    RX, RY = p.RX, p.RY
    r = ring(p, RX, CAP / 2, RX, RY, p.rx_t, p.ry_t)
    t = diag((RX + RX * 0.24, CAP * 0.30), (RX + RX * 0.94, -CAP * 0.035), p.stem * 0.98)
    return r + [t], p.sbr, p.sbr


@g("R", 0x52)
def _(p):
    st = p.stem
    W = cw(p) * 0.845
    cx = st * 0.5
    bot = CAP * 0.445
    ry = (CAP + OSC * 0.4 - bot) / 2
    bowl = arc(p, cx, bot + ry, W - cx, ry, p.rx_t, p.ry_t, D(90), D(-90), "r", "r")
    WL = cw(p) * 0.90
    leg = diag((st + (W - st) * 0.30, bot + p.hstem * 0.55),
               (WL - hw_of((0, bot), (WL, 0), st), 0), st)
    return [rect(0, 0, st, CAP), bowl, leg], p.sb, p.sbd


def _S(p, H, y0, wr):
    """Espinha do S.

    Dois arcos. O de cima termina no seu ponto mais baixo; o de baixo começa
    no seu mais alto. Se os dois cruzassem na mesma linha, o material de cada
    um ficaria de um lado dela e a barriga do S abriria uma fenda. Por isso o
    bojo de baixo nasce uma espessura acima de onde o de cima morre: as duas
    faixas viram uma só. Um deslocamento horizontal pequeno entre os bojos dá
    a inclinação da espinha.
    """
    ov = OSC * 0.9 if H > 600 else OS * 0.9
    top, bot = y0 + H + ov, y0 - ov
    meet = y0 + H * 0.507
    ty = p.ry_t
    ub = meet - ty / 2                     # borda externa de baixo do bojo alto
    lt = meet + ty / 2                     # borda externa de cima do bojo baixo
    ryu = (top - ub) / 2
    ryl = (lt - bot) / 2
    rx = wr / 2
    d = rx * 0.055
    up = arc(p, rx + d, top - ryu, rx * 0.955 - d, ryu, p.rx_t, ty,
             D(26), D(286), "h", "r", seg=3)
    lo = arc(p, rx - d, bot + ryl, rx - d, ryl, p.rx_t, ty,
             D(106), D(-154), "r", "h", seg=3)
    return [up, lo]


@g("S", 0x53)
def _(p):
    return _S(p, CAP, 0, cw(p) * 0.835), p.sbr, p.sbr


@g("T", 0x54)
def _(p):
    st, hs = p.stem, p.hstem
    W = cw(p) * 0.845
    return ([rect(0, CAP - hs, W, CAP),
             rect(W / 2 - st / 2, 0, W / 2 + st / 2, CAP)], p.sb - 14, p.sb - 14)


@g("U", 0x55)
def _(p):
    st = p.stem
    W = cw(p) * 0.905
    rx = W / 2
    ry = rx * 1.07
    cy = ry - OSC
    a = arc(p, rx, cy, rx, ry, p.rx_t, p.ry_t, D(180), D(360), "r", "r")
    return ([a, rect(0, cy, st, CAP), rect(W - st, cy, W, CAP)], p.sb, p.sb)


@g("V", 0x56)
def _(p):
    W = cw(p) * 0.95
    st = p.stem
    hw = hw_of((0, CAP), (W / 2, 0), st)
    return ([polystroke([(hw, CAP), (W / 2 - hw, -OSC * 0.5), (W - hw, CAP)], st,
                        fit={0: ("L", 0, None), 1: ("B", W / 2, -OSC * 0.5),
                             2: ("R", W, None)})], p.sbd, p.sbd)


@g("W", 0x57)
def _(p):
    W = cw(p) * 1.36
    st = p.stem * 0.97
    hw = hw_of((0, CAP), (W * 0.25, 0), st)
    v1, v2 = W * 0.268, W * 0.732
    vy = -OSC * 0.5
    return ([polystroke([(hw, CAP), (v1 - hw, vy), (W / 2 + hw, CAP),
                         (v2 - hw, vy), (W - hw, CAP)], st,
                        fit={0: ("L", 0, None), 1: ("B", v1, vy),
                             2: ("T", W / 2, CAP), 3: ("B", v2, vy),
                             4: ("R", W, None)})], p.sbd, p.sbd)


@g("X", 0x58)
def _(p):
    W = cw(p) * 0.92
    st = p.stem
    hw = hw_of((0, CAP), (W, 0), st)
    return ([diag((hw, CAP), (W - hw, 0), st), diag((hw, 0), (W - hw, CAP), st)],
            p.sbd, p.sbd)


@g("Y", 0x59)
def _(p):
    W = cw(p) * 0.90
    st = p.stem
    jy = CAP * 0.415
    hw = hw_of((0, CAP), (W / 2, jy), st)
    return ([diag((hw, CAP), (W / 2, jy), st), diag((W - hw, CAP), (W / 2, jy), st),
             rect(W / 2 - st / 2, 0, W / 2 + st / 2, jy)], p.sbd, p.sbd)


@g("Z", 0x5A)
def _(p):
    W = cw(p) * 0.845
    st, hs = p.stem, p.hstem
    hw = hw_of((0, CAP), (W, 0), st)
    return ([rect(0, CAP - hs, W, CAP), rect(0, 0, W, hs),
             diag((W - hw, CAP - hs * 0.35), (hw, hs * 0.35), st)], p.sb - 6, p.sb - 6)


# ══════════════════════════════════════════════ CAIXA BAIXA
def _shoulder(p, rx, up=True, ry_f=0.93):
    """Ombro do n/m/h/u: meia superelipse com as pontas na vertical."""
    ry = p.ry * ry_f
    if up:
        cy = XH + OS - ry
        return arc(p, rx, cy, rx, ry, p.rx_t, p.ry_t, D(180), D(0), "r", "r"), cy
    cy = -OS + ry
    return arc(p, rx, cy, rx, ry, p.rx_t, p.ry_t, D(180), D(360), "r", "r"), cy


@g("a", 0x61)
def _(p):
    rx = p.rx * 0.95
    st = p.stem
    r = ring(p, rx, XH / 2, rx, p.ry, p.rx_t, p.ry_t)
    return r + [rect(2 * rx - st, 0, 2 * rx, XH)], p.sbr, p.sb


@g("b", 0x62)
def _(p):
    rx, st = p.rx, p.stem
    r = ring(p, rx, XH / 2, rx, p.ry, p.rx_t, p.ry_t)
    return [rect(0, 0, st, ASC)] + r, p.sb, p.sbr


@g("c", 0x63)
def _(p):
    rx = p.rx
    return ([arc(p, rx, XH / 2, rx, p.ry, p.rx_t, p.ry_t, D(62), D(298), "v", "v")],
            p.sbr, p.sbr - 4)


@g("d", 0x64)
def _(p):
    rx, st = p.rx, p.stem
    r = ring(p, rx, XH / 2, rx, p.ry, p.rx_t, p.ry_t)
    return r + [rect(2 * rx - st, 0, 2 * rx, ASC)], p.sbr, p.sb


@g("e", 0x65)
def _(p):
    rx, hs = p.rx, p.hstem
    cy = XH / 2
    a = arc(p, rx, cy, rx, p.ry, p.rx_t, p.ry_t, D(0), D(305), "r", "v")
    bar = rect(p.rx_t * 0.55, cy - hs / 2, 2 * rx, cy + hs / 2)
    return [a, bar], p.sbr, p.sbr - 4


@g("f", 0x66)
def _(p):
    st, hs = p.stem, p.hstem
    rx = p.rx * 0.72
    ry = p.ry * 0.72
    cy = ASC - ry
    a = arc(p, rx, cy, rx, ry, p.rx_t, p.ry_t, D(180), D(62), "r", "v")
    stem = rect(0, 0, st, cy + 2)
    bar = rect(-rx * 0.46, XH - hs / 2, rx * 1.30, XH + hs / 2)
    return [a, stem, bar], p.sb - 6, p.sb - 16


@g("g", 0x67)
def _(p):
    rx, st = p.rx * 0.98, p.stem
    r = ring(p, rx, XH / 2, rx, p.ry, p.rx_t, p.ry_t)
    rxt = rx * 0.80
    ryt = 92 + p.stem * 0.16
    cyt = DESC + ryt
    cxt = 2 * rx - rxt
    tail = arc(p, cxt, cyt, rxt, ryt, p.rx_t * 0.94, p.ry_t, D(0), D(-168), "r", "h")
    stem = rect(2 * rx - st, cyt, 2 * rx, XH / 2)
    return r + [stem, tail], p.sbr, p.sb - 4


@g("h", 0x68)
def _(p):
    rx = p.rx * 0.945
    st = p.stem
    sh, cy = _shoulder(p, rx)
    return ([rect(0, 0, st, ASC), sh, rect(2 * rx - st, 0, 2 * rx, cy + 2)],
            p.sb, p.sb)


@g("i", 0x69)
def _(p):
    st = p.stem
    d = dot(st * 0.60, XH + 40 + st * 0.62, st * 0.62)
    return [rect(0, 0, st, XH), d], p.sb + 8, p.sb + 8


@g("dotlessi", 0x131)
def _(p):
    return [rect(0, 0, p.stem, XH)], p.sb + 8, p.sb + 8


@g("j", 0x6A)
def _(p):
    st = p.stem
    rxt = p.rx * 0.66
    ryt = 92 + p.stem * 0.16
    cyt = DESC + ryt
    tail = arc(p, -rxt, cyt, rxt, ryt, p.rx_t * 0.94, p.ry_t, D(0), D(-168),
               "r", "h")
    stem = rect(-st, cyt, 0, XH)
    d = dot(-st * 0.40, XH + 40 + st * 0.62, st * 0.62)
    return [stem, tail, d], p.sb - 40, p.sb - 2


@g("dotlessj", 0x237)
def _(p):
    st = p.stem
    rxt = p.rx * 0.66
    ryt = 92 + p.stem * 0.16
    cyt = DESC + ryt
    tail = arc(p, -rxt, cyt, rxt, ryt, p.rx_t * 0.94, p.ry_t, D(0), D(-168),
               "r", "h")
    return [rect(-st, cyt, 0, XH), tail], p.sb - 40, p.sb - 2


@g("k", 0x6B)
def _(p):
    st = p.stem
    W = p.rx * 1.79
    jy = XH * 0.34
    up = diag((st * 0.70, jy), (W - hw_of((0, jy), (W, XH), st * 0.97), XH), st * 0.97)
    lo = diag((st * 0.60, jy), (W - hw_of((0, jy), (W, 0), st), 0), st)
    return [rect(0, 0, st, ASC), up, lo], p.sb, p.sbd


@g("l", 0x6C)
def _(p):
    return [rect(0, 0, p.stem, ASC)], p.sb + 8, p.sb + 8


@g("m", 0x6D)
def _(p):
    rx = p.rx * 0.905
    st = p.stem
    sh1, cy = _shoulder(p, rx)
    sh2 = shift([_shoulder(p, rx)[0]], 2 * rx - st)[0]
    return ([rect(0, 0, st, cy + 2), sh1,
             rect(2 * rx - st, 0, 2 * rx, cy + 2), sh2,
             rect(4 * rx - 2 * st, 0, 4 * rx - 2 * st + st, cy + 2)],
            p.sb, p.sb)


@g("n", 0x6E)
def _(p):
    rx = p.rx * 0.945
    st = p.stem
    sh, cy = _shoulder(p, rx)
    return ([rect(0, 0, st, cy + 2), sh, rect(2 * rx - st, 0, 2 * rx, cy + 2)],
            p.sb, p.sb)


@g("o", 0x6F)
def _(p):
    return ring(p, p.rx, XH / 2, p.rx, p.ry, p.rx_t, p.ry_t), p.sbr, p.sbr


@g("p", 0x70)
def _(p):
    rx, st = p.rx, p.stem
    r = ring(p, rx, XH / 2, rx, p.ry, p.rx_t, p.ry_t)
    return [rect(0, DESC, st, XH)] + r, p.sb, p.sbr


@g("q", 0x71)
def _(p):
    rx, st = p.rx, p.stem
    r = ring(p, rx, XH / 2, rx, p.ry, p.rx_t, p.ry_t)
    return r + [rect(2 * rx - st, DESC, 2 * rx, XH)], p.sbr, p.sb


@g("r", 0x72)
def _(p):
    st = p.stem
    rx = p.rx * 0.82
    ry = p.ry * 0.93
    cy = XH + OS - ry
    a = arc(p, rx, cy, rx, ry, p.rx_t, p.ry_t, D(180), D(52), "r", "v")
    return [rect(0, 0, st, XH), a], p.sb, p.sb - 20


@g("s", 0x73)
def _(p):
    return _S(p, XH, 0, p.rx * 1.66), p.sbr, p.sbr


@g("t", 0x74)
def _(p):
    st, hs = p.stem, p.hstem
    top = XH + (ASC - XH) * 0.66
    bar = rect(-p.rx * 0.44, XH - hs / 2, p.rx * 0.86, XH + hs / 2)
    return [rect(0, 0, st, top), bar], p.sb - 8, p.sb - 14


@g("u", 0x75)
def _(p):
    rx = p.rx * 0.945
    st = p.stem
    sh, cy = _shoulder(p, rx, up=False)
    return ([sh, rect(0, cy - 2, st, XH), rect(2 * rx - st, 0, 2 * rx, XH)],
            p.sb, p.sb)


@g("v", 0x76)
def _(p):
    W = p.rx * 1.86
    st = p.stem * 0.97
    hw = hw_of((0, XH), (W / 2, 0), st)
    return ([polystroke([(hw, XH), (W / 2 - hw, -OS * 0.4), (W - hw, XH)], st,
                        fit={0: ("L", 0, None), 1: ("B", W / 2, -OS * 0.4),
                             2: ("R", W, None)})], p.sbd, p.sbd)


@g("w", 0x77)
def _(p):
    W = p.rx * 2.66
    st = p.stem * 0.94
    hw = hw_of((0, XH), (W * 0.25, 0), st)
    v1, v2 = W * 0.268, W * 0.732
    vy = -OS * 0.4
    return ([polystroke([(hw, XH), (v1 - hw, vy), (W / 2 + hw, XH),
                         (v2 - hw, vy), (W - hw, XH)], st,
                        fit={0: ("L", 0, None), 1: ("B", v1, vy),
                             2: ("T", W / 2, XH), 3: ("B", v2, vy),
                             4: ("R", W, None)})], p.sbd, p.sbd)


@g("x", 0x78)
def _(p):
    W = p.rx * 1.79
    st = p.stem
    hw = hw_of((0, XH), (W, 0), st)
    return ([diag((hw, XH), (W - hw, 0), st), diag((hw, 0), (W - hw, XH), st)],
            p.sbd, p.sbd)


@g("y", 0x79)
def _(p):
    W = p.rx * 1.86
    st = p.stem * 0.97
    hw = hw_of((0, XH), (W / 2, 0), st)
    xb = W * 0.235
    lon = diag((W - hw, XH), (xb, DESC), st)
    sho = diag((hw, XH), (W * 0.5 + hw * 0.2, 0), st)
    return [lon, sho], p.sbd, p.sbd


@g("z", 0x7A)
def _(p):
    W = p.rx * 1.68
    st, hs = p.stem * 0.97, p.hstem
    hw = hw_of((0, XH), (W, 0), st)
    return ([rect(0, XH - hs, W, XH), rect(0, 0, W, hs),
             diag((W - hw, XH - hs * 0.35), (hw, hs * 0.35), st)], p.sb - 8, p.sb - 8)
