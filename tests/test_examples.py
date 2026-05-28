import json
from pathlib import Path

from eve_overview_manager.yaml_io.parser import load_overview_yaml


def test_sample_profile_report_fixture_has_resolved_character_names():
    report = json.loads(Path("Examples/sample_profile_report.json").read_text(encoding="utf-8"))

    character_names = {
        file["characterName"]
        for file in report["files"]
        if file["fileType"] == "core_char" and "characterName" in file
    }
    assert report["profilePath"] == "C:\\Example\\EVE\\settings_Default"
    assert report["counts"]["coreChar"] == 9
    assert "Mizz Betty" in character_names
    assert "EEL" in character_names


def test_community_overview_samples_parse_without_import_warnings():
    samples = sorted(Path("Examples/community-overviews").glob("*.yaml"))

    assert samples
    for sample in samples:
        document = load_overview_yaml(sample)
        assert document.meta.importWarnings == [], sample.name
        assert document.tabs or document.presets, sample.name


def test_standard_complete_overview_template_loads():
    document = load_overview_yaml("Examples/standard_complete_overview.yaml")

    assert document.meta.importWarnings == []
    assert len(document.tabs) >= 10
    assert len(document.presets) >= 12
    assert document.columns.enabled
    assert document.appearance.stateBlinks
