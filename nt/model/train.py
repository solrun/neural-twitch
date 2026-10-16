"""Train the abstraction generator.

  python -m nt.model.train --data data/dataset --out runs/first [--epochs 60]
  python -m nt.model.train --smoke        # CPU self-test on built-in problems

Loss = generation NLL of the helpful abstractions (weights 1/(1+r),
normalised per example) + --score-weight x scorer BCE on all labelled
abstractions. Validation each epoch:
  nll       mean generation NLL per helpful abstraction (lower is better)
  auc       scorer ranking of helps vs not (0.5 = chance)
  hit@k     share of examples where one of the scorer's top k of
            --samples sampled abstractions is a known helpful one
  valid     share of samples that decode to a well-formed term (must be 1)
The checkpoint with the best hit@5 is kept as best.pt; log.jsonl has every
epoch.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import tempfile
import time

import torch

from nt.graph import Graph, decode_actions
from nt.model.data import Item, Target, collate, collate_graphs, load, to
from nt.model.net import Generator


def batches(items: list, size: int, shuffle: bool):
    order = list(range(len(items)))
    if shuffle:
        random.shuffle(order)
    for i in range(0, len(order), size):
        yield [items[j] for j in order[i:i + size]]


def auc(scores: list, labels: list) -> float:
    pos = [s for s, l in zip(scores, labels) if l]
    neg = [s for s, l in zip(scores, labels) if not l]
    if not pos or not neg:
        return float("nan")
    ranked = sorted([(s, 1) for s in pos] + [(s, 0) for s in neg])
    rank_sum, i = 0.0, 0
    while i < len(ranked):                      # average ranks over ties
        j = i
        while j + 1 < len(ranked) and ranked[j + 1][0] == ranked[i][0]:
            j += 1
        rank_sum += sum(1 for k in range(i, j + 1) if ranked[k][1]) * (i + j + 2) / 2
        i = j + 1
    return (rank_sum - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def decode(actions: list, g) -> str | None:
    try:
        return decode_actions(actions, Graph(sym_names=g.sym_names,
                                             sym_arity=g.sym_arity.tolist()))
    except ValueError:
        return None


@torch.no_grad()
def generate(model, items: list, device, samples: int, batch_items: int = 8,
             temperature: float = 1.0) -> list[list[tuple[str | None, float]]]:
    """For each item: (abstraction or None, scorer logit) for each sample,
    duplicates merged keeping the best score, best first."""
    model.eval()
    out = []
    for chunk in batches(items, batch_items, shuffle=False):
        b = to(collate_graphs([it.graph for it in chunk]), device)
        graph = torch.arange(len(chunk), device=device).repeat_interleave(samples)
        flat = torch.tensor([int(it.flatten) for it in chunk], device=device).repeat_interleave(samples)
        acts, score = model.sample(b, graph, flat, temperature=temperature)
        for k, it in enumerate(chunk):
            best: dict = {}
            for i in range(k * samples, (k + 1) * samples):
                s = decode(acts[i], it.graph)
                if s not in best or float(score[i]) > best[s]:
                    best[s] = float(score[i])
            out.append(sorted(best.items(), key=lambda x: -x[1]))
    return out


@torch.no_grad()
def evaluate(model, items: list, device, samples: int, batch: int) -> dict:
    model.eval()
    nll_sum = n_help = 0.0
    scores, labels = [], []
    for chunk in batches(items, batch, shuffle=False):
        b = to(collate(chunk), device)
        r = model(b)
        helps = b["t_helps"].bool()
        nll_sum += float(r["nll"][helps].sum())
        n_help += int(helps.sum())
        scores += r["score"].tolist()
        labels += b["t_helps"].tolist()
    gens = generate(model, items, device, samples)
    hit = {1: 0, 5: 0, "any": 0}
    total = invalid = 0
    for it, cands in zip(items, gens):
        good = {t.abstraction for t in it.targets if t.helps}
        names = [c for c, _ in cands]
        invalid += sum(1 for c in names if c is None)
        total += len(names)
        if good:
            hit[1] += bool(good & set(names[:1]))
            hit[5] += bool(good & set(names[:5]))
            hit["any"] += bool(good & set(names))
    n_with = sum(1 for it in items if any(t.helps for t in it.targets)) or 1
    return {"nll": nll_sum / max(n_help, 1), "auc": auc(scores, labels),
            "hit@1": hit[1] / n_with, "hit@5": hit[5] / n_with, "hit@any": hit["any"] / n_with,
            "valid": 1 - invalid / max(total, 1)}


def train(args, data: dict) -> dict:
    torch.manual_seed(args.seed)
    random.seed(args.seed)
    device = torch.device(args.device if args.device != "auto" else
                          ("cuda" if torch.cuda.is_available() else "cpu"))
    model = Generator(args.hidden, args.layers, not args.no_names, args.name_dropout).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    os.makedirs(args.out, exist_ok=True)
    log = open(os.path.join(args.out, "log.jsonl"), "w")
    best, history = -1.0, []
    print(f"train {len(data['train'])} examples, val {len(data['val'])}; device {device}; "
          f"{sum(p.numel() for p in model.parameters()):,} parameters", flush=True)
    for epoch in range(1, args.epochs + 1):
        model.train()
        t0, tot = time.time(), {"gen": 0.0, "score": 0.0, "n": 0}
        for chunk in batches(data["train"], args.batch, shuffle=True):
            b = to(collate(chunk), device)
            r = model(b)
            loss = r["gen_loss"] + args.score_weight * r["score_loss"]
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            tot["gen"] += float(r["gen_loss"]) * len(chunk)
            tot["score"] += float(r["score_loss"]) * len(chunk)
            tot["n"] += len(chunk)
        rec = {"epoch": epoch, "train_gen": tot["gen"] / tot["n"],
               "train_score": tot["score"] / tot["n"], "secs": round(time.time() - t0, 1)}
        if data["val"] and (epoch % args.eval_every == 0 or epoch == args.epochs):
            rec.update({f"val_{k}": v for k, v in
                        evaluate(model, data["val"], device, args.samples, args.batch).items()})
            if rec["val_hit@5"] > best:
                best = rec["val_hit@5"]
                torch.save({"model": model.state_dict(), "args": vars(args), "epoch": epoch},
                           os.path.join(args.out, "best.pt"))
        torch.save({"model": model.state_dict(), "args": vars(args), "epoch": epoch},
                   os.path.join(args.out, "last.pt"))
        log.write(json.dumps(rec) + "\n")
        log.flush()
        history.append(rec)
        print(" ".join(f"{k}={v:.3f}" if isinstance(v, float) else f"{k}={v}"
                       for k, v in rec.items()), flush=True)
    return {"model": model, "history": history}


# ------------------------------------------------------------------ smoke

SMOKE_PROBLEMS = {
    "GRPa": "cnf(a1,axiom,f(f(X,Y),Z) = f(X,f(Y,Z))).\ncnf(a2,axiom,f(e,X) = X).\n"
            "cnf(a3,axiom,f(i(X),X) = e).\ncnf(g,negated_conjecture,f(a,i(a)) != e).\n",
    "LATa": "cnf(a1,axiom,j(X,X) = X).\ncnf(a2,axiom,m(X,X) = X).\ncnf(a3,axiom,j(X,m(X,Y)) = X).\n"
            "cnf(a4,axiom,m(X,j(X,Y)) = X).\ncnf(g,negated_conjecture,j(a,b) != j(b,a)).\n",
    "RNGa": "cnf(a1,axiom,p(X,z) = X).\ncnf(a2,axiom,t(X,p(Y,W)) = p(t(X,Y),t(X,W))).\n"
            "cnf(a3,axiom,p(X,n(X)) = z).\ncnf(g,negated_conjecture,t(a,z) != z).\n",
}


def smoke_data() -> dict:
    """Tiny dataset from SMOKE_PROBLEMS with a learnable rule: for each
    binary symbol f, f(X0, X0) helps and f(X0, X1) does not."""
    from nt.graph import build_graph, encode_abstraction, problem_clauses
    from nt.model.data import graph_from_row
    tmp = tempfile.mkdtemp()
    items = []
    for name, text in SMOKE_PROBLEMS.items():
        p = os.path.join(tmp, name + ".p")
        open(p, "w").write(text)
        g = build_graph(problem_clauses(p, tptp_root=""))
        gt = graph_from_row({"problem": name, "split": "train", "path": p, "graph": g.to_dict()})
        for flat in (True, False):
            ts = []
            binary = [s for s, a in zip(g.sym_names, g.sym_arity) if a == 2]
            for s in binary:
                for a, good in ((f"{s}(X0, X0)", True), (f"{s}(X0, X1)", False),
                                (f"{s}(X0, {s}(X1, X0))", False)):
                    ts.append(Target(encode_abstraction(a, g), a, good, 0.0, 1.0))
            n_good = sum(t.helps for t in ts)
            for t in ts:
                t.gen_weight = (1.0 / n_good) if t.helps else 0.0
                t.score_weight = 1.0 / len(ts)
            items.append(Item(gt, flat, ts))
    return {"train": items, "val": items}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--data", help="output directory of nt.dataset")
    ap.add_argument("--out", default="runs/default")
    ap.add_argument("--weight", default="f0.5", help="weight setting of the labels to use")
    ap.add_argument("--epochs", type=int, default=60)
    ap.add_argument("--batch", type=int, default=16, help="examples per batch")
    ap.add_argument("--hidden", type=int, default=128)
    ap.add_argument("--layers", type=int, default=4)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--score-weight", type=float, default=1.0)
    ap.add_argument("--no-names", action="store_true", help="no named symbol embeddings")
    ap.add_argument("--name-dropout", type=float, default=0.3)
    ap.add_argument("--samples", type=int, default=32, help="samples per example in validation")
    ap.add_argument("--eval-every", type=int, default=1)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--smoke", action="store_true", help="CPU self-test on built-in problems")
    args = ap.parse_args()

    if args.smoke:
        args.epochs, args.hidden, args.layers, args.batch = 150, 32, 2, 6
        args.samples, args.eval_every, args.device = 16, 50, "cpu"
        args.out = tempfile.mkdtemp()
        r = train(args, smoke_data())
        first, last = r["history"][0], r["history"][-1]
        ok = (last["train_gen"] < 0.5 * first["train_gen"] and last["val_valid"] == 1.0
              and last["val_hit@5"] >= 0.99 and last["val_auc"] > 0.9)
        print(f"\nsmoke test {'PASSED' if ok else 'FAILED'}: train_gen {first['train_gen']:.3f} -> "
              f"{last['train_gen']:.3f}, valid {last['val_valid']:.2f}, hit@5 {last['val_hit@5']:.2f}, "
              f"auc {last['val_auc']:.2f}")
        raise SystemExit(0 if ok else 1)

    if not args.data:
        ap.error("--data is required (or --smoke)")
    data = load(args.data, args.weight)
    train(args, data)


if __name__ == "__main__":
    main()
