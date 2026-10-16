"""Report on the Twee evaluation of generated sets (slurm/eval_sets.sbatch).

  python -m nt.eval_report out/eval/*.jsonl --data data/dataset [--out eval_report.md]

Inputs are nt.single_runs outputs named <method>_k<K>_<flat|noflat>[_<shard>].jsonl
(shards of one file are merged). Each problem has a "base" run (no hints)
and a "set" run (the generated set) under the same setting. Splits come
from the dataset's graphs (test, hard, ...).

Sections:
  1. per method, k, flattening and split: problems, proved without / with
     the set, new proofs (set proves, base does not), lost proofs, and for
     problems both prove the CP ratio (median, geometric mean, share >= 1.5x
     faster / slower)
  2. head-to-head between methods at the same k, flattening and split:
     problems only one proves, and the CP ratio between the two sets
  3. portfolio over both flattening settings: problems proved by the set in
     either setting vs by plain Twee in either setting
  4. complementarity: problems proved by each method in any configuration
     (any k, either setting), the union, and which problems only one method
     or only one configuration proves (names listed for --list-splits)
"""

from __future__ import annotations

import argparse
import collections
import glob
import gzip
import json
import math
import os
import re
import statistics

NAME = re.compile(r"^(?P<method>.+)_k(?P<k>\d+)_(?P<flat>flat|noflat)(?:_\d+)?$")
FAST = 1 / 1.5


def parse_name(path: str):
    m = NAME.match(os.path.basename(path)[:-len(".jsonl")])
    if not m:
        return None
    return m["method"], int(m["k"]), m["flat"] == "flat"


def load_runs(paths: list[str]) -> dict:
    """{(method, k, flat): {problem: {"base": row, "set": row}}}"""
    out: dict = collections.defaultdict(lambda: collections.defaultdict(dict))
    for p in paths:
        key = parse_name(p)
        if key is None:
            print(f"skipping {p}: name is not <method>_k<K>_<flat|noflat>[_<shard>].jsonl")
            continue
        for line in open(p):
            if not line.strip():
                continue
            r = json.loads(line)
            if r["kind"] in ("base", "set"):
                out[key][r["problem"]][r["kind"]] = r
    return out


def load_splits(data_dir: str) -> dict:
    splits = {}
    with gzip.open(os.path.join(data_dir, "graphs.jsonl.gz"), "rt") as f:
        for line in f:
            r = json.loads(line)
            splits[r["problem"]] = r["split"]
    return splits


def proved(r) -> bool:
    return bool(r) and r["status"] == "proved"


def gmean(xs):
    return math.exp(sum(math.log(x) for x in xs) / len(xs)) if xs else float("nan")


def fmt(x, nd=2):
    return "–" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{nd}f}"


def per_config(runs: dict, splits: dict) -> list[str]:
    lines = ["## 1. Generated sets against plain Twee", "",
             "| method | k | flatten | split | problems | base proved | set proved | new | lost "
             "| both | median ratio | geo-mean ratio | ≥1.5x faster | ≥1.5x slower |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for (method, k, flat) in sorted(runs, key=lambda x: (x[1], not x[2], x[0])):
        by_split = collections.defaultdict(list)
        for p, rr in runs[method, k, flat].items():
            if "base" in rr and "set" in rr:
                by_split[splits.get(p, "?")].append(rr)
        for split in sorted(by_split):
            rows = by_split[split]
            bp = sum(proved(r["base"]) for r in rows)
            sp = sum(proved(r["set"]) for r in rows)
            new = sum(proved(r["set"]) and not proved(r["base"]) for r in rows)
            lost = sum(proved(r["base"]) and not proved(r["set"]) for r in rows)
            ratios = [r["set"]["cps"] / r["base"]["cps"] for r in rows
                      if proved(r["base"]) and proved(r["set"]) and r["base"]["cps"]]
            med = statistics.median(ratios) if ratios else None
            faster = sum(x <= FAST for x in ratios)
            slower = sum(x >= 1 / FAST for x in ratios)
            lines.append(f"| {method} | {k} | {'on' if flat else 'off'} | {split} | {len(rows)} "
                         f"| {bp} | {sp} | {new} | {lost} | {len(ratios)} | {fmt(med)} "
                         f"| {fmt(gmean(ratios))} | {faster} | {slower} |")
    lines += ["", "ratio = CPs with the set / CPs without, on problems both prove; "
              "below 1 is faster. Ratios within 0.67–1.5 are within schedule noise.", ""]
    return lines


def head_to_head(runs: dict, splits: dict) -> list[str]:
    methods = sorted({m for m, _, _ in runs})
    if len(methods) < 2:
        return []
    lines = ["## 2. Head to head", "",
             "| A | B | k | flatten | split | problems | only A proves | only B proves "
             "| both | median A/B | A ≥1.5x faster | B ≥1.5x faster |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    configs = sorted({(k, f) for _, k, f in runs}, key=lambda x: (x[0], not x[1]))
    for i, a in enumerate(methods):
        for b in methods[i + 1:]:
            for k, flat in configs:
                ra, rb = runs.get((a, k, flat)), runs.get((b, k, flat))
                if not ra or not rb:
                    continue
                by_split = collections.defaultdict(list)
                for p in set(ra) & set(rb):
                    if "set" in ra[p] and "set" in rb[p]:
                        by_split[splits.get(p, "?")].append((ra[p]["set"], rb[p]["set"]))
                for split in sorted(by_split):
                    pairs = by_split[split]
                    oa = sum(proved(x) and not proved(y) for x, y in pairs)
                    ob = sum(proved(y) and not proved(x) for x, y in pairs)
                    rat = [x["cps"] / y["cps"] for x, y in pairs
                           if proved(x) and proved(y) and y["cps"]]
                    lines.append(
                        f"| {a} | {b} | {k} | {'on' if flat else 'off'} | {split} | {len(pairs)} "
                        f"| {oa} | {ob} | {len(rat)} | {fmt(statistics.median(rat) if rat else None)} "
                        f"| {sum(x <= FAST for x in rat)} | {sum(x >= 1 / FAST for x in rat)} |")
    return lines + [""]


def portfolio(runs: dict, splits: dict) -> list[str]:
    lines = ["## 3. Portfolio over both flattening settings", "",
             "Proved in either setting (base = plain Twee with flattening on or off).", "",
             "| method | k | split | problems | base proved | set proved | new | lost |",
             "|---|---|---|---|---|---|---|---|"]
    for method, k in sorted({(m, k) for m, k, _ in runs}, key=lambda x: (x[1], x[0])):
        on, off = runs.get((method, k, True), {}), runs.get((method, k, False), {})
        by_split = collections.defaultdict(list)
        for p in set(on) | set(off):
            rs = [x for x in (on.get(p), off.get(p)) if x]
            b = any(proved(r.get("base")) for r in rs)
            s = any(proved(r.get("set")) for r in rs)
            by_split[splits.get(p, "?")].append((b, s))
        for split in sorted(by_split):
            xs = by_split[split]
            lines.append(f"| {method} | {k} | {split} | {len(xs)} | {sum(b for b, _ in xs)} "
                         f"| {sum(s for _, s in xs)} | {sum(s and not b for b, s in xs)} "
                         f"| {sum(b and not s for b, s in xs)} |")
    return lines + [""]


def solved_sets(runs: dict, splits: dict):
    """{split: {config or "plain": set(problems proved)}}; config = (method, k, flat)."""
    out: dict = collections.defaultdict(lambda: collections.defaultdict(set))
    for cfg, probs in runs.items():
        for p, rr in probs.items():
            sp = splits.get(p, "?")
            out[sp].setdefault(cfg, set())
            if proved(rr.get("set")):
                out[sp][cfg].add(p)
            if proved(rr.get("base")):
                out[sp]["plain"].add(p)
    return out


def complementarity(runs: dict, splits: dict, list_splits=("hard",)) -> list[str]:
    lines = ["## 4. Complementarity", "",
             "Proved in any configuration of a method (any k, either flattening setting).", ""]
    methods = sorted({m for m, _, _ in runs})
    for split, by_cfg in sorted(solved_sets(runs, splits).items()):
        plain = by_cfg.get("plain", set())
        per_m = {m: set().union(*[v for c, v in by_cfg.items() if c != "plain" and c[0] == m])
                 for m in methods}
        union = set().union(*per_m.values()) if per_m else set()
        lines += [f"### {split}", "",
                  "| | proved | new (not plain Twee) | only this method |", "|---|---|---|---|"]
        lines.append(f"| plain Twee (either setting) | {len(plain)} | – | – |")
        for m in methods:
            others = set().union(*[v for mm, v in per_m.items() if mm != m])
            lines.append(f"| {m} | {len(per_m[m])} | {len(per_m[m] - plain)} "
                         f"| {len(per_m[m] - others)} |")
        lines.append(f"| union of all sets | {len(union)} | {len(union - plain)} | – |")
        lines.append(f"| union of all sets and plain Twee | {len(union | plain)} | – | – |")
        lines.append("")
        # how many configurations prove each newly proved problem
        cfgs = [c for c in by_cfg if c != "plain"]
        count = collections.Counter(p for c in cfgs for p in by_cfg[c] - plain)
        if count:
            hist = collections.Counter(count.values())
            lines.append("Newly proved problems by number of configurations (of "
                         f"{len(cfgs)}) that prove them: "
                         + ", ".join(f"{n}: {hist[n]}" for n in sorted(hist)) + ".")
            lines.append("")
        if split in list_splits:
            for m in methods:
                others = set().union(*[v for mm, v in per_m.items() if mm != m])
                only = sorted(per_m[m] - others - plain)
                if only:
                    lines.append(f"- only {m}: " + ", ".join(
                        f"{p} ({_cfg_list(by_cfg, p, m)})" for p in only))
            lost = sorted(plain - union)
            if lost:
                lines.append("- plain Twee only: " + ", ".join(lost))
            lines.append("")
    return lines


def _cfg_list(by_cfg, p, method) -> str:
    return " ".join(f"k{k}{'f' if flat else 'n'}" for (m, k, flat) in
                    sorted(c for c in by_cfg if c != "plain" and c[0] == method)
                    if p in by_cfg[m, k, flat])


def report(runs: dict, splits: dict, list_splits=("hard",)) -> str:
    return "\n".join(["# Twee evaluation of generated sets", ""]
                     + per_config(runs, splits) + head_to_head(runs, splits)
                     + portfolio(runs, splits) + complementarity(runs, splits, list_splits))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("files", nargs="+", help="out/eval/*.jsonl (merged or shard files)")
    ap.add_argument("--data", required=True, help="output directory of nt.dataset (for splits)")
    ap.add_argument("--out", help="also write the report to this file")
    ap.add_argument("--list-splits", default="hard",
                    help="splits whose problems section 4 lists by name")
    args = ap.parse_args()
    files = [f for pat in args.files for f in (glob.glob(pat) or [pat])]
    # if a merged file and its shards are both given, use only the shards
    merged = {f for f in files if re.search(r"_\d+\.jsonl$", f) is None}
    shards = {re.sub(r"_\d+\.jsonl$", ".jsonl", f) for f in files if f not in merged}
    files = [f for f in files if f not in (merged & shards)]
    text = report(load_runs(files), load_splits(args.data),
                  tuple(x for x in args.list_splits.split(",") if x))
    print(text)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text + "\n")


if __name__ == "__main__":
    main()
