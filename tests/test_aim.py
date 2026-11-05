import json
import subprocess
import sys

from nt import aim


def run(problem, flatten, status="proved", alloc=10**9, cpu=0.3):
    return {"problem": problem, "flatten": flatten, "status": status,
            "allocated_bytes": alloc if status == "proved" else None,
            "cpu_seconds": cpu if status == "proved" else None, "wall": 0.5}


def test_names():
    assert aim.strip("AIM-KK_Kcom_to_aK1__goal_10") == "KK_Kcom_to_aK1__goal_10"
    assert aim.family("KK_Kcom_to_aK1__goal_10") == "KK_Kcom_to_aK1"
    assert aim.goal_index("KK_Kcom_to_aK1__goal_10") == 10


def test_budgets():
    rows = [run("AIM-a__goal_1", True),
            run("AIM-a__goal_2", True, alloc=5 * 10**9, cpu=2.0),   # over both budgets
            run("AIM-a__goal_2", False, alloc=2 * 10**9, cpu=1.5),  # alloc only
            run("AIM-a__goal_3", False, status="timeout")]
    S = aim.solved_sets(rows, alloc_budget=2.75e9, cpu_budget=1.0)
    assert S["alloc", "either"] == {"a__goal_1", "a__goal_2"}
    assert S["alloc", "on"] == {"a__goal_1"}
    assert S["cpu", "either"] == {"a__goal_1"}
    assert S["cap", "either"] == {"a__goal_1", "a__goal_2"}


def test_report(tmp_path):
    runs = tmp_path / "base_0.jsonl"
    runs.write_text("\n".join(json.dumps(r) for r in [
        run("AIM-a__goal_1", True), run("AIM-a__goal_1", False),
        run("AIM-b__goal_1", True, status="budget"), run("AIM-b__goal_1", False, status="budget"),
    ]) + "\n{\"truncated")
    (tmp_path / "p9").write_text("b__goal_1\n")
    (tmp_path / "e").write_text("")
    out = subprocess.run([sys.executable, "-m", "nt.aim", "report", str(runs),
                          "--p9", str(tmp_path / "p9"), "--e", str(tmp_path / "e"),
                          "--write-lists", str(tmp_path / "lists")],
                         capture_output=True, text=True, check=True).stdout
    assert "| Twee alloc, flattening either | 1 | 2 | 1 |" in out
    assert "all three together: 2 of" in out
    assert (tmp_path / "lists" / "twee_alloc_either.txt").read_text() == "a__goal_1\n"
    assert (tmp_path / "lists" / "unsolved.txt").read_text() == ""
