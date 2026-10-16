"""Non-learned baselines for the abstraction generator.

Reads the dataset written by nt.dataset (no PyTorch needed) and ranks
abstractions for each validation/test example from what helped on the
training examples:

  name      abstractions that helped on training problems, restricted to
            those whose symbols (with arities) the problem has; ranked by
            how often they helped (smoothed rate as tie-break), counted per
            goal-flattening setting with the other setting as fallback.
            Works within a theory, where TPTP reuses names like multiply.
  shape     symbol names replaced by placeholders, f(X0, g(X0)) becoming
            F2(X0, F1(X0)); shapes ranked by how often they helped on any
            training problem, then instantiated with the problem's own
            symbols of matching arities (distinct placeholders, distinct
            symbols; more frequent symbols first). Carries over between
            theories: the plan's "small patterns ranked by experience".
  combined  name candidates first, then shape candidates.

Metrics match nt.model.train's validation: hit@k = share of examples with
at least one helpful abstraction where one of the top k candidates is a
known helpful abstraction for that problem and setting.

  python -m nt.baseline --data data/dataset [--splits val,test] [--write-sets out/base]

--write-sets writes the top-k lists as sets (out/base_{method}_k{K}_{flat|noflat}.jsonl)
for `nt.single_runs --sets`, so the baselines get the same Twee evaluation as
the model's predictions.
"""

from __future__ import annotations

import argparse
import collections
import gzip
import itertools
import json
import os

from nt.terms import App, ParseError, Var, parse

KS = (1, 5, 10)
PH = "zzs"          # placeholder symbol prefix in shapes (lower case: the term parser
                    # reads capitalised names as variables)


def load(data_dir: str, weight: str):
    graphs = {}
    with gzip.open(os.path.join(data_dir, "graphs.jsonl.gz"), "rt") as f:
        for line in f:
            r = json.loads(line)
            g = r["graph"]
            uses = collections.Counter(g["edges"].get("head", [[], []])[1])
            graphs[r["problem"]] = {
                "split": r["split"], "path": r.get("path", ""),
                "syms": [(n, a, uses[i]) for i, (n, a) in
                         enumerate(zip(g["sym_names"], g["sym_arity"]))]}
    examples = []
    with gzip.open(os.path.join(data_dir, "examples.jsonl.gz"), "rt") as f:
        for line in f:
            r = json.loads(line)
            if weight and r["weight"] != weight:
                continue
            examples.append(r)
    return graphs, examples


def shape_of(t) -> tuple[str, list[int]] | None:
    """(template, placeholder arities): symbols renamed zzs0, zzs1, ... in
    first-occurrence order, the same symbol always the same placeholder."""
    names: dict = {}
    arities: list[int] = []

    def go(u):
        if isinstance(u, Var):
            return u
        key = (u.fn, len(u.args))
        if key not in names:
            names[key] = f"{PH}{len(names)}"
            arities.append(len(u.args))
        return App(names[key], tuple(go(a) for a in u.args))

    return str(go(t)), arities


def instantiate(template: str, arities: list[int], syms: list, limit: int) -> list[str]:
    """Fill a shape's placeholders with distinct problem symbols of the right
    arity, more frequently used symbols first; at most `limit` results."""
    by_arity = collections.defaultdict(list)
    for name, ar, uses in sorted(syms, key=lambda s: -s[2]):
        by_arity[ar].append(name)
    pools = [by_arity[a] for a in arities]
    if any(not p for p in pools):
        return []
    t = parse(template)
    out = []
    for combo in itertools.product(*pools):
        if len(set(combo)) < len(combo):
            continue
        mapping = {f"{PH}{i}": s for i, s in enumerate(combo)}

        def go(u):
            if isinstance(u, Var):
                return u
            return App(mapping[u.fn], tuple(go(a) for a in u.args))

        out.append(str(go(t)))
        if len(out) >= limit:
            break
    return out


class Baselines:
    def __init__(self, train_examples: list, alpha: float = 1.0):
        self.name = collections.defaultdict(lambda: [0, 0])     # (flat, abstr) -> [helps, n]
        self.shape = collections.defaultdict(lambda: [0, 0])    # (flat, template) -> [helps, n]
        self.shape_arities: dict = {}
        self.syms_of: dict = {}                                 # abstraction -> {(sym, arity)}
        self.alpha = alpha
        for ex in train_examples:
            for t in ex["singles"]:
                a = t["abstraction"]
                try:
                    term = parse(a)
                except ParseError:
                    continue
                if a not in self.syms_of:
                    self.syms_of[a] = set(_symbols(term))
                tpl, ars = shape_of(term)
                self.shape_arities[tpl] = ars
                good = t["label"] == "helps"
                for key, table in (((ex["flatten"], a), self.name), ((ex["flatten"], tpl), self.shape)):
                    table[key][0] += good
                    table[key][1] += 1

    def _score(self, table, flat, key):
        h, n = table[(flat, key)]
        h2, n2 = table[(not flat, key)]
        # own setting first; the other setting as a weak fallback
        hits = h + 0.25 * h2
        rate = (h + self.alpha * 0.25) / (n + self.alpha)
        return (hits, rate)

    def rank_name(self, syms: list, flat: bool) -> list[str]:
        have = {(n, a) for n, a, _ in syms}
        cands = {a for (f, a), (h, n) in self.name.items() if h > 0 and self.syms_of[a] <= have}
        return sorted(cands, key=lambda a: self._score(self.name, flat, a), reverse=True)

    def rank_shape(self, syms: list, flat: bool, per_shape: int = 20, total: int = 200) -> list[str]:
        shapes = {tpl for (f, tpl), (h, n) in self.shape.items() if h > 0}
        out, seen = [], set()
        for tpl in sorted(shapes, key=lambda s: self._score(self.shape, flat, s), reverse=True):
            for a in instantiate(tpl, self.shape_arities[tpl], syms, per_shape):
                if a not in seen:
                    seen.add(a)
                    out.append(a)
            if len(out) >= total:
                break
        return out

    def rank_combined(self, syms: list, flat: bool) -> list[str]:
        named = self.rank_name(syms, flat)
        seen = set(named)
        return named + [a for a in self.rank_shape(syms, flat) if a not in seen]


def _symbols(t):
    if isinstance(t, App):
        yield (t.fn, len(t.args))
        for a in t.args:
            yield from _symbols(a)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--data", required=True, help="output directory of nt.dataset")
    ap.add_argument("--weight", default="f0.5")
    ap.add_argument("--splits", default="val,test")
    ap.add_argument("--write-sets", metavar="PREFIX",
                    help="write top-k sets for nt.single_runs --sets")
    ap.add_argument("--top", default="1,3,5", help="set sizes for --write-sets")
    ap.add_argument("--set-splits", default="test,hard", help="splits for --write-sets")
    args = ap.parse_args()

    graphs, examples = load(args.data, args.weight)
    base = Baselines([e for e in examples if e["split"] == "train"])
    methods = {"name": base.rank_name, "shape": base.rank_shape, "combined": base.rank_combined}

    print("| split | method | examples | hit@1 | hit@5 | hit@10 | in top 200 |")
    print("|---|---|---|---|---|---|---|")
    for split in args.splits.split(","):
        exs = [e for e in examples if e["split"] == split
               and any(t["label"] == "helps" for t in e["singles"])]
        if not exs:
            continue
        for mname, rank in methods.items():
            hits = collections.Counter()
            for e in exs:
                good = {t["abstraction"] for t in e["singles"] if t["label"] == "helps"}
                ranked = rank(graphs[e["problem"]]["syms"], e["flatten"])
                for k in KS:
                    hits[k] += bool(good & set(ranked[:k]))
                hits["all"] += bool(good & set(ranked[:200]))
            n = len(exs)
            print(f"| {split} | {mname} | {n} | " + " | ".join(
                f"{hits[k] / n:.3f}" for k in (*KS, "all")) + " |")

    if args.write_sets:
        tops = [int(k) for k in args.top.split(",")]
        splits = set(args.set_splits.split(","))
        os.makedirs(os.path.dirname(args.write_sets) or ".", exist_ok=True)
        for mname, rank in methods.items():
            for flat in (True, False):
                files = {k: open(f"{args.write_sets}_{mname}_k{k}_{'flat' if flat else 'noflat'}.jsonl", "w")
                         for k in tops}
                for p, g in sorted(graphs.items()):
                    if g["split"] not in splits:
                        continue
                    ranked = rank(g["syms"], flat)
                    for k in tops:
                        if ranked:
                            files[k].write(json.dumps({"problem": p, "path": g["path"],
                                                       "domain": p[:3],
                                                       "abstractions": ranked[:k]}) + "\n")
                for fh in files.values():
                    fh.close()
        print(f"\nwrote sets to {args.write_sets}_<method>_k<K>_<flat|noflat>.jsonl")


if __name__ == "__main__":
    main()
