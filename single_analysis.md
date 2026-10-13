# Single-abstraction experiment

12429 runs on 295 problems; schedule alloc:2750000000 (12429).

## 0. Run outcomes

| kind   | runs | proved | budget | timeout | error | ratio defined |
|--------|------|--------|--------|---------|-------|---------------|
| base   | 1506 | 1506   | 0      | 0       | 0     | 1506          |
| set    | 1506 | 1433   | 8      | 64      | 1     | 1441          |
| single | 9417 | 8924   | 145    | 342     | 6     | 9069          |

First error (LCL400-10, f0.2_c0.0_noflat):

```
twee: Twee/Term.hs:(115,3)-(116,19): Non-exhaustive patterns in case

HasCallStack backtrace:
  collectBacktraces, called at libraries/ghc-internal/src/GHC/Internal/Exception.hs:169:13 in ghc-internal:GHC.Internal.Exception
  toExceptionWithBacktrace, called at libraries/ghc-internal/src/GHC/Internal/Exception.hs:89:42 in ghc-internal:GHC.Internal.Exception
  throw, called at libraries/ghc-internal/src/GHC/Internal/Control/Exception/Base.hs:422:30 in ghc-internal:GHC.Internal.Control.Exception.Base



```

## 1. Do abstractions help on their own?

| setting            | single runs | helps | neutral | hurts | median ratio | sets: helps |
|--------------------|-------------|-------|---------|-------|--------------|-------------|
| cost 1, flat       | 1517        | 28%   | 58%     | 14%   | 1.00         | 57%         |
| factor 0.2, flat   | 1506        | 30%   | 53%     | 18%   | 1.00         | 56%         |
| factor 0.5, flat   | 1521        | 26%   | 61%     | 13%   | 1.00         | 55%         |
| cost 1, noflat     | 1520        | 32%   | 48%     | 20%   | 0.97         | 63%         |
| factor 0.2, noflat | 1478        | 33%   | 43%     | 24%   | 0.99         | 59%         |
| factor 0.5, noflat | 1527        | 32%   | 50%     | 18%   | 0.97         | 64%         |

Of 1820 (problem, abstraction) pairs, 939 (52%) help alone under at least one setting and 228 (13%) under every setting they were run in.

## 2. Can a set's effect be predicted from its members?

For (problem, setting) pairs where the set and every member have a ratio. Error is |log2(predicted / actual)|: 1.0 means off by 2x.

| predictor          | Spearman with set ratio | median error (log2) | within 1.5x |
|--------------------|-------------------------|---------------------|-------------|
| best single        | 0.67                    | 0.87                | 34%         |
| product of singles | 0.61                    | 2.04                | 19%         |
| geometric mean     | 0.62                    | 1.04                | 31%         |

1138 pairs. Set helps although no member helps alone: 67 (6%). Some member helps alone but the set does not: 261 (23%).

## 3. Are labels stable across settings?

Single-abstraction labels, Spearman of log ratios between two settings over the same (problem, abstraction) pairs, and how often one says helps and the other hurts.

| setting A          | setting B          | pairs | Spearman | helps vs hurts |
|--------------------|--------------------|-------|----------|----------------|
| cost 1, flat       | factor 0.2, flat   | 1501  | 0.76     | 27 (2%)        |
| cost 1, flat       | factor 0.5, flat   | 1513  | 0.89     | 13 (1%)        |
| cost 1, flat       | cost 1, noflat     | 1227  | 0.24     | 92 (7%)        |
| factor 0.2, flat   | factor 0.5, flat   | 1499  | 0.69     | 36 (2%)        |
| factor 0.2, flat   | factor 0.2, noflat | 1203  | 0.22     | 112 (9%)       |
| factor 0.5, flat   | factor 0.5, noflat | 1233  | 0.23     | 80 (6%)        |
| cost 1, noflat     | factor 0.2, noflat | 1468  | 0.77     | 42 (3%)        |
| cost 1, noflat     | factor 0.5, noflat | 1514  | 0.87     | 21 (1%)        |
| factor 0.2, noflat | factor 0.5, noflat | 1467  | 0.70     | 55 (4%)        |

## 4. Do our ratios agree with Twitch's?

Full sets run by both, same weight setting and flattening: 735. Spearman of log ratios: 0.62.

| Twitch \ ours | helps | neutral | hurts |
|---------------|-------|---------|-------|
| helps         | 437   | 74      | 42    |
| neutral       | 50    | 45      | 20    |
| hurts         | 16    | 24      | 27    |

Same class: 509 of 735 (69%); helps vs hurts contradictions: 58 (8%).

By setting:

| setting            | pairs | Spearman | same class |
|--------------------|-------|----------|------------|
| cost 1, flat       | 93    | 0.72     | 73%        |
| factor 0.2, flat   | 88    | 0.72     | 61%        |
| factor 0.5, flat   | 111   | 0.71     | 68%        |
| cost 1, noflat     | 124   | 0.63     | 73%        |
| factor 0.2, noflat | 147   | 0.61     | 68%        |
| factor 0.5, noflat | 172   | 0.45     | 70%        |

Twitch's ratios are wall-clock times from a different Twee build and the CPU-time schedule; ours are CP counts under the allocation clock.

Wrote 10510 labels to data/single_labels.jsonl.
