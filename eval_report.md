# Twee evaluation of generated sets

Re-scored with an allocation budget of 2.8e+12 bytes: a run counts as proved only if it allocated at most that; ratios are allocation ratios.

## 0. Budget check

Allocation rate of proved runs over 10 s: min 0.85, 1% 1.16, median 2.36 GB/s (1635 runs).
Shortest wall-clock timeout 2400 s, so timed-out runs allocated at least ~2.8 TB (1% rate).
Allocation budget 2.80 TB: ABOVE that: some timeouts might have finished within the budget; choose a smaller one.
187 proved runs exceed the budget and count as unproved.

## 1. Generated sets against plain Twee

| method | k | flatten | split | problems | base proved | set proved | new | lost | both | median ratio | geo-mean ratio | ≥1.5x faster | ≥1.5x slower |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base_combined | 1 | on | hard | 96 | 1 | 11 | 11 | 1 | 0 | – | – | 0 | 0 |
| base_combined | 1 | on | test | 97 | 78 | 85 | 14 | 7 | 71 | 1.04 | 1.11 | 12 | 20 |
| rerank | 1 | on | hard | 96 | 1 | 15 | 15 | 1 | 0 | – | – | 0 | 0 |
| rerank | 1 | on | test | 97 | 78 | 88 | 13 | 3 | 75 | 1.04 | 0.96 | 16 | 23 |
| base_combined | 1 | off | hard | 96 | 1 | 7 | 7 | 1 | 0 | – | – | 0 | 0 |
| base_combined | 1 | off | test | 97 | 84 | 84 | 5 | 5 | 79 | 0.79 | 0.64 | 38 | 14 |
| rerank | 1 | off | hard | 96 | 1 | 11 | 11 | 1 | 0 | – | – | 0 | 0 |
| rerank | 1 | off | test | 97 | 84 | 85 | 5 | 4 | 80 | 0.94 | 0.77 | 36 | 15 |
| base_combined | 3 | on | hard | 96 | 1 | 16 | 16 | 1 | 0 | – | – | 0 | 0 |
| base_combined | 3 | on | test | 97 | 78 | 79 | 7 | 6 | 72 | 1.11 | 0.84 | 23 | 31 |
| mix | 3 | on | hard | 96 | 1 | 16 | 16 | 1 | 0 | – | – | 0 | 0 |
| mix | 3 | on | test | 97 | 78 | 79 | 7 | 6 | 72 | 1.08 | 0.83 | 23 | 29 |
| rerank | 3 | on | hard | 96 | 1 | 18 | 17 | 0 | 1 | 0.92 | 0.92 | 0 | 0 |
| rerank | 3 | on | test | 97 | 78 | 80 | 6 | 4 | 74 | 1.10 | 0.81 | 24 | 27 |
| base_combined | 3 | off | hard | 96 | 1 | 11 | 11 | 1 | 0 | – | – | 0 | 0 |
| base_combined | 3 | off | test | 97 | 84 | 84 | 5 | 5 | 79 | 0.82 | 0.59 | 34 | 17 |
| mix | 3 | off | hard | 96 | 1 | 12 | 12 | 1 | 0 | – | – | 0 | 0 |
| mix | 3 | off | test | 97 | 84 | 84 | 5 | 5 | 79 | 0.82 | 0.58 | 34 | 19 |
| rerank | 3 | off | hard | 96 | 1 | 9 | 8 | 0 | 1 | 0.23 | 0.23 | 1 | 0 |
| rerank | 3 | off | test | 97 | 84 | 76 | 4 | 12 | 72 | 0.87 | 0.97 | 26 | 22 |
| base_combined | 5 | on | hard | 96 | 1 | 17 | 17 | 1 | 0 | – | – | 0 | 0 |
| base_combined | 5 | on | test | 97 | 78 | 75 | 4 | 7 | 71 | 0.87 | 0.65 | 26 | 19 |
| mix | 5 | on | hard | 96 | 1 | 17 | 17 | 1 | 0 | – | – | 0 | 0 |
| mix | 5 | on | test | 97 | 78 | 75 | 4 | 7 | 71 | 0.87 | 0.66 | 26 | 21 |
| rerank | 5 | on | hard | 96 | 1 | 16 | 16 | 1 | 0 | – | – | 0 | 0 |
| rerank | 5 | on | test | 97 | 78 | 76 | 6 | 8 | 70 | 1.00 | 0.79 | 21 | 21 |
| base_combined | 5 | off | hard | 96 | 1 | 11 | 11 | 1 | 0 | – | – | 0 | 0 |
| base_combined | 5 | off | test | 97 | 84 | 80 | 4 | 8 | 76 | 1.08 | 1.01 | 30 | 33 |
| mix | 5 | off | hard | 96 | 1 | 11 | 11 | 1 | 0 | – | – | 0 | 0 |
| mix | 5 | off | test | 97 | 84 | 80 | 4 | 8 | 76 | 1.08 | 0.97 | 30 | 34 |
| rerank | 5 | off | hard | 96 | 1 | 7 | 7 | 1 | 0 | – | – | 0 | 0 |
| rerank | 5 | off | test | 97 | 84 | 81 | 4 | 7 | 77 | 1.25 | 1.39 | 23 | 30 |

ratio = cost with the set / cost without (CPs, or allocated bytes with --alloc-budget), on problems both prove; below 1 is faster. Ratios within 0.67–1.5 are within schedule noise.

## 2. Head to head

| A | B | k | flatten | split | problems | only A proves | only B proves | both | median A/B | A ≥1.5x faster | B ≥1.5x faster |
|---|---|---|---|---|---|---|---|---|---|---|---|
| base_combined | mix | 3 | on | hard | 96 | 0 | 0 | 16 | 1.00 | 1 | 3 |
| base_combined | mix | 3 | on | test | 97 | 0 | 0 | 79 | 1.00 | 0 | 0 |
| base_combined | mix | 3 | off | hard | 96 | 0 | 1 | 11 | 1.00 | 1 | 0 |
| base_combined | mix | 3 | off | test | 97 | 0 | 0 | 84 | 1.00 | 2 | 0 |
| base_combined | mix | 5 | on | hard | 96 | 0 | 0 | 17 | 1.00 | 0 | 0 |
| base_combined | mix | 5 | on | test | 97 | 0 | 0 | 75 | 1.00 | 2 | 0 |
| base_combined | mix | 5 | off | hard | 96 | 0 | 0 | 11 | 1.00 | 0 | 0 |
| base_combined | mix | 5 | off | test | 97 | 0 | 0 | 80 | 1.00 | 1 | 5 |
| base_combined | rerank | 1 | on | hard | 96 | 1 | 5 | 10 | 1.00 | 2 | 3 |
| base_combined | rerank | 1 | on | test | 97 | 1 | 4 | 84 | 1.00 | 5 | 5 |
| base_combined | rerank | 1 | off | hard | 96 | 1 | 5 | 6 | 1.00 | 0 | 0 |
| base_combined | rerank | 1 | off | test | 97 | 0 | 1 | 84 | 1.00 | 14 | 10 |
| base_combined | rerank | 3 | on | hard | 96 | 3 | 5 | 13 | 1.10 | 3 | 4 |
| base_combined | rerank | 3 | on | test | 97 | 3 | 4 | 76 | 1.00 | 14 | 14 |
| base_combined | rerank | 3 | off | hard | 96 | 4 | 2 | 7 | 1.00 | 1 | 2 |
| base_combined | rerank | 3 | off | test | 97 | 10 | 2 | 74 | 0.86 | 33 | 5 |
| base_combined | rerank | 5 | on | hard | 96 | 4 | 3 | 13 | 1.36 | 0 | 6 |
| base_combined | rerank | 5 | on | test | 97 | 3 | 4 | 72 | 0.93 | 23 | 15 |
| base_combined | rerank | 5 | off | hard | 96 | 4 | 0 | 7 | 1.66 | 0 | 4 |
| base_combined | rerank | 5 | off | test | 97 | 2 | 3 | 78 | 0.95 | 28 | 17 |
| mix | rerank | 3 | on | hard | 96 | 3 | 5 | 13 | 1.00 | 4 | 3 |
| mix | rerank | 3 | on | test | 97 | 3 | 4 | 76 | 1.00 | 14 | 14 |
| mix | rerank | 3 | off | hard | 96 | 5 | 2 | 7 | 1.00 | 1 | 2 |
| mix | rerank | 3 | off | test | 97 | 10 | 2 | 74 | 0.89 | 31 | 5 |
| mix | rerank | 5 | on | hard | 96 | 4 | 3 | 13 | 1.36 | 0 | 6 |
| mix | rerank | 5 | on | test | 97 | 3 | 4 | 72 | 0.93 | 23 | 17 |
| mix | rerank | 5 | off | hard | 96 | 4 | 0 | 7 | 1.66 | 0 | 4 |
| mix | rerank | 5 | off | test | 97 | 2 | 3 | 78 | 0.94 | 28 | 14 |

## 3. Portfolio over both flattening settings

Proved in either setting (base = plain Twee with flattening on or off).

| method | k | split | problems | base proved | set proved | new | lost |
|---|---|---|---|---|---|---|---|
| base_combined | 1 | hard | 96 | 1 | 14 | 14 | 1 |
| base_combined | 1 | test | 97 | 97 | 96 | 0 | 1 |
| rerank | 1 | hard | 96 | 1 | 19 | 19 | 1 |
| rerank | 1 | test | 97 | 97 | 96 | 0 | 1 |
| base_combined | 3 | hard | 96 | 1 | 18 | 18 | 1 |
| base_combined | 3 | test | 97 | 97 | 92 | 0 | 5 |
| mix | 3 | hard | 96 | 1 | 18 | 18 | 1 |
| mix | 3 | test | 97 | 97 | 92 | 0 | 5 |
| rerank | 3 | hard | 96 | 1 | 20 | 19 | 0 |
| rerank | 3 | test | 97 | 97 | 93 | 0 | 4 |
| base_combined | 5 | hard | 96 | 1 | 20 | 20 | 1 |
| base_combined | 5 | test | 97 | 97 | 92 | 0 | 5 |
| mix | 5 | hard | 96 | 1 | 20 | 20 | 1 |
| mix | 5 | test | 97 | 97 | 92 | 0 | 5 |
| rerank | 5 | hard | 96 | 1 | 17 | 17 | 1 |
| rerank | 5 | test | 97 | 97 | 94 | 0 | 3 |

## 4. Complementarity

Proved in any configuration of a method (any k, either flattening setting).

### hard

| | proved | new (not plain Twee) | only this method |
|---|---|---|---|
| plain Twee (either setting) | 1 | – | – |
| base_combined | 22 | 22 | 0 |
| mix | 22 | 22 | 0 |
| rerank | 25 | 24 | 6 |
| union of all sets | 28 | 27 | – |
| union of all sets and plain Twee | 28 | – | – |

Newly proved problems by number of configurations (of 16) that prove them: 1: 4, 2: 2, 4: 2, 5: 2, 6: 1, 7: 1, 8: 4, 9: 3, 10: 1, 11: 3, 15: 2, 16: 2.

- only rerank: COL002-10 (k1n k1f), LAT075-1 (k3n), LAT400-1 (k1n), LAT400-3 (k5f), LCL304-10 (k1f)

### test

| | proved | new (not plain Twee) | only this method |
|---|---|---|---|
| plain Twee (either setting) | 97 | – | – |
| base_combined | 96 | 0 | 0 |
| mix | 93 | 0 | 0 |
| rerank | 97 | 0 | 1 |
| union of all sets | 97 | 0 | – |
| union of all sets and plain Twee | 97 | – | – |

