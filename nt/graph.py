"""Problem graphs and decoder targets for the abstraction generator.

Graph (plan, Phase 2 "Encoder"): one heterogeneous graph per problem, built
from all its clauses with includes expanded.

  node types   eq     one per clause; features [role, negated]
                      role: 0 axiom, 1 hypothesis, 2 goal (negated conjecture)
               term   one per distinct application f(...) or constant;
                      features [number of arguments]
               var    one per variable per clause
               sym    one per function symbol / constant; features [arity];
                      names kept for optional named embeddings
  relations    eq   -side-> term|var   both sides of the equation (unordered)
               term -arg->  term|var   with the argument position
               term -head-> sym

Identical subterms share a node: ground ones across the whole problem,
others within their clause (variables are clause-local). Reverse edges are
left to the model code.

Targets (plan, "Decoder"): an abstraction is emitted in prefix order as a
sequence of actions [kind, index]:
  [0, s]  a function symbol: pointer to sym node s
  [1, k]  a variable: k < number of variables so far reuses slot k,
          k == that number opens a new one
The root must be a symbol and arities are fixed by the symbol table, so a
sequence is well formed exactly when the arity stack empties at its end.
Canonical abstractions (variables X0, X1, ... in first-occurrence order)
encode one-to-one.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field

from nt import tptp
from nt.terms import App, ParseError, Term, Var, parse

ROLES = {"axiom": 0, "hypothesis": 1, "negated_conjecture": 2}
FUNC, VAR = 0, 1


@dataclass
class Clause:
    role: str
    lhs: Term
    rhs: Term
    negated: bool


def problem_clauses(problem_path: str, tptp_root: str | None = None) -> list[Clause]:
    """All unit (dis)equations of a problem, includes expanded.
    Raises FileNotFoundError for a missing include and ValueError for a
    clause that is not a parsable unit equation."""
    tptp_root = tptp_root if tptp_root is not None else os.environ.get("TPTP_ROOT")
    stmts = []
    for st in tptp.statements(open(problem_path).read()):
        if st.kind == "include":
            p = tptp.resolve_include(st.path, problem_path, tptp_root)
            if p is None:
                raise FileNotFoundError(f"{st.path} (included by {problem_path}); set TPTP_ROOT")
            stmts += [s for s in tptp.statements(open(p).read()) if s.kind == "cnf"]
        elif st.kind == "cnf":
            stmts.append(st)
    out = []
    for st in stmts:
        sides = tptp.equation_sides(st.formula)
        if sides is None:
            raise ValueError(f"not a unit equation: {st.name} in {problem_path}")
        try:
            out.append(Clause(st.role, parse(sides[0]), parse(sides[1]), sides[2]))
        except ParseError as e:
            raise ValueError(f"{st.name} in {problem_path}: {e}") from None
    return out


def axiomatization_key(clauses: list[Clause]) -> str:
    """Identifies the theory a problem is posed in: its clauses with role
    'axiom', up to variable renaming and orientation. Hypotheses and goals
    are left out, so problems (and hindsight subproblems) over the same
    axioms share a key and can be kept in the same split."""
    from nt.expand import equation_key        # local import: expand imports heavy modules
    keys = sorted(equation_key(c.lhs, c.rhs) for c in clauses if c.role == "axiom")
    return hashlib.sha1("\n".join(keys).encode()).hexdigest()[:16]


@dataclass
class Graph:
    sym_names: list[str] = field(default_factory=list)
    sym_arity: list[int] = field(default_factory=list)
    eq_feat: list[list[int]] = field(default_factory=list)      # [role, negated]
    term_feat: list[list[int]] = field(default_factory=list)    # [n_args]
    n_var: int = 0
    edges: dict = field(default_factory=dict)                   # name -> [src, dst(, pos)]

    def to_dict(self) -> dict:
        return {"sym_names": self.sym_names, "sym_arity": self.sym_arity,
                "eq_feat": self.eq_feat, "term_feat": self.term_feat,
                "n_var": self.n_var, "edges": self.edges}

    def sym_index(self) -> dict[tuple[str, int], int]:
        return {(n, a): i for i, (n, a) in enumerate(zip(self.sym_names, self.sym_arity))}


def _symbols_of(t: Term, out: dict) -> None:
    if isinstance(t, App):
        out.setdefault((t.fn, len(t.args)), None)
        for a in t.args:
            _symbols_of(a, out)


def build_graph(clauses: list[Clause]) -> Graph:
    g = Graph()
    syms: dict = {}
    for c in clauses:
        _symbols_of(c.lhs, syms)
        _symbols_of(c.rhs, syms)
    for name, arity in sorted(syms):
        g.sym_names.append(name)
        g.sym_arity.append(arity)
    sidx = g.sym_index()
    e = {k: [[], []] for k in ("side_term", "side_var", "head")}
    e.update({k: [[], [], []] for k in ("arg_term", "arg_var")})
    shared: dict = {}                       # key -> term node

    def is_ground(t: Term) -> bool:
        return isinstance(t, App) and all(is_ground(a) for a in t.args)

    def node(t: Term, ci: int, cvars: dict) -> tuple[str, int]:
        if isinstance(t, Var):
            if t.name not in cvars:
                cvars[t.name] = g.n_var
                g.n_var += 1
            return "var", cvars[t.name]
        key = (None if is_ground(t) else ci, str(t))
        if key in shared:
            return "term", shared[key]
        tid = len(g.term_feat)
        shared[key] = tid
        g.term_feat.append([len(t.args)])
        e["head"][0].append(tid)
        e["head"][1].append(sidx[t.fn, len(t.args)])
        for pos, a in enumerate(t.args):
            kind, aid = node(a, ci, cvars)
            rel = e["arg_" + kind]
            rel[0].append(tid)
            rel[1].append(aid)
            rel[2].append(pos)
        return "term", tid

    for ci, c in enumerate(clauses):
        g.eq_feat.append([ROLES.get(c.role, 0), int(c.negated)])
        cvars: dict = {}
        for side in (c.lhs, c.rhs):
            kind, nid = node(side, ci, cvars)
            e["side_" + kind][0].append(ci)
            e["side_" + kind][1].append(nid)
    g.edges = e
    return g


# ------------------------------------------------------------------ targets

def encode_abstraction(abstraction: str, g: Graph) -> list[list[int]] | None:
    """Action sequence for an abstraction, or None if it uses a symbol (or
    arity) the problem does not have, or is not a valid pattern."""
    try:
        t = parse(abstraction)
    except ParseError:
        return None
    if not isinstance(t, App):
        return None                               # bare variable
    sidx = g.sym_index()
    slots: dict[str, int] = {}
    out: list[list[int]] = []

    def go(u: Term) -> bool:
        if isinstance(u, Var):
            if u.name not in slots:
                slots[u.name] = len(slots)
            out.append([VAR, slots[u.name]])
            return True
        s = sidx.get((u.fn, len(u.args)))
        if s is None:
            return False
        out.append([FUNC, s])
        return all(go(a) for a in u.args)

    return out if go(t) else None


def decode_actions(actions: list[list[int]], g: Graph) -> str:
    """Inverse of encode_abstraction; raises ValueError if ill formed."""
    pos = 0
    n_vars = 0

    def go(root: bool) -> Term:
        nonlocal pos, n_vars
        if pos >= len(actions):
            raise ValueError("sequence ends inside a term")
        kind, idx = actions[pos]
        pos += 1
        if kind == VAR:
            if root:
                raise ValueError("root must be a function symbol")
            if not 0 <= idx <= n_vars:
                raise ValueError(f"variable slot {idx} with {n_vars} open")
            if idx == n_vars:
                n_vars += 1
            return Var(f"X{idx}")
        if not 0 <= idx < len(g.sym_names):
            raise ValueError(f"no symbol {idx}")
        return App(g.sym_names[idx], tuple(go(False) for _ in range(g.sym_arity[idx])))

    t = go(True)
    if pos != len(actions):
        raise ValueError("trailing actions")
    return str(t)


def valid_next(actions: list[list[int]], g: Graph) -> tuple[bool, int] | None:
    """What the decoder may emit next, for masking: (variables allowed,
    number of variable slots open), or None if the sequence is complete.
    Symbols are always allowed except that a bare variable cannot be the
    root."""
    need, n_vars = 1, 0
    for kind, idx in actions:
        need -= 1
        if kind == FUNC:
            need += g.sym_arity[idx]
        elif idx == n_vars:
            n_vars += 1
    if need == 0:
        return None
    return (len(actions) > 0, n_vars)
