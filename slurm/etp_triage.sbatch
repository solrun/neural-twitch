#!/usr/bin/env bash
# Triage of the ETP implications (nt.etp): plain Twee, both flattening
# settings and a CP budget, as a job array.
#   mkdir -p logs out/etp
#   sbatch --array=0-15 slurm/etp_triage.sbatch
#   python -m nt.etp report out/etp/triage_*.jsonl --write-lists out/etp/lists
# (outputs are out/etp/<NAME>_<K>.jsonl; NAME defaults to triage_<tiers>)
# Problems are written to node-local $TMPDIR. With NT_STORE set (slurm/vera.env),
# proofs of at least PROOF_MIN_CPS go to $NT_STORE/etp/proofs, the problems
# with such a proof are copied to $NT_STORE/etp/problems, and the output rows
# point there (nt.etp keep), so the label band needs no second run. Only a few
# files reach project storage: it has a file quota, and 100k problem files
# exceeded it. Without NT_STORE, no proofs are kept and rows keep $TMPDIR paths.
# Options (--export=ALL,...):
#   TIERS      subset of degenerate:hasse:closure:equiv, separated by ':' (sbatch's
#              --export splits at commas), e.g. TIERS=degenerate:hasse:equiv; default all
#   MAX_CPS    CP budget per run (default 1000000)
#   WALL       wall cap in seconds per run (default 300)
#   NAME       output prefix (default triage_<tiers>, e.g. triage_closure, so runs
#              of different tiers don't overwrite each other)
#   PROOFS     1 to keep proofs, 0 not to (default 1 with NT_STORE, else 0)
#   PROOF_MIN_CPS  keep only proofs needing at least this many CPs (default 10000,
#              nt.expand's DEFAULT_MIN_CPS: cheaper proofs are never labelled)
#   COMPACT    1 to turn the output into out/etp/<NAME>_<K>.tsv.gz (nt.etp compact)
#              and drop the .jsonl; default 1 for TIERS=all (16M runs), else 0
#   SAMPLE     random N problems of the chosen tiers (fixed by seed 0), e.g. a
#              first look at the 100k random tier
# After an interruption, rerun the unfinished shards with the same SHARDS and
# --resume, which keeps finished runs:
#   sbatch --array=2,5 --export=ALL,SHARDS=16,EXTRA_ARGS=--resume slurm/etp_triage.sbatch
#SBATCH -J nt-etp-triage
#SBATCH -p vera
#SBATCH -C ZEN4
#SBATCH -n 1
#SBATCH -c 32
#SBATCH -t 0-08:00:00
#SBATCH -o logs/%x_%A_%a.out
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
source slurm/vera.env

K=$SLURM_ARRAY_TASK_ID
N=${SHARDS:-$SLURM_ARRAY_TASK_COUNT}
TAG=${TIERS:-all}
NAME=${NAME:-triage_${TAG//[:,+ ]/-}}${SAMPLE:+_s$SAMPLE}
WORK=$(mktemp -d "${TMPDIR:-/tmp}/etp.XXXXXX")
trap 'rm -rf "$WORK"' EXIT

if [ -n "${NT_STORE:-}" ]; then
    PROOFS=${PROOFS:-1}
else
    PROOFS=${PROOFS:-0}
fi
if [ "$PROOFS" = 1 ]; then
    [ -n "${NT_STORE:-}" ] || { echo "PROOFS=1 needs NT_STORE (home quota)" >&2; exit 1; }
    PROOF_ARGS=(--proof-dir "$NT_STORE/etp/proofs" --proof-min-cps "${PROOF_MIN_CPS:-10000}")
else
    PROOF_ARGS=(--no-proofs)
fi

python -m nt.etp write data/etp ${TIERS:+--tiers "$TIERS"} ${SAMPLE:+--sample "$SAMPLE"} \
    --shard "$K/$N" \
    --out-dir "$WORK" --manifest "$WORK/manifest.jsonl"
# shellcheck disable=SC2086  # EXTRA_ARGS is word-split on purpose
python -m nt.expand base "$WORK/manifest.jsonl" --out "out/etp/${NAME}_${K}.jsonl" \
    "${PROOF_ARGS[@]}" --max-cps "${MAX_CPS:-1000000}" --wall-timeout "${WALL:-300}" \
    --workers "$SLURM_CPUS_PER_TASK" ${EXTRA_ARGS:-}
if [ -n "${NT_STORE:-}" ]; then
    python -m nt.etp keep "out/etp/${NAME}_${K}.jsonl" --to "$NT_STORE/etp/problems"
fi
if [ "${COMPACT:-$([ "${TIERS:-}" = all ] && echo 1 || echo 0)}" = 1 ]; then
    python -m nt.etp compact "out/etp/${NAME}_${K}.jsonl" --remove
fi
