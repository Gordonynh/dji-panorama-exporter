#!/usr/bin/env python3
"""Run the full DJI Studio export pipeline: health check, export, report, and mapping."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from dji_paths import get_output_default, get_project_root, get_source_default  # noqa: E402


def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", type=Path, nargs="?", default=get_source_default(), help="Directory containing source OSV files")
    parser.add_argument("output_dir", type=Path, nargs="?", default=get_output_default(), help="Directory for exported panoramic MP4 files")
    parser.add_argument("--preset", choices=("6k", "8k"), default="8k")
    parser.add_argument("--pattern", default="*.OSV")
    parser.add_argument(
        "--skip-export",
        action="store_true",
        help="Do not export again; only run healthcheck/report/mapping on an existing output directory",
    )
    parser.add_argument(
        "--prefix",
        default="pipeline_run",
        help="Prefix used for generated JSON/CSV artifacts under exports/dji_studio_live",
    )
    args = parser.parse_args()

    input_dir = args.input_dir.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    artifact_dir = get_project_root() / "output"

    healthcheck_json = artifact_dir / f"{args.prefix}_healthcheck.json"
    export_manifest = artifact_dir / f"{args.prefix}_export_manifest.json"
    report_json = artifact_dir / f"{args.prefix}_report.json"
    report_csv = artifact_dir / f"{args.prefix}_report.csv"
    mapping_json = artifact_dir / f"{args.prefix}_mapping.json"
    mapping_csv = artifact_dir / f"{args.prefix}_mapping.csv"

    run(
        [
            sys.executable,
            str(SCRIPT_DIR / "dji_studio_healthcheck.py"),
            "--json-out",
            str(healthcheck_json),
        ]
    )

    if not args.skip_export:
        run(
            [
                sys.executable,
                str(SCRIPT_DIR / "dji_studio_export.py"),
                str(input_dir),
                str(output_dir),
                "--preset",
                args.preset,
                "--pattern",
                args.pattern,
                "--manifest",
                str(export_manifest),
            ]
        )

    run(
        [
            sys.executable,
            str(SCRIPT_DIR / "dji_studio_report_exports.py"),
            str(output_dir),
            "--json-out",
            str(report_json),
            "--csv-out",
            str(report_csv),
        ]
    )

    run(
        [
            sys.executable,
            str(SCRIPT_DIR / "dji_studio_map_exports.py"),
            str(input_dir),
            str(output_dir),
            "--pattern",
            args.pattern,
            "--report-json",
            str(report_json),
            "--json-out",
            str(mapping_json),
            "--csv-out",
            str(mapping_csv),
        ]
    )

    print("healthcheck", healthcheck_json)
    if not args.skip_export:
        print("manifest", export_manifest)
    print("report_json", report_json)
    print("report_csv", report_csv)
    print("mapping_json", mapping_json)
    print("mapping_csv", mapping_csv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
