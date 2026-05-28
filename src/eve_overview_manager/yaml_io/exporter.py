"""YAML exporter foundation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from eve_overview_manager.models.overview import OverviewDocument

DEFAULT_TOP_LEVEL_ORDER = [
    "backgroundOrder",
    "backgroundStates",
    "columnOrder",
    "flagOrder",
    "flagStates",
    "overviewColumns",
    "presets",
    "shipLabelOrder",
    "shipLabels",
    "stateBlinks",
    "stateColorsNameList",
    "tabSetup",
    "userSettings",
]
DEFAULT_PRESET_FIELD_ORDER = ["alwaysShownStates", "filteredStates", "groups"]
DEFAULT_TAB_FIELD_ORDER = ["bracket", "color", "name", "overview"]


def _dict_to_pairs(value: dict[str, Any]) -> list[list[Any]]:
    return [[key, item] for key, item in value.items()]


def _argb_to_rgb_float_list(value: str | None) -> list[float] | None:
    if value is None or len(value) != 8:
        return None
    try:
        red = int(value[2:4], 16) / 255
        green = int(value[4:6], 16) / 255
        blue = int(value[6:8], 16) / 255
    except ValueError:
        return None
    return [round(red, 4), round(green, 4), round(blue, 4)]


def _ordered_pairs(fields: dict[Any, Any], requested_order: list[Any], fallback_order: list[Any]) -> list[list[Any]]:
    remaining = dict(fields)
    pairs: list[list[Any]] = []
    for key in requested_order or fallback_order:
        if key in remaining:
            pairs.append([key, remaining.pop(key)])
    for key in fallback_order:
        if key in remaining:
            pairs.append([key, remaining.pop(key)])
    pairs.extend([[key, value] for key, value in remaining.items()])
    return pairs


def _build_yaml_sections(document: OverviewDocument) -> dict[str, Any]:
    sections: dict[str, Any] = {}
    sections.update(document.unknown)
    sections["backgroundOrder"] = document.appearance.backgroundOrder
    sections["backgroundStates"] = document.appearance.backgroundStates
    sections["columnOrder"] = document.columns.columnOrder
    sections["flagOrder"] = document.appearance.flagOrder
    sections["flagStates"] = document.appearance.flagStates
    sections["overviewColumns"] = document.columns.enabled
    sections["presets"] = [
        [
            preset.name,
            _ordered_pairs(
                {
                    "alwaysShownStates": preset.alwaysShownStates,
                    "filteredStates": preset.filteredStates,
                    "groups": preset.groups,
                },
                preset.fieldOrder,
                DEFAULT_PRESET_FIELD_ORDER,
            ),
        ]
        for preset in document.presets
    ]
    sections["shipLabelOrder"] = document.labels.shipLabelOrder
    sections["shipLabels"] = _ordered_pairs(document.labels.shipLabels, document.labels.shipLabelsOrder, list(document.labels.shipLabels.keys()))
    sections["stateBlinks"] = _ordered_pairs(
        document.appearance.stateBlinks,
        document.appearance.stateBlinksOrder,
        list(document.appearance.stateBlinks.keys()),
    )
    sections["stateColorsNameList"] = _ordered_pairs(
        document.appearance.stateColors,
        document.appearance.stateColorsOrder,
        list(document.appearance.stateColors.keys()),
    )
    sections["tabSetup"] = []
    for tab in document.tabs:
        fields: dict[str, Any] = {}
        if tab.bracketPresetRef is not None:
            fields["bracket"] = tab.bracketPresetRef
        color = _argb_to_rgb_float_list(tab.colorARGB)
        if color is not None:
            fields["color"] = color
        fields["name"] = tab.label
        if tab.overviewPresetRef is not None:
            fields["overview"] = tab.overviewPresetRef
        fields.update(tab.unknown)
        sections["tabSetup"].append([tab.slot, _ordered_pairs(fields, tab.fieldOrder, DEFAULT_TAB_FIELD_ORDER)])
    sections["userSettings"] = _ordered_pairs(document.misc.userSettings, document.misc.userSettingsOrder, list(document.misc.userSettings.keys()))
    return sections


def _ordered_sections(document: OverviewDocument, sections: dict[str, Any]) -> dict[str, Any]:
    ordered: dict[str, Any] = {}
    requested_order = document.meta.topLevelKeyOrder or DEFAULT_TOP_LEVEL_ORDER
    for key in requested_order:
        if key in sections:
            ordered[key] = sections.pop(key)
    for key in DEFAULT_TOP_LEVEL_ORDER:
        if key in sections:
            ordered[key] = sections.pop(key)
    ordered.update(sections)
    return ordered


def export_overview_yaml(document: OverviewDocument, path: str | Path) -> None:
    data = _ordered_sections(document, _build_yaml_sections(document))

    yaml = YAML()
    yaml.default_flow_style = False
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        yaml.dump(data, file)
