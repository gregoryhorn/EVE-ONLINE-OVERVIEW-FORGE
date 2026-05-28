from pathlib import Path

from ruamel.yaml import YAML

from eve_overview_manager.yaml_io.parser import load_overview_yaml
from eve_overview_manager.yaml_io.roundtrip import roundtrip_overview_yaml


def top_level_keys(path):
    yaml = YAML(typ="rt")
    with Path(path).open("r", encoding="utf-8") as file:
        return list((yaml.load(file) or {}).keys())


def yaml_data(path):
    yaml = YAML(typ="rt")
    with Path(path).open("r", encoding="utf-8") as file:
        return yaml.load(file) or {}


def pair_keys(pair_list):
    return [item[0] for item in pair_list if isinstance(item, list) and len(item) == 2]


def test_yaml_parser_loads_sample_file():
    document = load_overview_yaml(Path("Examples/sample_overview.yaml"))

    assert document.presets[0].name == "PVP Main"
    assert "unknownTopLevelExample" in document.unknown
    assert document.meta.topLevelKeyOrder[0] == "unknownTopLevelExample"


def test_yaml_roundtrip_preserves_unknown_top_level_key(tmp_path):
    output = tmp_path / "roundtrip.yaml"

    roundtrip_overview_yaml(Path("Examples/sample_overview.yaml"), output)
    document = load_overview_yaml(output)

    assert document.unknown["unknownTopLevelExample"]["preserved"] is True


def test_real_overview_yaml_loads_tabs_and_pair_lists():
    document = load_overview_yaml(Path("Examples/Real-Overview.yaml"))

    assert len(document.presets) > 1
    assert len(document.tabs) == 9
    assert document.tabs[0].label == "NORMAL"
    assert document.tabs[0].overviewPresetRef == "PRIMARY"
    assert document.tabs[0].bracketPresetRef == "_BracketFilterShowAll"
    assert document.tabs[0].colorARGB == "FF40FF40"
    assert document.tabs[0].fieldOrder == ["bracket", "color", "name", "overview", "tabColumns"]
    assert document.presets[0].fieldOrder == ["alwaysShownStates", "filteredStates", "groups"]
    assert document.tabs[1].unknown["tabColumns"]
    assert document.appearance.stateBlinks["background_13"] is True
    assert document.appearance.stateBlinksOrder[0] == "background_13"
    assert document.appearance.stateColors["flag_44"] == "red"
    assert document.appearance.stateColorsOrder[0] == "background_44"


def test_real_overview_roundtrip_preserves_recognized_real_fields(tmp_path):
    output = tmp_path / "real-roundtrip.yaml"
    original = load_overview_yaml(Path("Examples/Real-Overview.yaml"))

    roundtrip_overview_yaml(Path("Examples/Real-Overview.yaml"), output)
    document = load_overview_yaml(output)

    assert len(document.presets) == len(original.presets)
    assert len(document.tabs) == len(original.tabs)
    assert len(document.appearance.stateBlinks) == len(original.appearance.stateBlinks)
    assert len(document.appearance.stateColors) == len(original.appearance.stateColors)
    assert len(document.labels.shipLabels) == len(original.labels.shipLabels)
    assert len(document.misc.userSettings) == len(original.misc.userSettings)
    assert document.tabs[1].unknown["tabColumnOrder"]
    assert document.appearance.stateBlinks["flag_68"] is True
    assert document.appearance.stateColors["background_52"] == "orange"


def test_real_overview_roundtrip_preserves_top_level_key_order(tmp_path):
    output = tmp_path / "real-roundtrip.yaml"
    original_order = top_level_keys("Examples/Real-Overview.yaml")

    roundtrip_overview_yaml(Path("Examples/Real-Overview.yaml"), output)

    assert top_level_keys(output) == original_order


def test_unknown_top_level_key_keeps_original_position(tmp_path):
    output = tmp_path / "roundtrip.yaml"
    original_order = top_level_keys("Examples/sample_overview.yaml")

    roundtrip_overview_yaml(Path("Examples/sample_overview.yaml"), output)

    assert top_level_keys(output)[0] == "unknownTopLevelExample"
    assert top_level_keys(output)[: len(original_order)] == original_order


def test_real_overview_roundtrip_preserves_tab_field_order(tmp_path):
    output = tmp_path / "real-roundtrip.yaml"
    original = yaml_data("Examples/Real-Overview.yaml")

    roundtrip_overview_yaml(Path("Examples/Real-Overview.yaml"), output)
    exported = yaml_data(output)

    assert pair_keys(exported["tabSetup"][0][1]) == pair_keys(original["tabSetup"][0][1])
    assert pair_keys(exported["tabSetup"][1][1]) == pair_keys(original["tabSetup"][1][1])


def test_real_overview_roundtrip_preserves_preset_field_order(tmp_path):
    output = tmp_path / "real-roundtrip.yaml"
    original = yaml_data("Examples/Real-Overview.yaml")

    roundtrip_overview_yaml(Path("Examples/Real-Overview.yaml"), output)
    exported = yaml_data(output)

    assert pair_keys(exported["presets"][0][1]) == pair_keys(original["presets"][0][1])


def test_real_overview_roundtrip_preserves_remaining_pair_list_order(tmp_path):
    output = tmp_path / "real-roundtrip.yaml"
    original = yaml_data("Examples/Real-Overview.yaml")

    roundtrip_overview_yaml(Path("Examples/Real-Overview.yaml"), output)
    exported = yaml_data(output)

    assert pair_keys(exported["shipLabels"]) == pair_keys(original["shipLabels"])
    assert pair_keys(exported["userSettings"]) == pair_keys(original["userSettings"])
    assert pair_keys(exported["stateBlinks"]) == pair_keys(original["stateBlinks"])
    assert pair_keys(exported["stateColorsNameList"]) == pair_keys(original["stateColorsNameList"])


def test_tehl_style_tab_color_in_name_is_modeled_and_preserved(tmp_path):
    output = tmp_path / "tehl-roundtrip.yaml"
    document = load_overview_yaml(Path("Examples/tehl_style_overview.yaml"))

    assert document.tabs[0].label == "<color=0xFFFF4444>   hostile   </color>"
    assert document.tabs[0].colorARGB == "FFFF4444"

    roundtrip_overview_yaml(Path("Examples/tehl_style_overview.yaml"), output)
    exported = yaml_data(output)

    assert exported["tabSetup"][0][1][0] == ["name", "<color=0xFFFF4444>   hostile   </color>"]
    assert pair_keys(exported["shipLabels"][0][1]) == ["post", "pre", "state", "type"]


def test_valid_real_overview_has_no_import_warnings():
    document = load_overview_yaml(Path("Examples/Real-Overview.yaml"))

    assert document.meta.importWarnings == []


def test_malformed_preset_entry_produces_import_warning(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("presets:\n  - bad-entry\n", encoding="utf-8")

    document = load_overview_yaml(path)

    assert document.presets == []
    assert document.meta.importWarnings[0].code == "YAML_PRESET_ENTRY_INVALID"
    assert document.meta.importWarnings[0].path == "presets[0]"


def test_invalid_tab_slot_produces_import_warning(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("tabSetup:\n  - - not-a-slot\n    - []\n", encoding="utf-8")

    document = load_overview_yaml(path)

    assert document.tabs == []
    assert document.meta.importWarnings[0].code == "YAML_TAB_SLOT_INVALID"


def test_malformed_pair_list_entry_warns_but_keeps_valid_pairs(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("userSettings:\n  - [hideCorpTicker, true]\n  - malformed\n", encoding="utf-8")

    document = load_overview_yaml(path)

    assert document.misc.userSettings["hideCorpTicker"] is True
    assert document.meta.importWarnings[0].code == "YAML_PAIR_ENTRY_INVALID"
