#!/usr/bin/env python3
"""Launch the NativeApp in self-test mode and verify UI-driven export/cancel flow."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

APP_EXEC = Path('/Users/gordonyoung/Desktop/Projects/DJIStudio/NativeApp/.build/debug/DJIStudioNativeApp')
RUNTIME_ROOT = Path.home() / 'Library' / 'Application Support' / 'DJIStudioNativeApp'
RUNS_DIR = RUNTIME_ROOT / 'runs'
UI_CHECK_DIR = Path('/Users/gordonyoung/Desktop/Projects/DJIStudio/output/ui_checks')


def latest_json(pattern: str) -> Path | None:
    files = sorted(RUNS_DIR.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def take_screenshot(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['screencapture', '-x', str(path)], check=False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--stop-after', type=float, default=8.0)
    parser.add_argument('--wait-after', type=float, default=12.0)
    parser.add_argument('--summary', type=Path, required=True)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    before_manifests = {p.name for p in RUNS_DIR.glob('native_app_export_manifest_*.json')}
    before_progress = {p.name for p in RUNS_DIR.glob('native_app_export_progress_*.json')}

    proc = subprocess.Popen([
        str(APP_EXEC),
        '--ui-test-file', str(args.source.resolve()),
        '--ui-test-output-dir', str(args.output_dir.resolve()),
        '--ui-test-preset', '8k',
        '--ui-test-frame-rate', 'source',
        '--ui-test-bitrate-mode', 'high',
        '--ui-test-denoise',
        '--ui-test-denoise-mode', 'quality',
        '--ui-test-ten-bit',
        '--ui-test-parallel-count', '1',
        '--ui-test-autostart',
        '--ui-test-autostop-after', str(args.stop_after),
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    time.sleep(3)
    take_screenshot(UI_CHECK_DIR / 'native_app_smoke_running.png')
    time.sleep(args.wait_after)
    take_screenshot(UI_CHECK_DIR / 'native_app_smoke_after.png')

    manifest = None
    progress = None
    deadline = time.time() + 30
    while time.time() < deadline and (manifest is None or progress is None):
        m = latest_json('native_app_export_manifest_*.json')
        p = latest_json('native_app_export_progress_*.json')
        if m and m.name not in before_manifests:
            manifest = m
        if p and p.name not in before_progress:
            progress = p
        time.sleep(1)

    if proc.poll() is None:
        proc.send_signal(signal.SIGTERM)
    stdout, stderr = proc.communicate(timeout=30)

    manifest_data: dict[str, Any] | None = None
    progress_data: dict[str, Any] | None = None
    if manifest and manifest.exists():
        manifest_data = json.loads(manifest.read_text())
    if progress and progress.exists():
        progress_data = json.loads(progress.read_text())

    output_files = sorted(str(p) for p in args.output_dir.glob('*'))
    summary = {
        'source': str(args.source.resolve()),
        'output_dir': str(args.output_dir.resolve()),
        'manifest': str(manifest) if manifest else None,
        'progress': str(progress) if progress else None,
        'manifest_data': manifest_data,
        'progress_data': progress_data,
        'output_files_after': output_files,
        'stdout': stdout,
        'stderr': stderr,
        'returncode': proc.returncode,
        'screenshots': [
            str(UI_CHECK_DIR / 'native_app_smoke_running.png'),
            str(UI_CHECK_DIR / 'native_app_smoke_after.png'),
        ],
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(args.summary.resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
