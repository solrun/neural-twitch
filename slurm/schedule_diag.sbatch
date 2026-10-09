#!/usr/bin/env bash
# Housekeeping-schedule diagnostic (nt.schedule_diag): 42 runs, one per core.
#   mkdir -p logs out
#   sbatch slurm/schedule_diag.sbatch
#   python -m nt.schedule_diag data/labels.jsonl "$TWITCH_DIR/data/TPTP" out/schedule_diag.jsonl --report
#SBATCH -J nt-schedule-diag
#SBATCH -p vera
#SBATCH -C ZEN4
#SBATCH -n 1
#SBATCH -c 48
#SBATCH -t 0-01:00:00
#SBATCH -o logs/%x_%j.out
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
source slurm/vera.env

python -m nt.schedule_diag data/labels.jsonl "$TWITCH_DIR/data/TPTP" \
    out/schedule_diag.jsonl --workers "$SLURM_CPUS_PER_TASK" ${EXTRA_ARGS:-}
