"""Choose the critical-pair budget for nt.single_runs.

Runs Twee without hints on every problem the single-abstraction experiment
will use, with an effectively unlimited CP budget and a wall-clock cap, and
reports how many critical pairs each baseline proof needs. Pick --max-cps for
nt.single_runs so that nearly all baselines fit, with headroom for
abstractions that slow the search down.

Each problem is run twice under each goal-flattening setting (on and off by
default), which doubles as the determinism check: both runs must report the
same CP count.

Usage:
    python -m nt.calibrate data/labels.jsonl <twitch_repo>/data/TPTP out/calibration.jsonl \
        [--wall-timeout 1000] [--workers 8] [--limit N] [--flatten both|on|off]
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import statistics as st
from concurrent.futures import ProcessPoolExecutor, as_completed

from nt import twee
from nt.single_runs import FLATTEN_MODES, best_sets
from nt.twee import Setting

UNLIMITED = 10**12


def _run(problem, path, rep, wall_timeout, flatten):
    r = twee.run(path, [], Setting(flatten_goal=flatten), UNLIMITED, wall_timeout)
    return {"problem": problem, "flatten": flatten, "rep": rep, **r.to_dict()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("labels")
    ap.add_argument("tptp_dir")
    ap.add_argument("out")
    ap.add_argument("--wall-timeout", type=float, default=1000.0)
    ap.add_argument("--workers", type=int, default=twee.default_workers())
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--shard", default="", metavar="K/N",
                    help="run only shard K of N (for Slurm job arrays)")
    ap.add_argument("--flatten", choices=FLATTEN_MODES, default="both",
                    help="goal flattening: calibrate with it on and off (default), "
                         "or only one of them")
    args = ap.parse_args()

    paths = {os.path.basename(p)[:-2]: p
             for p in glob.glob(os.path.join(args.tptp_dir, "*_UEQ_UNSAT", "*.p"))}
    problems = sorted(p for p in best_sets(args.labels) if p in paths)
    if args.limit:
        problems = problems[:args.limit]
    problems = twee.select_shard(problems, args.shard)
    modes = FLATTEN_MODES[args.flatten]
    print(f"{len(problems)} problems x {len(modes)} flattening settings x 2 runs, "
          f"wall cap {args.wall_timeout}s")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    rows = []
    with open(args.out, "w") as out, ProcessPoolExecutor(args.workers) as ex:
        futs = [ex.submit(_run, p, paths[p], rep, args.wall_timeout, flatten)
                for p in problems for flatten in modes for rep in (0, 1)]
        for i, f in enumerate(as_completed(futs), 1):
            r = f.result()
            rows.append(r)
            out.write(json.dumps(r) + "\n")
            out.flush()
            if i % 50 == 0:
                print(f"{i}/{len(futs)} runs done")
    report(rows)


def report(rows: list[dict]) -> None:
    # Older calibration files have no "flatten" field; they ran with it on.
    modes = sorted({r.get("flatten", True) for r in rows}, reverse=True)
    for flatten in modes:
        sub = [r for r in rows if r.get("flatten", True) == flatten]
        print(f"\n=== goal flattening {'on' if flatten else 'off'} ===")
        report_one(sub)
    if len(modes) > 1:
        print("\nUse one --max-cps for both settings: the larger of the two "
              "suggestions above.")


def report_one(rows: list[dict]) -> None:
    by = {}
    for r in rows:
        by.setdefault(r["problem"], []).append(r)
    errors = [r for r in rows if r["status"] == "error"]
    if errors:
        print(f"\n{len(errors)} runs failed to produce a stats line. First error:")
        print(errors[0]["error"][-1500:])

    # determinism
    pairs = [(rs[0]["cps"], rs[1]["cps"]) for rs in by.values()
             if len(rs) == 2 and all(r["status"] == "proved" for r in rs)]
    mismatched = [p for p in pairs if p[0] != p[1]]
    print(f"\nDeterminism: {len(pairs)} problems proved twice, "
          f"{len(mismatched)} with differing CP counts.")
    if mismatched:
        print("  NOT deterministic, e.g.", mismatched[:5],
              "- do not use CP counts as labels until this is understood.")

    # budget
    cps = sorted(rs[0]["cps"] for rs in by.values() if rs[0]["status"] == "proved")
    unproved = sum(1 for rs in by.values() if rs[0]["status"] != "proved")
    print(f"\nBaselines proved within the wall cap: {len(cps)} of {len(by)} "
          f"({unproved} timed out or failed).")
    if not cps:
        return
    q = st.quantiles(cps, n=20, method="inclusive") if len(cps) >= 2 else cps * 19
    print(f"CPs needed: median {st.median(cps):,.0f}, 90th pct {q[17]:,.0f}, "
          f"95th pct {q[18]:,.0f}, max {cps[-1]:,}.")
    walls = [r["wall"] / r["cps"] for r in rows if r["status"] == "proved" and r["cps"]]
    if walls:
        print(f"Wall time per million CPs: median {1e6 * st.median(walls):.1f}s.")
    for mult in (2, 5, 10):
        budget = mult * q[18]
        print(f"  --max-cps {budget:,.0f}  ({mult}x the 95th percentile): "
              f"{sum(c <= budget for c in cps)} of {len(by)} baselines fit")


if __name__ == "__main__":
    main()
