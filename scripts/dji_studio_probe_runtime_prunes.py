#!/usr/bin/env python3
"""Probe finer-grained runtime_candidate prunes against real export validation."""

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
    "remove_quicklook_host": ["Contents/PlugIns/DJIStudioQuickLookHost.app"],
    "remove_iconengines": ["Contents/PlugIns/iconengines"],
    "remove_networkinformation": ["Contents/PlugIns/networkinformation"],
    "remove_geometryloaders": ["Contents/PlugIns/geometryloaders"],
    "remove_sceneparsers": ["Contents/PlugIns/sceneparsers"],
    "remove_sqldrivers": ["Contents/PlugIns/sqldrivers"],
}


def run_variant(name: str, remove_paths: list[str], project_dir: Path, timeout: float) -> dict[str, object]:
    manifest = OUTPUT_DIR / f"runtime_prune_probe_{name}.json"
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
    for rel in remove_paths:
        cmd.extend(["--remove-path", rel])
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
        "remove_paths": remove_paths,
        "returncode": proc.returncode,
        "manifest": str(manifest),
        "export_success": bool(report.get("export_success")),
        "export_started": bool(report.get("export_started")),
        "output_exists": report.get("output_exists"),
        "final_states": report.get("batch_data", {}).get("final_states") if report else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", type=Path, default=get_support_dir() / "project" / "24")
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument(
        "--variant",
        action="append",
        default=[],
        help="Limit probing to one or more named variants",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=OUTPUT_DIR / "runtime_prune_probe_summary.json",
    )
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    project_dir = args.project_dir.expanduser().resolve()
    selected = VARIANTS
    if args.variant:
        selected = {name: VARIANTS[name] for name in args.variant}

    results = []
    for name, remove_paths in selected.items():
        results.append(run_variant(name, remove_paths, project_dir, args.timeout))

    summary = {"project_dir": str(project_dir), "variants": results}
    args.json_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.json_out.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
