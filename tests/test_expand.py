from nt import tptp
from nt.expand import equation_key, parse_lemmas, problem_id
from nt.terms import parse

PROOF = """Axiom 1 (assoc): f(f(X, Y), Z) = f(X, f(Y, Z)).

Lemma 2: f(X, e) = X.
Proof:
  f(X, e)
= { by axiom 1 (assoc) }
  X

Lemma 3:
  f(f(X, Y), f(Z, W)) =
    f(X, f(Y, f(Z, W))).
Proof:
  f(f(X, Y), f(Z, W))

Goal 1 (goal): f(a, b) = f(b, a).
Proof:
  f(a, b)
"""

PROBLEM = """% a comment with a full stop. and (parens
include('Axioms/X.ax').
cnf(ax1, axiom,
    f(X, f(Y, X)) = Y ).
cnf(hyp, hypothesis, f(a, b) = c).
cnf(goal, negated_conjecture,
    f(b, a) != c ).
"""


def test_parse_lemmas_handles_wrapped_statements():
    assert parse_lemmas(PROOF) == [
        (2, "f(X, e)", "X"),
        (3, "f(f(X, Y), f(Z, W))", "f(X, f(Y, f(Z, W)))"),
    ]


def test_equation_key_ignores_names_and_orientation():
    k = equation_key(parse("f(X, Y)"), parse("f(Y, X)"))
    assert k == equation_key(parse("f(B, A)"), parse("f(A, B)"))
    assert k != equation_key(parse("f(X, X)"), parse("X"))


def test_statements_roles_and_comments():
    st = tptp.statements(PROBLEM)
    assert [(s.kind, s.role) for s in st] == [
        ("include", ""), ("cnf", "axiom"), ("cnf", "hypothesis"), ("cnf", "negated_conjecture")]
    assert st[0].path == "Axioms/X.ax"
    assert tptp.equation_sides(st[3].formula) == ("f(b, a)", "c", True)


def test_with_goal_replaces_conjecture_and_skolemizes(tmp_path):
    p = tmp_path / "P.p"
    p.write_text(PROBLEM)
    out = tptp.with_goal(str(p), "f(X, sk1)", "Y", comment="src")
    st = tptp.statements(out)
    goals = [s for s in st if s.role == "negated_conjecture"]
    assert len(goals) == 1
    lhs, rhs, neg = tptp.equation_sides(goals[0].formula)
    assert neg and "X" not in lhs and rhs.startswith("sk") and "sk1" in lhs
    assert lhs.split("(")[1].split(",")[0] not in ("sk1",)   # fresh constant, not the existing sk1
    assert any(s.kind == "include" for s in st)
    assert out.startswith("% src\n")


def test_problem_id_prefixes_domain():
    assert problem_id("1076_102", "ETP") == "ETP-1076_102"
    assert problem_id("GRP001-2", "GRP") == "GRP001-2"
