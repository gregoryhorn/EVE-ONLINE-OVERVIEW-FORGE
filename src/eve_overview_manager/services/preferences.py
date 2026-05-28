"""Small JSON preferences store for local GUI defaults."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

from eve_overview_manager.services.paths import default_cache_dir, default_overview_dir


class GuiPreferences(BaseModel):
    importExportFolder: str
    groupNamesPath: str | None = None


def default_preferences_path() -> Path:
    return default_cache_dir() / "gui_preferences.json"


def load_gui_preferences(path: str | Path | None = None) -> GuiPreferences:
    preferences_path = default_preferences_path() if path is None else Path(path)
    if not preferences_path.exists():
        return GuiPreferences(importExportFolder=str(default_overview_dir()))
    return GuiPreferences.model_validate_json(preferences_path.read_text(encoding="utf-8"))


def save_gui_preferences(preferences: GuiPreferences, path: str | Path | None = None) -> GuiPreferences:
    preferences_path = default_preferences_path() if path is None else Path(path)
    preferences_path.parent.mkdir(parents=True, exist_ok=True)
    preferences_path.write_text(preferences.model_dump_json(indent=2), encoding="utf-8")
    return preferences


def remember_import_export_folder(folder: str | Path, path: str | Path | None = None) -> GuiPreferences:
    preferences = load_gui_preferences(path)
    preferences.importExportFolder = str(Path(folder))
    return save_gui_preferences(preferences, path=path)


def remember_group_names_path(group_names_path: str | Path | None, path: str | Path | None = None) -> GuiPreferences:
    preferences = load_gui_preferences(path)
    preferences.groupNamesPath = str(Path(group_names_path)) if group_names_path else None
    return save_gui_preferences(preferences, path=path)
