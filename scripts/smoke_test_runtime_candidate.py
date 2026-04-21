#!/usr/bin/env python3
"""Launch the runtime candidate briefly and report the first missing dependency if it exits."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_BIN = PROJECT_ROOT / "runtime_candidate" / "DJI Studio.app" / "Contents" / "MacOS" / "DJIStudio"


def main() -> int:
    if not RUNTIME_BIN.exists():
        raise SystemExit(f"runtime candidate not found: {RUNTIME_BIN}")

    env = os.environ.copy()
    env["QT_DEBUG_PLUGINS"] = "1"
    env["DYLD_PRINT_LIBRARIES"] = "1"
    proc = subprocess.Popen(
        [str(RUNTIME_BIN)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    timed_out = False
    try:
        out, err = proc.communicate(timeout=8)
    except subprocess.TimeoutExpired:
        timed_out = True
        proc.terminate()
        try:
            out, err = proc.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            out, err = proc.communicate()

    missing = None
    match = re.search(r"Library not loaded: ([^\n]+)", err)
    if match:
        missing = match.group(1).strip()

    print(f"returncode={proc.returncode}")
    print(f"startup_ok={str(timed_out and missing is None).lower()}")
    if missing:
        print(f"missing_library={missing}")
    print("--- stderr ---")
    print(err[:12000])
    if missing:
        return 1
    if timed_out:
        return 0
    return 0 if proc.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
