"""Analysis of the single-abstraction experiment (nt.single_runs).

Answers:
  0. What happened: run outcomes, budget hits, timeouts, errors.
  1. Do abstractions help on their own?
  2. Can a set's effect be predicted from its members' single effects?
  3. Are labels stable across weight settings and goal flattening?
  4. Do our CP ratios agree with Twitch's wall-clock ratios for the same set
     and configuration?

Ratios are cost with hints / cost without (lower is better), as in
data/labels.jsonl. A ratio <= 2/3 counts as helping and >= 1.5 as hurting;
in between is neutral, about the size of the CP change caused by switching
the housekeeping schedule alone (80% of problems moved by 0.7-1.4x).

Runs that hit the CP budget have ratio = budget / baseline CPs, a lower bound
on the true ratio; they always count as hurting. Runs that hit the wall-clock
cap, or whose baseline did not prove, have no ratio and are left out.

Usage:
    python -m nt.analyze_single out/single.jsonl data/labels.jsonl > single_analysis.md
    # also write per-abstraction labels for training:
    python -m nt.analyze_single out/single.jsonl data/labels.jsonl --labels-out data/single_labels.jsonl
"""

from __future__ import annotations

import argparse
import collections
import itertools
import json
import math
import re
import statistics as st

GOOD = 2 / 3
BAD = 1.5
CLASSES = ("helps", "neutral", "hurts")
_SETTING = re.compile(r"f([0-9.]+)_c([0-9.]+)_(flat|noflat)$")


def parse_setting(key: str) -> tuple[float, float, bool]:
    m = _SETTING.match(key)
    if not m:
        raise ValueError(f"unexpected setting key {key!r}")
    return float(m.group(1)), float(m.group(2)), m.group(3) == "flat"


def weight_name(key: str) -> str:
    f, c, _ = parse_setting(key)
    return f"cost {c:g}" if f == 0 else f"factor {f:g}"


def flat_name(key: str) -> str:
    return "flat" if parse_setting(key)[2] else "noflat"


def cls(ratio: float) -> str:
    return "helps" if ratio <= GOOD else "hurts" if ratio >= BAD else "neutral"


def pct(a: int, b: int) -> str:
    return f"{100 * a / b:.0f}%" if b else "-"


def ranks(xs: list[float]) -> list[float]:
    order = sorted(range(len(xs)), key=xs.__getitem__)
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2
        i = j + 1
    return r


def spearman(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3:
        return None
    rx, ry = ranks(xs), ranks(ys)
    mx, my = st.mean(rx), st.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else None


def fmt_rho(r: float | None) -> str:
    return "-" if r is None else f"{r:.2f}"


def class_table(pairs: list[tuple[str, str]], row_label: str, col_label: str) -> list[str]:
    t = collections.Counter(pairs)
    out = [f"| {row_label} \\ {col_label} | " + " | ".join(CLASSES) + " |",
           "|---|" + "---|" * len(CLASSES)]
    for a in CLASSES:
        out.append(f"| {a} | " + " | ".join(str(t[a, b]) for b in CLASSES) + " |")
    agree = sum(t[c, c] for c in CLASSES)
    flips = t["helps", "hurts"] + t["hurts", "helps"]
    out.append("")
    out.append(f"Same class: {agree} of {len(pairs)} ({pct(agree, len(pairs))}); "
               f"helps vs hurts contradictions: {flips} ({pct(flips, len(pairs))}).")
    return out


def twitch_ratios(labels_path: str) -> dict:
    """(problem, factor, cost, flatten, frozenset(abstractions)) -> Twitch ratio
    (minimum over repeats; timeouts censored at the time limit)."""
    out: dict = {}
    for line in open(labels_path):
        r = json.loads(line)
        if r["ratio"] is None:
            continue
        k = (r["problem"], r["hint_skel_factor"], r["hint_skel_cost"],
             r["flatten_goal"], frozenset(r["abstractions"]))
        out[k] = min(out.get(k, r["ratio"]), r["ratio"])
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("single")
    ap.add_argument("labels")
    ap.add_argument("--labels-out", help="write one row per (problem, setting, abstraction)")
    args = ap.parse_args()

    rows = [json.loads(l) for l in open(args.single) if l.strip()]
    settings = sorted({r["setting"] for r in rows},
                      key=lambda k: (not parse_setting(k)[2], parse_setting(k)[:2]))
    p = print

    p("# Single-abstraction experiment\n")
    schedules = collections.Counter(r.get("schedule", "?") for r in rows)
    p(f"{len(rows)} runs on {len({r['problem'] for r in rows})} problems; "
      f"schedule {', '.join(f'{s} ({n})' for s, n in schedules.items())}.\n")

    # ---- 0. outcomes -------------------------------------------------------
    p("## 0. Run outcomes\n")
    p("| kind | runs | proved | budget | timeout | error | ratio defined |")
    p("|---|---|---|---|---|---|---|")
    for kind in ("base", "set", "single"):
        rs = [r for r in rows if r["kind"] == kind]
        c = collections.Counter(r["status"] for r in rs)
        p(f"| {kind} | {len(rs)} | {c['proved']} | {c['budget']} | {c['timeout']} | "
          f"{c['error']} | {sum(r['ratio'] is not None for r in rs)} |")
    errs = [r for r in rows if r["status"] == "error"]
    if errs:
        p(f"\nFirst error ({errs[0]['problem']}, {errs[0]['setting']}):\n")
        p("```\n" + errs[0].get("error", "")[-800:] + "\n```")
    p()

    # index ratios
    set_ratio: dict = {}                      # (problem, setting) -> ratio
    set_abs: dict = {}                        # problem -> abstraction list
    single: dict = {}                         # (problem, setting, abstraction) -> ratio
    for r in rows:
        if r["kind"] == "set":
            set_abs[r["problem"]] = r["abstractions"]
            if r["ratio"] is not None:
                set_ratio[r["problem"], r["setting"]] = r["ratio"]
        elif r["kind"] == "single" and r["ratio"] is not None:
            single[r["problem"], r["setting"], r["abstractions"][0]] = r["ratio"]

    # ---- 1. singles alone --------------------------------------------------
    p("## 1. Do abstractions help on their own?\n")
    p("| setting | single runs | helps | neutral | hurts | median ratio | sets: helps |")
    p("|---|---|---|---|---|---|---|")
    for s in settings:
        xs = [v for (pr, ss, a), v in single.items() if ss == s]
        ys = [v for (pr, ss), v in set_ratio.items() if ss == s]
        c = collections.Counter(map(cls, xs))
        p(f"| {weight_name(s)}, {flat_name(s)} | {len(xs)} | {pct(c['helps'], len(xs))} | "
          f"{pct(c['neutral'], len(xs))} | {pct(c['hurts'], len(xs))} | "
          f"{st.median(xs):.2f} | {pct(sum(cls(y) == 'helps' for y in ys), len(ys))} |"
          if xs else f"| {weight_name(s)}, {flat_name(s)} | 0 | | | | | |")
    per_abs = collections.defaultdict(list)
    for (pr, s, a), v in single.items():
        per_abs[pr, a].append(v)
    any_help = sum(any(cls(v) == "helps" for v in vs) for vs in per_abs.values())
    all_help = sum(all(cls(v) == "helps" for v in vs) for vs in per_abs.values())
    p(f"\nOf {len(per_abs)} (problem, abstraction) pairs, {any_help} ({pct(any_help, len(per_abs))}) "
      f"help alone under at least one setting and {all_help} ({pct(all_help, len(per_abs))}) "
      f"under every setting they were run in.\n")

    # ---- 2. set vs members -------------------------------------------------
    p("## 2. Can a set's effect be predicted from its members?\n")
    p("For (problem, setting) pairs where the set and every member have a ratio. "
      "Error is |log2(predicted / actual)|: 1.0 means off by 2x.\n")
    preds = {"best single": [], "product of singles": [], "geometric mean": []}
    actual, synergy, interference, n_pairs = [], 0, 0, 0
    for (pr, s), y in set_ratio.items():
        members = set_abs.get(pr, [])
        if len(members) < 2:
            continue
        vs = [single.get((pr, s, a)) for a in members]
        if any(v is None for v in vs):
            continue
        n_pairs += 1
        actual.append(y)
        preds["best single"].append(min(vs))
        preds["product of singles"].append(math.prod(vs))
        preds["geometric mean"].append(math.exp(st.mean(math.log(v) for v in vs)))
        helps_alone = any(cls(v) == "helps" for v in vs)
        if cls(y) == "helps" and not helps_alone:
            synergy += 1
        if helps_alone and cls(y) != "helps":
            interference += 1
    if n_pairs:
        p("| predictor | Spearman with set ratio | median error (log2) | within 1.5x |")
        p("|---|---|---|---|")
        la = [math.log(v) for v in actual]
        for name, xs in preds.items():
            errs_ = [abs(math.log2(x / y)) for x, y in zip(xs, actual)]
            within = sum(e <= math.log2(1.5) for e in errs_)
            p(f"| {name} | {fmt_rho(spearman([math.log(x) for x in xs], la))} | "
              f"{st.median(errs_):.2f} | {pct(within, len(errs_))} |")
        p(f"\n{n_pairs} pairs. Set helps although no member helps alone: {synergy} "
          f"({pct(synergy, n_pairs)}). Some member helps alone but the set does not: "
          f"{interference} ({pct(interference, n_pairs)}).\n")
    else:
        p("No pairs with complete ratios.\n")

    # ---- 3. stability ------------------------------------------------------
    p("## 3. Are labels stable across settings?\n")
    by_pa = collections.defaultdict(dict)        # (problem, abstraction) -> {setting: ratio}
    for (pr, s, a), v in single.items():
        by_pa[pr, a][s] = v
    p("Single-abstraction labels, Spearman of log ratios between two settings over the "
      "same (problem, abstraction) pairs, and how often one says helps and the other "
      "hurts.\n")
    p("| setting A | setting B | pairs | Spearman | helps vs hurts |")
    p("|---|---|---|---|---|")
    for a, b in itertools.combinations(settings, 2):
        same_w = weight_name(a) == weight_name(b)
        same_f = flat_name(a) == flat_name(b)
        if not (same_w or same_f):
            continue                             # change one thing at a time
        pairs = [(d[a], d[b]) for d in by_pa.values() if a in d and b in d]
        if not pairs:
            continue
        flips = sum({cls(x), cls(y)} == {"helps", "hurts"} for x, y in pairs)
        p(f"| {weight_name(a)}, {flat_name(a)} | {weight_name(b)}, {flat_name(b)} | "
          f"{len(pairs)} | {fmt_rho(spearman([math.log(x) for x, _ in pairs], [math.log(y) for _, y in pairs]))} | "
          f"{flips} ({pct(flips, len(pairs))}) |")
    p()

    # ---- 4. Twitch agreement -----------------------------------------------
    p("## 4. Do our ratios agree with Twitch's?\n")
    tw = twitch_ratios(args.labels)
    matched = []
    for (pr, s), y in set_ratio.items():
        f, c, flat = parse_setting(s)
        k = (pr, f, c, flat, frozenset(set_abs.get(pr, [])))
        if k in tw:
            matched.append((tw[k], y, s))
    if matched:
        p(f"Full sets run by both, same weight setting and flattening: {len(matched)}. "
          f"Spearman of log ratios: "
          f"{fmt_rho(spearman([math.log(t) for t, _, _ in matched], [math.log(y) for _, y, _ in matched]))}.\n")
        p(*class_table([(cls(t), cls(y)) for t, y, _ in matched], "Twitch", "ours"), sep="\n")
        p()
        p("By setting:\n")
        p("| setting | pairs | Spearman | same class |")
        p("|---|---|---|---|")
        for s in settings:
            ms = [(t, y) for t, y, ss in matched if ss == s]
            if ms:
                same = sum(cls(t) == cls(y) for t, y in ms)
                p(f"| {weight_name(s)}, {flat_name(s)} | {len(ms)} | "
                  f"{fmt_rho(spearman([math.log(t) for t, _ in ms], [math.log(y) for _, y in ms]))} | "
                  f"{pct(same, len(ms))} |")
        p("\nTwitch's ratios are wall-clock times from a different Twee build and the "
          "CPU-time schedule; ours are CP counts under the allocation clock.\n")
    else:
        p("No full set matched a Twitch run with the same configuration.\n")

    if args.labels_out:
        with open(args.labels_out, "w") as out:
            n = 0
            for r in rows:
                if r["kind"] not in ("single", "set") or r["ratio"] is None:
                    continue
                f, c, flat = parse_setting(r["setting"])
                out.write(json.dumps({
                    "problem": r["problem"], "domain": r["problem"][:3], "kind": r["kind"],
                    "abstractions": r["abstractions"], "hint_skel_factor": f,
                    "hint_skel_cost": c, "flatten_goal": flat,
                    "schedule": r.get("schedule"), "status": r["status"],
                    "ratio": r["ratio"], "label": cls(r["ratio"]),
                    "lower_bound": r["status"] == "budget"}) + "\n")
                n += 1
        p(f"Wrote {n} labels to {args.labels_out}.")


if __name__ == "__main__":
    main()
