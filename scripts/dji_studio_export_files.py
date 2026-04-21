#!/usr/bin/env python3
"""Export explicit OSV files via temporary live DJI Studio projects, then optionally clean them up."""

from __future__ import annotations

import argparse
import json
import os
import shutil
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

from dji_paths import get_app_bin, get_project_root, get_support_dir  # noqa: E402
from dji_studio_export_source_dir import create_live_project_for_source  # noqa: E402

PROJECT_ROOT = get_project_root()
SUPPORT_DIR = get_support_dir()
BATCH_SCRIPT = SCRIPT_DIR / "dji_studio_batch_internal_export.py"
APP_BIN = get_app_bin().resolve()


def cleanup_live_project(project_id: int, support_dir: Path) -> dict[str, Any]:
    media_db = support_dir / "media_db" / "data.db"
    live_project_dir = support_dir / "project" / str(project_id)
    result: dict[str, Any] = {
        "project_id": project_id,
        "live_project_dir": str(live_project_dir),
        "removed_dir": False,
        "removed_db_row": False,
    }
    if live_project_dir.exists():
        shutil.rmtree(live_project_dir)
        result["removed_dir"] = True

    conn = sqlite3.connect(media_db)
    try:
        cur = conn.execute("delete from project_draft_v2 where id = ?", (project_id,))
        conn.commit()
        result["removed_db_row"] = cur.rowcount > 0
    finally:
        conn.close()
    return result


def cleanup_clone_dir(clone_dir: str | None) -> dict[str, Any] | None:
    if not clone_dir:
        return None
    path = Path(clone_dir)
    if path.exists():
        shutil.rmtree(path)
        return {"clone_dir": str(path), "removed": True}
    return {"clone_dir": str(path), "removed": False}


def iter_runtime_pids() -> list[int]:
    proc = subprocess.run(
        ["ps", "ax", "-o", "pid=", "-o", "args="],
        text=True,
        capture_output=True,
        check=True,
    )
    pids: list[int] = []
    app_bin = str(APP_BIN)
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) != 2 or not parts[0].isdigit():
            continue
        pid = int(parts[0])
        args = parts[1]
        if app_bin in args and "QuickLookHost" not in args and "crashpad_handler" not in args:
            pids.append(pid)
    return pids


def terminate_runtime_processes() -> list[int]:
    terminated: list[int] = []
    for pid in iter_runtime_pids():
        try:
            os.kill(pid, signal.SIGTERM)
            terminated.append(pid)
        except ProcessLookupError:
            continue
    return terminated


def collect_task_ids(*, batch_manifests: list[Path], progress_manifests: list[Path]) -> list[int]:
    task_ids: set[int] = set()
    for path in batch_manifests:
        if not path.exists():
            continue
        try:
            data = load_json(path) or {}
        except Exception:
            continue
        for item in data.get("injected", []):
            task_id = item.get("task_id")
            if task_id is not None:
                task_ids.add(int(task_id))
    for path in progress_manifests:
        if not path.exists():
            continue
        try:
            data = load_json(path) or {}
        except Exception:
            continue
        for item in data.get("items", []):
            task_id = item.get("task_id")
            if task_id is not None:
                task_ids.add(int(task_id))
    return sorted(task_ids)


def find_pending_tasks_for_run(
    *,
    support_dir: Path,
    output_dir: Path,
    source_files: list[str],
    task_ids: list[int],
) -> list[dict[str, Any]]:
    db = support_dir / "media_db" / "data.db"
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    try:
        rows: list[sqlite3.Row] = []
        if task_ids:
            rows.extend(
                conn.execute(
                    f"select id, state, outPath, exportId, firstSourcePath from composeList where id in ({','.join('?' for _ in task_ids)})",
                    task_ids,
                ).fetchall()
            )
        rows.extend(
            conn.execute(
                "select id, state, outPath, exportId, firstSourcePath from composeList where state in (0,1)"
            ).fetchall()
        )
        output_dir_str = str(output_dir.resolve())
        source_set = {str(Path(src).resolve()) for src in source_files}
        matched: dict[int, dict[str, Any]] = {}
        running_found = any(int(row["state"]) == 1 for row in rows)
        for row in rows:
            task_id = int(row["id"])
            out_path = str(row["outPath"] or "")
            first_source = str(row["firstSourcePath"] or "")
            by_id = task_id in task_ids
            by_output = bool(out_path) and out_path.startswith(output_dir_str + "/")
            by_source = bool(first_source) and str(Path(first_source).resolve()) in source_set
            if by_id or by_output or by_source:
                matched[task_id] = dict(row)
        return sorted(matched.values(), key=lambda item: int(item["id"]))
    finally:
        conn.close()


def cancel_compose_tasks(
    *,
    support_dir: Path,
    output_dir: Path,
    source_files: list[str],
    task_ids: list[int],
) -> dict[str, Any]:
    rows = find_pending_tasks_for_run(
        support_dir=support_dir,
        output_dir=output_dir,
        source_files=source_files,
        task_ids=task_ids,
    )
    if not rows:
        return {"task_ids": [], "removed": [], "runtime_pids_terminated": []}
    db = support_dir / "media_db" / "data.db"
    conn = sqlite3.connect(db)
    removed: list[dict[str, Any]] = []
    runtime_pids_terminated: list[int] = []
    try:
        running_found = any(int(row["state"]) == 1 for row in rows)
        if running_found:
            runtime_pids_terminated = terminate_runtime_processes()
            time.sleep(1.0)
        for row in rows:
            task_id = int(row["id"])
            out_path = Path(str(row["outPath"])) if row["outPath"] else None
            export_id = row["exportId"]
            conn.execute("delete from composeList where id = ?", (task_id,))
            if export_id:
                conn.execute("delete from exportDataTable where exportId = ?", (export_id,))
            removed_output = False
            if out_path and out_path.exists():
                try:
                    out_path.unlink()
                    removed_output = True
                except OSError:
                    removed_output = False
            removed.append(
                {
                    "task_id": task_id,
                    "state": int(row["state"]),
                    "outPath": str(out_path) if out_path else None,
                    "firstSourcePath": row.get("firstSourcePath"),
                    "removed_output": removed_output,
                    "exportId": export_id,
                }
            )
        conn.commit()
    finally:
        conn.close()
    return {
        "task_ids": [int(row["id"]) for row in rows],
        "removed": removed,
        "runtime_pids_terminated": runtime_pids_terminated,
    }


def run_batch(
    project_dirs: list[str],
    output_dir: Path,
    resolution_type: int,
    timeout: float,
    manifest: Path,
    launch_if_needed: bool,
    foreground_launch: bool,
    *,
    frame_rate: int | None,
    bitrate_mode: str,
    custom_bitrate_mbps: float | None,
    denoise: bool,
    denoise_mode: str,
    ten_bit: bool,
    parallel_count: int,
    progress_manifest: Path | None,
) -> subprocess.Popen[str]:
    cmd = [
        sys.executable,
        str(BATCH_SCRIPT),
        *project_dirs,
        "--output-dir",
        str(output_dir),
        "--resolution-type",
        str(resolution_type),
        "--timeout",
        str(timeout),
        "--manifest",
        str(manifest),
        "--launch-if-needed",
        "--bitrate-mode",
        bitrate_mode,
        "--denoise-mode",
        denoise_mode,
        "--parallel-count",
        str(parallel_count),
    ]
    if frame_rate is not None:
        cmd.extend(["--frame-rate", str(frame_rate)])
    if custom_bitrate_mbps is not None:
        cmd.extend(["--custom-bitrate-mbps", str(custom_bitrate_mbps)])
    if denoise:
        cmd.append("--denoise")
    else:
        cmd.append("--no-denoise")
    if ten_bit:
        cmd.append("--ten-bit")
    else:
        cmd.append("--no-ten-bit")
    if foreground_launch:
        cmd.append("--foreground-launch")
    if progress_manifest is not None:
        cmd.extend(["--progress-manifest", str(progress_manifest)])
    return subprocess.Popen(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def chunked[T](items: list[T], size: int) -> list[list[T]]:
    size = max(1, size)
    return [items[i:i + size] for i in range(0, len(items), size)]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text()) if path.exists() else None


def write_progress_manifest(progress_path: Path, payload: dict[str, Any]) -> None:
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    progress_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path, help="OSV files to export")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--resolution-type", type=int, default=14)
    parser.add_argument("--support-dir", type=Path, default=SUPPORT_DIR)
    parser.add_argument("--template-project-dir", type=Path, default=get_support_dir() / "project" / "24")
    parser.add_argument("--timeout", type=float, default=900.0)
    parser.add_argument("--cleanup-temp-projects", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--foreground-launch", action="store_true")
    parser.add_argument("--frame-rate", type=int, choices=[24, 25, 30, 50, 60], default=None)
    parser.add_argument("--bitrate-mode", choices=["default", "low", "medium", "high", "custom"], default="default")
    parser.add_argument("--custom-bitrate-mbps", type=float, default=None)
    parser.add_argument("--denoise", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--denoise-mode", choices=["performance", "quality"], default="quality")
    parser.add_argument("--ten-bit", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--parallel-count", type=int, default=1)
    parser.add_argument("--progress-manifest", type=Path, default=None)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=PROJECT_ROOT / "output" / "export_files_manifest.json",
    )
    args = parser.parse_args()

    support_dir = args.support_dir.expanduser().resolve()
    template_project_dir = args.template_project_dir.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)

    created_projects: list[dict[str, Any]] = []
    cleanup_actions: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    batch_manifests: list[str] = []
    batch_manifest_paths: list[Path] = []
    batch_progress_paths: list[Path] = []
    progress_state: dict[str, dict[str, Any]] = {
        str(p.expanduser().resolve()): {
            "source": str(p.expanduser().resolve()),
            "status": "pending",
            "progress": 0.0,
            "output_path": str(output_dir / f"{p.expanduser().resolve().stem}_official.mp4"),
            "size_bytes": 0,
            "expected_size_bytes": 0,
        }
        for p in args.files
    }

    result: dict[str, Any] | None = None
    returncode = 1
    batch_manifest: Path | None = None
    cancelled = False
    active_batch_proc: subprocess.Popen[str] | None = None

    def handle_cancel(signum, _frame) -> None:  # type: ignore[no-untyped-def]
        nonlocal cancelled, active_batch_proc
        cancelled = True
        if active_batch_proc and active_batch_proc.poll() is None:
            try:
                active_batch_proc.terminate()
            except ProcessLookupError:
                pass

    signal.signal(signal.SIGTERM, handle_cancel)
    signal.signal(signal.SIGINT, handle_cancel)

    try:
        for source in args.files:
            source = source.expanduser().resolve()
            if not source.exists():
                errors.append({"source": str(source), "error": "missing_source"})
                progress_state[str(source)]["status"] = "error"
                continue
            try:
                created = create_live_project_for_source(source, template_project_dir, support_dir)
                created["source"] = str(source)
                created_projects.append(created)
                progress_state[str(source)]["status"] = "prepared"
            except Exception as exc:  # noqa: BLE001
                errors.append({"source": str(source), "error": str(exc)})
                progress_state[str(source)]["status"] = "error"

        batch_reports: list[dict[str, Any]] = []
        runnable_chunks = chunked(created_projects, args.parallel_count)
        for chunk_index, chunk in enumerate(runnable_chunks, 1):
            if cancelled:
                returncode = 130
                break
            runnable_projects = [item["project_dir"] for item in chunk]
            if not runnable_projects:
                continue
            batch_manifest = args.manifest.parent / f"{args.manifest.stem}_batch_{chunk_index}.json"
            batch_progress = args.manifest.parent / f"{args.manifest.stem}_progress_{chunk_index}.json"
            batch_manifest_paths.append(batch_manifest)
            batch_progress_paths.append(batch_progress)
            batch_proc = run_batch(
                runnable_projects,
                output_dir,
                args.resolution_type,
                args.timeout,
                batch_manifest,
                launch_if_needed=True,
                foreground_launch=args.foreground_launch,
                frame_rate=args.frame_rate,
                bitrate_mode=args.bitrate_mode,
                custom_bitrate_mbps=args.custom_bitrate_mbps,
                denoise=args.denoise,
                denoise_mode=args.denoise_mode,
                ten_bit=args.ten_bit,
                parallel_count=args.parallel_count,
                progress_manifest=batch_progress if args.progress_manifest else None,
            )
            active_batch_proc = batch_proc
            while True:
                if cancelled:
                    if batch_proc.poll() is None:
                        batch_proc.terminate()
                        try:
                            batch_proc.wait(timeout=5.0)
                        except subprocess.TimeoutExpired:
                            batch_proc.kill()
                            batch_proc.wait(timeout=5.0)
                    returncode = 130
                    break
                rc = batch_proc.poll()
                if args.progress_manifest and batch_progress.exists():
                    chunk_progress = load_json(batch_progress) or {}
                    for item in chunk_progress.get("items", []):
                        source = str(item["source_path"])
                        entry = progress_state.get(source)
                        if entry is None:
                            continue
                        state = int(item.get("state", 0))
                        entry["progress"] = float(item.get("progress", 0.0))
                        entry["size_bytes"] = int(item.get("size_bytes", 0))
                        entry["expected_size_bytes"] = int(item.get("expected_size_bytes", 0))
                        entry["output_path"] = item.get("output_path")
                        entry["status"] = {0: "queued", 1: "running", 2: "finished", 3: "finished"}.get(state, "unknown")
                    write_progress_manifest(
                        args.progress_manifest,
                        {
                            "summary": {
                                "total": len(progress_state),
                                "completed": sum(1 for item in progress_state.values() if item["status"] == "finished"),
                                "running": sum(1 for item in progress_state.values() if item["status"] == "running"),
                                "queued": sum(1 for item in progress_state.values() if item["status"] in ("pending", "prepared", "queued")),
                            },
                            "items": list(progress_state.values()),
                            "current_chunk": chunk_index,
                            "chunk_progress_manifest": str(batch_progress),
                        },
                    )
                if rc is not None:
                    stdout, stderr = batch_proc.communicate()
                    batch_reports.append(
                        {
                            "manifest": str(batch_manifest),
                            "progress_manifest": str(batch_progress) if args.progress_manifest else None,
                            "returncode": rc,
                            "stdout": stdout[-4000:],
                            "stderr": stderr[-4000:],
                        }
                    )
                    batch_manifests.append(str(batch_manifest))
                    if rc != 0:
                        returncode = rc
                    break
                time.sleep(1.0)
            active_batch_proc = None
            if cancelled:
                break
        result = {
            "files": [str(p.expanduser().resolve()) for p in args.files],
            "output_dir": str(output_dir),
            "resolution_type": args.resolution_type,
            "frame_rate": args.frame_rate,
            "bitrate_mode": args.bitrate_mode,
            "custom_bitrate_mbps": args.custom_bitrate_mbps,
            "denoise": args.denoise,
            "denoise_mode": args.denoise_mode,
            "ten_bit": args.ten_bit,
            "parallel_count": args.parallel_count,
            "created_projects": created_projects,
            "errors": errors,
            "cleanup_temp_projects": args.cleanup_temp_projects,
            "cancelled": cancelled,
            "batch_manifests": batch_manifests,
            "batch": batch_reports,
            "cleanup": [],
        }
        if batch_manifests:
            result["batch_data"] = [load_json(Path(path)) for path in batch_manifests if Path(path).exists()]
        returncode = 0
        if errors:
            returncode = 1
        if any(int(report["returncode"]) != 0 for report in batch_reports):
            returncode = next(int(report["returncode"]) for report in batch_reports if int(report["returncode"]) != 0)
    finally:
        cancel_result: dict[str, Any] | None = None
        if cancelled:
            task_ids = collect_task_ids(batch_manifests=batch_manifest_paths, progress_manifests=batch_progress_paths)
            cancel_result = cancel_compose_tasks(
                support_dir=support_dir,
                output_dir=output_dir,
                source_files=[str(p.expanduser().resolve()) for p in args.files],
                task_ids=task_ids,
            )
        if args.cleanup_temp_projects:
            for item in created_projects:
                cleanup_actions.append(cleanup_live_project(int(item["project_id"]), support_dir))
                clone_cleanup = cleanup_clone_dir(item.get("clone_dir"))
                if clone_cleanup:
                    cleanup_actions.append(clone_cleanup)

        if result is None:
            result = {
                "files": [str(p.expanduser().resolve()) for p in args.files],
                "output_dir": str(output_dir),
                "resolution_type": args.resolution_type,
                "created_projects": created_projects,
                "errors": errors,
                "cleanup_temp_projects": args.cleanup_temp_projects,
                "batch_manifest": str(batch_manifest) if batch_manifest and batch_manifest.exists() else None,
                "batch": None,
                "cleanup": [],
            }
        result["cleanup"] = cleanup_actions
        if cancel_result is not None:
            result["cancel"] = cancel_result
        args.manifest.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        if args.progress_manifest:
            write_progress_manifest(
                args.progress_manifest,
                {
                    "summary": {
                        "total": len(progress_state),
                        "completed": sum(1 for item in progress_state.values() if item["status"] == "finished"),
                        "running": 0,
                        "queued": sum(1 for item in progress_state.values() if item["status"] in ("pending", "prepared", "queued")),
                    },
                    "items": list(progress_state.values()),
                    "finished": not cancelled,
                    "cancelled": cancelled,
                    "manifest": str(args.manifest),
                },
            )
        print(args.manifest.resolve())
    return returncode


if __name__ == "__main__":
    raise SystemExit(main())
