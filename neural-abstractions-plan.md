# Neural Generation of Twitch-Style Abstractions for Twee — Research Plan

**Builds on:**
- Chvalovský, Suda, Urban — *Neural Conjecturing for Saturation Theorem Provers* (graph-to-clause cut generation)
- Axelrod, Johansson, Smallbone — *Twitch: Learning Abstractions for Equational Theorem Proving* (IJCAR 2026)

---

## 1. Core idea

Use Stitch and Twee to build a supervised dataset, then train a neural model to generate the abstractions directly. In this setup, Stitch produces candidate abstractions and Twee measures which ones help. A symbol-pointer graph-to-term generator then learns to propose abstractions for an unseen problem, without needing a curated domain of easier problems or a long failed run first.

Twitch's own future-work section proposes learning abstraction proposals from accumulated (problem, abstraction) data. The neural conjecturing paper supplies most of the machinery to do that.

The neural conjecturing paper's argument carries over unchanged: abstractions are purely speculative. A bad one costs time but cannot affect soundness. They are even cheaper to test than cuts, because they don't change the search space and many can be supplied at once.

**Motivating gap.** Twitch's best results need a set of easier problems from the same domain, and GRP677-1 only fell after manual domain curation. Conditioning the generator on the problem's own axioms is essentially automatic domain curation.

## 2. What changes when moving from cuts to abstractions

| | Neural conjecturing (cuts) | This project (abstractions) |
|---|---|---|
| Output object | Clause (literals, predicates) | Single term pattern, function-rooted |
| Label | r = (C₁+C₂)/C₀, both branches must prove | r = cost(P⊕A)/cost(P) under Twee's weighting |
| Delivery | One AVATAR claim per run | Many abstractions per run, each with a small effect |
| Credit assignment | Per lemma | Per abstraction *and* per set (LAT075-1 needed abstractions 1 and 3 together) |
| Data scale | 122K–2.5M pairs | ~1041 UEQ problems, which is the main risk |

## 3. Phase 0 — Infrastructure (a few weeks)

- **Deterministic cost in Twee.** Twitch's effect metric uses wall-clock time, which is too noisy as a training label. Add a counter for critical pairs selected or rules derived, or count CPU instructions as the neural conjecturing paper does with Vampire. All labels should use this measure.
- **Canonical abstraction format.** Alpha-normalize variables in first-occurrence order and deduplicate modulo renaming. Keep nonlinearity explicit, since f(x,x) and f(x,y) are different abstractions.
- **Batch harness.** Given (P, set of abstractions, weight scheme k, flat/no-flat), the harness runs Twee and returns cost, solved status, and the proof. Everything below is a call to this.

## 4. Phase 1 — Data generation (the critical phase)

Twitch's 1041 problems are far too few to train on directly. Combine four sources:

1. **Exhaustive Twitch labeling.** Run `LocalAbstractions` over every solved UEQ problem, crossing strategies (flat/no-flat), weight factors, and top-k. Also add single-abstraction runs so each abstraction gets its own label, not only the set's.
2. **Hindsight subproblems.** The neural conjecturing paper mined proof lemmas from solved Mizar problems; the equational analogue is to treat each derived lemma l = r in a Twee proof as a new goal over the same axioms. Each one has a known proof to give to Stitch and is cheap to re-run with abstractions. This could multiply the data by one or two orders of magnitude.
3. **The Equational Theories Project corpus** (reference [9] in Twitch). It contains a very large number of magma implications with a single binary operation. Most are trivial, so keep only those where Twee needs non-negligible effort. This is the closest available thing to Mizar-scale data for this setting.
4. **Partial-proof material.** From short Twee runs on unsolved problems, take the interestingness-ranked lemmas and their Stitch abstractions. Label them by whether they help in the remaining time.

**Labeling choices**
- Weight samples by 1/(1+r) and normalize per problem. This stops GRP, with its 481 problems and many near-variants, from dominating.
- Keep r ≥ 1 examples as explicit negatives. A learned filter will need them later.
- Record the weight factor k with each label, because whether an abstraction helps depends on k.

## 5. Phase 2 — Model

- **Encoder.** Reuse the heterogeneous GNN, with node types simplified for UEQ: equation, term, variable, symbol, plus a flag marking the goal. Optionally, condition on a partial-proof snapshot by adding the top-k interesting lemmas from a short Twee run as extra equation nodes. This combines Twitch's two modes in one model.
- **Decoder.** Use the same pointer mechanism with a reduced action set: `ArgFunc` (pointer to a symbol), `ArgVar` (a new or reused variable slot), and `EndArgs`, with the arity stack enforcing well-formedness. The root must be a function symbol, and a pattern that is a bare variable is masked out. Reusing variable slots is what lets the model generate nonlinear patterns like f(x,x), which matter most here because repeated variables are counted only once in the weight.
- **Optional heads.** Predict a per-abstraction weight factor k. Possibly generate a whole set autoregressively (abstraction₁ ; abstraction₂ ; …) to capture joint effects. Start with independent sampling and greedy set construction, and move to set decoding only if interaction effects turn out to matter.
- **Symbols.** UEQ problems have very few function symbols, so the GNN must tell problems apart mainly by axiom structure. Add optional named embeddings for recurring TPTP names (multiply, inverse, join, meet), mirroring the Mizar named embeddings.

## 6. Phase 3 — Evaluation

**Splits**
- Avoid leakage from near-duplicate TPTP variants by splitting by axiomatization, not by problem name.
- Keep Twitch's 70 hard problems (rating ≥ 0.9, Twee fails at 1000 s) fully held out.
- Run one leave-domain-out experiment, for example training without ROB or REL, to test transfer.

**Baselines**
- Twee with and without goal flattening.
- Twitch with partial-proof abstractions and with domain abstractions.
- Brute-force enumeration of all small patterns up to size n, ranked by frequency in partial proofs. This baseline matters: with one binary operation the pattern space is small, and the neural model has to beat it.

**Metrics**
- Hard problems solved.
- Cactus plots against Twitch.
- Rank of the first useful abstraction (cf. Table 5 of the neural conjecturing paper).
- Coverage from ensembles and from combining configurations.
- Accounting that includes generation time and failed candidates (the budget-accounting threat from the neural conjecturing paper).

**Deployment modes**
- (a) Give the top-N abstractions as one set.
- (b) Use a time-sliced portfolio of disjoint sets.

Twitch's robustness result suggests (a) might work well, which would beat cuts on budget.

## 7. Phase 4 — Closing the loop and extensions

- **Iterate.** Newly solved problems give new proofs; Stitch and Twee turn those into new labeled abstractions, and the model is retrained. The neural conjecturing paper found that initializing from the previous checkpoint and mixing old with new data worked best, and that training from scratch overfit.
- **Equational cuts and hints.** The same decoder emits full equations l = r after a small change. These can serve as cuts (prove the lemma, then add it) or as the "hints" in Twitch's future work. This is a cheap side track that reuses everything.
- **Normal-form robustness.** Twitch's brittleness issue is that demodulation destroys matches (e.g. f(f(x,x),y) → f(x,f(x,y)) under associativity). Labels taken from real Twee runs already penalize abstractions that get rewritten away, so check whether the learned model prefers patterns that are stable under normalization.
- **Transfer.** Test whether a model trained on TPTP UEQ helps on ETP or other algebra settings, the analogue of the E→Vampire transfer result.

## 8. Main risks

1. **Data scarcity.** This is the main risk, and Phase 1 sources 2 and 3 are the mitigation. If hindsight subproblems don't yield enough diversity, the project may depend more on ETP than expected.
2. **The enumeration baseline might win** on single-operation domains. The contribution then shifts to *ranking* or filtering candidates, which is still publishable and matches the learned-utility-model suggestion in the neural conjecturing paper.
3. **Set effects.** If per-abstraction labels predict set performance poorly, set-level modeling is needed earlier than planned.
4. **Twee time limits.** Keep labeling runs short and deterministic, and save the 1000 s runs for final evaluation only.

## 9. First milestone

1. Build Phase 0 and Phase 1 source 1.
2. Before any neural work, run a quick check:
   - Do individually labeled abstractions predict set-level speedups?
   - How well does the enumeration baseline do?

   The answers decide the model design.
3. For a fast sign of life, train a small pointer model on the GRP and LAT data alone and test it on held-out LAT problems, including LAT075-1.
