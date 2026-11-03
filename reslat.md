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

## Triage (to run)

    mkdir -p logs out/reslat
    sbatch --array=0-7 slurm/reslat_triage.sbatch
    python -m nt.reslat report out/reslat/triage_*.jsonl --write-lists out/reslat/lists

Buckets: trivial (proved under both settings, < 10k CPs), label (proved,
otherwise), open (unproved within 1M CPs / 300 s), saturated (Twee completed
without the goal). **A saturated run is a bug**: the goal is a theorem, so
either an axiomatization is incomplete or a decider is wrong. The report also
gives CPs by size, to see whether larger random terms are harder.

If most problems are trivial, next steps would be larger terms (`--max-ops`),
more variables, equations only (`--leq 0`), or Jipsen's lists of standard
RL/LG identities.
