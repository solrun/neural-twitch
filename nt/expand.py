"""Grow the dataset: new problems and abstraction sets for nt.single_runs.

Three stages, each a subcommand:

  base       Run Twee without hints on a set of problems under both
             goal-flattening settings, and keep the proofs. Output rows have
             the calibration format, so they also serve as
             `nt.single_runs --calibration` input.
  hindsight  Turn lemmas from those proofs into new problems: the same axioms
             (includes kept), the lemma as the negated conjecture. Only
             lemmas stated over the axioms' own symbols are used, which
             excludes lemmas about the goal's constants and about symbols
             introduced by goal flattening.
  abstract   Run Twitch's local-abstraction extraction on each proof (proof
             terms -> Stitch -> Twitch's filters and expansion), canonicalise
             the result, and write the sets that `nt.single_runs --sets`
             reads.

Typical flow, for the ETP problems shipped with Twitch and for hindsight
subproblems of the TPTP problems:

  # proofs
  python -m nt.expand base $TWITCH_DIR/data/TPTP/ETP_UEQ_UNSAT --out out/expand/etp_base.jsonl
  python -m nt.expand base $TWITCH_DIR/data/TPTP/*_UEQ_UNSAT --exclude ETP --out out/expand/tptp_base.jsonl
  # hindsight subproblems, then their proofs
  python -m nt.expand hindsight out/expand/tptp_base.jsonl --out-dir out/expand/hindsight
  python -m nt.expand base out/expand/hindsight/manifest.jsonl --out out/expand/hs_base.jsonl
  # abstraction sets
  python -m nt.expand abstract out/expand/etp_base.jsonl out/expand/hs_base.jsonl --out out/expand/sets.jsonl
  # labels
  python -m nt.single_runs --sets out/expand/sets.jsonl out/single_expand.jsonl \\
      --calibration out/expand/etp_base.jsonl out/expand/hs_base.jsonl --max-cps 6000000

`abstract` needs Twitch's code (TWITCH_DIR) and its Python dependencies
stitch_core and python-dotenv.
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import random
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

from nt import tptp, twee
from nt.calibrate import UNLIMITED
from nt.single_runs import FLATTEN_MODES
from nt.terms import App, ParseError, canonical, normalize, parse, symbols
from nt.twee import Setting

DEFAULT_MIN_CPS = 10_000   # below this, housekeeping hardly runs and ratios say little


# ---------------------------------------------------------------- problems

def domain_of_dir(d: str) -> str:
    return os.path.basename(os.path.normpath(d)).split("_")[0]


def problem_id(stem: str, domain: str) -> str:
    """Problem names must start with their domain (analysis code uses the
    first three characters), so e.g. ETP's 1076_102 becomes ETP-1076_102."""
    return stem if stem.startswith(domain) else f"{domain}-{stem}"


def collect_problems(inputs: list[str]) -> list[dict]:
    """Problems from directories of .p files, single .p files, or manifest
    .jsonl files with rows {problem, path, domain}."""
    out = {}
    for inp in inputs:
        if not os.path.exists(inp):
            hint = (" (is TWITCH_DIR set? `source slurm/vera.env` sets it)"
                    if inp.startswith("/data/") else "")
            raise SystemExit(f"no such file or directory: {inp!r}{hint}")
        if inp.endswith(".jsonl"):
            for line in open(inp):
                if line.strip():
                    r = json.loads(line)
                    out[r["problem"]] = {"problem": r["problem"], "path": r["path"],
                                         "domain": r.get("domain", r["problem"][:3])}
        elif os.path.isdir(inp):
            dom = domain_of_dir(inp)
            for p in sorted(glob.glob(os.path.join(inp, "*.p"))):
                pid = problem_id(os.path.basename(p)[:-2], dom)
                out[pid] = {"problem": pid, "path": os.path.abspath(p), "domain": dom}
        elif inp.endswith(".p"):
            dom = domain_of_dir(os.path.dirname(inp) or ".")
            pid = problem_id(os.path.basename(inp)[:-2], dom)
            out[pid] = {"problem": pid, "path": os.path.abspath(inp), "domain": dom}
        else:
            raise SystemExit(f"don't know what to do with {inp!r}")
    return [out[k] for k in sorted(out)]


def read_rows(paths: list[str]) -> list[dict]:
    return [json.loads(l) for p in paths for l in open(p) if l.strip()]


# -------------------------------------------------------------------- base

def _base_job(prob, flatten, proof_dir, wall_timeout, schedule):
    tag = "flat" if flatten else "noflat"
    proof = os.path.join(proof_dir, prob["domain"], f"{prob['problem']}_{tag}.txt.gz")
    r = twee.run(prob["path"], [], Setting(flatten_goal=flatten), UNLIMITED, wall_timeout,
                 schedule=schedule, proof_path=proof)
    return {**prob, "flatten": flatten, "rep": 0, "schedule": schedule, **r.to_dict(),
            "proof": proof if r.status == "proved" else None}


def finished_runs(path: str, schedule: str) -> set:
    """(problem, flatten) pairs already in a base output file, for --resume.
    Drops a truncated last line (a job killed mid-write) and runs that ended
    in an error, rewriting the file without them, so those are run again."""
    keep, done, dropped = [], set(), 0
    for line in open(path):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            dropped += 1
            continue
        if r["status"] == "error" or r.get("schedule") != schedule:
            dropped += 1
            continue
        keep.append(line if line.endswith("\n") else line + "\n")
        done.add((r["problem"], r["flatten"]))
    if dropped:
        with open(path, "w") as f:
            f.writelines(keep)
        print(f"dropped {dropped} truncated, failed or other-schedule rows from {path}")
    return done


def cmd_base(args) -> None:
    probs = collect_problems(args.inputs)
    if args.exclude:
        skip = set(args.exclude.split(","))
        probs = [p for p in probs if p["domain"] not in skip]
    if args.sample:
        # a fixed random subset: --limit takes the first problems by name,
        # which for ETP all share the same hypothesis law
        probs = sorted(random.Random(args.seed).sample(probs, min(args.sample, len(probs))),
                       key=lambda p: p["problem"])
    if args.limit:
        probs = probs[:args.limit]
    probs = twee.select_shard(probs, args.shard)
    modes = FLATTEN_MODES[args.flatten]
    jobs = [(p, f) for p in probs for f in modes]
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    mode = "w"
    if args.resume and os.path.exists(args.out):
        done = finished_runs(args.out, args.schedule)
        before = len(jobs)
        jobs = [(p, f) for p, f in jobs if (p["problem"], f) not in done]
        print(f"resuming: {before - len(jobs)} runs already in {args.out}, "
              f"{len(jobs)} to go", flush=True)
        mode = "a"
    print(f"{len(probs)} problems x {len(modes)} flattening settings, {len(jobs)} runs, wall cap "
          f"{args.wall_timeout}s, schedule {args.schedule}, {args.workers} workers", flush=True)
    t0, counts = time.monotonic(), collections.Counter()
    with open(args.out, mode) as out, ProcessPoolExecutor(args.workers) as ex:
        futs = [ex.submit(_base_job, p, f, args.proof_dir, args.wall_timeout, args.schedule)
                for p, f in jobs]
        for i, fut in enumerate(as_completed(futs), 1):
            r = fut.result()
            counts[r["status"]] += 1
            out.write(json.dumps(r) + "\n")
            out.flush()
            if i % 50 == 0 or i == len(futs):
                print(f"[{time.monotonic() - t0:6.0f}s] {i}/{len(futs)} {dict(counts)}", flush=True)
    errs = [r for r in read_rows([args.out]) if r["status"] == "error"]
    if errs:
        print(f"{len(errs)} runs failed. First error ({errs[0]['problem']}):\n"
              f"{errs[0]['error'][-1500:]}")


# --------------------------------------------------------------- hindsight

_LEMMA = re.compile(r"^Lemma (\d+):(.*)$")


def parse_lemmas(text: str) -> list[tuple[int, str, str]]:
    """(number, lhs, rhs) of every lemma in a Twee proof, in proof order.
    A lemma's statement may wrap over several lines before 'Proof:'."""
    out, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        m = _LEMMA.match(lines[i])
        if not m:
            i += 1
            continue
        parts = [m.group(2)]
        i += 1
        while i < len(lines) and lines[i].strip() != "Proof:" and not _LEMMA.match(lines[i]):
            parts.append(lines[i])
            i += 1
        stmt = " ".join(" ".join(parts).split()).rstrip(".").strip()
        sides = tptp.equation_sides(stmt)
        if sides and not sides[2]:
            out.append((int(m.group(1)), sides[0], sides[1]))
    return out


def equation_key(lhs, rhs) -> str:
    """Canonical form of an unoriented equation, up to variable renaming."""
    a = str(normalize(App("=", (lhs, rhs))))
    b = str(normalize(App("=", (rhs, lhs))))
    return min(a, b)


def hindsight_candidates(problem_path: str, proofs: list[str], per_problem: int,
                         tptp_root: str | None) -> tuple[list[dict], collections.Counter]:
    """Up to per_problem distinct lemmas from the given proofs, latest in
    the proof first, that are usable as standalone goals."""
    axioms = tptp.axiom_statements(problem_path, tptp_root)
    sig = tptp.signature(axioms)
    known = set()
    for st in axioms:
        sides = tptp.equation_sides(st.formula)
        if sides and not sides[2]:
            try:
                known.add(equation_key(parse(sides[0]), parse(sides[1])))
            except ParseError:
                pass
    why = collections.Counter()
    # latest lemmas first, alternating between the proofs (one per flattening
    # setting) so that both contribute
    ranked = []
    for pi, proof in enumerate(proofs):
        for rank, lem in enumerate(reversed(parse_lemmas(twee.read_text(proof)))):
            ranked.append((rank, pi, lem))
    ranked.sort(key=lambda x: (x[0], x[1]))
    picked, seen = [], set()
    for _, pi, (num, ls, rs) in ranked:
        if len(picked) >= per_problem:
            break
        if "$" in ls + rs:
            why["encoding symbol"] += 1
            continue
        try:
            l, r = parse(ls), parse(rs)
        except ParseError:
            why["unparsable"] += 1
            continue
        used = dict(symbols(l)) | dict(symbols(r))
        if any(sig.get(f) != n for f, n in used.items()):
            why["symbol outside the axioms"] += 1
            continue
        if l == r:
            why["trivial"] += 1
            continue
        key = equation_key(l, r)
        if key in known:
            why["is an axiom"] += 1
            continue
        if key in seen:
            why["duplicate"] += 1
            continue
        seen.add(key)
        picked.append({"lemma_number": num, "lhs": ls, "rhs": rs, "key": key,
                       "proof": proofs[pi]})
    why["picked"] += len(picked)
    return picked, why


def cmd_hindsight(args) -> None:
    rows = read_rows(args.base)
    by_problem = collections.defaultdict(list)
    for r in rows:
        if r["status"] == "proved" and r.get("proof") and r["cps"] >= args.min_source_cps:
            by_problem[r["problem"]].append(r)
    os.makedirs(args.out_dir, exist_ok=True)
    manifest = os.path.join(args.out_dir, "manifest.jsonl")
    why_total, n = collections.Counter(), 0
    with open(manifest, "w") as man:
        for prob in sorted(by_problem):
            rs = sorted(by_problem[prob], key=lambda r: not r["flatten"])
            src = rs[0]
            try:
                cands, why = hindsight_candidates(src["path"], [r["proof"] for r in rs],
                                                  args.per_problem, args.tptp_root)
            except FileNotFoundError as e:
                print(f"{prob}: {e}", file=sys.stderr)
                why_total["missing include"] += 1
                continue
            why_total.update(why)
            for k, c in enumerate(cands, 1):
                pid = f"{prob}_hs{k}"
                path = os.path.abspath(os.path.join(args.out_dir, src["domain"], f"{pid}.p"))
                comment = (f"Hindsight subproblem of {prob}: Lemma {c['lemma_number']} of its "
                           f"proof\n({os.path.basename(c['proof'])}), as a standalone goal.\n"
                           f"{c['lhs']} = {c['rhs']}")
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w") as f:
                    f.write(tptp.with_goal(src["path"], c["lhs"], c["rhs"], comment,
                                           tptp_root=args.tptp_root))
                man.write(json.dumps({"problem": pid, "path": path, "domain": src["domain"],
                                      "source": prob, "lemma_number": c["lemma_number"],
                                      "lemma": f"{c['lhs']} = {c['rhs']}",
                                      "source_proof": c["proof"]}) + "\n")
                n += 1
    print(f"{len(by_problem)} source problems with proofs >= {args.min_source_cps} CPs; "
          f"wrote {n} subproblems to {args.out_dir}")
    print("lemma filter:", dict(why_total.most_common()))
    print(f"manifest: {manifest}")


# ---------------------------------------------------------------- abstract

_TWITCH = {}


def _load_twitch(twitch_dir: str) -> None:
    """Import Twitch's extraction code (no licence file in that repo, so it
    is used from a clone rather than copied here)."""
    if _TWITCH:
        return
    src = os.path.join(twitch_dir, "src")
    if not os.path.isdir(os.path.join(src, "stitch")):
        raise SystemExit(f"Twitch sources not found under {src}; set TWITCH_DIR")
    sys.path.insert(0, src)
    import utils as tw_utils                                     # noqa: E402
    from stitch.Abstractions import Stitch_Abstractions        # noqa: E402
    _TWITCH.update(utils=tw_utils, stitch=Stitch_Abstractions)


def twitch_abstractions(proof_text: str, iterations: int, max_arity: int) -> tuple[list[str], int]:
    """Twitch's local_abs extraction on one proof: (canonical abstraction
    bodies, number of raw Stitch abstractions)."""
    u = _TWITCH["utils"]
    terms = u.extract_terms(proof_text, {"onlyProofTerms": True, "onlyPeakTerms": False})
    if not terms:
        return [], 0
    raw = _TWITCH["stitch"](terms, iterations, max_arity).fo_abstractions
    expanded = u.expand_abstractions(
        u.filter_out_uninteresting(u.filter_out_higer_order_abstractions(raw)))
    out = []
    for a in expanded:
        c = canonical(a)
        if c is not None and c not in out:
            out.append(c)
    return out, len(raw)


def _abstract_job(row, twitch_dir, iterations, max_arity):
    try:
        _load_twitch(twitch_dir)
        abstr, n_raw = twitch_abstractions(twee.read_text(row["proof"]), iterations, max_arity)
        return row, abstr, n_raw, ""
    except SystemExit:
        raise
    except Exception as e:                     # Stitch or parsing failure on one proof
        return row, [], 0, f"{type(e).__name__}: {e}"


def cmd_abstract(args) -> None:
    rows = read_rows(args.base)
    best = {}
    prefer = args.prefer_flatten == "on"
    for r in rows:
        if r["status"] != "proved" or not r.get("proof") or r["cps"] < args.min_cps:
            continue
        cur = best.get(r["problem"])
        if cur is None or (r["flatten"] == prefer and cur["flatten"] != prefer):
            best[r["problem"]] = r
    todo = [best[k] for k in sorted(best)]
    print(f"{len(todo)} problems with a proof needing >= {args.min_cps} CPs; Stitch "
          f"iterations {args.iterations}, max arity {args.max_arity}", flush=True)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    stats = collections.Counter()
    with open(args.out, "w") as out, ProcessPoolExecutor(args.workers) as ex:
        futs = [ex.submit(_abstract_job, r, args.twitch_dir, args.iterations, args.max_arity)
                for r in todo]
        for fut in as_completed(futs):
            r, abstr, n_raw, err = fut.result()
            if err:
                stats["failed"] += 1
                print(f"{r['problem']}: {err}", file=sys.stderr)
                continue
            if not abstr:
                stats["no valid abstractions"] += 1
                continue
            stats["sets"] += 1
            out.write(json.dumps({"problem": r["problem"], "path": r["path"],
                                  "domain": r["domain"], "abstractions": abstr,
                                  "n_raw": n_raw, "source_flatten": r["flatten"],
                                  "base_cps": r["cps"], "iterations": args.iterations,
                                  "max_arity": args.max_arity}) + "\n")
    print(dict(stats), f"-> {args.out}")


# -------------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("base", help="baseline runs with proofs")
    b.add_argument("inputs", nargs="+", help="problem directories, .p files or manifest .jsonl files")
    b.add_argument("--out", required=True)
    b.add_argument("--proof-dir", default="out/expand/proofs")
    b.add_argument("--exclude", default="", help="comma-separated domains to skip")
    b.add_argument("--flatten", choices=FLATTEN_MODES, default="both")
    b.add_argument("--wall-timeout", type=float, default=1000.0)
    b.add_argument("--schedule", default=twee.DEFAULT_SCHEDULE)
    b.add_argument("--workers", type=int, default=twee.default_workers())
    b.add_argument("--limit", type=int, default=0, help="first N problems by name")
    b.add_argument("--sample", type=int, default=0, help="random N problems (fixed by --seed)")
    b.add_argument("--seed", type=int, default=0)
    b.add_argument("--shard", default="", metavar="K/N")
    b.add_argument("--resume", action="store_true",
                   help="keep finished runs in --out and run only the rest")
    b.set_defaults(func=cmd_base)

    h = sub.add_parser("hindsight", help="lemmas from proofs as new problems")
    h.add_argument("base", nargs="+", help="output of the base stage")
    h.add_argument("--out-dir", required=True)
    h.add_argument("--per-problem", type=int, default=5,
                   help="lemmas per source problem, latest in the proof first")
    h.add_argument("--min-source-cps", type=int, default=DEFAULT_MIN_CPS,
                   help="only use proofs that needed at least this many CPs")
    h.add_argument("--tptp-root", default=os.environ.get("TPTP_ROOT"))
    h.set_defaults(func=cmd_hindsight)

    a = sub.add_parser("abstract", help="Twitch/Stitch abstraction sets from proofs")
    a.add_argument("base", nargs="+", help="output of the base stage")
    a.add_argument("--out", required=True)
    a.add_argument("--min-cps", type=int, default=DEFAULT_MIN_CPS,
                   help="only problems whose proof needed at least this many CPs")
    a.add_argument("--prefer-flatten", choices=["on", "off"], default="on",
                   help="which setting's proof to abstract when both proved")
    a.add_argument("--iterations", type=int, default=10, help="Stitch iterations (Twitch: 10)")
    a.add_argument("--max-arity", type=int, default=10, help="Stitch max arity (Twitch: 10)")
    a.add_argument("--twitch-dir", default=os.environ.get("TWITCH_DIR", ""))
    a.add_argument("--workers", type=int, default=twee.default_workers())
    a.set_defaults(func=cmd_abstract)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
