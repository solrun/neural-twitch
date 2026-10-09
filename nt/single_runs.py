"""Single-abstraction experiment: does an abstraction help on its own?

For every problem with a measurable baseline, take its best-performing local
abstraction set from the existing Twitch runs, then under each weight setting
and each goal-flattening setting (on and off by default) run Twee
  * with no hints (baseline),
  * with the full set,
  * with each abstraction alone,
all under the same deterministic critical-pair budget. The output answers
whether per-abstraction labels predict set-level speedups, and gives the first
per-abstraction training labels.

Usage:
    python -m nt.single_runs data/labels.jsonl <twitch_repo>/data/TPTP out/single.jsonl \
        [--max-cps 2000000] [--workers 8] [--problems GRP,LAT] [--limit N] \
        [--flatten both|on|off]

Output rows (one per run):
    {"problem", "setting", "kind": "base"|"set"|"single",
     "abstractions": [...], "status", "cps", ..., "ratio"}
ratio = cps / baseline cps under the same setting; runs that hit the budget
get ratio = max_cps / baseline cps (a lower bound on the true ratio).
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
import os
from concurrent.futures import ProcessPoolExecutor, as_completed

from nt import twee
from nt.twee import Setting

FLATTEN_MODES = {"both": (True, False), "on": (True,), "off": (False,)}


def settings(flatten_modes=(True, False)) -> list[Setting]:
    return [s for flatten in flatten_modes
            for s in (Setting(factor=0.0, cost=1.0, flatten_goal=flatten),
                      Setting(factor=0.2, flatten_goal=flatten),
                      Setting(factor=0.5, flatten_goal=flatten))]

MIN_BASE = 1.0  # seconds, as in nt.analyze


def best_sets(labels_path: str) -> dict[str, list[str]]:
    best: dict[str, dict] = {}
    for line in open(labels_path):
        r = json.loads(line)
        if r["ratio"] is None or not r["base_time"] or r["base_time"] < MIN_BASE:
            continue
        if not r["abstractions"]:
            continue
        if r["problem"] not in best or r["ratio"] < best[r["problem"]]["ratio"]:
            best[r["problem"]] = r
    return {p: r["abstractions"] for p, r in best.items()}


def jobs_for(problem: str, path: str, abstractions: list[str],
             flatten_modes=(True, False)):
    for s in settings(flatten_modes):
        yield problem, path, s, "base", []
        yield problem, path, s, "set", abstractions
        if len(abstractions) > 1:
            for a in abstractions:
                yield problem, path, s, "single", [a]


def _run(job, max_cps, wall_timeout, schedule):
    problem, path, setting, kind, abstractions = job
    res = twee.run(path, abstractions, setting, max_cps, wall_timeout,
                   schedule=schedule)
    return {"problem": problem, "setting": setting.key(), "kind": kind,
            "abstractions": abstractions, "schedule": schedule, **res.to_dict()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("labels")
    ap.add_argument("tptp_dir")
    ap.add_argument("out")
    ap.add_argument("--max-cps", type=int, default=2_000_000)
    ap.add_argument("--wall-timeout", type=float, default=1200.0)
    ap.add_argument("--workers", type=int, default=twee.default_workers())
    ap.add_argument("--problems", default="", help="comma-separated domain prefixes")
    ap.add_argument("--limit", type=int, default=0, help="max problems (for a trial run)")
    ap.add_argument("--shard", default="", metavar="K/N",
                    help="run only shard K of N (for Slurm job arrays)")
    ap.add_argument("--flatten", choices=FLATTEN_MODES, default="both",
                    help="goal flattening: run with it on and off (default), "
                         "or only one of them")
    ap.add_argument("--schedule", default=twee.DEFAULT_SCHEDULE,
                    help="housekeeping schedule: cps:N (--deterministic), alloc:N "
                         "(--deterministic-alloc) or none (CPU time, not reproducible); "
                         f"default {twee.DEFAULT_SCHEDULE}")
    args = ap.parse_args()

    paths = {os.path.basename(p)[:-2]: p
             for p in glob.glob(os.path.join(args.tptp_dir, "*_UEQ_UNSAT", "*.p"))}
    sets = best_sets(args.labels)
    domains = [d for d in args.problems.split(",") if d]
    problems = sorted(p for p in sets if p in paths
                      and (not domains or p[:3] in domains))
    if args.limit:
        problems = problems[:args.limit]
    problems = twee.select_shard(problems, args.shard)
    jobs = [j for p in problems for j in jobs_for(p, paths[p], sets[p], FLATTEN_MODES[args.flatten])]
    print(f"{len(problems)} problems, {len(jobs)} Twee runs, budget {args.max_cps} CPs, "
          f"schedule {args.schedule}")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    results = []
    with open(args.out, "w") as out, ProcessPoolExecutor(args.workers) as ex:
        futs = [ex.submit(_run, j, args.max_cps, args.wall_timeout, args.schedule)
                for j in jobs]
        for i, f in enumerate(as_completed(futs), 1):
            r = f.result()
            results.append(r)
            out.write(json.dumps(r) + "\n")
            out.flush()
            if i % 100 == 0:
                print(f"{i}/{len(jobs)} runs done")

    add_ratios(args.out, results, args.max_cps)


def add_ratios(out_path: str, results: list[dict], max_cps: int) -> None:
    """Rewrite the output with ratio = cps / baseline cps (same setting)."""
    base = {(r["problem"], r["setting"]): r for r in results if r["kind"] == "base"}
    with open(out_path, "w") as out:
        for r in results:
            b = base.get((r["problem"], r["setting"]))
            ratio = None
            if b and b["status"] == "proved" and b["cps"]:
                if r["status"] == "proved":
                    ratio = r["cps"] / b["cps"]
                elif r["status"] == "budget":
                    ratio = max_cps / b["cps"]
            r["ratio"] = ratio
            out.write(json.dumps(r) + "\n")
    proved = collections.Counter((r["kind"], r["status"]) for r in results)
    print("run outcomes:", dict(proved))


if __name__ == "__main__":
    main()
