# gastro — o inventário vivo da gastronomia (working title)

Evolução do 50Best: em vez de painel de jurados, um inventário contínuo de tudo que
influenciadores de comida postam, estruturado e curado.

## Pipeline
1. **Ingest** — posts/vídeos/comentários de perfis curados (APIs oficiais ou dados com consentimento do criador).
2. **Extract** — transcrição do vídeo + OCR + LLM → restaurante, prato, local, preço (entidades canônicas).
3. **Sentiment** — comentários classificados por (restaurante, prato), com filtro de spam/bot/ironia.
4. **Emotion** — sinal de reação do influenciador ao provar o prato (ver docs/METODOLOGIA.md).
5. **Score** — ranking por restaurante e por prato, com intervalo de confiança.
6. **Curadoria** — humanos validam entidades, resolvem duplicatas e aprovam o que entra no mapa.
7. **Mapa** — web/index.html: melhores pratos, bares, restaurantes, doces, cafés.

## Estrutura
- `db/schema.sql` — Postgres + PostGIS
- `pipeline/scoring.py` — score bayesiano (+ testes em `test_scoring.py`)
- `web/index.html` — protótipo do mapa com dados de exemplo
- `docs/METODOLOGIA.md` — decisões, riscos, legal

## Próximos passos
Ver o fim de docs/METODOLOGIA.md.
