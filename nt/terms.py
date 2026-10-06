"""First-order term patterns used as Twitch/Twee abstractions.

An abstraction is a first-order term over the problem's function symbols and
pattern variables, e.g. ``f(X, X)``. This module gives one canonical
representation so abstractions can be compared, deduplicated and fed to a
model:

* parsing of the TPTP-style strings Twitch writes (``fn_2(A) = f(A, A)``),
* alpha-normalisation (variables renamed X0, X1, ... in first-occurrence
  order), so ``f(A, A)`` and ``f(B, B)`` are the same abstraction,
* the quantities Twee's weighting uses: size, skeleton weight, nonlinearity.

Conventions follow TPTP: identifiers starting with an upper-case letter or
``_`` are variables, everything else is a function symbol or constant.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

_TOKEN = re.compile(r"\s*([A-Za-z_$][A-Za-z0-9_$]*|'[^']*'|\(|\)|,)")


@dataclass(frozen=True)
class Var:
    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class App:
    fn: str
    args: tuple["Term", ...] = ()

    def __str__(self) -> str:
        if not self.args:
            return self.fn
        return f"{self.fn}({', '.join(map(str, self.args))})"


Term = Var | App


class ParseError(ValueError):
    pass


def _tokenize(s: str) -> list[str]:
    toks, pos = [], 0
    s = s.strip()
    while pos < len(s):
        m = _TOKEN.match(s, pos)
        if not m:
            raise ParseError(f"cannot tokenize {s!r} at {pos}")
        toks.append(m.group(1))
        pos = m.end()
    return toks


def _is_var(tok: str) -> bool:
    return tok[0].isupper() or tok[0] == "_"


def parse(s: str) -> Term:
    """Parse a first-order term. Raises ParseError on higher-order syntax
    (a variable applied to arguments, as Stitch sometimes produces)."""
    toks = _tokenize(s)
    pos = 0

    def term() -> Term:
        nonlocal pos
        if pos >= len(toks):
            raise ParseError(f"unexpected end in {s!r}")
        tok = toks[pos]
        pos += 1
        if tok in "(),":
            raise ParseError(f"unexpected {tok!r} in {s!r}")
        args: list[Term] = []
        if pos < len(toks) and toks[pos] == "(":
            pos += 1
            args.append(term())
            while toks[pos] == ",":
                pos += 1
                args.append(term())
            if toks[pos] != ")":
                raise ParseError(f"expected ')' in {s!r}")
            pos += 1
        if _is_var(tok):
            if args:
                raise ParseError(f"higher-order application of {tok} in {s!r}")
            return Var(tok)
        return App(tok, tuple(args))

    t = term()
    if pos != len(toks):
        raise ParseError(f"trailing input in {s!r}")
    return t


def parse_definition(s: str) -> tuple[str, Term]:
    """Parse a Twitch line ``fn_2(A) = f(A, A)`` into (name, body)."""
    lhs, sep, rhs = s.partition("=")
    if not sep:
        raise ParseError(f"no '=' in {s!r}")
    name = lhs.strip().split("(")[0].strip()
    return name, parse(rhs)


def variables(t: Term) -> list[str]:
    """Variable occurrences in left-to-right order (with repeats)."""
    if isinstance(t, Var):
        return [t.name]
    out: list[str] = []
    for a in t.args:
        out.extend(variables(a))
    return out


def symbols(t: Term) -> list[tuple[str, int]]:
    """(symbol, arity) occurrences in left-to-right order."""
    if isinstance(t, Var):
        return []
    out = [(t.fn, len(t.args))]
    for a in t.args:
        out.extend(symbols(a))
    return out


def normalize(t: Term) -> Term:
    """Rename variables to X0, X1, ... in first-occurrence order."""
    mapping: dict[str, str] = {}

    def go(u: Term) -> Term:
        if isinstance(u, Var):
            if u.name not in mapping:
                mapping[u.name] = f"X{len(mapping)}"
            return Var(mapping[u.name])
        return App(u.fn, tuple(go(a) for a in u.args))

    return go(t)


def size(t: Term) -> int:
    """Twee's weight w: 1 per symbol occurrence and 1 per variable occurrence."""
    if isinstance(t, Var):
        return 1
    return 1 + sum(size(a) for a in t.args)


def skeleton_weight(t: Term) -> int:
    """Weight with variables counted as 0 (the w_skel(A) of Twitch Sect. 4.1)."""
    return len(symbols(t))


def is_linear(t: Term) -> bool:
    vs = variables(t)
    return len(vs) == len(set(vs))


def is_ground(t: Term) -> bool:
    return not variables(t)


def depth(t: Term) -> int:
    if isinstance(t, Var) or not t.args:
        return 1
    return 1 + max(depth(a) for a in t.args)


def is_valid_abstraction(t: Term) -> bool:
    """Function-rooted with at least one symbol below the root or a variable;
    a bare variable matches everything and is useless as an abstraction."""
    return isinstance(t, App)


def canonical(s: str) -> str | None:
    """Canonical string for an abstraction body or definition, or None if it
    is not a valid first-order abstraction."""
    try:
        t = parse_definition(s)[1] if "=" in s else parse(s)
    except ParseError:
        return None
    if not is_valid_abstraction(t):
        return None
    return str(normalize(t))
