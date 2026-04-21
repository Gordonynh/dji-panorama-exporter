#!/usr/bin/env python3
"""Simple entrypoint for official DJI Studio panorama export."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from dji_paths import get_output_default, get_project_root, get_source_default  # noqa: E402

PRESET_MAP = {
    "6k": 12,
    "8k": 14,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", type=Path, nargs="?", default=get_source_default(), help="Directory containing OSV files")
    parser.add_argument("output_dir", type=Path, nargs="?", default=get_output_default(), help="Directory for exported panoramic MP4 files")
    parser.add_argument("--preset", choices=sorted(PRESET_MAP), default="8k")
    parser.add_argument("--pattern", default="*.OSV")
    parser.add_argument("--create-missing", action="store_true", default=True)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=get_project_root() / "output" / "export_run_manifest.json",
    )
    args = parser.parse_args()

    cmd = [
        sys.executable,
        str(SCRIPT_DIR / "dji_studio_export_source_dir.py"),
        str(args.input_dir.expanduser().resolve()),
        "--pattern",
        args.pattern,
        "--resolution-type",
        str(PRESET_MAP[args.preset]),
        "--output-dir",
        str(args.output_dir.expanduser().resolve()),
        "--manifest",
        str(args.manifest.expanduser().resolve()),
    ]
    if args.create_missing:
        cmd.append("--create-missing")

    proc = subprocess.run(cmd)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
