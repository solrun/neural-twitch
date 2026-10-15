"""Build the training dataset for the abstraction generator.

Joins the per-run labels written by `nt.analyze_single --labels-out` with
problem graphs (nt.graph) and splits problems so that related problems never
straddle train and test.

Output directory:
  graphs.jsonl.gz    one row per problem: {problem, domain, axioms, split,
                     graph}; also for the held-out hard problems, which have
                     no labels but are what the model is finally tested on
  examples.jsonl.gz  one row per (problem, flattening, weight setting):
                     {problem, split, flatten, weight, singles: [...], sets: [...]}
                     each target {abstraction(s), actions, ratio, label,
                     lower_bound}; ratio is None for wall-clock timeouts
  splits.json        problems per split and the options used
  text.jsonl         (with --text) prompt/completion pairs for an LLM:
                     the problem's clauses in TPTP (includes expanded) and
                     the abstractions that help, best first
  stats.md           what went in and what was dropped

Splits (--group):
  axioms   problems with the same axioms (role 'axiom', up to renaming and
           orientation; hypotheses and goals ignored) stay together. This is
           the plan's split: TPTP variants of one theory, and hindsight
           subproblems with their source, cannot leak across splits.
  source   only a hindsight subproblem and its source stay together.
  problem  no grouping.
Groups go to train/val/test by a hash of the group key, so the assignment is
stable when data is added. --holdout-domain puts a whole domain in its own
split for the leave-domain-out experiment; problems in --hard go to 'hard'.

Usage:
  python -m nt.dataset --labels data/single_labels.jsonl data/expand_labels.jsonl \\
      --tptp-dir $TWITCH_DIR/data/TPTP --problems out/expand/hindsight/manifest.jsonl \\
      --out data/dataset [--group axioms] [--holdout-domain ROB] [--text]
"""

from __future__ import annotations

import argparse
import collections
import glob
import gzip
import hashlib
import json
import os
import re
import statistics as st

from nt import tptp
from nt.graph import (axiomatization_key, build_graph, encode_abstraction,
                      problem_clauses)

WEIGHT_NAMES = {(0.0, 1.0): "cost1", (0.2, 0.0): "f0.2", (0.5, 0.0): "f0.5"}
_HS = re.compile(r"_hs\d+$")


def weight_name(factor: float, cost: float) -> str:
    return WEIGHT_NAMES.get((float(factor), float(cost)), f"f{factor:g}_c{cost:g}")


def source_of(problem: str) -> str:
    return _HS.sub("", problem)


def unit_hash(key: str, seed: int) -> float:
    h = hashlib.sha1(f"{seed}:{key}".encode()).hexdigest()
    return int(h[:12], 16) / 16 ** 12


def problem_paths(tptp_dir: str | None, manifests: list[str]) -> dict[str, dict]:
    out = {}
    if tptp_dir:
        for p in glob.glob(os.path.join(tptp_dir, "*_UEQ_UNSAT", "*.p")):
            dom = os.path.basename(os.path.dirname(p)).split("_")[0]
            stem = os.path.basename(p)[:-2]
            pid = stem if stem.startswith(dom) else f"{dom}-{stem}"
            out[pid] = {"path": p, "domain": dom}
    for m in manifests:
        for line in open(m):
            if line.strip():
                r = json.loads(line)
                out[r["problem"]] = {"path": r["path"], "domain": r.get("domain", r["problem"][:3])}
    return out


def read_hard(path: str | None) -> set[str]:
    if not path:
        return set()
    return {l.strip() for l in open(path) if l.strip() and not l.startswith("#")}


def tptp_text(problem_path: str, tptp_root: str | None) -> str:
    """The problem's cnf clauses with includes expanded, for text models."""
    tptp_root = tptp_root if tptp_root is not None else os.environ.get("TPTP_ROOT")
    out = []
    for st_ in tptp.statements(open(problem_path).read()):
        if st_.kind == "include":
            p = tptp.resolve_include(st_.path, problem_path, tptp_root)
            out += [s.text for s in tptp.statements(open(p).read()) if s.kind == "cnf"]
        elif st_.kind == "cnf":
            out.append(st_.text)
    return "\n".join(" ".join(s.split()) for s in out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--labels", nargs="+", required=True,
                    help="files from nt.analyze_single --labels-out")
    ap.add_argument("--tptp-dir", help="Twitch's data/TPTP (paths of the original problems)")
    ap.add_argument("--problems", nargs="*", default=[],
                    help="manifests or sets files from nt.expand (paths of new problems)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--group", choices=["axioms", "source", "problem"], default="axioms")
    ap.add_argument("--fractions", default="0.8,0.1,0.1", help="train,val,test")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--holdout-domain", default="", help="comma-separated domains")
    ap.add_argument("--hard", default=os.path.join(os.path.dirname(__file__), "..", "data",
                                                   "hard_problems.txt"))
    ap.add_argument("--tptp-root", default=os.environ.get("TPTP_ROOT"))
    ap.add_argument("--text", action="store_true", help="also write text.jsonl for LLMs")
    args = ap.parse_args()

    fr = [float(x) for x in args.fractions.split(",")]
    if len(fr) != 3 or abs(sum(fr) - 1) > 1e-6:
        ap.error("--fractions needs three numbers summing to 1")
    held_domains = {d for d in args.holdout_domain.split(",") if d}
    hard = read_hard(args.hard)
    paths = problem_paths(args.tptp_dir, args.problems)
    drop = collections.Counter()

    # labels, grouped per (problem, flatten, weight)
    groups: dict = collections.defaultdict(lambda: {"singles": {}, "sets": []})
    for f in args.labels:
        for line in open(f):
            if not line.strip():
                continue
            r = json.loads(line)
            k = (r["problem"], r["flatten_goal"],
                 weight_name(r["hint_skel_factor"], r["hint_skel_cost"]))
            tgt = {"ratio": r["ratio"], "label": r["label"],
                   "lower_bound": bool(r.get("lower_bound"))}
            if r["kind"] == "single":
                groups[k]["singles"][r["abstractions"][0]] = tgt
            else:
                groups[k]["sets"].append({"abstractions": r["abstractions"], **tgt})
    labelled = {p for p, _, _ in groups}

    # graphs for every labelled problem and every hard problem
    graphs, meta = {}, {}
    for p in sorted(labelled | (hard & set(paths))):
        if p not in paths:
            drop["problem file not found"] += 1
            continue
        try:
            clauses = problem_clauses(paths[p]["path"], args.tptp_root)
        except FileNotFoundError:
            drop["missing include (set TPTP_ROOT)"] += 1
            continue
        except ValueError:
            drop["clause not a parsable unit equation"] += 1
            continue
        graphs[p] = build_graph(clauses)
        meta[p] = {"domain": paths[p]["domain"], "axioms": axiomatization_key(clauses)}

    # splits
    def group_key(p: str) -> str:
        if args.group == "axioms":
            return meta[p]["axioms"]
        return source_of(p) if args.group == "source" else p

    split = {}
    for p in graphs:
        if p in hard:
            split[p] = "hard"
        elif meta[p]["domain"] in held_domains:
            split[p] = "heldout_domain"
        else:
            u = unit_hash(group_key(p), args.seed)
            split[p] = "train" if u < fr[0] else "val" if u < fr[0] + fr[1] else "test"
    # a source and its hindsight subproblems must agree even if one of them is
    # hard or in a held-out domain: the stricter split wins
    rank = {"hard": 0, "heldout_domain": 1, "test": 2, "val": 3, "train": 4}
    by_src = collections.defaultdict(list)
    for p in split:
        by_src[source_of(p)].append(p)
    for ps in by_src.values():
        s = min((split[p] for p in ps), key=rank.__getitem__)
        for p in ps:
            split[p] = s

    os.makedirs(args.out, exist_ok=True)
    with gzip.open(os.path.join(args.out, "graphs.jsonl.gz"), "wt") as out:
        for p in sorted(graphs):
            out.write(json.dumps({"problem": p, **meta[p], "split": split[p],
                                  "graph": graphs[p].to_dict()}) + "\n")

    n_ex, n_single, n_set = 0, 0, 0
    label_counts = collections.Counter()
    text_rows = []
    with gzip.open(os.path.join(args.out, "examples.jsonl.gz"), "wt") as out:
        for (p, flat, w), d in sorted(groups.items(), key=lambda x: (x[0][0], x[0][1], x[0][2])):
            if p not in graphs:
                drop["labels for a problem without a graph"] += len(d["singles"]) + len(d["sets"])
                continue
            g = graphs[p]
            singles = []
            for a, tgt in d["singles"].items():
                acts = encode_abstraction(a, g)
                if acts is None:
                    drop["abstraction outside the problem's symbols"] += 1
                    continue
                singles.append({"abstraction": a, "actions": acts, **tgt})
                label_counts[tgt["label"]] += 1
            sets = []
            for s in d["sets"]:
                acts = [encode_abstraction(a, g) for a in s["abstractions"]]
                if any(x is None for x in acts):
                    drop["set with an abstraction outside the symbols"] += 1
                    continue
                sets.append({**s, "actions": acts})
            if not singles and not sets:
                continue
            out.write(json.dumps({"problem": p, "domain": meta[p]["domain"], "split": split[p],
                                  "flatten": flat, "weight": w,
                                  "singles": singles, "sets": sets}) + "\n")
            n_ex += 1
            n_single += len(singles)
            n_set += len(sets)
            if args.text:
                good = sorted((t for t in singles if t["label"] == "helps"),
                              key=lambda t: t["ratio"])
                # a set that helps is a target too when no single member does
                if not good:
                    good = [{"abstraction": a} for s in sets if s["label"] == "helps"
                            for a in s["abstractions"]]
                text_rows.append({
                    "problem": p, "split": split[p], "flatten": flat, "weight": w,
                    "prompt": (f"% goal flattening: {'on' if flat else 'off'}\n"
                               + tptp_text(paths[p]["path"], args.tptp_root)),
                    "completion": "\n".join(dict.fromkeys(t["abstraction"] for t in good))})

    if args.text:
        with open(os.path.join(args.out, "text.jsonl"), "w") as out:
            for r in text_rows:
                out.write(json.dumps(r) + "\n")

    per_split = collections.defaultdict(list)
    for p, s in split.items():
        per_split[s].append(p)
    with open(os.path.join(args.out, "splits.json"), "w") as out:
        json.dump({"options": {"group": args.group, "fractions": fr, "seed": args.seed,
                               "holdout_domain": sorted(held_domains), "hard": args.hard},
                   "splits": {s: sorted(ps) for s, ps in per_split.items()}}, out, indent=1)

    # stats
    group_sizes = collections.Counter(group_key(p) for p in graphs if split[p] not in ("hard",))
    lines = [f"# Dataset ({args.out})", "",
             f"Problems with graphs: {len(graphs)}; examples (problem x flattening x weight): "
             f"{n_ex}; single targets: {n_single}; set targets: {n_set}.", "",
             "| split | problems | domains |", "|---|---|---|"]
    for s in ("train", "val", "test", "heldout_domain", "hard"):
        ps = per_split.get(s, [])
        doms = collections.Counter(meta[p]["domain"] for p in ps)
        lines.append(f"| {s} | {len(ps)} | {', '.join(f'{d} {n}' for d, n in sorted(doms.items()))} |")
    lines += ["", f"Single-abstraction labels: {dict(label_counts)}.", "",
              f"Grouping '{args.group}': {len(group_sizes)} groups; largest "
              f"{', '.join(str(n) for _, n in group_sizes.most_common(5))} problems "
              f"(median {st.median(group_sizes.values()) if group_sizes else 0})."]
    if group_sizes and group_sizes.most_common(1)[0][1] > 0.2 * sum(group_sizes.values()):
        lines.append("Warning: one group holds over 20% of the problems, so split sizes "
                     "will be uneven; consider --group source.")
    lines += ["", "Dropped:", *(f"- {k}: {v}" for k, v in drop.most_common())] if drop else []
    text = "\n".join(lines) + "\n"
    open(os.path.join(args.out, "stats.md"), "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
