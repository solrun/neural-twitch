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
| `single_analysis.md` | Report of the single-abstraction runs. |
| `nt/graph.py` | Problem graphs for the encoder (equation/term/variable/symbol nodes, goal flag, argument positions) and abstractions as pointer-decoder actions, with masks. |
| `nt/dataset.py` | Training dataset: labels joined with graphs, split by axiomatization, hard problems held out, optional text export for an LLM. |
| `data/hard_problems.txt` | Twitch's hard problems (Twee alone fails in 1000 s), held out as the final test set. |
| `nt/analyze_single.py` | Report on the single-abstraction runs: do abstractions help alone, can a set be predicted from its members, are labels stable across settings, do ratios agree with Twitch. `--labels-out` writes per-abstraction training labels. |
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

  It also adds `--deterministic-alloc N`, which measures the schedule in bytes
  allocated by the Haskell runtime, with N bytes counting as one second.
  The cost of a critical pair varies between problems, while Twee allocates
  at a nearly constant rate: 2.6–3.0 GB per CPU second on Vera across the six
  problems in `nt.schedule_diag`, which ran at 3,300–4,500 CPs per second.
  Housekeeping allocates too, so the time budgets apply again.
  `--print-stats` now also reports `allocated_bytes` and `cpu_seconds` for
  the whole run, which is how to choose N (see `nt.schedule_diag`).

  Either way, Twee's run time is very sensitive to *when* housekeeping
  happens. Across `--deterministic 500/1000/2000/7000`, LAT074-1 takes
  timeout/27 s/143 s/timeout, and the other diagnostic problems swing just as
  much. Twee's normal schedule is stable from run to run (55.6k vs 55.8k CPs
  on LAT074-1) only because machine load perturbs it little. No deterministic
  clock reproduces Twitch's times problem by problem, and the same
  sensitivity can make an abstraction look much better or worse than it is.

```bash
git clone https://github.com/nick8325/twee && cd twee
git apply ../neural-twitch/twee-print-stats.patch
git apply ../neural-twitch/twee-deterministic.patch
cabal install exe:twee --installdir=$HOME/.local/bin   # needs GMP: libgmp-dev / gmp-devel / brew install gmp
twee some-problem.p --print-stats --deterministic 2000 --max-cps 1000000
# last line: % twee-stats: considered_cps=... rules_created=... active_rules=... solved=true allocated_bytes=... cpu_seconds=...
```

`nt/twee.py` passes `--deterministic-alloc 2750000000` (`ALLOC_PER_SECOND`)
by default.
`nt.calibrate` and `nt.single_runs` take `--schedule cps:N`, `alloc:N` or
`none` to change it. `nt/calibrate.py` runs every problem twice under each
flattening setting and reports any CP-count mismatch.

## Running the single-abstraction experiment

```bash
export TWEE_PATH=/path/to/patched/twee TPTP_ROOT=/path/to/TPTP-v9.2.1
# calibrate: determinism check and CP budget (306 problems x 2 flattening settings x 2 baseline runs)
python -m nt.calibrate data/labels.jsonl ijcar26-twee_abstractions/data/TPTP out/calibration.jsonl
# trial run: 3 LAT problems
python -m nt.single_runs data/labels.jsonl ijcar26-twee_abstractions/data/TPTP out/single_trial.jsonl \
    --problems LAT --limit 3 --max-cps 2000000
# full run: 306 problems, 15,222 Twee runs
python -m nt.single_runs data/labels.jsonl ijcar26-twee_abstractions/data/TPTP out/single.jsonl
```

For each problem it takes the best set from the existing runs and, under three
weight settings (`cost 1`, `factor 0.2`, `factor 0.5`), each with goal
flattening on and off, runs the baseline, the full set and each abstraction
alone. Every row gets `ratio` = critical pairs relative to the baseline under
the same setting. `--flatten on` or `--flatten off` restricts both scripts to
one flattening setting.

Afterwards:

```bash
cat out/single_*.jsonl > out/single.jsonl
python -m nt.analyze_single out/single.jsonl data/labels.jsonl \
    --labels-out data/single_labels.jsonl > single_analysis.md
```

The CP budget needs calibrating once the binary exists: pick it so the
baseline still proves nearly all 306 problems, otherwise most ratios are
undefined.

## What the single-abstraction runs say

Full report: `single_analysis.md` (12,429 runs on 295 problems, allocation
clock, 6M CP budget; produced before wall-clock timeouts counted as hurting,
which adds ~3–4 points to "hurts").

1. **Single abstractions often help.** Per setting, 26–33% of single runs
   are a >=1.5x speedup, 43–61% neutral, 13–24% a slowdown. 52% of
   (problem, abstraction) pairs help under at least one setting, 13% under
   all six. (These are members of Twitch's best set per problem, so this is
   conditional on that selection.)
2. **A set behaves like its best member, not like the sum of its members.**
   The best single ratio predicts the set ratio best (Spearman 0.67); the
   product of single ratios is far off (median error 4x). In 23% of cases a
   member helps alone but the set does not; only 6% show synergy. Per-
   abstraction labels carry most of the signal, and adding abstractions
   can cost more than it gains.
3. **Within a flattening setting, the weight setting hardly matters** for
   these three settings: Spearman 0.69–0.89 between cost 1, factor 0.2 and
   factor 0.5, with 1–4% helps-vs-hurts contradictions. The model need not
   predict a weight among them.
4. **Goal flattening changes which abstractions help.** Between flattening
   on and off for the same weight setting, Spearman is only 0.22–0.24, with
   6–9% contradictions. Weight changes also alter the search, yet labels
   agree there, so this is more than generic schedule sensitivity. Labels
   (and the model) should be conditioned on flattening.
5. **Our CP ratios agree with Twitch's wall-clock ratios** for the same set
   and configuration: Spearman 0.62, same class 69%, contradictions 8%,
   despite a different Twee build and clock. The deterministic setup
   measures the same effect.
6. **Twee crashes on 7 hinted runs** (`Twee/Term.hs:(115,3)-(116,19):
   Non-exhaustive patterns`), e.g. LCL400-10 with factor 0.2 and no
   flattening. Rare, but worth reporting upstream with the hint that
   triggers it.

## Growing the dataset

`nt/expand.py` produces new problems and abstraction sets in three stages;
`nt.single_runs --sets` then labels them exactly like the Twitch sets.

| Stage | What it does |
|---|---|
| `base` | Baseline runs (allocation clock, both flattening settings, 1000 s cap) that keep Twee's proof (`--all-lemmas --show-peaks`, gzipped under `out/expand/proofs/`). Rows have the calibration format, so they double as `--calibration` input. |
| `hindsight` | For each proof needing at least 10k CPs, takes up to 5 lemmas (latest in the proof first) and writes each as a new problem: same axioms and includes, the lemma skolemised as the negated conjecture. Lemmas mentioning the goal's constants or symbols introduced by goal flattening, axioms, trivial lemmas and duplicates are dropped. Writes a manifest for `base`. |
| `abstract` | Runs Twitch's own local-abstraction extraction on each proof (proof terms, Stitch with 10 iterations and max arity 10, Twitch's filters and expansion) and canonicalises the result. Imports Twitch's code from `TWITCH_DIR` (that repo has no licence file, so it isn't copied here); needs `stitch_core` and `python-dotenv`. |

ETP problems get the prefix `ETP-` (e.g. `ETP-1076_102`) and hindsight
subproblems the suffix `_hsK`, so names still start with their domain.

```bash
# stitch_core 0.1.25 does not install on Python 3.14; the abstract step uses
# its own venv on Python 3.12 (Twitch was tested on 3.11)
module purge; module load <a Python/3.12 module>   # see `module spider Python/3.12`
python -m venv ~/venvs/nt-stitch && source ~/venvs/nt-stitch/bin/activate
pip install -r requirements.txt            # adds stitch_core, python-dotenv
source slurm/vera.env                      # back to the main venv for everything else
mkdir -p logs out/expand
T=$HOME/ijcar26-twee_abstractions/data/TPTP
# 1. proofs for the ETP problems and for all TPTP UEQ problems (job arrays)
sbatch --array=0-7 --export=ALL,NAME=etp,INPUTS=$T/ETP_UEQ_UNSAT slurm/expand_base.sbatch
sbatch --array=0-7 --export=ALL,NAME=tptp,INPUTS="$T/*_UEQ_UNSAT",EXTRA_ARGS="--exclude ETP" \
    slurm/expand_base.sbatch
cat out/expand/etp_base_*.jsonl > out/expand/etp_base.jsonl
cat out/expand/tptp_base_*.jsonl > out/expand/tptp_base.jsonl
# 2. hindsight subproblems (seconds; fine on a login node), then their proofs
python -m nt.expand hindsight out/expand/tptp_base.jsonl out/expand/etp_base.jsonl \
    --out-dir out/expand/hindsight
sbatch --array=0-7 --export=ALL,NAME=hs,INPUTS=out/expand/hindsight/manifest.jsonl \
    slurm/expand_base.sbatch
cat out/expand/hs_base_*.jsonl > out/expand/hs_base.jsonl
# 3. abstraction sets (Stitch; one node; in the Python 3.12 venv)
module load <the Python/3.12 module>; source ~/venvs/nt-stitch/bin/activate
srun -c 32 -t 2:00:00 python -m nt.expand abstract \
    out/expand/etp_base.jsonl out/expand/hs_base.jsonl --out out/expand/sets.jsonl
# 4. labels
sbatch --array=0-31 --export=ALL,MAX_CPS=6000000,SETS=out/expand/sets.jsonl,NAME=single_expand,\
EXTRA_ARGS="--weights f0.5 --wall-timeout 2400 --calibration out/expand/hs_base.jsonl" \
    slurm/single_runs.sbatch
cat out/single_expand_*.jsonl > out/single_expand.jsonl
```

`--weights f0.5` runs one weight setting (both flattening settings): in the
first experiment the three weight settings gave closely agreeing labels, and
factor 0.5 agrees best with cost 1 (Spearman 0.87–0.89), so one setting keeps
nearly all the information at a third of the cost.

## Preparing the training data

```bash
python -m nt.analyze_single out/single.jsonl data/labels.jsonl --labels-out data/single_labels.jsonl
python -m nt.analyze_single out/single_expand.jsonl data/labels.jsonl --labels-out data/expand_labels.jsonl
python -m nt.dataset --labels data/single_labels.jsonl data/expand_labels.jsonl \
    --tptp-dir $TWITCH_DIR/data/TPTP --problems out/expand/hindsight/manifest.jsonl \
    --out data/dataset --text
cat data/dataset/stats.md
```

Needs `TPTP_ROOT` (most problems include axiom files). Design choices, from
the plan and the single-abstraction results:

* **Graph.** One node per clause (role axiom/hypothesis/goal, negated flag),
  per distinct application or constant (ground subterms shared across the
  problem, others within their clause), per variable per clause, and per
  symbol (arity, name for optional named embeddings). Equations are
  unordered (`side` edges); `arg` edges carry the argument position.
* **Targets.** An abstraction is a prefix-order sequence of actions:
  `[0, s]` = pointer to symbol node s, `[1, k]` = variable slot k (k equal to
  the number of open slots opens a new one), so nonlinear patterns like
  f(X0, X0) are explicit. `nt.graph.valid_next` gives the decoder's mask
  (no variable at the root; arities close the term). Abstractions using
  symbols the problem lacks are dropped (in Twitch's sets: 76 of 5,413, all
  `equals`/`tuple` from Twee's encoding of existential goals).
* **Labels.** Per abstraction, conditioned on goal flattening (an input to
  the model) and weight setting; ratio, class and lower-bound flag are kept
  so loss weighting stays a training-time choice.
* **Splits.** By axiomatization (role-`axiom` clauses up to renaming), so
  TPTP variants of one theory and hindsight subproblems with their source
  stay together; stable hash assignment; `--holdout-domain` for
  leave-domain-out; `data/hard_problems.txt` always held out. `stats.md`
  warns if one theory dominates; `--group source` is the fallback.

## Next steps

1. **Deterministic cost in Twee.** Done: `--deterministic-alloc` gives
   identical CP counts across runs and nodes.
2. **Single-abstraction runs.** Done; see "What the single-abstraction runs
   say". Labels in `data/single_labels.jsonl` (on Vera).
3. **ETP data.** The Twitch repo contains 1,027 self-contained Equational
   Theories Project problems in `data/TPTP/ETP_UEQ_UNSAT` that the paper
   does not use. They come from Twitch's `generate_tptp_for_unknown.py`,
   i.e. implications that resisted ETP's automatic first pass, so they are
   probably hard: the first five (all with hypothesis law 1076) timed out at
   120 s under both settings. Measure the solve rate on a random sample
   (`nt.expand base ... --sample 64 --wall-timeout 1000`) before running
   all of them.
4. **Hindsight subproblems.** Derived lemmas from base proofs as new goals.
   Code written (`nt.expand hindsight`); remaining: run it.
