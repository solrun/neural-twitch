"""Compare our calibration baselines with Twitch's baselines on the same
problems, per goal-flattening setting.

For each (problem, flattening setting) it puts our first calibration run
(proved / timeout / error, wall time) next to Twitch's baseline (minimum user
time over its repeated base runs, or a baseline timeout). The interesting
cases are problems Twitch proved that time out here: if there are many, the
deterministic housekeeping schedule is slowing the search down.

Note that Twitch's times are user CPU time and ours are wall time, so the
ratios slightly overstate our slowdown.

Usage:
    python -m nt.compare_calibration data/labels.jsonl out/calibration_*.jsonl \
        [--csv out/calibration_vs_twitch.csv]
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import statistics as st


def twitch_baselines(labels_path: str) -> dict:
    """(problem, flatten) -> Twitch baseline seconds, or None if it timed out."""
    times: dict = {}
    timed_out: set = set()
    for line in open(labels_path):
        r = json.loads(line)
        k = (r["problem"], r["flatten_goal"])
        if r["base_time"]:
            times[k] = min(times.get(k, r["base_time"]), r["base_time"])
        elif r["status"] == "base_timeout":
            timed_out.add(k)
    out = {k: None for k in timed_out}
    out.update(times)
    return out


def ours(paths: list[str]) -> dict:
    """(problem, flatten) -> first calibration run (rep 0 if present)."""
    runs: dict = {}
    for p in paths:
        for line in open(p):
            if not line.strip():
                continue
            r = json.loads(line)
            k = (r["problem"], r.get("flatten", True))
            if k not in runs or r.get("rep", 0) < runs[k].get("rep", 0):
                runs[k] = r
    return runs


def fmt(t):
    return "-" if t is None else f"{t:.1f}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("labels")
    ap.add_argument("calibration", nargs="+")
    ap.add_argument("--csv", help="also write one row per (problem, setting)")
    args = ap.parse_args()

    tw = twitch_baselines(args.labels)
    us = ours(args.calibration)
    rows = []
    for k, r in sorted(us.items()):
        if k not in tw:
            continue
        rows.append({"problem": k[0], "flatten": k[1], "ours": r["status"],
                     "ours_wall": r.get("wall"), "ours_cps": r.get("cps"),
                     "twitch": "timeout" if tw[k] is None else "proved",
                     "twitch_time": tw[k]})

    for flatten in sorted({r["flatten"] for r in rows}, reverse=True):
        sub = [r for r in rows if r["flatten"] == flatten]
        print(f"\n=== goal flattening {'on' if flatten else 'off'}: {len(sub)} problems ===")
        table = collections.Counter((r["ours"], r["twitch"]) for r in sub)
        print(f"{'ours / Twitch':<22}{'proved':>8}{'timeout':>9}")
        for status in ("proved", "timeout", "budget", "error"):
            if any(s == status for s, _ in table):
                print(f"{status:<22}{table[status, 'proved']:>8}{table[status, 'timeout']:>9}")

        both = [r for r in sub if r["ours"] == "proved" and r["twitch"] == "proved"
                and r["twitch_time"] >= 1.0]
        if both:
            ratios = sorted(r["ours_wall"] / r["twitch_time"] for r in both)
            q = st.quantiles(ratios, n=10) if len(ratios) >= 2 else ratios * 9
            print(f"Our wall / Twitch time, {len(both)} problems proved by both "
                  f"(Twitch >= 1 s): median {st.median(ratios):.2f}, "
                  f"10th pct {q[0]:.2f}, 90th pct {q[8]:.2f}, max {ratios[-1]:.2f}")
            slow = sorted(both, key=lambda r: r["twitch_time"], reverse=True)[:5]
            print("  slowest for Twitch:", ", ".join(
                f"{r['problem']} {fmt(r['twitch_time'])}s -> {fmt(r['ours_wall'])}s"
                for r in slow))

        lost = sorted((r for r in sub if r["ours"] != "proved" and r["twitch"] == "proved"),
                      key=lambda r: r["twitch_time"])
        if lost:
            print(f"Proved by Twitch but not here ({len(lost)}), by Twitch time:")
            for r in lost:
                print(f"  {r['problem']:<14} Twitch {fmt(r['twitch_time']):>7}s   "
                      f"ours: {r['ours']} after {fmt(r['ours_wall'])}s")
            buckets = collections.Counter(
                "<100s" if r["twitch_time"] < 100 else
                "100-500s" if r["twitch_time"] < 500 else ">=500s" for r in lost)
            print("  Twitch time of these:", dict(buckets))

    if args.csv:
        with open(args.csv, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        print(f"\nwrote {len(rows)} rows to {args.csv}")


if __name__ == "__main__":
    main()
