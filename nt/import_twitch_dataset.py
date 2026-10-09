"""Import the runs in the Twitch authors' `twitch_dataset.jsonl` that are not
already in `data/labels.jsonl`.

`twitch_dataset.jsonl` (3,313 rows, 922 problems) is a curated release of the
Twitch experiments with the exact Twee flags of each run. It differs from the
local-abstraction summaries that `nt.build_dataset` reads:

* Positives only: every row has speedup > 1, and at most 3 sets per
  (problem, configuration) are kept. It cannot be used on its own to learn
  what hurts; `data/labels.jsonl` stays the source of negatives.
* About 2,660 rows are runs we already have (same set, same configuration,
  identical times). The rest are runs from the other Twitch stages: large
  sets (median ~50 abstractions, mostly `--hint-skel-factor 0.2`) and 88
  rows flagged `--proof-on-saturation --max-time 50`, which look like the
  partial-proof stage (t_par = 50 s). Those 88 carry no `--hint-skel-*`
  flags, so the hinted run's weight setting is not recorded; they get
  `hint_skel_factor = hint_skel_cost = None`.
* `cnf_clauses` lists only the problem file's own clauses: TPTP `include`s
  are not expanded, so the TPTP files are still needed.

Output rows use the `labels.jsonl` schema with `source = "twitch_dataset"`,
`status = "success"` and `ratio = 1 / speedup`.

Usage:
    python -m nt.import_twitch_dataset twitch_dataset.jsonl data/labels.jsonl data/labels_extra.jsonl
"""

from __future__ import annotations

import json
import re
import sys

from nt.terms import canonical

_NUM = r"([0-9.eE+-]+)"


def parse_flags(flags: list[str]) -> dict:
    joined = " ".join(flags)
    f = re.search(r"--hint-skel-factor\s+" + _NUM, joined)
    c = re.search(r"--hint-skel-cost\s+" + _NUM, joined)
    return {"hint_skel_factor": float(f.group(1)) if f else None,
            "hint_skel_cost": float(c.group(1)) if c else None,
            "flatten_goal": "--flatten-goal" in flags}


def canon_set(abstractions: list[str]) -> list[str]:
    out = []
    for a in abstractions:
        c = canonical(a)
        if c is not None and c not in out:
            out.append(c)
    return out


def key(problem, factor, cost, flatten, abstractions):
    return (problem, factor, cost, flatten, frozenset(abstractions))


def convert(row: dict) -> dict:
    flags = parse_flags(row["twee_flags"])
    partial = "--proof-on-saturation" in row["twee_flags"]
    return {
        "problem": row["problem"],
        "domain": row["theory"],
        "source": "twitch_dataset",
        "stage": "partial_proof" if partial else "abstractions",
        **flags,
        "twee_flags": row["twee_flags"],
        "abstractions": canon_set(row["abstractions"]),
        "n_raw": len(row["abstractions"]),
        "status": "success",
        "base_time": row["base_time"],
        "hint_time": row["hints_time"],
        "ratio": 1.0 / row["speedup"],
    }


def main(dataset: str, labels: str, out: str) -> None:
    have = set()
    with open(labels) as fh:
        for line in fh:
            r = json.loads(line)
            have.add(key(r["problem"], r["hint_skel_factor"], r["hint_skel_cost"],
                         r["flatten_goal"], r["abstractions"]))
    n_in = n_new = 0
    with open(dataset) as fh, open(out, "w") as fo:
        for line in fh:
            n_in += 1
            r = convert(json.loads(line))
            k = key(r["problem"], r["hint_skel_factor"], r["hint_skel_cost"],
                    r["flatten_goal"], r["abstractions"])
            if k in have:
                continue
            have.add(k)
            fo.write(json.dumps(r) + "\n")
            n_new += 1
    print(f"{n_in} rows read, {n_in - n_new} already in {labels}, {n_new} written to {out}",
          file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
