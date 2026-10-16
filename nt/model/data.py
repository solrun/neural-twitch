"""Load data/dataset (nt.dataset) into tensors and collate batches.

An item is one (problem, flattening) example with its labelled single
abstractions. A batch concatenates the problems' graphs (node indices
offset per type, as in PyG) and lists every target abstraction with the
batch position of its graph.
"""

from __future__ import annotations

import gzip
import json
import zlib
from dataclasses import dataclass

import torch

RELATIONS = [          # (edge list name in the graph file, source type, destination type)
    ("side_term", "eq", "term"),
    ("side_var", "eq", "var"),
    ("head", "term", "sym"),
    ("arg_term", "term", "term"),
    ("arg_var", "term", "var"),
]
NODE_TYPES = ("eq", "term", "var", "sym")
NAME_BUCKETS = 1024      # hashed symbol names; bucket 0 = unknown / dropped
MAX_ARITY = 8            # arity / argument-count features are capped here
MAX_POS = 8              # argument positions are capped here
MAX_SLOTS = 8            # variable slots the decoder can open
FUNC, VAR = 0, 1


def name_bucket(name: str) -> int:
    return 1 + zlib.crc32(name.encode()) % (NAME_BUCKETS - 1)


@dataclass
class GraphT:
    """One problem graph as tensors."""
    problem: str
    path: str
    split: str
    sym_names: list
    sym_arity: torch.Tensor      # [S]
    sym_name: torch.Tensor       # [S] hashed name bucket
    eq_feat: torch.Tensor        # [E, 2] role, negated
    term_nargs: torch.Tensor     # [T]
    n_var: int
    edges: dict                  # name -> (src [K], dst [K], pos [K] or None)

    def n(self, kind: str) -> int:
        return {"eq": len(self.eq_feat), "term": len(self.term_nargs),
                "var": self.n_var, "sym": len(self.sym_arity)}[kind]


def graph_from_row(r: dict) -> GraphT:
    g = r["graph"]
    edges = {}
    for name, _, _ in RELATIONS:
        e = g["edges"].get(name, [[], []])
        src = torch.tensor(e[0], dtype=torch.long)
        dst = torch.tensor(e[1], dtype=torch.long)
        pos = torch.tensor(e[2], dtype=torch.long).clamp(max=MAX_POS - 1) if len(e) > 2 else None
        edges[name] = (src, dst, pos)
    return GraphT(
        problem=r["problem"], path=r.get("path", ""), split=r["split"],
        sym_names=g["sym_names"],
        sym_arity=torch.tensor(g["sym_arity"], dtype=torch.long),
        sym_name=torch.tensor([name_bucket(n) for n in g["sym_names"]], dtype=torch.long),
        eq_feat=torch.tensor(g["eq_feat"], dtype=torch.long).reshape(-1, 2),
        term_nargs=torch.tensor([t[0] for t in g["term_feat"]], dtype=torch.long),
        n_var=g["n_var"], edges=edges)


@dataclass
class Target:
    actions: list          # [[kind, index], ...]
    abstraction: str
    helps: bool            # label == "helps"
    gen_weight: float      # weight in the generation loss (0 if it does not help)
    score_weight: float    # weight in the scorer loss


@dataclass
class Item:
    graph: GraphT
    flatten: bool
    targets: list          # [Target]


def load(dataset_dir: str, weight: str = "f0.5", splits=("train", "val", "test")) -> dict:
    """{split: [Item]} plus {"graphs": {problem: GraphT}}.

    Generation weights follow the plan: a helpful abstraction gets 1/(1+r),
    normalised to sum 1 per example, so problems with many helpful
    abstractions do not dominate. Scorer weights are uniform per example,
    also summing to 1. Wall-clock timeouts (ratio None) are negatives."""
    graphs = {}
    with gzip.open(f"{dataset_dir}/graphs.jsonl.gz", "rt") as f:
        for line in f:
            r = json.loads(line)
            graphs[r["problem"]] = graph_from_row(r)
    out = {s: [] for s in splits}
    with gzip.open(f"{dataset_dir}/examples.jsonl.gz", "rt") as f:
        for line in f:
            r = json.loads(line)
            if r["split"] not in out or (weight and r["weight"] != weight):
                continue
            # the decoder has MAX_SLOTS variable slots and targets are capped at 64 actions
            ts = [t for t in r["singles"] if len(t["actions"]) <= 64
                  and max((i for k, i in t["actions"] if k == VAR), default=-1) < MAX_SLOTS]
            if not ts or r["problem"] not in graphs:
                continue
            gw = [1.0 / (1.0 + t["ratio"]) if t["label"] == "helps" and t["ratio"] else 0.0
                  for t in ts]
            gsum = sum(gw) or 1.0
            out[r["split"]].append(Item(graphs[r["problem"]], r["flatten"], [
                Target(t["actions"], t["abstraction"], t["label"] == "helps",
                       w / gsum, 1.0 / len(ts))
                for t, w in zip(ts, gw)]))
    out["graphs"] = graphs
    return out


def prefix_state(actions: list, arity: list) -> tuple[list, list]:
    """For each decoder input position 0..L (before predicting action t+1,
    and after the last action): open argument places ('need') and open
    variable slots."""
    need, n_open = [1], [0]
    nd, no = 1, 0
    for kind, idx in actions:
        nd -= 1
        if kind == FUNC:
            nd += arity[idx]
        elif idx == no:
            no += 1
        need.append(nd)
        n_open.append(no)
    return need, n_open


def collate_graphs(graphs: list) -> dict:
    """Concatenate graphs, offsetting node indices per type."""
    off = {k: 0 for k in NODE_TYPES}
    offsets = []
    eq_feat, term_nargs, sym_arity, sym_name = [], [], [], []
    eq_batch, sym_batch, var_count = [], [], 0
    edges = {name: ([], [], []) for name, _, _ in RELATIONS}
    for gi, g in enumerate(graphs):
        offsets.append(dict(off))
        eq_feat.append(g.eq_feat)
        term_nargs.append(g.term_nargs)
        sym_arity.append(g.sym_arity)
        sym_name.append(g.sym_name)
        eq_batch.append(torch.full((g.n("eq"),), gi, dtype=torch.long))
        sym_batch.append(torch.full((g.n("sym"),), gi, dtype=torch.long))
        for name, st, dt in RELATIONS:
            src, dst, pos = g.edges[name]
            edges[name][0].append(src + off[st])
            edges[name][1].append(dst + off[dt])
            edges[name][2].append(pos if pos is not None else torch.zeros_like(src))
        for k in NODE_TYPES:
            off[k] += g.n(k)
    cat = lambda xs, dt=torch.long: torch.cat(xs) if xs else torch.zeros(0, dtype=dt)
    # padded symbol index per graph, for the pointer
    smax = max(g.n("sym") for g in graphs)
    sym_pad = torch.zeros(len(graphs), smax, dtype=torch.long)
    sym_mask = torch.zeros(len(graphs), smax, dtype=torch.bool)
    arity_pad = torch.zeros(len(graphs), smax, dtype=torch.long)
    for gi, g in enumerate(graphs):
        s = g.n("sym")
        sym_pad[gi, :s] = torch.arange(s) + offsets[gi]["sym"]
        sym_mask[gi, :s] = True
        arity_pad[gi, :s] = g.sym_arity
    return {
        "n": dict(off), "eq_feat": torch.cat(eq_feat).reshape(-1, 2),
        "term_nargs": cat(term_nargs), "sym_arity": cat(sym_arity), "sym_name": cat(sym_name),
        "eq_batch": cat(eq_batch), "sym_batch": cat(sym_batch), "n_graphs": len(graphs),
        "edges": {k: (cat(v[0]), cat(v[1]), cat(v[2])) for k, v in edges.items()},
        "sym_pad": sym_pad, "sym_mask": sym_mask, "arity_pad": arity_pad,
    }


def collate(items: list) -> dict:
    """A training batch: graphs plus teacher-forcing tensors for every target.

    For target i with L actions, decoder inputs are positions 0..L (start
    token, then each action); outputs at 0..L-1 predict actions 1..L and the
    output at L is the scorer's summary."""
    batch = collate_graphs([it.graph for it in items])
    tg, flat, acts, lens = [], [], [], []
    gen_w, score_w, helps = [], [], []
    for gi, it in enumerate(items):
        for t in it.targets:
            tg.append(gi)
            flat.append(int(it.flatten))
            acts.append(t.actions)
            lens.append(len(t.actions))
            gen_w.append(t.gen_weight)
            score_w.append(t.score_weight)
            helps.append(float(t.helps))
    n, lmax = len(acts), max(lens)
    kind = torch.zeros(n, lmax, dtype=torch.long)
    idx = torch.zeros(n, lmax, dtype=torch.long)
    need = torch.zeros(n, lmax + 1, dtype=torch.long)
    n_open = torch.zeros(n, lmax + 1, dtype=torch.long)
    for i, a in enumerate(acts):
        g = items[tg[i]].graph
        nd, no = prefix_state(a, g.sym_arity.tolist())
        kind[i, :len(a)] = torch.tensor([x[0] for x in a])
        idx[i, :len(a)] = torch.tensor([x[1] for x in a])
        need[i, :len(a) + 1] = torch.tensor(nd)
        n_open[i, :len(a) + 1] = torch.tensor(no)
    batch.update({
        "t_graph": torch.tensor(tg), "t_flatten": torch.tensor(flat),
        "t_kind": kind, "t_idx": idx, "t_len": torch.tensor(lens),
        "t_need": need.clamp(max=MAX_ARITY - 1), "t_open": n_open,
        "t_gen_w": torch.tensor(gen_w), "t_score_w": torch.tensor(score_w),
        "t_helps": torch.tensor(helps),
    })
    return batch


def to(batch: dict, device) -> dict:
    out = {}
    for k, v in batch.items():
        if isinstance(v, torch.Tensor):
            out[k] = v.to(device)
        elif isinstance(v, dict):
            out[k] = {kk: (tuple(x.to(device) for x in vv) if isinstance(vv, tuple)
                           else vv) for kk, vv in v.items()}
        else:
            out[k] = v
    return out
