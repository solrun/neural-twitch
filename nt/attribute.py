"""Which abstractions are behind the problems a method proves?

  python -m nt.attribute out/eval/*.jsonl --method pred --sets-prefix out/pred \\
      --splits-data data/dataset --train-data data/dataset_extra \\
      --alloc-budget 2e12 [--all] [--splits hard,?] [--out attribution_pred.md]

Inputs: the nt.single_runs outputs of slurm/eval_sets.sbatch for every method
(merged or shard files, named <method>_k<K>_<flat|noflat>[_<shard>].jsonl, as
for nt.eval_report), and the sets file of --method (<prefix>_k<K>_<flat|noflat>.jsonl
from nt.model.predict or nt.model.rerank --write-sets).

For each problem in --splits that --method proves in some configuration
(any k, either flattening setting) and no other method proves in any, it
lists the configurations that prove it and, for each, the set's
abstractions with two kinds of novelty against the training labels of
--train-data:
  new string  this exact abstraction was never labelled on a training problem
  new shape   neither was its shape (symbols renamed, nt.baseline.shape_of)
A k=1 configuration attributes the proof to one abstraction exactly.
"""

from __future__ import annotations

import argparse
import collections
import json
import os

from nt import eval_report as er
from nt.baseline import shape_of
from nt.model.predict import train_abstractions
from nt.terms import parse


def shape(a: str) -> str:
    return shape_of(parse(a))[0]


def load_sets(prefix: str, configs) -> dict:
    """{(k, flat): {problem: abstractions}} for the configurations evaluated."""
    out = {}
    for k, flat in configs:
        path = f"{prefix}_k{k}_{'flat' if flat else 'noflat'}.jsonl"
        if not os.path.exists(path):
            continue
        out[k, flat] = {r["problem"]: r["abstractions"]
                        for r in map(json.loads, open(path)) if r.get("abstractions")}
    return out


def proved_by(runs: dict) -> dict:
    """{method: {problem: [(k, flat), ...]}} for set runs within the budget."""
    out: dict = collections.defaultdict(lambda: collections.defaultdict(list))
    for (method, k, flat), probs in runs.items():
        for p, rr in probs.items():
            if er.proved(rr.get("set")):
                out[method][p].append((k, flat))
    return out


TAGS = ("seen", "new string", "new shape")


def cfg_name(k: int, flat: bool) -> str:
    return f"k{k}{'f' if flat else 'n'}"


def attribute(runs: dict, splits: dict, method: str, sets: dict, seen: set[str],
              keep_splits: set[str], all_problems: bool = False) -> list[str]:
    """Report the proving sets of `method`'s problems in keep_splits: only the
    ones no other method proves, or with all_problems every one it proves.

    A problem *needs a new shape* if every set of `method` that proves it
    contains a new-shape abstraction; if some proving set has none, known
    shapes suffice. A k=1 proof attributes the proof to one abstraction."""
    by = proved_by(runs)
    if method not in by:
        return [f"No proofs by {method!r}; methods with proofs: {', '.join(sorted(by))}"]
    other_methods = sorted(m for m in by if m != method)
    seen_shapes = {shape(a) for a in seen}

    def tag(a: str) -> str:
        if shape(a) not in seen_shapes:
            return "new shape"
        return "new string" if a not in seen else "seen"

    probs = sorted(p for p in by[method] if splits.get(p, "?") in keep_splits
                   and (all_problems or not any(p in by[m] for m in other_methods)))
    k1_tags: collections.Counter = collections.Counter()
    needs_new, body = [], []
    for p in probs:
        cfgs = sorted(by[method][p])
        also = [m for m in other_methods if p in by[m]]
        body += [f"## {p} ({splits.get(p, '?')}): {' '.join(cfg_name(*c) for c in cfgs)}",
                 "", f"Also proved by: {', '.join(also) or 'no other method'}.", ""]
        known_suffices, any_set = False, False
        for k, f in cfgs:
            abstr = sets.get((k, f), {}).get(p)
            if abstr is None:
                body.append(f"- {cfg_name(k, f)}: set not found")
                continue
            any_set = True
            tags = [tag(a) for a in abstr]
            known_suffices |= "new shape" not in tags
            if k == 1:
                k1_tags[tags[0]] += 1
            body.append(f"- {cfg_name(k, f)}: "
                        + ", ".join(f"`{a}` ({t})" for a, t in zip(abstr, tags)))
        if any_set and not known_suffices:
            needs_new.append((p, also))
        body.append("")

    scope = "every problem" if all_problems else "problems only"
    lines = [f"# Attribution: {scope} {method} proves", "",
             f"Splits {', '.join(sorted(keep_splits))}; other methods: "
             f"{', '.join(other_methods) or 'none'}.", "",
             f"- {len(probs)} problems.",
             f"- k=1 proofs (one abstraction each, counted per proving configuration): "
             + ", ".join(f"{t} {k1_tags[t]}" for t in TAGS) + ".",
             f"- Every proving set has a new-shape abstraction (candidates for a needed new "
             f"pattern): {len(needs_new)}"
             + (": " + ", ".join(f"{p}" + (f" (also {'/'.join(a)})" if a else "")
                                 for p, a in needs_new) if needs_new else "") + ".",
             f"- Known shapes suffice (some proving set has no new shape): "
             f"{len(probs) - len(needs_new)}.", ""]
    return lines + body


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("files", nargs="+", help="out/eval/*.jsonl (merged or shard files)")
    ap.add_argument("--method", required=True)
    ap.add_argument("--sets-prefix", required=True, help="e.g. out/pred")
    ap.add_argument("--splits-data", required=True, help="nt.dataset output for the splits")
    ap.add_argument("--train-data", required=True, help="nt.dataset output the model trained on")
    ap.add_argument("--splits", default="hard,?")
    ap.add_argument("--all", action="store_true",
                    help="every problem --method proves, not only those no other method proves")
    ap.add_argument("--alloc-budget", type=float, metavar="BYTES")
    ap.add_argument("--out")
    args = ap.parse_args()
    er.ALLOC_BUDGET = args.alloc_budget
    runs = er.load_runs(args.files)
    configs = {(k, f) for m, k, f in runs if m == args.method}
    text = "\n".join(attribute(runs, er.load_splits(args.splits_data), args.method,
                               load_sets(args.sets_prefix, configs),
                               train_abstractions(args.train_data), set(args.splits.split(",")),
                               all_problems=args.all))
    print(text)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text + "\n")


if __name__ == "__main__":
    main()
