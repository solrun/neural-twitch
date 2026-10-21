# Unit-equality TPTP problems not used by Twitch

TPTP v9.2.1 has 1,143 unsatisfiable UEQ problems (Twitch's
`data/TPTP/UEQ_Unsat.txt`, the output of `tptp2T UnitEquality Status Unsatisfiable`).
Twitch's `filter.py` copied only the nine domains ALG, BOO, COL, GRP, LAT, LCL, REL,
RNG and ROB, which gives its 1,041 problems (`UEQ_UNS`). The other 100 problems are
listed in `new_ueq_unsat.tsv`.

The 83 problems with fewer than 1,000 clauses are copied here, in one
`<DOM>_UEQ_UNSAT/` directory per domain, so `nt.expand` gets the domain from the
directory name. The 17 larger ones are left out: 15 CSR problems (SUMO, up to 44k
clauses) and PLA031-10.019. MVA problems include `Axioms/MVA001-0.ax`, which is
already under `$TPTP_ROOT/Axioms` on Vera. All 83 parse as CNF unit equalities with
`nt.tptp`.

| | native UEQ | `-10` ifeq-encoded | total |
|---|---|---|---|
| copied here | 33 | 50 | 83 |
| left out (≥1,000 clauses) | 0 | 17 | 17 |

**Native** problems: MVA (15), LDA (3), TOP (5), SWV (4), NUN (2), SYN (2), ANA (1),
COM (1).

**ifeq-encoded** problems are the `-10` versions. They are non-UEQ problems (Horn
clauses with predicates) translated to unit equality using `ifeq(A,A,B,C) = B`
axioms. All 15 KLE problems are of this kind. Their proofs and abstractions are
dominated by `ifeq` terms, so analyse them separately from the native problems
(the `encoding` column in the TSV).

KLE and MVA are theories that don't appear anywhere in the current dataset, so they
are candidates for the leave-domain-out test.

## Triage (baseline runs with proofs)

```bash
sbatch --array=0-3 --export=ALL,NAME=extra,INPUTS="data/tptp_extra/*_UEQ_UNSAT" \
    slurm/expand_base.sbatch
cat out/expand/extra_base_*.jsonl > out/expand/extra_base.jsonl
```

After that, the usual pipeline applies: `hindsight` → `base` on the subproblem
manifest → `abstract` → `single_runs`.
