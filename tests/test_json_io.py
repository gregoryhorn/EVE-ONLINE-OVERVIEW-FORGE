import pytest
from pydantic import ValidationError

from eve_overview_manager.json_io.exporter import export_overview_json
from eve_overview_manager.json_io.parser import load_overview_json
from eve_overview_manager.validation.engine import validate_overview
from eve_overview_manager.yaml_io.exporter import export_overview_yaml
from eve_overview_manager.yaml_io.parser import load_overview_yaml


def test_load_sample_canonical_json():
    document = load_overview_json("Examples/sample_canonical.json")

    assert document.schemaVersion == "codex-overview/v1"
    assert document.presets[0].name == "PVP Main"


def test_export_json_from_real_yaml_reloads_and_validates(tmp_path):
    json_path = tmp_path / "real.json"

    export_overview_json(load_overview_yaml("Examples/Real-Overview.yaml"), json_path)
    document = load_overview_json(json_path)

    assert len(document.tabs) == 9
    assert validate_overview(document) == []


def test_export_yaml_from_json_validates(tmp_path):
    json_path = tmp_path / "real.json"
    yaml_path = tmp_path / "real.yaml"

    export_overview_json(load_overview_yaml("Examples/Real-Overview.yaml"), json_path)
    export_overview_yaml(load_overview_json(json_path), yaml_path)
    document = load_overview_yaml(yaml_path)

    assert document.meta.importWarnings == []
    assert validate_overview(document) == []


def test_invalid_json_shape_fails_strictly(tmp_path):
    json_path = tmp_path / "bad.json"
    json_path.write_text('{"tabs": "not-a-list"}', encoding="utf-8")

    with pytest.raises(ValidationError):
        load_overview_json(json_path)
