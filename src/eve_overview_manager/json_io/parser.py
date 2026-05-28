"""Strict canonical JSON parser."""

from __future__ import annotations

from pathlib import Path

from eve_overview_manager.models.overview import OverviewDocument


def load_overview_json(path: str | Path) -> OverviewDocument:
    return OverviewDocument.model_validate_json(Path(path).read_text(encoding="utf-8"))
