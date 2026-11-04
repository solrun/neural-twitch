# Residuated lattices and l-groups as Twee problems (2026-11-03)

Code: `nt/reslat.py`, `slurm/reslat_triage.sbatch`, `tests/test_reslat.py`;
selection in `data/reslat/`.

## Why

ETP's true implications are all easy for Twee, and its harder-looking
problems were false or of unknown truth. Residuated lattices (RL) and
lattice-ordered groups (LG) are varieties with decidable equational theories
(Jipsen's web pages implement both deciders in JavaScript), so random
equations can be labelled true or false *before* Twee sees them. Only true
ones become problems; an unproved run is then hard, never false.

## Deciders

- **RL:** the cut-free sequent calculus FL (Ono–Komori; Okada–Terui; as in
  Jipsen–Tsinakis, *A survey of residuated lattices*). Backward search,
  invertible rules first, memoized; every rule shrinks the sequent.
- **LG:** Holland–McCleary. The term `t s^-1` is put in the form
  join of meets of reduced group words. `e <= J_i M_j w_ij` fails iff for some
  choice of one word per meet, the points p.u (u a prefix of a chosen word)
  can be weakly ordered with every variable acting as a strictly
  order-preserving partial bijection and every chosen word below p (such a
  finite configuration extends to automorphisms of Q). The search picks words
  meet by meet and abandons a partial choice with no configuration.
- Equations the deciders cannot settle within the step budget are dropped
  (0 for RL, 155 of 106,615 tried for LG).

**Checks** (`python -m nt.reslat selftest`, `pytest tests/test_reslat.py`):
- Every axiom of both axiomatizations is valid according to the deciders.
- Known identities and non-identities are decided correctly.
- On 6,000 random equations (seeds 1 and 2), every true verdict holds in all
  sample algebras: for RL, Gödel, Łukasiewicz and Sugihara chains, Z, and
  binary relations on a 3-element set (noncommutative); for LG, Z, Z² and
  piecewise-linear automorphisms of Q (noncommutative). Of the false
  verdicts, all but 3 RL ones are refuted by one of these algebras (the
  rest presumably need a non-distributive countermodel).
- The whole RL selection and 1,500 of the LG selection hold in those
  algebras.

## Problems

TPTP CNF in Twitch's format: axioms, then the goal negated and skolemized
(a, b, c). Inequalities s <= t are goals `join(s, t) = t`.

- **RL** (domain `RLT`): lattice, monoid, multiplication distributes over
  join on both sides, and `x(x\y) <= y`, `y <= x\(xy)`, `x\y <= x\(y v z)`
  with mirror images (19 axioms; symbols `meet`, `join`, `multiply`,
  `identity`, `ldiv`, `rdiv`). Complete: these give `xy <= z` iff
  `y <= x\z`.
- **LG** (domain `LGR`): the axioms and symbol names of TPTP's GRP004-2.ax
  (16 axioms), so these share an axiomatization with the TPTP l-group
  problems in GRP. As a held-out theory, LG is therefore not new; RL is.
  TPTP's MVA (Veroff's generalized MV-algebras) are residuated lattices with
  an extra law, so RL also overlaps with MVA (check MVA001-0.ax's symbols).

## Selection (`build --count 5000 --min-ops 4 --max-ops 18 --seed 0`)

Random terms over 2–3 variables, both sides together 4–18 operations, no
subterm that one axiom step removes (x ^ x, 1x, inverse(inverse(x)), ...),
half inequalities and half equations as generated; deduplicated up to
variable renaming.

| | tried | true | kept | inequalities | equations | 2 vars | 3 vars |
|---|---|---|---|---|---|---|---|
| RL | 379,306 | 1.6% | 5,000 | 4,902 | 98 | 3,434 | 1,566 |
| LG | 106,615 | 4.7% | 5,000 | 4,851 | 149 | 3,504 | 1,496 |

True equations are rare (random two-sided equations almost never hold), so
the selection is mostly inequalities.

## Triage (2026-11-04, Vera)

Plain Twee, both flattening settings, 1M CPs / 300 s per run
(`slurm/reslat_triage.sbatch`, `--array=0-7`):

| domain | trivial | label | open | saturated |
|---|---|---|---|---|
| LGR | 2,276 | 2,627 | 97 | 0 |
| RLT | 3,041 | 1,932 | 27 | 0 |

Proved runs (out of 5,000 per domain and setting):

| | flattening | proved | median CPs | max CPs |
|---|---|---|---|---|
| LGR | off | 4,017 | 3,282 | 776,523 |
| LGR | on | 4,888 | 841 | 997,408 |
| RLT | off | 3,974 | 205 | 966,089 |
| RLT | on | 4,970 | 356 | 796,802 |

- **No saturated runs:** no evidence of an axiomatization or decider bug.
- **Unlike ETP, most problems are not trivial:** 4,559 label and 124 open
  (true, but not proved within 1M CPs under either setting).
- **Goal flattening matters a lot:** about 1,000 problems per domain fail
  without it but are proved with it. Part of the label bucket is therefore
  "fails without flattening" rather than "needs many CPs".
- Open problems: 97 l-groups and 27 residuated lattices, a candidate hard
  set.

The first report printed `ops=None` (nt.expand base output does not carry
the manifest's fields). The report now reads sizes from the selection and
splits the buckets by size, kind and variables, and the label bucket by
the better setting's CPs and by which settings prove it:

    python -m nt.reslat report out/reslat/triage_*.jsonl --write-lists out/reslat/lists --show-open

If most problems had been trivial, the next steps would have been larger
terms (`--max-ops`), more variables, equations only (`--leq 0`), or
Jipsen's lists of standard RL/LG identities.
