#!/usr/bin/env python3
"""Compare a manual export and an automated export at file/stream level."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def ffprobe_json(path: Path) -> dict[str, object]:
    proc = subprocess.run(
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
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(proc.stdout)


def video_stream(data: dict[str, object]) -> dict[str, object]:
    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video":
            return stream
    return {}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manual_mp4", type=Path)
    parser.add_argument("auto_mp4", type=Path)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args()

    manual = ffprobe_json(args.manual_mp4.expanduser().resolve())
    auto = ffprobe_json(args.auto_mp4.expanduser().resolve())
    mstream = video_stream(manual)
    astream = video_stream(auto)

    report = {
        "manual_mp4": str(args.manual_mp4.expanduser().resolve()),
        "auto_mp4": str(args.auto_mp4.expanduser().resolve()),
        "manual_size_bytes": args.manual_mp4.stat().st_size,
        "auto_size_bytes": args.auto_mp4.stat().st_size,
        "manual_video": {
            "codec_name": mstream.get("codec_name"),
            "profile": mstream.get("profile"),
            "pix_fmt": mstream.get("pix_fmt"),
            "width": mstream.get("width"),
            "height": mstream.get("height"),
            "r_frame_rate": mstream.get("r_frame_rate"),
            "bit_rate": mstream.get("bit_rate"),
        },
        "auto_video": {
            "codec_name": astream.get("codec_name"),
            "profile": astream.get("profile"),
            "pix_fmt": astream.get("pix_fmt"),
            "width": astream.get("width"),
            "height": astream.get("height"),
            "r_frame_rate": astream.get("r_frame_rate"),
            "bit_rate": astream.get("bit_rate"),
        },
    }
    report["delta"] = {
        "size_bytes": report["manual_size_bytes"] - report["auto_size_bytes"],
        "manual_vs_auto_size_ratio": round(report["manual_size_bytes"] / max(report["auto_size_bytes"], 1), 4),
    }

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.json_out.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
