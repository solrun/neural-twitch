"""Graph encoder, pointer decoder and scorer.

Encoder: L rounds of typed message passing over the problem graph (every
relation in both directions, argument positions embedded on arg edges),
mean aggregation, residual update with LayerNorm per node type. Graph
context = mean of clause nodes and mean of symbol nodes.

Decoder: a GRU over the action sequence, initialised from the graph context
and the goal-flattening flag. Inputs are the previous action (the chosen
symbol node's embedding, or a variable-slot embedding) plus the number of
argument places still open. Each step scores every symbol node of the
problem (pointer) and the variable slots, masked by `nt.graph.valid_next`'s
rules: no variable at the root, only open or the next new slot, and near the
length limit only symbols that close the term.

Scorer: an MLP on the decoder state after the whole abstraction (and the
initial state), predicting whether the abstraction helps on this problem.
"""

from __future__ import annotations

import math

import torch
from torch import nn
import torch.nn.functional as F

from nt.model.data import (FUNC, MAX_ARITY, MAX_POS, MAX_SLOTS, NAME_BUCKETS, NODE_TYPES,
                           RELATIONS, VAR)


class Encoder(nn.Module):
    def __init__(self, hidden: int = 128, layers: int = 4, names: bool = True,
                 name_dropout: float = 0.3):
        super().__init__()
        H = hidden
        self.names, self.name_dropout = names, name_dropout
        self.eq_role = nn.Embedding(3, H)
        self.eq_neg = nn.Embedding(2, H)
        self.term_nargs = nn.Embedding(MAX_ARITY, H)
        self.var_init = nn.Parameter(torch.randn(H) * 0.1)
        self.sym_arity = nn.Embedding(MAX_ARITY, H)
        self.sym_name = nn.Embedding(NAME_BUCKETS, H) if names else None
        self.pos = nn.Embedding(MAX_POS, H)
        self.layers = nn.ModuleList()
        for _ in range(layers):
            self.layers.append(nn.ModuleDict({
                "fwd": nn.ModuleDict({n: nn.Linear(H, H) for n, _, _ in RELATIONS}),
                "rev": nn.ModuleDict({n: nn.Linear(H, H) for n, _, _ in RELATIONS}),
                "self": nn.ModuleDict({t: nn.Linear(H, H) for t in NODE_TYPES}),
                "norm": nn.ModuleDict({t: nn.LayerNorm(H) for t in NODE_TYPES}),
            }))

    def forward(self, b: dict) -> tuple[dict, torch.Tensor]:
        n = b["n"]
        dev = b["eq_feat"].device
        name = b["sym_name"]
        if self.training and self.name_dropout > 0:
            name = torch.where(torch.rand(name.shape, device=dev) < self.name_dropout,
                               torch.zeros_like(name), name)
        h = {
            "eq": self.eq_role(b["eq_feat"][:, 0]) + self.eq_neg(b["eq_feat"][:, 1]),
            "term": self.term_nargs(b["term_nargs"].clamp(max=MAX_ARITY - 1)),
            "var": self.var_init.unsqueeze(0).repeat(n["var"], 1),
            "sym": self.sym_arity(b["sym_arity"].clamp(max=MAX_ARITY - 1))
                   + (self.sym_name(name) if self.names else 0),
        }
        for layer in self.layers:
            agg = {t: torch.zeros_like(h[t]) for t in NODE_TYPES}
            cnt = {t: torch.zeros(h[t].shape[0], 1, device=dev) for t in NODE_TYPES}
            for rel, st, dt in RELATIONS:
                src, dst, pos = b["edges"][rel]
                if src.numel() == 0:
                    continue
                pe = self.pos(pos) if rel.startswith("arg") else 0
                ones = torch.ones(src.shape[0], 1, device=dev)
                agg[dt].index_add_(0, dst, layer["fwd"][rel](h[st][src]) + pe)
                cnt[dt].index_add_(0, dst, ones)
                agg[st].index_add_(0, src, layer["rev"][rel](h[dt][dst]) + pe)
                cnt[st].index_add_(0, src, ones)
            h = {t: layer["norm"][t](h[t] + F.relu(layer["self"][t](h[t])
                                                   + agg[t] / cnt[t].clamp(min=1)))
                 for t in NODE_TYPES}
        G = b["n_graphs"]

        def mean(x, idx):
            s = torch.zeros(G, x.shape[1], device=dev).index_add_(0, idx, x)
            c = torch.zeros(G, 1, device=dev).index_add_(0, idx, torch.ones(len(idx), 1, device=dev))
            return s / c.clamp(min=1)

        ctx = torch.cat([mean(h["eq"], b["eq_batch"]), mean(h["sym"], b["sym_batch"])], dim=1)
        return h, ctx


class Generator(nn.Module):
    def __init__(self, hidden: int = 128, layers: int = 4, names: bool = True,
                 name_dropout: float = 0.3):
        super().__init__()
        H = hidden
        self.H = H
        self.encoder = Encoder(H, layers, names, name_dropout)
        self.flat = nn.Embedding(2, H)
        self.init = nn.Sequential(nn.Linear(3 * H, H), nn.Tanh())
        self.start = nn.Parameter(torch.randn(H) * 0.1)
        self.slot_in = nn.Embedding(MAX_SLOTS, H)
        self.need_in = nn.Embedding(MAX_ARITY, H)
        self.sym_in = nn.Linear(H, H)
        self.gru = nn.GRU(H, H, batch_first=True)
        self.query = nn.Linear(H, H)
        self.sym_key = nn.Linear(H, H)
        self.slot_key = nn.Parameter(torch.randn(MAX_SLOTS, H) * 0.1)
        self.scorer = nn.Sequential(nn.Linear(2 * H, H), nn.ReLU(), nn.Linear(H, 1))

    # ------------------------------------------------------------ helpers
    def _h0(self, ctx, graph, flatten):
        return self.init(torch.cat([ctx[graph], self.flat(flatten)], dim=1))

    def _action_emb(self, h_sym, sym_pad_rows, kind, idx):
        """Embedding of actions [N, L] (kind, idx are per-problem indices)."""
        smax = sym_pad_rows.shape[1]
        glob = torch.gather(sym_pad_rows, 1, idx.clamp(max=smax - 1))
        func = self.sym_in(h_sym[glob])
        var = self.slot_in(idx.clamp(max=MAX_SLOTS - 1))
        return torch.where((kind == FUNC).unsqueeze(-1), func, var)

    def _logits(self, out, h_sym, sym_pad_rows, sym_mask_rows):
        """Raw symbol and slot logits for decoder outputs out [N, L, H]."""
        keys = self.sym_key(h_sym)[sym_pad_rows]                     # [N, S, H]
        q = self.query(out)
        scale = 1 / math.sqrt(self.H)
        sym = torch.einsum("nlh,nsh->nls", q, keys) * scale
        sym = sym.masked_fill(~sym_mask_rows.unsqueeze(1), float("-inf"))
        var = (q @ self.slot_key.T) * scale                          # [N, L, MAX_SLOTS]
        return sym, var

    # ------------------------------------------------------ teacher forcing
    def forward(self, b: dict) -> dict:
        h, ctx = self.encoder(b)
        g, kind, idx = b["t_graph"], b["t_kind"], b["t_idx"]
        N, L = kind.shape
        h0 = self._h0(ctx, g, b["t_flatten"])
        pad, mask = b["sym_pad"][g], b["sym_mask"][g]
        x = torch.cat([self.start.expand(N, 1, -1),
                       self._action_emb(h["sym"], pad, kind, idx)], dim=1)
        x = x + self.need_in(b["t_need"])
        out, _ = self.gru(x, h0.unsqueeze(0).contiguous())           # [N, L+1, H]
        sym, var = self._logits(out[:, :L], h["sym"], pad, mask)
        slots = torch.arange(MAX_SLOTS, device=kind.device)
        var_ok = slots.view(1, 1, -1) <= b["t_open"][:, :L].unsqueeze(-1)
        var_ok[:, 0, :] = False                                      # no variable at the root
        var = var.masked_fill(~var_ok, float("-inf"))
        logits = torch.cat([sym, var], dim=-1)                       # [N, L, S + MAX_SLOTS]
        gold = torch.where(kind == FUNC, idx, sym.shape[-1] + idx)
        valid = torch.arange(L, device=kind.device).unsqueeze(0) < b["t_len"].unsqueeze(1)
        nll = F.cross_entropy(logits.reshape(N * L, -1), gold.reshape(-1),
                              reduction="none").reshape(N, L)
        nll = (nll * valid).sum(1)                                   # per target
        summary = out[torch.arange(N, device=kind.device), b["t_len"]]
        score = self.scorer(torch.cat([summary, h0], dim=1)).squeeze(-1)
        n_items = b["n_graphs"]
        gen_loss = (nll * b["t_gen_w"]).sum() / n_items
        score_loss = (F.binary_cross_entropy_with_logits(score, b["t_helps"], reduction="none")
                      * b["t_score_w"]).sum() / n_items
        return {"gen_loss": gen_loss, "score_loss": score_loss, "nll": nll, "score": score}

    # ------------------------------------------------------------ sampling
    @torch.no_grad()
    def sample(self, b: dict, graph: torch.Tensor, flatten: torch.Tensor,
               max_len: int = 24, temperature: float = 1.0) -> tuple[list, torch.Tensor]:
        """Sample one abstraction per row (graph[i], flatten[i]).
        Returns (action lists, scorer logits)."""
        h, ctx = self.encoder(b)
        N = graph.shape[0]
        dev = graph.device
        h0 = self._h0(ctx, graph, flatten)
        pad, mask, ar = b["sym_pad"][graph], b["sym_mask"][graph], b["arity_pad"][graph]
        S = pad.shape[1]
        state = h0.unsqueeze(0).contiguous()
        need = torch.ones(N, dtype=torch.long, device=dev)
        n_open = torch.zeros(N, dtype=torch.long, device=dev)
        done = torch.zeros(N, dtype=torch.bool, device=dev)
        summarised = torch.zeros(N, dtype=torch.bool, device=dev)
        summary = torch.zeros(N, self.H, device=dev)
        x = self.start.expand(N, -1) + self.need_in(need.clamp(max=MAX_ARITY - 1))
        actions = [[] for _ in range(N)]
        slots = torch.arange(MAX_SLOTS, device=dev)
        for t in range(max_len + 1):
            out, state = self.gru(x.unsqueeze(1), state)
            o = out[:, 0]
            newly = done & ~summarised
            summary[newly] = o[newly]
            summarised |= newly
            if bool(done.all()):
                break
            sym, var = self._logits(o.unsqueeze(1), h["sym"], pad, mask)
            sym, var = sym[:, 0], var[:, 0]
            remaining = max_len - t                                  # actions left incl. this one
            sym_ok = mask & (need.unsqueeze(1) - 1 + ar <= remaining - 1)
            var_ok = (slots.unsqueeze(0) <= n_open.unsqueeze(1)) & (t > 0)
            logits = torch.cat([sym.masked_fill(~sym_ok, float("-inf")),
                                var.masked_fill(~var_ok, float("-inf"))], dim=1)
            logits = logits.masked_fill(done.unsqueeze(1), 0.0)      # finished rows: dummy
            choice = torch.multinomial(F.softmax(logits / temperature, dim=1), 1).squeeze(1)
            is_var = choice >= S
            kind = is_var.long()
            idx = torch.where(is_var, choice - S, choice)
            arity = torch.gather(ar, 1, idx.clamp(max=S - 1).unsqueeze(1)).squeeze(1)
            active = ~done
            need = torch.where(active, need - 1 + torch.where(is_var, torch.zeros_like(arity), arity),
                               need)
            n_open = torch.where(active & is_var & (idx == n_open), n_open + 1, n_open)
            for i in torch.nonzero(active).flatten().tolist():
                actions[i].append([int(kind[i]), int(idx[i])])
            done = done | (need == 0)
            emb = self._action_emb(h["sym"], pad, kind.unsqueeze(1), idx.unsqueeze(1))[:, 0]
            x = emb + self.need_in(need.clamp(min=0, max=MAX_ARITY - 1))
        score = self.scorer(torch.cat([summary, h0], dim=1)).squeeze(-1)
        return actions, score
