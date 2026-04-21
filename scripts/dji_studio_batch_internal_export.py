#!/usr/bin/env python3
"""Batch-inject live DJI Studio projects, then start export via internal autoCompose."""

from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
import time
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from dji_studio_inject_compose_task import SUPPORT_DIR, inject_task  # noqa: E402


SUCCESS_STATES = {2, 3}


def read_source_path(project_dir: Path) -> Path:
    conn = sqlite3.connect(project_dir / "proj.db")
    try:
        row = conn.execute("select path from mediaAssetInfo_v3 limit 1").fetchone()
        if row is None or not row[0]:
            raise RuntimeError(f"no media row in {project_dir / 'proj.db'}")
        return Path(row[0])
    finally:
        conn.close()


def snapshot_task_progress(last: dict[int, dict[str, object]], injected: list[dict[str, object]]) -> dict[str, object]:
    injected_by_id = {int(item["task_id"]): item for item in injected if item.get("task_id") is not None}
    items: list[dict[str, object]] = []
    for task_id, item in injected_by_id.items():
        row = last.get(task_id, {})
        state = int(row.get("state", item.get("state", 0)))
        total_during = float(row.get("totalDuring") or 0)
        composed_during = float(row.get("composedDuring") or 0)
        output_path = Path(str(item["output_path"]))
        size_bytes = output_path.stat().st_size if output_path.exists() else 0
        expected_size_bytes = int(item.get("expected_size_bytes") or 0)
        time_progress = 1.0 if state == 2 else (composed_during / total_during if total_during > 0 else 0.0)
        size_progress = (size_bytes / expected_size_bytes) if expected_size_bytes > 0 else 0.0
        progress = size_progress if size_progress > 0 else time_progress
        if state == 1 and size_bytes > 0 and progress <= 0:
            progress = 0.01
        if state in SUCCESS_STATES:
            progress = 1.0
        elif progress >= 1.0:
            progress = 0.99
        progress = max(0.0, min(progress, 1.0))
        items.append(
            {
                "task_id": task_id,
                "source_path": item["source_path"],
                "output_path": item["output_path"],
                "state": state,
                "progress": progress,
                "composed_during": composed_during,
                "total_during": total_during,
                "size_bytes": size_bytes,
                "expected_size_bytes": expected_size_bytes,
            }
        )
    completed = sum(1 for item in items if int(item["state"]) in SUCCESS_STATES)
    running = sum(1 for item in items if int(item["state"]) == 1)
    queued = sum(1 for item in items if int(item["state"]) == 0)
    return {
        "items": items,
        "summary": {
            "total": len(items),
            "completed": completed,
            "running": running,
            "queued": queued,
        },
    }


def poll_tasks(
    task_ids: list[int],
    support_dir: Path,
    timeout: float,
    interval: float,
    *,
    injected: list[dict[str, object]] | None = None,
    progress_manifest: Path | None = None,
) -> dict[int, dict[str, object]]:
    db = support_dir / "media_db/data.db"
    deadline = time.time() + timeout
    last: dict[int, dict[str, object]] = {}
    last_trigger_at = 0.0
    while time.time() < deadline:
        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                f"select id,state,createTime,synthesisTime,outPath,totalDuring,composedDuring from composeList where id in ({','.join('?' for _ in task_ids)})",
                task_ids,
            ).fetchall()
        finally:
            conn.close()
        for row in rows:
            last[int(row["id"])] = dict(row)
        if progress_manifest and injected is not None:
            progress_manifest.parent.mkdir(parents=True, exist_ok=True)
            progress_manifest.write_text(json.dumps(snapshot_task_progress(last, injected), ensure_ascii=False, indent=2))
        states = [int(last[tid]["state"]) for tid in task_ids if tid in last]
        if states and all(state == 0 for state in states):
            now = time.time()
            if now - last_trigger_at >= 10.0:
                subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT_DIR / "dji_studio_trigger_internal_autocompose.py"),
                        "--output",
                        str((SCRIPT_DIR.parent / "output" / "batch_internal_retrigger.txt").resolve()),
                        "--launch-if-needed",
                    ],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                last_trigger_at = now
        if len(last) == len(task_ids) and all(int(last[tid]["state"]) in SUCCESS_STATES for tid in task_ids):
            break
        time.sleep(interval)
    return last


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dirs", nargs="+", type=Path, help="Live DJI Studio project dirs")
    parser.add_argument("--output-dir", type=Path, required=True, help="Destination directory for exported mp4 files")
    parser.add_argument("--resolution-type", type=int, default=14)
    parser.add_argument("--use-cylinder", type=int, choices=[0, 1], default=1)
    parser.add_argument("--launch-if-needed", action="store_true")
    parser.add_argument(
        "--foreground-launch",
        action="store_true",
        help="When launching DJI Studio automatically, allow it to remain visible/frontmost instead of hiding it.",
    )
    parser.add_argument("--timeout", type=float, default=900.0)
    parser.add_argument("--poll-interval", type=float, default=2.0)
    parser.add_argument("--skip-existing", action="store_true")
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
        default=Path("exports/dji_studio_live/batch_internal_export_manifest.json"),
    )
    args = parser.parse_args()

    support_dir = SUPPORT_DIR.resolve()
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    injected: list[dict[str, object]] = []
    for project_dir in args.project_dirs:
        project_dir = project_dir.expanduser().resolve()
        source_path = read_source_path(project_dir)
        output_path = output_dir / f"{source_path.stem}_official.mp4"
        if args.skip_existing and output_path.exists():
            injected.append(
                {
                    "project_dir": str(project_dir),
                    "source_path": str(source_path),
                    "output_path": str(output_path),
                    "skipped_existing": True,
                }
            )
            continue
        result = inject_task(
            project_dir=project_dir,
            output_path=output_path,
            support_dir=support_dir,
            resolution_type=args.resolution_type,
            state=0,
            use_cylinder_override=args.use_cylinder,
            frame_rate_override=args.frame_rate,
            bitrate_mode=None if args.bitrate_mode == "default" else args.bitrate_mode,
            custom_bitrate_mbps=args.custom_bitrate_mbps,
            enable_denoise=args.denoise,
            denoise_mode=args.denoise_mode,
            enable_10bit=args.ten_bit,
        )
        result["project_dir"] = str(project_dir)
        injected.append(result)

    pending_task_ids = [int(item["task_id"]) for item in injected if not item.get("skipped_existing")]
    trigger_report = None
    if pending_task_ids:
        trigger_cmd = [
            "python3",
            str(SCRIPT_DIR / "dji_studio_trigger_internal_autocompose.py"),
            "--output",
            str(Path("exports/dji_studio_live/batch_internal_trigger.txt").resolve()),
        ]
        if args.launch_if_needed:
            trigger_cmd.append("--launch-if-needed")
        if args.foreground_launch:
            trigger_cmd.append("--foreground-launch")
        proc = subprocess.run(trigger_cmd, text=True, capture_output=True)
        trigger_report = {
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }

    final_states = poll_tasks(
        pending_task_ids,
        support_dir,
        args.timeout,
        args.poll_interval,
        injected=injected,
        progress_manifest=args.progress_manifest.expanduser().resolve() if args.progress_manifest else None,
    ) if pending_task_ids else {}
    manifest = {
        "support_dir": str(support_dir),
        "output_dir": str(output_dir),
        "parallel_count": args.parallel_count,
        "injected": injected,
        "trigger": trigger_report,
        "final_states": final_states,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(args.manifest.resolve())
    if pending_task_ids and (
        len(final_states) != len(pending_task_ids)
        or any(int(final_states[tid]["state"]) not in SUCCESS_STATES for tid in pending_task_ids if tid in final_states)
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
