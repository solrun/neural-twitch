# Running the experiments on Vera (C3SE)

The experiments are many independent Twee runs, so each script is split into
shards and submitted as a Slurm job array: one array task per shard, each
using part of a node. Critical-pair counts are deterministic, so it doesn't
matter which node a run lands on; the jobs still request `-C ZEN4` so the
wall-clock caps mean the same thing everywhere.

## One-time setup

### 1. A Twee binary that runs on Vera

Easiest: build a **static** binary on your laptop (in your patched Twee
clone) and copy it over. It has no library dependencies, so Vera needs no
Haskell toolchain:

```bash
cabal install exe:twee --flags=static --installdir=$HOME/twee-static --install-method=copy
file $HOME/twee-static/twee        # should say "statically linked"
ssh <cid>@vera1.c3se.chalmers.se 'mkdir -p ~/bin ~/TPTP-v9.2.1'
scp $HOME/twee-static/twee <cid>@vera1.c3se.chalmers.se:bin/twee
# check it runs on Vera and has the patch
ssh <cid>@vera1.c3se.chalmers.se '~/bin/twee --expert-help | grep -- --deterministic'
```

Static linking needs the static libraries for GMP, libffi and glibc
(`libgmp-dev`, `libffi-dev`, `libc6-dev` on Ubuntu/Debian). Warnings about
`getpwnam` and similar functions in static glibc programs are harmless here.

**Fallback: Apptainer.** If the static build fails, build a container on a
Vera login node instead, from the repository root:

```bash
mkdir -p ~/containers
apptainer build ~/containers/twee.sif slurm/twee.def
```

Then set `TWEE_SIF` and point `TWEE_PATH` at `slurm/twee-apptainer` in
`slurm/vera.env` (both lines are in the example file).

### 2. Code, problems and TPTP axioms

```bash
ssh <cid>@vera1.c3se.chalmers.se          # from the Chalmers network or VPN
git clone https://github.com/solrun/neural-twitch
# only the problem files (~3,200 files; the full repo is ~6,000)
git clone --depth 1 --filter=blob:none --sparse https://github.com/WeAreDevo/ijcar26-twee_abstractions
git -C ijcar26-twee_abstractions sparse-checkout set data/TPTP
```

Cloning on the login node is fine: it only writes to your home directory on
shared storage. If GitHub isn't reachable from Vera, clone on your laptop and
`rsync` the folders over.

Copy only TPTP's `Axioms/` directory, not the whole TPTP tree: the home
directory has a 60,000-file quota (check usage with `C3SE_quota`).

```bash
# on your laptop
rsync -a $TPTP_ROOT/Axioms <cid>@vera1.c3se.chalmers.se:TPTP-v9.2.1/
```

### 3. Python environment and settings

```bash
cd ~/neural-twitch
module spider Python                       # pick a version
module load <the Python module>
python -m venv ~/venvs/nt && source ~/venvs/nt/bin/activate
pip install -r requirements.txt
cp slurm/vera.env.example slurm/vera.env   # then edit: module name, paths
```

Check it end to end in a short interactive job (login nodes are shared, so
keep even small Twee runs off them):

```bash
srun -A <project> -p vera -n 1 -c 2 -t 0:10:00 --pty bash
cd ~/neural-twitch && source slurm/vera.env
python -m nt.calibrate data/labels.jsonl $TWITCH_DIR/data/TPTP /tmp/check.jsonl \
    --limit 2 --wall-timeout 60 --workers 2
```

## Calibration

```bash
mkdir -p logs out
sbatch -A <project> --array=0-7 slurm/calibrate.sbatch
squeue -u $USER                                # watch progress
python -m nt.calibrate_report out/calibration_*.jsonl
```

8 shards × 32 cores, each shard about 38 problems × 2 flattening settings ×
2 runs with a 1000 s cap: at worst 5 rounds of 1000 s per shard, so the 4-hour
limit leaves ample room. The allocation is at most about 1,000 core-hours,
typically much less.

## Single-abstraction experiment

Choose the budget from the calibration report, then:

```bash
sbatch -A <project> --array=0-31 --export=ALL,MAX_CPS=<budget> slurm/single_runs.sbatch
cat out/single_*.jsonl > out/single.jsonl
```

Each problem runs under both flattening settings (15,222 Twee runs), so the
array has 32 shards to keep each one inside the 12-hour limit. Ratios are
computed within each shard; shards split by problem, so every problem's
baselines are in the same shard as its abstraction runs.

## Schedule diagnostic

```bash
sbatch slurm/schedule_diag.sbatch
python -m nt.schedule_diag data/labels.jsonl $TWITCH_DIR/data/TPTP out/schedule_diag.jsonl --report
```

48 runs on 48 cores with a 1000 s cap, so about 17 minutes. Low CPU use in
Grafana is expected: runs that prove quickly free their cores while the rest
run to the cap. `--report` prints the table from the output file, including a
partial one from a job that was cut off.

## Notes

* Extra script options go through `EXTRA_ARGS`, for example only one
  flattening setting: `--export=ALL,MAX_CPS=...,EXTRA_ARGS="--flatten off"`.
* The scripts write Twee's input files to `$TMPDIR`, which Slurm points at
  the node's local disk, so nothing touches shared storage per run.
* `--workers` defaults to the CPUs Slurm allocated (not the whole node).
