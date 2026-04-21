#!/usr/bin/env python3
"""Toggle DJIStudio project between installed, vendor, and runtime-candidate modes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from dji_paths import CONFIG_PATH, get_runtime_root, get_vendor_root


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("installed", "vendor", "runtime_candidate"))
    args = parser.parse_args()

    data = {}
    if CONFIG_PATH.exists():
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

    if args.mode == "installed":
        data["prefer_vendor_components"] = False
        data["component_mode"] = "installed"
    elif args.mode == "vendor":
        vendor_root = get_vendor_root()
        vendor_bundle = vendor_root / "DJI Studio.app"
        if not vendor_bundle.exists() and not (vendor_root / "Contents" / "MacOS" / "DJIStudio").exists():
            raise SystemExit("vendor components not found; run snapshot_official_components.py first")
        data["prefer_vendor_components"] = True
        data["component_mode"] = "vendor"
    else:
        runtime_root = get_runtime_root()
        runtime_bundle = runtime_root / "DJI Studio.app"
        if not runtime_bundle.exists() and not (runtime_root / "Contents" / "MacOS" / "DJIStudio").exists():
            raise SystemExit("runtime candidate not found; run build_runtime_candidate.py first")
        data["prefer_vendor_components"] = False
        data["component_mode"] = "runtime_candidate"

    CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(CONFIG_PATH)
    print(f"mode={args.mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
