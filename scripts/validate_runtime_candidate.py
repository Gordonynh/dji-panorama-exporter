#!/usr/bin/env python3
"""Build and validate the runtime candidate, then write a small JSON report."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from dji_paths import get_project_root


PROJECT_ROOT = get_project_root()
BUILD_SCRIPT = PROJECT_ROOT / "scripts" / "build_runtime_candidate.py"
SMOKE_SCRIPT = PROJECT_ROOT / "scripts" / "smoke_test_runtime_candidate.py"
VENDOR_APP = PROJECT_ROOT / "vendor" / "DJI Studio.app"
RUNTIME_APP = PROJECT_ROOT / "runtime_candidate" / "DJI Studio.app"
OUTPUT_DIR = PROJECT_ROOT / "output"
REPORT_PATH = OUTPUT_DIR / "runtime_candidate_validation.json"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def du_bytes(path: Path) -> int | None:
    if not path.exists():
        return None
    total = 0
    for entry in path.rglob("*"):
        try:
            if entry.is_file():
                total += entry.stat().st_size
        except FileNotFoundError:
            continue
    return total


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    build = run(["python3", str(BUILD_SCRIPT)])
    smoke = run(["python3", str(SMOKE_SCRIPT)])

    quicklook_path = RUNTIME_APP / "Contents" / "PlugIns" / "DJIStudioQuickLookHost.app"
    if quicklook_path.exists():
        shutil.rmtree(quicklook_path)
    smoke_without_quicklook = run(["python3", str(SMOKE_SCRIPT)])

    report = {
        "vendor_app": str(VENDOR_APP),
        "runtime_app": str(RUNTIME_APP),
        "vendor_size_bytes": du_bytes(VENDOR_APP),
        "runtime_size_bytes": du_bytes(RUNTIME_APP),
        "quicklook_removed_for_startup_test": True,
        "quicklook_present_after_test": quicklook_path.exists(),
        "build_returncode": build.returncode,
        "build_stdout": build.stdout[-4000:],
        "build_stderr": build.stderr[-4000:],
        "smoke_returncode": smoke.returncode,
        "smoke_stdout": smoke.stdout[-12000:],
        "smoke_stderr": smoke.stderr[-12000:],
        "smoke_without_quicklook_returncode": smoke_without_quicklook.returncode,
        "smoke_without_quicklook_stdout": smoke_without_quicklook.stdout[-12000:],
        "smoke_without_quicklook_stderr": smoke_without_quicklook.stderr[-12000:],
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(REPORT_PATH)
    print(f"startup_ok={'startup_ok=true' in smoke.stdout}")
    print(f"startup_ok_without_quicklook={'startup_ok=true' in smoke_without_quicklook.stdout}")
    return 0 if smoke.returncode == 0 and smoke_without_quicklook.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
