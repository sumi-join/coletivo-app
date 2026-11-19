from scoring import rank, wilson_lower_bound


def test_pouca_evidencia_perde():
    r = rank([{"name": "A", "pos": 10, "total": 10}, {"name": "B", "pos": 900, "total": 1000}])
    assert r[0]["name"] == "B"


def test_zero():
    assert wilson_lower_bound(0, 0) == 0.0
