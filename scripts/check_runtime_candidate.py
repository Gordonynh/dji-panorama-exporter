#!/usr/bin/env python3
"""Quick checks for the runtime candidate layout."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_APP = PROJECT_ROOT / "runtime_candidate" / "DJI Studio.app"

REQUIRED = [
    "Contents/MacOS/DJIStudio",
    "Contents/Frameworks/DualStitcher.framework",
    "Contents/Frameworks/MKMediaEditor.framework",
    "Contents/Frameworks/libpano_selfcali.dylib",
    "Contents/Resources/filter",
    "Contents/Resources/qml",
    "Contents/PlugIns/platforms",
    "Contents/PlugIns/quick",
]


def main() -> int:
    missing = []
    for rel in REQUIRED:
        path = RUNTIME_APP / rel
        print(f"{rel}: {'ok' if path.exists() else 'missing'}")
        if not path.exists():
            missing.append(rel)
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
