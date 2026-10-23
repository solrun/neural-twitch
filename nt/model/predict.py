"""Generate abstractions with a trained model and write them as sets for Twee.

  python -m nt.model.predict --checkpoint runs/first/best.pt --data data/dataset \\
      --split test,hard --top 1,3,5 --out out/pred

For every problem in the split and each goal-flattening setting, samples
--samples abstractions from the generator, merges duplicates and ranks them:

  count    how often the generator sampled it (a Monte Carlo estimate of its
           likelihood); ties broken by the scorer. The default: reranking by
           likelihood beats the scorer, which ranks worse than the baseline.
  scorer   the scorer head's logit (the original ranking)

and writes the top k as a set: out/pred_k{K}_{flat|noflat}.jsonl, in the
format `nt.single_runs --sets` and slurm/eval_sets.sbatch read. Each set row
also says which of its abstractions are novel: not among the abstractions
labelled on any training problem (any label, any setting), so not something
the model could have copied. out/pred_candidates.jsonl keeps every distinct
sample with its count, score and novelty.

For the hard split, the plain-Twee runs do not prove, so every proved "set"
row is a problem Twee alone could not solve.
"""

from __future__ import annotations

import argparse
import collections
import gzip
import json
import os

RANKINGS = ("count", "scorer")


def rank_samples(samples: list[tuple[str | None, float]], by: str = "count") -> list[dict]:
    """Merge (abstraction, scorer logit) samples into distinct candidates
    {abstraction, count, score}, best first. Undecodable samples (None) are
    dropped. count: most sampled first, ties by score; scorer: by score."""
    count: collections.Counter = collections.Counter()
    score: dict = {}
    for a, s in samples:
        if a is None:
            continue
        count[a] += 1
        score[a] = max(score.get(a, float("-inf")), s)
    cands = [{"abstraction": a, "count": count[a], "score": score[a]} for a in count]
    if by == "count":
        key = lambda c: (-c["count"], -c["score"], c["abstraction"])
    elif by == "scorer":
        key = lambda c: (-c["score"], -c["count"], c["abstraction"])
    else:
        raise ValueError(f"unknown ranking {by!r}; choose from {RANKINGS}")
    return sorted(cands, key=key)


def train_abstractions(data_dir: str) -> set[str]:
    """Every abstraction labelled on a training problem: singles and set
    members, any label, flattening setting and weight."""
    seen = set()
    with gzip.open(os.path.join(data_dir, "examples.jsonl.gz"), "rt") as f:
        for line in f:
            r = json.loads(line)
            if r["split"] != "train":
                continue
            seen.update(t["abstraction"] for t in r["singles"])
            for s in r["sets"]:
                seen.update(s["abstractions"])
    return seen


def sample_all(model, items: list, device, samples: int, temperature: float,
               batch_items: int = 8) -> list[list[tuple[str | None, float]]]:
    """All raw samples per item: (abstraction or None, scorer logit)."""
    import torch

    from nt.model.data import collate_graphs, to
    from nt.model.train import batches, decode

    out = []
    with torch.no_grad():
        model.eval()
        for chunk in batches(items, batch_items, shuffle=False):
            b = to(collate_graphs([it.graph for it in chunk]), device)
            graph = torch.arange(len(chunk), device=device).repeat_interleave(samples)
            flat = torch.tensor([int(it.flatten) for it in chunk],
                                device=device).repeat_interleave(samples)
            acts, score = model.sample(b, graph, flat, temperature=temperature)
            for k, it in enumerate(chunk):
                out.append([(decode(acts[i], it.graph), float(score[i]))
                            for i in range(k * samples, (k + 1) * samples)])
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--data", required=True, help="output directory of nt.dataset")
    ap.add_argument("--split", default="test", help="comma-separated splits, e.g. test,hard")
    ap.add_argument("--samples", type=int, default=128)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--rank", choices=RANKINGS, default="count")
    ap.add_argument("--top", default="1,3,5", help="set sizes to write")
    ap.add_argument("--out", required=True, help="output prefix")
    ap.add_argument("--device", default="auto")
    args = ap.parse_args()

    import torch

    from nt.model.data import Item, graph_from_row
    from nt.model.net import Generator

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
    seen = train_abstractions(args.data)
    print(f"{len(items) // 2} problems in {sorted(splits)}; {args.samples} samples each, "
          f"both flattening settings; ranked by {args.rank}; "
          f"{len(seen)} distinct abstractions labelled in train", flush=True)
    raw = sample_all(model, items, device, args.samples, args.temperature)

    tops = [int(k) for k in args.top.split(",")]
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    files = {(k, f): open(f"{args.out}_k{k}_{'flat' if f else 'noflat'}.jsonl", "w")
             for k in tops for f in (True, False)}
    stats = collections.Counter()
    with open(f"{args.out}_candidates.jsonl", "w") as cand:
        for it, samples in zip(items, raw):
            ranked = rank_samples(samples, args.rank)
            for c in ranked:
                c["novel"] = c["abstraction"] not in seen
            stats["invalid samples"] += sum(s is None for s, _ in samples)
            stats["samples"] += len(samples)
            stats["distinct"] += len(ranked)
            stats["distinct novel"] += sum(c["novel"] for c in ranked)
            cand.write(json.dumps({"problem": it.graph.problem, "split": it.graph.split,
                                   "flatten": it.flatten, "candidates": ranked}) + "\n")
            if not ranked:
                stats["items without a valid sample"] += 1
            for k in tops:
                if not ranked:
                    continue
                top = ranked[:k]
                stats[f"k{k} novel"] += sum(c["novel"] for c in top)
                stats[f"k{k} written"] += len(top)
                files[k, it.flatten].write(json.dumps({
                    "problem": it.graph.problem, "path": it.graph.path,
                    "domain": it.graph.problem[:3], "split": it.graph.split,
                    "abstractions": [c["abstraction"] for c in top],
                    "counts": [c["count"] for c in top],
                    "scores": [c["score"] for c in top],
                    "novel": [c["novel"] for c in top]}) + "\n")
    for fh in files.values():
        fh.close()
    n = stats["samples"] or 1
    print(f"samples: {stats['invalid samples'] / n:.1%} undecodable; "
          f"{stats['distinct']} distinct candidates, "
          f"{stats['distinct novel'] / max(stats['distinct'], 1):.0%} novel")
    for k in tops:
        w = stats[f"k{k} written"]
        print(f"k={k}: {stats[f'k{k} novel']} of {w} abstractions in the sets are novel "
              f"({stats[f'k{k} novel'] / max(w, 1):.0%})")
    if stats["items without a valid sample"]:
        print(f"{stats['items without a valid sample']} (problem, setting) pairs got no "
              f"valid sample and have no set")
    print("wrote", ", ".join(sorted(fh.name for fh in files.values())))


if __name__ == "__main__":
    main()
