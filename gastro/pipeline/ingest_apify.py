"""Lê exports JSON de datasets do Apify (posts + comentários do Instagram/TikTok)
e normaliza para o formato interno. Uso: python ingest_apify.py data/raw/*.json

Campos variam por actor; os mapeamentos abaixo cobrem os nomes mais comuns e
devem ser ajustados ao actor escolhido. Autor do comentário vira hash (privacidade)."""
import hashlib, json, sys


def h(s: str) -> str:
    return hashlib.sha256(("gastro:" + (s or "")).encode()).hexdigest()[:16]


def pick(d: dict, *keys, default=None):
    for k in keys:
        if d.get(k) not in (None, ""):
            return d[k]
    return default


def normalize_post(r: dict) -> dict:
    return {
        "url": pick(r, "url", "postUrl", "webVideoUrl"),
        "creator": pick(r, "ownerUsername", "authorMeta.name", "username"),
        "caption": pick(r, "caption", "text", default=""),
        "posted_at": pick(r, "timestamp", "createTimeISO"),
        "video_url": pick(r, "videoUrl", "mediaUrls"),
        "location": pick(r, "locationName"),
        "comments": [
            {"author_hash": h(pick(c, "ownerUsername", "uniqueId", default="")),
             "body": pick(c, "text", default="")}
            for c in (r.get("latestComments") or r.get("comments") or [])
        ],
    }


if __name__ == "__main__":
    out = []
    for path in sys.argv[1:]:
        with open(path, encoding="utf-8") as f:
            out += [normalize_post(r) for r in json.load(f)]
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
