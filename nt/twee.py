"""Run Twee on a TPTP problem with abstraction hints and a deterministic budget.

Requires a Twee built with `twee-print-stats.patch` (adds --print-stats) and
`twee-deterministic.patch` (adds --deterministic and --deterministic-alloc).
Without the second patch, Twee schedules interreduction and queue
simplification by CPU time, so the search, and the critical-pair count,
depend on machine load.

The housekeeping schedule is given as a string:
  "none"      Twee's normal CPU-time schedule (not reproducible),
  "cps:N"     --deterministic N: N critical pairs count as one second,
  "alloc:N"   --deterministic-alloc N: N bytes allocated count as one second.
A bare number means "cps:N".

Cost is the number of critical pairs considered; `--max-cps` turns it into a
budget.

Environment: TWEE_PATH (binary), TPTP_ROOT (for axiom includes).
"""

from __future__ import annotations

import os
import re
import signal
import subprocess
import tempfile
import time
from dataclasses import dataclass, asdict

_STATS = re.compile(
    r"% twee-stats: considered_cps=(\d+) rules_created=(\d+) "
    r"active_rules=(\d+) solved=(true|false)"
    r"(?: allocated_bytes=(\d+) cpu_seconds=([0-9.eE+-]+))?")

# Critical pairs that count as one second for Twee's housekeeping schedule
# under --deterministic. About Twee's throughput on a laptop core (the first
# calibration measured ~2,800 CPs/s), so housekeeping runs roughly as often
# as it does in CPU-time mode.
# Updated to 7000 for running on Vera nodes.
CPS_PER_SECOND = 7000

# Bytes allocated that count as one second under --deterministic-alloc: the
# median allocation rate of Twee's normal schedule on Vera Zen 4 nodes
# (2.56-2.96 GB per CPU second in nt.schedule_diag). The default schedule:
# it is deterministic like the CP clock, but tracks CPU time across problems
# and enforces Twee's housekeeping time budgets (calibration 2026-10-13:
# 0 mismatches, 6 more baselines proved per flattening setting than
# cps:7000, ~10-15% less wall time per CP).
ALLOC_PER_SECOND = 2_750_000_000

DEFAULT_SCHEDULE = f"alloc:{ALLOC_PER_SECOND}"

# Flags Twitch always passes (see src/utils.py in the Twitch repo).
BASE_FLAGS = ["--kbo-weight0-unary"]


def schedule_flags(schedule: str | int | None) -> list[str]:
    """Twee flags for a housekeeping schedule (see the module docstring)."""
    if schedule in (None, "", "none"):
        return []
    s = str(schedule)
    kind, _, value = s.rpartition(":")
    if kind in ("", "cps"):
        return ["--deterministic", str(int(value))]
    if kind == "alloc":
        return ["--deterministic-alloc", str(int(value))]
    raise ValueError(f"bad schedule {schedule!r}: use none, cps:N or alloc:N")


def default_workers() -> int:
    """CPUs this process may use. Under Slurm, os.cpu_count() reports the
    whole node, not the allocation, so use the affinity mask instead."""
    try:
        return len(os.sched_getaffinity(0))
    except AttributeError:  # not Linux
        return os.cpu_count() or 1


def select_shard(problems: list[str], spec: str) -> list[str]:
    """Problems for shard "K/N" (0 <= K < N): every N-th problem starting at
    K, so shards get a similar mix of easy and hard problems."""
    if not spec:
        return problems
    k, n = (int(x) for x in spec.split("/"))
    if not 0 <= k < n:
        raise ValueError(f"bad shard {spec!r}: need 0 <= K < N")
    return problems[k::n]


@dataclass
class Setting:
    """A Twee abstraction-weight setting (Twitch Sect. 4.1)."""
    factor: float = 0.5        # --hint-skel-factor
    cost: float = 0.0          # --hint-skel-cost
    # Twee's default. nt.calibrate and nt.single_runs run both settings
    # (--flatten both|on|off).
    flatten_goal: bool = True

    def flags(self) -> list[str]:
        return ["--hint-skel-factor", str(self.factor),
                "--hint-skel-cost", str(self.cost),
                "--flatten-goal" if self.flatten_goal else "--no-flatten-goal"]

    def key(self) -> str:
        return f"f{self.factor}_c{self.cost}_{'flat' if self.flatten_goal else 'noflat'}"


@dataclass
class RunResult:
    status: str                # "proved" | "budget" | "timeout" | "error"
    cps: int | None            # critical pairs considered
    rules_created: int | None
    active_rules: int | None
    wall: float
    error: str = ""
    allocated_bytes: int | None = None   # whole run, if Twee reports it
    cpu_seconds: float | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def hints_block(abstractions: list[str]) -> str:
    """TPTP lines that pass abstractions to Twee, in the format Twitch uses."""
    return "\n".join(f"cnf(hint_{i}, axiom,\n\t $hint( {a} )).\n"
                     for i, a in enumerate(abstractions, start=1))


def parse_stats(output: str) -> dict | None:
    m = _STATS.search(output)
    if not m:
        return None
    return {"cps": int(m.group(1)), "rules_created": int(m.group(2)),
            "active_rules": int(m.group(3)), "solved": m.group(4) == "true",
            "allocated_bytes": int(m.group(5)) if m.group(5) else None,
            "cpu_seconds": float(m.group(6)) if m.group(6) else None}


def _run_capped(cmd: list[str], wall_timeout: float) -> tuple[str, str]:
    """Run cmd and return (stdout, stderr); raise subprocess.TimeoutExpired
    after wall_timeout seconds.

    The command runs in its own process group, and a timeout kills the whole
    group. subprocess.run(timeout=...) kills only the process it started, so
    when TWEE_PATH is a wrapper script (or the Apptainer wrapper) the real
    Twee would keep running as an orphan, holding a core until it finished."""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, start_new_session=True)
    try:
        return p.communicate(timeout=wall_timeout)
    except subprocess.TimeoutExpired:
        _kill_group(p)
        raise
    except BaseException:  # e.g. KeyboardInterrupt: don't leave Twee behind
        _kill_group(p)
        raise


def _kill_group(p: subprocess.Popen) -> None:
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    p.communicate()


def run(problem_path: str, abstractions: list[str], setting: Setting,
        max_cps: int, wall_timeout: float = 600.0,
        twee: str | None = None, tptp_root: str | None = None,
        extra_flags: list[str] | None = None,
        schedule: str | int | None = DEFAULT_SCHEDULE) -> RunResult:
    """Run Twee once under the given housekeeping schedule (see the module
    docstring). "none" runs Twee's normal CPU-time schedule, whose CP counts
    are not reproducible."""
    twee = twee or os.environ["TWEE_PATH"]
    tptp_root = tptp_root or os.environ.get("TPTP_ROOT", "")
    with open(problem_path) as f:
        text = f.read()
    with tempfile.NamedTemporaryFile("w", suffix=".p", delete=False) as tmp:
        tmp.write(text)
        if abstractions:
            tmp.write("\n\n" + hints_block(abstractions))
        tmp_path = tmp.name
    sched = schedule_flags(schedule)
    cmd = [twee, tmp_path, *BASE_FLAGS, *sched, *setting.flags(),
           "--max-cps", str(max_cps), "--print-stats", "--quiet", "--no-proof",
           *(extra_flags or [])]
    if tptp_root:
        cmd += ["--root", tptp_root]
    start = time.monotonic()
    try:
        out, err = _run_capped(cmd, wall_timeout)
        wall = time.monotonic() - start
        stats = parse_stats(out)
        if stats is None:
            return RunResult("error", None, None, None, wall, (err or out)[-2000:])
        status = "proved" if stats["solved"] else "budget"
        return RunResult(status, stats["cps"], stats["rules_created"],
                         stats["active_rules"], wall,
                         allocated_bytes=stats["allocated_bytes"],
                         cpu_seconds=stats["cpu_seconds"])
    except subprocess.TimeoutExpired:
        return RunResult("timeout", None, None, None, time.monotonic() - start)
    finally:
        os.unlink(tmp_path)
