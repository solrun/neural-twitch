"""nt.expand mine: rules from Twee's search output as new problems.

The log format follows Twee's message printing (src/Twee.hs, `Pretty
(Message f)` and `Pretty (Active f)`; executable/SequentialMain.hs prints
each message with `say` unless --quiet).
"""

import json
import stat
import subprocess
import sys

from nt import twee
from nt.expand import parse_search_log, pick, reprove_band, split_rule

LOG = """Here is the input problem:
  Axiom 1 (assoc): f(f(X, Y), Z) = f(X, f(Y, Z)).
  Axiom 2 (unit): f(e, X) = X.
  Goal 1 (goal): f(a, b) = f(b, a).

1. f(f(X, Y), Z) -> f(X, f(Y, Z))
2. f(e, X) -> X
  (12 queued critical pairs)
3. f(X, f(e, Y)) -> f(X, Y)
(0.5) 4. f(i(X), f(X, Y)) -> Y
  (delete rule 3)
  (simplifying rules with respect to one another...)
5. f(X, f(Y, f(Z, f(W,
     V)))) <-> f(Y, f(X, f(Z, f(W, V))))
6. f(a, X) = f(X, a)
7. f(X, i(X)) -> e
  (hard) f(X, Y) = f(Y, X)

Gave up on reaching the given resource limit.
Here is the final rewrite system:
  f(e, X) -> X
  f(X, i(X)) -> e

% twee-stats: considered_cps=500 rules_created=7 active_rules=6 solved=false allocated_bytes=10 cpu_seconds=0.01
"""

PROBLEM = """cnf(assoc, axiom, f(f(X, Y), Z) = f(X, f(Y, Z))).
cnf(unit, axiom, f(e, X) = X).
cnf(inv, axiom, f(i(X), X) = e).
cnf(goal, negated_conjecture, f(a, b) != f(b, a)).
"""


def test_split_rule_finds_the_top_level_arrow():
    assert split_rule("f(X, Y) -> X") == ("f(X, Y)", "X")
    assert split_rule("f(X, Y) <-> f(Y, X)") == ("f(X, Y)", "f(Y, X)")
    assert split_rule("g(X) ~> h(X)") == ("g(X)", "h(X)")
    assert split_rule("f(a, X) = f(X, a)") == ("f(a, X)", "f(X, a)")
    assert split_rule("f(X)") is None


def test_parse_search_log():
    rules, deleted = parse_search_log(LOG)
    assert sorted(rules) == [1, 2, 3, 4, 5, 6, 7]
    assert rules[4] == ("f(i(X), f(X, Y))", "Y")                  # score prefix
    assert rules[5] == ("f(X, f(Y, f(Z, f(W, V))))", "f(Y, f(X, f(Z, f(W, V))))")  # wrapped
    assert rules[7] == ("f(X, i(X))", "e")        # not swallowed by the "(hard)" line
    assert deleted == {3}


def test_replace_minimal_uses_one_fresh_variable():
    from nt.expand import replace_minimal
    from nt.terms import parse
    ls, rs, had = replace_minimal("f(f(X, f(?, f(?, ?))), V0)", "f(X, ?)")
    assert had and "?" not in ls + rs
    assert ls == "f(f(X, f(V1, f(V1, V1))), V0)" and rs == "f(X, V1)"
    parse(ls), parse(rs)
    assert replace_minimal("f(X)", "X") == ("f(X)", "X", False)


def test_mined_rule_with_minimal_constant(tmp_path):
    from nt.expand import mine_candidates
    prob = tmp_path / "LAT001-1.p"
    prob.write_text("cnf(a, axiom, f(X, f(Y, Y)) = X).\n"
                    "cnf(goal, negated_conjecture, f(a, a) != a).\n")
    log = tmp_path / "l.log"
    log.write_text("1. f(X, f(Y, Y)) -> X\n2. f(f(X, f(?, ?)), Z) -> f(X, Z)\n")
    cands, why = mine_candidates(str(prob), [{"log": str(log), "flatten": True,
                                              "status": "budget", "cps": 1}],
                                 "", 0.0, 0, True)
    assert [c["lhs"] for c in cands] == ["f(f(X, f(V0, V0)), Z)"]
    assert why["minimal constant -> variable"] == 1 and not why["unparsable"]


def test_pick():
    c = list(range(10))
    assert pick(c, 3, "latest") == [0, 1, 2]
    assert pick(c, 3, "spread") == [0, 4, 9] or pick(c, 3, "spread") == [0, 5, 9]
    assert pick(c, 20, "spread") == c
    assert pick(c, 1, "spread") == [0]


def test_reprove_band():
    p = lambda cps: {"status": "proved", "cps": cps}
    u = {"status": "budget", "cps": 10**6}
    assert reprove_band([p(5), p(9)], 10) == "trivial"
    assert reprove_band([p(5), p(50)], 10) == "label"
    assert reprove_band([p(5), u], 10) == "label"
    assert reprove_band([u, u], 10) == "unproved"


def stub_twee(tmp_path):
    path = tmp_path / "twee"
    log = tmp_path / "log.txt"
    log.write_text(LOG)
    # prints the progress log unless --quiet is among the arguments
    path.write_text("#!/bin/sh\n"
                    'for a in "$@"; do [ "$a" = --quiet ] && q=1; done\n'
                    f'if [ -z "$q" ]; then cat {log}; else echo "% twee-stats: considered_cps=500 '
                    'rules_created=7 active_rules=6 solved=false allocated_bytes=10 cpu_seconds=0.01"; fi\n')
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return str(path)


def test_run_keeps_log_only_when_asked(tmp_path):
    prob = tmp_path / "GRP001-1.p"
    prob.write_text(PROBLEM)
    tw = stub_twee(tmp_path)
    r = twee.run(str(prob), [], twee.Setting(), 1000, 10, twee=tw, tptp_root="")
    assert r.status == "saturated"
    log = tmp_path / "out" / "l.log.gz"
    r = twee.run(str(prob), [], twee.Setting(), 1000, 10, twee=tw, tptp_root="",
                 log_path=str(log))
    assert r.status == "saturated" and "final rewrite system" in twee.read_text(str(log))


def test_logged_run_streams_and_keeps_partial_output_on_timeout(tmp_path):
    prob = tmp_path / "p.p"
    prob.write_text(PROBLEM)
    tw = tmp_path / "slow"
    tw.write_text("#!/bin/sh\necho '1. f(X, Y) -> X'\necho '2. g(X) -> X'\nsleep 30\n")
    tw.chmod(tw.stat().st_mode | stat.S_IEXEC)
    log = tmp_path / "logs" / "p.log.gz"
    r = twee.run(str(prob), [], twee.Setting(), 1000, 1, twee=str(tw), tptp_root="",
                 log_path=str(log))
    assert r.status == "timeout"
    assert parse_search_log(twee.read_text(str(log)))[0] == {1: ("f(X, Y)", "X"), 2: ("g(X)", "X")}
    assert not list((tmp_path / "logs").glob("*.part"))


def test_base_mine_report_end_to_end(tmp_path):
    d = tmp_path / "GRP_UEQ_UNSAT"
    d.mkdir()
    (d / "GRP001-1.p").write_text(PROBLEM)
    (d / "GRP002-1.p").write_text(PROBLEM)
    names = tmp_path / "hard.txt"
    names.write_text("# hard\nGRP001-1\n")
    env = {"TWEE_PATH": stub_twee(tmp_path), "TPTP_ROOT": "", "PATH": "/usr/bin:/bin"}
    cwd = str(tmp_path)
    py = [sys.executable, "-m"]
    pp = {"PYTHONPATH": str(__import__("pathlib").Path(__file__).resolve().parents[1])}

    def call(*a):
        return subprocess.run(py + list(a), cwd=cwd, env={**env, **pp}, check=True,
                              capture_output=True, text=True).stdout

    call("nt.expand", "base", str(d), "--only", str(names), "--out", "base.jsonl",
         "--log-dir", "logs", "--no-proofs", "--max-cps", "1000", "--workers", "1")
    rows = [json.loads(l) for l in open(tmp_path / "base.jsonl")]
    assert {r["problem"] for r in rows} == {"GRP001-1"} and len(rows) == 2
    assert all(r["log"] and r["status"] == "saturated" for r in rows)

    out = call("nt.expand", "mine", "base.jsonl", "--out-dir", "mined", "--min-lateness", "0",
               "--tptp-root", "")
    man = [json.loads(l) for l in open(tmp_path / "mined" / "manifest.jsonl")]
    lemmas = {m["lemma"] for m in man}
    # axioms 1 and 2 are dropped, rule 3 was deleted, rule 6 mentions the goal's constant a
    assert lemmas == {"f(i(X), f(X, Y)) = Y", "f(X, f(Y, f(Z, f(W, V)))) = f(Y, f(X, f(Z, f(W, V))))",
                      "f(X, i(X)) = e"}
    assert all(m["source"] == "GRP001-1" for m in man)
    assert "is an axiom" in out and "symbol outside the axioms" in out

    # reprove: fake results instead of running Twee again
    with open(tmp_path / "re.jsonl", "w") as f:
        for i, m in enumerate(man):
            for flat in (True, False):
                st, cps = (("proved", 50_000) if i == 0 else ("proved", 100))
                f.write(json.dumps({"problem": m["problem"], "flatten": flat, "status": st,
                                    "cps": cps}) + "\n")
    rep = call("nt.expand", "mine-report", "mined/manifest.jsonl", "re.jsonl", "--buckets", "0")
    assert "| all | 2 | 1 | 0 | 33% |" in rep
