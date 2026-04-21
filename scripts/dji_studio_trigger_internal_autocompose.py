#!/usr/bin/env python3
"""Trigger DJI Studio's internal autoCompose(true) path without clicking Export."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from dji_paths import get_app_bin, get_app_bundle, get_project_root  # noqa: E402

APP_BIN = str(get_app_bin())
APP_BUNDLE = get_app_bundle()
SYMBOLS = {
    "auto_compose": "__ZN18ExportTabViewModel11autoComposeEb",
    "ctor": "__ZN18ExportTabViewModelC2EP7QObject",
    "export_list_count": "__ZNK18ExportTabViewModel15exportListCountEv",
}


def run(cmd: list[str] | str, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        shell=isinstance(cmd, str),
        text=True,
        capture_output=True,
        errors="replace",
        check=check,
    )


def iter_dji_processes() -> list[tuple[int, str, str]]:
    proc = run(
        ["ps", "ax", "-o", "pid=", "-o", "comm=", "-o", "args="],
        check=True,
    )
    rows: list[tuple[int, str, str]] = []
    for line in proc.stdout.splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) != 3 or not parts[0].isdigit():
            continue
        rows.append((int(parts[0]), parts[1], parts[2]))
    return rows


def get_pid() -> int:
    fallback = None
    for pid, comm, args in iter_dji_processes():
        if "Contents/MacOS/DJIStudio" not in args:
            continue
        if "QuickLookHost" in args or "crashpad_handler" in args:
            continue
        if APP_BIN in args:
            return pid
        fallback = fallback or pid
    if fallback is not None:
        return fallback
    raise SystemExit("DJIStudio is not running")


def hide_process(pid: int) -> None:
    script = f"""
tell application "System Events"
  repeat with p in every process
    try
      if unix id of p is {pid} then
        set visible of p to false
        return
      end if
    end try
  end repeat
end tell
"""
    subprocess.run(
        ["osascript", "-e", script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def launch_if_needed(*, background: bool = True) -> None:
    bundle_path = Path(APP_BUNDLE)
    if bundle_path.exists():
        cmd = ["open", "-na"]
        cmd.append(str(bundle_path))
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    elif Path(APP_BIN).exists():
        subprocess.Popen([APP_BIN], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        raise SystemExit(f"DJI Studio binary not found: {APP_BIN}")


def get_vmaddr(symbol: str) -> int:
    proc = run(f"nm -gU '{APP_BIN}' | rg '{re.escape(symbol)}'")
    match = re.search(r"([0-9a-fA-F]{16})", proc.stdout)
    if not match:
        raise SystemExit(f"Failed to resolve symbol: {symbol}")
    return int(match.group(1), 16)


def get_slide(pid: int) -> int:
    proc = run(
        [
            "lldb",
            "-b",
            "-o",
            f"process attach --pid {pid}",
            "-o",
            "image list -o -f",
            "-o",
            "detach",
            "-o",
            "quit",
        ]
    )
    for line in proc.stdout.splitlines():
        if "DJIStudio" in line:
            match = re.search(r"\[\s*0\]\s+0x([0-9a-fA-F]+)", line)
            if match:
                return int(match.group(1), 16)
    raise SystemExit("Failed to resolve runtime slide")


def wait_for_pid(seconds: float) -> int:
    deadline = time.time() + seconds
    while time.time() < deadline:
        try:
            return get_pid()
        except SystemExit:
            pass
        time.sleep(0.2)
    raise SystemExit("DJIStudio did not start in time")


def build_lldb_script(pid: int, runtime: dict[str, int]) -> str:
    return "\n".join(
        [
            f"process attach --pid {pid}",
            "expr -l c++ -- void *$vm = (void*)calloc(1, 1024)",
            f"expr -l c++ -- ((void (*)(void*, void*))0x{runtime['ctor']:x})($vm, (void*)0)",
            (
                "expr -l c++ -- (int)printf(\"EXPORT_LIST_COUNT=%lld\\n\", "
                f"((long long (*)(void*))0x{runtime['export_list_count']:x})($vm))"
            ),
            f"expr -l c++ -- ((void (*)(void*, bool))0x{runtime['auto_compose']:x})($vm, true)",
            "detach",
            "quit",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--launch-if-needed", action="store_true")
    parser.add_argument(
        "--foreground-launch",
        action="store_true",
        help="When launching DJI Studio, allow it to activate normally instead of starting hidden/background.",
    )
    parser.add_argument("--wait-seconds", type=float, default=8.0)
    parser.add_argument("--warmup-seconds", type=float, default=5.0)
    parser.add_argument(
        "--output",
        type=Path,
        default=get_project_root() / "output" / "internal_autocompose_last.txt",
        help="Write a small debug report here",
    )
    args = parser.parse_args()

    launched = False
    try:
        pid = get_pid()
    except SystemExit:
        if not args.launch_if_needed:
            raise
        launch_if_needed(background=not args.foreground_launch)
        pid = wait_for_pid(args.wait_seconds)
        launched = True
    if not args.foreground_launch:
        hide_process(pid)
    if launched and args.warmup_seconds > 0:
        time.sleep(args.warmup_seconds)

    slide = get_slide(pid)
    runtime = {name: get_vmaddr(symbol) + slide for name, symbol in SYMBOLS.items()}
    lldb_script = build_lldb_script(pid, runtime)

    with tempfile.NamedTemporaryFile("w", suffix=".lldb", delete=False) as handle:
        handle.write(lldb_script)
        lldb_path = handle.name

    try:
        proc = run(["lldb", "-s", lldb_path], check=False)
    finally:
        Path(lldb_path).unlink(missing_ok=True)

    report = [
        f"pid={pid}",
        f"slide=0x{slide:x}",
        *(f"{name}=0x{addr:x}" for name, addr in runtime.items()),
        "--- stdout ---",
        proc.stdout.strip(),
        "--- stderr ---",
        proc.stderr.strip(),
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(report) + "\n")

    count_match = re.search(r"EXPORT_LIST_COUNT=(\d+)|\(int\)\s+\$\d+\s+=\s+(\d+)", proc.stdout)
    if count_match:
        print(f"EXPORT_LIST_COUNT={count_match.group(1) or count_match.group(2)}")
    else:
        print("EXPORT_LIST_COUNT=unknown")
    print(args.output.resolve())
    if proc.returncode != 0:
        if proc.stdout:
            sys.stdout.write(proc.stdout)
        if proc.stderr:
            sys.stderr.write(proc.stderr)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
