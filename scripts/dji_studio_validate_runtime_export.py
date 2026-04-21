#!/usr/bin/env python3
"""Validate that the runtime candidate can perform a real export."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from dji_paths import CONFIG_PATH, get_project_root, get_support_dir  # noqa: E402

PROJECT_ROOT = get_project_root()
OUTPUT_DIR = PROJECT_ROOT / "output"
RUNTIME_ROOT = PROJECT_ROOT / "runtime_candidate" / "DJI Studio.app"
BUILD_SCRIPT = SCRIPT_DIR / "build_runtime_candidate.py"
SMOKE_SCRIPT = SCRIPT_DIR / "smoke_test_runtime_candidate.py"
BATCH_SCRIPT = SCRIPT_DIR / "dji_studio_batch_internal_export.py"
SET_MODE_SCRIPT = SCRIPT_DIR / "set_component_mode.py"
VENDOR_ROOT = PROJECT_ROOT / "vendor" / "DJI Studio.app"


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


def ffprobe_json(path: Path) -> dict[str, object]:
    proc = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_streams",
            "-show_format",
            str(path),
        ],
        check=True,
    )
    return json.loads(proc.stdout)


def safe_file_info(path: Path) -> dict[str, object]:
    info: dict[str, object] = {
        "exists": path.exists(),
        "path": str(path),
    }
    if path.exists():
        info["size_bytes"] = path.stat().st_size
        try:
            info["ffprobe"] = ffprobe_json(path)
        except subprocess.CalledProcessError as exc:
            info["ffprobe_error"] = {
                "returncode": exc.returncode,
                "stderr": exc.stderr[-2000:] if exc.stderr else "",
                "stdout": exc.stdout[-2000:] if exc.stdout else "",
            }
    return info


def kill_dji_processes() -> list[dict[str, object]]:
    proc = subprocess.run(
        ["ps", "-axo", "pid=,command="],
        text=True,
        capture_output=True,
        check=True,
    )
    killed: list[dict[str, object]] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        pid_str, _, command = line.partition(" ")
        if not pid_str.isdigit():
            continue
        if "DJIStudio" not in command and "DJI Studio.app" not in command and "DJIStudioQuickLookHost" not in command:
            continue
        pid = int(pid_str)
        if pid == os.getpid():
            continue
        try:
            os.kill(pid, 15)
            killed.append({"pid": pid, "command": command, "signal": 15})
        except ProcessLookupError:
            continue
        except PermissionError:
            killed.append({"pid": pid, "command": command, "signal": "denied"})
    time.sleep(2)
    return killed


def restore_vendor_paths(relative_paths: list[str]) -> list[str]:
    restored: list[str] = []
    for rel in relative_paths:
        source = VENDOR_ROOT / rel
        target = RUNTIME_ROOT / rel
        if not source.exists():
            raise FileNotFoundError(f"vendor path missing: {source}")
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target)
            else:
                target.unlink()
        if source.is_dir() and not source.is_symlink():
            shutil.copytree(source, target, symlinks=True, ignore_dangling_symlinks=True)
        else:
            shutil.copy2(source, target, follow_symlinks=False)
        restored.append(rel)
    return restored


def remove_runtime_paths(relative_paths: list[str]) -> list[str]:
    removed: list[str] = []
    for rel in relative_paths:
        target = RUNTIME_ROOT / rel
        if not target.exists():
            continue
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        else:
            target.unlink()
        removed.append(rel)
    return removed


def pending_compose_tasks() -> list[dict[str, object]]:
    db = get_support_dir() / "media_db" / "data.db"
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "select id,state,outPath,firstSourcePath from composeList where state in (0,1) order by id"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def cleanup_project_owned_pending_tasks() -> list[int]:
    db = get_support_dir() / "media_db" / "data.db"
    conn = sqlite3.connect(db)
    try:
        rows = conn.execute(
            "select id, outPath, exportId from composeList where state in (0,1) order by id"
        ).fetchall()
        removed: list[int] = []
        for task_id, out_path, export_id in rows:
            if not out_path:
                continue
            out_path_str = str(out_path)
            if "/Desktop/Projects/DJIStudio/output/runtime_export_" not in out_path_str:
                continue
            conn.execute("delete from composeList where id = ?", (task_id,))
            if export_id:
                conn.execute("delete from exportDataTable where exportId = ?", (export_id,))
            removed.append(int(task_id))
        conn.commit()
        return removed
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", type=Path, default=get_support_dir() / "project" / "24")
    parser.add_argument("--resolution-type", type=int, default=14)
    parser.add_argument("--remove-quicklook", action="store_true")
    parser.add_argument(
        "--rebuild-runtime",
        dest="rebuild_runtime",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Rebuild runtime_candidate before validation (default: true)",
    )
    parser.add_argument(
        "--restore-path",
        action="append",
        default=[],
        help="Restore one relative path from vendor into runtime_candidate before export validation",
    )
    parser.add_argument(
        "--remove-path",
        action="append",
        default=[],
        help="Remove one relative path from runtime_candidate after build/restore and before export validation",
    )
    parser.add_argument(
        "--kill-existing",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Terminate running DJIStudio/DJIStudioQuickLookHost processes before validation",
    )
    parser.add_argument(
        "--cleanup-pending",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Delete stale project-owned pending compose tasks created by previous runtime export probes",
    )
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=OUTPUT_DIR / "runtime_export_validation.json",
    )
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    project_dir = args.project_dir.expanduser().resolve()
    ts = int(time.time() * 1000)
    export_dir = OUTPUT_DIR / f"runtime_export_{ts}"
    export_dir.mkdir(parents=True, exist_ok=True)
    batch_manifest = OUTPUT_DIR / f"runtime_export_batch_{ts}.json"

    original_config = CONFIG_PATH.read_text(encoding="utf-8") if CONFIG_PATH.exists() else None
    report: dict[str, object] = {
        "project_dir": str(project_dir),
        "runtime_app": str(RUNTIME_ROOT),
        "remove_quicklook": args.remove_quicklook,
        "resolution_type": args.resolution_type,
        "export_dir": str(export_dir),
        "batch_manifest": str(batch_manifest),
        "restore_paths": args.restore_path,
        "remove_paths": args.remove_path,
        "kill_existing": args.kill_existing,
        "cleanup_pending": args.cleanup_pending,
    }

    try:
        if args.kill_existing:
            report["killed_processes"] = kill_dji_processes()
        if args.cleanup_pending:
            report["cleaned_pending_task_ids"] = cleanup_project_owned_pending_tasks()

        if args.rebuild_runtime:
            build = run(["python3", str(BUILD_SCRIPT)], check=True)
            report["build"] = {
                "returncode": build.returncode,
                "stdout": build.stdout[-4000:],
                "stderr": build.stderr[-4000:],
            }
        else:
            report["build"] = {"skipped": True}

        quicklook_path = RUNTIME_ROOT / "Contents" / "PlugIns" / "DJIStudioQuickLookHost.app"
        report["quicklook_present_before"] = quicklook_path.exists()
        if args.remove_quicklook and quicklook_path.exists():
            shutil.rmtree(quicklook_path)
        report["quicklook_present_after"] = quicklook_path.exists()
        if args.restore_path:
            report["restored_paths"] = restore_vendor_paths(args.restore_path)
        if args.remove_path:
            report["removed_paths"] = remove_runtime_paths(args.remove_path)

        smoke = run(["python3", str(SMOKE_SCRIPT)], check=False)
        report["smoke"] = {
            "returncode": smoke.returncode,
            "startup_ok": "startup_ok=true" in smoke.stdout,
            "stdout": smoke.stdout[-12000:],
            "stderr": smoke.stderr[-4000:],
        }

        run(["python3", str(SET_MODE_SCRIPT), "runtime_candidate"], check=True)
        report["preexisting_pending_tasks"] = pending_compose_tasks()

        batch = run(
            [
                "python3",
                str(BATCH_SCRIPT),
                str(project_dir),
                "--output-dir",
                str(export_dir),
                "--resolution-type",
                str(args.resolution_type),
                "--timeout",
                str(args.timeout),
                "--manifest",
                str(batch_manifest),
                "--launch-if-needed",
            ],
            check=False,
        )
        report["batch"] = {
            "returncode": batch.returncode,
            "stdout": batch.stdout[-4000:],
            "stderr": batch.stderr[-4000:],
        }

        if batch_manifest.exists():
            batch_data = json.loads(batch_manifest.read_text(encoding="utf-8"))
            report["batch_data"] = batch_data
            injected = batch_data.get("injected") or []
            if injected:
                output_path = Path(injected[0]["output_path"])
                report["output_path"] = str(output_path)
                report["output_exists"] = output_path.exists()
                report["output_info"] = safe_file_info(output_path)
                if report["output_info"].get("ffprobe"):
                    report["ffprobe"] = report["output_info"]["ffprobe"]
                report["export_started"] = bool(report["output_info"].get("exists"))
        report["export_success"] = bool(
            report.get("output_exists")
            and report.get("batch_data", {}).get("final_states")
            and all(int(v.get("state", -1)) == 2 for v in report["batch_data"]["final_states"].values())
            and "ffprobe" in report
        )
        if report.get("preexisting_pending_tasks"):
            report["blocked_by_preexisting_queue"] = True
    finally:
        if original_config is not None:
            CONFIG_PATH.write_text(original_config, encoding="utf-8")

    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.manifest.resolve())
    return 0 if report.get("export_success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
