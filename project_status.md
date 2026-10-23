# Neural Twitch: project status (2026-10-16)

Goal: learn to generate Twitch-style abstractions (term patterns given to Twee as hints) for equational problems, in the spirit of neural conjecturing (Chvalovský/Suda/Urban), and show that they make Twee prove more problems or prove them faster. Code: solrun/neural-twitch.

## 1. Infrastructure (done)

- **Deterministic Twee.** Patches add `--print-stats` and two deterministic housekeeping clocks. The allocation clock (`--deterministic-alloc 2750000000`, ≈ 1 CPU second on Vera Zen4) gives 0 CP mismatches between runs and nodes, so a run's cost is its CP count, not wall time.
- **Noise floor.** Changing only the clock moves 80% of problems by 0.7–1.4x in CPs, so ratios in 0.67–1.5 count as neutral.
- **Evaluation protocol.** 6M CP budget, 2400 s wall cap (3600 s from now on); ratio = CPs with hints / CPs without, per goal-flattening setting; timeouts with a proved baseline are lower-bounded "hurts".
- **Cluster tooling.** Slurm job arrays with sharding and resume for Vera (C3SE); Apptainer container and training script prepared for Arrhenius (GPU).

## 2. What the labels say (done; see single_analysis.md)

- On Twitch's 295 problems (12,429 runs): single abstractions from Twitch's best sets help (≥1.5x) in 26–33% of runs.
- A set behaves like its best member (Spearman 0.67); the product of singles is a poor predictor. So per-abstraction labels carry most of the signal, and small sets are preferable.
- The weight setting barely matters (Spearman 0.69–0.89), but goal flattening changes which abstractions help (0.22–0.24). The model is therefore conditioned on flattening, with one weight (factor 0.5).
- Agreement with Twitch's own wall-clock ratios: Spearman 0.62.

## 3. Dataset (done)

- **Hindsight subproblems.** TPTP UEQ proofs give lemmas over the axiom signature, which become new goals: 1,332 subproblems from 269 proofs.
- **Stitch sets** for the 823 hard enough to matter; labels for 497. They behave like the original problems, so the labels are pooled.
- **Graphs and splits.** 888 problems as typed graphs (equations, terms, variables, symbols), with abstractions encoded as pointer-decoder action sequences. The split is by axiomatization, stratified by domain: train 611, val 84, test 97. 96 hard problems, which Twee alone does not prove, are held out.
- **ETP.** The 1,027 ETP problems in Twitch's repo are hard (the sampled ones time out), so they are not used for labels yet.

## 4. Models and baselines (first results)

- **Baseline (no learning).** The "name" method ranks abstractions that helped on training problems with the same symbols. The "shape" method takes symbol-agnostic patterns ranked by how often they helped and instantiates them with the problem's symbols. The "combined" method takes name candidates first, then shape candidates.
- **Generator.** A typed message-passing graph encoder feeds a GRU pointer decoder (over the problem's symbols and variable slots), with a scorer head. It trains in seconds per epoch on CPU and overfits after about 30 epochs on about 1,000 examples.

Results are hit@k: the share of examples where a known helpful abstraction is in the top k.

|                                                   | val hit@1 | val hit@5 | val hit@10 | test hit@1 | test hit@5 |
|---------------------------------------------------|-----------|-----------|------------|------------|------------|
| baseline (combined)                               | 0.317     | 0.525     | 0.574      | 0.176      | 0.676      |
| model, sampling (best epoch)                      | 0.287     | 0.525     | –          | –          | –          |
| baseline top 50, reranked by generator likelihood | 0.287     | 0.594     | 0.743      | 0.389      | 0.630      |
| reranked, fusion of baseline + scorer + generator | 0.337     | 0.604     | 0.663      | 0.269      | 0.667      |

**Reading:**
- Names carry over within theories, and the baseline's candidate pool usually contains a helpful abstraction (89% of val in its top 200). Ranking is the hard part.
- Sampling from the model alone only ties the baseline.
- The generator's likelihood is a useful reranker of the baseline's candidates. The scorer head is worse than the baseline order and is set aside for now.
- With about 100 examples per split, differences under about 0.1 are within noise.

## 5. Twee evaluation of generated sets (2026-10-16)

**Setup:**
- Sets come from `rerank` (fusion of the baseline order and the generator's likelihood, top 100 baseline candidates) and from `base_combined` (the baseline).
- Set sizes k = 1, 3 and 5, each with goal flattening on and off, factor 0.5, 6M CPs.
- Problems: 97 test and 96 hard. Each problem gets a run without hints and a run with the set.
- Full report: `eval_report.md` (`nt.eval_report`).

**Hard problems: generated hints give new proofs.** Plain Twee proves 3 of 96 per setting, 4 in either setting. With the sets:

| portfolio (either flattening setting) | k=1    | k=3 | k=5 |
|---------------------------------------|--------|-----|-----|
| baseline sets: hard proved            | 17     | 22  | 23  |
| rerank sets: hard proved              | **24** | 22  | 18  |

In a single setting, the sets prove 8–19 hard problems.

**Complementarity on hard** (any k, either setting; 6 configurations per method, so both get the same number of attempts):

|                                | hard proved | new (not plain Twee) |
|--------------------------------|-------------|----------------------|
| plain Twee                     | 4           | –                    |
| baseline sets                  | 26          | 24                   |
| rerank sets                    | 31          | 29                   |
| union of all sets + plain Twee | 33          | –                    |

- Every new proof the baseline gets, rerank also gets in some configuration. Five hard problems are proved only by rerank: COL002-10, GRP693-1, LAT400-1, LAT400-3, LCL304-10. One (GRP689-1) is proved only by plain Twee.
- The new proofs vary in how robust they are: 5 of the 29 come from just 1–2 of the 12 configurations, while 4 come from 11 or 12.

**Rerank against the baseline per configuration.** Counted by problems that only one of the two proves (sign test):
- **k=1:** rerank is better on hard, 13 vs. 2 problems pooled over both settings (p ≈ 0.007; flattening off alone 8 vs. 0). This matches the hit@1 gain: the reranked top pick is better.
- **k=5, flattening off:** the baseline is better on hard, 8 vs. 1 (p ≈ 0.04).
- **k=3, flattening off:** the baseline is better on test, 10 vs. 3 (p ≈ 0.09), and 29 vs. 3 faster.
- Elsewhere the two are even.
- Working hypothesis: reranking by likelihood puts similar candidates together, so its longer lists are less diverse than the baseline's.
- Caveat: these are many comparisons, so only the k=1 result is clearly significant.

**Test problems: modest speedups, mostly with flattening off.**
- With flattening off, the median ratio is 0.65–0.76 for every method and k (geometric mean 0.44–0.68).
- With flattening on, the median is about 1.0 except at k=5 (0.8). This is consistent with the labels, where singles help more often with flattening off.
- Plain Twee already proves all 97 test problems in one of the two settings, so test only measures speed.
- The sets also lose some proofs: 3–13 test problems per setting, and 1–5 in the portfolio over both settings. So in practice hints belong in a portfolio alongside plain Twee.

**Wall-cap noise (resolved):** GRP663-1 and its subproblem GRP663-1_hs1 prove in some files and hit the 2400 s wall cap in others. Future runs use `WALL=3600` so that the CP budget, which is deterministic, decides.

**Running:** mixed sets (`rerank --method mix`: rerank's top pick, then the baseline order) for k = 3 and 5.

## 6. Open questions and next steps

- **Diversity at larger k:** analyse the mixed sets when they finish; next, reranking with a diversity penalty (e.g. no two candidates with the same shape).
- **Overlap of hard with training theories:** check how many hard problems share an axiomatization with training problems, i.e. whether the new proofs come from within-theory transfer.
- **Better generalisation:** smaller model or stronger name dropout, more data (more hindsight subproblems, more TPTP domains), or train the scorer against near-miss candidates instead of only labelled singles.
- **Leave-domain-out test** (e.g. REL, currently only in train), to measure transfer across theories rather than within them; also a `--no-names` ablation.
- **ETP** solve rate with the generated sets.
- **Possible LLM comparison**, using the text form of the dataset (`text.jsonl`).
- **Label backup:** commit the label files to git as a backup.
