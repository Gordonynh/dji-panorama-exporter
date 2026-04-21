#!/usr/bin/env python3
"""Shared path/config resolver for the DJIStudio project."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "dji_paths.json"


def load_config() -> dict[str, Any]:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return {}


def _path_from_env_or_config(env_key: str, config_key: str, default: str) -> Path:
    cfg = load_config()
    raw = os.environ.get(env_key) or cfg.get(config_key) or default
    return Path(raw).expanduser().resolve()


def get_project_root() -> Path:
    return PROJECT_ROOT


def get_vendor_root() -> Path:
    return _path_from_env_or_config(
        "DJI_STUDIO_VENDOR_ROOT",
        "vendor_root",
        str(PROJECT_ROOT / "vendor"),
    )


def get_runtime_root() -> Path:
    return _path_from_env_or_config(
        "DJI_STUDIO_RUNTIME_ROOT",
        "runtime_root",
        str(PROJECT_ROOT / "runtime_candidate"),
    )


def get_support_dir() -> Path:
    return _path_from_env_or_config(
        "DJI_STUDIO_SUPPORT_DIR",
        "support_dir",
        str(Path.home() / "Library/Application Support/DJI Studio"),
    )


def get_setting_ini() -> Path:
    return get_support_dir() / "setting.ini"


def get_app_bundle() -> Path:
    cfg = load_config()
    component_mode = cfg.get("component_mode")
    env_bundle = os.environ.get("DJI_STUDIO_APP_BUNDLE")
    if env_bundle:
        return Path(env_bundle).expanduser().resolve()
    if component_mode == "runtime_candidate":
        runtime_root = get_runtime_root()
        runtime_bundle = runtime_root / "DJI Studio.app"
        if runtime_bundle.exists():
            return runtime_bundle
        if (runtime_root / "Contents" / "MacOS" / "DJIStudio").exists():
            return runtime_root
    prefer_vendor = bool(cfg.get("prefer_vendor_components"))
    if component_mode == "vendor" or (component_mode is None and prefer_vendor):
        vendor_root = get_vendor_root()
        vendored_bundle = vendor_root / "DJI Studio.app"
        if vendored_bundle.exists():
            return vendored_bundle
        vendored_partial = vendor_root
        if (vendored_partial / "Contents" / "MacOS" / "DJIStudio").exists():
            return vendored_partial
    bundle = cfg.get("app_bundle") or "/Applications/DJI Studio.app"
    return Path(bundle).expanduser().resolve()


def get_app_bin() -> Path:
    return get_app_bundle() / "Contents" / "MacOS" / "DJIStudio"


def get_source_default() -> Path:
    return _path_from_env_or_config(
        "DJI_STUDIO_SOURCE_DEFAULT",
        "source_default",
        str(PROJECT_ROOT / "examples"),
    )


def get_output_default() -> Path:
    return _path_from_env_or_config(
        "DJI_STUDIO_OUTPUT_DEFAULT",
        "output_default",
        str(PROJECT_ROOT / "output"),
    )
