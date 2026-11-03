import random

from nt import reslat as R

X, Y, Z = ("v", "X"), ("v", "Y"), ("v", "Z")


def test_known_rl_and_lg_identities():
    for v in ("rl", "lg"):
        for kind, s, t, truth in R.KNOWN[v]:
            assert R.decide(v, kind, s, t) == truth, (v, R.show(s, v), kind, R.show(t, v))


def test_axioms_are_valid():
    for v in ("rl", "lg"):
        for name, f in R.AXIOMS[v]:
            lhs, rhs = (R.parse(x, v) for x in f.split(" = "))
            assert R.decide(v, "eq", lhs, rhs), name


def test_true_verdicts_hold_in_concrete_algebras():
    rng = random.Random(3)
    for v, algs in (("rl", R.rl_algebras(rng)), ("lg", R.lg_algebras(rng))):
        found = 0
        while found < 15:
            s, t = R.random_term(rng, v, 3, 2), R.random_term(rng, v, 3, 2)
            if R.decide(v, "leq", s, t):
                found += 1
                for name, alg in algs:
                    assert R.holds_in(alg, "leq", s, t, rng, 30), (v, name, s, t)


def test_lg_normal_form_and_order():
    # x v y = x(x^-1 y v e), and e <= |x|
    assert R.decide("lg", "eq", ("join", X, Y),
                    ("mul", X, ("join", ("mul", ("inv", X), Y), R.ONE)))
    assert R.lg_leq(R.ONE, ("join", X, ("inv", X)))
    assert not R.lg_leq(R.ONE, X)


def test_problem_text_is_twitch_format():
    row = {"problem": "RLT-00000", "variety": "rl", "kind": "leq",
           "term": [["mul", X, ["ld", X, Y]], Y]}
    text = R.problem_text(row)
    assert "cnf(goal, negated_conjecture,\n    join(multiply(a,ldiv(a,b)),b) != b )." in text
    assert text.count("axiom") == len(R.AXIOMS["rl"])


def test_canonical_renames_by_first_occurrence():
    s, t = R.canonical("eq", ("meet", Z, Y), ("join", Y, Z))
    assert {R.show(s, "rl"), R.show(t, "rl")} in ({"meet(X,Y)", "join(Y,X)"},
                                                  {"join(X,Y)", "meet(Y,X)"})
    assert R.canonical("eq", ("join", Y, Z), ("meet", Z, Y)) == (s, t)
    assert R.canonical("leq", ("meet", Z, Y), Z) == (("meet", X, Y), X)
