"""First-milestone analysis of the labeled Twitch dataset.

Answers, from existing data only:
  1. How noisy are wall-clock labels?
  2. How often does a local abstraction set help, and how much does the
     weight setting matter for the *same* set?
  3. What do helpful abstractions look like (size, linearity, constants)?
  4. Do helpful abstractions recur across problems and domains?
  5. Is brute-force enumeration of small patterns a viable baseline?

Usage:
    python -m nt.analyze data/labels.jsonl <twitch_repo>/data/TPTP > analysis.md
"""

from __future__ import annotations

import collections
import glob
import json
import os
import re
import statistics as st
import sys
from functools import lru_cache

from nt.terms import (App, is_linear, is_ground, parse, skeleton_weight,
                      symbols, variables)

MIN_BASE = 1.0      # seconds; below this, timing noise dominates
GOOD = 2 / 3        # ratio <= 2/3 means at least a 1.5x speedup
BAD = 1.5           # ratio >= 1.5 means at least a 1.5x slowdown


def load(path):
    return [json.loads(line) for line in open(path)]


def pct(a, b):
    return f"{100 * a / b:.1f}%" if b else "n/a"


# ---------------------------------------------------------------- signatures

_SYM = re.compile(r"([a-z][A-Za-z0-9_]*)\s*(\()?")


def problem_signature(path: str) -> dict[str, int]:
    """Function symbols and arities appearing in a TPTP CNF file (excluding
    included axiom files, which are not in the repo)."""
    text = "\n".join(l for l in open(path) if not l.lstrip().startswith("%"))
    sig: dict[str, int] = {}
    for m in re.finditer(r"cnf\(\s*[^,]+,\s*[^,]+,(.*?)\)\s*\.", text, re.S):
        body = m.group(1)
        for side in re.split(r"!=|=", body):
            side = side.strip().strip("()").strip()
            if not side:
                continue
            try:
                t = parse(side)
            except Exception:
                continue
            for f, n in symbols(t):
                sig[f] = max(sig.get(f, 0), n)
    return sig


@lru_cache(maxsize=None)
def bell(n: int) -> int:
    if n == 0:
        return 1
    from math import comb
    return sum(comb(n - 1, k) * bell(k) for k in range(n))


def enumeration_space(sig: dict[str, int], max_skel: int) -> int:
    """Number of distinct alpha-normalised, function-rooted patterns with at
    most max_skel symbol occurrences over the given signature. Variable leaves
    may be shared in any way (set partitions -> Bell numbers)."""
    arities = list(sig.values())
    # T[s][v] = number of term shapes with s symbols and v variable leaves
    T = [collections.Counter() for _ in range(max_skel + 1)]
    T[0][1] = 1  # a single variable
    for s in range(1, max_skel + 1):
        for n in arities:
            # combine n children whose symbol counts sum to s-1
            combos = collections.Counter({(0, 0): 1})
            for _ in range(n):
                nxt = collections.Counter()
                for (cs, cv), c in combos.items():
                    for s2 in range(0, s - cs):
                        for v2, c2 in T[s2].items():
                            if cs + s2 <= s - 1:
                                nxt[(cs + s2, cv + v2)] += c * c2
                combos = nxt
            for (cs, cv), c in combos.items():
                if cs == s - 1:
                    T[s][cv] += c
    return sum(c * bell(v) for s in range(1, max_skel + 1) for v, c in T[s].items())


# ------------------------------------------------------------------ analyses

def main(labels_path: str, tptp_dir: str) -> None:
    rows = load(labels_path)
    out = print

    out("# First-milestone analysis of existing Twitch runs\n")
    out(f"Rows: {len(rows)} runs over {len({r['problem'] for r in rows})} problems.\n")

    # 1. label noise ------------------------------------------------------
    out("## 1. Label noise (wall clock)\n")
    gaps = [r["mean_base_time"] / r["base_time"] for r in
            {r["problem"]: r for r in rows if r["base_time"] and r["mean_base_time"]
             and r["base_time"] >= MIN_BASE}.values()]
    if gaps:
        q = st.quantiles(gaps, n=10)
        out(f"Baseline time is recorded as the minimum over repeated base runs. For "
            f"{len(gaps)} problems with baseline >= {MIN_BASE}s, mean/min baseline time has "
            f"median {st.median(gaps):.2f}, 90th percentile {q[-1]:.2f}, max {max(gaps):.2f}.\n")
    # repeated identical (problem, set, config)
    groups = collections.defaultdict(list)
    for r in rows:
        if r["status"] == "success" and r["base_time"] and r["base_time"] >= MIN_BASE:
            key = (r["problem"], tuple(r["abstractions"]), r["hint_skel_factor"],
                   r["hint_skel_cost"], r["flatten_goal"])
            groups[key].append(r["hint_time"])
    reps = [max(v) / min(v) for v in groups.values() if len(v) > 1 and min(v) > 0]
    if reps:
        out(f"{len(reps)} (problem, set, config) triples were run more than once; "
            f"max/min hinted time across repeats has median {st.median(reps):.2f}, "
            f"max {max(reps):.2f}.\n")

    # 2. how often sets help, and sensitivity to weights -------------------
    out("## 2. How often a local set helps\n")
    usable = [r for r in rows if r["ratio"] is not None and r["base_time"] >= MIN_BASE]
    out(f"Usable runs (baseline >= {MIN_BASE}s, outcome known): {len(usable)} "
        f"on {len({r['problem'] for r in usable})} problems.\n")
    out("| hint-skel-factor | hint-skel-cost | flatten | runs | >=1.5x faster | >=1.5x slower (incl. timeout) |")
    out("|---|---|---|---|---|---|")
    byconf = collections.defaultdict(list)
    for r in usable:
        byconf[(r["hint_skel_factor"], r["hint_skel_cost"], r["flatten_goal"])].append(r)
    for conf, rs in sorted(byconf.items(), key=lambda kv: str(kv[0])):
        g = sum(r["ratio"] <= GOOD for r in rs)
        b = sum(r["ratio"] >= BAD for r in rs)
        out(f"| {conf[0]} | {conf[1]} | {conf[2]} | {len(rs)} | {pct(g, len(rs))} | {pct(b, len(rs))} |")
    out("")
    # same set, different weight config, no flattening (isolate weight effect)
    same = collections.defaultdict(dict)
    for r in usable:
        if not r["flatten_goal"]:
            same[(r["problem"], tuple(r["abstractions"]))][(r["hint_skel_factor"], r["hint_skel_cost"])] = r["ratio"]
    spreads = [max(d.values()) / min(d.values()) for d in same.values() if len(d) >= 3 and min(d.values()) > 0]
    flips = sum(1 for d in same.values() if len(d) >= 3
                and min(d.values()) <= GOOD and max(d.values()) >= BAD)
    multi = sum(1 for d in same.values() if len(d) >= 3)
    if spreads:
        out(f"For {multi} abstraction sets run under 3+ weight settings (no flattening), the "
            f"best/worst ratio differs by a median factor of {st.median(spreads):.2f}; "
            f"in {flips} of them ({pct(flips, multi)}) the same set is a >=1.5x speedup under one "
            f"setting and a >=1.5x slowdown under another.\n")
    best_per_problem = {}
    for r in usable:
        p = r["problem"]
        if p not in best_per_problem or r["ratio"] < best_per_problem[p]["ratio"]:
            best_per_problem[p] = r
    nb = len(best_per_problem)
    g = sum(r["ratio"] <= GOOD for r in best_per_problem.values())
    out(f"Taking the best configuration per problem: {g} of {nb} problems ({pct(g, nb)}) get a >=1.5x speedup.\n")

    # 3. what helpful abstractions look like -----------------------------
    out("## 3. What abstractions in helpful sets look like\n")
    good_sets = [r for r in usable if r["ratio"] <= GOOD]
    bad_sets = [r for r in usable if r["ratio"] >= BAD]

    def profile(rs):
        ab = [parse(a) for r in rs for a in r["abstractions"]]
        if not ab:
            return None
        sk = [skeleton_weight(t) for t in ab]
        return {
            "n": len(ab),
            "skel_median": st.median(sk),
            "skel_le3": pct(sum(s <= 3 for s in sk), len(ab)),
            "nonlinear": pct(sum(not is_linear(t) for t in ab), len(ab)),
            "ground": pct(sum(is_ground(t) for t in ab), len(ab)),
            "has_const": pct(sum(any(n == 0 for _, n in symbols(t)) for t in ab), len(ab)),
            "set_size": st.median([len(r["abstractions"]) for r in rs]),
        }

    pg, pb = profile(good_sets), profile(bad_sets)
    out("| | in >=1.5x-faster sets | in >=1.5x-slower sets |")
    out("|---|---|---|")
    for k, label in [("n", "abstraction occurrences"), ("set_size", "median set size"),
                     ("skel_median", "median skeleton weight"), ("skel_le3", "skeleton weight <= 3"),
                     ("nonlinear", "nonlinear (repeated variable)"), ("ground", "ground"),
                     ("has_const", "mentions a constant")]:
        out(f"| {label} | {pg[k]} | {pb[k]} |")
    out("")

    # 4. recurrence ------------------------------------------------------
    out("## 4. Recurrence across problems and domains\n")
    probs_of = collections.defaultdict(set)
    doms_of = collections.defaultdict(set)
    for r in good_sets:
        for a in r["abstractions"]:
            probs_of[a].add(r["problem"])
            doms_of[a].add(r["domain"])
    na = len(probs_of)
    multi_p = sum(len(v) >= 2 for v in probs_of.values())
    multi_d = sum(len(v) >= 2 for v in doms_of.values())
    out(f"{na} distinct canonical abstractions occur in helpful sets. {multi_p} ({pct(multi_p, na)}) occur "
        f"in helpful sets for 2+ problems, {multi_d} ({pct(multi_d, na)}) in 2+ domains.\n")
    out("Most widespread (problems / domains):\n")
    out("| abstraction | problems | domains |")
    out("|---|---|---|")
    for a, ps in sorted(probs_of.items(), key=lambda kv: -len(kv[1]))[:15]:
        out(f"| `{a}` | {len(ps)} | {','.join(sorted(doms_of[a]))} |")
    out("")

    # 5. enumeration baseline feasibility --------------------------------
    out("## 5. Is enumeration of small patterns viable?\n")
    paths = {os.path.basename(p)[:-2]: p for p in glob.glob(os.path.join(tptp_dir, "*_UEQ_UNSAT", "*.p"))}
    sig_of = {}
    for r in good_sets:
        p = r["problem"]
        if p in sig_of or p not in paths:
            continue
        sig = problem_signature(paths[p])
        # add symbols seen in this problem's abstractions (covers included axioms)
        for rr in rows:
            if rr["problem"] == p:
                for a in rr["abstractions"]:
                    for f, n in symbols(parse(a)):
                        sig[f] = max(sig.get(f, 0), n)
        sig_of[p] = sig
    sk_all = [skeleton_weight(parse(a)) for r in good_sets for a in r["abstractions"]]
    out("Coverage of helpful abstractions by skeleton weight, and the per-problem number of "
        "candidate patterns an enumerator would have to consider (median over problems with a "
        "helpful set; signature = symbols in the problem file plus those seen in its abstractions, "
        "so this is a lower bound):\n")
    out("| max skeleton weight | helpful abstractions covered | median candidates / problem | max candidates / problem |")
    out("|---|---|---|---|")
    for s in range(1, 7):
        cov = pct(sum(x <= s for x in sk_all), len(sk_all))
        sizes = [enumeration_space(sig, s) for sig in sig_of.values()]
        out(f"| {s} | {cov} | {int(st.median(sizes)):,} | {max(sizes):,} |")
    out("")
    nsym = [len(s) for s in sig_of.values()]
    out(f"Signature size over those problems: median {st.median(nsym)}, max {max(nsym)} symbols.\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
