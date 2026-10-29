#!/usr/bin/env bash
# Vampire on a list of ETP problems (nt.etp fmb): countermodel search with the
# finite model builder (MODE=fmb, default) or proof search with the CASC
# strategy schedule (MODE=casc). E.g. the pairs problems Twee did not prove:
#   mkdir -p logs out/etp
#   sbatch --array=0-15 --export=ALL,LIST=out/etp/lists_pairs/hard.txt,NAME=fmb_pairs \
#       slurm/etp_fmb.sbatch
#   python -m nt.etp fmb-report out/etp/fmb_pairs_*.tsv \
#       --triage out/etp/triage_pairs_*.jsonl --write-lists out/etp/lists_pairs
# Needs VAMPIRE_PATH (slurm/vera.env): the static Vampire 5.0 binary from
# Janota's Zenodo archive (eq_vampire/vampire) works as is.
# Options (--export=ALL,...):
#   LIST    problem names, one per line (required)
#   NAME    output prefix (default fmb)
#   MODE    fmb (countermodels, default) or casc (proofs)
#   LIMIT   seconds per problem (default 60 for fmb, 600 for casc)
# Proofs and models of decided problems are kept in out/etp/vampire_<NAME>/.
# Proof search on the problems the model builder left open:
#   sbatch --array=0-3 --export=ALL,LIST=out/etp/lists_pairs/fmb_unknown.txt,MODE=casc,NAME=casc_pairs \
#       slurm/etp_fmb.sbatch
# After an interruption, rerun the unfinished shards with the same SHARDS and
# EXTRA_ARGS=--resume.
#SBATCH -J nt-etp-fmb
#SBATCH -p vera
#SBATCH -C ZEN4
#SBATCH -n 1
#SBATCH -c 32
#SBATCH -t 0-02:00:00
#SBATCH -o logs/%x_%A_%a.out
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
source slurm/vera.env
: "${LIST:?pass a list of problem names with --export=ALL,LIST=...}"
: "${VAMPIRE_PATH:?set VAMPIRE_PATH in slurm/vera.env}"

K=$SLURM_ARRAY_TASK_ID
N=${SHARDS:-$SLURM_ARRAY_TASK_COUNT}
NAME=${NAME:-fmb}
WORK=$(mktemp -d "${TMPDIR:-/tmp}/etp.XXXXXX")
trap 'rm -rf "$WORK"' EXIT

python -m nt.etp write data/etp --problems "$LIST" --shard "$K/$N" --out-dir "$WORK"
# shellcheck disable=SC2086  # EXTRA_ARGS is word-split on purpose
python -m nt.etp fmb "$WORK/manifest.jsonl" --out "out/etp/${NAME}_${K}.tsv" \
    --vampire "$VAMPIRE_PATH" --mode "${MODE:-fmb}" \
    --limit "${LIMIT:-$([ "${MODE:-fmb}" = casc ] && echo 600 || echo 60)}" \
    --save-dir "out/etp/vampire_${NAME}" --workers "$SLURM_CPUS_PER_TASK" \
    ${EXTRA_ARGS:-}
