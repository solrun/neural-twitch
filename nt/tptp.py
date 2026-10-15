"""Minimal TPTP CNF handling for unit-equality problems.

Enough to read a problem (statements, roles, includes), collect the function
symbols of its axioms, and write a variant with a different goal. Not a full
TPTP parser: it assumes CNF unit equalities (`s = t` / `s != t`), which is
what the UEQ problems and Twee's proofs contain.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

from nt.terms import App, ParseError, Var, parse, symbols

_CNF = re.compile(r"^\s*cnf\(\s*([^,\s]+)\s*,\s*([a-z_]+)\s*,(.*)\)\s*$", re.S)
_INCLUDE = re.compile(r"^\s*include\(\s*'([^']+)'", re.S)


@dataclass
class Statement:
    text: str                  # the statement as written, including the final '.'
    kind: str                  # "cnf" | "include" | "other"
    name: str = ""
    role: str = ""
    formula: str = ""          # for cnf
    path: str = ""             # for include


def strip_comments(text: str) -> str:
    """Remove % line comments and /* */ block comments outside quotes."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c in "'\"":
            j = text.find(c, i + 1)
            j = n - 1 if j < 0 else j
            out.append(text[i:j + 1])
            i = j + 1
        elif c == "%":
            j = text.find("\n", i)
            i = n if j < 0 else j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            i = n if j < 0 else j + 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def statements(text: str) -> list[Statement]:
    """Split a TPTP file into top-level statements."""
    text = strip_comments(text)
    out, depth, start, i, n = [], 0, 0, 0, len(text)
    while i < n:
        c = text[i]
        if c in "'\"":
            j = text.find(c, i + 1)
            i = n if j < 0 else j + 1
            continue
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif c == "." and depth == 0:
            raw = text[start:i + 1].strip()
            if raw:
                out.append(_classify(raw))
            start = i + 1
        i += 1
    if text[start:].strip():
        raise ValueError(f"unterminated TPTP statement: {text[start:start + 80]!r}")
    return out


def _classify(raw: str) -> Statement:
    body = raw[:-1]
    m = _CNF.match(body)
    if m:
        return Statement(raw, "cnf", m.group(1), m.group(2), m.group(3).strip())
    m = _INCLUDE.match(body)
    if m:
        return Statement(raw, "include", path=m.group(1))
    return Statement(raw, "other")


def equation_sides(formula: str) -> tuple[str, str, bool] | None:
    """(lhs, rhs, negated) for a unit (dis)equality, or None."""
    f = formula.strip()
    while f.startswith("(") and f.endswith(")") and _balanced(f[1:-1]):
        f = f[1:-1].strip()
    depth, i = 0, 0
    while i < len(f):
        c = f[i]
        if c in "'\"":                    # quoted names such as '>=' or '==>'
            j = f.find(c, i + 1)
            i = len(f) if j < 0 else j + 1
            continue
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif depth == 0 and f.startswith("!=", i):
            return f[:i].strip(), f[i + 2:].strip(), True
        elif depth == 0 and c == "=":
            return f[:i].strip(), f[i + 1:].strip(), False
        i += 1
    return None


def _balanced(s: str) -> bool:
    depth, i = 0, 0
    while i < len(s):
        c = s[i]
        if c in "'\"":
            j = s.find(c, i + 1)
            i = len(s) if j < 0 else j + 1
            continue
        depth += (c == "(") - (c == ")")
        if depth < 0:
            return False
        i += 1
    return depth == 0


def resolve_include(path: str, problem_path: str, tptp_root: str | None) -> str | None:
    for base in filter(None, [tptp_root, os.path.dirname(problem_path)]):
        p = os.path.join(base, path)
        if os.path.exists(p):
            return p
    return None


def axiom_statements(problem_path: str, tptp_root: str | None = None) -> list[Statement]:
    """All non-conjecture cnf statements of a problem, includes expanded.
    Raises FileNotFoundError if an include cannot be found."""
    tptp_root = tptp_root if tptp_root is not None else os.environ.get("TPTP_ROOT")
    out = []
    for st in statements(open(problem_path).read()):
        if st.kind == "include":
            p = resolve_include(st.path, problem_path, tptp_root)
            if p is None:
                raise FileNotFoundError(f"{st.path} (included by {problem_path}); set TPTP_ROOT")
            out += [s for s in statements(open(p).read())
                    if s.kind == "cnf" and s.role != "negated_conjecture"]
        elif st.kind == "cnf" and st.role != "negated_conjecture":
            out.append(st)
    return out


def signature(stmts: list[Statement]) -> dict[str, int]:
    """Function symbols (with arity) occurring in the given cnf statements."""
    sig: dict[str, int] = {}
    for st in stmts:
        sides = equation_sides(st.formula)
        if sides is None:
            continue
        for side in sides[:2]:
            try:
                t = parse(side)
            except ParseError:
                continue
            for f, n in symbols(t):
                sig[f] = n
    return sig


def skolemize(t, mapping: dict[str, str], fresh) -> App:
    if isinstance(t, Var):
        if t.name not in mapping:
            mapping[t.name] = next(fresh)
        return App(mapping[t.name], ())
    return App(t.fn, tuple(skolemize(a, mapping, fresh) for a in t.args))


def with_goal(problem_path: str, lhs: str, rhs: str, comment: str = "",
              goal_name: str = "hindsight_goal", tptp_root: str | None = None) -> str:
    """The problem's text with its negated conjecture(s) replaced by
    `lhs != rhs`, variables skolemized to fresh constants."""
    stmts = statements(open(problem_path).read())
    lt, rt = parse(lhs), parse(rhs)
    # fresh constants must avoid every symbol of the problem (includes too,
    # when they can be found) and of the lemma itself
    try:
        used = set(signature(axiom_statements(problem_path, tptp_root)))
    except FileNotFoundError:
        used = set()
    used |= set(signature([s for s in stmts if s.kind == "cnf"]))
    used |= {f for f, _ in symbols(lt) + symbols(rt)}
    fresh = (c for c in (f"sk{i}" for i in range(1, 10_000)) if c not in used)
    mapping: dict[str, str] = {}
    l = skolemize(lt, mapping, fresh)
    r = skolemize(rt, mapping, fresh)
    header = "".join(f"% {line}\n" for line in comment.splitlines())
    body = [s.text for s in stmts
            if not (s.kind == "cnf" and s.role == "negated_conjecture")]
    body.append(f"cnf({goal_name},negated_conjecture,\n    {l} != {r} ).")
    return header + "\n" + "\n\n".join(body) + "\n"
