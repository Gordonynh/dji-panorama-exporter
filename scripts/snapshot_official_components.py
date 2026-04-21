#!/usr/bin/env python3
"""Copy selected DJI Studio official components into the local vendor directory."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from dji_paths import get_app_bundle, get_vendor_root


DEFAULT_RELATIVE_PATHS = [
    "Contents/MacOS/DJIStudio",
    "Contents/Frameworks/DualStitcher.framework",
    "Contents/Frameworks/libpano_selfcali.dylib",
    "Contents/PlugIns/DJIStudioQuickLookHost.app",
]


def copy_item(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    if dst.exists():
        if dst.is_dir() and not dst.is_symlink():
            shutil.rmtree(dst)
        else:
            dst.unlink()
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dst, symlinks=True, ignore_dangling_symlinks=True)
    else:
        shutil.copy2(src, dst)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--include-app-bundle",
        action="store_true",
        help="Copy the entire DJI Studio.app into vendor/. This is larger but more self-contained.",
    )
    args = parser.parse_args()

    app_bundle = get_app_bundle()
    vendor_root = get_vendor_root()
    vendor_root.mkdir(parents=True, exist_ok=True)

    if args.include_app_bundle:
        dst = vendor_root / app_bundle.name
        copy_item(app_bundle, dst)
        print(dst)
        return 0

    for rel in DEFAULT_RELATIVE_PATHS:
        src = app_bundle / rel
        dst = vendor_root / rel
        copy_item(src, dst)
        print(dst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
