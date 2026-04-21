#!/usr/bin/env python3
"""Insert a compose task into DJI Studio's live export database and stage a compose draft."""

from __future__ import annotations

import argparse
import configparser
import json
import shutil
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import sys

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from dji_paths import get_project_root, get_setting_ini, get_support_dir  # noqa: E402

SUPPORT_DIR = get_support_dir()
SETTING_INI = get_setting_ini()
PANO_RESOLUTION_MAP: dict[int, tuple[int, int]] = {
    12: (6000, 3000),
    14: (7680, 3840),
}
FRAME_RATE_SETTING_MAP: dict[int, int] = {
    1: 24,
    2: 25,
    3: 30,
    4: 50,
    5: 60,
}
PANO_RESOLUTION_NAME_MAP: dict[int, str] = {
    12: "6K",
    14: "8K",
}
PANO_DEVICE_NAME_MAP: dict[str, str] = {
    "DJI Avata360": "DUSS_REMUX_RECORD_PANO_VIDEO",
}


def backup_file(path: Path) -> Path:
    backup_dir = (get_project_root() / "output" / "backups").resolve()
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{path.name}.{int(time.time() * 1000)}.bak"
    shutil.copy2(path, backup_path)
    return backup_path


def project_paths(project_dir: Path) -> tuple[Path, Path]:
    proj_files = sorted(project_dir.glob("*.proj"))
    if len(proj_files) != 1:
        raise RuntimeError(f"expected exactly one .proj in {project_dir}, found {len(proj_files)}")
    return proj_files[0], project_dir / "proj.db"


def read_default_pano_resolution(setting_ini: Path) -> int:
    parser = configparser.ConfigParser()
    if setting_ini.exists():
        parser.read(setting_ini)
        try:
            return parser.getint("General", "key_export_pano_resolution")
        except Exception:
            pass
    return 12


def read_export_settings(setting_ini: Path) -> dict[str, int]:
    parser = configparser.ConfigParser()
    settings = {
        "pano_resolution": 12,
        "frame_rate": 0,
        "bitrate": 0,
        "bitrate_custom": 0,
    }
    if setting_ini.exists():
        parser.read(setting_ini)
        for key, ini_key in (
            ("pano_resolution", "key_export_pano_resolution"),
            ("frame_rate", "key_export_frameRate"),
            ("bitrate", "key_export_bitrate"),
            ("bitrate_custom", "key_export_bitrate_custom"),
        ):
            try:
                settings[key] = parser.getint("General", ini_key)
            except Exception:
                pass
    return settings


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


def read_video_cache_row(media_db: Path, file_md5: str) -> dict[str, Any] | None:
    conn = sqlite3.connect(media_db)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "select * from videoInfoCache where file_MD5 = ? limit 1",
            (file_md5,),
        ).fetchone()
        return dict(row) if row is not None else None
    finally:
        conn.close()


def patch_compose_profile(
    draft_path: Path,
    resolution_type: int,
    video_cache_row: dict[str, Any] | None,
    output_frame_rate: int,
    target_bitrate: int,
    enable_denoise: bool,
    color_depth: int,
) -> dict[str, Any]:
    data = json.loads(draft_path.read_text())
    profile = dict(data.get("profile") or {})
    if resolution_type in PANO_RESOLUTION_MAP:
        width, height = PANO_RESOLUTION_MAP[resolution_type]
        profile["width"] = width
        profile["height"] = height
        profile["canvasManual_changed"] = False
    if output_frame_rate > 0:
        profile["framerate"] = output_frame_rate
    elif video_cache_row:
        fps = float(video_cache_row.get("video_fps") or 0)
        if fps > 0:
            profile["framerate"] = round(fps)
    if target_bitrate > 0:
        profile["bitrate"] = target_bitrate
    if enable_denoise:
        profile["denoiseType"] = 1
    else:
        profile["denoiseType"] = 0
    profile["enableDolbyVision"] = False
    profile["colorSpace"] = 65793
    if color_depth > 0:
        profile["colorDepth"] = color_depth
    if "preciseStitcher" not in profile:
        profile["preciseStitcher"] = False
    data["profile"] = profile
    draft_path.write_text(json.dumps(data, ensure_ascii=False, indent=4))
    return profile


def duration_seconds_from_media_row(media_row: dict[str, Any]) -> int:
    duration = float(media_row.get("duration") or 0)
    if duration <= 0:
        return 0
    return max(1, int(round(duration / 30000.0)))


def estimate_output_size_bytes(duration_seconds: int, target_bitrate: int) -> int:
    if duration_seconds <= 0 or target_bitrate <= 0:
        return 0
    audio_bitrate = 256_000
    container_overhead = 1.015
    return int(round(((target_bitrate + audio_bitrate) * duration_seconds / 8.0) * container_overhead))


def resolve_output_frame_rate(
    export_settings: dict[str, int],
    video_cache_row: dict[str, Any] | None,
    *,
    prefer_source_fps: bool = True,
    frame_rate_override: int | None = None,
) -> int:
    if frame_rate_override and frame_rate_override > 0:
        return frame_rate_override
    configured = FRAME_RATE_SETTING_MAP.get(int(export_settings.get("frame_rate") or 0), 0)
    if video_cache_row:
        fps = float(video_cache_row.get("video_fps") or 0)
        if fps > 0:
            source_fps = round(fps)
            if prefer_source_fps or configured <= 0:
                return source_fps
    if configured > 0:
        return configured
    return 60


def compute_high_bitrate(width: int, height: int, frame_rate: int) -> int:
    base_pixels = 7680 * 3840
    base_fps = 60
    base_bitrate = 349_733_025
    scale = (width * height * max(frame_rate, 1)) / (base_pixels * base_fps)
    return int(round(base_bitrate * scale))


def compute_target_bitrate(resolution_type: int, frame_rate: int, export_settings: dict[str, int]) -> int:
    width, height = PANO_RESOLUTION_MAP.get(resolution_type, PANO_RESOLUTION_MAP[14])
    mode = int(export_settings.get("bitrate") or 0)
    custom = int(export_settings.get("bitrate_custom") or 0)
    if mode >= 2:
        return compute_high_bitrate(width, height, frame_rate)
    if custom > 0:
        return custom * 1_000_000
    return 0


def compute_target_bitrate_override(
    resolution_type: int,
    frame_rate: int,
    export_settings: dict[str, int],
    *,
    bitrate_mode: str | None = None,
    custom_bitrate_mbps: float | None = None,
) -> int:
    width, height = PANO_RESOLUTION_MAP.get(resolution_type, PANO_RESOLUTION_MAP[14])
    high = compute_high_bitrate(width, height, frame_rate)
    mode = (bitrate_mode or "").lower().strip()
    if mode == "custom" and custom_bitrate_mbps and custom_bitrate_mbps > 0:
        return int(round(custom_bitrate_mbps * 1_000_000))
    if mode == "high":
        return high
    if mode == "medium":
        return int(round(high * 0.7))
    if mode == "low":
        return int(round(high * 0.45))
    return compute_target_bitrate(resolution_type, frame_rate, export_settings)


def build_export_data_content(
    *,
    output_path: Path,
    export_id: str,
    resolution_type: int,
    frame_rate: int,
    bitrate: int,
    color_depth: int,
    device_name: str,
    media_row: dict[str, Any],
    video_cache_row: dict[str, Any] | None,
    enable_denoise: bool,
    denoise_mode: str,
) -> dict[str, Any]:
    width, height = PANO_RESOLUTION_MAP.get(resolution_type, PANO_RESOLUTION_MAP[14])
    work_duration = duration_seconds_from_media_row(media_row)
    device_slug = PANO_DEVICE_NAME_MAP.get(device_name, device_name or "DUSS_REMUX_RECORD_PANO_VIDEO")
    source_fps = int(round(float(video_cache_row.get("video_fps") or 0))) if video_cache_row else frame_rate
    material_size_mb = round(float(media_row.get("size") or 0) / 1_000_000, 1)
    function_used: list[str] = []
    denoise_type = ""
    if enable_denoise:
        if denoise_mode == "performance":
            denoise_type = "noise_reduction_fast"
        else:
            denoise_type = "noise_reduction"
        function_used.append("NOISE_REDUCTION")
    if color_depth >= 10:
        function_used.append("EXPORT_10BIT")
    return {
        "bitrateMap": {"frameRate": bitrate},
        "colorDepth": color_depth,
        "dataMap": {
            "clip_duration": list(str(work_duration)),
            "dashboard_source_list": [""],
            "dashboard_tab_list": [""],
            "filter_slug_list": [],
            "font_slug_list": [],
            "is_dashboard": False,
            "is_default": [],
            "is_pano": True,
            "is_proxy": False,
            "is_tonalenhance": False,
            "movement_slug_list": [],
            "music_code_list": [],
            "playback_speed": [1],
            "reduce_color_jump_level": ["close"],
            "sticker_slug": ["[]"],
            "stitching_list": ["BJ_AI"],
            "tracking_cnt": 0,
            "tracking_duration": 0,
            "work_duration": work_duration,
        },
        "denoise": enable_denoise,
        "denoiseType": denoise_type,
        "dolbyVision": False,
        "exportCnt": 1,
        "exportId": export_id,
        "exportType": "timeline",
        "export_media_type": "panoramic",
        "frameRateMap": {"frameRate": frame_rate, "name": f"{frame_rate} fps"},
        "function_used": function_used,
        "is_retry": False,
        "is_thumb_success": True,
        "materialDataMap": {
            "bitrate": "",
            "devices_name": [device_slug],
            "duration": work_duration,
            "file_color_mode_list": ["NORMAL"],
            "file_encode_format_list": ["H.265"],
            "fps": source_fps,
            "has_hdr_display": color_depth >= 10,
            "is_device_material": True,
            "is_pano": True,
            "media_format": ["OSV"],
            "media_type": ["panoramic_video"],
            "number_of_material": 1,
            "project_colorspace": "sdr_rec709",
            "resolution": f"{width}x{height}",
            "size": material_size_mb,
        },
        "outputPath": str(output_path),
        "resolutionMap": {
            "height": height,
            "name": PANO_RESOLUTION_NAME_MAP.get(resolution_type, f"{width}x{height}"),
            "width": width,
        },
        "scopeType": "all",
    }


def copy_compose_draft(project_dir: Path, support_dir: Path) -> tuple[Path, Path]:
    proj_file, _ = project_paths(project_dir)
    media_row = read_media_row(project_dir / "proj.db")
    source_md5 = str(media_row["fileMD5"])

    ts = int(time.time() * 1000)
    compose_dir = support_dir / "compose" / str(ts)
    compose_dir.mkdir(parents=True, exist_ok=False)

    draft_path = compose_dir / f"{source_md5}.proj"
    shutil.copy2(proj_file, draft_path)

    cover_candidates = list(project_dir.glob("*.cover.jpg"))
    if cover_candidates:
        shutil.copy2(cover_candidates[0], compose_dir / "cover.jpg")

    return compose_dir, draft_path


def inject_task(
    project_dir: Path,
    output_path: Path,
    support_dir: Path,
    resolution_type: int,
    state: int,
    use_cylinder_override: int | None,
    prefer_source_fps: bool = True,
    frame_rate_override: int | None = None,
    bitrate_mode: str | None = None,
    custom_bitrate_mbps: float | None = None,
    enable_denoise: bool = True,
    denoise_mode: str = "quality",
    enable_10bit: bool = True,
) -> dict[str, Any]:
    media_db = support_dir / "media_db/data.db"
    backup_path = backup_file(media_db)
    compose_dir, draft_path = copy_compose_draft(project_dir, support_dir)
    _, proj_db = project_paths(project_dir)
    media_row = read_media_row(proj_db)

    source_path = str(media_row["path"])
    device_name = str(media_row.get("deviceName") or "")
    file_md5 = str(media_row["fileMD5"])
    duration = float(media_row.get("duration") or 0)
    video_cache_row = read_video_cache_row(media_db, file_md5)
    export_settings = read_export_settings(SETTING_INI)
    output_frame_rate = resolve_output_frame_rate(
        export_settings,
        video_cache_row,
        prefer_source_fps=prefer_source_fps,
        frame_rate_override=frame_rate_override,
    )
    target_bitrate = compute_target_bitrate_override(
        resolution_type,
        output_frame_rate,
        export_settings,
        bitrate_mode=bitrate_mode,
        custom_bitrate_mbps=custom_bitrate_mbps,
    )
    color_depth = 10 if enable_10bit else 8
    duration_seconds = duration_seconds_from_media_row(media_row)
    expected_size_bytes = estimate_output_size_bytes(duration_seconds, target_bitrate)
    patched_profile = patch_compose_profile(
        draft_path,
        resolution_type,
        video_cache_row,
        output_frame_rate,
        target_bitrate,
        enable_denoise,
        color_depth,
    )
    if use_cylinder_override is None:
        use_cylinder = int((media_row.get("viewingMode") or 0) == 3)
    else:
        use_cylinder = int(use_cylinder_override)
    has_device_material = 1 if device_name else 0
    now_iso = datetime.now().isoformat(timespec="milliseconds")
    export_id = f"AUTO_INTERNAL_{int(time.time() * 1000)}"

    conn = sqlite3.connect(media_db)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute(
            """
            insert into composeList
            (draftPath, outPath, firstSourcePath, state, createTime, draftId,
             useCylinder, hasDeviceMaterial, resolutionType, composeSize, fileMD5,
             entrance, isMultiFragment, fragmentCount, totalDuring, composedDuring, exportId)
            values
            (:draftPath, :outPath, :firstSourcePath, :state, :createTime, :draftId,
             :useCylinder, :hasDeviceMaterial, :resolutionType, :composeSize, :fileMD5,
             :entrance, :isMultiFragment, :fragmentCount, :totalDuring, :composedDuring, :exportId)
            """,
            {
                "draftPath": str(draft_path),
                "outPath": str(output_path),
                "firstSourcePath": source_path,
                "state": state,
                "createTime": now_iso,
                "draftId": -1,
                "useCylinder": use_cylinder,
                "hasDeviceMaterial": has_device_material,
                "resolutionType": resolution_type,
                "composeSize": 0.0,
                "fileMD5": file_md5,
                "entrance": 0,
                "isMultiFragment": 0,
                "fragmentCount": 0,
                "totalDuring": duration,
                "composedDuring": 0.0,
                "exportId": export_id,
            },
        )
        task_id = conn.execute("select last_insert_rowid()").fetchone()[0]

        color_depth = int(patched_profile.get("colorDepth") or (10 if enable_10bit else 8))
        data_content = build_export_data_content(
            output_path=output_path,
            export_id=export_id,
            resolution_type=resolution_type,
            frame_rate=output_frame_rate,
            bitrate=target_bitrate,
            color_depth=color_depth,
            device_name=device_name,
            media_row=media_row,
            video_cache_row=video_cache_row,
            enable_denoise=enable_denoise,
            denoise_mode=denoise_mode,
        )
        conn.execute(
            """
            insert into exportDataTable (dataContent, exportPath, outPutPath, createTime, exportId)
            values (:dataContent, :exportPath, :outPutPath, :createTime, :exportId)
            """,
            {
                "dataContent": json.dumps(data_content, ensure_ascii=False, separators=(",", ":")),
                "exportPath": str(draft_path),
                "outPutPath": str(output_path),
                "createTime": now_iso,
                "exportId": export_id,
            },
        )
        conn.commit()
        return {
            "backup_db": str(backup_path),
            "compose_dir": str(compose_dir),
            "draft_path": str(draft_path),
            "task_id": task_id,
            "output_path": str(output_path),
            "source_path": source_path,
            "file_md5": file_md5,
            "patched_profile": patched_profile,
            "export_id": export_id,
            "resolution_type": resolution_type,
            "state": state,
            "export_settings": export_settings,
            "output_frame_rate": output_frame_rate,
            "target_bitrate": target_bitrate,
            "duration_seconds": duration_seconds,
            "expected_size_bytes": expected_size_bytes,
            "data_content": data_content,
            "prefer_source_fps": prefer_source_fps,
            "frame_rate_override": frame_rate_override,
            "bitrate_mode": bitrate_mode,
            "custom_bitrate_mbps": custom_bitrate_mbps,
            "enable_denoise": enable_denoise,
            "denoise_mode": denoise_mode,
            "enable_10bit": enable_10bit,
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def poll_task(support_dir: Path, draft_path: str, seconds: float) -> list[dict[str, Any]]:
    media_db = support_dir / "media_db/data.db"
    deadline = time.time() + seconds
    seen: list[dict[str, Any]] = []
    while time.time() < deadline:
        conn = sqlite3.connect(media_db)
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute(
                """
                select id, draftPath, outPath, firstSourcePath, state, createTime,
                       synthesisTime, composeSize, totalDuring, composedDuring
                from composeList where draftPath = ?
                """,
                (draft_path,),
            ).fetchone()
            if row is not None:
                snapshot = dict(row)
                if not seen or snapshot != seen[-1]:
                    seen.append(snapshot)
        finally:
            conn.close()
        time.sleep(1.0)
    return seen


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path, help="Live or offline project dir containing one .proj and proj.db")
    parser.add_argument("output_mp4", type=Path, help="Target output file path")
    parser.add_argument("--support-dir", type=Path, default=SUPPORT_DIR)
    parser.add_argument("--resolution-type", type=int, default=None)
    parser.add_argument("--initial-state", type=int, default=0)
    parser.add_argument("--use-cylinder", type=int, choices=[0, 1], default=None)
    parser.add_argument("--frame-rate", type=int, choices=[24, 25, 30, 50, 60], default=None)
    parser.add_argument("--bitrate-mode", choices=["default", "low", "medium", "high", "custom"], default="default")
    parser.add_argument("--custom-bitrate-mbps", type=float, default=None)
    parser.add_argument("--denoise", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--denoise-mode", choices=["performance", "quality"], default="quality")
    parser.add_argument("--ten-bit", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument(
        "--prefer-setting-frame-rate",
        action="store_true",
        help="Use DJI Studio's configured export frame-rate instead of preserving the source fps when they differ.",
    )
    parser.add_argument("--poll-seconds", type=float, default=12.0)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=get_project_root() / "output" / "compose_inject_manifest.json",
        help="Write injection result JSON here",
    )
    args = parser.parse_args()

    project_dir = args.project_dir.expanduser().resolve()
    output_mp4 = args.output_mp4.expanduser().resolve()
    support_dir = args.support_dir.expanduser().resolve()
    resolution_type = (
        args.resolution_type
        if args.resolution_type is not None
        else read_default_pano_resolution(SETTING_INI)
    )

    result = inject_task(
        project_dir,
        output_mp4,
        support_dir,
        resolution_type,
        args.initial_state,
        args.use_cylinder,
        not args.prefer_setting_frame_rate,
        args.frame_rate,
        None if args.bitrate_mode == "default" else args.bitrate_mode,
        args.custom_bitrate_mbps,
        args.denoise,
        args.denoise_mode,
        args.ten_bit,
    )
    result["poll"] = poll_task(support_dir, result["draft_path"], args.poll_seconds)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(args.manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
