#!/usr/bin/env python3
"""Run stop/cancel regression tests by cancelling exports after they enter state=1."""

from __future__ import annotations

import argparse
import json
import os
import signal
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from dji_paths import get_project_root, get_support_dir  # noqa: E402

PROJECT_ROOT = get_project_root()
SUPPORT_DIR = get_support_dir()
EXPORT_SCRIPT = SCRIPT_DIR / "dji_studio_export_files.py"
APP_BUNDLE = PROJECT_ROOT / "runtime_candidate" / "DJI Studio.app"


def launch_runtime_if_needed() -> int | None:
    proc = subprocess.run(
        ["ps", "ax", "-o", "pid=", "-o", "args="],
        text=True,
        capture_output=True,
        check=True,
    )
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) == 2 and parts[0].isdigit() and str(APP_BUNDLE / "Contents/MacOS/DJIStudio") in parts[1]:
            return int(parts[0])
    subprocess.run(["open", "-na", str(APP_BUNDLE)], check=True)
    deadline = time.time() + 30
    while time.time() < deadline:
        proc = subprocess.run(
            ["ps", "ax", "-o", "pid=", "-o", "args="],
            text=True,
            capture_output=True,
            check=True,
        )
        for line in proc.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split(None, 1)
            if len(parts) == 2 and parts[0].isdigit() and str(APP_BUNDLE / "Contents/MacOS/DJIStudio") in parts[1]:
                return int(parts[0])
        time.sleep(0.5)
    return None


def compose_rows_for_output(output_dir: Path) -> list[sqlite3.Row]:
    db = SUPPORT_DIR / "media_db" / "data.db"
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "select id,state,outPath,exportId,firstSourcePath,synthesisTime from composeList where outPath like ? order by id",
            (str(output_dir.resolve()) + "/%",),
        ).fetchall()
        return rows
    finally:
        conn.close()


def wait_for_state1(output_dir: Path, timeout: float) -> tuple[list[dict[str, Any]], bool, float]:
    start = time.time()
    seen: list[dict[str, Any]] = []
    while time.time() - start < timeout:
        rows = [dict(r) for r in compose_rows_for_output(output_dir)]
        if rows:
            seen = rows
        if any(int(r["state"]) == 1 for r in rows):
            return rows, True, time.time() - start
        time.sleep(1)
    return seen, False, time.time() - start


def run_one(source: Path, output_root: Path, resolution_type: int, timeout: float) -> dict[str, Any]:
    sample_name = source.stem
    output_dir = output_root / sample_name
    manifest = output_root / f"{sample_name}_manifest.json"
    progress = output_root / f"{sample_name}_progress.json"
    if output_dir.exists():
        subprocess.run(["rm", "-rf", str(output_dir)], check=True)
    for path in [manifest, progress]:
        if path.exists():
            path.unlink()

    runtime_pid_before = launch_runtime_if_needed()
    cmd = [
        sys.executable,
        str(EXPORT_SCRIPT),
        str(source),
        "--output-dir",
        str(output_dir),
        "--resolution-type",
        str(resolution_type),
        "--manifest",
        str(manifest),
        "--progress-manifest",
        str(progress),
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    rows_at_cancel, reached_state1, waited = wait_for_state1(output_dir, timeout)
    if proc.poll() is None:
        proc.send_signal(signal.SIGTERM)
    try:
        stdout, stderr = proc.communicate(timeout=60)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()

    manifest_data = json.loads(manifest.read_text()) if manifest.exists() else None
    progress_data = json.loads(progress.read_text()) if progress.exists() else None
    remaining_rows = [dict(r) for r in compose_rows_for_output(output_dir)]
    runtime_ps = subprocess.run(
        ["ps", "ax", "-o", "pid=", "-o", "args="],
        text=True,
        capture_output=True,
        check=True,
    ).stdout.splitlines()
    runtime_pids_after = []
    runtime_bin = str(APP_BUNDLE / "Contents/MacOS/DJIStudio")
    for line in runtime_ps:
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) == 2 and parts[0].isdigit() and runtime_bin in parts[1]:
            runtime_pids_after.append(int(parts[0]))

    output_files = [str(p) for p in output_dir.glob("*.mp4")] if output_dir.exists() else []
    cancel = manifest_data.get("cancel", {}) if manifest_data else {}
    removed = cancel.get("removed", []) if isinstance(cancel, dict) else []
    removed_output = any(bool(item.get("removed_output")) for item in removed if isinstance(item, dict))
    runtime_terminated = bool(cancel.get("runtime_pids_terminated")) if isinstance(cancel, dict) else False
    passed = bool(
        reached_state1
        and manifest_data
        and manifest_data.get("cancelled") is True
        and runtime_terminated
        and not remaining_rows
        and not output_files
    )
    return {
        "source": str(source),
        "output_dir": str(output_dir),
        "manifest": str(manifest),
        "progress": str(progress),
        "runtime_pid_before": runtime_pid_before,
        "runtime_pids_after": runtime_pids_after,
        "waited_seconds": round(waited, 2),
        "reached_state1": reached_state1,
        "rows_at_cancel": rows_at_cancel,
        "remaining_rows": remaining_rows,
        "output_files_after": output_files,
        "manifest_data": manifest_data,
        "progress_data": progress_data,
        "stdout": stdout,
        "stderr": stderr,
        "returncode": proc.returncode,
        "passed": passed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="+", type=Path)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--resolution-type", type=int, default=14)
    parser.add_argument("--state1-timeout", type=float, default=180.0)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()

    output_root = args.output_root.expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    results = []
    for source in args.sources:
        results.append(run_one(source.expanduser().resolve(), output_root, args.resolution_type, args.state1_timeout))
    summary = {
        "output_root": str(output_root),
        "results": results,
        "all_passed": all(item["passed"] for item in results),
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(args.summary.resolve())
    return 0 if summary["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
