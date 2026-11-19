"""Score de qualidade a partir de comentários positivos/total."""
from math import sqrt


def wilson_lower_bound(pos: int, total: int, z: float = 1.96) -> float:
    if total == 0:
        return 0.0
    p = pos / total
    d = 1 + z * z / total
    centre = p + z * z / (2 * total)
    margin = z * sqrt((p * (1 - p) + z * z / (4 * total)) / total)
    return (centre - margin) / d


def bayes_mean(pos: int, total: int, prior_mean: float = 0.7, prior_n: int = 20) -> float:
    return (pos + prior_mean * prior_n) / (total + prior_n)


def rank(items: list[dict], min_total: int = 10) -> list[dict]:
    """items: [{name, pos, total}] -> ordenado por limite inferior de Wilson."""
    out = [dict(i, score=wilson_lower_bound(i["pos"], i["total"]))
           for i in items if i["total"] >= min_total]
    return sorted(out, key=lambda i: i["score"], reverse=True)
