#!/usr/bin/env bash
# Twee evaluation of generated abstraction sets on one node: for each sets file
# (nt.model.rerank / nt.model.predict / nt.baseline --write-sets), run Twee
# without hints and with the whole set, under the matching goal-flattening
# setting (taken from the file name: *_flat.jsonl or *_noflat.jsonl).
#
#   mkdir -p logs out/eval
#   sbatch -A <project> slurm/eval_sets.sbatch out/rerank_k3_flat.jsonl out/base_combined_k3_flat.jsonl ...
#
# Results: out/eval/<sets file name>.jsonl. Files already evaluated are skipped,
# so resubmitting after a timeout continues where it stopped.
#SBATCH -J nt-eval
#SBATCH -p vera
#SBATCH -C ZEN4
#SBATCH -n 1
#SBATCH -c 32
#SBATCH -t 0-24:00:00
#SBATCH -o logs/%x_%j.out
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
source slurm/vera.env
MAX_CPS=${MAX_CPS:-6000000}
WALL=${WALL:-2400}
mkdir -p out/eval

for sets in "$@"; do
    name=$(basename "$sets" .jsonl)
    out="out/eval/$name.jsonl"
    case "$name" in
        *_noflat) flatten=off ;;
        *_flat)   flatten=on ;;
        *) echo "cannot tell the flattening setting of $sets" >&2; exit 1 ;;
    esac
    if [[ -s "$out" ]] && grep -q '"ratio"' "$out"; then
        echo "== $name: already done"; continue
    fi
    echo "== $name (flatten $flatten)"
    python -m nt.single_runs --sets "$sets" "$out" --no-singles \
        --flatten "$flatten" --weights f0.5 --max-cps "$MAX_CPS" \
        --wall-timeout "$WALL" --workers "$SLURM_CPUS_PER_TASK"
done
