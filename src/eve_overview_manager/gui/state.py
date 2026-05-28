"""Shared in-memory app state for the GUI server."""

from __future__ import annotations

from pathlib import Path
from typing import Any

_current_document: dict[str, Any] | None = None
_current_path: Path | None = None
_recent_files: list[dict[str, Any]] = []


def get_document() -> dict[str, Any] | None:
    return _current_document


def get_current_path() -> Path | None:
    return _current_path


def set_document(doc: dict[str, Any], path: Path | None = None) -> None:
    global _current_document, _current_path
    _current_document = doc
    _current_path = path
    if path:
        _push_recent(path, doc)


def _push_recent(path: Path, doc: dict[str, Any]) -> None:
    import datetime
    entry = {
        "path": str(path),
        "name": path.name,
        "tabCount": len(doc.get("tabs", [])),
        "presetCount": len(doc.get("presets", [])),
        "openedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    global _recent_files
    _recent_files = [e for e in _recent_files if e["path"] != str(path)]
    _recent_files.insert(0, entry)
    _recent_files = _recent_files[:5]


def get_recent_files() -> list[dict[str, Any]]:
    return _recent_files
