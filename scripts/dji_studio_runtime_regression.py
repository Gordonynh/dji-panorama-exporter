#!/usr/bin/env python3
"""Run runtime export regression across multiple live DJI Studio projects."""

from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
VALIDATE_SCRIPT = SCRIPT_DIR / "dji_studio_validate_runtime_export.py"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True)


def read_source_path(project_dir: Path) -> str | None:
    db = project_dir / "proj.db"
    if not db.exists():
        return None
    conn = sqlite3.connect(db)
    try:
        row = conn.execute("select path from mediaAssetInfo_v3 limit 1").fetchone()
        return str(row[0]) if row and row[0] else None
    finally:
        conn.close()


def read_video_summary(report_path: Path) -> dict[str, Any]:
    obj = json.loads(report_path.read_text())
    ffprobe = obj.get("ffprobe") or {}
    streams = ffprobe.get("streams") or []
    video = next((s for s in streams if s.get("codec_type") == "video"), streams[0] if streams else {})
    return {
        "width": video.get("width"),
        "height": video.get("height"),
        "fps": video.get("r_frame_rate"),
        "profile": video.get("profile"),
        "pix_fmt": video.get("pix_fmt"),
        "bit_rate": video.get("bit_rate"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dirs", nargs="+", type=Path, help="Live DJI Studio project directories")
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_regression_summary.json"),
    )
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    runs: list[dict[str, Any]] = []

    for idx, project_dir in enumerate(args.project_dirs, 1):
        project_dir = project_dir.expanduser().resolve()
        manifest = args.output.parent / f"runtime_regression_run_{idx}_{project_dir.name}.json"
        proc = run(
            [
                sys.executable,
                str(VALIDATE_SCRIPT),
                "--project-dir",
                str(project_dir),
                "--timeout",
                str(args.timeout),
                "--manifest",
                str(manifest),
            ]
        )
        run_entry: dict[str, Any] = {
            "project_dir": str(project_dir),
            "source_path": read_source_path(project_dir),
            "manifest": str(manifest),
            "returncode": proc.returncode,
            "stdout": proc.stdout[-2000:],
            "stderr": proc.stderr[-2000:],
        }
        if manifest.exists():
            report = json.loads(manifest.read_text())
            run_entry["export_success"] = report.get("export_success")
            run_entry["output_path"] = report.get("output_path")
            run_entry["video"] = read_video_summary(manifest)
        runs.append(run_entry)

    summary = {
        "projects": [str(p.expanduser().resolve()) for p in args.project_dirs],
        "runs": runs,
        "all_passed": all(r.get("returncode") == 0 and r.get("export_success") for r in runs),
    }
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(args.output.resolve())
    return 0 if summary["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
