# Twee evaluation of generated sets

## 1. Generated sets against plain Twee

| method | k | flatten | split | problems | base proved | set proved | new | lost | both | median ratio | geo-mean ratio | ≥1.5x faster | ≥1.5x slower |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base_combined | 1 | on | hard | 96 | 3 | 12 | 11 | 2 | 1 | 0.76 | 0.76 | 0 | 0 |
| base_combined | 1 | on | test | 97 | 81 | 85 | 11 | 7 | 74 | 1.00 | 1.03 | 18 | 14 |
| rerank | 1 | on | hard | 96 | 3 | 15 | 15 | 3 | 0 | – | – | 0 | 0 |
| rerank | 1 | on | test | 97 | 81 | 88 | 10 | 3 | 78 | 1.00 | 0.89 | 19 | 16 |
| base_combined | 1 | off | hard | 96 | 3 | 9 | 9 | 3 | 0 | – | – | 0 | 0 |
| base_combined | 1 | off | test | 97 | 89 | 85 | 0 | 4 | 85 | 0.75 | 0.55 | 36 | 7 |
| rerank | 1 | off | hard | 96 | 3 | 17 | 16 | 2 | 1 | 0.21 | 0.21 | 1 | 0 |
| rerank | 1 | off | test | 97 | 89 | 85 | 0 | 4 | 85 | 0.75 | 0.58 | 36 | 5 |
| base_combined | 3 | on | hard | 96 | 3 | 19 | 19 | 3 | 0 | – | – | 0 | 0 |
| base_combined | 3 | on | test | 97 | 80 | 82 | 7 | 5 | 75 | 1.00 | 0.64 | 24 | 22 |
| mix | 3 | on | hard | 96 | 6 | 20 | 18 | 4 | 2 | 0.61 | 0.58 | 1 | 0 |
| mix | 3 | on | test | 97 | 87 | 85 | 4 | 6 | 81 | 0.94 | 0.64 | 27 | 23 |
| rerank | 3 | on | hard | 96 | 3 | 19 | 18 | 2 | 1 | 0.33 | 0.33 | 1 | 0 |
| rerank | 3 | on | test | 97 | 80 | 80 | 6 | 6 | 74 | 0.91 | 0.62 | 29 | 19 |
| base_combined | 3 | off | hard | 96 | 3 | 14 | 13 | 2 | 1 | 0.14 | 0.14 | 1 | 0 |
| base_combined | 3 | off | test | 97 | 89 | 85 | 0 | 4 | 85 | 0.65 | 0.44 | 44 | 15 |
| mix | 3 | off | hard | 96 | 5 | 19 | 17 | 3 | 2 | 0.30 | 0.25 | 2 | 0 |
| mix | 3 | off | test | 97 | 90 | 87 | 0 | 3 | 87 | 0.65 | 0.47 | 44 | 16 |
| rerank | 3 | off | hard | 96 | 3 | 11 | 9 | 1 | 2 | 0.16 | 0.16 | 2 | 0 |
| rerank | 3 | off | test | 97 | 89 | 78 | 2 | 13 | 76 | 0.76 | 0.63 | 34 | 18 |
| base_combined | 5 | on | hard | 96 | 3 | 19 | 19 | 3 | 0 | – | – | 0 | 0 |
| base_combined | 5 | on | test | 97 | 80 | 76 | 4 | 8 | 72 | 0.80 | 0.54 | 30 | 11 |
| mix | 5 | on | hard | 96 | 6 | 20 | 19 | 5 | 1 | 0.17 | 0.17 | 1 | 0 |
| mix | 5 | on | test | 97 | 87 | 81 | 4 | 10 | 77 | 0.79 | 0.54 | 31 | 11 |
| rerank | 5 | on | hard | 96 | 3 | 17 | 17 | 3 | 0 | – | – | 0 | 0 |
| rerank | 5 | on | test | 97 | 81 | 76 | 6 | 11 | 70 | 0.79 | 0.59 | 27 | 13 |
| base_combined | 5 | off | hard | 96 | 3 | 15 | 14 | 2 | 1 | 0.10 | 0.10 | 1 | 0 |
| base_combined | 5 | off | test | 97 | 89 | 81 | 1 | 9 | 80 | 0.73 | 0.58 | 39 | 20 |
| mix | 5 | off | hard | 96 | 5 | 15 | 14 | 4 | 1 | 0.12 | 0.12 | 1 | 0 |
| mix | 5 | off | test | 97 | 90 | 82 | 0 | 8 | 82 | 0.73 | 0.56 | 40 | 15 |
| rerank | 5 | off | hard | 96 | 3 | 8 | 8 | 3 | 0 | – | – | 0 | 0 |
| rerank | 5 | off | test | 97 | 89 | 81 | 1 | 9 | 80 | 0.75 | 0.68 | 36 | 18 |

ratio = CPs with the set / CPs without, on problems both prove; below 1 is faster. Ratios within 0.67–1.5 are within schedule noise.

## 2. Head to head

| A | B | k | flatten | split | problems | only A proves | only B proves | both | median A/B | A ≥1.5x faster | B ≥1.5x faster |
|---|---|---|---|---|---|---|---|---|---|---|---|
| base_combined | mix | 3 | on | hard | 96 | 0 | 1 | 19 | 1.00 | 1 | 1 |
| base_combined | mix | 3 | on | test | 97 | 0 | 3 | 82 | 1.00 | 0 | 0 |
| base_combined | mix | 3 | off | hard | 96 | 0 | 5 | 14 | 1.00 | 1 | 0 |
| base_combined | mix | 3 | off | test | 97 | 0 | 2 | 85 | 1.00 | 0 | 0 |
| base_combined | mix | 5 | on | hard | 96 | 0 | 1 | 19 | 1.00 | 0 | 0 |
| base_combined | mix | 5 | on | test | 97 | 0 | 5 | 76 | 1.00 | 2 | 0 |
| base_combined | mix | 5 | off | hard | 96 | 0 | 0 | 15 | 1.00 | 1 | 0 |
| base_combined | mix | 5 | off | test | 97 | 0 | 1 | 81 | 1.00 | 0 | 1 |
| base_combined | rerank | 1 | on | hard | 96 | 2 | 5 | 10 | 1.30 | 1 | 3 |
| base_combined | rerank | 1 | on | test | 97 | 1 | 4 | 84 | 1.00 | 6 | 5 |
| base_combined | rerank | 1 | off | hard | 96 | 0 | 8 | 9 | 1.00 | 0 | 0 |
| base_combined | rerank | 1 | off | test | 97 | 0 | 0 | 85 | 1.00 | 13 | 10 |
| base_combined | rerank | 3 | on | hard | 96 | 4 | 4 | 15 | 1.10 | 1 | 4 |
| base_combined | rerank | 3 | on | test | 97 | 5 | 3 | 77 | 1.00 | 13 | 14 |
| base_combined | rerank | 3 | off | hard | 96 | 7 | 4 | 7 | 1.00 | 0 | 2 |
| base_combined | rerank | 3 | off | test | 97 | 10 | 3 | 75 | 0.95 | 29 | 3 |
| base_combined | rerank | 5 | on | hard | 96 | 5 | 3 | 14 | 1.14 | 0 | 6 |
| base_combined | rerank | 5 | on | test | 97 | 3 | 3 | 73 | 1.02 | 17 | 17 |
| base_combined | rerank | 5 | off | hard | 96 | 8 | 1 | 7 | 1.53 | 0 | 5 |
| base_combined | rerank | 5 | off | test | 97 | 3 | 3 | 78 | 1.00 | 26 | 13 |
| mix | rerank | 3 | on | hard | 96 | 4 | 3 | 16 | 1.05 | 1 | 4 |
| mix | rerank | 3 | on | test | 97 | 8 | 3 | 77 | 1.00 | 13 | 14 |
| mix | rerank | 3 | off | hard | 96 | 11 | 3 | 8 | 1.00 | 0 | 3 |
| mix | rerank | 3 | off | test | 97 | 10 | 1 | 77 | 0.95 | 27 | 5 |
| mix | rerank | 5 | on | hard | 96 | 6 | 3 | 14 | 1.14 | 0 | 6 |
| mix | rerank | 5 | on | test | 97 | 6 | 1 | 75 | 1.02 | 17 | 19 |
| mix | rerank | 5 | off | hard | 96 | 8 | 1 | 7 | 1.53 | 0 | 5 |
| mix | rerank | 5 | off | test | 97 | 4 | 3 | 78 | 0.98 | 26 | 11 |

## 3. Portfolio over both flattening settings

Proved in either setting (base = plain Twee with flattening on or off).

| method | k | split | problems | base proved | set proved | new | lost |
|---|---|---|---|---|---|---|---|
| base_combined | 1 | hard | 96 | 4 | 17 | 16 | 3 |
| base_combined | 1 | test | 97 | 97 | 96 | 0 | 1 |
| rerank | 1 | hard | 96 | 4 | 24 | 23 | 3 |
| rerank | 1 | test | 97 | 97 | 96 | 0 | 1 |
| base_combined | 3 | hard | 96 | 4 | 22 | 21 | 3 |
| base_combined | 3 | test | 97 | 97 | 93 | 0 | 4 |
| mix | 3 | hard | 96 | 8 | 25 | 21 | 4 |
| mix | 3 | test | 97 | 97 | 94 | 0 | 3 |
| rerank | 3 | hard | 96 | 4 | 22 | 20 | 2 |
| rerank | 3 | test | 97 | 97 | 93 | 0 | 4 |
| base_combined | 5 | hard | 96 | 4 | 23 | 22 | 3 |
| base_combined | 5 | test | 97 | 97 | 92 | 0 | 5 |
| mix | 5 | hard | 96 | 8 | 24 | 22 | 6 |
| mix | 5 | test | 97 | 97 | 92 | 0 | 5 |
| rerank | 5 | hard | 96 | 4 | 18 | 17 | 3 |
| rerank | 5 | test | 97 | 97 | 94 | 0 | 3 |

## 4. Complementarity

Proved in any configuration of a method (any k, either flattening setting).

### hard

| | proved | new (not plain Twee) | only this method |
|---|---|---|---|
| plain Twee (either setting) | 8 | – | – |
| base_combined | 26 | 22 | 1 |
| mix | 27 | 23 | 1 |
| rerank | 31 | 26 | 5 |
| union of all sets | 33 | 26 | – |
| union of all sets and plain Twee | 34 | – | – |

Newly proved problems by number of configurations (of 16) that prove them: 1: 2, 2: 2, 4: 1, 5: 3, 8: 5, 9: 3, 10: 1, 11: 5, 15: 2, 16: 2.

- only rerank: GRP693-1 (k3n), LAT400-1 (k1n), LAT400-3 (k5n k5f)
- plain Twee only: GRP689-1

### test

| | proved | new (not plain Twee) | only this method |
|---|---|---|---|
| plain Twee (either setting) | 97 | – | – |
| base_combined | 96 | 0 | 0 |
| mix | 94 | 0 | 0 |
| rerank | 97 | 0 | 1 |
| union of all sets | 97 | 0 | – |
| union of all sets and plain Twee | 97 | – | – |

