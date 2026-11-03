import os
import stat

from nt import twee


def stub(tmp_path, cps, solved):
    """A fake Twee binary that prints only the stats line."""
    path = tmp_path / "twee"
    path.write_text("#!/bin/sh\n"
                    f"echo '% twee-stats: considered_cps={cps} rules_created=1 "
                    f"active_rules=1 solved={'true' if solved else 'false'} "
                    "allocated_bytes=10 cpu_seconds=0.01'\n")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return str(path)


def run(tmp_path, cps, solved, max_cps=1000, extra=None):
    prob = tmp_path / "p.p"
    prob.write_text("cnf(a, axiom, X = X).\n")
    return twee.run(str(prob), [], twee.Setting(), max_cps, 10,
                    twee=stub(tmp_path, cps, solved), tptp_root="",
                    extra_flags=extra).status


def test_outcomes(tmp_path):
    assert run(tmp_path, 20, True) == "proved"
    assert run(tmp_path, 25, False) == "saturated"          # stopped below the limit
    assert run(tmp_path, 1000, False) == "budget"           # reached the limit
    # another limit could have stopped it, so no saturation claim
    assert run(tmp_path, 25, False, extra=["--max-term-size", "20"]) == "budget"
    assert run(tmp_path, 25, False, extra=["--max-rules=5"]) == "budget"


def test_unsolved_status():
    assert twee.unsolved_status(10, 10) == "budget"
    assert twee.unsolved_status(9, 10) == "saturated"
    assert twee.unsolved_status(9, 10, ["--max-time", "3"]) == "budget"
