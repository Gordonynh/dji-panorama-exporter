#!/usr/bin/env python3
"""Probe which removed runtime_candidate paths are required for real export."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from dji_paths import get_project_root, get_support_dir


PROJECT_ROOT = get_project_root()
SCRIPT_DIR = PROJECT_ROOT / "scripts"
VALIDATE_SCRIPT = SCRIPT_DIR / "dji_studio_validate_runtime_export.py"
OUTPUT_DIR = PROJECT_ROOT / "output"

VARIANTS: dict[str, list[str]] = {
    "baseline": [],
    "sqldrivers": ["Contents/PlugIns/sqldrivers"],
    "sqldrivers_network": [
        "Contents/PlugIns/sqldrivers",
        "Contents/PlugIns/networkinformation",
    ],
    "all_removed_plugins": [
        "Contents/PlugIns/sqldrivers",
        "Contents/PlugIns/networkinformation",
        "Contents/PlugIns/geometryloaders",
        "Contents/PlugIns/sceneparsers",
        "Contents/PlugIns/iconengines",
    ],
}


def run_variant(name: str, restore_paths: list[str], project_dir: Path, timeout: float) -> dict[str, object]:
    manifest = OUTPUT_DIR / f"runtime_restore_probe_{name}.json"
    cmd = [
        "python3",
        str(VALIDATE_SCRIPT),
        "--project-dir",
        str(project_dir),
        "--timeout",
        str(timeout),
        "--manifest",
        str(manifest),
    ]
    for rel in restore_paths:
        cmd.extend(["--restore-path", rel])
    proc = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    report = {}
    if manifest.exists():
        report = json.loads(manifest.read_text(encoding="utf-8"))
    return {
        "name": name,
        "restore_paths": restore_paths,
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
        "manifest": str(manifest),
        "export_success": bool(report.get("export_success")),
        "output_path": report.get("output_path"),
        "output_exists": report.get("output_exists"),
        "final_states": report.get("batch_data", {}).get("final_states") if report else None,
        "report": report,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", type=Path, default=get_support_dir() / "project" / "67")
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument(
        "--json-out",
        type=Path,
        default=OUTPUT_DIR / "runtime_restore_probe_summary.json",
    )
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for name, restore_paths in VARIANTS.items():
        results.append(run_variant(name, restore_paths, args.project_dir.expanduser().resolve(), args.timeout))

    summary = {
        "project_dir": str(args.project_dir.expanduser().resolve()),
        "variants": results,
    }
    args.json_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.json_out.resolve())
    return 0 if any(v.get("export_success") for v in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
