# ETP implications as Twee problems (2026-10-29)

Code: `nt/etp.py`, `slurm/etp_triage.sbatch`; selection in `data/etp/`.

## Twitch's ETP problems are non-theorems

All 1,027 problems in `ijcar26-twee_abstractions/data/TPTP/ETP_UEQ_UNSAT`
(written by `generate_tptp_for_unknown.py` on 2025-08-02) are false
implications according to ETP's final implication matrix (explorer export of
2026-10-23): 559 explicitly refuted, 468 refuted by closure. They were the
implications still open in August 2025, and ETP has since refuted all of
them. This is why every sampled run timed out (64 problems x 2 settings at
1000 s). Check any directory with
`python -m nt.etp check --implications <csv> <dir>`.

## The matrix

Explorer CSV export, row = hypothesis, column = conclusion (equation numbers
minus one). Codes from ETP's `home_page/implications/script.js`: 4 / -4
explicit proof true / false, 3 / -3 implied by closure, ±2 / ±1 conjectures,
0 unknown. The 2026-10-23 export has no unknowns or conjectures: 8,178,279
true (10,657 explicit), 13,855,357 false.

4,694 laws form 1,415 equivalence classes. 1,496 laws are equivalent to
x = y. Between the other classes there are 25,615 implications, and their
transitive reduction has 4,721 edges, every one with an explicit ETP proof.

## Selection

| tier | problems | what |
|---|---|---|
| degenerate | 1,495 | law => x = y for each law equivalent to x = y |
| hasse | 4,721 | one per edge of the transitive reduction of the class order |
| closure | 20,894 | one per other pair of classes P => Q |
| equiv | 2,053 | a cycle a1 => a2 => … => a1 within each class |
| random | 100,000 | random true pairs (seed 0), hypothesis not degenerate, no pure instances, none of the above |

For a class pair, the representative is an explicitly proved pair if there
is one, otherwise the pair with the fewest operations. Problems are CNF in
Twitch's format (axiom `equation<n>`, goal skolemized with a, b, c, …),
named `ETP-<hyp>_<concl>`. Each row records `instance`: the conclusion is a
substitution instance of the hypothesis, so one rewrite proves it.

## First triage: degenerate, hasse, equiv

Plain Twee, both flattening settings, 1M CPs, 300 s cap, allocation clock.
8,269 problems, 16,538 runs:

- **Every run proved**, and every problem is trivial by our definition
  (proved under both settings with fewer than 10k CPs).
- CPs per run: **median 2**, p90 16, p99 110, max 6,918.
- Most expensive: ETP-3089_3071 (6,918 CPs, flattening on, 3.7 s) and
  ETP-450_432 (6,409, 3.8 s); then hypotheses 3874 and 3495 at about 6,150 CPs
  whatever the conclusion (the cost is in saturating the hypothesis).
- Nothing took more than 4 s.

Why: choosing the smallest pair per class pair picks instances. The share of
pure instances per tier:

| tier | instance | not instance |
|---|---|---|
| degenerate | 0 | 1,495 |
| hasse | 3,169 (67%) | 1,552 |
| equiv | 176 (9%) | 1,877 |
| closure | 2,939 (14%) | 17,955 |
| all true non-degenerate pairs (20k sample) | 3% | 97% |

The non-instances were easy too (the degenerate tier has no instances, and
all of it is trivial), so the representatives are cheap for Twee in general,
not only because of instances.

## Next

- Closure tier: running (2026-10-29).
- The random tier is the search for hard problems: 100k problems x 2 settings
  at well under a second each is cheap. A sample first:
  `--export=ALL,TIERS=random,SAMPLE=10000`.
- If the random tier is also all trivial, ETP's positive implications are
  too easy for Twee to be useful for labels as they stand. The known hard
  positive implications would have to be found specifically (or
  harder variants made, e.g. hindsight goals from the longest proofs).
