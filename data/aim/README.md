# AIM problems (Veroff and Urban)

61,800 problems about AIM loops from Bob Veroff and Josef Urban (received
2026-11-05; Urban plans to put them on GitHub). The problems themselves are
not in this repository (245 MB each for `ladr/` and `tptp/`); keep the
tarball `problems.tar.gz` (`problems/{ladr,tptp,00p9_1s,00e_1s}`) in
`$NT_STORE/aim/` on Vera.

- `ladr/<name>`: the Prover9 input.
- `tptp/<name>.p`: the same problem with the axioms as `cnf` unit equalities
  and the goal as one `fof` conjecture (universally quantified, not negated
  or skolemized; Twee handles that). Symbols not legal in TPTP are renamed
  (`*` → `m`, `\` → `ld`, `/` → `rd`, `1` → `e`, `K` → `k`, …); the
  mapping is in each file's header comment.
- Names are `<family>__goal_<n>`: about 150 families, and within a family the
  goals form a curriculum, so learning from earlier proved goals should help
  with later ones.

Urban's 1-second results (copied here):

| | proved |
|---|---|
| `00p9_1s`: Prover9, no flags | 22,272 |
| `00e_1s`: E `--auto` | 21,594 |
| either | 23,745 |

Twee baseline: `slurm/aim_baseline.sbatch`, then `python -m nt.aim report`.
