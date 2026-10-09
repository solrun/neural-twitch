"""How much does the housekeeping schedule change Twee's search?

Runs baselines (no hints) on a few problems under Twee's normal CPU-time
schedule, under `--deterministic N` (critical pairs as the clock) for several
N, and under `--deterministic-alloc N` (bytes allocated as the clock), and
prints them next to Twitch's baseline time. The default problems are the six that Twitch proved
in under 100 s without goal flattening but that time out in our calibration.

Reading the result:
  * normal schedule proves them about as fast as Twitch, deterministic ones
    do not: the deterministic schedule causes the outliers;
  * the normal schedule also times out: our Twee build differs from the one
    Twitch used;
  * results swing a lot between values of N: the search is sensitive to
    housekeeping timing in general, and N should be chosen with care.

The normal schedule is not reproducible, so it runs --reps times (default 2)
to show how much it varies by itself; deterministic runs are identical on
every repeat and run once.

Lower --deterministic values mean more frequent housekeeping. On problems
where Twee manages far fewer CPs per second than the chosen value, the
deterministic schedule housekeeps much less often than the normal one; the
low values test whether that explains the outliers. The allocation clock
also counts time spent on housekeeping, so Twee's per-task time budgets
apply as they do normally.

Normal-schedule runs report bytes allocated per CPU second (needs the
current twee-deterministic.patch); that is the value to try for
--deterministic-alloc.

Usage:
    python -m nt.schedule_diag data/labels.jsonl <twitch_repo>/data/TPTP out/schedule_diag.jsonl \
        [--problems GRP770-1,LAT074-1] [--flatten off] [--schedules none,500,7000,alloc:2000000000] \
        [--reps 2] [--wall-timeout 1000] [--workers N]

    # print the table from an existing (possibly partial) output file
    python -m nt.schedule_diag data/labels.jsonl <twitch_repo>/data/TPTP out/schedule_diag.jsonl --report
"""

from __future__ import annotations

import argparse
import statistics
import glob
import json
import os
from concurrent.futures import ProcessPoolExecutor, as_completed

from nt import twee
from nt.calibrate import UNLIMITED
from nt.compare_calibration import twitch_baselines
from nt.twee import Setting

DEFAULT_PROBLEMS = "GRP770-1,LAT074-1,LAT075-1,REL045-1,REL040-3,LAT079-1"


def _run(problem, path, schedule, rep, flatten, wall_timeout):
    r = twee.run(path, [], Setting(flatten_goal=flatten), UNLIMITED, wall_timeout,
                 schedule=schedule)
    return {"problem": problem, "flatten": flatten, "schedule": schedule,
            "rep": rep, **r.to_dict()}


def n_reps(schedule: str, reps: int) -> int:
    return reps if schedule == "none" else 1


def columns(schedules, reps):
    return [(s, i) for s in schedules for i in range(n_reps(s, reps))]


def label(schedule: str) -> str:
    """Column header: 'alloc:3000000000' -> 'alloc 3G'."""
    if schedule.startswith("alloc:"):
        n = int(schedule[6:])
        return f"alloc {n / 1e9:g}G" if n >= 1e9 else f"alloc {n / 1e6:g}M"
    return schedule


def cell(r: dict) -> str:
    if r["status"] == "proved":
        cps = r["cps"]
        work = f"{cps / 1e6:.2f}M" if cps >= 100_000 else f"{cps / 1e3:.1f}k"
        return f"{r['wall']:.0f}s/{work}"
    return r["status"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("labels")
    ap.add_argument("tptp_dir")
    ap.add_argument("out")
    ap.add_argument("--problems", default=DEFAULT_PROBLEMS)
    ap.add_argument("--flatten", choices=["on", "off"], default="off")
    ap.add_argument("--schedules",
                    default="none,500,1000,2000,7000,alloc:1000000000,alloc:3000000000",
                    help="comma-separated: 'none' (CPU-time schedule), a --deterministic "
                         "value (N or cps:N) or alloc:N for --deterministic-alloc")
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--wall-timeout", type=float, default=1000.0)
    ap.add_argument("--workers", type=int, default=twee.default_workers())
    ap.add_argument("--report", action="store_true",
                    help="don't run anything; print the table from the output file")
    args = ap.parse_args()

    flatten = args.flatten == "on"
    paths = {os.path.basename(p)[:-2]: p
             for p in glob.glob(os.path.join(args.tptp_dir, "*_UEQ_UNSAT", "*.p"))}
    problems = [p for p in args.problems.split(",") if p]
    missing = [p for p in problems if p not in paths]
    if missing:
        raise SystemExit(f"problem files not found: {missing}")
    schedules = [s for s in args.schedules.split(",") if s]
    if args.report:
        rows = [json.loads(l) for l in open(args.out) if l.strip()]
        report(rows, problems, schedules, args.reps, flatten, args.labels)
        return
    jobs = [(p, paths[p], s, rep) for p in problems for s in schedules
            for rep in range(n_reps(s, args.reps))]
    print(f"{len(jobs)} runs, flattening {args.flatten}, wall cap {args.wall_timeout}s, "
          f"{args.workers} workers", flush=True)
    if args.workers < len(jobs):
        print(f"  fewer workers than runs: expect up to "
              f"{-(-len(jobs) // args.workers)} rounds of {args.wall_timeout:.0f}s", flush=True)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    rows = []
    with open(args.out, "w") as out, ProcessPoolExecutor(args.workers) as ex:
        futs = [ex.submit(_run, p, path, s, rep, flatten, args.wall_timeout)
                for p, path, s, rep in jobs]
        for f in as_completed(futs):
            r = f.result()
            rows.append(r)
            out.write(json.dumps(r) + "\n")
            out.flush()

    report(rows, problems, schedules, args.reps, flatten, args.labels)


def report(rows, problems, schedules, reps, flatten, labels) -> None:
    errors = [r for r in rows if r["status"] == "error"]
    if errors:
        print(f"\n{len(errors)} runs failed. First error:\n{errors[0]['error'][-1500:]}")
    bad = [s for s in schedules if s != "none" and not twee.schedule_flags(s)]
    if bad:
        print(f"unknown schedules: {bad}")

    tw = twitch_baselines(labels)
    cols = columns(schedules, reps)
    head = ["problem", "Twitch"] + [f"{label(s)} #{i + 1}" if n_reps(s, reps) > 1
                                     else label(s) for s, i in cols]
    width = 14
    print("\nwall time / critical pairs; 'none' = Twee's normal CPU-time schedule")
    print("".join(h.ljust(width) for h in head))
    by = {(r["problem"], r["schedule"], r["rep"]): r for r in rows}
    for p in problems:
        t = tw.get((p, flatten), "?")
        line = [p, "timeout" if t is None else t if t == "?" else f"{t:.0f}s"]
        line += [cell(by[p, s, i]) if (p, s, i) in by else "(not run)"
                 for s, i in cols]
        print("".join(str(c).ljust(width) for c in line))

    rates = [(r["problem"], r["allocated_bytes"] / r["cpu_seconds"]) for r in rows
             if r["schedule"] == "none" and r.get("allocated_bytes")
             and r.get("cpu_seconds") and r["cpu_seconds"] >= 1.0]
    if rates:
        vals = sorted(v for _, v in rates)
        print(f"\nBytes allocated per CPU second, normal schedule ({len(vals)} runs "
              f">= 1 s): median {statistics.median(vals) / 1e9:.2f} GB/s, "
              f"min {vals[0] / 1e9:.2f}, max {vals[-1] / 1e9:.2f}")
        print("  " + ", ".join(f"{p} {v / 1e9:.2f}" for p, v in sorted(rates)))
        print(f"  --deterministic-alloc {statistics.median(vals):,.0f} matches the median")


if __name__ == "__main__":
    main()
