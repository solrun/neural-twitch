"""Residuated lattices (RL) and lattice-ordered groups (LG) as unit-equality
problems with known truth.

Both varieties have decidable equational theories, so random equations can be
labelled true or false before Twee sees them, and only true ones become
problems (unlike ETP's pairs, where the truth of the conclusions was unknown).

Deciders (pure Python, no dependencies):

  RL  The cut-free sequent calculus FL (Ono and Komori 1985; Okada and Terui
      1999; the version in Jipsen and Tsinakis, "A survey of residuated
      lattices", 2002, and on Jipsen's page "Deciding equations in residuated
      lattices"). s <= t holds in RL iff the sequent s |- t is provable.
      Backward search with invertible rules first and memoization; every rule
      makes the sequent smaller, so the search terminates.

  LG  Holland and McCleary (1979). Every l-group embeds in the automorphism
      group of a chain (Holland), so e <= t fails in some l-group iff it fails
      at one point p of some Aut(Omega). Write t as a join of meets of
      reduced group words, J_i M_j w_ij. Then e <= t fails at p iff for every
      i some j has p.w_ij < p. Only the finitely many points p.u (u a prefix
      of some w_ij) matter: the inequality fails iff these points can be
      totally preordered so that each variable x acts as a strictly
      order-preserving partial bijection (u -> ux) and every i has a j with
      p.w_ij < p. A finite order-preserving partial bijection of Q extends to
      an automorphism of Q, so such a configuration is a counterexample in
      Aut(Q). The search assigns the points one at a time to a weak order.

Problems are TPTP CNF in Twitch's format (axioms, then the goal negated and
skolemized with a, b, c, ...). The axiomatizations:

  RL  lattice, monoid, multiplication distributing over join on both sides,
      and for each residual x(x\\y) <= y, y <= x\\(xy), x\\y <= x\\(y v z)
      (and mirror images). These give residuation: xy <= z implies
      y <= x\\(xy) <= x\\z, and y <= x\\z implies xy <= x(x\\z) <= z.
  LG  the l-group axioms of TPTP's GRP004-2.ax (group, lattice, and
      multiplication distributing over meet and join on both sides), with
      its symbol names, so these problems share an axiomatization with the
      TPTP lattice-ordered group problems.

Inequalities s <= t are stated as join(s, t) = t.

Usage:

  # random equations, decided, deduplicated; writes data/reslat/<variety>.jsonl.gz
  python -m nt.reslat build --variety rl --count 2000 --seed 0
  python -m nt.reslat build --variety lg --count 2000 --seed 0
  # problem files and a manifest for nt.expand base (as nt.etp write)
  python -m nt.reslat write data/reslat --out-dir $TMPDIR/reslat [--shard K/N]
  # after nt.expand base: trivial / label / open / saturated per variety
  python -m nt.reslat report out/reslat/triage_*.jsonl
  # labels: triage rows of the pool (label problems needing >= 10k CPs
  # under the better setting; pool.txt from report --write-lists), then
  # nt.expand abstract and nt.single_runs --sets as for other problems
  python -m nt.reslat select out/reslat/*.jsonl --problems out/reslat/lists/pool.txt \\
      --out out/reslat/pool_rows.jsonl
  # hint check: the same hand-picked hints for a list of problems, as an
  # nt.single_runs --sets file (base, whole set, each hint alone)
  python -m nt.reslat hints --problems RLT-00999,RLT-02679 --out-dir $NT_STORE/reslat/hints
  # self-test of both deciders against concrete algebras
  python -m nt.reslat selftest

Domains: RLT (residuated lattices), LGR (l-groups). Problem names
RLT-<n> and LGR-<n> follow the order of the selection file.
"""

from __future__ import annotations

import argparse
import collections
import gzip
import itertools
import json
import os
import random
import sys
from fractions import Fraction

# ------------------------------------------------------------------- terms
#
# ('v', 'X') variable, ('1',) unit, ('inv', a), and binary
# ('meet', a, b), ('join', a, b), ('mul', a, b),
# ('ld', a, b) = a\b, ('rd', b, a) = b/a.

ONE = ("1",)
VARS = ("X", "Y", "Z", "W", "U", "V")
SKOLEM = {"X": "a", "Y": "b", "Z": "c", "W": "d", "U": "e", "V": "f"}

SYMBOLS = {
    "rl": {"meet": "meet", "join": "join", "mul": "multiply", "ld": "ldiv", "rd": "rdiv",
           "1": "identity"},
    "lg": {"meet": "greatest_lower_bound", "join": "least_upper_bound", "mul": "multiply",
           "inv": "inverse", "1": "identity"},
}
DOMAIN = {"rl": "RLT", "lg": "LGR"}
OPS = {"rl": ("meet", "join", "mul", "ld", "rd"), "lg": ("meet", "join", "mul", "inv")}

AXIOMS = {
    "rl": [
        ("meet_commutative", "meet(X,Y) = meet(Y,X)"),
        ("join_commutative", "join(X,Y) = join(Y,X)"),
        ("meet_associative", "meet(meet(X,Y),Z) = meet(X,meet(Y,Z))"),
        ("join_associative", "join(join(X,Y),Z) = join(X,join(Y,Z))"),
        ("meet_idempotent", "meet(X,X) = X"),
        ("join_idempotent", "join(X,X) = X"),
        ("meet_absorption", "meet(X,join(X,Y)) = X"),
        ("join_absorption", "join(X,meet(X,Y)) = X"),
        ("multiply_associative", "multiply(multiply(X,Y),Z) = multiply(X,multiply(Y,Z))"),
        ("left_identity", "multiply(identity,X) = X"),
        ("right_identity", "multiply(X,identity) = X"),
        ("multiply_join_left", "multiply(X,join(Y,Z)) = join(multiply(X,Y),multiply(X,Z))"),
        ("multiply_join_right", "multiply(join(Y,Z),X) = join(multiply(Y,X),multiply(Z,X))"),
        ("ldiv_counit", "join(multiply(X,ldiv(X,Y)),Y) = Y"),
        ("ldiv_unit", "meet(Y,ldiv(X,multiply(X,Y))) = Y"),
        ("ldiv_monotone", "meet(ldiv(X,Y),ldiv(X,join(Y,Z))) = ldiv(X,Y)"),
        ("rdiv_counit", "join(multiply(rdiv(Y,X),X),Y) = Y"),
        ("rdiv_unit", "meet(Y,rdiv(multiply(Y,X),X)) = Y"),
        ("rdiv_monotone", "meet(rdiv(Y,X),rdiv(join(Y,Z),X)) = rdiv(Y,X)"),
    ],
    "lg": [  # TPTP GRP004-2.ax (group theory, lattice-ordered)
        ("left_identity", "multiply(identity,X) = X"),
        ("left_inverse", "multiply(inverse(X),X) = identity"),
        ("associativity", "multiply(multiply(X,Y),Z) = multiply(X,multiply(Y,Z))"),
        ("symmetry_of_glb", "greatest_lower_bound(X,Y) = greatest_lower_bound(Y,X)"),
        ("symmetry_of_lub", "least_upper_bound(X,Y) = least_upper_bound(Y,X)"),
        ("associativity_of_glb", "greatest_lower_bound(X,greatest_lower_bound(Y,Z)) = "
                                 "greatest_lower_bound(greatest_lower_bound(X,Y),Z)"),
        ("associativity_of_lub", "least_upper_bound(X,least_upper_bound(Y,Z)) = "
                                 "least_upper_bound(least_upper_bound(X,Y),Z)"),
        ("idempotence_of_lub", "least_upper_bound(X,X) = X"),
        ("idempotence_of_gld", "greatest_lower_bound(X,X) = X"),
        ("lub_absorbtion", "least_upper_bound(X,greatest_lower_bound(X,Y)) = X"),
        ("glb_absorbtion", "greatest_lower_bound(X,least_upper_bound(X,Y)) = X"),
        ("monotony_lub1", "multiply(X,least_upper_bound(Y,Z)) = "
                          "least_upper_bound(multiply(X,Y),multiply(X,Z))"),
        ("monotony_glb1", "multiply(X,greatest_lower_bound(Y,Z)) = "
                          "greatest_lower_bound(multiply(X,Y),multiply(X,Z))"),
        ("monotony_lub2", "multiply(least_upper_bound(Y,Z),X) = "
                          "least_upper_bound(multiply(Y,X),multiply(Z,X))"),
        ("monotony_glb2", "multiply(greatest_lower_bound(Y,Z),X) = "
                          "greatest_lower_bound(multiply(Y,X),multiply(Z,X))"),
    ],
}


def show(t, variety: str, names: dict | None = None) -> str:
    """TPTP prefix syntax; names maps variables (e.g. to Skolem constants)."""
    sym = SYMBOLS[variety]
    if t[0] == "v":
        return names[t[1]] if names else t[1]
    if t[0] == "1":
        return sym["1"]
    return f"{sym[t[0]]}({','.join(show(a, variety, names) for a in t[1:])})"


def size(t) -> int:
    """Number of operation symbols (identity counts as one)."""
    return 0 if t[0] == "v" else 1 + sum(size(a) for a in t[1:])


def variables(t, acc=None) -> list[str]:
    acc = [] if acc is None else acc
    if t[0] == "v":
        if t[1] not in acc:
            acc.append(t[1])
    else:
        for a in t[1:]:
            variables(a, acc)
    return acc


def rename(t, m: dict):
    if t[0] == "v":
        return ("v", m[t[1]])
    return (t[0],) + tuple(rename(a, m) for a in t[1:])


class Budget(Exception):
    """The decider gave up (search too large)."""


# ---------------------------------------------------------------- RL decider

class FL:
    """Proof search in FL (no exchange, weakening or contraction) for the
    language meet, join, mul, ld, rd, 1. prove(G, c): is the sequent G |- c
    provable, i.e. does G1 * ... * Gn <= c hold in every residuated lattice
    (empty product = 1)?"""

    def __init__(self, max_steps: int = 200_000):
        self.memo: dict = {}
        self.steps = 0
        self.max_steps = max_steps

    def prove(self, G: tuple, c) -> bool:
        key = (G, c)
        r = self.memo.get(key)
        if r is None:
            self.steps += 1
            if self.steps > self.max_steps:
                raise Budget
            r = self.memo[key] = self._prove(G, c)
        return r

    def _prove(self, G: tuple, c) -> bool:
        op = c[0]
        # invertible right rules
        if op == "meet":
            return self.prove(G, c[1]) and self.prove(G, c[2])
        if op == "ld":                          # G |- a\b  iff  a,G |- b
            return self.prove((c[1],) + G, c[2])
        if op == "rd":                          # G |- b/a  iff  G,a |- b
            return self.prove(G + (c[2],), c[1])
        # invertible left rules
        for i, f in enumerate(G):
            if f[0] == "1":
                return self.prove(G[:i] + G[i + 1:], c)
            if f[0] == "mul":
                return self.prove(G[:i] + (f[1], f[2]) + G[i + 1:], c)
            if f[0] == "join":
                return (self.prove(G[:i] + (f[1],) + G[i + 1:], c)
                        and self.prove(G[:i] + (f[2],) + G[i + 1:], c))
        # axioms
        if op == "1" and not G:
            return True
        if op == "v" and G == (c,):
            return True
        # non-invertible rules
        if op == "join" and (self.prove(G, c[1]) or self.prove(G, c[2])):
            return True
        if op == "mul":
            for k in range(len(G) + 1):
                if self.prove(G[:k], c[1]) and self.prove(G[k:], c[2]):
                    return True
        for i, f in enumerate(G):
            if f[0] == "meet":
                if (self.prove(G[:i] + (f[1],) + G[i + 1:], c)
                        or self.prove(G[:i] + (f[2],) + G[i + 1:], c)):
                    return True
            elif f[0] == "ld":                  # D, a\b with D |- a: b
                a, b = f[1], f[2]
                for k in range(i + 1):
                    if self.prove(G[k:i], a) and self.prove(G[:k] + (b,) + G[i + 1:], c):
                        return True
            elif f[0] == "rd":                  # b/a, D with D |- a: b
                b, a = f[1], f[2]
                for k in range(i + 1, len(G) + 1):
                    if self.prove(G[i + 1:k], a) and self.prove(G[:i] + (b,) + G[k:], c):
                        return True
        return False


def rl_leq(s, t, max_steps: int = 200_000) -> bool:
    return FL(max_steps).prove((s,), t)


# ---------------------------------------------------------------- LG decider
#
# Words: tuples of (variable, +1 | -1), freely reduced.

def wmul(u: tuple, v: tuple) -> tuple:
    out = list(u)
    for l in v:
        if out and out[-1][0] == l[0] and out[-1][1] == -l[1]:
            out.pop()
        else:
            out.append(l)
    return tuple(out)


def winv(u: tuple) -> tuple:
    return tuple((x, -e) for x, e in reversed(u))


def _absorb(dnf: list) -> list:
    """Join of meets: drop duplicates and any meet that has a sub-meet in the
    list (M <= M' when M contains M')."""
    sets = sorted(set(dnf), key=len)
    out = []
    for m in sets:
        if not any(k <= m for k in out):
            out.append(m)
    return out


def lg_nf(t, cap: int = 4000) -> list[frozenset]:
    """t as a join of meets of reduced words: a list of frozensets of words."""
    op = t[0]
    if op == "v":
        return [frozenset({((t[1], 1),)})]
    if op == "1":
        return [frozenset({()})]
    if op == "join":
        r = lg_nf(t[1], cap) + lg_nf(t[2], cap)
    elif op == "meet":
        r = [a | b for a in lg_nf(t[1], cap) for b in lg_nf(t[2], cap)]
    elif op == "mul":       # (J_i M_j u)(J_k M_l v) = J_{i,k} M_{j,l} uv
        r = [frozenset(wmul(u, v) for u in a for v in b)
             for a in lg_nf(t[1], cap) for b in lg_nf(t[2], cap)]
    elif op == "inv":       # (J_i M_j u)^-1 = M_i J_j u^-1, distributed back
        acc = [frozenset()]
        for m in lg_nf(t[1], cap):
            acc = _absorb([d | {winv(u)} for d in acc for u in m])
            if len(acc) > cap:
                raise Budget
        r = acc
    else:
        raise ValueError(f"not an l-group term: {t!r}")
    r = _absorb(r)
    if len(r) > cap or sum(len(m) for m in r) > 4 * cap:
        raise Budget
    return r


def _configuration_exists(words: frozenset, budget: list) -> bool:
    """Can the points p.u (u a prefix of a word in `words`) be weakly
    ordered so that every variable acts as a strictly order-preserving
    partial bijection and p.w < p for every w in words?"""
    edges = collections.defaultdict(set)
    order, seen = [()], {()}
    for w in sorted(words, key=lambda w: (len(w), w)):   # word by word, so each
        for k in range(len(w)):                          # goal is checked early
            u, v = w[:k], w[:k + 1]
            if v not in seen:
                seen.add(v)
                order.append(v)
            x, e = w[k]
            edges[x].add((u, v) if e == 1 else (v, u))
    index = {n: i for i, n in enumerate(order)}
    # pair constraints: for edges (a,a'), (b,b') of one variable,
    # a < b iff a' < b' and a ~ b iff a' ~ b'; checked once all four are placed
    cons = collections.defaultdict(list)
    for es in edges.values():
        for (a, a2), (b, b2) in itertools.combinations(sorted(es), 2):
            last = max(index[a], index[a2], index[b], index[b2])
            cons[last].append((a, b, a2, b2))
    below = collections.defaultdict(list)     # goals: p.w < p
    for w in words:
        below[index[w]].append(w)

    rank: dict = {(): 0}       # node -> class index; classes kept dense
    classes: list[list] = [[()]]

    def cmp(a, b):
        return (rank[a] > rank[b]) - (rank[a] < rank[b])

    def ok(i):
        for a, b, a2, b2 in cons[i]:
            if cmp(a, b) != cmp(a2, b2):
                return False
        return all(rank[w] < rank[()] for w in below[i])

    def renumber(g):
        for c in range(g, len(classes)):
            for x in classes[c]:
                rank[x] = c

    def place(i) -> bool:
        if i == len(order):
            return True
        budget[0] -= 1
        if budget[0] < 0:
            raise Budget
        n = order[i]
        for slot in range(2 * len(classes) + 1):
            c = slot // 2
            if slot % 2:                       # join an existing class
                classes[c].append(n)
                rank[n] = c
                if ok(i) and place(i + 1):
                    return True
                classes[c].pop()
                del rank[n]
            else:                              # a new class at gap c
                classes.insert(c, [n])
                renumber(c)
                if ok(i) and place(i + 1):
                    return True
                classes.pop(c)
                del rank[n]
                renumber(c)
        return False

    return place(1)


def lg_e_leq(dnf: list, max_nodes: int = 200_000) -> bool:
    """Does e <= J_i M_j w_ij hold in all l-groups? It fails iff for some
    choice of one word w_i per meet there is a configuration with
    p.w_i < p for all i (see the module docstring); only the chosen words'
    points matter, since the variables can then be extended to
    automorphisms of Q. Choices are made meet by meet, and a partial choice
    without a configuration is abandoned (more words only add constraints)."""
    dnf = [m - {()} for m in dnf]               # p.e < p is impossible
    if any(not m for m in dnf):                 # a meet that is just e
        return True
    dnf = sorted(dnf, key=len)
    budget = [max_nodes]
    memo: dict = {}

    def feasible(ws):
        r = memo.get(ws)
        if r is None:
            r = memo[ws] = _configuration_exists(ws, budget)
        return r

    def search(i, chosen) -> bool:              # True: a counterexample exists
        if i == len(dnf):
            return True
        for w in sorted(dnf[i], key=lambda w: (len(w), w)):
            ws = chosen | {w}
            if feasible(ws) and search(i + 1, ws):
                return True
        return False

    return not search(0, frozenset())


def lg_leq(s, t, max_nodes: int = 200_000) -> bool:
    """s <= t in LG iff e <= t s^-1."""
    return lg_e_leq(lg_nf(("mul", t, ("inv", s))), max_nodes)


# ------------------------------------------------------------------ deciding

def decide(variety: str, kind: str, s, t, effort: int = 200_000) -> bool:
    """Truth of s = t (kind 'eq') or s <= t (kind 'leq'); Budget if unsure."""
    leq = (lambda a, b: rl_leq(a, b, effort)) if variety == "rl" else \
          (lambda a, b: lg_leq(a, b, effort))
    if kind == "leq":
        return leq(s, t)
    return leq(s, t) and leq(t, s)


# ---------------------------------------------------------------- generator

def random_term(rng: random.Random, variety: str, ops: int, nvars: int,
                p_one: float = 0.1):
    """A random term with exactly `ops` operation symbols (inverse counts),
    over the first nvars variables."""
    if ops == 0:
        return ONE if rng.random() < p_one else ("v", VARS[rng.randrange(nvars)])
    op = rng.choice(OPS[variety])
    if op == "inv":
        return ("inv", random_term(rng, variety, ops - 1, nvars, p_one))
    k = rng.randrange(ops)
    return (op, random_term(rng, variety, k, nvars, p_one),
            random_term(rng, variety, ops - 1 - k, nvars, p_one))


def is_clean(t) -> bool:
    """No subterm that one axiom step removes: x ^ x, x v x, 1x, x1, 1\\x,
    x/1, (x^-1)^-1, 1^-1. Random terms are full of these, and they only
    pad the size."""
    op = t[0]
    if op in ("v", "1"):
        return True
    args = t[1:]
    if op in ("meet", "join") and args[0] == args[1]:
        return False
    if op == "mul" and ONE in args:
        return False
    if op == "ld" and args[0] == ONE or op == "rd" and args[1] == ONE:
        return False
    if op == "inv" and args[0][0] in ("inv", "1"):
        return False
    return all(is_clean(a) for a in args)


def random_clean_term(rng: random.Random, variety: str, ops: int, nvars: int):
    for _ in range(1000):
        t = random_term(rng, variety, ops, nvars)
        if is_clean(t):
            return t
    raise ValueError(f"no clean term with {ops} operations")


def quick_refute(kind: str, s, t, rng: random.Random, tries: int = 20) -> bool:
    """A cheap counterexample in Z (an l-group and a residuated lattice) with
    small random values; most random equations fail there, which spares the
    decider."""
    vs = variables(t, variables(s))
    alg = Alg((), {"meet": min, "join": max, "mul": lambda x, y: x + y, "1": 0,
                   "inv": lambda x: -x, "ld": lambda x, y: y - x, "rd": lambda y, x: y - x})
    for _ in range(tries):
        env = {x: rng.randint(-4, 4) for x in vs}
        a, b = alg.ev(s, env), alg.ev(t, env)
        if (a > b) if kind == "leq" else (a != b):
            return True
    return False


def canonical(kind: str, s, t):
    """Variables renamed X, Y, ... by first occurrence; an equation is
    oriented so that its key does not depend on the order of the sides."""
    def norm(a, b):
        vs = variables(b, variables(a))
        m = {v: VARS[i] for i, v in enumerate(vs)}
        return rename(a, m), rename(b, m)
    if kind == "leq":
        return norm(s, t)
    return min(norm(s, t), norm(t, s), key=repr)


def goal_sides(kind: str, s, t):
    """The goal as an equation: s <= t becomes join(s, t) = t."""
    return (("join", s, t), t) if kind == "leq" else (s, t)


def cmd_build(args) -> None:
    rng = random.Random(args.seed)
    v = args.variety
    out_path = os.path.join(args.out_dir, f"{v}.jsonl.gz")
    seen, rows, counts = set(), [], collections.Counter()
    tries = 0
    while len(rows) < args.count and tries < args.max_tries:
        tries += 1
        kind = "leq" if rng.random() < args.leq else "eq"
        nvars = rng.randint(args.min_vars, args.max_vars)
        n = rng.randint(args.min_ops, args.max_ops)
        k = rng.randint(1, n - 1) if n > 1 else 1
        s = random_clean_term(rng, v, k, nvars)
        t = random_clean_term(rng, v, n - k, nvars)
        if len(variables(t, variables(s))) < args.min_vars:
            counts["too few variables"] += 1
            continue
        if s == t:
            counts["identical"] += 1
            continue
        s, t = canonical(kind, s, t)
        key = (kind, repr(s), repr(t))
        if key in seen:
            counts["duplicate"] += 1
            continue
        seen.add(key)
        if quick_refute(kind, s, t, rng):
            counts["false"] += 1
            continue
        try:
            truth = decide(v, kind, s, t, args.effort)
        except Budget:
            counts["undecided"] += 1
            continue
        except RecursionError:
            counts["undecided"] += 1
            continue
        counts["true" if truth else "false"] += 1
        if truth:
            rows.append({"kind": kind, "lhs": show(s, v), "rhs": show(t, v),
                         "ops": size(s) + size(t), "vars": len(variables(t, variables(s))),
                         "term": [s, t]})
        if tries % 5000 == 0:
            print(f"  {tries} tried: {dict(counts)}", flush=True)
    os.makedirs(args.out_dir, exist_ok=True)
    dom = DOMAIN[v]
    with gzip.open(out_path, "wt") as f:
        for i, r in enumerate(rows):
            f.write(json.dumps({"problem": f"{dom}-{i:05d}", "variety": v, **r}) + "\n")
    print(f"{v}: {tries} tried, {dict(counts)}; {len(rows)} true -> {out_path}")


# ------------------------------------------------------------------- write

def to_term(x):
    """JSON lists back to tuples."""
    return tuple(to_term(a) if isinstance(a, list) else a for a in x)


def problem_text(row: dict) -> str:
    v = row["variety"]
    s, t = (to_term(x) for x in row["term"])
    gl, gr = goal_sides(row["kind"], s, t)
    rel = "<=" if row["kind"] == "leq" else "="
    lines = [f"% {row['problem']}: {'residuated lattices' if v == 'rl' else 'l-groups'}, "
             f"{show(s, v)} {rel} {show(t, v)}",
             "% generated by nt.reslat; true by the decision procedure "
             f"({'FL sequent calculus' if v == 'rl' else 'Holland-McCleary'})", ""]
    for name, f in AXIOMS[v]:
        lines.append(f"cnf({name}, axiom,\n    {f} ).")
    lines += ["", f"cnf(goal, negated_conjecture,\n    {show(gl, v, SKOLEM)} != "
              f"{show(gr, v, SKOLEM)} ).", ""]
    return "\n".join(lines)


def read_selection(data_dir: str, varieties: list[str]) -> list[dict]:
    rows = []
    for v in varieties:
        p = os.path.join(data_dir, f"{v}.jsonl.gz")
        if os.path.exists(p):
            with gzip.open(p, "rt") as f:
                rows += [json.loads(l) for l in f if l.strip()]
    return rows


def cmd_write(args) -> None:
    rows = read_selection(args.data_dir, args.varieties.split(","))
    if args.problems:
        want = {l.strip() for l in open(args.problems) if l.strip()}
        rows = [r for r in rows if r["problem"] in want]
    if args.sample:
        rows = random.Random(args.seed).sample(rows, min(args.sample, len(rows)))
    rows.sort(key=lambda r: r["problem"])
    if args.shard:
        k, n = (int(x) for x in args.shard.split("/"))
        rows = rows[k::n]
    manifest = args.manifest or os.path.join(args.out_dir, "manifest.jsonl")
    os.makedirs(os.path.dirname(os.path.abspath(manifest)), exist_ok=True)
    with open(manifest, "w") as man:
        for r in rows:
            dom = DOMAIN[r["variety"]]
            d = os.path.join(args.out_dir, dom)
            os.makedirs(d, exist_ok=True)
            path = os.path.abspath(os.path.join(d, r["problem"] + ".p"))
            with open(path, "w") as f:
                f.write(problem_text(r))
            man.write(json.dumps({"problem": r["problem"], "path": path, "domain": dom,
                                  **{k: r[k] for k in ("variety", "kind", "ops", "vars")}})
                      + "\n")
    print(f"{len(rows)} problems -> {args.out_dir}, manifest {manifest}")


# ------------------------------------------------------------------ report

def bucket(runs: list[dict], min_cps: int, max_cps: int) -> str:
    """trivial: proved under every setting with < min_cps CPs; label: proved
    under some setting; saturated: unproved and stopped below the CP budget
    in some run (impossible for a true goal: an axiomatization or decider
    error); open: unproved otherwise."""
    proved = [r for r in runs if r["status"] == "proved"]
    if proved:
        if len(proved) == len(runs) and max(r["cps"] for r in proved) < min_cps:
            return "trivial"
        return "label"
    if any(r["status"] == "saturated" or (r["status"] == "budget" and r.get("cps") is not None
                                          and r["cps"] < max_cps) for r in runs):
        return "saturated"
    return "open"


OPS_BANDS = ((4, 7), (8, 11), (12, 15), (16, 99))
CPS_BANDS = ((0, 10_000), (10_000, 100_000), (100_000, 10**12))


def _band(x, bands) -> str:
    """Inclusive bands; the last one is open-ended."""
    for lo, hi in bands:
        if lo <= x <= hi:
            return f"{lo}-{hi}" if hi < 99 else f"{lo}+"
    return "?"


def _cps_band(x: int) -> str:
    return {0: "<10k", 10_000: "10k-100k", 100_000: ">=100k"}[
        max(lo for lo, _ in CPS_BANDS if x >= lo)]


def cmd_report(args) -> None:
    sel = {r["problem"]: r for r in read_selection(args.data_dir, ["rl", "lg"])}
    runs = collections.defaultdict(list)
    for p in args.runs:
        for line in open(p):
            if line.strip():
                r = json.loads(line)
                if r["status"] != "error":
                    runs[r["problem"]].append(r)
    missing = [p for p in runs if p not in sel]
    if missing:
        raise SystemExit(f"{len(missing)} problems not in {args.data_dir} (e.g. {missing[0]}); "
                         "pass the --data-dir the problems were written from")
    dom = {p: DOMAIN[sel[p]["variety"]] for p in runs}
    buckets = {p: bucket(rs, args.min_cps, args.max_cps) for p, rs in runs.items()}
    names = ("trivial", "label", "open", "saturated")
    doms = sorted(set(dom.values()))

    def table(title, key, keys):
        c = collections.Counter((dom[p], key(p), buckets[p]) for p in buckets)
        print(f"\n{title}")
        print(f"  {'':16s}" + "".join(f"{b:>10s}" for b in names))
        for d in doms:
            for k in keys:
                row = [c[d, k, b] for b in names]
                if sum(row):
                    print(f"  {d + ' ' + str(k):16s}" + "".join(f"{x:10d}" for x in row))

    print(f"{len(buckets)} problems; trivial = proved under every setting with "
          f"< {args.min_cps} CPs; open = unproved within the budget")
    table("by domain", lambda p: "", [""])
    table("by size (operations in both sides)",
          lambda p: _band(sel[p]["ops"], OPS_BANDS),
          [_band(lo, OPS_BANDS) for lo, _ in OPS_BANDS])
    table("by kind", lambda p: sel[p]["kind"], ["eq", "leq"])
    table("by variables", lambda p: sel[p]["vars"], [2, 3])

    # the label bucket split by how hard the problem is for the better
    # setting, and by whether the other setting also proves it
    lab = collections.Counter()
    for p, rs in runs.items():
        if buckets[p] != "label":
            continue
        proved = {r["flatten"]: r["cps"] for r in rs if r["status"] == "proved"}
        which = ("both" if len(proved) == 2 else
                 "flat on only" if True in proved else "flat off only")
        lab[dom[p], _cps_band(min(proved.values())), which] += 1
    whiches = ("both", "flat on only", "flat off only")
    print("\nlabel: CPs of the better setting x which settings prove it")
    print(f"  {'':16s}" + "".join(f"{w:>15s}" for w in whiches))
    for d in doms:
        for band in ("<10k", "10k-100k", ">=100k"):
            print(f"  {d + ' ' + band:16s}" + "".join(f"{lab[d, band, w]:15d}" for w in whiches))

    by = collections.defaultdict(list)
    for p, rs in runs.items():
        for r in rs:
            if r["status"] == "proved":
                by[(dom[p], r["flatten"])].append(r["cps"])
    print("\nproved runs: CPs by flattening (median, 90th percentile, max)")
    for k in sorted(by):
        xs = sorted(by[k])
        print(f"  {k[0]} flat={'on ' if k[1] else 'off'}: n={len(xs):5d} median {xs[len(xs) // 2]:7d} "
              f"p90 {xs[int(0.9 * len(xs))]:7d} max {xs[-1]:7d}")

    if args.write_lists:
        os.makedirs(args.write_lists, exist_ok=True)
        for b in names:
            with open(os.path.join(args.write_lists, f"{b}.txt"), "w") as f:
                f.writelines(f"{p}\n" for p in sorted(buckets) if buckets[p] == b)
        pool = sorted(p for p, rs in runs.items() if buckets[p] == "label"
                      and min(r["cps"] for r in rs if r["status"] == "proved") >= args.min_cps)
        with open(os.path.join(args.write_lists, "pool.txt"), "w") as f:
            f.writelines(f"{p}\n" for p in pool)
        print(f"\nlists -> {args.write_lists}/{{{','.join(names)}}}.txt, and pool.txt: "
              f"{len(pool)} label problems needing >= {args.min_cps} CPs under the better setting")
    if args.show_open:
        print("\nopen problems")
        for p in sorted(b for b in buckets if buckets[b] == "open"):
            r = sel[p]
            rel = "<=" if r["kind"] == "leq" else "="
            print(f"  {p}  {r['lhs']} {rel} {r['rhs']}")


# ------------------------------------------------------- labels and hints

def read_names(spec: str) -> list[str]:
    """Problem names from a file (one per line) or a comma-separated list."""
    if os.path.exists(spec):
        return [l.strip() for l in open(spec) if l.strip()]
    return [x for x in spec.split(",") if x]


def cmd_select(args) -> None:
    """Rows of nt.expand base output (the triage) for the given problems, as
    input for nt.expand abstract and as --calibration for nt.single_runs."""
    want = set(read_names(args.problems))
    n, seen = 0, set()
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as out:
        for p in args.runs:
            for line in open(p):
                if line.strip():
                    r = json.loads(line)
                    if r["problem"] in want:
                        out.write(line if line.endswith("\n") else line + "\n")
                        n += 1
                        seen.add(r["problem"])
    print(f"{n} rows for {len(seen)} of {len(want)} problems -> {args.out}")
    if len(seen) < len(want):
        print(f"  no rows for {len(want) - len(seen)} problems "
              f"(e.g. {sorted(want - seen)[0]})")


# Hand-picked hints for the check that the open problems are hard for want
# of lemmas: the residuation counits, nested residuals (the shape of the
# short open goals) and multiplication over join (monotonicity).
DEFAULT_HINTS = {
    "rl": ["multiply(X0, ldiv(X0, X1))", "multiply(rdiv(X0, X1), X1)",
           "ldiv(X0, rdiv(X1, X2))", "multiply(X0, join(X1, X2))",
           "multiply(join(X0, X1), X2)", "join(multiply(X0, X1), X2)"],
    "lg": ["least_upper_bound(X0, identity)", "greatest_lower_bound(X0, identity)",
           "multiply(X0, least_upper_bound(X1, X2))", "inverse(least_upper_bound(X0, X1))",
           "multiply(X0, inverse(X1))"],
}


def cmd_hints(args) -> None:
    """Problem files and an nt.single_runs --sets file that gives every listed
    problem the same hand-picked hints (base, the whole set, and each hint
    alone)."""
    sel = {r["problem"]: r for r in read_selection(args.data_dir, ["rl", "lg"])}
    names = read_names(args.problems)
    unknown = [p for p in names if p not in sel]
    if unknown:
        raise SystemExit(f"{len(unknown)} problems not in {args.data_dir}: {unknown[:5]}")
    rows = []
    for p in names:
        r = sel[p]
        hints = args.hint or DEFAULT_HINTS[r["variety"]]
        dom = DOMAIN[r["variety"]]
        d = os.path.join(args.out_dir, dom)
        os.makedirs(d, exist_ok=True)
        path = os.path.abspath(os.path.join(d, p + ".p"))
        with open(path, "w") as f:
            f.write(problem_text(r))
        rows.append({"problem": p, "path": path, "domain": dom, "abstractions": hints})
    sets = args.sets or os.path.join(args.out_dir, "hint_sets.jsonl")
    with open(sets, "w") as f:
        f.writelines(json.dumps(r) + "\n" for r in rows)
    print(f"{len(rows)} problems, hints {rows[0]['abstractions'] if rows else []} -> {sets}")


# ------------------------------------------------------- concrete algebras
#
# For the self-test: every equation the deciders call true must hold in these.

class Alg:
    def __init__(self, elems, ops):
        self.elems, self.ops = elems, ops

    def ev(self, t, env):
        if t[0] == "v":
            return env[t[1]]
        if t[0] == "1":
            return self.ops["1"]
        return self.ops[t[0]](*(self.ev(a, env) for a in t[1:]))


def rl_algebras(rng: random.Random) -> list[tuple[str, Alg]]:
    out = []
    n = 4                                   # chains 0..n
    out.append(("Goedel chain", Alg(range(n + 1), {
        "meet": min, "join": max, "mul": min, "1": n,
        "ld": lambda x, y: n if x <= y else y, "rd": lambda y, x: n if x <= y else y})))
    out.append(("Lukasiewicz chain", Alg(range(n + 1), {
        "meet": min, "join": max, "mul": lambda x, y: max(0, x + y - n), "1": n,
        "ld": lambda x, y: min(n, n - x + y), "rd": lambda y, x: min(n, n - x + y)})))
    out.append(("Z", Alg(range(-6, 7), {
        "meet": min, "join": max, "mul": lambda x, y: x + y, "1": 0,
        "ld": lambda x, y: y - x, "rd": lambda y, x: y - x})))
    def sug_mul(x, y):          # odd Sugihara monoid on -2..2, unit 0
        return (x if abs(x) > abs(y) else y) if abs(x) != abs(y) else min(x, y)

    def sug_imp(x, y):
        return max(-x, y) if x <= y else min(-x, y)
    out.append(("Sugihara chain", Alg(range(-2, 3), {
        "meet": min, "join": max, "mul": sug_mul, "1": 0,
        "ld": sug_imp, "rd": lambda y, x: sug_imp(x, y)})))
    # binary relations on a 3-element set: noncommutative
    pts = range(3)
    full = frozenset(itertools.product(pts, pts))

    def comp(r, s):
        return frozenset((a, c) for a, b in r for b2, c in s if b == b2)

    def ld(r, s):     # largest T with r;T <= s
        return frozenset((a, b) for a, b in full if all((c, b) in s for c, a2 in r if a2 == a))

    def rd(s, r):     # largest T with T;r <= s
        return frozenset((a, b) for a, b in full if all((a, c) in s for b2, c in r if b2 == b))
    rels = [frozenset(p for p in full if rng.random() < 0.4) for _ in range(40)]
    out.append(("relations on 3", Alg(rels, {
        "meet": lambda r, s: r & s, "join": lambda r, s: r | s, "mul": comp,
        "1": frozenset((a, a) for a in pts), "ld": ld, "rd": rd})))
    return out


class PL:
    """A piecewise-linear order automorphism of Q: breakpoints (x_i, y_i),
    strictly increasing, slope 1 outside them. Acts on the right:
    p.(fg) = g(f(p))."""

    def __init__(self, pts):
        self.pts = tuple(pts)

    def __call__(self, x):
        p = self.pts
        if not p:
            return x
        if x <= p[0][0]:
            return x + p[0][1] - p[0][0]
        if x >= p[-1][0]:
            return x + p[-1][1] - p[-1][0]
        for (x0, y0), (x1, y1) in zip(p, p[1:]):
            if x0 <= x <= x1:
                return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
        raise AssertionError

    def inv(self):
        return PL((y, x) for x, y in self.pts)

    @staticmethod
    def from_points(xs, f):
        """PL through (x, f(x)), dropping breakpoints where the slope does
        not change (slope 1 counts outside the outermost points)."""
        pts = [(x, f(x)) for x in sorted(set(xs))]
        if not pts:
            return PL(())
        out = []
        for i, (x, y) in enumerate(pts):
            left = (y - pts[i - 1][1]) / (x - pts[i - 1][0]) if i else 1
            right = (pts[i + 1][1] - y) / (pts[i + 1][0] - x) if i + 1 < len(pts) else 1
            if left != right:
                out.append((x, y))
        if not out:         # slope 1 everywhere: a translation
            out = [pts[0]]
        return PL(out)

    def xs(self):
        return [x for x, _ in self.pts]

    def then(self, g):          # x -> g(self(x))
        xs = self.xs() + [self.inv()(x) for x in g.xs()]
        return PL.from_points(xs, lambda x: g(self(x)))

    def lattice(self, g, pick):
        xs = sorted(set(self.xs() + g.xs()))
        extra = []
        if xs:
            ext = [xs[0] - 1] + xs + [xs[-1] + 1]
            for a, b in zip(ext, ext[1:]):
                da, db = self(a) - g(a), self(b) - g(b)
                if da * db < 0:                 # crossing inside (a, b)
                    extra.append(a + (b - a) * da / (da - db))
        return PL.from_points(xs + extra, lambda x: pick(self(x), g(x)))

    def key(self):
        xs = self.xs()
        if not xs:
            return ()
        probe = [xs[0] - 1] + xs + [xs[-1] + 1]
        return tuple(self(x) - x for x in probe)

    def __eq__(self, other):
        xs = sorted(set(self.xs() + other.xs()))
        probe = ([xs[0] - 1] + xs + [xs[-1] + 1]) if xs else [Fraction(0)]
        return all(self(x) == other(x) for x in probe)

    def __hash__(self):
        return 0


def lg_algebras(rng: random.Random) -> list[tuple[str, Alg]]:
    def rand_pl():
        k = rng.randint(1, 3)
        xs = sorted(rng.sample(range(-8, 9), k))
        ys = sorted(rng.sample(range(-8, 9), k))
        return PL((Fraction(x), Fraction(y)) for x, y in zip(xs, ys))
    out = [("Z", Alg(range(-6, 7), {"meet": min, "join": max, "mul": lambda x, y: x + y,
                                     "1": 0, "inv": lambda x: -x})),
           ("Z^2", Alg([(a, b) for a in range(-3, 4) for b in range(-3, 4)], {
               "meet": lambda x, y: (min(x[0], y[0]), min(x[1], y[1])),
               "join": lambda x, y: (max(x[0], y[0]), max(x[1], y[1])),
               "mul": lambda x, y: (x[0] + y[0], x[1] + y[1]), "1": (0, 0),
               "inv": lambda x: (-x[0], -x[1])})),
           ("PL(Q)", Alg([rand_pl() for _ in range(30)], {
               "meet": lambda f, g: f.lattice(g, min), "join": lambda f, g: f.lattice(g, max),
               "mul": lambda f, g: f.then(g), "1": PL(()), "inv": lambda f: f.inv()}))]
    return out


def holds_in(alg: Alg, kind: str, s, t, rng: random.Random, samples: int) -> bool:
    vs = variables(t, variables(s))
    for _ in range(samples):
        env = {v: rng.choice(list(alg.elems)) for v in vs}
        a, b = alg.ev(s, env), alg.ev(t, env)
        if kind == "leq":
            b = alg.ev(t, env)
            if alg.ops["join"](a, b) != b:
                return False
        elif a != b:
            return False
    return True


KNOWN = {
    "rl": [   # (kind, s, t, truth)
        ("leq", ("mul", ("v", "X"), ("ld", ("v", "X"), ("v", "Y"))), ("v", "Y"), True),
        ("eq", ("ld", ("mul", ("v", "X"), ("v", "Y")), ("v", "Z")),
         ("ld", ("v", "Y"), ("ld", ("v", "X"), ("v", "Z"))), True),
        ("eq", ("ld", ("v", "X"), ("rd", ("v", "Y"), ("v", "Z"))),
         ("rd", ("ld", ("v", "X"), ("v", "Y")), ("v", "Z")), True),
        ("leq", ("mul", ("ld", ("v", "X"), ("v", "Y")), ("ld", ("v", "Y"), ("v", "Z"))),
         ("ld", ("v", "X"), ("v", "Z")), True),
        ("eq", ("ld", ("join", ("v", "X"), ("v", "Y")), ("v", "Z")),
         ("meet", ("ld", ("v", "X"), ("v", "Z")), ("ld", ("v", "Y"), ("v", "Z"))), True),
        ("eq", ("mul", ("v", "X"), ("v", "Y")), ("mul", ("v", "Y"), ("v", "X")), False),
        ("leq", ("meet", ("v", "X"), ("join", ("v", "Y"), ("v", "Z"))),
         ("join", ("meet", ("v", "X"), ("v", "Y")), ("meet", ("v", "X"), ("v", "Z"))), False),
        ("leq", ("v", "X"), ONE, False),
        ("leq", ("mul", ("v", "X"), ("v", "X")), ("v", "X"), False),
        ("leq", ONE, ("ld", ("v", "X"), ("v", "X")), True),
    ],
    "lg": [
        ("leq", ("meet", ("v", "X"), ("join", ("v", "Y"), ("v", "Z"))),
         ("join", ("meet", ("v", "X"), ("v", "Y")), ("meet", ("v", "X"), ("v", "Z"))), True),
        ("eq", ("mul", ("v", "X"), ("v", "Y")), ("mul", ("v", "Y"), ("v", "X")), False),
        ("eq", ("mul", ("join", ("v", "X"), ONE), ("meet", ("v", "X"), ONE)), ("v", "X"), True),
        ("eq", ("inv", ("join", ("v", "X"), ("v", "Y"))),
         ("meet", ("inv", ("v", "X")), ("inv", ("v", "Y"))), True),
        ("leq", ONE, ("join", ("v", "X"), ("inv", ("v", "X"))), True),
        ("leq", ONE, ("join", ("v", "X"), ("v", "Y")), False),
        # x^2 ^ e <= x: at a point p, px < p implies pxx < px
        ("leq", ("meet", ("mul", ("v", "X"), ("v", "X")), ONE), ("v", "X"), True),
        ("eq", ("join", ("mul", ("v", "X"), ("v", "Y")), ONE),
         ("join", ("mul", ("v", "Y"), ("v", "X")), ONE), False),
        # x v y = x (x^-1 y v e)
        ("eq", ("join", ("v", "X"), ("v", "Y")),
         ("mul", ("v", "X"), ("join", ("mul", ("inv", ("v", "X")), ("v", "Y")), ONE)), True),
        # (x v e)^n: e <= (x v e) and |x| = x v x^-1 >= e
        ("leq", ("meet", ("v", "X"), ("inv", ("v", "X"))), ONE, True),
    ],
}


def parse(text: str, variety: str):
    """TPTP prefix term (as printed by show) back to a term."""
    inv = {name: op for op, name in SYMBOLS[variety].items()}
    pos = 0

    def term():
        nonlocal pos
        j = pos
        while j < len(text) and (text[j].isalnum() or text[j] == "_"):
            j += 1
        name, pos = text[pos:j], j
        if pos < len(text) and text[pos] == "(":
            pos += 1
            args = [term()]
            while text[pos] == ",":
                pos += 1
                args.append(term())
            pos += 1                                   # ")"
            return (inv[name],) + tuple(args)
        if name == SYMBOLS[variety]["1"]:
            return ONE
        return ("v", name)
    text = text.replace(" ", "")
    t = term()
    assert pos == len(text), text
    return t


def cmd_selftest(args) -> None:
    rng = random.Random(args.seed)
    bad = 0
    for v in ("rl", "lg"):          # the axioms hold (soundness of the problems)
        for name, f in AXIOMS[v]:
            lhs, rhs = (parse(x, v) for x in f.split(" = "))
            if not decide(v, "eq", lhs, rhs):
                bad += 1
                print(f"{v} axiom {name} is not valid: {f}")
    for v in ("rl", "lg"):
        for kind, s, t, truth in KNOWN[v]:
            got = decide(v, kind, s, t)
            if got != truth:
                bad += 1
                print(f"KNOWN {v} WRONG: {show(s, v)} {kind} {show(t, v)}: got {got}")
        algs = rl_algebras(rng) if v == "rl" else lg_algebras(rng)
        counts = collections.Counter()
        for _ in range(args.count):
            kind = "leq" if rng.random() < 0.5 else "eq"
            nvars = rng.randint(1, 3)
            n = rng.randint(2, args.max_ops)
            k = rng.randint(1, n - 1)
            s, t = random_term(rng, v, k, nvars), random_term(rng, v, n - k, nvars)
            try:
                truth = decide(v, kind, s, t)
            except Budget:
                counts["undecided"] += 1
                continue
            counts[truth] += 1
            if truth:
                for name, alg in algs:
                    if not holds_in(alg, kind, s, t, rng, args.samples):
                        bad += 1
                        print(f"{v} decider says true but fails in {name}: "
                              f"{show(s, v)} {kind} {show(t, v)}")
            elif any(not holds_in(alg, kind, s, t, rng, args.samples) for _, alg in algs):
                counts["false, refuted by an algebra"] += 1
            else:
                print(f"  {v} false, no algebra refutes it: {show(s, v)} {kind} {show(t, v)}")
        print(f"{v}: {dict(counts)}")
    print("OK" if not bad else f"{bad} problems")
    sys.exit(1 if bad else 0)


def main() -> None:
    sys.setrecursionlimit(20000)
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="random equations, decided; keeps the true ones")
    b.add_argument("--variety", choices=("rl", "lg"), required=True)
    b.add_argument("--count", type=int, default=1000, help="true equations wanted")
    b.add_argument("--max-tries", type=int, default=10_000_000)
    b.add_argument("--min-ops", type=int, default=4, help="operations in both sides together")
    b.add_argument("--max-ops", type=int, default=10)
    b.add_argument("--max-vars", type=int, default=3)
    b.add_argument("--min-vars", type=int, default=2,
                   help="distinct variables required (one-variable equations are mostly easy)")
    b.add_argument("--leq", type=float, default=0.5, help="share of inequalities")
    b.add_argument("--effort", type=int, default=20_000,
                   help="decider step budget (equations it cannot settle are dropped)")
    b.add_argument("--seed", type=int, default=0)
    b.add_argument("--out-dir", default="data/reslat")
    w = sub.add_parser("write", help="problem files and a manifest for nt.expand base")
    w.add_argument("data_dir", nargs="?", default="data/reslat")
    w.add_argument("--varieties", default="rl,lg")
    w.add_argument("--out-dir", required=True)
    w.add_argument("--problems", default="", help="file with problem names to keep")
    w.add_argument("--sample", type=int, default=0)
    w.add_argument("--seed", type=int, default=0)
    w.add_argument("--shard", default="", metavar="K/N")
    w.add_argument("--manifest", default="")
    r = sub.add_parser("report", help="triage buckets from nt.expand base output")
    r.add_argument("runs", nargs="+")
    r.add_argument("--min-cps", type=int, default=10_000)
    r.add_argument("--max-cps", type=int, default=1_000_000,
                   help="the triage's CP budget (to tell saturation from running out)")
    r.add_argument("--write-lists", default="", metavar="DIR")
    r.add_argument("--data-dir", default="data/reslat",
                   help="selection the problems were written from (sizes, kinds)")
    r.add_argument("--show-open", action="store_true", help="print the open problems")
    sl = sub.add_parser("select", help="triage rows for a list of problems")
    sl.add_argument("runs", nargs="+")
    sl.add_argument("--problems", required=True, help="file (one name per line) or comma list")
    sl.add_argument("--out", required=True)
    hn = sub.add_parser("hints", help="the same hand-picked hints for a list of problems")
    hn.add_argument("--problems", required=True, help="file (one name per line) or comma list")
    hn.add_argument("--hint", action="append", default=[],
                    help="a hint term, e.g. 'multiply(X0, ldiv(X0, X1))' (repeat; "
                         "default: DEFAULT_HINTS for the problem's variety)")
    hn.add_argument("--out-dir", required=True, help="where the problem files go")
    hn.add_argument("--sets", default="", help="default OUT_DIR/hint_sets.jsonl")
    hn.add_argument("--data-dir", default="data/reslat")
    t = sub.add_parser("selftest", help="check both deciders against concrete algebras")
    t.add_argument("--count", type=int, default=500)
    t.add_argument("--max-ops", type=int, default=8)
    t.add_argument("--samples", type=int, default=60)
    t.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    {"build": cmd_build, "write": cmd_write, "report": cmd_report, "select": cmd_select,
     "hints": cmd_hints, "selftest": cmd_selftest}[args.cmd](args)


if __name__ == "__main__":
    main()
