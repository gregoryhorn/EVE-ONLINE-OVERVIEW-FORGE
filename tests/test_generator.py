import json
from pathlib import Path

from eve_overview_manager.generator.builder import build_overview_document, load_generator_spec
from eve_overview_manager.validation.engine import validate_overview


def test_generator_builds_valid_overview_document_from_sample_spec():
    document = build_overview_document(load_generator_spec("Examples/sample_generator.json"))

    assert document.meta.sourceFormat == "codex-generator"
    assert [tab.label for tab in document.tabs] == ["Hostile", "Travel"]
    assert [preset.id for preset in document.presets] == ["hostile", "travel"]
    assert document.columns.enabled == ["ICON", "DISTANCE", "NAME", "TYPE"]
    assert validate_overview(document) == []


def test_generator_spec_is_valid_json_fixture():
    spec = json.loads(Path("Examples/sample_generator.json").read_text(encoding="utf-8"))

    assert spec["schemaVersion"] == "codex-generator/v1"
    assert len(spec["tabs"]) == 2
