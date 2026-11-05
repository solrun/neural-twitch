#!/usr/bin/env bash
# Triage of the residuated-lattice and l-group problems (nt.reslat): plain
# Twee, both flattening settings and a CP budget, as a job array.
#   mkdir -p logs out/reslat
#   sbatch --array=0-7 slurm/reslat_triage.sbatch
#   python -m nt.reslat report out/reslat/triage_*.jsonl --write-lists out/reslat/lists
# Every problem is a theorem (decided before writing), so an unproved run is
# either hard (open) or, if Twee saturated, a bug in the axioms or a decider.
# With NT_STORE set (slurm/vera.env), problems go to $NT_STORE/reslat/problems
# and proofs to $NT_STORE/reslat/proofs; without it, problems go to node-local
# $TMPDIR and no proofs are kept.
# Options (--export=ALL,...):
#   VARIETIES  comma-separated subset of rl,lg (default both)
#   MAX_CPS    CP budget per run (default 1000000)
#   WALL       wall cap in seconds per run (default 300)
#   NAME       output prefix (default triage)
#   PROOFS     1 to keep proofs, 0 not to (default 1 with NT_STORE, else 0)
#   LIST       file of problem names to run (default all)
#   FLATTEN    both, on or off (default both)
# Long runs use a lot of memory: with WALL=3600 and 32 workers a shard ran
# out of memory (job 10644159_0), so give fewer workers for long runs:
#   EXTRA_ARGS="--workers 8"   (the last --workers wins)
# Resume unfinished shards with the same SHARDS and --resume:
#   sbatch --array=2,5 --export=ALL,SHARDS=8,EXTRA_ARGS=--resume slurm/reslat_triage.sbatch
#SBATCH -J nt-reslat-triage
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
WORK=$(mktemp -d "${TMPDIR:-/tmp}/reslat.XXXXXX")
trap 'rm -rf "$WORK"' EXIT

if [ -n "${NT_STORE:-}" ]; then
    PROBLEMS="$NT_STORE/reslat/problems"
    PROOFS=${PROOFS:-1}
else
    PROBLEMS="$WORK"
    PROOFS=${PROOFS:-0}
fi
if [ "$PROOFS" = 1 ]; then
    [ -n "${NT_STORE:-}" ] || { echo "PROOFS=1 needs NT_STORE (home quota)" >&2; exit 1; }
    PROOF_ARGS=(--proof-dir "$NT_STORE/reslat/proofs")
else
    PROOF_ARGS=(--no-proofs)
fi

python -m nt.reslat write data/reslat --varieties "${VARIETIES:-rl,lg}" --shard "$K/$N" \
    ${LIST:+--problems "$LIST"} \
    --out-dir "$PROBLEMS" --manifest "$WORK/manifest.jsonl"
# shellcheck disable=SC2086  # EXTRA_ARGS is word-split on purpose
python -m nt.expand base "$WORK/manifest.jsonl" --out "out/reslat/${NAME}_${K}.jsonl" \
    "${PROOF_ARGS[@]}" --flatten "${FLATTEN:-both}" --max-cps "${MAX_CPS:-1000000}" --wall-timeout "${WALL:-300}" \
    --workers "$SLURM_CPUS_PER_TASK" ${EXTRA_ARGS:-}
