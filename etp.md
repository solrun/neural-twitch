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
| known | 550 | pairs with a Vampire or hand-written proof in ETP (`data/etp/known.tsv`, from ETP commit 2f49bda), not in the tiers above: 506 from Vampire, 42 from `Subgraph.lean`, 1571 => 3167 and 4656 |
| pairs | 19,884 | two laws as hypotheses, E1 and E2 => E3, neither implying E3 alone; truth unknown (below) |
| vampire_hard | 2,166 | pairs Janota's Vampire runs proved only with the 600 s limit (`data/etp/vampire_hard.tsv`), not in the tiers above; hypotheses 650 and 2923 only |

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

## Random tier

First 10,000 (fixed sample), then all 100,000 (random true pairs, seed 0, no
pure instances): **99,999 trivial, one in the label band, none hard.**

The one is ETP-2923_2638, an equivalence (both laws in class 4):
2923 `X = m(m(m(Y, m(X, Z)), Y), X)` => 2638 `X = m(m(Y, m(m(Z, W), U)), X)`.
65 CPs with goal flattening off, **11,512 with flattening on** (3.7 s), so
only flattening makes it non-trivial. Its proof is kept
(`$NT_STORE/etp/proofs/ETP/ETP-2923_2638_flat.txt.gz`). The same hypothesis
has the fifth longest Vampire proof in ETP, 2923 => 2628 (62 steps), which
is trivial for Twee (known tier).

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
  **All 550 are trivial** (same triage settings), including 1571 => 3167 and
  1571 => 4656. The other 1,063 are in the tiers above (27 in the random
  tier), so every pair ETP proved on its own has now been run: all trivial.

## Consistency with the literature

- **ETP paper** (Bolan et al., *The Equational Theories Project: Advancing
  Collaborative Mathematical Research at Scale*, Dec 2025, arXiv:2512.07087).
  The counts match the matrix as we read it: 8,178,279 true, 13,855,357
  false, and 10,657 positive / 586,925 negative implications formalized
  directly (our codes 4 / -4), the rest by transitivity and duality
  (Sect. 1.3, 3). ATPs "could be deployed at extremely fast speeds to
  establish a complete generating set of positive implications" (1.3),
  "the positive implications in the main implication graph of the project
  were all simple enough that we did not need a semi-automatic approach for
  them" (7.2), and "more challenging were the 13 855 357 (62.88%)
  implications that were false" (1.3); the hardest result, E1729 ⊭ E817,
  is a refutation that took months.
- **Prover9** (7.3.5): proves all positive implications between laws of
  order up to 4 with max_weight 55; with default parameters "all
  consequences of each equation can be proven in at most 1 second per
  equation, with the exception of laws E450 and E650 (and their duals),
  which take somewhat longer" (details in the Zulip thread "Which
  implications are harder for ATPs"). **This matches Twee:** hypothesis 450
  is the second most expensive in our triage (about 6,400 CPs whatever the
  conclusion), and 650 => 448 has the fourth longest Vampire proof in ETP
  (65 steps); in our runs both stay under 10k CPs.
- **Vampire** (Janota, *Experimental Results for Vampire on the Equational
  Theories Project*, arXiv:2508.15856, cited as [40]): Vampire 5.0 proves
  all 8,173,585 non-reflexive true implications, all but 2,390 (99.97%)
  within 500 instructions, and "the challenge lies [in] the implications
  that need to be refuted". It leaves 1,062 implications undecided (310
  apparently needing infinite models).
- Twee is not discussed in either paper.

## Janota's Vampire data (Zenodo 10.5281/zenodo.16910288)

`eq_vampire.tgz`: per-pair status, time and method for all 22,028,942
pairs (methods: fmb and saturation with 500 instructions, fmb 60 s, fmb and
saturation 600 s).

- **Vampire agrees with the ETP matrix on every pair:** 8,173,585 proved,
  13,854,295 refuted, no contradictions; the 1,062 it leaves undecided are
  all false in ETP.
- **Twitch's ETP set comes from Vampire's undecided set.** Of Twitch's 1,027
  problems, 1,016 are among the 1,062 Vampire left undecided and 11 were
  refuted only in its long runs. Janota's `generate_tptp.py` writes the same
  file format as Twitch's problems ("% LHS", "% RHS negated and
  skolemized").
- **Vampire-hard true implications:** 8,171,195 are proved within 500
  instructions (median 0.02 s, max 2.7 s); the other **2,390** need the 600 s
  run (median 30 s, max 102 s, 450 => 432). They have only **four
  hypotheses: 650 and its dual 2923 (1,192 each), 450 and its dual 3089 (3
  each)**, the laws the ETP paper names for Prover9 (7.3.5). In Twee too,
  450 and 3089 are the most expensive hypotheses (about 6,400 and 6,900 CPs)
  and 2923 gives the one problem over 10k CPs. So in all three provers the
  difficulty belongs to the hypothesis law, not the implication.
- 224 of the 2,390 were already run here (all trivial); the other 2,166 are
  the `vampire_hard` tier.

**vampire_hard triage** (2,166 problems, same settings): 2,163 trivial,
**3 in the label band**, none hard. All three have hypothesis 2923 and the
profile of ETP-2923_2638: 65 CPs with flattening off, about 11,500 with it
on (3.6–3.7 s).

| problem | flattening off | flattening on |
|---|---|---|
| ETP-2923_2579 | 65 | 11,525 |
| ETP-2923_2618 | 65 | 11,523 |
| ETP-2923_2633 | 65 | 11,505 |
| ETP-2923_2638 (random tier) | 65 | 11,512 |

## Twee vs Vampire: time

Per problem, Twee's wall time from the triage (Vera, allocation clock, 1M
CPs) against Vampire's time in Janota's data (his machine, up to 100
parallel workers; the time of the method that solved it). Both include
process startup. All 131,879 problems:

| | median | p99 | max | total |
|---|---|---|---|---|
| Vampire | 0.023 s | 29.9 s | 101.6 s | 69,701 s |
| Twee, flattening off | 0.027 s | 0.11 s | 3.65 s | 4,714 s |
| Twee, flattening on | 0.029 s | 0.30 s | 5.14 s | 6,582 s |

- **The 126,245 Vampire proved within 500 instructions:** no real
  difference; both take 20–30 ms, mostly startup. Vampire is slightly
  faster (Twee flattening off: Vampire/Twee geometric mean 0.97, median
  0.90; Twee faster on 46%).
- **The 2,390 Vampire needed its 600 s run for** (hypotheses 650, 2923, 450,
  3089): Vampire median 30 s, max 102 s; Twee with flattening off median
  0.05 s, max 3.65 s. **Twee is about 500x faster** (geometric mean 475,
  median 552) with flattening off and about 70x with it on (median 0.36 s,
  max 5.1 s), and faster on every one of them. For 450 => 432, Vampire
  102 s, Twee 3.7 s (about 28x).
- Caveats: different machines and load; Vampire's `--mode casc` runs a
  schedule of strategies, so its 30 s is mostly time on strategies that fail
  (a single good strategy would be much faster); 3,244 easy ones were
  solved by Vampire's finite model builder run.

## Pairs tier: two-law hypotheses (2026-10-29)

ETP's true implications are too easy, and its false ones have nothing to
prove. ETP only covers single laws, so the pairs tier strengthens the
hypothesis instead: **E1 and E2 => E3**, where in ETP neither E1 => E3 nor
E2 => E3 holds. Such problems are new, have two axioms (more critical
pairs), and are far more numerous; but their truth is unknown.

**Small-magma filter.** Every law is evaluated in all magmas of size 2 (16)
and 3 (19,683) and 10,000 random ones of size 4: 29,699 magmas
(`nt.etp.satisfaction`, about 9 minutes). Checked against the ETP matrix,
the filter is **sound** (it refutes no true implication) and refutes **98.1%**
of the false single-law implications (ETP's own hand-picked magmas of size
at most 4 got 99.3%).

**Selection** (`build --pairs 4000 --pairs-per 5`, seed 0): 4,000 random
pairs E1, E2 of incomparable, non-degenerate laws that some filter magma
satisfies together (so their conjunction is not x = y), and for each up to
5 random conclusions E3 (not x = x) that no filter magma refutes: 19,884
problems over 2,386 hypothesis laws and 3,063 conclusions. Named
`ETP-<hyp>_<hyp2>_<concl>`, `code` null.

**Caveat.** The filter is weak for pairs: the median pair of laws has only
5 of the 29,699 magmas satisfying both, and a median of 627 conclusions per
pair survive it. Many survivors are presumably false (needing larger or
infinite countermodels). So in the triage only proofs count: proved ones
with at least 10k CPs are labelling candidates; unproved ones are of unknown
status and must not be treated as hard theorems (the mistake behind Twitch's
ETP set).

**Pairs triage** (19,884 problems, same settings): **16,481 trivial, none in
the label band, 3,403 unproved** under both settings within 1M CPs / 300 s.
Twee either finds a proof almost at once or none at all.

How the unproved runs ended (`budget` split by CP count: under 1M CPs means
Twee **saturated**, i.e. completed the rewrite system without the goal):
1,809 problems saturated under some setting (median 25 CPs, max 38,173);
1,500 hit the 300 s cap under both settings; 94 hit the 1M CP limit under at
least one.

**Countermodel search** (`nt.etp fmb`: Vampire 5.0 finite model builder,
60 s per problem, all 3,403 unproved): **3,285 false** (countermodels of size
4: 2,297, 5: 599, 6: 141, 7: 57, 8: 37, 9: 64, 10: 90), 118 unknown, none
true. Against Twee's endings:

| Twee | false | true | unknown |
|---|---|---|---|
| saturated | 1,805 | 0 | 4 |
| open | 1,480 | 0 | 114 |

So a Twee saturation does mean a false problem here (no saturated problem
is true; the 4 unknown just have no countermodel found in 60 s). Countermodels
on a test sample were checked independently (`nt.etp.satisfaction`: both
hypotheses hold, the conclusion fails).

**Pairs tier in total:** 16,481 true (all trivial for Twee), 3,285 false,
118 undecided (4 saturated, so presumably false; 114 open). No problem in
the label band.

## All true implications (2026-10-29)

Every one of the 8,173,585 non-reflexive true implications (`TIERS=all`),
both flattening settings, same settings as the triage: **16,347,170 runs,
all proved.** Proved runs by CP count:

| CPs | flattening off | flattening on |
|---|---|---|
| 0 | 4,093,419 (50.1%) | 3,846,491 (47.1%) |
| 1–9 | 3,955,103 (48.4%) | 3,102,852 (38.0%) |
| 10–99 | 124,730 (1.5%) | 1,151,020 (14.1%) |
| 100–999 | 317 | 71,670 (0.9%) |
| 1,000–9,999 | 16 | 1,548 |
| 10,000–99,999 | 0 | 4 |
| total wall | 101,662 s | 111,936 s |

The only problems needing 10k CPs are the four already found in the
triage (ETP-2923_2579, 2618, 2633, 2638; about 11,500 CPs with flattening
on, 65 without), so the tiers above missed nothing. With flattening off, no
true ETP implication needs even 10k CPs, and 98.5% need fewer than 10.

## Conclusion

**All 8,173,585 true ETP implications are proved by plain Twee** (16,347,170
runs; total wall time about 59 hours). Only four need more than 10k CPs, all
with hypothesis 2923 (the dual of 650) and only with goal flattening on
(about 11,500 CPs; 65 without). Two-law hypotheses (pairs tier) do not
change this: 16,481 of 19,884 true and trivial, none in between, 3,285
shown false by countermodels, 118 undecided. Below 10k CPs hint ratios mean little
(DEFAULT_MIN_CPS), so ETP gives neither labels nor hard problems for Twee,
and cannot serve as the leave-domain-out test as planned. This matches the
ETP paper and Janota: the positive implications are easy for ATPs, the
difficulty is in the refutations (finite and infinite counterexamples),
which Twee does not address, and what little difficulty there is belongs to
the hypotheses 450, 650 and their duals. On the 2,390 implications Vampire
found hard, Twee is about 500x faster.
