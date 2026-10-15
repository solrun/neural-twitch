#!/usr/bin/env bash
# Train the abstraction generator on one GH200.
#   cd /nobackup/proj/disk/<project>/neural-twitch     # repo + data/dataset copied here
#   mkdir -p logs runs
#   sbatch -A <project> --export=ALL,SIF=/nobackup/proj/disk/<project>/containers/pytorch.sif,NAME=first \
#       slurm/arrhenius/train.sbatch
# Extra options for nt.model.train go through EXTRA_ARGS.
#SBATCH -J nt-train
#SBATCH -p gpu
#SBATCH --gpus 1
#SBATCH -c 16
#SBATCH -t 0-12:00:00
#SBATCH -o logs/%x_%j.out
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
: "${SIF:?pass the container image with --export=ALL,SIF=...}"
: "${NAME:=default}"
# shellcheck disable=SC2086
apptainer exec --nv "$SIF" python -m nt.model.train --data data/dataset \
    --out "runs/$NAME" ${EXTRA_ARGS:-}
