# Coletivo Sans

A letra do coletivo. Família geométrica de **seis pesos** (300–900), cada um com
**itálico**, mais duas **fontes variáveis**. 229 glifos, Latin-1 completo,
kerning por classes, algarismos tabulares. Livre sob a
[SIL Open Font License 1.1](OFL.txt).

Espécime e download: **[coletivo.app/fonte](https://coletivo.app/fonte/)**.
Números medidos: **[BENCH.md](BENCH.md)**.

## Por quê

A marca vinha vestida com Futura — licenciada, emprestada e substituída por
qualquer coisa que o aparelho tivesse à mão. Um mercado que não tem dono também
não devia alugar a própria letra.

## A voz

**Geometria de mesa.** Os redondos não são círculos puros (Futura) nem elipses
moles: são **superelipses de expoente 2,3** — cheias perto da diagonal, quase
retas nos lados, como um tampo redondo de borda viva. Isso põe mais ar dentro da
letra, o que segura o desenho no corpo pequeno da lista de pedidos, e dá à
família um timbre próprio.

| | |
|---|---|
| altura-x | 512 (alta para uma geométrica — Jost tem 460) |
| caixa alta | 706 |
| ascendente / descendente | 740 / −212 |
| haste no Regular | 68 (12,4% da em) |
| avanço do `m` | 922 — mais estreita que Poppins (1030) e Montserrat (1061) |

## Como é feita

Não há coordenada digitada à mão. **Cada letra é uma função do peso**: o mesmo
código desenha o Light e o Black mudando a espessura do traço. É isso que garante
que os seis pesos tenham estrutura de pontos idêntica — condição para a fonte
variável interpolar sem torcer o desenho — e que a variável reproduza as
estáticas ponto a ponto (ver seção 5 do bench).

```
tipografia/
  build.py            # CLI: gera tudo em /fonte
  bench.py            # mede e escreve BENCH.md
  preview.py          # rasteriza provas em PNG (QA visual)
  coletivo/
    core.py           # superelipse, arcos com espessura, traço mitrado, métricas
    glyphs.py         # A–Z, a–z
    extras.py         # algarismos, pontuação, símbolos, acentos, compostas
    features.py       # kerning por classes
    build.py          # masters → estáticas → variável (fvar/gvar/STAT)
```

Três ideias fazem o resto funcionar:

- **Arco com espessura** (`core.arc`) — desenha o traço curvo como duas
  superelipses concêntricas. O expoente da curva interna é resolvido para que a
  espessura na diagonal bata com a dos extremos; sem isso o `o` engorda 7% no
  canto.
- **Corte de terminal perpendicular** — nas laterais do redondo o traço corre na
  vertical, então o corte é horizontal; em cima e embaixo, o contrário. Cortar
  errado é geometricamente impossível (a curva interna não alcança) e produz
  espetos — foi o que quebrou o primeiro `S`.
- **Traço mitrado no referencial de quem percorre** (`core.polystroke`) — A, V,
  W e M nascem de um zigue-zague com deslocamento horizontal. O lado acompanha o
  sentido do traço: descendo, +x é a esquerda de quem anda. Sem esse sinal as
  bordas trocam de lado no bico e o contorno se auto-cruza.

## Gerar

```bash
pip install fonttools brotli
python3 tipografia/build.py                      # → /fonte (woff2 + ttf + css)
python3 tipografia/bench.py                      # → tipografia/BENCH.md
python3 tipografia/preview.py fonte/ttf/ColetivoSans-Regular.ttf prova.png
```

O build leva ~3 s e sai com 14 arquivos: 12 estáticas, 2 variáveis, em TTF e
WOFF2, mais `coletivo-sans.css`.

## Usar no site

Já está ligada em todas as páginas. Em qualquer outro lugar:

```html
<link rel="stylesheet" href="https://coletivo.app/fonte/coletivo-sans.css">
```
```css
body { font-family: var(--fonte-coletivo); }   /* cai em Futura/Century Gothic se faltar */
```

A variável cobre 300–900 num arquivo de 34 KB; qualquer `font-weight` entre eles
vale. Algarismos são tabulares de fábrica — preço em coluna alinha sozinho.

## Licença

SIL Open Font License 1.1, com Reserved Font Name "Coletivo". Pode usar em
qualquer coisa, comercial inclusive; pode modificar e redistribuir; não pode
vender a fonte sozinha. Se derivar, troque o nome.
