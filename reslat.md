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

Breakdown (second report):

- **Flattening on almost dominates:** only 18 label problems are proved
  with flattening off but not on. Most of the label bucket (LGR 1,600, RLT
  1,322) is cheap (< 10k CPs) with flattening on and fails or is expensive
  without it.
- **Hard for the better setting (>= 10k CPs):** LGR 1,027 (473 of them
  >= 100k), RLT 609 (46 >= 100k). This, plus the 124 open, is the useful
  pool for abstraction labels.
- **Difficulty grows with size:** in LGR, 4-7 operations gives 0 open and
  27% label; 16+ gives 65 open and 69% label. To get more hard problems,
  generate larger terms.
- **Equations are mostly trivial** (199 of 247); the hard ones are
  inequalities.
- **Some open RL problems are short, with three-step human proofs**, e.g.
  RLT-00999 `1/x <= y\((y v z)/x)` (y(1/x)x <= y <= y v z), RLT-02679
  `1/((x v y) v y) <= z\(z/y)` and RLT-01229 `x ^ y <= x\((xy)/(x\y))`.
  The proofs use only monotonicity of multiplication and the residuals,
  which the equational axioms give only indirectly. These are good
  showcase problems for lemma or abstraction hints.

**Rerun of the open flattening-on timeouts** (51 problems, flattening on,
1 h wall cap, same 1M CP budget, `NAME=open_long`, job 10644159): 15
proved, all expensive (14 LGR, 1 RLT: RLT-01280). Final counts:

| domain | trivial | label | label >= 10k CPs (better setting) | open |
|---|---|---|---|---|
| LGR | 2,276 | 2,641 | 1,041 | 83 |
| RLT | 3,041 | 1,933 | 610 | 26 |

**Final.** Shard 0 ran out of memory after an hour (32 Twee processes of up
to an hour each) and was resumed with `--resume --workers 8`. All 51 now
have a 1 h run: 15 proved, 28 used up the 1M CP budget, 8 timed out again.
So of the 109 open, 101 used up the 1M CP budget with flattening on (73 in
the first triage, 28 in the rerun) and are open by a deterministic
criterion; 8 timed out after an hour without reaching it. The short RL
showcase problems (RLT-00999, RLT-02679, RLT-01229) are among the open.

## Labels and hint check (set up 2026-11-05)

**Labels** for the pool: label problems needing >= 10k CPs under the better
setting (1,651: LGR 1,041, RLT 610). Same pipeline as the TPTP problems
(README, "Growing the dataset"): Twitch's abstraction extraction on the
triage proofs, then `nt.single_runs --sets` (factor 0.5, both flattening
settings, 6M CPs, 2400 s). Start with a pilot of 100 sets to measure set
sizes, run times and memory before the full array.

    # pool list, and the pool's triage rows (proofs; also the calibration)
    python -m nt.reslat report out/reslat/triage_*.jsonl out/reslat/open_long_*.jsonl \
        --write-lists out/reslat/lists
    python -m nt.reslat select out/reslat/triage_*.jsonl out/reslat/open_long_*.jsonl \
        --problems out/reslat/lists/pool.txt --out out/reslat/pool_rows.jsonl
    # abstraction sets (Stitch; in the Python 3.12 venv)
    srun -c 32 -t 4:00:00 python -m nt.expand abstract out/reslat/pool_rows.jsonl \
        --out out/reslat/sets.jsonl
    # pilot, then the full array
    shuf -n 100 --random-source=out/reslat/sets.jsonl out/reslat/sets.jsonl > out/reslat/sets_pilot.jsonl
    sbatch --array=0-3 --export="ALL,MAX_CPS=6000000,SETS=out/reslat/sets_pilot.jsonl,NAME=reslat_pilot,EXTRA_ARGS=--weights f0.5 --wall-timeout 2400 --workers 16 --calibration out/reslat/pool_rows.jsonl" \
        slurm/single_runs.sbatch

**Hint check.** The short open RL problems have three-step proofs from
x(x\y) <= y, (y/x)x <= y and monotonicity of multiplication. If they are
hard for want of these lemmas, hints should crack them. `nt.reslat hints`
gives every listed problem the same six hints (`DEFAULT_HINTS["rl"]`:
`multiply(X0, ldiv(X0, X1))`, `multiply(rdiv(X0, X1), X1)`,
`ldiv(X0, rdiv(X1, X2))`, `multiply(X0, join(X1, X2))`,
`multiply(join(X0, X1), X2)`, `join(multiply(X0, X1), X2)`), and
`nt.single_runs` runs the base, the whole set and each hint alone. Budget
1M CPs, the triage's, so "proved" means "proved where plain Twee was not".

    grep RLT out/reslat/lists/open.txt > out/reslat/lists/open_rlt.txt
    python -m nt.reslat hints --problems out/reslat/lists/open_rlt.txt \
        --out-dir $NT_STORE/reslat/hints --sets out/reslat/hint_sets.jsonl
    sbatch --array=0-3 --export="ALL,MAX_CPS=1000000,SETS=out/reslat/hint_sets.jsonl,NAME=reslat_hints,EXTRA_ARGS=--weights f0.5 --wall-timeout 1200 --workers 8" \
        slurm/single_runs.sbatch

26 problems x 2 settings x 8 runs = 416 runs, at most about 4 h per shard.

The first report printed `ops=None` (nt.expand base output does not carry
the manifest's fields). The report now reads sizes from the selection and
splits the buckets by size, kind and variables, and the label bucket by
the better setting's CPs and by which settings prove it:

    python -m nt.reslat report out/reslat/triage_*.jsonl --write-lists out/reslat/lists --show-open

If most problems had been trivial, the next steps would have been larger
terms (`--max-ops`), more variables, equations only (`--leq 0`), or
Jipsen's lists of standard RL/LG identities.
