"""Generate abstractions with a trained model and write them as sets for Twee.

  python -m nt.model.predict --checkpoint runs/first/best.pt --data data/dataset \\
      --split test --top 1,3,5 --out out/pred

For every problem in the split and each goal-flattening setting, samples
--samples abstractions, merges duplicates, ranks them by the scorer and
writes the top k as a set: out/pred_k{K}_{flat|noflat}.jsonl, in the format
`nt.single_runs --sets` reads. Evaluate a file with the matching setting:

  python -m nt.single_runs --sets out/pred_k3_flat.jsonl out/eval_k3_flat.jsonl \\
      --flatten on --weights f0.5 --max-cps 6000000

For the hard split, leave out --calibration (their baselines do not prove)
and read the status of the "set" rows: every "proved" is a problem Twee
alone could not solve.
out/pred_candidates.jsonl keeps all ranked candidates with scores.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os

import torch

from nt.model.data import Item, graph_from_row
from nt.model.net import Generator
from nt.model.train import generate


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--data", required=True, help="output directory of nt.dataset")
    ap.add_argument("--split", default="test", help="comma-separated splits, e.g. test,hard")
    ap.add_argument("--samples", type=int, default=128)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--top", default="1,3,5", help="set sizes to write")
    ap.add_argument("--out", required=True, help="output prefix")
    ap.add_argument("--device", default="auto")
    args = ap.parse_args()

    device = torch.device(args.device if args.device != "auto" else
                          ("cuda" if torch.cuda.is_available() else "cpu"))
    ck = torch.load(args.checkpoint, map_location=device)
    a = ck["args"]
    model = Generator(a["hidden"], a["layers"], not a["no_names"], a["name_dropout"]).to(device)
    model.load_state_dict(ck["model"])
    model.eval()

    splits = set(args.split.split(","))
    items = []
    with gzip.open(os.path.join(args.data, "graphs.jsonl.gz"), "rt") as f:
        for line in f:
            r = json.loads(line)
            if r["split"] in splits:
                g = graph_from_row(r)
                items += [Item(g, True, []), Item(g, False, [])]
    print(f"{len(items) // 2} problems in {sorted(splits)}; {args.samples} samples each, "
          f"both flattening settings", flush=True)
    gens = generate(model, items, device, args.samples, temperature=args.temperature)

    tops = [int(k) for k in args.top.split(",")]
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    files = {(k, f): open(f"{args.out}_k{k}_{'flat' if f else 'noflat'}.jsonl", "w")
             for k in tops for f in (True, False)}
    with open(f"{args.out}_candidates.jsonl", "w") as cand:
        for it, cands in zip(items, gens):
            ranked = [(s, sc) for s, sc in cands if s is not None]
            cand.write(json.dumps({"problem": it.graph.problem, "split": it.graph.split,
                                   "flatten": it.flatten, "candidates": ranked}) + "\n")
            for k in tops:
                if ranked:
                    files[k, it.flatten].write(json.dumps({
                        "problem": it.graph.problem, "path": it.graph.path,
                        "domain": it.graph.problem[:3],
                        "abstractions": [s for s, _ in ranked[:k]],
                        "scores": [sc for _, sc in ranked[:k]]}) + "\n")
    for fh in files.values():
        fh.close()
    print("wrote", ", ".join(sorted(fh.name for fh in files.values())))


if __name__ == "__main__":
    main()
