#!/usr/bin/env python3
"""Watch for a new manual export and capture its compose/export config for quality analysis."""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from dji_paths import get_project_root, get_support_dir  # noqa: E402

PROJECT_ROOT = get_project_root()
SUPPORT_DIR = get_support_dir()
MEDIA_DB = SUPPORT_DIR / "media_db" / "data.db"


def fetch_scalar(conn: sqlite3.Connection, sql: str) -> int:
    return int(conn.execute(sql).fetchone()[0])


def fetch_row(conn: sqlite3.Connection, table: str, row_id: int) -> dict[str, object] | None:
    conn.row_factory = sqlite3.Row
    row = conn.execute(f"select * from {table} where id = ?", (row_id,)).fetchone()
    return dict(row) if row is not None else None


def stable_size(path: Path, wait_seconds: float = 2.0) -> bool:
    if not path.exists():
        return False
    size_a = path.stat().st_size
    time.sleep(wait_seconds)
    if not path.exists():
        return False
    size_b = path.stat().st_size
    return size_a == size_b and size_b > 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--poll-interval", type=float, default=0.5)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "output" / "quality_capture",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=PROJECT_ROOT / "output" / "quality_capture_latest.json",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(MEDIA_DB)
    try:
        base_export_id = fetch_scalar(conn, "select ifnull(max(id),0) from exportDataTable")
        base_compose_id = fetch_scalar(conn, "select ifnull(max(id),0) from composeList")
    finally:
        conn.close()

    deadline = time.time() + args.timeout
    export_row = None
    compose_row = None
    while time.time() < deadline:
        conn = sqlite3.connect(MEDIA_DB)
        try:
            export_row = fetch_row(
                conn,
                "exportDataTable",
                fetch_scalar(conn, f"select ifnull(min(id),0) from exportDataTable where id > {base_export_id}"),
            )
            compose_row = fetch_row(
                conn,
                "composeList",
                fetch_scalar(conn, f"select ifnull(min(id),0) from composeList where id > {base_compose_id}"),
            )
        finally:
            conn.close()
        if export_row or compose_row:
            break
        time.sleep(args.poll_interval)

    report: dict[str, object] = {
        "media_db": str(MEDIA_DB),
        "base_export_id": base_export_id,
        "base_compose_id": base_compose_id,
        "export_row": export_row,
        "compose_row": compose_row,
    }

    draft_copy = None
    if compose_row and compose_row.get("draftPath"):
        draft_path = Path(str(compose_row["draftPath"]))
        if draft_path.exists():
            draft_copy = args.output_dir / draft_path.name
            shutil.copy2(draft_path, draft_copy)
    report["draft_copy"] = str(draft_copy) if draft_copy else None

    output_path = None
    if compose_row and compose_row.get("outPath"):
        output_path = Path(str(compose_row["outPath"]))
        wait_deadline = time.time() + args.timeout
        while time.time() < wait_deadline:
            if stable_size(output_path):
                break
            time.sleep(args.poll_interval)
    report["output_path"] = str(output_path) if output_path else None
    report["output_stable"] = bool(output_path and output_path.exists() and stable_size(output_path, wait_seconds=0.2))

    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.manifest.resolve())
    return 0 if export_row or compose_row else 1


if __name__ == "__main__":
    raise SystemExit(main())
