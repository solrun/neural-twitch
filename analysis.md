# First-milestone analysis of existing Twitch runs

Rows: 16875 runs over 1041 problems.

## 1. Label noise (wall clock)

Baseline time is recorded as the minimum over repeated base runs. For 307 problems with baseline >= 1.0s, mean/min baseline time has median 1.03, 90th percentile 1.17, max 2.80.

19 (problem, set, config) triples were run more than once; max/min hinted time across repeats has median 1.01, max 1.84.

## 2. How often a local set helps

Usable runs (baseline >= 1.0s, outcome known): 3471 on 306 problems.

| hint-skel-factor | hint-skel-cost | flatten | runs | >=1.5x faster | >=1.5x slower (incl. timeout) |
|---|---|---|---|---|---|
| 0.0 | 0.0 | False | 243 | 45.3% | 41.2% |
| 0.0 | 0.0 | True | 151 | 53.6% | 28.5% |
| 0.0 | 1.0 | False | 243 | 60.9% | 17.7% |
| 0.0 | 1.0 | True | 151 | 64.2% | 15.9% |
| 0.0 | 2.0 | False | 243 | 45.3% | 22.6% |
| 0.0 | 2.0 | True | 151 | 40.4% | 23.2% |
| 0.2 | 0.0 | False | 451 | 56.1% | 25.9% |
| 0.2 | 0.0 | True | 151 | 58.9% | 22.5% |
| 0.5 | 0.0 | False | 694 | 52.3% | 19.3% |
| 0.5 | 0.0 | True | 205 | 61.5% | 16.6% |
| 0.7 | 0.0 | False | 243 | 50.2% | 13.2% |
| 0.7 | 0.0 | True | 151 | 49.7% | 22.5% |
| 1.0 | 0.0 | False | 243 | 14.4% | 35.4% |
| 1.0 | 0.0 | True | 151 | 16.6% | 33.1% |

For 243 abstraction sets run under 3+ weight settings (no flattening), the best/worst ratio differs by a median factor of 15.98; in 118 of them (48.6%) the same set is a >=1.5x speedup under one setting and a >=1.5x slowdown under another.

Taking the best configuration per problem: 269 of 306 problems (87.9%) get a >=1.5x speedup.

## 3. What abstractions in helpful sets look like

| | in >=1.5x-faster sets | in >=1.5x-slower sets |
|---|---|---|
| abstraction occurrences | 10724 | 5135 |
| median set size | 7 | 7 |
| median skeleton weight | 3.0 | 2 |
| skeleton weight <= 3 | 64.5% | 81.7% |
| nonlinear (repeated variable) | 38.8% | 30.1% |
| ground | 4.3% | 4.3% |
| mentions a constant | 30.8% | 23.7% |

## 4. Recurrence across problems and domains

884 distinct canonical abstractions occur in helpful sets. 281 (31.8%) occur in helpful sets for 2+ problems, 26 (2.9%) in 2+ domains.

Most widespread (problems / domains):

| abstraction | problems | domains |
|---|---|---|
| `join(X0, meet(X1, X2))` | 57 | LAT,REL |
| `meet(X0, join(X1, X2))` | 52 | LAT,REL |
| `join(X0, complement(X1))` | 41 | LAT,REL |
| `join(complement(X0), complement(X1))` | 33 | LAT,REL |
| `join(complement(X0), X1)` | 31 | LAT,REL |
| `multiply(inverse(X0), X1)` | 28 | GRP |
| `composition(converse(X0), X1)` | 25 | REL |
| `meet(X0, complement(X1))` | 24 | LAT,REL |
| `join(X0, join(X1, X2))` | 24 | LAT,REL |
| `greatest_lower_bound(X0, identity)` | 20 | GRP |
| `converse(complement(X0))` | 20 | REL |
| `meet(X0, join(X1, meet(X0, X2)))` | 20 | LAT |
| `meet(X0, meet(X1, X2))` | 19 | LAT |
| `least_upper_bound(X0, identity)` | 18 | GRP |
| `greatest_lower_bound(identity, X0)` | 17 | GRP |

## 5. Is enumeration of small patterns viable?

Coverage of helpful abstractions by skeleton weight, and the per-problem number of candidate patterns an enumerator would have to consider (median over problems with a helpful set; signature = symbols in the problem file plus those seen in its abstractions, so this is a lower bound):

| max skeleton weight | helpful abstractions covered | median candidates / problem | max candidates / problem |
|---|---|---|---|
| 1 | 1.0% | 8 | 48 |
| 2 | 45.3% | 124 | 22,350 |
| 3 | 64.5% | 2,766 | 33,701,424 |
| 4 | 76.3% | 80,660 | 105,634,723,558 |
| 5 | 82.8% | 2,850,688 | 570,210,963,165,850 |
| 6 | 86.1% | 116,961,432 | 4,755,549,950,914,402,744 |

Signature size over those problems: median 5, max 12 symbols.

