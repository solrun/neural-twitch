#!/usr/bin/env bash
# Baseline calibration as a job array: each array task runs one shard.
#   mkdir -p logs out
#   sbatch -A <project> --array=0-7 slurm/calibrate.sbatch
#   python -m nt.calibrate_report out/calibration_*.jsonl     # when all are done
#SBATCH -J nt-calibrate
#SBATCH -p vera
#SBATCH -C ZEN4
#SBATCH -n 1
#SBATCH -c 32
#SBATCH -t 0-04:00:00
#SBATCH -o logs/%x_%A_%a.out
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
source slurm/vera.env

K=$SLURM_ARRAY_TASK_ID
N=$SLURM_ARRAY_TASK_COUNT
python -m nt.calibrate data/labels.jsonl "$TWITCH_DIR/data/TPTP" \
    "out/calibration_${K}.jsonl" --shard "$K/$N" \
    --workers "$SLURM_CPUS_PER_TASK" ${EXTRA_ARGS:-}
