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
| known | 550 | pairs ETP proved on their own (`data/etp/known.tsv`, from ETP commit 2f49bda), not in the tiers above: 506 from Vampire, 42 from `Subgraph.lean`, 1571 => 3167 and 4656 |

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

## Closure tier

The full selection (all four tiers, 29,163 problems, 58,326 runs; same
settings) is the same picture: **every run proved, every problem trivial**,
max 6,918 CPs. The ten most expensive runs share three hypotheses: 3089
(6,918 CPs, flattening on, for 3071, 3065, 3052), 450 (about 6,408, for 432,
413, 426) and 3874 (6,175, flattening off, for 3660, 3659, 4068, 4065). The
cost does not depend on the conclusion, so it lies in saturating those laws,
not in the goal.

So none of the 29,163 class representatives is useful for labels or as a
hard problem.

## Random sample

10,000 of the random tier (seed 0; random true pairs, no pure instances):
**all trivial** as well.

## ETP's own hard implications

- **Vampire.** ETP has 1,507 implications proved by Vampire
  (`Generated/VampireProven`). The longest proof, 947 => 3897 (154 steps), is
  in our hasse tier, and so are 723 => 872 (58), 2666 => 3460 (54),
  2860 => 2660 (45), 3940 => 4477 (44) and 2789 => 898 (38): all trivial for
  Twee. 1,001 of the 1,507 are in the selection.
- **By hand.** Outside `Subgraph.lean` (mostly about x = y), the hand-written
  positive results are Tarski's axiom 543 => 11, 16, 40, 3823, 4369 (all in
  our closure tier, all trivial), 37 => 2 and 514 => 2 (degenerate tier,
  trivial) and 1571 => 3167, 4656 (now in the known tier). `ManuallyProved/`
  is mostly refutations.
- The **known tier** (2026-10-29) holds the 550 of these 1,613 pairs not
  already selected, among them the second and third longest Vampire proofs,
  3957 => 3971 (133 steps) and 3569 => 3957 (105), and 650 => 448 (65).

## Conclusion

39,163 true implications, including ETP's hardest automated and hand-proved
ones, and not one needs 10k CPs. Below that, hint ratios mean little
(DEFAULT_MIN_CPS), so ETP's positive implications give neither labels nor
hard problems for Twee, and ETP cannot serve as the leave-domain-out test
as planned. What remains of ETP's difficulty is in the refutations (finite
and infinite counterexamples), which Twee does not address.
