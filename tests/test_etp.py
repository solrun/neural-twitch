import numpy as np

from nt import etp


def toy_matrix():
    """Laws 1 (x = x), 2 (x = y), 3 <=> 4, 3 => 5, 5 => 7, 6 <=> 2 (degenerate)."""
    n = 7
    T = np.zeros((n, n), dtype=bool)
    edges = [(3, 4), (4, 3), (3, 5), (5, 7), (6, 2), (2, 6)]
    for a, b in edges:
        T[a - 1, b - 1] = True
    T[:, 0] = True                   # everything implies x = x
    T[1, :] = True                   # x = y implies everything
    T[5, :] = True
    np.fill_diagonal(T, True)
    for _ in range(n):               # transitive closure
        T = T | ((T.astype(int) @ T.astype(int)) > 0)
    M = np.where(T, 3, -3).astype(np.int8)
    M[2, 4] = 4                      # 3 => 5 explicit
    return M


def test_select_tiers():
    M = toy_matrix()
    rows, stats = etp.select(M, [0, 0, 2, 2, 1, 3, 2])
    by = {(r["hyp"], r["concl"]): r["tier"] for r in rows}
    assert by[(6, 2)] == "degenerate"
    # classes {3,4} => {5} => {7}: two direct edges and one by chaining
    assert by[(3, 5)] == "hasse"                  # explicit pair preferred
    assert by[(5, 7)] == "hasse"
    assert [t for (a, b), t in by.items() if b == 7 and a in (3, 4)] == ["closure"]
    assert by[(3, 4)] == "equiv" and by[(4, 3)] == "equiv"
    assert all(b != 1 for _, b in by)             # nothing into x = x
    assert all(M[a - 1, b - 1] > 0 for a, b in by)
    assert stats["tiers"] == {"degenerate": 1, "hasse": 2, "closure": 1, "equiv": 2}


def test_problem_text():
    laws = {10: {"id": 10, "formula": "X = m(Y, m(X, Y))"},
            20: {"id": 20, "formula": "m(X, Y) = m(Y, X)"}}
    row = {"hyp": 10, "concl": 20, "tier": "hasse", "code": 4,
           "hyp_class": 1, "concl_class": 2}
    text = etp.problem_text(row, laws)
    assert "cnf(equation10, axiom,\n    X = m(Y, m(X, Y)) )." in text
    assert "cnf(goal, negated_conjecture,\n    m(a, b) != m(b, a) )." in text


def test_parse_law():
    num, formula, vs = etp.parse_law("fof(equation2531, axiom, ![X, Y]: X=m(m(Y, m(m(Y, X), X)), Y)).\n")
    assert (num, formula, vs) == (2531, "X = m(m(Y, m(m(Y, X), X)), Y)", ["X", "Y"])
    assert etp.law_size(formula) == 4


def test_triage_bucket():
    p = lambda f, c: {"flatten": f, "status": "proved", "cps": c}
    t = lambda f: {"flatten": f, "status": "budget", "cps": None}
    assert etp.triage_bucket([p(True, 10), p(False, 20)], 10_000) == "trivial"
    assert etp.triage_bucket([p(True, 10), t(False)], 10_000) == "label"
    assert etp.triage_bucket([p(True, 50_000), p(False, 20)], 10_000) == "label"
    assert etp.triage_bucket([t(True), t(False)], 10_000) == "hard"


def test_is_instance():
    assert etp.is_instance("X = m(X, X)", "m(Y, Y) = Y")                  # flipped
    assert etp.is_instance("m(X, Y) = m(Y, X)", "m(m(X, X), Y) = m(Y, m(X, X))")
    assert not etp.is_instance("m(X, Y) = m(Y, X)", "m(X, Y) = m(X, Y)")   # Y would be both
    assert not etp.is_instance("X = m(X, X)", "X = m(Y, X)")


def test_random_tier():
    M = toy_matrix()
    formulas = ["X = X", "X = Y", "X = m(X, X)", "m(X, X) = X", "X = m(X, m(X, X))",
                "X = m(Y, Z)", "m(X, Y) = m(Y, X)"]
    rows, stats = etp.select(M, [0, 0, 1, 1, 2, 1, 2], formulas, n_random=50, seed=1)
    rnd = [r for r in rows if r["tier"] == "random"]
    other = {(r["hyp"], r["concl"]) for r in rows if r["tier"] != "random"}
    assert rnd and all(not r["instance"] for r in rnd)
    assert all((r["hyp"], r["concl"]) not in other for r in rnd)
    assert all(r["hyp"] not in (2, 6) and r["concl"] != 1 for r in rnd)
    assert all(r["instance"] is not None for r in rows)


def test_known_tier():
    M = toy_matrix()
    formulas = ["X = X", "X = Y", "X = m(X, X)", "m(X, X) = X", "X = m(X, m(X, X))",
                "X = m(Y, Z)", "m(X, Y) = m(Y, X)"]
    known = [{"hyp": "3", "concl": "5", "source": "vampire", "vampire_steps": "12"},  # hasse
             {"hyp": "4", "concl": "5", "source": "vampire", "vampire_steps": "40"},
             {"hyp": "7", "concl": "3", "source": "manual", "vampire_steps": ""}]    # false
    rows, _ = etp.select(M, [0, 0, 1, 1, 2, 1, 2], formulas, known=known)
    k = [r for r in rows if r["tier"] == "known"]
    assert [(r["hyp"], r["concl"], r["source"], r["vampire_steps"]) for r in k] == \
        [(4, 5, "vampire", 40)]


def test_vampire_hard_tier_and_class_count():
    M = toy_matrix()
    formulas = ["X = X", "X = Y", "X = m(X, X)", "m(X, X) = X", "X = m(X, m(X, X))",
                "X = m(Y, Z)", "m(X, Y) = m(Y, X)"]
    known = [{"hyp": "4", "concl": "5", "source": "vampire", "vampire_steps": "40"}]
    hard = [{"hyp": "4", "concl": "5", "source": "vampire_600s", "vampire_steps": "",
             "vampire_time": "31.5"},                                    # already known
            {"hyp": "4", "concl": "7", "source": "vampire_600s", "vampire_steps": "",
             "vampire_time": "40.0"}]
    rows, stats = etp.select(M, [0, 0, 1, 1, 2, 1, 2], formulas, known=known,
                             vampire_hard=hard)
    v = [r for r in rows if r["tier"] == "vampire_hard"]
    assert [(r["hyp"], r["concl"], r["vampire_time"]) for r in v] == [(4, 7, 40.0)]
    assert stats["classes"] == 5          # {1}, {2,6}, {3,4}, {5}, {7}
