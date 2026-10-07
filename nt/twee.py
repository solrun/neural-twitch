"""Run Twee on a TPTP problem with abstraction hints and a deterministic budget.

Requires a Twee built with `twee-print-stats.patch` (adds --print-stats) and
`twee-deterministic.patch` (adds --deterministic). Without the second patch,
Twee schedules interreduction and queue simplification by CPU time, so the
search, and the critical-pair count, depend on machine load.

Cost is the number of critical pairs considered; `--max-cps` turns it into a
budget.

Environment: TWEE_PATH (binary), TPTP_ROOT (for axiom includes).
"""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
import time
from dataclasses import dataclass, asdict

_STATS = re.compile(
    r"% twee-stats: considered_cps=(\d+) rules_created=(\d+) "
    r"active_rules=(\d+) solved=(true|false)")

# Critical pairs that count as one second for Twee's housekeeping schedule
# under --deterministic. About Twee's throughput on a laptop core (the first
# calibration measured ~2,800 CPs/s), so housekeeping runs roughly as often
# as it does in CPU-time mode.
CPS_PER_SECOND = 2000

# Flags Twitch always passes (see src/utils.py in the Twitch repo), plus
# deterministic scheduling.
BASE_FLAGS = ["--kbo-weight0-unary", "--deterministic", str(CPS_PER_SECOND)]


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
    # Twee's default. Off only for the flattening ablation (--no-flatten in
    # nt.calibrate and nt.single_runs).
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
            "active_rules": int(m.group(3)), "solved": m.group(4) == "true"}


def run(problem_path: str, abstractions: list[str], setting: Setting,
        max_cps: int, wall_timeout: float = 600.0,
        twee: str | None = None, tptp_root: str | None = None,
        extra_flags: list[str] | None = None) -> RunResult:
    twee = twee or os.environ["TWEE_PATH"]
    tptp_root = tptp_root or os.environ.get("TPTP_ROOT", "")
    with open(problem_path) as f:
        text = f.read()
    with tempfile.NamedTemporaryFile("w", suffix=".p", delete=False) as tmp:
        tmp.write(text)
        if abstractions:
            tmp.write("\n\n" + hints_block(abstractions))
        tmp_path = tmp.name
    cmd = [twee, tmp_path, *BASE_FLAGS, *setting.flags(),
           "--max-cps", str(max_cps), "--print-stats", "--quiet", "--no-proof",
           *(extra_flags or [])]
    if tptp_root:
        cmd += ["--root", tptp_root]
    start = time.monotonic()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=wall_timeout)
        wall = time.monotonic() - start
        stats = parse_stats(p.stdout)
        if stats is None:
            return RunResult("error", None, None, None, wall,
                             (p.stderr or p.stdout)[-2000:])
        status = "proved" if stats["solved"] else "budget"
        return RunResult(status, stats["cps"], stats["rules_created"],
                         stats["active_rules"], wall)
    except subprocess.TimeoutExpired:
        return RunResult("timeout", None, None, None, time.monotonic() - start)
    finally:
        os.unlink(tmp_path)
