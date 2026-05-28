"""Canonical JSON exporter."""

from __future__ import annotations

from pathlib import Path

from eve_overview_manager.models.overview import OverviewDocument


def export_overview_json(document: OverviewDocument, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document.model_dump_json(indent=2), encoding="utf-8")
