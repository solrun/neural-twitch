#!/usr/bin/env bash
# Baseline runs with proofs for nt.expand, as a job array.
#   mkdir -p logs out/expand
#   sbatch --array=0-7 --export=ALL,NAME=etp,INPUTS=$HOME/ijcar26-twee_abstractions/data/TPTP/ETP_UEQ_UNSAT \
#       slurm/expand_base.sbatch
#   cat out/expand/etp_base_*.jsonl > out/expand/etp_base.jsonl
# INPUTS: problem directories, .p files or a manifest .jsonl, space-separated;
# globs are expanded inside the job.
#SBATCH -J nt-expand-base
#SBATCH -p vera
#SBATCH -C ZEN4
#SBATCH -n 1
#SBATCH -c 32
#SBATCH -t 0-08:00:00
#SBATCH -o logs/%x_%A_%a.out
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
source slurm/vera.env
: "${NAME:?pass a name for the output files with --export=ALL,NAME=...}"
: "${INPUTS:?pass the problems with --export=ALL,INPUTS=...}"

K=$SLURM_ARRAY_TASK_ID
N=$SLURM_ARRAY_TASK_COUNT
# shellcheck disable=SC2086  # INPUTS and EXTRA_ARGS are word-split and globbed on purpose
python -m nt.expand base $INPUTS --out "out/expand/${NAME}_base_${K}.jsonl" \
    --shard "$K/$N" --workers "$SLURM_CPUS_PER_TASK" ${EXTRA_ARGS:-}
