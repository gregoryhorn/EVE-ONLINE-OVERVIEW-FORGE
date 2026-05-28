"""YAML round-trip helper."""

from __future__ import annotations

from pathlib import Path

from eve_overview_manager.yaml_io.exporter import export_overview_yaml
from eve_overview_manager.yaml_io.parser import load_overview_yaml


def roundtrip_overview_yaml(input_path: str | Path, output_path: str | Path) -> None:
    export_overview_yaml(load_overview_yaml(input_path), output_path)
