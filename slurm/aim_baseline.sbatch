#!/usr/bin/env bash
# Plain-Twee baseline on the AIM problems (Veroff/Urban, nt.aim): both
# flattening settings, deterministic allocation clock, as a job array.
#   rsync -a ~/data/problems.tar.gz <cid>@vera1.c3se.chalmers.se:<NT_STORE>/aim/
#   mkdir -p logs out/aim
#   sbatch -A C3SE2026-1-12 --array=0-15 slurm/aim_baseline.sbatch
#   python -m nt.aim report out/aim/base_*.jsonl --write-lists out/aim/lists
# Proofs of the solved problems only:
#   sbatch --array=0-15 --export=ALL,LIST=out/aim/lists/twee_alloc_either.txt,PROOFS=1,NAME=proofs \
#       slurm/aim_baseline.sbatch
# Each task unpacks the TPTP files from the tarball into node-local $TMPDIR
# (61,800 files; nothing lands on home or NT_STORE), in a directory named AIM
# so problem ids are AIM-<name>.
# Options (--export=ALL,...):
#   TARBALL    problems tarball with problems/tptp/*.p (default $NT_STORE/aim/problems.tar.gz)
#   LIST       file of problem names to run, one per line, with or without the
#              AIM- prefix and .p suffix (default all), e.g. the solved list
#              from `nt.aim report --write-lists` to rerun them with PROOFS=1
#   WALL       wall cap in seconds per run (default 10; the report's 1 s budgets are
#              computed from allocation and CPU time, the cap only bounds the cost)
#   MAX_CPS    CP budget per run (default unlimited)
#   FLATTEN    both|on|off (default both)
#   NAME       output prefix (default base)
#   PROOFS     1 to keep proofs in $NT_STORE/aim/proofs (default 0; ~2 files per proved problem)
# After an interruption, rerun the unfinished shards with the same SHARDS and
# --resume, which keeps finished runs:
#   sbatch --array=2,5 --export=ALL,SHARDS=16,EXTRA_ARGS=--resume slurm/aim_baseline.sbatch
#SBATCH -J nt-aim-base
#SBATCH -p vera
#SBATCH -C ZEN4
#SBATCH -n 1
#SBATCH -c 32
#SBATCH -t 0-03:00:00
#SBATCH -o logs/%x_%A_%a.out
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
source slurm/vera.env

K=$SLURM_ARRAY_TASK_ID
N=${SHARDS:-$SLURM_ARRAY_TASK_COUNT}
NAME=${NAME:-base}
TARBALL=${TARBALL:-${NT_STORE:?set NT_STORE or TARBALL}/aim/problems.tar.gz}
WORK=$(mktemp -d "${TMPDIR:-/tmp}/aim.XXXXXX")
trap 'rm -rf "$WORK"' EXIT

mkdir -p "$WORK/AIM"
tar xzf "$TARBALL" -C "$WORK/AIM" --strip-components=2 --wildcards 'problems/tptp/*.p'
echo "$(find "$WORK/AIM" -name '*.p' | wc -l) problems unpacked"
if [ -n "${LIST:-}" ]; then
    # keep only the listed problems, before sharding, so shards stay balanced
    sed -e 's/^AIM-//' -e 's/\.p$//' -e '/^[[:space:]]*$/d' "$LIST" | sort -u > "$WORK/keep"
    find "$WORK/AIM" -name '*.p' -printf '%f\n' | sed 's/\.p$//' | sort > "$WORK/all"
    missing=$(comm -23 "$WORK/keep" "$WORK/all" | wc -l)
    [ "$missing" = 0 ] || echo "warning: $missing listed problems not in the tarball" >&2
    comm -13 "$WORK/keep" "$WORK/all" | sed "s|^|$WORK/AIM/|; s|\$|.p|" | xargs -r rm -f
    echo "$(find "$WORK/AIM" -name '*.p' | wc -l) problems kept from $LIST"
fi

if [ "${PROOFS:-0}" = 1 ]; then
    PROOF_ARGS=(--proof-dir "${NT_STORE:?PROOFS=1 needs NT_STORE}/aim/proofs")
else
    PROOF_ARGS=(--no-proofs)
fi

# shellcheck disable=SC2086  # EXTRA_ARGS is word-split on purpose
python -m nt.expand base "$WORK/AIM" --shard "$K/$N" --out "out/aim/${NAME}_${K}.jsonl" \
    "${PROOF_ARGS[@]}" --flatten "${FLATTEN:-both}" --wall-timeout "${WALL:-10}" \
    ${MAX_CPS:+--max-cps "$MAX_CPS"} --workers "$SLURM_CPUS_PER_TASK" ${EXTRA_ARGS:-}
