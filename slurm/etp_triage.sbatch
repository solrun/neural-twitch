#!/usr/bin/env bash
# Triage of the ETP implications (nt.etp): plain Twee, both flattening
# settings and a CP budget, as a job array.
#   mkdir -p logs out/etp
#   sbatch --array=0-15 slurm/etp_triage.sbatch
#   python -m nt.etp report out/etp/triage_*.jsonl --write-lists out/etp/lists
# With NT_STORE set (slurm/vera.env), problems go to $NT_STORE/etp/problems
# and proofs to $NT_STORE/etp/proofs, so the label band needs no second run
# (`nt.expand abstract` reads the proofs directly). Without it, each shard's
# problems go to node-local $TMPDIR and no proofs are kept, so nothing counts
# against the home quota.
# Options (--export=ALL,...):
#   TIERS      subset of degenerate:hasse:closure:equiv, separated by ':' (sbatch's
#              --export splits at commas), e.g. TIERS=degenerate:hasse:equiv; default all
#   MAX_CPS    CP budget per run (default 1000000)
#   WALL       wall cap in seconds per run (default 300)
#   NAME       output prefix (default triage)
#   PROOFS     1 to keep proofs, 0 not to (default 1 with NT_STORE, else 0)
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
NAME=${NAME:-triage}
WORK=$(mktemp -d "${TMPDIR:-/tmp}/etp.XXXXXX")
trap 'rm -rf "$WORK"' EXIT

if [ -n "${NT_STORE:-}" ]; then
    PROBLEMS="$NT_STORE/etp/problems"
    PROOFS=${PROOFS:-1}
else
    PROBLEMS="$WORK"
    PROOFS=${PROOFS:-0}
fi
if [ "$PROOFS" = 1 ]; then
    [ -n "${NT_STORE:-}" ] || { echo "PROOFS=1 needs NT_STORE (home quota)" >&2; exit 1; }
    PROOF_ARGS=(--proof-dir "$NT_STORE/etp/proofs")
else
    PROOF_ARGS=(--no-proofs)
fi

python -m nt.etp write data/etp ${TIERS:+--tiers "$TIERS"} --shard "$K/$N" \
    --out-dir "$PROBLEMS" --manifest "$WORK/manifest.jsonl"
# shellcheck disable=SC2086  # EXTRA_ARGS is word-split on purpose
python -m nt.expand base "$WORK/manifest.jsonl" --out "out/etp/${NAME}_${K}.jsonl" \
    "${PROOF_ARGS[@]}" --max-cps "${MAX_CPS:-1000000}" --wall-timeout "${WALL:-300}" \
    --workers "$SLURM_CPUS_PER_TASK" ${EXTRA_ARGS:-}
