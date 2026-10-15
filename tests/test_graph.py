import pytest

from nt import tptp
from nt.graph import (FUNC, VAR, axiomatization_key, build_graph, decode_actions,
                      encode_abstraction, problem_clauses, valid_next)

PROBLEM = """
cnf(assoc, axiom, f(f(X, Y), Z) = f(X, f(Y, Z))).
cnf(unit, axiom, f(e, X) = X).
cnf(hyp, hypothesis, f(a, b) = e).
cnf(goal, negated_conjecture, f(b, a) != e).
"""


@pytest.fixture
def problem(tmp_path):
    p = tmp_path / "P.p"
    p.write_text(PROBLEM)
    return str(p)


def test_graph_shape(problem):
    g = build_graph(problem_clauses(problem, tptp_root=""))
    assert list(zip(g.sym_names, g.sym_arity)) == [("a", 0), ("b", 0), ("e", 0), ("f", 2)]
    assert [r for r, _ in g.eq_feat] == [0, 0, 1, 2]
    assert g.eq_feat[3][1] == 1                       # the goal is a disequation
    # f(f(X,Y),Z) and f(X,f(Y,Z)): 4 terms; f(e,X), e: 2; f(a,b), a, b: 3 (e shared); f(b,a): 1
    assert len(g.term_feat) == 10
    assert g.n_var == 3 + 1                           # X,Y,Z in assoc; X in unit
    assert len(g.edges["side_term"][0]) + len(g.edges["side_var"][0]) == 8


def test_quoted_symbols():
    assert tptp.equation_sides("'>='(A,A) = true") == ("'>='(A,A)", "true", False)
    assert tptp.equation_sides("'==>'(X,Y) != '0'") == ("'==>'(X,Y)", "'0'", True)


def test_axiom_key_ignores_goal_hypotheses_and_renaming(problem, tmp_path):
    other = tmp_path / "Q.p"
    other.write_text("cnf(u, axiom, X = f(e, X)).\ncnf(a2, axiom, f(A, f(B, C)) = f(f(A, B), C)).\n"
                     "cnf(g, negated_conjecture, f(a, a) != a).\n")
    k1 = axiomatization_key(problem_clauses(problem, tptp_root=""))
    k2 = axiomatization_key(problem_clauses(str(other), tptp_root=""))
    assert k1 == k2


@pytest.mark.parametrize("a", ["f(X0, X0)", "f(X0, f(X1, X0))", "f(a, X0)", "f(f(X0, e), X1)"])
def test_round_trip(problem, a):
    g = build_graph(problem_clauses(problem, tptp_root=""))
    acts = encode_abstraction(a, g)
    assert acts is not None and acts[0][0] == FUNC
    assert decode_actions(acts, g) == a


@pytest.mark.parametrize("a", ["X0", "h(X0)", "f(X0)"])
def test_unrepresentable(problem, a):
    g = build_graph(problem_clauses(problem, tptp_root=""))
    assert encode_abstraction(a, g) is None


def test_decode_rejects_ill_formed(problem):
    g = build_graph(problem_clauses(problem, tptp_root=""))
    f = g.sym_names.index("f")
    for bad in ([[VAR, 0]], [[FUNC, f], [VAR, 1], [VAR, 0]], [[FUNC, f], [VAR, 0]],
                [[FUNC, f], [VAR, 0], [VAR, 0], [VAR, 0]]):
        with pytest.raises(ValueError):
            decode_actions(bad, g)


def test_valid_next_masks(problem):
    g = build_graph(problem_clauses(problem, tptp_root=""))
    f = g.sym_names.index("f")
    assert valid_next([], g) == (False, 0)            # root: no variables
    assert valid_next([[FUNC, f]], g) == (True, 0)    # one new slot allowed
    assert valid_next([[FUNC, f], [VAR, 0]], g) == (True, 1)
    assert valid_next([[FUNC, f], [VAR, 0], [VAR, 0]], g) is None
