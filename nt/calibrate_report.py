"""Combined calibration report over several output files (e.g. the shards
of a Slurm job array).

Usage:
    python -m nt.calibrate_report out/calibration_*.jsonl
"""

from __future__ import annotations

import json
import sys

from nt.calibrate import report


def main(paths: list[str]) -> None:
    rows = [json.loads(line) for p in paths for line in open(p) if line.strip()]
    print(f"{len(rows)} runs from {len(paths)} files")
    report(rows)


if __name__ == "__main__":
    main(sys.argv[1:])
