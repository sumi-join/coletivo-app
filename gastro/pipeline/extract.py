"""Extrai restaurante/prato/categoria + sentimento dos comentários com Claude.
Requer ANTHROPIC_API_KEY. Uso: python ingest_apify.py ... | python extract.py"""
import json, sys
import anthropic

MODEL = "claude-sonnet-5-5"
SYSTEM = """Você estrutura posts de influenciadores de comida do Rio de Janeiro.
Responda SOMENTE JSON: {"venues":[{"name":str,"category":"restaurante|bar|doceria|cafe|padaria|outro",
"neighborhood":str|null,"dishes":[{"name":str,"price_brl":number|null}]}],
"comments":[{"i":int,"sentiment":"pos|neu|neg|spam","about":"venue|dish|other"}]}
Sorteios ("marca amigos"), emoji soltos e bots = spam. Não invente: se não está no post, null."""


def extract(post: dict, client: anthropic.Anthropic) -> dict:
    payload = {"caption": post["caption"], "location": post["location"],
               "comments": [{"i": i, "t": c["body"][:300]} for i, c in enumerate(post["comments"][:150])]}
    msg = client.messages.create(model=MODEL, max_tokens=4000, system=SYSTEM,
                                 messages=[{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}])
    return json.loads(msg.content[0].text)


if __name__ == "__main__":
    client = anthropic.Anthropic()
    for p in json.load(sys.stdin):
        print(json.dumps({"url": p["url"], **extract(p, client)}, ensure_ascii=False))
