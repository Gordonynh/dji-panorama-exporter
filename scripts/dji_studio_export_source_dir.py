#!/usr/bin/env python3
"""Export a source directory by auto-matching or creating live DJI Studio projects."""

from __future__ import annotations

import argparse
import configparser
import json
import sqlite3
import subprocess
import sys
import time
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from dji_paths import get_project_root, get_source_default, get_support_dir  # noqa: E402
from dji_studio_inject_compose_task import SUPPORT_DIR  # noqa: E402


def scan_live_projects(support_dir: Path) -> dict[str, list[dict[str, object]]]:
    root = support_dir / "project"
    mapping: dict[str, list[dict[str, object]]] = {}
    for project_dir in sorted(root.iterdir(), key=lambda p: int(p.name) if p.name.isdigit() else 999999):
        if not project_dir.is_dir() or not project_dir.name.isdigit():
            continue
        db = project_dir / "proj.db"
        if not db.exists():
            continue
        try:
            conn = sqlite3.connect(db)
            row = conn.execute("select path, duration, fileMD5 from mediaAssetInfo_v3 limit 1").fetchone()
            conn.close()
        except Exception:
            continue
        if not row or not row[0]:
            continue
        mapping.setdefault(str(Path(row[0]).resolve()), []).append(
            {
                "project_dir": str(project_dir),
                "project_id": int(project_dir.name),
                "duration": int(row[1] or 0),
                "file_md5": row[2],
            }
        )
    return mapping


def choose_best_project(candidates: list[dict[str, object]]) -> dict[str, object]:
    return sorted(candidates, key=lambda item: (int(item["duration"]), int(item["project_id"])), reverse=True)[0]


def rename_live_project(project_id: int, ui_name: str, support_dir: Path) -> None:
    media_db = support_dir / "media_db/data.db"
    conn = sqlite3.connect(media_db)
    try:
        conn.execute(
            "update project_draft_v2 set name = ?, modifyTime = ? where id = ?",
            (ui_name, int(time.time() * 1000), project_id),
        )
        conn.commit()
    finally:
        conn.close()


def create_live_project_for_source(source_path: Path, template_project_dir: Path, support_dir: Path) -> dict[str, object]:
    clone_script = SCRIPT_DIR / "dji_studio_clone_import_project.py"
    install_script = SCRIPT_DIR / "dji_studio_install_live_project.py"
    clone_proc = subprocess.run(
        [sys.executable, str(clone_script), str(source_path), str(template_project_dir)],
        text=True,
        capture_output=True,
        check=True,
    )
    clone_dir = Path(clone_proc.stdout.strip())
    install_manifest = get_project_root() / "output" / f"install_auto_{source_path.stem}.json"
    install_proc = subprocess.run(
        [sys.executable, str(install_script), str(clone_dir), "--manifest", str(install_manifest.resolve())],
        text=True,
        capture_output=True,
        check=True,
    )
    _ = install_proc
    install_data = json.loads(install_manifest.read_text())
    project_id = int(install_data["live_project_id"])
    rename_live_project(project_id, f"ZZ_AUTO_{project_id}_{source_path.stem}", support_dir)
    return {
        "project_dir": install_data["live_project_dir"],
        "project_id": project_id,
        "created": True,
        "clone_dir": str(clone_dir),
        "install_manifest": str(install_manifest.resolve()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", type=Path, nargs="?", default=get_source_default())
    parser.add_argument("--pattern", default="*.OSV")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--resolution-type", type=int, default=14)
    parser.add_argument("--use-cylinder", type=int, choices=[0, 1], default=1)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--create-missing", action="store_true")
    parser.add_argument("--template-project-dir", type=Path, default=get_support_dir() / "project" / "24")
    parser.add_argument("--support-dir", type=Path, default=SUPPORT_DIR)
    parser.add_argument("--manifest", type=Path, default=get_project_root() / "output" / "export_source_dir_manifest.json")
    args = parser.parse_args()

    input_dir = args.input_dir.expanduser().resolve()
    support_dir = args.support_dir.expanduser().resolve()
    template_project_dir = args.template_project_dir.expanduser().resolve()
    files = sorted(input_dir.glob(args.pattern))
    if not files:
        raise SystemExit(f"no files matched {args.pattern} in {input_dir}")

    mapping = scan_live_projects(support_dir)
    selected_projects: list[str] = []
    matches: list[dict[str, object]] = []

    for source in files:
        key = str(source.resolve())
        candidates = mapping.get(key, [])
        if candidates:
            chosen = choose_best_project(candidates)
            matches.append({"source": key, "match": chosen, "status": "matched"})
            selected_projects.append(str(chosen["project_dir"]))
            continue
        if not args.create_missing:
            matches.append({"source": key, "status": "missing_project"})
            continue
        created = create_live_project_for_source(source, template_project_dir, support_dir)
        matches.append({"source": key, "match": created, "status": "created"})
        selected_projects.append(str(created["project_dir"]))

    manifest = {
        "input_dir": str(input_dir),
        "files": [str(f) for f in files],
        "matches": matches,
    }

    runnable_projects = [m["match"]["project_dir"] for m in matches if m["status"] in ("matched", "created")]
    batch_manifest = None
    if runnable_projects:
        batch_manifest = args.manifest.parent / f"{args.manifest.stem}_batch.json"
        cmd = [
            sys.executable,
            str(SCRIPT_DIR / "dji_studio_batch_internal_export.py"),
            *runnable_projects,
            "--output-dir",
            str(args.output_dir.expanduser().resolve()),
            "--resolution-type",
            str(args.resolution_type),
            "--use-cylinder",
            str(args.use_cylinder),
            "--manifest",
            str(batch_manifest.resolve()),
        ]
        if args.skip_existing:
            cmd.append("--skip-existing")
        subprocess.run(cmd, check=True)
        manifest["batch_manifest"] = str(batch_manifest.resolve())

    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(args.manifest.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
