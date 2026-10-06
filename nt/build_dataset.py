"""Turn Twitch's local-abstraction runs into a labeled dataset.

Each output row is one (problem, abstraction set, Twee configuration) run:

    {"problem": "LAT075-1", "domain": "LAT", "source": "local_abs_10iter",
     "hint_skel_factor": 0.5, "hint_skel_cost": 0.0, "flatten_goal": false,
     "abstractions": ["f(X0, X0)", ...],       # canonical, deduplicated
     "n_raw": 10, "n_dropped_higher_order": 4,
     "status": "success" | "timeout" | "base_timeout" | "other",
     "base_time": 36.7, "hint_time": 92.6,
     "ratio": 2.52}                             # hint/base, lower is better

Labels are set-level and wall-clock based: these are the limits of the
existing data, which Phase 0 is meant to fix (per-abstraction runs and a
deterministic step count in Twee).

Usage:
    python -m nt.build_dataset <twitch_repo>/data/experiments out/labels.jsonl
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys

import yaml

from nt.terms import canonical

_FLAG = re.compile(r"--(hint-skel-factor|hint-skel-cost)\s+([0-9.eE+-]+)")


def parse_flags(flags: list[str]) -> dict:
    joined = " ".join(flags)
    out = {"hint_skel_factor": None, "hint_skel_cost": None,
           "flatten_goal": "--flatten-goal" in flags}
    for name, val in _FLAG.findall(joined):
        out[name.replace("-", "_")] = float(val)
    return out


def classify_status(r: dict) -> str:
    st = r.get("hints_status") or r.get("status") or ""
    if st == "success":
        return "success"
    if st == "timeout":
        return "timeout"
    if "base timeout" in st:
        return "base_timeout"
    return "other"


def rows_from_run(run_dir: str, source: str):
    cfg = yaml.safe_load(open(os.path.join(run_dir, "config.yaml"))) or {}
    flags = parse_flags(cfg.get("twee", {}).get("flags", []))
    timeout = cfg.get("twee", {}).get("timeout")
    for r in json.load(open(os.path.join(run_dir, "summary.json"))):
        raw = r.get("abstractions", [])
        expanded = r.get("expanded_abstractions", [])
        canon = []
        for a in expanded:
            c = canonical(a)
            if c is not None and c not in canon:
                canon.append(c)
        status = classify_status(r)
        base = r.get("min_base_user_time")
        hint = r.get("hints_time_user")
        if status == "timeout" and timeout:
            hint = float(timeout)  # censored at the time limit
        ratio = (hint / base) if (base and hint and status in ("success", "timeout")) else None
        yield {
            "problem": r["problem"],
            "domain": r["problem"][:3],
            "source": source,
            "run": os.path.basename(run_dir),
            **flags,
            "abstractions": canon,
            "n_raw": len(raw),
            "n_dropped_higher_order": len(raw) - len(expanded),
            "status": status,
            "base_time": base,
            "mean_base_time": r.get("mean_base_user_time"),
            "hint_time": hint,
            "ratio": ratio,
        }


def main(exp_dir: str, out_path: str) -> None:
    n = 0
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w") as out:
        for run_dir in sorted(glob.glob(os.path.join(exp_dir, "local_abs_*iter", "*"))):
            if not os.path.exists(os.path.join(run_dir, "summary.json")):
                continue
            source = os.path.basename(os.path.dirname(run_dir))
            for row in rows_from_run(run_dir, source):
                out.write(json.dumps(row) + "\n")
                n += 1
    print(f"wrote {n} rows to {out_path}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
