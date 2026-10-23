# Twee evaluation of generated sets

Re-scored with an allocation budget of 2e+12 bytes: a run counts as proved only if it allocated at most that; ratios are allocation ratios.

## 0. Budget check

Allocation rate of proved runs over 10 s: min 0.85, 1% 1.16, median 2.36 GB/s (1635 runs).
Shortest wall-clock timeout 2400 s, so timed-out runs allocated at least ~2.8 TB (1% rate).
Allocation budget 2.00 TB: below that, so every timeout counts as over budget and the results are deterministic.
264 proved runs exceed the budget and count as unproved.

## 1. Generated sets against plain Twee

| method | k | flatten | split | problems | base proved | set proved | new | lost | both | median ratio | geo-mean ratio | ≥1.5x faster | ≥1.5x slower |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base_combined | 1 | on | hard | 96 | 0 | 11 | 11 | 0 | 0 | – | – | 0 | 0 |
| base_combined | 1 | on | test | 97 | 78 | 78 | 7 | 7 | 71 | 1.04 | 1.11 | 12 | 20 |
| rerank | 1 | on | hard | 96 | 0 | 14 | 14 | 0 | 0 | – | – | 0 | 0 |
| rerank | 1 | on | test | 97 | 78 | 82 | 7 | 3 | 75 | 1.04 | 0.96 | 16 | 23 |
| base_combined | 1 | off | hard | 96 | 0 | 4 | 4 | 0 | 0 | – | – | 0 | 0 |
| base_combined | 1 | off | test | 97 | 84 | 84 | 5 | 5 | 79 | 0.79 | 0.64 | 38 | 14 |
| rerank | 1 | off | hard | 96 | 0 | 7 | 7 | 0 | 0 | – | – | 0 | 0 |
| rerank | 1 | off | test | 97 | 84 | 85 | 5 | 4 | 80 | 0.94 | 0.77 | 36 | 15 |
| base_combined | 3 | on | hard | 96 | 0 | 11 | 11 | 0 | 0 | – | – | 0 | 0 |
| base_combined | 3 | on | test | 97 | 78 | 77 | 6 | 7 | 71 | 1.09 | 0.82 | 23 | 30 |
| mix | 3 | on | hard | 96 | 0 | 13 | 13 | 0 | 0 | – | – | 0 | 0 |
| mix | 3 | on | test | 97 | 78 | 77 | 6 | 7 | 71 | 1.07 | 0.81 | 23 | 28 |
| rerank | 3 | on | hard | 96 | 0 | 16 | 16 | 0 | 0 | – | – | 0 | 0 |
| rerank | 3 | on | test | 97 | 78 | 79 | 6 | 5 | 73 | 1.06 | 0.79 | 24 | 26 |
| base_combined | 3 | off | hard | 96 | 0 | 8 | 8 | 0 | 0 | – | – | 0 | 0 |
| base_combined | 3 | off | test | 97 | 84 | 82 | 3 | 5 | 79 | 0.82 | 0.59 | 34 | 17 |
| mix | 3 | off | hard | 96 | 0 | 8 | 8 | 0 | 0 | – | – | 0 | 0 |
| mix | 3 | off | test | 97 | 84 | 82 | 3 | 5 | 79 | 0.82 | 0.58 | 34 | 19 |
| rerank | 3 | off | hard | 96 | 0 | 9 | 9 | 0 | 0 | – | – | 0 | 0 |
| rerank | 3 | off | test | 97 | 84 | 76 | 4 | 12 | 72 | 0.87 | 0.97 | 26 | 22 |
| base_combined | 5 | on | hard | 96 | 0 | 14 | 14 | 0 | 0 | – | – | 0 | 0 |
| base_combined | 5 | on | test | 97 | 78 | 75 | 4 | 7 | 71 | 0.87 | 0.65 | 26 | 19 |
| mix | 5 | on | hard | 96 | 0 | 14 | 14 | 0 | 0 | – | – | 0 | 0 |
| mix | 5 | on | test | 97 | 78 | 75 | 4 | 7 | 71 | 0.87 | 0.66 | 26 | 21 |
| rerank | 5 | on | hard | 96 | 0 | 15 | 15 | 0 | 0 | – | – | 0 | 0 |
| rerank | 5 | on | test | 97 | 78 | 75 | 6 | 9 | 69 | 0.98 | 0.72 | 21 | 20 |
| base_combined | 5 | off | hard | 96 | 0 | 10 | 10 | 0 | 0 | – | – | 0 | 0 |
| base_combined | 5 | off | test | 97 | 84 | 79 | 4 | 9 | 75 | 1.04 | 0.96 | 30 | 32 |
| mix | 5 | off | hard | 96 | 0 | 10 | 10 | 0 | 0 | – | – | 0 | 0 |
| mix | 5 | off | test | 97 | 84 | 79 | 4 | 9 | 75 | 1.04 | 0.92 | 30 | 33 |
| rerank | 5 | off | hard | 96 | 0 | 6 | 6 | 0 | 0 | – | – | 0 | 0 |
| rerank | 5 | off | test | 97 | 84 | 80 | 4 | 8 | 76 | 1.16 | 1.28 | 23 | 29 |

ratio = cost with the set / cost without (CPs, or allocated bytes with --alloc-budget), on problems both prove; below 1 is faster. Ratios within 0.67–1.5 are within schedule noise.

## 2. Head to head

| A | B | k | flatten | split | problems | only A proves | only B proves | both | median A/B | A ≥1.5x faster | B ≥1.5x faster |
|---|---|---|---|---|---|---|---|---|---|---|---|
| base_combined | mix | 3 | on | hard | 96 | 0 | 2 | 11 | 1.00 | 1 | 1 |
| base_combined | mix | 3 | on | test | 97 | 0 | 0 | 77 | 1.00 | 0 | 0 |
| base_combined | mix | 3 | off | hard | 96 | 0 | 0 | 8 | 1.00 | 1 | 0 |
| base_combined | mix | 3 | off | test | 97 | 0 | 0 | 82 | 1.00 | 2 | 0 |
| base_combined | mix | 5 | on | hard | 96 | 0 | 0 | 14 | 1.00 | 0 | 0 |
| base_combined | mix | 5 | on | test | 97 | 0 | 0 | 75 | 1.00 | 2 | 0 |
| base_combined | mix | 5 | off | hard | 96 | 0 | 0 | 10 | 1.00 | 0 | 0 |
| base_combined | mix | 5 | off | test | 97 | 0 | 0 | 79 | 1.00 | 1 | 5 |
| base_combined | rerank | 1 | on | hard | 96 | 1 | 4 | 10 | 1.00 | 2 | 3 |
| base_combined | rerank | 1 | on | test | 97 | 0 | 4 | 78 | 1.00 | 5 | 5 |
| base_combined | rerank | 1 | off | hard | 96 | 0 | 3 | 4 | 1.00 | 0 | 0 |
| base_combined | rerank | 1 | off | test | 97 | 0 | 1 | 84 | 1.00 | 14 | 10 |
| base_combined | rerank | 3 | on | hard | 96 | 0 | 5 | 11 | 1.23 | 3 | 4 |
| base_combined | rerank | 3 | on | test | 97 | 2 | 4 | 75 | 1.00 | 14 | 14 |
| base_combined | rerank | 3 | off | hard | 96 | 1 | 2 | 7 | 1.00 | 1 | 2 |
| base_combined | rerank | 3 | off | test | 97 | 8 | 2 | 74 | 0.86 | 33 | 5 |
| base_combined | rerank | 5 | on | hard | 96 | 2 | 3 | 12 | 1.68 | 0 | 6 |
| base_combined | rerank | 5 | on | test | 97 | 4 | 4 | 71 | 0.93 | 22 | 15 |
| base_combined | rerank | 5 | off | hard | 96 | 4 | 0 | 6 | 1.96 | 0 | 4 |
| base_combined | rerank | 5 | off | test | 97 | 2 | 3 | 77 | 0.95 | 28 | 16 |
| mix | rerank | 3 | on | hard | 96 | 1 | 4 | 12 | 1.02 | 4 | 3 |
| mix | rerank | 3 | on | test | 97 | 2 | 4 | 75 | 1.00 | 14 | 14 |
| mix | rerank | 3 | off | hard | 96 | 1 | 2 | 7 | 1.00 | 1 | 2 |
| mix | rerank | 3 | off | test | 97 | 8 | 2 | 74 | 0.89 | 31 | 5 |
| mix | rerank | 5 | on | hard | 96 | 2 | 3 | 12 | 1.68 | 0 | 6 |
| mix | rerank | 5 | on | test | 97 | 4 | 4 | 71 | 0.93 | 22 | 17 |
| mix | rerank | 5 | off | hard | 96 | 4 | 0 | 6 | 1.96 | 0 | 4 |
| mix | rerank | 5 | off | test | 97 | 2 | 3 | 77 | 0.92 | 28 | 13 |

## 3. Portfolio over both flattening settings

Proved in either setting (base = plain Twee with flattening on or off).

| method | k | split | problems | base proved | set proved | new | lost |
|---|---|---|---|---|---|---|---|
| base_combined | 1 | hard | 96 | 0 | 12 | 12 | 0 |
| base_combined | 1 | test | 97 | 97 | 96 | 0 | 1 |
| rerank | 1 | hard | 96 | 0 | 15 | 15 | 0 |
| rerank | 1 | test | 97 | 97 | 96 | 0 | 1 |
| base_combined | 3 | hard | 96 | 0 | 13 | 13 | 0 |
| base_combined | 3 | test | 97 | 97 | 92 | 0 | 5 |
| mix | 3 | hard | 96 | 0 | 14 | 14 | 0 |
| mix | 3 | test | 97 | 97 | 92 | 0 | 5 |
| rerank | 3 | hard | 96 | 0 | 19 | 19 | 0 |
| rerank | 3 | test | 97 | 97 | 92 | 0 | 5 |
| base_combined | 5 | hard | 96 | 0 | 18 | 18 | 0 |
| base_combined | 5 | test | 97 | 97 | 92 | 0 | 5 |
| mix | 5 | hard | 96 | 0 | 18 | 18 | 0 |
| mix | 5 | test | 97 | 97 | 92 | 0 | 5 |
| rerank | 5 | hard | 96 | 0 | 16 | 16 | 0 |
| rerank | 5 | test | 97 | 97 | 93 | 0 | 4 |

## 4. Complementarity

Proved in any configuration of a method (any k, either flattening setting).

### hard

| | proved | new (not plain Twee) | only this method |
|---|---|---|---|
| plain Twee (either setting) | 0 | – | – |
| base_combined | 19 | 19 | 0 |
| mix | 19 | 19 | 0 |
| rerank | 23 | 23 | 5 |
| union of all sets | 24 | 24 | – |
| union of all sets and plain Twee | 24 | – | – |

Newly proved problems by number of configurations (of 16) that prove them: 1: 5, 2: 1, 3: 2, 5: 1, 7: 2, 8: 6, 9: 2, 10: 1, 15: 2, 16: 2.

- only rerank: COL046-1 (k3n), LAT075-1 (k3n), LAT400-3 (k5f), LCL304-10 (k1f), LCL339-10 (k3f)

### test

| | proved | new (not plain Twee) | only this method |
|---|---|---|---|
| plain Twee (either setting) | 97 | – | – |
| base_combined | 96 | 0 | 0 |
| mix | 93 | 0 | 0 |
| rerank | 96 | 0 | 0 |
| union of all sets | 96 | 0 | – |
| union of all sets and plain Twee | 97 | – | – |

