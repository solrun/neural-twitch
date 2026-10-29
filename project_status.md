# Neural Twitch: project status (2026-10-23)

Goal: learn to generate Twitch-style abstractions (term patterns given to Twee as hints) for equational problems, in the spirit of neural conjecturing (Chvalovský/Suda/Urban), and show that they make Twee prove more problems or prove them faster. Code: solrun/neural-twitch.

**New since 2026-10-21:**
- The dataset now includes the TPTP unit-equality problems Twitch did not use: 124 more labelled problems, including two new theories (MVA, KLE), and 29 more hard problems (section 3).
- A model retrained on it gives the same hard-problem results within noise (24 of 96 over all configurations) and the first clear speedups on test (median 0.61 at k=1, flattening off) (section 5).
- **Sampling is now the best method on hard problems.** The new model's own samples (`nt.model.predict`, ranked by frequency) prove 16 / 20 / 21 of the 96 at k = 1 / 3 / 5, and 26 over all configurations, against 14 / 19 / 18 and 24 for reranking with the same model (section 5c).
- But the proofs come from reuse, not invention: every single-abstraction proof uses an abstraction labelled in training exactly as written, and no proved problem needs a new shape. 12 of the 26 hard proofs are on ifeq-encoded problems, mostly via one generic encoding pattern (section 5c).

## 1. Infrastructure (done)

- **Deterministic Twee.** Patches add `--print-stats` and two deterministic housekeeping clocks. The allocation clock (`--deterministic-alloc 2750000000`, ≈ 1 CPU second on Vera Zen4) gives 0 CP mismatches between runs and nodes, so a run's cost is its CP count, not wall time.
- **Noise floor.** Changing only the clock moves 80% of problems by 0.7–1.4x in CPs, so ratios in 0.67–1.5 count as neutral.
- **Evaluation protocol.** 6M CP budget and a wall cap (2400 s, later 3600 s). The report is scored with `--alloc-budget 2.0e12`: a run counts as proved only if it allocated at most 2.0 TB. That is below what any 2400 s timeout allocates (slowest rate 0.83–0.85 GB/s), so the result no longer depends on the wall cap or the node. Ratios are allocation ratios (with hints / without), per goal-flattening setting.
- **Cluster tooling.** Slurm job arrays with sharding and resume for Vera (C3SE); Apptainer container and training script prepared for Arrhenius (GPU).
- **CPU training on Vera.** `slurm/train_cpu.sbatch` trains with C3SE's `PyTorch/2.1.2-foss-2023b` module instead of the venv (training needs nothing beyond PyTorch). The Twee and Stitch jobs still use the venv in `slurm/vera.env`.

## 2. What the labels say (done; see single_analysis.md)

- On Twitch's 295 problems (12,429 runs): single abstractions from Twitch's best sets help (≥1.5x) in 26–33% of runs.
- A set behaves like its best member (Spearman 0.67); the product of singles is a poor predictor. So per-abstraction labels carry most of the signal, and small sets are preferable.
- The weight setting barely matters (Spearman 0.69–0.89), but goal flattening changes which abstractions help (0.22–0.24). The model is therefore conditioned on flattening, with one weight (factor 0.5).
- Agreement with Twitch's own wall-clock ratios: Spearman 0.62.
- The new problems (section 3) label the same way: flattening on vs off 0.29, best single vs set 0.75, singles help in 11% (flattening on) and 20% (off) of runs.

## 3. Dataset (done; extended 2026-10-22)

- **Hindsight subproblems.** TPTP UEQ proofs give lemmas over the axiom signature, which become new goals: 1,332 subproblems from 269 proofs.
- **Stitch sets** for the 823 hard enough to matter; labels for 497. They behave like the original problems, so the labels are pooled.
- **ETP** (`etp.md`). The 1,027 ETP problems in Twitch's repo are all false implications according to ETP's final matrix, which is why they timed out. A new selection of true implications (`nt.etp`, `data/etp/`) is far too easy: 39,163 true implications (all class representatives, 10,000 random pairs, and ETP's longest Vampire proofs and hand-proved ones such as Tarski's axiom) are all proved in under 7k CPs (median 2). So ETP gives neither labels nor hard problems.

**New TPTP problems (`data/tptp_extra/`, branch `tptp-extra-ueq`).**
- TPTP v9.2.1 has 1,143 unsatisfiable UEQ problems. Twitch's `filter.py` kept only nine domains (ALG, BOO, COL, GRP, LAT, LCL, REL, RNG, ROB), giving its 1,041. The other 100 are listed in `new_ueq_unsat.tsv`; 83 with fewer than 1,000 clauses are copied (the 17 left out are mostly CSR/SUMO problems with up to 44k clauses).
- 33 are native unit equality; 50 are `-10` versions, Horn problems translated to UEQ with `ifeq` axioms (all 15 KLE problems are of this kind).
- **Triage** (plain Twee, both flattening settings, 1000 s): 24 worth labelling (MVA ×13, KLE ×9, ANA133-1, NUN133-1), 29 hard (3 native, 26 ifeq; `hard_extra.txt`), 30 trivial (under 10k CPs).
- **Fix:** ANA133-1, NUN133-1 and NUN134-1 used the quoted symbol `'+'`, which Twee prints infix and Twitch's term parser cannot read (`IndexError: pop from empty list` in `nt.expand abstract`). The symbol is renamed `plus` in those files.
- **Labels:** hindsight and Stitch gave 124 sets with 990 abstractions; 2,238 runs (0 errors); 2,013 labels in `data/extra_labels.jsonl`.

**Graphs and splits.** Problems as typed graphs (equations, terms, variables, symbols), with abstractions encoded as pointer-decoder action sequences. The split is by axiomatization, stratified by domain.

| | `data/dataset` | `data/dataset_extra` | added |
|---|---|---|---|
| train | 611 | 723 | MVA 74, KLE 33, NUN 3, ANA 2 |
| val | 84 | 90 | KLE 6 |
| test | 97 | 103 | KLE 6 |
| hard (no labels) | 96 | 125 | the 29 in `hard_extra.txt` |

- The old assignments are unchanged: splits are assigned domain by domain, so a new domain does not move others.
- MVA is one axiom group of 74 problems (all share `MVA001-0.ax`), the second-largest group, about 10% of train. Watch whether it dominates training.
- KLE forms five axiom groups (the ifeq encoding folds each problem's hypotheses into its axioms), one each in val and test.

## 4. Models and baselines

- **Baseline (no learning).** The "name" method ranks abstractions that helped on training problems with the same symbols. The "shape" method takes symbol-agnostic patterns ranked by how often they helped and instantiates them with the problem's symbols. The "combined" method takes name candidates first, then shape candidates.
- **Generator.** A typed message-passing graph encoder feeds a GRU pointer decoder (over the problem's symbols and variable slots), with a scorer head. It trains in seconds per epoch on CPU and overfits after about 30 epochs on about 1,000 examples.

First results (`data/dataset`). hit@k is the share of examples where a known helpful abstraction is in the top k.

| | val hit@1 | val hit@5 | val hit@10 | test hit@1 | test hit@5 |
|---|---|---|---|---|---|
| baseline (combined) | 0.317 | 0.525 | 0.574 | 0.176 | 0.676 |
| model, sampling (best epoch) | 0.287 | 0.525 | – | – | – |
| baseline top 50, reranked by generator likelihood | 0.287 | 0.594 | 0.743 | 0.389 | 0.630 |
| reranked, fusion of baseline + scorer + generator | 0.337 | 0.604 | 0.663 | 0.269 | 0.667 |

**Reading:**
- Names carry over within theories, and the baseline's candidate pool usually contains a helpful abstraction (89% of val in its top 200). Ranking is the hard part.
- Sampling from the model alone only ties the baseline.
- The generator's likelihood is a useful reranker of the baseline's candidates. The scorer head is worse than the baseline order and is set aside for now.
- With about 100 examples per split, differences under about 0.1 are within noise.

**Retrained with the new problems (2026-10-23, `runs/extra`).** Old and new model scored on the same `data/dataset_extra` examples (111 per split, top 100 baseline candidates):

| bgen (used for the sets) | val hit@1 | val hit@5 | test hit@1 | test hit@5 |
|---|---|---|---|---|
| baseline | 0.288 | 0.550 | 0.171 | 0.595 |
| old model | 0.342 | 0.622 | 0.234 | 0.685 |
| new model | 0.378 | 0.604 | 0.297 | 0.676 |

- hit@1 rises for both fusion methods on both splits (bgen +4 and +7 examples, fuse +7 and +6); hit@5 is flat. Each difference is within noise alone, but they all point the same way.
- Part of the gain may come from the KLE problems now in val and test, which only the new model has seen in training.
- The scorer got worse (val hit@1 0.207 → 0.063); it is not used.

**Generation (`nt.model.predict`, changed 2026-10-23).**
- It now ranks samples by how often the generator produced them out of 128 (`--rank count`, the default), not by the scorer. Every abstraction is marked `novel` if it was never labelled on a training problem.
- New model on test and hard (228 problems, both settings): 0% undecodable; 10,403 distinct candidates (about 23 per problem and setting).

| | new string | new shape (symbols renamed, `nt.baseline.shape_of`) |
|---|---|---|
| k=1 | 18% | 3% |
| k=3 | 30% | 8% |
| k=5 | 37% | 12% |

- So the generator mostly writes known patterns with the problem's own symbols, close to what the baseline's shape method does. Genuinely new shapes are 3–12%, and that count includes trivial variants.
- Offline, sampling only tied the baseline, but hit@k counts only abstractions already labelled helpful. In Twee, sampled sets do best (section 5c).

## 5. Twee evaluation of generated sets

### 5a. Old model, `data/dataset` (2026-10-21)

**Setup:**
- Three methods: `base_combined` (the baseline order), `rerank` (fusion of the baseline order and the generator's likelihood over the top 100 baseline candidates), and `mix` (rerank's top pick, then the baseline order; k = 3 and 5 only, since its k=1 equals rerank's).
- Set sizes k = 1, 3 and 5, each with goal flattening on and off, factor 0.5, 6M CPs.
- Problems: 97 test and 96 hard. Each problem gets a run without hints and a run with the set.
- Scored on the equal allocation budget of 2.0e12 bytes (section 1). Full report: `eval_report.md` (`nt.eval_report --alloc-budget 2.0e12`).

**Why the allocation budget.** The mix runs had a 3600 s wall cap and the earlier runs 2400 s. In raw form, their plain-Twee runs proved more (hard 6/5 vs 3/3 per setting), and 41 of their proved runs took over 2400 s, so mix looked better than it was. With the allocation budget, every method is judged by the same deterministic cutoff. The conclusions are somewhat sensitive to the budget: at 2.8e12 (slightly too generous), the baseline still won at k=3 on hard; at 2.0e12 it no longer does.

**Hard problems: generated hints give new proofs.** Under the budget, plain Twee proves none of the 96.

| portfolio (either flattening setting) | k=1 | k=3 | k=5 |
|---|---|---|---|
| baseline sets: hard proved | 12 | 13 | 18 |
| mix sets: hard proved | – | 14 | 18 |
| rerank sets: hard proved | **15** | **19** | 16 |

**Complementarity on hard** (any k, either setting):

| | hard proved | only this method |
|---|---|---|
| plain Twee | 0 | – |
| baseline sets | 19 | 0 |
| mix sets | 19 | 0 |
| rerank sets | 23 | 5 |
| union of all sets | 24 | – |

- Only rerank proves COL046-1, LAT075-1, LAT400-3, LCL304-10 and LCL339-10.
- Robustness varies: 5 of the 24 come from a single configuration out of 16, 4 from 15–16.

**Mix is the same as the baseline.** At k = 3 and 5, mix and the baseline differ on 2 hard problems in total (both in mix's favour, k=3 flattening on) and on no test problems; their portfolio counts match. Putting the reranked top pick in front of the baseline's candidates changes nothing once those candidates are in the set too, consistent with "a set behaves like its best member".

**Rerank against the baseline on hard, per k** (problems only one proves, pooled over both settings; two-sided sign test):
- k=1: rerank 7, baseline 1 (p ≈ 0.07).
- k=3: rerank 7, baseline 1 (p ≈ 0.07).
- k=5: rerank 3, baseline 6 (p ≈ 0.5); with flattening off, baseline 4, rerank 0.
- All k: rerank 17, baseline 8 (p ≈ 0.11, and the k values are not independent).
- So rerank is better at small k and the baseline possibly at k=5 with flattening off, but none of this is significant on its own. The earlier k=1 result (13 vs 2, p ≈ 0.007) relied partly on runs that exceed the budget.

**Test problems: little speedup in allocation terms.**
- With flattening off, the median ratio is 0.79 (baseline k=1), 0.82 (baseline and mix k=3) and 0.87–0.94 (rerank k=1, 3); at k=5 it is above 1.
- With flattening on, the median is 0.87–1.09.
- The sets lose 3–12 test proofs per setting and 1–5 in the portfolio, so hints belong in a portfolio alongside plain Twee.

### 5b. Model retrained with the new problems (2026-10-23)

`rerank_extra`: the same rerank method (bgen, top 100) with the new model, the same k, settings and 2.0e12 budget. Report: `eval_report_extra.md`, scored with the old dataset's splits so that the original 96 hard and 97 test problems line up with 5a; the new problems appear under split `?`.

**Hard (original 96): the same within noise.**

| portfolio (either flattening setting) | k=1 | k=3 | k=5 | any configuration |
|---|---|---|---|---|
| rerank, old model (5a) | 15 | 19 | 16 | 23 |
| rerank, new model | 14 | 19 | 18 | 24 |

- Proved in all 6 configurations: BOO004-10, COL038-1, RNG001-10, RNG004-10. Five come from a single configuration.
- The five problems only the old rerank proved in 5a are all proved again.
- k=5 improves slightly (16 → 18), consistent with the old model's long lists being too similar.

**Test (original 97): the first clear speedups.**

| flattening off | old model: median / geo-mean | new model: median / geo-mean | ≥1.5x faster (new) |
|---|---|---|---|
| k=1 | 0.94 / 0.77 | **0.61 / 0.60** | 49 of 82 |
| k=3 | 0.87 / 0.97 | **0.73 / 0.75** | 31 of 73 |
| k=5 | 1.16 / 1.28 | **0.65 / 0.86** | 38 of 72 |

- With flattening on, medians are 0.92–0.97.
- More proofs are lost: at k=1 with flattening on, 9 (old model: 3); in the portfolio over both settings, 4 / 5 / 5 at k = 1 / 3 / 5 (old model: 1 / 5 / 4).

**New problems (split `?`: 6 KLE test, 29 new hard).** Plain Twee proves 6 of the 35 (the KLE test problems); the sets prove 5 of the 29 new hard problems.

**Head to head, old vs new model** (`eval_report_all.md`): on hard, problems only one of the two proves, summed over the six configurations, are 11 each. So on hard the two rerankers are even; the new model's gain is speed on test.

**New hard problems proved** (any method): ANA034-10 and MVA004-1 by the new reranker only, plus three proved by both reranked and sampled sets.

### 5c. Sampled sets, new model (2026-10-23)

`pred`: `nt.model.predict` with the new model, 128 samples per problem and setting, the k most often sampled abstractions as the set. Same k, settings and 2.0e12 budget. One report with every method: `eval_report_all.md` (`nt.eval_report out/eval/*.jsonl --data data/dataset --alloc-budget 2e12 --list-splits "hard,?"`).

**Hard (original 96): sampling leads at every k.**

| portfolio (either flattening setting) | k=1 | k=3 | k=5 | any configuration |
|---|---|---|---|---|
| baseline | 12 | 13 | 18 | 19 |
| rerank, old model | 15 | 19 | 16 | 23 |
| rerank, new model | 14 | 19 | 18 | 24 |
| **sampled, new model** | **16** | **20** | **21** | **26** |
| union of all methods | | | | 27 |

- Same model, sampled vs reranked: problems only one proves, summed over configurations, 24 vs 12 (k=1: 3 vs 1, k=3: 11 vs 6, k=5: 10 vs 5); two-sided sign test p ≈ 0.07, and configurations overlap, so a strong hint rather than significant.
- The biggest gap is k=5 with flattening off: 15 hard problems sampled, against 9 (new rerank), 6 (old rerank) and 10 (baseline). This fits the diversity hypothesis: reranked lists bunch similar candidates, samples are more varied.
- Only sampled sets prove ROB032-2 (k3 both settings) and ROB034-1 (k3 flattening on, k5 off).
- Robustness: 4 hard problems are proved in 27–28 of the 28 configurations of all methods.

**Test (original 97):** like the other methods. Median ratio with flattening off 0.64 / 0.94 / 0.97 at k = 1 / 3 / 5; 4–5 proofs lost in the portfolio over both settings.

**New problems (`?`):** sampled sets prove 3 of the 29 new hard problems, the new reranker 5.

**Attribution** (`nt.attribute --all`, `attribution_pred_all.md`). Every problem sampling proves (26 hard plus 9 new problems in split `?`), each proving set's abstractions marked seen (labelled in training), new string, or new shape (symbols renamed, `nt.baseline.shape_of`):
- **k=1 proofs: all 36 proving configurations use a seen abstraction**, exactly as written. When one abstraction suffices, the model retrieves one it learned, usually from the same theory with the same symbols (`apply(apply(s, X0), X1)` for COL, `meet(a, X0)` for LAT400, `multiplication(antidomain(X0), X1)` for KLE).
- **No problem needs a new shape.** Only COL046-1 and LCL225-10 have a new-shape abstraction in every proving sampled set, and reranked sets (and for LCL225-10 the baseline) prove both without one. 33 of 35 have a proving set of known shapes only.
- **New shapes appear** in about a third of the sets, but as trivial variants (`apply(apply(b, X0), X0)`) or long ground terms (nested `apply(apply(b, b), apply(b, …))`), never as what makes the difference.
- **Where sampling adds:** ROB031-2, ROB032-2, ROB034-1, ROB035-1 at k=3 and 5, with variants of the seen `negate(add(X0, X1))` such as `add(X0, negate(X1))` and `add(X0, negate(add(X1, X2)))` (new strings, known shapes). ROB032-2 and ROB034-1 are the two problems only sampling proves.
- **ifeq-encoded problems:** 12 of the 26 hard proofs (BOO004-10, RNG001-10, RNG004-10, and LCL225/245/289/304/331/339/348/375/395-10). Most are proved at k=1 by one generic encoding pattern, `ifeq(X0, true, X1, true)` or `ifeq(X0, true, theorem(X1), true)` (the latter alone proves LCL245, 289, 304, 331 and 348 at k=1). That is a property of the Horn-to-equation encoding, not of the mathematics.
- **So the claim is:** the model retrieves the right seen abstraction, and sampling adds useful variants of known patterns, which is why it beats reranking at k=3 and 5. It does not yet invent useful new abstractions; transfer to unseen theories is untested.

## 6. Open questions and next steps

- **Leave-domain-out test, now the key experiment:** every proof so far is explained by reuse of seen abstractions, so only a held-out theory shows whether anything transfers (e.g. hold out REL, ROB or COL; also a `--no-names` ablation).
- **Native vs ifeq-encoded problems:** report hard results separately for the two, since one generic encoding pattern accounts for 12 of the 26 sampled hard proofs.
- **New patterns, not just reuse:** try a decoder built for diversity, e.g. a conditional VAE as in the neural conjecturing work, or sampling at a higher temperature.
- **Overlap of hard with training theories:** quantify how many hard problems share an axiomatization (or symbol names) with training problems; the attribution suggests most proved ones do.
- **Sampling as the default method** for later evaluations (leave-domain-out), with rerank as the comparison.
- **Lost test proofs:** the new model loses more at k=1 with flattening on (9 vs 3). Look at which problems, and whether a portfolio with plain Twee covers them all.
- **Portfolio of singles instead of sets:** run each of rerank's top k candidates as a separate single-abstraction run, against a k-set at the same total cost (tooling done: `eval_sets.sbatch MODE=singles`, `nt.eval_report --singles`).
- **MVA weight in training:** one axiom group is about 10% of train; try per-group down-weighting, or a run without MVA.
- **Diversity in reranking:** a diversity penalty (e.g. no two candidates with the same shape) might close rerank's gap to sampling at k=5.
- **Better generalisation:** smaller model or stronger name dropout, more data (more hindsight subproblems), or train the scorer against near-miss candidates instead of only labelled singles.
- **ETP:** its true implications are all easy for Twee (`etp.md`), so it is out as a benchmark and as the leave-domain-out test; that test needs a held-out TPTP theory.
- **Possible LLM comparison**, using the text form of the dataset (`text.jsonl`).
- **Label backup:** commit the label files to git as a backup.
- **Citation:** on the AITP 2026 programme, *Neural Conjecturing for Saturation Theorem Provers* is by Jakubův, Olšák, Suda and Urban; check which paper and author list the "Chvalovský/Suda/Urban" references mean.
