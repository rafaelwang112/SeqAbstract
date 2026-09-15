#!/usr/bin/env python3
"""Shim: synth honesty is included in the shared grader."""
import subprocess
import sys
from pathlib import Path


def find_grader(start: Path) -> Path:
    p = start
    for _ in range(8):
        cand = p / "grader" / "check_template.py"
        if cand.exists():
            return cand
        p = p.parent
    raise SystemExit("could not find ClockGate/grader/check_template.py")


here = Path(__file__).resolve().parent
sys.exit(subprocess.call([sys.executable, str(find_grader(here)), str(here)]))
