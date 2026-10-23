import json

from nt import eval_report as er
from nt.single_runs import jobs_for, settings


def single(rank, status, alloc, cps=1000):
    return {"kind": "single", "rank": rank, "status": status,
            "allocated_bytes": alloc, "cps": cps}


def test_jobs_for_singles_only_gives_ranked_singles():
    jobs = list(jobs_for("P", "p.p", ["a", "b", "c"], (True,), ("f0.5",), singles_only=True))
    assert [(j[3], j[4], j[5]) for j in jobs] == [
        ("single", ["a"], 0), ("single", ["b"], 1), ("single", ["c"], 2)]
    # a one-element set still gets its single (unlike the default mode)
    assert len(list(jobs_for("P", "p.p", ["a"], (True,), ("f0.5",), singles_only=True))) == 1


def test_portfolio_shares_the_budget():
    er.ALLOC_BUDGET = 100.0
    by_rank = {0: single(0, "budget", None), 1: single(1, "proved", 40),
               2: single(2, "proved", 20)}
    assert not er.proved(er.singles_portfolio(by_rank, 1))   # top 1 fails
    p2 = er.singles_portfolio(by_rank, 2)                    # 2 x 40 = 80 <= 100
    assert er.proved(p2) and p2["allocated_bytes"] == 80
    p3 = er.singles_portfolio(by_rank, 3)                    # 3 x 20 = 60
    assert er.proved(p3) and p3["rank"] == 2
    by_rank[2] = single(2, "proved", 35)                     # 3 x 35 = 105 > 100
    assert not er.proved(er.singles_portfolio(by_rank, 3))
    er.ALLOC_BUDGET = None


def test_add_singles_reuses_base_and_matches_set_ks(tmp_path):
    base = {"kind": "base", "status": "proved", "allocated_bytes": 50, "cps": 10}
    runs = {("rerank", k, True): {"P": {"base": base, "set": base}} for k in (1, 3, 5)}
    f = tmp_path / "rerank_k5_flat_0.jsonl"
    f.write_text("\n".join(json.dumps({"problem": "P", **single(r, "proved", 10)})
                           for r in range(5)))
    er.add_singles(runs, er.load_singles([str(f)]))
    assert {k for m, k, _ in runs if m == "rerank-singles"} == {1, 3, 5}
    assert runs["rerank-singles", 3, True]["P"]["base"] is base
    assert runs["rerank-singles", 3, True]["P"]["set"]["allocated_bytes"] == 30
