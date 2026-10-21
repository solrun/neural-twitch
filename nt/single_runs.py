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

    # abstraction sets from nt.expand instead of the Twitch runs:
    python -m nt.single_runs --sets out/expand/sets.jsonl out/single_expand.jsonl ...

    # each member of generated sets alone, without the baseline and set runs
    # (those are already in the set evaluation; rows get "rank" = position
    # in the set, so the top-K singles of a k=5 file cover every K <= 5):
    python -m nt.single_runs --sets out/rerank_k5_flat.jsonl out/eval_singles/rerank_k5_flat.jsonl \
        --singles-only --flatten on ...

Output rows (one per run):
    {"problem", "setting", "kind": "base"|"set"|"single",
     "abstractions": [...], "status", "cps", ..., "ratio"}
(single rows from --singles-only also have "rank", the 0-based position of
the abstraction in its set)
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


# Weight settings: (--hint-skel-factor, --hint-skel-cost).
WEIGHTS = {"cost1": (0.0, 1.0), "f0.2": (0.2, 0.0), "f0.5": (0.5, 0.0)}


def settings(flatten_modes=(True, False), weights=tuple(WEIGHTS)) -> list[Setting]:
    return [Setting(factor=WEIGHTS[w][0], cost=WEIGHTS[w][1], flatten_goal=flatten)
            for flatten in flatten_modes for w in weights]

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
             flatten_modes=(True, False), weights=tuple(WEIGHTS), singles: bool = True,
             singles_only: bool = False):
    for s in settings(flatten_modes, weights):
        if singles_only:
            for i, a in enumerate(abstractions):
                yield problem, path, s, "single", [a], i
            continue
        yield problem, path, s, "base", []
        yield problem, path, s, "set", abstractions
        if singles and len(abstractions) > 1:
            for a in abstractions:
                yield problem, path, s, "single", [a]


def proved_baselines(paths: list[str], max_cps: int, schedule: str) -> set:
    """(problem, flatten) pairs whose calibration baseline proved within
    max_cps under the given schedule. Without a proved baseline no ratio can
    be computed, and the runs mostly sit until the budget, so they are
    skipped."""
    ok, seen = set(), set()
    for path in paths:
        for line in open(path):
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("schedule", schedule) != schedule:
                continue
            k = (r["problem"], r.get("flatten", True))
            seen.add(k)
            if r["status"] == "proved" and r["cps"] <= max_cps:
                ok.add(k)
    if not seen:
        raise SystemExit(f"no calibration rows for schedule {schedule} in {paths}")
    return ok


def _run(job, max_cps, wall_timeout, schedule):
    problem, path, setting, kind, abstractions = job[:5]
    res = twee.run(path, abstractions, setting, max_cps, wall_timeout,
                   schedule=schedule)
    row = {"problem": problem, "setting": setting.key(), "kind": kind,
           "abstractions": abstractions, "schedule": schedule, **res.to_dict()}
    if len(job) > 5:
        row["rank"] = job[5]
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("labels", nargs="?", help="data/labels.jsonl (not with --sets)")
    ap.add_argument("tptp_dir", nargs="?", help="Twitch's data/TPTP (not with --sets)")
    ap.add_argument("out")
    ap.add_argument("--sets", metavar="FILE",
                    help="abstraction sets from nt.expand (rows with problem, path, "
                         "abstractions), instead of the best Twitch set per problem")
    ap.add_argument("--max-cps", type=int, default=2_000_000)
    ap.add_argument("--wall-timeout", type=float, default=1200.0)
    ap.add_argument("--workers", type=int, default=twee.default_workers())
    ap.add_argument("--problems", default="", help="comma-separated domain prefixes")
    ap.add_argument("--limit", type=int, default=0, help="max problems (for a trial run)")
    ap.add_argument("--shard", default="", metavar="K/N",
                    help="run only shard K of N (for Slurm job arrays)")
    ap.add_argument("--calibration", nargs="+", metavar="FILE",
                    help="calibration output for the same --schedule; skip (problem, "
                         "flattening) pairs whose baseline did not prove within --max-cps")
    ap.add_argument("--weights", default=",".join(WEIGHTS),
                    help=f"comma-separated weight settings out of {', '.join(WEIGHTS)} "
                         "(default: all; the first experiment found their labels agree "
                         "closely, so one is enough for new problems)")
    ap.add_argument("--flatten", choices=FLATTEN_MODES, default="both",
                    help="goal flattening: run with it on and off (default), "
                         "or only one of them")
    ap.add_argument("--no-singles", action="store_true",
                    help="run only the baseline and the whole set, not each member alone "
                         "(for evaluating generated sets)")
    ap.add_argument("--singles-only", action="store_true",
                    help="run only each member of the set alone, with its rank in the set "
                         "(no baseline or set runs; for portfolios of singles in nt.eval_report)")
    ap.add_argument("--schedule", default=twee.DEFAULT_SCHEDULE,
                    help="housekeeping schedule: cps:N (--deterministic), alloc:N "
                         "(--deterministic-alloc) or none (CPU time, not reproducible); "
                         f"default {twee.DEFAULT_SCHEDULE}")
    args = ap.parse_args()
    if args.no_singles and args.singles_only:
        ap.error("--no-singles and --singles-only exclude each other")

    if args.sets:
        if args.labels or args.tptp_dir:
            ap.error("give either --sets or LABELS TPTP_DIR, not both")
        rows = [json.loads(l) for l in open(args.sets) if l.strip()]
        paths = {r["problem"]: r["path"] for r in rows}
        sets = {r["problem"]: r["abstractions"] for r in rows}
    else:
        if not (args.labels and args.tptp_dir):
            ap.error("need LABELS and TPTP_DIR, or --sets")
        paths = {os.path.basename(p)[:-2]: p
                 for p in glob.glob(os.path.join(args.tptp_dir, "*_UEQ_UNSAT", "*.p"))}
        sets = best_sets(args.labels)
    domains = [d for d in args.problems.split(",") if d]
    problems = sorted(p for p in sets if p in paths
                      and (not domains or p[:3] in domains))
    if args.limit:
        problems = problems[:args.limit]
    problems = twee.select_shard(problems, args.shard)
    weights = tuple(w for w in args.weights.split(",") if w)
    bad = [w for w in weights if w not in WEIGHTS]
    if bad or not weights:
        ap.error(f"unknown weight settings {bad}; choose from {', '.join(WEIGHTS)}")
    jobs = [j for p in problems
            for j in jobs_for(p, paths[p], sets[p], FLATTEN_MODES[args.flatten], weights,
                             singles=not args.no_singles, singles_only=args.singles_only)]
    if args.calibration:
        ok = proved_baselines(args.calibration, args.max_cps, args.schedule)
        n = len(jobs)
        jobs = [j for j in jobs if (j[0], j[2].flatten_goal) in ok]
        print(f"skipping {n - len(jobs)} runs without a proved calibration baseline")
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
