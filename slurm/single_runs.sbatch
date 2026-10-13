#!/usr/bin/env bash
# Single-abstraction experiment as a job array: each array task runs one shard.
#   mkdir -p logs out
#   sbatch -A <project> --array=0-31 --export=ALL,MAX_CPS=<budget> slurm/single_runs.sbatch
#   cat out/single_*.jsonl > out/single.jsonl                 # when all are done
#SBATCH -J nt-single
#SBATCH -p vera
#SBATCH -C ZEN4
#SBATCH -n 1
#SBATCH -c 32
#SBATCH -t 0-12:00:00
#SBATCH -o logs/%x_%A_%a.out
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
source slurm/vera.env
: "${MAX_CPS:?pass the CP budget with --export=ALL,MAX_CPS=...}"

K=$SLURM_ARRAY_TASK_ID
# SHARDS fixes the shard count, so a rerun of some shards (--array=2,5)
# still splits the problems the same way as the original array.
N=${SHARDS:-$SLURM_ARRAY_TASK_COUNT}
# SETS=<file from nt.expand> labels those sets instead of the Twitch ones;
# NAME sets the output prefix (default "single").
if [[ -n "${SETS:-}" ]]; then
    inputs=(--sets "$SETS")
else
    inputs=(data/labels.jsonl "$TWITCH_DIR/data/TPTP")
fi
# shellcheck disable=SC2086  # EXTRA_ARGS is word-split and globbed on purpose
python -m nt.single_runs "${inputs[@]}" \
    "out/${NAME:-single}_${K}.jsonl" --shard "$K/$N" --max-cps "$MAX_CPS" \
    --workers "$SLURM_CPUS_PER_TASK" ${EXTRA_ARGS:-}
