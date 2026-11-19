# Metodologia

## Ranking
Contagem bruta de comentários positivos premia só quem é grande. Usamos:
- **Proporção positiva suavizada** (Beta/Bayes, prior = média global) → um prato com 8/8 positivos
  não ganha de um com 900/1000.
- **Limite inferior de Wilson (95%)** para o ranking final: pune pouca evidência.
- Pesos: comentário de seguidor orgânico > comentário de conta nova; dedupe por autor;
  descarta spam, sorteio ("marca 3 amigos"), ironia detectada.
- Ranking separado: `restaurante`, `prato`, categorias (doce, café, bar).
- Curadoria humana pode destacar/rebaixar, sempre com o motivo registrado (transparência é o diferencial vs. 50Best).

## Emoção do influenciador + TRIBE v2 — pontos de atenção
**Não consegui ler o post do TRIBE v2 (rede bloqueada); tudo abaixo é premissa a validar.**
- Modelos "brain-predictive" em geral preveem a resposta cerebral *média* de um espectador a um estímulo
  (vídeo/áudio/texto). Isso mede o quanto o *clipe* engaja, não o que o influenciador sente.
  Se for isso, o uso correto é: "engajamento neural previsto do trecho em que ele prova o prato".
- A emoção do influenciador vem de outro modelo (expressão facial + prosódia da fala), e o dado é
  ruidoso: influenciador performa pra câmera. Tratar como **feature auxiliar com peso baixo**, nunca
  como nota principal, até validar contra os comentários.
- Checar: licença/pesos públicos, custo de GPU, e se vale rodar em todo vídeo ou só nos trechos de degustação.

## Legal / risco (resolver antes de escalar)
- Expressão facial inferindo emoção = dado biométrico/sensível na LGPD; a UE restringe reconhecimento
  de emoção. Fazer com consentimento do criador, guardar só o score agregado (não embeddings de rosto).
- Scraping de Instagram/TikTok viola os termos; preferir APIs oficiais, parceria com criadores e
  dados enviados por eles. Comentários têm dados pessoais: anonimizar autor.
- Restaurante avaliado por terceiros: canal de contestação e correção.

## Próximos passos
1. Escolher 1 cidade + 20 criadores (piloto Rio) e definir a fonte de dados legal.
2. Extração de entidades com Claude sobre ~200 vídeos; medir acerto contra rotulagem manual.
3. Validar score vs. avaliação de curadores humanos.
4. Só então testar emoção/TRIBE como feature e medir se melhora a correlação.
