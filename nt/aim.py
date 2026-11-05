"""AIM problems (Veroff/Urban): plain-Twee baseline against Prover9 and E.

The dataset is 61,800 AIM-loop problems from Bob Veroff and Josef Urban, each
in LADR (ladr/) and TPTP (tptp/) form: unit-equality axioms as cnf and one
universally quantified equation as an fof conjecture. Problem names are
<family>__goal_<n>; within a family the goals form a curriculum (earlier
proved goals should help with later ones). Urban's 1-second results,
`00p9_1s` (Prover9, no flags) and `00e_1s` (E --auto), are kept in data/aim/.

Runs come from `nt.expand base` on the tptp/ files in a directory named AIM,
so problem ids are AIM-<name> (see slurm/aim_baseline.sbatch). The report
counts a run as proved within a budget in three ways:

  alloc  allocated bytes <= --alloc-budget (default: one second of the
         allocation clock, nt.twee.ALLOC_PER_SECOND). Deterministic.
  cpu    Twee's own CPU time <= --cpu-budget (default 1 s), closest to how
         the Prover9/E lists were made, but machine dependent.
  cap    proved at all within the job's wall cap.

  python -m nt.aim report out/aim/base_*.jsonl --write-lists out/aim/lists
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import re

from nt.twee import ALLOC_PER_SECOND

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(HERE), "data", "aim")
PREFIX = "AIM-"
TOTAL = 61_800

_GOAL = re.compile(r"^(.*)__goal_(\d+)$")


def strip(problem: str) -> str:
    return problem[len(PREFIX):] if problem.startswith(PREFIX) else problem


def family(name: str) -> str:
    m = _GOAL.match(name)
    return m.group(1) if m else name


def goal_index(name: str) -> int:
    m = _GOAL.match(name)
    return int(m.group(2)) if m else -1


def read_list(path: str) -> set[str]:
    with open(path) as f:
        return {l.strip() for l in f if l.strip()}


def read_runs(paths: list[str]) -> list[dict]:
    rows = []
    for p in paths:
        with open(p) as f:
            for line in f:
                if line.strip():
                    try:
                        rows.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass            # truncated last line of a killed shard
    return rows


def within(r: dict, how: str, alloc_budget: float, cpu_budget: float) -> bool:
    if r.get("status") != "proved":
        return False
    if how == "cap":
        return True
    if how == "alloc":
        b = r.get("allocated_bytes")
        return b is not None and b <= alloc_budget
    if how == "cpu":
        c = r.get("cpu_seconds")
        c = r.get("wall") if c is None else c
        return c is not None and c <= cpu_budget
    raise ValueError(how)


def solved_sets(rows: list[dict], alloc_budget: float, cpu_budget: float):
    """{(how, setting): set of names}; setting is "on", "off" or "either"."""
    out = collections.defaultdict(set)
    for r in rows:
        name = strip(r["problem"])
        setting = "on" if r["flatten"] else "off"
        for how in ("alloc", "cpu", "cap"):
            if within(r, how, alloc_budget, cpu_budget):
                out[how, setting].add(name)
                out[how, "either"].add(name)
    return out


def cmd_report(args) -> None:
    rows = [r for r in read_runs(args.runs) if r.get("status") != "error"]
    errors = [r for r in read_runs(args.runs) if r.get("status") == "error"]
    ran = collections.defaultdict(set)
    for r in rows:
        ran["on" if r["flatten"] else "off"].add(strip(r["problem"]))
    p9, e = read_list(args.p9), read_list(args.e)
    S = solved_sets(rows, args.alloc_budget, args.cpu_budget)
    statuses = collections.Counter(r["status"] for r in rows)
    total = len(ran["on"] | ran["off"])

    print(f"runs: {len(rows)} ({dict(statuses)}), errors: {len(errors)}; problems run "
          f"with flattening on {len(ran['on'])}, off {len(ran['off'])} (of {TOTAL})")
    if total < TOTAL:
        p9 &= ran["on"] | ran["off"]
        e &= ran["on"] | ran["off"]
        print(f"partial run: Prover9 and E restricted to the {total} problems run")
    if errors:
        print(f"  first error ({errors[0]['problem']}): {errors[0].get('error', '')[-300:]!r}")
    print(f"budgets: alloc <= {args.alloc_budget:.3g} bytes, cpu <= {args.cpu_budget} s, "
          f"cap = proved within the wall cap\n")

    print("## Proved\n")
    print("| prover | proved | with P9 or E | new vs P9 or E |")
    print("|---|---|---|---|")
    union = p9 | e
    print(f"| Prover9 1 s | {len(p9)} | | |")
    print(f"| E --auto 1 s | {len(e)} | | |")
    print(f"| P9 or E | {len(union)} | | |")
    for how in ("alloc", "cpu", "cap"):
        for setting in ("off", "on", "either"):
            s = S[how, setting]
            label = f"Twee {how}, flattening {setting}"
            print(f"| {label} | {len(s)} | {len(s | union)} | {len(s - union)} |")

    main = S[args.headline, "either"]
    print(f"\n## Overlap (Twee = {args.headline}, either flattening setting)\n")
    venn = collections.Counter()
    for name in main | p9 | e:
        key = ("T" if name in main else "-") + ("P" if name in p9 else "-") + \
              ("E" if name in e else "-")
        venn[key] += 1
    print("| Twee | P9 | E | problems |")
    print("|---|---|---|---|")
    for key in sorted(venn, key=lambda k: -venn[k]):
        print(f"| {'x' if key[0] == 'T' else ''} | {'x' if key[1] == 'P' else ''} "
              f"| {'x' if key[2] == 'E' else ''} | {venn[key]} |")
    print(f"\nall three together: {len(main | union)} of {total}")

    on, off = S[args.headline, "on"], S[args.headline, "off"]
    print(f"\nflattening: only on {len(on - off)}, only off {len(off - on)}, both {len(on & off)}")

    # per family: how much each prover gets, sorted by family size
    fam_total = collections.Counter(family(n) for n in ran["on"] | ran["off"])
    rows_f = []
    for f, n in fam_total.items():
        rows_f.append((f, n, sum(family(x) == f for x in main),
                       sum(family(x) == f for x in p9), sum(family(x) == f for x in e)))
    rows_f.sort(key=lambda t: (-t[1], t[0]))
    print(f"\n## Families ({len(rows_f)}; the {args.families} largest)\n")
    print("| family | goals | Twee | P9 | E |")
    print("|---|---|---|---|---|")
    for f, n, t, p, ee in rows_f[:args.families]:
        print(f"| {f} | {n} | {t} | {p} | {ee} |")

    if args.write_lists:
        os.makedirs(args.write_lists, exist_ok=True)
        for (how, setting), s in sorted(S.items()):
            with open(os.path.join(args.write_lists, f"twee_{how}_{setting}.txt"), "w") as f:
                f.writelines(f"{n}\n" for n in sorted(s))
        unsolved = (ran["on"] | ran["off"]) - main - union
        with open(os.path.join(args.write_lists, "unsolved.txt"), "w") as f:
            f.writelines(f"{n}\n" for n in sorted(unsolved, key=lambda n: (family(n), goal_index(n))))
        print(f"\nlists -> {args.write_lists}/ (twee_<how>_<setting>.txt, unsolved.txt)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("report", help="Twee baseline vs Prover9 and E")
    r.add_argument("runs", nargs="+", help="nt.expand base output (.jsonl)")
    r.add_argument("--p9", default=os.path.join(DATA_DIR, "00p9_1s"))
    r.add_argument("--e", default=os.path.join(DATA_DIR, "00e_1s"))
    r.add_argument("--alloc-budget", type=float, default=float(ALLOC_PER_SECOND),
                   help="bytes (default: 1 s of the allocation clock)")
    r.add_argument("--cpu-budget", type=float, default=1.0, help="seconds")
    r.add_argument("--headline", choices=["alloc", "cpu", "cap"], default="alloc",
                   help="which Twee count the overlap and family tables use")
    r.add_argument("--families", type=int, default=30)
    r.add_argument("--write-lists", default="", metavar="DIR")
    args = ap.parse_args()
    {"report": cmd_report}[args.cmd](args)


if __name__ == "__main__":
    main()
