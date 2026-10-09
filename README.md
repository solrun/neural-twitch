# neural-twitch

Starter code for learning Twitch-style abstractions for Twee with a neural
generator (see `neural-abstractions-plan.md` for the full plan).

This first step uses only data that already exists: the local-abstraction runs
published with the Twitch paper
([WeAreDevo/ijcar26-twee_abstractions](https://github.com/WeAreDevo/ijcar26-twee_abstractions)).

## Contents

| Path | What it is |
|---|---|
| `nt/terms.py` | Canonical abstraction representation: parser, alpha-normalisation (`X0, X1, …` in first-occurrence order), size, skeleton weight, linearity. Rejects higher-order Stitch output and bare variables. |
| `nt/build_dataset.py` | Converts Twitch's `local_abs_*iter` summaries into `data/labels.jsonl`, one row per (problem, abstraction set, Twee config) run. |
| `nt/analyze.py` | First-milestone analysis: label noise, how often sets help, sensitivity to weight settings, shape of helpful abstractions, recurrence across domains, enumeration-space size. |
| `analysis.md` | Output of the analysis on the published data. |
| `data/labels.jsonl` | The dataset (16,875 rows over 1,041 problems). |
| `twitch_dataset.jsonl` | Curated release of the Twitch runs from the paper's authors, with exact Twee flags per run (see "Twitch's released dataset and Twee flags" below). |
| `nt/import_twitch_dataset.py` | Adds the runs in `twitch_dataset.jsonl` that `labels.jsonl` lacks to `data/labels_extra.jsonl`. |
| `data/labels_extra.jsonl` | 649 extra runs (positives only) from the other Twitch stages, in the `labels.jsonl` schema. |
| `tests/test_terms.py` | Tests for the term module. |
| `twee-print-stats.patch` | Twee patch adding `--print-stats`: prints the critical-pair count and rule counts at the end of a run. |
| `nt/twee.py` | Runs the patched Twee on a problem plus hints under a deterministic `--max-cps` budget and parses the statistics. |
| `nt/single_runs.py` | The single-abstraction experiment (next step 2 below). |
| `nt/calibrate.py` | Baseline runs that check CP determinism and pick the `--max-cps` budget for `nt/single_runs.py`. |
| `nt/calibrate_report.py` | Combined calibration report over several output files (e.g. job-array shards). |
| `slurm/` | Job scripts and setup guide for the Vera cluster (`slurm/README.md`). |

## Reproduce

```bash
git clone --depth 1 https://github.com/WeAreDevo/ijcar26-twee_abstractions
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m nt.build_dataset ijcar26-twee_abstractions/data/experiments data/labels.jsonl
python -m nt.analyze data/labels.jsonl ijcar26-twee_abstractions/data/TPTP > analysis.md
python -m pytest tests
```

## What the existing data says

Full numbers are in `analysis.md`; the points that affect the plan:

1. **The weight setting matters as much as the abstractions.** The same
   abstraction set differs by a median factor of ~16 between its best and worst
   weight setting, and for about half of the sets it is a ≥1.5x speedup under
   one setting and a ≥1.5x slowdown under another. Repeated identical runs
   differ by only ~1% (median), so this is not timing noise. The model should
   output a weight (or a weight class) per abstraction or per set, not just
   the patterns. `hint-skel-cost 1` and factor `0.2`–`0.5` are the most
   reliable settings; factor `1.0` rarely helps and often hurts.
2. **Labels are set-level only.** There are no single-abstraction runs, so
   the per-abstraction vs. set question from the plan cannot be answered from
   this data. Single-abstraction runs are the first new experiment to run.
3. **Helpful abstractions recur within domains, rarely across them.** About a
   third of the abstractions in helpful sets help on two or more problems, but
   only ~3% cross domains (mostly LAT/REL lattice terms). This supports
   problem-conditioned generation and argues for leave-domain-out evaluation
   being hard.
4. **Enumeration is a serious baseline only at very small sizes.** Skeleton
   weight ≤ 2 covers 45% of helpful abstractions with a median of ~120
   candidates per problem; weight ≤ 3 covers 65% but already needs ~2,800
   candidates (and millions for large signatures). The interesting regime for
   the neural model is weight 3–5, where a third of the helpful abstractions
   live and enumeration stops being feasible.
5. **Helpful abstractions are larger and more often nonlinear** than those in
   harmful sets (median skeleton weight 3 vs 2; 39% vs 30% nonlinear), and
   about 30% mention a constant. A symbol-pointer decoder
   handles those naturally.
6. **Only ~306 problems have a baseline long enough (≥1 s) to measure a
   speedup.** That is the training set as it stands, which confirms data
   scarcity as the main risk.

## Twitch's released dataset and Twee flags

`twitch_dataset.jsonl` (3,313 rows, 922 problems) records each run's problem
clauses, abstraction set, base and hinted time, speedup and Twee flags.

* **Positives only.** Every row has speedup > 1, and at most 3 sets are kept
  per (problem, configuration). `labels.jsonl` stays the source of negatives.
* **Mostly runs we already have.** 2,664 rows match a `labels.jsonl` row
  (same set and configuration, identical times). The other 649 come from
  stages `nt.build_dataset` does not read: large sets (median 51
  abstractions, almost all `--hint-skel-factor 0.2`) and 88 partial-proof
  runs. They cover 175 usable (baseline ≥ 1 s) problems, only 3 of them new.
  `python -m nt.import_twitch_dataset twitch_dataset.jsonl data/labels.jsonl data/labels_extra.jsonl`
  writes them out.
* **Clauses are not self-contained.** `cnf_clauses` holds only the problem
  file's own clauses (median 3 per problem); TPTP `include`s are not
  expanded, so the TPTP axiom files are still needed.

Every run passes `--all-lemmas --show-peaks`, then either
`--hint-skel-factor F --hint-skel-cost C` with `(F, C)` in
{(0,0), (0,1), (0,2), (0.2,0), (0.5,0), (0.7,0), (1,0)}, or, for the
partial-proof stage, `--proof-on-saturation --max-time 50` with no hint flags
recorded; and finally `--flatten-goal` or `--no-flatten-goal`. Checked against
Twee's source (`executable/SequentialMain.hs`, `src/Twee.hs`):

* `--all-lemmas`, `--show-peaks` and `--proof-on-saturation` only change proof
  output, not the search, so `nt/twee.py` can leave them out.
  `--kbo-weight0-unary` (in our `BASE_FLAGS`) is already on by default.
* Twee's built-in hint defaults are `--hint-skel-cost 1 --hint-skel-factor 0`,
  which is presumably what the 88 partial-proof runs used for their hinted run.
* `--flatten-goal` is on by default in Twee. The arXiv version
  (2603.06849, Appendix A) calls its baseline "default Twee without goal
  flattening"; that is the paper's baseline, not Twee's default. The appendix
  gives settings by name, not as flags: strategies are
  {flattening on, off} × weight factor {0, 0.2, 0.5, 0.7}, the
  domain-abstraction runs use factor 0.2 (τ = 0.2, final Stitch step on),
  the partial-proof runs factor 0.2 with the top 50 lemmas and
  t_par ∈ {50, 150, 500}, and factor ≈ 0.5 is reported as best overall.

## Building the patched Twee

Two patches against Twee's GitHub `master` (2.6.2), which already has the
`--hint-skel-*` flags Twitch uses:

* `twee-print-stats.patch` adds `--print-stats`, which prints the number of
  critical pairs considered and rules created at the end of a run.
* `twee-deterministic.patch` adds `--deterministic N`. Twee normally runs its
  periodic housekeeping (interreduction, queue simplification, goal
  recomputation) on a CPU-time schedule, so the search depends on machine
  load: in the first calibration, 213 of 247 problems gave a different CP
  count on a second run. With `--deterministic N` the schedule is measured in
  critical pairs instead, with N CPs counting as one second. The housekeeping
  time budgets are not enforced in this mode, so on very large rule sets
  housekeeping can take a bigger share of wall time; raise N if that matters.

```bash
git clone https://github.com/nick8325/twee && cd twee
git apply ../neural-twitch/twee-print-stats.patch
git apply ../neural-twitch/twee-deterministic.patch
cabal install exe:twee --installdir=$HOME/.local/bin   # needs GMP: libgmp-dev / gmp-devel / brew install gmp
twee some-problem.p --print-stats --deterministic 2000 --max-cps 1000000
# last line: % twee-stats: considered_cps=... rules_created=... active_rules=... solved=true
```

`nt/twee.py` passes `--deterministic 2000` on every run. `nt/calibrate.py`
runs every problem twice and reports any CP-count mismatch.

## Running the single-abstraction experiment

```bash
export TWEE_PATH=/path/to/patched/twee TPTP_ROOT=/path/to/TPTP-v9.2.1
# calibrate: determinism check and CP budget (306 problems x 2 baseline runs)
python -m nt.calibrate data/labels.jsonl ijcar26-twee_abstractions/data/TPTP out/calibration.jsonl
# trial run: 3 LAT problems
python -m nt.single_runs data/labels.jsonl ijcar26-twee_abstractions/data/TPTP out/single_trial.jsonl \
    --problems LAT --limit 3 --max-cps 2000000
# full run: 306 problems, 7,611 Twee runs
python -m nt.single_runs data/labels.jsonl ijcar26-twee_abstractions/data/TPTP out/single.jsonl
```

For each problem it takes the best set from the existing runs and, under three
weight settings (goal flattening on, as in Twee's default; `--no-flatten` for
the ablation) (`cost 1`, `factor 0.2`, `factor 0.5`), runs the baseline, the
full set and each abstraction alone. Every row gets `ratio` = critical pairs
relative to the baseline under the same setting.

The CP budget needs calibrating once the binary exists: pick it so the
baseline still proves nearly all 306 problems, otherwise most ratios are
undefined.

## Next steps

1. **Deterministic cost in Twee.** Patches written (`twee-print-stats.patch`,
   `twee-deterministic.patch`). Remaining: rebuild and confirm with
   `nt.calibrate` that repeated runs give identical CP counts.
2. **Single-abstraction runs.** Harness written (`nt/single_runs.py`).
   Remaining: calibrate the CP budget and run it. The result answers whether
   individual labels predict set-level speedups.
3. **ETP data.** The Twitch repo already contains 1,027 self-contained
   Equational Theories Project problems in `data/TPTP/ETP_UEQ_UNSAT` (one
   binary operation, no includes) that the paper does not use. Running the
   `base` and `local_abs` stages on them is the cheapest way to grow the
   dataset.
4. **Hindsight subproblems.** Extract derived lemmas from the existing base
   proofs as new goals (Phase 1, source 2).
