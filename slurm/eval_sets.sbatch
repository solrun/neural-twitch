#!/usr/bin/env bash
# Twee evaluation of generated abstraction sets as a job array: every array
# task runs one shard of one sets file (nt.model.rerank / nt.model.predict /
# nt.baseline --write-sets). Each problem is run without hints and with the
# whole set, under the goal-flattening setting in the file name
# (*_flat.jsonl -> on, *_noflat.jsonl -> off).
#
#   F=(out/rerank_k3_flat.jsonl out/rerank_k3_noflat.jsonl ...)
#   SHARDS=4                                   # shards per file
#   mkdir -p logs out/eval
#   sbatch -A <project> --array=0-$(( ${#F[@]} * SHARDS - 1 )) \
#       --export=ALL,SHARDS=$SHARDS slurm/eval_sets.sbatch "${F[@]}"
#
# Task i runs shard i % SHARDS of file i / SHARDS, writing
# out/eval/<file name>_<shard>.jsonl. Rerun failed tasks with the same
# file list and SHARDS, e.g. --array=3,7. When all are done:
#   for f in "${F[@]}"; do n=$(basename $f .jsonl); cat out/eval/${n}_*.jsonl > out/eval/$n.jsonl; done
#SBATCH -J nt-eval
#SBATCH -p vera
#SBATCH -C ZEN4
#SBATCH -n 1
#SBATCH -c 32
#SBATCH -t 0-12:00:00
#SBATCH -o logs/%x_%A_%a.out
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
source slurm/vera.env
MAX_CPS=${MAX_CPS:-6000000}
WALL=${WALL:-2400}
SHARDS=${SHARDS:-1}
mkdir -p out/eval

files=("$@")
i=$SLURM_ARRAY_TASK_ID
f=$(( i / SHARDS ))
k=$(( i % SHARDS ))
if (( f >= ${#files[@]} )); then
    echo "array index $i: only ${#files[@]} files x $SHARDS shards" >&2; exit 1
fi
sets=${files[$f]}
name=$(basename "$sets" .jsonl)
case "$name" in
    *_noflat) flatten=off ;;
    *_flat)   flatten=on ;;
    *) echo "cannot tell the flattening setting of $sets" >&2; exit 1 ;;
esac
echo "== $name shard $k/$SHARDS (flatten $flatten)"
python -m nt.single_runs --sets "$sets" "out/eval/${name}_${k}.jsonl" --no-singles \
    --shard "$k/$SHARDS" --flatten "$flatten" --weights f0.5 --max-cps "$MAX_CPS" \
    --wall-timeout "$WALL" --workers "$SLURM_CPUS_PER_TASK"
