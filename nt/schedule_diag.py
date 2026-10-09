"""How much does the housekeeping schedule change Twee's search?

Runs baselines (no hints) on a few problems under Twee's normal CPU-time
schedule and under `--deterministic N` for several N, and prints them next to
Twitch's baseline time. The default problems are the six that Twitch proved
in under 100 s without goal flattening but that time out in our calibration.

Reading the result:
  * normal schedule proves them about as fast as Twitch, deterministic ones
    do not: the deterministic schedule causes the outliers;
  * the normal schedule also times out: our Twee build differs from the one
    Twitch used;
  * results swing a lot between values of N: the search is sensitive to
    housekeeping timing in general, and N should be chosen with care.

The normal schedule is not reproducible, so use --reps 2 or more to see how
much it varies by itself.

Usage:
    python -m nt.schedule_diag data/labels.jsonl <twitch_repo>/data/TPTP out/schedule_diag.jsonl \
        [--problems GRP770-1,LAT074-1] [--flatten off] [--schedules none,2000,5000,7000] \
        [--reps 2] [--wall-timeout 1000] [--workers N]
"""

from __future__ import annotations

import argparse
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
    det = None if schedule == "none" else int(schedule)
    r = twee.run(path, [], Setting(flatten_goal=flatten), UNLIMITED, wall_timeout,
                 deterministic=det)
    return {"problem": problem, "flatten": flatten, "schedule": schedule,
            "rep": rep, **r.to_dict()}


def cell(r: dict) -> str:
    if r["status"] == "proved":
        return f"{r['wall']:.0f}s/{r['cps'] / 1e6:.2f}M"
    return r["status"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("labels")
    ap.add_argument("tptp_dir")
    ap.add_argument("out")
    ap.add_argument("--problems", default=DEFAULT_PROBLEMS)
    ap.add_argument("--flatten", choices=["on", "off"], default="off")
    ap.add_argument("--schedules", default="none,2000,5000,7000",
                    help="comma-separated: 'none' (CPU-time schedule) or a --deterministic value")
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--wall-timeout", type=float, default=1000.0)
    ap.add_argument("--workers", type=int, default=twee.default_workers())
    args = ap.parse_args()

    flatten = args.flatten == "on"
    paths = {os.path.basename(p)[:-2]: p
             for p in glob.glob(os.path.join(args.tptp_dir, "*_UEQ_UNSAT", "*.p"))}
    problems = [p for p in args.problems.split(",") if p]
    missing = [p for p in problems if p not in paths]
    if missing:
        raise SystemExit(f"problem files not found: {missing}")
    schedules = [s for s in args.schedules.split(",") if s]
    jobs = [(p, paths[p], s, rep) for p in problems for s in schedules
            for rep in range(args.reps)]
    print(f"{len(jobs)} runs, flattening {args.flatten}, wall cap {args.wall_timeout}s, "
          f"{args.workers} workers")

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

    errors = [r for r in rows if r["status"] == "error"]
    if errors:
        print(f"\n{len(errors)} runs failed. First error:\n{errors[0]['error'][-1500:]}")

    tw = twitch_baselines(args.labels)
    head = ["problem", "Twitch"] + [f"{s} #{i + 1}" if args.reps > 1 else s
                                     for s in schedules for i in range(args.reps)]
    width = 16
    print("\nwall time / critical pairs; 'none' = Twee's normal CPU-time schedule")
    print("".join(h.ljust(width) for h in head))
    by = {(r["problem"], r["schedule"], r["rep"]): r for r in rows}
    for p in problems:
        t = tw.get((p, flatten), "?")
        line = [p, "timeout" if t is None else t if t == "?" else f"{t:.0f}s"]
        line += [cell(by[p, s, i]) for s in schedules for i in range(args.reps)]
        print("".join(str(c).ljust(width) for c in line))


if __name__ == "__main__":
    main()
