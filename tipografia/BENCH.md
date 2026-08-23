# Bench — Coletivo Sans

Gerado por `python3 tipografia/bench.py`. Todas as medidas em unidades de 1000 por em, salvo indicação.

## 1. O desenho, contra as referências

| fonte | altura-x | caixa alta | haste | av. `o` | av. `n` | av. `m` | av. `0` |
|---|---|---|---|---|---|---|---|
| **Coletivo Sans** | **512** | **706** | **68** | **562** | **561** | **922** | **576** |
| Jost | 460 | 700 | 80 | 546 | 525 | 780 | 600 |
| Poppins | 548 | 698 | 91 | 640 | 640 | 1030 | 628 |
| Montserrat | 525 | 700 | 71 | 627 | 676 | 1061 | 662 |

Largura: o `m` da Coletivo é 96% da média das referências — mais econômica na horizontal, que é o que interessa num app cheio de lista e preço.

## 2. Quanto texto cabe na linha

Largura em px de cada frase a 16px, moldada com kerning (`uharfbuzz`, o mesmo caminho do navegador).

| frase | Coletivo | Jost | Poppins | Montserrat |
|---|---|---|---|---|
| O coletivo tira o intermediário caro do meio… | 314 | 303 | 352 | 350 |
| divide a mesa | 99 | 94 | 113 | 110 |
| R$ 38,90 — 23% de taxa | 168 | 171 | 185 | 187 |
| Não é um dono mais barato. É não ter dono. | 318 | 304 | 352 | 351 |
| Cadastre seu restaurante e comece a vender h… | 362 | 334 | 404 | 394 |

## 3. Cobertura

- Glifos: **229** por peso (230 caracteres mapeados).
- Caracteres distintos usados hoje nas páginas do coletivo: **116**.
- Faltando: **4** — サ ド ン ️ (katakana do letreiro do Rio Sandô e seletor de variação; caem na pilha de fallback, como devem).
- Latin-1 completo: sim.

## 4. Peso dos arquivos

- Variável romana: **36.2 KB** (woff2), cobre os seis pesos de 300 a 900.
- Variável itálica: **33.7 KB**.
- Estáticas: 12 arquivos, 9.1 KB em média.
- Referência Jost variável (9 pesos): 132 KB em TTF, 535 glifos.
- Referência Poppins Regular: 157 KB em TTF, 1060 glifos.

O par que o site carrega (variável romana + itálica) pesa **70 KB**.

## 5. A variável bate com as estáticas?

Cada peso estático é gerado direto do desenho paramétrico e a variável tem um master por peso publicado. Os dois caminhos têm de dar no mesmo desenho — o que sobra é arredondamento de coordenada inteira. Diferença máxima de coordenada, por peso:

| peso | maior diferença | glifo |
|---|---|---|
| 300 | 0.5 un. | zero |
| 400 | 0.0 un. | — |
| 500 | 0.5 un. | zero |
| 600 | 1.1 un. | U |
| 700 | 1.2 un. | dieresis |
| 900 | 0.5 un. | B |

## 6. Rasterização

Todo o mapa de caracteres rasterizado em 11, 13, 16 e 24 px (0.0s): **nenhum glifo vazio ou fora de esquadro**.

## 7. Kerning

- Pares cobertos: **1597** (por classes).
- Tabela GPOS presente em todas as estáticas e nas duas variáveis.

