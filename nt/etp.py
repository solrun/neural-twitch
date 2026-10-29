"""Unit-equality problems from the Equational Theories Project (ETP).

ETP settled all 4694 x 4694 implications between the equational laws of
order at most 4 over one binary operation. This module turns its true
implications into TPTP CNF problems (hypothesis law as an axiom, conclusion
law negated and skolemized) in the format of Twitch's ETP problems, so the
rest of the pipeline reads them unchanged.

Inputs (from ETP): the raw implication matrix exported from the ETP
implications explorer (export_raw_implications_<date>.csv, row = hypothesis,
column = conclusion, both 1-based equation numbers minus one) and the laws as
TPTP files (axioms/<n>.p, conjectures/<n>.p, as directories or .tar.gz).
Matrix codes (home_page/implications/script.js in the ETP repository):

   4 explicit proof true    -4 explicit proof false
   3 implicit proof true    -3 implicit proof false
   2/-2 explicit conjecture  1/-1 implicit conjecture  0 unknown

"Implicit" means derived by ETP's closure (transitivity, duality) from the
explicit results.

There are about 8.2M true implications, mostly redundant, so `build`
selects a set in tiers, using the equivalence classes of laws (A and B are
equivalent when each implies the other):

  degenerate  every law equivalent to x = y (equation 2), as "law => x = y".
              Such a law implies everything, so this one problem stands for
              its whole row.
  hasse       one problem per edge of the transitive reduction of the
              implication order on the remaining classes: the direct
              implications.
  closure     one problem per remaining pair of classes (P, Q) with P => Q:
              implications that ETP derived by chaining.
  equiv       within each class of two or more laws, a cycle a1 => a2 =>
              ... => ak => a1 (laws sorted by size), so every law is both a
              hypothesis and a conclusion once.

Implications into x = x (equation 1) are left out. For a pair of classes, the
representative laws are an explicitly proved pair if there is one, otherwise
the pair with the fewest operations in total (lowest numbers on ties).

  # once, from the ETP files (needs numpy and pandas)
  python -m nt.etp build --implications export_raw_implications_10_23_2026.csv \\
      --axioms axioms.tar.gz --conjectures conjectures.tar.gz --out-dir data/etp
  # problem files for some tiers, optionally one shard of them
  python -m nt.etp write data/etp --tiers degenerate,hasse --out-dir $TMPDIR/etp --shard 3/16
  # after a triage run (slurm/etp_triage.sbatch): trivial / label / hard per tier
  python -m nt.etp report out/etp/triage_*.jsonl --write-lists out/etp/lists
  # truth of existing ETP problem files (e.g. Twitch's ETP_UEQ_UNSAT)
  python -m nt.etp check --implications export_raw_implications_10_23_2026.csv \\
      $TWITCH_DIR/data/TPTP/ETP_UEQ_UNSAT

`write` reads only data/etp (laws.tsv and implications.jsonl.gz) and the
standard library, so it runs on the cluster without the ETP files. It writes
<out-dir>/ETP/ETP-<hyp>_<concl>.p and <out-dir>/manifest.jsonl, which
`nt.expand base` takes as input.
"""

from __future__ import annotations

import argparse
import collections
import gzip
import json
import os
import random
import re
import sys
import tarfile

TIERS = ("degenerate", "hasse", "closure", "equiv")
CODES = {4: "explicit_proof_true", 3: "implicit_proof_true",
         -4: "explicit_proof_false", -3: "implicit_proof_false",
         2: "explicit_conjecture_true", -2: "explicit_conjecture_false",
         1: "implicit_conjecture_true", -1: "implicit_conjecture_false", 0: "unknown"}
EQ_X_EQ_X, EQ_X_EQ_Y = 1, 2       # equation numbers of x = x and x = y
SKOLEM = {"X": "a", "Y": "b", "Z": "c", "W": "d", "U": "e", "V": "f"}  # as Twitch's files

_FOF = re.compile(r"^\s*fof\(equation(\d+)\s*,\s*(axiom|conjecture)\s*,\s*"
                  r"!\[([A-Z0-9_, ]+)\]\s*:\s*(.*)\)\.\s*$", re.S)
_VAR = re.compile(r"\b([A-Z][A-Za-z0-9_]*)\b")


# ------------------------------------------------------------------- laws

def _read_dir_or_tar(src: str) -> dict[int, str]:
    """{equation number: file text} from a directory or .tar(.gz) of n.p files."""
    out = {}
    if os.path.isdir(src):
        items = ((f, open(os.path.join(src, f)).read()) for f in os.listdir(src))
    else:
        tf = tarfile.open(src)
        items = ((os.path.basename(m.name), tf.extractfile(m).read().decode())
                 for m in tf.getmembers() if m.isfile())
    for name, text in items:
        m = re.fullmatch(r"(\d+)\.p", name)
        if m:
            out[int(m.group(1))] = text
    return out


def parse_law(text: str) -> tuple[int, str, list[str]]:
    """(equation number, 'lhs = rhs', variables) of an ETP fof file."""
    m = _FOF.match(text)
    if not m:
        raise ValueError(f"not an ETP law: {text[:120]!r}")
    lhs, sep, rhs = m.group(4).partition("=")
    if not sep:
        raise ValueError(f"no equation in {text[:120]!r}")
    return int(m.group(1)), f"{lhs.strip()} = {rhs.strip()}", \
        [v.strip() for v in m.group(3).split(",")]


def law_size(formula: str) -> int:
    """Number of operation applications (ETP's 'order')."""
    return formula.count("(")


def load_laws(path: str) -> dict[int, dict]:
    laws = {}
    with open(path) as f:
        header = f.readline().rstrip("\n").split("\t")
        for line in f:
            r = dict(zip(header, line.rstrip("\n").split("\t")))
            laws[int(r["id"])] = {"id": int(r["id"]), "class": int(r["class"]),
                                  "size": int(r["size"]), "formula": r["formula"]}
    return laws


def load_matrix(path: str):
    import numpy as np
    m = np.loadtxt(path, delimiter=",", dtype=np.int8)
    if m.ndim != 2 or m.shape[0] != m.shape[1]:
        raise SystemExit(f"{path}: expected a square matrix, got shape {m.shape}")
    return m


# ---------------------------------------------------------------- problems

def skolemize(formula: str) -> str:
    def sub(m):
        v = m.group(1)
        if v not in SKOLEM:
            raise ValueError(f"no Skolem constant for variable {v} in {formula!r}")
        return SKOLEM[v]
    return _VAR.sub(sub, formula)


def problem_name(hyp: int, concl: int) -> str:
    return f"ETP-{hyp}_{concl}"


def problem_text(row: dict, laws: dict[int, dict]) -> str:
    """TPTP CNF in the format of Twitch's ETP problems. The axiom is named
    after its law, so problems with the same hypothesis have identical
    axioms (one axiomatization for the dataset split)."""
    h, c = laws[row["hyp"]], laws[row["concl"]]
    lhs, _, rhs = skolemize(c["formula"]).partition(" = ")
    status = CODES.get(row["code"], str(row["code"]))
    return (f"% ETP implication: equation {h['id']} => equation {c['id']} ({status})\n"
            f"% tier {row['tier']}; hypothesis class {row['hyp_class']}, "
            f"conclusion class {row['concl_class']}\n"
            f"% {h['id']}: {h['formula']}\n"
            f"% {c['id']}: {c['formula']}\n"
            f"cnf(equation{h['id']}, axiom,\n    {h['formula']} ).\n\n"
            f"cnf(goal, negated_conjecture,\n    {lhs} != {rhs} ).\n")


# ------------------------------------------------------------------- build

def equivalence_classes(T) -> list[int]:
    """Class index per law (0-based), classes numbered by their smallest law."""
    import numpy as np
    E = T & T.T
    cls = -np.ones(len(T), dtype=int)
    k = 0
    for i in range(len(T)):
        if cls[i] < 0:
            cls[E[i]] = k
            k += 1
    return cls


def select(M, sizes) -> tuple[list[dict], dict]:
    """The tiered selection described in the module docstring."""
    import numpy as np
    import pandas as pd
    n = len(M)
    T = M > 0
    if (M == 0).any() or (np.abs(M) <= 2).any():
        print(f"warning: {int((np.abs(M) <= 2).sum())} unknown or conjectured entries "
              "are treated as false", file=sys.stderr)
    cls = equivalence_classes(T)
    sizes = np.asarray(sizes)
    deg_cls, triv_cls = cls[EQ_X_EQ_Y - 1], cls[EQ_X_EQ_X - 1]
    rows = []

    def row(a, b, tier):        # a, b 0-based
        return {"problem": problem_name(a + 1, b + 1), "hyp": int(a + 1), "concl": int(b + 1),
                "tier": tier, "code": int(M[a, b]), "hyp_class": int(cls[a]),
                "concl_class": int(cls[b]), "hyp_size": int(sizes[a]),
                "concl_size": int(sizes[b])}

    # degenerate: law => x = y
    for a in np.nonzero(cls == deg_cls)[0]:
        if a != EQ_X_EQ_Y - 1:
            rows.append(row(a, EQ_X_EQ_Y - 1, "degenerate"))

    # class-level order on the other classes
    a_idx, b_idx = np.nonzero(T)
    keep = (cls[a_idx] != cls[b_idx]) & (cls[a_idx] != deg_cls) & (cls[b_idx] != triv_cls)
    a_idx, b_idx = a_idx[keep], b_idx[keep]
    df = pd.DataFrame({"a": a_idx, "b": b_idx, "P": cls[a_idx], "Q": cls[b_idx],
                       "nonexplicit": M[a_idx, b_idx] != 4,
                       "total": sizes[a_idx] + sizes[b_idx]})
    reps = (df.sort_values(["P", "Q", "nonexplicit", "total", "a", "b"])
              .drop_duplicates(["P", "Q"]))
    k = int(cls.max()) + 1
    C = np.zeros((k, k), dtype=bool)
    C[reps.P.to_numpy(), reps.Q.to_numpy()] = True
    Ci = C.astype(np.float32)
    via = (Ci @ Ci) > 0          # P => R => Q for some R distinct from P and Q
    for a, b, P, Q in zip(reps.a, reps.b, reps.P, reps.Q):
        rows.append(row(a, b, "closure" if via[P, Q] else "hasse"))

    # equivalence cycles
    members = collections.defaultdict(list)
    for i in range(n):
        if cls[i] not in (deg_cls, triv_cls):
            members[cls[i]].append(i)
    for P, ms in members.items():
        if len(ms) > 1:
            ms = sorted(ms, key=lambda i: (sizes[i], i))
            for x, y in zip(ms, ms[1:] + ms[:1]):
                rows.append(row(x, y, "equiv"))

    assert all(M[r["hyp"] - 1, r["concl"] - 1] > 0 for r in rows)
    stats = {"laws": n, "classes": k, "degenerate_laws": int((cls == deg_cls).sum()),
             "true_offdiag": int(T.sum() - n), "explicit_true": int((M == 4).sum()),
             "class_implications": int(C.sum()),
             "tiers": dict(collections.Counter(r["tier"] for r in rows)),
             "explicit_by_tier": dict(collections.Counter(r["tier"] for r in rows
                                                          if r["code"] == 4))}
    return rows, stats


def cmd_build(args) -> None:
    ax = _read_dir_or_tar(args.axioms)
    cj = _read_dir_or_tar(args.conjectures)
    M = load_matrix(args.implications)
    n = len(M)
    if sorted(ax) != list(range(1, n + 1)) or sorted(cj) != list(range(1, n + 1)):
        raise SystemExit(f"expected laws 1..{n}; got {len(ax)} axioms, {len(cj)} conjectures")
    laws = {}
    for i in range(1, n + 1):
        num, formula, _ = parse_law(ax[i])
        num2, formula2, _ = parse_law(cj[i])
        if num != i or num2 != i or formula != formula2:
            raise SystemExit(f"axiom and conjecture files for equation {i} disagree")
        skolemize(formula)      # every variable has a constant
        laws[i] = {"id": i, "size": law_size(formula), "formula": formula}
    rows, stats = select(M, [laws[i]["size"] for i in range(1, n + 1)])
    cls = equivalence_classes(M > 0)
    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "laws.tsv"), "w") as f:
        f.write("id\tclass\tsize\tformula\n")
        for i in range(1, n + 1):
            f.write(f"{i}\t{cls[i - 1]}\t{laws[i]['size']}\t{laws[i]['formula']}\n")
    rows.sort(key=lambda r: (TIERS.index(r["tier"]), r["hyp"], r["concl"]))
    with gzip.open(os.path.join(args.out_dir, "implications.jsonl.gz"), "wt") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    stats["source"] = os.path.basename(args.implications)
    with open(os.path.join(args.out_dir, "stats.json"), "w") as f:
        json.dump(stats, f, indent=1)
    print(json.dumps(stats, indent=1))


# ------------------------------------------------------------------- write

def read_selection(data_dir: str) -> list[dict]:
    with gzip.open(os.path.join(data_dir, "implications.jsonl.gz"), "rt") as f:
        return [json.loads(l) for l in f if l.strip()]


def cmd_write(args) -> None:
    laws = load_laws(os.path.join(args.data_dir, "laws.tsv"))
    rows = read_selection(args.data_dir)
    tiers = set(args.tiers.split(",")) if args.tiers else set(TIERS)
    if tiers - set(TIERS):
        raise SystemExit(f"unknown tiers {sorted(tiers - set(TIERS))}; known: {TIERS}")
    rows = [r for r in rows if r["tier"] in tiers]
    if args.problems:
        want = {l.strip() for l in open(args.problems) if l.strip()}
        rows = [r for r in rows if r["problem"] in want]
    if args.sample:
        rows = random.Random(args.seed).sample(rows, min(args.sample, len(rows)))
    rows.sort(key=lambda r: r["problem"])
    if args.shard:
        k, n = (int(x) for x in args.shard.split("/"))
        if not 0 <= k < n:
            raise SystemExit(f"bad shard {args.shard!r}: need 0 <= K < N")
        rows = rows[k::n]
    pdir = os.path.join(args.out_dir, "ETP")
    os.makedirs(pdir, exist_ok=True)
    manifest = args.manifest or os.path.join(args.out_dir, "manifest.jsonl")
    os.makedirs(os.path.dirname(os.path.abspath(manifest)), exist_ok=True)
    with open(manifest, "w") as man:
        for r in rows:
            path = os.path.abspath(os.path.join(pdir, r["problem"] + ".p"))
            with open(path, "w") as f:
                f.write(problem_text(r, laws))
            man.write(json.dumps({"problem": r["problem"], "path": path, "domain": "ETP",
                                  **{k: r[k] for k in r if k != "problem"}}) + "\n")
    print(f"{len(rows)} problems ({dict(collections.Counter(r['tier'] for r in rows))}) "
          f"-> {pdir}, manifest {manifest}")


# ------------------------------------------------------------------- check

def cmd_check(args) -> None:
    """Look up each <hyp>_<concl>.p (or ETP-<hyp>_<concl>) in the matrix."""
    M = load_matrix(args.implications)
    counts, names = collections.Counter(), collections.defaultdict(list)
    for src in args.inputs:
        files = sorted(os.listdir(src)) if os.path.isdir(src) else [os.path.basename(src)]
        for f in files:
            m = re.fullmatch(r"(?:ETP-)?(\d+)_(\d+)\.p", f)
            if m:
                a, b = int(m.group(1)), int(m.group(2))
                code = CODES[int(M[a - 1, b - 1])]
                counts[code] += 1
                names[code].append(f)
    for code, k in counts.most_common():
        print(f"{k:7d}  {code}")
    if args.list:
        for code in args.list.split(","):
            for f in names.get(code, []):
                print(f"{code}\t{f}")


# ------------------------------------------------------------------ report

def triage_bucket(runs: list[dict], min_cps: int) -> str:
    """trivial: proved under every flattening setting run, each under min_cps;
    hard: proved under none; label: everything in between."""
    proved = [r for r in runs if r["status"] == "proved"]
    if not proved:
        return "hard"
    if len(proved) == len(runs) and max(r["cps"] for r in proved) < min_cps:
        return "trivial"
    return "label"


def cmd_report(args) -> None:
    sel = {r["problem"]: r for r in read_selection(args.data_dir)}
    runs = collections.defaultdict(list)
    for p in args.runs:
        for line in open(p):
            if line.strip():
                r = json.loads(line)
                if r["problem"] in sel and r["status"] != "error":
                    runs[r["problem"]].append(r)
    buckets = {p: triage_bucket(rs, args.min_cps) for p, rs in runs.items()}
    table = collections.Counter((sel[p]["tier"], b) for p, b in buckets.items())
    names = ("trivial", "label", "hard")
    print(f"{len(buckets)} problems with runs (of {len(sel)} selected); "
          f"trivial = proved under every setting with < {args.min_cps} CPs\n")
    print(f"{'tier':12s}" + "".join(f"{b:>9s}" for b in names) + "  hyp classes (label)")
    for t in TIERS:
        cls = {sel[p]["hyp_class"] for p, b in buckets.items()
               if b == "label" and sel[p]["tier"] == t}
        print(f"{t:12s}" + "".join(f"{table[t, b]:9d}" for b in names) + f"  {len(cls):9d}")
    flat = collections.Counter()
    for p, rs in runs.items():
        st = {r["flatten"]: r["status"] == "proved" for r in rs}
        if len(st) == 2 and st[True] != st[False]:
            flat["only flattening on" if st[True] else "only flattening off"] += 1
    if flat:
        print("\nproved under one flattening setting only:", dict(flat))
    if args.write_lists:
        os.makedirs(args.write_lists, exist_ok=True)
        for b in names:
            with open(os.path.join(args.write_lists, f"{b}.txt"), "w") as f:
                f.writelines(f"{p}\n" for p in sorted(buckets) if buckets[p] == b)
        print(f"\nlists -> {args.write_lists}/{{{','.join(names)}}}.txt")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="laws table and tiered selection from the ETP files")
    b.add_argument("--implications", required=True, help="export_raw_implications_*.csv")
    b.add_argument("--axioms", required=True, help="directory or .tar.gz of axioms/<n>.p")
    b.add_argument("--conjectures", required=True,
                   help="directory or .tar.gz of conjectures/<n>.p")
    b.add_argument("--out-dir", default="data/etp")
    w = sub.add_parser("write", help="problem files and a manifest for nt.expand base")
    w.add_argument("data_dir", nargs="?", default="data/etp")
    w.add_argument("--out-dir", required=True)
    w.add_argument("--tiers", default="", help=f"comma-separated subset of {','.join(TIERS)}")
    w.add_argument("--problems", default="", help="file with problem names to keep")
    w.add_argument("--sample", type=int, default=0, help="random N problems (fixed by --seed)")
    w.add_argument("--seed", type=int, default=0)
    w.add_argument("--shard", default="", metavar="K/N")
    w.add_argument("--manifest", default="",
                   help="manifest path (default <out-dir>/manifest.jsonl); give each shard "
                        "its own when shards share an --out-dir")
    c = sub.add_parser("check", help="truth of existing ETP problem files")
    c.add_argument("inputs", nargs="+", help="directories or .p files named <hyp>_<concl>.p")
    c.add_argument("--implications", required=True)
    c.add_argument("--list", default="", help="print the files with these codes")
    r = sub.add_parser("report", help="triage buckets from nt.expand base output")
    r.add_argument("runs", nargs="+", help="nt.expand base output (.jsonl)")
    r.add_argument("--data-dir", default="data/etp")
    r.add_argument("--min-cps", type=int, default=10_000,
                   help="below this a proof counts as trivial (nt.expand's DEFAULT_MIN_CPS)")
    r.add_argument("--write-lists", default="", metavar="DIR",
                   help="write trivial.txt, label.txt, hard.txt (for write --problems)")
    args = ap.parse_args()
    {"build": cmd_build, "write": cmd_write, "check": cmd_check,
     "report": cmd_report}[args.cmd](args)


if __name__ == "__main__":
    main()
