from nt.baseline import Baselines, instantiate, shape_of
from nt.terms import parse


def test_shape_renames_symbols_consistently():
    tpl, ars = shape_of(parse("f(f(X0, X0), a)"))
    assert tpl == "zzs0(zzs0(X0, X0), zzs1)" and ars == [2, 0]


def test_instantiate_uses_distinct_symbols_most_used_first():
    tpl, ars = shape_of(parse("f(X0, g(X0))"))
    syms = [("m", 2, 1), ("mult", 2, 9), ("inv", 1, 5), ("e", 0, 2)]
    assert instantiate(tpl, ars, syms, 10) == ["mult(X0, inv(X0))", "m(X0, inv(X0))"]
    tpl2, ars2 = shape_of(parse("g(h(X0))"))           # needs two different unary symbols
    assert instantiate(tpl2, ars2, syms, 10) == []      # the problem has only one
    assert instantiate(*shape_of(parse("f(X0, k(X0, X1))")), syms, 10) == \
        ["mult(X0, m(X0, X1))", "m(X0, mult(X0, X1))"]


def test_rankings_prefer_what_helped():
    ex = lambda p, a, lab: {"problem": p, "split": "train", "flatten": True, "weight": "f0.5",
                            "singles": [{"abstraction": a, "label": lab}], "sets": []}
    train = [ex("P1", "f(X0, X0)", "helps"), ex("P2", "f(X0, X0)", "helps"),
             ex("P3", "f(X0, X1)", "neutral"), ex("P4", "g(X0, X0)", "helps")]
    b = Baselines(train)
    syms = [("f", 2, 3), ("h", 2, 1)]
    assert b.rank_name(syms, True) == ["f(X0, X0)"]          # g is not in this problem
    assert b.rank_shape(syms, True)[:2] == ["f(X0, X0)", "h(X0, X0)"]
    assert b.rank_combined(syms, True)[:2] == ["f(X0, X0)", "h(X0, X0)"]
