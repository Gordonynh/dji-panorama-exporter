#!/usr/bin/env python3
"""Build a runtime candidate by copying vendor app and pruning only confirmed non-export extras."""

from __future__ import annotations

import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENDOR_APP = PROJECT_ROOT / "vendor" / "DJI Studio.app"
RUNTIME_ROOT = PROJECT_ROOT / "runtime_candidate"

REMOVE_PATHS = [
    "Contents/Resources/appcast.xml",
    "Contents/Resources/UserGuideVideo.mp4",
    "Contents/Resources/ThirdCopyright.txt",
    "Contents/Resources/filter",
    "Contents/Resources/resource",
    "Contents/Resources/resource/dashboard",
    "Contents/Resources/tracking",
    "Contents/PlugIns/DJIStudioQuickLookHost.app",
    "Contents/PlugIns/iconengines",
    "Contents/PlugIns/networkinformation",
    "Contents/PlugIns/geometryloaders",
    "Contents/PlugIns/sceneparsers",
    "Contents/PlugIns/styles",
    "Contents/PlugIns/renderplugins",
    "Contents/PlugIns/renderers",
    "Contents/PlugIns/imageformats",
    "Contents/PlugIns/multimedia",
    "Contents/PlugIns/tls",
]


def remove_path(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def main() -> int:
    if RUNTIME_ROOT.exists():
        shutil.rmtree(RUNTIME_ROOT)
    shutil.copytree(VENDOR_APP, RUNTIME_ROOT / "DJI Studio.app", symlinks=True, ignore_dangling_symlinks=True)
    runtime_app = RUNTIME_ROOT / "DJI Studio.app"
    for rel in REMOVE_PATHS:
        remove_path(runtime_app / rel)
        print(f"removed {rel}")
    print(runtime_app)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
