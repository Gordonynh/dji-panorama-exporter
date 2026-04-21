#!/usr/bin/env python3
"""Summarize exported MP4 files into JSON and CSV reports."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path


def ffprobe(path: Path) -> dict[str, object]:
    proc = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=codec_name,profile,pix_fmt,width,height,r_frame_rate",
            "-show_entries",
            "format=duration,size",
            "-of",
            "json",
            str(path),
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    data = json.loads(proc.stdout)
    stream = (data.get("streams") or [{}])[0]
    fmt = data.get("format") or {}
    return {
        "path": str(path),
        "filename": path.name,
        "codec_name": stream.get("codec_name"),
        "profile": stream.get("profile"),
        "pix_fmt": stream.get("pix_fmt"),
        "width": stream.get("width"),
        "height": stream.get("height"),
        "r_frame_rate": stream.get("r_frame_rate"),
        "duration": fmt.get("duration"),
        "size": fmt.get("size"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export_dir", type=Path)
    parser.add_argument(
        "--json-out",
        type=Path,
        default=Path("exports/dji_studio_live/export_report.json"),
    )
    parser.add_argument(
        "--csv-out",
        type=Path,
        default=Path("exports/dji_studio_live/export_report.csv"),
    )
    args = parser.parse_args()

    export_dir = args.export_dir.expanduser().resolve()
    files = sorted(export_dir.glob("*.mp4"))
    rows = [ffprobe(path) for path in files]

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.csv_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps({"export_dir": str(export_dir), "count": len(rows), "files": rows}, ensure_ascii=False, indent=2))

    fieldnames = [
        "filename",
        "path",
        "codec_name",
        "profile",
        "pix_fmt",
        "width",
        "height",
        "r_frame_rate",
        "duration",
        "size",
    ]
    with args.csv_out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(args.json_out.resolve())
    print(args.csv_out.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
