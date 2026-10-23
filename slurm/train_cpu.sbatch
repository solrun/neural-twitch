#!/usr/bin/env bash
# Train the abstraction generator on a Vera CPU node, with C3SE's PyTorch
# module instead of a venv (training needs nothing beyond PyTorch).
#   mkdir -p logs runs
#   sbatch -A <project> --export=ALL,NAME=extra,DATA=data/dataset_extra slurm/train_cpu.sbatch
# Extra options for nt.model.train go through EXTRA_ARGS, e.g.
#   --export=ALL,NAME=extra,DATA=data/dataset_extra,EXTRA_ARGS="--epochs 30"
# Check the module once: `python -m nt.model.train --smoke` in an interactive job.
#SBATCH -J nt-train-cpu
#SBATCH -p vera
#SBATCH -C ZEN4
#SBATCH -n 1
#SBATCH -c 16
#SBATCH -t 0-08:00:00
#SBATCH -o logs/%x_%j.out
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
module purge
module load PyTorch/2.1.2-foss-2023b
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
: "${NAME:=default}"
: "${DATA:=data/dataset}"
# shellcheck disable=SC2086  # EXTRA_ARGS is word-split on purpose
python -m nt.model.train --data "$DATA" --out "runs/$NAME" --device cpu ${EXTRA_ARGS:-}
