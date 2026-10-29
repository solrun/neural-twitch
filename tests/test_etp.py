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


def test_satisfaction_counts():
    # of the 16 magmas on {0, 1}: all satisfy x = x, 8 are commutative, only
    # the left projection satisfies x = x*y, none satisfies x = y
    mags = [etp.all_magmas(2)]
    sat = etp.satisfaction(["X = X", "m(X, Y) = m(Y, X)", "X = m(X, Y)", "X = Y"], mags)
    assert sat.shape == (4, 16)
    assert sat[0].all() and sat[1].sum() == 8 and sat[2].sum() == 1 and not sat[3].any()
    # associativity on {0, 1}: 8 of the 16 tables are semigroups
    assoc = etp.satisfaction(["m(m(X, Y), Z) = m(X, m(Y, Z))"], mags)
    assert assoc.sum() == 8


def test_pairs_problem_text():
    laws = {10: {"id": 10, "formula": "X = m(X, X)"},
            20: {"id": 20, "formula": "m(X, Y) = m(Y, X)"},
            30: {"id": 30, "formula": "m(X, m(X, Y)) = m(Y, m(X, X))"}}
    row = {"hyp": 10, "hyp2": 20, "concl": 30, "tier": "pairs", "code": None,
           "hyp_class": 1, "hyp2_class": 2, "concl_class": 3}
    text = etp.problem_text(row, laws)
    assert "cnf(equation10, axiom," in text and "cnf(equation20, axiom," in text
    assert "m(a, m(a, b)) != m(b, m(a, a))" in text
    assert etp.problem_name(10, 30, 20) == "ETP-10_20_30"


def test_select_pairs_filters():
    import numpy as np
    # laws: 1 x=x, 2 x=y, 3 idempotent, 4 commutative, 5 a consequence of
    # commutativity that this toy matrix does not record, 6 left projection
    formulas = ["X = X", "X = Y", "X = m(X, X)", "m(X, Y) = m(Y, X)",
                "m(X, m(X, Y)) = m(m(Y, X), X)", "X = m(X, Y)"]
    n = len(formulas)
    T = np.eye(n, dtype=bool); T[:, 0] = True; T[1, :] = True
    M = np.where(T, 3, -3).astype(np.int8)
    cls = etp.equivalence_classes(M > 0)
    sat = etp.satisfaction(formulas, [etp.all_magmas(2), etp.all_magmas(3)])
    rows = etp.select_pairs(M, cls, sat, n_pairs=3, per_pair=5, seed=0,
                            sizes=[0] * n, formulas=formulas)
    for r in rows:
        a, b, c = r["hyp"] - 1, r["hyp2"] - 1, r["concl"] - 1
        both = sat[a] & sat[b]
        assert both.any() and not (both & ~sat[c]).any()       # no filter magma refutes
        assert M[a, c] <= 0 and M[b, c] <= 0 and c not in (0, 1)
    # 3 and 4 => 5 is true, so no magma refutes it and it must be a candidate
    assert any((r["hyp"], r["hyp2"], r["concl"]) == (3, 4, 5) for r in rows)


def test_bits_all_rows_compact_summarize(tmp_path):
    import gzip, json, types
    M = toy_matrix()                                  # 7 laws
    etp.write_bits(M, str(tmp_path / etp.BITS_FILE))
    with open(tmp_path / "laws.tsv", "w") as f:
        f.write("id\tclass\tsize\tformula\n")
        for i in range(1, 8):
            f.write(f"{i}\t{i}\t1\tX = X\n")
    laws = etp.load_laws(str(tmp_path / "laws.tsv"))
    rows = list(etp.all_true_rows(str(tmp_path), laws))
    want = {(a + 1, b + 1) for a in range(7) for b in range(7) if a != b and M[a, b] > 0}
    assert {(r["hyp"], r["concl"]) for r in rows} == want
    assert {(r["hyp"], r["concl"]) for r in rows if r["code"] == 4} == {(3, 5)}
    runs = tmp_path / "t_0.jsonl"
    with open(runs, "w") as f:
        for r in rows:
            for flat in (True, False):
                cps = 20_000 if (r["hyp"], r["concl"], flat) == (3, 5, True) else 5
                f.write(json.dumps({"problem": r["problem"], "path": "/x", "flatten": flat,
                                    "status": "proved", "cps": cps, "wall": 0.0123456,
                                    "cpu_seconds": 0.01, "allocated_bytes": 1,
                                    "proof": None}) + "\n")
    etp.cmd_compact(types.SimpleNamespace(runs=[str(runs)], remove=True))
    assert not runs.exists()
    with gzip.open(tmp_path / "t_0.tsv.gz", "rt") as f:
        assert "\t0.01235\t" in f.read()
    etp.cmd_summarize(types.SimpleNamespace(
        runs=[str(tmp_path / "t_0.tsv.gz")], min_cps=10_000, show=5, count_problems=True,
        write_lists=str(tmp_path / "lists")))
    assert open(tmp_path / "lists" / "label.txt").read() == "ETP-3_5\n"
