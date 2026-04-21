#!/usr/bin/env python3
"""Install an offline DJI Studio project clone into the live support directory."""

from __future__ import annotations

import argparse
import configparser
import json
import shutil
import sqlite3
import time
from pathlib import Path
from typing import Any


SUPPORT_DIR = Path.home() / "Library/Application Support/DJI Studio"


def backup_file(path: Path) -> Path:
    backup_dir = Path("exports/dji_studio_backups").resolve()
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{path.name}.{int(time.time() * 1000)}.bak"
    shutil.copy2(path, backup_path)
    return backup_path


def read_media_row(proj_db: Path) -> dict[str, Any]:
    conn = sqlite3.connect(proj_db)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute("select * from mediaAssetInfo_v3 limit 1").fetchone()
        if row is None:
            raise RuntimeError(f"no media row in {proj_db}")
        return dict(row)
    finally:
        conn.close()


def update_config_create_time(config_path: Path) -> None:
    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str
    parser.read(config_path, encoding="utf-8")
    if not parser.has_section("General"):
        parser["General"] = {}
    parser["General"][".__dummmy_key_create_time__"] = str(int(time.time() * 1000))
    with config_path.open("w", encoding="utf-8") as handle:
        parser.write(handle, space_around_delimiters=False)


def install_project(clone_dir: Path, support_dir: Path) -> dict[str, Any]:
    media_db = support_dir / "media_db/data.db"
    backup_path = backup_file(media_db)

    conn = sqlite3.connect(media_db)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute("select max(id) as max_id from project_draft_v2").fetchone()
        next_id = int(row["max_id"] or 0) + 1
        live_project_dir = support_dir / "project" / str(next_id)
        while live_project_dir.exists():
            next_id += 1
            live_project_dir = support_dir / "project" / str(next_id)

        shutil.copytree(
            clone_dir,
            live_project_dir,
            ignore=shutil.ignore_patterns("clone_manifest.json", "*.bak"),
        )
        config_path = live_project_dir / "config.ini"
        if config_path.exists():
            update_config_create_time(config_path)

        media_row = read_media_row(live_project_dir / "proj.db")
        source_path = Path(str(media_row["path"]))
        name = source_path.stem
        duration = int(media_row.get("duration") or 0)
        now_ms = int(time.time() * 1000)

        conn.execute(
            """
            insert into project_draft_v2
            (id, version, name, suffixNumber, size, duration, modifyTime, createTime, projectPath)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                next_id,
                None,
                name,
                0,
                0,
                duration,
                now_ms,
                now_ms,
                str(support_dir / "project"),
            ),
        )
        conn.commit()
        return {
            "backup_db": str(backup_path),
            "live_project_id": next_id,
            "live_project_dir": str(live_project_dir),
            "source_path": str(source_path),
            "project_name": name,
            "duration": duration,
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("clone_dir", type=Path, help="Offline project clone dir created by dji_studio_clone_project.py")
    parser.add_argument("--support-dir", type=Path, default=SUPPORT_DIR)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("exports/dji_studio_live/install_manifest.json"),
        help="Write install result JSON here",
    )
    args = parser.parse_args()

    clone_dir = args.clone_dir.expanduser().resolve()
    support_dir = args.support_dir.expanduser().resolve()
    if not clone_dir.is_dir():
        raise SystemExit(f"missing clone dir: {clone_dir}")

    result = install_project(clone_dir, support_dir)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(args.manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
