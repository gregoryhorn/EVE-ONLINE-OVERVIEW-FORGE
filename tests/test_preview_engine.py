from eve_overview_manager.models.overview import AppearanceConfig, ColumnsConfig, OverviewDocument, Preset, TabBinding
from eve_overview_manager.preview import build_preview
from eve_overview_manager.preview.engine import SAMPLE_ENTITIES, STATE_SAMPLE_NAMES


def _doc(*, groups=None, always=None, filtered=None, columns=None):
    return OverviewDocument(
        tabs=[TabBinding(slot=1, label="PVP", overviewPresetRef="pvp")],
        presets=[
            Preset(
                id="pvp",
                name="PVP",
                groups=groups or [],
                alwaysShownStates=always or [],
                filteredStates=filtered or [],
            )
        ],
        columns=ColumnsConfig(
            columnOrder=columns or ["ICON", "DISTANCE", "NAME", "TYPE"],
            enabled=columns or ["ICON", "DISTANCE", "NAME", "TYPE"],
        ),
    )


def test_preview_uses_active_tab_preset_groups():
    preview = build_preview(_doc(groups=[25]))

    assert "Frigate" in [row["cells"]["TYPE"] for row in preview["rows"]]


def test_empty_preset_groups_hide_sample_rows():
    preview = build_preview(_doc(groups=[]))

    assert preview["rows"] == []


def test_always_shown_state_overrides_missing_group():
    preview = build_preview(_doc(groups=[], always=[11]))

    assert "Ansiblex Jump Bridge" in [row["cells"]["TYPE"] for row in preview["rows"]]
    assert all(11 in row["stateIds"] for row in preview["rows"])


def test_filtered_state_hides_matching_entity():
    preview = build_preview(_doc(groups=[1408], filtered=[11]))

    assert preview["rows"] == []


def test_columns_follow_enabled_order():
    preview = build_preview(_doc(groups=[25], columns=["ICON", "NAME", "CORPORATION", "VELOCITY"]))

    assert [column["id"] for column in preview["columns"]] == ["ICON", "NAME", "CORPORATION", "VELOCITY"]
    assert preview["rows"][0]["groupName"] == "Frigate"
    assert preview["rows"][0]["cells"]["CORPORATION"] == "Fleet"


def test_preview_columns_use_document_columns_not_imported_tab_columns():
    document = _doc(groups=[25], columns=["ICON", "NAME"])
    document.tabs[0].unknown["tabColumns"] = ["ICON", "DISTANCE", "NAME", "TYPE"]

    preview = build_preview(document)

    assert [column["id"] for column in preview["columns"]] == ["ICON", "NAME"]


def test_bracket_mode_uses_tab_bracket_preset_reference():
    document = OverviewDocument(
        tabs=[TabBinding(slot=1, label="PVP", overviewPresetRef="overview", bracketPresetRef="brackets")],
        presets=[
            Preset(id="overview", name="Overview", groups=[25]),
            Preset(id="brackets", name="Brackets", groups=[10]),
        ],
        columns=ColumnsConfig(columnOrder=["ICON", "NAME", "TYPE"], enabled=["ICON", "NAME", "TYPE"]),
    )

    preview = build_preview(document, mode="brackets")

    assert preview["mode"] == "brackets"
    assert preview["activePreset"]["name"] == "Brackets"
    assert [row["cells"]["TYPE"] for row in preview["rows"]] == ["Stargate (Caldari System)"]


def test_bracket_mode_warning_mentions_bracket_preset():
    document = OverviewDocument(tabs=[TabBinding(slot=1, label="PVP", overviewPresetRef="overview")])

    preview = build_preview(document, mode="brackets")

    assert preview["warnings"] == ["No bracket preset selected; sample rows are unfiltered."]


def test_preview_exposes_appearance_resolution():
    document = _doc(groups=[1408])
    document.appearance = AppearanceConfig(
        flagOrder=[11],
        backgroundOrder=[11],
        stateColors={"flag_11": "red", "background_11": "orange"},
        stateBlinks={"background_11": True},
    )

    preview = build_preview(document)

    assert preview["rows"][0]["appearance"] == {
        "flagStateId": 11,
        "backgroundStateId": 11,
        "flagColor": "#d80000",
        "backgroundColor": "#ff6a00",
        "flagBlink": False,
        "backgroundBlink": True,
    }


def test_preview_exposes_flag_blink_and_color_names():
    document = _doc(groups=[25])
    document.appearance = AppearanceConfig(
        flagOrder=[12],
        stateColors={"flag_12": "turquoise"},
        stateBlinks={"flag_12": True},
    )

    preview = build_preview(document)

    assert preview["rows"][0]["appearance"]["flagColor"] == "#00a8a8"
    assert preview["rows"][0]["appearance"]["flagBlink"] is True


def test_preview_group_names_can_use_sde_name_map():
    preview = build_preview(_doc(groups=[25]), group_names={25: "SDE Frigate"})

    assert preview["rows"][0]["groupName"] == "SDE Frigate"


def test_preview_catalog_covers_visible_preset_group_controls():
    expected_group_ids = {
        9,
        10,
        12,
        15,
        25,
        26,
        27,
        28,
        29,
        30,
        31,
        100,
        185,
        186,
        187,
        188,
        189,
        358,
        365,
        419,
        463,
        485,
        513,
        541,
        543,
        547,
        548,
        659,
        831,
        832,
        833,
        838,
        883,
        894,
        988,
        1082,
        1246,
        1247,
        1404,
        1406,
        1408,
        1538,
        1657,
    }

    sample_group_ids = {entity["groupId"] for entity in SAMPLE_ENTITIES}

    assert expected_group_ids <= sample_group_ids


def test_preview_catalog_includes_required_celestial_and_misc_rows():
    required = {
        6: "Sun M0",
        7: "Planet (Gas)",
        8: "Moon",
        9: "Asteroid Belt",
        4079: "Encounter Surveillance System",
        1979: "Abyssal Filament",
    }

    types_by_group = {}
    for entity in SAMPLE_ENTITIES:
        types_by_group.setdefault(entity["groupId"], set()).add(entity["type"])

    for group_id, type_name in required.items():
        assert type_name in types_by_group.get(group_id, set())


def test_preview_icon_column_uses_icon_kind_not_bracket_letters():
    preview = build_preview(_doc(groups=[25]))

    assert preview["rows"][0]["cells"]["ICON"] == "ship"


def test_preview_can_target_preset_directly_without_active_tab():
    document = OverviewDocument(
        tabs=[TabBinding(slot=1, label="PVP", overviewPresetRef="ships")],
        presets=[
            Preset(id="ships", name="Ships", groups=[25]),
            Preset(id="gates", name="Gates", groups=[10]),
        ],
        columns=ColumnsConfig(columnOrder=["ICON", "NAME", "TYPE"], enabled=["ICON", "NAME", "TYPE"]),
    )

    preview = build_preview(document, preset_id="gates")

    assert preview["activePreset"]["id"] == "gates"
    assert "Stargate (Caldari System)" in [row["cells"]["TYPE"] for row in preview["rows"]]


def test_preview_generates_labeled_rows_for_imported_groups_without_static_samples():
    preview = build_preview(_doc(groups=[529]), group_names={529: "Strategic Cruiser"}, coverage=True)

    assert preview["rows"][0]["groupName"] == "Strategic Cruiser"
    assert preview["rows"][0]["cells"]["NAME"] == "Strategic Cruiser sample"
    assert preview["rows"][0]["cells"]["ICON"] == "unknown"


def test_preview_falls_back_to_group_id_for_unknown_imported_groups():
    preview = build_preview(_doc(groups=[999999]), coverage=True)

    assert preview["rows"][0]["groupName"] == "Group 999999"
    assert preview["rows"][0]["cells"]["NAME"] == "Group 999999 sample"
    assert preview["rows"][0]["cells"]["TYPE"] == "Group 999999"


def test_normal_preview_does_not_generate_rows_for_every_imported_group():
    preview = build_preview(_doc(groups=[529]), group_names={529: "Strategic Cruiser"})

    assert preview["rows"] == []
    assert preview["coverage"] is False


def test_coverage_preview_generates_rows_for_imported_groups():
    preview = build_preview(_doc(groups=[529]), group_names={529: "Strategic Cruiser"}, coverage=True)

    assert preview["coverage"] is True
    assert preview["rows"][0]["groupName"] == "Strategic Cruiser"


def test_preview_state_samples_cover_visible_state_filters():
    preview = build_preview(_doc(groups=[], always=list(STATE_SAMPLE_NAMES)))
    covered_states = {state for row in preview["rows"] for state in row["stateIds"]}

    assert set(STATE_SAMPLE_NAMES) <= covered_states


def test_preview_state_sample_labels_match_common_eve_states():
    assert STATE_SAMPLE_NAMES[11] == "Pilot is in your fleet"
    assert STATE_SAMPLE_NAMES[13] == "Pilot is at war with your corporation/alliance"
    assert STATE_SAMPLE_NAMES[50] == "Pilot is a suspect"
    assert STATE_SAMPLE_NAMES[51] == "Pilot is a criminal"
    assert STATE_SAMPLE_NAMES[52] == "Pilot has a limited engagement with you"
    assert STATE_SAMPLE_NAMES[53] == "Pilot has a kill right on them that you can activate"


def test_filtering_all_visible_state_samples_hides_preview_rows():
    preview = build_preview(_doc(groups=[25, 100, 1657], filtered=list(STATE_SAMPLE_NAMES)))

    assert preview["rows"] == []


def test_preview_generates_state_samples_for_selected_preset_group():
    preview = build_preview(_doc(groups=[6, 25]), preset_id="pvp")

    state_sample_rows = [row for row in preview["rows"] if row["groupId"] == 25 and row["stateIds"][0] in STATE_SAMPLE_NAMES]
    covered_states = {state for row in state_sample_rows for state in row["stateIds"]}

    assert set(STATE_SAMPLE_NAMES) <= covered_states
    assert all("Sun with" not in row["cells"]["TYPE"] for row in state_sample_rows)
    assert all("state sample" not in row["cells"]["TYPE"] for row in state_sample_rows)


def test_preview_state_samples_can_use_structure_and_drone_groups():
    structure_preview = build_preview(_doc(groups=[6, 1657]), preset_id="pvp")
    drone_preview = build_preview(_doc(groups=[100]), preset_id="pvp")

    structure_rows = [row for row in structure_preview["rows"] if row["groupId"] == 1657 and row["cells"]["NAME"].endswith("Citadel")]
    drone_rows = [row for row in drone_preview["rows"] if row["groupId"] == 100 and row["cells"]["NAME"].endswith("Combat Drone")]

    assert {state for row in structure_rows for state in row["stateIds"]} == set(STATE_SAMPLE_NAMES)
    assert {state for row in drone_rows for state in row["stateIds"]} == set(STATE_SAMPLE_NAMES)


def test_preview_catalog_has_state_variety_for_ships_drones_and_structures():
    ship_states = {state for row in SAMPLE_ENTITIES if row["icon"] == "ship" for state in row["stateIds"]}
    drone_states = {state for row in SAMPLE_ENTITIES if row["icon"] == "drone" for state in row["stateIds"]}
    structure_states = {state for row in SAMPLE_ENTITIES if row["icon"] == "structure" for state in row["stateIds"]}

    assert {9, 11, 12, 13, 14, 50, 51} <= ship_states
    assert {11, 12, 20, 50} <= drone_states
    assert {11, 12, 14, 20} <= structure_states


def test_preview_state_samples_skip_non_entity_presets():
    preview = build_preview(_doc(groups=[6]), preset_id="pvp")

    state_sample_rows = [
        row
        for row in preview["rows"]
        if row["stateIds"][0] in STATE_SAMPLE_NAMES and row["cells"]["NAME"].endswith(" sample")
    ]

    assert state_sample_rows == []
