"""
Coletivo Sans — núcleo geométrico.

Tudo é desenhado por parâmetro. Nenhuma coordenada é digitada duas vezes:
cada peso nasce da mesma função, mudando só a espessura do traço. É isso que
garante que os 6 pesos interpolem (mesma estrutura de pontos) e que a fonte
variável seja idêntica às estáticas.

A voz da família é a "geometria de mesa": os redondos não são círculos puros
(Futura) nem elipses moles — são superelipses de expoente 2.3, redondos com o
canto levemente reto, como um tampo de mesa redonda de borda viva.
"""
import math

# ─────────────────────────────────────────── métricas verticais (fixas)
UPM = 1000
XH = 512          # altura-x
CAP = 706         # altura de caixa alta
ASC = 740         # ascendente (b d f h k l)
DESC = -212       # descendente (g j p q y)
FIG = 700         # altura dos algarismos (levemente abaixo da caixa alta)
OS = 9            # transbordo dos redondos de caixa baixa
OSC = 11          # transbordo dos redondos de caixa alta
SUPER = 2.30      # expoente da superelipse — a assinatura da família

# métricas de linha
TYPO_ASC, TYPO_DESC, TYPO_GAP = 980, -270, 0


# ─────────────────────────────────────────── parâmetros por peso
# escada de hastes linear por trechos entre os masters 300/500/700/900,
# de forma que os pesos intermediários (400/600) sejam interpolação exata.
STEM = {300: 46, 400: 68, 500: 90, 600: 114, 700: 138, 800: 158, 900: 178}
# Um master por peso publicado. O corte dos terminais é resolvido por
# bissecção — não é função linear da haste —, então um peso interpolado no
# meio do caminho não bate exatamente com o desenhado. Com master em cada peso
# da família, os seis pesos publicados saem idênticos na variável e na estática.
MASTERS = (300, 400, 500, 600, 700, 900)
INSTANCES = (300, 400, 500, 600, 700, 900)
STYLE_NAME = {300: "Light", 400: "Regular", 500: "Medium",
              600: "SemiBold", 700: "Bold", 900: "Black"}


class P:
    """Parâmetros derivados de um peso. Tudo aqui é linear na haste,
    para que a interpolação entre masters seja exata."""

    def __init__(self, wght, italic=False):
        self.wght = wght
        self.italic = italic
        s = self.stem = STEM[wght]
        d = s - STEM[400]                      # desvio em relação ao Regular

        # horizontais mais finas que as verticais, e a diferença cresce com o
        # peso: no Black, horizontal grossa fecharia o miolo do e e do a.
        self.hstem = s * (0.90 - d * 0.00055)
        self.rx_t = s * 1.02                   # espessura lateral dos redondos
        self.ry_t = self.hstem * 0.96          # espessura topo/base dos redondos
        self.thin = s * 0.86                   # traços finos (barras internas)

        # largura: os pesos pesados abrem para proteger o contraforma
        g = d * 0.26
        self.rx = 248 + g                      # raio horizontal externo (baixa)
        self.ry = XH / 2 + OS                  # raio vertical externo (baixa)
        self.RX = 336 + g * 1.35               # caixa alta
        self.RY = CAP / 2 + OSC
        self.fx = 300 + g * 1.1                # algarismos (mais estreitos)
        self.fy = FIG / 2 + OSC

        # espaçamento: aperta levemente conforme engorda
        self.sb = 46 - d * 0.085               # lateral reta (n, h, i)
        self.sbr = self.sb - 13                # lateral redonda (o, c, e)
        self.sbd = self.sb - 20                # lateral diagonal (v, w, x, y)
        self.sbf = self.sb - 4                 # algarismos

        # itálico
        self.slant = math.tan(math.radians(10.0)) if italic else 0.0
        self.pivot = XH / 2
        if italic:                             # redondos comprimem 3% no itálico
            self.rx *= 0.97
            self.RX *= 0.97
            self.fx *= 0.97

    # alturas de barra — a "linha da mesa": tudo que é travessão mora aqui
    @property
    def bar_uc(self):      # barra de A E F H P R (caixa alta)
        return CAP * 0.512

    @property
    def bar_lc(self):      # barra do e
        return XH * 0.505

    def q(self, v):
        return v


# ─────────────────────────────────────────── caminho (contorno)
class Path:
    """Contorno fechado: um ponto inicial + segmentos ('l', pt) ou ('c', c1, c2, pt)."""

    __slots__ = ("start", "segs")

    def __init__(self, start=None):
        self.start = start
        self.segs = []

    def line(self, pt):
        self.segs.append(("l", pt))
        return self

    def curve(self, c1, c2, pt):
        self.segs.append(("c", c1, c2, pt))
        return self

    def points(self):
        pts = [self.start]
        for s in self.segs:
            pts.append(s[-1])
        return pts

    def sample(self, n=10):
        """Polilinha aproximada — usada para área/orientação."""
        out = [self.start]
        cur = self.start
        for s in self.segs:
            if s[0] == "l":
                out.append(s[1]); cur = s[1]
            else:
                c1, c2, p = s[1], s[2], s[3]
                for i in range(1, n + 1):
                    t = i / n
                    mt = 1 - t
                    x = (mt**3 * cur[0] + 3 * mt * mt * t * c1[0]
                         + 3 * mt * t * t * c2[0] + t**3 * p[0])
                    y = (mt**3 * cur[1] + 3 * mt * mt * t * c1[1]
                         + 3 * mt * t * t * c2[1] + t**3 * p[1])
                    out.append((x, y))
                cur = p
        return out

    def area(self):
        pts = self.sample()
        a = 0.0
        for i in range(len(pts)):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % len(pts)]
            a += x0 * y1 - x1 * y0
        return a / 2.0

    def reversed(self):
        pts = [self.start]
        segs = []
        cur = self.start
        for s in self.segs:
            if s[0] == "l":
                segs.append(("l", cur, None, None, s[1]))
                cur = s[1]
            else:
                segs.append(("c", cur, s[1], s[2], s[3]))
                cur = s[3]
        p = Path(cur)
        for kind, a, c1, c2, b in reversed(segs):
            if kind == "l":
                p.line(a)
            else:
                p.curve(c2, c1, a)
        return p

    def oriented(self, clockwise=True):
        # y para cima: horário => área negativa
        neg = self.area() < 0
        if neg == clockwise:
            return self
        return self.reversed()

    def transform(self, fn):
        p = Path(fn(self.start))
        for s in self.segs:
            if s[0] == "l":
                p.line(fn(s[1]))
            else:
                p.curve(fn(s[1]), fn(s[2]), fn(s[3]))
        return p


# ─────────────────────────────────────────── superelipse
def se_pt(cx, cy, rx, ry, n, a):
    ca, sa = math.cos(a), math.sin(a)
    f = (abs(ca) ** n + abs(sa) ** n) ** (-1.0 / n)
    return (cx + rx * f * ca, cy + ry * f * sa)


def se_tan(cx, cy, rx, ry, n, a, h=1e-5):
    x0, y0 = se_pt(cx, cy, rx, ry, n, a - h)
    x1, y1 = se_pt(cx, cy, rx, ry, n, a + h)
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    return (dx / L, dy / L)


def _fit(p0, t0, p1, t1, m):
    """Cúbica com tangentes dadas cujo ponto médio passa por m."""
    rx = 8 * m[0] - 4 * p0[0] - 4 * p1[0]
    ry = 8 * m[1] - 4 * p0[1] - 4 * p1[1]
    a11, a12 = 3 * t0[0], -3 * t1[0]
    a21, a22 = 3 * t0[1], -3 * t1[1]
    det = a11 * a22 - a12 * a21
    if abs(det) < 1e-9:
        d = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) * 0.36
        d0 = d1 = d
    else:
        d0 = (rx * a22 - a12 * ry) / det
        d1 = (a11 * ry - rx * a21) / det
        lim = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) * 1.6
        d0 = max(0.0, min(d0, lim))
        d1 = max(0.0, min(d1, lim))
    return ((p0[0] + t0[0] * d0, p0[1] + t0[1] * d0),
            (p1[0] - t1[0] * d1, p1[1] - t1[1] * d1))


def se_arc(path, cx, cy, rx, ry, n, a0, a1, nseg=None):
    """Acrescenta um arco de superelipse a `path` (que já começou em se_pt(a0))."""
    if nseg is None:
        nseg = max(1, int(math.ceil(abs(a1 - a0) / (math.pi / 2 * 1.0001))))
    for i in range(nseg):
        b0 = a0 + (a1 - a0) * i / nseg
        b1 = a0 + (a1 - a0) * (i + 1) / nseg
        p0 = se_pt(cx, cy, rx, ry, n, b0)
        p1 = se_pt(cx, cy, rx, ry, n, b1)
        t0 = se_tan(cx, cy, rx, ry, n, b0)
        t1 = se_tan(cx, cy, rx, ry, n, b1)
        if a1 < a0:
            t0 = (-t0[0], -t0[1]); t1 = (-t1[0], -t1[1])
        m = se_pt(cx, cy, rx, ry, n, (b0 + b1) / 2)
        c1, c2 = _fit(p0, t0, p1, t1, m)
        path.curve(c1, c2, p1)
    return path


def n_inner(n, rx, ry, tx, ty):
    """Expoente da superelipse interna que iguala a espessura na diagonal.

    Numa superelipse o raio a 45° é f=2^(1/2-1/n) vezes o dos extremos. Se a
    interna usasse o mesmo expoente, o traço engordaria ~7% justo no canto e o
    'o' ficaria com peso desigual. Aqui se resolve o expoente interno que faz a
    espessura na diagonal bater com a dos extremos.
    """
    r = (rx + ry) / 2.0
    t = (tx + ty) / 2.0
    if r - t <= 8:
        return n
    f_out = 2.0 ** (0.5 - 1.0 / n)
    f_in = (f_out * r - t) / (r - t)
    f_in = min(1.35, max(1.0, f_in))
    ni = 1.0 / (0.5 - math.log(f_in, 2))
    return min(4.0, max(1.7, ni))


# ─────────────────────────────────────────── primitivas
def ring(p, cx, cy, rx, ry, tx, ty, n=SUPER):
    """Anel (redondo com contraforma)."""
    o = Path(se_pt(cx, cy, rx, ry, n, 0))
    se_arc(o, cx, cy, rx, ry, n, 0, 2 * math.pi, 4)
    ni = n_inner(n, rx, ry, tx, ty)
    rxi, ryi = max(6, rx - tx), max(6, ry - ty)
    i = Path(se_pt(cx, cy, rxi, ryi, ni, 0))
    se_arc(i, cx, cy, rxi, ryi, ni, 0, 2 * math.pi, 4)
    return [o.oriented(True), i.oriented(False)]


def _ang_for(cx, cy, rx, ry, n, lo, hi, target, axis):
    """Ângulo dentro de [lo,hi] cujo x (axis=0) ou y (axis=1) vale target."""
    f = lambda a: se_pt(cx, cy, rx, ry, n, a)[axis] - target
    flo, fhi = f(lo), f(hi)
    if flo * fhi > 0:                          # fora de alcance: devolve a borda
        return lo if abs(flo) < abs(fhi) else hi
    for _ in range(60):
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def arc(p, cx, cy, rx, ry, tx, ty, a0, a1, cut0="r", cut1="r", n=SUPER, seg=None):
    """Arco com espessura e terminais cortados na reta.

    cut: 'r' radial, 'v' corte vertical, 'h' corte horizontal.
    """
    ni = n_inner(n, rx, ry, tx, ty)
    rxi, ryi = max(6, rx - tx), max(6, ry - ty)

    def inner_angle(a_out, cut):
        """Ângulo interno que fecha o terminal na reta pedida.

        A busca fica presa ao quadrante do ponto externo: ali x e y são
        monótonos, então a bissecção é válida e, quando a curva interna não
        alcança o alvo (acontece nos pesos gordos, em que o miolo encolhe),
        o resultado é o ponto mais próximo em vez de um ângulo qualquer —
        o terminal vira uma corda, não um espeto.
        """
        if cut == "r":
            return a_out
        po = se_pt(cx, cy, rx, ry, n, a_out)
        axis = 0 if cut == "v" else 1
        q = math.floor(a_out / (math.pi / 2))
        lo, hi = q * (math.pi / 2), (q + 1) * (math.pi / 2)
        return _ang_for(cx, cy, rxi, ryi, ni, lo, hi, po[axis], axis)

    ai0 = inner_angle(a0, cut0)
    ai1 = inner_angle(a1, cut1)
    if seg is None:
        seg = max(1, int(math.ceil(abs(a1 - a0) / (math.pi / 2 * 1.0001))))
    path = Path(se_pt(cx, cy, rx, ry, n, a0))
    se_arc(path, cx, cy, rx, ry, n, a0, a1, seg)
    path.line(se_pt(cx, cy, rxi, ryi, ni, ai1))
    se_arc(path, cx, cy, rxi, ryi, ni, ai1, ai0, seg)
    path.line(se_pt(cx, cy, rx, ry, n, a0))
    return path.oriented(True)


def rect(x0, y0, x1, y1):
    p = Path((x0, y0)).line((x0, y1)).line((x1, y1)).line((x1, y0))
    return p.oriented(True)


def poly(pts):
    p = Path(pts[0])
    for q in pts[1:]:
        p.line(q)
    return p.oriented(True)


def isect(a, b, c, d):
    """Interseção das retas ab e cd."""
    x1, y1 = a; x2, y2 = b; x3, y3 = c; x4, y4 = d
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-9:
        return ((x2 + x3) / 2, (y2 + y3) / 2)
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def hw_for(p0, p1, t):
    """Meia-largura horizontal que dá espessura perpendicular t."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    if abs(dy) < 1e-6:
        return t / 2
    return t * L / (2 * abs(dy))


def diag(p0, p1, t):
    """Traço diagonal com pontas cortadas na horizontal."""
    hw = hw_for(p0, p1, t)
    return poly([(p0[0] - hw, p0[1]), (p0[0] + hw, p0[1]),
                 (p1[0] + hw, p1[1]), (p1[0] - hw, p1[1])])


def diagv(p0, p1, t):
    """Traço diagonal com pontas cortadas na vertical (diagonais rasas)."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    hv = t / 2 if abs(dx) < 1e-6 else t * L / (2 * abs(dx))
    return poly([(p0[0], p0[1] - hv), (p0[0], p0[1] + hv),
                 (p1[0], p1[1] + hv), (p1[0], p1[1] - hv)])


def scaled(paths, k, dx=0.0, dy=0.0, ky=None):
    ky = k if ky is None else ky
    return [q.transform(lambda t: (t[0] * k + dx, t[1] * ky + dy)) for q in paths]


def rot180(paths, cx, cy):
    return [q.transform(lambda t: (2 * cx - t[0], 2 * cy - t[1])) for q in paths]


def bounds(paths):
    xs, ys = [], []
    for q in paths:
        for x, y in q.sample(8):
            xs.append(x); ys.append(y)
    if not xs:
        return (0.0, 0.0, 0.0, 0.0)
    return (min(xs), min(ys), max(xs), max(ys))


def _chains(pts, t):
    """Bordas esquerda/direita do traço, no referencial de quem percorre.

    O deslocamento é horizontal (é o que dá ponta cortada na horizontal e
    mitra exata), mas o lado tem de acompanhar o sentido: descendo, +x é a
    esquerda de quem anda. Sem esse sinal as duas bordas trocam de cadeia no
    bico e o contorno se auto-cruza — o A abria um talho no ápice.
    """
    left, right = [], []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        hw = hw_for(a, b, t)
        sg = 1.0 if b[1] >= a[1] else -1.0
        left.append(((a[0] - hw * sg, a[1]), (b[0] - hw * sg, b[1])))
        right.append(((a[0] + hw * sg, a[1]), (b[0] + hw * sg, b[1])))

    def chain(edges):
        out = [edges[0][0]]
        for i in range(len(edges) - 1):
            out.append(isect(edges[i][0], edges[i][1],
                             edges[i + 1][0], edges[i + 1][1]))
        out.append(edges[-1][1])
        return out

    return chain(left), chain(right)


def _pick(a, b, mode):
    if mode == "L":
        return a if a[0] <= b[0] else b
    if mode == "R":
        return a if a[0] >= b[0] else b
    if mode == "T":
        return a if a[1] >= b[1] else b
    return a if a[1] <= b[1] else b


def polystroke(pts, t, fit=None, iters=12, damp=0.55):
    """Traço em zigue-zague com junções em bico (A, V, W, M, setas).

    `fit` diz onde cada extremidade deve parar: {índice: (modo, x, y)}, com
    modo em L/R/T/B — o ponto mais à esquerda, à direita, mais alto ou mais
    baixo daquele vértice. Como os braços de um W não são simétricos, o bico
    mitrado não cai sozinho no lugar; o eixo é reajustado até bater.
    """
    pts = [tuple(q) for q in pts]
    base = list(pts)

    def sane(ch):
        return all(abs(q[0]) < 4000 and abs(q[1]) < 4000 for q in ch)

    if fit:
        for _ in range(iters):
            L, R = _chains(pts, t)
            if not (sane(L) and sane(R)):        # traço muito grosso para o
                pts = list(base)                 # ângulo: desiste do ajuste
                break
            for i, (mode, tx, ty) in fit.items():
                cur = _pick(L[i], R[i], mode)
                dx = 0.0 if tx is None else (tx - cur[0]) * damp
                dy = 0.0 if ty is None else (ty - cur[1]) * damp
                dx = max(-260.0, min(260.0, dx))
                dy = max(-260.0, min(260.0, dy))
                pts[i] = (pts[i][0] + dx, pts[i][1] + dy)
        L, R = _chains(pts, t)
        if not (sane(L) and sane(R)):
            pts = base
    L, R = _chains(pts, t)
    return poly(L + R[::-1])


def dot(cx, cy, r, n=SUPER):
    p = Path(se_pt(cx, cy, r, r, n, 0))
    se_arc(p, cx, cy, r, r, n, 0, 2 * math.pi, 4)
    return p.oriented(True)


# ─────────────────────────────────────────── glifo
class Glyph:
    __slots__ = ("paths", "adv", "name")

    def __init__(self, name, paths, adv):
        self.name = name
        self.paths = paths
        self.adv = adv


def shift(paths, dx, dy=0.0):
    return [p.transform(lambda q: (q[0] + dx, q[1] + dy)) for p in paths]


def mirror(paths, axis_x):
    out = []
    for p in paths:
        out.append(p.transform(lambda q: (2 * axis_x - q[0], q[1])).oriented(
            p.area() < 0))
    return out


def slantify(paths, p):
    if not p.slant:
        return paths
    s, pv = p.slant, p.pivot
    return [q.transform(lambda t: (t[0] + s * (t[1] - pv), t[1])) for q in paths]
