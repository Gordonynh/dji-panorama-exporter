#!/usr/bin/env python3
"""Clone a DJI Studio import-style project using official mediaAsset metadata from copy_info.json."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any


SUPPORT_DIR = Path.home() / "Library/Application Support/DJI Studio"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def dump_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def md5sum_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def copy_info_media_asset(source_path: Path, support_dir: Path) -> dict[str, Any]:
    copy_info_path = support_dir / "media_db/copy_info.json"
    items = load_json(copy_info_path)
    resolved = str(source_path.resolve())
    matches = [item for item in items if item.get("finderPath") == resolved]
    if not matches:
        raise RuntimeError(f"no copy_info entry for {resolved}")
    media_asset = matches[-1].get("mediaAsset")
    if not isinstance(media_asset, dict):
        raise RuntimeError(f"copy_info entry for {resolved} is missing mediaAsset")
    return media_asset


def create_bookmark(path: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    swift_script = """
import Foundation

let source = URL(fileURLWithPath: CommandLine.arguments[1])
let output = URL(fileURLWithPath: CommandLine.arguments[2])

do {
    let data = try source.bookmarkData(
        options: [.withSecurityScope],
        includingResourceValuesForKeys: nil,
        relativeTo: nil
    )
    try data.write(to: output)
} catch {
    fputs("bookmark generation failed: \\(error)\\n", stderr)
    exit(1)
}
"""
    subprocess.run(
        ["swift", "-", str(path), str(destination)],
        input=swift_script,
        text=True,
        check=True,
    )


def rewrite_project_json(project: dict[str, Any], old_source: str, media_asset: dict[str, Any]) -> None:
    fragment_length = int(media_asset["duration"]) // 1000 * 1000
    fragment_out = max(fragment_length - 1, 0)

    for track in project.get("video", {}).get("tractor", []):
        for fragment in track.get("fragments", []):
            if fragment.get("path") != old_source:
                continue

            fragment["path"] = media_asset["path"]
            fragment["length"] = fragment_length
            fragment["out"] = fragment_out
            fragment["sourceType"] = str(fragment.get("sourceType", ""))

            tf_info = json.loads(fragment["tfInfo"])
            tf_info["path"] = media_asset["path"]
            tf_info["checksum"] = media_asset["fileMD5"]
            tf_info["duration"] = int(media_asset["duration"])
            tf_info["fileSize"] = int(media_asset["size"])
            tf_info["fileType"] = int(media_asset["fileType"])
            fragment["tfInfo"] = json.dumps(tf_info, ensure_ascii=False, separators=(",", ":"))

            for filter_item in fragment.get("filters", []):
                if filter_item.get("id") != "mika.panorama":
                    continue
                for para in filter_item.get("para", []):
                    if para.get("name") == "input" and para.get("value") == old_source:
                        para["value"] = media_asset["path"]


def rewrite_proj_db(proj_db: Path, old_source: str, media_asset: dict[str, Any]) -> dict[str, Any]:
    conn = sqlite3.connect(proj_db)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("select * from mediaAssetInfo_v3").fetchall()
        if len(rows) != 1:
            raise RuntimeError(f"expected exactly 1 media row in {proj_db}, found {len(rows)}")

        row = dict(rows[0])
        if row["path"] != old_source:
            raise RuntimeError(f"template path mismatch: {row['path']} != {old_source}")

        now_ms = int(time.time() * 1000)
        row["id"] = str(uuid.uuid4())
        row["path"] = media_asset["path"]
        row["createTime"] = now_ms
        row["importTime"] = now_ms
        row["editorTime"] = now_ms
        row["size"] = int(media_asset["size"])
        row["duration"] = int(media_asset["duration"])
        row["fileType"] = int(media_asset["fileType"])
        row["cutBegin"] = 0
        row["cutLength"] = 1
        row["width"] = int(media_asset["width"])
        row["height"] = int(media_asset["height"])
        row["fileMD5"] = media_asset["fileMD5"]
        row["isQuickCut"] = int(bool(media_asset.get("isQuickCut", False)))
        row["panoramaAdjustedJson"] = media_asset.get("panoramaAdjustedJson", "")
        row["deviceName"] = media_asset["deviceName"]
        row["fileMetaType"] = int(media_asset["fileMetaType"])
        row["viewingMode"] = int(media_asset["viewingMode"])

        conn.execute("delete from mediaAssetInfo_v3")
        columns = list(row.keys())
        placeholders = ", ".join("?" for _ in columns)
        conn.execute(
            f"insert into mediaAssetInfo_v3 ({', '.join(columns)}) values ({placeholders})",
            tuple(row[column] for column in columns),
        )
        conn.commit()
        return row
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_osv", type=Path, help="Source OSV/LRF file already present in DJI Studio copy_info.json")
    parser.add_argument(
        "template_project_dir",
        type=Path,
        help="Existing DJI Studio import-style project dir, usually project/24",
    )
    parser.add_argument("--support-dir", type=Path, default=SUPPORT_DIR)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("exports/dji_studio_import_templates"),
        help="Where to write the cloned import-style project",
    )
    args = parser.parse_args()

    source_osv = args.source_osv.expanduser().resolve()
    template_dir = args.template_project_dir.expanduser().resolve()
    support_dir = args.support_dir.expanduser().resolve()
    if not source_osv.exists():
        raise SystemExit(f"missing source file: {source_osv}")
    if not template_dir.is_dir():
        raise SystemExit(f"missing template dir: {template_dir}")

    proj_files = sorted(template_dir.glob("*.proj"))
    if len(proj_files) != 1:
        raise SystemExit(f"expected exactly one .proj in template dir, found {len(proj_files)}")
    proj_file = proj_files[0]
    proj_db = template_dir / "proj.db"
    if not proj_db.exists():
        raise SystemExit(f"missing proj.db: {proj_db}")

    project = load_json(proj_file)
    tracks = project.get("video", {}).get("tractor", [])
    if len(tracks) != 1 or len(tracks[0].get("fragments", [])) != 1:
        raise SystemExit("template must be a single-track, single-fragment import project")
    old_source = tracks[0]["fragments"][0].get("path")
    if not isinstance(old_source, str) or not old_source:
        raise SystemExit("template fragment path is empty")

    media_asset = copy_info_media_asset(source_osv, support_dir)

    clone_root = args.output_dir.expanduser().resolve()
    clone_root.mkdir(parents=True, exist_ok=True)
    clone_dir = clone_root / f"{int(time.time() * 1000)}_{source_osv.stem}"
    shutil.copytree(template_dir, clone_dir)

    resources_dir = clone_dir / "resources"
    if resources_dir.exists():
        shutil.rmtree(resources_dir)
        resources_dir.mkdir(parents=True, exist_ok=True)

    bookmark_dir = clone_dir / "bookmark"
    if bookmark_dir.exists():
        shutil.rmtree(bookmark_dir)
    bookmark_path = bookmark_dir / f"{media_asset['fileMD5']}.bookmark"
    create_bookmark(source_osv, bookmark_path)

    cloned_proj = next(clone_dir.glob("*.proj"))
    cloned_project = load_json(cloned_proj)
    rewrite_project_json(cloned_project, old_source, media_asset)
    dump_json(cloned_proj, cloned_project)
    proj_bytes = cloned_proj.read_bytes()
    proj_name = f"{md5sum_bytes(proj_bytes)}.proj"
    renamed_proj = cloned_proj.with_name(proj_name)
    if renamed_proj != cloned_proj:
        cloned_proj.rename(renamed_proj)
        cloned_proj = renamed_proj

    cloned_row = rewrite_proj_db(clone_dir / "proj.db", old_source, media_asset)

    manifest = {
        "template_project_dir": str(template_dir),
        "template_project_file": str(proj_file),
        "output_project_file": str(cloned_proj),
        "output_project_dir": str(clone_dir),
        "source_before": old_source,
        "source_after": str(source_osv),
        "media_asset": media_asset,
        "bookmark_path": str(bookmark_path),
        "media_asset_row": cloned_row,
    }
    dump_json(clone_dir / "clone_manifest.json", manifest)

    print(clone_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
