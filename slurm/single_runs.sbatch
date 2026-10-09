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
N=$SLURM_ARRAY_TASK_COUNT
python -m nt.single_runs data/labels.jsonl "$TWITCH_DIR/data/TPTP" \
    "out/single_${K}.jsonl" --shard "$K/$N" --max-cps "$MAX_CPS" \
    --workers "$SLURM_CPUS_PER_TASK" ${EXTRA_ARGS:-}
