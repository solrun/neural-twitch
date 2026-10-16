"""Rerank the baseline's candidates with a trained model.

The baseline already has a helpful abstraction in its top 200 for ~90% of
validation examples, but ranks it first only ~30% of the time. This scores
the baseline's top --pool candidates with the model, without sampling:

  baseline   the baseline's own order (nt.baseline combined)
  scorer     the model's scorer logit
  gen        the generator's log-likelihood of the candidate
  fuse       reciprocal-rank fusion of baseline, scorer and gen orders
  bgen       reciprocal-rank fusion of baseline and gen orders (no scorer)
  mix        bgen's first candidate, then the baseline order: keeps the
             reranked top pick (better at k=1 in the Twee evaluation) and the
             baseline's more varied tail (better at k=3, 5)

  python -m nt.model.rerank --checkpoint runs/first/best.pt --data data/dataset

With --write-sets PREFIX it writes the top-k sets of --method for --set-splits
(PREFIX_k{K}_{flat|noflat}.jsonl), the same format as nt.model.predict.
"""

from __future__ import annotations

import argparse
import collections
import json
import os

import torch

from nt.baseline import Baselines, load as load_baseline
from nt.model.data import (FUNC, MAX_SLOTS, VAR, Item, Target, collate, graph_from_row, to)
from nt.model.net import Generator

KS = (1, 5, 10)
METHODS = ("baseline", "scorer", "gen", "fuse", "bgen", "mix")


def encode(abstraction: str, g) -> list | None:
    """Action sequence on a GraphT (cf. nt.graph.encode_abstraction)."""
    from nt.terms import App, ParseError, Var, parse
    try:
        t = parse(abstraction)
    except ParseError:
        return None
    if not isinstance(t, App):
        return None
    sidx = {(n, int(a)): i for i, (n, a) in enumerate(zip(g.sym_names, g.sym_arity.tolist()))}
    slots: dict = {}
    out: list = []

    def go(u) -> bool:
        if isinstance(u, Var):
            slots.setdefault(u.name, len(slots))
            out.append([VAR, slots[u.name]])
            return True
        s = sidx.get((u.fn, len(u.args)))
        if s is None:
            return False
        out.append([FUNC, s])
        return all(go(a) for a in u.args)

    if not go(t) or len(out) > 64 or len(slots) > MAX_SLOTS:
        return None
    return out


@torch.no_grad()
def model_scores(model, graph, flatten: bool, cands: list, device) -> tuple[list, list]:
    """(scorer logits, generator log-likelihoods) for candidates (None if unencodable)."""
    enc = [(c, encode(c, graph)) for c in cands]
    ok = [(c, a) for c, a in enc if a]
    sc, ll = {}, {}
    for i in range(0, len(ok), 256):
        chunk = ok[i:i + 256]
        it = Item(graph, flatten, [Target(a, c, False, 0.0, 0.0) for c, a in chunk])
        r = model(to(collate([it]), device))
        for (c, _), s, n in zip(chunk, r["score"].tolist(), r["nll"].tolist()):
            sc[c], ll[c] = s, -n
    return [sc.get(c) for c in cands], [ll.get(c) for c in cands]


def rankings(cands: list, sc: list, ll: list, rrf_k: float = 10.0) -> dict:
    keep = [i for i, s in enumerate(sc) if s is not None]
    base = [cands[i] for i in keep]
    by_sc = [cands[i] for i in sorted(keep, key=lambda i: -sc[i])]
    by_ll = [cands[i] for i in sorted(keep, key=lambda i: -ll[i])]
    def rrf(*orders):
        fused = collections.Counter()
        for order in orders:
            for r, c in enumerate(order):
                fused[c] += 1.0 / (rrf_k + r)
        return [c for c, _ in fused.most_common()]

    bgen = rrf(base, by_ll)
    mix = bgen[:1] + [c for c in base if c not in bgen[:1]]
    return {"baseline": base, "scorer": by_sc, "gen": by_ll,
            "fuse": rrf(base, by_sc, by_ll), "bgen": bgen, "mix": mix}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--data", required=True, help="output directory of nt.dataset")
    ap.add_argument("--weight", default="f0.5")
    ap.add_argument("--splits", default="val,test")
    ap.add_argument("--pool", type=int, default=50, help="baseline candidates to rerank")
    ap.add_argument("--method", default="bgen", choices=METHODS, help="ranking for --write-sets")
    ap.add_argument("--write-sets", metavar="PREFIX")
    ap.add_argument("--top", default="1,3,5")
    ap.add_argument("--set-splits", default="test,hard")
    ap.add_argument("--device", default="auto")
    args = ap.parse_args()

    device = torch.device(args.device if args.device != "auto" else
                          ("cuda" if torch.cuda.is_available() else "cpu"))
    ck = torch.load(args.checkpoint, map_location=device)
    a = ck["args"]
    model = Generator(a["hidden"], a["layers"], not a["no_names"], a["name_dropout"]).to(device)
    model.load_state_dict(ck["model"])
    model.eval()

    import gzip
    graphs = {}
    with gzip.open(os.path.join(args.data, "graphs.jsonl.gz"), "rt") as f:
        for line in f:
            r = json.loads(line)
            graphs[r["problem"]] = graph_from_row(r)
    bgraphs, examples = load_baseline(args.data, args.weight)
    base = Baselines([e for e in examples if e["split"] == "train"])

    print(f"| split | method | examples | " + " | ".join(f"hit@{k}" for k in KS)
          + f" | in pool ({args.pool}) |")
    print("|---|---|---|" + "---|" * (len(KS) + 1))
    for split in args.splits.split(","):
        exs = [e for e in examples if e["split"] == split
               and any(t["label"] == "helps" for t in e["singles"])]
        if not exs:
            continue
        hits = {m: collections.Counter() for m in METHODS}
        for e in exs:
            good = {t["abstraction"] for t in e["singles"] if t["label"] == "helps"}
            cands = base.rank_combined(bgraphs[e["problem"]]["syms"], e["flatten"])[:args.pool]
            sc, ll = model_scores(model, graphs[e["problem"]], e["flatten"], cands, device)
            for m, order in rankings(cands, sc, ll).items():
                for k in KS:
                    hits[m][k] += bool(good & set(order[:k]))
                hits[m]["pool"] += bool(good & set(order))
        n = len(exs)
        for m in METHODS:
            print(f"| {split} | {m} | {n} | "
                  + " | ".join(f"{hits[m][k] / n:.3f}" for k in (*KS, "pool")) + " |", flush=True)

    if args.write_sets:
        tops = [int(k) for k in args.top.split(",")]
        splits = set(args.set_splits.split(","))
        os.makedirs(os.path.dirname(args.write_sets) or ".", exist_ok=True)
        files = {(k, f): open(f"{args.write_sets}_k{k}_{'flat' if f else 'noflat'}.jsonl", "w")
                 for k in tops for f in (True, False)}
        for p, g in sorted(graphs.items()):
            if g.split not in splits:
                continue
            for flat in (True, False):
                cands = base.rank_combined(bgraphs[p]["syms"], flat)[:args.pool]
                sc, ll = model_scores(model, g, flat, cands, device)
                order = rankings(cands, sc, ll)[args.method]
                for k in tops:
                    if order:
                        files[k, flat].write(json.dumps({
                            "problem": p, "path": g.path, "domain": p[:3],
                            "abstractions": order[:k]}) + "\n")
        for fh in files.values():
            fh.close()
        print("wrote", ", ".join(sorted(fh.name for fh in files.values())))


if __name__ == "__main__":
    main()
