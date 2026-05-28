"""Build a local, approximate overview preview from a canonical document."""

from __future__ import annotations

from typing import Any

from eve_overview_manager.models.overview import OverviewDocument, Preset, TabBinding

DEFAULT_COLUMNS = ["ICON", "DISTANCE", "NAME", "TYPE"]
COLUMN_LABELS = {
    "ICON": "",
    "DISTANCE": "Dist",
    "NAME": "Name",
    "TYPE": "Type",
    "TAG": "Tag",
    "CORPORATION": "Corp",
    "ALLIANCE": "Alliance",
    "VELOCITY": "Velocity",
    "TRANSVERSALVELOCITY": "Transversal",
    "RADIALVELOCITY": "Radial",
    "ANGULARVELOCITY": "Angular",
    "SIZE": "Size",
}

GROUP_NAMES = {
    6: "Sun",
    7: "Planet",
    8: "Moon",
    9: "Asteroid Belt",
    10: "Stargate",
    12: "Cargo Container",
    15: "Station",
    25: "Frigate",
    26: "Cruiser",
    27: "Battleship",
    28: "Hauler",
    29: "Capsule",
    30: "Titan",
    31: "Shuttle",
    100: "Combat Drone",
    185: "Pirate Drone",
    186: "Wreck",
    187: "NPC Battleship",
    188: "NPC Industrial",
    189: "NPC Hauler",
    358: "Heavy Assault Cruiser",
    365: "Control Tower",
    419: "Combat Battlecruiser",
    420: "Destroyer",
    463: "Mining Barge",
    485: "Dreadnought",
    513: "Freighter",
    541: "Interdictor",
    543: "Exhumer",
    547: "Carrier",
    548: "Interdiction Probe",
    659: "Supercarrier",
    831: "Interceptor",
    832: "Logistics",
    833: "Force Recon Ship",
    838: "Cynosural Generator Array",
    883: "Capital Industrial Ship",
    894: "Heavy Interdiction Cruiser",
    988: "Wormhole",
    1003: "Territorial Claim Unit",
    1012: "Sovereignty Hub",
    1082: "Capsuleer Bases",
    1246: "Mobile Depot",
    1247: "Mobile Siphon Unit",
    1404: "Engineering Complex",
    1406: "Refinery",
    1408: "Upwell Jump Bridge",
    1538: "Force Auxiliary",
    1657: "Citadel",
    1909: "Battlecruiser",
    1979: "Abyssal Filaments",
    2017: "Upwell Cyno Beacon",
    4079: "Encounter Surveillance System",
    4093: "Mobile Cynosural Beacon",
}

STATE_SAMPLE_NAMES = {
    9: "Pilot has a security status below -5",
    10: "Pilot has a security status below 0",
    11: "Pilot is in your fleet",
    12: "Pilot is in your Capsuleer corporation",
    13: "Pilot is at war with your corporation/alliance",
    14: "Pilot is in your alliance",
    15: "Pilot has Excellent Standing.",
    16: "Pilot has Good Standing.",
    17: "Pilot has Neutral Standing",
    18: "Pilot has Bad Standing.",
    19: "Pilot has Terrible Standing.",
    20: "Pilot has No Standing.",
    21: "Pilot (agent) is interactable",
    36: "Pilot is a suspect",
    37: "Pilot is a criminal",
    44: "Pilot is at war with your militia",
    45: "Pilot is in your militia or allied to your militia",
    48: "Pilot is an ally in one or more of your wars",
    49: "Pilot is an ally in one or more of your wars",
    50: "Pilot is a suspect",
    51: "Pilot is a criminal",
    52: "Pilot has a limited engagement with you",
    53: "Pilot has a kill right on them that you can activate",
    66: "Pilot is in your Non Capsuleer corporation",
    68: "Pilot has retribution timer",
}

STATE_SAMPLE_GROUP_ID = 25
STATE_SAMPLE_GROUP_IDS = {
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
    420,
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
    1012,
    1082,
    1246,
    1247,
    1404,
    1406,
    1408,
    1538,
    1657,
    2017,
    4079,
    4093,
}

SAMPLE_ENTITIES: list[dict[str, Any]] = [
    {"groupId": 1657, "stateIds": [20], "icon": "structure", "name": "4-HWWF - WinterCo. Keepstar", "distance": "0 m", "type": "Keepstar", "corporation": "-", "alliance": "WinterCo.", "velocity": "0 m/s"},
    {"groupId": 1657, "stateIds": [12], "icon": "structure", "name": "Fleet Astrahus", "distance": "420 km", "type": "Astrahus", "corporation": "Fleet", "alliance": "Fleet", "velocity": "0 m/s"},
    {"groupId": 1657, "stateIds": [11], "icon": "structure", "name": "War Target Fortizar", "distance": "620 km", "type": "Fortizar", "corporation": "Hostile", "alliance": "Hostile", "velocity": "0 m/s"},
    {"groupId": 1406, "stateIds": [14], "icon": "structure", "name": "Corp Athanor", "distance": "780 km", "type": "Athanor", "corporation": "Corp", "alliance": "Alliance", "velocity": "0 m/s"},
    {"groupId": 838, "stateIds": [20], "icon": "deployable", "name": "Industrial Cynosural Field", "distance": "75 km", "type": "Industrial Cynosural Field", "corporation": "-", "alliance": "-", "velocity": "0 m/s"},
    {"groupId": 2017, "stateIds": [20], "icon": "structure", "name": "4-HWWF - Northern Cyno Beacon", "distance": "349 km", "type": "Pharolux Cyno Beacon", "corporation": "-", "alliance": "-", "velocity": "0 m/s"},
    {"groupId": 1657, "stateIds": [20], "icon": "structure", "name": "4-HWWF - ROSEMARY's", "distance": "1,117 km", "type": "'Draccous' Fortizar", "corporation": "-", "alliance": "WinterCo.", "velocity": "0 m/s"},
    {"groupId": 1406, "stateIds": [20], "icon": "structure", "name": "4-HWWF - WinterCo. Refinery", "distance": "1,221 km", "type": "Tatara", "corporation": "-", "alliance": "WinterCo.", "velocity": "0 m/s"},
    {"groupId": 10, "stateIds": [20], "icon": "gate", "name": "YMJG-4", "distance": "2,171 km", "type": "Stargate (Caldari System)", "corporation": "-", "alliance": "-", "velocity": "0 m/s"},
    {"groupId": 1404, "stateIds": [20], "icon": "structure", "name": "4-HWWF - WinterCo. Sotiyo", "distance": "3,303 km", "type": "Sotiyo", "corporation": "-", "alliance": "WinterCo.", "velocity": "0 m/s"},
    {"groupId": 15, "stateIds": [20], "icon": "structure", "name": "Jita IV - Moon 4 - Caldari Navy Assembly Plant", "distance": "5.1 AU", "type": "Station", "corporation": "Caldari Navy", "alliance": "-", "velocity": "0 m/s"},
    {"groupId": 7, "stateIds": [20], "icon": "celestial", "name": "4-HWWF VI", "distance": "55,163 km", "type": "Planet (Gas)", "corporation": "-", "alliance": "-", "velocity": "0 m/s"},
    {"groupId": 1408, "stateIds": [11], "icon": "gate", "name": "4-HWWF * 7-K5EL - N", "distance": "203,572 km", "type": "Ansiblex Jump Bridge", "corporation": "-", "alliance": "Hostile", "velocity": "0 m/s"},
    {"groupId": 9, "stateIds": [20], "icon": "celestial", "name": "Desolate Asteroid Belt", "distance": "7.3 AU", "type": "Asteroid Belt", "corporation": "-", "alliance": "-", "velocity": "0 m/s"},
    {"groupId": 1012, "stateIds": [20], "icon": "structure", "name": "Sovereignty Hub", "distance": "8.4 AU", "type": "Sovereignty Hub", "corporation": "-", "alliance": "-", "velocity": "0 m/s"},
    {"groupId": 6, "stateIds": [20], "icon": "celestial", "name": "4-HWWF - Star", "distance": "8.4 AU", "type": "Sun M0", "corporation": "-", "alliance": "-", "velocity": "0 m/s"},
    {"groupId": 8, "stateIds": [20], "icon": "celestial", "name": "4-HWWF IV - Moon 3", "distance": "5.6 AU", "type": "Moon", "corporation": "-", "alliance": "-", "velocity": "0 m/s"},
    {"groupId": 4079, "stateIds": [20], "icon": "structure", "name": "Encounter Surveillance System", "distance": "6.2 AU", "type": "Encounter Surveillance System", "corporation": "-", "alliance": "-", "velocity": "0 m/s"},
    {"groupId": 1979, "stateIds": [20], "icon": "deployable", "name": "Abyssal Filament Trace", "distance": "41 km", "type": "Abyssal Filament", "corporation": "-", "alliance": "-", "velocity": "0 m/s"},
    {"groupId": 25, "stateIds": [12], "icon": "ship", "name": "Fleet Tackle", "distance": "18 km", "type": "Frigate", "corporation": "Fleet", "alliance": "Fleet", "velocity": "3,921 m/s"},
    {"groupId": 420, "stateIds": [14], "icon": "ship", "name": "Corp Destroyer", "distance": "24 km", "type": "Destroyer", "corporation": "Corp", "alliance": "Alliance", "velocity": "1,214 m/s"},
    {"groupId": 26, "stateIds": [51], "icon": "ship", "name": "Criminal Cruiser", "distance": "19 km", "type": "Cruiser", "corporation": "Criminal", "alliance": "-", "velocity": "1,630 m/s"},
    {"groupId": 27, "stateIds": [13], "icon": "ship", "name": "War Target Battleship", "distance": "71 km", "type": "Battleship", "corporation": "Hostile", "alliance": "Hostile", "velocity": "220 m/s"},
    {"groupId": 28, "stateIds": [20], "icon": "ship", "name": "Neutral Industrial", "distance": "42 km", "type": "Industrial", "corporation": "-", "alliance": "-", "velocity": "210 m/s"},
    {"groupId": 29, "stateIds": [20], "icon": "ship", "name": "Capsule", "distance": "16 km", "type": "Capsule", "corporation": "-", "alliance": "-", "velocity": "410 m/s"},
    {"groupId": 30, "stateIds": [11], "icon": "ship", "name": "War Target Avatar", "distance": "150 km", "type": "Titan", "corporation": "Hostile", "alliance": "Hostile", "velocity": "55 m/s"},
    {"groupId": 31, "stateIds": [20], "icon": "ship", "name": "Shuttle", "distance": "61 km", "type": "Shuttle", "corporation": "-", "alliance": "-", "velocity": "4,200 m/s"},
    {"groupId": 419, "stateIds": [50], "icon": "ship", "name": "Suspect Battlecruiser", "distance": "39 km", "type": "Combat Battlecruiser", "corporation": "Suspect", "alliance": "-", "velocity": "842 m/s"},
    {"groupId": 463, "stateIds": [20], "icon": "ship", "name": "Retriever", "distance": "23 km", "type": "Mining Barge", "corporation": "-", "alliance": "-", "velocity": "120 m/s"},
    {"groupId": 485, "stateIds": [11], "icon": "ship", "name": "War Target Revelation", "distance": "78 km", "type": "Dreadnought", "corporation": "Hostile", "alliance": "Hostile", "velocity": "80 m/s"},
    {"groupId": 513, "stateIds": [20], "icon": "ship", "name": "Charon", "distance": "12 km", "type": "Freighter", "corporation": "-", "alliance": "-", "velocity": "95 m/s"},
    {"groupId": 541, "stateIds": [11], "icon": "ship", "name": "War Target Sabre", "distance": "32 km", "type": "Interdictor", "corporation": "Hostile", "alliance": "Hostile", "velocity": "2,900 m/s"},
    {"groupId": 543, "stateIds": [20], "icon": "ship", "name": "Hulk", "distance": "28 km", "type": "Exhumer", "corporation": "-", "alliance": "-", "velocity": "95 m/s"},
    {"groupId": 547, "stateIds": [11], "icon": "ship", "name": "War Target Thanatos", "distance": "116 km", "type": "Carrier", "corporation": "Hostile", "alliance": "Hostile", "velocity": "72 m/s"},
    {"groupId": 659, "stateIds": [11], "icon": "ship", "name": "War Target Nyx", "distance": "181 km", "type": "Supercarrier", "corporation": "Hostile", "alliance": "Hostile", "velocity": "64 m/s"},
    {"groupId": 831, "stateIds": [11], "icon": "ship", "name": "War Target Stiletto", "distance": "14 km", "type": "Interceptor", "corporation": "Hostile", "alliance": "Hostile", "velocity": "5,200 m/s"},
    {"groupId": 832, "stateIds": [12], "icon": "ship", "name": "Fleet Guardian", "distance": "46 km", "type": "Logistics", "corporation": "Fleet", "alliance": "Fleet", "velocity": "820 m/s"},
    {"groupId": 833, "stateIds": [11], "icon": "ship", "name": "War Target Rapier", "distance": "38 km", "type": "Recon Ship", "corporation": "Hostile", "alliance": "Hostile", "velocity": "1,140 m/s"},
    {"groupId": 883, "stateIds": [20], "icon": "ship", "name": "Rorqual", "distance": "54 km", "type": "Rorqual", "corporation": "-", "alliance": "-", "velocity": "52 m/s"},
    {"groupId": 894, "stateIds": [11], "icon": "ship", "name": "War Target Onyx", "distance": "29 km", "type": "Heavy Interdictor", "corporation": "Hostile", "alliance": "Hostile", "velocity": "780 m/s"},
    {"groupId": 1538, "stateIds": [12], "icon": "ship", "name": "Fleet Apostle", "distance": "91 km", "type": "Force Auxiliary", "corporation": "Fleet", "alliance": "Fleet", "velocity": "62 m/s"},
    {"groupId": 358, "stateIds": [11], "icon": "ship", "name": "War Target Cerberus", "distance": "63 km", "type": "Heavy Assault Cruiser", "corporation": "Hostile", "alliance": "Hostile", "velocity": "1,680 m/s"},
    {"groupId": 100, "stateIds": [20], "icon": "drone", "name": "Hammerhead II", "distance": "27 km", "type": "Combat Drone", "corporation": "-", "alliance": "-", "velocity": "2,400 m/s"},
    {"groupId": 100, "stateIds": [12], "icon": "drone", "name": "Fleet Warrior II", "distance": "18 km", "type": "Combat Drone", "corporation": "Fleet", "alliance": "Fleet", "velocity": "4,900 m/s"},
    {"groupId": 100, "stateIds": [11], "icon": "drone", "name": "War Target Hobgoblin II", "distance": "22 km", "type": "Combat Drone", "corporation": "Hostile", "alliance": "Hostile", "velocity": "4,200 m/s"},
    {"groupId": 100, "stateIds": [50], "icon": "drone", "name": "Suspect Acolyte II", "distance": "24 km", "type": "Combat Drone", "corporation": "Suspect", "alliance": "-", "velocity": "4,500 m/s"},
    {"groupId": 185, "stateIds": [20], "icon": "npc", "name": "Angel Webifier", "distance": "31 km", "type": "NPC Frigate", "corporation": "Angel Cartel", "alliance": "-", "velocity": "1,100 m/s"},
    {"groupId": 186, "stateIds": [20], "icon": "npc", "name": "Guristas Nullifier", "distance": "37 km", "type": "NPC Cruiser", "corporation": "Guristas", "alliance": "-", "velocity": "540 m/s"},
    {"groupId": 187, "stateIds": [20], "icon": "npc", "name": "Sansha Overlord", "distance": "52 km", "type": "NPC Battleship", "corporation": "Sansha", "alliance": "-", "velocity": "210 m/s"},
    {"groupId": 188, "stateIds": [20], "icon": "npc", "name": "Blood Raider Industrial", "distance": "44 km", "type": "NPC Industrial", "corporation": "Blood Raiders", "alliance": "-", "velocity": "160 m/s"},
    {"groupId": 189, "stateIds": [20], "icon": "npc", "name": "Serpentis Hauler", "distance": "48 km", "type": "NPC Hauler", "corporation": "Serpentis", "alliance": "-", "velocity": "140 m/s"},
    {"groupId": 12, "stateIds": [20], "icon": "wreck", "name": "Wreck of Hostile Cruiser", "distance": "31 km", "type": "Wreck", "corporation": "-", "alliance": "-", "velocity": "0 m/s"},
    {"groupId": 548, "stateIds": [20], "icon": "deployable", "name": "Mobile Tractor Unit", "distance": "46 km", "type": "Mobile Tractor Unit", "corporation": "-", "alliance": "-", "velocity": "0 m/s"},
    {"groupId": 365, "stateIds": [20], "icon": "structure", "name": "Offline POS Tower", "distance": "2.4 AU", "type": "Control Tower", "corporation": "-", "alliance": "-", "velocity": "0 m/s"},
    {"groupId": 1082, "stateIds": [20], "icon": "deployable", "name": "Warp Disruption Probe", "distance": "18 km", "type": "Interdiction Sphere", "corporation": "-", "alliance": "-", "velocity": "0 m/s"},
    {"groupId": 1246, "stateIds": [20], "icon": "deployable", "name": "Mobile Depot", "distance": "22 km", "type": "Mobile Depot", "corporation": "-", "alliance": "-", "velocity": "0 m/s"},
    {"groupId": 1247, "stateIds": [20], "icon": "deployable", "name": "Mobile Siphon Unit", "distance": "26 km", "type": "Mobile Siphon Unit", "corporation": "-", "alliance": "-", "velocity": "0 m/s"},
    {"groupId": 9, "stateIds": [20], "icon": "asteroid", "name": "Veldspar", "distance": "12 km", "type": "Asteroid", "corporation": "-", "alliance": "-", "velocity": "0 m/s"},
    {"groupId": 988, "stateIds": [20], "icon": "wormhole", "name": "Unstable Wormhole", "distance": "3.2 AU", "type": "Wormhole", "corporation": "-", "alliance": "-", "velocity": "0 m/s"},
    {"groupId": 25, "stateIds": [9], "icon": "ship", "name": "Outlaw Frigate", "distance": "34 km", "type": "Frigate", "corporation": "Outlaw", "alliance": "-", "velocity": "2,200 m/s"},
]

STATE_SAMPLE_ENTITIES: list[dict[str, Any]] = [
    {
        "groupId": STATE_SAMPLE_GROUP_ID,
        "stateIds": [state_id],
        "icon": "ship" if state_id not in {52, 53} else "npc",
        "name": f"{name} pilot sample",
        "distance": f"{18 + index} km",
        "type": "Frigate",
        "corporation": name,
        "alliance": "State Samples",
        "velocity": "1,000 m/s",
    }
    for index, (state_id, name) in enumerate(STATE_SAMPLE_NAMES.items())
]

STATE_ROW_CLASSES = {
    9: "row-wartarget",
    11: "row-wartarget",
    12: "row-fleet",
    14: "row-corp",
    16: "row-good",
    45: "row-good",
    36: "row-suspect",
    37: "row-criminal",
    50: "row-suspect",
    51: "row-criminal",
    52: "row-wartarget",
}

COLOR_NAMES = {
    "darkturquoise": "#007c78",
    "turquoise": "#00a8a8",
    "cyan": "#00a8a8",
    "purple": "#5a148c",
    "darkblue": "#0b2698",
    "blue": "#2878ff",
    "violet": "#8a2cff",
    "green": "#28b928",
    "orange": "#ff6a00",
    "yellow": "#ffc000",
    "black": "#000000",
    "white": "#d8d8d8",
    "red": "#d80000",
}


def build_preview(
    document: OverviewDocument,
    active_slot: int | None = None,
    mode: str = "overview",
    group_names: dict[int, str] | None = None,
    preset_id: str | None = None,
    coverage: bool = False,
) -> dict[str, Any]:
    tabs = sorted(document.tabs, key=lambda tab: tab.slot)
    active_tab = _active_tab(tabs, active_slot)
    presets = {preset.id: preset for preset in document.presets}
    preset_ref = (
        preset_id
        if preset_id
        else active_tab.bracketPresetRef if mode == "brackets" and active_tab else active_tab.overviewPresetRef if active_tab else None
    )
    active_preset = _resolve_preset(preset_ref, document.presets)
    columns = _columns_for(document, active_tab)
    name_map = {**GROUP_NAMES, **(group_names or {})}
    entities = [
        *SAMPLE_ENTITIES,
        *STATE_SAMPLE_ENTITIES,
        *(_missing_group_entities(active_preset, name_map) if coverage else []),
        *(_preset_state_sample_entities(active_preset, name_map) if preset_id else []),
    ]
    visible_rows = [_entity_row(entity, document, columns, name_map) for entity in entities if _is_visible(entity, active_preset)]

    return {
        "mode": mode,
        "coverage": coverage,
        "tabs": [
            {
                "slot": tab.slot,
                "label": tab.label,
                "overviewPresetRef": tab.overviewPresetRef,
                "bracketPresetRef": tab.bracketPresetRef,
                "colorARGB": tab.colorARGB,
                "active": active_tab is not None and tab.slot == active_tab.slot,
                "presetFound": (tab.overviewPresetRef in presets) if tab.overviewPresetRef else False,
            }
            for tab in tabs
        ],
        "activeTab": active_tab.model_dump() if active_tab else None,
        "activePreset": active_preset.model_dump() if active_preset else None,
        "columns": [{"id": column, "label": COLUMN_LABELS.get(column, column.title())} for column in columns],
        "rows": visible_rows,
        "totalSampleRows": len(entities),
        "warnings": _preview_warnings(active_tab, active_preset, preset_ref, mode),
    }


def _active_tab(tabs: list[TabBinding], active_slot: int | None) -> TabBinding | None:
    if not tabs:
        return None
    if active_slot is not None:
        for tab in tabs:
            if tab.slot == active_slot:
                return tab
    return tabs[0]


def _resolve_preset(reference: str | None, presets: list[Preset]) -> Preset | None:
    if not reference:
        return None
    return next((preset for preset in presets if preset.id == reference or preset.name == reference), None)


def _is_visible(entity: dict[str, Any], preset: Preset | None) -> bool:
    if preset is None:
        return True
    groups = {group for group in preset.groups if isinstance(group, int)}
    always = {state for state in preset.alwaysShownStates if isinstance(state, int)}
    filtered = {state for state in preset.filteredStates if isinstance(state, int)}
    states = {state for state in entity["stateIds"] if isinstance(state, int)}
    if states & always:
        return True
    if states & filtered:
        return False
    return entity["groupId"] in groups


def _missing_group_entities(preset: Preset | None, group_names: dict[int, str]) -> list[dict[str, Any]]:
    if preset is None:
        return []
    sample_group_ids = {entity["groupId"] for entity in [*SAMPLE_ENTITIES, *STATE_SAMPLE_ENTITIES]}
    entities = []
    for group_id in sorted({group for group in preset.groups if isinstance(group, int)} - sample_group_ids):
        label = _group_label(group_names, group_id)
        entities.append(
            {
                "groupId": group_id,
                "stateIds": [13],
                "icon": "unknown",
                "name": f"{label} sample",
                "distance": "50 km",
                "type": label,
                "corporation": "-",
                "alliance": "-",
                "velocity": "0 m/s",
            }
        )
    return entities


def _preset_state_sample_entities(preset: Preset | None, group_names: dict[int, str]) -> list[dict[str, Any]]:
    if preset is None:
        return []
    groups = sorted({group for group in preset.groups if isinstance(group, int)})
    if not groups:
        return []
    sample_group_id = _state_sample_group(groups)
    if sample_group_id is None:
        return []
    group_name = _group_label(group_names, sample_group_id)
    return [
        {
            "groupId": sample_group_id,
            "stateIds": [state_id],
            "icon": _icon_for_group(sample_group_id),
            "name": f"{state_name} {group_name}",
            "distance": f"{20 + index} km",
            "type": group_name,
            "corporation": state_name,
            "alliance": "State Samples",
            "velocity": "1,000 m/s",
        }
        for index, (state_id, state_name) in enumerate(STATE_SAMPLE_NAMES.items())
    ]


def _state_sample_group(groups: list[int]) -> int | None:
    for group_id in groups:
        if group_id in STATE_SAMPLE_GROUP_IDS:
            return group_id
    return None


def _icon_for_group(group_id: int) -> str:
    if group_id in {6, 7, 8, 9, 15, 988}:
        return "celestial"
    if group_id in {10, 1408}:
        return "gate"
    if group_id in {12}:
        return "wreck"
    if group_id in {100}:
        return "drone"
    if group_id in {185, 186, 187, 188, 189}:
        return "npc"
    if group_id in {365, 1003, 1012, 1404, 1406, 1657, 2017, 4079}:
        return "structure"
    if group_id in {548, 838, 1082, 1246, 1247, 1979}:
        return "deployable"
    if group_id in GROUP_NAMES:
        return "ship"
    return "unknown"


def _columns_for(document: OverviewDocument, tab: TabBinding | None) -> list[str]:
    if document.columns.enabled:
        columns = [str(column) for column in document.columns.enabled]
    else:
        columns = DEFAULT_COLUMNS
    order = [str(column) for column in document.columns.columnOrder]
    if order:
        columns = [column for column in order if column in columns] + [column for column in columns if column not in order]
    return columns


def _entity_row(entity: dict[str, Any], document: OverviewDocument, columns: list[str], group_names: dict[int, str]) -> dict[str, Any]:
    flag_state_id = _first_priority_state(entity["stateIds"], document.appearance.flagOrder)
    background_state_id = _first_priority_state(entity["stateIds"], document.appearance.backgroundOrder)
    state_id = background_state_id or flag_state_id or entity["stateIds"][0]
    return {
        "groupId": entity["groupId"],
        "groupName": _group_label(group_names, entity["groupId"]),
        "stateIds": entity["stateIds"],
        "className": STATE_ROW_CLASSES.get(state_id, "row-neutral"),
        "appearance": _appearance_for(document, flag_state_id, background_state_id),
        "cells": {column: _cell_value(entity, column) for column in columns},
    }


def _group_label(group_names: dict[int, str], group_id: int) -> str:
    return group_names.get(group_id) or f"Group {group_id}"


def _cell_value(entity: dict[str, Any], column: str) -> str:
    key = {
        "ICON": "icon",
        "DISTANCE": "distance",
        "NAME": "name",
        "TYPE": "type",
        "CORPORATION": "corporation",
        "ALLIANCE": "alliance",
        "VELOCITY": "velocity",
    }.get(column)
    if key:
        return str(entity.get(key, ""))
    if column == "TAG":
        return ""
    return ""


def _first_priority_state(state_ids: list[int], priority: list[Any]) -> int | None:
    for state in priority:
        if isinstance(state, int) and state in state_ids:
            return state
    return None


def _appearance_for(
    document: OverviewDocument,
    flag_state_id: int | None,
    background_state_id: int | None,
) -> dict[str, Any]:
    return {
        "flagStateId": flag_state_id,
        "backgroundStateId": background_state_id,
        "flagColor": _color_for(document.appearance.stateColors.get(f"flag_{flag_state_id}") if flag_state_id else None),
        "backgroundColor": _color_for(
            document.appearance.stateColors.get(f"background_{background_state_id}") if background_state_id else None
        ),
        "flagBlink": bool(document.appearance.stateBlinks.get(f"flag_{flag_state_id}")) if flag_state_id else False,
        "backgroundBlink": bool(document.appearance.stateBlinks.get(f"background_{background_state_id}")) if background_state_id else False,
    }


def _color_for(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower()
    if normalized.startswith("#") and len(normalized) in {4, 7}:
        return normalized
    return COLOR_NAMES.get(normalized)


def _preview_warnings(tab: TabBinding | None, preset: Preset | None, preset_ref: str | None, mode: str) -> list[str]:
    warnings: list[str] = []
    if tab is None:
        warnings.append("No tabs defined; sample rows are unfiltered.")
    elif preset_ref and preset is None and not preset_ref.startswith(("DefaultPreset_", "_BracketFilter")):
        warnings.append(f"Preset reference was not found: {preset_ref}")
    elif preset is None:
        label = "bracket" if mode == "brackets" else "overview"
        warnings.append(f"No {label} preset selected; sample rows are unfiltered.")
    return warnings
