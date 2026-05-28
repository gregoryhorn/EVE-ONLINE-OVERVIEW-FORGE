from eve_overview_manager.models.overview import AppearanceConfig, ColumnsConfig, OverviewDocument, OverviewMeta, Preset, TabBinding
from eve_overview_manager.validation.engine import validate_overview
from eve_overview_manager.validation.group_validator import InMemoryGroupValidator, load_group_ids
from eve_overview_manager.yaml_io.parser import load_overview_yaml


def codes(document):
    return {result.code for result in validate_overview(document)}


def test_duplicate_tab_slots_are_detected():
    document = OverviewDocument(tabs=[TabBinding(slot=1, label="A"), TabBinding(slot=1, label="B")])

    assert "TAB_SLOT_UNIQUE" in codes(document)


def test_current_tab_limit_over_configured_cap_fails():
    document = OverviewDocument(tabs=[TabBinding(slot=index, label=str(index)) for index in range(21)])

    assert "TAB_LIMIT_CURRENT" in codes(document)


def test_legacy_tab_limit_over_five_fails():
    document = OverviewDocument(
        meta=OverviewMeta(compatibilityMode="legacy"),
        tabs=[TabBinding(slot=index, label=str(index)) for index in range(6)],
    )

    assert "TAB_LIMIT_LEGACY" in codes(document)


def test_invalid_argb_color_is_detected():
    document = OverviewDocument(tabs=[TabBinding(slot=1, label="A", colorARGB="red")])

    assert "COLOR_FORMAT" in codes(document)


def test_missing_preset_reference_is_detected():
    document = OverviewDocument(tabs=[TabBinding(slot=1, label="A", overviewPresetRef="missing")])

    assert "PRESET_REF_EXISTS" in codes(document)


def test_builtin_bracket_show_all_reference_is_allowed():
    document = OverviewDocument(tabs=[TabBinding(slot=1, label="A", bracketPresetRef="_BracketFilterShowAll")])

    assert "PRESET_REF_EXISTS" not in codes(document)


def test_default_preset_reference_is_allowed():
    document = OverviewDocument(tabs=[TabBinding(slot=1, label="A", overviewPresetRef="DefaultPreset_639448")])

    assert "PRESET_REF_EXISTS" not in codes(document)


def test_group_and_state_ids_must_be_integers():
    document = OverviewDocument(presets=[Preset(id="a", name="A", groups=["25"], alwaysShownStates=["11"])])

    result_codes = codes(document)
    assert "GROUP_ID_INTEGER" in result_codes
    assert "STATE_ID_INTEGER" in result_codes


def test_column_enabled_must_be_subset_of_order():
    document = OverviewDocument(columns=ColumnsConfig(columnOrder=["ICON"], enabled=["ICON", "NAME"]))

    assert "COLUMN_SUBSET" in codes(document)


def test_unknown_column_warns():
    document = OverviewDocument(columns=ColumnsConfig(columnOrder=["ICON", "MADE_UP"], enabled=["ICON"]))

    assert "COLUMN_KNOWN" in codes(document)


def test_invalid_state_blink_key_warns():
    document = OverviewDocument(appearance=AppearanceConfig(stateBlinks={"bad_13": True}))

    assert "STATE_BLINK_KEY_FORMAT" in codes(document)


def test_unknown_state_id_warns():
    document = OverviewDocument(presets=[Preset(id="a", name="A", alwaysShownStates=[999999])])

    assert "STATE_ID_KNOWN" in codes(document)


def test_non_integer_appearance_state_order_fails():
    document = OverviewDocument(appearance=AppearanceConfig(flagOrder=["11"]))

    assert "STATE_ORDER_INTEGER" in codes(document)


def test_mock_group_validator_warns_for_unknown_group_id():
    document = OverviewDocument(presets=[Preset(id="a", name="A", groups=[25, 999999])])
    results = validate_overview(document, group_validator=InMemoryGroupValidator({25}))

    assert "GROUP_ID_KNOWN" in {result.code for result in results}


def test_group_ids_load_from_json_array(tmp_path):
    path = tmp_path / "groups.json"
    path.write_text("[25, \"26\"]", encoding="utf-8")

    assert load_group_ids(path) == {25, 26}


def test_group_ids_load_from_json_object_keys(tmp_path):
    path = tmp_path / "groups.json"
    path.write_text('{"25": {"name": "Frigate"}, "26": {"name": "Cruiser"}}', encoding="utf-8")

    assert load_group_ids(path) == {25, 26}


def test_group_ids_load_from_json_lines(tmp_path):
    path = tmp_path / "groups.jsonl"
    path.write_text('{"groupIds": [25]}\n{"groups": ["26"]}\n', encoding="utf-8")

    assert load_group_ids(path) == {25, 26}


def test_real_overview_with_nine_tabs_is_allowed_in_current_mode():
    document = load_overview_yaml("Examples/Real-Overview.yaml")

    assert "TAB_LIMIT_CURRENT" not in codes(document)
