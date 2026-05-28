"""Path helpers for likely local EVE folders."""

from __future__ import annotations

import os
from pathlib import Path


def likely_windows_eve_paths() -> list[Path]:
    paths: list[Path] = []
    local_app_data = os.environ.get("LOCALAPPDATA")
    user_profile = os.environ.get("USERPROFILE")
    if local_app_data:
        paths.append(Path(local_app_data) / "CCP" / "EVE")
    if user_profile:
        paths.append(Path(user_profile) / "Documents" / "EVE" / "Overview")
    return paths


def default_profile_root() -> Path | None:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        return None

    eve_root = Path(local_app_data) / "CCP" / "EVE"
    tranquility_default = eve_root / "c_ccp_eve_tq_tranquility" / "settings_Default"
    if tranquility_default.exists():
        return tranquility_default

    tranquility_root = eve_root / "c_ccp_eve_tq_tranquility"
    if tranquility_root.exists():
        return tranquility_root

    if eve_root.exists():
        setting_dirs = sorted(
            path
            for path in eve_root.rglob("settings_*")
            if path.is_dir() and ".bak_" not in path.name
        )
        if setting_dirs:
            return setting_dirs[0]
        return eve_root

    return eve_root


def default_cache_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "eve-overview-manager"
    return Path.home() / ".eve-overview-manager"


def default_overview_dir() -> Path:
    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        return Path(user_profile) / "Documents" / "EVE" / "Overview"
    return Path.home() / "Documents" / "EVE" / "Overview"
