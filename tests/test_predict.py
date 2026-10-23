import gzip
import json

from nt.model.predict import rank_samples, train_abstractions


def test_rank_by_count_merges_duplicates_and_drops_undecodable():
    samples = [("f(X0, X0)", 0.1), ("g(X0)", 2.0), ("f(X0, X0)", -1.0), (None, 5.0),
               ("f(X0, X0)", 0.3), ("g(X0)", 1.0), ("h(X0, X1)", 3.0)]
    ranked = rank_samples(samples, "count")
    assert [c["abstraction"] for c in ranked] == ["f(X0, X0)", "g(X0)", "h(X0, X1)"]
    assert [c["count"] for c in ranked] == [3, 2, 1]
    assert ranked[0]["score"] == 0.3                      # best score of the duplicates


def test_rank_by_scorer_and_count_ties():
    samples = [("a", 1.0), ("b", 3.0), ("c", 2.0), ("c", 0.0)]
    assert [c["abstraction"] for c in rank_samples(samples, "scorer")] == ["b", "c", "a"]
    # equal counts fall back to the score
    assert [c["abstraction"] for c in rank_samples([("a", 1.0), ("b", 3.0)], "count")] == ["b", "a"]
    assert rank_samples([(None, 1.0)], "count") == []


def test_train_abstractions_reads_only_train(tmp_path):
    rows = [
        {"problem": "P1", "split": "train", "singles": [{"abstraction": "f(X0, X0)"}],
         "sets": [{"abstractions": ["f(X0, X0)", "g(X0)"]}]},
        {"problem": "P2", "split": "test", "singles": [{"abstraction": "h(X0)"}], "sets": []},
    ]
    with gzip.open(tmp_path / "examples.jsonl.gz", "wt") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    assert train_abstractions(str(tmp_path)) == {"f(X0, X0)", "g(X0)"}
