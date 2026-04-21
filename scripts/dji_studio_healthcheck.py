#!/usr/bin/env python3
"""Run a non-destructive health check for the DJI Studio export toolchain."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from dji_paths import get_app_bin, get_project_root, get_setting_ini, get_support_dir  # noqa: E402

APP_BIN = get_app_bin()
SUPPORT_DIR = get_support_dir()
PROJECT_DIR = SUPPORT_DIR / "project"
MEDIA_DB = SUPPORT_DIR / "media_db/data.db"
SETTING_INI = get_setting_ini()
TEMPLATE_PROJECT = PROJECT_DIR / "24"
SYMBOLS = {
    "auto_compose": "__ZN18ExportTabViewModel11autoComposeEb",
    "ctor": "__ZN18ExportTabViewModelC2EP7QObject",
    "start_compose": "__ZN9pc_editor14ComposeManager12startComposeERK7QStringS3_S3_RK4QMapIS1_8QVariantEbbNS_11VideoConfig12ComposeRangeE",
}


def run(cmd: list[str] | str, check: bool = True) -> subprocess.CompletedProcess[str]:
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


def get_pid() -> int | None:
    fallback = None
    for pid, comm, args in iter_dji_processes():
        if "Contents/MacOS/DJIStudio" not in args:
            continue
        if "QuickLookHost" in args or "crashpad_handler" in args:
            continue
        if APP_BIN.as_posix() in args:
            return pid
        fallback = fallback or pid
    return fallback


def check_attach(pid: int) -> dict[str, object]:
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
        ],
        check=False,
    )
    ok = proc.returncode == 0 and "Process " in proc.stdout
    slide = None
    if ok:
        for line in proc.stdout.splitlines():
            if "DJIStudio" in line:
                match = re.search(r"\[\s*0\]\s+0x([0-9a-fA-F]+)", line)
                if match:
                    slide = f"0x{match.group(1)}"
                    break
    return {
        "ok": ok,
        "slide": slide,
        "stdout_tail": "\n".join(proc.stdout.splitlines()[-12:]),
        "stderr_tail": "\n".join(proc.stderr.splitlines()[-12:]),
    }


def resolve_symbols() -> dict[str, object]:
    results: dict[str, object] = {}
    if not APP_BIN.exists():
        return {"ok": False, "symbols": results}
    nm = shutil.which("nm")
    if not nm:
        return {"ok": False, "symbols": results, "error": "nm not found"}
    ok = True
    for name, symbol in SYMBOLS.items():
        proc = run(f"nm -gU '{APP_BIN}' | rg '{re.escape(symbol)}'", check=False)
        match = re.search(r"([0-9a-fA-F]{16})", proc.stdout)
        if match:
            results[name] = {"symbol": symbol, "vmaddr": f"0x{match.group(1)}"}
        else:
            ok = False
            results[name] = {"symbol": symbol, "vmaddr": None}
    return {"ok": ok, "symbols": results}


def count_live_projects() -> dict[str, object]:
    project_count = 0
    db_count = 0
    if PROJECT_DIR.exists():
        for child in PROJECT_DIR.iterdir():
            if child.is_dir() and child.name.isdigit():
                project_count += 1
                if (child / "proj.db").exists():
                    db_count += 1
    return {"project_dirs": project_count, "project_dbs": db_count}


def media_db_stats() -> dict[str, object]:
    if not MEDIA_DB.exists():
        return {"ok": False}
    conn = sqlite3.connect(MEDIA_DB)
    try:
        compose_count = conn.execute("select count(*) from composeList").fetchone()[0]
        export_count = conn.execute("select count(*) from exportDataTable").fetchone()[0]
        draft_count = conn.execute("select count(*) from project_draft_v2").fetchone()[0]
    finally:
        conn.close()
    return {
        "ok": True,
        "compose_count": compose_count,
        "export_count": export_count,
        "project_draft_count": draft_count,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json-out",
        type=Path,
        default=get_project_root() / "output" / "healthcheck.json",
    )
    args = parser.parse_args()

    pid = get_pid()
    tool_paths = {name: shutil.which(name) for name in ("python3", "ffprobe", "lldb", "nm", "rg")}
    attach = check_attach(pid) if pid else {"ok": False, "reason": "DJIStudio is not running"}

    report = {
        "app_bin": {"path": str(APP_BIN), "exists": APP_BIN.exists()},
        "support_dir": {"path": str(SUPPORT_DIR), "exists": SUPPORT_DIR.exists()},
        "setting_ini": {"path": str(SETTING_INI), "exists": SETTING_INI.exists()},
        "template_project_24": {"path": str(TEMPLATE_PROJECT), "exists": TEMPLATE_PROJECT.exists()},
        "media_db": {"path": str(MEDIA_DB), "exists": MEDIA_DB.exists(), **media_db_stats()},
        "live_projects": count_live_projects(),
        "tools": tool_paths,
        "running_pid": pid,
        "attach_test": attach,
        "symbols": resolve_symbols(),
    }

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.json_out.resolve())

    if not APP_BIN.exists():
        return 2
    if not tool_paths["ffprobe"] or not tool_paths["lldb"]:
        return 3
    if pid and not attach.get("ok"):
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
